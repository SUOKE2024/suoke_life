#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务注册与发现模块
提供服务注册、发现、健康检查等功能
"""

from .service_registry import (
    ServiceInstance,
    ServiceConfig,
    ServiceStatus,
    ServiceRegistry,
    InMemoryServiceRegistry,
    ServiceDiscovery,
    get_service_registry,
    get_service_discovery
)

__all__ = [
    'ServiceInstance',
    'ServiceConfig',
    'ServiceStatus',
    'ServiceRegistry',
    'InMemoryServiceRegistry',
    'ServiceDiscovery',
    'get_service_registry',
    'get_service_discovery'
] 