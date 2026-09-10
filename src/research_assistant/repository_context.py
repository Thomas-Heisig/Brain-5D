"""Bounded read-only retrieval over the repository for all AI observer surfaces.

The repository view is shared by chat, AI insight and AIRR evaluation paths. It
never grants filesystem mutation or experiment-execution authority. Large and
binary artifacts are indexed by metadata and digest rather than copied into a
prompt wholesale.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

_TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".py",
    ".pyi",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".sh",
    ".ps1",
    ".cmd",
    ".bat",
    ".tex",
    ".bib",
    ".csv",
    ".tsv",
    ".xml",
    ".svg",
}
_TEXT_NAMES = {
    "Dockerfile",
    "Makefile",
    "LICENSE",
    "NOTICE",
    ".gitignore",
    ".gitattributes",
    ".pre-commit-config.yaml",
}
_SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
    "private",
    "review_private",
    "review-private",
    "review_responses",
    "review-responses",
    "responses",
    "backups",
}
_SENSITIVE_NAME_FRAGMENTS = (
    ".env",
    "secret",
    "credential",
    "private_key",
    "id_rsa",
    "id_ed25519",
)
_TOKEN_RE = re.compile(r"[A-Za-z0-9_.:/-]{2,}")


@dataclass(frozen=True, slots=True)
class RepositoryContext:
    """One deterministic bounded retrieval result."""

    text: str
    digest: str
    indexed_files: int
    selected_files: tuple[str, ...]
    omitted_large_files: int


class RepositoryKnowledgeView:
    """Search readable repository files without loading the whole tree at once."""

    def __init__(
        self,
        root: Path,
        *,
        max_file_bytes: int = 2_000_000,
        per_file_chars: int = 8_000,
        max_selected_files: int = 32,
        max_context_chars: int = 80_000,
        blocked_roots: tuple[str, ...] = (),
    ) -> None:
        self.root = root.resolve()
        self.max_file_bytes = max_file_bytes
        self.per_file_chars = per_file_chars
        self.max_selected_files = max_selected_files
        self.max_context_chars = max_context_chars
        self.blocked_roots = set(blocked_roots)

    def retrieve(self, query: str) -> RepositoryContext:
        """Return query-relevant repository snippets plus provenance metadata."""
        tokens = {token.lower() for token in _TOKEN_RE.findall(query)}
        candidates: list[tuple[int, str, str]] = []
        indexed = 0
        omitted_large = 0
        if not self.root.is_dir():
            return RepositoryContext("", hashlib.sha256(b"").hexdigest(), 0, (), 0)

        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            try:
                path.resolve().relative_to(self.root)
            except ValueError:
                continue
            relative = path.relative_to(self.root)
            if self._skip(relative):
                continue
            indexed += 1
            if not self._readable(path):
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > self.max_file_bytes:
                omitted_large += 1
                metadata = (
                    f"[REPOSITORY FILE: {relative.as_posix()}]\n"
                    f"binary_or_large_index_only=true size_bytes={size} "
                    f"sha256={self._digest_file(path)}"
                )
                score = self._path_score(relative.as_posix(), tokens)
                if score > 0:
                    candidates.append((score, relative.as_posix(), metadata))
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            # Exported questionnaire payloads are private even if misfiled in Git.
            if (
                "instrument_sha256" in content
                and "participant_code" in content
                and (path.suffix.lower() in {".json", ".jsonl", ".csv", ".tsv"})
            ):
                continue
            score = self._score(relative.as_posix(), content, tokens)
            if score <= 0 and tokens:
                continue
            snippet = content[: self.per_file_chars]
            if len(content) > self.per_file_chars:
                snippet += (
                    "\n[TRUNCATED: "
                    f"chars={len(content)} sha256={self._digest_file(path)}]"
                )
            candidates.append(
                (
                    score,
                    relative.as_posix(),
                    f"[REPOSITORY FILE: {relative.as_posix()}]\n{snippet}",
                )
            )

        candidates.sort(key=lambda item: (-item[0], item[1]))
        selected = candidates[: self.max_selected_files]
        header = (
            "REPOSITORY READ-ONLY RETRIEVAL\n"
            "Scientific authority is unchanged: source code/docs/AI output are not EVID.\n"
            f"indexed_files={indexed} selected_files={len(selected)} "
            f"omitted_large_files={omitted_large}\n"
            + ("binary_or_large_index_only=true\n" if omitted_large else "")
        )
        text = header + "\n\n".join(item[2] for item in selected)
        text = text[: self.max_context_chars]
        return RepositoryContext(
            text=text,
            digest=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            indexed_files=indexed,
            selected_files=tuple(item[1] for item in selected),
            omitted_large_files=omitted_large,
        )

    def _skip(self, relative: Path) -> bool:
        parts = relative.parts
        if not parts:
            return True
        if parts[0] in self.blocked_roots:
            return True
        if any(part.lower() in _SKIP_PARTS for part in parts):
            return True
        lower_name = relative.as_posix().lower()
        return any(fragment in lower_name for fragment in _SENSITIVE_NAME_FRAGMENTS)

    @staticmethod
    def _readable(path: Path) -> bool:
        return path.name in _TEXT_NAMES or path.suffix.lower() in _TEXT_SUFFIXES

    @staticmethod
    def _path_score(path: str, tokens: set[str]) -> int:
        lower = path.lower()
        return sum(8 for token in tokens if token in lower)

    @classmethod
    def _score(cls, path: str, content: str, tokens: set[str]) -> int:
        if not tokens:
            return 1
        lower_content = content.lower()
        score = cls._path_score(path, tokens)
        for token in tokens:
            occurrences = lower_content.count(token)
            if occurrences:
                score += min(occurrences, 12)
        if path.startswith("research/"):
            score += 2
        if path.startswith("src/"):
            score += 1
        return score

    @staticmethod
    def _digest_file(path: Path) -> str:
        digest = hashlib.sha256()
        try:
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError:
            return "unavailable"
        return digest.hexdigest()


__all__ = ["RepositoryContext", "RepositoryKnowledgeView"]
