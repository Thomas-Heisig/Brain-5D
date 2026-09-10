"""Encrypted, transactional storage outside the repository and experiment tree."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from cryptography.fernet import Fernet, InvalidToken


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Store:
    def __init__(self, directory: Path, key: bytes, context: str, retention_days: int) -> None:
        self.cipher = Fernet(key)
        self.retention_days = retention_days
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name != "nt":
            directory.chmod(0o700)
        self.path = directory / "reviews.sqlite3"
        with self.connection() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS meta (name TEXT PRIMARY KEY, value BLOB NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS invitations (token_hash TEXT PRIMARY KEY, expires INTEGER NOT NULL, used_by TEXT, payload_hash TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS responses (id TEXT PRIMARY KEY, ciphertext BLOB NOT NULL, withdrawal_hash TEXT NOT NULL, created INTEGER NOT NULL, expires INTEGER NOT NULL)")
            row = db.execute("SELECT value FROM meta WHERE name='key_check'").fetchone()
            if row:
                try:
                    if self.cipher.decrypt(row[0]) != b"mhrn-review-key-check-v1":
                        raise ValueError("Falscher Schluessel.")
                except InvalidToken as exc:
                    raise ValueError("Der Schluessel passt nicht zur bestehenden Datenbank.") from exc
            else:
                db.execute("INSERT INTO meta VALUES ('key_check', ?)", (self.cipher.encrypt(b"mhrn-review-key-check-v1"),))
            row = db.execute("SELECT value FROM meta WHERE name='context'").fetchone()
            if row and row[0] != context:
                raise ValueError("Geaenderter Erhebungskontext: separate Datenbank erforderlich.")
            if not row:
                db.execute("INSERT INTO meta VALUES ('context', ?)", (context,))
        if os.name != "nt":
            self.path.chmod(0o600)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=10)
        db.execute("PRAGMA secure_delete=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _purge(db: sqlite3.Connection, now: int) -> int:
        count = db.execute("DELETE FROM responses WHERE expires <= ?", (now,)).rowcount
        db.execute("DELETE FROM invitations WHERE expires <= ?", (now,))
        return count

    def purge(self) -> int:
        with self.connection() as db:
            return self._purge(db, int(time.time()))

    def invite(self) -> dict[str, Any]:
        token = secrets.token_urlsafe(32)
        now = int(time.time())
        expires = now + 14 * 86400
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            self._purge(db, now)
            if db.execute("SELECT COUNT(*) FROM invitations").fetchone()[0] >= 10000:
                raise ValueError("Maximal 10000 aktive Einladungen.")
            db.execute("INSERT INTO invitations VALUES (?, ?, NULL, NULL)", (digest(token), expires))
        return {"invitation_code": token, "expires_unix": expires, "uses": 1}

    def submit(self, invitation: str, response: dict[str, Any], withdrawal_token: str) -> bool:
        """Consume an invitation and write immutable ciphertext atomically.

        Exact retry returns False; a new submission returns True. An invitation
        can never overwrite an earlier response or reopen after withdrawal.
        """
        now = int(time.time())
        raw = json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        payload_hash = digest(raw)
        invitation_hash = digest(invitation)
        withdrawal_hash = digest(withdrawal_token)
        response_id = response["response_id"]
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            self._purge(db, now)
            invite = db.execute("SELECT used_by, payload_hash FROM invitations WHERE token_hash=? AND expires>?", (invitation_hash, now)).fetchone()
            if not invite:
                raise PermissionError("Einladung ungueltig oder abgelaufen.")
            existing = db.execute("SELECT withdrawal_hash FROM responses WHERE id=?", (response_id,)).fetchone()
            if invite[0] is not None:
                if invite[0] == response_id and invite[1] == payload_hash and existing and secrets.compare_digest(existing[0], withdrawal_hash):
                    return False
                raise FileExistsError("Einladung wurde bereits verwendet. Keine Ueberschreibung.")
            if existing:
                raise FileExistsError("Abgabe-ID wurde bereits verwendet.")
            stored = {"response": response, "server_received_unix": now, "expires_unix": now + self.retention_days * 86400, "classification": "HUMAN_REVIEW_DATA_NOT_EVIDENCE"}
            ciphertext = self.cipher.encrypt(json.dumps(stored, ensure_ascii=False).encode("utf-8"))
            db.execute("INSERT INTO responses VALUES (?, ?, ?, ?, ?)", (response_id, ciphertext, withdrawal_hash, now, stored["expires_unix"]))
            db.execute("UPDATE invitations SET used_by=?, payload_hash=? WHERE token_hash=?", (response_id, payload_hash, invitation_hash))
        return True

    def withdraw(self, response_id: str, token: str) -> None:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            self._purge(db, int(time.time()))
            row = db.execute("SELECT withdrawal_hash FROM responses WHERE id=?", (response_id,)).fetchone()
            expected = row[0] if row else "0" * 64
            if secrets.compare_digest(expected, digest(token)) and row:
                db.execute("DELETE FROM responses WHERE id=?", (response_id,))

    def export(self) -> list[dict[str, Any]]:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            self._purge(db, int(time.time()))
            rows = db.execute("SELECT ciphertext FROM responses ORDER BY created, id").fetchall()
        return [json.loads(self.cipher.decrypt(row[0])) for row in rows]
