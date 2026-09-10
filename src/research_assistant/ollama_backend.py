"""Optional local Ollama adapter with bounded retries and no mutation authority."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.language_organ.protocols import LanguageRequest, LanguageResponse

from .contracts import AIInferenceFailureEvent
from .repository_context import RepositoryContext, RepositoryKnowledgeView


class OllamaBackend:
    """Shared read-only provider for chat, insights and AIRR evaluation."""

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
        retries: int = 2,
        retry_backoff_seconds: float = 0.25,
        repository_root: Path | None = None,
        repository_context_chars: int = 80_000,
    ) -> None:
        if retries < 0 or retries > 5:
            raise ValueError("retries must be between 0 and 5")
        if retry_backoff_seconds < 0.0 or retry_backoff_seconds > 5.0:
            raise ValueError("retry_backoff_seconds must be between 0 and 5")
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
        self.retries = retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.repository_root = (
            repository_root.resolve()
            if repository_root is not None
            else Path(__file__).resolve().parents[2]
        )
        self.repository_context_chars = max(8_000, int(repository_context_chars))
        self._last_failure_event: AIInferenceFailureEvent | None = None
        self._last_repository_context: RepositoryContext | None = None

    @property
    def last_failure_event(self) -> AIInferenceFailureEvent | None:
        return self._last_failure_event

    @property
    def name(self) -> str:
        return "ollama"

    def infer(self, request: LanguageRequest) -> LanguageResponse:
        started_ns = perf_counter_ns()
        prompt = _request_prompt(request)
        request_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        self._last_failure_event = None
        try:
            text, _metadata = self._generate(prompt)
            return LanguageResponse(
                request_id=request.request_id,
                text=text,
                backend_name=self.name,
                success=True,
            )
        except (OSError, ValueError, HTTPError, URLError) as exc:
            self._last_failure_event = AIInferenceFailureEvent.create(
                request_id=request.request_id,
                backend=self.name,
                request_digest=request_digest,
                latency_ms=(perf_counter_ns() - started_ns) / 1_000_000,
                retry_status="exhausted",
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
        """Return schema-shaped analysis and preserve invalid provider output as failure."""
        text, metadata = self._generate(prompt, format_json=True)
        try:
            parsed = _parse_json_object(text)
            metadata["structured_output_valid"] = True
            return parsed, metadata
        except ValueError as first_error:
            repair_prompt = (
                "Convert the following assistant output to ONE valid JSON object only. "
                "Required keys: assessment (string), observations (array), "
                "methodological_concerns (array), alternative_explanations (array), "
                "recommended_experiments (array), requested_evidence (array), "
                "confidence (number 0..1), effect_direction (string). Do not add facts.\n\n"
                + text[:12000]
            )
            try:
                repaired_text, repaired_metadata = self._generate(
                    repair_prompt, format_json=True
                )
                parsed = _parse_json_object(repaired_text)
                repaired_metadata["structured_output_valid"] = True
                repaired_metadata["structured_output_repaired"] = True
                repaired_metadata["original_response_digest"] = metadata.get(
                    "response_digest", "not_reported"
                )
                return parsed, repaired_metadata
            except (OSError, ValueError, HTTPError, URLError) as repair_error:
                failure = _structured_failure(first_error, repair_error)
                metadata["structured_output_valid"] = False
                metadata["structured_output_repaired"] = False
                metadata["structured_output_error"] = str(first_error)
                metadata["structured_repair_error"] = str(repair_error)
                return failure, metadata

    def generate_text(
        self,
        prompt: str,
        images: list[str] | None = None,
        tools: list[dict[str, object]] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        return self._generate(prompt, images=images, tools=tools)

    def _repository_prompt(self, prompt: str) -> str:
        if "[REPOSITORY FILE:" in prompt or "REPOSITORY READ-ONLY RETRIEVAL" in prompt:
            self._last_repository_context = None
            return prompt
        context = RepositoryKnowledgeView(
            self.repository_root,
            max_context_chars=self.repository_context_chars,
        ).retrieve(prompt[:16_000])
        self._last_repository_context = context
        if not context.text:
            return prompt
        return (
            prompt
            + "\n\nSHARED REPOSITORY CONTEXT (read-only; source/docs are not scientific EVID):\n"
            + context.text
        )

    def _generate(
        self,
        prompt: str,
        images: list[str] | None = None,
        tools: list[dict[str, object]] | None = None,
        format_json: bool = False,
    ) -> tuple[str, dict[str, Any]]:
        grounded_prompt = self._repository_prompt(prompt)
        payload: dict[str, object] = {
            "model": self.model,
            "prompt": grounded_prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        }
        options = cast(dict[str, object], payload["options"])
        options.update(
            {
                key: value
                for key, value in {
                    "top_k": self.top_k,
                    "num_ctx": self.num_ctx,
                    "seed": self.seed,
                }.items()
                if value is not None
            }
        )
        if self.stop:
            options["stop"] = self.stop
        if images:
            payload["images"] = images
        if tools:
            payload["tools"] = tools
        if format_json:
            payload["format"] = "json"
        request_data = json.dumps(payload).encode("utf-8")
        request_digest = hashlib.sha256(request_data).hexdigest()
        last_error: BaseException | None = None
        attempts = self.retries + 1
        for attempt in range(attempts):
            request_timestamp = datetime.now(timezone.utc).isoformat()
            request = Request(
                self.endpoint,
                data=request_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urlopen(  # nosec B310: local/configured explicit provider endpoint
                    request, timeout=self.timeout
                ) as response:
                    raw = response.read().decode("utf-8")
                response_payload = json.loads(raw)
                if not isinstance(response_payload, dict):
                    raise ValueError("Ollama response must be a JSON object.")
                text = response_payload.get("response")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("Ollama returned no analysis text.")
                return text, self._metadata(
                    response_payload,
                    text,
                    request_digest=request_digest,
                    request_timestamp=request_timestamp,
                    retry_count=attempt,
                )
            except (
                OSError,
                ValueError,
                json.JSONDecodeError,
                HTTPError,
                URLError,
            ) as exc:
                last_error = exc
                if attempt + 1 >= attempts:
                    break
                if self.retry_backoff_seconds:
                    time.sleep(self.retry_backoff_seconds * (attempt + 1))
        raise OSError(
            f"Ollama inference failed after {attempts} attempt(s): {last_error}"
        ) from last_error

    def _metadata(
        self,
        payload: dict[str, Any],
        text: str,
        *,
        request_digest: str,
        request_timestamp: str,
        retry_count: int,
    ) -> dict[str, Any]:
        context = self._last_repository_context
        return {
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
            "retry_count": retry_count,
            "retry_limit": self.retries,
            "retry_policy": "bounded_linear_backoff",
            "request_digest": request_digest,
            "response_digest": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "response_fingerprint": hashlib.sha256(
                json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
            ).hexdigest(),
            "tokenizer_digest": self.tokenizer_digest,
            "prompt_template_digest": self.prompt_template_digest,
            "system_prompt_digest": self.system_prompt_digest,
            "toolset_digest": self.toolset_digest,
            "retrieval_snapshot_digest": (
                context.digest if context is not None else self.retrieval_snapshot_digest
            ),
            "repository_indexed_files": (
                context.indexed_files if context is not None else "provided_upstream"
            ),
            "repository_selected_files": (
                list(context.selected_files) if context is not None else "provided_upstream"
            ),
            "repository_omitted_large_files": (
                context.omitted_large_files if context is not None else "provided_upstream"
            ),
            "repository_authority": "read_only_non_evidentiary",
            "created_at": str(payload.get("created_at", "not_reported")),
            "done_reason": str(payload.get("done_reason", "not_reported")),
            "total_duration_ns": _numeric_metadata(payload.get("total_duration")),
            "load_duration_ns": _numeric_metadata(payload.get("load_duration")),
            "prompt_eval_count": _numeric_metadata(payload.get("prompt_eval_count")),
            "eval_count": _numeric_metadata(payload.get("eval_count")),
        }


def _structured_failure(
    first_error: BaseException, repair_error: BaseException
) -> dict[str, Any]:
    return {
        "assessment": "Provider output could not be validated as structured analysis; no scientific interpretation is inferred.",
        "observations": [],
        "methodological_concerns": [
            f"Initial structured output invalid: {type(first_error).__name__}: {first_error}",
            f"Repair attempt failed: {type(repair_error).__name__}: {repair_error}",
        ],
        "alternative_explanations": [],
        "recommended_experiments": [],
        "requested_evidence": [
            "Repeat provider analysis from the same immutable research packet."
        ],
        "effect_direction": "not_assessed",
        "confidence": 0.0,
    }


def _parse_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    stripped = text.strip()
    candidates = [stripped]
    if "```" in stripped:
        candidates.extend(
            block.strip() for block in stripped.split("```")[1::2] if block.strip()
        )
    for candidate in candidates:
        candidate = candidate.removeprefix("json").strip()
        try:
            output_raw: Any = json.loads(candidate)
        except json.JSONDecodeError:
            output_raw = None
        if isinstance(output_raw, dict):
            return _normalize_analysis_output(cast(dict[str, Any], output_raw))
        for index, character in enumerate(candidate):
            if character != "{":
                continue
            try:
                output_raw, _ = decoder.raw_decode(candidate[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(output_raw, dict):
                return _normalize_analysis_output(cast(dict[str, Any], output_raw))
    raise ValueError("Ollama output must contain a JSON object.")


def _normalize_analysis_output(output: dict[str, Any]) -> dict[str, Any]:
    if "confidence" not in output:
        return output
    confidence = output.get("confidence")
    if isinstance(confidence, str):
        try:
            output["confidence"] = float(confidence.strip())
        except ValueError:
            output["confidence"] = 0.0
    elif not isinstance(confidence, (int, float)):
        output["confidence"] = 0.0
    return output


def _request_prompt(request: LanguageRequest) -> str:
    return json.dumps(request.to_dict(), sort_keys=True, ensure_ascii=True)


def _numeric_metadata(value: object) -> int | str:
    return value if isinstance(value, int) and not isinstance(value, bool) else "not_reported"
