from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .main import create_app
from .routes import router

"""
API 层
API Layer

提供 RESTful API 和 WebSocket 接口
"""


__all__ = ["create_app", "router"]
