from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time
from typing import Optional
from loguru import logger

# 定义监控指标
class RAGMetrics:
    def __init__(self):
        # 请求计数器
        self.request_count = Counter(
            'rag_request_total',
            'Total number of RAG requests',
            ['endpoint', 'status']
        )
        
        # 请求延迟直方图
        self.request_latency = Histogram(
            'rag_request_latency_seconds',
            'Request latency in seconds',
            ['endpoint'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
        )
        
        # 向量检索延迟
        self.vector_search_latency = Histogram(
            'rag_vector_search_latency_seconds',
            'Vector search latency in seconds',
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, float('inf'))
        )
        
        # 缓存命中率
        self.cache_hits = Counter(
            'rag_cache_hits_total',
            'Total number of cache hits',
            ['cache_type']
        )
        self.cache_misses = Counter(
            'rag_cache_misses_total',
            'Total number of cache misses',
            ['cache_type']
        )
        
        # 错误计数器
        self.error_count = Counter(
            'rag_error_total',
            'Total number of errors',
            ['error_type']
        )
        
        # 当前活跃请求数
        self.active_requests = Gauge(
            'rag_active_requests',
            'Number of active requests'
        )
        
        # 向量存储健康状态
        self.vector_store_health = Gauge(
            'rag_vector_store_health',
            'Vector store health status (1 for healthy, 0 for unhealthy)'
        )
        
        # LLM API延迟
        self.llm_api_latency = Histogram(
            'rag_llm_api_latency_seconds',
            'LLM API latency in seconds',
            ['provider'],
            buckets=(0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
        )
        
        # 知识库大小
        self.knowledge_base_size = Gauge(
            'rag_knowledge_base_size',
            'Total number of documents in knowledge base'
        )

# 创建全局指标实例
metrics = RAGMetrics()

def track_request_metrics(endpoint: str):
    """请求指标跟踪装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.time()
            metrics.active_requests.inc()
            
            try:
                result = f(*args, **kwargs)
                metrics.request_count.labels(endpoint=endpoint, status='success').inc()
                return result
            except Exception as e:
                metrics.request_count.labels(endpoint=endpoint, status='error').inc()
                metrics.error_count.labels(error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                metrics.request_latency.labels(endpoint=endpoint).observe(duration)
                metrics.active_requests.dec()
        return wrapped
    return decorator

def track_vector_search(f):
    """向量检索指标跟踪装饰器"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            metrics.vector_search_latency.observe(duration)
            return result
        except Exception as e:
            metrics.error_count.labels(error_type='vector_search_error').inc()
            raise
    return wrapped

def track_llm_api(provider: str):
    """LLM API指标跟踪装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                metrics.llm_api_latency.labels(provider=provider).observe(duration)
                return result
            except Exception as e:
                metrics.error_count.labels(error_type=f'llm_api_error_{provider}').inc()
                raise
        return wrapped
    return decorator

def track_cache_metrics(cache_type: str):
    """缓存指标跟踪装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            result = f(*args, **kwargs)
            if result is not None:
                metrics.cache_hits.labels(cache_type=cache_type).inc()
            else:
                metrics.cache_misses.labels(cache_type=cache_type).inc()
            return result
        return wrapped
    return decorator

def update_vector_store_health(is_healthy: bool):
    """更新向量存储健康状态"""
    metrics.vector_store_health.set(1 if is_healthy else 0)

def update_knowledge_base_size(size: int):
    """更新知识库大小"""
    metrics.knowledge_base_size.set(size)

# 告警阈值配置
class AlertThresholds:
    ERROR_RATE_THRESHOLD = 0.1  # 错误率阈值
    LATENCY_THRESHOLD = 5.0     # 延迟阈值（秒）
    CACHE_HIT_RATE_THRESHOLD = 0.7  # 缓存命中率阈值

def check_alerts():
    """检查是否需要触发告警"""
    # 计算错误率
    total_requests = sum(metrics.request_count._value.values())
    total_errors = sum(metrics.error_count._value.values())
    if total_requests > 0:
        error_rate = total_errors / total_requests
        if error_rate > AlertThresholds.ERROR_RATE_THRESHOLD:
            logger.warning(f"High error rate detected: {error_rate:.2%}")
    
    # 检查平均延迟
    for endpoint, latencies in metrics.request_latency._sum.items():
        count = metrics.request_latency._count[endpoint]
        if count > 0:
            avg_latency = latencies / count
            if avg_latency > AlertThresholds.LATENCY_THRESHOLD:
                logger.warning(f"High latency detected for {endpoint}: {avg_latency:.2f}s")
    
    # 检查缓存命中率
    for cache_type in ['memory', 'redis']:
        hits = metrics.cache_hits.labels(cache_type=cache_type)._value
        misses = metrics.cache_misses.labels(cache_type=cache_type)._value
        total = hits + misses
        if total > 0:
            hit_rate = hits / total
            if hit_rate < AlertThresholds.CACHE_HIT_RATE_THRESHOLD:
                logger.warning(f"Low cache hit rate for {cache_type}: {hit_rate:.2%}") 