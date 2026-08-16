from src.storage.structural_journal import StructuralChangeKind, StructuralChangeRecord
from src.visualization.structural_heatmap import StructuralHeatmapSource


def test_structural_heatmap_projects_xy() -> None:
    records = (
        StructuralChangeRecord(
            sequence=1,
            tick=1,
            kind=StructuralChangeKind.NEURON_ADD,
            coord=(1, 2, 0, 0, 0),
        ),
        StructuralChangeRecord(
            sequence=2,
            tick=2,
            kind=StructuralChangeKind.NEURON_ADD,
            coord=(1, 2, 1, 0, 0),
        ),
    )
    result = StructuralHeatmapSource((4, 4, 4, 4, 4)).build(records, "neuron_additions")
    assert result.values[1, 2] == 2.0
    assert result.populated_cells == 1
