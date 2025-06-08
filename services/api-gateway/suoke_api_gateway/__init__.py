from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .core.app import create_app
from .core.config import Settings, get_settings
from .models.gateway import GatewayRequest, GatewayResponse

"""
索克生活 API 网关服务

一个现代化的微服务 API 网关，提供统一的服务入口、路由管理、
认证授权、限流熔断、监控日志等功能。

支持 REST API 和 gRPC 双协议，为索克生活健康管理平台
提供高性能、高可用的网关服务。
"""

__version__ = "0.1.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suoke.life"


__all__ = [
    "create_app",
    "Settings",
    "get_settings",
    "GatewayRequest",
    "GatewayResponse",
]