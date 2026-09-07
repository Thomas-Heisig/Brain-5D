"""Isolated full-stack browser fixture using the real HTTP server and SNN.

All mutable output lives in a TemporaryDirectory. The optional fixture route
only changes explicitly labelled virtual inventory; it is never installed by
production entry points and never activates hardware or peripheral learning.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    from src.controller.runtime import RuntimeController
    from src.core.network import Brain5DConfig, NeuralNetwork, StepResult
    from src.dashboard.docs_source import create_docs_source
    from src.dashboard.live_projection import TelemetryFrameStore
    from src.dashboard.models import SystemMetrics
    from src.dashboard.operator_bridge import OperatorBridge
    from src.dashboard.research_source import ResearchSource
    from src.dashboard.server import DashboardRequestHandler, DashboardServer
    from src.dashboard.state import DashboardStateStore
    from src.embodiment.connections import (
        ConnectionDescriptor,
        ConnectionKind,
        ConnectionManager,
        ConnectionStatus,
        RelationshipClass,
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4174)
    parser.add_argument("--dashboard-only", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="brain5d-browser-") as directory:
        root = Path(directory)
        research = root / "research"
        docs = root / "docs"
        docs.mkdir()
        for name in ("registry", "protocols", "preregistrations", "schemas"):
            shutil.copytree(ROOT / "research" / name, research / name)
        shutil.copytree(ROOT / "configs", root / "configs")
        (docs / "preview.md").write_text(
            "# Gemeinsamer Renderer\n\n**Dateiinhalt** im Viewer und Chat.\n\n"
            "[Messdaten](sample.json)\n\n<script>window.unsafeExecuted=true</script>\n",
            encoding="utf-8",
        )
        (docs / "sample.json").write_text(
            '{"measured": [1, 2, 3], "evidence": false}\n', encoding="utf-8"
        )
        (docs / "data.csv").write_text('name,value\n"a,b",3\n', encoding="utf-8")
        (docs / "unknown.b5d").write_bytes(b"B5D\x00binary")
        # Copy actual canonical docs for the file links in the release workspace.
        shutil.copytree(ROOT / "docs" / "08-roadmap", docs / "08-roadmap")
        shutil.copytree(ROOT / "docs" / "07-changelog", docs / "07-changelog")
        store = DashboardStateStore()
        network = NeuralNetwork(
            Brain5DConfig(dimensions=(2, 2, 2, 2, 2)), random.Random(42)
        )
        first = network.add_neuron((0, 0, 0, 0, 0))
        second = network.add_neuron((1, 1, 1, 1, 1))
        network.connect(first, second, weight=8.0, delay=1)
        controller = RuntimeController(
            network, target_hz=100, telemetry_interval_ticks=1
        )
        frames = TelemetryFrameStore(capture_interval_ticks=1)
        frames.prime(network)
        controller.add_pre_hook(lambda _tick: network.inject_current(first, 10.0))

        def publish(_tick: int, result: StepResult) -> None:
            store.update(
                system=SystemMetrics(
                    tick=network.current_tick,
                    neurons=network.neuron_count,
                    synapses=network.synapse_count,
                    spikes_total=network.total_spikes,
                    spikes_last_tick=result.spikes_this_tick,
                )
            )
            frames.prime(network)

        controller.add_hook(publish)
        controller.run_ticks(2)
        connections = ConnectionManager(cache_seconds=60)
        bridge = (
            None
            if args.dashboard_only
            else OperatorBridge(controller, telemetry_store=frames)
        )
        server = DashboardServer(
            ("127.0.0.1", args.port),
            store,
            None,
            bridge,
            docs_source=create_docs_source(docs),
            research_source=ResearchSource(research),
            connection_manager=connections,
        )

        class FixtureHandler(DashboardRequestHandler):
            """Test-only inventory changes, never exported by the production server."""

            def do_POST(self) -> None:
                if self.path != "/__test__/inventory":
                    super().do_POST()
                    return
                value = cast(dict[str, Any], self._read_json_body())
                available = value.get("available") is True
                for connection_id, kind in (
                    ("sensor.camera.browser", ConnectionKind.SENSOR),
                    ("actuator.robotics.browser", ConnectionKind.ACTUATOR),
                ):
                    connections.register(
                        ConnectionDescriptor(
                            connection_id=connection_id,
                            name="Browser fixture " + kind.value,
                            kind=kind,
                            relationship=RelationshipClass.REACHABLE,
                            status=(
                                ConnectionStatus.AVAILABLE
                                if available
                                else ConnectionStatus.UNAVAILABLE
                            ),
                            available=available,
                            source="browser_fixture",
                            message="Not a physical device",
                        )
                    )
                self._send_json({"ok": True})

        server.RequestHandlerClass = FixtureHandler
        try:
            print(
                json.dumps({"port": args.port, "runtime": not args.dashboard_only}),
                flush=True,
            )
            server.serve_forever()
        finally:
            controller.stop()
            server.server_close()


if __name__ == "__main__":
    main()
