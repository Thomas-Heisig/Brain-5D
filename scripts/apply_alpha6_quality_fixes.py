"""Apply narrow v0.4.0-alpha.6 type-quality fixes to the current repository."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    """Replace one known source fragment, remaining idempotent after migration."""

    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Expected source fragment not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_manipulator() -> None:
    """Make create_neuron return explicitly typed int instead of Any."""

    path = ROOT / "src" / "manipulation" / "manipulator.py"
    replace_once(
        path,
        "nid = self.network.add_neuron(coord)",
        "nid = int(self.network.add_neuron(coord))",
    )


def patch_self_organization() -> None:
    """Give free-coordinate lookup an explicit Coord5D return contract."""

    path = ROOT / "src" / "self_organization" / "engine.py"
    text = path.read_text(encoding="utf-8")
    import_old = (
        "from src.core.spatial_index import iter_neighbour_coords, "
        "pack_coords, unpack_coords"
    )
    import_new = (
        "from src.core.spatial_index import (\n"
        "    Coord5D,\n"
        "    iter_neighbour_coords,\n"
        "    pack_coords,\n"
        "    unpack_coords,\n"
        ")"
    )
    if "Coord5D," not in text:
        if import_old not in text:
            raise RuntimeError("Self-organization spatial-index import not found")
        text = text.replace(import_old, import_new, 1)
    old_signature = "def _find_free_coord(self, neuron_id: int):"
    new_signature = "def _find_free_coord(self, neuron_id: int) -> Coord5D | None:"
    if new_signature not in text:
        if old_signature not in text:
            raise RuntimeError("_find_free_coord signature not found")
        text = text.replace(old_signature, new_signature, 1)
    path.write_text(text, encoding="utf-8")


def patch_learning_lab() -> None:
    """Align the experiment constructor with the typed core configuration."""

    path = ROOT / "src" / "experiments" / "learning_lab.py"
    text = path.read_text(encoding="utf-8")
    old_import = "from src.core.network import NeuralNetwork"
    new_import = "from src.core.network import ConfigDict, NeuralNetwork"
    if new_import not in text:
        if old_import not in text:
            raise RuntimeError("Learning-lab core import not found")
        text = text.replace(old_import, new_import, 1)
    old_line = (
        'network = NeuralNetwork(dict(config), '
        'random.Random(int(config.get("seed", 42))))'
    )
    new_lines = (
        "network_config = cast(ConfigDict, dict(config))\n"
        "    network = NeuralNetwork(\n"
        "        network_config, random.Random(int(config.get(\"seed\", 42)))\n"
        "    )"
    )
    if "network_config = cast(ConfigDict, dict(config))" not in text:
        if old_line not in text:
            raise RuntimeError("Learning-lab network constructor not found")
        text = text.replace(old_line, new_lines, 1)
    path.write_text(text, encoding="utf-8")


def patch_recovery_protocol_adapter() -> None:
    """Make SnapshotView satisfy the writer protocol's mutable attributes."""

    path = ROOT / "src" / "storage" / "recovery.py"
    replace_once(
        path,
        "@dataclass(frozen=True, slots=True)\nclass _SnapshotView:",
        "@dataclass(slots=True)\nclass _SnapshotView:",
    )


def main() -> None:
    """Apply all narrow quality fixes."""

    patch_manipulator()
    patch_self_organization()
    patch_learning_lab()
    patch_recovery_protocol_adapter()
    print("alpha.6 quality fixes applied")


if __name__ == "__main__":
    main()
