"""
service_registry - 索克生活项目模块
"""

            import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
import asyncio
import contextlib
import logging
import time

#!/usr/bin/env python3
"""
服务注册中心实现
支持服务注册、发现、健康检查等功能
"""


logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


@dataclass
class ServiceInstance:
    """服务实例"""

    service_name: str
    instance_id: str
    host: str
    port: int
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    health_check_url: str | None = None

    @property
    def address(self) -> str:
        """获取服务地址"""
        return f"{self.host}:{self.port}"

    @property
    def is_healthy(self) -> bool:
        """是否健康"""
        return self.status == ServiceStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "service_name": self.service_name,
            "instance_id": self.instance_id,
            "host": self.host,
            "port": self.port,
            "address": self.address,
            "metadata": self.metadata,
            "tags": self.tags,
            "status": self.status.value,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "health_check_url": self.health_check_url,
        }


@dataclass
class ServiceConfig:
    """服务配置"""

    name: str
    version: str = "1.0.0"
    protocol: str = "http"
    load_balancer: str = "round_robin"  # round_robin, random, least_connections
    health_check_interval: int = 10  # 秒
    health_check_timeout: int = 5  # 秒
    deregister_after: int = 60  # 秒，多久没有心跳后注销
    metadata: dict[str, Any] = field(default_factory=dict)


class ServiceRegistry(ABC):
    """服务注册中心抽象接口"""

    @abstractmethod
    async def register(self, instance: ServiceInstance) -> bool:
        """注册服务实例"""
        pass

    @abstractmethod
    async def deregister(self, service_name: str, instance_id: str) -> bool:
        """注销服务实例"""
        pass

    @abstractmethod
    async def get_instances(self, service_name: str) -> list[ServiceInstance]:
        """获取服务的所有实例"""
        pass

    @abstractmethod
    async def get_healthy_instances(self, service_name: str) -> list[ServiceInstance]:
        """获取服务的健康实例"""
        pass

    @abstractmethod
    async def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """发送心跳"""
        pass


class InMemoryServiceRegistry(ServiceRegistry):
    """内存服务注册中心实现"""

    def __init__(self):
        self.services: dict[str, dict[str, ServiceInstance]] = {}
        self.service_configs: dict[str, ServiceConfig] = {}
        self._lock = asyncio.Lock()
        self._health_check_task = None
        self._cleanup_task = None

        # 统计信息
        self.stats = {
            "total_registrations": 0,
            "total_deregistrations": 0,
            "health_checks_performed": 0,
            "failed_health_checks": 0,
        }

    async def start(self):
        """启动服务注册中心"""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("服务注册中心已启动")

    async def stop(self):
        """停止服务注册中心"""
        if self._health_check_task:
            self._health_check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._health_check_task

        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        logger.info("服务注册中心已停止")

    async def register(self, instance: ServiceInstance) -> bool:
        """注册服务实例"""
        async with self._lock:
            if instance.service_name not in self.services:
                self.services[instance.service_name] = {}

            self.services[instance.service_name][instance.instance_id] = instance
            self.stats["total_registrations"] += 1

            logger.info(
                f"注册服务实例: {instance.service_name}/{instance.instance_id} at {instance.address}"
            )
            return True

    async def deregister(self, service_name: str, instance_id: str) -> bool:
        """注销服务实例"""
        async with self._lock:
            if (
                service_name in self.services
                and instance_id in self.services[service_name]
            ):
                del self.services[service_name][instance_id]
                self.stats["total_deregistrations"] += 1

                # 如果服务没有实例了，删除服务
                if not self.services[service_name]:
                    del self.services[service_name]

                logger.info(f"注销服务实例: {service_name}/{instance_id}")
                return True

            return False

    async def get_instances(self, service_name: str) -> list[ServiceInstance]:
        """获取服务的所有实例"""
        async with self._lock:
            if service_name in self.services:
                return list(self.services[service_name].values())
            return []

    async def get_healthy_instances(self, service_name: str) -> list[ServiceInstance]:
        """获取服务的健康实例"""
        instances = await self.get_instances(service_name)
        return [inst for inst in instances if inst.is_healthy]

    async def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """发送心跳"""
        async with self._lock:
            if (
                service_name in self.services
                and instance_id in self.services[service_name]
            ):
                instance = self.services[service_name][instance_id]
                instance.last_heartbeat = datetime.now()
                instance.status = ServiceStatus.HEALTHY
                return True
            return False

    async def set_service_config(self, config: ServiceConfig):
        """设置服务配置"""
        async with self._lock:
            self.service_configs[config.name] = config

    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(5)  # 每5秒检查一次
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查错误: {e}")

    async def _perform_health_checks(self):
        """执行健康检查"""
        async with self._lock:
            services_copy = {
                svc: dict(instances) for svc, instances in self.services.items()
            }

        for service_name, instances in services_copy.items():
            config = self.service_configs.get(service_name)

            for instance_id, instance in instances.items():
                # 检查心跳超时
                if config:
                    timeout = timedelta(seconds=config.deregister_after)
                else:
                    timeout = timedelta(seconds=60)

                if datetime.now() - instance.last_heartbeat > timeout:
                    instance.status = ServiceStatus.UNHEALTHY
                    logger.warning(f"服务实例心跳超时: {service_name}/{instance_id}")

                # 如果有健康检查URL，执行HTTP健康检查
                if instance.health_check_url:
                    # 这里可以实现HTTP健康检查
                    pass

                self.stats["health_checks_performed"] += 1

    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒清理一次
                await self._cleanup_unhealthy_instances()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务错误: {e}")

    async def _cleanup_unhealthy_instances(self):
        """清理不健康的实例"""
        to_remove = []

        async with self._lock:
            for service_name, instances in self.services.items():
                config = self.service_configs.get(service_name)

                for instance_id, instance in instances.items():
                    # 长时间不健康的实例
                    if instance.status == ServiceStatus.UNHEALTHY:
                        if config:
                            timeout = timedelta(seconds=config.deregister_after * 2)
                        else:
                            timeout = timedelta(seconds=120)

                        if datetime.now() - instance.last_heartbeat > timeout:
                            to_remove.append((service_name, instance_id))

        # 移除实例
        for service_name, instance_id in to_remove:
            await self.deregister(service_name, instance_id)
            logger.info(f"清理不健康实例: {service_name}/{instance_id}")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        total_instances = sum(len(instances) for instances in self.services.values())
        healthy_instances = sum(
            sum(1 for inst in instances.values() if inst.is_healthy)
            for instances in self.services.values()
        )

        return {
            **self.stats,
            "total_services": len(self.services),
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "unhealthy_instances": total_instances - healthy_instances,
        }


class ServiceDiscovery:
    """服务发现客户端"""

    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self._cache: dict[str, list[ServiceInstance]] = {}
        self._cache_ttl = 5  # 缓存5秒
        self._last_cache_update: dict[str, float] = {}
        self._round_robin_counters: dict[str, int] = {}

    async def discover(
        self,
        service_name: str,
        load_balancer: str = "round_robin",
        tags: list[str] | None = None,
    ) -> ServiceInstance | None:
        """发现服务实例"""
        instances = await self.get_healthy_instances(service_name, tags)

        if not instances:
            return None

        # 根据负载均衡策略选择实例
        if load_balancer == "random":

            return random.choice(instances)

        elif load_balancer == "round_robin":
            if service_name not in self._round_robin_counters:
                self._round_robin_counters[service_name] = 0

            index = self._round_robin_counters[service_name] % len(instances)
            self._round_robin_counters[service_name] += 1

            return instances[index]

        elif load_balancer == "least_connections":
            # 这里需要实现连接数统计
            # 暂时返回第一个
            return instances[0]

        else:
            return instances[0]

    async def get_healthy_instances(
        self, service_name: str, tags: list[str] | None = None
    ) -> list[ServiceInstance]:
        """获取健康的服务实例"""
        # 检查缓存
        current_time = time.time()
        if (
            service_name in self._cache
            and service_name in self._last_cache_update
            and current_time - self._last_cache_update[service_name] < self._cache_ttl
        ):
            instances = self._cache[service_name]
        else:
            # 从注册中心获取
            instances = await self.registry.get_healthy_instances(service_name)
            self._cache[service_name] = instances
            self._last_cache_update[service_name] = current_time

        # 过滤标签
        if tags:
            instances = [
                inst for inst in instances if all(tag in inst.tags for tag in tags)
            ]

        return instances

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._last_cache_update.clear()


# 全局服务注册中心
_global_registry = InMemoryServiceRegistry()


async def get_service_registry() -> ServiceRegistry:
    """获取全局服务注册中心"""
    return _global_registry


async def get_service_discovery() -> ServiceDiscovery:
    """获取服务发现客户端"""
    return ServiceDiscovery(_global_registry)
