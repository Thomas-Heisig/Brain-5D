from src.language_organ.bridge import LanguageOrgan
from src.language_organ.null_backend import NullLanguageBackend
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
