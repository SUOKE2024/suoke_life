#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强监控系统
包括性能指标、业务指标、分布式追踪和智能告警
"""

import asyncio
import time
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from contextlib import asynccontextmanager

# 监控相关导入
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
import opentelemetry.trace as trace
from opentelemetry import baggage
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor

logger = logging.getLogger(__name__)

@dataclass
class MetricConfig:
    """监控配置"""
    # Prometheus配置
    prometheus_enabled: bool = True
    prometheus_port: int = 8090
    
    # OpenTelemetry配置
    otlp_enabled: bool = True
    otlp_endpoint: str = "http://localhost:4317"
    
    # 业务指标配置
    business_metrics_enabled: bool = True
    
    # 告警配置
    alerting_enabled: bool = True
    alert_thresholds: Dict[str, float] = None
    
    # 性能监控配置
    performance_monitoring: bool = True
    slow_query_threshold: float = 1.0  # 秒
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                'error_rate': 0.05,  # 5%
                'response_time_p95': 2.0,  # 2秒
                'memory_usage': 0.8,  # 80%
                'cpu_usage': 0.8,  # 80%
            }


@dataclass
class BusinessMetric:
    """业务指标"""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    description: str = ""


@dataclass
class PerformanceMetric:
    """性能指标"""
    operation: str
    duration: float
    success: bool
    error_type: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Alert:
    """告警"""
    id: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str  # critical, warning, info
    message: str
    timestamp: datetime
    resolved: bool = False


class PrometheusMetrics:
    """Prometheus指标收集器"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        
        # 请求指标
        self.request_count = Counter(
            'xiaoai_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'xiaoai_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # 业务指标
        self.diagnosis_count = Counter(
            'xiaoai_diagnosis_total',
            'Total number of diagnoses',
            ['diagnosis_type', 'success'],
            registry=self.registry
        )
        
        self.syndrome_analysis_duration = Histogram(
            'xiaoai_syndrome_analysis_duration_seconds',
            'Syndrome analysis duration in seconds',
            ['analysis_type'],
            registry=self.registry
        )
        
        self.multimodal_fusion_duration = Histogram(
            'xiaoai_multimodal_fusion_duration_seconds',
            'Multimodal fusion duration in seconds',
            ['modality_count'],
            registry=self.registry
        )
        
        # 系统指标
        self.memory_usage = Gauge(
            'xiaoai_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.cpu_usage = Gauge(
            'xiaoai_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        # 缓存指标
        self.cache_hits = Counter(
            'xiaoai_cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'xiaoai_cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # 模型指标
        self.model_inference_duration = Histogram(
            'xiaoai_model_inference_duration_seconds',
            'Model inference duration in seconds',
            ['model_name', 'modality'],
            registry=self.registry
        )
        
        self.model_accuracy = Gauge(
            'xiaoai_model_accuracy',
            'Model accuracy score',
            ['model_name', 'metric_type'],
            registry=self.registry
        )
        
        # 错误指标
        self.error_count = Counter(
            'xiaoai_errors_total',
            'Total number of errors',
            ['error_type', 'component'],
            registry=self.registry
        )


class DistributedTracing:
    """分布式追踪"""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.tracer_provider = None
        self.tracer = None
        
        if config.otlp_enabled:
            self._setup_tracing()
    
    def _setup_tracing(self):
        """设置分布式追踪"""
        try:
            # 创建TracerProvider
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            
            # 创建OTLP导出器
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config.otlp_endpoint,
                insecure=True
            )
            
            # 创建批量处理器
            span_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # 获取tracer
            self.tracer = trace.get_tracer(__name__)
            
            # 自动instrumentation
            AsyncioInstrumentor().instrument()
            
            logger.info("分布式追踪初始化成功")
            
        except Exception as e:
            logger.error(f"分布式追踪初始化失败: {e}")
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, **attributes):
        """追踪操作上下文管理器"""
        if not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(operation_name) as span:
            # 设置属性
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
            
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise


class AlertManager:
    """告警管理器"""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.alert_handlers = []
        self.lock = threading.Lock()
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def check_threshold(self, metric_name: str, current_value: float) -> Optional[Alert]:
        """检查阈值"""
        if not self.config.alerting_enabled:
            return None
        
        threshold = self.config.alert_thresholds.get(metric_name)
        if threshold is None:
            return None
        
        if current_value > threshold:
            alert_id = f"{metric_name}_{int(time.time())}"
            
            # 确定严重程度
            if current_value > threshold * 1.5:
                severity = "critical"
            elif current_value > threshold * 1.2:
                severity = "warning"
            else:
                severity = "info"
            
            alert = Alert(
                id=alert_id,
                metric_name=metric_name,
                current_value=current_value,
                threshold=threshold,
                severity=severity,
                message=f"{metric_name} 超过阈值: {current_value:.2f} > {threshold:.2f}",
                timestamp=datetime.now()
            )
            
            return alert
        
        return None
    
    def fire_alert(self, alert: Alert):
        """触发告警"""
        with self.lock:
            # 检查是否已存在相同告警
            existing_alert = self.active_alerts.get(alert.metric_name)
            if existing_alert and not existing_alert.resolved:
                return  # 避免重复告警
            
            self.active_alerts[alert.metric_name] = alert
            self.alert_history.append(alert)
        
        # 调用告警处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"告警处理器执行失败: {e}")
        
        logger.warning(f"告警触发: {alert.message}")
    
    def resolve_alert(self, metric_name: str):
        """解决告警"""
        with self.lock:
            alert = self.active_alerts.get(metric_name)
            if alert and not alert.resolved:
                alert.resolved = True
                logger.info(f"告警已解决: {metric_name}")
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        with self.lock:
            return [alert for alert in self.active_alerts.values() if not alert.resolved]


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.metrics_buffer = deque(maxlen=10000)
        self.slow_queries = deque(maxlen=100)
        self.lock = threading.Lock()
    
    def record_performance(self, metric: PerformanceMetric):
        """记录性能指标"""
        with self.lock:
            self.metrics_buffer.append(metric)
            
            # 记录慢查询
            if metric.duration > self.config.slow_query_threshold:
                self.slow_queries.append(metric)
    
    def get_performance_stats(self, operation: str = None, 
                            time_window: timedelta = timedelta(minutes=5)) -> Dict[str, Any]:
        """获取性能统计"""
        with self.lock:
            now = datetime.now()
            cutoff_time = now - time_window
            
            # 过滤指标
            filtered_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= cutoff_time and (operation is None or m.operation == operation)
            ]
            
            if not filtered_metrics:
                return {}
            
            # 计算统计信息
            durations = [m.duration for m in filtered_metrics]
            success_count = sum(1 for m in filtered_metrics if m.success)
            total_count = len(filtered_metrics)
            
            durations.sort()
            p50 = durations[int(len(durations) * 0.5)] if durations else 0
            p95 = durations[int(len(durations) * 0.95)] if durations else 0
            p99 = durations[int(len(durations) * 0.99)] if durations else 0
            
            return {
                'total_requests': total_count,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'p50_duration': p50,
                'p95_duration': p95,
                'p99_duration': p99,
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0
            }
    
    def get_slow_queries(self) -> List[PerformanceMetric]:
        """获取慢查询"""
        with self.lock:
            return list(self.slow_queries)


class EnhancedMonitoring:
    """增强监控系统"""
    
    def __init__(self, config: MetricConfig = None):
        self.config = config or MetricConfig()
        
        # 初始化组件
        self.prometheus_metrics = PrometheusMetrics()
        self.distributed_tracing = DistributedTracing(self.config)
        self.alert_manager = AlertManager(self.config)
        self.performance_monitor = PerformanceMonitor(self.config)
        
        # 业务指标缓冲区
        self.business_metrics = deque(maxlen=1000)
        self.business_metrics_lock = threading.Lock()
        
        # 监控任务
        self.monitoring_tasks = []
        self.running = False
        
        logger.info("增强监控系统初始化完成")
    
    async def start(self):
        """启动监控系统"""
        self.running = True
        
        # 启动监控任务
        if self.config.prometheus_enabled:
            self.monitoring_tasks.append(
                asyncio.create_task(self._prometheus_server())
            )
        
        if self.config.alerting_enabled:
            self.monitoring_tasks.append(
                asyncio.create_task(self._alert_checker())
            )
        
        self.monitoring_tasks.append(
            asyncio.create_task(self._system_metrics_collector())
        )
        
        logger.info("监控系统已启动")
    
    async def stop(self):
        """停止监控系统"""
        self.running = False
        
        # 取消监控任务
        for task in self.monitoring_tasks:
            task.cancel()
        
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        logger.info("监控系统已停止")
    
    async def _prometheus_server(self):
        """Prometheus指标服务器"""
        from aiohttp import web
        
        async def metrics_handler(request):
            metrics_data = generate_latest(self.prometheus_metrics.registry)
            return web.Response(text=metrics_data.decode('utf-8'), 
                              content_type='text/plain')
        
        app = web.Application()
        app.router.add_get('/metrics', metrics_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.config.prometheus_port)
        await site.start()
        
        logger.info(f"Prometheus指标服务器启动在端口 {self.config.prometheus_port}")
        
        try:
            while self.running:
                await asyncio.sleep(1)
        finally:
            await runner.cleanup()
    
    async def _alert_checker(self):
        """告警检查器"""
        while self.running:
            try:
                # 检查性能指标
                stats = self.performance_monitor.get_performance_stats()
                if stats:
                    # 检查错误率
                    error_rate = 1 - stats.get('success_rate', 1)
                    alert = self.alert_manager.check_threshold('error_rate', error_rate)
                    if alert:
                        self.alert_manager.fire_alert(alert)
                    
                    # 检查响应时间
                    p95_duration = stats.get('p95_duration', 0)
                    alert = self.alert_manager.check_threshold('response_time_p95', p95_duration)
                    if alert:
                        self.alert_manager.fire_alert(alert)
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"告警检查失败: {e}")
                await asyncio.sleep(60)
    
    async def _system_metrics_collector(self):
        """系统指标收集器"""
        import psutil
        
        while self.running:
            try:
                # 收集系统指标
                memory_usage = psutil.virtual_memory().used
                cpu_usage = psutil.cpu_percent() / 100.0
                
                # 更新Prometheus指标
                self.prometheus_metrics.memory_usage.set(memory_usage)
                self.prometheus_metrics.cpu_usage.set(cpu_usage)
                
                # 检查告警
                alert = self.alert_manager.check_threshold('memory_usage', 
                                                         psutil.virtual_memory().percent / 100.0)
                if alert:
                    self.alert_manager.fire_alert(alert)
                
                alert = self.alert_manager.check_threshold('cpu_usage', cpu_usage)
                if alert:
                    self.alert_manager.fire_alert(alert)
                
                await asyncio.sleep(10)  # 每10秒收集一次
                
            except Exception as e:
                logger.error(f"系统指标收集失败: {e}")
                await asyncio.sleep(30)
    
    # 业务指标记录方法
    def record_diagnosis(self, diagnosis_type: str, success: bool, duration: float):
        """记录诊断指标"""
        # Prometheus指标
        self.prometheus_metrics.diagnosis_count.labels(
            diagnosis_type=diagnosis_type,
            success=str(success)
        ).inc()
        
        # 性能指标
        metric = PerformanceMetric(
            operation=f"diagnosis_{diagnosis_type}",
            duration=duration,
            success=success
        )
        self.performance_monitor.record_performance(metric)
    
    def record_syndrome_analysis(self, analysis_type: str, duration: float):
        """记录辨证分析指标"""
        self.prometheus_metrics.syndrome_analysis_duration.labels(
            analysis_type=analysis_type
        ).observe(duration)
    
    def record_multimodal_fusion(self, modality_count: int, duration: float):
        """记录多模态融合指标"""
        self.prometheus_metrics.multimodal_fusion_duration.labels(
            modality_count=str(modality_count)
        ).observe(duration)
    
    def record_model_inference(self, model_name: str, modality: str, duration: float):
        """记录模型推理指标"""
        self.prometheus_metrics.model_inference_duration.labels(
            model_name=model_name,
            modality=modality
        ).observe(duration)
    
    def record_cache_hit(self, cache_type: str):
        """记录缓存命中"""
        self.prometheus_metrics.cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """记录缓存未命中"""
        self.prometheus_metrics.cache_misses.labels(cache_type=cache_type).inc()
    
    def record_error(self, error_type: str, component: str):
        """记录错误"""
        self.prometheus_metrics.error_count.labels(
            error_type=error_type,
            component=component
        ).inc()
    
    def record_business_metric(self, metric: BusinessMetric):
        """记录业务指标"""
        with self.business_metrics_lock:
            self.business_metrics.append(metric)
    
    # 上下文管理器
    @asynccontextmanager
    async def trace_diagnosis(self, diagnosis_type: str, **attributes):
        """诊断追踪上下文"""
        start_time = time.time()
        success = True
        error_type = None
        
        async with self.distributed_tracing.trace_operation(
            f"diagnosis_{diagnosis_type}", **attributes
        ) as span:
            try:
                yield span
            except Exception as e:
                success = False
                error_type = type(e).__name__
                self.record_error(error_type, "diagnosis")
                raise
            finally:
                duration = time.time() - start_time
                self.record_diagnosis(diagnosis_type, success, duration)
    
    @asynccontextmanager
    async def trace_model_inference(self, model_name: str, modality: str, **attributes):
        """模型推理追踪上下文"""
        start_time = time.time()
        
        async with self.distributed_tracing.trace_operation(
            f"model_inference_{model_name}", model_name=model_name, 
            modality=modality, **attributes
        ) as span:
            try:
                yield span
            finally:
                duration = time.time() - start_time
                self.record_model_inference(model_name, modality, duration)
    
    # 查询方法
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """获取监控统计"""
        return {
            'performance': self.performance_monitor.get_performance_stats(),
            'active_alerts': len(self.alert_manager.get_active_alerts()),
            'slow_queries': len(self.performance_monitor.get_slow_queries()),
            'business_metrics_count': len(self.business_metrics)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        active_alerts = self.alert_manager.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.severity == "critical"]
        
        return {
            'status': 'unhealthy' if critical_alerts else 'healthy',
            'active_alerts': len(active_alerts),
            'critical_alerts': len(critical_alerts),
            'monitoring_running': self.running
        }


# 全局监控实例
_monitoring = None

async def get_monitoring(config: Optional[MetricConfig] = None) -> EnhancedMonitoring:
    """获取监控实例"""
    global _monitoring
    
    if _monitoring is None:
        _monitoring = EnhancedMonitoring(config)
        await _monitoring.start()
    
    return _monitoring


# 监控装饰器
def monitor_performance(operation_name: str):
    """性能监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitoring = await get_monitoring()
            start_time = time.time()
            success = True
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                monitoring.record_error(type(e).__name__, operation_name)
                raise
            finally:
                duration = time.time() - start_time
                metric = PerformanceMetric(
                    operation=operation_name,
                    duration=duration,
                    success=success
                )
                monitoring.performance_monitor.record_performance(metric)
        
        return wrapper
    return decorator 