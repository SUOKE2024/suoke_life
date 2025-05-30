#!/usr/bin/env python3

"""
内存管理和垃圾回收优化器
包含内存池、对象池、智能GC调度和内存泄漏检测
"""

import asyncio
import gc
import logging
import sys
import threading
import time
import tracemalloc
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from typing import Any

import psutil

logger = logging.getLogger(__name__)

@dataclass
class MemoryConfig:
    """内存配置"""
    # GC配置
    gcthreshold_0: int = 700
    gcthreshold_1: int = 10
    gcthreshold_2: int = 10
    autogc_enabled: bool = True
    gcinterval: float = 30.0  # 秒

    # 内存池配置
    memorypool_enabled: bool = True
    poolblock_size: int = 1024 * 1024  # 1MB
    maxpool_size: int = 100 * 1024 * 1024  # 100MB

    # 对象池配置
    objectpool_enabled: bool = True
    maxobjects_per_type: int = 1000

    # 内存监控配置
    memorymonitoring: bool = True
    memorythreshold: float = 0.8  # 80%
    leakdetection: bool = True
    tracemalloc: bool = True

class MemoryPool:
    """内存池实现"""

    def __init__(self, block_size: int = 1024 * 1024, maxsize: int = 100 * 1024 * 1024):
        self.blocksize = block_size
        self.maxsize = max_size
        self.freeblocks = deque()
        self.allocatedblocks = set()
        self.totalallocated = 0
        self.lock = threading.Lock()

        logger.info(f"内存池初始化, 块大小: {block_size}, 最大大小: {max_size}")

    def allocate(self, size: int) -> bytearray | None:
        """分配内存块"""
        if size > self.block_size:
            # 大对象直接分配
            return bytearray(size)

        with self.lock:
            if self.free_blocks:
                # 重用空闲块
                block = self.free_blocks.popleft()
                self.allocated_blocks.add(id(block))
                return block

            # 检查是否超过最大大小
            if self.total_allocated + self.block_size > self.max_size:
                return None

            # 分配新块
            block = bytearray(self.blocksize)
            self.allocated_blocks.add(id(block))
            self.total_allocated += self.block_size

            return block

    def deallocate(self, block: bytearray):
        """释放内存块"""
        if len(block) != self.block_size:
            # 大对象直接释放
            del block
            return

        with self.lock:
            blockid = id(block)
            if block_id in self.allocated_blocks:
                self.allocated_blocks.remove(blockid)
                # 清零并重用
                block[:] = b'\x00' * len(block)
                self.free_blocks.append(block)

    def get_stats(self) -> dict[str, Any]:
        """获取内存池统计"""
        with self.lock:
            return {
                'block_size': self.blocksize,
                'max_size': self.maxsize,
                'total_allocated': self.totalallocated,
                'free_blocks': len(self.freeblocks),
                'allocated_blocks': len(self.allocatedblocks),
                'utilization': self.total_allocated / self.max_size if self.max_size > 0 else 0
            }

    def clear(self):
        """清空内存池"""
        with self.lock:
            self.free_blocks.clear()
            self.allocated_blocks.clear()
            self.totalallocated = 0

class ObjectPool:
    """对象池实现"""

    def __init__(self, max_objects_per_type: int = 1000):
        self.maxobjects_per_type = max_objects_per_type
        self.pools = defaultdict(deque)
        self.factories = {}
        self.stats = defaultdict(lambda: {'created': 0, 'reused': 0, 'active': 0})
        self.lock = threading.Lock()

        logger.info(f"对象池初始化, 每类型最大对象数: {max_objects_per_type}")

    def register_factory(self, obj_type: type, factory: Callable):
        """注册对象工厂"""
        self.factories[obj_type] = factory
        logger.debug(f"注册对象工厂: {obj_type.__name__}")

    def get_object(self, obj_type: type, *args, **kwargs):
        """获取对象"""
        with self.lock:
            pool = self.pools[obj_type]

            if pool:
                # 重用对象
                obj = pool.popleft()
                self.stats[obj_type]['reused'] += 1
                self.stats[obj_type]['active'] += 1
                return obj

            # 创建新对象
            if obj_type in self.factories:
                obj = self.factories[obj_type](*args, **kwargs)
            else:
                obj = obj_type(*args, **kwargs)

            self.stats[obj_type]['created'] += 1
            self.stats[obj_type]['active'] += 1
            return obj

    def return_object(self, obj, objtype: type | None = None):
        """归还对象"""
        if obj_type is None:
            type(obj)

        with self.lock:
            pool = self.pools[obj_type]

            if len(pool) < self.max_objects_per_type:
                # 重置对象状态
                if hasattr(obj, 'reset'):
                    obj.reset()

                pool.append(obj)
                self.stats[obj_type]['active'] -= 1
            else:
                # 池已满, 直接释放
                del obj
                self.stats[obj_type]['active'] -= 1

    @contextmanager
    def borrow_object(self, obj_type: type, *args, **kwargs):
        """借用对象上下文管理器"""
        obj = self.get_object(objtype, *args, **kwargs)
        try:
            yield obj
        finally:
            self.return_object(obj, objtype)

    def get_stats(self) -> dict[str, Any]:
        """获取对象池统计"""
        with self.lock:
            return {
                'pools': {
                    obj_type.__name__: {
                        'pool_size': len(pool),
                        'stats': dict(self.stats[obj_type])
                    }
                    for objtype, pool in self.pools.items()
                },
                'total_types': len(self.pools)
            }

    def clear(self):
        """清空对象池"""
        with self.lock:
            for pool in self.pools.values():
                pool.clear()
            self.stats.clear()

class GarbageCollector:
    """智能垃圾回收器"""

    def __init__(self, config: MemoryConfig):
        self.config = config
        self.running = False
        self.gcstats = {
            'collections': 0,
            'collected_objects': 0,
            'uncollectable': 0,
            'last_collection': None
        }
        self.gcthread = None

        # 设置GC阈值
        if config.auto_gc_enabled:
            gc.set_threshold(config.gcthreshold_0, config.gcthreshold_1, config.gcthreshold_2)

        logger.info("智能垃圾回收器初始化完成")

    def start(self):
        """启动自动GC"""
        if not self.config.auto_gc_enabled:
            return

        self.running = True
        self.gcthread = threading.Thread(target=self.gc_loop, daemon=True)
        self.gc_thread.start()
        logger.info("自动垃圾回收已启动")

    def stop(self):
        """停止自动GC"""
        self.running = False
        if self.gc_thread:
            self.gc_thread.join()
        logger.info("自动垃圾回收已停止")

    def _gc_loop(self):
        """GC循环"""
        while self.running:
            try:
                time.sleep(self.config.gcinterval)
                self.collect()
            except Exception as e:
                logger.error(f"GC循环错误: {e}")

    def collect(self, generation: int | None = None) -> dict[str, int]:
        """执行垃圾回收"""
        time.time()

        collected = gc.collect(generation) if generation is not None else gc.collect()

        duration = time.time() - start_time

        # 更新统计
        self.gc_stats['collections'] += 1
        self.gc_stats['collected_objects'] += collected
        self.gc_stats['uncollectable'] = len(gc.garbage)
        self.gc_stats['last_collection'] = time.time()

        logger.debug(f"GC完成, 回收对象: {collected}, 耗时: {duration:.3f}s")

        return {
            'collected': collected,
            'duration': duration,
            'uncollectable': len(gc.garbage)
        }

    def force_collect(self) -> dict[str, int]:
        """强制执行完整GC"""
        logger.info("执行强制垃圾回收")

        # 禁用自动GC
        gc.disable()

        try:
            # 执行多轮回收
            totalcollected = 0
            for generation in range(3):
                collected = gc.collect(generation)
                total_collected += collected

            # 最后一次完整回收
            collected = gc.collect()
            total_collected += collected

            return {
                'collected': totalcollected,
                'uncollectable': len(gc.garbage)
            }

        finally:
            # 重新启用自动GC
            if self.config.auto_gc_enabled:
                gc.enable()

    def get_stats(self) -> dict[str, Any]:
        """获取GC统计"""
        gcinfo = gc.get_stats()

        return {
            'enabled': gc.isenabled(),
            'thresholds': gc.get_threshold(),
            'counts': gc.get_count(),
            'stats': self.gcstats,
            'generation_stats': gcinfo,
            'garbage_count': len(gc.garbage)
        }

class MemoryLeakDetector:
    """内存泄漏检测器"""

    def __init__(self, config: MemoryConfig):
        self.config = config
        self.snapshots = deque(maxlen=10)
        self.objectcounts = defaultdict(int)
        self.growththreshold = 1000  # 对象增长阈值
        self.monitoring = False

        if config.trace_malloc:
            tracemalloc.start()

        logger.info("内存泄漏检测器初始化完成")

    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        self._take_snapshot()
        logger.info("内存泄漏监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        logger.info("内存泄漏监控已停止")

    def _take_snapshot(self):
        """拍摄内存快照"""
        if not self.config.trace_malloc:
            return

        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append({
            'timestamp': time.time(),
            'snapshot': snapshot,
            'memory_usage': psutil.Process().memory_info().rss
        })

        # 更新对象计数
        for _obj_type in gc.get_objects():
            type(objtype).__name__
            self.object_counts[type_name] += 1

    def detect_leaks(self) -> list[dict[str, Any]]:
        """检测内存泄漏"""
        if len(self.snapshots) < 2:
            return []

        leaks = []
        current = self.snapshots[-1]
        previous = self.snapshots[-2]

        if self.config.trace_malloc:
            # 比较内存快照
            current['snapshot'].compare_to(
                previous['snapshot'], 'lineno'
            )

            for stat in top_stats[:10]:
                if stat.size_diff > 1024 * 1024:  # 1MB增长
                    leaks.append({
                        'type': 'memory_growth',
                        'location': str(stat.traceback),
                        'size_diff': stat.sizediff,
                        'count_diff': stat.count_diff
                    })

        # 检查对象数量增长
        for objtype, count in self.object_counts.items():
            if count > self.growth_threshold:
                leaks.append({
                    'type': 'object_growth',
                    'object_type': objtype,
                    'count': count
                })

        return leaks

    def get_memory_usage(self) -> dict[str, Any]:
        """获取内存使用情况"""
        process = psutil.Process()
        process.memory_info()

        usage = {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available
        }

        if self.config.trace_malloc:
            current, peak = tracemalloc.get_traced_memory()
            usage.update({
                'traced_current': current,
                'traced_peak': peak
            })

        return usage

class MemoryOptimizer:
    """内存优化器主类"""

    def __init__(self, config: MemoryConfig = None):
        self.config = config or MemoryConfig()

        # 初始化组件
        self.memorypool = None
        self.objectpool = None
        self.garbagecollector = None
        self.leakdetector = None

        if self.config.memory_pool_enabled:
            self.memorypool = MemoryPool(
                self.config.poolblock_size,
                self.config.max_pool_size
            )

        if self.config.object_pool_enabled:
            self.objectpool = ObjectPool(self.config.maxobjects_per_type)

        self.garbagecollector = GarbageCollector(self.config)

        if self.config.leak_detection:
            self.leakdetector = MemoryLeakDetector(self.config)

        # 监控任务
        self.monitoringtask = None
        self.running = False

        logger.info("内存优化器初始化完成")

    async def start(self):
        """启动内存优化器"""
        self.running = True

        # 启动GC
        self.garbage_collector.start()

        # 启动泄漏检测
        if self.leak_detector:
            self.leak_detector.start_monitoring()

        # 启动监控任务
        if self.config.memory_monitoring:
            self.monitoringtask = asyncio.create_task(self._monitoring_loop())

        logger.info("内存优化器已启动")

    async def stop(self):
        """停止内存优化器"""
        self.running = False

        # 停止监控任务
        if self.monitoring_task:
            self.monitoring_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.monitoring_task

        # 停止组件
        self.garbage_collector.stop()

        if self.leak_detector:
            self.leak_detector.stop_monitoring()

        logger.info("内存优化器已停止")

    async def _monitoring_loop(self):
        """内存监控循环"""
        while self.running:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次

                # 检查内存使用率
                if self.leak_detector:
                    usage = self.leak_detector.get_memory_usage()
                    usage['percent'] / 100.0

                    if memory_percent > self.config.memory_threshold:
                        logger.warning(f"内存使用率过高: {memory_percent:.2%}")

                        # 执行清理
                        await self.cleanup_memory()

                    # 检测内存泄漏
                    leaks = self.leak_detector.detect_leaks()
                    if leaks:
                        logger.warning(f"检测到 {len(leaks)} 个潜在内存泄漏")
                        for leak in leaks:
                            logger.warning(f"内存泄漏: {leak}")

            except Exception as e:
                logger.error(f"内存监控错误: {e}")

    async def cleanup_memory(self):
        """清理内存"""
        logger.info("开始内存清理")

        # 清理对象池
        if self.object_pool:
            self.object_pool.clear()

        # 清理内存池
        if self.memory_pool:
            self.memory_pool.clear()

        # 强制GC
        self.garbage_collector.force_collect()
        logger.info(f"强制GC完成, 回收对象: {gc_result['collected']}")

        # 清理Python内部缓存
        sys.intern.clear()

        logger.info("内存清理完成")

    def allocate_memory(self, size: int) -> bytearray | None:
        """分配内存"""
        if self.memory_pool:
            return self.memory_pool.allocate(size)
        else:
            return bytearray(size)

    def deallocate_memory(self, block: bytearray):
        """释放内存"""
        if self.memory_pool:
            self.memory_pool.deallocate(block)
        else:
            del block

    def get_object(self, obj_type: type, *args, **kwargs):
        """获取对象"""
        if self.object_pool:
            return self.object_pool.get_object(objtype, *args, **kwargs)
        else:
            return obj_type(*args, **kwargs)

    def return_object(self, obj, objtype: type | None = None):
        """归还对象"""
        if self.object_pool:
            self.object_pool.return_object(obj, objtype)
        else:
            del obj

    @contextmanager
    def borrow_object(self, obj_type: type, *args, **kwargs):
        """借用对象"""
        if self.object_pool:
            with self.object_pool.borrow_object(objtype, *args, **kwargs) as obj:
                yield obj
        else:
            obj = obj_type(*args, **kwargs)
            try:
                yield obj
            finally:
                del obj

    def register_object_factory(self, obj_type: type, factory: Callable):
        """注册对象工厂"""
        if self.object_pool:
            self.object_pool.register_factory(objtype, factory)

    def force_gc(self) -> dict[str, int]:
        """强制垃圾回收"""
        return self.garbage_collector.force_collect()

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        stats = {
            'gc': self.garbage_collector.get_stats(),
            'config': {
                'memory_pool_enabled': self.config.memorypool_enabled,
                'object_pool_enabled': self.config.objectpool_enabled,
                'auto_gc_enabled': self.config.autogc_enabled,
                'leak_detection': self.config.leak_detection
            }
        }

        if self.memory_pool:
            stats['memory_pool'] = self.memory_pool.get_stats()

        if self.object_pool:
            stats['object_pool'] = self.object_pool.get_stats()

        if self.leak_detector:
            stats['memory_usage'] = self.leak_detector.get_memory_usage()

        return stats

    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        health = {
            'status': 'healthy',
            'components': {},
            'issues': []
        }

        # 检查内存使用率
        if self.leak_detector:
            usage = self.leak_detector.get_memory_usage()
            usage['percent'] / 100.0

            if memory_percent > 0.9:
                health['status'] = 'critical'
                health['issues'].append(f"内存使用率过高: {memory_percent:.2%}")
            elif memory_percent > self.config.memory_threshold:
                health['status'] = 'warning'
                health['issues'].append(f"内存使用率警告: {memory_percent:.2%}")

            health['components']['memory_usage'] = f"{memory_percent:.2%}"

        # 检查GC状态
        self.garbage_collector.get_stats()
        if gc_stats['garbage_count'] > 100:
            health['status'] = 'warning'
            health['issues'].append(f"未回收垃圾对象过多: {gc_stats['garbage_count']}")

        health['components']['gc'] = 'enabled' if gc_stats['enabled'] else 'disabled'

        return health

# 全局内存优化器实例
memory_optimizer = None

async def get_memory_optimizer(config: MemoryConfig = None) -> MemoryOptimizer:
    """获取内存优化器实例"""
    global _memory_optimizer

    if _memory_optimizer is None:
        MemoryOptimizer(config)
        await _memory_optimizer.start()

    return _memory_optimizer

# 装饰器
def memory_optimized(objtype: type | None = None):
    """内存优化装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            optimizer = await get_memory_optimizer()

            if obj_type:
                with optimizer.borrow_object(objtype) as obj:
                    return await func(obj, *args, **kwargs)
            else:
                return await func(*args, **kwargs)

        return wrapper
    return decorator
