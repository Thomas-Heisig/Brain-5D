"""Frontend regressions for the animated Brain-5D embodiment map."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

STATIC_DIR = Path(__file__).parent.parent / "src" / "dashboard" / "static"


def _read(name: str) -> str:
    return (STATIC_DIR / name).read_text(encoding="utf-8")


def test_brain5d_being_is_a_valid_svg_asset() -> None:
    asset = STATIC_DIR / "assets" / "brain5d-being.svg"
    root = ElementTree.parse(asset).getroot()

    assert root.tag.endswith("svg")
    assert root.attrib["viewBox"] == "0 0 1000 620"


def test_embodiment_map_exposes_all_published_system_organs() -> None:
    html = _read("index.html")

    assert 'src="/assets/brain5d-being.svg"' in html
    for element_id in (
        "being-tick",
        "being-neurons",
        "being-synapses",
        "being-spikes",
        "being-energy",
        "being-homeostasis",
        "being-sensors",
        "being-actuators",
        "being-stdp",
        "being-signal-frames",
        "being-language-state",
        "being-knowledge-items",
        "being-structural-changes",
        "being-storage-state",
        "being-system-status",
    ):
        assert f'id="{element_id}"' in html


def test_embodiment_animation_is_store_driven_and_accessible() -> None:
    workspace_js = _read("workspace-panels.js")
    styles = _read("styles.css")

    for state_key in (
        "state.learning",
        "state.storage",
        "state.homeostasis",
        "state.structural",
        "state.spikes",
        "state.language_organ",
        "state.knowledge_intake",
        "state.signal_metrics",
    ):
        assert state_key in workspace_js
    assert 'livingMap.style.setProperty("--activity"' in workspace_js
    assert 'livingMap.style.setProperty("--energy"' in workspace_js
    assert 'livingMap.style.setProperty("--synchrony"' in workspace_js
    assert "@media (prefers-reduced-motion: reduce)" in styles
    assert ".brain5d-being," in styles