"""
linkerd_client - 索克生活项目模块
"""

    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
from dataclasses import dataclass, field
from typing import Any
import logging

#!/usr/bin/env python3
"""
Linkerd客户端
提供对Linkerd服务网格的支持
"""


try:

    HAS_KUBERNETES = True
except ImportError:
    HAS_KUBERNETES = False

logger = logging.getLogger(__name__)


@dataclass
class TrafficSplit:
    """Linkerd流量分割"""

    name: str
    namespace: str = "default"
    service: str = ""
    backends: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def add_backend(self, service: str, weight: int, subset: str | None = None):
        """添加后端服务"""
        backend = {"service": service, "weight": weight}

        if subset:
            backend["subset"] = subset

        self.backends.append(backend)

    def to_k8s_manifest(self) -> dict[str, Any]:
        """转换为Kubernetes清单"""
        spec = {"service": self.service, "backends": self.backends}

        return {
            "apiVersion": "split.smi-spec.io/v1alpha1",
            "kind": "TrafficSplit",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": self.labels,
                "annotations": self.annotations,
            },
            "spec": spec,
        }


@dataclass
class ServiceProfile:
    """Linkerd服务配置"""

    name: str
    namespace: str = "default"
    routes: list[dict[str, Any]] = field(default_factory=list)
    retry_budget: dict[str, Any] | None = None
    dst_overrides: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def add_route(
        self,
        name: str,
        condition: dict[str, Any],
        timeout: str | None = None,
        retry_budget: dict[str, Any] | None = None,
        response_classes: list[dict[str, Any]] | None = None,
    ):
        """添加路由"""
        route = {"name": name, "condition": condition}

        if timeout:
            route["timeout"] = timeout
        if retry_budget:
            route["retryBudget"] = retry_budget
        if response_classes:
            route["responseClasses"] = response_classes

        self.routes.append(route)

    def to_k8s_manifest(self) -> dict[str, Any]:
        """转换为Kubernetes清单"""
        spec = {}

        if self.routes:
            spec["routes"] = self.routes
        if self.retry_budget:
            spec["retryBudget"] = self.retry_budget
        if self.dst_overrides:
            spec["dstOverrides"] = self.dst_overrides

        return {
            "apiVersion": "linkerd.io/v1alpha2",
            "kind": "ServiceProfile",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": self.labels,
                "annotations": self.annotations,
            },
            "spec": spec,
        }


class LinkerdClient:
    """Linkerd客户端"""

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

    async def create_traffic_split(self, traffic_split: TrafficSplit) -> bool:
        """创建流量分割"""
        try:
            manifest = traffic_split.to_k8s_manifest()

            self.custom_api.create_namespaced_custom_object(
                group="split.smi-spec.io",
                version="v1alpha1",
                namespace=traffic_split.namespace,
                plural="trafficsplits",
                body=manifest,
            )

            logger.info(f"创建流量分割成功: {traffic_split.name}")
            return True

        except ApiException as e:
            logger.error(f"创建流量分割失败: {e}")
            return False

    async def create_service_profile(self, service_profile: ServiceProfile) -> bool:
        """创建服务配置"""
        try:
            manifest = service_profile.to_k8s_manifest()

            self.custom_api.create_namespaced_custom_object(
                group="linkerd.io",
                version="v1alpha2",
                namespace=service_profile.namespace,
                plural="serviceprofiles",
                body=manifest,
            )

            logger.info(f"创建服务配置成功: {service_profile.name}")
            return True

        except ApiException as e:
            logger.error(f"创建服务配置失败: {e}")
            return False

    async def get_traffic_split(
        self, name: str, namespace: str = "default"
    ) -> dict[str, Any] | None:
        """获取流量分割"""
        try:
            result = self.custom_api.get_namespaced_custom_object(
                group="split.smi-spec.io",
                version="v1alpha1",
                namespace=namespace,
                plural="trafficsplits",
                name=name,
            )

            return result

        except ApiException as e:
            if e.status == 404:
                return None
            logger.error(f"获取流量分割失败: {e}")
            return None

    async def update_traffic_split(self, traffic_split: TrafficSplit) -> bool:
        """更新流量分割"""
        try:
            manifest = traffic_split.to_k8s_manifest()

            self.custom_api.patch_namespaced_custom_object(
                group="split.smi-spec.io",
                version="v1alpha1",
                namespace=traffic_split.namespace,
                plural="trafficsplits",
                name=traffic_split.name,
                body=manifest,
            )

            logger.info(f"更新流量分割成功: {traffic_split.name}")
            return True

        except ApiException as e:
            logger.error(f"更新流量分割失败: {e}")
            return False

    async def delete_traffic_split(self, name: str, namespace: str = "default") -> bool:
        """删除流量分割"""
        try:
            self.custom_api.delete_namespaced_custom_object(
                group="split.smi-spec.io",
                version="v1alpha1",
                namespace=namespace,
                plural="trafficsplits",
                name=name,
            )

            logger.info(f"删除流量分割成功: {name}")
            return True

        except ApiException as e:
            logger.error(f"删除流量分割失败: {e}")
            return False
