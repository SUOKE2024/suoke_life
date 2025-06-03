#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的消息总线监控系统
专门针对消息总线的指标收集、性能监控和业务指标
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Union
from collections import defaultdict, deque
import threading

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available, metrics will be limited")

try:
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.warning("OpenTelemetry not available, distributed tracing will be disabled")

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricConfig:
    """指标配置"""
    # 基础配置
    collection_interval: float = 10.0
    retention_period: int = 86400  # 24小时
    max_metrics_in_memory: int = 10000
    
    # Prometheus配置
    prometheus_enabled: bool = True
    prometheus_port: int = 8090
    prometheus_path: str = "/metrics"
    
    # OpenTelemetry配置
    opentelemetry_enabled: bool = True
    jaeger_endpoint: Optional[str] = None
    
    # 告警配置
    alerting_enabled: bool = True
    alert_thresholds: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # 自定义指标
    custom_metrics: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class MetricPoint:
    """指标数据点"""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp,
            'labels': self.labels,
            'type': self.metric_type.value
        }

@dataclass
class Alert:
    """告警信息"""
    id: str
    name: str
    level: AlertLevel
    message: str
    timestamp: float
    metric_name: str
    metric_value: float
    threshold: float
    labels: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level.value,
            'message': self.message,
            'timestamp': self.timestamp,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'labels': self.labels,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at
        }

class MetricCollector:
    """指标收集器"""
    
    def __init__(self, name: str):
        self.name = name
        self.metrics: deque = deque(maxlen=1000)
        self._lock = threading.Lock()
    
    def record(self, value: float, labels: Dict[str, str] = None, timestamp: float = None):
        """记录指标值"""
        labels = labels or {}
        timestamp = timestamp or time.time()
        
        metric_point = MetricPoint(
            name=self.name,
            value=value,
            timestamp=timestamp,
            labels=labels
        )
        
        with self._lock:
            self.metrics.append(metric_point)
    
    def get_latest(self, count: int = 1) -> List[MetricPoint]:
        """获取最新的指标"""
        with self._lock:
            return list(self.metrics)[-count:]
    
    def get_average(self, duration_seconds: int = 60) -> float:
        """获取指定时间内的平均值"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        with self._lock:
            values = [
                m.value for m in self.metrics 
                if m.timestamp >= cutoff_time
            ]
        
        return sum(values) / len(values) if values else 0.0
    
    def get_percentile(self, percentile: float, duration_seconds: int = 60) -> float:
        """获取指定时间内的百分位数"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        with self._lock:
            values = [
                m.value for m in self.metrics 
                if m.timestamp >= cutoff_time
            ]
        
        if not values:
            return 0.0
        
        values.sort()
        index = int(len(values) * percentile / 100)
        return values[min(index, len(values) - 1)]

class MessageBusMetrics:
    """消息总线专用指标"""
    
    def __init__(self):
        # 消息指标
        self.messages_published = MetricCollector("messages_published_total")
        self.messages_consumed = MetricCollector("messages_consumed_total")
        self.messages_failed = MetricCollector("messages_failed_total")
        self.message_size = MetricCollector("message_size_bytes")
        self.message_processing_time = MetricCollector("message_processing_duration_seconds")
        
        # 主题指标
        self.topic_partition_count = MetricCollector("topic_partition_count")
        self.topic_message_count = MetricCollector("topic_message_count")
        self.topic_size_bytes = MetricCollector("topic_size_bytes")
        
        # 生产者指标
        self.producer_throughput = MetricCollector("producer_throughput_messages_per_second")
        self.producer_latency = MetricCollector("producer_latency_seconds")
        self.producer_errors = MetricCollector("producer_errors_total")
        
        # 消费者指标
        self.consumer_lag = MetricCollector("consumer_lag_messages")
        self.consumer_throughput = MetricCollector("consumer_throughput_messages_per_second")
        self.consumer_errors = MetricCollector("consumer_errors_total")
        
        # 路由指标
        self.routing_decisions = MetricCollector("routing_decisions_total")
        self.routing_latency = MetricCollector("routing_latency_seconds")
        self.routing_errors = MetricCollector("routing_errors_total")
        
        # 存储指标
        self.storage_operations = MetricCollector("storage_operations_total")
        self.storage_latency = MetricCollector("storage_latency_seconds")
        self.storage_errors = MetricCollector("storage_errors_total")
        
        # 系统指标
        self.cpu_usage = MetricCollector("cpu_usage_percent")
        self.memory_usage = MetricCollector("memory_usage_bytes")
        self.disk_usage = MetricCollector("disk_usage_percent")
        self.network_io = MetricCollector("network_io_bytes")
        
        # 业务指标
        self.active_connections = MetricCollector("active_connections")
        self.queue_depth = MetricCollector("queue_depth")
        self.circuit_breaker_state = MetricCollector("circuit_breaker_state")

class PrometheusExporter:
    """Prometheus指标导出器"""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        
        if PROMETHEUS_AVAILABLE:
            self._init_prometheus_metrics()
    
    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        # 消息指标
        self.metrics['messages_published'] = Counter(
            'messagebus_messages_published_total',
            'Total number of published messages',
            ['topic', 'status'],
            registry=self.registry
        )
        
        self.metrics['message_processing_time'] = Histogram(
            'messagebus_message_processing_duration_seconds',
            'Message processing duration',
            ['topic', 'operation'],
            registry=self.registry
        )
        
        self.metrics['message_size'] = Histogram(
            'messagebus_message_size_bytes',
            'Message size in bytes',
            ['topic'],
            registry=self.registry
        )
        
        # 主题指标
        self.metrics['topic_partitions'] = Gauge(
            'messagebus_topic_partitions',
            'Number of partitions per topic',
            ['topic'],
            registry=self.registry
        )
        
        self.metrics['topic_messages'] = Gauge(
            'messagebus_topic_messages',
            'Number of messages in topic',
            ['topic'],
            registry=self.registry
        )
        
        # 系统指标
        self.metrics['active_connections'] = Gauge(
            'messagebus_active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        self.metrics['queue_depth'] = Gauge(
            'messagebus_queue_depth',
            'Current queue depth',
            ['queue_type'],
            registry=self.registry
        )
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """记录指标"""
        if not PROMETHEUS_AVAILABLE:
            return
        
        labels = labels or {}
        metric = self.metrics.get(name)
        
        if metric is None:
            return
        
        try:
            if hasattr(metric, 'labels'):
                metric.labels(**labels).observe(value) if hasattr(metric, 'observe') else metric.labels(**labels).inc(value)
            else:
                metric.set(value) if hasattr(metric, 'set') else metric.inc(value)
        except Exception as e:
            logger.error(f"记录Prometheus指标失败: {e}")
    
    def get_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        if not PROMETHEUS_AVAILABLE:
            return ""
        
        return generate_latest(self.registry).decode('utf-8')

class AlertManager:
    """告警管理器"""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self._lock = threading.Lock()
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def check_threshold(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """检查阈值并生成告警"""
        if not self.config.alerting_enabled:
            return
        
        thresholds = self.config.alert_thresholds.get(metric_name, {})
        if not thresholds:
            return
        
        labels = labels or {}
        alert_key = f"{metric_name}:{':'.join(f'{k}={v}' for k, v in sorted(labels.items()))}"
        
        # 检查各级别阈值
        for level_name, threshold in thresholds.items():
            try:
                level = AlertLevel(level_name)
                
                if value >= threshold:
                    # 触发告警
                    if alert_key not in self.active_alerts:
                        alert = Alert(
                            id=f"{alert_key}:{int(time.time())}",
                            name=f"{metric_name}_threshold_exceeded",
                            level=level,
                            message=f"{metric_name} value {value} exceeds threshold {threshold}",
                            timestamp=time.time(),
                            metric_name=metric_name,
                            metric_value=value,
                            threshold=threshold,
                            labels=labels
                        )
                        
                        self._trigger_alert(alert)
                else:
                    # 解决告警
                    if alert_key in self.active_alerts:
                        self._resolve_alert(alert_key)
            
            except ValueError:
                logger.warning(f"无效的告警级别: {level_name}")
    
    def _trigger_alert(self, alert: Alert):
        """触发告警"""
        with self._lock:
            self.active_alerts[alert.id] = alert
            self.alert_history.append(alert)
        
        logger.warning(f"告警触发: {alert.message}")
        
        # 调用告警处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"告警处理器执行失败: {e}")
    
    def _resolve_alert(self, alert_key: str):
        """解决告警"""
        with self._lock:
            alert = self.active_alerts.pop(alert_key, None)
            if alert:
                alert.resolved = True
                alert.resolved_at = time.time()
                self.alert_history.append(alert)
        
        if alert:
            logger.info(f"告警解决: {alert.message}")
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """获取告警历史"""
        with self._lock:
            return list(self.alert_history)[-limit:]

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.performance_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.Lock()
    
    def record_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None):
        """记录性能数据"""
        metadata = metadata or {}
        
        perf_data = {
            'operation': operation,
            'duration': duration,
            'timestamp': time.time(),
            'metadata': metadata
        }
        
        with self._lock:
            self.performance_data[operation].append(perf_data)
    
    def get_performance_stats(self, operation: str, duration_seconds: int = 300) -> Dict[str, float]:
        """获取性能统计"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds
        
        with self._lock:
            durations = [
                data['duration'] for data in self.performance_data[operation]
                if data['timestamp'] >= cutoff_time
            ]
        
        if not durations:
            return {}
        
        durations.sort()
        count = len(durations)
        
        return {
            'count': count,
            'min': min(durations),
            'max': max(durations),
            'avg': sum(durations) / count,
            'p50': durations[int(count * 0.5)],
            'p90': durations[int(count * 0.9)],
            'p95': durations[int(count * 0.95)],
            'p99': durations[int(count * 0.99)]
        }
    
    def get_slow_operations(self, threshold_seconds: float = 1.0, limit: int = 10) -> List[Dict[str, Any]]:
        """获取慢操作"""
        slow_ops = []
        
        with self._lock:
            for operation, data_list in self.performance_data.items():
                for data in data_list:
                    if data['duration'] >= threshold_seconds:
                        slow_ops.append(data)
        
        # 按持续时间排序
        slow_ops.sort(key=lambda x: x['duration'], reverse=True)
        return slow_ops[:limit]

class EnhancedMetricsCollector:
    """
    增强的消息总线监控系统
    专门针对消息总线的指标收集、性能监控和业务指标
    """
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.message_bus_metrics = MessageBusMetrics()
        self.prometheus_exporter = PrometheusExporter(config)
        self.alert_manager = AlertManager(config)
        self.performance_analyzer = PerformanceAnalyzer()
        
        # 自定义指标收集器
        self.custom_collectors: Dict[str, MetricCollector] = {}
        
        # 运行状态
        self._running = False
        self._collection_task: Optional[asyncio.Task] = None
        self._alert_task: Optional[asyncio.Task] = None
        
        # 初始化自定义指标
        self._init_custom_metrics()
        
        # 设置默认告警阈值
        self._setup_default_thresholds()
    
    def _init_custom_metrics(self):
        """初始化自定义指标"""
        for metric_config in self.config.custom_metrics:
            name = metric_config.get('name')
            if name:
                self.custom_collectors[name] = MetricCollector(name)
    
    def _setup_default_thresholds(self):
        """设置默认告警阈值"""
        default_thresholds = {
            'message_processing_duration_seconds': {
                'warning': 1.0,
                'error': 5.0,
                'critical': 10.0
            },
            'producer_errors_total': {
                'warning': 10,
                'error': 50,
                'critical': 100
            },
            'consumer_lag_messages': {
                'warning': 1000,
                'error': 5000,
                'critical': 10000
            },
            'cpu_usage_percent': {
                'warning': 70,
                'error': 85,
                'critical': 95
            },
            'memory_usage_bytes': {
                'warning': 0.8 * 1024 * 1024 * 1024,  # 800MB
                'error': 0.9 * 1024 * 1024 * 1024,    # 900MB
                'critical': 1024 * 1024 * 1024        # 1GB
            }
        }
        
        # 合并用户配置的阈值
        for metric_name, thresholds in default_thresholds.items():
            if metric_name not in self.config.alert_thresholds:
                self.config.alert_thresholds[metric_name] = thresholds
            else:
                # 合并阈值
                self.config.alert_thresholds[metric_name].update(thresholds)
    
    async def start(self):
        """启动监控系统"""
        if self._running:
            return
        
        self._running = True
        
        # 启动指标收集任务
        self._collection_task = asyncio.create_task(self._collection_loop())
        
        # 启动告警检查任务
        self._alert_task = asyncio.create_task(self._alert_loop())
        
        logger.info("增强监控系统已启动")
    
    async def stop(self):
        """停止监控系统"""
        if not self._running:
            return
        
        self._running = False
        
        # 停止后台任务
        for task in [self._collection_task, self._alert_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("增强监控系统已停止")
    
    async def _collection_loop(self):
        """指标收集循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.collection_interval)
                await self._collect_system_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"指标收集出错: {e}")
    
    async def _alert_loop(self):
        """告警检查循环"""
        while self._running:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次告警
                await self._check_alerts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"告警检查出错: {e}")
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent()
            self.record_metric('cpu_usage_percent', cpu_percent)
            
            # 内存使用
            memory = psutil.virtual_memory()
            self.record_metric('memory_usage_bytes', memory.used)
            self.record_metric('memory_usage_percent', memory.percent)
            
            # 磁盘使用
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric('disk_usage_percent', disk_percent)
            
            # 网络IO
            network = psutil.net_io_counters()
            self.record_metric('network_io_bytes', network.bytes_sent + network.bytes_recv)
            
        except ImportError:
            logger.warning("psutil not available, system metrics collection disabled")
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
    
    async def _check_alerts(self):
        """检查告警条件"""
        try:
            # 检查所有指标的最新值
            all_collectors = {
                **{name: getattr(self.message_bus_metrics, name) for name in dir(self.message_bus_metrics) if isinstance(getattr(self.message_bus_metrics, name), MetricCollector)},
                **self.custom_collectors
            }
            
            for name, collector in all_collectors.items():
                latest_metrics = collector.get_latest(1)
                if latest_metrics:
                    metric = latest_metrics[0]
                    self.alert_manager.check_threshold(
                        metric.name, 
                        metric.value, 
                        metric.labels
                    )
        
        except Exception as e:
            logger.error(f"检查告警失败: {e}")
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None, timestamp: float = None):
        """记录指标"""
        labels = labels or {}
        timestamp = timestamp or time.time()
        
        # 记录到内部收集器
        if hasattr(self.message_bus_metrics, name):
            collector = getattr(self.message_bus_metrics, name)
            collector.record(value, labels, timestamp)
        elif name in self.custom_collectors:
            self.custom_collectors[name].record(value, labels, timestamp)
        
        # 导出到Prometheus
        self.prometheus_exporter.record_metric(name, value, labels)
    
    def record_message_published(self, topic: str, size: int, success: bool = True):
        """记录消息发布"""
        labels = {'topic': topic, 'status': 'success' if success else 'failed'}
        self.record_metric('messages_published_total', 1, labels)
        self.record_metric('message_size_bytes', size, {'topic': topic})
    
    def record_message_consumed(self, topic: str, processing_time: float, success: bool = True):
        """记录消息消费"""
        labels = {'topic': topic, 'status': 'success' if success else 'failed'}
        self.record_metric('messages_consumed_total', 1, labels)
        self.record_metric('message_processing_duration_seconds', processing_time, {'topic': topic})
    
    def record_routing_decision(self, strategy: str, latency: float, success: bool = True):
        """记录路由决策"""
        labels = {'strategy': strategy, 'status': 'success' if success else 'failed'}
        self.record_metric('routing_decisions_total', 1, labels)
        self.record_metric('routing_latency_seconds', latency, {'strategy': strategy})
    
    def record_storage_operation(self, operation: str, latency: float, success: bool = True):
        """记录存储操作"""
        labels = {'operation': operation, 'status': 'success' if success else 'failed'}
        self.record_metric('storage_operations_total', 1, labels)
        self.record_metric('storage_latency_seconds', latency, {'operation': operation})
    
    def record_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None):
        """记录性能数据"""
        self.performance_analyzer.record_performance(operation, duration, metadata)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        return {
            'message_metrics': {
                'published_total': self.message_bus_metrics.messages_published.get_latest(1)[0].value if self.message_bus_metrics.messages_published.get_latest(1) else 0,
                'consumed_total': self.message_bus_metrics.messages_consumed.get_latest(1)[0].value if self.message_bus_metrics.messages_consumed.get_latest(1) else 0,
                'failed_total': self.message_bus_metrics.messages_failed.get_latest(1)[0].value if self.message_bus_metrics.messages_failed.get_latest(1) else 0,
                'avg_processing_time': self.message_bus_metrics.message_processing_time.get_average(300),
                'avg_message_size': self.message_bus_metrics.message_size.get_average(300)
            },
            'system_metrics': {
                'cpu_usage': self.message_bus_metrics.cpu_usage.get_average(60),
                'memory_usage': self.message_bus_metrics.memory_usage.get_latest(1)[0].value if self.message_bus_metrics.memory_usage.get_latest(1) else 0,
                'active_connections': self.message_bus_metrics.active_connections.get_latest(1)[0].value if self.message_bus_metrics.active_connections.get_latest(1) else 0
            },
            'performance_stats': {
                operation: self.performance_analyzer.get_performance_stats(operation)
                for operation in ['message_publish', 'message_consume', 'routing', 'storage']
            },
            'alerts': {
                'active_count': len(self.alert_manager.get_active_alerts()),
                'total_count': len(self.alert_manager.get_alert_history())
            }
        }
    
    def get_prometheus_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        return self.prometheus_exporter.get_metrics()
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        return [alert.to_dict() for alert in self.alert_manager.get_active_alerts()]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            'slow_operations': self.performance_analyzer.get_slow_operations(),
            'operation_stats': {
                operation: self.performance_analyzer.get_performance_stats(operation)
                for operation in ['message_publish', 'message_consume', 'routing', 'storage']
            }
        }
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """添加告警处理器"""
        self.alert_manager.add_alert_handler(handler)
    
    def create_custom_metric(self, name: str) -> MetricCollector:
        """创建自定义指标"""
        if name not in self.custom_collectors:
            self.custom_collectors[name] = MetricCollector(name)
        return self.custom_collectors[name]

# 监控系统工厂
class MetricsFactory:
    """监控系统工厂"""
    
    @staticmethod
    def create_enhanced_metrics_collector(
        config: Optional[MetricConfig] = None
    ) -> EnhancedMetricsCollector:
        """创建增强监控系统"""
        if config is None:
            config = MetricConfig()
        
        return EnhancedMetricsCollector(config) 