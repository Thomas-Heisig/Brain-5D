"""Read-only, replaceable language model organ for Brain-5D.

This package provides a controlled, replaceable interface between
Brain-5D and external language models. The Language Organ is:

- Optional and replaceable (NullBackend, LlamaCppBackend, etc.)
- Read-only (never mutates Brain-5D state)
- Fault-tolerant (failures do not stop the simulation)
- Asynchronous (does not block the simulation loop)

The Language Organ translates between symbolic text and subsymbolic
SignalFrames, enabling semantic interpretation and monitoring without
allowing direct network mutation.
"""

from .bridge import LanguageOrgan, LanguageOrganStatus
from .null_backend import NullBackend, NullLanguageBackend
from .protocols import LanguageModelBackend, LanguageRequest, LanguageResponse

__all__ = [
    # Bridge
    "LanguageOrgan",
    "LanguageOrganStatus",
    # Backends
    "NullLanguageBackend",
    "NullBackend",
    # Protocols
    "LanguageModelBackend",
    "LanguageRequest",
    "LanguageResponse",
]