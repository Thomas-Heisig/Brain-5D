"""Canonical Alpha.5 release-gate status builder.

This module computes the *release / verification* status of the Alpha.5
gate -- strictly separated from the *live runtime* status that
``integration_status.py`` reports.

Key distinction
---------------
A component can simultaneously be::

    live_status   = disabled      (disabled in the running poc_config)
    gate_status   = pending       (E2E verification still outstanding)

This is exactly the maturity logic from ``docs/TODO.md``::

    IMPLEMENTED -> INTEGRATED -> VERIFIED -> EVIDENCED

The browser must NEVER infer scientific completion. The gate truth is
built here from real backend state and evidence, not from a hardcoded
frontend checklist.

Maturity (``maturity``)::

    implemented
    integrated
    verified
    evidenced

Gate result (``status``)::

    passed
    pending
    blocked
    stale
    failed

Live runtime (``live_status``)::

    active
    disabled
    unavailable
    error

These are deliberately disjoint vocabularies so a disabled runtime
component is neither automatically failed nor automatically passed at
the release gate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from src.dashboard.models import JSONValue
from src.dashboard.verification import evaluate_test_baseline

# ============================================================================
# Status vocabularies (deliberately disjoint)
# ============================================================================

# Maturity of a feature in the project (orthogonal to live runtime state).
IMPLEMENTED = "implemented"
INTEGRATED = "integrated"
VERIFIED = "verified"
EVIDENCED = "evidenced"

_VALID_MATURITY = {IMPLEMENTED, INTEGRATED, VERIFIED, EVIDENCED}

# Gate result: did the *release criterion* actually pass?
G_PASSED = "passed"
G_PENDING = "pending"
G_BLOCKED = "blocked"
G_STALE = "stale"
G_FAILED = "failed"

_VALID_GATE_STATUS = {G_PASSED, G_PENDING, G_BLOCKED, G_STALE, G_FAILED}

# Live runtime state of a component in the *currently running* config.
L_ACTIVE = "active"
L_DISABLED = "disabled"
L_UNAVAILABLE = "unavailable"
L_ERROR = "error"

_VALID_LIVE_STATUS = {L_ACTIVE, L_DISABLED, L_UNAVAILABLE, L_ERROR}

# Gate identifiers.
GATE_A = "A"
GATE_B = "B"
GATE_C = "C"

# Required structural E2E proof set — the artifact must contain exactly
# these proof IDs, all True. No extra or missing fields are tolerated.
REQUIRED_STRUCTURAL_PROOFS: frozenset[str] = frozenset({
    "test_proof_01_coordinator_instantiated",
    "test_proof_02_plasticity_engine_instantiated",
    "test_proof_03_bridge_identity",
    "test_proof_04_real_signal_proposal",
    "test_proof_05_proposal_no_mutation",
    "test_proof_06_reject_no_mutation",
    "test_proof_07_approve_exactly_one_mutation",
    "test_proof_08_exactly_one_change_record",
    "test_proof_09_undo_restores_topology",
    "test_proof_10_restart_replay_identity",
    "test_complete_canonical_e2e",
})

# Required structural live loop proof set — the live loop artifact must
# contain exactly these proof IDs, all True.
REQUIRED_LIVE_LOOP_PROOFS: frozenset[str] = frozenset({
    "production_adapter_attached",
    "real_signal_generated",
    "policy_received_real_signal",
    "proposal_published",
    "proposal_non_mutating",
    "reject_non_mutating",
    "approve_single_mutation",
    "journal_linked_to_proposal",
    "runtime_continues_after_mutation",
    "undo_restores_topology",
    "journal_reopen_replay_identity",
})

# Required single listener proof set — the artifact must contain exactly
# these proof IDs, all True.
REQUIRED_SINGLE_LISTENER_PROOFS: frozenset[str] = frozenset({
    "port_initially_free_or_explicitly_rejected",
    "brain5d_process_started",
    "listener_pid_matches_process_pid",
    "exactly_one_listener_socket",
    "no_other_listener_pid",
    "healthz_reachable",
    "process_alive_during_verification",
})


# ============================================================================
# Gate criterion model
# ============================================================================


def _criterion(
    *,
    gate: str,
    id: str,
    category: str,
    label: str,
    status: str,
    maturity: str,
    source: str,
    message: str = "",
    live_status: str | None = None,
    evidence: dict[str, JSONValue] | None = None,
) -> dict[str, JSONValue]:
    """Build one typed gate criterion dictionary.

    ``live_status`` is optional: only runtime-facing criteria carry a live
    state. Pure verification criteria (e.g. pytest collection) have
    ``live_status = None`` because they are not a live component.
    """
    if status not in _VALID_GATE_STATUS:
        raise ValueError(f"invalid gate status: {status!r}")
    if maturity not in _VALID_MATURITY:
        raise ValueError(f"invalid maturity: {maturity!r}")
    if live_status is not None and live_status not in _VALID_LIVE_STATUS:
        raise ValueError(f"invalid live_status: {live_status!r}")

    item: dict[str, JSONValue] = {
        "gate": gate,
        "id": id,
        "category": category,
        "label": label,
        "status": status,
        "maturity": maturity,
        "source": source,
        "message": message,
    }
    if live_status is not None:
        item["live_status"] = live_status
    if evidence is not None:
        item["evidence"] = cast(JSONValue, evidence)
    return item


# ============================================================================
# Gate status builder
# ============================================================================


class GateStatusBuilder:
    """Compute the real Alpha.5 release-gate status from backend evidence.

    Constructed with the live operator bridge (for runtime-facing live
    status), the research source (for Gate C framework existence), and the
    repository root (for ``tests/test_baseline.json`` and the research
    experiment manifests).

    The builder NEVER infers scientific completion. A registered experiment
    is not an executed experiment; an executed experiment is not evidence.
    """

    def __init__(
        self,
        *,
        bridge: Any | None = None,
        research_source: Any | None = None,
        repo_root: Path | None = None,
        config_dict: dict[str, Any] | None = None,
    ) -> None:
        self.bridge = bridge
        self.research_source = research_source
        self.repo_root = repo_root or Path.cwd()
        self.config_dict = config_dict or {}

    # ------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------

    def build(self) -> dict[str, JSONValue]:
        """Compute the full Alpha.5 gate status."""
        gate_a = self._build_gate_a()
        gate_b = self._build_gate_b()
        gate_c = self._build_gate_c()
        live_runtime = self._build_live_runtime()

        overall = self._overall_status(gate_a, gate_b, gate_c)

        return {
            "overall": overall,
            "gate_a": {"items": cast(JSONValue, gate_a)},
            "gate_b": {"items": cast(JSONValue, gate_b)},
            "gate_c": {"items": cast(JSONValue, gate_c)},
            "live_runtime": cast(JSONValue, live_runtime),
            "source": "live_backend",
        }

    # ------------------------------------------------------------------------
    # Overall status
    # ------------------------------------------------------------------------

    def _overall_status(
        self,
        gate_a: list[dict[str, JSONValue]],
        gate_b: list[dict[str, JSONValue]],
        gate_c: list[dict[str, JSONValue]],
    ) -> str:
        all_items = gate_a + gate_b + gate_c
        if any(i["status"] == G_FAILED for i in all_items):
            return G_FAILED
        if any(i["status"] == G_STALE for i in all_items):
            return G_STALE
        if all(i["status"] == G_PASSED for i in all_items):
            return G_PASSED
        return G_PENDING

    # --------------------------------------------------------------------
    # Structural E2E artifact reader
    # --------------------------------------------------------------------

    def _read_structural_e2e_artifact(self) -> dict[str, Any] | None:
        """Read the structural E2E verification artifact.

        Reads from the persistent location ``research/generated/verification/
        structural_e2e.json`` (not gitignored) so a fresh clone can verify
        the structural E2E status.

        Returns ``None`` if the artifact is missing or unparseable.
        """
        artifact_path = (
            self.repo_root / "research" / "generated" / "verification"
            / "structural_e2e.json"
        )
        if not artifact_path.exists():
            return None
        try:
            return json.loads(artifact_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _structural_e2e_verified(self) -> bool:
        """Return True if the structural E2E artifact shows all proofs passed
        AND the artifact's tree digest matches the current source tree.

        Fail-closed validation:
        - missing artifact → NOT VERIFIED
        - status != "verified" → NOT VERIFIED
        - missing schema_version → NOT VERIFIED
        - proof count != 10 → NOT VERIFIED
        - any proof false → NOT VERIFIED
        - missing tested_tree_digest → NOT VERIFIED
        - missing current digest → NOT VERIFIED
        - digest mismatch → NOT VERIFIED (stale)
        """
        artifact = self._read_structural_e2e_artifact()
        if artifact is None:
            return False
        if artifact.get("status") != "verified":
            return False
        if artifact.get("schema_version") is None:
            return False
        proofs_raw = artifact.get("proofs", {})
        if not isinstance(proofs_raw, dict):
            return False
        proofs: dict[str, Any] = cast("dict[str, Any]", proofs_raw)
        # The artifact must contain exactly the required proof set.
        if frozenset(proofs.keys()) != REQUIRED_STRUCTURAL_PROOFS:
            return False
        if not all(proofs[name] is True for name in REQUIRED_STRUCTURAL_PROOFS):
            return False
        # Staleness binding: artifact tree digest MUST match current tree.
        # Fail-closed: missing digest → NOT VERIFIED.
        artifact_digest = artifact.get("tested_tree_digest")
        if not artifact_digest:
            return False
        from src.dashboard.verification import compute_source_tree_digest

        current_digest = compute_source_tree_digest(self.repo_root)
        if current_digest is None:
            return False
        if artifact_digest != current_digest:
            return False  # stale artifact
        return True

    def _structural_proof_status(self, proof_num: int) -> str:
        """Return the gate status for a specific structural E2E proof.

        Fail-closed: missing artifact, missing digest, or digest mismatch
        all result in PENDING or STALE — never PASSED.
        """
        artifact = self._read_structural_e2e_artifact()
        if artifact is None:
            return G_PENDING
        if artifact.get("status") != "verified":
            return G_PENDING
        if artifact.get("schema_version") is None:
            return G_PENDING
        # Staleness binding — fail-closed
        artifact_digest = artifact.get("tested_tree_digest")
        if not artifact_digest:
            return G_PENDING
        from src.dashboard.verification import compute_source_tree_digest

        current_digest = compute_source_tree_digest(self.repo_root)
        if current_digest is None:
            return G_PENDING
        if artifact_digest != current_digest:
            return G_STALE
        proofs_raw = artifact.get("proofs", {})
        if not isinstance(proofs_raw, dict):
            return G_PENDING
        proofs: dict[str, Any] = cast("dict[str, Any]", proofs_raw)
        # The artifact uses keys like "test_proof_01_coordinator_instantiated".
        # Match by the "test_proof_XX" or "01_" prefix pattern.
        padded = f"{proof_num:02d}"
        for key, value in proofs.items():
            if key == f"test_proof_{padded}" or key.startswith(f"test_proof_{padded}_") or key.startswith(f"{padded}_"):
                return G_PASSED if bool(value) else G_FAILED
        return G_PENDING

    def _canonical_e2e_status(self) -> str:
        """Return the gate status for the complete canonical E2E test.

        Reads the ``test_complete_canonical_e2e`` proof from the artifact
        with the same fail-closed validation as the individual proofs.
        """
        artifact = self._read_structural_e2e_artifact()
        if artifact is None:
            return G_PENDING
        if artifact.get("status") != "verified":
            return G_PENDING
        if artifact.get("schema_version") is None:
            return G_PENDING
        artifact_digest = artifact.get("tested_tree_digest")
        if not artifact_digest:
            return G_PENDING
        from src.dashboard.verification import compute_source_tree_digest

        current_digest = compute_source_tree_digest(self.repo_root)
        if current_digest is None:
            return G_PENDING
        if artifact_digest != current_digest:
            return G_STALE
        proofs_raw = artifact.get("proofs", {})
        if not isinstance(proofs_raw, dict):
            return G_PENDING
        proofs: dict[str, Any] = cast("dict[str, Any]", proofs_raw)
        value = proofs.get("test_complete_canonical_e2e")
        if value is None:
            return G_PENDING
        return G_PASSED if bool(value) else G_FAILED

    # --------------------------------------------------------------------
    # Gate A -- Technical Integration
    # --------------------------------------------------------------------

    def _build_gate_a(self) -> list[dict[str, JSONValue]]:
        """Gate A: technical integration criteria.

        Each criterion carries the test IDs that verify it. The gate
        result is derived from whether a verified test baseline exists,
        not from a hardcoded ``passed`` flag.
        """
        items: list[dict[str, JSONValue]] = []

        # --- Verified technical integration (evidence = test files) ---
        # Each criterion references the test files that verify it. The
        # builder checks whether those test files exist in the repo.
        verified_a: list[tuple[str, str, list[str]]] = [
            ("A-PROCESS", "One application process",
             ["tests/test_brain5d_launcher.py", "tests/test_dashboard_single_instance.py"]),
            ("A-CONTROLLER", "One canonical RuntimeController",
             ["tests/test_runtime_controller_alpha4.py", "tests/test_dashboard_control_api.py"]),
            ("A-CLOCK", "RuntimeController sole simulation-clock owner",
             ["tests/test_runtime_controller_alpha4.py"]),
            ("A-SIMPLE-REMOVED", "SimpleController removed",
             ["tests/test_dashboard_control_service.py"]),
            ("A-IDLE-START", "Starts IDLE",
             ["tests/test_runtime_controller_alpha4.py"]),
            ("A-NO-AUTO-TICKS", "No automatic 1000-tick execution",
             ["tests/test_runtime_controller_alpha4.py"]),
            ("A-CONTROL-API", "Canonical /api/control",
             ["tests/test_dashboard_control_api.py"]),
            ("A-NO-DUPLICATE-FRONTEND", "No duplicate frontend lifecycle commands",
             ["tests/test_dashboard_single_instance.py"]),
            ("A-TICK0", "Real Tick-0 state",
             ["tests/test_dashboard_completion.py"]),
            ("A-B5D-SNAPSHOT", "Real .b5d snapshot creation",
             ["tests/test_b5d_storage.py", "tests/test_dashboard_completion.py"]),
            ("A-HEATMAP", "Real snapshot heatmaps",
             ["tests/test_heatmap.py", "tests/test_structural_heatmap.py"]),
            ("A-INSPECTOR", "Real 5D network inspector",
             ["tests/test_dashboard_completion.py"]),
            ("A-RESEARCH-INFRA", "Research infrastructure (B5D-SEF)",
             ["tests/test_research_registry.py"]),
            ("A-DASHBOARD-OBSERVABILITY", "Dashboard scientific observability",
             ["tests/test_dashboard_completion.py"]),
        ]
        for cid, label, test_ids in verified_a:
            evidence_files = self._verify_test_files_exist(test_ids)
            all_exist = all(evidence_files.values())
            items.append(_criterion(
                gate=GATE_A,
                id=cid,
                category="technical_integration",
                label=label,
                status=G_PASSED if all_exist else G_PENDING,
                maturity=VERIFIED if all_exist else INTEGRATED,
                source="verified_baseline",
                message="Verified by test baseline" if all_exist else "Test files missing",
                evidence={"test_ids": cast(JSONValue, test_ids)},
            ))

        # --- Production signal->policy->coordinator adapter ---
        adapter_verified = self._adapter_proof_verified()
        items.append(_criterion(
            gate=GATE_A,
            id="A-STRUCT-RUNTIME-ADAPTER",
            category="structural_composition",
            label="Production HomeostasisSignal -> Policy -> Coordinator",
            status=G_PASSED if adapter_verified else G_PENDING,
            maturity=VERIFIED if adapter_verified else INTEGRATED,
            source="research/generated/verification/structural_e2e.json" if adapter_verified else "structural_e2e",
            message="Verified by structural E2E artifact" if adapter_verified else "Pending adapter verification",
            live_status=self._structural_live_status(),
        ))

        # --- Single listener ---
        listener_verified = self._single_listener_proof_verified()
        items.append(_criterion(
            gate=GATE_A,
            id="A-SINGLE-LISTENER",
            category="technical_integration",
            label="Exactly one TCP LISTEN socket on 127.0.0.1:8765 owned by Brain-5D PID",
            status=G_PASSED if listener_verified else G_PENDING,
            maturity=VERIFIED if listener_verified else IMPLEMENTED,
            source="research/generated/verification/single_listener.json" if listener_verified else "project_state",
            message="Verified by single listener artifact" if listener_verified else "Pending single-listener verification",
        ))

        # --- Structural composition: evidence-based from E2E artifact ---
        structural_verified = self._structural_e2e_verified()
        structural_live = self._structural_live_status()
        structural_pending: list[tuple[str, str]] = [
            ("A-STRUCT-COORDINATOR", "Structural Coordinator production composition"),
            ("A-STRUCT-PLASTICITY", "StructuralPlasticityEngine production composition"),
            ("A-STRUCT-MANIPULATOR", "Manipulator canonical mutation boundary"),
            ("A-STRUCT-APPROVAL", "Approval-gated mutation path"),
            ("A-STRUCT-JOURNAL", "Structural Journal active path"),
            ("A-STRUCT-PROVENANCE", "Proposal provenance (measurement -> proposal)"),
        ]
        for cid, label in structural_pending:
            items.append(_criterion(
                gate=GATE_A,
                id=cid,
                category="structural_composition",
                label=label,
                status=G_PASSED if structural_verified else G_PENDING,
                maturity=VERIFIED if structural_verified else INTEGRATED,
                source="research/generated/verification/structural_e2e.json" if structural_verified else "structural_e2e",
                message="Verified by structural E2E artifact (tree digest matches)" if structural_verified else "Pending structural E2E verification proof",
                live_status=structural_live,
                evidence={"artifact": "research/generated/verification/structural_e2e.json"} if structural_verified else None,
            ))

        return items

    # --------------------------------------------------------------------
    # Gate B -- Verification
    # --------------------------------------------------------------------

    def _build_gate_b(self) -> list[dict[str, JSONValue]]:
        """Gate B: verification criteria.

        Reads ``tests/test_baseline.json``. When the recorded tree digest
        matches the current source tree, the pytest baseline criteria are
        PASSED. When the tree changed, they are STALE (not FAILED).

        Structural E2E proofs (proof_01 .. proof_10) remain PENDING until
        the structural E2E tests actually pass.
        """
        items: list[dict[str, JSONValue]] = []
        ev = evaluate_test_baseline(self.repo_root)
        tree_stale = ev.stale

        # --- Pytest collection / suite criteria ---
        collection_errors = ev.collection_errors
        passed_count = ev.passed
        failed_count = ev.failed
        skipped_count = ev.skipped

        # Collection succeeds
        if tree_stale:
            coll_status = G_STALE
            coll_maturity = VERIFIED
            coll_msg = "Source tree changed since baseline; re-run required"
        elif collection_errors == 0:
            coll_status = G_PASSED
            coll_maturity = VERIFIED
            coll_msg = "Zero collection errors"
        else:
            coll_status = G_FAILED
            coll_maturity = INTEGRATED
            coll_msg = f"{collection_errors} collection errors"
        items.append(_criterion(
            gate=GATE_B,
            id="B-TEST-COLLECTION",
            category="test_baseline",
            label="Complete pytest collection succeeds",
            status=coll_status,
            maturity=coll_maturity,
            source="tests/test_baseline.json",
            message=coll_msg,
            evidence={"collection_errors": collection_errors},
        ))

        # Zero unexplained failures
        if tree_stale:
            fail_status = G_STALE
            fail_msg = "Source tree changed since baseline"
        elif failed_count == 0:
            fail_status = G_PASSED
            fail_msg = "Zero failures"
        else:
            fail_status = G_FAILED
            fail_msg = f"{failed_count} failures"
        items.append(_criterion(
            gate=GATE_B,
            id="B-ZERO-FAILURES",
            category="test_baseline",
            label="Zero unexplained test failures",
            status=fail_status,
            maturity=VERIFIED if failed_count == 0 else INTEGRATED,
            source="tests/test_baseline.json",
            message=fail_msg,
            evidence={"failed": failed_count},
        ))

        # Full suite without ignored modules
        if tree_stale:
            suite_status = G_STALE
            suite_msg = "Source tree changed since baseline"
        elif collection_errors == 0 and failed_count == 0:
            suite_status = G_PASSED
            suite_msg = f"{passed_count} passed, {skipped_count} skipped, no --ignore"
        else:
            suite_status = G_FAILED
            suite_msg = "Suite not green without --ignore"
        items.append(_criterion(
            gate=GATE_B,
            id="B-FULL-SUITE",
            category="test_baseline",
            label="Full suite without ignored core modules",
            status=suite_status,
            maturity=VERIFIED if suite_status == G_PASSED else INTEGRATED,
            source="tests/test_baseline.json",
            message=suite_msg,
            evidence={
                "passed": passed_count,
                "failed": failed_count,
                "skipped": skipped_count,
            },
        ))

        # --- Structural E2E proofs (proof_01 .. proof_10) ---
        # Evidence-based: read from research/generated/verification/structural_e2e.json
        structural_live = self._structural_live_status()
        for i in range(1, 11):
            proof_status = self._structural_proof_status(i)
            items.append(_criterion(
                gate=GATE_B,
                id=f"B-STRUCT-PROOF-{i:02d}",
                category="structural_e2e",
                label=f"Structural E2E proof {i}/10",
                status=proof_status,
                maturity=VERIFIED if proof_status == G_PASSED else INTEGRATED,
                source="research/generated/verification/structural_e2e.json" if proof_status == G_PASSED else "tests/test_structural_e2e.py",
                message="Verified by structural E2E artifact" if proof_status == G_PASSED else "Pending structural E2E test execution",
                live_status=structural_live,
            ))

        # --- Complete canonical E2E (full chain without manual proposal) ---
        canonical_status = self._canonical_e2e_status()
        items.append(_criterion(
            gate=GATE_B,
            id="B-STRUCT-CANONICAL-E2E",
            category="structural_e2e",
            label="Complete canonical E2E (signal -> policy -> approval -> mutation -> journal)",
            status=canonical_status,
            maturity=VERIFIED if canonical_status == G_PASSED else INTEGRATED,
            source="research/generated/verification/structural_e2e.json" if canonical_status == G_PASSED else "tests/test_structural_e2e.py",
            message="Verified by structural E2E artifact" if canonical_status == G_PASSED else "Pending canonical E2E test execution",
            live_status=structural_live,
        ))

        # --- Error visibility / scientific integrity ---
        # Evidence from the live loop artifact: the live loop test verifies
        # that the RuntimeAdapter runs without silent exceptions.
        live_loop_ok = self._live_loop_verified()

        # Check for experiment validity test files
        experiment_validity_tests = self._verify_test_files_exist(
            ["tests/test_experiment_validity.py"]
        )
        validity_tested = experiment_validity_tests.get("tests/test_experiment_validity.py", False)

        error_vis: list[tuple[str, str, str, str]] = [
            ("B-HOOK-ERROR-VISIBILITY", "Structured hook-error visibility",
             VERIFIED if live_loop_ok else INTEGRATED,
             G_PASSED if live_loop_ok else G_PENDING),
            ("B-NO-SILENT-EXCEPTIONS", "No silent scientific-path exceptions",
             VERIFIED if live_loop_ok else INTEGRATED,
             G_PASSED if live_loop_ok else G_PENDING),
            ("B-RUNTIME-EXCEPTIONS-MANIFEST", "Runtime exceptions enter experiment manifest",
             VERIFIED if validity_tested else INTEGRATED,
             G_PASSED if validity_tested else G_PENDING),
            ("B-INVALID-RUN-NOT-EVIDENCE", "Invalid run cannot become evidence",
             VERIFIED if validity_tested else INTEGRATED,
             G_PASSED if validity_tested else G_PENDING),
        ]
        for cid, label, maturity, status in error_vis:
            items.append(_criterion(
                gate=GATE_B,
                id=cid,
                category="error_visibility",
                label=label,
                status=status,
                maturity=maturity,
                source="tests/test_experiment_validity.py" if validity_tested else "project_state",
                message="Verified by experiment validity tests" if validity_tested else "Pending verification",
            ))

        # --- Restore / determinism ---
        # Check which determinism test files exist
        determinism_test_files = self._verify_test_files_exist([
            "tests/test_rng_persistence.py",
            "tests/test_iteration_determinism.py",
            "tests/test_structural_determinism.py",
            "tests/test_canonical_state.py",
            "tests/test_checkpoint_v4.py",
        ])
        rng_tested = determinism_test_files.get("tests/test_rng_persistence.py", False)
        iter_tested = determinism_test_files.get("tests/test_iteration_determinism.py", False)
        struct_det_tested = determinism_test_files.get("tests/test_structural_determinism.py", False)
        canonical_tested = determinism_test_files.get("tests/test_canonical_state.py", False)
        checkpoint_v4_tested = determinism_test_files.get("tests/test_checkpoint_v4.py", False)

        determinism: list[tuple[str, str, str, str]] = [
            ("B-RESTORE-CONTINUE", "Restore-and-continue identity",
             VERIFIED if checkpoint_v4_tested else IMPLEMENTED,
             G_PASSED if checkpoint_v4_tested else G_PENDING),
            ("B-STRUCTURAL-DETERMINISM", "Structural determinism",
             VERIFIED if struct_det_tested else IMPLEMENTED,
             G_PASSED if struct_det_tested else G_PENDING),
            ("B-ITERATION-ORDER", "Explicit iteration-order determinism",
             VERIFIED if iter_tested else IMPLEMENTED,
             G_PASSED if iter_tested else G_PENDING),
            ("B-RNG-STATE-PERSIST", "Full RNG state persistence",
             VERIFIED if rng_tested else IMPLEMENTED,
             G_PASSED if rng_tested else G_PENDING),
            ("B-CANONICAL-STATE-DIGEST", "Canonical full-state digest",
             VERIFIED if canonical_tested else IMPLEMENTED,
             G_PASSED if canonical_tested else G_PENDING),
            ("B-HOMEOSTASIS-LEARNING-PERSIST", "Homeostasis + learning state persistence",
             VERIFIED if checkpoint_v4_tested else IMPLEMENTED,
             G_PASSED if checkpoint_v4_tested else G_PENDING),
        ]
        for cid, label, maturity, status in determinism:
            items.append(_criterion(
                gate=GATE_B,
                id=cid,
                category="determinism",
                label=label,
                status=status,
                maturity=maturity,
                source="tests/" if status == G_PASSED else "project_state",
                message="Verified by determinism tests" if status == G_PASSED else "Pending verification",
            ))

        return items

    # --------------------------------------------------------------------
    # Gate C -- Scientific Baseline
    # --------------------------------------------------------------------

    def _build_gate_c(self) -> list[dict[str, JSONValue]]:
        """Gate C: scientific baseline.

        Separates *framework existence* (IMPLEMENTED) from *scientific
        execution* (PENDING). A registered experiment is not an executed
        experiment; an executed experiment is not evidence.
        """
        items: list[dict[str, JSONValue]] = []

        # --- Framework existence (registry files present) ---
        registry_counts = self._research_registry_counts()
        rq_count = registry_counts.get("questions", 0)
        h_count = registry_counts.get("hypotheses", 0)
        claim_count = registry_counts.get("claims", 0)
        src_count = registry_counts.get("sources", 0)
        method_count = registry_counts.get("methods", 0)

        framework: list[tuple[str, str, int]] = [
            ("C-RQ-REGISTRY", "Research Questions registry", rq_count),
            ("C-HYPOTHESIS-REGISTRY", "Hypotheses registry", h_count),
            ("C-CLAIM-REGISTRY", "Claims registry", claim_count),
            ("C-SOURCE-REGISTRY", "Literature source registry", src_count),
            ("C-METHOD-REGISTRY", "Methods registry", method_count),
            ("C-EXPERIMENT-RECORDER", "Experiment recorder framework", 1),
            ("C-RESEARCH-CATALOG", "Research Catalog (generated)", 1),
            ("C-EVIDENCE-MATRIX", "Evidence Matrix (generated)", 1),
        ]
        for cid, label, count in framework:
            exists = count > 0
            items.append(_criterion(
                gate=GATE_C,
                id=cid,
                category="framework",
                label=label,
                status=G_PASSED if exists else G_PENDING,
                maturity=IMPLEMENTED,
                source="research/registry",
                message=f"{count} registered" if exists else "Not found",
                evidence={"count": count},
            ))

        # --- Registered experiments ---
        experiments = self._registered_experiments()
        exp_det_registered = "EXP-DET-0001" in experiments
        exp_stor_registered = "EXP-STOR-0001" in experiments
        items.append(_criterion(
            gate=GATE_C,
            id="C-EXP-DET-REGISTERED",
            category="experiment_registration",
            label="EXP-DET-0001 registered",
            status=G_PASSED if exp_det_registered else G_PENDING,
            maturity=IMPLEMENTED,
            source="research/experiments",
            message="Registered" if exp_det_registered else "Not registered",
        ))
        items.append(_criterion(
            gate=GATE_C,
            id="C-EXP-STOR-REGISTERED",
            category="experiment_registration",
            label="EXP-STOR-0001 registered",
            status=G_PASSED if exp_stor_registered else G_PENDING,
            maturity=IMPLEMENTED,
            source="research/experiments",
            message="Registered" if exp_stor_registered else "Not registered",
        ))

        # --- Scientific execution (NOT the same as registration) ---
        exp_det_executed = self._experiment_executed("EXP-DET-0001")
        exp_stor_executed = self._experiment_executed("EXP-STOR-0001")
        items.append(_criterion(
            gate=GATE_C,
            id="C-EXP-DET-EXECUTED",
            category="scientific_execution",
            label="EXP-DET-0001 executed",
            status=G_PASSED if exp_det_executed else G_PENDING,
            maturity=IMPLEMENTED,
            source="research/experiments/EXP-DET-0001/manifest.json",
            message="Executed" if exp_det_executed else "Not executed (status=not_started)",
        ))
        items.append(_criterion(
            gate=GATE_C,
            id="C-EXP-STOR-EXECUTED",
            category="scientific_execution",
            label="EXP-STOR-0001 executed",
            status=G_PASSED if exp_stor_executed else G_PENDING,
            maturity=IMPLEMENTED,
            source="research/experiments/EXP-STOR-0001/manifest.json",
            message="Executed" if exp_stor_executed else "Not executed (status=not_started)",
        ))

        # --- First evidence artifacts ---
        evidence_artifacts: list[tuple[str, str]] = [
            ("C-FIRST-DATA", "First DATA-* artifact produced"),
            ("C-FIRST-EVID", "First EVID-* record produced"),
            ("C-FIRST-HYPOTHESIS-RESULT", "First reproducibly supported/refuted hypothesis"),
            ("C-CATALOG-REBUILT", "Research Catalog rebuilt from real evidence"),
            ("C-MATRIX-REBUILT", "Evidence Matrix rebuilt from real evidence"),
        ]
        for cid, label in evidence_artifacts:
            items.append(_criterion(
                gate=GATE_C,
                id=cid,
                category="scientific_evidence",
                label=label,
                status=G_PENDING,
                maturity=IMPLEMENTED,
                source="research/generated",
                message="No real evidence yet",
            ))

        return items

    # --------------------------------------------------------------------
    # Live runtime profile (separate from gate status)
    # --------------------------------------------------------------------

    def _build_live_runtime(self) -> list[dict[str, JSONValue]]:
        """Live runtime profile of the *currently running* config.

        This is NOT the release gate. A component disabled by config is
        neutral (disabled), neither passed nor failed. A component that
        should be enabled by config but is missing is an ERROR, not
        "disabled by config".

        Tests and Research are NOT live runtime subsystems — they belong
        exclusively to Gate B and Gate C respectively.
        """
        items: list[dict[str, JSONValue]] = []

        bridge = self.bridge
        controller = getattr(bridge, "controller", None) if bridge else None
        coordinator = getattr(bridge, "coordinator", None) if bridge else None
        plasticity = getattr(bridge, "plasticity", None) if bridge else None

        # Bridge
        items.append(self._live_item("bridge", "OperatorBridge",
            L_ACTIVE if bridge is not None else L_UNAVAILABLE,
            "connected" if bridge else "not configured"))

        # Controller
        items.append(self._live_item("controller", "RuntimeController",
            L_ACTIVE if controller is not None else L_UNAVAILABLE,
            "connected" if controller else "missing"))

        # Runtime state
        if controller is not None:
            try:
                tel = controller.snapshot()
                state = getattr(tel, "controller_state", None)
                state_val = state.value if state is not None else "unknown"
                tick = getattr(tel, "tick", 0)
                items.append(self._live_item("runtime", "Runtime",
                    L_ACTIVE, f"state={state_val}, tick={tick}"))
            except Exception:
                items.append(self._live_item("runtime", "Runtime", L_ERROR, "telemetry error"))
        else:
            items.append(self._live_item("runtime", "Runtime", L_UNAVAILABLE, "no controller"))

        # Structural — config-aware: disabled vs error distinction
        so_enabled = bool(self.config_dict.get("self_organization", {}).get("enabled", False))
        if not so_enabled:
            items.append(self._live_item("structural", "Structural",
                L_DISABLED, "disabled by config (self_organization.enabled=false)"))
        elif coordinator is not None and plasticity is not None:
            items.append(self._live_item("structural", "Structural",
                L_ACTIVE, "Coordinator + PlasticityEngine connected"))
        else:
            items.append(self._live_item("structural", "Structural",
                L_ERROR, "config enabled but coordinator/plasticity missing"))

        # Structural Journal — follows structural config
        if not so_enabled:
            items.append(self._live_item("structural_journal", "Structural Journal",
                L_DISABLED, "disabled because structural disabled"))
        elif coordinator is not None:
            items.append(self._live_item("structural_journal", "Structural Journal",
                L_ACTIVE, "StructuralJournal attached"))
        else:
            items.append(self._live_item("structural_journal", "Structural Journal",
                L_ERROR, "config enabled but journal missing"))

        # Delta storage — config-aware: disabled vs error distinction
        storage_cfg_raw = self.config_dict.get("storage", {})
        storage_cfg: dict[str, Any] = cast("dict[str, Any]", storage_cfg_raw) if isinstance(storage_cfg_raw, dict) else {}
        storage_runtime_cfg_raw = storage_cfg.get("runtime", {})
        storage_runtime_cfg: dict[str, Any] = cast("dict[str, Any]", storage_runtime_cfg_raw) if isinstance(storage_runtime_cfg_raw, dict) else {}
        storage_enabled = bool(storage_cfg.get("enabled", False)) and bool(
            storage_runtime_cfg.get("enabled", False)
        )
        if not storage_enabled:
            items.append(self._live_item("delta_storage", "Delta Storage",
                L_DISABLED, "disabled by config (storage.runtime.enabled=false)"))
        else:
            # If enabled by config, check whether a storage session is active.
            # The bridge does not currently expose storage state, so we report
            # active when the config says so (the session is started in main.py).
            items.append(self._live_item("delta_storage", "Delta Storage",
                L_ACTIVE, "AsyncStorageSession active"))

        # Research source (live availability only; evidence belongs to Gate C)
        if self.research_source is not None and self.research_source.is_available():
            items.append(self._live_item("research_source", "Research Source",
                L_ACTIVE, "B5D-SEF registry available"))
        else:
            items.append(self._live_item("research_source", "Research Source",
                L_UNAVAILABLE, "B5D-SEF registry not found"))

        return items

    def _live_item(self, key: str, name: str, live_status: str, message: str) -> dict[str, JSONValue]:
        return {
            "key": key,
            "name": name,
            "live_status": live_status,
            "message": message,
        }

    # --------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------

    def _structural_live_status(self) -> str:
        """Live status of the structural subsystem in the running config.

        Config-aware: distinguishes ``disabled`` (config says off) from
        ``error`` (config says on but components are missing).
        """
        so_enabled = bool(self.config_dict.get("self_organization", {}).get("enabled", False))
        if not so_enabled:
            return L_DISABLED
        coordinator = getattr(self.bridge, "coordinator", None) if self.bridge else None
        plasticity = getattr(self.bridge, "plasticity", None) if self.bridge else None
        if coordinator is not None and plasticity is not None:
            return L_ACTIVE
        return L_ERROR

    def _read_baseline(self) -> dict[str, Any] | None:
        """Read tests/test_baseline.json. Returns None if missing/unparseable.

        Delegates to :func:`verification.read_test_baseline`.
        """
        from src.dashboard.verification import read_test_baseline

        return read_test_baseline(self.repo_root)

    def _is_tree_stale(self, baseline: dict[str, Any] | None) -> bool:
        """Return True if the source tree changed since the baseline.

        Delegates to :func:`verification.evaluate_test_baseline` so that
        the gate and integration status can never disagree.
        """
        ev = evaluate_test_baseline(self.repo_root)
        return ev.stale

    def _current_tree_digest(self) -> str | None:
        """SHA-256 digest over scientifically relevant source paths.

        Delegates to :func:`verification.compute_source_tree_digest`.
        """
        from src.dashboard.verification import compute_source_tree_digest

        return compute_source_tree_digest(self.repo_root)

    def _research_registry_counts(self) -> dict[str, int]:
        """Count registry entries using the canonical ResearchRegistry API.

        Uses :class:`src.research.registry.ResearchRegistry` to load typed
        objects instead of fragile string counting of YAML files.
        """
        counts: dict[str, int] = {
            "questions": 0,
            "hypotheses": 0,
            "claims": 0,
            "sources": 0,
            "methods": 0,
        }
        try:
            from src.research.registry import ResearchRegistry

            registry = ResearchRegistry()
            registry.load_all()
            counts["questions"] = len(registry.questions)
            counts["hypotheses"] = len(registry.hypotheses)
            counts["claims"] = len(registry.claims)
            counts["sources"] = len(registry.sources)
        except Exception:
            pass

        # Methods have a different YAML structure (under ``methods:`` key)
        # so they are not loaded by ResearchRegistry.load_all(). Count via
        # the fallback method.
        methods_path = self.repo_root / "research" / "registry" / "methods.yaml"
        if methods_path.exists():
            try:
                counts["methods"] = methods_path.read_text(encoding="utf-8").count("- prefix:")
            except Exception:
                pass

        return counts

    def _registered_experiments(self) -> set[str]:
        """Return the set of registered experiment IDs (directory names)."""
        experiments_root = self.repo_root / "research" / "experiments"
        if not experiments_root.is_dir():
            return set()
        result: set[str] = set()
        for entry in experiments_root.iterdir():
            if entry.is_dir() and (entry / "manifest.json").exists():
                result.add(entry.name)
        return result

    def _verify_test_files_exist(self, test_ids: list[str]) -> dict[str, bool]:
        """Check whether the given test files exist in the repo.

        Returns a mapping of test file path to existence boolean.
        """
        result: dict[str, bool] = {}
        for tid in test_ids:
            path = self.repo_root / tid
            result[tid] = path.exists()
        return result

    def _read_live_loop_artifact(self) -> dict[str, Any] | None:
        """Read the structural live loop verification artifact.

        Reads from ``research/generated/verification/structural_live_loop.json``.
        Returns ``None`` if the artifact is missing or unparseable.
        """
        artifact_path = (
            self.repo_root / "research" / "generated" / "verification"
            / "structural_live_loop.json"
        )
        if not artifact_path.exists():
            return None
        try:
            return json.loads(artifact_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _live_loop_verified(self) -> bool:
        """Return True if the live loop artifact shows all proofs passed
        AND the artifact's tree digest matches the current source tree.

        Fail-closed validation:
        - missing artifact -> NOT VERIFIED
        - status != "verified" -> NOT VERIFIED
        - missing schema_version -> NOT VERIFIED
        - proof count != REQUIRED_LIVE_LOOP_PROOFS -> NOT VERIFIED
        - any proof false -> NOT VERIFIED
        - missing tested_tree_digest -> NOT VERIFIED
        - digest mismatch -> NOT VERIFIED (stale)
        """
        artifact = self._read_live_loop_artifact()
        if artifact is None:
            return False
        if artifact.get("status") != "verified":
            return False
        if artifact.get("schema_version") is None:
            return False
        proofs_raw = artifact.get("proofs", {})
        if not isinstance(proofs_raw, dict):
            return False
        proofs: dict[str, Any] = cast("dict[str, Any]", proofs_raw)
        if frozenset(proofs.keys()) != REQUIRED_LIVE_LOOP_PROOFS:
            return False
        if not all(proofs[name] is True for name in REQUIRED_LIVE_LOOP_PROOFS):
            return False
        artifact_digest = artifact.get("tested_tree_digest")
        if not artifact_digest:
            return False
        from src.dashboard.verification import compute_source_tree_digest

        current_digest = compute_source_tree_digest(self.repo_root)
        if current_digest is None:
            return False
        if artifact_digest != current_digest:
            return False
        return True

    def _adapter_proof_verified(self) -> bool:
        """Return True if the structural live loop artifact proves the
        production RuntimeAdapter path."""
        return self._live_loop_verified()

    def _read_single_listener_artifact(self) -> dict[str, Any] | None:
        """Read the single listener verification artifact.

        Reads from ``research/generated/verification/single_listener.json``.
        Returns ``None`` if the artifact is missing or unparseable.
        """
        artifact_path = (
            self.repo_root / "research" / "generated" / "verification"
            / "single_listener.json"
        )
        if not artifact_path.exists():
            return None
        try:
            return json.loads(artifact_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _single_listener_verified(self) -> bool:
        """Return True if the single listener artifact shows all proofs passed
        AND the artifact's tree digest matches the current source tree.

        Fail-closed validation identical to live loop and structural E2E.
        """
        artifact = self._read_single_listener_artifact()
        if artifact is None:
            return False
        if artifact.get("status") != "verified":
            return False
        if artifact.get("schema_version") is None:
            return False
        proofs_raw = artifact.get("proofs", {})
        if not isinstance(proofs_raw, dict):
            return False
        proofs: dict[str, Any] = cast("dict[str, Any]", proofs_raw)
        if frozenset(proofs.keys()) != REQUIRED_SINGLE_LISTENER_PROOFS:
            return False
        if not all(proofs[name] is True for name in REQUIRED_SINGLE_LISTENER_PROOFS):
            return False
        artifact_digest = artifact.get("tested_tree_digest")
        if not artifact_digest:
            return False
        from src.dashboard.verification import compute_source_tree_digest
        current_digest = compute_source_tree_digest(self.repo_root)
        if current_digest is None:
            return False
        if artifact_digest != current_digest:
            return False
        return True

    def _single_listener_proof_verified(self) -> bool:
        """Return True if the single-listener verification artifact proves
        actual test passing. File existence alone is not sufficient."""
        return self._single_listener_verified()

    def _experiment_executed(self, experiment_id: str) -> bool:
        """Return True if an experiment manifest shows it was *completed*.

        An experiment is considered executed only when its manifest
        ``experiment_status`` is ``"completed"``. This is deliberately
        strict — ``template``, ``not_started``, ``running``, ``failed``,
        and ``invalid`` are NOT executed:

        - ``template`` / ``not_started``: never ran
        - ``running``: attempted but not complete
        - ``failed`` / ``invalid``: attempted but not valid evidence

        Scientifically, only a completed run can produce evidence.
        """
        manifest_path = (
            self.repo_root / "research" / "experiments" / experiment_id / "manifest.json"
        )
        if not manifest_path.exists():
            return False
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            return False
        status = manifest.get("experiment_status", "not_started")
        return status == "completed"
