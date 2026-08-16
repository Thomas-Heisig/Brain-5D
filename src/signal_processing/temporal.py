"""Temporal helpers for signal windows."""


def window_duration_ms(tick_from: int, tick_to: int, *, dt_ms: float) -> float:
    """Return inclusive observation-window duration in milliseconds."""
    if dt_ms <= 0.0:
        raise ValueError("dt_ms must be positive")
    if tick_to < tick_from:
        raise ValueError("tick_to must be >= tick_from")
    return (tick_to - tick_from + 1) * dt_ms
