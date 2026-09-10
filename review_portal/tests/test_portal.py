from __future__ import annotations

import copy
import datetime as dt
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from review_portal.analysis import summarize
from review_portal.app import MAX_BYTES, ROOT, Settings, create_app
from review_portal.catalogue import DIGEST, INSTRUMENT, ITEMS, SECTIONS, SPECIALISTS, javascript
from review_portal.store import Store


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    study = {
        "enabled": True, "study_id": "pilot-01", "wave": "baseline", "title": "Review pilot",
        "controller": "Test study office", "contact": "research@example.org", "purpose": "Independent project screening",
        "retention_days": 30, "compensation": "None", "privacy_notice": "Private responses; withdraw by code.",
        "reviewed_revision": "a" * 40, "materials_url": "https://example.org/materials/" + "a" * 40,
        "public_origin": "http://localhost",
    }
    return Settings(study, tmp_path / "private", Fernet.generate_key(), "admin_" + "a" * 60)


@pytest.fixture
def client(settings: Settings):
    with TestClient(create_app(settings), base_url="http://localhost") as value:
        yield value


def auth(settings: Settings) -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.admin_token}"}


def response(settings: Settings) -> dict:
    cfg = settings.public_config()
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    return {
        "instrument_id": INSTRUMENT["id"], "instrument_version": INSTRUMENT["version"], "instrument_sha256": DIGEST,
        **{key: cfg[key] for key in ("study_id", "wave", "reviewed_revision", "materials_url", "study_config_sha256")},
        "response_id": str(uuid.uuid4()), "participant_code": "participant-01", "participant_type": "reviewer", "modules": ["Q"],
        "answers": {"A4": "SECRET-RESPONDENT-DO-NOT-PUBLISH", "B1": 3, "C1": "Nicht beurteilbar", "H1": 4},
        "notes": {}, "consent": {"accepted": True, "adult": True, "version": "1.0.0", "accepted_at": now},
        "started_at": now, "completed_at": now,
    }


def invite(client: TestClient, settings: Settings) -> str:
    result = client.post("/api/review/admin/invitations", headers=auth(settings))
    assert result.status_code == 200
    return result.json()["invitation_code"]


def submit(client: TestClient, settings: Settings, answer: dict | None = None, code: str | None = None, token: str = "b" * 64):
    code = code or invite(client, settings)
    answer = answer or response(settings)
    return client.post("/api/review/responses", headers={"X-Review-Invitation": code, "Origin": "http://localhost"}, json={"response": answer, "withdrawal_token": token})


def records(client: TestClient, settings: Settings) -> list:
    return client.get("/api/review/admin/export", headers=auth(settings)).json()["records"]


def test_catalogue_complete_and_generated_bytes_match():
    assert len(ITEMS) == 135
    assert sum(len(s["items"]) for s in SECTIONS) == 75
    assert sum(len(s["items"]) for s in SPECIALISTS) == 60
    assert set(ITEMS) >= {"A1", "A10", "H5", "IT10", "BIO10", "OPS10", "BACK10", "ETH10", "Q10"}
    assert (ROOT / "src/dashboard/static/review/instrument.js").read_text(encoding="utf-8") == javascript()


@pytest.mark.parametrize("path", ["/", "/index.html", "/review/index.html", "/admin.html", "/instrument.js", "/app.js", "/review.css"])
def test_public_static_and_security_headers(client: TestClient, path: str):
    res = client.get(path)
    assert res.status_code == 200
    assert res.headers["x-frame-options"] == "DENY"
    assert "no-store" in res.headers["cache-control"]
    assert "frame-ancestors 'none'" in res.headers["content-security-policy"]


@pytest.mark.parametrize("path", ["/api/control", "/api/files", "/docs", "/openapi.json", "/reviews.sqlite3", "/review_portal/app.py", "/review/%2e%2e/%2e%2e/review_portal/app.py"])
def test_no_runtime_or_private_files(client: TestClient, path: str):
    assert client.get(path).status_code == 404


def test_preview_does_not_collect(monkeypatch):
    monkeypatch.delenv("MHRN_REVIEW_STUDY", raising=False)
    with TestClient(create_app()) as client:
        assert client.get("/").status_code == 200
        assert client.get("/api/review/config").json()["collection_enabled"] is False
        assert client.post("/api/review/responses", json={}).status_code == 503


def test_admin_export_is_private(client: TestClient, settings: Settings):
    assert client.get("/api/review/admin/export").status_code == 401
    assert client.post("/api/review/admin/invitations").status_code == 401
    cfg = client.get("/api/review/config").text
    assert settings.admin_token not in cfg
    assert settings.encryption_key.decode() not in cfg
    assert str(settings.data_dir) not in cfg


def test_encrypted_at_rest_and_secrets_not_exported(client: TestClient, settings: Settings):
    code = invite(client, settings)
    res = submit(client, settings, code=code)
    assert res.status_code == 201
    assert len(records(client, settings)) == 1
    text = json.dumps(records(client, settings))
    assert "SECRET-RESPONDENT" in text
    assert code not in text and "b" * 64 not in text
    for file in settings.data_dir.glob("reviews.sqlite3*"):
        data = file.read_bytes()
        assert b"SECRET-RESPONDENT" not in data
        assert code.encode() not in data
        assert ("b" * 64).encode() not in data


def test_retry_idempotent_and_no_overwrite(client: TestClient, settings: Settings):
    code = invite(client, settings)
    answer = response(settings)
    assert submit(client, settings, answer, code).status_code == 201
    assert submit(client, settings, answer, code).status_code == 200
    edited = copy.deepcopy(answer); edited["answers"]["B1"] = 5
    assert submit(client, settings, edited, code).status_code == 409
    assert submit(client, settings, response(settings), code).status_code == 409
    assert submit(client, settings, answer, invite(client, settings)).status_code == 409
    assert len(records(client, settings)) == 1


def test_withdrawal_is_private_idempotent_and_not_new_vote(client: TestClient, settings: Settings):
    code, answer = invite(client, settings), response(settings)
    assert submit(client, settings, answer, code).status_code == 201
    endpoint = "/api/review/withdraw"
    wrong = {"response_id": answer["response_id"], "withdrawal_token": "c" * 64}
    assert client.post(endpoint, json=wrong).json() == {"processed": True}
    assert len(records(client, settings)) == 1
    good = {**wrong, "withdrawal_token": "b" * 64}
    assert client.post(endpoint, json=good).json() == {"processed": True}
    assert client.post(endpoint, json=good).json() == {"processed": True}
    assert records(client, settings) == []
    assert submit(client, settings, answer, code).status_code == 409


def test_attention_failure_is_retained(client: TestClient, settings: Settings):
    assert submit(client, settings).status_code == 201
    assert records(client, settings)[0]["response"]["answers"]["H1"] == 4


def test_empty_optional_answers_are_allowed(client: TestClient, settings: Settings):
    answer = response(settings); answer["answers"] = {}
    assert submit(client, settings, answer).status_code == 201


@pytest.mark.parametrize("field,value", [("B1", 0), ("B1", 6), ("B1", 3.0), ("B1", True), ("A1", 17), ("A5", -1), ("A2", "x"), ("H5", {"date": "2026-02-31", "signature": ""}), ("IT1", "hidden module"), ("UNKNOWN", "text"), ("G1", "x" * 4001)])
def test_invalid_answers_rejected(client: TestClient, settings: Settings, field: str, value):
    answer = response(settings); answer["answers"][field] = value
    assert submit(client, settings, answer).status_code == 422
    assert records(client, settings) == []


@pytest.mark.parametrize("field,value", [("instrument_sha256", "0" * 64), ("study_config_sha256", "0" * 64), ("reviewed_revision", "b" * 40), ("wave", "wrong"), ("completed_at", None), ("modules", ["Q", "Q"]), ("response_id", "not-a-uuid")])
def test_stale_or_invalid_context_rejected(client: TestClient, settings: Settings, field: str, value):
    answer = response(settings); answer[field] = value
    assert submit(client, settings, answer).status_code == 422


def test_consent_is_required(client: TestClient, settings: Settings):
    answer = response(settings); answer["consent"]["accepted"] = False
    assert submit(client, settings, answer).status_code == 422


def test_no_additional_privilege_fields(client: TestClient, settings: Settings):
    answer = response(settings); answer["promote_evidence"] = True
    assert submit(client, settings, answer).status_code == 422


def test_origin_and_body_guards(client: TestClient, settings: Settings):
    assert client.post("/api/review/admin/invitations", headers={**auth(settings), "Origin": "https://evil.example"}).status_code == 403
    assert client.post("/api/review/responses", content=b"x" * (MAX_BYTES + 1)).status_code == 413
    assert client.post("/api/review/responses", content=b"{}", headers={"Content-Encoding":"gzip"}).status_code == 415
    assert client.post("/api/review/responses", content='{"response": 1,"response": 2}', headers={"Content-Type":"application/json"}).status_code == 400
    assert client.post("/api/review/responses", content='{"v":NaN}', headers={"Content-Type":"application/json"}).status_code == 400
    assert client.post("/api/review/responses", content=b"{}", headers={"Content-Type":"text/plain"}).status_code == 415


def test_expiry_and_wrong_key_fail_closed(settings: Settings):
    cfg = settings.public_config()
    store = Store(settings.data_dir, settings.encryption_key, cfg["study_config_sha256"], 30)
    code = store.invite()["invitation_code"]
    store.submit(code, response(settings), "b" * 64)
    with store.connection() as db:
        db.execute("UPDATE responses SET expires=0")
    assert store.purge() == 1
    assert store.export() == []
    with pytest.raises(ValueError):
        Store(settings.data_dir, Fernet.generate_key(), cfg["study_config_sha256"], 30)
    with pytest.raises(ValueError):
        Store(settings.data_dir, settings.encryption_key, "changed-context", 30)


def test_atomic_concurrent_retry(settings: Settings):
    store = Store(settings.data_dir, settings.encryption_key, settings.public_config()["study_config_sha256"], 30)
    code, answer = store.invite()["invitation_code"], response(settings)
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(lambda _: store.submit(code, answer, "b" * 64), range(6)))
    assert sum(results) == 1
    assert len(store.export()) == 1


@pytest.mark.parametrize("key,value", [("enabled", False), ("controller", "EINTRAGEN"), ("retention_days", 0), ("retention_days", True), ("public_origin", "http://example.org"), ("public_origin", "https://example.org/path"), ("reviewed_revision", "main")])
def test_configuration_fails_closed(settings: Settings, key: str, value):
    study = {**settings.study, key: value}
    with pytest.raises(ValueError):
        Settings(study, settings.data_dir, settings.encryption_key, settings.admin_token)


def test_answers_cannot_live_in_repository(settings: Settings):
    with pytest.raises(ValueError):
        Settings(settings.study, ROOT / "private", settings.encryption_key, settings.admin_token)


def test_descriptive_missing_values_and_pilot_alpha():
    rows = [{"response": {"answers": {"B1": v}}} for v in [1, 5, None, "Nicht beurteilbar", "Keine Angabe"]]
    result = summarize(rows)
    item = result["items"]["B1"]
    assert (item["n"], item["missing"], item["not_assessable"], item["declined"], item["mean"]) == (2, 1, 1, 1, 3)
    assert result["reliability"]["B"]["alpha"] is None
    assert result["automatic_exclusions"] == 0


def test_alpha_diagnostic_and_constant_data():
    rows = [{"response": {"answers": {f"B{i}": n % 5 + 1 for i in range(1,11)}}} for n in range(20)]
    assert summarize(rows)["reliability"]["B"]["alpha"] == pytest.approx(1)
    rows = [{"response": {"answers": {f"B{i}": 3 for i in range(1,11)}}} for _ in range(20)]
    assert summarize(rows)["reliability"]["B"]["status"] == "zero_total_variance"
