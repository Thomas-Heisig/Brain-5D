import json
from pathlib import Path
from typing import Dict, Any, cast

from conftest import base_config, TestConfig
from src.diagnostics.stimulus import StimulusResult
from src.utils.run_artifacts import RunArtifacts


def test_run_artifacts(tmp_path: Path) -> None:
    """Test the RunArtifacts context manager with a temporary directory."""
    cfg: TestConfig = base_config()
    # RunArtifacts expects Dict[str, Any]; we cast to satisfy the type checker.
    # The cast does not change runtime behavior; cfg is a plain dict.
    with RunArtifacts(cast(Dict[str, Any], cfg), run_id="test", root=tmp_path) as a:
        a.log_metrics({"tick": 0, "spikes_this_tick": 1})
        a.log_spikes(0, (123,))
        a.log_stimulus(StimulusResult(0, "manual", (123,), (100.0,), 100.0))
        a.save_topology({"neurons": 1})
        a.save_summary({"ok": True})

    d = tmp_path / "test"
    assert (d / "metrics.csv").exists()
    assert json.loads((d / "run_summary.json").read_text())["ok"] is True