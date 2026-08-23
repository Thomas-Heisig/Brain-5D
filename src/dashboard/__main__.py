"""Run the Brain-5D operator dashboard with ``python -m src.dashboard``.

This module serves as the entry point for the Brain-5D dashboard application.
It delegates to the server's main() function with enhanced error handling
and user-friendly messages.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def _configure_logging(level: str = "INFO") -> None:
    """Configure logging for the dashboard application."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def main() -> int:
    """Main entry point for the Brain-5D dashboard.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    _configure_logging()
    logger = logging.getLogger(__name__)

    try:
        from .server import main as server_main

        if not (Path(__file__).parent / "static").exists():
            logger.warning(
                "Static directory not found. Dashboard may not display correctly."
            )

        server_main()
        return 0

    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user.")
        return 0

    except ImportError as e:
        logger.error(f"Failed to import required module: {e}")
        return 1

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


def run() -> None:
    """Run the dashboard and exit with the appropriate status code."""
    sys.exit(main())


if __name__ == "__main__":
    run()
