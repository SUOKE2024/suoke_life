"""
指标收集模块，用于监控服务性能和健康状态
"""
import time
import logging
import functools
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from prometheus_client import Counter, Histogram, Gauge, Summary, REGISTRY, push_to_gateway

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