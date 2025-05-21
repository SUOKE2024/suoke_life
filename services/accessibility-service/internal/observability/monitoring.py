"""
监控和可观测性服务 - 提供指标收集、分布式追踪和结构化日志
"""
import logging
import time
import json
import os
import socket
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)


class MetricsClient:
    """指标客户端 - 负责收集和上报指标"""
    
    def __init__(self, config):
        """初始化指标客户端

        Args:
            config: 配置对象
        """
        self.config = config
        self.provider = config.observability.metrics.provider
        self.endpoint = config.observability.metrics.endpoint
        self.push_gateway = config.observability.metrics.push_gateway
        self.interval_seconds = config.observability.metrics.interval_seconds
        self.default_labels = config.observability.metrics.labels
        self.hostname = socket.gethostname()
        self.client = None
        
        logger.info(f"初始化指标客户端，提供者: {self.provider}")
        self._initialize_client()
        
    def _initialize_client(self):
        """初始化具体的指标客户端"""
        try:
            if self.provider == "prometheus":
                self._init_prometheus_client()
            elif self.provider == "datadog":
                self._init_datadog_client()
            elif self.provider == "memory":
                self._init_memory_client()
            else:
                logger.warning(f"不支持的指标提供者: {self.provider}")
        except Exception as e:
            logger.error(f"初始化指标客户端失败: {str(e)}")
            # 回退到内存客户端
            self._init_memory_client()
    
    def _init_prometheus_client(self):
        """初始化Prometheus客户端"""
        logger.info("初始化Prometheus客户端")
        # 实际实现中应该使用prometheus_client库
        # 这里使用模拟实现
        self.client = {
            "type": "prometheus",
            "metrics": {},
            "push_gateway": self.push_gateway
        }
    
    def _init_datadog_client(self):
        """初始化Datadog客户端"""
        logger.info("初始化Datadog客户端")
        # 实际实现中应该使用datadog库
        # 这里使用模拟实现
        self.client = {
            "type": "datadog",
            "metrics": {},
            "api_key": os.environ.get("DATADOG_API_KEY", "")
        }
    
    def _init_memory_client(self):
        """初始化内存客户端（用于开发/测试）"""
        logger.info("初始化内存指标客户端")
        self.client = {
            "type": "memory",
            "metrics": {},
            "last_report": time.time()
        }
    
    def counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """计数器指标

        Args:
            name: 指标名称
            value: 增加的值
            labels: 指标标签
        """
        full_labels = self._merge_labels(labels)
        metric_key = f"{name}:{self._labels_to_key(full_labels)}"
        
        if metric_key not in self.client["metrics"]:
            self.client["metrics"][metric_key] = {
                "name": name,
                "type": "counter",
                "value": 0,
                "labels": full_labels
            }
        
        self.client["metrics"][metric_key]["value"] += value
        
        logger.debug(f"计数器 {name} 增加 {value}")
        
        # 实际实现中应该直接调用具体客户端
        self._maybe_push_metrics()
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """仪表盘指标

        Args:
            name: 指标名称
            value: 设置的值
            labels: 指标标签
        """
        full_labels = self._merge_labels(labels)
        metric_key = f"{name}:{self._labels_to_key(full_labels)}"
        
        self.client["metrics"][metric_key] = {
            "name": name,
            "type": "gauge",
            "value": value,
            "labels": full_labels
        }
        
        logger.debug(f"仪表盘 {name} 设置为 {value}")
        
        # 实际实现中应该直接调用具体客户端
        self._maybe_push_metrics()
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """直方图指标

        Args:
            name: 指标名称
            value: 观察值
            labels: 指标标签
        """
        full_labels = self._merge_labels(labels)
        metric_key = f"{name}:{self._labels_to_key(full_labels)}"
        
        if metric_key not in self.client["metrics"]:
            self.client["metrics"][metric_key] = {
                "name": name,
                "type": "histogram",
                "values": [],
                "count": 0,
                "sum": 0,
                "labels": full_labels
            }
        
        self.client["metrics"][metric_key]["values"].append(value)
        self.client["metrics"][metric_key]["count"] += 1
        self.client["metrics"][metric_key]["sum"] += value
        
        logger.debug(f"直方图 {name} 添加观察值 {value}")
        
        # 实际实现中应该直接调用具体客户端
        self._maybe_push_metrics()
    
    def _merge_labels(self, labels: Dict[str, str] = None) -> Dict[str, str]:
        """合并默认标签和自定义标签

        Args:
            labels: 自定义标签
            
        Returns:
            Dict[str, str]: 合并后的标签
        """
        result = {
            "service": "accessibility-service",
            "host": self.hostname
        }
        
        # 添加配置中的默认标签
        if self.default_labels:
            result.update(self.default_labels)
            
        # 添加自定义标签
        if labels:
            result.update(labels)
            
        return result
    
    def _labels_to_key(self, labels: Dict[str, str]) -> str:
        """将标签转换为字符串键

        Args:
            labels: 标签字典
            
        Returns:
            str: 标签键
        """
        if not labels:
            return ""
            
        parts = []
        for k, v in sorted(labels.items()):
            parts.append(f"{k}={v}")
            
        return ",".join(parts)
    
    def _maybe_push_metrics(self):
        """根据需要推送指标"""
        # 只在内存模式下进行周期性推送
        if self.client["type"] != "memory":
            return
            
        now = time.time()
        if now - self.client.get("last_report", 0) > self.interval_seconds:
            self._push_metrics()
            self.client["last_report"] = now
    
    def _push_metrics(self):
        """推送指标到远程服务器"""
        if self.client["type"] == "prometheus" and self.push_gateway:
            logger.info(f"推送指标到Prometheus Push Gateway: {self.push_gateway}")
            # 实际实现中应该调用push_to_gateway
        elif self.client["type"] == "datadog":
            logger.info("推送指标到Datadog")
            # 实际实现中应该调用datadog.api.Metric.send
        elif self.client["type"] == "memory":
            logger.debug(f"内存指标状态: {len(self.client['metrics'])} 个指标")
            # 实际实现中可能会输出到日志或控制台


class TracingClient:
    """追踪客户端 - 负责分布式追踪"""
    
    def __init__(self, config):
        """初始化追踪客户端

        Args:
            config: 配置对象
        """
        self.config = config
        self.provider = config.observability.tracing.provider
        self.endpoint = config.observability.tracing.endpoint
        self.service_name = config.observability.tracing.service_name
        self.sample_rate = config.observability.tracing.sample_rate
        self.tracer = None
        
        logger.info(f"初始化追踪客户端，提供者: {self.provider}")
        self._initialize_tracer()
        
    def _initialize_tracer(self):
        """初始化追踪器"""
        try:
            if self.provider == "opentelemetry":
                self._init_opentelemetry_tracer()
            elif self.provider == "jaeger":
                self._init_jaeger_tracer()
            elif self.provider == "memory":
                self._init_memory_tracer()
            else:
                logger.warning(f"不支持的追踪提供者: {self.provider}")
                self._init_memory_tracer()
        except Exception as e:
            logger.error(f"初始化追踪器失败: {str(e)}")
            self._init_memory_tracer()
    
    def _init_opentelemetry_tracer(self):
        """初始化OpenTelemetry追踪器"""
        logger.info(f"初始化OpenTelemetry追踪器，端点: {self.endpoint}")
        # 实际实现中应该使用opentelemetry库
        # 这里使用模拟实现
        self.tracer = {
            "type": "opentelemetry",
            "service_name": self.service_name,
            "endpoint": self.endpoint,
            "active_spans": {}
        }
    
    def _init_jaeger_tracer(self):
        """初始化Jaeger追踪器"""
        logger.info(f"初始化Jaeger追踪器，端点: {self.endpoint}")
        # 实际实现中应该使用jaeger-client库
        # 这里使用模拟实现
        self.tracer = {
            "type": "jaeger",
            "service_name": self.service_name,
            "endpoint": self.endpoint,
            "active_spans": {}
        }
    
    def _init_memory_tracer(self):
        """初始化内存追踪器"""
        logger.info("初始化内存追踪器")
        self.tracer = {
            "type": "memory",
            "service_name": self.service_name,
            "active_spans": {},
            "completed_spans": []
        }
    
    def start_span(self, name: str, parent_span_id: str = None, 
                 attributes: Dict[str, Any] = None) -> str:
        """启动一个追踪Span

        Args:
            name: Span名称
            parent_span_id: 父Span ID
            attributes: Span属性
            
        Returns:
            str: 新Span的ID
        """
        import uuid
        
        span_id = str(uuid.uuid4())
        
        # 创建Span
        span = {
            "id": span_id,
            "name": name,
            "parent_id": parent_span_id,
            "start_time": time.time(),
            "end_time": None,
            "attributes": attributes or {},
            "events": [],
            "status": "active"
        }
        
        self.tracer["active_spans"][span_id] = span
        
        logger.debug(f"启动Span: {name} (ID: {span_id})")
        
        return span_id
    
    def end_span(self, span_id: str, attributes: Dict[str, Any] = None):
        """结束一个追踪Span

        Args:
            span_id: Span ID
            attributes: 要添加的属性
        """
        if span_id not in self.tracer["active_spans"]:
            logger.warning(f"尝试结束不存在的Span: {span_id}")
            return
            
        span = self.tracer["active_spans"][span_id]
        span["end_time"] = time.time()
        span["status"] = "completed"
        
        # 添加属性
        if attributes:
            span["attributes"].update(attributes)
            
        logger.debug(f"结束Span: {span['name']} (ID: {span_id})")
        
        # 从活动Span中移除
        del self.tracer["active_spans"][span_id]
        
        # 对于内存追踪器，保存已完成的Span
        if self.tracer["type"] == "memory":
            self.tracer["completed_spans"].append(span)
            
        # 实际实现中应该根据具体的追踪库结束Span
    
    def add_event(self, span_id: str, name: str, attributes: Dict[str, Any] = None):
        """向Span添加事件

        Args:
            span_id: Span ID
            name: 事件名称
            attributes: 事件属性
        """
        if span_id not in self.tracer["active_spans"]:
            logger.warning(f"尝试向不存在的Span添加事件: {span_id}")
            return
            
        span = self.tracer["active_spans"][span_id]
        
        event = {
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        }
        
        span["events"].append(event)
        
        logger.debug(f"向Span {span['name']} 添加事件: {name}")
        
        # 实际实现中应该根据具体的追踪库添加事件
    
    def set_span_status(self, span_id: str, status: str, description: str = None):
        """设置Span状态

        Args:
            span_id: Span ID
            status: 状态 (ok/error)
            description: 状态描述
        """
        if span_id not in self.tracer["active_spans"]:
            logger.warning(f"尝试设置不存在的Span状态: {span_id}")
            return
            
        span = self.tracer["active_spans"][span_id]
        
        span["status"] = status
        if description:
            span["status_description"] = description
            
        logger.debug(f"设置Span {span['name']} 状态: {status}")
        
        # 实际实现中应该根据具体的追踪库设置状态


class LoggingClient:
    """日志客户端 - 负责结构化日志处理"""
    
    def __init__(self, config):
        """初始化日志客户端

        Args:
            config: 配置对象
        """
        self.config = config
        self.provider = config.observability.logging.provider
        self.forward_address = config.observability.logging.forward_address
        self.structured = config.observability.logging.structured
        self.client = None
        
        logger.info(f"初始化日志客户端，提供者: {self.provider}")
        self._initialize_client()
        
    def _initialize_client(self):
        """初始化日志客户端"""
        try:
            if self.provider == "fluent-bit":
                self._init_fluentbit_client()
            elif self.provider == "elasticsearch":
                self._init_elasticsearch_client()
            elif self.provider == "stdout":
                self._init_stdout_client()
            else:
                logger.warning(f"不支持的日志提供者: {self.provider}")
                self._init_stdout_client()
        except Exception as e:
            logger.error(f"初始化日志客户端失败: {str(e)}")
            self._init_stdout_client()
    
    def _init_fluentbit_client(self):
        """初始化Fluent Bit客户端"""
        logger.info(f"初始化Fluent Bit客户端，地址: {self.forward_address}")
        # 实际实现中应该使用fluent-logger库
        # 这里使用模拟实现
        self.client = {
            "type": "fluent-bit",
            "address": self.forward_address
        }
        
        # 配置记录器以便将日志转发到Fluent Bit
        self._configure_logging_handler()
    
    def _init_elasticsearch_client(self):
        """初始化Elasticsearch客户端"""
        logger.info(f"初始化Elasticsearch日志客户端，地址: {self.forward_address}")
        # 实际实现中应该使用elasticsearch库
        # 这里使用模拟实现
        self.client = {
            "type": "elasticsearch",
            "address": self.forward_address
        }
        
        # 配置记录器以便将日志转发到Elasticsearch
        self._configure_logging_handler()
    
    def _init_stdout_client(self):
        """初始化标准输出客户端"""
        logger.info("初始化标准输出日志客户端")
        self.client = {
            "type": "stdout"
        }
        
        # 配置记录器以便将结构化日志输出到标准输出
        self._configure_logging_handler()
    
    def _configure_logging_handler(self):
        """配置日志处理器"""
        # 实际实现中应该根据具体的日志提供者配置处理器
        # 这里仅做模拟
        pass
    
    def log(self, level: str, message: str, context: Dict[str, Any] = None):
        """记录结构化日志

        Args:
            level: 日志级别
            message: 日志消息
            context: 上下文数据
        """
        # 创建结构化日志记录
        log_record = {
            "message": message,
            "level": level,
            "timestamp": time.time(),
            "service": "accessibility-service",
            "host": socket.gethostname()
        }
        
        # 添加上下文
        if context:
            log_record["context"] = context
            
        # 根据提供者发送日志
        if self.client["type"] == "fluent-bit":
            # 实际实现中应该调用fluent-logger
            pass
        elif self.client["type"] == "elasticsearch":
            # 实际实现中应该调用elasticsearch客户端
            pass
        elif self.client["type"] == "stdout":
            # 输出到标准日志
            if level == "debug":
                logger.debug(message, extra={"context": context})
            elif level == "info":
                logger.info(message, extra={"context": context})
            elif level == "warning":
                logger.warning(message, extra={"context": context})
            elif level == "error":
                logger.error(message, extra={"context": context})
            elif level == "critical":
                logger.critical(message, extra={"context": context})
    
    def debug(self, message: str, context: Dict[str, Any] = None):
        """记录调试日志

        Args:
            message: 日志消息
            context: 上下文数据
        """
        self.log("debug", message, context)
    
    def info(self, message: str, context: Dict[str, Any] = None):
        """记录信息日志

        Args:
            message: 日志消息
            context: 上下文数据
        """
        self.log("info", message, context)
    
    def warning(self, message: str, context: Dict[str, Any] = None):
        """记录警告日志

        Args:
            message: 日志消息
            context: 上下文数据
        """
        self.log("warning", message, context)
    
    def error(self, message: str, context: Dict[str, Any] = None):
        """记录错误日志

        Args:
            message: 日志消息
            context: 上下文数据
        """
        self.log("error", message, context)
    
    def critical(self, message: str, context: Dict[str, Any] = None):
        """记录严重错误日志

        Args:
            message: 日志消息
            context: 上下文数据
        """
        self.log("critical", message, context)


class MonitoringService:
    """监控服务 - 整合指标、追踪和日志"""
    
    def __init__(self, config):
        """初始化监控服务

        Args:
            config: 配置对象
        """
        self.config = config
        logger.info("初始化监控服务")
        
        # 初始化各个客户端
        self.metrics_client = self._initialize_metrics_client()
        self.tracing_client = self._initialize_tracing_client()
        self.logging_client = self._initialize_logging_client()
        
    def _initialize_metrics_client(self) -> MetricsClient:
        """初始化指标客户端

        Returns:
            MetricsClient: 指标客户端
        """
        try:
            return MetricsClient(self.config)
        except Exception as e:
            logger.error(f"初始化指标客户端失败: {str(e)}")
            # 如果出错，创建一个默认配置的客户端
            return self._create_default_metrics_client()
    
    def _create_default_metrics_client(self) -> MetricsClient:
        """创建默认配置的指标客户端

        Returns:
            MetricsClient: 默认指标客户端
        """
        # 创建一个具有内存提供者的默认客户端
        class DefaultConfig:
            class observability:
                class metrics:
                    provider = "memory"
                    endpoint = "/metrics"
                    push_gateway = None
                    interval_seconds = 60
                    labels = {
                        "service": "accessibility-service",
                        "environment": "development"
                    }
        
        return MetricsClient(DefaultConfig())
    
    def _initialize_tracing_client(self) -> TracingClient:
        """初始化追踪客户端

        Returns:
            TracingClient: 追踪客户端
        """
        try:
            return TracingClient(self.config)
        except Exception as e:
            logger.error(f"初始化追踪客户端失败: {str(e)}")
            # 如果出错，创建一个默认配置的客户端
            return self._create_default_tracing_client()
    
    def _create_default_tracing_client(self) -> TracingClient:
        """创建默认配置的追踪客户端

        Returns:
            TracingClient: 默认追踪客户端
        """
        # 创建一个具有内存提供者的默认客户端
        class DefaultConfig:
            class observability:
                class tracing:
                    provider = "memory"
                    endpoint = None
                    service_name = "accessibility-service"
                    sample_rate = 0.1
        
        return TracingClient(DefaultConfig())
    
    def _initialize_logging_client(self) -> LoggingClient:
        """初始化日志客户端

        Returns:
            LoggingClient: 日志客户端
        """
        try:
            return LoggingClient(self.config)
        except Exception as e:
            logger.error(f"初始化日志客户端失败: {str(e)}")
            # 如果出错，创建一个默认配置的客户端
            return self._create_default_logging_client()
    
    def _create_default_logging_client(self) -> LoggingClient:
        """创建默认配置的日志客户端

        Returns:
            LoggingClient: 默认日志客户端
        """
        # 创建一个具有标准输出提供者的默认客户端
        class DefaultConfig:
            class observability:
                class logging:
                    provider = "stdout"
                    forward_address = None
                    structured = True
        
        return LoggingClient(DefaultConfig())
    
    def setup(self):
        """配置和启动监控服务"""
        logger.info("启动监控服务")
        
        # 注册公共指标
        self._register_common_metrics()
        
        # 配置告警规则
        self._setup_alerting()
        
        # 初始化服务级别追踪
        self._setup_service_tracing()
    
    def _register_common_metrics(self):
        """注册公共指标"""
        # 服务启动时间
        self.metrics_client.gauge("accessibility_service_start_time", time.time())
        
        # 服务版本
        version = getattr(self.config.service, "version", "unknown")
        self.metrics_client.gauge("accessibility_service_info", 1, {"version": version})
    
    def _setup_alerting(self):
        """配置告警规则"""
        # 实际实现中应该配置Prometheus Alertmanager或其他告警系统
        # 这里仅做模拟
        logger.info("配置监控告警规则")
    
    def _setup_service_tracing(self):
        """配置服务级别追踪"""
        # 创建服务根追踪Span
        self.service_span_id = self.tracing_client.start_span(
            "accessibility_service",
            attributes={
                "service.name": "accessibility-service",
                "service.version": getattr(self.config.service, "version", "unknown")
            }
        )
        
        logger.info(f"初始化服务根追踪Span: {self.service_span_id}")
    
    def record_request_metrics(self, service: str, method: str, duration_ms: float, status: str):
        """记录请求指标

        Args:
            service: 服务名称
            method: 方法名称
            duration_ms: 持续时间(毫秒)
            status: 状态(success/error)
        """
        # 请求计数器
        self.metrics_client.counter(
            "accessibility_request_count",
            1,
            {"service": service, "method": method, "status": status}
        )
        
        # 请求延迟直方图
        self.metrics_client.histogram(
            "accessibility_request_duration_ms",
            duration_ms,
            {"service": service, "method": method, "status": status}
        )
        
        # 如果是错误，增加错误计数器
        if status == "error":
            self.metrics_client.counter(
                "accessibility_request_error_count",
                1,
                {"service": service, "method": method}
            )
    
    def record_model_inference_metrics(self, model: str, input_size: int, 
                                    duration_ms: float, status: str):
        """记录模型推理指标

        Args:
            model: 模型名称
            input_size: 输入大小(字节)
            duration_ms: 持续时间(毫秒)
            status: 状态(success/error)
        """
        # 推理计数器
        self.metrics_client.counter(
            "accessibility_model_inference_count",
            1,
            {"model": model, "status": status}
        )
        
        # 推理延迟直方图
        self.metrics_client.histogram(
            "accessibility_model_inference_duration_ms",
            duration_ms,
            {"model": model, "status": status}
        )
        
        # 输入大小
        self.metrics_client.histogram(
            "accessibility_model_input_size_bytes",
            input_size,
            {"model": model}
        )
        
        # 如果是错误，增加错误计数器
        if status == "error":
            self.metrics_client.counter(
                "accessibility_model_inference_error_count",
                1,
                {"model": model}
            )
    
    def record_accessibility_usage(self, feature: str, user_type: str):
        """记录无障碍功能使用情况

        Args:
            feature: 功能名称
            user_type: 用户类型
        """
        self.metrics_client.counter(
            "accessibility_feature_usage",
            1,
            {"feature": feature, "user_type": user_type}
        )
    
    def trace_request(self, service: str, method: str) -> str:
        """追踪请求

        Args:
            service: 服务名称
            method: 方法名称
            
        Returns:
            str: Span ID
        """
        return self.tracing_client.start_span(
            f"{service}.{method}",
            parent_span_id=self.service_span_id,
            attributes={
                "service": service,
                "method": method,
                "start_time": time.time()
            }
        )
    
    def end_trace(self, span_id: str, status: str = "ok", 
                error: Exception = None, attributes: Dict[str, Any] = None):
        """结束追踪

        Args:
            span_id: Span ID
            status: 状态
            error: 错误对象
            attributes: 附加属性
        """
        # 合并属性
        all_attributes = attributes or {}
        
        if error:
            self.tracing_client.set_span_status(span_id, "error", str(error))
            all_attributes["error.message"] = str(error)
            all_attributes["error.type"] = type(error).__name__
        else:
            self.tracing_client.set_span_status(span_id, status)
            
        # 添加结束时间属性
        all_attributes["end_time"] = time.time()
        
        # 结束Span
        self.tracing_client.end_span(span_id, all_attributes)
    
    def log_structured(self, level: str, message: str, context: Dict[str, Any] = None,
                     span_id: str = None):
        """记录结构化日志

        Args:
            level: 日志级别
            message: 日志消息
            context: 上下文数据
            span_id: 关联的Span ID
        """
        # 创建完整上下文
        full_context = context or {}
        
        # 添加追踪上下文
        if span_id and span_id in self.tracing_client.tracer.get("active_spans", {}):
            full_context["trace"] = {
                "span_id": span_id,
                "trace_id": self.service_span_id
            }
            
        # 记录日志
        self.logging_client.log(level, message, full_context) 