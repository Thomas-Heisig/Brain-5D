"""
Brain-5D — Compatibility shim for legacy build frontends.

The authoritative project configuration lives in ``pyproject.toml``
(``[project]``, ``[build-system]``, ``[tool.*]``).

This file exists only so that legacy tools (``pip install -e .`` without
``--no-build-isolation``, older ``setuptools`` versions, some IDEs) can
discover package metadata without reading ``pyproject.toml``.

New build frontends (``pip >= 21.3``, ``build``, ``pypa/build``) read
``pyproject.toml`` directly and do **not** invoke this file.
"""

from __future__ import annotations

from setuptools import setup

# All metadata is declared in pyproject.toml under [project].
# The setup() call here is intentionally empty — setuptools reads
# pyproject.toml automatically when this shim is invoked.
if __name__ == "__main__":
    setup()
