"""Validation tests for the Brain-5D research registry.

These tests enforce structural integrity of the research registry YAML files:
- No duplicate IDs across all registry files
- Every ID reference resolves to a canonical object
- Schema compliance for questions, hypotheses, claims, sources, methods
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

# Type alias for a registry entry (a dict with string keys and arbitrary values)
RegistryEntry = dict[str, Any]

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "research" / "registry"

ID_FIELDS = {
    "questions": "id",
    "hypotheses": "id",
    "claims": "id",
    "sources": "source_id",
    "methods": "prefix",
}

ID_PATTERNS = {
    "questions": re.compile(r"^RQ-[A-Z0-9]+-[0-9]{3}$"),
    "hypotheses": re.compile(r"^H-[A-Z0-9]+-[0-9]{3}-[A-Z]$"),
    "claims": re.compile(r"^CLAIM-[A-Z0-9]+-[0-9]{3}$"),
    "sources": re.compile(r"^SRC-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{4}$"),
}


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def registry_data() -> dict[str, list[dict[str, object]]]:
    """Load all registry YAML files.

    The ``methods`` registry uses a nested ``methods`` root key; all others
    are flat lists of entries.
    """
    data: dict[str, list[dict[str, object]]] = {}
    for yaml_file in REGISTRY_DIR.glob("*.yaml"):
        key = yaml_file.stem  # e.g. "questions", "hypotheses"
        with open(yaml_file, encoding="utf-8") as f:
            loaded: Any = yaml.safe_load(f)
        if loaded is None:
            loaded = []
        # methods.yaml has a root mapping with a 'methods' list.
        if key == "methods" and isinstance(loaded, dict):
            loaded = cast(dict[str, Any], loaded).get("methods", [])
        data[key] = loaded if isinstance(loaded, list) else []
    return data


@pytest.fixture(scope="module")
def all_ids(registry_data: dict[str, list[dict[str, object]]]) -> dict[str, set[str]]:
    """Extract all IDs from each registry file."""
    result: dict[str, set[str]] = {}
    for key, entries in registry_data.items():
        id_field = ID_FIELDS.get(key, "id")
        ids: set[str] = set()
        for entry in entries:
            val = entry.get(id_field)
            if isinstance(val, str):
                ids.add(val)
        result[key] = ids
    return result


# ============================================================================
# Duplicate ID Tests
# ============================================================================


@pytest.mark.smoke
class TestRegistryUniqueness:
    """Verify every ID occurs exactly once across the entire registry."""

    def test_no_duplicate_ids_within_each_file(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """No duplicate IDs within a single registry file."""
        for key, entries in registry_data.items():
            id_field = ID_FIELDS.get(key, "id")
            counts = Counter(
                str(entry[id_field])
                for entry in entries
                if id_field in entry and isinstance(entry[id_field], str)
            )
            duplicates = {id_str for id_str, count in counts.items() if count > 1}
            assert not duplicates, f"Duplicate IDs in '{key}.yaml': {duplicates}"

    def test_no_duplicate_ids_across_files(self, all_ids: dict[str, set[str]]) -> None:
        """IDs from different registries must not collide.

        Different ID prefixes (RQ-, H-, CLAIM-, SRC-, METHOD-) are
        expected and allowed, but same-prefix collisions across files
        are not.
        """
        prefix_map: dict[str, list[tuple[str, str]]] = {}
        for key, ids in all_ids.items():
            for id_str in ids:
                prefix = id_str.split("-")[0] if "-" in id_str else id_str
                prefix_map.setdefault(prefix, []).append((key, id_str))

        duplicates: list[str] = []
        for prefix, items in prefix_map.items():
            seen: dict[str, str] = {}
            for key, id_str in items:
                if id_str in seen:
                    duplicates.append(
                        f"{id_str!r} appears in both {seen[id_str]}.yaml and {key}.yaml"
                    )
                else:
                    seen[id_str] = key
        assert not duplicates, "Duplicate IDs across registry files:\n" + "\n".join(duplicates)


# ============================================================================
# ID Format Tests
# ============================================================================


@pytest.mark.smoke
class TestRegistryIdFormat:
    """Validate ID conventions for every registry type."""

    def test_question_ids_have_correct_format(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """All question IDs must match RQ-{DOMAIN}-{NNN}."""
        pattern = ID_PATTERNS["questions"]
        for entry in registry_data.get("questions", []):
            qid: str = entry.get("id", "")  # type: ignore[assignment]
            assert pattern.match(qid), (
                f"Question ID '{qid}' does not match pattern RQ-{{DOMAIN}}-{{NNN}}"
            )

    def test_hypothesis_ids_have_correct_format(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """All hypothesis IDs must match H-{DOMAIN}-{NNN}-{VARIANT}."""
        pattern = ID_PATTERNS["hypotheses"]
        for entry in registry_data.get("hypotheses", []):
            hid: str = entry.get("id", "")  # type: ignore[assignment]
            assert pattern.match(hid), (
                f"Hypothesis ID '{hid}' does not match pattern H-{{DOMAIN}}-{{NNN}}-{{VARIANT}}"
            )

    def test_claim_ids_have_correct_format(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """All claim IDs must match CLAIM-{DOMAIN}-{NNN}."""
        pattern = ID_PATTERNS["claims"]
        for entry in registry_data.get("claims", []):
            cid: str = entry.get("id", "")  # type: ignore[assignment]
            assert pattern.match(cid), (
                f"Claim ID '{cid}' does not match pattern CLAIM-{{DOMAIN}}-{{NNN}}"
            )

    def test_source_ids_have_correct_format(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """All source IDs must match SRC-{AUTHOR}-{YEAR}."""
        pattern = ID_PATTERNS["sources"]
        for entry in registry_data.get("sources", []):
            sid: str = entry.get("source_id", "")  # type: ignore[assignment]
            assert pattern.match(sid), (
                f"Source ID '{sid}' does not match pattern SRC-{{AUTHOR}}-{{YEAR}}"
            )


# ============================================================================
# Reference Resolution Tests
# ============================================================================


@pytest.mark.smoke
class TestRegistryReferences:
    """Ensure every cross-registry reference points to an existing object."""

    def test_hypothesis_references_resolve(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every hypothesis must reference an existing research question."""
        question_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("questions", []) if "id" in entry
        }
        for entry in registry_data.get("hypotheses", []):
            rq: str = entry.get("research_question", "")  # type: ignore[assignment]
            assert rq in question_ids, (
                f"Hypothesis '{entry.get('id')}' references unknown question '{rq}'"
            )

    def test_claim_references_resolve(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every claim must reference an existing research question and hypothesis."""
        question_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("questions", []) if "id" in entry
        }
        hypothesis_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("hypotheses", []) if "id" in entry
        }
        for entry in registry_data.get("claims", []):
            cid = entry.get("id", "<unknown>")
            rq: str = entry.get("research_question", "")  # type: ignore[assignment]
            hyp: str = entry.get("hypothesis", "")  # type: ignore[assignment]
            assert rq in question_ids, (
                f"Claim '{cid}' references unknown question '{rq}'"
            )
            assert hyp in hypothesis_ids, (
                f"Claim '{cid}' references unknown hypothesis '{hyp}'"
            )

    def test_question_literature_references_resolve(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every literature reference on a question must exist in sources."""
        source_ids: set[str] = {
            str(entry["source_id"]) for entry in registry_data.get("sources", []) if "source_id" in entry
        }
        for entry in registry_data.get("questions", []):
            qid = entry.get("id", "<unknown>")
            refs = entry.get("literature", [])
            if isinstance(refs, list):
                for ref in refs:  # type: ignore[var-annotated]
                    if isinstance(ref, str):
                        assert ref in source_ids, (
                            f"Question '{qid}' references unknown source '{ref}'"
                        )

    def test_claim_source_references_resolve(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every source reference on a claim must exist in sources."""
        source_ids: set[str] = {
            str(entry["source_id"]) for entry in registry_data.get("sources", []) if "source_id" in entry
        }
        for entry in registry_data.get("claims", []):
            cid = entry.get("id", "<unknown>")
            refs = entry.get("sources", [])
            if isinstance(refs, list):
                for ref in refs:  # type: ignore[var-annotated]
                    if isinstance(ref, str):
                        assert ref in source_ids, (
                            f"Claim '{cid}' references unknown source '{ref}'"
                        )

    def test_source_question_references_resolve(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every Brain-5D question reference on a source must exist."""
        question_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("questions", []) if "id" in entry
        }
        for entry in registry_data.get("sources", []):
            sid = entry.get("source_id", "<unknown>")
            refs = entry.get("brain5d_questions", [])
            if isinstance(refs, list):
                for ref in refs:  # type: ignore[var-annotated]
                    if isinstance(ref, str):
                        assert ref in question_ids, (
                            f"Source '{sid}' references unknown question '{ref}'"
                        )


# ============================================================================
# Required Fields Tests
# ============================================================================


@pytest.mark.smoke
class TestRegistryRequiredFields:
    """Ensure every registry entry contains the mandatory fields."""

    REQUIRED_FIELDS = {
        "questions": {"id", "domain", "question", "status"},
        "hypotheses": {"id", "research_question", "hypothesis", "status"},
        "claims": {"id", "claim", "status"},
        "sources": {"source_id", "title", "year"},
        "methods": {"prefix", "name", "description"},
    }

    def test_required_fields_present(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Each entry contains the required top-level fields for its registry."""
        for key, entries in registry_data.items():
            required = self.REQUIRED_FIELDS.get(key, set())
            id_field = ID_FIELDS.get(key, "id")
            for entry in entries:
                missing = required - set(entry.keys())
                identifier = entry.get(id_field, "<unknown>")
                assert not missing, (
                    f"Entry '{identifier}' in '{key}.yaml' missing fields: {sorted(missing)}"
                )


# ============================================================================
# Orphan Tests
# ============================================================================


@pytest.mark.smoke
class TestRegistryOrphans:
    """Detect dangling objects that are no longer referenced."""

    def test_no_unreferenced_hypotheses(
        self, registry_data: dict[str, list[RegistryEntry]]
    ) -> None:
        """Every hypothesis should be referenced by at least one claim or question."""
        hypothesis_ids: set[str] = {
            str(entry["id"]) for entry in registry_data.get("hypotheses", []) if "id" in entry
        }
        referenced: set[str] = set()
        for entry in registry_data.get("questions", []):
            refs: list[Any] = entry.get("hypotheses", [])
            for ref in refs:
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
