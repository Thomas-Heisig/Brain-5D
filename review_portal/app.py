"""Standalone review API without runtime, file-manager or evidence-write routes.

Run behind a TLS reverse proxy. With no study configuration this serves only
local/export mode; online collection requires complete settings and secrets.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import secrets
import time
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .analysis import summarize
from .catalogue import DIGEST, INSTRUMENT
from .store import Store
from .validation import parse_json, validate_response

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src/dashboard/static/review"
MAX_BYTES = 2 * 1024 * 1024
STUDY_FIELDS = {"enabled", "study_id", "wave", "title", "controller", "contact", "purpose", "retention_days", "compensation", "privacy_notice", "reviewed_revision", "materials_url", "public_origin"}


def _secret(name: str) -> str:
    direct, file = os.environ.get(name), os.environ.get(name + "_FILE")
    if bool(direct) == bool(file):
        raise ValueError(f"Genau {name} oder {name}_FILE muss gesetzt sein.")
    return direct.strip() if direct else Path(str(file)).read_text(encoding="utf-8").strip()


@dataclass(frozen=True)
class Settings:
    study: dict[str, Any]
    data_dir: Path
    encryption_key: bytes
    admin_token: str

    def __post_init__(self) -> None:
        s = self.study
        if not isinstance(s, dict) or set(s) != STUDY_FIELDS or s["enabled"] is not True:
            raise ValueError("Erhebung ist unvollstaendig oder nicht explizit aktiviert.")
        for key in STUDY_FIELDS - {"enabled", "retention_days"}:
            value = s[key]
            if not isinstance(value, str) or not value.strip() or len(value) > 6000 or "EINTRAGEN" in value.upper() or "TODO" in value.upper():
                raise ValueError(f"Erhebungsangabe fehlt oder ist ungueltig: {key}.")
        if type(s["retention_days"]) is not int or not 1 <= s["retention_days"] <= 3650:
            raise ValueError("Aufbewahrungsfrist muss 1 bis 3650 Tage betragen.")
        for key in ("study_id", "wave"):
            if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", s[key]):
                raise ValueError(f"Ungueltige Kennung: {key}.")
        if not re.fullmatch(r"[0-9a-f]{40}", s["reviewed_revision"]):
            raise ValueError("Pruefunterlagen muessen an einen vollen Commit gebunden sein.")
        materials = urlsplit(s["materials_url"])
        if materials.scheme != "https" or not materials.netloc or materials.username or materials.password or len(s["materials_url"]) > 600:
            raise ValueError("Pruefunterlagen benoetigen eine gueltige HTTPS-URL.")
        origin = urlsplit(s["public_origin"])
        local = origin.scheme == "http" and origin.hostname in ("127.0.0.1", "localhost", "::1")
        if (origin.scheme != "https" and not local) or not origin.netloc or origin.path or origin.query or origin.fragment or origin.username or origin.password:
            raise ValueError("public_origin muss eine HTTPS-Origin ohne Pfad sein (lokal HTTP erlaubt).")
        if not re.fullmatch(r"[A-Za-z0-9_-]{32,200}", self.admin_token):
            raise ValueError("Administrationsschluessel muss mindestens 32 zufaellige Zeichen haben.")
        if self.data_dir.resolve().is_relative_to(ROOT):
            raise ValueError("Antwortdaten muessen AUSSERHALB des Repositorys gespeichert werden.")

    def public_config(self) -> dict[str, Any]:
        canonical = json.dumps(self.study, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return {**self.study, "study_config_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(), "protocol": "mhrn-review-v1", "collection_enabled": True, "instrument_sha256": DIGEST, "instrument_version": INSTRUMENT["version"]}

    @classmethod
    def from_env(cls) -> Settings | None:
        config = os.environ.get("MHRN_REVIEW_STUDY")
        if not config:
            return None
        study = parse_json(Path(config).read_bytes())
        default_dir = Path.home() / ".local/share/mhrn-review"
        return cls(study, Path(os.environ.get("MHRN_REVIEW_DATA_DIR", str(default_dir))), _secret("MHRN_REVIEW_KEY").encode("ascii"), _secret("MHRN_REVIEW_ADMIN_TOKEN"))


class Guard:
    """Bound request bodies, reject cross-origin writes and add security headers."""
    def __init__(self, app: ASGIApp, origin: str | None) -> None:
        self.app, self.origin = app, origin
        self.salt = secrets.token_bytes(32)
        self.buckets: dict[bytes, tuple[int, int]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {key.lower(): value for key, value in scope["headers"]}
        response_headers = {
            "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
            "X-Frame-Options": "DENY", "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        }

        async def fail(code: int, detail: str) -> None:
            await JSONResponse({"detail": detail}, status_code=code, headers=response_headers)(scope, receive, send)

        if self.origin and b"origin" in headers and headers[b"origin"].decode("latin1") != self.origin:
            await fail(403, "Fremde Origin ist nicht erlaubt.")
            return
        if scope["path"].startswith("/api/review/"):
            now = int(time.monotonic()) // 60
            self.buckets = {key: value for key, value in self.buckets.items() if value[0] == now}
            peer = str((scope.get("client") or ("unknown",))[0]).encode("utf-8")
            key = hashlib.sha256(self.salt + peer).digest()
            _, count = self.buckets.get(key, (now, 0))
            if count >= 120 or (key not in self.buckets and len(self.buckets) >= 4096):
                await fail(429, "Zu viele Anfragen. Spaeter erneut versuchen.")
                return
            self.buckets[key] = (now, count + 1)
        try:
            length = int(headers.get(b"content-length", b"0"))
            if length < 0 or length > MAX_BYTES:
                await fail(413, "Maximale Anfragegroesse: 2 MiB.")
                return
        except ValueError:
            await fail(400, "Ungueltige Content-Length.")
            return
        if headers.get(b"content-encoding", b"identity") != b"identity":
            await fail(415, "Komprimierte Anfragen sind nicht erlaubt.")
            return
        chunks: list[bytes] = []
        size = 0
        try:
            async with asyncio.timeout(15):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    chunk = message.get("body", b"")
                    size += len(chunk)
                    if size > MAX_BYTES:
                        await fail(413, "Maximale Anfragegroesse: 2 MiB.")
                        return
                    chunks.append(chunk)
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            await fail(408, "Zeitlimit beim Lesen der Anfrage.")
            return
        raw = b"".join(chunks)
        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": raw, "more_body": False}
            return await receive()

        async def secure_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                existing = list(message.get("headers", []))
                existing.extend((key.lower().encode("ascii"), value.encode("ascii")) for key, value in response_headers.items())
                message["headers"] = existing
            await send(message)

        await self.app(scope, replay, secure_send)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    config = settings.public_config() if settings else {"protocol": "mhrn-review-v1", "collection_enabled": False, "instrument_sha256": DIGEST}
    store = Store(settings.data_dir, settings.encryption_key, config["study_config_sha256"], settings.study["retention_days"]) if settings else None

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async def cleanup() -> None:
            while True:
                if store:
                    await asyncio.to_thread(store.purge)
                await asyncio.sleep(60)
        task = asyncio.create_task(cleanup())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.add_middleware(Guard, origin=settings.study["public_origin"] if settings else None)

    def active() -> Store:
        if not store:
            raise HTTPException(503, "Online-Erhebung ist nicht eingerichtet.")
        return store

    def admin(request: Request) -> Store:
        service = active()
        authorization = request.headers.get("authorization", "")
        supplied = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
        expected = settings.admin_token if settings else ""
        if not supplied or not secrets.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8")):
            raise HTTPException(401, "Administrationsschluessel fehlt oder ist ungueltig.")
        return service

    async def body(request: Request) -> dict[str, Any]:
        if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
            raise HTTPException(415, "application/json erforderlich.")
        try:
            value = parse_json(await request.body())
            if not isinstance(value, dict):
                raise ValueError("JSON-Objekt erforderlich.")
            return value
        except (ValueError, UnicodeDecodeError, RecursionError) as exc:
            raise HTTPException(400, "Ungueltiges JSON.") from exc

    @app.get("/api/review/config")
    def public_config() -> dict[str, Any]:
        return config

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "isolated-review-portal"}

    @app.post("/api/review/responses")
    async def submit(request: Request) -> JSONResponse:
        service = active()
        data = await body(request)
        token = data.get("withdrawal_token")
        if set(data) != {"response", "withdrawal_token"} or not isinstance(token, str) or not re.fullmatch(r"[0-9a-f]{64}", token):
            raise HTTPException(422, "Ungueltiger Abgabeumschlag oder Ruecktrittscode.")
        try:
            response = validate_response(data["response"], config)
            invitation = request.headers.get("x-review-invitation", "")
            if not re.fullmatch(r"[A-Za-z0-9_-]{32,100}", invitation):
                raise PermissionError("Einladung fehlt oder ist ungueltig.")
            created = await asyncio.to_thread(service.submit, invitation, response, token)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        except PermissionError as exc:
            raise HTTPException(403, str(exc)) from exc
        except FileExistsError as exc:
            raise HTTPException(409, str(exc)) from exc
        return JSONResponse({"response_id": response["response_id"], "stored": True, "classification": "HUMAN_REVIEW_DATA_NOT_EVIDENCE"}, status_code=201 if created else 200)

    @app.post("/api/review/withdraw")
    async def withdraw(request: Request) -> dict[str, bool]:
        service = active()
        data = await body(request)
        response_id, token = data.get("response_id"), data.get("withdrawal_token")
        if set(data) != {"response_id", "withdrawal_token"} or not isinstance(response_id, str) or len(response_id) != 36 or not isinstance(token, str) or not re.fullmatch(r"[0-9a-f]{64}", token):
            raise HTTPException(422, "Abgabe-ID und Ruecktrittscode erforderlich.")
        await asyncio.to_thread(service.withdraw, response_id, token)
        return {"processed": True}

    @app.post("/api/review/admin/invitations")
    def invitation(request: Request) -> dict[str, Any]:
        try:
            return admin(request).invite()
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/review/admin/export")
    def export(request: Request) -> dict[str, Any]:
        return {"classification": "PRIVATE_NOT_FOR_PUBLICATION", "instrument": INSTRUMENT, "study": config, "records": admin(request).export()}

    @app.get("/api/review/admin/summary")
    def summary(request: Request) -> dict[str, Any]:
        return summarize(admin(request).export())

    @app.post("/api/review/admin/purge")
    def purge(request: Request) -> dict[str, int]:
        return {"expired_responses_deleted": admin(request).purge()}

    app.mount("/review", StaticFiles(directory=STATIC, html=True), name="review-alias")
    app.mount("/", StaticFiles(directory=STATIC, html=True), name="review")
    return app
