from pathlib import Path

import pytest

from src.embodiment import (
    EmbodimentTreatmentProvenance,
    EnergyObservation,
    EnergyState,
    MSBAGatewayConfig,
    ResourcePressure,
    SymbolFrame,
    allocation_gate,
    default_modality_profiles,
    energy_state,
    energy_units,
    msba_contract,
    phase_coherence,
    phase_weighted_stdp,
    recommended_protection_policy,
    resource_pressure,
    visual_growth_probability,
)


def test_msba_contract_is_fail_closed_and_core_safe() -> None:
    payload = msba_contract()
    gateway = payload["gateway"]
    boundary = payload["scientific_boundary"]
    assert isinstance(gateway, dict)
    assert isinstance(boundary, dict)
    assert gateway["synaptic_plasticity_enabled"] is False
    assert gateway["structural_plasticity_enabled"] is False
    assert gateway["meta_gating_enabled"] is False
    assert gateway["adaptive_allocation_enabled"] is False
    assert boundary["core_mutation"] is False
    assert boundary["activation_requires_preregistered_experiment"] is True


def test_modality_profiles_preserve_distinct_pathways_without_fixed_5d_axes() -> None:
    profiles = {item.modality.value: item for item in default_modality_profiles()}
    assert profiles["audio"].pathway == "temporal_coherence"
    assert profiles["vision"].pathway == "spatial_multiplex"
    assert profiles["digital"].pathway == "quantized_high_fidelity"
    assert profiles["digital"].exact_payload_outside_snn is True
    topology = msba_contract()["topology"]
    assert isinstance(topology, dict)
    assert topology["fixed_axis_semantics"] is False


def test_digital_symbol_frame_is_exact_and_deterministic() -> None:
    frame = SymbolFrame(b"fire", sequence=7, provenance="unit-test")
    assert frame.checksum == SymbolFrame(b"fire").checksum
    assert frame.deterministic_population(8) == frame.deterministic_population(8)
    assert len(frame.deterministic_population(8)) == 8
    assert set(frame.deterministic_population(8)) <= {0, 1}
    persisted = frame.to_json()
    assert persisted["checksum_algorithm"] == "sha256"
    assert persisted["checksum"] == frame.checksum
    assert persisted["payload_size_bytes"] == 4
    assert persisted["provenance"] == "unit-test"


def test_energy_accounting_keeps_measured_and_estimated_joules_separate() -> None:
    estimate = energy_units(
        EnergyObservation(spikes=2, synaptic_events=3, measured_joules=0.25),
        joules_per_unit=0.01,
    )
    assert estimate.normalized_energy_units > 0.0
    assert estimate.estimated_joules is not None
    assert estimate.measured_joules == pytest.approx(0.25)
    assert estimate.estimated_joules != estimate.measured_joules


def test_energy_accounting_rejects_negative_counters() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        energy_units(EnergyObservation(spikes=-1))


def test_resource_pressure_and_fan_failure_are_bounded_and_fail_safe() -> None:
    nominal = resource_pressure(ResourcePressure())
    loaded = resource_pressure(
        ResourcePressure(energy=1.0, thermal=1.0, compute=1.0, memory=1.0)
    )
    failed = resource_pressure(ResourcePressure(fan_failure=True))
    assert nominal == pytest.approx(0.0)
    assert 0.0 < loaded <= 1.0
    assert failed == pytest.approx(1.0)
    assert energy_state(ResourcePressure(fan_failure=True)) is EnergyState.SURVIVAL


def test_allocation_gate_prefers_higher_utility_and_lower_cost() -> None:
    pressure = ResourcePressure(energy=0.4, compute=0.2)
    config = MSBAGatewayConfig(allocation_beta=4.0)
    useful = allocation_gate(utility=2.0, cost=0.2, pressure=pressure, config=config)
    costly = allocation_gate(utility=0.5, cost=2.0, pressure=pressure, config=config)
    assert 0.0 <= costly < useful <= 1.0


def test_phase_weighting_never_inverts_stdp_sign() -> None:
    assert phase_coherence(0.0) == pytest.approx(1.0)
    assert phase_coherence(3.141592653589793) == pytest.approx(0.0)
    assert phase_weighted_stdp(0.2, 0.5) >= 0.0
    assert phase_weighted_stdp(-0.2, 0.5) <= 0.0


def test_visual_growth_decreases_with_distance_and_resource_pressure() -> None:
    free = ResourcePressure()
    constrained = ResourcePressure(energy=1.0, thermal=1.0, compute=1.0, memory=1.0)
    near = visual_growth_probability(10.0, 0.1, 1.0, free, eta_growth=0.1)
    far = visual_growth_probability(10.0, 3.0, 1.0, free, eta_growth=0.1)
    pressured = visual_growth_probability(10.0, 0.1, 1.0, constrained, eta_growth=0.1)
    assert near > far
    assert near > pressured


def test_survival_policy_preserves_safety_and_module_has_no_core_import() -> None:
    policy = recommended_protection_policy(EnergyState.SURVIVAL)
    preserve = policy["preserve"]
    assert isinstance(preserve, list)
    assert "fan_monitoring" in preserve
    assert "core_persistence" in preserve
    source = Path("src/embodiment/msba.py").read_text(encoding="utf-8")
    assert "from src.core" not in source
    assert "import src.core" not in source


def test_msba_contract_requires_digital_checksum_persistence() -> None:
    boundary = msba_contract()["scientific_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["digital_payload_outside_snn"] is True
    assert boundary["digital_checksum_persisted"] is True


def test_treatment_provenance_binds_adapter_projection_gateway_and_energy() -> None:
    record = EmbodimentTreatmentProvenance(
        adapter_id="vision.adapter.test",
        adapter_architecture="onnx-runtime",
        projection_mode="shuffled",
        projection_dimensions=8,
    ).to_json()

    assert record["record_type"] == "embodiment_treatment_provenance"
    assert record["status"] == "DATA_ONLY"
    assert record["adapter"] == {
        "id": "vision.adapter.test",
        "architecture": "onnx-runtime",
    }
    assert record["projection"]["mode"] == "shuffled"
    assert record["projection"]["dimensions"] == 8
    assert record["gateway"]["requires_preregistration"] is True
    assert record["energy"]["units_are_not_physical_joules"] is True
    assert record["scientific_boundary"]["does_not_promote_to_evid"] is True
    assert len(record["record_sha256"]) == 64
    assert record == EmbodimentTreatmentProvenance(
        adapter_id="vision.adapter.test",
        adapter_architecture="onnx-runtime",
        projection_mode="shuffled",
        projection_dimensions=8,
    ).to_json()
