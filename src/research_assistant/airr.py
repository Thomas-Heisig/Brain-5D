"""AIRR generation with deterministic provenance and rendering boundaries."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from .assistant import AnalysisBackend, ResearchAssistant
from .models import AIAnalysisRecord, ResearchPacket
from .statistics import reject_model_statistics, require_statistics_engine_artifact

AI_WARNING = """============================================================
BRAIN-5D - AI GENERATED SCIENTIFIC ANALYSIS
============================================================

Dieser Bericht wurde durch ein kuenstliches Intelligenzsystem erzeugt.

Er stellt eine wissenschaftliche Interpretation von Brain-5D-Forschungsdaten dar.

Er ist KEINE wissenschaftliche Evidenz.

Er wurde zum Zeitpunkt der Erstellung noch nicht automatisch durch einen Menschen bestaetigt.

Human Review Status: PENDING
============================================================"""

_ROLES = ("scientific_analyst", "critical_reviewer", "scientific_writer")
_STATUSES = {
    "generated",
    "review_pending",
    "reviewed",
    "accepted_as_interpretation",
    "rejected",
    "superseded",
}


@dataclass(frozen=True, slots=True)
class AIResearchReport:
    """Canonical AIRR record. Its epistemic flags are not model-controlled."""

    report_id: str
    experiment_id: str
    research_question_id: str
    hypothesis_ids: list[str]
    claim_ids: list[str]
    generated_at: str
    report_schema_version: str
    report_protocol_version: str
    generated_by: str
    ai_generated: bool
    scientific_evidence: bool
    human_review_required: bool
    status: str
    content: dict[str, Any]
    provenance: dict[str, Any]
    analysis_ids: list[str]
    supersedes: str | None = None
    content_digest: str = ""
    markdown_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "experiment_id": self.experiment_id,
            "research_question_id": self.research_question_id,
            "hypothesis_ids": self.hypothesis_ids,
            "claim_ids": self.claim_ids,
            "generated_at": self.generated_at,
            "report_schema_version": self.report_schema_version,
            "report_protocol_version": self.report_protocol_version,
            "generated_by": self.generated_by,
            "ai_generated": self.ai_generated,
            "scientific_evidence": self.scientific_evidence,
            "human_review_required": self.human_review_required,
            "status": self.status,
            "content": self.content,
            "provenance": self.provenance,
            "analysis_ids": self.analysis_ids,
            "supersedes": self.supersedes,
            "content_digest": self.content_digest,
            "markdown_digest": self.markdown_digest,
        }


class AIRRPipeline:
    """Run the three AI roles and write one append-only JSON/Markdown AIRR."""

    def __init__(self, research_root: Path) -> None:
        self._root = research_root.resolve()
        self._assistant = ResearchAssistant(self._root)

    def analyze(
        self,
        experiment_id: str,
        backend: AnalysisBackend,
        *,
        supersedes: str | None = None,
    ) -> AIResearchReport:
        packet = self._assistant.build_packet(experiment_id)
        analyst = self._run_role("scientific_analyst", packet, backend)
        reviewer = self._run_role("critical_reviewer", packet, backend, analyst)
        writer = self._run_role("scientific_writer", packet, backend, analyst, reviewer)
        report = _build_report(
            packet,
            analyst,
            reviewer,
            writer,
            supersedes,
            self._root / "reports" / experiment_id,
        )
        directory = self._root / "reports" / experiment_id
        directory.mkdir(parents=True, exist_ok=True)
        json_path = directory / f"{report.report_id}.json"
        markdown_path = directory / f"{report.report_id}.md"
        if json_path.exists() or markdown_path.exists():
            raise FileExistsError(f"Report already exists: {report.report_id}")
        markdown = render_markdown(report)
        final = _with_digests(report, markdown)
        json_path.write_text(
            json.dumps(final.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        markdown_path.write_text(render_markdown(final), encoding="utf-8")
        return final

    def _run_role(
        self,
        role: str,
        packet: ResearchPacket,
        backend: AnalysisBackend,
        *analyses: AIAnalysisRecord,
    ) -> AIAnalysisRecord:
        prompt = _role_prompt(role, packet, analyses)
        output, model = backend(prompt)
        reject_model_statistics(output)
        record = AIAnalysisRecord.create(
            role=role, model=model, packet=packet, output=output, prompt=prompt
        )
        directory = self._root / "analysis"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{record.analysis_id}.json"
        if path.exists():
            raise FileExistsError(
                f"Analysis record already exists: {record.analysis_id}"
            )
        path.write_text(
            json.dumps(record.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return record


def _role_prompt(
    role: str, packet: ResearchPacket, analyses: tuple[AIAnalysisRecord, ...]
) -> str:
    context = [record.to_dict() for record in analyses]
    review_instruction = (
        "Actively attempt to falsify the analyst and list confounders, leakage, "
        "dependence, missing controls, and mismatched statistics.\n"
        if role == "critical_reviewer"
        else ""
    )
    return (
        f"Role: {role}\n"
        "Return exactly one JSON object with these fields: assessment (string), "
        "observations (array), effect_direction (string), "
        "methodological_concerns (array), alternative_explanations (array), "
        "recommended_experiments (array), requested_evidence (array), and "
        "confidence (number from 0 to 1). Use empty arrays when no items apply. "
        "Separate observations, calculations, interpretation, limitations and "
        "requested evidence. Never create evidence, confirm claims, answer a "
        "research question, or issue execution commands.\n"
        + review_instruction
        + f"Prior role outputs: {json.dumps(context, sort_keys=True)}\n"
        + f"ResearchPacket: {packet.to_json()}"
    )


def _build_report(
    packet: ResearchPacket,
    analyst: AIAnalysisRecord,
    reviewer: AIAnalysisRecord,
    writer: AIAnalysisRecord,
    supersedes: str | None,
    report_directory: Path,
) -> AIResearchReport:
    question_id = str(packet.research_question.get("id", "NOT_AVAILABLE"))
    hypotheses = [str(item.get("id")) for item in packet.hypotheses if item.get("id")]
    claims = [str(item.get("id")) for item in packet.claims if item.get("id")]
    manifest = packet.manifest
    content = {
        "identification": {
            "experiment": packet.experiment_id,
            "research_question": packet.research_question.get(
                "question", "NOT_AVAILABLE"
            ),
            "hypotheses": packet.hypotheses,
            "date": datetime.now(timezone.utc).date().isoformat(),
            "source_sha": packet.provenance.get("git_commit", "NOT_AVAILABLE"),
        },
        "executive_summary": writer.output.get("assessment", "NOT_AVAILABLE"),
        "research_question": packet.research_question,
        "experimental_design": packet.protocol or manifest.get("conditions", {}),
        "data_basis": _data_basis(packet),
        "quantitative_results": _statistics(packet),
        "observations": analyst.output.get("observations", []),
        "interpretation": writer.output,
        "methodological_critique": reviewer.output.get("methodological_concerns", []),
        "alternative_explanations": reviewer.output.get("alternative_explanations", []),
        "reproducibility": packet.provenance,
        "epistemic_status": {
            "implementation": "NOT_DETERMINED",
            "experiment_data": "PRESENT" if packet.data is not None else "ABSENT",
            "registered_evidence": "PRESENT" if packet.evidence else "ABSENT",
            "ai_interpretation": "PRESENT",
            "human_review": "PENDING",
            "claim_support": "NOT_DETERMINED",
            "rq_status": "IN_PROGRESS",
        },
        "ai_confidence": writer.output.get("confidence", 0.0),
        "missing_evidence": writer.output.get("requested_evidence", []),
        "recommended_follow_up": writer.output.get("recommended_experiments", []),
        "conclusion": writer.output.get("assessment", "NOT_AVAILABLE"),
        "human_review": {
            "status": "PENDING",
            "reviewer": None,
            "reviewed_at": None,
            "disposition": None,
            "comments": None,
        },
        "aiar": {
            "analyst": analyst.to_dict(),
            "reviewer": reviewer.to_dict(),
            "writer": writer.to_dict(),
        },
    }
    now = datetime.now(timezone.utc).isoformat()
    return AIResearchReport(
        report_id=_next_report_id(report_directory, now),
        experiment_id=packet.experiment_id,
        research_question_id=question_id,
        hypothesis_ids=hypotheses,
        claim_ids=claims,
        generated_at=now,
        report_schema_version="1.0",
        report_protocol_version="PROTOCOL-AIRR-001",
        generated_by="artificial_intelligence",
        ai_generated=True,
        scientific_evidence=False,
        human_review_required=True,
        status="review_pending",
        content=content,
        provenance={
            "research_packet_digest": packet.digest,
            "source": packet.provenance,
        },
        analysis_ids=[analyst.analysis_id, reviewer.analysis_id, writer.analysis_id],
        supersedes=supersedes,
    )


def _next_report_id(report_directory: Path, now: str) -> str:
    year = now[:4]
    reports = list(report_directory.glob(f"AIRR-{year}-*.json"))
    count = len(reports)
    return f"AIRR-{year}-{count + 1:04d}"


def _data_basis(packet: ResearchPacket) -> dict[str, Any]:
    return {
        "data": packet.data or {},
        "evid": packet.evidence,
        "literature": packet.literature_sources,
    }


def _statistics(packet: ResearchPacket) -> dict[str, Any]:
    if isinstance(packet.data, dict) and isinstance(
        packet.data.get("statistics"), dict
    ):
        statistics = cast(dict[str, Any], packet.data["statistics"])
        require_statistics_engine_artifact(statistics)
        return statistics
    return {"status": "NOT_AVAILABLE", "source": "deterministic statistics.json"}


def _with_digests(report: AIResearchReport, markdown: str) -> AIResearchReport:
    payload = report.to_dict()
    payload["content_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    payload["markdown_digest"] = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    return AIResearchReport(
        **{key: payload[key] for key in AIResearchReport.__dataclass_fields__}
    )


def render_markdown(report: AIResearchReport) -> str:
    sections = report.content
    lines = [AI_WARNING, "", f"# AI Research Report {report.report_id}", ""]
    lines.append(f"Status: {report.status} | Experiment: {report.experiment_id}")
    lines.append(f"Research Question: {report.research_question_id}")
    for title, key in (
        ("Executive Summary", "executive_summary"),
        ("Research Question", "research_question"),
        ("Experimental Design", "experimental_design"),
        ("Data Basis", "data_basis"),
        ("Quantitative Results", "quantitative_results"),
        ("Observations", "observations"),
        ("Interpretation", "interpretation"),
        ("Methodological Critique", "methodological_critique"),
        ("Alternative Explanations", "alternative_explanations"),
        ("Reproducibility", "reproducibility"),
        ("Epistemic Status", "epistemic_status"),
        ("Missing Evidence", "missing_evidence"),
        ("Recommended Follow-up Experiments", "recommended_follow_up"),
        ("Conclusion", "conclusion"),
        ("Human Review", "human_review"),
    ):
        lines.extend(
            [
                f"## {title}",
                "",
                "```json",
                json.dumps(sections.get(key), indent=2, ensure_ascii=False),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            f"AI confidence: {sections.get('ai_confidence', 0.0)}",
            "This value describes internal AI confidence and is not a statistical confidence interval.",
            "",
            f"Content digest: {report.content_digest}",
            f"JSON/Markdown link digest: {report.markdown_digest}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_human_review(
    research_root: Path, experiment_id: str, report_id: str, review: dict[str, Any]
) -> Path:
    if not experiment_id or "/" in experiment_id or "\\" in experiment_id:
        raise ValueError("Invalid experiment id")
    if not report_id or "/" in report_id or "\\" in report_id:
        raise ValueError("Invalid report id")
    directory = research_root / "reports" / experiment_id
    report_path = directory / f"{report_id}.json"
    if not report_path.is_file():
        raise ValueError("AIRR report does not exist")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("AIRR report is unreadable") from exc
    if not isinstance(report, dict):
        raise ValueError("AIRR report identity does not match")
    report = cast(dict[str, Any], report)
    if report.get("report_id") != report_id:
        raise ValueError("AIRR report identity does not match")
    if report.get("status") != "review_pending":
        raise ValueError("AIRR report is not awaiting human review")
    if report.get("scientific_evidence") is not False:
        raise ValueError("AIRR review cannot grant scientific evidence")

    status = review.get("review_status")
    if status not in {"accepted_as_interpretation", "rejected"}:
        raise ValueError("Human review must accept or reject the interpretation")
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("Human reviewer identity is required")
    comments = review.get("comments")
    if not isinstance(comments, str) or not comments.strip():
        raise ValueError("Human review comments are required")
    path = directory / f"{report_id}.review.json"
    if path.exists():
        raise FileExistsError(f"Human review already exists: {report_id}")
    payload = {
        "report_id": report_id,
        "review_status": status,
        "reviewer": reviewer.strip(),
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "comments": comments.strip(),
        "report_content_digest": report.get("content_digest"),
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path
