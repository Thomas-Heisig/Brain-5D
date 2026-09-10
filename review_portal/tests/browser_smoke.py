"""Real Chromium checks for desktop/mobile, private submission and export-only mode."""
from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen

from cryptography.fernet import Fernet
from playwright.sync_api import expect, sync_playwright

BASE = "http://127.0.0.1:8766"


def main() -> None:
    output = Path(os.environ.get("REVIEW_SCREENSHOTS", "review-portal-screenshots"))
    output.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="mhrn-review-browser-") as tmp:
        private = Path(tmp)
        admin = secrets.token_urlsafe(48)
        study = {
            "enabled": True, "study_id": "synthetic-browser-test", "wave": "baseline", "title": "MHRN - externes Review (synthetischer Test)",
            "controller": "Testverwaltung, keine echte Erhebung", "contact": "review@example.org", "purpose": "Automatisierter Oberflaechentest",
            "retention_days": 1, "compensation": "Keine Verguetung, keine echte Teilnahme.", "privacy_notice": "Ausschliesslich synthetische Testdaten.",
            "reviewed_revision": "a" * 40, "materials_url": "https://example.org/review-materials/" + "a" * 40, "public_origin": BASE,
        }
        (private / "study.json").write_text(json.dumps(study), encoding="utf-8")
        env = {**os.environ, "MHRN_REVIEW_STUDY": str(private / "study.json"), "MHRN_REVIEW_DATA_DIR": str(private / "data"), "MHRN_REVIEW_KEY": Fernet.generate_key().decode(), "MHRN_REVIEW_ADMIN_TOKEN": admin}
        process = subprocess.Popen([sys.executable, "-m", "review_portal"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            for _ in range(100):
                try:
                    with urlopen(BASE + "/health", timeout=1):
                        break
                except OSError:
                    if process.poll() is not None:
                        raise RuntimeError("Review server did not start")
                    time.sleep(0.1)
            else:
                raise RuntimeError("Review server startup timeout")

            def api(path: str, method: str = "GET") -> dict:
                request = Request(BASE + "/api/review/admin/" + path, method=method, headers={"Authorization": "Bearer " + admin})
                with urlopen(request, timeout=10) as result:
                    return json.load(result)

            code = api("invitations", "POST")["invitation_code"]
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
                page = context.new_page()
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("dialog", lambda dialog: dialog.accept())
                page.goto(BASE + "/review/index.html", wait_until="networkidle")
                page.screenshot(path=str(output / "desktop-intro.png"), full_page=True)
                page.locator("#start").click()
                expect(page.locator("#intro-error")).not_to_be_empty()
                page.locator("#adult").check(); page.locator("#consent").check(); page.locator("#start").click()
                assert page.locator("input[type=radio]:checked").count() == 0
                page.locator('.question:has(.qid:text-is("A4")) textarea').first.fill("SYNTHETIC UI TEST")
                assert page.evaluate("localStorage.length") == 0
                page.get_by_role("button", name=re.compile(r"^B -")).click()
                page.locator('input[name="B1"][value="4"]').check()
                page.screenshot(path=str(output / "desktop-questionnaire.png"))
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.screenshot(path=str(output / "mobile-questionnaire.png"))
                page.get_by_role("button", name="END - Abschluss").click()
                page.locator("#invitation").fill(code)
                with page.expect_download() as event:
                    page.locator("#submit").click()
                event.value.save_as(str(private / "synthetic-receipt.json"))
                expect(page.locator("#receipt")).to_contain_text("Serverabgabe bestaetigt", timeout=15000)
                expect(page.locator("#submit")).to_be_disabled()
                assert len(api("export")["records"]) == 1
                page.get_by_text("Bereits abgegebene Antworten", exact=False).click()
                page.locator("#withdraw").click()
                expect(page.locator("#withdraw-status")).to_contain_text("Anfrage verarbeitet")
                assert api("export")["records"] == []
                admin_page = context.new_page(); admin_page.goto(BASE + "/admin.html")
                admin_page.locator("#admin-token").fill(admin)
                admin_page.locator("#summary").click()
                expect(admin_page.locator("#admin-output")).to_contain_text('"n": 0')
                admin_page.locator("#logout").click()
                expect(admin_page.locator("#admin-token")).to_have_value("")

                local = browser.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
                local.route("**/api/review/config", lambda route: route.fulfill(status=404, body="No collector"))
                local_page = local.new_page(); local_page.on("pageerror", lambda error: errors.append(str(error)))
                local_page.on("dialog", lambda dialog: dialog.accept())
                local_page.goto(BASE + "/review/index.html", wait_until="networkidle")
                expect(local_page.locator("#mode")).to_contain_text("kein Versand")
                local_page.locator("#adult").check(); local_page.locator("#consent").check(); local_page.locator("#start").click()
                local_page.locator("#persist").check()
                local_page.locator('.question:has(.qid:text-is("A4")) textarea').first.fill("LOCAL SYNTHETIC TEST")
                local_page.reload(); local_page.locator("#adult").check(); local_page.locator("#consent").check(); local_page.locator("#start").click()
                local_page.locator("#restore").click()
                expect(local_page.locator('.question:has(.qid:text-is("A4")) textarea').first).to_have_value("LOCAL SYNTHETIC TEST")
                local_page.get_by_role("button", name="END - Abschluss").click()
                expect(local_page.locator("#online")).to_be_hidden()
                with local_page.expect_download() as event:
                    local_page.locator("#export-json").click()
                event.value.save_as(str(private / "local.json"))
                data = json.loads((private / "local.json").read_text(encoding="utf-8"))
                assert data["answers"]["A4"] == "LOCAL SYNTHETIC TEST"
                assert data["study_id"] == "local-review"
                assert "withdrawal_token" not in data
                data["instrument_version"] = "invalid"
                (private / "invalid.json").write_text(json.dumps(data), encoding="utf-8")
                local_page.locator("#import").set_input_files(str(private / "invalid.json"))
                expect(local_page.locator("#status")).to_contain_text("Instrumentversion")
                assert errors == [], errors
                browser.close()
                print("PASS: consent, desktop/mobile, submission, withdrawal, admin, offline export, opt-in draft recovery, invalid import, no page errors")
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)


if __name__ == "__main__":
    main()
