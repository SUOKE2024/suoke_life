"""模型部署器"""

import time
import uuid

import structlog

from ..models.config import ModelConfig
from ..models.deployment import DeploymentInfo, DeploymentStatus
from ..utils.k8s import KubernetesClient

logger = structlog.get_logger(__name__)


class ModelDeployer:
    """模型部署器"""

    def __init__(self, k8s_client: KubernetesClient) -> None:
        """初始化模型部署器

        Args:
            k8s_client: Kubernetes客户端
        """
        self.k8s_client = k8s_client

    async def deploy(self, model_config: ModelConfig) -> DeploymentInfo:
        """部署模型到Kubernetes集群

        Args:
            model_config: 模型配置

        Returns:
            部署信息
        """
        deployment_id = f"{model_config.model_id}-{uuid.uuid4().hex[:8]}"

        try:
            logger.info(
                "开始部署模型",
                model_id=model_config.model_id,
                deployment_id=deployment_id,
            )

            # 准备部署参数
            labels = {
                "app": deployment_id,
                "model-id": model_config.model_id,
                "model-type": model_config.model_type.value,
                "version": model_config.version,
                "managed-by": "ai-model-service",
            }

            # 创建Deployment
            await self.k8s_client.create_deployment(
                name=deployment_id,
                image=model_config.docker_image,
                replicas=model_config.scaling_config.get("min_replicas", 1),
                resources=model_config.resource_requirements,
                env_vars=model_config.environment_variables,
                labels=labels,
            )

            # 创建Service
            await self.k8s_client.create_service(
                name=deployment_id,
                selector={"app": deployment_id},
                port=8080,
                target_port=8080,
            )

            # 创建HPA（如果配置了扩缩容）
            scaling_config = model_config.scaling_config
            if scaling_config.get("max_replicas", 1) > 1:
                await self.k8s_client.create_hpa(
                    name=deployment_id,
                    target_name=deployment_id,
                    min_replicas=scaling_config.get("min_replicas", 1),
                    max_replicas=scaling_config.get("max_replicas", 5),
                    target_cpu_utilization=scaling_config.get(
                        "target_cpu_utilization", 70
                    ),
                )

            # 构建端点URL
            endpoint_url = f"http://{deployment_id}.{self.k8s_client.namespace}.svc.cluster.local:8080"

            # 创建部署信息
            deployment_info = DeploymentInfo(
                deployment_id=deployment_id,
                model_id=model_config.model_id,
                status=DeploymentStatus.DEPLOYING,
                replicas=scaling_config.get("min_replicas", 1),
                ready_replicas=0,
                endpoint_url=endpoint_url,
                created_at=time.time(),
                updated_at=time.time(),
                resource_usage={},
                performance_metrics={},
            )

            logger.info(
                "模型部署已启动",
                model_id=model_config.model_id,
                deployment_id=deployment_id,
            )
            return deployment_info

        except Exception as e:
            logger.error("模型部署失败", model_id=model_config.model_id, error=str(e))
            # 清理已创建的资源
            await self._cleanup_deployment(deployment_id)
            raise

    async def scale(self, deployment_id: str, replicas: int) -> None:
        """扩缩容模型部署

        Args:
            deployment_id: 部署ID
            replicas: 目标副本数
        """
        try:
            logger.info(
                "扩缩容模型部署", deployment_id=deployment_id, replicas=replicas
            )

            await self.k8s_client.scale_deployment(deployment_id, replicas)

            logger.info(
                "模型部署扩缩容完成", deployment_id=deployment_id, replicas=replicas
            )

        except Exception as e:
            logger.error(
                "模型部署扩缩容失败", deployment_id=deployment_id, error=str(e)
            )
            raise

    async def delete(self, deployment_id: str) -> None:
        """删除模型部署

        Args:
            deployment_id: 部署ID
        """
        try:
            logger.info("删除模型部署", deployment_id=deployment_id)

            await self._cleanup_deployment(deployment_id)

            logger.info("模型部署删除完成", deployment_id=deployment_id)

        except Exception as e:
            logger.error("删除模型部署失败", deployment_id=deployment_id, error=str(e))
            raise

    async def _cleanup_deployment(self, deployment_id: str) -> None:
        """清理部署资源

        Args:
            deployment_id: 部署ID
        """
        try:
            # 删除HPA
            await self.k8s_client.delete_hpa(deployment_id)
        except Exception as e:
            logger.warning("删除HPA失败", deployment_id=deployment_id, error=str(e))

        try:
            # 删除Service
            await self.k8s_client.delete_service(deployment_id)
        except Exception as e:
            logger.warning("删除Service失败", deployment_id=deployment_id, error=str(e))

        try:
            # 删除Deployment
            await self.k8s_client.delete_deployment(deployment_id)
        except Exception as e:
            logger.warning(
                "删除Deployment失败", deployment_id=deployment_id, error=str(e)
            )
