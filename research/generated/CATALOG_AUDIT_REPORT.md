# Repository Catalog Audit Report

**Status:** `CLEAN`

The canonical ResearchRegistry remains authoritative. Historical/design references and test-only fixtures are listed with explicit reasons; an unknown missing identifier fails CI.

## Summary
- Question references: 968
- Hypothesis references: 794
- Missing questions: 24
- Missing hypotheses: 12
- Registry link issues: 0
- Disallowed missing identifiers: 0

## Historical/design references

- `H-GW-01`: Neural Symbiosis design hypothesis without a canonical protocol. Sources: `docs/02-architecture/NEURAL_SYMBIOSIS.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-GW-02`: Neural Symbiosis design hypothesis without a canonical protocol. Sources: `docs/02-architecture/NEURAL_SYMBIOSIS.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-GW-03`: Neural Symbiosis design hypothesis without a canonical protocol. Sources: `docs/02-architecture/NEURAL_SYMBIOSIS.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-GW-04`: Neural Symbiosis design hypothesis without a canonical protocol. Sources: `docs/02-architecture/NEURAL_SYMBIOSIS.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-GW-05`: Neural Symbiosis design hypothesis without a canonical protocol. Sources: `docs/02-architecture/NEURAL_SYMBIOSIS.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-GW-06`: Neural Symbiosis design hypothesis without a canonical protocol. Sources: `docs/02-architecture/NEURAL_SYMBIOSIS.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-MSBA-E`: MSBA programme family shorthand, not a canonical hypothesis ID. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_registry_fragments.py`
- `RQ-AI-DESIGN-001`: Research-positioning design question without a canonical protocol. Sources: `docs/06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md`, `research/registry/catalog_audit_allow_list.yaml`
- `RQ-AI-EFF-001`: Research-positioning efficiency question without a canonical protocol. Sources: `docs/06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md`, `research/registry/catalog_audit_allow_list.yaml`
- `RQ-AUTO-CANDIDATE`: Legacy evidence-engine candidate identifier. Sources: `research/registry/catalog_audit_allow_list.yaml`, `src/research/evidence_engine.py`
- `RQ-CAUSAL-001`: Research-positioning causal question without a canonical protocol. Sources: `docs/06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md`, `research/registry/catalog_audit_allow_list.yaml`
- `RQ-LAT-001`: Research-positioning latency question without a canonical protocol. Sources: `docs/06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md`, `research/registry/catalog_audit_allow_list.yaml`
- `RQ-LEARN-INTERF-001`: Follow-up programme question pending canonical registration. Sources: `research/protocols/EXP_GEN_0021_FOLLOWUP_PROGRAM.yaml`, `research/registry/catalog_audit_allow_list.yaml`
- `RQ-MSBA-E`: MSBA programme family shorthand, not a canonical question ID. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_registry_fragments.py`
- `RQ-PHIL-001`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `docs/08-roadmap/TODO_SELF_MODEL_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-002`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-003`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-004`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-005`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-006`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-007`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-008`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-PHIL-009`: Philosophical design question kept in its dedicated source file. Sources: `docs/06-research/PHILOSOPHICAL_SELF_MODEL_AND_THINKING.md`, `docs/08-roadmap/TODO_SELF_MODEL_THINKING.md`, `research/registry/catalog_audit_allow_list.yaml`, `research/registry/philosophical_questions_claims.yaml`
- `RQ-SELFMDL-001`: Research-positioning self-model question without a canonical protocol. Sources: `docs/06-research/RESEARCH_POSITIONING_AND_EVIDENCE_PROGRAM.md`, `research/registry/catalog_audit_allow_list.yaml`

## Test fixtures

- `H-BASE-001-A`: Registry-fragment test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_registry_fragments.py`
- `H-BROWSER-001-A`: Browser test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/browser/dashboard.spec.js`
- `H-EXTRA-E01-A`: Registry-fragment test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_registry_fragments.py`
- `H-MISSING-001`: Catalog-audit negative test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_catalog_audit.py`
- `H-TEST-001-A`: Catalog-audit test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_experiment_validity.py`, `tests/test_research_catalog_audit.py`, `tests/test_research_question_maturity.py`, `tests/test_scientific_execution_contract.py`
- `RQ-BASE-001`: Registry-fragment test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_registry_fragments.py`
- `RQ-BROWSER-001`: Browser test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/browser/dashboard.spec.js`
- `RQ-BROWSER-002`: Browser test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/browser/dashboard.spec.js`
- `RQ-DUP-001`: Duplicate-registry test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_registry_fragments.py`
- `RQ-EXTRA-E01`: Registry-fragment test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_registry_fragments.py`
- `RQ-MISSING-001`: Catalog-audit negative test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_research_catalog_audit.py`
- `RQ-TEST-001`: Catalog-audit test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_dashboard_batch_routes.py`, `tests/test_experiment_validity.py`, `tests/test_neural_symbiosis.py`, `tests/test_research_catalog_audit.py`, `tests/test_research_question_maturity.py`

## Failures

None.
