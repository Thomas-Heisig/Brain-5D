# Empirical delivery checkpoint — 2026-09-10

PR #45 was merged as `02c4be170e8c56fb054a3ab17f3278e9528e6b84`. The research-report job subsequently regenerated only `research/generated/EVIDENCE_MATRIX.md`, `OPEN_QUESTIONS.md`, and `RESEARCH_CATALOG.md` in `c51e512ad03995c09659d2bdb5d20e1e8de4bea5`.

The immutable primary campaign and addressing amendment contain 1,287 executed seed/condition records. The original failed scaling attempt and failed Brian2 conformance outcomes remain preserved. Manuscript 1.4 contains 57 explicitly historical chapters and four new empirical/methodological chapters. These are exploratory DATA and interpretation, not accepted EVID, independent replication, completed human reviews or institutional ethics approval.

Validated PR head: `f7cd978174593a552fb3f4d1a179086490d2c475`. PR CI run `34501609278` and empirical DATA/manuscript integrity run `34501609403` completed successfully. The source-bound Python baseline records 1,128 passed, two optional large-storage skips and zero failures. New main commits are checked separately by the ordinary CI pipeline; this document does not substitute for their actual job results.

## Hugging Face: publication was NOT performed

Sync workflow run `34502724651`, job `102957202878`, exited successfully only because its optional configuration check skipped publication. Its actual message was:

> Hugging Face mirror is not configured; skipping optional sync.

Both `HF_USERNAME` and `HF_TOKEN` were empty in that job. A green optional-sync workflow is therefore **not** evidence that the model repository or Space received manuscript 1.4 or the DATA. No Hugging Face publication/merge is claimed at this checkpoint.

To enable the existing publication path, configure the repository Actions secrets `HF_USERNAME` and `HF_TOKEN` with the intended Hugging Face account and appropriate repository write access, then explicitly run the existing **Sync to Hugging Face** workflow. Do not put credentials into files, issues or chat. Verify the actual remote revision after the push; do not infer success from an optional skip.

[Empirical report](../../research/experiments/EXP-EMP-20260910/ANALYSIS.md) · [Manuscript 1.4](../../research/publications/2026-09-10_recursive-epistemics_v1.4/README.md)
