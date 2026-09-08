"""Public naming constants and backwards-compatible environment translation.

Constants are checked against project_identity.json. Neither public branding nor
an environment alias changes serialized neuron IDs, data or scientific status.
"""

from __future__ import annotations

from collections.abc import Mapping

PROJECT_NAME = "MHRN"
PROJECT_TITLE = "Multi-Scale Homeostatic Recurrence Network"
PROJECT_SUBTITLE_DE = "Mehrskaliges homöostatisches Rekurrenznetzwerk"
PUBLICATION_TITLE = "Recursive Epistemics in Embodied Spiking Neural Architectures: A Framework for Delegated Agency and Multi-Scale Recurrence"
PUBLICATION_SUBTITLE_DE = "Rekursive Epistemik in verkörperten spikenden neuronalen Architekturen: Ein Framework für delegierte Handlungsmacht und mehrskalige Rekurrenz"


def legacy_environment_aliases(environment: Mapping[str, str]) -> dict[str, str]:
    """New prefix takes precedence, including explicit empty strings.

    Returned keys are only compatibility aliases. Existing legacy-only settings
    remain intact. Values are not logged and permission/safety defaults do not
    change. Call at a process entrypoint before importing runtime configuration.
    """
    return {
        "BRAIN5D_" + key.removeprefix("MHRN_"): value
        for key, value in environment.items()
        if key.startswith("MHRN_") and len(key) > len("MHRN_")
    }
