# Add after network and LearningEngine initialization in src/main.py:
from src.manipulation import Brain5DManipulator
from src.self_organization import SelfOrganizationEngine

manipulator = Brain5DManipulator(network)
self_organization = SelfOrganizationEngine(network, manipulator, config)
if self_organization.params.enabled:
    self_organization.attach()
