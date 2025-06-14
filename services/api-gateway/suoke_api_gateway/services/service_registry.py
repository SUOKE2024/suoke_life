#!/usr/bin/env python3
"""
索克生活 API 网关服务注册表

管理后端服务的注册、发现和负载均衡。
"""

from ..core.config import ServiceConfig, Settings
from ..core.logging import get_logger
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import httpx
import random
import time

logger = get_logger(__name__)


class ServiceInstance(BaseModel):
    """服务实例模型"""
    id: str
    name: str
    host: str
    port: int
    health_check_path: str
    healthy: bool = True
    last_health_check: Optional[datetime] = None
    failure_count: int = 0
    weight: int = 1
    metadata: Dict[str, str] = {}

    class Config:
        """Pydantic 配置"""
        # 允许任意类型
        arbitrary_types_allowed = True


class ServiceRegistry:
    """服务注册表"""

    def __init__(self, settings: Settings = None):
        """初始化服务注册表"""
        self.settings = settings
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.health_check_interval = 30  # 秒
        self.failure_threshold = 3
        self.recovery_threshold = 2
        self._health_check_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """初始化服务注册表"""
        # 从配置加载服务
        if self.settings and self.settings.services:
            for service_config in self.settings.services:
                await self.register_service_from_config(service_config)

        # 启动健康检查任务
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info("Service registry initialized", services=len(self.services))

    async def register_service_from_config(self, service_config: ServiceConfig) -> str:
        """从配置注册服务"""
        # 解析URL获取host和port
        from urllib.parse import urlparse
        parsed = urlparse(service_config.url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 80
        
        return await self.register_service(
            service_config.name,
            service_config,
            f"{service_config.name}-{host}-{port}"
        )

    async def cleanup(self) -> None:
        """清理资源"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

    async def register_service(
        self,
        service_name: str,
        service_config: ServiceConfig,
        instance_id: Optional[str] = None,
    ) -> str:
        """注册服务实例"""
        # 解析URL获取host和port
        from urllib.parse import urlparse
        parsed = urlparse(service_config.url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 80
        
        if instance_id is None:
            instance_id = f"{service_name}-{host}-{port}"

        instance = ServiceInstance(
            id=instance_id,
            name=service_name,
            host=host,
            port=port,
            health_check_path=service_config.health_check_path,
            weight=service_config.weight,
        )

        if service_name not in self.services:
            self.services[service_name] = []

        # 检查是否已存在相同实例
        existing_instance = None
        for i, existing in enumerate(self.services[service_name]):
            if existing.id == instance_id:
                existing_instance = i
                break

        if existing_instance is not None:
            # 更新现有实例
            self.services[service_name][existing_instance] = instance
            logger.info("Service instance updated", service=service_name, instance_id=instance_id)
        else:
            # 添加新实例
            self.services[service_name].append(instance)
            logger.info("Service instance registered", service=service_name, instance_id=instance_id)

        return instance_id

    async def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """注销服务实例"""
        if service_name not in self.services:
            return False

        for i, instance in enumerate(self.services[service_name]):
            if instance.id == instance_id:
                del self.services[service_name][i]
                logger.info("Service instance deregistered", service=service_name, instance_id=instance_id)

                # 如果没有实例了，删除服务
                if not self.services[service_name]:
                    del self.services[service_name]

                return True

        return False

    def get_service_instance(
        self,
        service_name: str,
        strategy: str = "round_robin"
    ) -> Optional[ServiceInstance]:
        """获取服务实例（负载均衡）"""
        if service_name not in self.services:
            return None

        # 过滤健康的实例
        healthy_instances = [
            instance for instance in self.services[service_name]
            if instance.healthy
        ]

        if not healthy_instances:
            logger.warning("No healthy instances available", service=service_name)
            return None

        # 根据策略选择实例
        if strategy == "round_robin":
            return self._round_robin_select(healthy_instances)
        elif strategy == "random":
            return random.choice(healthy_instances)
        elif strategy == "weighted":
            return self._weighted_select(healthy_instances)
        else:
            # 默认使用轮询
            return self._round_robin_select(healthy_instances)

    def get_all_services(self)-> Dict[str, List[ServiceInstance]]:
        """获取所有服务"""
        return self.services.copy()

    def get_service_health(self, service_name: str)-> Dict[str, any]:
        """获取服务健康状态"""
        if service_name not in self.services:
            return {"status": "not_found"}

        instances = self.services[service_name]
        healthy_count = sum(1 for instance in instances if instance.healthy)
        total_count = len(instances)

        return {
            "status": "healthy" if healthy_count > 0 else "unhealthy",
            "healthy_instances": healthy_count,
            "total_instances": total_count,
            "health_ratio": healthy_count / total_count if total_count > 0 else 0,
            "instances": [
                {
                    "id": instance.id,
                    "host": instance.host,
                    "port": instance.port,
                    "healthy": instance.healthy,
                    "failure_count": instance.failure_count,
                    "last_health_check": instance.last_health_check,
                }
                for instance in instances
            ]
        }

    async def _health_check_loop(self) -> None:
        """健康检查循环"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check loop error", error=str(e), exc_info=True)
                await asyncio.sleep(5)  # 短暂等待后重试

    async def _perform_health_checks(self) -> None:
        """执行健康检查"""
        tasks = []

        for service_name, instances in self.services.items():
            for instance in instances:
                task = asyncio.create_task(
                    self._check_instance_health(instance),
                    name=f"health_check_{instance.id}"
                )
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_instance_health(self, instance: ServiceInstance) -> None:
        """检查单个实例健康状态"""
        start_time = time.time()

        try:
            url = f"http://{instance.host}:{instance.port}{instance.health_check_path}"

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    # 健康检查成功
                    if not instance.healthy:
                        # 从不健康恢复
                        instance.failure_count = max(0, instance.failure_count - 1)
                        if instance.failure_count <= self.recovery_threshold:
                            instance.healthy = True
                            logger.info(
                                "Service instance recovered",
                                service=instance.name,
                                instance_id=instance.id,
                            )
                    else:
                        # 重置失败计数
                        instance.failure_count = 0
                else:
                    # 健康检查失败
                    self._handle_health_check_failure(instance, f"HTTP {response.status_code}")

        except Exception as e:
            # 健康检查异常
            self._handle_health_check_failure(instance, str(e))

        finally:
            instance.last_health_check = datetime.utcnow()

            # 记录健康检查指标
            duration = time.time() - start_time
            if hasattr(self, '_metrics_service'):
                self._metrics_service.record_health_check(
                    instance.name, duration, instance.healthy
                )

    def _handle_health_check_failure(self, instance: ServiceInstance, error: str) -> None:
        """处理健康检查失败"""
        instance.failure_count += 1

        if instance.healthy and instance.failure_count >= self.failure_threshold:
            instance.healthy = False
            logger.warning(
                "Service instance marked unhealthy",
                service=instance.name,
                instance_id=instance.id,
                failure_count=instance.failure_count,
                error=error,
            )

    def _round_robin_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """轮询选择"""
        # 简单的轮询实现，实际应该使用更复杂的状态管理
        return instances[int(time.time()) % len(instances)]

    def _weighted_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """加权选择"""
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return random.choice(instances)

        random_weight = random.randint(1, total_weight)
        current_weight = 0

        for instance in instances:
            current_weight += instance.weight
            if current_weight >= random_weight:
                return instance

        return instances[-1]  # 回退

    def record_response_time(self, service_name: str, instance_id: str, response_time: float) -> None:
        """记录响应时间"""
        # 这里可以添加响应时间记录逻辑
        # 暂时只记录日志
        logger.debug(
            "Response time recorded",
            service=service_name,
            instance=instance_id,
            response_time=response_time
        )

    def mark_unhealthy(self, service_name: str, instance_id: str) -> None:
        """标记实例为不健康"""
        if service_name not in self.services:
            return

        for instance in self.services[service_name]:
            if f"{instance.host}:{instance.port}" == instance_id or instance.id == instance_id:
                instance.healthy = False
                instance.failure_count += 1
                logger.warning(
                    "Instance marked as unhealthy",
                    service=service_name,
                    instance_id=instance_id
                )
                break