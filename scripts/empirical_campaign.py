"""Execute declared protocols without promoting DATA to accepted evidence.

Each protocol runs in a fresh process. The plan and source receipt precede data.
Human review templates and missing native adapters remain explicitly pending.
"""

from __future__ import annotations

import argparse
import dataclasses
import gzip
import hashlib
import importlib
import inspect
import json
import math
import platform
import subprocess
import sys
import time
import traceback
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.research.experiment_recorder import ExperimentRecorder  # noqa: E402
from src.research.protocol_registry import (  # noqa: E402
    OPERATIONAL_RUNNERS,
    protocol_catalog,
    validate_operational_protocol,
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, allow_nan=False
    ).encode()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value) + b"\n")


def source_receipt() -> dict[str, Any]:
    """Hash all tracked inputs, separately from generated experimental DATA."""
    names = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .split("\0")
    )
    files = {}
    prefixes = (
        "src/",
        "scripts/",
        "configs/",
        "research/protocols/",
        "research/preregistrations/",
        "research/registry/",
        "research/schemas/",
    )
    for name in names:
        if name and (
            name.startswith(prefixes) or name in ("pyproject.toml", "requirements.txt")
        ):
            files[name] = sha((ROOT / name).read_bytes())
    return {
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT)
        .decode()
        .strip(),
        "files": files,
        "digest": sha(encode(files)),
    }


def runner(name: str) -> Any:
    for module in (
        "src.research.experiment_suite",
        "src.research.followup_experiments",
    ):
        value = getattr(importlib.import_module(module), name, None)
        if value is not None:
            return value
    raise ValueError(f"Registered runner missing: {name}")


def make_plan() -> dict[str, Any]:
    selections = []
    templates = []
    for item in protocol_catalog(ROOT / "research"):
        if item.get("execution_kind") == "conceptual_audit":
            templates.append(
                {
                    "protocol": item["id"],
                    "status": "human_review_pending",
                    "executed": False,
                }
            )
            continue
        name = OPERATIONAL_RUNNERS[item["id"]]
        func = runner(name)
        prereg = validate_operational_protocol(
            ROOT / "research",
            question_id=item["research_question"],
            hypothesis_id=item["hypothesis"],
            protocol_id=item["id"],
            seed_count=10000,
        )
        minimum = item["minimum_independent_seeds"]
        declared = prereg["seed_strategy"].get("seeds")
        defaults = inspect.signature(func).parameters["seeds"].default
        seeds = (
            declared
            if declared
            else (
                list(defaults)
                if len(defaults) >= minimum
                else list(range(42, 42 + minimum))
            )
        )
        if len(seeds) < minimum or len(set(seeds)) != len(seeds):
            raise ValueError(f"Invalid registered seed budget: {item['id']}")
        ticks = item.get("default_ticks")
        if ticks is None and "ticks" in inspect.signature(func).parameters:
            ticks = inspect.signature(func).parameters["ticks"].default
        selections.append(
            {
                "protocol": item["id"],
                "runner": name,
                "seeds": seeds,
                "ticks": ticks,
                "research_question": item["research_question"],
                "hypothesis": item["hypothesis"],
                "preregistration": item["preregistration"],
                "primary_outcomes": item["primary_outcomes"],
                "registered_mode": prereg["mode"],
                "execution_mode": "EXPLORATORY_REEXECUTION",
                "timeout_seconds": 1200,
            }
        )
    selections.append(
        {
            "protocol": "foundational_seven_suite",
            "runner": "run_all",
            "seeds": [42, 43, 44],
            "ticks": 1000,
            "research_question": None,
            "hypothesis": None,
            "primary_outcomes": [],
            "execution_mode": "EXPLORATORY",
            "timeout_seconds": 1200,
        }
    )
    questions: list[dict[str, Any]] = []
    for file in sorted((ROOT / "research/registry").glob("questions*.yaml")):
        data = yaml.safe_load(file.read_text())
        questions.extend(data if isinstance(data, list) else data.get("questions", []))
    mapped = {s["research_question"] for s in selections}
    template_ids = {
        p["research_question"]
        for p in protocol_catalog(ROOT / "research")
        if p.get("execution_kind") == "conceptual_audit"
    }
    unmapped = sorted(
        q["id"] for q in questions if q["id"] not in mapped | template_ids
    )
    return {
        "schema_version": 1,
        "campaign": "EXP-EMP-20260910",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": source_receipt(),
        "config": "configs/learning_experiment.yaml",
        "config_sha256": sha((ROOT / "configs/learning_experiment.yaml").read_bytes()),
        "runtime_ai_calls": 0,
        "ai_assisted_design": True,
        "authority": "DATA_ONLY_HUMAN_REVIEW_REQUIRED",
        "external_preregistration_claimed": False,
        "execution_policy": "complete all declared budgets; no data-dependent tuning or retries; scientific negatives retained",
        "selections": selections,
        "human_templates": templates,
        "questions_without_specific_runnable_protocol": unmapped,
    }


def finite_json(
    value: Any, path: str = "root", problems: list[str] | None = None
) -> Any:
    """Keep non-finite values as explicit invalid sentinels; never silently drop."""
    if problems is None:
        problems = []
    if isinstance(value, float) and not math.isfinite(value):
        problems.append(path)
        return {"nonfinite": repr(value)}
    if isinstance(value, dict):
        return {
            str(k): finite_json(v, f"{path}.{k}", problems) for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [finite_json(v, f"{path}[{i}]", problems) for i, v in enumerate(value)]
    return value


def worker(output: Path, index: int) -> None:
    plan = json.loads((output / "plan.json").read_text())
    spec = plan["selections"][index]
    folder = output / f"{index + 1:03d}-{spec['protocol']}"
    folder.mkdir(parents=True, exist_ok=False)
    save(folder / "selection.json", spec)
    started = time.perf_counter()
    result: dict[str, Any] = {
        "protocol": spec["protocol"],
        "status": "failed",
        "runs": [],
        "nonfinite_paths": [],
    }
    try:
        config = yaml.safe_load((ROOT / plan["config"]).read_text())
        func = runner(spec["runner"])
        kwargs: dict[str, Any] = {"seeds": tuple(spec["seeds"])}
        if "ticks" in inspect.signature(func).parameters:
            kwargs["ticks"] = spec["ticks"]
        rows = [dataclasses.asdict(row) for row in func(config, **kwargs)]
        result["runs"] = finite_json(rows, problems=result["nonfinite_paths"])
        errors = [r.get("runtime_error") for r in rows if r.get("runtime_error")]
        result["status"] = (
            "invalid" if errors or result["nonfinite_paths"] else "completed"
        )
        result["runtime_errors"] = errors
    except Exception:
        result["error"] = traceback.format_exc()
    result["wall_seconds"] = time.perf_counter() - started
    result["environment"] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    raw = encode(result)
    with gzip.GzipFile(
        filename=str(folder / "runs.json.gz"), mode="wb", mtime=0
    ) as stream:
        stream.write(raw)
    recorder = ExperimentRecorder(
        f"EXP-EMP-20260910-{index + 1:03d}", output_dir=folder
    )
    recorder.record_config(plan["config"], plan["config_sha256"])
    recorder.record_simulation_params(seeds=spec["seeds"], ticks=spec["ticks"])
    if spec["research_question"]:
        recorder.record_research_links(
            research_questions=[spec["research_question"]],
            hypotheses=[spec["hypothesis"]],
        )
    recorder.record_artifact("raw_runs", "runs.json.gz")
    recorder.record_provenance_digests(
        code_digest=plan["source"]["digest"],
        config_digest=plan["config_sha256"],
        prompt_digest=sha(b"no runtime model prompt; AI-assisted experimental design"),
        data_digest=sha(raw),
    )
    recorder.record_results(
        protocol=spec["protocol"],
        run_count=len(result["runs"]),
        execution_status=result["status"],
        ai_assisted_design=True,
        runtime_ai_calls=0,
        pre_execution_source_digest=plan["source"]["digest"],
        accepted_evidence=False,
    )
    if result["status"] == "completed":
        recorder.mark_completed()
    else:
        recorder.mark_failed()
    recorder.save()
    save(
        folder / "receipt.json",
        {
            "protocol": spec["protocol"],
            "status": result["status"],
            "run_count": len(result["runs"]),
            "uncompressed_data_sha256": sha(raw),
            "compressed_data_sha256": sha((folder / "runs.json.gz").read_bytes()),
            "wall_seconds": result["wall_seconds"],
            "error": result.get("error"),
        },
    )


def execute(
    output: Path, protocols: list[str] | None = None, campaign: str = "EXP-EMP-20260910"
) -> None:
    """Freeze input first, run each selection once, retain interrupted attempts."""
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError(
            "Execute outside the source checkout; publish immutable receipts afterwards"
        )
    if output.exists():
        raise ValueError("Refusing to overwrite an earlier campaign")
    dirty = (
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)
        .decode()
        .strip()
    )
    if dirty:
        raise ValueError("Commit source and preregistration before campaign execution")
    output.mkdir(parents=True)
    plan = make_plan()
    plan["campaign"] = campaign
    if protocols:
        known = {item["protocol"] for item in plan["selections"]}
        if set(protocols) - known:
            raise ValueError("Unknown or human-review-only selected protocol")
        plan["not_selected_protocols"] = sorted(known - set(protocols))
        plan["selections"] = [
            item for item in plan["selections"] if item["protocol"] in protocols
        ]
        plan["selection_scope"] = "explicitly selected amendment; not a full rerun"
    save(output / "plan.json", plan)

    def launch(index: int) -> None:
        spec = plan["selections"][index]
        with (output / f"worker-{index + 1:03d}.log").open("w") as log:
            try:
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).resolve()),
                        "--worker",
                        str(index),
                        "--output",
                        str(output),
                    ],
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=spec["timeout_seconds"],
                    check=False,
                )
                save(
                    output / f"process-{index + 1:03d}.json",
                    {"returncode": completed.returncode, "protocol": spec["protocol"]},
                )
            except subprocess.TimeoutExpired:
                save(
                    output / f"process-{index + 1:03d}.json",
                    {
                        "returncode": None,
                        "status": "timeout",
                        "protocol": spec["protocol"],
                    },
                )
        print(spec["protocol"], "attempt recorded", flush=True)

    # Serial execution avoids confounded CPU/RSS measurements across protocols.
    with ThreadPoolExecutor(max_workers=1) as pool:
        list(pool.map(launch, range(len(plan["selections"]))))
    unchanged = source_receipt()["digest"] == plan["source"]["digest"]
    save(
        output / "completion.json",
        {
            "source_unchanged": unchanged,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    analyze(output)
    if not unchanged:
        raise RuntimeError("Source changed during campaign")


def analyze(output: Path) -> dict[str, Any]:
    from src.research.empirical_evaluation import holm_adjust, paired_summary

    plan = json.loads((output / "plan.json").read_text())
    summary: dict[str, Any] = {
        "campaign": plan["campaign"],
        "source": plan["source"]["commit"],
        "source_digest": plan["source"]["digest"],
        "ai_assisted_analysis": True,
        "accepted_evidence": False,
        "protocols": [],
        "human_review_pending": len(plan["human_templates"]),
        "questions_without_specific_runnable_protocol": plan[
            "questions_without_specific_runnable_protocol"
        ],
        "comparisons": {},
    }
    for index, spec in enumerate(plan["selections"]):
        folder = output / f"{index + 1:03d}-{spec['protocol']}"
        if not (folder / "runs.json.gz").exists():
            summary["protocols"].append(
                {"protocol": spec["protocol"], "status": "incomplete", "runs": 0}
            )
            continue
        result = json.loads(gzip.decompress((folder / "runs.json.gz").read_bytes()))
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for run in result["runs"]:
            groups[run["condition"]].append(run)
        conditions = {}
        for condition, runs in groups.items():
            scalars: dict[str, list[float]] = defaultdict(list)
            for run in runs:
                for key, value in run["metrics"].items():
                    if (
                        isinstance(value, (int, float))
                        and not isinstance(value, bool)
                        and math.isfinite(value)
                    ):
                        scalars[key].append(float(value))
            conditions[condition] = {
                "runs": len(runs),
                "metrics": {
                    key: {
                        "mean": sum(vals) / len(vals),
                        "min": min(vals),
                        "max": max(vals),
                        "unique_values": len(set(vals)),
                    }
                    for key, vals in scalars.items()
                },
                "boolean_outcomes": {
                    key: [r["metrics"].get(key) for r in runs]
                    for key in sorted(
                        {
                            k
                            for r in runs
                            for k, v in r["metrics"].items()
                            if isinstance(v, bool)
                        }
                    )
                },
            }
        summary["protocols"].append(
            {
                "protocol": spec["protocol"],
                "status": result["status"],
                "runs": len(result["runs"]),
                "conditions": conditions,
                "wall_seconds": result["wall_seconds"],
                "error": result.get("error"),
                "data": f"{folder.name}/runs.json.gz",
            }
        )
        comparisons = []
        pid = spec["protocol"]
        if (
            pid in ("dimensional_connectivity_v1", "native_association_holdout_v1")
            and result["status"] == "completed"
        ):
            metric = (
                "output_spikes"
                if pid == "dimensional_connectivity_v1"
                else "test_accuracy"
            )
            reference = (
                "geometry_5d" if pid == "dimensional_connectivity_v1" else "learning_on"
            )
            alternatives = (
                [f"geometry_{d}d" for d in (2, 3, 4, 6, 8)]
                if pid == "dimensional_connectivity_v1"
                else ["learning_off", "sham_replay", "weight_reset", "weight_shuffle"]
            )
            for alternative in alternatives:
                a = sorted(groups[reference], key=lambda r: r["seed"])
                b = sorted(groups[alternative], key=lambda r: r["seed"])
                if [r["seed"] for r in a] != [r["seed"] for r in b]:
                    raise ValueError("Unmatched comparison seeds")
                comparisons.append(
                    {
                        "reference": reference,
                        "control": alternative,
                        "metric": metric,
                        **paired_summary(
                            [r["metrics"][metric] for r in a],
                            [r["metrics"][metric] for r in b],
                        ),
                    }
                )
            adjusted = holm_adjust(
                [row["exact_two_sided_sign_flip_p"] for row in comparisons]
            )
            for row, p in zip(comparisons, adjusted):
                row["holm_adjusted_p"] = p
            summary["comparisons"][pid] = comparisons
    summary["status_counts"] = dict(
        Counter(item["status"] for item in summary["protocols"])
    )
    summary["total_runs"] = sum(item["runs"] for item in summary["protocols"])
    save(output / "summary.json", summary)
    lines = [
        "# Empirical campaign: executed DATA, not accepted EVID",
        "",
        f"Source: `{summary['source']}`; digest `{summary['source_digest']}`.",
        "",
        "AI-assisted design/analysis; zero runtime model calls. No independent replication or ethics approval asserted.",
        "",
        "| Protocol | Execution | Runs |",
        "| --- | --- | ---: |",
    ]
    for item in summary["protocols"]:
        lines.append(f"| {item['protocol']} | {item['status']} | {item['runs']} |")
    lines += [
        "",
        f"Human review templates not executed: {summary['human_review_pending']}.",
        "",
        "## Scope and inference",
        "",
        "Engineering completion is not scientific success. Constant outcomes across seeds do not establish independent empirical variation. The legacy matched-5D protocol preserves one graph and measures embedding invariance. Local seeded replication is not an external team's replication. Component memory, world-model and profile experiments are not SNN-learning evidence. Real human reviews remain pending.",
        "",
        "New topology contrasts measure propagation, not task advantage. The teacher-paired native association task is synthetic; test weights are frozen, evaluation episodes are novel, and teacher current is absent during all tests. Brian2 covers matched single-cell integration only, not framework superiority. Scaling is a short active sparse workload; RSS samples are not isolated memory peaks and no electrical energy is measured.",
        "",
        "New inferential comparisons use paired simulation seeds, 2000 fixed-seed percentile bootstraps, exact two-sided sign flips and Holm correction per family; n is small and the sign-flip symmetry assumption is not empirically guaranteed. Degenerate effects have no invented standardized effect size. No automatic EVID promotion.",
        "",
        "## Declared comparisons",
        "",
        "```json",
        json.dumps(summary["comparisons"], indent=2),
        "```",
        "",
        "## Questions without a matching runnable protocol",
        "",
        ", ".join(summary["questions_without_specific_runnable_protocol"]),
        "",
        "These are not replaced by generic tick runs. External assessment, unavailable adapters, independent teams and additional framework integrations cannot be manufactured by this campaign.",
    ]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worker", type=int)
    parser.add_argument("--protocol", action="append")
    parser.add_argument("--campaign-id", default="EXP-EMP-20260910")
    parser.add_argument("--analyze", action="store_true")
    args = parser.parse_args()
    if args.worker is not None:
        worker(args.output, args.worker)
    elif args.analyze:
        analyze(args.output)
    else:
        execute(args.output, args.protocol, args.campaign_id)


if __name__ == "__main__":
    main()
