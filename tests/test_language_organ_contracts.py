import json

from src.language_organ.bridge import LanguageOrgan
from src.language_organ.null_backend import NullLanguageBackend
from src.language_organ.protocols import LanguageRequest
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


def test_ollama_backend_implements_read_only_language_contract(monkeypatch) -> None:
    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps({"response": '{"assessment":"ok"}'}).encode()

    monkeypatch.setattr(
        "src.research_assistant.ollama_backend.urlopen",
        lambda *_args, **_kwargs: _Response(),
    )
    response = OllamaBackend("qwen").infer(
        LanguageRequest(request_id="req-1", purpose="monitor", text="status")
    )

    assert response.success is True
    assert response.backend_name == "ollama"
    assert response.text == '{"assessment":"ok"}'
