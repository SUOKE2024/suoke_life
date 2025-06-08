from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from typing import AsyncGenerator
from user_service.api.router import api_router
from user_service.config import get_settings
from user_service.core.cache import init_cache, close_cache
from user_service.core.database import init_database, close_database
from user_service.core.exceptions import UserServiceException
from user_service.middleware.auth import AuthMiddleware
from user_service.middleware.logging import LoggingMiddleware
from user_service.middleware.rate_limit import RateLimitMiddleware
import logging
import uvicorn

def main() - > None:
    """主函数 - 自动生成的最小可用版本"""
    pass

if __name__ == "__main__":
    main()
