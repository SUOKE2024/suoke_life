"""
istio_client - 索克生活项目模块
"""

    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
from dataclasses import dataclass, field
from typing import Any
import logging

#!/usr/bin/env python3
"""
Istio客户端
提供对Istio服务网格的支持
"""


try:

    HAS_KUBERNETES = True
except ImportError:
    HAS_KUBERNETES = False

logger = logging.getLogger(__name__)


@dataclass
class VirtualService:
    """Istio虚拟服务"""

    name: str
    namespace: str = "default"
    hosts: list[str] = field(default_factory=list)
    gateways: list[str] = field(default_factory=list)
    http_routes: list[dict[str, Any]] = field(default_factory=list)
    tcp_routes: list[dict[str, Any]] = field(default_factory=list)
    tls_routes: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def add_http_route(
        self,
        match: list[dict[str, Any]],
        route: list[dict[str, Any]],
        fault: dict[str, Any] | None = None,
        timeout: str | None = None,
        retries: dict[str, Any] | None = None,
        mirror: dict[str, Any] | None = None,
    ):
        """添加HTTP路由"""
        http_route = {"match": match, "route": route}

        if fault:
            http_route["fault"] = fault
        if timeout:
            http_route["timeout"] = timeout
        if retries:
            http_route["retries"] = retries
        if mirror:
            http_route["mirror"] = mirror

        self.http_routes.append(http_route)

    def to_k8s_manifest(self) -> dict[str, Any]:
        """转换为Kubernetes清单"""
        spec = {}

        if self.hosts:
            spec["hosts"] = self.hosts
        if self.gateways:
            spec["gateways"] = self.gateways
        if self.http_routes:
            spec["http"] = self.http_routes
        if self.tcp_routes:
            spec["tcp"] = self.tcp_routes
        if self.tls_routes:
            spec["tls"] = self.tls_routes

        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": self.labels,
                "annotations": self.annotations,
            },
            "spec": spec,
        }


@dataclass
class DestinationRule:
    """Istio目标规则"""

    name: str
    namespace: str = "default"
    host: str = ""
    traffic_policy: dict[str, Any] | None = None
    port_level_settings: list[dict[str, Any]] = field(default_factory=list)
    subsets: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def add_subset(
        self,
        name: str,
        labels: dict[str, str],
        traffic_policy: dict[str, Any] | None = None,
    ):
        """添加子集"""
        subset = {"name": name, "labels": labels}

        if traffic_policy:
            subset["trafficPolicy"] = traffic_policy

        self.subsets.append(subset)

    def set_load_balancer(
        self,
        simple: str | None = None,
        consistent_hash: dict[str, Any] | None = None,
    ):
        """设置负载均衡策略"""
        if not self.traffic_policy:
            self.traffic_policy = {}

        load_balancer = {}
        if simple:
            load_balancer["simple"] = simple
        if consistent_hash:
            load_balancer["consistentHash"] = consistent_hash

        self.traffic_policy["loadBalancer"] = load_balancer

    def set_circuit_breaker(
        self,
        consecutive_errors: int | None = None,
        interval: str | None = None,
        base_ejection_time: str | None = None,
        max_ejection_percent: int | None = None,
    ):
        """设置熔断器"""
        if not self.traffic_policy:
            self.traffic_policy = {}

        outlier_detection = {}
        if consecutive_errors:
            outlier_detection["consecutiveErrors"] = consecutive_errors
        if interval:
            outlier_detection["interval"] = interval
        if base_ejection_time:
            outlier_detection["baseEjectionTime"] = base_ejection_time
        if max_ejection_percent:
            outlier_detection["maxEjectionPercent"] = max_ejection_percent

        self.traffic_policy["outlierDetection"] = outlier_detection

    def to_k8s_manifest(self) -> dict[str, Any]:
        """转换为Kubernetes清单"""
        spec = {"host": self.host}

        if self.traffic_policy:
            spec["trafficPolicy"] = self.traffic_policy
        if self.port_level_settings:
            spec["portLevelSettings"] = self.port_level_settings
        if self.subsets:
            spec["subsets"] = self.subsets

        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": self.labels,
                "annotations": self.annotations,
            },
            "spec": spec,
        }


@dataclass
class Gateway:
    """Istio网关"""

    name: str
    namespace: str = "default"
    selector: dict[str, str] = field(default_factory=dict)
    servers: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def add_server(
        self,
        port: dict[str, Any],
        hosts: list[str],
        tls: dict[str, Any] | None = None,
    ):
        """添加服务器配置"""
        server = {"port": port, "hosts": hosts}

        if tls:
            server["tls"] = tls

        self.servers.append(server)

    def to_k8s_manifest(self) -> dict[str, Any]:
        """转换为Kubernetes清单"""
        spec = {"selector": self.selector, "servers": self.servers}

        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": self.labels,
                "annotations": self.annotations,
            },
            "spec": spec,
        }


@dataclass
class ServiceEntry:
    """Istio服务条目"""

    name: str
    namespace: str = "default"
    hosts: list[str] = field(default_factory=list)
    ports: list[dict[str, Any]] = field(default_factory=list)
    location: str = "MESH_EXTERNAL"
    resolution: str = "DNS"
    addresses: list[str] = field(default_factory=list)
    endpoints: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def to_k8s_manifest(self) -> dict[str, Any]:
        """转换为Kubernetes清单"""
        spec = {
            "hosts": self.hosts,
            "ports": self.ports,
            "location": self.location,
            "resolution": self.resolution,
        }

        if self.addresses:
            spec["addresses"] = self.addresses
        if self.endpoints:
            spec["endpoints"] = self.endpoints

        return {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "ServiceEntry",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": self.labels,
                "annotations": self.annotations,
            },
            "spec": spec,
        }


class IstioClient:
    """Istio客户端"""

    def __init__(self, kubeconfig_path: str | None = None, context: str | None = None):
        if not HAS_KUBERNETES:
            raise ImportError("kubernetes未安装，请安装: pip install kubernetes")

        # 加载Kubernetes配置
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path, context=context)
        else:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config(context=context)

        # 创建API客户端
        self.api_client = client.ApiClient()
        self.custom_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()

        # Istio API组和版本
        self.group = "networking.istio.io"
        self.version = "v1beta1"

    async def create_virtual_service(self, virtual_service: VirtualService) -> bool:
        """创建虚拟服务"""
        try:
            manifest = virtual_service.to_k8s_manifest()

            self.custom_api.create_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=virtual_service.namespace,
                plural="virtualservices",
                body=manifest,
            )

            logger.info(f"创建虚拟服务成功: {virtual_service.name}")
            return True

        except ApiException as e:
            logger.error(f"创建虚拟服务失败: {e}")
            return False

    async def get_virtual_service(
        self, name: str, namespace: str = "default"
    ) -> dict[str, Any] | None:
        """获取虚拟服务"""
        try:
            result = self.custom_api.get_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=namespace,
                plural="virtualservices",
                name=name,
            )

            return result

        except ApiException as e:
            if e.status == 404:
                return None
            logger.error(f"获取虚拟服务失败: {e}")
            return None

    async def update_virtual_service(self, virtual_service: VirtualService) -> bool:
        """更新虚拟服务"""
        try:
            manifest = virtual_service.to_k8s_manifest()

            self.custom_api.patch_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=virtual_service.namespace,
                plural="virtualservices",
                name=virtual_service.name,
                body=manifest,
            )

            logger.info(f"更新虚拟服务成功: {virtual_service.name}")
            return True

        except ApiException as e:
            logger.error(f"更新虚拟服务失败: {e}")
            return False

    async def delete_virtual_service(
        self, name: str, namespace: str = "default"
    ) -> bool:
        """删除虚拟服务"""
        try:
            self.custom_api.delete_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=namespace,
                plural="virtualservices",
                name=name,
            )

            logger.info(f"删除虚拟服务成功: {name}")
            return True

        except ApiException as e:
            logger.error(f"删除虚拟服务失败: {e}")
            return False

    async def create_destination_rule(self, destination_rule: DestinationRule) -> bool:
        """创建目标规则"""
        try:
            manifest = destination_rule.to_k8s_manifest()

            self.custom_api.create_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=destination_rule.namespace,
                plural="destinationrules",
                body=manifest,
            )

            logger.info(f"创建目标规则成功: {destination_rule.name}")
            return True

        except ApiException as e:
            logger.error(f"创建目标规则失败: {e}")
            return False

    async def create_gateway(self, gateway: Gateway) -> bool:
        """创建网关"""
        try:
            manifest = gateway.to_k8s_manifest()

            self.custom_api.create_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=gateway.namespace,
                plural="gateways",
                body=manifest,
            )

            logger.info(f"创建网关成功: {gateway.name}")
            return True

        except ApiException as e:
            logger.error(f"创建网关失败: {e}")
            return False

    async def create_service_entry(self, service_entry: ServiceEntry) -> bool:
        """创建服务条目"""
        try:
            manifest = service_entry.to_k8s_manifest()

            self.custom_api.create_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=service_entry.namespace,
                plural="serviceentries",
                body=manifest,
            )

            logger.info(f"创建服务条目成功: {service_entry.name}")
            return True

        except ApiException as e:
            logger.error(f"创建服务条目失败: {e}")
            return False

    async def list_virtual_services(
        self, namespace: str | None = None
    ) -> list[dict[str, Any]]:
        """列出虚拟服务"""
        try:
            if namespace:
                result = self.custom_api.list_namespaced_custom_object(
                    group=self.group,
                    version=self.version,
                    namespace=namespace,
                    plural="virtualservices",
                )
            else:
                result = self.custom_api.list_cluster_custom_object(
                    group=self.group, version=self.version, plural="virtualservices"
                )

            return result.get("items", [])

        except ApiException as e:
            logger.error(f"列出虚拟服务失败: {e}")
            return []

    def create_canary_deployment(
        self,
        service_name: str,
        namespace: str,
        stable_version: str,
        canary_version: str,
        canary_weight: int = 10,
    ) -> tuple[VirtualService, DestinationRule]:
        """创建金丝雀部署配置"""
        # 创建目标规则
        destination_rule = DestinationRule(
            name=f"{service_name}-destination", namespace=namespace, host=service_name
        )

        # 添加稳定版本子集
        destination_rule.add_subset(name="stable", labels={"version": stable_version})

        # 添加金丝雀版本子集
        destination_rule.add_subset(name="canary", labels={"version": canary_version})

        # 创建虚拟服务
        virtual_service = VirtualService(
            name=f"{service_name}-virtual", namespace=namespace, hosts=[service_name]
        )

        # 添加HTTP路由
        virtual_service.add_http_route(
            match=[{"uri": {"prefix": "/"}}],
            route=[
                {
                    "destination": {"host": service_name, "subset": "stable"},
                    "weight": 100 - canary_weight,
                },
                {
                    "destination": {"host": service_name, "subset": "canary"},
                    "weight": canary_weight,
                },
            ],
        )

        return virtual_service, destination_rule

    def create_circuit_breaker(
        self,
        service_name: str,
        namespace: str,
        consecutive_errors: int = 5,
        interval: str = "30s",
        base_ejection_time: str = "30s",
        max_ejection_percent: int = 50,
    ) -> DestinationRule:
        """创建熔断器配置"""
        destination_rule = DestinationRule(
            name=f"{service_name}-circuit-breaker",
            namespace=namespace,
            host=service_name,
        )

        destination_rule.set_circuit_breaker(
            consecutive_errors=consecutive_errors,
            interval=interval,
            base_ejection_time=base_ejection_time,
            max_ejection_percent=max_ejection_percent,
        )

        return destination_rule
