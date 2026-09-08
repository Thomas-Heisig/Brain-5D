"""Execute the naming-only migration and record actual verification results."""
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
checks = []


def run(name: str, command: list[str]) -> bool:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(f"{name}: exit={result.returncode}\n{result.stdout[-9000:]}", flush=True)
    checks.append({"check": name, "command": command, "exit_code": result.returncode, "output": result.stdout[-20000:]})
    return result.returncode == 0


def main() -> None:
    if os.environ.get("GITHUB_REF_NAME") != "migration/mhrn-20260908":
        raise ValueError("Naming materialization is confined to the migration branch")
    start = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if not Path(".maintenance/mhrn-migration-complete.json").exists():
        if not run("platform_identity_attempt", [sys.executable, ".maintenance/mhrn_platforms.py"]):
            raise ValueError("Platform identity report unavailable")
        if not run("materialize_naming", [sys.executable, ".maintenance/mhrn_migrate.py"]):
            raise ValueError("Naming migration failed")
    platform = json.loads(Path("docs/05-quality/mhrn-platform-migration.json").read_text(encoding="utf-8"))
    sync = Path(".github/workflows/sync-huggingface.yml")
    text = sync.read_text(encoding="utf-8")
    import re
    text = re.sub(r"HF_REPO: [^\n]+", "HF_REPO: " + platform["huggingface_model"]["actual"].split("/")[-1], text)
    text = re.sub(r"HF_SPACE_REPO: [^\n]+", "HF_SPACE_REPO: " + platform["huggingface_space"]["actual"].split("/")[-1], text)
    sync.write_text(text, encoding="utf-8")
    browser = Path("tests/browser/publication.spec.js")
    text = browser.read_text(encoding="utf-8").replace("Aktuelle Fassung 1.2", "Edition 1.3").replace("Historische Lesefassung 1.0", "Lesefassung 1.0")
    if "mhrn_new_edition" not in text:
        text = text.replace("    await viewer.getByRole('button', { name: 'Lesefassung 1.0', exact: true }).click();", """    // mhrn_new_edition: new source plus historical source remain reachable.
    const newBase = 'publications/2026-09-08_recursive-epistemics_v1.3/';
    await viewer.getByRole('button', { name: 'Die vollständige aktuelle wissenschaftliche Abhandlung lesen', exact: true }).click();
    await expect(viewer).toContainText('Recursive Epistemics in Embodied');
    await expect(viewer).toContainText('Rekursive Epistemik in verkörperten');
    const currentManifestResponse = await page.request.get(`http://127.0.0.1:${port}/api/files/preview/` + encodeURIComponent(newBase + 'manifest.json') + '?source=research');
    const currentManifest = JSON.parse((await currentManifestResponse.json()).content);
    expect(currentManifest.section_count).toBe(57);
    for (const name of currentManifest.section_order) {
      const r = await page.request.get(`http://127.0.0.1:${port}/api/files/preview/` + encodeURIComponent(newBase + name) + '?source=research');
      const d = await r.json();
      expect(d.truncated, name).toBe(false);
      expect(d.read_only, name).toBe(true);
    }
    await viewer.getByRole('button', { name: 'Publikationsübersicht', exact: true }).click();
    await viewer.getByRole('button', { name: 'Lesefassung 1.0', exact: true }).click();""")
    browser.write_text(text, encoding="utf-8")
    # Workflow files are committed through the authorized connector, not the runner token.
    subprocess.run(["git", "restore", "--source=HEAD", "--staged", "--worktree", "--", ".github/workflows"], check=True)
    # Workflow files are committed through the authorized connector, not the runner token.
    subprocess.run(["git", "restore", "--source=HEAD", "--staged", "--worktree", "--", ".github/workflows"], check=True)
    run("format", [sys.executable, "-m", "black", "src", "tests", "scripts"])
    run("lint_fix", [sys.executable, "-m", "ruff", "check", "--fix", "src", "tests", "scripts"])
    run("format_check", [sys.executable, "-m", "black", "--check", "src", "tests", "scripts"])
    run("lint", [sys.executable, "-m", "ruff", "check", "src", "tests", "scripts"])
    run("reinstall_named_package", [sys.executable, "-m", "pip", "install", "-e", ".[dev,docs]"])
    for item in ("publication_bundle", "publication_revision", "publication_cognition", "publication_naming"):
        run(item, [sys.executable, "scripts/" + item + ".py"])
    run("naming_regressions", [sys.executable, "-m", "pytest", "tests/test_mhrn_naming.py", "-q"])
    run("pyright", [sys.executable, "-m", "pyright"])
    run("mypy", [sys.executable, "-m", "mypy", "src/"])
    run("fast_regressions", [sys.executable, "-m", "pytest", "-m", "not slow", "-q"])
    run("build", [sys.executable, "-m", "build", "--wheel", "--outdir", os.environ["RUNNER_TEMP"] + "/mhrn-wheel"])
    run("browser_dependencies", ["npm", "ci"])
    run("chromium", ["npx", "playwright", "install", "--with-deps", "chromium"])
    run("browser_suite", ["npx", "playwright", "test"])
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "base_head": start,
              "workflow_run_id": os.environ.get("GITHUB_RUN_ID"), "checks": checks,
              "all_checks_passed": all(item["exit_code"] == 0 for item in checks),
              "authority": "software_verification_only", "platform_operations": platform}
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    report["tested_file_sha256"] = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in changed if Path(name).is_file()}
    path = Path("docs/05-quality/mhrn-verification.json")
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["git", "config", "user.name", "MHRN naming migration (AI-assisted)"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "refactor: apply MHRN identity and bilingual Recursive Epistemics edition"], check=True)
    subprocess.run(["git", "push", "origin", "HEAD:refs/heads/migration/mhrn-20260908"], check=True)
    raise SystemExit(0 if report["all_checks_passed"] else 1)


if __name__ == "__main__":
    main()
