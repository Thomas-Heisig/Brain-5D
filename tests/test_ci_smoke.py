"""CI smoke tests — quick import, config, and basic sanity checks.

These tests run first in CI to catch catastrophic failures early.
They are all marked ``smoke`` and should complete in under 5 seconds.
"""

from __future__ import annotations

import pytest

# ============================================================================
# Import smoke tests
# ============================================================================


@pytest.mark.smoke
class TestCoreImports:
    """Verify every top-level src/ package imports cleanly."""

    def test_core_neuron(self) -> None:
        from src.core.neuron import Neuron, NeuronConfig, NeuronType, create_neuron

        assert Neuron is not None
        assert NeuronConfig is not None
        assert NeuronType is not None
        assert create_neuron is not None

    def test_core_network(self) -> None:
        from src.core.network import Brain5DConfig, NeuralNetwork, StepResult

        assert NeuralNetwork is not None
        assert StepResult is not None
        assert Brain5DConfig is not None

    def test_core_synapse(self) -> None:
        from src.core.synapse import Synapse, SynapseConfig

        assert Synapse is not None
        assert SynapseConfig is not None

    def test_core_spatial_index(self) -> None:
        from src.core.spatial_index import (
            pack_coords,
            unpack_coords,
            validate_dims,
        )

        assert pack_coords is not None
        assert unpack_coords is not None
        assert validate_dims is not None

    def test_storage_b5d(self) -> None:
        from src.storage.b5d import B5DFormatError, B5DReader

        assert B5DReader is not None
        assert B5DFormatError is not None

    def test_storage_runtime(self) -> None:
        from src.storage.runtime import StorageRuntimeConfig, StorageSession

        assert StorageSession is not None
        assert StorageRuntimeConfig is not None

    def test_storage_checkpoint(self) -> None:
        from src.storage.checkpoint import (
            capture_runtime_checkpoint,
            write_runtime_checkpoint,
        )

        assert capture_runtime_checkpoint is not None
        assert write_runtime_checkpoint is not None

    def test_homeostasis(self) -> None:
        from src.homeostasis import HomeostasisEngine, HomeostasisParameters

        assert HomeostasisEngine is not None
        assert HomeostasisParameters is not None

    def test_learning(self) -> None:
        from src.learning import LearningEngine, LearningParameters

        assert LearningEngine is not None
        assert LearningParameters is not None

    def test_self_organization(self) -> None:
        from src.self_organization import (
            SelfOrganizationCoordinator,
            SelfOrganizationEngine,
            StructuralPlasticityEngine,
        )

        assert SelfOrganizationEngine is not None
        assert SelfOrganizationCoordinator is not None
        assert StructuralPlasticityEngine is not None

    def test_dashboard(self) -> None:
        from src.dashboard import DashboardStateStore, serve_dashboard

        assert serve_dashboard is not None
        assert DashboardStateStore is not None

    def test_embodiment(self) -> None:
        from src.embodiment import EmbodimentAgent, EnvironmentAdapter

        assert EmbodimentAgent is not None
        assert EnvironmentAdapter is not None

    def test_signal_processing(self) -> None:
        from src.signal_processing import SignalFrame, SignalInterpreter

        assert SignalInterpreter is not None
        assert SignalFrame is not None

    def test_manipulation(self) -> None:
        from src.manipulation import Brain5DManipulator

        assert Brain5DManipulator is not None

    def test_runtime(self) -> None:
        from src.runtime import RuntimeController

        assert RuntimeController is not None

    def test_config(self) -> None:
        from src.config import load_config

        assert load_config is not None


@pytest.mark.smoke
class TestConfigSmoke:
    """Verify that shipped YAML configs are loadable."""

    @pytest.mark.parametrize(
        "config_path",
        [
            "configs/poc_config.yaml",
            "configs/poc_config_stdp_on.yaml",
        ],
    )
    def test_config_loads(self, config_path: str) -> None:
        from src.config import load_config

        cfg = load_config(config_path)
        assert "dimensions" in cfg
        assert len(cfg["dimensions"]) == 5


@pytest.mark.smoke
class TestNetworkBasic:
    """Minimal network creation and stepping."""

    def test_create_and_step(self) -> None:
        import random

        from src.core.network import NeuralNetwork

        net = NeuralNetwork(
            {
                "dimensions": [2, 1, 1, 1, 1],
                "simulation": {"dt_ms": 1.0, "max_delay": 2},
            },
            random.Random(0),
        )
        nid = net.add_neuron((0, 0, 0, 0, 0))
        assert nid in net.neurons
        net.step()
        result = net.step()
        assert result.tick == 1

    def test_synapse_creation(self) -> None:
        import random

        from src.core.network import NeuralNetwork

        net = NeuralNetwork(
            {
                "dimensions": [2, 1, 1, 1, 1],
                "simulation": {"dt_ms": 1.0, "max_delay": 2},
            },
            random.Random(0),
        )
        src = net.add_neuron((0, 0, 0, 0, 0))
        tgt = net.add_neuron((1, 0, 0, 0, 0))
        net.connect(src, tgt, 0.5, 1)
        assert net.synapse_count == 1

    def test_spike_propagation(self) -> None:
        import random

        from src.core.network import NeuralNetwork

        net = NeuralNetwork(
            {
                "dimensions": [2, 1, 1, 1, 1],
                "simulation": {"dt_ms": 1.0, "max_delay": 2},
            },
            random.Random(0),
        )
        src = net.add_neuron((0, 0, 0, 0, 0))
        tgt = net.add_neuron((1, 0, 0, 0, 0))
        net.connect(src, tgt, 0.5, 1)
        net.inject_current(src, 100.0)
        for _ in range(10):
            net.step()
        # After enough current, src should have spiked
        assert net.neurons[src].spike_counter > 0


@pytest.mark.smoke
class TestStorageBasic:
    """Minimal storage smoke tests."""

    def test_b5d_header_constants(self) -> None:
        from src.storage.b5d import FORMAT_VERSION, MAGIC

        assert MAGIC is not None
        assert FORMAT_VERSION is not None


@pytest.mark.smoke
class TestSelfOrgBasic:
    """Minimal self-organization smoke tests."""

    def test_parameters_validation(self) -> None:
        from src.self_organization.engine import SelfOrganizationParameters

        params = SelfOrganizationParameters()
        params.validate()  # should not raise

    def test_parameters_from_config(self) -> None:
        from src.self_organization.engine import SelfOrganizationParameters

        params = SelfOrganizationParameters.from_config(
            {"self_organization": {"enabled": True, "interval_ticks": 50}}
        )
        assert params.enabled is True
        assert params.interval_ticks == 50
