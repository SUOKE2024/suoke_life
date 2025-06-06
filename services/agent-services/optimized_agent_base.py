"""
optimized_agent_base - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from aiohttp import web, ClientSession
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import wraps, lru_cache
from numba import jit
from typing import Dict, List, Any, Optional, Union, Callable
import aioredis
import asyncio
import asyncpg
import hashlib
import json
import logging
import multiprocessing
import pickle
import psutil
import threading
import time
import uuid

#!/usr/bin/env python3
"""
索克生活 - 优化后的智能体服务基础类
为四个智能体（小艾、小克、老克、索儿）提供统一的优化基础架构
"""


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentRequest:
    """智能体请求数据结构"""
    request_id: str
    agent_type: str
    action: str
    input_data: Dict[str, Any]
    user_id: Optional[str] = None
    priority: int = 1
    timeout: float = 30.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AgentResponse:
    """智能体响应数据结构"""
    request_id: str
    agent_type: str
    action: str
    result: Dict[str, Any]
    success: bool
    execution_time: float
    memory_usage: float
    error_message: Optional[str] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now()

class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.profiles = {}
        self.lock = threading.Lock()
    
    def profile_function(self, func_name: str):
        """函数性能分析装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    
                    self._record_profile(
                        func_name,
                        end_time - start_time,
                        end_memory - start_memory,
                        success,
                        error
                    )
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    
                    self._record_profile(
                        func_name,
                        end_time - start_time,
                        end_memory - start_memory,
                        success,
                        error
                    )
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def _record_profile(self, func_name: str, execution_time: float, 
                       memory_usage: float, success: bool, error: Optional[str]):
        """记录性能数据"""
        with self.lock:
            if func_name not in self.profiles:
                self.profiles[func_name] = {
                    'call_count': 0,
                    'total_time': 0.0,
                    'total_memory': 0.0,
                    'success_count': 0,
                    'error_count': 0,
                    'avg_time': 0.0,
                    'avg_memory': 0.0,
                    'last_error': None
                }
            
            profile = self.profiles[func_name]
            profile['call_count'] += 1
            profile['total_time'] += execution_time
            profile['total_memory'] += memory_usage
            
            if success:
                profile['success_count'] += 1
            else:
                profile['error_count'] += 1
                profile['last_error'] = error
            
            profile['avg_time'] = profile['total_time'] / profile['call_count']
            profile['avg_memory'] = profile['total_memory'] / profile['call_count']
    
    def get_profiles(self) -> Dict[str, Any]:
        """获取性能分析数据"""
        with self.lock:
            return self.profiles.copy()

class OptimizedCache:
    """优化缓存系统"""
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis = redis_client
        self.local_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self.lock = asyncio.Lock()
    
    async def get(self, key: str, use_local: bool = True) -> Optional[Any]:
        """获取缓存值"""
        # 先尝试本地缓存
        if use_local and key in self.local_cache:
            self.cache_stats['hits'] += 1
            return self.local_cache[key]['value']
        
        # 尝试Redis缓存
        if self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    data = pickle.loads(value)
                    # 更新本地缓存
                    if use_local:
                        self.local_cache[key] = {
                            'value': data,
                            'timestamp': time.time()
                        }
                    self.cache_stats['hits'] += 1
                    return data
            except Exception as e:
                logger.error(f"Redis缓存获取失败: {key}, 错误: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300, use_local: bool = True):
        """设置缓存值"""
        # 设置本地缓存
        if use_local:
            self.local_cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
        
        # 设置Redis缓存
        if self.redis:
            try:
                serialized_value = pickle.dumps(value)
                await self.redis.setex(key, ttl, serialized_value)
            except Exception as e:
                logger.error(f"Redis缓存设置失败: {key}, 错误: {e}")
        
        self.cache_stats['sets'] += 1
    
    async def delete(self, key: str):
        """删除缓存值"""
        # 删除本地缓存
        self.local_cache.pop(key, None)
        
        # 删除Redis缓存
        if self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                logger.error(f"Redis缓存删除失败: {key}, 错误: {e}")
        
        self.cache_stats['deletes'] += 1
    
    def cleanup_local_cache(self):
        """清理过期的本地缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.local_cache.items():
            if current_time - data['timestamp'] > data.get('ttl', 300):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.local_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            'hit_rate': hit_rate,
            'local_cache_size': len(self.local_cache)
        }

class JITOptimizedAlgorithms:
    """JIT优化算法库"""
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def vector_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """向量相似度计算 - JIT优化"""
        dot_product = 0.0
        norm1 = 0.0
        norm2 = 0.0
        
        for i in range(len(vec1)):
            dot_product += vec1[i] * vec2[i]
            norm1 += vec1[i] * vec1[i]
            norm2 += vec2[i] * vec2[i]
        
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        
        return dot_product / (np.sqrt(norm1) * np.sqrt(norm2))
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def weighted_average(values: np.ndarray, weights: np.ndarray) -> float:
        """加权平均计算 - JIT优化"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for i in range(len(values)):
            weighted_sum += values[i] * weights[i]
            total_weight += weights[i]
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def matrix_multiply_optimized(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """优化矩阵乘法 - JIT优化"""
        rows_a, cols_a = a.shape
        rows_b, cols_b = b.shape
        
        if cols_a != rows_b:
            raise ValueError("Matrix dimensions don't match")
        
        result = np.zeros((rows_a, cols_b))
        
        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i, j] += a[i, k] * b[k, j]
        
        return result

class OptimizedAgentBase(ABC):
    """优化后的智能体基础类"""
    
    def __init__(self, 
                 agent_name: str,
                 max_workers: Optional[int] = None,
                 redis_url: Optional[str] = None,
                 database_url: Optional[str] = None):
        self.agent_name = agent_name
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.redis_url = redis_url
        self.database_url = database_url
        
        # 核心组件
        self.cpu_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        self.io_pool = ThreadPoolExecutor(max_workers=self.max_workers * 2)
        
        # 性能监控
        self.profiler = PerformanceProfiler()
        
        # 缓存系统
        self.redis_client: Optional[aioredis.Redis] = None
        self.cache: Optional[OptimizedCache] = None
        
        # 数据库连接池
        self.db_pool: Optional[asyncpg.Pool] = None
        
        # HTTP客户端
        self.http_session: Optional[ClientSession] = None
        
        # JIT算法库
        self.algorithms = JITOptimizedAlgorithms()
        
        # Web应用
        self.app: Optional[web.Application] = None
        
        logger.info(f"智能体 {agent_name} 初始化完成")
    
    async def initialize(self):
        """异步初始化"""
        # 初始化Redis连接
        if self.redis_url:
            self.redis_client = await aioredis.from_url(self.redis_url)
            self.cache = OptimizedCache(self.redis_client)
        else:
            self.cache = OptimizedCache()
        
        # 初始化数据库连接池
        if self.database_url:
            self.db_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20
            )
        
        # 初始化HTTP客户端
        self.http_session = ClientSession()
        
        # 初始化Web应用
        self._setup_web_app()
        
        # 预热JIT算法
        await self._warmup_jit_algorithms()
        
        # 启动后台任务
        asyncio.create_task(self._background_tasks())
        
        logger.info(f"智能体 {self.agent_name} 异步初始化完成")
    
    def _setup_web_app(self):
        """设置Web应用"""
        self.app = web.Application()
        
        # 注册通用路由
        self.app.router.add_post("/process", self._process_handler)
        self.app.router.add_get("/health", self._health_handler)
        self.app.router.add_get("/metrics", self._metrics_handler)
        self.app.router.add_get("/profiles", self._profiles_handler)
        
        # 注册智能体特定路由
        self._register_agent_routes()
    
    @abstractmethod
    def _register_agent_routes(self):
        """注册智能体特定路由 - 子类实现"""
        pass
    
    async def _warmup_jit_algorithms(self):
        """预热JIT算法"""
        logger.info(f"预热 {self.agent_name} JIT算法...")
        
        # 创建测试数据
        test_vec1 = np.random.rand(100).astype(np.float32)
        test_vec2 = np.random.rand(100).astype(np.float32)
        test_values = np.random.rand(50).astype(np.float32)
        test_weights = np.random.rand(50).astype(np.float32)
        
        # 在进程池中预热
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.cpu_pool,
            self.algorithms.vector_similarity,
            test_vec1,
            test_vec2
        )
        
        await loop.run_in_executor(
            self.cpu_pool,
            self.algorithms.weighted_average,
            test_values,
            test_weights
        )
        
        logger.info(f"{self.agent_name} JIT算法预热完成")
    
    async def _background_tasks(self):
        """后台任务"""
        while True:
            try:
                # 清理本地缓存
                if self.cache:
                    self.cache.cleanup_local_cache()
                
                # 其他后台任务
                await self._custom_background_tasks()
                
                await asyncio.sleep(60)  # 每分钟执行一次
            except Exception as e:
                logger.error(f"{self.agent_name} 后台任务错误: {e}")
                await asyncio.sleep(10)
    
    async def _custom_background_tasks(self):
        """自定义后台任务 - 子类可重写"""
        pass
    
    @profiler.profile_function("process_request")
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """处理请求的主入口"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            # 检查缓存
            cache_key = self._generate_cache_key(request)
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                logger.info(f"缓存命中: {request.request_id}")
                return AgentResponse(
                    request_id=request.request_id,
                    agent_type=self.agent_name,
                    action=request.action,
                    result=cached_result,
                    success=True,
                    execution_time=time.time() - start_time,
                    memory_usage=0.0
                )
            
            # 处理请求
            result = await self._process_action(request)
            
            # 缓存结果
            await self.cache.set(cache_key, result, ttl=300)
            
            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory
            
            return AgentResponse(
                request_id=request.request_id,
                agent_type=self.agent_name,
                action=request.action,
                result=result,
                success=True,
                execution_time=execution_time,
                memory_usage=memory_usage
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory
            
            logger.error(f"{self.agent_name} 处理请求失败: {request.request_id}, 错误: {e}")
            
            return AgentResponse(
                request_id=request.request_id,
                agent_type=self.agent_name,
                action=request.action,
                result={},
                success=False,
                execution_time=execution_time,
                memory_usage=memory_usage,
                error_message=str(e)
            )
    
    @abstractmethod
    async def _process_action(self, request: AgentRequest) -> Dict[str, Any]:
        """处理具体动作 - 子类实现"""
        pass
    
    def _generate_cache_key(self, request: AgentRequest) -> str:
        """生成缓存键"""
        key_data = {
            'agent': self.agent_name,
            'action': request.action,
            'input_hash': hashlib.md5(
                json.dumps(request.input_data, sort_keys=True).encode()
            ).hexdigest()
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"agent_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def _process_handler(self, request: web.Request) -> web.Response:
        """处理HTTP请求"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', str(uuid.uuid4())),
                agent_type=self.agent_name,
                action=data['action'],
                input_data=data['input_data'],
                user_id=data.get('user_id'),
                priority=data.get('priority', 1),
                timeout=data.get('timeout', 30.0)
            )
            
            response = await self.process_request(agent_request)
            
            return web.json_response(asdict(response))
            
        except Exception as e:
            logger.error(f"{self.agent_name} HTTP请求处理失败: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def _health_handler(self, request: web.Request) -> web.Response:
        """健康检查处理器"""
        health_status = {
            "agent": self.agent_name,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "active_workers": self.max_workers
            }
        }
        
        return web.json_response(health_status)
    
    async def _metrics_handler(self, request: web.Request) -> web.Response:
        """指标处理器"""
        metrics = {
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "cache_stats": self.cache.get_stats() if self.cache else {},
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent
            }
        }
        
        return web.json_response(metrics)
    
    async def _profiles_handler(self, request: web.Request) -> web.Response:
        """性能分析处理器"""
        profiles = self.profiler.get_profiles()
        
        return web.json_response({
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "profiles": profiles
        })
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """启动服务器"""
        await self.initialize()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"智能体 {self.agent_name} 服务启动: http://{host}:{port}")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"正在关闭智能体 {self.agent_name}...")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """关闭智能体服务"""
        logger.info(f"正在关闭智能体 {self.agent_name}...")
        
        # 关闭进程池和线程池
        self.cpu_pool.shutdown(wait=True)
        self.io_pool.shutdown(wait=True)
        
        # 关闭HTTP客户端
        if self.http_session:
            await self.http_session.close()
        
        # 关闭Redis连接
        if self.redis_client:
            await self.redis_client.close()
        
        # 关闭数据库连接池
        if self.db_pool:
            await self.db_pool.close()
        
        logger.info(f"智能体 {self.agent_name} 已关闭")

# 工具函数
def cpu_intensive_task(func: Callable) -> Callable:
    """CPU密集型任务装饰器"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.cpu_pool, func, self, *args, **kwargs)
    return wrapper

def io_intensive_task(func: Callable) -> Callable:
    """I/O密集型任务装饰器"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.io_pool, func, self, *args, **kwargs)
    return wrapper

def cached_result(ttl: int = 300):
    """缓存结果装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 生成缓存键
            cache_key = f"{self.agent_name}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            if hasattr(self, 'cache') and self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # 执行函数
            result = await func(self, *args, **kwargs)
            
            # 缓存结果
            if hasattr(self, 'cache') and self.cache:
                await self.cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator 