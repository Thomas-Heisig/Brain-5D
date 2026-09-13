"""Temporary deterministic patcher for Stage-0 model-selection integration."""

from pathlib import Path
import re


def sub(path: str, pattern: str, replacement: str, count: int = 1) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    new, n = re.subn(pattern, replacement, text, count=count, flags=re.S)
    if n != count:
        raise SystemExit(f"{path}: expected {count} replacement(s), got {n}")
    p.write_text(new, encoding="utf-8")


def patch_network() -> None:
    p = Path("src/core/network.py")
    text = p.read_text(encoding="utf-8")
    text = text.replace("from typing import Any\n", "from typing import Any, cast\n", 1)
    marker = '        net = data.get("network", {})\n\n        return cls(\n'
    if marker not in text:
        raise SystemExit("network from_dict insertion marker missing")
    text = text.replace(
        marker,
        '        net = data.get("network", {})\n'
        '        neuron_data = cast(dict[str, Any], data.get("neuron", {}))\n'
        '        energy_data = cast(dict[str, Any], data.get("energy", {}))\n'
        '        neuron_payload = dict(neuron_data)\n'
        '        neuron_payload.setdefault("dt_ms", float(sim.get("dt_ms", 1.0)))\n'
        '        neuron_payload["spike_cost"] = float(\n'
        '            energy_data.get("spike_cost", neuron_payload.get("spike_cost", 0.001))\n'
        '        )\n'
        '        neuron_payload["resting_energy"] = float(\n'
        '            energy_data.get("initial", neuron_payload.get("resting_energy", 1.0))\n'
        '        )\n\n'
        '        return cls(\n',
        1,
    )
    old_neuron = re.compile(
        r"            neuron=NeuronConfig\(\n.*?            \),\n            synapse=SynapseConfig\(",
        re.S,
    )
    text, n = old_neuron.subn(
        "            neuron=NeuronConfig.from_dict(neuron_payload),\n"
        "            synapse=SynapseConfig(",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("legacy NeuronConfig construction block missing")
    p.write_text(text, encoding="utf-8")


def patch_loader() -> None:
    sub(
        "src/config/loader.py",
        r"class NeuronConfig\(TypedDict, total=False\):.*?\n\nclass SynapseConfig",
        '''class NeuronConfig(TypedDict, total=False):
    """Configuration for neuron parameters and dynamics model."""

    model: str
    a: float
    b: float
    c: float
    d: float
    initial_v: float
    initial_u: float
    izhikevich_threshold: float
    lif_resting_potential: float
    lif_tau_m_ms: float
    lif_resistance: float
    lif_threshold: float
    lif_reset: float
    refractory_ticks: int
    enable_threshold_adaptation: bool
    enable_energy_dynamics: bool
    enable_traces: bool
    enable_homeostasis: bool


class SynapseConfig''',
    )
    sub(
        "src/config/loader.py",
        r'    "neuron": \{.*?\n    \},\n    "energy":',
        '''    "neuron": {
        "model": "izhikevich-2003",
        "a": 0.02,
        "b": 0.2,
        "c": -65.0,
        "d": 8.0,
        "initial_v": -65.0,
        "initial_u": -13.0,
        "izhikevich_threshold": 30.0,
        "lif_resting_potential": -65.0,
        "lif_tau_m_ms": 20.0,
        "lif_resistance": 1.0,
        "lif_threshold": -50.0,
        "lif_reset": -65.0,
        "refractory_ticks": 0,
        "enable_threshold_adaptation": True,
        "enable_energy_dynamics": True,
        "enable_traces": True,
        "enable_homeostasis": True,
    },
    "energy":''',
    )
    sub(
        "src/config/loader.py",
        r"def _validate_neuron_config\(.*?\n\ndef _validate_synapse_config",
        '''def _validate_neuron_config(
    raw: dict[str, Any], defaults: NeuronConfig
) -> NeuronConfig:
    """Validate and normalize neuron model configuration."""
    result: NeuronConfig = {}

    model_raw = raw.get("model", defaults.get("model", "izhikevich-2003"))
    if not isinstance(model_raw, str):
        raise ValueError(
            f"neuron.model must be a string, got {type(model_raw).__name__}"
        )
    aliases = {
        "izh": "izhikevich-2003",
        "izhikevich": "izhikevich-2003",
        "izhikevich-2003": "izhikevich-2003",
        "lif": "lif-current-v1",
        "leaky-integrate-and-fire": "lif-current-v1",
        "lif-current-v1": "lif-current-v1",
    }
    try:
        result["model"] = aliases[model_raw.strip().lower()]
    except KeyError as exc:
        raise ValueError(
            f"unsupported neuron.model {model_raw!r}; expected izhikevich or lif"
        ) from exc

    numeric_keys = (
        "a", "b", "c", "d", "initial_v", "initial_u",
        "izhikevich_threshold", "lif_resting_potential", "lif_tau_m_ms",
        "lif_resistance", "lif_threshold", "lif_reset",
    )
    for key in numeric_keys:
        value = raw.get(key, defaults.get(key))
        if not isinstance(value, (int, float)):
            raise ValueError(f"neuron.{key} must be numeric")
        result[key] = float(value)  # type: ignore[literal-required]

    if result["lif_tau_m_ms"] <= 0.0:
        raise ValueError("neuron.lif_tau_m_ms must be > 0")

    refractory = raw.get("refractory_ticks", defaults.get("refractory_ticks", 0))
    if not isinstance(refractory, (int, float)):
        raise ValueError("neuron.refractory_ticks must be numeric")
    result["refractory_ticks"] = int(refractory)
    if result["refractory_ticks"] < 0:
        raise ValueError("neuron.refractory_ticks must be >= 0")

    for key in (
        "enable_threshold_adaptation", "enable_energy_dynamics",
        "enable_traces", "enable_homeostasis",
    ):
        value = raw.get(key, defaults.get(key, True))
        if not isinstance(value, bool):
            raise ValueError(f"neuron.{key} must be a boolean")
        result[key] = value  # type: ignore[literal-required]

    return result


def _validate_synapse_config''',
    )
    p = Path("src/config/loader.py")
    text = p.read_text(encoding="utf-8")
    needle = '''    net = config.get("network")
    if net:
        _validate_network_config(
            cast("dict[str, Any]", net), cast("NetworkConfig", defaults["network"])
        )
'''
    if needle not in text:
        raise SystemExit("validate_config network block missing")
    text = text.replace(
        needle,
        needle
        + '''
    neuron = config.get("neuron")
    if neuron:
        _validate_neuron_config(
            cast("dict[str, Any]", neuron), cast("NeuronConfig", defaults["neuron"])
        )
''',
        1,
    )
    p.write_text(text, encoding="utf-8")


def patch_timeline() -> None:
    sub(
        "src/dashboard/development_timeline.py",
        r"        StageSpec\(\n            0,.*?\n        \),\n        StageSpec\(\n            1,",
        '''        StageSpec(
            0,
            "single_neuron",
            "Einzelne Nervenzelle",
            "Neuron",
            (
                "Einzelnes künstliches Neuron",
                "deterministische Membrandynamik",
                "Spike-, Reset- und Erholungsverhalten",
                "versionierte und umschaltbare Neuronenmodelle",
            ),
            {"neurons": "1", "synapses": "0-1"},
            (
                CriterionSpec(
                    "neuron_model",
                    "Versioned neuron model",
                    paths=("src/core/neuron.py", "src/core/neuron_models.py"),
                    tests=("tests/test_single_neuron_contract.py",),
                    verification=("research/generated/verification/single_neuron_reference.json",),
                ),
                CriterionSpec(
                    "membrane_dynamics",
                    "Deterministic membrane dynamics",
                    paths=("src/core/neuron.py", "src/core/neuron_models.py"),
                    tests=("tests/test_single_neuron_contract.py",),
                    verification=("research/generated/verification/single_neuron_reference.json",),
                ),
                CriterionSpec(
                    "spike_and_refractory",
                    "Spike, reset, recovery and refractory variant",
                    tests=("tests/test_single_neuron_contract.py",),
                    verification=("research/generated/verification/single_neuron_reference.json",),
                ),
                CriterionSpec(
                    "single_cell_verification",
                    "Deterministic replay and state continuation",
                    tests=("tests/test_single_neuron_contract.py",),
                    verification=("research/generated/verification/single_neuron_reference.json",),
                ),
                CriterionSpec(
                    "model_switch_provenance",
                    "Model selection and provenance",
                    paths=("src/core/neuron_models.py",),
                    tests=("tests/test_single_neuron_contract.py",),
                    verification=("research/generated/verification/single_neuron_reference.json",),
                ),
            ),
            ("src/core/neuron.py", "src/core/neuron_models.py"),
            ("tests/test_neuron.py", "tests/test_single_neuron_contract.py"),
            (),
            (),
            ("This stage is a software primitive, not evidence of biological equivalence.",),
            (),
            (),
        ),
        StageSpec(
            1,''',
    )


def patch_tests() -> None:
    p = Path("tests/test_single_neuron_contract.py")
    text = p.read_text(encoding="utf-8")
    text = text.replace(
        "from src.core.neuron import (",
        "from src.config import load_config\nfrom src.core.network import Brain5DConfig\nfrom src.core.neuron import (",
        1,
    )
    text += '''


def test_yaml_model_selection_reaches_core_config(tmp_path: Path) -> None:
    path = tmp_path / "lif.yaml"
    path.write_text(
        "dimensions: [2, 2, 2, 2, 2]\\n"
        "initial_neurons: 1\\n"
        "neuron:\\n"
        "  model: lif\\n"
        "  lif_tau_m_ms: 15.0\\n"
        "  lif_threshold: -52.0\\n"
        "  refractory_ticks: 2\\n",
        encoding="utf-8",
    )
    loaded = load_config(path)
    assert loaded["neuron"]["model"] == "lif-current-v1"
    config = Brain5DConfig.from_dict(dict(loaded))
    assert config.neuron.model is NeuronModel.LEAKY_INTEGRATE_AND_FIRE
    assert config.neuron.lif_tau_m_ms == 15.0
    assert config.neuron.lif_threshold == -52.0
    assert config.neuron.refractory_ticks == 2


def test_yaml_unknown_model_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_text(
        "dimensions: [2, 2, 2, 2, 2]\\n"
        "initial_neurons: 1\\n"
        "neuron:\\n"
        "  model: unknown-theory\\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unsupported neuron.model"):
        load_config(path)
'''
    p.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch_network()
    patch_loader()
    patch_timeline()
    patch_tests()
