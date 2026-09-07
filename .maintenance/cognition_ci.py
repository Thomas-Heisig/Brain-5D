"""Run real bounded checks and commit their actual results on the task branch."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "integration/cognition-ethics-20260907"
PY = sys.executable
checks = []


def run(name: str, command: list[str]) -> bool:
    print(f"\n=== {name} ===", flush=True)
    process = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(process.stdout, flush=True)
    checks.append({"check": name, "command": command, "exit_code": process.returncode, "output": process.stdout[-12000:]})
    return process.returncode == 0


if os.environ.get("GITHUB_REF_NAME") != BRANCH:
    raise SystemExit("Importer/commit workflow is restricted to its named task branch")
if not run("one_time_import", [PY, ".maintenance/integrate_cognition.py", "--apply"]):
    raise SystemExit(1)
files = ["src/research/cognition_metrics.py", "src/research/cognition_governance.py", "src/research/registry.py", "src/research/evidence_engine.py", "src/research/catalog_status.py", "src/dashboard/experiment_workflow.py", "tests/test_cognition_program.py", "scripts/publication_cognition.py"]
run("format", [PY, "-m", "black", *files])
run("lint_fix", [PY, "-m", "ruff", "check", "--fix", *files])
run("format_check", [PY, "-m", "black", "--check", *files])
run("lint", [PY, "-m", "ruff", "check", *files])
run("original_publication_integrity", [PY, "scripts/publication_bundle.py"])
run("previous_revision_integrity", [PY, "scripts/publication_revision.py"])
run("cognition_edition_integrity", [PY, "scripts/publication_cognition.py"])
run("cognition_and_publication_tests", [PY, "-m", "pytest", "tests/test_cognition_program.py", "tests/test_publication_revision.py", "tests/test_publication_integration.py", "-q"])
run("pyright", [PY, "-m", "pyright"])
run("fast_regressions", [PY, "-m", "pytest", "-m", "not slow", "-q"])
# Hash exact tested source files. This is a test report, not a source-frozen SNN run.
hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
report = {"generated_at": datetime.now(timezone.utc).isoformat(), "base_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "workflow_run_id": os.environ.get("GITHUB_RUN_ID"), "tested_sources_sha256": hashes, "checks": checks, "all_passed": all(check["exit_code"] == 0 for check in checks), "authority": "software_verification_only", "empirical_brain5d_consciousness_experiments": False, "external_ethics_approval": False}
report_path = ROOT / "research/generated/verification/cognition_program.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
allowed = [".maintenance", ".github/workflows/cognition-integration.yml", ".github/workflows/cognition-program.yml", "README.md", "research/publications", "research/README.md", "research/registry/questions.cognition.yaml", "research/registry/hypotheses.cognition.yaml", "research/registry/sources.cognition.yaml", "research/protocols/COGNITION_CONSCIOUSNESS.md", "research/protocols/COGNITION_CONSCIOUSNESS_V1.json", "research/preregistrations/cognition", "research/critique", "research/ethics", "research/literature/COGNITION_SOURCES.md", "research/literature/COGNITION_SOURCES.json", "research/literature/cognition_sources.bib", "research/schemas/cognition_evidence_candidate.schema.json", "research/generated/verification/cognition_program.json", "docs/06-research/CONSCIOUSNESS_AND_WELFARE.md", "docs/08-roadmap/TODO.md", "src/dashboard/static/file-viewer.js", "tests/browser/publication.spec.js", *files]
for path in allowed:
    if (ROOT / path).exists():
        subprocess.run(["git", "add", "--", path], cwd=ROOT, check=True)
# Explicitly forbid changes to historic measurements, registries and old editions.
changed = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).splitlines()
for path in changed:
    if path.startswith(("research/experiments/", "research/registry/evidence/", "research/generated/data/", "research/publications/reader/", "research/publications/2026-09-07_ki-die-geliehene-intelligenz/", "research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/")):
        raise SystemExit(f"Forbidden historical mutation: {path}")
if changed:
    subprocess.run(["git", "config", "user.name", "Brain-5D cognition integration (AI-assisted)"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", "research: integrate cognition critique, task contracts and precautionary boundaries"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "HEAD:refs/heads/" + BRANCH], cwd=ROOT, check=True)
raise SystemExit(0 if report["all_passed"] else 1)
