from __future__ import annotations

from pathlib import Path

import pytest

from src.research_assistant.governance import (
    KnowledgeOrigin,
    NetworkMode,
    PreregistrationLock,
    PromptRegistry,
    RetrievalRecord,
    VersionedPrompt,
    validate_network_mode,
)
from src.research_assistant.models import AIAnalysisRecord, ResearchPacket


def test_prompt_registry_rejects_changed_content_at_same_version() -> None:
    registry = PromptRegistry()
    prompt = VersionedPrompt.create("analysis", 1, "Use only DATA.")
    registry.register(prompt)
    assert registry.get("analysis", 1) == prompt
    registry.register(prompt)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(VersionedPrompt.create("analysis", 1, "Use DATA and claims."))


def test_prompt_registry_loads_frozen_prompt_file() -> None:
    registry = PromptRegistry()
    registry.load_directory(Path("research/prompts"))
    assert registry.get("analysis", 1).protocol_digest.startswith("3f016076")


def test_preregistration_lock_rejects_protocol_changes() -> None:
    protocol = {"hypotheses": ["H1"], "seeds": [1, 2], "metrics": ["accuracy"]}
    lock = PreregistrationLock.create("EXP-001", 1, protocol)
    lock.validate(protocol)
    with pytest.raises(ValueError, match="changed protocol"):
        lock.validate({**protocol, "seeds": [1, 2, 3]})


def test_retrieval_record_requires_visible_snapshot() -> None:
    record = RetrievalRecord(
        enabled=True,
        mode=NetworkMode.FROZEN_CORPUS,
        snapshot_digest="sha256:corpus",
        source_count=2,
        knowledge_origin=KnowledgeOrigin.EXTERNAL_RETRIEVAL,
    )
    assert record.to_dict()["mode"] == "FROZEN_CORPUS"
    with pytest.raises(ValueError, match="snapshot digest"):
        RetrievalRecord(
            enabled=True,
            mode=NetworkMode.LIVE_NETWORK,
            snapshot_digest="",
            source_count=1,
            knowledge_origin=KnowledgeOrigin.EXTERNAL_RETRIEVAL,
        )


def test_scientific_runs_reject_live_network_mode() -> None:
    validate_network_mode(NetworkMode.FROZEN_CORPUS, scientific_run=True)
    with pytest.raises(ValueError, match="require OFFLINE"):
        validate_network_mode(NetworkMode.LIVE_NETWORK, scientific_run=True)


def test_model_self_confidence_is_separate_from_empirical_metrics() -> None:
    packet = ResearchPacket(
        experiment_id="EXP-001",
        research_question={},
        hypotheses=[],
        claims=[],
        manifest={},
        data=None,
        evidence=[],
        literature_sources=[],
        protocol=None,
        known_limitations=[],
        previous_analyses=[],
        provenance={},
    )
    output = {
        "assessment": "uncertain",
        "observations": [],
        "methodological_concerns": [],
        "alternative_explanations": [],
        "recommended_experiments": [],
        "requested_evidence": [],
        "confidence": 0.8,
    }
    record = AIAnalysisRecord.create(
        role="research_assistant",
        model={},
        packet=packet,
        output=output,
        prompt="prompt",
    )
    assert record.provenance["model_self_confidence"] == "0.8"
