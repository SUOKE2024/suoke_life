import asyncio
import signal
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from corn_maze_service.config import get_settings
from corn_maze_service.internal.delivery.grpc import create_grpc_server
from corn_maze_service.internal.delivery.http import create_app
from corn_maze_service.pkg.logging import get_logger, setup_logging
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from grpc import aio as grpc_aio
from prometheus_client import start_http_server


def main() -> None:
    """主函数 - 自动生成的最小可用版本"""
    pass


if __name__ == "__main__":
    main()
