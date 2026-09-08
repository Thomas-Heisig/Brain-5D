"""Refresh source-bound verification after the reviewed naming migration.

The catalog correction recognizes only an exact declared namespace prefix in
its defining governance module. Unknown entities elsewhere must still fail.
Test totals are taken from an actual complete run, never edited by assumption.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
BRANCH = "fix/mhrn-verification-20260908"
LOG = ROOT / "docs/05-quality/mhrn-post-migration-verification.json"
checks = []


def run(name: str, command: list[str]) -> bool:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, check=False)
    print(name + ": " + str(result.returncode) + "\n" + result.stdout[-10000:], flush=True)
    checks.append({"check": name, "command": command, "exit_code": result.returncode,
                   "output": result.stdout[-20000:]})
    return result.returncode == 0


def save() -> None:
    report = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "tested_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "run_id": os.environ.get("GITHUB_RUN_ID"), "checks": checks,
              "all_checks_passed": bool(checks) and all(v["exit_code"] == 0 for v in checks),
              "authority": "software_verification_only"}
    LOG.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if os.environ.get("GITHUB_REF_NAME") != BRANCH:
        raise ValueError("Use the isolated verification branch")
    subprocess.run(["git", "config", "user.name", "MHRN verification (AI-assisted)"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    path = ROOT / "scripts/generate_catalog_audit_report.py"
    text = path.read_text(encoding="utf-8")
    if '"namespace_prefixes":' not in text:
        needle = '    historical = set(allow_list["historical_only"])'
        replacement = '''    # Namespace selectors are not entity IDs. Keep this exception exact and
    # confined to the defining module; a matching reference elsewhere fails.
    from src.research.cognition_governance import HYPOTHESIS_PREFIXES, PREFIXES

    declared_prefixes = set(PREFIXES) | set(HYPOTHESIS_PREFIXES)
    namespace_prefixes = {
        identifier
        for identifier in missing & declared_prefixes
        if _references_for(audit, identifier)
        == ["src/research/cognition_governance.py"]
    }
    historical = set(allow_list["historical_only"])
'''
        if needle not in text:
            raise ValueError("Catalog report source changed")
        text = text.replace(needle, replacement.rstrip())
        text = text.replace('disallowed = sorted(missing - historical - fixtures - scoped_proposals)',
                            'disallowed = sorted(\n        missing - historical - fixtures - scoped_proposals - namespace_prefixes\n    )')
        needle = '        "disallowed_missing": {'
        addition = '''        "namespace_prefixes": {
            identifier: {
                "reason": "Exact declared governance family selector, not a research entity; allowed only in its defining module.",
                "references": _references_for(audit, identifier),
            }
            for identifier in sorted(namespace_prefixes)
        },
'''
        text = text.replace(needle, addition + needle)
        text = text.replace('        ("Test fixtures", "test_fixtures"),',
                            '        ("Test fixtures", "test_fixtures"),\n        ("Code namespace selectors - not research entities", "namespace_prefixes"),')
        path.write_text(text, encoding="utf-8")
    if not run("format_catalog_tests", [sys.executable, "-m", "black", "scripts/generate_catalog_audit_report.py", "tests/test_catalog_namespace_prefixes.py"]):
        raise SystemExit(1)
    if not run("lint_catalog_tests", [sys.executable, "-m", "ruff", "check", "scripts/generate_catalog_audit_report.py", "tests/test_catalog_namespace_prefixes.py"]):
        raise SystemExit(1)
    subprocess.run(["git", "add", "scripts/generate_catalog_audit_report.py", "tests/test_catalog_namespace_prefixes.py"], check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], check=False).returncode:
        subprocess.run(["git", "commit", "-m", "fix: distinguish exact governance namespace selectors from research entities"], check=True)
    protected_roots = [ROOT / "research/experiments", ROOT / "research/preregistrations", ROOT / "research/registry/evidence", ROOT / "research/publications"]
    protected = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                 for base in protected_roots for p in base.rglob("*") if p.is_file()}
    run("catalog_negative_and_positive_tests", [sys.executable, "-m", "pytest", "tests/test_catalog_audit_report.py", "tests/test_catalog_namespace_prefixes.py", "-q"])
    run("catalog_audit", [sys.executable, "scripts/generate_catalog_audit_report.py"])
    run("complete_baseline_real_execution", [sys.executable, "scripts/generate_baseline.py"])
    run("documentation_consistency", [sys.executable, "scripts/check_doc_consistency.py", "--check-tests"])
    run("publication_naming", [sys.executable, "scripts/publication_naming.py"])
    run("pyright", [sys.executable, "-m", "pyright"])
    run("format", [sys.executable, "-m", "black", "--check", "src", "tests", "scripts"])
    run("lint", [sys.executable, "-m", "ruff", "check", "src", "tests", "scripts"])
    changed = [p for p, sha in protected.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest() != sha]
    checks.append({"check": "historical_scientific_bytes_unchanged", "exit_code": int(bool(changed)), "paths_changed": changed})
    save()
    subprocess.run(["git", "add", "tests/test_baseline.json", "research/generated", "docs/05-quality/mhrn-post-migration-verification.json"], check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], check=False).returncode:
        subprocess.run(["git", "commit", "-m", "test: publish genuinely executed full MHRN baseline and catalog verification"], check=True)
    subprocess.run(["git", "push", "origin", "HEAD:refs/heads/" + BRANCH], check=True)
    raise SystemExit(0 if all(v["exit_code"] == 0 for v in checks) else 1)


if __name__ == "__main__":
    main()
