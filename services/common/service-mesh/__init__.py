#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务网格支持模块
提供Istio、Linkerd等服务网格的集成支持
"""

from .istio_client import (
    IstioClient,
    VirtualService,
    DestinationRule,
    Gateway,
    ServiceEntry
)

from .linkerd_client import (
    LinkerdClient,
    TrafficSplit,
    ServiceProfile
)

from .envoy_config import (
    EnvoyConfigManager,
    ClusterConfig,
    ListenerConfig,
    RouteConfig
)

from .mesh_manager import (
    ServiceMeshManager,
    MeshConfig,
    TrafficPolicy,
    SecurityPolicy,
    get_mesh_manager
)

__all__ = [
    # Istio支持
    'IstioClient',
    'VirtualService',
    'DestinationRule',
    'Gateway',
    'ServiceEntry',
    
    # Linkerd支持
    'LinkerdClient',
    'TrafficSplit',
    'ServiceProfile',
    
    # Envoy配置
    'EnvoyConfigManager',
    'ClusterConfig',
    'ListenerConfig',
    'RouteConfig',
    
    # 网格管理
    'ServiceMeshManager',
    'MeshConfig',
    'TrafficPolicy',
    'SecurityPolicy',
    'get_mesh_manager'
] 