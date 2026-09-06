import pytest

from src.embodiment.msba import (
    MAX_PROJECTION_DIMENSIONS,
    MSBAGatewayConfig,
    msba_contract,
    validate_projection_dimensions,
)


def test_msba_projection_dimensions_can_exceed_five_without_core_mutation() -> None:
    config = MSBAGatewayConfig(projection_dimensions=8)

    assert config.projection_dimensions == 8
    assert config.to_json()["core_learning_rules_unchanged"] is True


def test_msba_projection_dimension_bounds_fail_closed() -> None:
    assert validate_projection_dimensions(1) == 1
    assert (
        validate_projection_dimensions(MAX_PROJECTION_DIMENSIONS)
        == MAX_PROJECTION_DIMENSIONS
    )
    with pytest.raises(ValueError, match="projection_dimensions"):
        MSBAGatewayConfig(projection_dimensions=0)
    with pytest.raises(ValueError, match="projection_dimensions"):
        MSBAGatewayConfig(projection_dimensions=MAX_PROJECTION_DIMENSIONS + 1)


def test_msba_contract_distinguishes_projection_and_productive_core_dimensions() -> None:
    topology = msba_contract()["topology"]

    assert isinstance(topology, dict)
    assert topology["projection_dimensions"] == 5
    assert topology["projection_dimensions_range"] == [1, 32]
    assert topology["productive_core_dimensions"] == 5
    assert topology["core_dimension_migration_required_above_five"] is True
