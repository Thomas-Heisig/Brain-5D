# Add after network and LearningEngine initialization in src/main.py:
# ruff: noqa: F405, F821
from src.manipulation import Brain5DManipulator  # noqa: F401
from src.self_organization import SelfOrganizationEngine  # noqa: F401

manipulator = Brain5DManipulator(network)  # type: ignore[name-defined]
self_organization = SelfOrganizationEngine(network, manipulator, config)  # type: ignore[name-defined]
if self_organization.params.enabled:
    self_organization.attach()
