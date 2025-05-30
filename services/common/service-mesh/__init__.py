#!/usr/bin/env python3
"""
服务网格支持模块
提供Istio、Linkerd等服务网格的集成支持
"""

from .envoy_config import ClusterConfig, EnvoyConfigManager, ListenerConfig, RouteConfig
from .istio_client import (
    DestinationRule,
    Gateway,
    IstioClient,
    ServiceEntry,
    VirtualService,
)
from .linkerd_client import LinkerdClient, ServiceProfile, TrafficSplit
from .mesh_manager import (
    MeshConfig,
    SecurityPolicy,
    ServiceMeshManager,
    TrafficPolicy,
    get_mesh_manager,
)

__all__ = [
    "ClusterConfig",
    "DestinationRule",
    # Envoy配置
    "EnvoyConfigManager",
    "Gateway",
    # Istio支持
    "IstioClient",
    # Linkerd支持
    "LinkerdClient",
    "ListenerConfig",
    "MeshConfig",
    "RouteConfig",
    "SecurityPolicy",
    "ServiceEntry",
    # 网格管理
    "ServiceMeshManager",
    "ServiceProfile",
    "TrafficPolicy",
    "TrafficSplit",
    "VirtualService",
    "get_mesh_manager",
]
