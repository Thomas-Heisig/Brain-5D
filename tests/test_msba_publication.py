from pathlib import Path

STATIC = Path("src/dashboard/static")
MSBA = STATIC / "msba"


def test_public_msba_surface_is_present_and_explicitly_read_only() -> None:
    page = (MSBA / "index.html").read_text(encoding="utf-8")
    assert "Neural Symbiosis · MSBA" in page
    assert "PUBLIC · READ ONLY" in page
    assert "Wissenschaftliche Grenze" in page
    assert "Gateway-Plastizität bleibt standardmäßig deaktiviert" in page
    assert 'data-gateway-action' not in page
    assert "Aktivieren" not in page


def test_public_msba_client_only_reads_existing_contracts() -> None:
    client = (MSBA / "msba.js").read_text(encoding="utf-8")
    assert 'getJson("/api/embodiment/neural-symbiosis")' in client
    assert 'getJson("/api/embodiment/connections")' in client
    assert "method: \"POST\"" not in client
    assert "method:'POST'" not in client
    assert "fetch(" in client
    assert "availableConnectionIds" in client
    assert "endpointReachable" in client
    assert "pipeline-reachable" in client


def test_public_msba_publishes_modalities_resources_and_guards() -> None:
    page = (MSBA / "index.html").read_text(encoding="utf-8")
    for required in (
        "AUDIO · TEMPORAL",
        "VISION · SPATIOTEMPORAL",
        "DIGITAL · HIGH FIDELITY",
        "Ressourcenökonomie",
        "Frozen · Random · Shuffle · Plastic",
        "Human Review",
        "keine direkten Schreibrechte in den kanonischen SNN-Kern",
    ):
        assert required in page


def test_public_aliases_point_to_canonical_msba_page() -> None:
    for name in ("msba.html", "neural-symbiosis.html"):
        source = (STATIC / name).read_text(encoding="utf-8")
        assert "/msba/index.html" in source


def test_msba_styles_are_standalone_and_responsive() -> None:
    styles = (MSBA / "msba.css").read_text(encoding="utf-8")
    assert ".three-grid" in styles
    assert ".pipeline-row" in styles
    assert ".area-grid" in styles
    assert "@media(max-width:900px)" in styles
    assert "@media(max-width:560px)" in styles


def test_existing_gateway_runtime_remains_fail_closed() -> None:
    runtime = Path("src/embodiment/gateway_runtime.py").read_text(encoding="utf-8")
    assert '"experimental_validation_incomplete"' in runtime
    assert '"experiment_only": True' in runtime
    assert '"canonical_core_mutation": False' in runtime
    assert '"direct_llm_write": False' in runtime
    assert 'GatewayCondition.FROZEN' in runtime
    assert 'GatewayCondition.RANDOM' in runtime
    assert 'GatewayCondition.SHUFFLE' in runtime
    assert 'GatewayCondition.PLASTIC' in runtime


def test_symbiosis_catalog_keeps_reachability_separate_from_activation() -> None:
    source = Path("src/embodiment/neural_symbiosis.py").read_text(encoding="utf-8")
    assert '"pipeline_reachability_is_not_activation": True' in source
    assert '"activation_requires_explicit_experiment": True' in source
    assert '"enabled": False' in source
    assert '"instantiated": False' in source
    assert '"gateway_learning": "disabled"' in source
