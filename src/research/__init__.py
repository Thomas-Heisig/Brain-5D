"""
Brain-5D Scientific Evidence Framework (B5D-SEF)
================================================

A self-tracking scientific evidence system that turns every Brain-5D run into
a documented, reproducible experiment with explicit links from research
questions through hypotheses and experiments to evidence and claims.

Modules:
    registry       — Load/save/query research registries (questions, hypotheses, claims)
    experiment_recorder — Capture experiment manifests during Brain-5D runs
    evidence_engine     — Evaluate evidence strength and update claim/hypothesis status
    literature_registry — Manage BibTeX sources and literature mappings
    report_builder      — Generate markdown reports (catalog, matrix, dissertation map)
"""

__version__ = "0.1.0"
