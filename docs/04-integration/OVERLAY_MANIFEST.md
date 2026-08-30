# Brain-5D repository overlay — v0.5.0-alpha.5

This overlay combines the current alpha.5 README/documentation update with
community, security, GitHub template, CI, user-guide and developer-guide files.

## Files

- README.md
- LICENSE
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- setup.py
- .github/ISSUE_TEMPLATE/bug_report.md
- .github/ISSUE_TEMPLATE/feature_request.md
- .github/PULL_REQUEST_TEMPLATE.md
- .github/workflows/ci.yml
- docs/01-guides/UserGuide.md
- docs/01-guides/DeveloperGuide.md
- docs/02-architecture/Brain-5D_STORAGE_THEORY_ALPHA5_UPDATE.md
- docs/02-architecture/STRUCTURAL_PLASTICITY_ALPHA5.md
- docs/08-roadmap/ROADMAP_ALPHA5_TO_ALPHA6.md

## Important integration notes

- `pyproject.toml` remains the authoritative build configuration.
- `setup.py` is only a compatibility shim.
- No fabricated security e-mail address is inserted.
- SECURITY.md directs sensitive reports to GitHub private security reporting
  when available.
- CI uses the currently verified alpha.5 strict-Pyright production scope rather
  than pretending that the entire historical repository is strict-Pyright clean.
- Auto-approval remains OFF by default.
- Neuron pruning remains OFF by default.

## Suggested review

```powershell
git status
git diff -- README.md LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md .github docs setup.py
git diff --check
```

Then run the repository quality gates before committing.
