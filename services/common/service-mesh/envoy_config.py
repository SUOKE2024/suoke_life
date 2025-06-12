"""
envoy_config - 索克生活项目模块
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import yaml

#! / usr / bin / env python3
"""
Envoy配置管理器
提供对Envoy代理的配置管理支持
"""



logger = logging.getLogger(__name__)


@dataclass
class ClusterConfig:
    """Envoy集群配置"""

    name: str
    type: str = "STRICT_DNS"  # STATIC, STRICT_DNS, LOGICAL_DNS, EDS
    lb_policy: str = "ROUND_ROBIN"  # ROUND_ROBIN, LEAST_REQUEST, RING_HASH, RANDOM
    hosts: list[dict[str, Any]] = field(default_factory = list)
    health_checks: list[dict[str, Any]] = field(default_factory = list)
    circuit_breakers: dict[str, Any] | None = None
    outlier_detection: dict[str, Any] | None = None
    tls_context: dict[str, Any] | None = None

    def add_host(self, address: str, port: int):
        """添加主机"""
        self.hosts.append({"socket_address": {"address": address, "port_value": port}})

    def add_health_check(
        self,
        path: str = " / health",
        timeout: str = "5s",
        interval: str = "10s",
        unhealthy_threshold: int = 3,
        healthy_threshold: int = 2,
    ):
        """添加健康检查"""
        self.health_checks.append(
            {
                "timeout": timeout,
                "interval": interval,
                "unhealthy_threshold": unhealthy_threshold,
                "healthy_threshold": healthy_threshold,
                "http_health_check": {"path": path},
            }
        )

    def set_circuit_breaker(
        self,
        max_connections: int = 1024,
        max_pending_requests: int = 1024,
        max_requests: int = 1024,
        max_retries: int = 3,
    ):
        """设置熔断器"""
        self.circuit_breakers = {
            "thresholds": [
                {
                    "priority": "DEFAULT",
                    "max_connections": max_connections,
                    "max_pending_requests": max_pending_requests,
                    "max_requests": max_requests,
                    "max_retries": max_retries,
                }
            ]
        }

    def set_outlier_detection(
        self,
        consecutive_5xx: int = 5,
        interval: str = "30s",
        base_ejection_time: str = "30s",
        max_ejection_percent: int = 50,
    ):
        """设置异常检测"""
        self.outlier_detection = {
            "consecutive_5xx": consecutive_5xx,
            "interval": interval,
            "base_ejection_time": base_ejection_time,
            "max_ejection_percent": max_ejection_percent,
        }

    def to_envoy_config(self) -> dict[str, Any]:
        """转换为Envoy配置"""
        config = {
            "name": self.name,
            "type": self.type,
            "lb_policy": self.lb_policy,
            "load_assignment": {
                "cluster_name": self.name,
                "endpoints": [
                    {"lb_endpoints": [{"endpoint": host} for host in self.hosts]}
                ],
            },
        }

        if self.health_checks:
            config["health_checks"] = self.health_checks
        if self.circuit_breakers:
            config["circuit_breakers"] = self.circuit_breakers
        if self.outlier_detection:
            config["outlier_detection"] = self.outlier_detection
        if self.tls_context:
            config["transport_socket"] = {
                "name": "envoy.transport_sockets.tls",
                "typed_config": {
                    "@type": "type.googleapis.com / envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext",
                   ***self.tls_context,
                },
            }

        return config


@dataclass
class ListenerConfig:
    """Envoy监听器配置"""

    name: str
    address: str = "0.0.0.0"
    port: int = 8080
    filter_chains: list[dict[str, Any]] = field(default_factory = list)

    def add_http_filter_chain(
        self,
        route_config_name: str,
        domains: list[str] | None = None,
        filters: list[dict[str, Any]] | None = None,
    ):
        """添加HTTP过滤器链"""
        if domains is None:
            domains = [" * "]

        if filters is None:
            filters = []

        # 添加默认的HTTP连接管理器
        http_filters = [
            {
                "name": "envoy.filters.http.router",
                "typed_config": {
                    "@type": "type.googleapis.com / envoy.extensions.filters.http.router.v3.Router"
                },
            }
        ]

        # 添加自定义过滤器
        http_filters = filters + http_filters

        filter_chain = {
            "filters": [
                {
                    "name": "envoy.filters.network.http_connection_manager",
                    "typed_config": {
                        "@type": "type.googleapis.com / envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                        "stat_prefix": "ingress_http",
                        "route_config": {
                            "name": route_config_name,
                            "virtual_hosts": [
                                {
                                    "name": "local_service",
                                    "domains": domains,
                                    "routes": [
                                        {
                                            "match": {"prefix": " / "},
                                            "route": {"cluster": route_config_name},
                                        }
                                    ],
                                }
                            ],
                        },
                        "http_filters": http_filters,
                    },
                }
            ]
        }

        self.filter_chains.append(filter_chain)

    def to_envoy_config(self) -> dict[str, Any]:
        """转换为Envoy配置"""
        return {
            "name": self.name,
            "address": {
                "socket_address": {"address": self.address, "port_value": self.port}
            },
            "filter_chains": self.filter_chains,
        }


@dataclass
class RouteConfig:
    """Envoy路由配置"""

    name: str
    virtual_hosts: list[dict[str, Any]] = field(default_factory = list)

    def add_virtual_host(
        self, name: str, domains: list[str], routes: list[dict[str, Any]]
    ):
        """添加虚拟主机"""
        self.virtual_hosts.append({"name": name, "domains": domains, "routes": routes})

    def add_weighted_route(
        self,
        virtual_host_name: str,
        prefix: str,
        clusters: list[
            dict[str, Any]
        ],  # [{"name": "cluster1", "weight": 80}, {"name": "cluster2", "weight": 20}]
    ):
        """添加加权路由"""
        route = {
            "match": {"prefix": prefix},
            "route": {
                "weighted_clusters": {
                    "clusters": [
                        {"name": cluster["name"], "weight": cluster["weight"]}
                        for cluster in clusters
                    ]
                }
            },
        }

        # 查找虚拟主机并添加路由
        for vh in self.virtual_hosts:
            if vh["name"]==virtual_host_name:
                vh["routes"].append(route)
                break

    def to_envoy_config(self) -> dict[str, Any]:
        """转换为Envoy配置"""
        return {"name": self.name, "virtual_hosts": self.virtual_hosts}


class EnvoyConfigManager:
    """Envoy配置管理器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.clusters: dict[str, ClusterConfig] = {}
        self.listeners: dict[str, ListenerConfig] = {}
        self.routes: dict[str, RouteConfig] = {}

    def add_cluster(self, cluster: ClusterConfig):
        """添加集群配置"""
        self.clusters[cluster.name] = cluster
        logger.info(f"添加Envoy集群: {cluster.name}")

    def add_listener(self, listener: ListenerConfig):
        """添加监听器配置"""
        self.listeners[listener.name] = listener
        logger.info(f"添加Envoy监听器: {listener.name}")

    def add_route(self, route: RouteConfig):
        """添加路由配置"""
        self.routes[route.name] = route
        logger.info(f"添加Envoy路由: {route.name}")

    def generate_config(self) -> dict[str, Any]:
        """生成完整的Envoy配置"""
        config = {
            "static_resources": {
                "listeners": [
                    listener.to_envoy_config() for listener in self.listeners.values()
                ],
                "clusters": [
                    cluster.to_envoy_config() for cluster in self.clusters.values()
                ],
            },
            "admin": {
                "address": {
                    "socket_address": {"address": "0.0.0.0", "port_value": 9901}
                }
            },
        }

        return config

    def generate_json_config(self, indent: int = 2) -> str:
        """生成JSON格式的配置"""
        config = self.generate_config()
        return json.dumps(config, indent = indent)

    def generate_yaml_config(self) -> str:
        """生成YAML格式的配置"""
        config = self.generate_config()
        return yaml.dump(config, default_flow_style = False)

    def save_config(self, file_path: str, format: str = "yaml"):
        """保存配置到文件"""
        if format.lower()=="json":
            content = self.generate_json_config()
        elif format.lower()=="yaml":
            content = self.generate_yaml_config()
        else:
            raise ValueError("格式必须是 'json' 或 'yaml'")

        with open(file_path, "w", encoding = "utf - 8") as f:
            f.write(content)

        logger.info(f"Envoy配置已保存到: {file_path}")

    def create_health_service_config(
        self,
        service_name: str,
        hosts: list[tuple],  # [(address, port), ...]
        health_check_path: str = " / health",
    ) -> ClusterConfig:
        """创建健康服务配置（索克生活平台专用）"""
        cluster = ClusterConfig(
            name = f"{service_name} - cluster", type = "STRICT_DNS", lb_policy = "ROUND_ROBIN"
        )

        # 添加主机
        for address, port in hosts:
            cluster.add_host(address, port)

        # 添加健康检查
        cluster.add_health_check(path = health_check_path)

        # 设置熔断器
        cluster.set_circuit_breaker()

        # 设置异常检测
        cluster.set_outlier_detection()

        self.add_cluster(cluster)
        return cluster

    def create_canary_route_config(
        self,
        service_name: str,
        stable_cluster: str,
        canary_cluster: str,
        canary_weight: int = 10,
    ) -> RouteConfig:
        """创建金丝雀路由配置（索克生活平台专用）"""
        route = RouteConfig(name = f"{service_name} - route")

        # 添加虚拟主机
        route.add_virtual_host(
            name = f"{service_name} - vh", domains = [f"{service_name}.local", " * "], routes = []
        )

        # 添加加权路由
        route.add_weighted_route(
            virtual_host_name = f"{service_name} - vh",
            prefix = " / ",
            clusters = [
                {"name": stable_cluster, "weight": 100 - canary_weight},
                {"name": canary_cluster, "weight": canary_weight},
            ],
        )

        self.add_route(route)
        return route

    def create_rate_limit_filter(
        self, requests_per_second: int = 100, burst_size: int = 200
    ) -> dict[str, Any]:
        """创建限流过滤器配置"""
        return {
            "name": "envoy.filters.http.local_ratelimit",
            "typed_config": {
                "@type": "type.googleapis.com / udpa.type.v1.TypedStruct",
                "type_url": "type.googleapis.com / envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit",
                "value": {
                    "stat_prefix": "local_rate_limiter",
                    "token_bucket": {
                        "max_tokens": burst_size,
                        "tokens_per_fill": requests_per_second,
                        "fill_interval": "1s",
                    },
                    "filter_enabled": {
                        "runtime_key": "local_rate_limit_enabled",
                        "default_value": {"numerator": 100, "denominator": "HUNDRED"},
                    },
                    "filter_enforced": {
                        "runtime_key": "local_rate_limit_enforced",
                        "default_value": {"numerator": 100, "denominator": "HUNDRED"},
                    },
                },
            },
        }
