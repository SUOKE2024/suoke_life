"""Server startup script for look service."""

import asyncio
import signal
import sys
from typing import Any

import uvicorn
from uvicorn.config import LOGGING_CONFIG

from ..api.app import create_app
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


def setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def configure_uvicorn_logging() -> dict[str, Any]:
    """Configure uvicorn logging to match our logging setup."""
    config = LOGGING_CONFIG.copy()

    # Disable uvicorn's default logging if we're using JSON format
    if settings.monitoring.log_format == "json":
        config["disable_existing_loggers"] = True
        config["loggers"]["uvicorn"]["handlers"] = []
        config["loggers"]["uvicorn.access"]["handlers"] = []

    return config


async def run_server() -> None:
    """Run the FastAPI server with uvicorn."""
    logger.info("Starting Look Service server")

    # Create FastAPI app
    app = create_app()

    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host=settings.service.host,
        port=settings.service.port,
        workers=1,  # Use 1 worker for development, scale with deployment
        log_config=configure_uvicorn_logging(),
        log_level=settings.monitoring.log_level.lower(),
        access_log=True,
        use_colors=settings.monitoring.log_format != "json",
        reload=settings.is_development,
        reload_dirs=["look_service"] if settings.is_development else None,
    )

    # Create and run server
    server = uvicorn.Server(config)

    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")


def main() -> None:
    """Main entry point for the server."""
    logger.info(
        "Look Service starting",
        version=settings.service.service_version,
        environment=settings.service.environment,
        host=settings.service.host,
        port=settings.service.port,
    )

    # Setup signal handlers
    setup_signal_handlers()

    try:
        # Run the server
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
