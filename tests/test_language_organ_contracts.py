import json
from typing import Any

from src.language_organ.bridge import LanguageOrgan
from src.language_organ.null_backend import NullLanguageBackend
from src.language_organ.protocols import LanguageRequest
from src.language_organ.sham_backends import RandomLanguageOrgan, ReplayLanguageOrgan
from src.research_assistant.ollama_backend import OllamaBackend
from src.signal_processing.models import SignalFrame


def test_language_organ_is_disabled_by_default() -> None:
    frame = SignalFrame(0, 0, (), 0.0, 0, 0.0, 0.0, 0.0, 0.0, ())
    organ = LanguageOrgan(NullLanguageBackend())
    response = organ.interpret_signal(
        request_id="test", frame=frame, instruction="Describe the signal."
    )
    assert response.success is False
    assert organ.status.enabled is False
    assert response.backend_name == "null"


def test_random_language_sham_is_deterministic() -> None:
    request = LanguageRequest("req-sham", "monitor", "state")
    first = RandomLanguageOrgan(seed=7).infer(request)
    second = RandomLanguageOrgan(seed=7).infer(request)
    assert first.success is True
    assert first.backend_name == "random_sham"
    assert first.text == second.text


def test_replay_language_sham_fails_closed_without_live_fallback() -> None:
    request = LanguageRequest("req-replay", "monitor", "state")
    digest = ReplayLanguageOrgan.request_digest(request)
    backend = ReplayLanguageOrgan({digest: "replayed"})
    response = backend.infer(request)
    missing = backend.infer(LanguageRequest("other", "monitor", "state"))
    assert response.success is True
    assert response.text == "replayed"
    assert missing.success is False
    assert "No replay response" in (missing.error or "")


def test_ollama_backend_implements_read_only_language_contract(
    monkeypatch: Any,
) -> None:
    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args: Any) -> None:
            return None

        def read(self):
            return json.dumps({"response": '{"assessment":"ok"}'}).encode()

    def _urlopen(*_args: Any, **_kwargs: Any) -> _Response:
        return _Response()

    monkeypatch.setattr(
        "src.research_assistant.ollama_backend.urlopen",
        _urlopen,
    )
    response = OllamaBackend("qwen").infer(
        LanguageRequest(request_id="req-1", purpose="monitor", text="status")
    )

    assert response.success is True
    assert response.backend_name == "ollama"
    assert response.text == '{"assessment":"ok"}'


def test_ollama_backend_provenance_contains_sampling_parameters(
    monkeypatch: Any,
) -> None:
    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args: Any) -> None:
            return None

        def read(self):
            return json.dumps(
                {
                    "model": "qwen",
                    "response": "answer",
                    "created_at": "2026-09-03T00:00:00Z",
                    "done_reason": "stop",
                    "total_duration": 100,
                    "prompt_eval_count": 4,
                    "eval_count": 2,
                }
            ).encode()

    requests: list[Any] = []

    def _urlopen(request: Any, **_kwargs: Any) -> _Response:
        requests.append(json.loads(request.data.decode()))
        return _Response()

    monkeypatch.setattr("src.research_assistant.ollama_backend.urlopen", _urlopen)
    backend = OllamaBackend(
        "qwen", top_k=20, num_ctx=4096, seed=42, stop=["END"], timeout=12
    )
    answer, metadata = backend.generate_text("prompt")

    assert answer == "answer"
    assert requests[0]["options"]["top_k"] == 20
    assert requests[0]["options"]["num_ctx"] == 4096
    assert requests[0]["options"]["seed"] == 42
    assert requests[0]["options"]["stop"] == ["END"]
    assert metadata["timeout_seconds"] == 12
    assert metadata["retry_count"] == 0
    assert metadata["retry_policy"] == "disabled"
    assert metadata["model_id"] == "qwen"
    assert metadata["done_reason"] == "stop"
    assert metadata["prompt_eval_count"] == 4
    assert metadata["eval_count"] == 2
    request_digest = metadata["request_digest"]
    response_digest = metadata["response_digest"]
    assert isinstance(request_digest, str) and len(request_digest) == 64
    assert isinstance(response_digest, str) and len(response_digest) == 64


def test_ollama_inference_failure_is_audited(monkeypatch: Any) -> None:
    def _urlopen(*_args: Any, **_kwargs: Any) -> Any:
        raise OSError("provider unavailable")

    monkeypatch.setattr("src.research_assistant.ollama_backend.urlopen", _urlopen)
    backend = OllamaBackend("qwen")
    response = backend.infer(
        LanguageRequest(request_id="req-failure", purpose="describe", text="state")
    )

    assert response.success is False
    event = backend.last_failure_event
    assert event is not None
    assert event.request_id == "req-failure"
    assert event.backend == "ollama"
    assert event.retry_status == "not_retried"
    assert event.error == "provider unavailable"
    assert len(event.request_digest) == 64
    assert event.latency_ms >= 0
