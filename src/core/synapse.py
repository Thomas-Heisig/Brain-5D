from dataclasses import dataclass

A_PLUS = 0.1
A_MINUS = 0.12
TAU_PLUS = 20.0
TAU_MINUS = 20.0


@dataclass(slots=True)
class Synapse:
    target_id: int
    weight: float
    delay: int
    eligibility: float = 0.0
    last_pre_spike: int = -1

    def __post_init__(self) -> None:
        if self.delay < 1:
            raise ValueError("delay must be >= 1")
