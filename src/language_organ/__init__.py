"""Optional language-organ contracts for Brain-5D."""

from .null_backend import NullLanguageBackend
from .protocols import LanguageModelBackend, LanguageRequest, LanguageResponse

__all__ = [
    "LanguageModelBackend",
    "LanguageRequest",
    "LanguageResponse",
    "NullLanguageBackend",
]
