from collections.abc import AsyncGenerator
from collections.abc import Awaitable
from collections.abc import Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from health_data_service.api.routes import health_data_router
from health_data_service.api.routes.auth import auth_router
from health_data_service.core.cache import get_cache_manager
from health_data_service.core.config import settings
from health_data_service.core.database import get_database
from health_data_service.core.docs import setup_docs
from health_data_service.core.exceptions import DatabaseError
from health_data_service.core.exceptions import NotFoundError
from health_data_service.core.exceptions import ValidationError
from health_data_service.core.monitoring import get_health_status, get_metrics, record_request_metrics
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any
import asyncio
import logging
import signal
import sys
import time
import uvicorn

def main() -> None:
"""主函数 - 自动生成的最小可用版本"""
    pass

if __name__ == "__main__":
    main()
