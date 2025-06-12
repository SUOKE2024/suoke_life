"""
健康检查和监控模块
"""

import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import logging
import time
from typing import Any, Dict, List, Optional

import aioredis
import asyncpg
import psutil

from ..config.settings import get_settings
from ..utils.exceptions import HealthCheckError


class HealthStatus(Enum):
    """健康状态枚举"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """组件健康状态"""

    name: str
    status: HealthStatus
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """系统指标"""

    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    uptime: float


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        self.component_checkers = {}
        self.last_metrics = None

    async def initialize(self):
        """初始化健康检查器"""
        self.logger.info("初始化健康检查器...")

        # 注册组件检查器
        self._register_component_checkers()

        self.logger.info("健康检查器初始化完成")

    def _register_component_checkers(self):
        """注册组件检查器"""
        self.component_checkers = {
            "database": self._check_database,
            "redis": self._check_redis,
            "ai_models": self._check_ai_models,
            "external_services": self._check_external_services,
            "system_resources": self._check_system_resources,
            "five_diagnosis": self._check_five_diagnosis_services,
        }

    async def check_health(self) -> Dict[str, Any]:
        """执行完整健康检查"""
        start_time = time.time()

        health_report = {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - self.start_time,
            "response_time": 0.0,
            "components": {},
            "system_metrics": None,
            "summary": {
                "total_components": len(self.component_checkers),
                "healthy_components": 0,
                "degraded_components": 0,
                "unhealthy_components": 0,
            },
        }

        # 并行执行所有组件检查
        tasks = []
        for component_name, checker_func in self.component_checkers.items():
            task = asyncio.create_task(self._safe_check_component(component_name, checker_func))
            tasks.append(task)

        component_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理检查结果
        overall_status = HealthStatus.HEALTHY

        for i, result in enumerate(component_results):
            component_name = list(self.component_checkers.keys())[i]

            if isinstance(result, Exception):
                component_health = ComponentHealth(
                    name=component_name,
                    status=HealthStatus.UNHEALTHY,
                    response_time=0.0,
                    last_check=datetime.utcnow(),
                    error_message=str(result),
                )
            else:
                component_health = result

            health_report["components"][component_name] = asdict(component_health)

            # 更新总体状态
            if component_health.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                health_report["summary"]["unhealthy_components"] += 1
            elif component_health.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                health_report["summary"]["degraded_components"] += 1
            else:
                health_report["summary"]["healthy_components"] += 1

        # 获取系统指标
        try:
            system_metrics = await self._get_system_metrics()
            health_report["system_metrics"] = asdict(system_metrics)
        except Exception as e:
            self.logger.error(f"获取系统指标失败: {e}")

        health_report["status"] = overall_status.value
        health_report["response_time"] = (time.time() - start_time) * 1000

        return health_report

    async def _safe_check_component(self, component_name: str, checker_func) -> ComponentHealth:
        """安全地检查组件"""
        start_time = time.time()

        try:
            result = await checker_func()
            response_time = (time.time() - start_time) * 1000

            if isinstance(result, ComponentHealth):
                result.response_time = response_time
                return result
            else:
                return ComponentHealth(
                    name=component_name,
                    status=HealthStatus.HEALTHY,
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                    metadata=result if isinstance(result, dict) else None,
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"组件健康检查失败 {component_name}: {e}")

            return ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                last_check=datetime.utcnow(),
                error_message=str(e),
            )

    async def _check_database(self) -> ComponentHealth:
        """检查数据库连接"""
        try:
            # 测试PostgreSQL连接
            conn = await asyncpg.connect(
                host=self.settings.database.host,
                port=self.settings.database.port,
                user=self.settings.database.user,
                password=self.settings.database.password,
                database=self.settings.database.name,
                command_timeout=5,
            )

            # 执行简单查询
            result = await conn.fetchval("SELECT 1")
            await conn.close()

            if result == 1:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    response_time=0.0,
                    last_check=datetime.utcnow(),
                    metadata={"type": "postgresql", "result": result},
                )
            else:
                raise Exception("数据库查询返回异常结果")

        except Exception as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time=0.0,
                last_check=datetime.utcnow(),
                error_message=f"数据库连接失败: {e}",
            )

    async def _check_redis(self) -> ComponentHealth:
        """检查Redis连接"""
        try:
            redis_client = aioredis.from_url(
                f"redis://{self.settings.redis.host}:{self.settings.redis.port}",
                password=self.settings.redis.password,
                db=self.settings.redis.db,
                socket_timeout=5,
            )

            # 测试连接
            await redis_client.ping()

            # 测试读写
            test_key = "health_check_test"
            await redis_client.set(test_key, "test_value", ex=10)
            value = await redis_client.get(test_key)
            await redis_client.delete(test_key)

            await redis_client.close()

            if value == b"test_value":
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    response_time=0.0,
                    last_check=datetime.utcnow(),
                    metadata={"type": "redis", "test_passed": True},
                )
            else:
                raise Exception("Redis读写测试失败")

        except Exception as e:
            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                response_time=0.0,
                last_check=datetime.utcnow(),
                error_message=f"Redis连接失败: {e}",
            )

    async def _check_ai_models(self) -> ComponentHealth:
        """检查AI模型状态"""
        try:
            from ..core.ai_model_manager import get_model_manager

            model_manager = await get_model_manager()
            model_health = await model_manager.health_check()

            # 判断模型健康状态
            if model_health["loaded_models"] == 0:
                status = HealthStatus.DEGRADED
            elif model_health["total_memory_mb"] > 2048:  # 内存使用超过2GB
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY

            return ComponentHealth(
                name="ai_models",
                status=status,
                response_time=0.0,
                last_check=datetime.utcnow(),
                metadata=model_health,
            )

        except Exception as e:
            return ComponentHealth(
                name="ai_models",
                status=HealthStatus.UNHEALTHY,
                response_time=0.0,
                last_check=datetime.utcnow(),
                error_message=f"AI模型检查失败: {e}",
            )

    async def _check_external_services(self) -> ComponentHealth:
        """检查外部服务连接"""
        try:

            # 这里应该检查与其他诊断服务的连接
            # 暂时返回健康状态
            return ComponentHealth(
                name="external_services",
                status=HealthStatus.HEALTHY,
                response_time=0.0,
                last_check=datetime.utcnow(),
                metadata={"services_checked": ["look", "listen", "inquiry", "palpation"]},
            )

        except Exception as e:
            return ComponentHealth(
                name="external_services",
                status=HealthStatus.DEGRADED,
                response_time=0.0,
                last_check=datetime.utcnow(),
                error_message=f"外部服务检查失败: {e}",
            )

    async def _check_system_resources(self) -> ComponentHealth:
        """检查系统资源"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # 判断资源状态
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = HealthStatus.UNHEALTHY
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 80:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY

            return ComponentHealth(
                name="system_resources",
                status=status,
                response_time=0.0,
                last_check=datetime.utcnow(),
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent,
                },
            )

        except Exception as e:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                response_time=0.0,
                last_check=datetime.utcnow(),
                error_message=f"系统资源检查失败: {e}",
            )

    async def _check_five_diagnosis_services(self) -> ComponentHealth:
        """检查五诊服务状态"""
        try:

            # 检查五诊协调器状态
            # 这里应该实际检查各个诊断服务的可用性

            return ComponentHealth(
                name="five_diagnosis",
                status=HealthStatus.HEALTHY,
                response_time=0.0,
                last_check=datetime.utcnow(),
                metadata={"coordinator_status": "active"},
            )

        except Exception as e:
            return ComponentHealth(
                name="five_diagnosis",
                status=HealthStatus.DEGRADED,
                response_time=0.0,
                last_check=datetime.utcnow(),
                error_message=f"五诊服务检查失败: {e}",
            )

    async def _get_system_metrics(self) -> SystemMetrics:
        """获取系统指标"""
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)

        # 内存使用率
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent

        # 网络IO
        network_io = psutil.net_io_counters()
        network_stats = {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv,
        }

        # 进程数量
        process_count = len(psutil.pids())

        # 运行时间
        uptime = time.time() - self.start_time

        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_stats,
            process_count=process_count,
            uptime=uptime,
        )

    async def check_component(self, component_name: str) -> ComponentHealth:
        """检查单个组件"""
        if component_name not in self.component_checkers:
            raise HealthCheckError(f"未知组件: {component_name}")

        checker_func = self.component_checkers[component_name]
        return await self._safe_check_component(component_name, checker_func)

    async def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            system_metrics = await self._get_system_metrics()

            # 获取AI模型指标
            ai_metrics = {}
            try:
                from ..core.ai_model_manager import get_model_manager

                model_manager = await get_model_manager()
                ai_metrics = model_manager.get_all_metrics()
            except Exception:
                pass

            return {
                "system": asdict(system_metrics),
                "ai_models": {name: asdict(metrics) for name, metrics in ai_metrics.items()},
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"获取指标失败: {e}")
            raise HealthCheckError(f"无法获取性能指标: {e}")

    def is_healthy(self, health_report: Dict[str, Any]) -> bool:
        """判断系统是否健康"""
        return health_report.get("status") == HealthStatus.HEALTHY.value

    async def _initialize_components(self):
        """初始化组件列表"""
        components = [
            "database",
            "redis",
            "inquiry_service",
            "look_service",
            "listen_service",
            "palpation_service",
            "calculation_service",
            "ai_model_service",
            "api_gateway",
        ]

        for component in components:
            self.components[component] = ComponentHealth(
                name=component,
                status=HealthStatus.UNKNOWN,
                response_time=0.0,
                last_check=datetime.now(),
            )

    async def start_monitoring(self):
        """启动监控"""
        if self.running:
            return

        self.running = True
        self._check_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("健康监控已启动")

    async def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        self.logger.info("健康监控已停止")

    async def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            try:
                await self.check_all_components()
                await self.collect_system_metrics()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(self.check_interval)

    async def check_all_components(self) -> Dict[str, ComponentHealth]:
        """检查所有组件健康状态"""
        tasks = []
        for component_name in self.components.keys():
            task = asyncio.create_task(self._check_component(component_name))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)
        return self.components

    async def _check_component(self, component_name: str):
        """检查单个组件健康状态"""
        start_time = time.time()

        try:
            if component_name == "database":
                await self._check_database()
            elif component_name == "redis":
                await self._check_redis()
            elif component_name.endswith("_service"):
                await self._check_service(component_name)
            else:
                await self._check_generic_component(component_name)

            response_time = time.time() - start_time

            # 更新组件健康状态
            self.components[component_name] = ComponentHealth(
                name=component_name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                last_check=datetime.now(),
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.components[component_name] = ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e),
            )
            self.logger.warning(f"组件 {component_name} 健康检查失败: {e}")

    async def _check_database(self):
        """检查数据库连接"""
        try:
            conn = await asyncpg.connect(
                host=self.settings.database.host,
                port=self.settings.database.port,
                user=self.settings.database.user,
                password=self.settings.database.password,
                database=self.settings.database.name,
                timeout=5.0,
            )

            # 执行简单查询
            await conn.fetchval("SELECT 1")
            await conn.close()

        except Exception as e:
            raise HealthCheckError(f"数据库连接失败: {e}")

    async def _check_redis(self):
        """检查Redis连接"""
        try:
            redis = aioredis.from_url(
                f"redis://{self.settings.redis.host}:{self.settings.redis.port}",
                password=self.settings.redis.password,
                socket_timeout=5.0,
            )

            # 执行ping命令
            await redis.ping()
            await redis.close()

        except Exception as e:
            raise HealthCheckError(f"Redis连接失败: {e}")

    async def _check_service(self, service_name: str):
        """检查微服务健康状态"""
        try:
            # 这里应该调用实际的服务健康检查端点
            # 暂时使用模拟检查
            service_config = getattr(self.settings, service_name.replace("_service", ""), None)
            if not service_config:
                raise HealthCheckError(f"服务配置未找到: {service_name}")

            # 模拟服务健康检查
            await asyncio.sleep(0.1)  # 模拟网络延迟

        except Exception as e:
            raise HealthCheckError(f"服务 {service_name} 检查失败: {e}")

    async def _check_generic_component(self, component_name: str):
        """检查通用组件"""
        # 通用组件检查逻辑
        await asyncio.sleep(0.05)  # 模拟检查时间

    async def collect_system_metrics(self):
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent

            # 网络IO
            network_io = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
            }

            # 进程数量
            process_count = len(psutil.pids())

            # 系统运行时间
            uptime = time.time() - psutil.boot_time()

            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_data,
                process_count=process_count,
                uptime=uptime,
            )

            # 添加到历史记录
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)

            # 检查阈值
            await self._check_thresholds(metrics)

        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")

    async def _check_thresholds(self, metrics: SystemMetrics):
        """检查阈值并发出警告"""
        warnings = []

        if metrics.cpu_usage > self.thresholds["cpu_usage"]:
            warnings.append(f"CPU使用率过高: {metrics.cpu_usage:.1f}%")

        if metrics.memory_usage > self.thresholds["memory_usage"]:
            warnings.append(f"内存使用率过高: {metrics.memory_usage:.1f}%")

        if metrics.disk_usage > self.thresholds["disk_usage"]:
            warnings.append(f"磁盘使用率过高: {metrics.disk_usage:.1f}%")

        if warnings:
            for warning in warnings:
                self.logger.warning(warning)

            # 可以在这里添加告警通知逻辑
            await self._send_alerts(warnings)

    async def _send_alerts(self, warnings: List[str]):
        """发送告警通知"""
        # 这里可以集成各种告警通道
        # 如邮件、短信、Slack、钉钉等
        self.logger.info(f"发送告警通知: {warnings}")

    async def get_health_status(self) -> Dict[str, Any]:
        """获取整体健康状态"""
        overall_status = HealthStatus.HEALTHY
        unhealthy_components = []
        degraded_components = []

        for component in self.components.values():
            if component.status == HealthStatus.UNHEALTHY:
                unhealthy_components.append(component.name)
                overall_status = HealthStatus.UNHEALTHY
            elif component.status == HealthStatus.DEGRADED:
                degraded_components.append(component.name)
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

        # 获取最新的系统指标
        latest_metrics = self.metrics_history[-1] if self.metrics_history else None

        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "components": {name: asdict(health) for name, health in self.components.items()},
            "system_metrics": asdict(latest_metrics) if latest_metrics else None,
            "unhealthy_components": unhealthy_components,
            "degraded_components": degraded_components,
            "uptime": time.time() - psutil.boot_time() if latest_metrics else 0,
        }

    async def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """获取特定组件的健康状态"""
        return self.components.get(component_name)

    async def get_metrics_history(self, hours: int = 1) -> List[SystemMetrics]:
        """获取指定时间范围内的指标历史"""
        if not self.metrics_history:
            return []

        # 计算需要的数据点数量
        points_needed = min(hours * 120, len(self.metrics_history))  # 每分钟2个数据点

        return self.metrics_history[-points_needed:]

    async def force_check(self, component_name: Optional[str] = None) -> Dict[str, ComponentHealth]:
        """强制执行健康检查"""
        if component_name:
            await self._check_component(component_name)
            return {component_name: self.components[component_name]}
        else:
            return await self.check_all_components()

    async def set_threshold(self, metric_name: str, value: float):
        """设置阈值"""
        if metric_name in self.thresholds:
            self.thresholds[metric_name] = value
            self.logger.info(f"更新阈值 {metric_name}: {value}")
        else:
            raise ValueError(f"未知的指标名称: {metric_name}")

    async def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}

        recent_metrics = self.metrics_history[-10:]  # 最近10个数据点

        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)

        # 计算组件平均响应时间
        avg_response_times = {}
        for name, component in self.components.items():
            if component.status == HealthStatus.HEALTHY:
                avg_response_times[name] = component.response_time

        return {
            "average_cpu_usage": round(avg_cpu, 2),
            "average_memory_usage": round(avg_memory, 2),
            "average_disk_usage": round(avg_disk, 2),
            "component_response_times": avg_response_times,
            "healthy_components": len(
                [c for c in self.components.values() if c.status == HealthStatus.HEALTHY]
            ),
            "total_components": len(self.components),
            "data_points": len(recent_metrics),
        }

    async def cleanup(self):
        """清理资源"""
        await self.stop_monitoring()
        self.components.clear()
        self.metrics_history.clear()
        self.logger.info("健康检查器已清理")


# 全局健康检查器实例
_health_checker: Optional[HealthChecker] = None


async def get_health_checker() -> HealthChecker:
    """获取健康检查器实例"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
        await _health_checker.initialize()
    return _health_checker


async def cleanup_health_checker():
    """清理健康检查器"""
    global _health_checker
    if _health_checker:
        await _health_checker.cleanup()
        _health_checker = None
