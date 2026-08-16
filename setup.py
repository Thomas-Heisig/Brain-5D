"""Compatibility shim for build frontends that still invoke setup.py.

Brain-5D uses pyproject.toml as the authoritative project configuration.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
