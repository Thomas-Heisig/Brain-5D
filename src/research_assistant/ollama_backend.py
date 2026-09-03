"""Optional local Ollama adapter with no execution or filesystem authority."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from time import perf_counter_ns
from typing import Any, cast
from urllib.request import Request, urlopen

from src.language_organ.protocols import LanguageRequest, LanguageResponse

from .contracts import AIInferenceFailureEvent


class OllamaBackend:
    """Call Ollama through the read-only language-backend contract."""

    def __init__(
        self,
        model: str,
        endpoint: str = "http://127.0.0.1:11434/api/generate",
        temperature: float = 0.0,
        top_p: float = 0.9,
        max_tokens: int = 2048,
        top_k: int | None = None,
        num_ctx: int | None = None,
        seed: int | None = None,
        stop: list[str] | None = None,
        timeout: float = 60.0,
        model_digest: str | None = None,
        artifact_digest: str | None = None,
        quantization: str | None = None,
        precision: str | None = None,
        engine_version: str | None = None,
        hardware: str | None = None,
        tokenizer_digest: str | None = None,
        prompt_template_digest: str | None = None,
        system_prompt_digest: str | None = None,
        toolset_digest: str | None = None,
        retrieval_snapshot_digest: str | None = None,
        provider_revision: str | None = None,
        knowledge_origin: str = "UNKNOWN",
    ) -> None:
        self.model = model
        self.endpoint = endpoint
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.top_k = top_k
        self.num_ctx = num_ctx
        self.seed = seed
        self.stop = list(stop or [])
        self.timeout = timeout
        self.model_digest = model_digest or "not_reported"
        self.artifact_digest = artifact_digest or "not_reported"
        self.quantization = quantization or "not_reported"
        self.precision = precision or "not_reported"
        self.engine_version = engine_version or "not_reported"
        self.hardware = hardware or "not_reported"
        self.tokenizer_digest = tokenizer_digest or "not_reported"
        self.prompt_template_digest = prompt_template_digest or "not_reported"
        self.system_prompt_digest = system_prompt_digest or "not_reported"
        self.toolset_digest = toolset_digest or "not_reported"
        self.retrieval_snapshot_digest = retrieval_snapshot_digest or "not_reported"
        self.provider_revision = provider_revision or "not_reported"
        self.knowledge_origin = knowledge_origin.strip() or "UNKNOWN"
        self._last_failure_event: AIInferenceFailureEvent | None = None

    @property
    def last_failure_event(self) -> AIInferenceFailureEvent | None:
        """Return the most recent failed inference audit event, if any."""
        return self._last_failure_event

    @property
    def name(self) -> str:
        """Return a stable backend identifier for dashboard and provenance."""
        return "ollama"

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        """Process immutable language data and convert failures to responses."""
        started_ns = perf_counter_ns()
        request_digest = hashlib.sha256(
            _request_prompt(request).encode("utf-8")
        ).hexdigest()
        self._last_failure_event = None
        try:
            text, _metadata = self._generate(_request_prompt(request))
            return LanguageResponse(
                request_id=request.request_id,
                text=text,
                backend_name=self.name,
                success=True,
            )
        except (OSError, ValueError) as exc:
            self._last_failure_event = AIInferenceFailureEvent.create(
                request_id=request.request_id,
                backend=self.name,
                request_digest=request_digest,
                latency_ms=(perf_counter_ns() - started_ns) / 1_000_000,
                retry_status="not_retried",
                error=str(exc),
            )
            return LanguageResponse(
                request_id=request.request_id,
                text="",
                backend_name=self.name,
                success=False,
                error=str(exc),
            )

    def __call__(self, prompt: str) -> tuple[dict[str, Any], dict[str, Any]]:
        text, metadata = self._generate(prompt, format_json=True)
        return _parse_json_object(text), metadata

    def generate_text(
        self,
        prompt: str,
        images: list[str] | None = None,
        tools: list[dict[str, object]] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Return plain text for read-only chat consumers."""
        return self._generate(prompt, images=images, tools=tools)

    def _generate(
        self,
        prompt: str,
        images: list[str] | None = None,
        tools: list[dict[str, object]] | None = None,
        format_json: bool = False,
    ) -> tuple[str, dict[str, Any]]:
        payload: dict[str, object] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        }
        options = cast(dict[str, object], payload["options"])
        optional_options = {
            "top_k": self.top_k,
            "num_ctx": self.num_ctx,
            "seed": self.seed,
        }
        options.update(
            {key: value for key, value in optional_options.items() if value is not None}
        )
        if self.stop:
            options["stop"] = self.stop
        if images:
            payload["images"] = images
        if tools:
            payload["tools"] = tools
        if format_json:
            payload["format"] = "json"
        request_data = json.dumps(payload).encode()
        request = Request(
            self.endpoint,
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        request_digest = hashlib.sha256(request_data).hexdigest()
        request_timestamp = datetime.now(timezone.utc).isoformat()
        with urlopen(
            request, timeout=self.timeout
        ) as response:  # nosec B310: local, explicit endpoint
            payload = json.loads(response.read().decode("utf-8"))
        text = payload.get("response")
        if not isinstance(text, str):
            raise ValueError("Ollama returned no analysis text.")
        return text, {
            "provider": "ollama",
            "provider_revision": self.provider_revision,
            "request_timestamp": request_timestamp,
            "knowledge_origin": self.knowledge_origin,
            "model": self.model,
            "model_id": str(payload.get("model", self.model)),
            "model_digest": self.model_digest,
            "artifact_digest": self.artifact_digest,
            "quantization": self.quantization,
            "precision": self.precision,
            "engine_version": self.engine_version,
            "hardware": self.hardware,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k if self.top_k is not None else "not_reported",
            "num_ctx": self.num_ctx if self.num_ctx is not None else "not_reported",
            "seed": self.seed if self.seed is not None else "not_reported",
            "stop": list(self.stop),
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout,
            "retry_count": 0,
            "retry_policy": "disabled",
            "request_digest": request_digest,
            "response_digest": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "response_fingerprint": hashlib.sha256(
                json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
            ).hexdigest(),
            "tokenizer_digest": self.tokenizer_digest,
            "prompt_template_digest": self.prompt_template_digest,
            "system_prompt_digest": self.system_prompt_digest,
            "toolset_digest": self.toolset_digest,
            "retrieval_snapshot_digest": self.retrieval_snapshot_digest,
            "created_at": str(payload.get("created_at", "not_reported")),
            "done_reason": str(payload.get("done_reason", "not_reported")),
            "total_duration_ns": _numeric_metadata(payload.get("total_duration")),
            "load_duration_ns": _numeric_metadata(payload.get("load_duration")),
            "prompt_eval_count": _numeric_metadata(payload.get("prompt_eval_count")),
            "eval_count": _numeric_metadata(payload.get("eval_count")),
        }


def _parse_json_object(text: str) -> dict[str, Any]:
    """Parse an object from strict JSON or a model-wrapped JSON response."""
    decoder = json.JSONDecoder()
    stripped = text.strip()
    candidates = [stripped]
    if "```" in stripped:
        candidates.extend(
            block.strip()
            for block in stripped.split("```")[1::2]
            if block.strip().removeprefix("json").strip()
        )
    for candidate in candidates:
        candidate = candidate.removeprefix("json").strip()
        try:
            output_raw: Any = json.loads(candidate)
        except json.JSONDecodeError:
            output_raw = None
        if isinstance(output_raw, dict):
            return cast(dict[str, Any], output_raw)
        for index, character in enumerate(candidate):
            if character != "{":
                continue
            try:
                output_raw, _ = decoder.raw_decode(candidate[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(output_raw, dict):
                return cast(dict[str, Any], output_raw)
    raise ValueError("Ollama output must contain a JSON object.")


def _request_prompt(request: LanguageRequest) -> str:
    """Serialize only the immutable request contract for Ollama."""
    return json.dumps(request.to_dict(), sort_keys=True, ensure_ascii=True)


def _numeric_metadata(value: object) -> int | str:
    return (
        value
        if isinstance(value, int) and not isinstance(value, bool)
        else "not_reported"
    )
