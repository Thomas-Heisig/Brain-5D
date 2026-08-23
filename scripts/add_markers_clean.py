"""Add pytest markers to all test files — cleanly, after all imports."""

from __future__ import annotations

from pathlib import Path

CATEGORIES: dict[str, str] = {
    "test_artifacts": "core",
    "test_async_storage": "storage",
    "test_auto_approval": "plasticity",
    "test_b5d_storage": "storage",
    "test_checkpoint": "storage",
    "test_compaction": "storage",
    "test_crc": "storage",
    "test_dashboard": "dashboard",
    "test_dashboard_alpha6": "dashboard",
    "test_dashboard_alpha7": "dashboard",
    "test_dashboard_compatibility_v050a2": "dashboard",
    "test_dashboard_control_service": "dashboard",
    "test_dashboard_homeostasis": "dashboard",
    "test_dashboard_single_instance": "dashboard",
    "test_delta_journal": "storage",
    "test_eligibility": "learning",
    "test_embodiment": "embodiment",
    "test_golden_chain": "integration",
    "test_heatmap": "dashboard",
    "test_homeostasis_engine": "homeostasis",
    "test_knowledge_contracts": "core",
    "test_language_organ_contracts": "core",
    "test_lazy_storage_view": "storage",
    "test_learning_experiment": "learning",
    "test_manipulator": "core",
    "test_network": "core",
    "test_network_hooks": "core",
    "test_neuron": "core",
    "test_observatory_data": "dashboard",
    "test_optical_codec": "storage",
    "test_recovery": "storage",
    "test_research_dashboard_routes": "dashboard",
    "test_restore_continue": "storage",
    "test_reward": "learning",
    "test_runtime_control": "core",
    "test_runtime_controller_alpha4": "core",
    "test_self_organization": "plasticity",
    "test_self_organization_alpha4": "plasticity",
    "test_self_organization_policy_alpha3": "plasticity",
    "test_signal_processing_contracts": "core",
    "test_spatial_index": "core",
    "test_stdp_integration": "plasticity",
    "test_stdp_isolated": "plasticity",
    "test_storage_runtime": "storage",
    "test_structural_coordinator_alpha5": "plasticity",
    "test_structural_dashboard_routes": "dashboard",
    "test_structural_heatmap": "dashboard",
    "test_structural_journal": "storage",
    "test_structural_operator_bridge": "dashboard",
    "test_structural_plasticity_journal": "plasticity",
    "test_structural_recovery": "storage",
    "test_structural_undo": "plasticity",
}

SLOW: set[str] = {
    "test_b5d_storage",
    "test_delta_journal",
    "test_golden_chain",
    "test_restore_continue",
    "test_learning_experiment",
}

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"


def _find_insert_position(lines: list[str]) -> int:
    """Find the line after the last import statement, past docstrings."""
    in_docstring = False
    last_import = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('"""') or s.startswith("'''"):
            in_docstring = not in_docstring
        if in_docstring:
            continue
        if s.startswith("import ") or s.startswith("from "):
            last_import = i
    return last_import + 1 if last_import >= 0 else 0


def main() -> None:
    modified = 0
    for f in sorted(TESTS_DIR.glob("test_*.py")):
        stem = f.stem
        if stem == "test_ci_smoke" or stem == "conftest":
            continue

        cat = CATEGORIES.get(stem)
        if cat is None:
            print(f"  ?  {stem}: no category mapping")
            continue

        content = f.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Remove any existing pytestmark lines and import pytest
        cleaned: list[str] = []
        for line in lines:
            s = line.strip()
            if s.startswith("pytestmark") or s == "import pytest":
                continue
            cleaned.append(line)
        lines = cleaned

        # Find insert position after all imports
        insert_pos = _find_insert_position(lines)

        # Build marker line
        markers = [f"pytest.mark.{cat}"]
        if stem in SLOW:
            markers.append("pytest.mark.slow")

        if len(markers) == 1:
            marker_line = f"pytestmark = {markers[0]}"
        else:
            marker_line = f"pytestmark = [{', '.join(markers)}]"

        lines.insert(insert_pos, marker_line)
        f.write_text("\n".join(lines), encoding="utf-8")
        print(f"  {stem}: {cat}" + (" +slow" if stem in SLOW else ""))
        modified += 1

    print(f"\nDone: {modified} files modified")


if __name__ == "__main__":
    main()
