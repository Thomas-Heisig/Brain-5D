\"""Write the full test_restore_determinism_abc.py file."""
import os

# Read the existing first part (was written by PowerShell)
first_part_path = 'F:/Brain-5D/tests/test_restore_determinism_abc.py'
with open(first_part_path, 'r', encoding='utf-8') as f:
    first_part = f.read()

# The rest of the file to append
rest = '''
ARTIFACT_DIR = Path(__file__).resolve().parent.parent / "research" / "generated" / "verification"
ARTIFACT_PATH = ARTIFACT_DIR / "restore_determinism.json"
WORKER_PATH = Path(__file__).resolve().parent / "_restore_worker.py"

# ============================================================================
# Schedule cache
# ============================================================================

_SCHEDULE_CACHE: list[dict[str, Any]] | None = None


def _get_schedule() -> list[dict[str, Any]]:
    global _SCHEDULE_CACHE
    if _SCHEDULE_CACHE is None:
        _SCHEDULE_CACHE = build_absolute_schedule(make_config(), N)
    return _SCHEDULE_CACHE


def _write_production_artifacts(
    network: NeuralNetwork,
    homeo: HomeostasisEngine,
    learn: LearningEngine,
    tmp_path: Path,
    schedule: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Path]:
    """Write snapshot, journal, checkpoint, config, and schedule to tmp_path."""
    rt = StorageRuntimeConfig(
        snapshot_path=tmp_path / "base.b5d",
        journal_path=tmp_path / "base.b5d.journal",
        commit_interval_ticks=1,
    )
    with StorageSession(network, rt):  # type: ignore[arg-type]
        pass

    from tests._restore_helpers import capture_learning_state
    learn_state = capture_learning_state(learn) if learn is not None else None

    checkpoint = capture_runtime_checkpoint(
        network,
        homeostasis_rates=homeo._rates_hz if homeo is not None else None,
        learning_states=learn_state["states"] if learn_state else None,
        pending_rewards=learn_state["pending_rewards"] if learn_state else None,
    )
    cp_path = tmp_path / "runtime.json"
    write_runtime_checkpoint(cp_path, checkpoint)
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
    sched_path = tmp_path / "schedule.json"
    sched_path.write_text(json.dumps(schedule, sort_keys=True), encoding="utf-8")
    return {
        "snapshot": rt.snapshot_path,
        "journal": rt.journal_path,
        "checkpoint": cp_path,
        "config": cfg_path,
        "schedule": sched_path,
    }

# ============================================================================
# Path A — uninterrupted reference
# ============================================================================

def _run_path_A(config: dict[str, Any], schedule: list[dict[str, Any]]) -> str:
    """Run 0 -> N uninterrupted. Returns canonical digest at N."""
    network = create_network(config)
    homeo = HomeostasisEngine(network, config)
    homeo.attach()
    learn = LearningEngine(network, config)
    learn.attach()
    run_absolute_schedule(network, schedule, N)
    return compute_digest(network, homeo, learn, config_sha256_str=config_sha256(config))


def _run_path_A_digests(
    config: dict[str, Any],
    schedule: list[dict[str, Any]],
) -> dict[str, str]:
    """Run 0 -> N uninterrupted. Returns digests at K and N."""
    network = create_network(config)
    homeo = HomeostasisEngine(network, config)
    homeo.attach()
    learn = LearningEngine(network, config)
    learn.attach()
    run_absolute_schedule(network, schedule, K)
    digest_K = compute_digest(network, homeo, learn, config_sha256_str=config_sha256(config))
    run_absolute_schedule(network, schedule, N)
    digest_N = compute_digest(network, homeo, learn, config_sha256_str=config_sha256(config))
    return {"digest_K": digest_K, "digest_N": digest_N}


# ============================================================================
# Path B — in-process restore via production restore_full
# ============================================================================

def _run_path_B(
    config: dict[str, Any],
    schedule: list[dict[str, Any]],
    tmp_path: Path,
) -> dict[str, Any]:
    """Run B: in-process restore. Returns metadata dict with all proofs."""
    network = create_network(config)
    homeo = HomeostasisEngine(network, config)
    homeo.attach()
    learn = LearningEngine(network, config)
    learn.attach()

    # Digest at K before restore
    run_absolute_schedule(network, schedule, K)
    digest_B_pre_restore_K = compute_digest(
        network, homeo, learn, config_sha256_str=config_sha256(config),
    )

    # Write artifacts and restore
    artifacts = _write_production_artifacts(network, homeo, learn, tmp_path, schedule, config)
    bundle = restore_full(
        snapshot_path=artifacts["snapshot"],
        journal_path=artifacts["journal"],
        checkpoint_path=artifacts["checkpoint"],
        config=config,
        recovered_path=tmp_path / "recovered.b5d",
        create_homeostasis_engine=True,
        create_learning_engine=True,
    )

    # Digest at K after restore
    digest_B_restored_K = compute_digest(
        bundle.network, bundle.homeostasis_engine, bundle.learning_engine,
        config_sha256_str=config_sha256(config),
    )

    is_different = (bundle.network is not network)

    # Continue K -> N
    run_absolute_schedule(bundle.network, schedule, N)
    digest_N = compute_digest(
        bundle.network, bundle.homeostasis_engine, bundle.learning_engine,
        config_sha256_str=config_sha256(config),
    )

    return {
        "digest_N": digest_N,
        "digest_pre_restore_K": digest_B_pre_restore_K,
        "digest_restored_K": digest_B_restored_K,
        "restore_full_used": is_different,
        "pid": os.getpid(),
    }


# ============================================================================
# Path C — fresh-process terminate/restart via subprocess
# ============================================================================

def _run_path_C(
    config: dict[str, Any],
    schedule: list[dict[str, Any]],
    tmp_path: Path,
) -> dict[str, Any]:
    """Run C: fresh-process terminate/restart. Returns metadata dict.

    C1 is a subprocess that creates network, runs 0->K, writes artifacts, exits.
    C2 is a subprocess that restores from artifacts, runs K->N, writes result.

    Pytest process (P0) is orchestrator only.
    No in-memory network/engine/state object crosses the boundary.
    """
    c1_script = tmp_path / "_run_c1.py"
    parent = str(Path(__file__).resolve().parent.parent).replace("\\\\", "/")
    c1_code = (
        'import json, os, sys\\n'
        'from pathlib import Path\\n'
        f'sys.path.insert(0, r"{parent}")\\n'
        'from tests._restore_helpers import (\\n'
        '    K as _K, create_network, make_config, build_absolute_schedule,\\n'
        '    run_absolute_schedule, compute_digest, config_sha256,\\n'
        ')\\n'
        'from src.homeostasis.engine import HomeostasisEngine\\n'
        'from src.learning.learning_engine import LearningEngine\\n'
        'from src.storage.checkpoint import capture_runtime_checkpoint, write_runtime_checkpoint\\n'
        'from src.storage.runtime import StorageRuntimeConfig, StorageSession\\n\\n'
        '_cfg = make_config()\\n'
        '_sched = build_absolute_schedule(_cfg, _K)\\n'
        '_net = create_network(_cfg)\\n'
        '_homeo = HomeostasisEngine(_net, _cfg)\\n'
        '_homeo.attach()\\n'
        '_learn = LearningEngine(_net, _cfg)\\n'
        '_learn.attach()\\n'
        'run_absolute_schedule(_net, _sched, _K)\\n\\n'
        '_digest_K = compute_digest(_net, _homeo, _learn, config_sha256_str=config_sha256(_cfg))\\n\\n'
        f'_rt = StorageRuntimeConfig(\\n    snapshot_path=Path(r"{str(tmp_path / "c1_base.b5d").replace(chr(92), '/')}"),\\n    journal_path=Path(r"{str(tmp_path / "c1_base.b5d.journal").replace(chr(92), '/')}"),\\n    commit_interval_ticks=1,\\n)\\n'
        'with StorageSession(_net, _rt):\\n    pass\\n'
        'from tests._restore_helpers import capture_learning_state\\n'
        '_ls = capture_learning_state(_learn)\\n'
        '_cp = capture_runtime_checkpoint(\\n    _net,\\n    homeostasis_rates=_homeo._rates_hz,\\n    learning_states=_ls["states"],\\n    pending_rewards=_ls["pending_rewards"],\\n)\\n'
        f'write_runtime_checkpoint(Path(r"{str(tmp_path / "c1_runtime.json").replace(chr(92), '/')}"), _cp)\\n'
        f'Path(r"{str(tmp_path / "c1_config.json").replace(chr(92), '/')}").write_text(json.dumps(_cfg, sort_keys=True), encoding="utf-8")\\n'
        f'Path(r"{str(tmp_path / "c1_schedule.json").replace(chr(92), '/')}").write_text(json.dumps(_sched, sort_keys=True), encoding="utf-8")\\n'
        f'Path(r"{str(tmp_path / "c1_digest_K.json").replace(chr(92), '/')}").write_text(json.dumps({{\\"digest_K\\": _digest_K, \\"pid\\": os.getpid()}}), encoding="utf-8")\\n'
        f'Path(r"{str(tmp_path / "pid_C1.txt").replace(chr(92), '/')}").write_text(str(os.getpid()), encoding="utf-8")\\n'
        'print(f"C1 done: digest_K={_digest_K}, pid={os.getpid()}")\\n'
    )
    c1_script.write_text(c1_code)

    # ── Run C1 subprocess ────────────────────────────────────────────────
    c1_result = subprocess.run(
        [sys.executable, str(c1_script)],
        capture_output=True, text=True, timeout=300,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    if c1_result.returncode != 0:
        raise RuntimeError(
            f"C1 subprocess failed (exit {c1_result.returncode}):\\n"
            f"stdout: {c1_result.stdout}\\n"
            f"stderr: {c1_result.stderr}"
        )

    # Read C1 artifacts
    c1_digest_data = json.loads((tmp_path / "c1_digest_K.json").read_text(encoding="utf-8"))
    pid_C1 = c1_digest_data["pid"]
    digest_C1_K = c1_digest_data["digest_K"]

    # ── Run C2 subprocess ────────────────────────────────────────────────
    worker_args = [
        sys.executable,
        str(WORKER_PATH),
        "--snapshot", str(tmp_path / "c1_base.b5d"),
        "--journal", str(tmp_path / "c1_base.b5d.journal"),
        "--checkpoint", str(tmp_path / "c1_runtime.json"),
        "--config", str(tmp_path / "c1_config.json"),
        "--schedule", str(tmp_path / "c1_schedule.json"),
        "--output", str(tmp_path / "c2_result.json"),
        "--end-tick", str(N),
        "--digest-k", str(tmp_path / "c2_digest_K.json"),
    ]

    c2_result = subprocess.run(
        worker_args,
        capture_output=True, text=True, timeout=300,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    if c2_result.returncode != 0:
        raise RuntimeError(
            f"C2 worker failed (exit {c2_result.returncode}):\\n"
            f"stdout: {c2_result.stdout}\\n"
            f"stderr: {c2_result.stderr}"
        )

    c2_data = json.loads((tmp_path / "c2_result.json").read_text(encoding="utf-8"))
    pid_C2 = c2_data["pid"]
    digest_C2_restored_K = c2_data.get("digest_K", "")
    digest_C_N = c2_data["digest"]

    return {
        "digest_N": digest_C_N,
        "digest_C1_K": digest_C1_K,
        "digest_C2_restored_K": digest_C2_restored_K,
        "pid_C1": pid_C1,
        "pid_C2": pid_C2,
        "restore_full_used": c2_data.get("restore_full_used", False),
    }


# ============================================================================
# Tests
# ============================================================================

class TestRestoreDeterminismABC:
    """Full A/B/C restore determinism protocol."""

    def test_path_A_completes(self) -> None:
        config = make_config()
        d = _run_path_A(config, _get_schedule())
        assert isinstance(d, str) and len(d) == 64

    def test_path_B_completes(self, tmp_path: Path) -> None:
        config = make_config()
        result = _run_path_B(config, _get_schedule(), tmp_path)
        assert isinstance(result["digest_N"], str) and len(result["digest_N"]) == 64

    def test_path_C_completes(self, tmp_path: Path) -> None:
        config = make_config()
        result = _run_path_C(config, _get_schedule(), tmp_path)
        assert isinstance(result["digest_N"], str) and len(result["digest_N"]) == 64

    def test_A_equals_B(self, tmp_path: Path) -> None:
        config = make_config()
        schedule = _get_schedule()
        dA = _run_path_A(config, schedule)
        b_result = _run_path_B(config, schedule, tmp_path)
        assert b_result["restore_full_used"], "Path B did not use restore_full()"
        assert dA == b_result["digest_N"], f"A != B\\nA: {dA}\\nB: {b_result['digest_N']}"

    def test_A_equals_C(self, tmp_path: Path) -> None:
        config = make_config()
        schedule = _get_schedule()
        dA = _run_path_A(config, schedule)
        c_result = _run_path_C(config, schedule, tmp_path)
        assert c_result["pid_C1"] != c_result["pid_C2"], "C1 and C2 must be different processes"
        assert dA == c_result["digest_N"], f"A != C\\nA: {dA}\\nC: {c_result['digest_N']}"

    def test_B_equals_C(self, tmp_path: Path) -> None:
        config = make_config()
        schedule = _get_schedule()
        b_result = _run_path_B(config, schedule, tmp_path)
        c_result = _run_path_C(config, schedule, tmp_path)
        assert b_result["digest_N"] == c_result["digest_N"], (
            f"B != C\\nB: {b_result['digest_N']}\\nC: {c_result['digest_N']}"
        )

    def test_checkpoint_boundary_identity(self, tmp_path: Path) -> None: