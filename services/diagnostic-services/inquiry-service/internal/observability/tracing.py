"""
tracing - 索克生活项目模块
"""

from collections.abc import Callable
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from typing import Any, TypeVar, cast
import functools
import logging
import os

#! / usr / bin / env python

"""
分布式追踪模块
提供服务调用链追踪功能
"""



logger = logging.getLogger(__name__)

# 类型变量，用于装饰器函数签名
F = TypeVar("F", bound = Callable[..., Any])


class TracingManager:
    """追踪管理器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化追踪管理器

        Args:
            config: 追踪配置
        """
        self.config = config.get("tracing", {})
        self.enabled = self.config.get("enabled", False)
        self.service_name = self.config.get("service_name", "inquiry - service")
        self.otlp_endpoint = self.config.get("otlp_endpoint", "localhost:4317")

        self.provider = None
        self.tracer = None

        # 如果启用了追踪，则初始化
        if self.enabled:
            self._setup_tracing()

    def _setup_tracing(self)-> None:
        """设置追踪"""
        try:
            # 创建资源
            resource = Resource.create(
                {
                    ResourceAttributes.SERVICE_NAME: self.service_name,
                    ResourceAttributes.SERVICE_VERSION: self.config.get(
                        "service_version", "unknown"
                    ),
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.environ.get(
                        "SERVICE_ENV", "development"
                    ),
                }
            )

            # 创建追踪提供者
            self.provider = TracerProvider(resource = resource)

            # 创建和注册导出器
            otlp_exporter = OTLPSpanExporter(endpoint = self.otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            self.provider.add_span_processor(span_processor)

            # 设置全局追踪提供者
            trace.set_tracer_provider(self.provider)

            # 获取追踪器
            self.tracer = trace.get_tracer(self.service_name)

            logger.info(
                f"分布式追踪已初始化，服务名: {self.service_name}, 端点: {self.otlp_endpoint}"
            )
        except Exception as e:
            logger.error(f"初始化追踪时出错: {e!s}")
            self.enabled = False

    def create_span(self, name: str, attributes: dict[str, Any] | None = None)-> Any:
        """
        创建追踪跨度

        Args:
            name: 跨度名称
            attributes: 跨度属性

        Returns:
            追踪跨度对象
        """
        if not self.enabled or not self.tracer:
            # 如果追踪未启用，返回空上下文
            return trace.INVALID_SPAN

        return self.tracer.start_span(name = name, attributes = attributes or {})

    def trace_function(
        self, name: str | None = None, attributes: dict[str, Any] | None = None
    )-> Callable[[F], F]:
        """
        函数追踪装饰器

        Args:
            name: 跨度名称，默认为函数名
            attributes: 跨度属性

        Returns:
            装饰后的函数
        """

        def decorator(func: F)-> F:
            """TODO: 添加文档字符串"""
            if not self.enabled or not self.tracer:
                # 如果追踪未启用，直接返回原函数
                return func

            span_name = name or func.__name__

            @functools.wraps(func)
            def wrapper( * args: Any, * *kwargs: Any)-> Any:
                """TODO: 添加文档字符串"""
                with self.tracer.start_as_current_span(
                    name = span_name, attributes = attributes or {}
                ) as span:
                    try:
                        # 执行原函数
                        result = func( * args, * *kwargs)
                        return result
                    except Exception as e:
                        # 记录异常信息
                        span.record_exception(e)
                        span.set_status(trace.StatusCode.ERROR, str(e))
                        raise

            return cast("F", wrapper)

        return decorator

    def shutdown(self)-> None:
        """关闭追踪"""
        if self.provider:
            self.provider.shutdown()
            logger.info("追踪资源已关闭")

    def get_current_span(self)-> Any:
        """
        获取当前跨度

        Returns:
            当前跨度，如果不存在则返回无效跨度
        """
        if not self.enabled:
            return trace.INVALID_SPAN

        return trace.get_current_span()

    def add_event(self, name: str, attributes: dict[str, Any] | None = None)-> None:
        """
        向当前跨度添加事件

        Args:
            name: 事件名称
            attributes: 事件属性
        """
        if not self.enabled:
            return

        span = trace.get_current_span()
        if span is not trace.INVALID_SPAN:
            span.add_event(name, attributes or {})
