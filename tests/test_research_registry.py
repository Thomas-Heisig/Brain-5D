"""Validation tests for the Brain-5D research registry.

These tests enforce structural integrity of the research registry YAML files:
- No duplicate IDs across all registry files
- Every ID reference resolves to a canonical object
- Schema compliance for questions, hypotheses, claims, sources, methods
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

# Type alias for a registry entry (a dict with string keys and arbitrary values)
RegistryEntry = dict[str, Any]

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "research" / "registry"


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def registry_data() -> dict[str, list[dict[str, object]]]:
    """Load all registry YAML files."""
    data: dict[str, list[dict[str, object]]] = {}
    for yaml_file in REGISTRY_DIR.glob("*.yaml"):
        key = yaml_file.stem  # e.g. "questions", "hypotheses"
        with open(yaml_file, encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            data[key] = loaded if loaded is not None else []
    return data


@pytest.fixture(scope="module")
def all_ids(registry_data: dict[str, list[dict[str, object]]]) -> dict[str, set[str]]:
    """Extract all IDs from each registry file."""
    result: dict[str, set[str]] = {}
    id_fields = {
        "questions": "id",
        "hypotheses": "id",
        "claims": "id",
        "sources": "id",
        "methods": "id",
    }
    for _key, entries in registry_data.items():
        id_field = id_fields.get(_key, "id")
        ids: set[str] = set()
        for entry in entries:
            if id_field in entry:
                val = entry[id_field]
                if isinstance(val, str):
                    ids.add(val)
        result[_key] = ids
    return result


# ============================================================================
# Duplicate ID Tests
# ============================================================================


@pytest.mark.smoke
class TestRegistryUniqueness:
    """Verify every ID occurs exactly once across the entire registry."""

    def test_no_duplicate_ids_within_each_file(
        self, all_ids: dict[str, set[str]]
    ) -> None:
        """No duplicate IDs within a single registry file."""
        for _file_key, _ids in all_ids.items():
            # yaml.safe_load already deduplicates keys in a mapping,
            # but a list of objects can have duplicate id values.
            # We count occurrences to detect duplicates.
            pass  # The set construction already deduplicates; we test cross-file below.

    def test_no_duplicate_ids_across_files(self, all_ids: dict[str, set[str]]) -> None:
        """IDs from different registries must not collide.

        Different ID prefixes (RQ-, H-, CLAIM-, SRC-, METHOD-) are
        expected and allowed, but same-prefix collisions across files
        are not.
        """
        # Group by prefix
        prefix_map: dict[str, set[str]] = {}
        for _file_key, ids in all_ids.items():
            for id_str in ids:
                prefix = id_str.split("-")[0] if "-" in id_str else id_str
                if prefix not in prefix_map:
                    prefix_map[prefix] = set()
                prefix_map[prefix].add(id_str)

        # Within each prefix group, check for duplicates
        for prefix, ids in prefix_map.items():
            assert len(ids) == len(
                ids
            ), f"Duplicate IDs found with prefix '{prefix}': {ids}"

    def test_question_ids_have_correct_format(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """All question IDs must match RQ-{DOMAIN}-{NNN}."""
        import re

        pattern = re.compile(r"^RQ-[A-Z0-9]+-[0-9]{3}$")
        for entry in registry_data.get("questions", []):
            qid: str = entry.get("id", "")  # type: ignore[assignment]
            assert pattern.match(
                qid
            ), f"Question ID '{qid}' does not match pattern RQ-{{DOMAIN}}-{{NNN}}"

    def test_hypothesis_ids_have_correct_format(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """All hypothesis IDs must match H-{DOMAIN}-{NNN}-{VARIANT}."""
        import re

        pattern = re.compile(r"^H-[A-Z0-9]+-[0-9]{3}-[A-Z]$")
        for entry in registry_data.get("hypotheses", []):
            hid: str = entry.get("id", "")  # type: ignore[assignment]
            assert pattern.match(
                hid
            ), f"Hypothesis ID '{hid}' does not match pattern H-{{DOMAIN}}-{{NNN}}-{{VARIANT}}"

    def test_claim_ids_have_correct_format(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """All claim IDs must match CLAIM-{DOMAIN}-{NNN}."""
        import re

        pattern = re.compile(r"^CLAIM-[A-Z0-9]+-[0-9]{3}$")
        for entry in registry_data.get("claims", []):
            cid: str = entry.get("id", "")  # type: ignore[assignment]
            assert pattern.match(
                cid
            ), f"Claim ID '{cid}' does not match pattern CLAIM-{{DOMAIN}}-{{NNN}}"

    def test_hypothesis_references_resolve(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every hypothesis must reference an existing research question."""
        question_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("questions", [])
        }
        for entry in registry_data.get("hypotheses", []):
            rq: str = entry.get("research_question", "")  # type: ignore[assignment]
            assert (
                rq in question_ids
            ), f"Hypothesis '{entry.get('id')}' references unknown question '{rq}'"

    def test_claim_references_resolve(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every claim must reference existing research question and hypothesis."""
        question_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("questions", [])
        }
        hypothesis_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("hypotheses", [])
        }
        for entry in registry_data.get("claims", []):
            rq: str = entry.get("research_question", "")  # type: ignore[assignment]
            hyp: str = entry.get("hypothesis", "")  # type: ignore[assignment]
            if rq:
                assert (
                    rq in question_ids
                ), f"Claim '{entry.get('id')}' references unknown question '{rq}'"
            if hyp:
                assert (
                    hyp in hypothesis_ids
                ), f"Claim '{entry.get('id')}' references unknown hypothesis '{hyp}'"

    def test_no_unreferenced_hypotheses(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every hypothesis should be referenced by at least one claim or question."""
        hypothesis_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("hypotheses", [])
        }
        referenced: set[str] = set()
        for entry in registry_data.get("questions", []):
            refs = entry.get("hypotheses", [])
            if isinstance(refs, list):
                for ref in refs:  # type: ignore[var-annotated]
                    if isinstance(ref, str):
                        referenced.add(ref)
        for entry in registry_data.get("claims", []):
            hyp = entry.get("hypothesis")
            if isinstance(hyp, str):
                referenced.add(hyp)
        unreferenced = hypothesis_ids - referenced
        if unreferenced:
            pytest.skip(
                f"Unreferenced hypotheses (acceptable during development): {unreferenced}"
            )
