#!/usr/bin/env python

"""
健康检查模块
提供服务健康状态检查和报告功能
"""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """健康状态枚举"""

    UNKNOWN = "UNKNOWN"  # 未知状态
    SERVING = "SERVING"  # 正常服务中
    WARNING = "WARNING"  # 警告状态
    NOT_SERVING = "NOT_SERVING"  # 不可服务


@dataclass
class ComponentHealth:
    """组件健康状态"""

    name: str  # 组件名称
    status: HealthStatus  # 健康状态
    description: str | None = None  # 状态描述
    details: dict[str, Any] = field(default_factory=dict)  # 详细信息
    last_check_time: float = field(default_factory=time.time)  # 最后检查时间
    consecutive_failures: int = 0  # 连续失败次数
    consecutive_successes: int = 0  # 连续成功次数


class HealthChecker:
    """健康检查器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化健康检查器

        Args:
            config: 健康检查配置
        """
        self.config = config.get("health_check", {})
        self.enabled = self.config.get("enabled", True)
        self.interval_seconds = self.config.get("interval_seconds", 30)
        self.timeout_seconds = self.config.get("timeout_seconds", 5)
        self.unhealthy_threshold = self.config.get("unhealthy_threshold", 3)
        self.healthy_threshold = self.config.get("healthy_threshold", 2)

        self.components: dict[str, ComponentHealth] = {}
        self.checks: dict[
            str, Callable[[], Awaitable[tuple[bool, str | None, dict[str, Any]]]]
        ] = {}
        self.is_running = False
        self.check_task = None

        # 注册默认健康检查
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """注册默认的健康检查"""
        # 注册内存检查
        self.register_check("memory", self._check_memory)

        # 注册CPU检查
        self.register_check("cpu", self._check_cpu)

        # 注册磁盘检查
        self.register_check("disk", self._check_disk)

    async def _check_memory(self) -> tuple[bool, str | None, dict[str, Any]]:
        """检查内存使用情况"""
        try:
            import psutil

            memory = psutil.virtual_memory()

            # 内存使用率超过90%时报警
            is_healthy = memory.percent < 90.0

            return (
                is_healthy,
                None if is_healthy else f"内存使用率过高: {memory.percent:.1f}%",
                {
                    "total_mb": memory.total / (1024 * 1024),
                    "available_mb": memory.available / (1024 * 1024),
                    "used_mb": memory.used / (1024 * 1024),
                    "percent": memory.percent,
                },
            )
        except Exception as e:
            logger.error(f"内存检查失败: {e!s}")
            return False, f"内存检查失败: {e!s}", {}

    async def _check_cpu(self) -> tuple[bool, str | None, dict[str, Any]]:
        """检查CPU使用情况"""
        try:
            import psutil

            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.5)

            # CPU使用率超过85%时报警
            is_healthy = cpu_percent < 85.0

            return (
                is_healthy,
                None if is_healthy else f"CPU使用率过高: {cpu_percent:.1f}%",
                {"percent": cpu_percent, "count": psutil.cpu_count(logical=True)},
            )
        except Exception as e:
            logger.error(f"CPU检查失败: {e!s}")
            return False, f"CPU检查失败: {e!s}", {}

    async def _check_disk(self) -> tuple[bool, str | None, dict[str, Any]]:
        """检查磁盘使用情况"""
        try:
            import psutil

            # 获取服务目录所在磁盘使用情况
            disk_usage = psutil.disk_usage("/")

            # 磁盘使用率超过90%时报警
            is_healthy = disk_usage.percent < 90.0

            return (
                is_healthy,
                None if is_healthy else f"磁盘使用率过高: {disk_usage.percent:.1f}%",
                {
                    "total_gb": disk_usage.total / (1024**3),
                    "free_gb": disk_usage.free / (1024**3),
                    "used_gb": disk_usage.used / (1024**3),
                    "percent": disk_usage.percent,
                },
            )
        except Exception as e:
            logger.error(f"磁盘检查失败: {e!s}")
            return False, f"磁盘检查失败: {e!s}", {}

    def register_check(
        self,
        name: str,
        check_func: Callable[[], Awaitable[tuple[bool, str | None, dict[str, Any]]]],
    ) -> None:
        """
        注册健康检查函数

        Args:
            name: 检查名称
            check_func: 检查函数，返回(is_healthy, description, details)元组
        """
        self.checks[name] = check_func

        # 初始化组件状态
        if name not in self.components:
            self.components[name] = ComponentHealth(
                name=name, status=HealthStatus.UNKNOWN
            )

    def unregister_check(self, name: str) -> None:
        """
        取消注册健康检查函数

        Args:
            name: 检查名称
        """
        if name in self.checks:
            del self.checks[name]

    async def check_health(self) -> dict[str, ComponentHealth]:
        """
        执行所有健康检查

        Returns:
            组件健康状态字典
        """
        for name, check_func in self.checks.items():
            component = self.components.get(name)
            if not component:
                component = ComponentHealth(name=name, status=HealthStatus.UNKNOWN)
                self.components[name] = component

            try:
                # 执行检查
                is_healthy, description, details = await check_func()

                # 更新组件状态
                component.last_check_time = time.time()
                component.details = details

                if is_healthy:
                    component.consecutive_failures = 0
                    component.consecutive_successes += 1

                    # 达到健康阈值，标记为正常服务
                    if component.consecutive_successes >= self.healthy_threshold:
                        component.status = HealthStatus.SERVING
                else:
                    component.consecutive_successes = 0
                    component.consecutive_failures += 1
                    component.description = description

                    # 达到不健康阈值，标记为警告或不可服务
                    if component.consecutive_failures >= self.unhealthy_threshold:
                        if component.status != HealthStatus.NOT_SERVING:
                            logger.warning(f"组件 {name} 健康检查失败: {description}")
                        component.status = HealthStatus.NOT_SERVING
                    else:
                        component.status = HealthStatus.WARNING

            except Exception as e:
                logger.error(f"执行 {name} 健康检查时出错: {e!s}")
                component.status = HealthStatus.WARNING
                component.description = f"检查执行出错: {e!s}"
                component.consecutive_failures += 1

        return self.components

    def get_service_status(self) -> HealthStatus:
        """
        获取整体服务健康状态

        Returns:
            服务健康状态
        """
        if not self.components:
            return HealthStatus.UNKNOWN

        # 如果任何组件不可服务，则整体不可服务
        if any(c.status == HealthStatus.NOT_SERVING for c in self.components.values()):
            return HealthStatus.NOT_SERVING

        # 如果任何组件处于警告状态，则整体处于警告状态
        if any(c.status == HealthStatus.WARNING for c in self.components.values()):
            return HealthStatus.WARNING

        # 如果所有组件正常服务，则整体正常服务
        if all(c.status == HealthStatus.SERVING for c in self.components.values()):
            return HealthStatus.SERVING

        # 其他情况，返回未知状态
        return HealthStatus.UNKNOWN

    async def start(self) -> None:
        """启动定期健康检查"""
        if not self.enabled:
            logger.info("健康检查已禁用")
            return

        if self.is_running:
            logger.warning("健康检查已在运行中")
            return

        self.is_running = True

        # 创建异步任务
        self.check_task = asyncio.create_task(self._run_periodic_checks())
        logger.info(f"健康检查已启动，检查间隔: {self.interval_seconds}秒")

    async def stop(self) -> None:
        """停止定期健康检查"""
        if not self.is_running:
            return

        self.is_running = False

        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
            self.check_task = None

        logger.info("健康检查已停止")

    async def _run_periodic_checks(self) -> None:
        """定期执行健康检查"""
        try:
            while self.is_running:
                await self.check_health()

                # 记录整体状态
                status = self.get_service_status()
                if status != HealthStatus.SERVING:
                    logger.warning(f"服务健康状态: {status.value}")

                    # 记录不健康组件详情
                    for name, component in self.components.items():
                        if component.status != HealthStatus.SERVING:
                            logger.warning(
                                f"组件 {name} 状态: {component.status.value}, 原因: {component.description}"
                            )

                # 等待下一次检查
                await asyncio.sleep(self.interval_seconds)
        except asyncio.CancelledError:
            logger.info("健康检查任务已取消")
        except Exception as e:
            logger.error(f"健康检查任务出错: {e!s}", exc_info=True)
            self.is_running = False
