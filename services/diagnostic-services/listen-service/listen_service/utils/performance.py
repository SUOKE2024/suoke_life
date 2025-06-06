"""
performance - 索克生活项目模块
"""

        import psutil
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, List, TypeVar
import asyncio
import functools
import structlog
import threading
import time

"""
性能监控工具

提供异步函数性能监控、计时器和性能统计功能。
"""



logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class PerformanceMetrics:
    """性能指标"""

    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_count: int = 0

    @property
    def average_time(self) -> float:
        """平均执行时间"""
        return self.total_time / self.total_calls if self.total_calls > 0 else 0.0

    @property
    def recent_average_time(self) -> float:
        """最近的平均执行时间"""
        return (
            sum(self.recent_times) / len(self.recent_times)
            if self.recent_times
            else 0.0
        )

    def update(self, execution_time: float, is_error: bool = False) -> None:
        """更新性能指标"""
        self.total_calls += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.recent_times.append(execution_time)

        if is_error:
            self.error_count += 1


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics: dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self._lock = threading.Lock()

    def record(
        self, function_name: str, execution_time: float, is_error: bool = False
    ) -> None:
        """记录性能数据"""
        with self._lock:
            self.metrics[function_name].update(execution_time, is_error)

    def get_metrics(
        self, function_name: str | None = None
    ) -> dict[str, dict[str, Any]] | dict[str, Any]:
        """获取性能指标"""
        with self._lock:
            if function_name:
                metrics = self.metrics.get(function_name)
                if metrics:
                    return {
                        "total_calls": metrics.total_calls,
                        "total_time": metrics.total_time,
                        "average_time": metrics.average_time,
                        "recent_average_time": metrics.recent_average_time,
                        "min_time": metrics.min_time
                        if metrics.min_time != float("inf")
                        else 0.0,
                        "max_time": metrics.max_time,
                        "error_count": metrics.error_count,
                        "error_rate": metrics.error_count / metrics.total_calls
                        if metrics.total_calls > 0
                        else 0.0,
                    }
                return {}

            # 返回所有函数的指标
            result = {}
            for name, metrics in self.metrics.items():
                result[name] = {
                    "total_calls": metrics.total_calls,
                    "total_time": metrics.total_time,
                    "average_time": metrics.average_time,
                    "recent_average_time": metrics.recent_average_time,
                    "min_time": metrics.min_time
                    if metrics.min_time != float("inf")
                    else 0.0,
                    "max_time": metrics.max_time,
                    "error_count": metrics.error_count,
                    "error_rate": metrics.error_count / metrics.total_calls
                    if metrics.total_calls > 0
                    else 0.0,
                }
            return result

    def reset(self, function_name: str | None = None) -> None:
        """重置性能指标"""
        with self._lock:
            if function_name:
                if function_name in self.metrics:
                    del self.metrics[function_name]
            else:
                self.metrics.clear()


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def async_timer(func: F) -> F:
    """
    异步函数性能计时装饰器

    自动记录异步函数的执行时间和性能指标。
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        function_name = f"{func.__module__}.{func.__qualname__}"
        start_time = time.time()
        is_error = False

        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            is_error = True
            logger.error(
                "异步函数执行异常", function=function_name, error=str(e), exc_info=True
            )
            raise
        finally:
            execution_time = time.time() - start_time
            performance_monitor.record(function_name, execution_time, is_error)

            # 记录性能日志
            if execution_time > 5.0:  # 超过5秒的慢查询
                logger.warning(
                    "检测到慢查询",
                    function=function_name,
                    execution_time=execution_time,
                    args_count=len(args),
                    kwargs_count=len(kwargs),
                )
            else:
                logger.debug(
                    "函数执行完成",
                    function=function_name,
                    execution_time=execution_time,
                )

    return wrapper


def sync_timer(func: F) -> F:
    """
    同步函数性能计时装饰器
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        function_name = f"{func.__module__}.{func.__qualname__}"
        start_time = time.time()
        is_error = False

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            is_error = True
            logger.error(
                "同步函数执行异常", function=function_name, error=str(e), exc_info=True
            )
            raise
        finally:
            execution_time = time.time() - start_time
            performance_monitor.record(function_name, execution_time, is_error)

            # 记录性能日志
            if execution_time > 2.0:  # 超过2秒的慢查询
                logger.warning(
                    "检测到慢查询",
                    function=function_name,
                    execution_time=execution_time,
                )
            else:
                logger.debug(
                    "函数执行完成",
                    function=function_name,
                    execution_time=execution_time,
                )

    return wrapper


class AsyncContextTimer:
    """异步上下文管理器计时器"""

    def __init__(self, name: str, log_slow_threshold: float = 1.0):
        self.name = name
        self.log_slow_threshold = log_slow_threshold
        self.start_time: float | None = None
        self.execution_time: float | None = None

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            self.execution_time = time.time() - self.start_time
            is_error = exc_type is not None

            performance_monitor.record(self.name, self.execution_time, is_error)

            if self.execution_time > self.log_slow_threshold:
                logger.warning(
                    "上下文执行时间过长",
                    context=self.name,
                    execution_time=self.execution_time,
                    has_error=is_error,
                )
            else:
                logger.debug(
                    "上下文执行完成",
                    context=self.name,
                    execution_time=self.execution_time,
                )


class PerformanceProfiler:
    """性能分析器"""

    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self.is_profiling = False
        self.profile_data = []
        self._profile_task: asyncio.Task | None = None

    async def start_profiling(self) -> None:
        """开始性能分析"""
        if self.is_profiling:
            return

        self.is_profiling = True
        self.profile_data.clear()
        self._profile_task = asyncio.create_task(self._profile_loop())
        logger.info("性能分析已启动")

    async def stop_profiling(self) -> dict[str, Any]:
        """停止性能分析并返回结果"""
        if not self.is_profiling:
            return {}

        self.is_profiling = False

        if self._profile_task:
            self._profile_task.cancel()
            try:
                await self._profile_task
            except asyncio.CancelledError:
                pass

        # 分析数据
        result = self._analyze_profile_data()
        logger.info("性能分析已停止", profile_samples=len(self.profile_data))

        return result

    async def _profile_loop(self) -> None:
        """性能分析循环"""
        try:
            while self.is_profiling:
                # 收集当前性能数据
                sample = {
                    "timestamp": time.time(),
                    "metrics": performance_monitor.get_metrics(),
                }
                self.profile_data.append(sample)

                await asyncio.sleep(self.sample_interval)
        except asyncio.CancelledError:
            pass

    def _analyze_profile_data(self) -> dict[str, Any]:
        """分析性能数据"""
        if not self.profile_data:
            return {}

        # 计算各函数的性能趋势
        function_trends = defaultdict(list)

        for sample in self.profile_data:
            for func_name, metrics in sample["metrics"].items():
                function_trends[func_name].append(
                    {
                        "timestamp": sample["timestamp"],
                        "average_time": metrics["average_time"],
                        "total_calls": metrics["total_calls"],
                        "error_rate": metrics["error_rate"],
                    }
                )

        # 生成分析报告
        analysis = {
            "profile_duration": self.profile_data[-1]["timestamp"]
            - self.profile_data[0]["timestamp"],
            "total_samples": len(self.profile_data),
            "function_analysis": {},
        }

        for func_name, trend_data in function_trends.items():
            if len(trend_data) < 2:
                continue

            # 计算性能趋势
            start_metrics = trend_data[0]
            end_metrics = trend_data[-1]

            call_rate = (
                end_metrics["total_calls"] - start_metrics["total_calls"]
            ) / analysis["profile_duration"]
            avg_time_change = (
                end_metrics["average_time"] - start_metrics["average_time"]
            )

            analysis["function_analysis"][func_name] = {
                "call_rate": call_rate,
                "average_time_change": avg_time_change,
                "final_average_time": end_metrics["average_time"],
                "final_error_rate": end_metrics["error_rate"],
                "samples": len(trend_data),
            }

        return analysis


# 全局性能分析器实例
profiler = PerformanceProfiler()


async def get_system_performance() -> dict[str, Any]:
    """获取系统性能信息"""
    try:

        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用情况
        memory = psutil.virtual_memory()

        # 磁盘使用情况
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100,
            },
            "timestamp": time.time(),
        }
    except ImportError:
        logger.warning("psutil 未安装，无法获取系统性能信息")
        return {"error": "psutil not available"}
    except Exception as e:
        logger.error("获取系统性能信息失败", error=str(e))
        return {"error": str(e)}


class PerformanceAlert:
    """性能告警"""

    def __init__(self, thresholds: dict[str, float] | None = None):
        self.thresholds = thresholds or {
            "max_average_time": 5.0,  # 最大平均执行时间
            "max_error_rate": 0.1,  # 最大错误率
            "max_cpu_percent": 80.0,  # 最大CPU使用率
            "max_memory_percent": 85.0,  # 最大内存使用率
        }
        self.alert_callbacks = []

    def add_alert_callback(
        self, callback: Callable[[str, dict[str, Any]], None]
    ) -> None:
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)

    async def check_performance_alerts(self) -> List[dict[str, Any]]:
        """检查性能告警"""
        alerts = []

        # 检查函数性能
        metrics = performance_monitor.get_metrics()
        for func_name, func_metrics in metrics.items():
            if func_metrics["average_time"] > self.thresholds["max_average_time"]:
                alert = {
                    "type": "slow_function",
                    "function": func_name,
                    "average_time": func_metrics["average_time"],
                    "threshold": self.thresholds["max_average_time"],
                    "severity": "warning",
                }
                alerts.append(alert)

            if func_metrics["error_rate"] > self.thresholds["max_error_rate"]:
                alert = {
                    "type": "high_error_rate",
                    "function": func_name,
                    "error_rate": func_metrics["error_rate"],
                    "threshold": self.thresholds["max_error_rate"],
                    "severity": "critical",
                }
                alerts.append(alert)

        # 检查系统性能
        system_perf = await get_system_performance()
        if "error" not in system_perf:
            if system_perf.get("cpu_percent", 0) > self.thresholds["max_cpu_percent"]:
                alert = {
                    "type": "high_cpu_usage",
                    "cpu_percent": system_perf["cpu_percent"],
                    "threshold": self.thresholds["max_cpu_percent"],
                    "severity": "warning",
                }
                alerts.append(alert)

            memory_percent = system_perf.get("memory", {}).get("percent", 0)
            if memory_percent > self.thresholds["max_memory_percent"]:
                alert = {
                    "type": "high_memory_usage",
                    "memory_percent": memory_percent,
                    "threshold": self.thresholds["max_memory_percent"],
                    "severity": "critical",
                }
                alerts.append(alert)

        # 触发告警回调
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert["type"], alert)
                except Exception as e:
                    logger.error("告警回调执行失败", error=str(e))

        return alerts


# 全局性能告警实例
performance_alert = PerformanceAlert()
