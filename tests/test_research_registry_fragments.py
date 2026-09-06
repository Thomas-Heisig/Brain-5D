from pathlib import Path

import pytest

from src.research.registry import ResearchRegistry


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_registry_loads_question_and_hypothesis_fragments(tmp_path: Path) -> None:
    _write(
        tmp_path / "questions.yaml",
        "- id: RQ-BASE-001\n  domain: Base\n  question: Base?\n  relevance: base\n  hypotheses: [H-BASE-001-A]\n  status: open\n",
    )
    _write(
        tmp_path / "questions.extra.yaml",
        "- id: RQ-EXTRA-E01\n  domain: Extra\n  question: Extra?\n  relevance: extra\n  hypotheses: [H-EXTRA-E01-A]\n  status: open\n",
    )
    _write(
        tmp_path / "hypotheses.yaml",
        "- id: H-BASE-001-A\n  research_question: RQ-BASE-001\n  hypothesis: Base hypothesis\n",
    )
    _write(
        tmp_path / "hypotheses.extra.yaml",
        "- id: H-EXTRA-E01-A\n  research_question: RQ-EXTRA-E01\n  hypothesis: Extra hypothesis\n",
    )

    registry = ResearchRegistry(tmp_path).load_all()

    assert set(registry.questions) == {"RQ-BASE-001", "RQ-EXTRA-E01"}
    assert set(registry.hypotheses) == {"H-BASE-001-A", "H-EXTRA-E01-A"}
    assert registry.link_issues() == []

    registry.questions["RQ-EXTRA-E01"].status = "in_progress"
    registry.hypotheses["H-EXTRA-E01-A"].status = "inconclusive"
    registry.save_questions()
    registry.save_hypotheses()

    reloaded = ResearchRegistry(tmp_path).load_all()
    assert set(reloaded.questions) == {"RQ-BASE-001", "RQ-EXTRA-E01"}
    assert set(reloaded.hypotheses) == {"H-BASE-001-A", "H-EXTRA-E01-A"}
    assert reloaded.questions["RQ-EXTRA-E01"].status == "in_progress"
    assert reloaded.hypotheses["H-EXTRA-E01-A"].status == "inconclusive"


def test_registry_fragment_duplicate_ids_fail_closed(tmp_path: Path) -> None:
    base = "- id: RQ-DUP-001\n  domain: Test\n  question: Test?\n  relevance: test\n  status: open\n"
    _write(tmp_path / "questions.yaml", base)
    _write(tmp_path / "questions.duplicate.yaml", base)

    with pytest.raises(ValueError, match="Duplicate research registry IDs"):
        ResearchRegistry(tmp_path).load_all()


def test_canonical_registry_exposes_msba_questions_and_links() -> None:
    registry = ResearchRegistry().load_all()

    msba_question_ids = {f"RQ-MSBA-E{number:02d}" for number in range(1, 6)}
    msba_hypothesis_ids = {f"H-MSBA-E{number:02d}-A" for number in range(1, 6)}
    for question_id, hypothesis_id in zip(
        sorted(msba_question_ids), sorted(msba_hypothesis_ids), strict=True
    ):
        assert question_id in registry.questions
        assert hypothesis_id in registry.hypotheses
        assert registry.hypotheses[hypothesis_id].research_question == question_id

    msba_issues = [
        issue
        for issue in registry.link_issues()
        if issue.get("question_id") in msba_question_ids
        or issue.get("hypothesis_id") in msba_hypothesis_ids
    ]
    assert msba_issues == []
