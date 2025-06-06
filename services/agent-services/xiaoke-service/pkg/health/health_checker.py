"""
health_checker - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import aiohttp
import aioredis
import asyncio
import asyncpg
import logging
import time

#!/usr/bin/env python3
"""
健康检查和服务发现
提供多层次健康检查、自动故障检测和恢复、健康状态聚合和报告功能
"""



logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """健康状态枚举"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class CheckType(Enum):
    """检查类型枚举"""

    LIVENESS = "liveness"  # 存活检查
    READINESS = "readiness"  # 就绪检查
    STARTUP = "startup"  # 启动检查

@dataclass
class HealthCheckConfig:
    """健康检查配置"""

    interval: float = 30.0  # 检查间隔（秒）
    timeout: float = 10.0  # 检查超时（秒）
    retries: int = 3  # 重试次数
    failure_threshold: int = 3  # 失败阈值
    success_threshold: int = 1  # 成功阈值
    enabled: bool = True  # 是否启用

@dataclass
class HealthCheckResult:
    """健康检查结果"""

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0  # 检查耗时（秒）
    error: str | None = None

class HealthChecker(ABC):
    """健康检查器抽象基类"""

    def __init__(self, name: str, config: HealthCheckConfig = None):
        """
        初始化健康检查器

        Args:
            name: 检查器名称
            config: 检查配置
        """
        self.name = name
        self.config = config or HealthCheckConfig()

        # 状态跟踪
        self.current_status = HealthStatus.UNKNOWN
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_check_time = None
        self.last_success_time = None
        self.last_failure_time = None

        # 历史记录
        self.check_history: list[HealthCheckResult] = []
        self.max_history = 100

        logger.debug("创建健康检查器: %s", name)

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """执行健康检查"""
        pass

    async def perform_check(self) -> HealthCheckResult:
        """执行检查并更新状态"""
        if not self.config.enabled:
            return HealthCheckResult(
                name=self.name, status=HealthStatus.UNKNOWN, message="检查已禁用"
            )

        start_time = time.time()

        try:
            # 执行检查
            result = await asyncio.wait_for(self.check(), timeout=self.config.timeout)

            result.duration = time.time() - start_time
            result.timestamp = datetime.now()

            # 更新状态
            self._update_status(result)

            # 记录历史
            self._record_result(result)

            return result

        except TimeoutError:
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="检查超时",
                duration=time.time() - start_time,
                error="timeout",
            )

            self._update_status(result)
            self._record_result(result)

            return result

        except Exception as e:
            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"检查异常: {e!s}",
                duration=time.time() - start_time,
                error=str(e),
            )

            self._update_status(result)
            self._record_result(result)

            return result

    def _update_status(self, result: HealthCheckResult):
        """更新检查器状态"""
        self.last_check_time = result.timestamp

        if result.status == HealthStatus.HEALTHY:
            self.consecutive_successes += 1
            self.consecutive_failures = 0
            self.last_success_time = result.timestamp

            # 检查是否从不健康状态恢复
            if (
                self.current_status != HealthStatus.HEALTHY
                and self.consecutive_successes >= self.config.success_threshold
            ):
                self.current_status = HealthStatus.HEALTHY
                logger.info("健康检查器 %s 状态恢复为健康", self.name)

        else:
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            self.last_failure_time = result.timestamp

            # 检查是否需要标记为不健康
            if (
                self.current_status == HealthStatus.HEALTHY
                and self.consecutive_failures >= self.config.failure_threshold
            ):
                self.current_status = HealthStatus.UNHEALTHY
                logger.warning("健康检查器 %s 状态变为不健康", self.name)
            elif result.status == HealthStatus.DEGRADED:
                self.current_status = HealthStatus.DEGRADED

    def _record_result(self, result: HealthCheckResult):
        """记录检查结果"""
        self.check_history.append(result)

        # 限制历史记录数量
        if len(self.check_history) > self.max_history:
            self.check_history.pop(0)

    def get_status(self) -> dict[str, Any]:
        """获取检查器状态"""
        return {
            "name": self.name,
            "status": self.current_status.value,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "last_check_time": self.last_check_time.isoformat()
            if self.last_check_time
            else None,
            "last_success_time": self.last_success_time.isoformat()
            if self.last_success_time
            else None,
            "last_failure_time": self.last_failure_time.isoformat()
            if self.last_failure_time
            else None,
            "config": {
                "interval": self.config.interval,
                "timeout": self.config.timeout,
                "enabled": self.config.enabled,
            },
        }

class DatabaseHealthChecker(HealthChecker):
    """数据库健康检查器"""

    def __init__(
        self,
        name: str,
        connection_string: str,
        db_type: str = "postgresql",
        config: HealthCheckConfig = None,
    ):
        """
        初始化数据库健康检查器

        Args:
            name: 检查器名称
            connection_string: 数据库连接字符串
            db_type: 数据库类型
            config: 检查配置
        """
        super().__init__(name, config)
        self.connection_string = connection_string
        self.db_type = db_type.lower()

        # 连接对象
        self.connection = None

    async def check(self) -> HealthCheckResult:
        """执行数据库健康检查"""
        try:
            if self.db_type == "postgresql":
                return await self._check_postgresql()
            elif self.db_type == "mongodb":
                return await self._check_mongodb()
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"不支持的数据库类型: {self.db_type}",
                )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"数据库检查失败: {e!s}",
                error=str(e),
            )

    async def _check_postgresql(self) -> HealthCheckResult:
        """检查PostgreSQL"""
        try:
            conn = await asyncpg.connect(self.connection_string)

            # 执行简单查询
            result = await conn.fetchval("SELECT 1")

            # 获取连接信息
            server_version = await conn.fetchval("SELECT version()")

            await conn.close()

            if result == 1:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="PostgreSQL连接正常",
                    details={"server_version": server_version, "query_result": result},
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="PostgreSQL查询结果异常",
                )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"PostgreSQL连接失败: {e!s}",
                error=str(e),
            )

    async def _check_mongodb(self) -> HealthCheckResult:
        """检查MongoDB"""
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)

            # 执行ping命令
            result = await client.admin.command("ping")

            # 获取服务器信息
            server_info = await client.server_info()

            client.close()

            if result.get("ok") == 1:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="MongoDB连接正常",
                    details={
                        "server_version": server_info.get("version"),
                        "ping_result": result,
                    },
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="MongoDB ping失败",
                )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"MongoDB连接失败: {e!s}",
                error=str(e),
            )

class RedisHealthChecker(HealthChecker):
    """Redis健康检查器"""

    def __init__(self, name: str, redis_url: str, config: HealthCheckConfig = None):
        """
        初始化Redis健康检查器

        Args:
            name: 检查器名称
            redis_url: Redis连接URL
            config: 检查配置
        """
        super().__init__(name, config)
        self.redis_url = redis_url

    async def check(self) -> HealthCheckResult:
        """执行Redis健康检查"""
        try:
            redis_client = aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )

            # 执行ping命令
            pong = await redis_client.ping()

            # 获取Redis信息
            info = await redis_client.info()

            await redis_client.close()

            if pong:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Redis连接正常",
                    details={
                        "redis_version": info.get("redis_version"),
                        "used_memory": info.get("used_memory_human"),
                        "connected_clients": info.get("connected_clients"),
                    },
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Redis ping失败",
                )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis连接失败: {e!s}",
                error=str(e),
            )

class HTTPHealthChecker(HealthChecker):
    """HTTP服务健康检查器"""

    def __init__(
        self,
        name: str,
        url: str,
        expected_status: int = 200,
        headers: dict[str, str] | None = None,
        config: HealthCheckConfig = None,
    ):
        """
        初始化HTTP健康检查器

        Args:
            name: 检查器名称
            url: 检查URL
            expected_status: 期望的HTTP状态码
            headers: 请求头
            config: 检查配置
        """
        super().__init__(name, config)
        self.url = url
        self.expected_status = expected_status
        self.headers = headers or {}

    async def check(self) -> HealthCheckResult:
        """执行HTTP健康检查"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:
                    status_code = response.status
                    response_text = await response.text()

                    if status_code == self.expected_status:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.HEALTHY,
                            message=f"HTTP检查成功，状态码: {status_code}",
                            details={
                                "status_code": status_code,
                                "response_size": len(response_text),
                                "headers": dict(response.headers),
                            },
                        )
                    else:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.UNHEALTHY,
                            message=f"HTTP状态码异常: {status_code}, 期望: {self.expected_status}",
                            details={
                                "status_code": status_code,
                                "expected_status": self.expected_status,
                            },
                        )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"HTTP检查失败: {e!s}",
                error=str(e),
            )

class CustomHealthChecker(HealthChecker):
    """自定义健康检查器"""

    def __init__(
        self, name: str, check_function: Callable, config: HealthCheckConfig = None
    ):
        """
        初始化自定义健康检查器

        Args:
            name: 检查器名称
            check_function: 检查函数
            config: 检查配置
        """
        super().__init__(name, config)
        self.check_function = check_function

    async def check(self) -> HealthCheckResult:
        """执行自定义健康检查"""
        try:
            if asyncio.iscoroutinefunction(self.check_function):
                result = await self.check_function()
            else:
                result = self.check_function()

            # 如果返回的是HealthCheckResult，直接使用
            if isinstance(result, HealthCheckResult):
                result.name = self.name
                return result

            # 如果返回布尔值
            elif isinstance(result, bool):
                if result:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.HEALTHY,
                        message="自定义检查通过",
                    )
                else:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.UNHEALTHY,
                        message="自定义检查失败",
                    )

            # 如果返回字典
            elif isinstance(result, dict):
                status = HealthStatus(result.get("status", "unknown"))
                return HealthCheckResult(
                    name=self.name,
                    status=status,
                    message=result.get("message", ""),
                    details=result.get("details", {}),
                )

            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNKNOWN,
                    message=f"未知的检查结果类型: {type(result)}",
                )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"自定义检查异常: {e!s}",
                error=str(e),
            )

class HealthCheckManager:
    """健康检查管理器"""

    def __init__(self):
        """初始化健康检查管理器"""
        self.checkers: dict[str, HealthChecker] = {}
        self.check_tasks: dict[str, asyncio.Task] = {}
        self.is_running = False

        # 全局健康状态
        self.overall_status = HealthStatus.UNKNOWN
        self.last_update_time = None

        # 状态变更回调
        self.status_change_callbacks: list[Callable] = []

        # 统计信息
        self.stats = {
            "total_checks": 0,
            "healthy_checks": 0,
            "unhealthy_checks": 0,
            "degraded_checks": 0,
            "check_errors": 0,
        }

        logger.info("健康检查管理器初始化完成")

    def register_checker(self, checker: HealthChecker):
        """
        注册健康检查器

        Args:
            checker: 健康检查器实例
        """
        self.checkers[checker.name] = checker
        logger.info("注册健康检查器: %s", checker.name)

    def register_database_checker(
        self,
        name: str,
        connection_string: str,
        db_type: str = "postgresql",
        config: HealthCheckConfig = None,
    ):
        """注册数据库健康检查器"""
        checker = DatabaseHealthChecker(name, connection_string, db_type, config)
        self.register_checker(checker)

    def register_redis_checker(
        self, name: str, redis_url: str, config: HealthCheckConfig = None
    ):
        """注册Redis健康检查器"""
        checker = RedisHealthChecker(name, redis_url, config)
        self.register_checker(checker)

    def register_http_checker(
        self,
        name: str,
        url: str,
        expected_status: int = 200,
        headers: dict[str, str] | None = None,
        config: HealthCheckConfig = None,
    ):
        """注册HTTP健康检查器"""
        checker = HTTPHealthChecker(name, url, expected_status, headers, config)
        self.register_checker(checker)

    def register_custom_checker(
        self, name: str, check_function: Callable, config: HealthCheckConfig = None
    ):
        """注册自定义健康检查器"""
        checker = CustomHealthChecker(name, check_function, config)
        self.register_checker(checker)

    def add_status_change_callback(self, callback: Callable):
        """添加状态变更回调"""
        self.status_change_callbacks.append(callback)

    async def start(self):
        """启动健康检查"""
        if self.is_running:
            logger.warning("健康检查已在运行")
            return

        self.is_running = True

        # 为每个检查器启动定期检查任务
        for name, checker in self.checkers.items():
            if checker.config.enabled:
                task = asyncio.create_task(self._check_loop(checker))
                self.check_tasks[name] = task

        logger.info("健康检查已启动，共 %d 个检查器", len(self.check_tasks))

    async def _check_loop(self, checker: HealthChecker):
        """检查循环"""
        while self.is_running:
            try:
                # 执行检查
                result = await checker.perform_check()

                # 更新统计
                self._update_stats(result)

                # 更新全局状态
                await self._update_overall_status()

                # 等待下次检查
                await asyncio.sleep(checker.config.interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("检查循环异常，检查器: %s, 错误: %s", checker.name, str(e))
                self.stats["check_errors"] += 1
                await asyncio.sleep(checker.config.interval)

    def _update_stats(self, result: HealthCheckResult):
        """更新统计信息"""
        self.stats["total_checks"] += 1

        if result.status == HealthStatus.HEALTHY:
            self.stats["healthy_checks"] += 1
        elif result.status == HealthStatus.UNHEALTHY:
            self.stats["unhealthy_checks"] += 1
        elif result.status == HealthStatus.DEGRADED:
            self.stats["degraded_checks"] += 1

    async def _update_overall_status(self):
        """更新全局健康状态"""
        if not self.checkers:
            new_status = HealthStatus.UNKNOWN
        else:
            statuses = [checker.current_status for checker in self.checkers.values()]

            # 如果有任何不健康的检查器，整体状态为不健康
            if HealthStatus.UNHEALTHY in statuses:
                new_status = HealthStatus.UNHEALTHY
            # 如果有降级的检查器，整体状态为降级
            elif HealthStatus.DEGRADED in statuses:
                new_status = HealthStatus.DEGRADED
            # 如果所有检查器都健康，整体状态为健康
            elif all(status == HealthStatus.HEALTHY for status in statuses):
                new_status = HealthStatus.HEALTHY
            # 其他情况为未知
            else:
                new_status = HealthStatus.UNKNOWN

        # 检查状态是否发生变化
        if new_status != self.overall_status:
            old_status = self.overall_status
            self.overall_status = new_status
            self.last_update_time = datetime.now()

            logger.info(
                "全局健康状态变更: %s -> %s",
                old_status.value if old_status else "None",
                new_status.value,
            )

            # 调用状态变更回调
            for callback in self.status_change_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(old_status, new_status)
                    else:
                        callback(old_status, new_status)
                except Exception as e:
                    logger.error("状态变更回调异常: %s", str(e))

    async def get_health_status(self) -> dict[str, Any]:
        """获取健康状态"""
        checker_statuses = {}
        for name, checker in self.checkers.items():
            checker_statuses[name] = checker.get_status()

        return {
            "overall_status": self.overall_status.value,
            "last_update_time": self.last_update_time.isoformat()
            if self.last_update_time
            else None,
            "checkers": checker_statuses,
            "stats": self.stats.copy(),
            "summary": {
                "total_checkers": len(self.checkers),
                "enabled_checkers": len(
                    [c for c in self.checkers.values() if c.config.enabled]
                ),
                "healthy_checkers": len(
                    [
                        c
                        for c in self.checkers.values()
                        if c.current_status == HealthStatus.HEALTHY
                    ]
                ),
                "unhealthy_checkers": len(
                    [
                        c
                        for c in self.checkers.values()
                        if c.current_status == HealthStatus.UNHEALTHY
                    ]
                ),
                "degraded_checkers": len(
                    [
                        c
                        for c in self.checkers.values()
                        if c.current_status == HealthStatus.DEGRADED
                    ]
                ),
            },
        }

    async def check_all_now(self) -> dict[str, HealthCheckResult]:
        """立即执行所有检查"""
        results = {}

        tasks = []
        for _name, checker in self.checkers.items():
            if checker.config.enabled:
                tasks.append(checker.perform_check())

        if tasks:
            check_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(check_results):
                checker_name = list(self.checkers.keys())[i]
                if isinstance(result, Exception):
                    results[checker_name] = HealthCheckResult(
                        name=checker_name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"检查异常: {result!s}",
                        error=str(result),
                    )
                else:
                    results[checker_name] = result

        # 更新全局状态
        await self._update_overall_status()

        return results

    async def stop(self):
        """停止健康检查"""
        self.is_running = False

        # 取消所有检查任务
        for task in self.check_tasks.values():
            task.cancel()

        # 等待所有任务完成
        if self.check_tasks:
            await asyncio.gather(*self.check_tasks.values(), return_exceptions=True)

        self.check_tasks.clear()

        logger.info("健康检查已停止")

# 全局健康检查管理器实例
_health_check_manager: HealthCheckManager | None = None

def get_health_check_manager() -> HealthCheckManager:
    """获取健康检查管理器实例"""
    global _health_check_manager

    if _health_check_manager is None:
        _health_check_manager = HealthCheckManager()

    return _health_check_manager

async def close_health_check_manager():
    """关闭健康检查管理器"""
    global _health_check_manager

    if _health_check_manager:
        await _health_check_manager.stop()
        _health_check_manager = None
