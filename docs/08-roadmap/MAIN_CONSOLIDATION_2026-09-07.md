# Main consolidation - 2026-09-07

AI-assisted engineering record; not a human scientific review.

The concurrent file-viewer work through `ff173aded229f5fe978048adf9eae75bda188ab0`
is preserved, including archive/JSON rendering, Windows paths, navigation,
BibTeX links and flowing Markdown prose.

- `fix/footer-runtime-recovery-green-base` (`b242a96`) was already in main.
- `fix/footer-runtime-responsiveness-ci` (`8b4f434`) was merged at `65b8026`.
  Its behavior already exists in the newer canonical footer. Conflict resolution
  retains single dispatch, MAX yield, mode feedback, current styles and the
  duplicate-footer guard instead of restoring an obsolete second footer.
- `integration/scientific-publication-20260907` (`c6b7b6d`) was merged via PR #24
  at `b5c7740`. The complete publication contains 41 verified files plus its
  original archive and repository integrity manifest.

The central file renderer remains shared by the File Viewer and chat. Research
publications are now discoverable and immutable through the file API. Their
bytes are checked against the delivered SHA-256 manifest. Formatting hooks do
not rewrite publications or frozen preregistrations.

The prepared verification repair addresses XML DTD/entity attacks including
UTF-16 input, install-metadata-induced false baseline changes, missing final
newlines and incorrect wheel namespace/static-asset packaging. Verification
must use the final source tree; a pending CI run is not a passed CI run.

The maintenance workflow refreshes the real full-suite baseline and determinism
artifacts, checks style/types/security/build, and dispatches complete CI including
Playwright. Branch cleanup verifies ancestry and exact reviewed remote tips.
Concurrent new work aborts deletion; main is never force-overwritten.

Completed transport payloads and import automation are retired. Publication
import instructions are preserved in `docs/99-archive/publication-import/`.
Frozen DATA, preregistrations and evidence are unchanged. Human review,
EVID promotion and remaining research TODOs remain explicitly open. A clean
runner checkout does not assert that a user's local Windows tree is clean.


## Concurrent integration follow-up

PR #26 integrated `fix/publication-research-integration-20260907` at
`f0007c3e332add3032ec4d26ba3ffe79e2f262d5`. Its original tip is
`cbc7f78850ad22d6ea2b0eb1405c09b851f98f3d`. Subsequent main speech-reader and
research-report improvements are retained. The publication toolbar shortcut
uses the same file renderer; both isolated browser fixtures contain the full
publication. Duplicate category entries are not introduced by consolidation.

The eight manuscript synthesis hypotheses remain PROPOSED_NOT_REGISTERED.
The catalog report lists them separately and accepts these references only in
publication files and their explicit audit map. Referencing an unregistered
proposal from an operational protocol still fails the audit. No experiment,
preregistration, evidence promotion or human approval is invented.
