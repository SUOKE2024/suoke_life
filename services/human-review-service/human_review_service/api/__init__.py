"""
API 层
API Layer

提供 RESTful API 和 WebSocket 接口
"""

from .main import create_app
from .routes import router

__all__ = ["create_app", "router"] 