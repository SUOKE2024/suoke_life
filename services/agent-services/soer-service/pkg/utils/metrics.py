"""
metrics - 索克生活项目模块
"""

from collections import defaultdict
from functools import wraps
from pkg.utils.dependency_injection import ServiceLifecycle
from prometheus_client import (
from threading import Lock
from typing import Any
import logging
import time

#!/usr/bin/env python3
"""
指标收集器
提供Prometheus指标收集和暴露功能
"""

    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    generate_latest,
)


# 配置日志
logger = logging.getLogger(__name__)

# 全局指标收集器实例
_metrics_collector: MetricsCollector | None = None

class MetricsCollector(ServiceLifecycle):
    """指标收集器"""

    def __init__(self, registry: CollectorRegistry | None = None):
        self.registry = registry or REGISTRY
        self._lock = Lock()

        # 基础指标
        self._counters: dict[str, PrometheusCounter] = {}
        self._histograms: dict[str, PrometheusHistogram] = {}
        self._gauges: dict[str, PrometheusGauge] = {}
        self._infos: dict[str, PrometheusInfo] = {}

        # 内存中的指标缓存
        self._counter_cache: dict[str, float] = defaultdict(float)
        self._histogram_cache: dict[str, list[float]] = defaultdict(list)
        self._gauge_cache: dict[str, float] = {}

        # 初始化核心指标
        self._init_core_metrics()

    def _init_core_metrics(self) -> None:
        """初始化核心指标"""
        # 请求相关指标
        self.register_counter(
            "soer_requests_total",
            "总请求数",
            ["user_id", "endpoint", "method"]
        )

        self.register_counter(
            "soer_requests_success",
            "成功请求数",
            ["user_id", "endpoint"]
        )

        self.register_counter(
            "soer_requests_error",
            "错误请求数",
            ["user_id", "endpoint", "error_type"]
        )

        self.register_histogram(
            "soer_request_duration_seconds",
            "请求处理时间",
            ["endpoint", "method", "status_code"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
        )

        # 智能体相关指标
        self.register_counter(
            "soer_agent_conversations",
            "智能体对话数",
            ["user_id", "conversation_type"]
        )

        self.register_histogram(
            "soer_agent_response_time",
            "智能体响应时间",
            ["conversation_type"],
            buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 60.0]
        )

        # 缓存相关指标
        self.register_counter(
            "soer_cache_hits",
            "缓存命中数",
            ["cache_type", "endpoint"]
        )

        self.register_counter(
            "soer_cache_misses",
            "缓存未命中数",
            ["cache_type", "endpoint"]
        )

        # 数据库相关指标
        self.register_counter(
            "soer_db_queries",
            "数据库查询数",
            ["operation", "table"]
        )

        self.register_histogram(
            "soer_db_query_duration",
            "数据库查询时间",
            ["operation", "table"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )

        # 系统资源指标
        self.register_gauge(
            "soer_active_sessions",
            "活跃会话数"
        )

        self.register_gauge(
            "soer_memory_usage_bytes",
            "内存使用量（字节）"
        )

        self.register_gauge(
            "soer_cpu_usage_percent",
            "CPU使用率（百分比）"
        )

        # 错误相关指标
        self.register_counter(
            "soer_errors_total",
            "错误总数",
            ["error_type", "severity", "component"]
        )

        # 限流相关指标
        self.register_counter(
            "soer_rate_limit_exceeded",
            "限流触发次数",
            ["client_type", "endpoint"]
        )

        # 认证相关指标
        self.register_counter(
            "soer_auth_attempts",
            "认证尝试次数",
            ["result", "method"]
        )

    async def start(self) -> None:
        """启动指标收集器"""
        logger.info("指标收集器启动成功")

    async def stop(self) -> None:
        """停止指标收集器"""
        logger.info("指标收集器已停止")

    async def health_check(self) -> bool:
        """健康检查"""
        return True

    def register_counter(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None
    ) -> PrometheusCounter:
        """注册计数器指标"""
        with self._lock:
            if name not in self._counters:
                self._counters[name] = PrometheusCounter(
                    name, description, labels or [], registry=self.registry
                )
            return self._counters[name]

    def register_histogram(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: list[float] | None = None
    ) -> PrometheusHistogram:
        """注册直方图指标"""
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = PrometheusHistogram(
                    name, description, labels or [],
                    buckets=buckets, registry=self.registry
                )
            return self._histograms[name]

    def register_gauge(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None
    ) -> PrometheusGauge:
        """注册仪表盘指标"""
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = PrometheusGauge(
                    name, description, labels or [], registry=self.registry
                )
            return self._gauges[name]

    def register_info(
        self,
        name: str,
        description: str
    ) -> PrometheusInfo:
        """注册信息指标"""
        with self._lock:
            if name not in self._infos:
                self._infos[name] = PrometheusInfo(
                    name, description, registry=self.registry
                )
            return self._infos[name]

    def increment_counter(
        self,
        name: str,
        labels: dict[str, str] | None = None,
        value: float = 1.0
    ) -> None:
        """增加计数器"""
        try:
            if name in self._counters:
                if labels:
                    self._counters[name].labels(**labels).inc(value)
                else:
                    self._counters[name].inc(value)
            else:
                logger.warning(f"计数器指标未注册: {name}")
        except Exception as e:
            logger.error(f"增加计数器失败: {e}")

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None
    ) -> None:
        """观察直方图值"""
        try:
            if name in self._histograms:
                if labels:
                    self._histograms[name].labels(**labels).observe(value)
                else:
                    self._histograms[name].observe(value)
            else:
                logger.warning(f"直方图指标未注册: {name}")
        except Exception as e:
            logger.error(f"观察直方图失败: {e}")

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None
    ) -> None:
        """设置仪表盘值"""
        try:
            if name in self._gauges:
                if labels:
                    self._gauges[name].labels(**labels).set(value)
                else:
                    self._gauges[name].set(value)
            else:
                logger.warning(f"仪表盘指标未注册: {name}")
        except Exception as e:
            logger.error(f"设置仪表盘失败: {e}")

    def inc_gauge(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None
    ) -> None:
        """增加仪表盘值"""
        try:
            if name in self._gauges:
                if labels:
                    self._gauges[name].labels(**labels).inc(value)
                else:
                    self._gauges[name].inc(value)
            else:
                logger.warning(f"仪表盘指标未注册: {name}")
        except Exception as e:
            logger.error(f"增加仪表盘失败: {e}")

    def dec_gauge(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None
    ) -> None:
        """减少仪表盘值"""
        try:
            if name in self._gauges:
                if labels:
                    self._gauges[name].labels(**labels).dec(value)
                else:
                    self._gauges[name].dec(value)
            else:
                logger.warning(f"仪表盘指标未注册: {name}")
        except Exception as e:
            logger.error(f"减少仪表盘失败: {e}")

    def set_info(
        self,
        name: str,
        info: dict[str, str]
    ) -> None:
        """设置信息指标"""
        try:
            if name in self._infos:
                self._infos[name].info(info)
            else:
                logger.warning(f"信息指标未注册: {name}")
        except Exception as e:
            logger.error(f"设置信息指标失败: {e}")

    # 便捷方法
    def histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None
    ) -> None:
        """直方图观察的便捷方法"""
        self.observe_histogram(name, value, labels)

    def timer(self, name: str, labels: dict[str, str] | None = None):
        """计时器上下文管理器"""
        return TimerContext(self, name, labels)

    def get_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        return generate_latest(self.registry).decode('utf-8')

    def get_content_type(self) -> str:
        """获取指标内容类型"""
        return CONTENT_TYPE_LATEST

    def get_stats(self) -> dict[str, Any]:
        """获取指标统计信息"""
        return {
            "counters": len(self._counters),
            "histograms": len(self._histograms),
            "gauges": len(self._gauges),
            "infos": len(self._infos),
            "registry_collectors": len(list(self.registry._collector_to_names.keys()))
        }

class TimerContext:
    """计时器上下文管理器"""

    def __init__(self, metrics: MetricsCollector, name: str, labels: dict[str, str] | None = None):
        self.metrics = metrics
        self.name = name
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics.observe_histogram(self.name, duration, self.labels)

def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def setup_metrics_collector(collector: MetricsCollector) -> None:
    """设置全局指标收集器"""
    global _metrics_collector
    _metrics_collector = collector

def initialize_metrics(config: dict[str, Any]):
    """
    初始化指标收集

    Args:
        config: 指标收集配置
    """
    global _http_server_started

    try:
        # 获取指标服务器端口
        port = config.get("port", 9098)

        # 启动HTTP服务器（如果尚未启动）
        with _http_server_lock:
            if not _http_server_started:
                start_http_server(port)
                _http_server_started = True
                logger.info(f"Prometheus指标服务器已启动在端口 {port}")
    except Exception as e:
        logger.error(f"启动指标服务器失败: {str(e)}")

def track_api_request(method: str, endpoint: str, status_code: int, duration: float):
    """
    记录API请求指标

    Args:
        method: HTTP方法
        endpoint: API端点
        status_code: HTTP状态码
        duration: 请求持续时间（秒）
    """
    try:
        METRICS["api_requests_total"].labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()

        METRICS["api_request_duration_seconds"].labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    except Exception as e:
        logger.error(f"记录API请求指标失败: {str(e)}")

def track_health_plan_generation(constitution_type: str, status: str = "success"):
    """
    记录健康计划生成指标

    Args:
        constitution_type: 体质类型
        status: 生成状态 ("success" 或 "failure")
    """
    try:
        METRICS["health_plan_generations_total"].labels(
            constitution_type=constitution_type,
            status=status
        ).inc()
    except Exception as e:
        logger.error(f"记录健康计划生成指标失败: {str(e)}")

def track_emotional_analysis(input_type: str, status: str = "success"):
    """
    记录情绪分析指标

    Args:
        input_type: 输入类型 ("text", "voice", "physiological")
        status: 分析状态 ("success" 或 "failure")
    """
    try:
        METRICS["emotional_analyses_total"].labels(
            input_type=input_type,
            status=status
        ).inc()
    except Exception as e:
        logger.error(f"记录情绪分析指标失败: {str(e)}")

def track_llm_api_call(model: str, duration: float, status: str = "success",
                        input_tokens: int = 0, output_tokens: int = 0):
    """
    记录LLM API调用指标

    Args:
        model: 模型名称
        duration: 调用持续时间（秒）
        status: 调用状态 ("success" 或 "failure")
        input_tokens: 输入令牌数量
        output_tokens: 输出令牌数量
    """
    try:
        METRICS["llm_api_calls_total"].labels(
            model=model,
            status=status
        ).inc()

        METRICS["llm_api_duration_seconds"].labels(
            model=model
        ).observe(duration)

        METRICS["llm_token_usage"].labels(
            model=model,
            token_type="input"
        ).inc(input_tokens)

        METRICS["llm_token_usage"].labels(
            model=model,
            token_type="output"
        ).inc(output_tokens)
    except Exception as e:
        logger.error(f"记录LLM API调用指标失败: {str(e)}")

    @cache(timeout=300)  # 5分钟缓存
def track_database_query(query_type: str, database: str, duration: float):
    """
    记录数据库查询指标

    Args:
        query_type: 查询类型 ("select", "insert", "update", "delete")
        database: 数据库名称
        duration: 查询持续时间（秒）
    """
    try:
        METRICS["database_query_duration_seconds"].labels(
            query_type=query_type,
            database=database
        ).observe(duration)
    except Exception as e:
        logger.error(f"记录数据库查询指标失败: {str(e)}")

def update_active_connections(connection_type: str, count: int):
    """
    更新活动连接计数

    Args:
        connection_type: 连接类型 ("grpc", "http", "database")
        count: 连接数量
    """
    try:
        METRICS["active_connections"].labels(
            connection_type=connection_type
        ).set(count)
    except Exception as e:
        logger.error(f"更新活动连接计数失败: {str(e)}")

def track_function_time(module: str = "unknown"):
    """
    函数执行时间跟踪装饰器

    Args:
        module: 模块名称

    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                try:
                    METRICS["function_execution_time_seconds"].labels(
                        function_name=func.__name__,
                        module=module
                    ).observe(duration)
                except Exception as e:
                    logger.error(f"记录函数执行时间指标失败: {str(e)}")
        return wrapper
    return decorator

def track_async_function_time(module: str = "unknown"):
    """
    异步函数执行时间跟踪装饰器

    Args:
        module: 模块名称

    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                try:
                    METRICS["function_execution_time_seconds"].labels(
                        function_name=func.__name__,
                        module=module
                    ).observe(duration)
                except Exception as e:
                    logger.error(f"记录异步函数执行时间指标失败: {str(e)}")
        return wrapper
    return decorator
