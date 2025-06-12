"""Kubernetes客户端工具"""

import asyncio
from typing import Any, Dict, List, Optional

import structlog
from kubernetes import client
from kubernetes.client.rest import ApiException

logger = structlog.get_logger(__name__)


class KubernetesClient:
    """Kubernetes客户端封装"""

    def __init__(self, namespace: str = "suoke-life") -> None:
        """初始化Kubernetes客户端

        Args:
            namespace: Kubernetes命名空间
        """
        self.namespace = namespace
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()

    async def start(self) -> None:
        """启动Kubernetes客户端"""
        # Kubernetes客户端不需要特殊的启动逻辑
        pass

    async def shutdown(self) -> None:
        """关闭Kubernetes客户端"""
        # Kubernetes客户端不需要特殊的关闭逻辑
        pass

    async def create_deployment(
        self,
        name: str,
        image: str,
        replicas: int = 1,
        resources: Optional[Dict[str, Any]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> client.V1Deployment:
        """创建Deployment

        Args:
            name: 部署名称
            image: 容器镜像
            replicas: 副本数
            resources: 资源配置
            env_vars: 环境变量
            labels: 标签

        Returns:
            创建的Deployment对象
        """
        try:
            # 构建容器配置
            container = client.V1Container(
                name=name,
                image=image,
                ports=[client.V1ContainerPort(container_port=8080)],
                env=[
                    client.V1EnvVar(name=k, value=v)
                    for k, v in (env_vars or {}).items()
                ],
                resources=self._build_resource_requirements(resources),
                liveness_probe=client.V1Probe(
                    http_get=client.V1HTTPGetAction(path="/health/live", port=8080),
                    initial_delay_seconds=30,
                    period_seconds=10,
                ),
                readiness_probe=client.V1Probe(
                    http_get=client.V1HTTPGetAction(path="/health/ready", port=8080),
                    initial_delay_seconds=10,
                    period_seconds=5,
                ),
            )

            # 构建Pod模板
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels or {"app": name}),
                spec=client.V1PodSpec(containers=[container]),
            )

            # 构建Deployment规格
            spec = client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels=labels or {"app": name}),
                template=template,
            )

            # 构建Deployment对象
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(
                    name=name, namespace=self.namespace, labels=labels or {"app": name}
                ),
                spec=spec,
            )

            # 创建Deployment
            result = await asyncio.to_thread(
                self.apps_v1.create_namespaced_deployment,
                namespace=self.namespace,
                body=deployment,
            )

            logger.info("Deployment创建成功", name=name, namespace=self.namespace)
            return result

        except ApiException as e:
            logger.error("创建Deployment失败", name=name, error=str(e))
            raise

    async def create_service(
        self,
        name: str,
        selector: Dict[str, str],
        port: int = 8080,
        target_port: int = 8080,
        service_type: str = "ClusterIP",
    ) -> client.V1Service:
        """创建Service

        Args:
            name: 服务名称
            selector: 选择器
            port: 服务端口
            target_port: 目标端口
            service_type: 服务类型

        Returns:
            创建的Service对象
        """
        try:
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
                spec=client.V1ServiceSpec(
                    selector=selector,
                    ports=[
                        client.V1ServicePort(
                            port=port, target_port=target_port, protocol="TCP"
                        )
                    ],
                    type=service_type,
                ),
            )

            result = await asyncio.to_thread(
                self.core_v1.create_namespaced_service,
                namespace=self.namespace,
                body=service,
            )

            logger.info("Service创建成功", name=name, namespace=self.namespace)
            return result

        except ApiException as e:
            logger.error("创建Service失败", name=name, error=str(e))
            raise

    async def create_hpa(
        self,
        name: str,
        target_name: str,
        min_replicas: int = 1,
        max_replicas: int = 5,
        target_cpu_utilization: int = 70,
    ) -> client.V1HorizontalPodAutoscaler:
        """创建HorizontalPodAutoscaler

        Args:
            name: HPA名称
            target_name: 目标Deployment名称
            min_replicas: 最小副本数
            max_replicas: 最大副本数
            target_cpu_utilization: 目标CPU使用率

        Returns:
            创建的HPA对象
        """
        try:
            hpa = client.V1HorizontalPodAutoscaler(
                api_version="autoscaling/v1",
                kind="HorizontalPodAutoscaler",
                metadata=client.V1ObjectMeta(name=name, namespace=self.namespace),
                spec=client.V1HorizontalPodAutoscalerSpec(
                    scale_target_ref=client.V1CrossVersionObjectReference(
                        api_version="apps/v1", kind="Deployment", name=target_name
                    ),
                    min_replicas=min_replicas,
                    max_replicas=max_replicas,
                    target_cpu_utilization_percentage=target_cpu_utilization,
                ),
            )

            result = await asyncio.to_thread(
                self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler,
                namespace=self.namespace,
                body=hpa,
            )

            logger.info("HPA创建成功", name=name, namespace=self.namespace)
            return result

        except ApiException as e:
            logger.error("创建HPA失败", name=name, error=str(e))
            raise

    async def get_deployment(self, name: str) -> Optional[client.V1Deployment]:
        """获取Deployment

        Args:
            name: Deployment名称

        Returns:
            Deployment对象或None
        """
        try:
            result = await asyncio.to_thread(
                self.apps_v1.read_namespaced_deployment,
                name=name,
                namespace=self.namespace,
            )
            return result
        except ApiException as e:
            if e.status==404:
                return None
            logger.error("获取Deployment失败", name=name, error=str(e))
            raise

    async def scale_deployment(self, name: str, replicas: int) -> client.V1Deployment:
        """扩缩容Deployment

        Args:
            name: Deployment名称
            replicas: 目标副本数

        Returns:
            更新后的Deployment对象
        """
        try:
            # 获取当前Deployment
            deployment = await self.get_deployment(name)
            if not deployment:
                raise ValueError(f"Deployment {name} 不存在")

            # 更新副本数
            deployment.spec.replicas = replicas

            result = await asyncio.to_thread(
                self.apps_v1.patch_namespaced_deployment,
                name=name,
                namespace=self.namespace,
                body=deployment,
            )

            logger.info("Deployment扩缩容成功", name=name, replicas=replicas)
            return result

        except ApiException as e:
            logger.error("扩缩容Deployment失败", name=name, error=str(e))
            raise

    async def delete_deployment(self, name: str) -> None:
        """删除Deployment

        Args:
            name: Deployment名称
        """
        try:
            await asyncio.to_thread(
                self.apps_v1.delete_namespaced_deployment,
                name=name,
                namespace=self.namespace,
            )
            logger.info("Deployment删除成功", name=name, namespace=self.namespace)
        except ApiException as e:
            if e.status!=404:
                logger.error("删除Deployment失败", name=name, error=str(e))
                raise

    async def delete_service(self, name: str) -> None:
        """删除Service

        Args:
            name: Service名称
        """
        try:
            await asyncio.to_thread(
                self.core_v1.delete_namespaced_service,
                name=name,
                namespace=self.namespace,
            )
            logger.info("Service删除成功", name=name, namespace=self.namespace)
        except ApiException as e:
            if e.status!=404:
                logger.error("删除Service失败", name=name, error=str(e))
                raise

    async def delete_hpa(self, name: str) -> None:
        """删除HPA

        Args:
            name: HPA名称
        """
        try:
            await asyncio.to_thread(
                self.autoscaling_v1.delete_namespaced_horizontal_pod_autoscaler,
                name=name,
                namespace=self.namespace,
            )
            logger.info("HPA删除成功", name=name, namespace=self.namespace)
        except ApiException as e:
            if e.status!=404:
                logger.error("删除HPA失败", name=name, error=str(e))
                raise

    async def list_deployments(self, label_selector: Optional[str] = None) -> List[Any]:
        """列出Deployments

        Args:
            label_selector: 标签选择器

        Returns:
            Deployment列表
        """
        try:
            result = await asyncio.to_thread(
                self.apps_v1.list_namespaced_deployment,
                namespace=self.namespace,
                label_selector=label_selector,
            )
            return result.items  # type: ignore
        except ApiException as e:
            logger.error("列出Deployments失败", error=str(e))
            raise

    def _build_resource_requirements(
        self, resources: Optional[Dict[str, Any]]
    ) -> Optional[client.V1ResourceRequirements]:
        """构建资源需求配置

        Args:
            resources: 资源配置

        Returns:
            资源需求对象
        """
        if not resources:
            return None

        requests = {}
        limits = {}

        # CPU配置
        if "cpu" in resources:
            requests["cpu"] = resources["cpu"]
            limits["cpu"] = resources.get("cpu_limit", resources["cpu"])

        # 内存配置
        if "memory" in resources:
            requests["memory"] = resources["memory"]
            limits["memory"] = resources.get("memory_limit", resources["memory"])

        # GPU配置
        if "nvidia.com/gpu" in resources:
            gpu_count = resources["nvidia.com/gpu"]
            if gpu_count and int(gpu_count) > 0:
                requests["nvidia.com/gpu"] = gpu_count
                limits["nvidia.com/gpu"] = gpu_count

        return client.V1ResourceRequirements(
            requests=requests if requests else None, limits=limits if limits else None
        )
