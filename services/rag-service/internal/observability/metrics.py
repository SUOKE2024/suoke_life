#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指标收集器 - 提供详细的性能监控和业务指标
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import threading
from datetime import datetime, timedelta

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    CollectorRegistry, generate_latest,
    start_http_server
)
from loguru import logger


@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """性能统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化指标收集器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.registry = CollectorRegistry()
        
        # 基础指标
        self._init_basic_metrics()
        
        # RAG特定指标
        self._init_rag_metrics()
        
        # 中医特色指标
        self._init_tcm_metrics()
        
        # 性能统计
        self.performance_stats = PerformanceStats()
        self.response_times = deque(maxlen=1000)  # 保留最近1000次请求的响应时间
        
        # 缓存指标
        self.cache_stats = defaultdict(int)
        
        # 错误统计
        self.error_stats = defaultdict(int)
        
        # 用户行为指标
        self.user_behavior_stats = defaultdict(int)
        
        # 启动指标服务器
        self._start_metrics_server()
    
    def _init_basic_metrics(self) -> None:
        """初始化基础指标"""
        # 请求计数器
        self.request_counter = Counter(
            'rag_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        # 响应时间直方图
        self.response_time_histogram = Histogram(
            'rag_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # 活跃连接数
        self.active_connections = Gauge(
            'rag_active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        # 内存使用量
        self.memory_usage = Gauge(
            'rag_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        # CPU使用率
        self.cpu_usage = Gauge(
            'rag_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
    
    def _init_rag_metrics(self) -> None:
        """初始化RAG特定指标"""
        # 检索指标
        self.retrieval_counter = Counter(
            'rag_retrieval_requests_total',
            'Total number of retrieval requests',
            ['collection', 'status'],
            registry=self.registry
        )
        
        self.retrieval_latency = Histogram(
            'rag_retrieval_duration_seconds',
            'Retrieval duration in seconds',
            ['collection'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry
        )
        
        self.retrieval_results_count = Histogram(
            'rag_retrieval_results_count',
            'Number of retrieval results',
            ['collection'],
            buckets=[1, 5, 10, 20, 50, 100],
            registry=self.registry
        )
        
        # 生成指标
        self.generation_counter = Counter(
            'rag_generation_requests_total',
            'Total number of generation requests',
            ['model', 'status'],
            registry=self.registry
        )
        
        self.generation_latency = Histogram(
            'rag_generation_duration_seconds',
            'Generation duration in seconds',
            ['model'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        self.generation_tokens = Histogram(
            'rag_generation_tokens_count',
            'Number of generated tokens',
            ['model'],
            buckets=[50, 100, 500, 1000, 2000, 5000],
            registry=self.registry
        )
        
        # 缓存指标
        self.cache_operations = Counter(
            'rag_cache_operations_total',
            'Total number of cache operations',
            ['operation', 'result'],
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'rag_cache_hit_rate',
            'Cache hit rate',
            ['cache_type'],
            registry=self.registry
        )
        
        # 向量数据库指标
        self.vector_db_operations = Counter(
            'rag_vector_db_operations_total',
            'Total number of vector database operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.vector_db_latency = Histogram(
            'rag_vector_db_duration_seconds',
            'Vector database operation duration',
            ['operation'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0],
            registry=self.registry
        )
    
    def _init_tcm_metrics(self) -> None:
        """初始化中医特色指标"""
        # 辨证分析指标
        self.syndrome_analysis_counter = Counter(
            'tcm_syndrome_analysis_total',
            'Total number of syndrome analysis requests',
            ['primary_syndrome', 'confidence_level'],
            registry=self.registry
        )
        
        self.syndrome_analysis_latency = Histogram(
            'tcm_syndrome_analysis_duration_seconds',
            'Syndrome analysis duration in seconds',
            buckets=[0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry
        )
        
        # 体质分析指标
        self.constitution_analysis_counter = Counter(
            'tcm_constitution_analysis_total',
            'Total number of constitution analysis requests',
            ['constitution_type'],
            registry=self.registry
        )
        
        # 方剂推荐指标
        self.formula_recommendation_counter = Counter(
            'tcm_formula_recommendation_total',
            'Total number of formula recommendations',
            ['formula_category'],
            registry=self.registry
        )
        
        # 穴位推荐指标
        self.acupoint_recommendation_counter = Counter(
            'tcm_acupoint_recommendation_total',
            'Total number of acupoint recommendations',
            ['meridian'],
            registry=self.registry
        )
        
        # 中医知识图谱查询指标
        self.tcm_kg_query_counter = Counter(
            'tcm_knowledge_graph_queries_total',
            'Total number of TCM knowledge graph queries',
            ['query_type', 'status'],
            registry=self.registry
        )
        
        # 症状识别准确率
        self.symptom_recognition_accuracy = Gauge(
            'tcm_symptom_recognition_accuracy',
            'Symptom recognition accuracy',
            registry=self.registry
        )
        
        # 辨证准确率
        self.syndrome_diagnosis_accuracy = Gauge(
            'tcm_syndrome_diagnosis_accuracy',
            'Syndrome diagnosis accuracy',
            registry=self.registry
        )
    
    def _start_metrics_server(self) -> None:
        """启动指标服务器"""
        port = self.config.get('port', 9090)
        try:
            start_http_server(port, registry=self.registry)
            logger.info(f"Metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    @asynccontextmanager
    async def measure_time(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """
        测量执行时间的上下文管理器
        
        Args:
            metric_name: 指标名称
            labels: 标签
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_timing(metric_name, duration, labels or {})
    
    def record_timing(self, metric_name: str, duration: float, labels: Dict[str, str]) -> None:
        """记录时间指标"""
        if metric_name == 'retrieval':
            self.retrieval_latency.labels(**labels).observe(duration)
        elif metric_name == 'generation':
            self.generation_latency.labels(**labels).observe(duration)
        elif metric_name == 'syndrome_analysis':
            self.syndrome_analysis_latency.observe(duration)
        elif metric_name == 'vector_db':
            self.vector_db_latency.labels(**labels).observe(duration)
        else:
            self.response_time_histogram.labels(**labels).observe(duration)
        
        # 更新响应时间统计
        self.response_times.append(duration)
        self._update_performance_stats()
    
    def increment_counter(self, metric_name: str, labels: Dict[str, str], value: float = 1.0) -> None:
        """增加计数器指标"""
        if metric_name == 'request':
            self.request_counter.labels(**labels).inc(value)
        elif metric_name == 'retrieval':
            self.retrieval_counter.labels(**labels).inc(value)
        elif metric_name == 'generation':
            self.generation_counter.labels(**labels).inc(value)
        elif metric_name == 'syndrome_analysis':
            self.syndrome_analysis_counter.labels(**labels).inc(value)
        elif metric_name == 'constitution_analysis':
            self.constitution_analysis_counter.labels(**labels).inc(value)
        elif metric_name == 'formula_recommendation':
            self.formula_recommendation_counter.labels(**labels).inc(value)
        elif metric_name == 'acupoint_recommendation':
            self.acupoint_recommendation_counter.labels(**labels).inc(value)
        elif metric_name == 'tcm_kg_query':
            self.tcm_kg_query_counter.labels(**labels).inc(value)
        elif metric_name == 'cache':
            self.cache_operations.labels(**labels).inc(value)
        elif metric_name == 'vector_db':
            self.vector_db_operations.labels(**labels).inc(value)
    
    def set_gauge(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """设置仪表指标"""
        labels = labels or {}
        
        if metric_name == 'active_connections':
            self.active_connections.set(value)
        elif metric_name == 'memory_usage':
            self.memory_usage.set(value)
        elif metric_name == 'cpu_usage':
            self.cpu_usage.set(value)
        elif metric_name == 'cache_hit_rate':
            self.cache_hit_rate.labels(**labels).set(value)
        elif metric_name == 'symptom_recognition_accuracy':
            self.symptom_recognition_accuracy.set(value)
        elif metric_name == 'syndrome_diagnosis_accuracy':
            self.syndrome_diagnosis_accuracy.set(value)
    
    def record_histogram(self, metric_name: str, value: float, labels: Dict[str, str]) -> None:
        """记录直方图指标"""
        if metric_name == 'retrieval_results':
            self.retrieval_results_count.labels(**labels).observe(value)
        elif metric_name == 'generation_tokens':
            self.generation_tokens.labels(**labels).observe(value)
    
    def record_cache_operation(self, operation: str, result: str, cache_type: str = "default") -> None:
        """记录缓存操作"""
        self.increment_counter('cache', {'operation': operation, 'result': result})
        
        # 更新缓存统计
        self.cache_stats[f"{cache_type}_{result}"] += 1
        
        # 计算缓存命中率
        total_ops = self.cache_stats[f"{cache_type}_hit"] + self.cache_stats[f"{cache_type}_miss"]
        if total_ops > 0:
            hit_rate = self.cache_stats[f"{cache_type}_hit"] / total_ops
            self.set_gauge('cache_hit_rate', hit_rate, {'cache_type': cache_type})
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any]) -> None:
        """记录错误"""
        self.error_stats[error_type] += 1
        
        # 记录到日志
        logger.error(f"Error recorded: {error_type} - {error_message}", extra=context)
        
        # 更新错误率
        self._update_performance_stats()
    
    def record_user_behavior(self, action: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """记录用户行为"""
        self.user_behavior_stats[action] += 1
        
        # 记录详细的用户行为日志
        logger.info(f"User behavior: {action}", extra={
            'user_id': user_id,
            'action': action,
            'metadata': metadata or {}
        })
    
    def _update_performance_stats(self) -> None:
        """更新性能统计"""
        if not self.response_times:
            return
        
        # 计算响应时间统计
        sorted_times = sorted(self.response_times)
        self.performance_stats.avg_response_time = sum(sorted_times) / len(sorted_times)
        
        if len(sorted_times) >= 20:  # 至少20个样本才计算百分位数
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            self.performance_stats.p95_response_time = sorted_times[p95_index]
            self.performance_stats.p99_response_time = sorted_times[p99_index]
        
        # 计算错误率
        total_errors = sum(self.error_stats.values())
        total_requests = self.performance_stats.total_requests
        if total_requests > 0:
            self.performance_stats.error_rate = total_errors / total_requests
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        return {
            'performance_stats': {
                'total_requests': self.performance_stats.total_requests,
                'successful_requests': self.performance_stats.successful_requests,
                'failed_requests': self.performance_stats.failed_requests,
                'avg_response_time': self.performance_stats.avg_response_time,
                'p95_response_time': self.performance_stats.p95_response_time,
                'p99_response_time': self.performance_stats.p99_response_time,
                'cache_hit_rate': self.performance_stats.cache_hit_rate,
                'error_rate': self.performance_stats.error_rate
            },
            'cache_stats': dict(self.cache_stats),
            'error_stats': dict(self.error_stats),
            'user_behavior_stats': dict(self.user_behavior_stats)
        }
    
    def get_metrics_data(self) -> str:
        """获取Prometheus格式的指标数据"""
        return generate_latest(self.registry).decode('utf-8')
    
    async def collect_system_metrics(self) -> None:
        """收集系统指标"""
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.set_gauge('cpu_usage', cpu_percent)
            
            # 内存使用量
            memory = psutil.virtual_memory()
            self.set_gauge('memory_usage', memory.used)
            
            # 记录到日志
            logger.debug(f"System metrics - CPU: {cpu_percent}%, Memory: {memory.used / 1024 / 1024:.1f}MB")
            
        except ImportError:
            logger.warning("psutil not available, skipping system metrics collection")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def start_background_collection(self) -> None:
        """启动后台指标收集"""
        async def collect_loop():
            while True:
                try:
                    await self.collect_system_metrics()
                    await asyncio.sleep(30)  # 每30秒收集一次
                except Exception as e:
                    logger.error(f"Error in metrics collection loop: {e}")
                    await asyncio.sleep(60)  # 出错时等待更长时间
        
        # 在后台运行收集循环
        asyncio.create_task(collect_loop())
        logger.info("Background metrics collection started")
    
    def create_custom_metric(self, name: str, metric_type: str, description: str, labels: Optional[List[str]] = None) -> Any:
        """
        创建自定义指标
        
        Args:
            name: 指标名称
            metric_type: 指标类型 (counter, gauge, histogram, summary)
            description: 指标描述
            labels: 标签列表
            
        Returns:
            创建的指标对象
        """
        labels = labels or []
        
        if metric_type == 'counter':
            return Counter(name, description, labels, registry=self.registry)
        elif metric_type == 'gauge':
            return Gauge(name, description, labels, registry=self.registry)
        elif metric_type == 'histogram':
            return Histogram(name, description, labels, registry=self.registry)
        elif metric_type == 'summary':
            return Summary(name, description, labels, registry=self.registry)
        else:
            raise ValueError(f"Unsupported metric type: {metric_type}")
    
    def export_metrics_to_file(self, filepath: str) -> None:
        """导出指标到文件"""
        try:
            with open(filepath, 'w') as f:
                f.write(self.get_metrics_data())
            logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics to file: {e}")
    
    async def cleanup(self) -> None:
        """清理资源"""
        logger.info("Cleaning up metrics collector")
        # 这里可以添加清理逻辑，如关闭连接等 