"""
optimization - 索克生活项目模块
"""

    import redis
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps, lru_cache
from typing import Dict, List, Any, Optional, Callable, TypeVar, Generic
import asyncio
import gc
import hashlib
import pickle
import psutil
import threading
import time
import weakref

"""性能优化模块

提供缓存优化、并发控制、资源管理等性能优化功能
"""


try:
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

T = TypeVar('T')


@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class LRUCache(Generic[T]):
    """LRU 缓存实现"""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[int] = None):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, tuple[T, float]] = OrderedDict()
        self._stats = CacheStats(max_size=max_size)
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
            
            value, timestamp = self._cache[key]
            
            # 检查 TTL
            if self.ttl and time.time() - timestamp > self.ttl:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None
            
            # 移动到末尾（最近使用）
            self._cache.move_to_end(key)
            self._stats.hits += 1
            return value
    
    def put(self, key: str, value: T) -> None:
        """设置缓存值"""
        with self._lock:
            current_time = time.time()
            
            if key in self._cache:
                # 更新现有值
                self._cache[key] = (value, current_time)
                self._cache.move_to_end(key)
            else:
                # 添加新值
                if len(self._cache) >= self.max_size:
                    # 移除最旧的项
                    self._cache.popitem(last=False)
                    self._stats.evictions += 1
                
                self._cache[key] = (value, current_time)
            
            self._stats.size = len(self._cache)
    
    def remove(self, key: str) -> bool:
        """移除缓存项"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._stats.size = 0
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        return self._stats
    
    def keys(self) -> List[str]:
        """获取所有键"""
        with self._lock:
            return list(self._cache.keys())


class MultiLevelCache:
    """多级缓存"""
    
    def __init__(
        self,
        l1_size: int = 100,
        l2_size: int = 1000,
        redis_client: Optional[Any] = None,
        ttl: int = 3600
    ):
        # L1: 内存缓存（最热数据）
        self.l1_cache = LRUCache[Any](max_size=l1_size, ttl=ttl)
        
        # L2: 内存缓存（热数据）
        self.l2_cache = LRUCache[Any](max_size=l2_size, ttl=ttl * 2)
        
        # L3: Redis 缓存（温数据）
        self.redis_client = redis_client if REDIS_AVAILABLE else None
        self.redis_ttl = ttl * 4
        
        self._lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        # 尝试 L1 缓存
        value = self.l1_cache.get(key)
        if value is not None:
            return value
        
        # 尝试 L2 缓存
        value = self.l2_cache.get(key)
        if value is not None:
            # 提升到 L1
            self.l1_cache.put(key, value)
            return value
        
        # 尝试 Redis 缓存
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    value = pickle.loads(cached_data)
                    # 提升到 L2 和 L1
                    self.l2_cache.put(key, value)
                    self.l1_cache.put(key, value)
                    return value
            except Exception:
                pass
        
        return None
    
    async def put(self, key: str, value: Any) -> None:
        """设置缓存值"""
        # 存储到所有级别
        self.l1_cache.put(key, value)
        self.l2_cache.put(key, value)
        
        # 异步存储到 Redis
        if self.redis_client:
            try:
                serialized_value = pickle.dumps(value)
                await self.redis_client.setex(key, self.redis_ttl, serialized_value)
            except Exception:
                pass
    
    async def remove(self, key: str) -> None:
        """移除缓存项"""
        self.l1_cache.remove(key)
        self.l2_cache.remove(key)
        
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception:
                pass
    
    async def clear(self) -> None:
        """清空所有缓存"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        
        if self.redis_client:
            try:
                await self.redis_client.flushdb()
            except Exception:
                pass
    
    def get_stats(self) -> Dict[str, CacheStats]:
        """获取缓存统计"""
        return {
            "l1": self.l1_cache.get_stats(),
            "l2": self.l2_cache.get_stats()
        }


class ResourcePool(Generic[T]):
    """资源池"""
    
    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 10,
        min_size: int = 2,
        max_idle_time: int = 300
    ):
        self.factory = factory
        self.max_size = max_size
        self.min_size = min_size
        self.max_idle_time = max_idle_time
        
        self._pool: List[tuple[T, float]] = []
        self._in_use: set[T] = set()
        self._lock = asyncio.Lock()
        
        # 初始化最小数量的资源
        for _ in range(min_size):
            resource = factory()
            self._pool.append((resource, time.time()))
    
    async def acquire(self) -> T:
        """获取资源"""
        async with self._lock:
            # 清理过期资源
            await self._cleanup_expired()
            
            # 尝试从池中获取
            if self._pool:
                resource, _ = self._pool.pop()
                self._in_use.add(resource)
                return resource
            
            # 如果池为空且未达到最大限制，创建新资源
            if len(self._in_use) < self.max_size:
                resource = self.factory()
                self._in_use.add(resource)
                return resource
            
            # 等待资源释放
            while not self._pool and len(self._in_use) >= self.max_size:
                await asyncio.sleep(0.1)
            
            # 重试获取
            if self._pool:
                resource, _ = self._pool.pop()
                self._in_use.add(resource)
                return resource
            
            raise RuntimeError("无法获取资源")
    
    async def release(self, resource: T) -> None:
        """释放资源"""
        async with self._lock:
            if resource in self._in_use:
                self._in_use.remove(resource)
                self._pool.append((resource, time.time()))
    
    async def _cleanup_expired(self) -> None:
        """清理过期资源"""
        current_time = time.time()
        self._pool = [
            (resource, timestamp)
            for resource, timestamp in self._pool
            if current_time - timestamp < self.max_idle_time
        ]
        
        # 确保最小数量
        while len(self._pool) + len(self._in_use) < self.min_size:
            resource = self.factory()
            self._pool.append((resource, current_time))
    
    @asynccontextmanager
    async def get_resource(self):
        """上下文管理器方式获取资源"""
        resource = await self.acquire()
        try:
            yield resource
        finally:
            await self.release(resource)
    
    def get_stats(self) -> Dict[str, int]:
        """获取池统计"""
        return {
            "pool_size": len(self._pool),
            "in_use": len(self._in_use),
            "total": len(self._pool) + len(self._in_use)
        }


class ConcurrencyLimiter:
    """并发限制器"""
    
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_count = 0
        self._lock = asyncio.Lock()
    
    @asynccontextmanager
    async def acquire(self):
        """获取并发许可"""
        await self._semaphore.acquire()
        async with self._lock:
            self._active_count += 1
        
        try:
            yield
        finally:
            async with self._lock:
                self._active_count -= 1
            self._semaphore.release()
    
    def get_active_count(self) -> int:
        """获取当前活跃数量"""
        return self._active_count


class MemoryManager:
    """内存管理器"""
    
    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self._weak_refs: List[weakref.ref] = []
        self._lock = threading.Lock()
    
    def register_object(self, obj: Any) -> None:
        """注册对象用于内存管理"""
        with self._lock:
            self._weak_refs.append(weakref.ref(obj))
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """检查内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "used_gb": memory.used / (1024**3),
            "available_gb": memory.available / (1024**3),
            "percent": memory.percent,
            "is_high": memory.percent > self.max_memory_percent
        }
    
    def cleanup_if_needed(self) -> bool:
        """如果需要则清理内存"""
        memory_info = self.check_memory_usage()
        
        if memory_info["is_high"]:
            return self.force_cleanup()
        
        return False
    
    def force_cleanup(self) -> bool:
        """强制清理内存"""
        # 清理弱引用
        with self._lock:
            self._weak_refs = [ref for ref in self._weak_refs if ref() is not None]
        
        # 强制垃圾回收
        collected = gc.collect()
        
        return collected > 0


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 初始化组件
        self.cache = MultiLevelCache(
            l1_size=self.config.get("l1_cache_size", 100),
            l2_size=self.config.get("l2_cache_size", 1000),
            ttl=self.config.get("cache_ttl", 3600)
        )
        
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.get("max_threads", 10)
        )
        
        self.process_pool = ProcessPoolExecutor(
            max_workers=self.config.get("max_processes", 4)
        )
        
        self.concurrency_limiter = ConcurrencyLimiter(
            max_concurrent=self.config.get("max_concurrent", 20)
        )
        
        self.memory_manager = MemoryManager(
            max_memory_percent=self.config.get("max_memory_percent", 80.0)
        )
        
        # 资源池
        self._resource_pools: Dict[str, ResourcePool] = {}
    
    def create_resource_pool(
        self,
        name: str,
        factory: Callable[[], T],
        max_size: int = 10,
        min_size: int = 2
    ) -> ResourcePool[T]:
        """创建资源池"""
        pool = ResourcePool(factory, max_size, min_size)
        self._resource_pools[name] = pool
        return pool
    
    def get_resource_pool(self, name: str) -> Optional[ResourcePool]:
        """获取资源池"""
        return self._resource_pools.get(name)
    
    async def cached_call(
        self,
        func: Callable,
        *args,
        cache_key: Optional[str] = None,
        ttl: Optional[int] = None,
        **kwargs
    ) -> Any:
        """缓存函数调用"""
        # 生成缓存键
        if cache_key is None:
            key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
        
        # 尝试从缓存获取
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 执行函数
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        # 存储到缓存
        await self.cache.put(cache_key, result)
        
        return result
    
    async def concurrent_execute(
        self,
        func: Callable,
        items: List[Any],
        max_concurrent: Optional[int] = None
    ) -> List[Any]:
        """并发执行函数"""
        if max_concurrent:
            limiter = ConcurrencyLimiter(max_concurrent)
        else:
            limiter = self.concurrency_limiter
        
        async def execute_item(item):
            async with limiter.acquire():
                if asyncio.iscoroutinefunction(func):
                    return await func(item)
                else:
                    return func(item)
        
        tasks = [execute_item(item) for item in items]
        return await asyncio.gather(*tasks)
    
    async def batch_process(
        self,
        func: Callable,
        items: List[Any],
        batch_size: int = 10,
        max_concurrent: int = 5
    ) -> List[Any]:
        """批量处理"""
        results = []
        
        # 分批处理
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await self.concurrent_execute(func, batch, max_concurrent)
            results.extend(batch_results)
            
            # 检查内存使用
            if self.memory_manager.cleanup_if_needed():
                await asyncio.sleep(0.1)  # 给 GC 一些时间
        
        return results
    
    def cpu_bound_task(self, func: Callable, *args, **kwargs):
        """CPU 密集型任务"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.process_pool, func, *args, **kwargs)
    
    def io_bound_task(self, func: Callable, *args, **kwargs):
        """IO 密集型任务"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            "cache": self.cache.get_stats(),
            "memory": self.memory_manager.check_memory_usage(),
            "concurrency": {
                "active_count": self.concurrency_limiter.get_active_count(),
                "max_concurrent": self.concurrency_limiter.max_concurrent
            },
            "resource_pools": {
                name: pool.get_stats()
                for name, pool in self._resource_pools.items()
            }
        }
    
    async def cleanup(self) -> None:
        """清理资源"""
        await self.cache.clear()
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        self.memory_manager.force_cleanup()


# 装饰器
def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func):
        cache = LRUCache(max_size=1000, ttl=ttl)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            cache.put(cache_key, result)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存储到缓存
            cache.put(cache_key, result)
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def rate_limit(max_calls: int, time_window: int = 60):
    """限流装饰器"""
    calls = defaultdict(list)
    lock = threading.Lock()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = f"{func.__name__}"
            
            with lock:
                # 清理过期记录
                calls[key] = [
                    call_time for call_time in calls[key]
                    if current_time - call_time < time_window
                ]
                
                # 检查限流
                if len(calls[key]) >= max_calls:
                    raise RuntimeError(f"Rate limit exceeded: {max_calls} calls per {time_window} seconds")
                
                # 记录调用
                calls[key].append(current_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# 全局性能优化器
global_optimizer: Optional[PerformanceOptimizer] = None


def get_global_optimizer() -> PerformanceOptimizer:
    """获取全局性能优化器"""
    global global_optimizer
    if global_optimizer is None:
        raise RuntimeError("性能优化器未初始化")
    return global_optimizer


def init_performance_optimizer(config: Optional[Dict] = None) -> PerformanceOptimizer:
    """初始化性能优化器"""
    global global_optimizer
    global_optimizer = PerformanceOptimizer(config)
    return global_optimizer 