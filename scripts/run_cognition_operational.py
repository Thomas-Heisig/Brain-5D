from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from src.research import experiment_suite
from src.research.protocol_registry import (
    OPERATIONAL_RUNNERS,
    load_operational_protocols,
    validate_operational_protocol,
)

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
COGNITION_IDS = {
    "memory_delayed_information_v1",
    "world_model_prediction_v1",
    "behavior_profile_control_v1",
    *{f"cog_cns_{number}_v1" for number in range(101, 118)},
    "cog_epi_101_v1",
    "cog_epi_102_v1",
    "cog_wel_101_v1",
    "cog_wel_102_v1",
    "cog_wel_103_v1",
}


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def run_matrix(output_dir: Path, seeds: tuple[int, ...]) -> dict[str, Any]:
    protocols = {
        str(item["id"]): item
        for item in load_operational_protocols(RESEARCH)
        if str(item["id"]) in COGNITION_IDS
    }
    missing = sorted(COGNITION_IDS - set(protocols))
    if missing:
        raise RuntimeError(f"Missing cognition protocols: {', '.join(missing)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for protocol_id in sorted(COGNITION_IDS):
        contract = protocols[protocol_id]
        question_id = str(contract["research_question"])
        hypothesis_id = str(contract["hypothesis"])
        prereg = validate_operational_protocol(
            RESEARCH,
            question_id=question_id,
            hypothesis_id=hypothesis_id,
            protocol_id=protocol_id,
            seed_count=len(seeds),
        )
        runner_name = OPERATIONAL_RUNNERS[protocol_id]
        runner_value = getattr(experiment_suite, runner_name, None)
        if not callable(runner_value):
            raise RuntimeError(f"Runner unavailable: {protocol_id} -> {runner_name}")
        runner = runner_value
        runs = runner({}, seeds)
        serialized = [asdict(item) for item in runs]
        observed_seeds = {int(item["seed"]) for item in serialized}
        if observed_seeds != set(seeds):
            raise RuntimeError(
                f"Seed contract failed for {protocol_id}: {sorted(observed_seeds)}"
            )
        runtime_errors = [item for item in serialized if item.get("runtime_error")]
        artifact = {
            "schema_version": 1,
            "protocol_id": protocol_id,
            "research_question": question_id,
            "hypothesis": hypothesis_id,
            "execution_kind": contract.get("execution_kind"),
            "seeds": list(seeds),
            "preregistration_id": prereg["preregistration_id"],
            "conditions": sorted({str(item["condition"]) for item in serialized}),
            "run_count": len(serialized),
            "runtime_error_count": len(runtime_errors),
            "automatic_evidence_promotion": False,
            "scientific_evidence": False,
            "runs": serialized,
        }
        artifact["artifact_digest"] = _digest(artifact)
        path = output_dir / f"{protocol_id}.json"
        path.write_text(
            json.dumps(artifact, indent=2, ensure_ascii=True, default=str) + "\n",
            encoding="utf-8",
        )
        results.append(
            {
                "protocol_id": protocol_id,
                "question_id": question_id,
                "run_count": len(serialized),
                "runtime_error_count": len(runtime_errors),
                "artifact": path.name,
                "artifact_digest": artifact["artifact_digest"],
            }
        )

    report = {
        "schema_version": 1,
        "programme": "cognition-operational-v1",
        "protocol_count": len(results),
        "seeds": list(seeds),
        "completed_protocols": sum(
            item["runtime_error_count"] == 0 for item in results
        ),
        "failed_protocols": sum(item["runtime_error_count"] > 0 for item in results),
        "execution_results": results,
        "authority": "engineering_and_exploratory_data_only",
        "automatic_evidence_promotion": False,
    }
    report["matrix_digest"] = _digest(report)
    (output_dir / "matrix.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="101,102,103")
    args = parser.parse_args()
    seeds = tuple(int(value.strip()) for value in args.seeds.split(",") if value.strip())
    if len(set(seeds)) != len(seeds) or len(seeds) < 3:
        raise SystemExit("At least three distinct seeds are required.")
    report = run_matrix(args.output, seeds)
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report["failed_protocols"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
