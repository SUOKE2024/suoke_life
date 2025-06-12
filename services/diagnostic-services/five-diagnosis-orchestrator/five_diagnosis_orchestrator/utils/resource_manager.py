"""
资源管理器

管理五诊协同诊断系统的系统资源，包括内存、CPU、连接池等
"""

import asyncio
import gc
import logging
import threading
import time
import weakref
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """资源类型"""

    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    NETWORK = "network"
    CONNECTION = "connection"
    FILE_HANDLE = "file_handle"


class ResourceStatus(Enum):
    """资源状态"""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


@dataclass
class ResourceThreshold:
    """资源阈值"""

    warning_threshold: float = 0.7  # 70%
    critical_threshold: float = 0.9  # 90%
    max_threshold: float = 0.95  # 95%


@dataclass
class ResourceMetrics:
    """资源指标"""

    # 内存指标
    memory_usage_percent: float = 0.0
    memory_available_mb: float = 0.0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0

    # CPU指标
    cpu_usage_percent: float = 0.0
    cpu_count: int = 0
    load_average: List[float] = field(default_factory=list)

    # 磁盘指标
    disk_usage_percent: float = 0.0
    disk_free_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0

    # 网络指标
    network_connections: int = 0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0

    # 进程指标
    process_count: int = 0
    thread_count: int = 0
    file_descriptors: int = 0

    # 应用指标
    active_sessions: int = 0
    connection_pool_size: int = 0
    cache_size: int = 0

    # 时间戳
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceAlert:
    """资源告警"""

    resource_type: ResourceType
    status: ResourceStatus
    message: str
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ResourceManager:
    """资源管理器"""

    def __init__(
        self,
        monitoring_interval: int = 30,  # 监控间隔（秒）
        cleanup_interval: int = 300,  # 清理间隔（秒）
        enable_auto_cleanup: bool = True,
        enable_gc_optimization: bool = True,
    ):
        self.monitoring_interval = monitoring_interval
        self.cleanup_interval = cleanup_interval
        self.enable_auto_cleanup = enable_auto_cleanup
        self.enable_gc_optimization = enable_gc_optimization

        # 资源阈值
        self.thresholds = {
            ResourceType.MEMORY: ResourceThreshold(0.7, 0.85, 0.95),
            ResourceType.CPU: ResourceThreshold(0.7, 0.85, 0.95),
            ResourceType.DISK: ResourceThreshold(0.8, 0.9, 0.95),
            ResourceType.NETWORK: ResourceThreshold(0.7, 0.85, 0.95),
            ResourceType.CONNECTION: ResourceThreshold(0.7, 0.85, 0.95),
            ResourceType.FILE_HANDLE: ResourceThreshold(0.7, 0.85, 0.95),
        }

        # 监控数据
        self.current_metrics = ResourceMetrics()
        self.metrics_history: List[ResourceMetrics] = []
        self.max_history_size = 1440  # 保留24小时的数据（每分钟一个）

        # 告警
        self.active_alerts: List[ResourceAlert] = []
        self.alert_callbacks: List[Callable[[ResourceAlert], None]] = []

        # 连接池管理
        self.connection_pools: Dict[str, Any] = {}
        self.max_connections_per_pool = 100

        # 资源清理回调
        self.cleanup_callbacks: List[Callable[[], None]] = []

        # 控制
        self._shutdown = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        # 进程信息
        self.process = psutil.Process()

        # 锁
        self._metrics_lock = asyncio.Lock()
        self._alerts_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化资源管理器"""
        logger.info("初始化资源管理器...")

        try:
            # 获取初始指标
            await self._collect_metrics()

            # 启动监控任务
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

            # 启动清理任务
            if self.enable_auto_cleanup:
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            # 配置垃圾回收
            if self.enable_gc_optimization:
                self._configure_gc()

            logger.info("资源管理器初始化完成")

        except Exception as e:
            logger.error(f"资源管理器初始化失败: {e}")
            raise

    def _configure_gc(self) -> None:
        """配置垃圾回收"""
        # 设置垃圾回收阈值
        gc.set_threshold(700, 10, 10)

        # 启用垃圾回收调试（开发环境）
        # gc.set_debug(gc.DEBUG_STATS)

    async def _monitoring_loop(self) -> None:
        """监控循环"""
        logger.info("启动资源监控循环...")

        while not self._shutdown:
            try:
                # 收集指标
                await self._collect_metrics()

                # 检查告警
                await self._check_alerts()

                # 清理历史数据
                await self._cleanup_history()

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"资源监控异常: {e}")
                await asyncio.sleep(5)

    async def _cleanup_loop(self) -> None:
        """清理循环"""
        logger.info("启动资源清理循环...")

        while not self._shutdown:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(self.cleanup_interval)

            except Exception as e:
                logger.error(f"资源清理异常: {e}")
                await asyncio.sleep(30)

    async def _collect_metrics(self) -> None:
        """收集资源指标"""
        async with self._metrics_lock:
            try:
                metrics = ResourceMetrics()

                # 内存指标
                memory = psutil.virtual_memory()
                metrics.memory_usage_percent = memory.percent
                metrics.memory_available_mb = memory.available / 1024 / 1024
                metrics.memory_used_mb = memory.used / 1024 / 1024
                metrics.memory_total_mb = memory.total / 1024 / 1024

                # CPU指标
                metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
                metrics.cpu_count = psutil.cpu_count()
                try:
                    metrics.load_average = list(psutil.getloadavg())
                except AttributeError:
                    # Windows不支持getloadavg
                    metrics.load_average = [0.0, 0.0, 0.0]

                # 磁盘指标
                disk = psutil.disk_usage("/")
                metrics.disk_usage_percent = disk.percent
                metrics.disk_free_gb = disk.free / 1024 / 1024 / 1024
                metrics.disk_used_gb = disk.used / 1024 / 1024 / 1024
                metrics.disk_total_gb = disk.total / 1024 / 1024 / 1024

                # 网络指标
                try:
                    connections = psutil.net_connections()
                    metrics.network_connections = len(connections)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    metrics.network_connections = 0

                net_io = psutil.net_io_counters()
                if net_io:
                    metrics.network_bytes_sent = net_io.bytes_sent
                    metrics.network_bytes_recv = net_io.bytes_recv

                # 进程指标
                metrics.process_count = len(psutil.pids())
                try:
                    metrics.thread_count = self.process.num_threads()
                    metrics.file_descriptors = (
                        self.process.num_fds()
                        if hasattr(self.process, "num_fds")
                        else 0
                    )
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    metrics.thread_count = 0
                    metrics.file_descriptors = 0

                # 应用指标
                metrics.connection_pool_size = sum(
                    len(pool) if hasattr(pool, "__len__") else 0
                    for pool in self.connection_pools.values()
                )

                self.current_metrics = metrics

                # 添加到历史记录
                self.metrics_history.append(metrics)

            except Exception as e:
                logger.error(f"收集资源指标失败: {e}")

    async def _check_alerts(self) -> None:
        """检查资源告警"""
        async with self._alerts_lock:
            new_alerts = []

            # 检查内存使用
            memory_threshold = self.thresholds[ResourceType.MEMORY]
            memory_usage = self.current_metrics.memory_usage_percent / 100

            if memory_usage >= memory_threshold.max_threshold:
                alert = ResourceAlert(
                    resource_type=ResourceType.MEMORY,
                    status=ResourceStatus.EXHAUSTED,
                    message=f"内存使用率达到 {memory_usage*100:.1f}%，已接近耗尽",
                    value=memory_usage,
                    threshold=memory_threshold.max_threshold,
                )
                new_alerts.append(alert)
            elif memory_usage >= memory_threshold.critical_threshold:
                alert = ResourceAlert(
                    resource_type=ResourceType.MEMORY,
                    status=ResourceStatus.CRITICAL,
                    message=f"内存使用率达到 {memory_usage*100:.1f}%，处于危险水平",
                    value=memory_usage,
                    threshold=memory_threshold.critical_threshold,
                )
                new_alerts.append(alert)
            elif memory_usage >= memory_threshold.warning_threshold:
                alert = ResourceAlert(
                    resource_type=ResourceType.MEMORY,
                    status=ResourceStatus.WARNING,
                    message=f"内存使用率达到 {memory_usage*100:.1f}%，需要关注",
                    value=memory_usage,
                    threshold=memory_threshold.warning_threshold,
                )
                new_alerts.append(alert)

            # 检查CPU使用
            cpu_threshold = self.thresholds[ResourceType.CPU]
            cpu_usage = self.current_metrics.cpu_usage_percent / 100

            if cpu_usage >= cpu_threshold.critical_threshold:
                alert = ResourceAlert(
                    resource_type=ResourceType.CPU,
                    status=ResourceStatus.CRITICAL,
                    message=f"CPU使用率达到 {cpu_usage*100:.1f}%，处于高负载状态",
                    value=cpu_usage,
                    threshold=cpu_threshold.critical_threshold,
                )
                new_alerts.append(alert)
            elif cpu_usage >= cpu_threshold.warning_threshold:
                alert = ResourceAlert(
                    resource_type=ResourceType.CPU,
                    status=ResourceStatus.WARNING,
                    message=f"CPU使用率达到 {cpu_usage*100:.1f}%，负载较高",
                    value=cpu_usage,
                    threshold=cpu_threshold.warning_threshold,
                )
                new_alerts.append(alert)

            # 检查磁盘使用
            disk_threshold = self.thresholds[ResourceType.DISK]
            disk_usage = self.current_metrics.disk_usage_percent / 100

            if disk_usage >= disk_threshold.critical_threshold:
                alert = ResourceAlert(
                    resource_type=ResourceType.DISK,
                    status=ResourceStatus.CRITICAL,
                    message=f"磁盘使用率达到 {disk_usage*100:.1f}%，空间不足",
                    value=disk_usage,
                    threshold=disk_threshold.critical_threshold,
                )
                new_alerts.append(alert)
            elif disk_usage >= disk_threshold.warning_threshold:
                alert = ResourceAlert(
                    resource_type=ResourceType.DISK,
                    status=ResourceStatus.WARNING,
                    message=f"磁盘使用率达到 {disk_usage*100:.1f}%，建议清理",
                    value=disk_usage,
                    threshold=disk_threshold.warning_threshold,
                )
                new_alerts.append(alert)

            # 更新活跃告警
            self.active_alerts = new_alerts

            # 触发告警回调
            for alert in new_alerts:
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"告警回调执行失败: {e}")

    async def _cleanup_history(self) -> None:
        """清理历史数据"""
        if len(self.metrics_history) > self.max_history_size:
            # 保留最新的数据
            self.metrics_history = self.metrics_history[-self.max_history_size :]

    async def _perform_cleanup(self) -> None:
        """执行资源清理"""
        logger.debug("执行资源清理...")

        try:
            # 强制垃圾回收
            if self.enable_gc_optimization:
                collected = gc.collect()
                logger.debug(f"垃圾回收清理了 {collected} 个对象")

            # 执行自定义清理回调
            for callback in self.cleanup_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    logger.error(f"清理回调执行失败: {e}")

            # 清理连接池
            await self._cleanup_connection_pools()

            # 清理过期告警
            await self._cleanup_expired_alerts()

        except Exception as e:
            logger.error(f"资源清理失败: {e}")

    async def _cleanup_connection_pools(self) -> None:
        """清理连接池"""
        for pool_name, pool in self.connection_pools.items():
            try:
                if hasattr(pool, "cleanup"):
                    if asyncio.iscoroutinefunction(pool.cleanup):
                        await pool.cleanup()
                    else:
                        pool.cleanup()
            except Exception as e:
                logger.warning(f"清理连接池失败: {pool_name}, 错误: {e}")

    async def _cleanup_expired_alerts(self) -> None:
        """清理过期告警"""
        async with self._alerts_lock:
            # 清理1小时前的告警
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            self.active_alerts = [
                alert for alert in self.active_alerts if alert.timestamp > cutoff_time
            ]

    async def get_current_metrics(self) -> ResourceMetrics:
        """获取当前资源指标"""
        return self.current_metrics

    async def get_metrics_history(self, hours: int = 1) -> List[ResourceMetrics]:
        """获取历史指标"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            metrics
            for metrics in self.metrics_history
            if metrics.timestamp > cutoff_time
        ]

    async def get_active_alerts(self) -> List[ResourceAlert]:
        """获取活跃告警"""
        async with self._alerts_lock:
            return self.active_alerts.copy()

    def register_alert_callback(
        self, callback: Callable[[ResourceAlert], None]
    ) -> None:
        """注册告警回调"""
        self.alert_callbacks.append(callback)

    def register_cleanup_callback(self, callback: Callable[[], None]) -> None:
        """注册清理回调"""
        self.cleanup_callbacks.append(callback)

    async def register_connection_pool(self, name: str, pool: Any) -> None:
        """注册连接池"""
        self.connection_pools[name] = pool
        logger.info(f"注册连接池: {name}")

    async def unregister_connection_pool(self, name: str) -> None:
        """注销连接池"""
        if name in self.connection_pools:
            pool = self.connection_pools[name]

            # 尝试关闭连接池
            try:
                if hasattr(pool, "close"):
                    if asyncio.iscoroutinefunction(pool.close):
                        await pool.close()
                    else:
                        pool.close()
            except Exception as e:
                logger.warning(f"关闭连接池失败: {name}, 错误: {e}")

            del self.connection_pools[name]
            logger.info(f"注销连接池: {name}")

    async def force_cleanup(self) -> Dict[str, Any]:
        """强制执行清理"""
        logger.info("强制执行资源清理...")

        cleanup_results = {
            "gc_collected": 0,
            "callbacks_executed": 0,
            "pools_cleaned": 0,
            "alerts_cleared": 0,
        }

        try:
            # 强制垃圾回收
            if self.enable_gc_optimization:
                cleanup_results["gc_collected"] = gc.collect()

            # 执行清理回调
            for callback in self.cleanup_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                    cleanup_results["callbacks_executed"] += 1
                except Exception as e:
                    logger.error(f"清理回调执行失败: {e}")

            # 清理连接池
            for pool_name in list(self.connection_pools.keys()):
                try:
                    await self._cleanup_connection_pools()
                    cleanup_results["pools_cleaned"] += 1
                except Exception as e:
                    logger.error(f"清理连接池失败: {pool_name}, 错误: {e}")

            # 清理告警
            async with self._alerts_lock:
                cleanup_results["alerts_cleared"] = len(self.active_alerts)
                self.active_alerts.clear()

            logger.info(f"强制清理完成: {cleanup_results}")

        except Exception as e:
            logger.error(f"强制清理失败: {e}")

        return cleanup_results

    async def get_resource_summary(self) -> Dict[str, Any]:
        """获取资源摘要"""
        metrics = self.current_metrics
        alerts = await self.get_active_alerts()

        return {
            "memory": {
                "usage_percent": metrics.memory_usage_percent,
                "available_mb": metrics.memory_available_mb,
                "used_mb": metrics.memory_used_mb,
                "total_mb": metrics.memory_total_mb,
            },
            "cpu": {
                "usage_percent": metrics.cpu_usage_percent,
                "count": metrics.cpu_count,
                "load_average": metrics.load_average,
            },
            "disk": {
                "usage_percent": metrics.disk_usage_percent,
                "free_gb": metrics.disk_free_gb,
                "used_gb": metrics.disk_used_gb,
                "total_gb": metrics.disk_total_gb,
            },
            "network": {
                "connections": metrics.network_connections,
                "bytes_sent": metrics.network_bytes_sent,
                "bytes_recv": metrics.network_bytes_recv,
            },
            "process": {
                "count": metrics.process_count,
                "threads": metrics.thread_count,
                "file_descriptors": metrics.file_descriptors,
            },
            "application": {
                "active_sessions": metrics.active_sessions,
                "connection_pools": len(self.connection_pools),
                "connection_pool_size": metrics.connection_pool_size,
            },
            "alerts": {
                "total": len(alerts),
                "critical": len(
                    [a for a in alerts if a.status == ResourceStatus.CRITICAL]
                ),
                "warning": len(
                    [a for a in alerts if a.status == ResourceStatus.WARNING]
                ),
            },
            "timestamp": metrics.timestamp.isoformat(),
        }

    async def set_threshold(
        self, resource_type: ResourceType, threshold: ResourceThreshold
    ) -> None:
        """设置资源阈值"""
        self.thresholds[resource_type] = threshold
        logger.info(f"更新资源阈值: {resource_type.value}")

    async def get_threshold(self, resource_type: ResourceType) -> ResourceThreshold:
        """获取资源阈值"""
        return self.thresholds.get(resource_type, ResourceThreshold())

    async def close(self) -> None:
        """关闭资源管理器"""
        logger.info("关闭资源管理器...")

        self._shutdown = True

        # 取消监控任务
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        # 取消清理任务
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # 关闭所有连接池
        for pool_name in list(self.connection_pools.keys()):
            await self.unregister_connection_pool(pool_name)

        # 最后一次清理
        await self.force_cleanup()

        logger.info("资源管理器已关闭")


# 全局资源管理器实例
_global_resource_manager: Optional[ResourceManager] = None


async def get_resource_manager(**kwargs) -> ResourceManager:
    """获取全局资源管理器实例"""
    global _global_resource_manager
    if _global_resource_manager is None:
        _global_resource_manager = ResourceManager(**kwargs)
        await _global_resource_manager.initialize()
    return _global_resource_manager


async def close_global_resource_manager() -> None:
    """关闭全局资源管理器"""
    global _global_resource_manager
    if _global_resource_manager:
        await _global_resource_manager.close()
        _global_resource_manager = None


# 便捷函数
async def get_current_resource_metrics() -> ResourceMetrics:
    """获取当前资源指标的便捷函数"""
    manager = await get_resource_manager()
    return await manager.get_current_metrics()


async def get_resource_alerts() -> List[ResourceAlert]:
    """获取资源告警的便捷函数"""
    manager = await get_resource_manager()
    return await manager.get_active_alerts()


async def force_resource_cleanup() -> Dict[str, Any]:
    """强制资源清理的便捷函数"""
    manager = await get_resource_manager()
    return await manager.force_cleanup()


def resource_monitor(alert_callback: Optional[Callable[[ResourceAlert], None]] = None):
    """资源监控装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            manager = await get_resource_manager()

            if alert_callback:
                manager.register_alert_callback(alert_callback)

            # 记录执行前的资源状态
            before_metrics = await manager.get_current_metrics()

            try:
                # 执行函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                return result

            finally:
                # 记录执行后的资源状态
                after_metrics = await manager.get_current_metrics()

                # 计算资源使用变化
                memory_diff = (
                    after_metrics.memory_used_mb - before_metrics.memory_used_mb
                )
                if memory_diff > 100:  # 内存增长超过100MB
                    logger.warning(
                        f"函数 {func.__name__} 执行后内存增长 {memory_diff:.1f}MB"
                    )

            return wrapper

        return decorator
