"""Prometheus指标收集器"""

import time
from typing import Dict, Optional

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


class MetricsCollector:
    """Prometheus指标收集器"""

    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        """初始化指标收集器

        Args:
            registry: Prometheus注册表
        """
        self.registry = registry or CollectorRegistry()

        # 部署相关指标
        self.deployments_total = Counter(
            "ai_model_deployments_total",
            "Total number of model deployments",
            ["model_id", "model_type", "status"],
            registry=self.registry,
        )

        self.deployment_duration = Histogram(
            "ai_model_deployment_duration_seconds",
            "Time spent on model deployment",
            ["model_id", "model_type"],
            registry=self.registry,
        )

        # 推理相关指标
        self.inference_requests_total = Counter(
            "ai_model_inference_requests_total",
            "Total number of inference requests",
            ["model_id", "status"],
            registry=self.registry,
        )

        self.inference_duration = Histogram(
            "ai_model_inference_duration_seconds",
            "Time spent on inference",
            ["model_id"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry,
        )

        # 资源使用指标
        self.resource_usage = Gauge(
            "ai_model_resource_usage",
            "Model resource usage",
            ["model_id", "resource_type"],
            registry=self.registry,
        )

        # 健康状态指标
        self.health_status = Gauge(
            "ai_model_health_status",
            "Model health status (1=healthy, 0=unhealthy)",
            ["model_id", "deployment_id"],
            registry=self.registry,
        )

        # 副本数量指标
        self.replicas = Gauge(
            "ai_model_replicas",
            "Number of model replicas",
            ["model_id", "deployment_id", "status"],
            registry=self.registry,
        )

    def record_deployment(
        self,
        model_id: str,
        model_type: str,
        status: str,
        duration: Optional[float] = None,
    ) -> None:
        """记录部署指标

        Args:
            model_id: 模型ID
            model_type: 模型类型
            status: 部署状态
            duration: 部署耗时
        """
        self.deployments_total.labels(
            model_id=model_id, model_type=model_type, status=status
        ).inc()

        if duration is not None:
            self.deployment_duration.labels(
                model_id=model_id, model_type=model_type
            ).observe(duration)

    def record_inference(self, model_id: str, status: str, duration: float) -> None:
        """记录推理指标

        Args:
            model_id: 模型ID
            status: 推理状态
            duration: 推理耗时(秒)
        """
        self.inference_requests_total.labels(model_id=model_id, status=status).inc()

        self.inference_duration.labels(model_id=model_id).observe(duration)

    def update_resource_usage(
        self, model_id: str, resource_type: str, value: float
    ) -> None:
        """更新资源使用指标

        Args:
            model_id: 模型ID
            resource_type: 资源类型 (cpu, memory, gpu)
            value: 资源使用值
        """
        self.resource_usage.labels(model_id=model_id, resource_type=resource_type).set(
            value
        )

    def update_health_status(
        self, model_id: str, deployment_id: str, is_healthy: bool
    ) -> None:
        """更新健康状态指标

        Args:
            model_id: 模型ID
            deployment_id: 部署ID
            is_healthy: 是否健康
        """
        self.health_status.labels(model_id=model_id, deployment_id=deployment_id).set(
            1 if is_healthy else 0
        )

    def update_replicas(
        self, model_id: str, deployment_id: str, status: str, count: int
    ) -> None:
        """更新副本数量指标

        Args:
            model_id: 模型ID
            deployment_id: 部署ID
            status: 副本状态 (total, ready, unavailable)
            count: 副本数量
        """
        self.replicas.labels(
            model_id=model_id, deployment_id=deployment_id, status=status
        ).set(count)

    def get_metrics(self) -> bytes:
        """获取Prometheus格式的指标数据

        Returns:
            指标数据
        """
        return generate_latest(self.registry)

    async def start(self) -> None:
        """启动指标收集器"""
        # 指标收集器不需要特殊的启动逻辑
        pass

    async def shutdown(self) -> None:
        """关闭指标收集器"""
        # 指标收集器不需要特殊的关闭逻辑
        pass

    def generate_latest(self) -> bytes:
        """生成最新的指标数据（别名方法）

        Returns:
            指标数据
        """
        return self.get_metrics()


class MetricsTimer:
    """指标计时器上下文管理器"""

    def __init__(self, histogram: Histogram, labels: Dict[str, str]):
        """初始化计时器

        Args:
            histogram: Prometheus直方图
            labels: 标签
        """
        self.histogram = histogram
        self.labels = labels
        self.start_time: Optional[float] = None

    def __enter__(self) -> "MetricsTimer":
        self.start_time = time.time()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.histogram.labels(**self.labels).observe(duration)
