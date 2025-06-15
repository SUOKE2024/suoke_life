#!/usr/bin/env python3
"""
优化的健康检查模块
通过并发优化、缓存机制和智能调度提升性能
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from .health_check import (
    HealthChecker,
    HealthCheckManager,
    HealthCheckResult,
    HealthStatus,
    global_health_manager,
)

logger = logging.getLogger(__name__)


@dataclass
class CheckerPerformanceStats:
    """检查器性能统计"""

    name: str
    avg_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    success_rate: float = 100.0
    total_runs: int = 0
    failed_runs: int = 0
    last_run_time: float = 0.0


class CachedHealthChecker(HealthChecker):
    """带缓存的健康检查器基类"""

    def __init__(self, name: str, timeout: float = 2.0, cache_ttl: float = 30.0):
        super().__init__(name, timeout)
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_lock = threading.Lock()

    async def check(self) -> HealthCheckResult:
        """带缓存的检查方法"""
        current_time = time.time()

        # 检查缓存
        with self._cache_lock:
            if self.name in self._cache:
                cached_result, cache_time = self._cache[self.name]
                if current_time - cache_time < self.cache_ttl:
                    # 返回缓存结果，但更新时间戳
                    cached_result.timestamp = current_time
                    return cached_result

        # 执行实际检查
        result = await super().check()

        # 更新缓存
        with self._cache_lock:
            self._cache[self.name] = (result, current_time)

        return result

    def clear_cache(self) -> None:
        """清除缓存"""
        with self._cache_lock:
            self._cache.clear()


class FastConfigurationChecker(CachedHealthChecker):
    """快速配置检查器"""

    def __init__(self, config=None, cache_ttl: float = 60.0):
        super().__init__("fast_configuration", timeout=0.5, cache_ttl=cache_ttl)
        self.config = config

    async def _perform_check(self) -> dict[str, Any]:
        """快速配置检查"""
        try:
            if not self.config:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": "配置对象未提供",
                    "details": {"config_available": False},
                }

            # 快速检查关键配置项
            essential_checks = {
                "has_version": hasattr(self.config, "version"),
                "has_service_config": hasattr(self.config, "service"),
                "config_loaded": True,
            }

            failed_checks = [k for k, v in essential_checks.items() if not v]

            if failed_checks:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": f"配置检查失败: {', '.join(failed_checks)}",
                    "details": essential_checks,
                }

            return {
                "status": HealthStatus.HEALTHY,
                "message": "配置完整",
                "details": essential_checks,
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"配置检查异常: {str(e)}",
                "details": {"error": str(e)},
            }


class FastSystemResourcesChecker(CachedHealthChecker):
    """快速系统资源检查器"""

    def __init__(self, cache_ttl: float = 15.0):
        super().__init__("fast_system_resources", timeout=1.0, cache_ttl=cache_ttl)
        self._last_cpu_check = 0
        self._cpu_cache = 0.0

    async def _perform_check(self) -> dict[str, Any]:
        """快速系统资源检查"""
        try:
            import psutil

            current_time = time.time()

            # CPU 检查 - 使用缓存减少频繁调用
            if current_time - self._last_cpu_check > 5.0:  # 5秒缓存
                self._cpu_cache = psutil.cpu_percent(interval=0.1)
                self._last_cpu_check = current_time

            cpu_percent = self._cpu_cache

            # 快速内存检查
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 简化的状态判断
            issues = []
            if cpu_percent > 90:
                issues.append(f"CPU使用率过高: {cpu_percent:.1f}%")
            if memory_percent > 95:
                issues.append(f"内存使用率过高: {memory_percent:.1f}%")

            if issues:
                status = (
                    HealthStatus.DEGRADED
                    if len(issues) == 1
                    else HealthStatus.UNHEALTHY
                )
                message = "; ".join(issues)
            else:
                status = HealthStatus.HEALTHY
                message = f"系统资源正常 (CPU: {cpu_percent:.1f}%, 内存: {memory_percent:.1f}%)"

            return {
                "status": status,
                "message": message,
                "details": {
                    "cpu_percent": round(cpu_percent, 1),
                    "memory_percent": round(memory_percent, 1),
                    "cached_cpu": current_time - self._last_cpu_check < 5.0,
                },
            }

        except ImportError:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "psutil库未安装",
                "details": {"psutil_available": False},
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"系统资源检查失败: {str(e)}",
                "details": {"error": str(e)},
            }


class OptimizedHealthCheckManager(HealthCheckManager):
    """优化的健康检查管理器"""

    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.max_workers = max_workers
        self.performance_stats: dict[str, CheckerPerformanceStats] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._stats_lock = threading.Lock()

    def add_checker(self, checker: HealthChecker):
        """添加检查器并初始化性能统计"""
        super().add_checker(checker)
        with self._stats_lock:
            if checker.name not in self.performance_stats:
                self.performance_stats[checker.name] = CheckerPerformanceStats(
                    name=checker.name
                )

    async def check_health(self) -> "HealthCheckSummary":
        """优化的健康检查执行"""
        start_time = time.time()

        # 按优先级分组检查器
        critical_checkers = []
        normal_checkers = []

        for checker in self.checkers:
            if isinstance(
                checker, FastConfigurationChecker | FastSystemResourcesChecker
            ):
                critical_checkers.append(checker)
            else:
                normal_checkers.append(checker)

        # 先执行关键检查器
        critical_results = await self._run_checkers_batch(critical_checkers, "关键检查")

        # 如果关键检查都通过，再执行普通检查器
        if all(r.status == HealthStatus.HEALTHY for r in critical_results):
            normal_results = await self._run_checkers_batch(normal_checkers, "常规检查")
            all_results = critical_results + normal_results
        else:
            # 关键检查失败，跳过部分普通检查以节省时间
            logger.warning("关键检查失败，执行快速模式")
            normal_results = await self._run_checkers_batch(
                normal_checkers[:2], "快速检查"
            )
            all_results = critical_results + normal_results

        # 计算整体状态
        overall_status = self._calculate_overall_status(all_results)

        # 更新性能统计
        total_duration = time.time() - start_time
        self._update_performance_stats(all_results, total_duration)

        from .health_check import HealthCheckSummary

        return HealthCheckSummary(
            overall_status=overall_status,
            checks=all_results,
            timestamp=time.time(),
            duration=total_duration,
        )

    async def _run_checkers_batch(
        self, checkers: list[HealthChecker], batch_name: str
    ) -> list[HealthCheckResult]:
        """批量运行检查器"""
        if not checkers:
            return []

        batch_start = time.time()
        logger.debug(f"开始执行{batch_name}: {len(checkers)}个检查器")

        # 创建任务
        tasks = []
        for checker in checkers:
            task = asyncio.create_task(self._run_single_checker(checker))
            tasks.append(task)

        # 等待所有任务完成，但有超时保护
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=max(2.0, min(checker.timeout for checker in checkers) * 2),
            )
        except TimeoutError:
            logger.warning(f"{batch_name}批量执行超时")
            results = []
            for task in tasks:
                if task.done():
                    try:
                        results.append(task.result())
                    except Exception as e:
                        results.append(
                            self._create_error_result(
                                f"task_error_{len(results)}", str(e)
                            )
                        )
                else:
                    task.cancel()
                    results.append(
                        self._create_error_result(f"timeout_{len(results)}", "检查超时")
                    )

        # 处理异常结果
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                checker_name = checkers[i].name if i < len(checkers) else f"unknown_{i}"
                final_results.append(
                    self._create_error_result(checker_name, str(result))
                )
            elif isinstance(result, HealthCheckResult):
                final_results.append(result)
            else:
                checker_name = checkers[i].name if i < len(checkers) else f"unknown_{i}"
                final_results.append(
                    self._create_error_result(checker_name, "未知结果类型")
                )

        batch_duration = time.time() - batch_start
        logger.debug(f"{batch_name}完成，耗时: {batch_duration:.2f}秒")

        return final_results

    async def _run_single_checker(self, checker: HealthChecker) -> HealthCheckResult:
        """运行单个检查器"""
        start_time = time.time()
        try:
            result = await checker.check()
            duration = time.time() - start_time

            # 更新单个检查器的性能统计
            with self._stats_lock:
                if checker.name in self.performance_stats:
                    stats = self.performance_stats[checker.name]
                    stats.total_runs += 1
                    stats.last_run_time = duration

                    # 更新平均时间
                    if stats.total_runs == 1:
                        stats.avg_duration = duration
                    else:
                        stats.avg_duration = (
                            stats.avg_duration * (stats.total_runs - 1) + duration
                        ) / stats.total_runs

                    # 更新最小最大时间
                    stats.min_duration = min(stats.min_duration, duration)
                    stats.max_duration = max(stats.max_duration, duration)

                    # 更新成功率
                    if result.status == HealthStatus.UNHEALTHY:
                        stats.failed_runs += 1
                    stats.success_rate = (
                        (stats.total_runs - stats.failed_runs) / stats.total_runs
                    ) * 100

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"检查器 {checker.name} 执行失败: {e}")

            # 更新失败统计
            with self._stats_lock:
                if checker.name in self.performance_stats:
                    stats = self.performance_stats[checker.name]
                    stats.total_runs += 1
                    stats.failed_runs += 1
                    stats.last_run_time = duration
                    stats.success_rate = (
                        (stats.total_runs - stats.failed_runs) / stats.total_runs
                    ) * 100

            return self._create_error_result(checker.name, str(e))

    def _create_error_result(self, name: str, error_msg: str) -> HealthCheckResult:
        """创建错误结果"""
        return HealthCheckResult(
            name=name,
            status=HealthStatus.UNHEALTHY,
            message=f"检查失败: {error_msg}",
            timestamp=time.time(),
            duration=0.0,
            details={"error": error_msg},
        )

    def _update_performance_stats(
        self, results: list[HealthCheckResult], total_duration: float
    ):
        """更新整体性能统计"""
        logger.info(
            f"健康检查完成，总耗时: {total_duration:.2f}秒，检查项: {len(results)}"
        )

        # 记录性能警告
        if total_duration > 2.0:
            slow_checkers = []
            for result in results:
                if result.duration and result.duration > 1.0:
                    slow_checkers.append(f"{result.name}({result.duration:.2f}s)")

            if slow_checkers:
                logger.warning(f"慢检查器: {', '.join(slow_checkers)}")

    def get_performance_summary(self) -> dict[str, Any]:
        """获取性能摘要"""
        with self._stats_lock:
            total_runs = sum(
                stats.total_runs for stats in self.performance_stats.values()
            )
            total_failures = sum(
                stats.failed_runs for stats in self.performance_stats.values()
            )
            avg_success_rate = (
                sum(stats.success_rate for stats in self.performance_stats.values())
                / len(self.performance_stats)
                if self.performance_stats
                else 100
            )

            slowest_checker = max(
                self.performance_stats.values(),
                key=lambda s: s.avg_duration,
                default=None,
            )
            fastest_checker = min(
                self.performance_stats.values(),
                key=lambda s: s.avg_duration,
                default=None,
            )

            return {
                "total_checkers": len(self.performance_stats),
                "total_runs": total_runs,
                "total_failures": total_failures,
                "overall_success_rate": round(avg_success_rate, 2),
                "slowest_checker": (
                    {
                        "name": slowest_checker.name,
                        "avg_duration": round(slowest_checker.avg_duration, 3),
                    }
                    if slowest_checker
                    else None
                ),
                "fastest_checker": (
                    {
                        "name": fastest_checker.name,
                        "avg_duration": round(fastest_checker.avg_duration, 3),
                    }
                    if fastest_checker
                    else None
                ),
                "performance_stats": {
                    name: {
                        "avg_duration": round(stats.avg_duration, 3),
                        "min_duration": round(stats.min_duration, 3),
                        "max_duration": round(stats.max_duration, 3),
                        "success_rate": round(stats.success_rate, 1),
                        "total_runs": stats.total_runs,
                    }
                    for name, stats in self.performance_stats.items()
                },
            }

    def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)


# 全局优化健康检查管理器
optimized_health_manager = OptimizedHealthCheckManager(max_workers=4)


def setup_optimized_health_checks(config=None):
    """设置优化的健康检查"""
    # 清除现有检查器
    optimized_health_manager.checkers.clear()

    # 添加优化的检查器
    optimized_health_manager.add_checker(FastConfigurationChecker(config))
    optimized_health_manager.add_checker(FastSystemResourcesChecker())

    # 从原有管理器复制其他检查器（如果需要）
    for checker in global_health_manager.checkers:
        if checker.name not in ["configuration", "system_resources"]:
            # 为现有检查器添加缓存包装
            if not isinstance(checker, CachedHealthChecker):
                cached_checker = CachedHealthChecker(
                    name=f"cached_{checker.name}",
                    timeout=min(checker.timeout, 2.0),  # 限制超时时间
                    cache_ttl=30.0,
                )
                cached_checker._perform_check = checker._perform_check
                optimized_health_manager.add_checker(cached_checker)
            else:
                optimized_health_manager.add_checker(checker)

    logger.info(
        f"优化健康检查已设置，检查器数量: {len(optimized_health_manager.checkers)}"
    )


async def run_optimized_health_check() -> "HealthCheckSummary":
    """运行优化的健康检查"""
    return await optimized_health_manager.check_health()


def get_optimized_health_performance() -> dict[str, Any]:
    """获取优化健康检查的性能数据"""
    return optimized_health_manager.get_performance_summary()
