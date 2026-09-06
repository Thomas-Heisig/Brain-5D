from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "dashboard" / "static"


def _read(name: str) -> str:
    return (STATIC / name).read_text(encoding="utf-8")


def test_three_area_shell_is_loaded_and_has_exact_primary_areas() -> None:
    console = _read("console-log.js")
    shell = _read("frontend-architecture.js")

    assert 'import "./frontend-architecture.js"' in console
    assert 'data-primary-area="dashboard"' in shell
    assert 'data-primary-area="science"' in shell
    assert 'data-primary-area="wesen"' in shell
    assert "Dashboard" in shell
    assert "Wissenschaft" in shell
    assert "Runtime & Wesen" in shell
    assert ".tab-nav { display:none !important; }" in shell


def test_science_area_preserves_network_research_and_settings_routes() -> None:
    shell = _read("frontend-architecture.js")
    console = _read("console-log.js")

    for route in ("network", "research", "settings"):
        assert f'data-science-route="{route}"' in shell
    assert 'for (const name of ["network", "gate"] )' in console
    assert 'button.classList.add("wesen-utility-hidden")' in console
    assert "querySelector('.tab-btn[data-tab=\"network\"]')?.remove()" not in console
    assert "querySelector('.tab-btn[data-tab=\"gate\"]')?.remove()" not in console


def test_future_runtime_capabilities_are_visible_but_not_claimed_live() -> None:
    shell = _read("frontend-architecture.js")

    assert "Einzelne Sinne aktivieren/deaktivieren: Not implemented yet" in shell
    assert "Produktive Gateway-Aktivierung und Gateway-Plastizität: Not implemented yet" in shell
    assert "Profil laden/speichern/exportieren/löschen: Not implemented yet" in shell
    assert "Memory-/World-Model-Layer: Not implemented yet" in shell


def test_neuron_model_viewer_replaces_legacy_projection_without_deleting_it() -> None:
    console = _read("console-log.js")
    viewer = _read("neuron-model-viewer.js")

    assert 'import "./neuron-model-viewer.js"' in console
    assert 'section.id = "neuron-model-viewer"' in viewer
    assert 'byId("network-projection")' in viewer
    assert "legacy.hidden = true" in viewer
    assert 'legacy.dataset.replacedBy = "neuron-model-viewer"' in viewer


def test_neuron_model_viewer_uses_bounded_real_data_and_client_pca() -> None:
    viewer = _read("neuron-model-viewer.js")

    assert "/api/network/projection?limit=${limit}&mode=activity" in viewer
    assert "/api/network/synapses?limit=${MAX_DENSITY_SYNAPSES}&offset=0" in viewer
    assert "function computePca" in viewer
    assert "function jacobiEigen" in viewer
    assert "sampleCount: 500" in viewer
    assert '<option value="500" selected>500 Neuronen</option>' in viewer
    assert '<option value="0" selected>Manuell</option>' in viewer
    assert 'data-nmv-view="correlation"' in viewer
    assert 'data-nmv-view="parallel"' in viewer


def test_heavy_embeddings_and_unavailable_metrics_are_honestly_marked() -> None:
    viewer = _read("neuron-model-viewer.js")

    assert '<option value="tsne" disabled>t-SNE · Not implemented yet</option>' in viewer
    assert '<option value="umap" disabled>UMAP · Not implemented yet</option>' in viewer
    assert "Cluster-Kennzahl" in viewer
    assert "Not implemented yet · keine Clusterlabels" in viewer
    assert "Per-neuron Hz" in viewer
    assert "Not implemented yet · Farbe nutzt Activity-Proxy" in viewer
    assert "Lasso / Cluster export" in viewer


def test_three_dimensional_mode_is_single_point_cloud_with_canvas_fallback() -> None:
    viewer = _read("neuron-model-viewer.js")

    assert "new THREE.BufferGeometry()" in viewer
    assert "new THREE.Points(geometry, material)" in viewer
    assert 'powerPreference: "low-power"' in viewer
    assert "drawThreeCanvasFallback" in viewer
