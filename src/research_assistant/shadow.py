"""Non-executing shadow mode for scientific AI proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .contracts import Interpretation, Observation, Proposal, ScientificContract
from .firewall import AIAuthority, ScientificAIFirewall


@dataclass(frozen=True, slots=True)
class ShadowResult:
    """A marked shadow output that has not been applied to system state."""

    contract: ScientificContract
    executed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"executed": self.executed, "contract": self.contract.to_dict()}


@dataclass(frozen=True, slots=True)
class ShadowProposalMetrics:
    """Deterministic metrics for comparing shadow proposals with outcomes."""

    precision: float
    recall: float
    false_positive_rate: float
    prediction_accuracy: float
    brier_score: float
    expected_calibration_error: float
    utility: float
    sample_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "precision": self.precision,
            "recall": self.recall,
            "false_positive_rate": self.false_positive_rate,
            "prediction_accuracy": self.prediction_accuracy,
            "brier_score": self.brier_score,
            "expected_calibration_error": self.expected_calibration_error,
            "utility": self.utility,
            "sample_count": self.sample_count,
        }


def evaluate_shadow_proposals(
    predicted: Sequence[bool],
    actual: Sequence[bool],
    *,
    confidence: Sequence[float] | None = None,
    utility: Sequence[float] | None = None,
) -> ShadowProposalMetrics:
    """Evaluate proposals without interpreting or executing their contents."""
    if not predicted or len(predicted) != len(actual):
        raise ValueError(
            "Predicted and actual proposal labels must have equal non-zero length."
        )
    if confidence is not None and len(confidence) != len(predicted):
        raise ValueError("Confidence values must match proposal count.")
    if utility is not None and len(utility) != len(predicted):
        raise ValueError("Utility values must match proposal count.")
    if confidence is not None and any(value < 0 or value > 1 for value in confidence):
        raise ValueError("Confidence values must be between 0 and 1.")

    true_positive = sum(
        predicted_value and actual_value
        for predicted_value, actual_value in zip(predicted, actual)
    )
    false_positive = sum(
        predicted_value and not actual_value
        for predicted_value, actual_value in zip(predicted, actual)
    )
    false_negative = sum(
        not predicted_value and actual_value
        for predicted_value, actual_value in zip(predicted, actual)
    )
    true_negative = sum(
        not predicted_value and not actual_value
        for predicted_value, actual_value in zip(predicted, actual)
    )
    count = len(predicted)
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    false_positive_rate = (
        false_positive / (false_positive + true_negative)
        if false_positive + true_negative
        else 0.0
    )
    accuracy = (true_positive + true_negative) / count
    probabilities = list(confidence or [float(value) for value in predicted])
    brier_score = (
        sum(
            (probability - float(outcome)) ** 2
            for probability, outcome in zip(probabilities, actual)
        )
        / count
    )
    calibration_bins = [0.0] * 10
    calibration_counts = [0] * 10
    for probability, outcome in zip(probabilities, actual):
        index = min(int(probability * 10), 9)
        calibration_bins[index] += float(outcome)
        calibration_counts[index] += 1
    expected_calibration_error = (
        sum(
            abs(
                calibration_bins[index] / calibration_counts[index] - (index + 0.5) / 10
            )
            * calibration_counts[index]
            for index in range(10)
            if calibration_counts[index]
        )
        / count
    )
    measured_utility = sum(utility or [float(value) for value in predicted]) / count
    return ShadowProposalMetrics(
        precision=precision,
        recall=recall,
        false_positive_rate=false_positive_rate,
        prediction_accuracy=accuracy,
        brier_score=brier_score,
        expected_calibration_error=expected_calibration_error,
        utility=measured_utility,
        sample_count=count,
    )


class ShadowMode:
    """Allow observation, interpretation and proposals without execution."""

    def __init__(self) -> None:
        self._firewall = ScientificAIFirewall(AIAuthority.PROPOSAL_ONLY)

    def observe(self, payload: object, *, source: str = "shadow") -> ShadowResult:
        self._firewall.authorize("observe")
        return ShadowResult(
            Observation.create(payload=payload, source=source, authority="read_only")
        )

    def interpret(self, payload: object, *, source: str = "shadow") -> ShadowResult:
        self._firewall.authorize("interpret")
        return ShadowResult(
            Interpretation.create(payload=payload, source=source, authority="read_only")
        )

    def propose(self, payload: object, *, source: str = "shadow") -> ShadowResult:
        self._firewall.authorize("propose")
        return ShadowResult(
            Proposal.create(payload=payload, source=source, authority="proposal_only")
        )
