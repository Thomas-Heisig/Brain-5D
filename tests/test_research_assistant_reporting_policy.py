from __future__ import annotations

from typing import cast

from src.research_assistant.assistant import ResearchAssistant
from src.research_assistant.models import ResearchPacket


class _PacketStub:
    def to_json(self) -> str:
        return '{"experiment_id":"EXP-TEST"}'


def test_scientific_writer_prompt_requires_quantitative_and_scope_checks() -> None:
    prompt = ResearchAssistant._prompt(  # pyright: ignore[reportPrivateUsage]
        "scientific_writer", cast(ResearchPacket, _PacketStub())
    )

    assert "semantic consistency" in prompt
    assert "research question, hypothesis, protocol" in prompt
    assert "exact numerical results" in prompt
    assert "equations" in prompt
    assert "statistically independent" in prompt
    assert "publication-style synthesis" in prompt
    assert "RQ/H and protocol mismatch" in prompt


def test_critical_reviewer_prompt_rejects_unjustified_statistics() -> None:
    prompt = ResearchAssistant._prompt(  # pyright: ignore[reportPrivateUsage]
        "critical_reviewer", cast(ResearchPacket, _PacketStub())
    )

    assert "pseudo-replication" in prompt
    assert "unjustified causal language" in prompt
    assert "missing statistical tests" in prompt
    assert "undefined metrics" in prompt
