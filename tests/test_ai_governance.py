from __future__ import annotations

from pathlib import Path

import pytest

from src.research_assistant.advisor import CognitiveAdvisor
from src.research_assistant.authority import AIRole, authority_for
from src.research_assistant.contracts import AIClockMode, AIInteractionRecord
from src.research_assistant.gateways import InterventionGateway, MemoryWriteGateway
from src.research_assistant.governance import (
    ConfirmatoryRunLock,
    DataPartition,
    KnowledgeOrigin,
    NetworkMode,
    PreregistrationLock,
    PromptRegistry,
    RetrievalRecord,
    VersionedPrompt,
    validate_data_partition,
    validate_network_mode,
)
from src.research_assistant.models import AIAnalysisRecord, ResearchPacket
from src.research_assistant.statistics import (
    require_statistics_engine_artifact,
    summarize,
)


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


def test_cognitive_advisor_is_proposal_only() -> None:
    proposal = CognitiveAdvisor().propose(
        action="inspect_snapshot",
        rationale="The observation is incomplete.",
        confidence=0.6,
    )
    assert proposal.to_dict()["executed"] is False
    assert "execute" not in proposal.to_dict()


def test_intervention_gateway_requires_capability_and_human_approval() -> None:
    proposal = CognitiveAdvisor().propose(
        action="inspect_snapshot", rationale="inspect", confidence=0.5
    )
    gateway = InterventionGateway({"inspect_snapshot"})
    proposal_id = gateway.submit(proposal, tick=4)
    approval = gateway.approve(proposal_id, reviewer_id="human-1", tick=4)
    assert approval.to_dict()["executed"] is False
    assert len(gateway.audit) == 1

    blocked = InterventionGateway({"inspect_snapshot"}, safety_envelope=lambda _item: False)
    with pytest.raises(PermissionError, match="Safety envelope"):
        blocked.submit(proposal, tick=4)


def test_memory_write_gateway_only_creates_digest_proposals() -> None:
    proposal = MemoryWriteGateway().propose(key="fact", value={"x": 1}, source="advisor")
    assert proposal.to_dict()["executed"] is False
    assert len(proposal.value_digest) == 64


def test_ai_interaction_records_clock_mode_and_application_tick() -> None:
    record = AIInteractionRecord.create(
        role="research_ai",
        experiment_id="EXP-001",
        tick=2,
        input_value={"x": 1},
        prompt="observe",
        output_value={"y": 1},
        model_provenance={},
        authority="read_only",
        clock_mode=AIClockMode.WALL_CLOCK,
        response_application_tick=4,
    )
    assert record.to_dict()["clock_mode"] == "WALL_CLOCK"
    assert record.to_dict()["response_application_tick"] == 4


def test_confirmatory_lock_rejects_protocol_prompt_or_analysis_changes() -> None:
    lock = ConfirmatoryRunLock.create(
        protocol={"hypothesis": "H1"},
        prompt_digest="prompt-sha",
        analysis_digest="analysis-sha",
    )
    lock.validate(
        protocol={"hypothesis": "H1"},
        prompt_digest="prompt-sha",
        analysis_digest="analysis-sha",
    )
    with pytest.raises(ValueError, match="rejects"):
        lock.validate(
            protocol={"hypothesis": "H2"},
            prompt_digest="prompt-sha",
            analysis_digest="analysis-sha",
        )


def test_formal_ai_roles_are_readable_and_bounded() -> None:
    assert authority_for(AIRole.AI_0_RESEARCH_AI.value).scientific_evidence is False
    assert "apply" not in authority_for(AIRole.AI_3_EXPERIMENTAL_CONTROLLER.value).capabilities


def test_scientific_runs_reject_development_partition() -> None:
    validate_data_partition(DataPartition.SCIENTIFIC_HOLDOUT, scientific_run=True)
    with pytest.raises(ValueError, match="DEVELOPMENT"):
        validate_data_partition(DataPartition.DEVELOPMENT, scientific_run=True)


def test_quantitative_results_require_statistics_engine_provenance() -> None:
    summary = summarize([1.0, 2.0, 3.0])
    require_statistics_engine_artifact(summary)
    with pytest.raises(ValueError, match="Statistics Engine"):
        require_statistics_engine_artifact({"mean": 2.0})
