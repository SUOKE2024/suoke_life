from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .analysis import router as analysis_router
from .health import router as health_router
from fastapi import APIRouter

"""API routes for look service."""



# Main API router
api_router = APIRouter()

# Include sub - routers
api_router.include_router(health_router, prefix = " / health", tags = ["health"])
api_router.include_router(analysis_router, prefix = " / analysis", tags = ["analysis"])

__all__ = ["api_router"]
