# Repository Catalog Audit Report

**Status:** `CLEAN`

The canonical ResearchRegistry remains authoritative. Historical/design references and test-only fixtures are listed with explicit reasons; an unknown missing identifier fails CI.

## Summary
- Question references: 1486
- Hypothesis references: 1251
- Missing questions: 25
- Missing hypotheses: 21
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
- `RQ-TEST-001`: Catalog-audit test fixture. Sources: `research/registry/catalog_audit_allow_list.yaml`, `tests/test_dashboard_batch_routes.py`, `tests/test_experiment_validity.py`, `tests/test_neural_symbiosis.py`, `tests/test_research_catalog_audit.py`, `tests/test_research_question_maturity.py`, `tests/test_research_report_generation.py`

## Code namespace selectors - not research entities

- `H-EPI-1`: Exact declared governance family selector, not a research entity; allowed only in its defining module. Sources: `src/research/cognition_governance.py`
- `RQ-EPI-1`: Exact declared governance family selector, not a research entity; allowed only in its defining module. Sources: `src/research/cognition_governance.py`

## Publication proposals - not registered or executed

- `H-SYN-01`: Review-packet compaction proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-SYN-02`: Resource-feedback recovery proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-SYN-03`: Self-state calibration proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-SYN-04`: Geometry-mechanism proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-SYN-05`: Local regulation-error proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-SYN-06`: Source and approval-status consistency proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-SYN-07`: Persistence versus episodic-recall proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`
- `H-SYN-08`: Intervention-window proposal; not preregistered and no evidence. Sources: `research/publications/2026-09-07_ki-die-geliehene-intelligenz/forschungsfragen_hypothesen.json`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz/wissenschaftliche_abhandlung.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.1/section-035.md`, `research/publications/2026-09-07_ki-die-geliehene-intelligenz_v1.2/section-035.md`, `research/publications/2026-09-08_recursive-epistemics_v1.3/section-035.md`, `research/publications/reader/section-035.md`, `research/registry/catalog_audit_allow_list.yaml`

## Failures

None.
