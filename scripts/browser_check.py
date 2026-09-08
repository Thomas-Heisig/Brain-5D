"""Run a Chromium smoke check against the MHRN dashboard."""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _wait_for_server(
    url: str, process: subprocess.Popen[bytes], timeout: float
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"Dashboard exited before becoming ready (exit {process.returncode})."
            )
        try:
            with urlopen(url, timeout=1):
                return
        except (OSError, URLError):
            time.sleep(0.1)
    raise TimeoutError(f"Dashboard did not become ready within {timeout:.1f}s: {url}")


def _start_dashboard(host: str, port: int) -> subprocess.Popen[bytes]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "src.dashboard",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def _stop_dashboard(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _run_check(
    url: str, timeout_ms: int, screenshot: Path | None, headed: bool
) -> None:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Browser tooling is missing. Install with "
            'python -m pip install -e ".[browser]" and '
            "python -m playwright install chromium."
        ) from error

    page_errors: list[str] = []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                headless=not headed,
                executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE"),
            )
        except PlaywrightError as error:
            raise RuntimeError(
                "Chromium is not installed. Run: "
                "python -m playwright install chromium"
            ) from error
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                page.locator("#tab-overview").wait_for(
                    state="visible", timeout=timeout_ms
                )
                page.locator('[data-primary-area="science"]').wait_for(
                    state="visible", timeout=timeout_ms
                )
                page.locator('[data-primary-area="science"]').click(timeout=timeout_ms)
                page.locator("#tab-research").wait_for(
                    state="visible", timeout=timeout_ms
                )
                page.locator("#workflow-batch-open").click(timeout=timeout_ms)
                page.locator("#workflow-batch-dialog").wait_for(
                    state="visible", timeout=timeout_ms
                )
                page.get_by_role("button", name="Abbrechen", exact=True).click(
                    timeout=timeout_ms
                )
                if screenshot is not None:
                    screenshot.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot), full_page=True)
                if page_errors:
                    raise RuntimeError(
                        "Dashboard page errors: " + "; ".join(page_errors)
                    )
            except PlaywrightError as error:
                raise RuntimeError(f"Browser interaction failed: {error}") from error
        finally:
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Use an already-running dashboard URL.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--timeout-ms", type=int, default=15_000)
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()

    process: subprocess.Popen[bytes] | None = None
    try:
        if args.url:
            url = args.url.rstrip("/") + "/"
        else:
            port = args.port or _free_port()
            process = _start_dashboard(args.host, port)
            url = f"http://{args.host}:{port}/"
            _wait_for_server(url, process, timeout=15)
        _run_check(url, args.timeout_ms, args.screenshot, args.headed)
        print(f"Chromium browser check passed: {url}")
        return 0
    except (RuntimeError, TimeoutError, OSError) as error:
        print(f"Chromium browser check failed: {error}", file=sys.stderr)
        return 1
    finally:
        if process is not None:
            _stop_dashboard(process)


if __name__ == "__main__":
    raise SystemExit(main())
