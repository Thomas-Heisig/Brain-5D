"""Dashboard alpha.7 documentation, snapshot, and embodiment tests."""

from pathlib import Path

from src.dashboard.docs_source import DocumentationSource
from src.dashboard.models import DashboardSnapshot
from src.embodiment.models import EmbodimentMetrics


def test_embodiment_metrics_are_exposed_by_dashboard() -> None:
    snapshot = DashboardSnapshot(
        embodiment=EmbodimentMetrics(
            environment_kind="simulated",
            active_sensors=2,
            active_actuators=1,
            episode=4,
            last_reward=0.75,
            last_action="move-left",
        )
    )
    payload = snapshot.to_json()
    embodiment = payload["embodiment"]
    assert isinstance(embodiment, dict)
    assert embodiment["environment_kind"] == "simulated"
    assert embodiment["episode"] == 4


def test_documentation_source_blocks_path_traversal(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# docs", encoding="utf-8")
    source = DocumentationSource(docs)
    assert source.read("README.md") == "# docs"
    assert source.list_documents()[0].name == "README.md"
    try:
        source.read("../secret.md")
    except ValueError:
        pass
    else:
        raise AssertionError("path traversal must be rejected")
