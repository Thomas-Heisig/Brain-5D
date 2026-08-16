import json
from conftest import base_config
from src.diagnostics.stimulus import StimulusResult
from src.utils.run_artifacts import RunArtifacts


def test_run_artifacts(tmp_path):
    cfg=base_config()
    with RunArtifacts(cfg,run_id="test",root=tmp_path) as a:
        a.log_metrics({"tick":0,"spikes_this_tick":1}); a.log_spikes(0,(123,)); a.log_stimulus(StimulusResult(0,"manual",(123,),(100.0,),100.0)); a.save_topology({"neurons":1}); a.save_summary({"ok":True})
    d=tmp_path/"test"; assert (d/"metrics.csv").exists(); assert json.loads((d/"run_summary.json").read_text())["ok"] is True
