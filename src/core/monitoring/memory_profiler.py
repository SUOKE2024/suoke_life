"""
索克生活项目 - 内存分析器
监控和分析应用程序的内存使用情况
"""

import gc
import logging
import sys
import time
import tracemalloc
from dataclasses import dataclass
from functools import wraps
from typing import Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """内存快照"""

    timestamp: float
    current_memory: float
    peak_memory: float
    objects_count: int
    gc_collections: Dict[int, int]


class MemoryProfiler:
    """内存分析器"""

    def __init__(self):
        self.snapshots: List[MemorySnapshot] = []
        self.tracemalloc_started = False
        self.baseline_snapshot = None

    def start_profiling(self):
        """开始内存分析"""
        if not self.tracemalloc_started:
            tracemalloc.start()
            self.tracemalloc_started = True
            logger.info("内存分析已启动")

    def stop_profiling(self):
        """停止内存分析"""
        if self.tracemalloc_started:
            tracemalloc.stop()
            self.tracemalloc_started = False
            logger.info("内存分析已停止")

    def take_snapshot(self, label: str = None) -> MemorySnapshot:
        """获取内存快照"""
        process = psutil.Process()
        memory_info = process.memory_info()

        snapshot = MemorySnapshot(
            timestamp=time.time(),
            current_memory=memory_info.rss / 1024 / 1024,  # MB
            peak_memory=memory_info.vms / 1024 / 1024,  # MB
            objects_count=len(gc.get_objects()),
            gc_collections={
                0: gc.get_count()[0],
                1: gc.get_count()[1],
                2: gc.get_count()[2],
            },
        )

        self.snapshots.append(snapshot)

        if label:
            logger.info(f"内存快照 [{label}]: {snapshot.current_memory:.2f}MB")

        return snapshot

    def set_baseline(self):
        """设置基线快照"""
        self.baseline_snapshot = self.take_snapshot("baseline")

    def get_memory_diff(self) -> Optional[float]:
        """获取与基线的内存差异"""
        if not self.baseline_snapshot or not self.snapshots:
            return None

        current = self.snapshots[-1]
        return current.current_memory - self.baseline_snapshot.current_memory

    def analyze_memory_leaks(self) -> List[str]:
        """分析内存泄漏"""
        if not self.tracemalloc_started:
            return ["内存分析未启动"]

        current, peak = tracemalloc.get_traced_memory()
        top_stats = tracemalloc.take_snapshot().statistics("lineno")

        leaks = []
        for stat in top_stats[:10]:
            leaks.append(f"{stat.traceback.format()[-1]}: {stat.size / 1024:.1f} KB")

        return leaks

    def force_garbage_collection(self) -> Dict[str, int]:
        """强制垃圾回收"""
        before_counts = gc.get_count()
        collected = gc.collect()
        after_counts = gc.get_count()

        result = {
            "collected_objects": collected,
            "before_counts": before_counts,
            "after_counts": after_counts,
        }

        logger.info(f"垃圾回收完成: 回收了 {collected} 个对象")
        return result

    def get_memory_report(self) -> str:
        """生成内存报告"""
        if not self.snapshots:
            return "没有内存快照数据"

        latest = self.snapshots[-1]
        report = f"""
内存使用报告
============
当前内存使用: {latest.current_memory:.2f} MB
峰值内存使用: {latest.peak_memory:.2f} MB
对象数量: {latest.objects_count:,}
GC统计: Gen0={latest.gc_collections[0]}, Gen1={latest.gc_collections[1]}, Gen2={latest.gc_collections[2]}
"""

        if self.baseline_snapshot:
            diff = self.get_memory_diff()
            report += f"与基线差异: {diff:+.2f} MB\n"

        if len(self.snapshots) > 1:
            trend = latest.current_memory - self.snapshots[0].current_memory
            report += f"总体趋势: {trend:+.2f} MB\n"

        return report


# 内存监控装饰器
def memory_monitor(func):
    """内存监控装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = MemoryProfiler()
        profiler.start_profiling()
        profiler.take_snapshot(f"before_{func.__name__}")

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.take_snapshot(f"after_{func.__name__}")
            diff = profiler.get_memory_diff()
            if diff and diff > 10:  # 超过10MB增长
                logger.warning(f"函数 {func.__name__} 内存增长: {diff:.2f}MB")
            profiler.stop_profiling()

    return wrapper


# 内存上下文管理器
class MemoryContext:
    """内存监控上下文管理器"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.profiler = MemoryProfiler()

    def __enter__(self):
        self.profiler.start_profiling()
        self.profiler.set_baseline()
        return self.profiler

    def __exit__(self, exc_type, exc_val, exc_tb):
        final_snapshot = self.profiler.take_snapshot(f"final_{self.operation_name}")
        diff = self.profiler.get_memory_diff()

        if diff and diff > 5:  # 超过5MB增长
            logger.warning(f"操作 {self.operation_name} 内存增长: {diff:.2f}MB")

        self.profiler.stop_profiling()


# 全局内存分析器实例
global_profiler = MemoryProfiler()
