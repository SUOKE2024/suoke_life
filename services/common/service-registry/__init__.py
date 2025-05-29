#!/usr/bin/env python3
"""
服务注册与发现模块
提供服务注册、发现、健康检查等功能
"""

from .service_registry import (
    InMemoryServiceRegistry,
    ServiceConfig,
    ServiceDiscovery,
    ServiceInstance,
    ServiceRegistry,
    ServiceStatus,
    get_service_discovery,
    get_service_registry,
)

__all__ = [
    "InMemoryServiceRegistry",
    "ServiceConfig",
    "ServiceDiscovery",
    "ServiceInstance",
    "ServiceRegistry",
    "ServiceStatus",
    "get_service_discovery",
    "get_service_registry",
]
