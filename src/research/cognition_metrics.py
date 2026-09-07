"""Bounded cognitive-task instruments, not a consciousness detector.

Stimulus generators and scoring operate on explicit inputs only. Test fixtures
are synthetic; these functions never execute, train, or certify Brain-5D.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from statistics import NormalDist, mean
from typing import Sequence


@dataclass(frozen=True)
class Stimulus:
    """Public stimulus; target annotations are deliberately stored separately."""

    trial_id: int
    sample: int
    probe: int
    delay_ticks: int


def _positive_int(value: int, name: str) -> None:
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def _finite(values: Sequence[float]) -> None:
    if not values or any(not math.isfinite(v) for v in values):
        raise ValueError("Non-empty finite observations are required")


def dmts_trials(
    seed: int,
    *,
    repeats: int = 8,
    symbols: int = 4,
    delays: tuple[int, ...] = (0, 10, 100),
) -> tuple[list[Stimulus], dict[int, int]]:
    """Exactly balance match/non-match at every sample and delay.

    Returns presentation records and private answer key. The adapter MUST NOT
    expose the key, future probe, trial seed, or whole schedule to the system.
    Present sample, blank delay, then probe via the registered event interface.
    """
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if 2 * repeats * symbols * len(delays) > 100000:
        raise ValueError("DMTS instrument budget exceeded")
    _positive_int(repeats, "repeats")
    _positive_int(symbols, "symbols")
    if symbols < 2 or not delays or len(set(delays)) != len(delays):
        raise ValueError("At least two symbols and distinct delays are required")
    if any(type(d) is not int or d < 0 for d in delays):
        raise ValueError("Delays must be non-negative integers")
    rng = random.Random(seed)
    raw: list[tuple[int, int, int, int]] = []
    for delay in delays:
        for sample in range(symbols):
            for _ in range(repeats):
                raw.append((sample, sample, delay, 1))
                alternative = rng.randrange(symbols - 1)
                probe = alternative + int(alternative >= sample)
                raw.append((sample, probe, delay, 0))
    rng.shuffle(raw)
    stimuli = [Stimulus(i, s, p, d) for i, (s, p, d, _) in enumerate(raw)]
    return stimuli, {i: y for i, (_, _, _, y) in enumerate(raw)}


def oddball_schedule(
    seed: int,
    *,
    trials: int = 200,
    deviants: int = 40,
    standard: int = 0,
    deviant: int = 1,
) -> tuple[list[int], list[bool]]:
    """Fixed-count random oddball schedule; not the full adaptation control.

    Reversed identities and equiprobable/many-standards blocks are separately
    required by the protocol. Consecutive deviants are allowed and recorded;
    no refractory scheduling rule or clinical timing is silently assumed.
    """
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if trials > 100000:
        raise ValueError("Oddball instrument budget exceeded")
    _positive_int(trials, "trials")
    if type(deviants) is not int:
        raise ValueError("deviants must be an integer")
    if not 0 < deviants < trials or standard == deviant:
        raise ValueError("Both distinct stimulus classes are required")
    flags = [True] * deviants + [False] * (trials - deviants)
    random.Random(seed).shuffle(flags)
    return [deviant if flag else standard for flag in flags], flags


def accuracy_by_delay(
    stimuli: Sequence[Stimulus],
    answers: dict[int, int],
    responses: dict[int, int],
) -> dict[int, dict[str, float | int]]:
    """Score every scheduled trial; omissions count as incorrect, not exclusions."""
    ids = [trial.trial_id for trial in stimuli]
    if not ids or len(set(ids)) != len(ids) or set(answers) != set(ids):
        raise ValueError("Unique trials and a complete answer key are required")
    if not set(responses) <= set(ids):
        raise ValueError("Unknown response trial")
    if any(type(v) is not int or v not in (0, 1) for v in answers.values()):
        raise ValueError("Answer values must be binary integers")
    if any(type(v) is not int or v not in (0, 1) for v in responses.values()):
        raise ValueError("Response values must be binary integers")
    result: dict[int, dict[str, float | int]] = {}
    for delay in sorted({trial.delay_ticks for trial in stimuli}):
        selected = [trial for trial in stimuli if trial.delay_ticks == delay]
        correct = sum(
            responses.get(t.trial_id, -1) == answers[t.trial_id] for t in selected
        )
        missing = sum(t.trial_id not in responses for t in selected)
        result[delay] = {
            "n": len(selected),
            "correct": correct,
            "omissions": missing,
            "accuracy": correct / len(selected),
        }
    return result


def signal_detection(
    hits: int, misses: int, false_alarms: int, correct_rejections: int
) -> dict[str, float]:
    """Type-1 d-prime with explicitly declared log-linear (0.5) correction."""
    counts = (hits, misses, false_alarms, correct_rejections)
    if any(type(v) is not int or v < 0 for v in counts):
        raise ValueError("Counts must be non-negative integers")
    if hits + misses == 0 or false_alarms + correct_rejections == 0:
        raise ValueError("Signal and noise trials are both required")
    h = (hits + 0.5) / (hits + misses + 1)
    f = (false_alarms + 0.5) / (false_alarms + correct_rejections + 1)
    zh, zf = NormalDist().inv_cdf(h), NormalDist().inv_cdf(f)
    return {
        "d_prime": zh - zf,
        "criterion": -(zh + zf) / 2,
        "corrected_hit_rate": h,
        "corrected_false_alarm_rate": f,
    }


def confidence_scores(
    correct: Sequence[int], confidence: Sequence[float]
) -> dict[str, float | None]:
    """Brier and type-2 AUROC; neither is meta-d-prime or proof of introspection.

    Confidence must be probability that the chosen answer is correct. AUC is
    unavailable when all trials have the same outcome. Ties contribute 0.5.
    """
    _finite(confidence)
    if len(correct) != len(confidence) or any(
        type(y) is not int or y not in (0, 1) for y in correct
    ):
        raise ValueError("Aligned binary correctness values are required")
    if any(not 0 <= p <= 1 for p in confidence):
        raise ValueError("Confidence probabilities must lie in [0, 1]")
    positives = sum(correct)
    negatives = len(correct) - positives
    auc = None
    if positives and negatives:
        ordered = sorted(zip(confidence, correct))
        wins = 0.0
        negatives_before = 0
        index = 0
        while index < len(ordered):
            stop = index + 1
            while stop < len(ordered) and ordered[stop][0] == ordered[index][0]:
                stop += 1
            group_positives = sum(label for _, label in ordered[index:stop])
            group_negatives = stop - index - group_positives
            wins += group_positives * (negatives_before + 0.5 * group_negatives)
            negatives_before += group_negatives
            index = stop
        auc = wins / (positives * negatives)
    return {
        "brier": mean((p - y) ** 2 for y, p in zip(correct, confidence)),
        "type2_auroc": auc,
        "meta_d_prime": None,
    }


def paired_effect(
    control: Sequence[float], treatment: Sequence[float]
) -> dict[str, float | int | None]:
    """Descriptive per-initialization contrast; no automatic p-value or verdict."""
    _finite(control)
    _finite(treatment)
    if len(control) != len(treatment):
        raise ValueError("Paired conditions must have equal length")
    differences = [b - a for a, b in zip(control, treatment)]
    n = len(differences)
    estimate = mean(differences)
    se = (
        None
        if n < 2
        else math.sqrt(sum((d - estimate) ** 2 for d in differences) / (n * (n - 1)))
    )
    return {"n_pairs": n, "mean_difference": estimate, "standard_error": se}


@dataclass(frozen=True)
class SignalContract:
    """Declared observation model; metadata alone does not validate its physics."""

    kind: str
    units: str
    sampling_hz: float
    observation_model: str
    preprocessing: str


def compare_evoked(
    reference: Sequence[float],
    candidate: Sequence[float],
    *,
    reference_contract: SignalContract,
    candidate_contract: SignalContract,
) -> dict[str, float | str]:
    """Compare pre-aligned evoked signals only with compatible EEG contracts.

    Population spike activity and LFP proxies cannot be relabelled as EEG here.
    Channel/source mapping, reference montage, artifact handling and calibration
    still require external validation. Correlation is not an equivalence test.
    """
    _finite(reference)
    _finite(candidate)
    if len(reference) != len(candidate) or len(reference) < 3:
        raise ValueError("At least three aligned signal samples are required")
    for contract in (reference_contract, candidate_contract):
        if contract.kind not in {"measured_eeg", "forward_model_eeg"}:
            raise ValueError(
                "EEG comparison requires a measured or forward-model EEG signal"
            )
        if not math.isfinite(contract.sampling_hz) or contract.sampling_hz <= 0:
            raise ValueError("Sampling rate must be finite and positive")
        if not contract.observation_model.strip() or not contract.preprocessing.strip():
            raise ValueError("Observation model and preprocessing must be declared")
    if (
        reference_contract.units not in {"V", "mV", "uV"}
        or reference_contract.units != candidate_contract.units
        or reference_contract.sampling_hz != candidate_contract.sampling_hz
        or reference_contract.preprocessing != candidate_contract.preprocessing
    ):
        raise ValueError("Units, sampling rate and preprocessing must match explicitly")
    a, b = mean(reference), mean(candidate)
    va = sum((x - a) ** 2 for x in reference)
    vb = sum((x - b) ** 2 for x in candidate)
    if va == 0 or vb == 0:
        raise ValueError("Correlation is undefined for constant signals")
    correlation = sum(
        (x - a) * (y - b) for x, y in zip(reference, candidate)
    ) / math.sqrt(va * vb)
    return {
        "correlation": max(-1.0, min(1.0, correlation)),
        "rmse": math.sqrt(mean((x - y) ** 2 for x, y in zip(reference, candidate))),
        "interpretation": "descriptive_only_not_equivalence_or_consciousness",
    }
