"""Apply narrow alpha.4 typing fixes to legacy modules in the working tree."""

from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    """Replace one known source fragment or fail loudly."""
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            return
        raise RuntimeError(f"expected fragment not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    """Apply the three non-storage mypy fixes identified in alpha.3."""
    replace_once(
        Path("src/manipulation/manipulator.py"),
        "nid = self.network.add_neuron(coord)",
        "nid = int(self.network.add_neuron(coord))",
    )
    engine = Path("src/self_organization/engine.py")
    replace_once(
        engine,
        (
            "from src.core.spatial_index import iter_neighbour_coords, "
            "pack_coords, unpack_coords"
        ),
        "from src.core.spatial_index import (\n"
        "    Coord5D,\n"
        "    iter_neighbour_coords,\n"
        "    pack_coords,\n"
        "    unpack_coords,\n"
        ")",
    )
    replace_once(
        engine,
        "def _find_free_coord(self, neuron_id: int):",
        "def _find_free_coord(self, neuron_id: int) -> Coord5D | None:",
    )
    learning_lab = Path("src/experiments/learning_lab.py")
    replace_once(
        learning_lab,
        "from src.core.network import NeuralNetwork",
        "from src.core.network import ConfigDict, NeuralNetwork",
    )
    replace_once(
        learning_lab,
        (
            "network = NeuralNetwork(dict(config), "
            "random.Random(int(config.get(\"seed\", 42))))"
        ),
        "network = NeuralNetwork(\n"
        "        cast(ConfigDict, dict(config)),\n"
        "        random.Random(int(config.get(\"seed\", 42))),\n"
        "    )",
    )
    print("Applied alpha.4 legacy typing fixes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
