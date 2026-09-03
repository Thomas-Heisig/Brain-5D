"""Optional local Ollama adapter with no execution or filesystem authority."""

from __future__ import annotations

import json
from typing import Any, cast
from urllib.request import Request, urlopen

from src.language_organ.protocols import LanguageRequest, LanguageResponse


class OllamaBackend:
    """Call Ollama through the read-only language-backend contract."""

    def __init__(
        self, model: str, endpoint: str = "http://127.0.0.1:11434/api/generate"
    ) -> None:
        self.model = model
        self.endpoint = endpoint

    @property
    def name(self) -> str:
        """Return a stable backend identifier for dashboard and provenance."""
        return "ollama"

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        """Process immutable language data and convert failures to responses."""
        try:
            text, _metadata = self._generate(_request_prompt(request))
            return LanguageResponse(
                request_id=request.request_id,
                text=text,
                backend_name=self.name,
                success=True,
            )
        except (OSError, ValueError) as exc:
            return LanguageResponse(
                request_id=request.request_id,
                text="",
                backend_name=self.name,
                success=False,
                error=str(exc),
            )

    def __call__(self, prompt: str) -> tuple[dict[str, Any], dict[str, str | float]]:
        text, metadata = self._generate(prompt)
        output_raw: Any = json.loads(text)
        if not isinstance(output_raw, dict):
            raise ValueError("Ollama output must be a JSON object.")
        output = cast(dict[str, Any], output_raw)
        return output, metadata

    def generate_text(self, prompt: str) -> tuple[str, dict[str, str | float]]:
        """Return plain text for read-only chat consumers."""
        return self._generate(prompt)

    def _generate(self, prompt: str) -> tuple[str, dict[str, str | float]]:
        request = Request(
            self.endpoint,
            data=json.dumps(
                {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0},
                }
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(
            request, timeout=60
        ) as response:  # nosec B310: local, explicit endpoint
            payload = json.loads(response.read().decode("utf-8"))
        text = payload.get("response")
        if not isinstance(text, str):
            raise ValueError("Ollama returned no analysis text.")
        return text, {"provider": "ollama", "model": self.model, "temperature": 0.0}


def _request_prompt(request: LanguageRequest) -> str:
    """Serialize only the immutable request contract for Ollama."""
    return json.dumps(request.to_dict(), sort_keys=True, ensure_ascii=True)
