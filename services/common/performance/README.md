# 微服务性能优化方案

## 概述

索克生活平台需要处理大量并发用户请求，本文档提供全面的性能优化方案。

## 性能优化策略

### 1. 异步处理优化

```python
# async_optimization.py
import asyncio
from typing import List, Any, Callable, TypeVar, Coroutine
from functools import wraps
import time

T = TypeVar('T')

class AsyncBatcher:
    """批量处理异步请求，减少 I/O 开销"""
    
    def __init__(self, batch_size: int = 100, timeout: float = 0.1):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending_items: List[tuple] = []
        self.results: dict = {}
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition()
    
    async def add_item(self, key: str, item: Any) -> Any:
        """添加项目到批处理队列"""
        future = asyncio.Future()
        
        async with self._lock:
            self.pending_items.append((key, item, future))
            
            if len(self.pending_items) >= self.batch_size:
                await self._process_batch()
        
        # 等待结果
        return await future
    
    async def _process_batch(self):
        """处理批次"""
        if not self.pending_items:
            return
        
        batch = self.pending_items[:self.batch_size]
        self.pending_items = self.pending_items[self.batch_size:]
        
        # 批量处理
        results = await self._batch_processor([item[1] for item in batch])
        
        # 设置结果
        for (key, item, future), result in zip(batch, results):
            future.set_result(result)

# 连接池优化
from contextlib import asynccontextmanager
import aioredis
import asyncpg

class ConnectionPoolManager:
    """统一管理各种连接池"""
    
    def __init__(self):
        self.redis_pool = None
        self.pg_pool = None
        self.initialized = False
    
    async def initialize(self, config: dict):
        """初始化所有连接池"""
        # Redis 连接池
        self.redis_pool = await aioredis.create_redis_pool(
            config['redis']['url'],
            minsize=config['redis'].get('min_connections', 5),
            maxsize=config['redis'].get('max_connections', 20),
            timeout=config['redis'].get('timeout', 5)
        )
        
        # PostgreSQL 连接池
        self.pg_pool = await asyncpg.create_pool(
            config['postgres']['dsn'],
            min_size=config['postgres'].get('min_connections', 10),
            max_size=config['postgres'].get('max_connections', 50),
            timeout=config['postgres'].get('timeout', 10),
            command_timeout=config['postgres'].get('command_timeout', 10)
        )
        
        self.initialized = True
    
    @asynccontextmanager
    async def get_redis(self):
        """获取 Redis 连接"""
        async with self.redis_pool.get() as conn:
            yield conn
    
    @asynccontextmanager
    async def get_postgres(self):
        """获取 PostgreSQL 连接"""
        async with self.pg_pool.acquire() as conn:
            yield conn
```

### 2. 缓存策略优化

```python
# cache_optimization.py
from typing import Optional, Any, Callable
import asyncio
import hashlib
import json
import time

class MultiLevelCache:
    """多级缓存系统"""
    
    def __init__(self, l1_size: int = 1000, l2_ttl: int = 300):
        # L1: 内存缓存（LRU）
        self.l1_cache = LRUCache(l1_size)
        # L2: Redis 缓存
        self.l2_cache = None  # Redis client
        self.l2_ttl = l2_ttl
        
        # 缓存预热
        self.warmer = CacheWarmer()
        
        # 缓存统计
        self.stats = CacheStats()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        # L1 查找
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats.l1_hit()
            return value
        
        # L2 查找
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                self.stats.l2_hit()
                # 提升到 L1
                self.l1_cache.set(key, value)
                return json.loads(value)
        
        self.stats.miss()
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        # 设置 L1
        self.l1_cache.set(key, value)
        
        # 设置 L2
        if self.l2_cache:
            ttl = ttl or self.l2_ttl
            await self.l2_cache.setex(key, ttl, json.dumps(value))
    
    def cache_aside(self, ttl: int = 300):
        """Cache-Aside 模式装饰器"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._generate_key(func.__name__, args, kwargs)
                
                # 尝试从缓存获取
                cached = await self.get(cache_key)
                if cached is not None:
                    return cached
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 写入缓存
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

class CacheWarmer:
    """缓存预热器"""
    
    def __init__(self):
        self.warmup_tasks = []
    
    def register_warmup_task(self, task: Callable):
        """注册预热任务"""
        self.warmup_tasks.append(task)
    
    async def warm_cache(self):
        """执行缓存预热"""
        tasks = [task() for task in self.warmup_tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. 数据库查询优化

```python
# db_optimization.py
from typing import List, Dict, Any, Optional
import asyncpg
from dataclasses import dataclass

@dataclass
class QueryOptimizer:
    """SQL 查询优化器"""
    
    async def explain_analyze(self, conn: asyncpg.Connection, query: str, params: list) -> Dict[str, Any]:
        """分析查询性能"""
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
        result = await conn.fetchval(explain_query, *params)
        return json.loads(result)
    
    async def suggest_indexes(self, conn: asyncpg.Connection, table: str) -> List[str]:
        """建议索引"""
        # 分析表的查询模式
        query = """
        SELECT 
            schemaname,
            tablename,
            attname,
            n_distinct,
            most_common_vals
        FROM pg_stats
        WHERE tablename = $1
        """
        stats = await conn.fetch(query, table)
        
        suggestions = []
        for stat in stats:
            if stat['n_distinct'] > 100:
                suggestions.append(f"CREATE INDEX idx_{table}_{stat['attname']} ON {table}({stat['attname']});")
        
        return suggestions

class QueryBatcher:
    """批量查询处理器"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.pending_queries = []
        self.lock = asyncio.Lock()
    
    async def add_query(self, query: str, params: list) -> Any:
        """添加查询到批处理"""
        future = asyncio.Future()
        
        async with self.lock:
            self.pending_queries.append((query, params, future))
            
            if len(self.pending_queries) >= self.batch_size:
                await self._execute_batch()
        
        return await future
    
    async def _execute_batch(self):
        """批量执行查询"""
        if not self.pending_queries:
            return
        
        batch = self.pending_queries[:self.batch_size]
        self.pending_queries = self.pending_queries[self.batch_size:]
        
        # 使用事务批量执行
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for query, params, future in batch:
                    try:
                        result = await conn.fetch(query, *params)
                        future.set_result(result)
                    except Exception as e:
                        future.set_exception(e)
```

### 4. API 响应优化

```python
# response_optimization.py
import gzip
import json
from typing import Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class CompressionMiddleware(BaseHTTPMiddleware):
    """响应压缩中间件"""
    
    def __init__(self, app, minimum_size: int = 1000):
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 检查是否支持压缩
        accept_encoding = request.headers.get('accept-encoding', '')
        if 'gzip' not in accept_encoding:
            return response
        
        # 读取响应内容
        body = b''
        async for chunk in response.body_iterator:
            body += chunk
        
        # 压缩响应
        if len(body) > self.minimum_size:
            compressed = gzip.compress(body)
            if len(compressed) < len(body):
                headers = dict(response.headers)
                headers['content-encoding'] = 'gzip'
                headers['content-length'] = str(len(compressed))
                
                return Response(
                    content=compressed,
                    status_code=response.status_code,
                    headers=headers
                )
        
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

class PaginationOptimizer:
    """分页查询优化"""
    
    @staticmethod
    async def cursor_pagination(
        conn: asyncpg.Connection,
        query: str,
        cursor: Optional[str],
        limit: int = 20
    ) -> Dict[str, Any]:
        """游标分页（高效）"""
        if cursor:
            query += f" WHERE id > ${len(params) + 1}"
            params.append(cursor)
        
        query += f" ORDER BY id LIMIT ${len(params) + 1}"
        params.append(limit + 1)
        
        rows = await conn.fetch(query, *params)
        
        has_next = len(rows) > limit
        if has_next:
            rows = rows[:-1]
        
        next_cursor = rows[-1]['id'] if has_next and rows else None
        
        return {
            'data': rows,
            'next_cursor': next_cursor,
            'has_next': has_next
        }
```

### 5. 性能监控配置

```yaml
# performance-config.yaml
performance:
  # 异步处理配置
  async:
    batch_size: 100
    batch_timeout: 0.1
    max_concurrent_requests: 1000
  
  # 连接池配置
  connection_pools:
    redis:
      min_connections: 10
      max_connections: 50
      timeout: 5
    postgres:
      min_connections: 20
      max_connections: 100
      timeout: 10
      statement_cache_size: 100
  
  # 缓存配置
  cache:
    l1_size: 10000
    l2_ttl: 600
    warm_on_startup: true
    cache_aside_ttl: 300
  
  # 查询优化
  query:
    slow_query_threshold: 100  # ms
    enable_query_cache: true
    batch_size: 50
  
  # API 优化
  api:
    enable_compression: true
    compression_min_size: 1000
    pagination_default_size: 20
    pagination_max_size: 100
```

## 性能测试和基准

```python
# performance_benchmark.py
import asyncio
import time
from locust import HttpUser, task, between

class PerformanceTest:
    """性能测试工具"""
    
    @staticmethod
    async def load_test(url: str, concurrent: int, duration: int):
        """负载测试"""
        async def make_request():
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return response.status
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            tasks = [make_request() for _ in range(concurrent)]
            await asyncio.gather(*tasks)
            request_count += concurrent
        
        elapsed = time.time() - start_time
        qps = request_count / elapsed
        
        return {
            'requests': request_count,
            'duration': elapsed,
            'qps': qps
        }

class SuokeLifeUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def test_api_gateway(self):
        self.client.get("/api/health")
    
    @task(3)
    def test_user_service(self):
        self.client.get("/api/users/profile")
```

## 优化清单

- [ ] 实施异步批处理
- [ ] 配置多级缓存
- [ ] 优化数据库连接池
- [ ] 实施查询优化
- [ ] 启用响应压缩
- [ ] 配置 CDN
- [ ] 实施限流
- [ ] 监控慢查询
- [ ] 定期性能测试 