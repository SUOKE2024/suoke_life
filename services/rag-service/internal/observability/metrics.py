#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
监控指标收集模块
提供全面的性能监控、业务指标和系统健康状态监控
"""

import time
import psutil
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import structlog
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

logger = structlog.get_logger(__name__)

# Prometheus指标定义

# 请求相关指标
REQUEST_COUNT = Counter(
    'rag_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'rag_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0]
)

REQUEST_SIZE = Histogram(
    'rag_request_size_bytes',
    'Request size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
)

RESPONSE_SIZE = Histogram(
    'rag_response_size_bytes',
    'Response size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
)

# 查询相关指标
QUERY_COUNT = Counter(
    'rag_queries_total',
    'Total number of queries',
    ['query_type', 'collection', 'status']
)

QUERY_LATENCY = Histogram(
    'rag_query_latency_seconds',
    'Query latency in seconds',
    ['query_type', 'stage'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

RETRIEVAL_LATENCY = Histogram(
    'rag_retrieval_latency_seconds',
    'Document retrieval latency in seconds',
    ['retriever_type', 'collection'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

GENERATION_LATENCY = Histogram(
    'rag_generation_latency_seconds',
    'Text generation latency in seconds',
    ['model_name', 'model_type'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0]
)

EMBEDDING_LATENCY = Histogram(
    'rag_embedding_latency_seconds',
    'Text embedding latency in seconds',
    ['model_name'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# 文档相关指标
DOCUMENT_COUNT = Gauge(
    'rag_documents_total',
    'Total number of documents',
    ['collection', 'source']
)

DOCUMENT_OPERATIONS = Counter(
    'rag_document_operations_total',
    'Total number of document operations',
    ['operation', 'collection', 'status']
)

VECTOR_DB_OPERATIONS = Counter(
    'rag_vector_db_operations_total',
    'Total number of vector database operations',
    ['operation', 'collection', 'status']
)

VECTOR_DB_LATENCY = Histogram(
    'rag_vector_db_latency_seconds',
    'Vector database operation latency',
    ['operation', 'collection'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# 缓存相关指标
CACHE_OPERATIONS = Counter(
    'rag_cache_operations_total',
    'Total number of cache operations',
    ['operation', 'cache_type', 'status']
)

CACHE_HIT_RATE = Gauge(
    'rag_cache_hit_rate',
    'Cache hit rate',
    ['cache_type']
)

CACHE_SIZE = Gauge(
    'rag_cache_size_bytes',
    'Cache size in bytes',
    ['cache_type']
)

# 模型相关指标
MODEL_REQUESTS = Counter(
    'rag_model_requests_total',
    'Total number of model requests',
    ['model_name', 'model_type', 'status']
)

MODEL_TOKENS = Counter(
    'rag_model_tokens_total',
    'Total number of tokens processed',
    ['model_name', 'token_type']  # token_type: input, output
)

MODEL_ERRORS = Counter(
    'rag_model_errors_total',
    'Total number of model errors',
    ['model_name', 'error_type']
)

# 系统资源指标
SYSTEM_CPU_USAGE = Gauge(
    'rag_system_cpu_usage_percent',
    'System CPU usage percentage'
)

SYSTEM_MEMORY_USAGE = Gauge(
    'rag_system_memory_usage_bytes',
    'System memory usage in bytes'
)

SYSTEM_DISK_USAGE = Gauge(
    'rag_system_disk_usage_bytes',
    'System disk usage in bytes',
    ['mount_point']
)

ACTIVE_CONNECTIONS = Gauge(
    'rag_active_connections',
    'Number of active connections'
)

# 业务指标
USER_QUERIES = Counter(
    'rag_user_queries_total',
    'Total number of user queries',
    ['user_type', 'query_category']
)

QUERY_SATISFACTION = Histogram(
    'rag_query_satisfaction_score',
    'Query satisfaction score',
    ['query_category'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

TCM_ANALYSIS_COUNT = Counter(
    'rag_tcm_analysis_total',
    'Total number of TCM analysis requests',
    ['analysis_type', 'status']
)

@dataclass
class MetricSnapshot:
    """指标快照"""
    timestamp: datetime
    request_count: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    active_connections: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0

@dataclass
class QueryMetrics:
    """查询指标"""
    query_id: str
    query_type: str
    start_time: float
    retrieval_time: Optional[float] = None
    generation_time: Optional[float] = None
    total_time: Optional[float] = None
    retrieved_docs: int = 0
    generated_tokens: int = 0
    cache_hit: bool = False
    error: Optional[str] = None

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._snapshots: deque = deque(maxlen=1000)  # 保留最近1000个快照
        self._query_metrics: Dict[str, QueryMetrics] = {}
        self._cache_stats = defaultdict(lambda: {"hits": 0, "misses": 0})
        self._system_monitor_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
    
    async def start_monitoring(self):
        """开始监控"""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        self._system_monitor_task = asyncio.create_task(self._system_monitor_loop())
        logger.info("指标监控已启动")
    
    async def stop_monitoring(self):
        """停止监控"""
        self._is_monitoring = False
        if self._system_monitor_task:
            self._system_monitor_task.cancel()
            try:
                await self._system_monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("指标监控已停止")
    
    async def _system_monitor_loop(self):
        """系统监控循环"""
        while self._is_monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(10)  # 每10秒收集一次系统指标
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("系统指标收集失败", error=str(e))
                await asyncio.sleep(10)
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)
            
            # 内存使用
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory.used)
            
            # 磁盘使用
            for partition in psutil.disk_partitions():
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    SYSTEM_DISK_USAGE.labels(mount_point=partition.mountpoint).set(disk_usage.used)
                except (PermissionError, FileNotFoundError):
                    continue
            
            # 网络连接数
            connections = len(psutil.net_connections())
            ACTIVE_CONNECTIONS.set(connections)
            
        except Exception as e:
            logger.error("系统指标收集失败", error=str(e))
    
    def record_request(self, method: str, endpoint: str, status_code: int, 
                      duration: float, request_size: int = 0, response_size: int = 0):
        """记录请求指标"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
        if request_size > 0:
            REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(request_size)
        
        if response_size > 0:
            RESPONSE_SIZE.labels(method=method, endpoint=endpoint).observe(response_size)
    
    def start_query(self, query_id: str, query_type: str) -> QueryMetrics:
        """开始查询计时"""
        metrics = QueryMetrics(
            query_id=query_id,
            query_type=query_type,
            start_time=time.time()
        )
        self._query_metrics[query_id] = metrics
        return metrics
    
    def record_retrieval(self, query_id: str, retriever_type: str, collection: str,
                        latency: float, doc_count: int, success: bool = True):
        """记录检索指标"""
        if query_id in self._query_metrics:
            self._query_metrics[query_id].retrieval_time = latency
            self._query_metrics[query_id].retrieved_docs = doc_count
        
        RETRIEVAL_LATENCY.labels(retriever_type=retriever_type, collection=collection).observe(latency)
        
        status = "success" if success else "error"
        QUERY_COUNT.labels(query_type="retrieval", collection=collection, status=status).inc()
    
    def record_generation(self, query_id: str, model_name: str, model_type: str,
                         latency: float, token_count: int, success: bool = True):
        """记录生成指标"""
        if query_id in self._query_metrics:
            self._query_metrics[query_id].generation_time = latency
            self._query_metrics[query_id].generated_tokens = token_count
        
        GENERATION_LATENCY.labels(model_name=model_name, model_type=model_type).observe(latency)
        MODEL_TOKENS.labels(model_name=model_name, token_type="output").inc(token_count)
        
        status = "success" if success else "error"
        MODEL_REQUESTS.labels(model_name=model_name, model_type=model_type, status=status).inc()
    
    def record_embedding(self, model_name: str, latency: float, token_count: int):
        """记录嵌入指标"""
        EMBEDDING_LATENCY.labels(model_name=model_name).observe(latency)
        MODEL_TOKENS.labels(model_name=model_name, token_type="input").inc(token_count)
    
    def finish_query(self, query_id: str, success: bool = True, error: Optional[str] = None):
        """完成查询计时"""
        if query_id not in self._query_metrics:
            return
        
        metrics = self._query_metrics[query_id]
        metrics.total_time = time.time() - metrics.start_time
        metrics.error = error
        
        # 记录查询延迟
        stage = "total"
        QUERY_LATENCY.labels(query_type=metrics.query_type, stage=stage).observe(metrics.total_time)
        
        if metrics.retrieval_time:
            QUERY_LATENCY.labels(query_type=metrics.query_type, stage="retrieval").observe(metrics.retrieval_time)
        
        if metrics.generation_time:
            QUERY_LATENCY.labels(query_type=metrics.query_type, stage="generation").observe(metrics.generation_time)
        
        # 记录查询计数
        status = "success" if success else "error"
        QUERY_COUNT.labels(query_type=metrics.query_type, collection="all", status=status).inc()
        
        # 清理
        del self._query_metrics[query_id]
    
    def record_cache_operation(self, cache_type: str, operation: str, hit: bool):
        """记录缓存操作"""
        status = "hit" if hit else "miss"
        CACHE_OPERATIONS.labels(operation=operation, cache_type=cache_type, status=status).inc()
        
        # 更新缓存统计
        if hit:
            self._cache_stats[cache_type]["hits"] += 1
        else:
            self._cache_stats[cache_type]["misses"] += 1
        
        # 计算命中率
        stats = self._cache_stats[cache_type]
        total = stats["hits"] + stats["misses"]
        if total > 0:
            hit_rate = stats["hits"] / total
            CACHE_HIT_RATE.labels(cache_type=cache_type).set(hit_rate)
    
    def record_document_operation(self, operation: str, collection: str, success: bool = True):
        """记录文档操作"""
        status = "success" if success else "error"
        DOCUMENT_OPERATIONS.labels(operation=operation, collection=collection, status=status).inc()
    
    def record_vector_db_operation(self, operation: str, collection: str, 
                                  latency: float, success: bool = True):
        """记录向量数据库操作"""
        status = "success" if success else "error"
        VECTOR_DB_OPERATIONS.labels(operation=operation, collection=collection, status=status).inc()
        VECTOR_DB_LATENCY.labels(operation=operation, collection=collection).observe(latency)
    
    def update_document_count(self, collection: str, source: str, count: int):
        """更新文档数量"""
        DOCUMENT_COUNT.labels(collection=collection, source=source).set(count)
    
    def record_user_query(self, user_type: str, query_category: str):
        """记录用户查询"""
        USER_QUERIES.labels(user_type=user_type, query_category=query_category).inc()
    
    def record_query_satisfaction(self, query_category: str, score: float):
        """记录查询满意度"""
        QUERY_SATISFACTION.labels(query_category=query_category).observe(score)
    
    def record_tcm_analysis(self, analysis_type: str, success: bool = True):
        """记录中医分析"""
        status = "success" if success else "error"
        TCM_ANALYSIS_COUNT.labels(analysis_type=analysis_type, status=status).inc()
    
    def record_model_error(self, model_name: str, error_type: str):
        """记录模型错误"""
        MODEL_ERRORS.labels(model_name=model_name, error_type=error_type).inc()
    
    def get_current_snapshot(self) -> MetricSnapshot:
        """获取当前指标快照"""
        try:
            # 计算请求统计
            request_count = sum(REQUEST_COUNT._value.values())
            
            # 计算平均响应时间
            duration_sum = sum(REQUEST_DURATION._sum.values())
            duration_count = sum(REQUEST_DURATION._count.values())
            avg_response_time = duration_sum / duration_count if duration_count > 0 else 0.0
            
            # 计算错误率
            error_count = sum(
                count for labels, count in REQUEST_COUNT._value.items()
                if labels[2] >= '400'  # status_code >= 400
            )
            error_rate = error_count / request_count if request_count > 0 else 0.0
            
            # 计算缓存命中率
            total_hits = sum(stats["hits"] for stats in self._cache_stats.values())
            total_requests = sum(stats["hits"] + stats["misses"] for stats in self._cache_stats.values())
            cache_hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
            
            # 系统指标
            cpu_usage = SYSTEM_CPU_USAGE._value._value if hasattr(SYSTEM_CPU_USAGE._value, '_value') else 0.0
            memory_usage = SYSTEM_MEMORY_USAGE._value._value if hasattr(SYSTEM_MEMORY_USAGE._value, '_value') else 0.0
            active_connections = ACTIVE_CONNECTIONS._value._value if hasattr(ACTIVE_CONNECTIONS._value, '_value') else 0
            
            snapshot = MetricSnapshot(
                timestamp=datetime.utcnow(),
                request_count=int(request_count),
                avg_response_time=avg_response_time,
                error_rate=error_rate,
                cache_hit_rate=cache_hit_rate,
                active_connections=int(active_connections),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage
            )
            
            self._snapshots.append(snapshot)
            return snapshot
            
        except Exception as e:
            logger.error("获取指标快照失败", error=str(e))
            return MetricSnapshot(timestamp=datetime.utcnow())
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        snapshot = self.get_current_snapshot()
        
        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "requests": {
                "total": snapshot.request_count,
                "avg_response_time": round(snapshot.avg_response_time, 3),
                "error_rate": round(snapshot.error_rate, 3)
            },
            "cache": {
                "hit_rate": round(snapshot.cache_hit_rate, 3)
            },
            "system": {
                "cpu_usage": round(snapshot.cpu_usage, 2),
                "memory_usage_mb": round(snapshot.memory_usage / 1024 / 1024, 2),
                "active_connections": snapshot.active_connections
            },
            "queries": {
                "active": len(self._query_metrics)
            }
        }
    
    def export_prometheus_metrics(self) -> str:
        """导出Prometheus格式的指标"""
        return generate_latest(self.registry)

# 全局指标收集器实例
metrics_collector = MetricsCollector()

# 装饰器和上下文管理器

@asynccontextmanager
async def track_query(query_id: str, query_type: str):
    """查询跟踪上下文管理器"""
    metrics = metrics_collector.start_query(query_id, query_type)
    try:
        yield metrics
        metrics_collector.finish_query(query_id, success=True)
    except Exception as e:
        metrics_collector.finish_query(query_id, success=False, error=str(e))
        raise

def track_request(func: Callable) -> Callable:
    """请求跟踪装饰器"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        method = kwargs.get('method', 'UNKNOWN')
        endpoint = kwargs.get('endpoint', 'UNKNOWN')
        
        try:
            result = await func(*args, **kwargs)
            status_code = getattr(result, 'status_code', 200)
            duration = time.time() - start_time
            
            metrics_collector.record_request(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            metrics_collector.record_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration
            )
            raise
    
    return wrapper

def track_cache_operation(cache_type: str, operation: str):
    """缓存操作跟踪装饰器"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                # 假设返回None表示缓存未命中
                hit = result is not None
                metrics_collector.record_cache_operation(cache_type, operation, hit)
                return result
            except Exception as e:
                metrics_collector.record_cache_operation(cache_type, operation, False)
                raise
        return wrapper
    return decorator

# 健康检查

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.thresholds = {
            "cpu_usage": 90.0,  # CPU使用率阈值
            "memory_usage": 0.9,  # 内存使用率阈值
            "error_rate": 0.1,  # 错误率阈值
            "avg_response_time": 5.0  # 平均响应时间阈值（秒）
        }
    
    def check_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        snapshot = self.metrics_collector.get_current_snapshot()
        
        health_status = {
            "status": "healthy",
            "timestamp": snapshot.timestamp.isoformat(),
            "components": {},
            "overall_score": 1.0
        }
        
        score = 1.0
        
        # 检查CPU使用率
        if snapshot.cpu_usage > self.thresholds["cpu_usage"]:
            health_status["components"]["cpu"] = {
                "status": "unhealthy",
                "value": snapshot.cpu_usage,
                "threshold": self.thresholds["cpu_usage"]
            }
            score -= 0.2
        else:
            health_status["components"]["cpu"] = {"status": "healthy", "value": snapshot.cpu_usage}
        
        # 检查内存使用率
        memory_total = psutil.virtual_memory().total
        memory_usage_rate = snapshot.memory_usage / memory_total
        if memory_usage_rate > self.thresholds["memory_usage"]:
            health_status["components"]["memory"] = {
                "status": "unhealthy",
                "value": memory_usage_rate,
                "threshold": self.thresholds["memory_usage"]
            }
            score -= 0.2
        else:
            health_status["components"]["memory"] = {"status": "healthy", "value": memory_usage_rate}
        
        # 检查错误率
        if snapshot.error_rate > self.thresholds["error_rate"]:
            health_status["components"]["error_rate"] = {
                "status": "unhealthy",
                "value": snapshot.error_rate,
                "threshold": self.thresholds["error_rate"]
            }
            score -= 0.3
        else:
            health_status["components"]["error_rate"] = {"status": "healthy", "value": snapshot.error_rate}
        
        # 检查响应时间
        if snapshot.avg_response_time > self.thresholds["avg_response_time"]:
            health_status["components"]["response_time"] = {
                "status": "unhealthy",
                "value": snapshot.avg_response_time,
                "threshold": self.thresholds["avg_response_time"]
            }
            score -= 0.3
        else:
            health_status["components"]["response_time"] = {"status": "healthy", "value": snapshot.avg_response_time}
        
        health_status["overall_score"] = max(0.0, score)
        
        if score < 0.7:
            health_status["status"] = "unhealthy"
        elif score < 0.9:
            health_status["status"] = "degraded"
        
        return health_status

# 全局健康检查器
health_checker = HealthChecker(metrics_collector) 