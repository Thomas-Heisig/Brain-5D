"""Optional local Ollama adapter with no execution or filesystem authority."""

from __future__ import annotations

import json
from typing import Any, cast
from urllib.request import Request, urlopen


class OllamaBackend:
    """Call a local Ollama model and accept only a JSON interpretation object."""

    def __init__(
        self, model: str, endpoint: str = "http://127.0.0.1:11434/api/generate"
    ) -> None:
        self.model = model
        self.endpoint = endpoint

    def __call__(self, prompt: str) -> tuple[dict[str, Any], dict[str, str | float]]:
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
        output_raw: Any = json.loads(text)
        if not isinstance(output_raw, dict):
            raise ValueError("Ollama output must be a JSON object.")
        output = cast(dict[str, Any], output_raw)
        return output, {"provider": "ollama", "model": self.model, "temperature": 0.0}
