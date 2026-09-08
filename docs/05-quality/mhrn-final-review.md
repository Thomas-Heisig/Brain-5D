# MHRN naming migration: final review

8 September 2026. Active identity is defined by `project_identity.json`; current publication is Recursive Epistemics, edition 1.3, with its German subtitle. The GitHub slug rename was denied with HTTP 403 and the Hugging Face credentials required by the existing workflow were unavailable. Neither remote operation is claimed as completed. See [platform outcomes](mhrn-platform-migration.json).

## Verified implementation

[MHRN verification](mhrn-verification.json) records the real migration run 34192118327: 945 fast Python tests passed, 32 slow tests deselected, 13 naming tests passed, 15 Playwright tests passed, Black/Ruff succeeded, Pyright reported zero errors/warnings, mypy checked 152 source files without issues, and the named wheel built successfully. Publication validators checked the old editions and the new 57-section edition. This is software verification, not scientific evidence.

The tested runtime/UI implementation is preserved in commit `9ec212e5b96bbad1d1c170a432a40bac6bda669e`. The final archival correction restores only the five historical files below to their exact original blobs from `7897fa43ff63b5e851acd9e317ca4845b22cd977`; no current runtime implementation or current publication chapter is changed by that correction. The preceding test report remains a dated, source-bound record, not a claim that a new full test run happened after an archival-only restoration.

## Archival correction

| Historical path | Restored Git blob |
| --- | --- |
| `docs/06-research/old/Eine hybride neural-symbolische Architektur für verkörperte kognitive Systeme.md` | `f3a69e69e35461783af719c7d8c37bb9a5c41ef7` |
| `docs/06-research/old/RESEARCH_ALIGNMENT.md` | `a36cfb606977528e3ae2e2671ddb57bd5482d029` |
| `docs/07-changelog/CHANGELOG.md` | `80494d10f872103df98ea73a4311acd31df157a2` |
| `scripts/update_dissertation_results.py` | `af96c70c895042e297f16449dec941b27cb605c5` |
| `scripts/archive/legacy-v040_verify_all.py` | `a93734ce99030060dd322f28a42d421a5dd02660` |

These paths had been swept into the intermediate public-label replacement. Their restoration is intentional: old manuscripts and changelogs document their historical names. In particular, the legacy dissertation updater's original append marker must remain unchanged to avoid duplicating an existing historical DOCX addendum. It is not the export entrypoint for edition 1.3. The current source-bound export is `scripts/publication_naming.py`.

The detailed naming audit records the initial migration pass; this final review overrides its changed-file classification for the five restored archival paths. Earlier publications, DATA, EVID and preregistration records were not rewritten. No external local clone, previously sent Word attachment, GitHub ownership/visibility or account credentials were changed.
