import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest

from src.embodiment import (
    AreaDescriptor,
    AreaKind,
    NeuralSymbiosisCatalog,
    NetworkAreaAdapter,
    PipelineDirection,
    PipelineTemplate,
    PlasticGatewayConfig,
    formation_probability,
    gate_signal,
    homeostatic_scale,
    pair_stdp_delta,
    pruning_probability,
    reward_modulated_delta,
)


class FakeConnection:
    def __init__(self, connection_id: str, available: bool) -> None:
        self.connection_id = connection_id
        self.available = available


def _object(value: object) -> dict[str, Any]:
    """Narrow a JSON object for structural assertions in type-checked tests."""

    assert isinstance(value, dict)
    return cast(dict[str, Any], value)


def _object_list(value: object) -> list[dict[str, Any]]:
    """Narrow a JSON array of objects for structural assertions."""

    assert isinstance(value, list)
    return cast(list[dict[str, Any]], value)


def test_catalog_is_open_set_and_fail_closed() -> None:
    catalog = NeuralSymbiosisCatalog()
    payload = catalog.to_json(
        [
            FakeConnection("sensor.camera.usb", True),
            FakeConnection("sensor.microphone.usb", False),
            FakeConnection("actuator.audio.default", True),
        ]
    )

    assert payload["name"] == "Neural Symbiosis"
    assert payload["scope"] == "embodiment"
    adapter_contract = _object(payload["adapter_contract"])
    gateway = _object(payload["gateway"])
    boundary = _object(payload["scientific_boundary"])
    assert adapter_contract["architecture_open_set"] is True
    assert gateway["synaptic_plasticity_enabled"] is False
    assert gateway["structural_plasticity_enabled"] is False
    assert gateway["efferent_gating_enabled"] is False
    assert boundary["core_mutation"] is False
    assert boundary["historical_data_unchanged"] is True
    assert boundary["catalog_presence_is_not_evidence"] is True

    pipelines = {
        str(item["pipeline_id"]): item for item in _object_list(payload["pipelines"])
    }
    assert pipelines["camera.vision"]["reachable"] is True
    assert pipelines["camera.vision"]["enabled"] is False
    assert pipelines["microphone.audio"]["reachable"] is False
    assert pipelines["core.audio"]["reachable"] is True


def test_catalog_accepts_arbitrary_network_area() -> None:
    catalog = NeuralSymbiosisCatalog()
    catalog.register_area(
        AreaDescriptor(
            area_id="research.custom-liquid-network",
            name="Liquid Network",
            kind=AreaKind.NEURAL,
            architecture="Liquid Neural Network",
            roles=("temporal", "control"),
            input_modalities=("features",),
            output_modalities=("latent",),
        )
    )
    catalog.register_pipeline(
        PipelineTemplate(
            pipeline_id="custom.cognitive",
            name="Custom cognitive area",
            direction=PipelineDirection.COGNITIVE,
            stages=(
                "research.custom-liquid-network",
                "gateway.cognitive",
                "brain5d.core",
            ),
            source_connection="virtual.custom",
        )
    )

    payload = catalog.to_json([])
    area_ids = {str(item["area_id"]) for item in _object_list(payload["areas"])}
    pipeline_ids = {
        str(item["pipeline_id"]) for item in _object_list(payload["pipelines"])
    }
    assert "research.custom-liquid-network" in area_ids
    assert "custom.cognitive" in pipeline_ids


def test_catalog_does_not_execute_peripheral_adapters_or_mutate_state() -> None:
    core_state: dict[str, Any] = {"neurons": [1], "synapses": []}
    research_state: dict[str, Any] = {"claims": ["RQ-TEST-001"]}
    calls = 0

    class HostileAdapter:
        area_id = "research.hostile"
        architecture = "test"

        def process(self, payload: object, tick: int) -> object:
            nonlocal calls
            calls += 1
            core_state["neurons"].append(tick)
            research_state["claims"].append("mutated")
            return payload

    adapter = HostileAdapter()
    assert isinstance(adapter, NetworkAreaAdapter)

    def digest(value: object) -> str:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    core_digest = digest(core_state)
    research_digest = digest(research_state)
    catalog = NeuralSymbiosisCatalog()
    catalog.register_area(
        AreaDescriptor(
            area_id=adapter.area_id,
            name="Hostile test area",
            kind=AreaKind.VIRTUAL,
            architecture=adapter.architecture,
            roles=("test",),
            input_modalities=("test",),
            output_modalities=("test",),
        )
    )
    catalog.register_pipeline(
        PipelineTemplate(
            pipeline_id="hostile.test",
            name="Hostile test pipeline",
            direction=PipelineDirection.COGNITIVE,
            stages=(adapter.area_id, "gateway.cognitive"),
            source_connection="virtual.hostile",
        )
    )

    payload = catalog.to_json([])

    assert payload["scope"] == "embodiment"
    assert calls == 0
    assert digest(core_state) == core_digest
    assert digest(research_state) == research_digest


def test_unknown_pipeline_stage_is_rejected() -> None:
    catalog = NeuralSymbiosisCatalog()
    with pytest.raises(ValueError, match="unknown pipeline stages"):
        catalog.register_pipeline(
            PipelineTemplate(
                pipeline_id="invalid",
                name="Invalid",
                direction=PipelineDirection.COGNITIVE,
                stages=("not.registered", "brain5d.core"),
            )
        )


def test_pair_stdp_delta_has_expected_direction_and_weight_dependence() -> None:
    config = PlasticGatewayConfig()
    potentiation = pair_stdp_delta(0.25, 5.0, config)
    depression = pair_stdp_delta(0.25, -5.0, config)
    near_max = pair_stdp_delta(0.95, 5.0, config)

    assert potentiation > 0.0
    assert depression < 0.0
    assert near_max < potentiation


def test_homeostatic_scale_moves_weight_toward_target_activity() -> None:
    config = PlasticGatewayConfig(target_rate_hz=5.0)
    underactive = homeostatic_scale(0.5, 2.5, config)
    overactive = homeostatic_scale(0.5, 10.0, config)

    assert underactive > 0.5
    assert overactive < 0.5
    assert 0.0 <= underactive <= 1.0
    assert 0.0 <= overactive <= 1.0


def test_gate_and_third_factor_math_is_bounded_and_explicit() -> None:
    config = PlasticGatewayConfig(gate_learning_eta=0.2)
    assert 0.0 < gate_signal(0.0, 0.0) < 1.0
    assert gate_signal(1000.0, 0.0) == pytest.approx(1.0)
    assert gate_signal(-1000.0, 0.0) == pytest.approx(0.0)
    assert reward_modulated_delta(0.25, 2.0, config) == pytest.approx(0.1)


def test_structural_probabilities_are_clipped_and_rng_free() -> None:
    config = PlasticGatewayConfig(structural_eta=0.5, pruning_eta=0.5)
    assert formation_probability(5.0, 5.0, 10.0, config) == pytest.approx(0.125)
    assert 0.0 <= pruning_probability(0.25, config) <= 1.0
    assert pruning_probability(0.1, config) > pruning_probability(0.9, config)

    source = Path("src/embodiment/neural_symbiosis.py").read_text(encoding="utf-8")
    assert "random" not in source
    assert "from src.core" not in source
    assert "import src.core" not in source


def test_wesen_neural_symbiosis_is_read_only() -> None:
    static = Path("src/dashboard/static")
    source = (static / "wesen-neural-symbiosis.js").read_text(encoding="utf-8")
    console = (static / "console-log.js").read_text(encoding="utf-8")

    assert 'fetch("/api/embodiment/connections"' in source
    assert 'method: "POST"' not in source
    assert 'method: "PUT"' not in source
    assert 'method: "DELETE"' not in source
    assert "/api/control" not in source
    assert "Scientific boundary" in source
    assert "Neural Symbiosis" in source
    assert 'import "./wesen-neural-symbiosis.js"' in console
    assert '"/wesen-neural-symbiosis.css"' in console
