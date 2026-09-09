"""Check cross-links, source provenance and epistemic boundaries, without promotion."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.research.connectome_embodiment import RUNNERS  # noqa: E402
from src.research.connectome_governance import (  # noqa: E402
    PROTECTED_HYPOTHESES,
    ConnectomeGovernanceError,
    connectome_catalog,
    guard_connectome_launch,
    guard_connectome_promotion,
    verify_design_lock,
)
from src.research.protocol_registry import (  # noqa: E402
    load_operational_protocols,
    validate_operational_protocol,
)
from src.research.registry import ResearchRegistry  # noqa: E402


def check(research_root: Path) -> dict[str, Any]:
    verify_design_lock(research_root)
    registry = ResearchRegistry(research_root / "registry").load_all()
    if registry.link_issues():
        raise ValueError("Canonical research links are inconsistent")
    programme = connectome_catalog(research_root)
    operational = {p["id"]: p for p in load_operational_protocols(research_root)}
    if {p["hypothesis"] for p in programme} != PROTECTED_HYPOTHESES:
        raise ValueError("Programme and protected hypotheses differ")
    native: list[str] = []
    blocked: list[str] = []
    for record in programme:
        pid, rq, hyp = record["id"], record["research_question"], record["hypothesis"]
        if hyp not in registry.questions[rq].hypotheses:
            raise ValueError("Question omits its programme hypothesis: " + hyp)
        if registry.hypotheses[hyp].research_question != rq:
            raise ValueError("Hypothesis belongs to another question")
        for source_id in record["sources"]:
            source = registry.sources[source_id].to_dict()
            if any(
                not source.get(key)
                for key in ("title", "url", "source_type", "verified_on", "limitations")
            ):
                raise ValueError("Missing source provenance: " + source_id)
        prereg = json.loads(
            (research_root / record["preregistration"]).read_text(encoding="utf-8")
        )
        if prereg["conditions"] != record["conditions"]:
            raise ValueError("Condition mismatch: " + pid)
        if (
            prereg["mode"] != "EXPLORATORY"
            or prereg["production_activation"] is not False
        ):
            raise ValueError(
                "Unreviewed programme cannot claim confirmation or production authority"
            )
        if pid in RUNNERS:
            contract = operational[pid]
            if contract["runner"] != RUNNERS[pid] or contract["hypothesis"] != hyp:
                raise ValueError("Runner contract mismatch: " + pid)
            validate_operational_protocol(
                research_root,
                question_id=rq,
                hypothesis_id=hyp,
                protocol_id=pid,
                seed_count=3,
            )
            guard_connectome_launch(research_root, rq, hyp, pid)
            native.append(pid)
        else:
            if pid in operational or prereg["freeze"]["status"] != "DRAFT":
                raise ValueError(
                    "Unavailable adapter falsely advertised as operational"
                )
            try:
                guard_connectome_launch(research_root, rq, hyp, pid)
            except ConnectomeGovernanceError:
                blocked.append(pid)
            else:
                raise ValueError("Draft passed the launch guard")
        try:
            guard_connectome_promotion(hyp, "CLAIM-CONN-SCREEN")
        except ConnectomeGovernanceError:
            pass
        else:
            raise ValueError("Unreviewed hypothesis can promote itself")
    claims = json.loads(
        (research_root / "literature/connectome_claims.json").read_text(
            encoding="utf-8"
        )
    )
    if not claims.get("ai_generated"):
        raise ValueError("AI interpretation provenance missing")
    for claim in claims["claims"]:
        if claim["source_id"] not in registry.sources or not claim.get("not_implied"):
            raise ValueError("Claim lacks a source or interpretation limit")
    return {
        "status": "PASS",
        "native_exploratory_protocols": native,
        "blocked_designs": blocked,
        "hypotheses": len(PROTECTED_HYPOTHESES),
        "automatic_evidence_promotion": False,
        "interpretation": "engineering integrity, not biological or scientific confirmation",
    }


if __name__ == "__main__":
    print(json.dumps(check(ROOT / "research"), indent=2))
