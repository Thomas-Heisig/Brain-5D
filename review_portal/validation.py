"""Strict server-side validation independent of the browser UI."""
from __future__ import annotations

import datetime as dt
import json
import uuid
from typing import Any

from .catalogue import CONSENT_VERSION, DIGEST, INSTRUMENT, ITEMS, MODULE_IDS, NA, SKIP, VERSION

FIELDS = {
    "instrument_id", "instrument_version", "instrument_sha256", "study_id", "wave",
    "reviewed_revision", "materials_url", "study_config_sha256", "response_id",
    "participant_code", "participant_type", "modules", "answers", "notes", "consent",
    "started_at", "completed_at",
}


def _timestamp(value: Any) -> bool:
    if not isinstance(value, str) or len(value) > 40:
        return False
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def _answer(q: dict[str, Any], value: Any) -> bool:
    if value is None or value == "" or value in (NA, SKIP):
        return True
    if q["kind"] == "scale":
        return type(value) is int and 1 <= value <= 5
    if q["kind"] == "number":
        return type(value) is int and q["minimum"] <= value <= q["maximum"]
    if q["kind"] == "choice":
        return isinstance(value, str) and value in q["choices"]
    if q["kind"] == "text":
        return isinstance(value, str) and len(value) <= 4000
    if q["kind"] == "signature":
        if not isinstance(value, dict) or set(value) != {"date", "signature"}:
            return False
        if not isinstance(value["signature"], str) or len(value["signature"]) > 160:
            return False
        date = value["date"]
        if date == "":
            return True
        if not isinstance(date, str):
            return False
        try:
            return dt.date.fromisoformat(date).isoformat() == date
        except ValueError:
            return False
    return False


def validate_response(value: Any, study: dict[str, Any]) -> dict[str, Any]:
    """Reject stale context, unknown fields, covert hidden answers and invalid values."""
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("Unbekannte oder fehlende Antwortfelder.")
    r: dict[str, Any] = value
    if (r["instrument_id"], r["instrument_version"], r["instrument_sha256"]) != (INSTRUMENT["id"], VERSION, DIGEST):
        raise ValueError("Instrumentversion oder Pruefsumme stimmt nicht ueberein.")
    for field in ("study_id", "wave", "reviewed_revision", "materials_url", "study_config_sha256"):
        if r[field] != study[field]:
            raise ValueError("Erhebung, Einwilligungsinformation oder Pruefunterlagen wurden geaendert.")
    try:
        if not isinstance(r["response_id"], str) or str(uuid.UUID(r["response_id"])) != r["response_id"]:
            raise ValueError("Nicht kanonische UUID.")
    except (ValueError, AttributeError) as exc:
        raise ValueError("Ungueltige Abgabe-ID.") from exc
    if not isinstance(r["participant_code"], str) or len(r["participant_code"]) > 80:
        raise ValueError("Pseudonym ist ungueltig.")
    if r["participant_type"] not in ("proband", "reviewer", "committee"):
        raise ValueError("Teilnahmetyp ist ungueltig.")
    modules = r["modules"]
    if not isinstance(modules, list) or any(not isinstance(m, str) or m not in MODULE_IDS for m in modules):
        raise ValueError("Unbekannte Module.")
    if len(set(modules)) != len(modules):
        raise ValueError("Doppelte Module.")
    allowed = {q["id"] for s in INSTRUMENT["sections"] + INSTRUMENT["specialists"] if s["id"] in modules or s["id"] in "ABCDEFGH" for q in s["items"]}
    for field in ("answers", "notes"):
        if not isinstance(r[field], dict) or not set(r[field]).issubset(allowed):
            raise ValueError("Unbekannte oder nicht ausgewaehlte Fragen.")
    for code, answer in r["answers"].items():
        if not _answer(ITEMS[code], answer):
            raise ValueError(f"Ungueltige Antwort: {code}.")
    if any(not isinstance(note, str) or len(note) > 2000 for note in r["notes"].values()):
        raise ValueError("Kommentar ist ungueltig oder zu lang.")
    consent = r["consent"]
    if not isinstance(consent, dict) or set(consent) != {"accepted", "adult", "version", "accepted_at"}:
        raise ValueError("Einwilligung fehlt.")
    if consent["accepted"] is not True or consent["adult"] is not True or consent["version"] != CONSENT_VERSION or not _timestamp(consent["accepted_at"]):
        raise ValueError("Einwilligung ist ungueltig.")
    if not _timestamp(r["started_at"]) or not _timestamp(r["completed_at"]):
        raise ValueError("Abschlusszeit oder Startzeit fehlt.")
    return r


def parse_json(raw: bytes) -> Any:
    """Reject duplicate keys and non-finite numbers rather than guessing intent."""
    def pairs(entries: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in entries:
            if key in result:
                raise ValueError("Doppeltes JSON-Feld.")
            result[key] = value
        return result

    def constant(_: str) -> None:
        raise ValueError("Nicht endliche Zahl.")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
