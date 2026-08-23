#!/usr/bin/env python3
"""
Brain-5D Scientific Evidence Framework — Report Generator

Usage:
    python research/generate_reports.py

Generates all markdown reports from the research registries:
    - RESEARCH_CATALOG.md
    - EVIDENCE_MATRIX.md
    - OPEN_QUESTIONS.md
    - CLAIM_REGISTER.md
    - DISSERTATION_MAP.md
    - LITERATURE_MATRIX.md
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research.registry import ResearchRegistry
from research.report_builder import ReportBuilder
from research.literature_registry import LiteratureRegistry


def main():
    print("Loading research registry...")
    registry = ResearchRegistry()
    registry.load_all()

    print(f"  Questions:  {len(registry.questions)}")
    print(f"  Hypotheses: {len(registry.hypotheses)}")
    print(f"  Claims:     {len(registry.claims)}")
    print(f"  Sources:    {len(registry.sources)}")

    print("\nGenerating reports...")
    builder = ReportBuilder(registry)
    paths = builder.write_all()

    lit_reg = LiteratureRegistry(registry)
    lit_path = lit_reg.write_literature_matrix()

    print("\n✅ Reports generated:")
    for name, path in paths.items():
        size = path.stat().st_size
        print(f"  {name:30s} → {path.relative_to(Path.cwd())} ({size} bytes)")

    size = lit_path.stat().st_size
    print(f"  {'LITERATURE_MATRIX.md':30s} → {lit_path.relative_to(Path.cwd())} ({size} bytes)")

    print("\nDone.")


if __name__ == "__main__":
    main()
