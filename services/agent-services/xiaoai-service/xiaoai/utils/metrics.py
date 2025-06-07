"""
小艾智能体指标收集模块
提供性能监控、指标收集和Prometheus集成功能
"""

import functools
import time

# 尝试导入Prometheus客户端
try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # 创建模拟类
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass

    def start_http_server(port):
        pass


class MetricsCollector:
    """指标收集器"""

    def __init__(self, enable_prometheus: bool = True):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self._counters = {}
        self._gauges = {}
        self._histograms = {}

        if self.enable_prometheus:
            self._init_prometheus_metrics()

    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        # 基础指标
        self._counters['requests_total'] = Counter(
            'requests_total', 'Total requests', ['method', 'endpoint', 'status']
        )
        self._counters['errors_total'] = Counter(
            'errors_total', 'Total errors', ['type', 'service']
        )

        self._gauges['active_sessions'] = Gauge(
            'active_sessions', 'Active sessions count'
        )

        self._histograms['request_duration'] = Histogram(
            'request_duration_seconds', 'Request duration', ['method', 'endpoint']
        )

    def increment_counter(self, name: str, value: int = 1, tags: dict[str, str] | None = None):
        """增加计数器"""
        if self.enable_prometheus and name in self._counters:
            if tags:
                self._counters[name].labels(**tags).inc(value)
            else:
                self._counters[name].inc(value)

    def set_gauge(self, name: str, value: float, tags: dict[str, str] | None = None):
        """设置仪表盘值"""
        if self.enable_prometheus and name in self._gauges:
            if tags:
                self._gauges[name].labels(**tags).set(value)
            else:
                self._gauges[name].set(value)

    def observe_histogram(self, name: str, value: float, tags: dict[str, str] | None = None):
        """观察直方图值"""
        if self.enable_prometheus and name in self._histograms:
            if tags:
                self._histograms[name].labels(**tags).observe(value)
            else:
                self._histograms[name].observe(value)

    def start_metrics_server(self, port: int = 8000):
        """启动指标服务器"""
        if self.enable_prometheus and PROMETHEUS_AVAILABLE:
            start_http_server(port)

# 全局指标收集器实例
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def increment_counter(name: str, value: int = 1, tags: dict[str, str] | None = None):
    """增加计数器的便捷函数"""
    collector = get_metrics_collector()
    collector.increment_counter(name, value, tags)


def set_gauge(name: str, value: float, tags: dict[str, str] | None = None):
    """设置仪表盘值的便捷函数"""
    collector = get_metrics_collector()
    collector.set_gauge(name, value, tags)


def record_time(name: str, duration: float, tags: dict[str, str] | None = None):
    """记录时间的便捷函数"""
    collector = get_metrics_collector()
    collector.observe_histogram(name, duration, tags)


class Timer:
    """计时器上下文管理器"""

    def __init__(self, name: str, tags: dict[str, str] | None = None):
        self.name = name
        self.tags = tags
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            record_time(self.name, duration, self.tags)


def timer(name: str, tags: dict[str, str] | None = None):
    """计时器装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                final_tags = (tags or {}).copy()
                final_tags.update({
                    'function': func.__name__,
                    'success': str(success)
                })
                record_time(name, duration, final_tags)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                final_tags = (tags or {}).copy()
                final_tags.update({
                    'function': func.__name__,
                    'success': str(success)
                })
                record_time(name, duration, final_tags)

        # 检查是否是异步函数
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# 业务指标记录函数
def record_agent_operation(agent_name: str, action: str, success: bool, duration: float):
    """记录智能体操作指标"""
    tags = {
        'agent': agent_name,
        'action': action,
        'success': str(success).lower()
    }
    increment_counter('agent_operations_total', 1.0, tags)
    record_time('agent_operation_duration', duration, tags)

def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
    """记录API请求指标"""
    tags = {
        'method': method,
        'endpoint': endpoint,
        'status_code': str(status_code),
        'success': str(200 <= status_code < 400).lower()
    }
    increment_counter('api_requests_total', 1.0, tags)
    record_time('api_request_duration', duration, tags)

def record_cache_operation(operation: str, hit: bool):
    """记录缓存操作指标"""
    tags = {'operation': operation}
    increment_counter('cache_operations_total', 1.0, tags)

    if hit:
        increment_counter('cache_hits_total', 1.0, tags)
    else:
        increment_counter('cache_misses_total', 1.0, tags)

def set_active_sessions(count: int):
    """设置活跃会话数"""
    set_gauge('active_sessions', float(count))

def record_chat_message(user_id: str, message_type: str):
    """记录聊天消息"""
    tags = {
        'user_id': user_id,
        'message_type': message_type
    }
    increment_counter('chat_messages_total', 1.0, tags)

def record_multimodal_process(input_type: str, status: str, latency: float, input_size: int):
    """记录多模态处理"""
    tags = {
        'input_type': input_type,
        'status': status
    }
    increment_counter('multimodal_processes_total', 1.0, tags)
    record_time('multimodal_process_duration', latency, tags)
    set_gauge('multimodal_input_size_bytes', float(input_size), tags)
