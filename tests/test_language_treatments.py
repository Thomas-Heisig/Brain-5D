from src.language_organ.protocols import LanguageOrganMode, LanguageRequest


def test_language_request_exposes_explicit_treatment_mode() -> None:
    request = LanguageRequest(
        request_id="req-1",
        purpose="describe",
        text="state",
        mode=LanguageOrganMode.SEMANTIC_AUGMENTATION,
    )
    assert request.to_dict()["mode"] == "SEMANTIC_AUGMENTATION"
