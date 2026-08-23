"""
Report Builder — Generates markdown reports from research registries.

Produces:
- RESEARCH_CATALOG.md      — Full catalog of questions, hypotheses, evidence
- EVIDENCE_MATRIX.md       — Overview of evidence status per question
- OPEN_QUESTIONS.md        — All unanswered questions
- CLAIM_REGISTER.md        — All claims with status
- DISSERTATION_MAP.md      — Dissertation chapter structure mapped to research
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT, ResearchQuestion, ResearchRegistry

GENERATED_DIR = REPO_ROOT / "research" / "generated"


class ReportBuilder:
    """Generates markdown reports from the research registry."""

    def __init__(self, registry: ResearchRegistry):
        self.registry = registry

    def build_research_catalog(self) -> str:
        """Generate a complete research catalog."""
        lines = [
            "# Brain-5D Research Catalog",
            "",
            f"*Generiert am {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "## Übersicht",
            "",
            f"- **Forschungsfragen:** {len(self.registry.questions)}",
            f"- **Hypothesen:** {len(self.registry.hypotheses)}",
            f"- **Claims:** {len(self.registry.claims)}",
            f"- **Literaturquellen:** {len(self.registry.sources)}",
            "",
            "---",
            "",
        ]

        domains: dict[str, list[ResearchQuestion]] = {}
        for q in self.registry.questions.values():
            domains.setdefault(q.domain, []).append(q)

        for domain in sorted(domains.keys()):
            lines.extend([f"## {domain}", ""])
            for q in domains[domain]:
                hypotheses = self.registry.hypotheses_for_question(q.id)
                claims = self.registry.claims_for_question(q.id)
                sources = self.registry.sources_for_question(q.id)

                lines.extend(
                    [
                        f"### {q.id}",
                        "",
                        f"**Frage:** {q.question}",
                        "",
                        f"**Status:** {q.status}",
                        f"**Relevanz:** {q.relevance}",
                        "",
                    ]
                )

                if q.answer.current:
                    lines.extend(
                        [
                            "**Aktuelle Antwort:**",
                            "",
                            f"> {q.answer.current}",
                            "",
                            f"*Konfidenz: {q.answer.confidence}*",
                            "",
                        ]
                    )

                if hypotheses:
                    lines.append("**Hypothesen:**")
                    for h in hypotheses:
                        lines.append(f"- `{h.id}`: {h.hypothesis} *({h.status})*")
                    lines.append("")

                if claims:
                    lines.append("**Claims:**")
                    for c in claims:
                        lines.append(
                            f"- `{c.id}`: {c.claim} *({c.status}, {c.confidence})*"
                        )
                    lines.append("")

                if sources:
                    lines.append("**Literatur:**")
                    for s in sources:
                        lines.append(
                            f"- `{s.source_id}`: {s.authors[0]} et al. ({s.year})"
                        )
                    lines.append("")

                if q.evidence:
                    lines.append(f"**Evidenzen:** {', '.join(q.evidence)}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def build_evidence_matrix(self) -> str:
        """Generate an evidence matrix showing status per question."""
        lines = [
            "# Brain-5D Evidence Matrix",
            "",
            f"*Generiert am {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "| Forschungsfrage | Hypothese | Literatur | Experimente | Evidenz | Antwort |",
            "|----------------|-----------|-----------|-------------|---------|---------|",
        ]

        for q in self.registry.questions.values():
            hypotheses = self.registry.hypotheses_for_question(q.id)
            sources = self.registry.sources_for_question(q.id)
            claims = self.registry.claims_for_question(q.id)

            h_text = ", ".join(f"`{h.id}`" for h in hypotheses) or "—"
            s_text = str(len(sources))
            c_text = ", ".join(f"`{c.id}`" for c in claims) if claims else "—"
            ev_text = str(len(q.evidence))
            answer_text = q.answer.confidence if q.answer.current else "offen"

            lines.append(
                f"| `{q.id}` | {h_text} | {s_text} | {c_text} | {ev_text} | {answer_text} |"
            )

        supported = sum(
            1 for c in self.registry.claims.values() if c.status == "supported"
        )
        refuted = sum(1 for c in self.registry.claims.values() if c.status == "refuted")
        untested = sum(
            1 for c in self.registry.claims.values() if c.status == "untested"
        )
        inconclusive = sum(
            1 for c in self.registry.claims.values() if c.status == "inconclusive"
        )

        lines.extend(
            [
                "",
                "## Zusammenfassung",
                "",
                "| Status | Anzahl |",
                "|--------|--------|",
                f"| ✅ Supported | {supported} |",
                f"| ❌ Refuted | {refuted} |",
                f"| 🔄 Inconclusive | {inconclusive} |",
                f"| ⬜ Untested | {untested} |",
                f"| **Gesamt** | **{len(self.registry.claims)}** |",
                "",
                "---",
                "*Automatisch generiert — Theorie, Beobachtung und Interpretation sind strikt getrennt.*",
            ]
        )

        return "\n".join(lines)

    def build_open_questions(self) -> str:
        """Generate a document listing all unanswered research questions."""
        lines = [
            "# Brain-5D Open Questions",
            "",
            f"*Generiert am {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "Die folgenden Forschungsfragen sind noch offen und warten auf experimentelle Evidenz.",
            "",
        ]

        for q in self.registry.open_questions():
            lines.extend(
                [
                    f"## {q.id}",
                    "",
                    f"**Domäne:** {q.domain}",
                    "",
                    f"**Frage:** {q.question}",
                    "",
                    f"**Relevanz:** {q.relevance}",
                    "",
                ]
            )
            sources = self.registry.sources_for_question(q.id)
            if sources:
                lines.append("**Literatur:**")
                for s in sources:
                    lines.append(f"- `{s.source_id}`: {s.authors[0]} et al. ({s.year})")
                lines.append("")
            hypotheses = self.registry.hypotheses_for_question(q.id)
            if hypotheses:
                lines.append("**Hypothesen:**")
                for h in hypotheses:
                    lines.append(f"- `{h.id}`: {h.hypothesis}")
                lines.append("")
            lines.append("---")
            lines.append("")

        lines.append(
            f"*Insgesamt {len(self.registry.open_questions())} offene Fragen.*"
        )
        return "\n".join(lines)

    def build_claim_register(self) -> str:
        """Generate a register of all scientific claims."""
        lines = [
            "# Brain-5D Claim Register",
            "",
            f"*Generiert am {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "| Claim | Status | Konfidenz | Evidenzen | Experimente |",
            "|-------|--------|-----------|-----------|-------------|",
        ]

        for c in self.registry.claims.values():
            icon = {
                "supported": "✅",
                "refuted": "❌",
                "inconclusive": "🔄",
                "untested": "⬜",
            }.get(c.status, "⬜")
            lines.append(
                f"| `{c.id}`: {c.claim[:80]}... | {icon} {c.status} | "
                f"{c.confidence} | {len(c.evidence)} | {len(c.experiments)} |"
            )

        lines.append("")
        return "\n".join(lines)

    def build_dissertation_map(self) -> str:
        """Generate a dissertation structure mapped to research entities."""
        chapters: dict[str, dict[str, Any]] = {
            "Kapitel 1 – Theorie und Grundlagen": {
                "questions": ["RQ-SNN-001", "RQ-SNN-002", "RQ-DET-001"],
                "sources": [
                    "SRC-IZHIKEVICH-2003",
                    "SRC-GERSTNER-2014",
                    "SRC-MAASS-1997",
                ],
                "description": "Einführung in SNN-Theorie, Izhikevich-Modell, deterministische Dynamik",
            },
            "Kapitel 2 – Plastizität und Lernen": {
                "questions": [
                    "RQ-SNN-004",
                    "RQ-SNN-005",
                    "RQ-STDP-001",
                    "RQ-STDP-002",
                    "RQ-HOM-001",
                    "RQ-HOM-002",
                ],
                "sources": [
                    "SRC-SONG-ABBOTT-2000",
                    "SRC-BI-POO-1998",
                    "SRC-TURRIGIANO-2008",
                    "SRC-HEBB-1949",
                ],
                "description": "STDP, Homeostase, Interaktion, Lernleistung",
            },
            "Kapitel 3 – 5D-Raum und Topologie": {
                "questions": ["RQ-5D-001", "RQ-5D-002", "RQ-5D-003", "RQ-5D-004"],
                "sources": [],
                "description": "Dimensionsablation, Signalpropagation, Modularität, Informationstheorie",
            },
            "Kapitel 4 – Persistenz und Speicherung": {
                "questions": [
                    "RQ-STORAGE-001",
                    "RQ-STORAGE-002",
                    "RQ-STORAGE-003",
                    "RQ-STORAGE-004",
                ],
                "sources": [],
                "description": ".b5d-Format, verlustfreie Serialisierung, Speicherdichte, Skalierung",
            },
            "Kapitel 5 – Selbstorganisation": {
                "questions": ["RQ-SELF-001", "RQ-SELF-002", "RQ-STRUCT-001"],
                "sources": [],
                "description": "Emergenz, Clusterbildung, Pruning, Sprouting",
            },
            "Kapitel 6 – Skalierung": {
                "questions": ["RQ-SCALE-001"],
                "sources": ["SRC-MARKRAM-2015"],
                "description": "Skalierung von 5k auf Millionen Neuronen",
            },
            "Kapitel 7 – Gedächtnis und Embodiment": {
                "questions": ["RQ-MEM-001", "RQ-EMB-001", "RQ-LLM-001"],
                "sources": [],
                "description": "Synaptisches Gedächtnis, Sensor-Aktor-Schleife, Language Organ",
            },
            "Kapitel 8 – Autorenschaft und Epistemologie": {
                "questions": ["RQ-ETH-001", "RQ-ETH-002", "RQ-EPIST-001"],
                "sources": [],
                "description": "Verteilte Autorenschaft, Kontrollverlust, maschinelle Erkenntnis",
            },
        }

        lines = [
            "# Brain-5D Dissertation Map",
            "",
            f"*Generiert am {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "Diese Karte zeigt, wie die Forschungsergebnisse von Brain-5D in eine",
            "Dissertationsstruktur eingeordnet werden können.",
            "",
        ]

        for chapter, info in chapters.items():
            lines.extend([f"## {chapter}", "", info["description"], ""])

            questions = [
                self.registry.questions[qid]
                for qid in info["questions"]
                if qid in self.registry.questions
            ]
            if questions:
                lines.append("**Forschungsfragen:**")
                for q in questions:
                    lines.append(f"- `{q.id}`: {q.question[:80]}... *({q.status})*")
                lines.append("")

            sources = [
                self.registry.sources[sid]
                for sid in info["sources"]
                if sid in self.registry.sources
            ]
            if sources:
                lines.append("**Literatur:**")
                for s in sources:
                    lines.append(f"- `{s.source_id}`: {s.authors[0]} et al. ({s.year})")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def write_all(self, output_dir: Path | None = None) -> dict[str, Path]:
        """Generate and write all reports. Returns dict of name -> path."""
        out = output_dir or GENERATED_DIR
        out.mkdir(parents=True, exist_ok=True)

        reports = {
            "RESEARCH_CATALOG.md": self.build_research_catalog,
            "EVIDENCE_MATRIX.md": self.build_evidence_matrix,
            "OPEN_QUESTIONS.md": self.build_open_questions,
            "CLAIM_REGISTER.md": self.build_claim_register,
            "DISSERTATION_MAP.md": self.build_dissertation_map,
        }

        paths: dict[str, Path] = {}
        for name, builder in reports.items():
            path = out / name
            path.write_text(builder(), encoding="utf-8")
            paths[name] = path

        return paths
