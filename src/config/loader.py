from pathlib import Path
import yaml


def load_config(path: str | Path) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    dims = tuple(cfg.get("dimensions", []))
    if len(dims) != 5 or any(int(d) <= 0 or int(d) > 256 for d in dims):
        raise ValueError("dimensions must contain five values in 1..256")
    total = 1
    for d in dims:
        total *= int(d)
    initial = int(cfg.get("initial_neurons", 0))
    if initial <= 0 or initial > total:
        raise ValueError("initial_neurons outside available positions")
    if float(cfg["simulation"].get("dt_ms", 0)) != 1.0:
        raise ValueError("Sprint 1 reference core requires dt_ms=1.0")
    if int(cfg["simulation"].get("max_delay", 0)) < 1:
        raise ValueError("max_delay must be >=1")
    return cfg
