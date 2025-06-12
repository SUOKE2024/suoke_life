"""
performance - 索克生活项目模块
"""

from .cache import get_cache_manager
from .monitoring import record_cache_metrics, record_db_metrics
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
import asyncio
import functools
import time

"""
性能优化模块

提供缓存优化、连接池管理、查询优化等性能提升功能。
"""




T = TypeVar('T')


@dataclass
class CacheConfig:
"""缓存配置"""
    ttl: int = 300  # 默认5分钟
    prefix: str = ""
    serialize: bool = True
    compress: bool = False


@dataclass
class QueryOptimization:
"""查询优化配置"""
    batch_size: int = 100
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0


class CacheDecorator:
"""缓存装饰器"""

    def __init__(self, config: CacheConfig):
    """TODO: 添加文档字符串"""
self.config = config

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
    """TODO: 添加文档字符串"""
@functools.wraps(func)
async def wrapper( * args,**kwargs) -> T:
    # 生成缓存键
cache_key = self._generate_cache_key(func.__name__, args, kwargs)

try:
    cache_manager = await get_cache_manager()

# 尝试从缓存获取
start_time = time.time()
cached_result = await cache_manager.get(cache_key)

if cached_result is not None:
    record_cache_metrics("get", success = True)
logger.debug(f"缓存命中: {cache_key}")
return cached_result

record_cache_metrics("get", success = False)

# 缓存未命中，执行函数
result = await func( * args,**kwargs)

# 存储到缓存
await cache_manager.set(
cache_key,
result,
ttl = self.config.ttl
)
record_cache_metrics("set", success = True)

logger.debug(f"缓存存储: {cache_key}")
return result

except Exception as e:
    logger.warning(f"缓存操作失败: {e}")
record_cache_metrics("get", success = False)
# 缓存失败时直接执行函数
return await func( * args,**kwargs)

return wrapper

    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
    """生成缓存键"""
# 简化的缓存键生成逻辑
key_parts = [self.config.prefix, func_name]

# 添加位置参数
for arg in args:
    if isinstance(arg, (str, int, float, bool)):
    key_parts.append(str(arg))

# 添加关键字参数
for k, v in sorted(kwargs.items()):
    if isinstance(v, (str, int, float, bool)):
    key_parts.append(f"{k}:{v}")

return ":".join(filter(None, key_parts))


class BatchProcessor:
"""批处理器"""

    def __init__(self, batch_size: int = 100, timeout: float = 5.0):
    """TODO: 添加文档字符串"""
self.batch_size = batch_size
self.timeout = timeout
self._queue: list[Any] = []
self._processing = False

    async def add_item(self, item: Any) -> None:
    """添加项目到批处理队列"""
self._queue.append(item)

if len(self._queue) >=self.batch_size:
    await self._process_batch()

    async def _process_batch(self) -> None:
    """处理批次"""
if self._processing or not self._queue:
    return

self._processing = True
try:
    batch = self._queue[:self.batch_size]
self._queue = self._queue[self.batch_size:]

# 这里应该实现具体的批处理逻辑
await self._execute_batch(batch)

finally:
    self._processing = False

    async def _execute_batch(self, batch: list[Any]) -> None:
    """执行批处理"""
# 子类应该重写此方法
pass

    async def flush(self) -> None:
    """强制处理所有待处理项目"""
while self._queue:
    await self._process_batch()


class ConnectionPool:
"""连接池管理器"""

    def __init__(self, max_connections: int = 10):
    """TODO: 添加文档字符串"""
self.max_connections = max_connections
self._connections: list[Any] = []
self._in_use: set = set()
self._lock = asyncio.Lock()

    async def acquire(self) -> Any:
    """获取连接"""
async with self._lock:
    # 尝试复用现有连接
for conn in self._connections:
    if conn not in self._in_use:
    self._in_use.add(conn)
return conn

# 创建新连接
if len(self._connections) < self.max_connections:
    conn = await self._create_connection()
self._connections.append(conn)
self._in_use.add(conn)
return conn

# 等待连接可用
while True:
    await asyncio.sleep(0.1)
for conn in self._connections:
    if conn not in self._in_use:
    self._in_use.add(conn)
return conn

    async def release(self, connection: Any) -> None:
    """释放连接"""
async with self._lock:
    if connection in self._in_use:
    self._in_use.remove(connection)

    async def _create_connection(self) -> Any:
    """创建新连接"""
# 子类应该重写此方法
return object()

    async def close_all(self) -> None:
    """关闭所有连接"""
async with self._lock:
    for conn in self._connections:
    await self._close_connection(conn)
self._connections.clear()
self._in_use.clear()

    async def _close_connection(self, connection: Any) -> None:
    """关闭连接"""
# 子类应该重写此方法
pass


class QueryOptimizer:
"""查询优化器"""

    def __init__(self, config: QueryOptimization):
    """TODO: 添加文档字符串"""
self.config = config

    async def execute_with_retry(
self,
operation: Callable[..., T],
* args,
**kwargs
    ) -> T:
    """带重试的执行操作"""
last_exception = None

for attempt in range(self.config.retry_count):
    try:
    start_time = time.time()

# 设置超时
result = await asyncio.wait_for(
operation( * args,**kwargs),
timeout = self.config.timeout
)

duration = time.time() - start_time
record_db_metrics("query", "unknown", duration, success = True)

return result

except asyncio.TimeoutError as e:
    last_exception = e
logger.warning(f"操作超时 (尝试 {attempt + 1} / {self.config.retry_count})")

except Exception as e:
    last_exception = e
logger.warning(f"操作失败 (尝试 {attempt + 1} / {self.config.retry_count}): {e}")

# 重试延迟
if attempt < self.config.retry_count - 1:
    await asyncio.sleep(self.config.retry_delay * (2 * * attempt))

# 记录失败指标
record_db_metrics("query", "unknown", 0, success = False)
raise last_exception

    async def execute_batch_query(
self,
queries: list[Callable[..., T]],
max_concurrent: int = 5
    ) -> list[T]:
    """批量执行查询"""
semaphore = asyncio.Semaphore(max_concurrent)

async def execute_single(query_func):
    async with semaphore:
    return await self.execute_with_retry(query_func)

tasks = [execute_single(query) for query in queries]
return await asyncio.gather( * tasks, return_exceptions = True)


class PerformanceMonitor:
"""性能监控器"""

    def __init__(self) -> None:
    """TODO: 添加文档字符串"""
self._metrics: dict[str, list[float]] = {}
self._start_times: dict[str, float] = {}

    @asynccontextmanager
async def measure(self, operation_name: str):
    """测量操作性能"""
start_time = time.time()
self._start_times[operation_name] = start_time

try:
    yield
finally:
    duration = time.time() - start_time

if operation_name not in self._metrics:
    self._metrics[operation_name] = []

self._metrics[operation_name].append(duration)

# 保持最近100个测量值
if len(self._metrics[operation_name]) > 100:
    self._metrics[operation_name] = self._metrics[operation_name][ - 100:]

logger.debug(f"操作 {operation_name} 耗时: {duration:.3f}s")

    def get_stats(self, operation_name: str) -> dict[str, float]:
    """获取操作统计信息"""
if operation_name not in self._metrics:
    return {}

durations = self._metrics[operation_name]
if not durations:
    return {}

return {
"count": len(durations),
"avg": sum(durations) / len(durations),
"min": min(durations),
"max": max(durations),
"p95": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
}

    def get_all_stats(self) -> dict[str, dict[str, float]]:
    """获取所有操作的统计信息"""
return {
operation: self.get_stats(operation)
for operation in self._metrics.keys()
}


# 全局实例
performance_monitor = PerformanceMonitor()
query_optimizer = QueryOptimizer(QueryOptimization())


def cache_result(ttl: int = 300, prefix: str = "") -> Callable:
"""缓存结果装饰器"""
    config = CacheConfig(ttl = ttl, prefix = prefix)
    return CacheDecorator(config)


async def warm_up_cache(cache_keys: list[str], warm_up_func: Callable) -> None:
    """预热缓存"""
    try:
    cache_manager = await get_cache_manager()

for key in cache_keys:
    cached_value = await cache_manager.get(key)
if cached_value is None:
    # 缓存未命中，执行预热函数
value = await warm_up_func(key)
await cache_manager.set(key, value, ttl = 3600)  # 1小时TTL
logger.info(f"缓存预热完成: {key}")

    except Exception as e:
    logger.error(f"缓存预热失败: {e}")


async def optimize_database_queries() -> None:
    """优化数据库查询"""
    # 这里可以实现查询优化逻辑
    # 例如：预编译常用查询、创建索引建议等
    logger.info("数据库查询优化完成")


def get_performance_stats() -> dict[str, Any]:
"""获取性能统计信息"""
    return {
"timestamp": datetime.now().isoformat(),
"operations": performance_monitor.get_all_stats(),
"cache_stats": {
# 这里可以添加缓存统计信息
},
"connection_pool_stats": {
# 这里可以添加连接池统计信息
}
    }
