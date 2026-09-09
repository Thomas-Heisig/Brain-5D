"""Deterministic one-joint reference body (SI units), not an organism model.

Modelled work is a mechanics estimate, never measured computer energy. Integrity
signals describe boundary violations, not subjective pain. No clocks, UI state,
network access, or neural-state writes are used by this component.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class JointParameters:
    inertia_kg_m2: float = 0.00005
    damping_nm_s: float = 0.002
    torque_limit_nm: float = 0.015
    lower_rad: float = -0.75
    upper_rad: float = 0.75

    def __post_init__(self) -> None:
        if not all(math.isfinite(value) for value in asdict(self).values()):
            raise ValueError("Body parameters must be finite")
        if min(self.inertia_kg_m2, self.torque_limit_nm) <= 0:
            raise ValueError("Inertia and torque limit must be positive")
        if self.damping_nm_s < 0 or self.lower_rad >= self.upper_rad:
            raise ValueError("Invalid damping or joint range")


@dataclass
class JointWorld:
    parameters: JointParameters
    q_rad: float = 0.0
    omega_rad_s: float = 0.0
    elapsed_s: float = 0.0
    modelled_absolute_work_j: float = 0.0
    contact_count: int = 0
    saturation_count: int = 0

    def __post_init__(self) -> None:
        if not math.isfinite(self.q_rad) or not math.isfinite(self.omega_rad_s):
            raise ValueError("Initial joint state must be finite")
        if not self.parameters.lower_rad <= self.q_rad <= self.parameters.upper_rad:
            raise ValueError("Initial angle outside joint range")

    def advance(
        self,
        torque_nm: float,
        dt_s: float,
        *,
        external_torque_nm: float = 0.0,
        actuator_gain: float = 1.0,
        blocked: bool = False,
    ) -> float:
        """Semi-implicit Euler with hard joint stops; return applied motor torque."""
        if not all(
            math.isfinite(value)
            for value in (torque_nm, dt_s, external_torque_nm, actuator_gain)
        ):
            raise ValueError("Nonfinite body input")
        if not 0 < dt_s <= 0.015 or not 0 <= actuator_gain <= 1:
            raise ValueError("Body step/gain outside verified engineering envelope")
        limit = self.parameters.torque_limit_nm
        clipped = max(-limit, min(limit, torque_nm))
        self.saturation_count += int(clipped != torque_nm)
        applied = clipped * actuator_gain
        old_angle = self.q_rad
        if blocked:
            self.omega_rad_s = 0.0
        else:
            acceleration = (
                applied
                + external_torque_nm
                - self.parameters.damping_nm_s * self.omega_rad_s
            ) / self.parameters.inertia_kg_m2
            self.omega_rad_s += acceleration * dt_s
            proposed = self.q_rad + self.omega_rad_s * dt_s
            self.q_rad = max(
                self.parameters.lower_rad, min(self.parameters.upper_rad, proposed)
            )
            if proposed != self.q_rad:
                self.contact_count += 1
                self.omega_rad_s = 0.0
        self.modelled_absolute_work_j += abs(applied * (self.q_rad - old_angle))
        self.elapsed_s += dt_s
        if not all(
            math.isfinite(value)
            for value in (self.q_rad, self.omega_rad_s, self.modelled_absolute_work_j)
        ):
            raise ValueError("Nonfinite body state; retain failed run for audit")
        return applied

    def state(self) -> dict[str, object]:
        """Serializable physical state; display coordinates are deliberately absent."""
        return asdict(self)
