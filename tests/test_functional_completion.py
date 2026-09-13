from pathlib import Path

STATIC = Path("src/dashboard/static")
MODULE = STATIC / "frontend" / "modules" / "functional-completion.js"


def test_functional_completion_is_loaded_by_frontend() -> None:
    source = MODULE.read_text(encoding="utf-8")
    frontend = (STATIC / "frontend" / "index.js").read_text(encoding="utf-8")
    assert "export function initFunctionalCompletion" in source
    assert 'import { initFunctionalCompletion } from "./modules/functional-completion.js";' in frontend
    assert "initFunctionalCompletion();" in frontend


def test_neuron_viewer_uses_real_runtime_contracts_for_cumulative_hz() -> None:
    source = MODULE.read_text(encoding="utf-8")
    assert '/api/network/summary' in source
    assert '/api/network/projection?limit=${requested}&mode=activity' in source
    assert "const dtMs = 1.0" in source
    assert "spikeCount / durationSeconds" in source
    assert "kumulative Feuerrate" in source
    assert "Kein EVIDENCE-Claim" in source


def test_neuron_view_profile_is_real_presentation_only_state() -> None:
    source = MODULE.read_text(encoding="utf-8")
    assert 'mhrn.neuron-model-viewer.profile.v1' in source
    assert 'scope: "presentation_only"' in source
    assert "localStorage.setItem" in source
    assert "localStorage.getItem" in source
    assert "Do not auto-run an expensive analysis job" in source


def test_embodiment_feedback_uses_pipeline_and_state_contracts() -> None:
    source = MODULE.read_text(encoding="utf-8")
    assert '/api/embodiment/pipeline' in source
    assert '/api/embodiment/state' in source
    for state in (
        "observation received",
        "adapter feedback unavailable",
        "enabled · waiting for observation",
        "ready · disabled",
        "state unknown",
    ):
        assert state in source


def test_guarded_disabled_controls_are_not_force_enabled() -> None:
    source = MODULE.read_text(encoding="utf-8")
    # Completion must never globally bypass authorization/lifecycle guards.
    assert ".disabled = false" not in source
    assert "removeAttribute(\"disabled\")" not in source
    assert "button:disabled" in source
    assert "Wird automatisch aktiviert" in source


def test_existing_sensor_and_gateway_guards_remain_explicit() -> None:
    wesen = (STATIC / "wesen.js").read_text(encoding="utf-8")
    gateway = (STATIC / "wesen-neural-symbiosis.js").read_text(encoding="utf-8")
    assert "!sensor.available" in wesen
    assert "!sensor.authorized" in wesen
    assert '/enable' in wesen or '"enable"' in wesen
    assert '/disable' in wesen or '"disable"' in wesen
    assert "button.disabled = !experimentMode" in gateway


def test_cognition_memory_controls_are_already_functional() -> None:
    cognition = (STATIC / "frontend" / "modules" / "cognition.js").read_text(encoding="utf-8")
    assert "/api/cognition/memory/controls" in cognition
    assert 'action: "read"' in cognition
    assert 'action: "write"' in cognition


def test_fullscreen_has_native_and_css_fallback() -> None:
    controller = (STATIC / "box-state-controller.js").read_text(encoding="utf-8")
    assert "requestFullscreen" in controller
    assert "box-fullscreen-fallback" in controller
