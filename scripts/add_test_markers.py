"""Add pytest markers to all test files that don't have them yet.

Usage: python scripts/add_test_markers.py
"""

from __future__ import annotations

import re
from pathlib import Path

# Mapping: filename pattern -> category marker
CATEGORY_MAP: dict[str, str] = {
    # Storage
    "test_b5d_storage": "storage",
    "test_async_storage": "storage",
    "test_checkpoint": "storage",
    "test_compaction": "storage",
    "test_crc": "storage",
    "test_delta_journal": "storage",
    "test_lazy_storage_view": "storage",
    "test_optical_codec": "storage",
    "test_recovery": "storage",
    "test_restore_continue": "storage",
    "test_storage_runtime": "storage",
    "test_structural_journal": "storage",
    "test_structural_recovery": "storage",
    # Dashboard
    "test_dashboard": "dashboard",
    "test_dashboard_alpha6": "dashboard",
    "test_dashboard_alpha7": "dashboard",
    "test_dashboard_compatibility_v050a2": "dashboard",
    "test_dashboard_control_service": "dashboard",
    "test_dashboard_homeostasis": "dashboard",
    "test_dashboard_single_instance": "dashboard",
    "test_heatmap": "dashboard",
    "test_observatory_data": "dashboard",
    "test_research_dashboard_routes": "dashboard",
    "test_structural_dashboard_routes": "dashboard",
    "test_structural_heatmap": "dashboard",
    "test_structural_operator_bridge": "dashboard",
    # Plasticity / Self-organization
    "test_auto_approval": "plasticity",
    "test_self_organization": "plasticity",
    "test_self_organization_alpha4": "plasticity",
    "test_self_organization_policy_alpha3": "plasticity",
    "test_stdp_integration": "plasticity",
    "test_stdp_isolated": "plasticity",
    "test_structural_coordinator_alpha5": "plasticity",
    "test_structural_plasticity_journal": "plasticity",
    "test_structural_undo": "plasticity",
    # Learning
    "test_eligibility": "learning",
    "test_learning_experiment": "learning",
    "test_reward": "learning",
    # Embodiment
    "test_embodiment": "embodiment",
    # Homeostasis
    "test_homeostasis_engine": "homeostasis",
    # Core
    "test_artifacts": "core",
    "test_brain5d_launcher": "core",
    "test_knowledge_contracts": "core",
    "test_language_organ_contracts": "core",
    "test_manipulator": "core",
    "test_network": "core",
    "test_network_hooks": "core",
    "test_neuron": "core",
    "test_runtime_control": "core",
    "test_runtime_controller_alpha4": "core",
    "test_signal_processing_contracts": "core",
    "test_spatial_index": "core",
    # Integration
    "test_golden_chain": "integration",
}

# Files that should also be marked as slow
SLOW_FILES: set[str] = {
    "test_b5d_storage",
    "test_delta_journal",
    "test_golden_chain",
    "test_restore_continue",
    "test_learning_experiment",
}

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"


def _has_pytestmark(content: str) -> bool:
    return bool(re.search(r"^pytestmark\s*=", content, re.MULTILINE))


def _has_any_marker(content: str, fname: str) -> bool:
    if _has_pytestmark(content):
        return True
    # Check for @pytest.mark in the first 30 lines
    lines = content.split("\n")[:30]
    return any("@pytest.mark" in line for line in lines)


def _add_marker(filepath: Path, marker: str, extra_markers: list[str] | None = None) -> bool:
    content = filepath.read_text(encoding="utf-8")

    if _has_any_marker(content, filepath.stem):
        return False

    # Find the first import line or after docstring
    lines = content.split("\n")
    insert_idx = 0
    in_docstring = False

    for i, line in enumerate(lines):
        if line.strip().startswith('"""') or line.strip().startswith("'''"):
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            insert_idx = i + 1
            break
        if line.strip() and not line.strip().startswith("#"):
            insert_idx = i
            break

    all_markers = [marker]
    if extra_markers:
        all_markers.extend(extra_markers)

    marker_line = f'pytestmark = pytest.mark.{", ".join(all_markers)}'
    indent = ""
    lines.insert(insert_idx, f"{indent}{marker_line}\n")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return True


def main() -> None:
    modified = 0
    skipped = 0
    errors = 0

    for filepath in sorted(TESTS_DIR.glob("test_*.py")):
        stem = filepath.stem
        if stem == "test_ci_smoke":
            skipped += 1
            continue

        marker = CATEGORY_MAP.get(stem)
        if marker is None:
            print(f"  ⚠  {stem}: no category mapping, skipped")
            skipped += 1
            continue

        extra = ["slow"] if stem in SLOW_FILES else None

        try:
            if _add_marker(filepath, marker, extra):
                print(f"  ✓  {stem}: @pytest.mark.{marker}")
                modified += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ✗  {stem}: error - {e}")
            errors += 1

    print(f"\nDone: {modified} modified, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
