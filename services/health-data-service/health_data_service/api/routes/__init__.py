"""API路由模块"""

from .health_data import router as health_data_router

__all__ = [
    "health_data_router",
]
