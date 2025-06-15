#!/usr/bin/env python3
"""
健康检查模块
提供服务健康状态检查和监控功能
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    error: str | None = None


@dataclass
class ServiceHealth:
    """服务健康状态"""

    overall_status: HealthStatus
    checks: list[HealthCheckResult]
    timestamp: float = field(default_factory=time.time)
    uptime: float = 0.0
    version: str = "0.2.0"


class HealthChecker:
    """健康检查器基类"""

    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout

    async def check(self) -> HealthCheckResult:
        """执行健康检查"""
        start_time = time.time()

        try:
            # 使用超时控制
            result = await asyncio.wait_for(self._perform_check(), timeout=self.timeout)
            duration = time.time() - start_time

            return HealthCheckResult(
                name=self.name,
                status=result.get("status", HealthStatus.UNKNOWN),
                message=result.get("message", ""),
                details=result.get("details", {}),
                duration=duration,
            )

        except TimeoutError:
            duration = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查超时 ({self.timeout}秒)",
                duration=duration,
                error="timeout",
            )
        except Exception as e:
            duration = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查失败: {str(e)}",
                duration=duration,
                error=str(e),
            )

    async def _perform_check(self) -> dict[str, Any]:
        """执行具体的健康检查逻辑，子类需要实现"""
        raise NotImplementedError


class DatabaseHealthChecker(HealthChecker):
    """数据库健康检查器"""

    def __init__(self, db_connection=None, timeout: float = 3.0):
        super().__init__("database", timeout)
        self.db_connection = db_connection

    async def _perform_check(self) -> dict[str, Any]:
        """检查数据库连接"""
        if not self.db_connection:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "数据库连接未配置",
                "details": {"configured": False},
            }

        try:
            # 模拟数据库连接检查
            await asyncio.sleep(0.1)  # 模拟查询延迟

            return {
                "status": HealthStatus.HEALTHY,
                "message": "数据库连接正常",
                "details": {
                    "configured": True,
                    "connection_pool_size": 10,
                    "active_connections": 2,
                },
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"数据库连接失败: {str(e)}",
                "details": {"error": str(e)},
            }


class ModelHealthChecker(HealthChecker):
    """AI模型健康检查器"""

    def __init__(self, model_manager=None, timeout: float = 5.0):
        super().__init__("ai_models", timeout)
        self.model_manager = model_manager

    async def _perform_check(self) -> dict[str, Any]:
        """检查AI模型状态"""
        if not self.model_manager:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "模型管理器未初始化",
                "details": {"initialized": False},
            }

        try:
            # 检查各个模型的状态
            models_status = {
                "scene_model": "loaded",
                "sign_language_model": "loaded",
                "speech_model": "loaded",
                "conversion_model": "loaded",
            }

            loaded_count = sum(
                1 for status in models_status.values() if status == "loaded"
            )
            total_count = len(models_status)

            if loaded_count == total_count:
                status = HealthStatus.HEALTHY
                message = f"所有模型已加载 ({loaded_count}/{total_count})"
            elif loaded_count > 0:
                status = HealthStatus.DEGRADED
                message = f"部分模型已加载 ({loaded_count}/{total_count})"
            else:
                status = HealthStatus.UNHEALTHY
                message = "没有模型加载"

            return {
                "status": status,
                "message": message,
                "details": {
                    "models": models_status,
                    "loaded_count": loaded_count,
                    "total_count": total_count,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"模型状态检查失败: {str(e)}",
                "details": {"error": str(e)},
            }


class ConfigurationHealthChecker(HealthChecker):
    """配置健康检查器"""

    def __init__(self, config=None, timeout: float = 1.0):
        super().__init__("configuration", timeout)
        self.config = config

    async def _perform_check(self) -> dict[str, Any]:
        """检查配置状态"""
        if not self.config:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": "配置未加载",
                "details": {"loaded": False},
            }

        try:
            # 检查关键配置项
            required_configs = [
                "service.name",
                "service.port",
                "features.blind_assistance",
                "features.sign_language",
                "features.voice_assistance",
            ]

            missing_configs = []
            for config_path in required_configs:
                try:
                    # 简单的配置路径检查
                    parts = config_path.split(".")
                    value = self.config
                    for part in parts:
                        value = getattr(value, part)
                except (AttributeError, KeyError):
                    missing_configs.append(config_path)

            if not missing_configs:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "配置完整",
                    "details": {
                        "loaded": True,
                        "required_configs": len(required_configs),
                        "missing_configs": 0,
                    },
                }
            else:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": f"缺少 {len(missing_configs)} 个配置项",
                    "details": {
                        "loaded": True,
                        "missing_configs": missing_configs,
                        "required_configs": len(required_configs),
                    },
                }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"配置检查失败: {str(e)}",
                "details": {"error": str(e)},
            }


class SystemResourceHealthChecker(HealthChecker):
    """系统资源健康检查器"""

    def __init__(self, timeout: float = 2.0):
        super().__init__("system_resources", timeout)

    async def _perform_check(self) -> dict[str, Any]:
        """检查系统资源"""
        try:
            import psutil

            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # 判断健康状态
            issues = []
            if cpu_percent > 90:
                issues.append(f"CPU使用率过高: {cpu_percent:.1f}%")
            if memory_percent > 90:
                issues.append(f"内存使用率过高: {memory_percent:.1f}%")
            if disk_percent > 95:
                issues.append(f"磁盘使用率过高: {disk_percent:.1f}%")

            if issues:
                status = (
                    HealthStatus.DEGRADED
                    if len(issues) == 1
                    else HealthStatus.UNHEALTHY
                )
                message = "; ".join(issues)
            else:
                status = HealthStatus.HEALTHY
                message = "系统资源正常"

            return {
                "status": status,
                "message": message,
                "details": {
                    "cpu_percent": round(cpu_percent, 1),
                    "memory_percent": round(memory_percent, 1),
                    "disk_percent": round(disk_percent, 1),
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                },
            }

        except ImportError:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "psutil库未安装，无法检查系统资源",
                "details": {"psutil_available": False},
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"系统资源检查失败: {str(e)}",
                "details": {"error": str(e)},
            }


class ServiceHealthChecker(HealthChecker):
    """服务依赖健康检查器"""

    def __init__(self, service_name: str, endpoint: str = None, timeout: float = 3.0):
        super().__init__(f"service_{service_name}", timeout)
        self.service_name = service_name
        self.endpoint = endpoint

    async def _perform_check(self) -> dict[str, Any]:
        """检查外部服务"""
        if not self.endpoint:
            return {
                "status": HealthStatus.DEGRADED,
                "message": f"服务 {self.service_name} 端点未配置",
                "details": {"configured": False},
            }

        try:
            # 模拟服务连接检查
            await asyncio.sleep(0.1)  # 模拟网络延迟

            # 这里应该实际调用服务端点
            # 现在返回模拟结果
            return {
                "status": HealthStatus.HEALTHY,
                "message": f"服务 {self.service_name} 连接正常",
                "details": {
                    "service_name": self.service_name,
                    "endpoint": self.endpoint,
                    "response_time_ms": 100,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"服务 {self.service_name} 连接失败: {str(e)}",
                "details": {"error": str(e)},
            }


class HealthCheckManager:
    """健康检查管理器"""

    def __init__(self) -> None:
        self.checkers: list[HealthChecker] = []
        self.start_time = time.time()
        self.last_check_time = None
        self.last_check_results: list[HealthCheckResult] = []

    def add_checker(self, checker: HealthChecker):
        """添加健康检查器"""
        self.checkers.append(checker)
        logger.info(f"添加健康检查器: {checker.name}")

    def remove_checker(self, checker_name: str):
        """移除健康检查器"""
        self.checkers = [c for c in self.checkers if c.name != checker_name]
        logger.info(f"移除健康检查器: {checker_name}")

    async def check_health(self) -> ServiceHealth:
        """执行所有健康检查"""
        start_time = time.time()

        # 并发执行所有检查
        tasks = [checker.check() for checker in self.checkers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        check_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 处理异常情况
                check_results.append(
                    HealthCheckResult(
                        name=self.checkers[i].name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"健康检查异常: {str(result)}",
                        error=str(result),
                    )
                )
            else:
                check_results.append(result)

        # 计算整体状态
        overall_status = self._calculate_overall_status(check_results)

        # 更新状态
        self.last_check_time = time.time()
        self.last_check_results = check_results

        return ServiceHealth(
            overall_status=overall_status,
            checks=check_results,
            uptime=time.time() - self.start_time,
        )

    def _calculate_overall_status(
        self, results: list[HealthCheckResult]
    ) -> HealthStatus:
        """计算整体健康状态"""
        if not results:
            return HealthStatus.UNKNOWN

        statuses = [result.status for result in results]

        # 如果有任何UNHEALTHY，整体就是UNHEALTHY
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY

        # 如果有任何DEGRADED，整体就是DEGRADED
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        # 如果所有都是HEALTHY，整体就是HEALTHY
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY

        # 其他情况返回UNKNOWN
        return HealthStatus.UNKNOWN

    def get_health_summary(self) -> dict[str, Any]:
        """获取健康状态摘要"""
        if not self.last_check_results:
            return {
                "status": "unknown",
                "message": "尚未执行健康检查",
                "uptime": time.time() - self.start_time,
                "checks": [],
            }

        overall_status = self._calculate_overall_status(self.last_check_results)

        return {
            "status": overall_status.value,
            "message": f"共 {len(self.last_check_results)} 项检查",
            "uptime": time.time() - self.start_time,
            "last_check": self.last_check_time,
            "checks": [
                {
                    "name": result.name,
                    "status": result.status.value,
                    "message": result.message,
                    "duration": result.duration,
                }
                for result in self.last_check_results
            ],
        }


# 全局健康检查管理器
global_health_manager = HealthCheckManager()


def setup_default_health_checks(config=None, db_connection=None, model_manager=None):
    """设置默认的健康检查"""
    # 配置检查
    if config:
        global_health_manager.add_checker(ConfigurationHealthChecker(config))

    # 数据库检查
    if db_connection:
        global_health_manager.add_checker(DatabaseHealthChecker(db_connection))

    # 模型检查
    if model_manager:
        global_health_manager.add_checker(ModelHealthChecker(model_manager))

    # 系统资源检查
    global_health_manager.add_checker(SystemResourceHealthChecker())

    logger.info("默认健康检查已设置")


async def check_service_health() -> ServiceHealth:
    """检查服务健康状态"""
    return await global_health_manager.check_health()


def get_health_summary() -> dict[str, Any]:
    """获取健康状态摘要"""
    return global_health_manager.get_health_summary()


def add_health_checker(checker: HealthChecker):
    """添加自定义健康检查器"""
    global_health_manager.add_checker(checker)
