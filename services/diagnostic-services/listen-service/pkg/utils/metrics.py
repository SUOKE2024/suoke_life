"""
metrics - 索克生活项目模块
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from prometheus_client import Counter, Histogram, Gauge, Summary, REGISTRY, push_to_gateway, Info, CollectorRegistry, generate_latest, start_http_server
from typing import Dict, List, Any, Optional, Callable, Union
import functools
import logging
import threading
import time

"""
优化的指标监控工具模块
支持Prometheus指标、性能监控、中医特色指标收集
"""

logger = logging.getLogger(__name__)

# 默认的量化单位
DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)

# 全局配置
_config = {
    "namespace": "suoke",
    "subsystem": "listen_service",
    "push_gateway": None,
    "push_interval": 10,  # 秒
    "enabled": True
}

# 指标注册表
_metrics = {}

# 推送线程
_push_thread = None
_push_thread_stop_event = threading.Event()

@dataclass
class AudioProcessingMetrics:
    """音频处理指标数据类"""
    total_processed: int = 0
    total_duration: float = 0.0
    total_processing_time: float = 0.0
    error_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

@dataclass
class TCMDiagnosisMetrics:
    """中医诊断指标数据类"""
    total_diagnoses: int = 0
    constitution_analyses: Dict[str, int] = None
    emotion_analyses: Dict[str, int] = None
    organ_analyses: Dict[str, int] = None
    
    def __post_init__(self):
        if self.constitution_analyses is None:
            self.constitution_analyses = defaultdict(int)
        if self.emotion_analyses is None:
            self.emotion_analyses = defaultdict(int)
        if self.organ_analyses is None:
            self.organ_analyses = defaultdict(int)

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, service_name: str = "listen_service"):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        
        # 基础服务指标
        self.request_count = Counter(
            'listen_service_requests_total',
            'Total number of requests',
            ['method', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'listen_service_request_duration_seconds',
            'Request duration in seconds',
            ['method'],
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'listen_service_active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        # 音频处理指标
        self.audio_processed_total = Counter(
            'listen_service_audio_processed_total',
            'Total number of audio files processed',
            ['format', 'status'],
            registry=self.registry
        )
        
        self.audio_processing_duration = Histogram(
            'listen_service_audio_processing_duration_seconds',
            'Audio processing duration in seconds',
            ['operation'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        self.audio_file_size = Histogram(
            'listen_service_audio_file_size_bytes',
            'Audio file size in bytes',
            buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600],
            registry=self.registry
        )
        
        self.audio_duration = Histogram(
            'listen_service_audio_duration_seconds',
            'Audio duration in seconds',
            buckets=[1, 5, 10, 30, 60, 120, 300, 600],
            registry=self.registry
        )
        
        # 特征提取指标
        self.feature_extraction_duration = Histogram(
            'listen_service_feature_extraction_duration_seconds',
            'Feature extraction duration in seconds',
            ['feature_type'],
            registry=self.registry
        )
        
        self.features_extracted_total = Counter(
            'listen_service_features_extracted_total',
            'Total number of features extracted',
            ['feature_type'],
            registry=self.registry
        )
        
        # 中医诊断指标
        self.tcm_diagnoses_total = Counter(
            'listen_service_tcm_diagnoses_total',
            'Total number of TCM diagnoses',
            ['diagnosis_type'],
            registry=self.registry
        )
        
        self.tcm_constitution_analysis = Counter(
            'listen_service_tcm_constitution_analysis_total',
            'TCM constitution analysis count',
            ['constitution_type'],
            registry=self.registry
        )
        
        self.tcm_emotion_analysis = Counter(
            'listen_service_tcm_emotion_analysis_total',
            'TCM emotion analysis count',
            ['emotion_type'],
            registry=self.registry
        )
        
        self.tcm_organ_analysis = Counter(
            'listen_service_tcm_organ_analysis_total',
            'TCM organ analysis count',
            ['organ_type'],
            registry=self.registry
        )
        
        # 缓存指标
        self.cache_operations = Counter(
            'listen_service_cache_operations_total',
            'Cache operations count',
            ['operation', 'result'],
            registry=self.registry
        )
        
        # 资源使用指标
        self.memory_usage = Gauge(
            'listen_service_memory_usage_bytes',
            'Memory usage in bytes',
            ['process'],
            registry=self.registry
        )
        
        self.cpu_usage = Gauge(
            'listen_service_cpu_usage_percent',
            'CPU usage percentage',
            ['process'],
            registry=self.registry
        )
        
        self.gpu_memory_usage = Gauge(
            'listen_service_gpu_memory_usage_bytes',
            'GPU memory usage in bytes',
            ['device'],
            registry=self.registry
        )
        
        # 健康状态指标
        self.health_status = Gauge(
            'listen_service_health_status',
            'Service health status (1=healthy, 0=unhealthy)',
            ['component'],
            registry=self.registry
        )
        
        # 服务信息
        self.service_info = Info(
            'listen_service_info',
            'Service information',
            registry=self.registry
        )
        
        # 内部统计
        self.audio_metrics = AudioProcessingMetrics()
        self.tcm_metrics = TCMDiagnosisMetrics()
        
        # 性能历史记录（用于计算趋势）
        self.processing_times = deque(maxlen=1000)
        self.memory_history = deque(maxlen=100)
        
        # 线程锁
        self._lock = threading.Lock()
        
    def record_request(self, method: str, status: str, duration: float):
        """记录请求指标"""
        self.request_count.labels(method=method, status=status).inc()
        self.request_duration.labels(method=method).observe(duration)
        
    def record_audio_processing(self, audio_format: str, status: str, 
                              duration: float, file_size: int, 
                              audio_duration: float, operation: str = "full_processing"):
        """记录音频处理指标"""
        with self._lock:
            # 基础指标
            self.audio_processed_total.labels(format=audio_format, status=status).inc()
            self.audio_processing_duration.labels(operation=operation).observe(duration)
            self.audio_file_size.observe(file_size)
            self.audio_duration.observe(audio_duration)
            
            # 内部统计
            if status == "success":
                self.audio_metrics.total_processed += 1
                self.audio_metrics.total_duration += audio_duration
                self.audio_metrics.total_processing_time += duration
                self.processing_times.append(duration)
            else:
                self.audio_metrics.error_count += 1
                
    def record_feature_extraction(self, feature_type: str, duration: float):
        """记录特征提取指标"""
        self.feature_extraction_duration.labels(feature_type=feature_type).observe(duration)
        self.features_extracted_total.labels(feature_type=feature_type).inc()
        
    def record_tcm_diagnosis(self, diagnosis_type: str, constitution_type: str = None,
                           emotion_type: str = None, organ_type: str = None):
        """记录中医诊断指标"""
        with self._lock:
            self.tcm_diagnoses_total.labels(diagnosis_type=diagnosis_type).inc()
            self.tcm_metrics.total_diagnoses += 1
            
            if constitution_type:
                self.tcm_constitution_analysis.labels(constitution_type=constitution_type).inc()
                self.tcm_metrics.constitution_analyses[constitution_type] += 1
                
            if emotion_type:
                self.tcm_emotion_analysis.labels(emotion_type=emotion_type).inc()
                self.tcm_metrics.emotion_analyses[emotion_type] += 1
                
            if organ_type:
                self.tcm_organ_analysis.labels(organ_type=organ_type).inc()
                self.tcm_metrics.organ_analyses[organ_type] += 1
                
    def record_cache_operation(self, operation: str, result: str):
        """记录缓存操作指标"""
        self.cache_operations.labels(operation=operation, result=result).inc()
        
        with self._lock:
            if result == "hit":
                self.audio_metrics.cache_hits += 1
            elif result == "miss":
                self.audio_metrics.cache_misses += 1
                
    def set_resource_usage(self, cpu_percent: float, memory_bytes: int, 
                          process_name: str = "main"):
        """设置资源使用指标"""
        self.cpu_usage.labels(process=process_name).set(cpu_percent)
        self.memory_usage.labels(process=process_name).set(memory_bytes)
        
        with self._lock:
            self.memory_history.append(memory_bytes)
            
    def set_gpu_memory_usage(self, memory_bytes: int, device: str = "0"):
        """设置GPU内存使用指标"""
        self.gpu_memory_usage.labels(device=device).set(memory_bytes)
        
    def set_health_status(self, healthy: bool, component: str = "service"):
        """设置健康状态"""
        self.health_status.labels(component=component).set(1 if healthy else 0)
        
    def set_active_connections(self, count: int):
        """设置活跃连接数"""
        self.active_connections.set(count)
        
    def set_service_info(self, version: str, build_time: str, 
                        python_version: str, dependencies: Dict[str, str]):
        """设置服务信息"""
        info_dict = {
            'version': version,
            'build_time': build_time,
            'python_version': python_version,
        }
        info_dict.update(dependencies)
        self.service_info.info(info_dict)
        
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        with self._lock:
            avg_processing_time = (
                sum(self.processing_times) / len(self.processing_times)
                if self.processing_times else 0
            )
            
            cache_hit_rate = (
                self.audio_metrics.cache_hits / 
                (self.audio_metrics.cache_hits + self.audio_metrics.cache_misses)
                if (self.audio_metrics.cache_hits + self.audio_metrics.cache_misses) > 0 else 0
            )
            
            return {
                "total_processed": self.audio_metrics.total_processed,
                "total_duration": self.audio_metrics.total_duration,
                "total_processing_time": self.audio_metrics.total_processing_time,
                "average_processing_time": avg_processing_time,
                "error_count": self.audio_metrics.error_count,
                "cache_hit_rate": cache_hit_rate,
                "recent_processing_times": list(self.processing_times)[-10:],
                "memory_trend": list(self.memory_history)[-10:]
            }
            
    def get_tcm_stats(self) -> Dict[str, Any]:
        """获取中医诊断统计信息"""
        with self._lock:
            return {
                "total_diagnoses": self.tcm_metrics.total_diagnoses,
                "constitution_analyses": dict(self.tcm_metrics.constitution_analyses),
                "emotion_analyses": dict(self.tcm_metrics.emotion_analyses),
                "organ_analyses": dict(self.tcm_metrics.organ_analyses)
            }
            
    def generate_metrics(self) -> str:
        """生成Prometheus格式的指标"""
        return generate_latest(self.registry).decode('utf-8')
        
    def start_http_server(self, port: int = 9090, addr: str = "0.0.0.0"):
        """启动HTTP指标服务器"""
        start_http_server(port, addr, registry=self.registry)
        
    def reset_metrics(self):
        """重置所有指标（用于测试）"""
        with self._lock:
            self.audio_metrics = AudioProcessingMetrics()
            self.tcm_metrics = TCMDiagnosisMetrics()
            self.processing_times.clear()
            self.memory_history.clear()

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self._start_times = {}
        
    def start_operation(self, operation_id: str):
        """开始操作计时"""
        self._start_times[operation_id] = time.time()
        
    def end_operation(self, operation_id: str, operation_type: str = "general") -> float:
        """结束操作计时并记录指标"""
        if operation_id not in self._start_times:
            return 0.0
            
        duration = time.time() - self._start_times[operation_id]
        del self._start_times[operation_id]
        
        # 根据操作类型记录不同的指标
        if operation_type == "audio_processing":
            self.metrics.audio_processing_duration.labels(operation="custom").observe(duration)
        elif operation_type == "feature_extraction":
            self.metrics.feature_extraction_duration.labels(feature_type="custom").observe(duration)
        
        return duration
        
    def measure_operation(self, operation_type: str = "general"):
        """操作计时装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                operation_id = f"{func.__name__}_{id(args)}"
                self.start_operation(operation_id)
                try:
                    result = func(*args, **kwargs)
                    duration = self.end_operation(operation_id, operation_type)
                    return result
                except Exception as e:
                    self.end_operation(operation_id, operation_type)
                    raise e
            return wrapper
        return decorator

class AlertManager:
    """告警管理器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5%错误率
            "avg_processing_time": 10.0,  # 10秒平均处理时间
            "memory_usage": 8 * 1024 * 1024 * 1024,  # 8GB内存使用
            "cache_hit_rate": 0.8  # 80%缓存命中率
        }
        self.alert_callbacks = []
        
    def add_alert_callback(self, callback):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)
        
    def check_alerts(self):
        """检查告警条件"""
        stats = self.metrics.get_processing_stats()
        alerts = []
        
        # 检查错误率
        total_requests = stats["total_processed"] + stats["error_count"]
        if total_requests > 0:
            error_rate = stats["error_count"] / total_requests
            if error_rate > self.alert_thresholds["error_rate"]:
                alerts.append({
                    "type": "error_rate",
                    "value": error_rate,
                    "threshold": self.alert_thresholds["error_rate"],
                    "message": f"错误率过高: {error_rate:.2%}"
                })
        
        # 检查平均处理时间
        if stats["average_processing_time"] > self.alert_thresholds["avg_processing_time"]:
            alerts.append({
                "type": "avg_processing_time",
                "value": stats["average_processing_time"],
                "threshold": self.alert_thresholds["avg_processing_time"],
                "message": f"平均处理时间过长: {stats['average_processing_time']:.2f}秒"
            })
        
        # 检查缓存命中率
        if stats["cache_hit_rate"] < self.alert_thresholds["cache_hit_rate"]:
            alerts.append({
                "type": "cache_hit_rate",
                "value": stats["cache_hit_rate"],
                "threshold": self.alert_thresholds["cache_hit_rate"],
                "message": f"缓存命中率过低: {stats['cache_hit_rate']:.2%}"
            })
        
        # 触发告警回调
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"告警回调执行失败: {e}")
        
        return alerts

# 全局指标收集器实例
_metrics_collector = None

def get_metrics(service_name: str = "listen_service") -> MetricsCollector:
    """获取全局指标收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(service_name)
    return _metrics_collector

def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例"""
    return PerformanceMonitor(get_metrics())

def get_alert_manager() -> AlertManager:
    """获取告警管理器实例"""
    return AlertManager(get_metrics())

def configure(
    namespace: str = None,
    subsystem: str = None,
    push_gateway: str = None,
    push_interval: int = None,
    enabled: bool = None
):
    """
    配置指标收集模块
    
    参数:
        namespace: 指标命名空间
        subsystem: 指标子系统
        push_gateway: Prometheus Push Gateway地址
        push_interval: 推送间隔（秒）
        enabled: 是否启用指标收集
    """
    global _config, _push_thread, _push_thread_stop_event
    
    # 更新配置
    if namespace is not None:
        _config["namespace"] = namespace
    if subsystem is not None:
        _config["subsystem"] = subsystem
    if push_gateway is not None:
        _config["push_gateway"] = push_gateway
    if push_interval is not None:
        _config["push_interval"] = push_interval
    if enabled is not None:
        _config["enabled"] = enabled
    
    # 如果启用了Push Gateway
    if _config["enabled"] and _config["push_gateway"]:
        # 停止现有的推送线程
        if _push_thread and _push_thread.is_alive():
            _push_thread_stop_event.set()
            _push_thread.join(timeout=5)
        
        # 重置停止事件
        _push_thread_stop_event.clear()
        
        # 创建新的推送线程
        _push_thread = threading.Thread(
            target=_push_metrics_loop,
            daemon=True,
            name="metrics-push-thread"
        )
        _push_thread.start()
        logger.info(f"启动指标推送线程，目标: {_config['push_gateway']}, 间隔: {_config['push_interval']}秒")

def _make_name(name: str) -> str:
    """
    创建完整的指标名称
    
    参数:
        name: 指标基本名称
        
    返回:
        完整指标名称
    """
    parts = []
    if _config["namespace"]:
        parts.append(_config["namespace"])
    if _config["subsystem"]:
        parts.append(_config["subsystem"])
    parts.append(name)
    return "_".join(parts)

def _push_metrics_loop():
    """推送指标循环"""
    while not _push_thread_stop_event.is_set():
        try:
            # 推送指标
            if _config["push_gateway"]:
                push_to_gateway(
                    gateway=_config["push_gateway"],
                    job="listen_service",
                    registry=REGISTRY
                )
                logger.debug(f"指标已推送到 {_config['push_gateway']}")
        except Exception as e:
            logger.error(f"推送指标失败: {str(e)}", exc_info=True)
        
        # 等待下一次推送
        _push_thread_stop_event.wait(_config["push_interval"])

def counter(name: str, description: str, labels: List[str] = None) -> Counter:
    """
    创建或获取计数器指标
    
    参数:
        name: 指标名称
        description: 指标描述
        labels: 标签列表
        
    返回:
        计数器对象
    """
    if not _config["enabled"]:
        return DummyMetric()
    
    full_name = _make_name(name)
    key = f"counter:{full_name}"
    
    if key not in _metrics:
        _metrics[key] = Counter(
            full_name,
            description,
            labels or []
        )
    
    return _metrics[key]

def gauge(name: str, description: str, labels: List[str] = None) -> Gauge:
    """
    创建或获取仪表盘指标
    
    参数:
        name: 指标名称
        description: 指标描述
        labels: 标签列表
        
    返回:
        仪表盘对象
    """
    if not _config["enabled"]:
        return DummyMetric()
    
    full_name = _make_name(name)
    key = f"gauge:{full_name}"
    
    if key not in _metrics:
        _metrics[key] = Gauge(
            full_name,
            description,
            labels or []
        )
    
    return _metrics[key]

def histogram(
    name: str,
    description: str,
    labels: List[str] = None,
    buckets: List[float] = None
) -> Histogram:
    """
    创建或获取直方图指标
    
    参数:
        name: 指标名称
        description: 指标描述
        labels: 标签列表
        buckets: 直方图桶
        
    返回:
        直方图对象
    """
    if not _config["enabled"]:
        return DummyMetric()
    
    full_name = _make_name(name)
    key = f"histogram:{full_name}"
    
    if key not in _metrics:
        _metrics[key] = Histogram(
            full_name,
            description,
            labels or [],
            buckets=buckets or DEFAULT_BUCKETS
        )
    
    return _metrics[key]

def summary(
    name: str,
    description: str,
    labels: List[str] = None
) -> Summary:
    """
    创建或获取摘要指标
    
    参数:
        name: 指标名称
        description: 指标描述
        labels: 标签列表
        
    返回:
        摘要对象
    """
    if not _config["enabled"]:
        return DummyMetric()
    
    full_name = _make_name(name)
    key = f"summary:{full_name}"
    
    if key not in _metrics:
        _metrics[key] = Summary(
            full_name,
            description,
            labels or []
        )
    
    return _metrics[key]

def increment_counter(name: str, labels: Dict[str, str] = None, value: float = 1.0):
    """
    增加计数器值
    
    参数:
        name: 指标名称
        labels: 标签字典
        value: 增加的值
    """
    if not _config["enabled"]:
        return
    
    try:
        metric = counter(name, f"Counter for {name}")
        if labels:
            metric.labels(**labels).inc(value)
        else:
            metric.inc(value)
    except Exception as e:
        logger.error(f"增加计数器失败: {name}, 错误: {str(e)}", exc_info=True)

def set_gauge(name: str, value: float, labels: Dict[str, str] = None):
    """
    设置仪表盘值
    
    参数:
        name: 指标名称
        value: 设置的值
        labels: 标签字典
    """
    if not _config["enabled"]:
        return
    
    try:
        metric = gauge(name, f"Gauge for {name}")
        if labels:
            metric.labels(**labels).set(value)
        else:
            metric.set(value)
    except Exception as e:
        logger.error(f"设置仪表盘失败: {name}, 错误: {str(e)}", exc_info=True)

def observe_histogram(name: str, value: float, labels: Dict[str, str] = None):
    """
    观察直方图值
    
    参数:
        name: 指标名称
        value: 观察的值
        labels: 标签字典
    """
    if not _config["enabled"]:
        return
    
    try:
        metric = histogram(name, f"Histogram for {name}")
        if labels:
            metric.labels(**labels).observe(value)
        else:
            metric.observe(value)
    except Exception as e:
        logger.error(f"观察直方图失败: {name}, 错误: {str(e)}", exc_info=True)

def observe_summary(name: str, value: float, labels: Dict[str, str] = None):
    """
    观察摘要值
    
    参数:
        name: 指标名称
        value: 观察的值
        labels: 标签字典
    """
    if not _config["enabled"]:
        return
    
    try:
        metric = summary(name, f"Summary for {name}")
        if labels:
            metric.labels(**labels).observe(value)
        else:
            metric.observe(value)
    except Exception as e:
        logger.error(f"观察摘要失败: {name}, 错误: {str(e)}", exc_info=True)

class DummyMetric:
    """
    空指标类，用于指标收集禁用时
    """
        @cache(timeout=300)  # 5分钟缓存
def __getattr__(self, name):
        return self._dummy_method
    
    def _dummy_method(self, *args, **kwargs):
        return self
    
    def labels(self, *args, **kwargs):
        return self

def timed(
    name: str = None,
    labels: Dict[str, str] = None,
    label_keys: List[str] = None,
    buckets: List[float] = None
):
    """
    计时装饰器，用于测量函数执行时间
    
    参数:
        name: 指标名称，默认为函数名
        labels: 静态标签字典
        label_keys: 从函数参数中提取的标签键列表
        buckets: 直方图桶
        
    示例:
        @timed(labels={"service": "my_service"})
        def my_function(param1, param2):
            # 函数代码
            
        @timed(label_keys=["user_id"])
        def process_user(user_id, data):
            # 函数代码
    """
    def decorator(func):
        metric_name = name or f"function_duration_{func.__name__}"
        
        # 提取标签键
        static_labels = labels or {}
        dynamic_label_keys = label_keys or []
        
        # 创建指标
        if _config["enabled"]:
            all_label_keys = list(static_labels.keys()) + dynamic_label_keys
            duration_metric = histogram(
                metric_name,
                f"函数 {func.__name__} 的执行时间",
                all_label_keys,
                buckets
            )
            calls_metric = counter(
                f"{metric_name}_calls",
                f"函数 {func.__name__} 的调用次数",
                all_label_keys + ["status"]
            )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not _config["enabled"]:
                return func(*args, **kwargs)
            
            # 从参数中提取标签
            dynamic_labels = {}
            for key in dynamic_label_keys:
                if key in kwargs:
                    dynamic_labels[key] = str(kwargs[key])
            
            # 合并静态和动态标签
            all_labels = {**static_labels, **dynamic_labels}
            
            start_time = time.time()
            status = "success"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                
                # 记录指标
                try:
                    duration_metric.labels(**all_labels).observe(duration)
                    calls_metric.labels(**all_labels, status=status).inc()
                except Exception as metric_error:
                    logger.error(f"记录指标失败: {str(metric_error)}", exc_info=True)
        
        return wrapper
    
    # 支持不带参数的装饰器调用
    if callable(name):
        func = name
        name = None
        return decorator(func)
    
    return decorator

def grpc_metrics(
    namespace: str = None,
    service_name: str = None
):
    """
    gRPC服务器指标装饰器
    
    参数:
        namespace: 指标命名空间
        service_name: 服务名称
        
    示例:
        @grpc_metrics(service_name="listen_service")
        class ListenServiceServicer(listen_service_pb2_grpc.ListenServiceServicer):
            # 服务实现
    """
    def decorator(servicer_class):
        service = service_name or servicer_class.__name__.replace("Servicer", "").lower()
        ns = namespace or _config["namespace"]
        
        # 查找所有gRPC方法
        original_methods = {}
        for name, method in servicer_class.__dict__.items():
            if callable(method) and not name.startswith('__'):
                original_methods[name] = method
        
        # 创建指标
        if _config["enabled"]:
            # 请求计数器
            request_counter = Counter(
                f"{ns}_{service}_requests_total",
                f"{service} gRPC请求总数",
                ["method", "status"]
            )
            
            # 请求延迟直方图
            request_latency = Histogram(
                f"{ns}_{service}_request_duration_seconds",
                f"{service} gRPC请求延迟（秒）",
                ["method"],
                buckets=DEFAULT_BUCKETS
            )
            
            # 活跃请求数
            active_requests = Gauge(
                f"{ns}_{service}_active_requests",
                f"{service} 活跃gRPC请求数",
                ["method"]
            )
        
        # 重写gRPC方法
        for name, method in original_methods.items():
            @functools.wraps(method)
            def wrapper(self, request, context, method_name=name, original_method=method):
                if not _config["enabled"]:
                    return original_method(self, request, context)
                
                active_requests.labels(method=method_name).inc()
                start_time = time.time()
                
                try:
                    result = original_method(self, request, context)
                    request_counter.labels(method=method_name, status="success").inc()
                    return result
                except Exception as e:
                    request_counter.labels(method=method_name, status="error").inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    request_latency.labels(method=method_name).observe(duration)
                    active_requests.labels(method=method_name).dec()
            
            setattr(servicer_class, name, wrapper)
        
        return servicer_class
    
    return decorator

def init_from_config(config: Dict[str, Any]):
    """
    从配置初始化指标模块
    
    参数:
        config: 配置字典
    """
    # 提取指标配置
    metrics_config = config.get("monitoring", {}).get("prometheus", {})
    
    if metrics_config:
        configure(
            namespace=metrics_config.get("namespace"),
            subsystem=metrics_config.get("subsystem"),
            push_gateway=metrics_config.get("push_gateway"),
            push_interval=metrics_config.get("push_interval"),
            enabled=metrics_config.get("enabled", True)
        )
        logger.info("指标收集已从配置初始化") 