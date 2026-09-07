"""Modality-Specific Synaptic Pathway Architecture (MSBA).

MSBA is an embodiment-only, fail-closed contract below Neural Symbiosis. It
models modality-specific gateway geometry, candidate plasticity mathematics,
resource/energy accounting and adaptive allocation without importing or
mutating the Brain-5D neural core.

All learning and structural growth flags default to disabled. The functions in
this module calculate candidate values only; applying them to a live gateway
requires an explicit preregistered experiment.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import StrEnum

from .models import JSONValue

MIN_PROJECTION_DIMENSIONS = 1
MAX_PROJECTION_DIMENSIONS = 32


class Modality(StrEnum):
    AUDIO = "audio"
    VISION = "vision"
    DIGITAL = "digital"


class EnergyState(StrEnum):
    NORMAL = "normal"
    CONSERVE = "conserve"
    CRITICAL = "critical"
    SURVIVAL = "survival"


def validate_projection_dimensions(value: int) -> int:
    """Validate an MSBA projection-space dimensionality without touching core IDs."""

    if isinstance(value, bool):
        raise ValueError("projection_dimensions must be an integer")
    if not MIN_PROJECTION_DIMENSIONS <= value <= MAX_PROJECTION_DIMENSIONS:
        raise ValueError(
            f"projection_dimensions must be between {MIN_PROJECTION_DIMENSIONS} "
            f"and {MAX_PROJECTION_DIMENSIONS}"
        )
    return value


@dataclass(frozen=True, slots=True)
class MSBAGatewayConfig:
    """Fail-closed configuration for modality-specific gateway experiments.

    ``projection_dimensions`` describes the external/adaptor projection space.
    It may be increased above five without changing the persisted 5D neuron-ID
    format. A future versioned core-format migration is required before the
    productive SNN itself can store more than five spatial coordinates.
    """

    audio_bands: int = 32
    audio_max_delay_ms: int = 20
    vision_width: int = 100
    vision_height: int = 100
    vision_targets_per_input: int = 8
    digital_population_size: int = 8
    projection_dimensions: int = 5
    allocation_beta: float = 5.0
    base_energy_price: float = 0.1
    pressure_energy_weight: float = 0.4
    pressure_thermal_weight: float = 0.25
    pressure_compute_weight: float = 0.2
    pressure_memory_weight: float = 0.15
    synaptic_plasticity_enabled: bool = False
    structural_plasticity_enabled: bool = False
    meta_gating_enabled: bool = False
    adaptive_allocation_enabled: bool = False

    def __post_init__(self) -> None:
        validate_projection_dimensions(self.projection_dimensions)

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "audio_bands": self.audio_bands,
            "audio_max_delay_ms": self.audio_max_delay_ms,
            "vision_width": self.vision_width,
            "vision_height": self.vision_height,
            "vision_targets_per_input": self.vision_targets_per_input,
            "digital_population_size": self.digital_population_size,
            "projection_dimensions": self.projection_dimensions,
            "projection_dimensions_min": MIN_PROJECTION_DIMENSIONS,
            "projection_dimensions_max": MAX_PROJECTION_DIMENSIONS,
            "allocation_beta": self.allocation_beta,
            "base_energy_price": self.base_energy_price,
            "synaptic_plasticity_enabled": self.synaptic_plasticity_enabled,
            "structural_plasticity_enabled": self.structural_plasticity_enabled,
            "meta_gating_enabled": self.meta_gating_enabled,
            "adaptive_allocation_enabled": self.adaptive_allocation_enabled,
            "requires_preregistration": True,
            "requires_experiment_mode": True,
            "core_learning_rules_unchanged": True,
        }


@dataclass(frozen=True, slots=True)
class EnergyCoefficients:
    """Normalized energy-unit coefficients; not physical joule calibration."""

    spike: float = 1.0
    synaptic_event: float = 1.0
    plasticity_update: float = 3.0
    structural_event: float = 20.0
    memory_byte: float = 0.0001
    io_byte: float = 0.0002
    adapter_base: float = 1.0

    def to_json(self) -> dict[str, JSONValue]:
        """Return the normalized accounting coefficients as provenance data."""

        return {
            "spike": self.spike,
            "synaptic_event": self.synaptic_event,
            "plasticity_update": self.plasticity_update,
            "structural_event": self.structural_event,
            "memory_byte": self.memory_byte,
            "io_byte": self.io_byte,
            "adapter_base": self.adapter_base,
            "units_are_not_physical_joules": True,
        }


@dataclass(frozen=True, slots=True)
class EnergyObservation:
    sensor_units: float = 0.0
    encoder_units: float = 0.0
    spikes: int = 0
    synaptic_events: int = 0
    plasticity_updates: int = 0
    structural_events: int = 0
    memory_bytes: int = 0
    io_bytes: int = 0
    adapter_units: float = 0.0
    measured_joules: float | None = None


@dataclass(frozen=True, slots=True)
class EnergyEstimate:
    normalized_energy_units: float
    estimated_joules: float | None
    measured_joules: float | None
    component_units: dict[str, float] | None = None

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "normalized_energy_units": self.normalized_energy_units,
            "estimated_joules": self.estimated_joules,
            "measured_joules": self.measured_joules,
            "component_units": self.component_units or {},
            "provenance": {
                "normalized_energy_units": "NORMALIZED_MODEL_ESTIMATE",
                "estimated_joules": (
                    "CALIBRATED_CONVERSION"
                    if self.estimated_joules is not None
                    else "NOT_AVAILABLE"
                ),
                "measured_joules": (
                    "DIRECT_TELEMETRY"
                    if self.measured_joules is not None
                    else "NOT_AVAILABLE"
                ),
            },
            "estimated_is_not_measured": True,
        }


@dataclass(frozen=True, slots=True)
class ResourcePressure:
    energy: float = 0.0
    thermal: float = 0.0
    compute: float = 0.0
    memory: float = 0.0
    fan_failure: bool = False
    thermal_safety_trip: bool = False
    persistence_failure: bool = False


@dataclass(frozen=True, slots=True)
class SymbolFrame:
    """Exact digital payload kept outside the lossy SNN representation."""

    payload: bytes
    codec: str = "raw"
    sequence: int = 0
    provenance: str = ""

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.payload).hexdigest()

    def deterministic_population(self, population_size: int = 8) -> tuple[int, ...]:
        """Map payload bytes to a deterministic, fixed-width population code."""

        if population_size <= 0:
            raise ValueError("population_size must be positive")
        digest = hashlib.sha256(self.payload).digest()
        return tuple(digest[index] % 2 for index in range(population_size))

    def to_json(self) -> dict[str, JSONValue]:
        """Persist digital provenance without replacing the exact payload."""

        return {
            "codec": self.codec,
            "sequence": self.sequence,
            "provenance": self.provenance,
            "payload_size_bytes": len(self.payload),
            "checksum_algorithm": "sha256",
            "checksum": self.checksum,
        }


@dataclass(frozen=True, slots=True)
class EmbodimentTreatmentProvenance:
    """Immutable DATA record for an explicit adapter/gateway treatment."""

    adapter_id: str
    adapter_architecture: str
    projection_mode: str = "structured"
    projection_dimensions: int = 5
    gateway: MSBAGatewayConfig = MSBAGatewayConfig()
    energy: EnergyCoefficients = EnergyCoefficients()

    def __post_init__(self) -> None:
        if not self.adapter_id.strip():
            raise ValueError("adapter_id must not be empty")
        if not self.adapter_architecture.strip():
            raise ValueError("adapter_architecture must not be empty")
        if not self.projection_mode.strip():
            raise ValueError("projection_mode must not be empty")
        validate_projection_dimensions(self.projection_dimensions)

    def to_json(self) -> dict[str, JSONValue]:
        """Return a deterministic, non-EVID treatment provenance record."""

        record: dict[str, JSONValue] = {
            "schema_version": 1,
            "record_type": "embodiment_treatment_provenance",
            "status": "DATA_ONLY",
            "adapter": {
                "id": self.adapter_id,
                "architecture": self.adapter_architecture,
            },
            "projection": {
                "mode": self.projection_mode,
                "dimensions": self.projection_dimensions,
                "productive_core_dimensions": 5,
            },
            "gateway": self.gateway.to_json(),
            "energy": self.energy.to_json(),
            "scientific_boundary": {
                "requires_preregistration": True,
                "requires_human_review": True,
                "does_not_promote_to_evid": True,
            },
        }
        canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
        record["record_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return record


@dataclass(frozen=True, slots=True)
class ModalityProfile:
    modality: Modality
    pathway: str
    coordinate_features: tuple[str, ...]
    plasticity: str
    throttles: tuple[str, ...]
    exact_payload_outside_snn: bool = False

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "modality": self.modality.value,
            "pathway": self.pathway,
            "coordinate_features": list(self.coordinate_features),
            "plasticity": self.plasticity,
            "throttles": list(self.throttles),
            "exact_payload_outside_snn": self.exact_payload_outside_snn,
        }


def default_modality_profiles() -> tuple[ModalityProfile, ...]:
    """Return MSBA profiles without assigning semantics to fixed axes."""

    return (
        ModalityProfile(
            Modality.AUDIO,
            "temporal_coherence",
            ("band", "phase_or_envelope", "channel", "lag", "feature"),
            "phase_weighted_t_stdp_candidate",
            ("band_count", "update_rate", "delay_taps", "encoder_complexity"),
        ),
        ModalityProfile(
            Modality.VISION,
            "spatial_multiplex",
            ("x", "y", "feature", "scale", "frame"),
            "s_stdp_plus_structural_growth_candidate",
            ("fps", "resolution", "roi", "feature_channels", "plasticity"),
        ),
        ModalityProfile(
            Modality.DIGITAL,
            "quantized_high_fidelity",
            ("symbol", "sequence", "source", "context", "route"),
            "population_meta_gating_candidate",
            ("symbol_rate", "batching", "admission", "gateway_duty_cycle"),
            exact_payload_outside_snn=True,
        ),
    )


def energy_units(
    observation: EnergyObservation,
    coefficients: EnergyCoefficients = EnergyCoefficients(),
    *,
    joules_per_unit: float | None = None,
) -> EnergyEstimate:
    """Estimate resource cost while keeping measured and estimated joules distinct."""

    values = (
        observation.sensor_units,
        observation.encoder_units,
        observation.spikes,
        observation.synaptic_events,
        observation.plasticity_updates,
        observation.structural_events,
        observation.memory_bytes,
        observation.io_bytes,
    )
    if any(value < 0 for value in values):
        raise ValueError("energy counters must be non-negative")
    units = (
        observation.sensor_units
        + observation.encoder_units
        + coefficients.adapter_base
        + observation.adapter_units
        + coefficients.spike * observation.spikes
        + coefficients.synaptic_event * observation.synaptic_events
        + coefficients.plasticity_update * observation.plasticity_updates
        + coefficients.structural_event * observation.structural_events
        + coefficients.memory_byte * observation.memory_bytes
        + coefficients.io_byte * observation.io_bytes
    )
    components = {
        "sensor": float(observation.sensor_units),
        "encoder": float(observation.encoder_units),
        "spikes": float(coefficients.spike * observation.spikes),
        "synaptic_events": float(
            coefficients.synaptic_event * observation.synaptic_events
        ),
        "plasticity": float(
            coefficients.plasticity_update * observation.plasticity_updates
        ),
        "structural": float(
            coefficients.structural_event * observation.structural_events
        ),
        "memory": float(coefficients.memory_byte * observation.memory_bytes),
        "io": float(coefficients.io_byte * observation.io_bytes),
        "adapter": float(coefficients.adapter_base + observation.adapter_units),
    }
    estimated = None if joules_per_unit is None else units * joules_per_unit
    return EnergyEstimate(
        float(units), estimated, observation.measured_joules, components
    )


def resource_pressure(
    pressure: ResourcePressure, config: MSBAGatewayConfig = MSBAGatewayConfig()
) -> float:
    """Return clipped soft resource pressure; fan failure is a hard safety override."""

    if (
        pressure.fan_failure
        or pressure.thermal_safety_trip
        or pressure.persistence_failure
    ):
        return 1.0
    terms = (
        config.pressure_energy_weight * _unit(pressure.energy)
        + config.pressure_thermal_weight * _unit(pressure.thermal)
        + config.pressure_compute_weight * _unit(pressure.compute)
        + config.pressure_memory_weight * _unit(pressure.memory)
    )
    return _unit(terms)


def energy_state(pressure: ResourcePressure) -> EnergyState:
    """Map resource pressure to a deterministic protection state."""

    if (
        pressure.fan_failure
        or pressure.thermal_safety_trip
        or pressure.persistence_failure
    ):
        return EnergyState.SURVIVAL
    level = resource_pressure(pressure)
    if level >= 0.85:
        return EnergyState.SURVIVAL
    if level >= 0.65:
        return EnergyState.CRITICAL
    if level >= 0.35:
        return EnergyState.CONSERVE
    return EnergyState.NORMAL


def energy_price(
    pressure: ResourcePressure, config: MSBAGatewayConfig = MSBAGatewayConfig()
) -> float:
    """Return the dynamic internal price used by soft allocation experiments."""

    return config.base_energy_price + resource_pressure(pressure)


def allocation_gate(
    utility: float,
    cost: float,
    pressure: ResourcePressure,
    threshold: float = 0.0,
    config: MSBAGatewayConfig = MSBAGatewayConfig(),
) -> float:
    """Return a candidate gateway quota in [0, 1] without activating a gateway."""

    if cost < 0.0:
        raise ValueError("cost must be non-negative")
    if (
        pressure.fan_failure
        or pressure.thermal_safety_trip
        or pressure.persistence_failure
    ):
        return 0.0
    drive = utility - energy_price(pressure, config) * cost - threshold
    return _sigmoid(config.allocation_beta * drive)


def phase_coherence(delta_phase_rad: float) -> float:
    """Non-negative phase term preserving the sign of the underlying STDP rule."""

    return 0.5 * (1.0 + math.cos(delta_phase_rad))


def phase_weighted_stdp(stdp_delta: float, delta_phase_rad: float) -> float:
    """Scale candidate temporal STDP by phase coherence without sign inversion."""

    return stdp_delta * phase_coherence(delta_phase_rad)


def visual_growth_probability(
    information_value: float,
    distance_5d: float,
    sigma: float,
    pressure: ResourcePressure,
    eta_growth: float = 0.001,
) -> float:
    """Candidate visual sprouting probability using utility, locality and energy."""

    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    if distance_5d < 0.0:
        raise ValueError("distance_5d must be non-negative")
    locality = math.exp(-(distance_5d**2) / (2.0 * sigma**2))
    availability = 1.0 - resource_pressure(pressure)
    return _unit(eta_growth * max(0.0, information_value) * locality * availability)


def recommended_protection_policy(state: EnergyState) -> dict[str, JSONValue]:
    """Return deterministic throttling guidance; it never mutates runtime state."""

    policies: dict[EnergyState, dict[str, JSONValue]] = {
        EnergyState.NORMAL: {
            "plasticity": "experiment_policy",
            "vision": "full_budget",
            "audio": "full_budget",
            "digital": "full_budget",
        },
        EnergyState.CONSERVE: {
            "plasticity": "reduce_first",
            "vision": "reduce_fps_then_resolution",
            "audio": "reduce_bands_or_update_rate",
            "digital": "reduce_admission_rate",
        },
        EnergyState.CRITICAL: {
            "plasticity": "freeze",
            "vision": "roi_low_resolution",
            "audio": "reduced_bands",
            "digital": "priority_symbols_only",
        },
        EnergyState.SURVIVAL: {
            "plasticity": "freeze",
            "vision": "off_unless_safety_critical",
            "audio": "minimal_unless_safety_critical",
            "digital": "safety_and_persistence_only",
            "preserve": [
                "thermal_sensing",
                "fan_monitoring",
                "core_persistence",
                "storage_integrity",
                "emergency_actuator_path",
            ],
        },
    }
    return policies[state]


def msba_contract() -> dict[str, JSONValue]:
    """Publish the complete read-only MSBA architecture contract."""

    config = MSBAGatewayConfig()
    return {
        "name": "Modalitaets-spezifische Synaptische Bahn-Architektur",
        "acronym": "MSBA",
        "scope": "neural_symbiosis.embodiment",
        "status": "experimental_contract",
        "profiles": [profile.to_json() for profile in default_modality_profiles()],
        "gateway": config.to_json(),
        "energy_accounting": {
            "components": [
                "sensor",
                "encoder",
                "spikes",
                "synaptic_events",
                "plasticity",
                "structural_growth",
                "memory",
                "io",
                "adapter",
            ],
            "reported_fields": [
                "normalized_energy_units",
                "estimated_joules",
                "measured_joules",
            ],
            "provenance_classes": {
                "normalized_energy_units": "NORMALIZED_MODEL_ESTIMATE",
                "estimated_joules": "CALIBRATED_CONVERSION",
                "measured_joules": "DIRECT_TELEMETRY",
                "missing": "NOT_AVAILABLE",
            },
            "estimated_is_not_measured": True,
        },
        "topology": {
            "fixed_axis_semantics": False,
            "projection_required": True,
            "projection_dimensions": config.projection_dimensions,
            "projection_dimensions_range": [
                MIN_PROJECTION_DIMENSIONS,
                MAX_PROJECTION_DIMENSIONS,
            ],
            "productive_core_dimensions": 5,
            "core_dimension_migration_required_above_five": True,
            "controls": [
                "structured_projection",
                "shuffled_projection",
                "random_projection",
                "reduced_dimension_projection",
                "increased_dimension_projection",
            ],
        },
        "scientific_boundary": {
            "core_imports": False,
            "core_mutation": False,
            "learning_disabled_by_default": True,
            "structural_growth_disabled_by_default": True,
            "digital_payload_outside_snn": True,
            "digital_checksum_persisted": True,
            "reachability_is_not_learned_use": True,
            "historical_data_unchanged": True,
            "activation_requires_preregistered_experiment": True,
        },
    }


def _unit(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        inverse = math.exp(-value)
        return 1.0 / (1.0 + inverse)
    exponent = math.exp(value)
    return exponent / (1.0 + exponent)


__all__ = [
    "EnergyCoefficients",
    "EnergyEstimate",
    "EnergyObservation",
    "EnergyState",
    "MAX_PROJECTION_DIMENSIONS",
    "MIN_PROJECTION_DIMENSIONS",
    "MSBAGatewayConfig",
    "Modality",
    "ModalityProfile",
    "ResourcePressure",
    "SymbolFrame",
    "allocation_gate",
    "default_modality_profiles",
    "energy_price",
    "energy_state",
    "energy_units",
    "msba_contract",
    "phase_coherence",
    "phase_weighted_stdp",
    "recommended_protection_policy",
    "resource_pressure",
    "validate_projection_dimensions",
    "visual_growth_probability",
]
