"""MHRN package with backwards-compatible process configuration."""

import os

from .identity import legacy_environment_aliases

os.environ.update(legacy_environment_aliases(dict(os.environ)))
