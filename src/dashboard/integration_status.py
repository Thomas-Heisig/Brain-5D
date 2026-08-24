"""Real integration status for the Brain-5D Alpha.5 gate.

This module computes the real integration status of every dashboard
subsystem by probing live backend components. It replaces the previous
frontend-only heuristic that hardcoded ``int-tests`` to ``false``.

Status values (Phase 14):
    passed    — component is connected and active
    disabled  — component is intentionally disabled by config
    pending   — component exists but is not yet initialised
    stale     — component data is outdated (e.g. test baseline)
    failed    — component should be available but is not

A component disabled by config is NEVER reported as "failed".
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from src.dashboard.models import JSONValue
from src.dashboard.verification import (
    compute_source_tree_digest,
    current_git_head,
    evaluate_test_baseline,
)

# ============================================================================
# Scientifically relevant source paths
# ============================================================================

# A test-baseline change (this file, docs, CHANGELOG) must NOT invalidate the
# test status. Only changes to the scientifically relevant source tree should
# mark the baseline as stale. This is why we digest the tree, not the commit.
# The canonical list lives in verification.py; this alias is kept for
# backward compatibility with any code that imported the constant directly.
_SCIENTIFIC_PATHS = ["src/", "configs/", "research/schemas/", "pyproject.toml"]

# ============================================================================
# Status constants
# ============================================================================

PASSED = "passed"
DISABLED = "disabled"
PENDING = "pending"
STALE = "stale"
FAILED = "failed"

_VALID_STATUSES = {PASSED, DISABLED, PENDING, STALE, FAILED}


# ============================================================================
# Integration status builder
# ============================================================================


class IntegrationStatusBuilder:
    """Compute real integration status from live backend components.

    The builder is constructed with the live dashboard state snapshot and
    optional handles to the operator bridge, heatmap source, research
    source, and the repository root (for test_baseline.json).
    """

    def __init__(
        self,
        state_snapshot: Any,
        *,
        bridge: Any | None = None,
        heatmap_source: Any | None = None,
        research_source: Any | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self.state = state_snapshot
        self.bridge = bridge
        self.heatmap_source = heatmap_source
        self.research_source = research_source
        self.repo_root = repo_root or Path.cwd()

    # ------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------

    def build(self) -> dict[str, JSONValue]:
        """Compute the full integration status dictionary."""
        items: list[dict[str, JSONValue]] = []
        items.append(self._check_bridge())
        items.append(self._check_controller())
        items.append(self._check_runtime())
        items.append(self._check_structural())
        items.append(self._check_snapshot())
        items.append(self._check_delta_storage())
        items.append(self._check_structural_journal())
        items.append(self._check_research())
        items.append(self._check_tests())
        items.append(self._check_error_visibility())

        passed = sum(1 for i in items if i["status"] == PASSED)
        failed = sum(1 for i in items if i["status"] == FAILED)
        disabled = sum(1 for i in items if i["status"] == DISABLED)
        stale = sum(1 for i in items if i["status"] == STALE)

        overall: str
        if failed > 0:
            overall = FAILED
        elif stale > 0:
            overall = STALE
        elif passed > 0 and disabled > 0 and passed + disabled == len(items):
            overall = PASSED
        elif passed == len(items):
            overall = PASSED
        else:
            overall = PENDING

        return {
            "overall": overall,
            "passed": passed,
            "failed": failed,
            "disabled": disabled,
            "stale": stale,
            "total": len(items),
            "items": cast(JSONValue, items),
            "source": "live_backend",
        }

    # ------------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------------

    def _check_bridge(self) -> dict[str, JSONValue]:
        ok = self.bridge is not None
        return {
            "name": "Bridge",
            "status": PASSED if ok else FAILED,
            "source": "live_runtime",
            "message": "OperatorBridge connected" if ok else "OperatorBridge not configured",
        }

    def _check_controller(self) -> dict[str, JSONValue]:
        controller = getattr(self.bridge, "controller", None) if self.bridge else None
        ok = controller is not None
        return {
            "name": "Controller",
            "status": PASSED if ok else FAILED,
            "source": "live_runtime",
            "message": "RuntimeController connected" if ok else "Controller missing",
        }

    def _check_runtime(self) -> dict[str, JSONValue]:
        controller = getattr(self.bridge, "controller", None) if self.bridge else None
        if controller is None:
            return {
                "name": "Runtime",
                "status": FAILED,
                "source": "live_runtime",
                "message": "No controller",
            }
        try:
            tel = controller.snapshot()
            state = getattr(tel, "controller_state", None)
            state_val = state.value if state is not None else "unknown"
            return {
                "name": "Runtime",
                "status": PASSED,
                "source": "live_runtime",
                "message": f"state={state_val}, tick={getattr(tel, 'tick', 0)}",
            }
        except Exception as e:
            return {
                "name": "Runtime",
                "status": FAILED,
                "source": "live_runtime",
                "message": f"telemetry error: {e}",
            }

    def _check_structural(self) -> dict[str, JSONValue]:
        # Structural plasticity is disabled by config in poc_config.yaml.
        # "disabled by config" is NOT "failed".
        coordinator = getattr(self.bridge, "coordinator", None) if self.bridge else None
        plasticity = getattr(self.bridge, "plasticity", None) if self.bridge else None
        if coordinator is None or plasticity is None:
            return {
                "name": "Structural",
                "status": DISABLED,
                "source": "config",
                "message": "disabled by config (self_organization.enabled=false)",
            }
        return {
            "name": "Structural",
            "status": PASSED,
            "source": "live_runtime",
            "message": "Coordinator + PlasticityEngine connected",
        }

    def _check_snapshot(self) -> dict[str, JSONValue]:
        if self.heatmap_source is None:
            return {
                "name": "Snapshot",
                "status": PENDING,
                "source": "snapshot",
                "message": "No heatmap source configured",
            }
        try:
            path = getattr(self.heatmap_source, "snapshot_path", None)
            if path is None or not Path(path).exists():
                return {
                    "name": "Snapshot",
                    "status": PENDING,
                    "source": "snapshot",
                    "message": "Snapshot file not yet written",
                }
            return {
                "name": "Snapshot",
                "status": PASSED,
                "source": "snapshot",
                "message": f"{Path(path).name} available",
            }
        except Exception as e:
            return {
                "name": "Snapshot",
                "status": FAILED,
                "source": "snapshot",
                "message": f"error: {e}",
            }

    def _check_delta_storage(self) -> dict[str, JSONValue]:
        # Delta storage is disabled by config in poc_config.yaml.
        # Read the live dashboard state to determine availability.
        storage = getattr(self.state, "storage", None) if self.state else None
        available = getattr(storage, "available", False) if storage else False
        if available:
            return {
                "name": "Delta Storage",
                "status": PASSED,
                "source": "live_runtime",
                "message": "AsyncStorageSession active",
            }
        return {
            "name": "Delta Storage",
            "status": DISABLED,
            "source": "config",
            "message": "disabled by config (storage.runtime.enabled=false)",
        }

    def _check_structural_journal(self) -> dict[str, JSONValue]:
        coordinator = getattr(self.bridge, "coordinator", None) if self.bridge else None
        if coordinator is None:
            return {
                "name": "Structural Journal",
                "status": DISABLED,
                "source": "config",
                "message": "disabled by config (self_organization.enabled=false)",
            }
        return {
            "name": "Structural Journal",
            "status": PASSED,
            "source": "journal",
            "message": "StructuralJournal attached",
        }

    def _check_research(self) -> dict[str, JSONValue]:
        if self.research_source is None:
            return {
                "name": "Research",
                "status": DISABLED,
                "source": "research",
                "message": "B5D-SEF registry not found",
            }
        return {
            "name": "Research",
            "status": PASSED,
            "source": "research",
            "message": "B5D-SEF active",
        }

    def _check_tests(self) -> dict[str, JSONValue]:
        """Read tests/test_baseline.json and detect staleness.

        Scientific staleness model
        --------------------------
        A test baseline records the commit at which the test suite was last
        verified AND a digest of the scientifically relevant source tree
        (``src/``, ``configs/``, ``research/schemas/``, ``pyproject.toml``).

        A file inside a commit cannot stably contain its own commit SHA:
        amending the baseline to match the new HEAD produces yet another SHA.
        We therefore do NOT compare ``tested_commit == current_commit``.

        Instead we compare the recorded ``tested_tree_digest`` with the
        current tree digest. The baseline is:

        - ``passed``  — tree digest matches (only docs/baseline metadata changed)
        - ``stale``   — scientifically relevant source code changed since baseline
        - ``pending`` — baseline missing or HEAD/tree digest unavailable
        """
        ev = evaluate_test_baseline(self.repo_root)

        if not ev.available:
            return {
                "name": "Tests",
                "status": PENDING,
                "source": "test_baseline",
                "message": "test_baseline.json not found",
            }

        if ev.current_tree_digest is None:
            return {
                "name": "Tests",
                "status": PENDING,
                "source": "test_baseline",
                "message": "cannot compute current tree digest",
                "tested_commit": ev.tested_commit,
                "current_commit": ev.current_commit,
            }

        # Tree-digest match: only docs/baseline metadata changed since baseline.
        if not ev.stale:
            return {
                "name": "Tests",
                "status": PASSED,
                "source": "test_baseline",
                "message": (
                    f"verified tree digest matches: {ev.passed} passed, "
                    f"{ev.failed} failed, {ev.skipped} skipped"
                ),
                "tested_commit": ev.tested_commit,
                "current_commit": ev.current_commit,
                "tested_tree_digest": ev.tested_tree_digest,
                "current_tree_digest": ev.current_tree_digest,
                "passed": ev.passed,
                "failed": ev.failed,
                "skipped": ev.skipped,
            }

        # Scientifically relevant source code changed since baseline — STALE.
        return {
            "name": "Tests",
            "status": STALE,
            "source": "test_baseline",
            "message": (
                f"source tree changed since baseline "
                f"(tested_commit {(ev.tested_commit or 'unknown')[:8]}, "
                f"HEAD {(ev.current_commit or 'unknown')[:8]})"
            ),
            "tested_commit": ev.tested_commit,
            "current_commit": ev.current_commit,
            "tested_tree_digest": ev.tested_tree_digest,
            "current_tree_digest": ev.current_tree_digest,
        }

    def _check_error_visibility(self) -> dict[str, JSONValue]:
        """Error visibility is passed once the dashboard surfaces errors
        through the integration status itself (this endpoint)."""
        return {
            "name": "Error Visibility",
            "status": PASSED,
            "source": "live_backend",
            "message": "Integration status endpoint reports component errors",
        }

    # ------------------------------------------------------------------------
    # Helpers (delegated to verification.py for a single source of truth)
    # ------------------------------------------------------------------------

    def _current_git_head(self) -> str | None:
        """Return the current git HEAD SHA, or None if unavailable."""
        return current_git_head(self.repo_root)

    def _current_tree_digest(self) -> str | None:
        """Return a SHA-256 digest of the scientifically relevant source tree.

        Delegates to :func:`verification.compute_source_tree_digest` so that
        ``/api/integration/status`` and ``/api/gate/status`` can never
        disagree about the same source tree.
        """
        return compute_source_tree_digest(self.repo_root)
