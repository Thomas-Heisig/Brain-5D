"""Launcher subprocess argument isolation tests."""

from argparse import Namespace
from pathlib import Path

from scripts.brain5d_launcher import build_command


def test_launcher_keeps_dashboard_arguments_out_of_simulation_command() -> None:
    args = Namespace(
        config=Path("configs/poc_config.yaml"),
        observe=True,
        dashboard=True,
        open_browser=True,
        host="0.0.0.0",
        port=9000,
        benchmark=False,
        no_learning=False,
        no_homeostasis=False,
        ticks=None,
    )

    simulation_command = build_command(args)

    assert simulation_command[1:4] == ["-m", "src.main", "--config"]
    assert simulation_command[-1] == "--observe"
    assert "--dashboard" not in simulation_command
    assert "--open-browser" not in simulation_command
    assert "--host" not in simulation_command
    assert "--port" not in simulation_command
