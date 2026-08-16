"""Safe read-only access to repository Markdown documentation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import JSONValue


@dataclass(frozen=True, slots=True)
class DocumentationEntry:
    """Metadata for one Markdown document."""

    name: str
    size_bytes: int

    def to_json(self) -> dict[str, JSONValue]:
        """Return JSON-ready document metadata."""
        return {"name": self.name, "size_bytes": self.size_bytes}


class DocumentationSource:
    """Expose Markdown files below one fixed documentation directory."""

    def __init__(self, docs_root: Path) -> None:
        self.docs_root = docs_root.resolve()

    def list_documents(self) -> tuple[DocumentationEntry, ...]:
        """List top-level Markdown documentation in stable order."""
        if not self.docs_root.is_dir():
            return ()
        return tuple(
            DocumentationEntry(path.name, path.stat().st_size)
            for path in sorted(self.docs_root.glob("*.md"))
            if path.is_file()
        )

    def read(self, name: str) -> str:
        """Read one safe Markdown file by basename."""
        if Path(name).name != name or not name.lower().endswith(".md"):
            raise ValueError("invalid documentation filename")
        candidate = (self.docs_root / name).resolve()
        if candidate.parent != self.docs_root or not candidate.is_file():
            raise FileNotFoundError(name)
        return candidate.read_text(encoding="utf-8")
