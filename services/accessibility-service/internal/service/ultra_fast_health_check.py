#!/usr/bin/env python3
"""
超级优化健康检查模块
目标：将健康检查时间从5.16秒优化到<2秒
优化策略：
1. 并行执行所有检查
2. 智能缓存和预加载
3. 快速失败机制
4. 异步I/O优化
5. 内存池和连接复用
"""

import asyncio
import logging
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from .health_check import HealthStatus

logger = logging.getLogger(__name__)


@dataclass
class UltraFastCheckResult:
    """超快检查结果"""

    name: str
    status: HealthStatus
    message: str
    duration: float
    timestamp: float
    cached: bool = False
    details: dict[str, Any] = field(default_factory=dict)


class PerformanceCache:
    """高性能缓存"""

    def __init__(self, max_size: int = 1000, default_ttl: float = 30.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: dict[str, tuple[Any, float, float]] = (
            {}
        )  # key: (value, timestamp, ttl)
        self._access_order = deque()  # LRU tracking
        self._lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                return None

            value, timestamp, ttl = self._cache[key]
            current_time = time.time()

            # 检查是否过期
            if current_time - timestamp > ttl:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return None

            # 更新访问顺序
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

            return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """设置缓存值"""
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl

            current_time = time.time()

            # 如果缓存已满，删除最旧的项
            if len(self._cache) >= self.max_size and key not in self._cache:
                if self._access_order:
                    oldest_key = self._access_order.popleft()
                    if oldest_key in self._cache:
                        del self._cache[oldest_key]

            self._cache[key] = (value, current_time, ttl)

            # 更新访问顺序
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()


class UltraFastChecker:
    """超快检查器基类"""

    def __init__(
        self,
        name: str,
        timeout: float = 0.5,
        cache_ttl: float = 15.0,
        priority: int = 1,
    ):
        self.name = name
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.priority = priority  # 1=高优先级, 2=中优先级, 3=低优先级
        self._last_result: UltraFastCheckResult | None = None
        self._consecutive_failures = 0
        self._adaptive_timeout = timeout

    async def check(self) -> UltraFastCheckResult:
        """执行检查"""
        start_time = time.time()

        try:
            # 使用自适应超时
            result = await asyncio.wait_for(
                self._perform_check(), timeout=self._adaptive_timeout
            )

            duration = time.time() - start_time

            # 成功时重置失败计数和超时
            self._consecutive_failures = 0
            self._adaptive_timeout = self.timeout

            check_result = UltraFastCheckResult(
                name=self.name,
                status=result.get("status", HealthStatus.UNKNOWN),
                message=result.get("message", ""),
                duration=duration,
                timestamp=time.time(),
                details=result.get("details", {}),
            )

            self._last_result = check_result
            return check_result

        except TimeoutError:
            duration = time.time() - start_time
            self._consecutive_failures += 1

            # 自适应超时调整
            if self._consecutive_failures > 2:
                self._adaptive_timeout = min(self.timeout * 0.5, 0.2)  # 快速失败

            return UltraFastCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"检查超时 ({duration:.2f}s)",
                duration=duration,
                timestamp=time.time(),
                details={
                    "timeout": True,
                    "consecutive_failures": self._consecutive_failures,
                },
            )

        except Exception as e:
            duration = time.time() - start_time
            self._consecutive_failures += 1

            return UltraFastCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"检查异常: {str(e)}",
                duration=duration,
                timestamp=time.time(),
                details={
                    "error": str(e),
                    "consecutive_failures": self._consecutive_failures,
                },
            )

    async def _perform_check(self) -> dict[str, Any]:
        """子类实现的具体检查逻辑"""
        raise NotImplementedError


class LightningConfigChecker(UltraFastChecker):
    """闪电配置检查器"""

    def __init__(self, config=None):
        super().__init__("lightning_config", timeout=0.1, cache_ttl=60.0, priority=1)
        self.config = config
        self._config_hash = None
        self._cached_result = None

    async def _perform_check(self) -> dict[str, Any]:
        """超快配置检查"""
        # 计算配置哈希，避免重复检查
        current_hash = hash(str(self.config)) if self.config else 0

        if self._config_hash == current_hash and self._cached_result:
            return self._cached_result

        try:
            if not self.config:
                result = {
                    "status": HealthStatus.DEGRADED,
                    "message": "配置未加载",
                    "details": {"config_available": False},
                }
            else:
                # 最小化配置检查
                has_basic_config = hasattr(self.config, "service") or hasattr(
                    self.config, "version"
                )

                if has_basic_config:
                    result = {
                        "status": HealthStatus.HEALTHY,
                        "message": "配置正常",
                        "details": {"config_available": True},
                    }
                else:
                    result = {
                        "status": HealthStatus.DEGRADED,
                        "message": "配置不完整",
                        "details": {"config_available": True, "complete": False},
                    }

            # 缓存结果
            self._config_hash = current_hash
            self._cached_result = result
            return result

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"配置检查失败: {str(e)[:50]}",
                "details": {"error": str(e)[:100]},
            }


class TurboSystemChecker(UltraFastChecker):
    """涡轮系统检查器"""

    def __init__(self) -> None:
        super().__init__("turbo_system", timeout=0.3, cache_ttl=10.0, priority=1)
        self._psutil = None
        self._last_cpu_time = 0
        self._last_cpu_value = 0.0
        self._cpu_cache_duration = 5.0  # CPU缓存5秒

    def _get_psutil(self) -> None:
        """延迟加载psutil"""
        if self._psutil is None:
            try:
                import psutil

                self._psutil = psutil
            except ImportError:
                self._psutil = False
        return self._psutil

    async def _perform_check(self) -> dict[str, Any]:
        """涡轮系统检查"""
        psutil = self._get_psutil()

        if not psutil:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "系统监控不可用",
                "details": {"psutil_available": False},
            }

        try:
            current_time = time.time()

            # 使用缓存的CPU值
            if current_time - self._last_cpu_time > self._cpu_cache_duration:
                # 使用非阻塞CPU检查
                self._last_cpu_value = psutil.cpu_percent(interval=0)
                self._last_cpu_time = current_time

            cpu_percent = self._last_cpu_value

            # 快速内存检查
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 简化状态判断
            if cpu_percent > 95 or memory_percent > 98:
                status = HealthStatus.UNHEALTHY
                message = "系统资源严重不足"
            elif cpu_percent > 85 or memory_percent > 90:
                status = HealthStatus.DEGRADED
                message = "系统资源紧张"
            else:
                status = HealthStatus.HEALTHY
                message = "系统正常"

            return {
                "status": status,
                "message": message,
                "details": {
                    "cpu": round(cpu_percent, 1),
                    "memory": round(memory_percent, 1),
                    "cached_cpu": current_time - self._last_cpu_time
                    < self._cpu_cache_duration,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"系统检查失败: {str(e)[:50]}",
                "details": {"error": str(e)[:100]},
            }


class RapidNetworkChecker(UltraFastChecker):
    """快速网络检查器"""

    def __init__(self) -> None:
        super().__init__("rapid_network", timeout=0.5, cache_ttl=20.0, priority=2)
        self._test_urls = ["https://www.baidu.com", "https://httpbin.org/status/200"]
        self._last_good_url = None

    async def _perform_check(self) -> dict[str, Any]:
        """快速网络检查"""
        try:
            import aiohttp

            # 优先测试上次成功的URL
            test_urls = self._test_urls.copy()
            if self._last_good_url and self._last_good_url in test_urls:
                test_urls.remove(self._last_good_url)
                test_urls.insert(0, self._last_good_url)

            timeout = aiohttp.ClientTimeout(total=0.3, connect=0.2)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                for url in test_urls:
                    try:
                        async with session.head(url) as response:
                            if response.status < 400:
                                self._last_good_url = url
                                return {
                                    "status": HealthStatus.HEALTHY,
                                    "message": "网络连接正常",
                                    "details": {
                                        "test_url": url,
                                        "status_code": response.status,
                                    },
                                }
                    except:
                        continue

                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "网络连接失败",
                    "details": {"tested_urls": len(test_urls)},
                }

        except ImportError:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "网络检查不可用",
                "details": {"aiohttp_available": False},
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"网络检查异常: {str(e)[:50]}",
                "details": {"error": str(e)[:100]},
            }


class UltraFastHealthManager:
    """超快健康检查管理器"""

    def __init__(self, max_workers: int = 6, global_timeout: float = 1.5):
        self.checkers: list[UltraFastChecker] = []
        self.max_workers = max_workers
        self.global_timeout = global_timeout
        self.cache = PerformanceCache(max_size=100, default_ttl=30.0)
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="ultra_health"
        )

        # 性能统计
        self.total_checks = 0
        self.total_duration = 0.0
        self.fastest_check = float("inf")
        self.slowest_check = 0.0

        # 预热标志
        self._warmed_up = False

    def add_checker(self, checker: UltraFastChecker):
        """添加检查器"""
        self.checkers.append(checker)
        # 按优先级排序
        self.checkers.sort(key=lambda c: c.priority)

    async def warmup(self) -> None:
        """预热检查器"""
        if self._warmed_up:
            return

        logger.info("预热健康检查器...")
        warmup_tasks = []

        for checker in self.checkers:
            if checker.priority == 1:  # 只预热高优先级检查器
                task = asyncio.create_task(checker.check())
                warmup_tasks.append(task)

        if warmup_tasks:
            await asyncio.gather(*warmup_tasks, return_exceptions=True)

        self._warmed_up = True
        logger.info("健康检查器预热完成")

    async def check_health(self) -> dict[str, Any]:
        """执行超快健康检查"""
        start_time = time.time()

        # 确保预热
        if not self._warmed_up:
            await self.warmup()

        try:
            # 并行执行所有检查，使用全局超时
            tasks = [asyncio.create_task(checker.check()) for checker in self.checkers]

            # 使用全局超时，确保总时间不超过限制
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.global_timeout,
            )

            total_duration = time.time() - start_time

            # 处理结果
            check_results = []
            exceptions = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    exceptions.append(f"{self.checkers[i].name}: {str(result)}")
                    # 创建失败结果
                    check_results.append(
                        UltraFastCheckResult(
                            name=self.checkers[i].name,
                            status=HealthStatus.UNHEALTHY,
                            message=f"检查异常: {str(result)[:50]}",
                            duration=total_duration,
                            timestamp=time.time(),
                            details={"exception": True},
                        )
                    )
                else:
                    check_results.append(result)

            # 计算总体状态
            overall_status = self._calculate_overall_status(check_results)

            # 更新性能统计
            self._update_performance_stats(total_duration)

            return {
                "overall_status": overall_status,
                "total_duration": round(total_duration, 3),
                "check_count": len(check_results),
                "healthy_count": sum(
                    1 for r in check_results if r.status == HealthStatus.HEALTHY
                ),
                "degraded_count": sum(
                    1 for r in check_results if r.status == HealthStatus.DEGRADED
                ),
                "unhealthy_count": sum(
                    1 for r in check_results if r.status == HealthStatus.UNHEALTHY
                ),
                "checks": [
                    {
                        "name": r.name,
                        "status": r.status.value,
                        "message": r.message,
                        "duration": round(r.duration, 3),
                        "cached": r.cached,
                        "details": r.details,
                    }
                    for r in check_results
                ],
                "exceptions": exceptions,
                "performance": {
                    "avg_duration": round(
                        self.total_duration / max(self.total_checks, 1), 3
                    ),
                    "fastest": (
                        round(self.fastest_check, 3)
                        if self.fastest_check != float("inf")
                        else 0
                    ),
                    "slowest": round(self.slowest_check, 3),
                },
            }

        except TimeoutError:
            total_duration = time.time() - start_time
            logger.warning(f"健康检查全局超时: {total_duration:.3f}s")

            return {
                "overall_status": HealthStatus.UNHEALTHY.value,
                "total_duration": round(total_duration, 3),
                "check_count": 0,
                "healthy_count": 0,
                "degraded_count": 0,
                "unhealthy_count": 1,
                "checks": [
                    {
                        "name": "global_timeout",
                        "status": HealthStatus.UNHEALTHY.value,
                        "message": f"全局检查超时 ({total_duration:.3f}s)",
                        "duration": total_duration,
                        "cached": False,
                        "details": {"timeout": True, "global": True},
                    }
                ],
                "exceptions": ["Global timeout exceeded"],
                "performance": {
                    "avg_duration": round(
                        self.total_duration / max(self.total_checks, 1), 3
                    ),
                    "fastest": (
                        round(self.fastest_check, 3)
                        if self.fastest_check != float("inf")
                        else 0
                    ),
                    "slowest": round(self.slowest_check, 3),
                },
            }

        except Exception as e:
            total_duration = time.time() - start_time
            logger.error(f"健康检查异常: {e}")

            return {
                "overall_status": HealthStatus.UNHEALTHY.value,
                "total_duration": round(total_duration, 3),
                "check_count": 0,
                "healthy_count": 0,
                "degraded_count": 0,
                "unhealthy_count": 1,
                "checks": [
                    {
                        "name": "manager_error",
                        "status": HealthStatus.UNHEALTHY.value,
                        "message": f"管理器异常: {str(e)[:50]}",
                        "duration": total_duration,
                        "cached": False,
                        "details": {"error": str(e)[:100]},
                    }
                ],
                "exceptions": [str(e)],
                "performance": {
                    "avg_duration": round(
                        self.total_duration / max(self.total_checks, 1), 3
                    ),
                    "fastest": (
                        round(self.fastest_check, 3)
                        if self.fastest_check != float("inf")
                        else 0
                    ),
                    "slowest": round(self.slowest_check, 3),
                },
            }

    def _calculate_overall_status(self, results: list[UltraFastCheckResult]) -> str:
        """计算总体状态"""
        if not results:
            return HealthStatus.UNKNOWN.value

        unhealthy_count = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for r in results if r.status == HealthStatus.DEGRADED)

        # 快速状态判断
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY.value
        elif degraded_count > 0:
            return HealthStatus.DEGRADED.value
        else:
            return HealthStatus.HEALTHY.value

    def _update_performance_stats(self, duration: float):
        """更新性能统计"""
        self.total_checks += 1
        self.total_duration += duration
        self.fastest_check = min(self.fastest_check, duration)
        self.slowest_check = max(self.slowest_check, duration)

    def get_performance_summary(self) -> dict[str, Any]:
        """获取性能摘要"""
        if self.total_checks == 0:
            return {"total_checks": 0, "avg_duration": 0, "fastest": 0, "slowest": 0}

        return {
            "total_checks": self.total_checks,
            "avg_duration": round(self.total_duration / self.total_checks, 3),
            "fastest": (
                round(self.fastest_check, 3)
                if self.fastest_check != float("inf")
                else 0
            ),
            "slowest": round(self.slowest_check, 3),
            "target_achieved": (self.total_duration / self.total_checks) < 2.0,
        }

    def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)
        self.cache.clear()


# 全局超快健康管理器
ultra_fast_health_manager = UltraFastHealthManager()


def setup_ultra_fast_health_checks(config=None):
    """设置超快健康检查"""
    # 清除现有检查器
    ultra_fast_health_manager.checkers.clear()

    # 添加超快检查器
    ultra_fast_health_manager.add_checker(LightningConfigChecker(config))
    ultra_fast_health_manager.add_checker(TurboSystemChecker())
    ultra_fast_health_manager.add_checker(RapidNetworkChecker())

    logger.info(f"已设置 {len(ultra_fast_health_manager.checkers)} 个超快健康检查器")


async def run_ultra_fast_health_check() -> dict[str, Any]:
    """运行超快健康检查"""
    return await ultra_fast_health_manager.check_health()


def get_ultra_fast_performance() -> dict[str, Any]:
    """获取超快检查性能统计"""
    return ultra_fast_health_manager.get_performance_summary()


async def demo_ultra_fast_health() -> None:
    """演示超快健康检查"""
    print("🚀 超快健康检查演示")
    print("目标：将检查时间从5.16秒优化到<2秒")

    # 设置检查器
    setup_ultra_fast_health_checks()

    # 预热
    print("\n🔥 预热检查器...")
    await ultra_fast_health_manager.warmup()

    # 运行多次测试
    print("\n⚡ 运行性能测试...")
    durations = []

    for i in range(10):
        start_time = time.time()
        result = await run_ultra_fast_health_check()
        duration = time.time() - start_time
        durations.append(duration)

        print(
            f"测试 {i+1}: {duration:.3f}s - {result['overall_status']} "
            f"({result['healthy_count']}/{result['check_count']} 健康)"
        )

    # 性能统计
    avg_duration = sum(durations) / len(durations)
    min_duration = min(durations)
    max_duration = max(durations)

    print("\n📊 性能统计:")
    print(f"平均时间: {avg_duration:.3f}s")
    print(f"最快时间: {min_duration:.3f}s")
    print(f"最慢时间: {max_duration:.3f}s")
    print(f"目标达成: {'✅' if avg_duration < 2.0 else '❌'} (<2秒)")

    # 性能改进
    original_time = 5.16
    improvement = ((original_time - avg_duration) / original_time) * 100
    print(f"性能提升: {improvement:.1f}% (从 {original_time}s 到 {avg_duration:.3f}s)")

    return {
        "avg_duration": avg_duration,
        "min_duration": min_duration,
        "max_duration": max_duration,
        "target_achieved": avg_duration < 2.0,
        "improvement_percentage": improvement,
    }


if __name__ == "__main__":
    asyncio.run(demo_ultra_fast_health())
