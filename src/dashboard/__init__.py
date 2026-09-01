"""Brain-5D local operator dashboard.

This package provides a web-based dashboard for monitoring and controlling
the Brain-5D runtime. It includes:

- A lightweight HTTP server with no external dependencies
- Real-time telemetry visualization
- Structural plasticity control (proposals, approval, history)
- Heatmap generation from B5D snapshots
- Documentation browsing with multi-format support (MD, DOCX, XLSX, CSV, JSON, PDF)
- Thread-safe state management with event notifications

The dashboard is designed to be run locally alongside the Brain-5D runtime
and accessed via a web browser.

Example:
    >>> from src.dashboard import serve_dashboard
    >>> serve_dashboard(host="127.0.0.1", port=8765)

    Or via command line:
    >>> python -m src.dashboard --host 0.0.0.0 --port 8765
"""

from __future__ import annotations

import logging

from src.version import BRAIN5D_VERSION_DISPLAY

from .docs_source import DocumentationSource, create_docs_source
from .heatmap_source import SnapshotHeatmapSource, create_heatmap_source
from .models import (
    DashboardSnapshot,
    ExperimentMetrics,
    HomeostasisMetrics,
    JSONValue,
    KnowledgeIntakeMetrics,
    LanguageOrganMetrics,
    LearningMetrics,
    NetworkMetrics,
    SelfOrganizationMetrics,
    SignalMetrics,
    SpikeMetrics,
    StorageMetrics,
    StructuralMetrics,
    SystemMetrics,
)
from .operator_bridge import OperatorBridge
from .server import serve_dashboard
from .state import (
    DashboardStateStore,
    create_state_store,
    get_current_state,
    publish_state,
)

# Package version
__version__ = BRAIN5D_VERSION_DISPLAY

# Module logger
logger = logging.getLogger(__name__)


# ============================================================================
# Convenience Functions
# ============================================================================


def create_default_dashboard(
    host: str = "127.0.0.1",
    port: int = 8765,
    snapshot_path: str | None = None,
    docs_root: str | None = None,
    state_store: DashboardStateStore | None = None,
    structural_bridge: OperatorBridge | None = None,
) -> None:
    """Create and run a dashboard with default configuration.

    This is a convenience wrapper around serve_dashboard that provides
    sensible defaults and handles path resolution.

    Args:
        host: Host address to bind to (default: 127.0.0.1).
        port: Port to bind to (default: 8765).
        snapshot_path: Optional path to the default B5D snapshot.
        docs_root: Optional path to the documentation root.
        state_store: Optional custom state store.
        structural_bridge: Optional operator bridge for structural control.

    Example:
        >>> from src.dashboard import create_default_dashboard
        >>> create_default_dashboard(port=9000)
    """
    from pathlib import Path

    # Resolve paths if provided
    snapshot = Path(snapshot_path).resolve() if snapshot_path else None
    docs = Path(docs_root).resolve() if docs_root else None

    # Create state store if not provided
    if state_store is None:
        state_store = create_state_store(with_history=True, history_limit=100)

    # Run the dashboard
    serve_dashboard(
        host=host,
        port=port,
        state=state_store,
        snapshot_path=snapshot,
        docs_root=docs,
        structural_bridge=structural_bridge,
    )


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Core types
    "DashboardSnapshot",
    "DashboardStateStore",
    "OperatorBridge",
    "DocumentationSource",
    "SnapshotHeatmapSource",
    # Metric models
    "SystemMetrics",
    "LearningMetrics",
    "StorageMetrics",
    "SelfOrganizationMetrics",
    "HomeostasisMetrics",
    "StructuralMetrics",
    "SpikeMetrics",
    "NetworkMetrics",
    "LanguageOrganMetrics",
    "KnowledgeIntakeMetrics",
    "SignalMetrics",
    "ExperimentMetrics",
    "JSONValue",
    # Server functions
    "serve_dashboard",
    "create_default_dashboard",
    # State management
    "create_state_store",
    "get_current_state",
    "publish_state",
    # Factory functions
    "create_heatmap_source",
    "create_docs_source",
    # Version
    "__version__",
]
