"""
Literature Registry — Manage BibTeX sources and literature mappings.

Provides tools for maintaining the .bib files and generating literature
relevance matrices for research questions.
"""

from __future__ import annotations

from pathlib import Path

from .registry import REPO_ROOT, ResearchRegistry, Source

LITERATURE_DIR = REPO_ROOT / "research" / "literature"


class LiteratureRegistry:
    """Manages literature sources and generates reference documents."""

    def __init__(self, registry: ResearchRegistry):
        self.registry = registry

    def get_sources_by_topic(self, topic: str) -> list[Source]:
        """Get all sources matching a topic tag."""
        return [s for s in self.registry.sources.values() if topic in s.topic]

    def get_sources_by_question(self, question_id: str) -> list[Source]:
        """Get all sources linked to a research question."""
        return [
            s
            for s in self.registry.sources.values()
            if question_id in s.brain5d_questions
        ]

    def generate_literature_matrix(self) -> str:
        """
        Generate a markdown literature → Brain-5D relevance matrix.
        """
        lines = [
            "# Literatur → Brain-5D Relevanzmatrix",
            "",
            "| Quelle | Aussage | Brain-5D-Frage(n) | Status |",
            "|--------|---------|-------------------|--------|",
        ]

        for source in self.registry.sources.values():
            claims_text = "; ".join(source.claims[:2])
            questions = ", ".join(source.brain5d_questions)
            statuses: list[str] = []
            for qid in source.brain5d_questions:
                q = self.registry.questions.get(qid)
                statuses.append(q.status if q else "unknown")
            status_text = ", ".join(set(statuses))

            short_authors = source.authors[0].split()[-1] if source.authors else "Unk."
            ref = f"{short_authors} ({source.year})"

            lines.append(f"| {ref} | {claims_text} | {questions} | {status_text} |")

        lines.extend(
            [
                "",
                "---",
                f"*Automatisch generiert am {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}*",
            ]
        )

        return "\n".join(lines)

    def write_literature_matrix(self, path: Path | None = None) -> Path:
        """Write the literature matrix to a markdown file."""
        output = path or (REPO_ROOT / "research" / "generated" / "LITERATURE_MATRIX.md")
        output.write_text(self.generate_literature_matrix(), encoding="utf-8")
        return output
