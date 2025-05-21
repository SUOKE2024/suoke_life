#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标收集工具
用于收集服务运行指标，支持Prometheus集成
"""

import time
import logging
import functools
from typing import Dict, Any, Optional, Callable, List

try:
    import prometheus_client as prom
    from prometheus_client import Counter, Gauge, Histogram, Summary
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    logging.warning("未安装prometheus_client，将使用简易指标收集")

from .config_loader import get_config

logger = logging.getLogger(__name__)

class MetricsCollector:
    """指标收集器，用于监控服务运行情况"""
    
    def __init__(self):
        """初始化指标收集器"""
        config = get_config()
        
        # 获取基本指标配置
        self.metrics_prefix = config.get("service.name", "xiaoai_service")
        self.is_enabled = config.get_nested("monitoring", "prometheus", "enabled", default=True)
        self.metrics_port = config.get_nested("monitoring", "prometheus", "port", default=51053)
        
        # 存储已创建的指标
        self._metrics: Dict[str, Any] = {}
        
        # 服务基本信息
        self.service_info = prom.Info(
            f"{self.metrics_prefix}_info",
            "XiaoAI服务基本信息"
        )
        self.service_info.info({
            'version': config.get("service.version", "unknown"),
            'name': config.get("service.name", "xiaoai-service"),
            'description': config.get("service.description", "索克生活APP小艾智能体服务")
        })
        
        # 设置是否使用Prometheus
        self.use_prometheus = HAS_PROMETHEUS
        
        if self.use_prometheus:
            self._init_prometheus_metrics()
        else:
            self._init_simple_metrics()
        
        self.logger.info("指标收集器初始化完成，使用Prometheus: %s", self.use_prometheus)
        
        # 启动指标服务器
        if self.is_enabled:
            try:
                prom.start_http_server(self.metrics_port)
                logger.info(f"Prometheus指标服务器已启动，端口: {self.metrics_port}")
            except Exception as e:
                logger.error(f"启动Prometheus指标服务器失败: {str(e)}")
    
    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        # LLM相关指标
        self._metrics["llm_requests"] = prom.Counter(
            f"{self.metrics_prefix}_llm_requests_total", 
            "大模型请求总数", 
            ["model", "status"]
        )
        self._metrics["llm_latency"] = prom.Histogram(
            f"{self.metrics_prefix}_llm_latency_seconds", 
            "大模型请求延迟",
            ["model"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0)
        )
        self._metrics["llm_token_usage"] = prom.Counter(
            f"{self.metrics_prefix}_llm_token_usage_total", 
            "大模型token使用量",
            ["model", "token_type"]
        )
        
        # 会话相关指标
        self._metrics["active_sessions"] = prom.Gauge(
            f"{self.metrics_prefix}_active_sessions", 
            "当前活跃会话数"
        )
        self._metrics["session_count"] = prom.Counter(
            f"{self.metrics_prefix}_session_count_total", 
            "会话计数",
            ["status"]
        )
        self._metrics["session_duration"] = prom.Histogram(
            f"{self.metrics_prefix}_session_duration_seconds", 
            "会话持续时间",
            buckets=(60, 300, 600, 1800, 3600, 7200, 14400, 28800)
        )
        
        # 消息相关指标
        self._metrics["message_count"] = prom.Counter(
            f"{self.metrics_prefix}_message_count_total", 
            "消息数",
            ["direction", "type"]
        )
        
        # 多模态处理指标
        self._metrics["multimodal_processing"] = prom.Counter(
            f"{self.metrics_prefix}_multimodal_processing_total", 
            "多模态处理次数",
            ["type", "status"]
        )
        self._metrics["multimodal_latency"] = prom.Histogram(
            f"{self.metrics_prefix}_multimodal_latency_seconds", 
            "多模态处理延迟",
            ["type"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
        )
        
        # 错误指标
        self._metrics["errors"] = prom.Counter(
            f"{self.metrics_prefix}_errors_total", 
            "错误数",
            ["component", "error_type"]
        )
        
        # 系统资源指标
        self._metrics["cpu_usage"] = prom.Gauge(
            f"{self.metrics_prefix}_cpu_usage_percent", 
            "CPU使用率"
        )
        self._metrics["memory_usage"] = prom.Gauge(
            f"{self.metrics_prefix}_memory_usage_bytes", 
            "内存使用量"
        )
    
    def _init_simple_metrics(self):
        """初始化简易指标收集（不使用Prometheus）"""
        # 使用字典存储计数器
        self.counters = {
            'llm_requests': {},
            'llm_token_usage': {},
            'session_count': {},
            'message_count': {},
            'multimodal_processing': {},
            'errors': {}
        }
        
        # 使用字典存储仪表盘
        self.gauges = {
            'active_sessions': 0,
            'cpu_usage': 0,
            'memory_usage': 0
        }
        
        # 使用列表存储分布
        self.histograms = {
            'llm_latency': [],
            'session_duration': [],
            'multimodal_latency': []
        }
    
    def track_llm_request(self, model: str, status: str):
        """
        跟踪大模型请求
        
        Args:
            model: 模型名称
            status: 请求状态 (success/failure)
        """
        if self.use_prometheus:
            self._metrics["llm_requests"].labels(model=model, status=status).inc()
        else:
            key = f"{model}:{status}"
            self.counters['llm_requests'][key] = self.counters['llm_requests'].get(key, 0) + 1
    
    def track_llm_latency(self, model: str, latency: float):
        """
        跟踪大模型请求延迟
        
        Args:
            model: 模型名称
            latency: 请求延迟（秒）
        """
        if self.use_prometheus:
            self._metrics["llm_latency"].labels(model=model).observe(latency)
        else:
            self.histograms['llm_latency'].append((model, latency))
    
    def track_llm_token_usage(self, model: str, prompt_tokens: int, completion_tokens: int):
        """
        跟踪大模型token使用量
        
        Args:
            model: 模型名称
            prompt_tokens: 提示token数
            completion_tokens: 补全token数
        """
        if self.use_prometheus:
            self._metrics["llm_token_usage"].labels(model=model, token_type='prompt').inc(prompt_tokens)
            self._metrics["llm_token_usage"].labels(model=model, token_type='completion').inc(completion_tokens)
        else:
            prompt_key = f"{model}:prompt"
            completion_key = f"{model}:completion"
            
            self.counters['llm_token_usage'][prompt_key] = self.counters['llm_token_usage'].get(prompt_key, 0) + prompt_tokens
            self.counters['llm_token_usage'][completion_key] = self.counters['llm_token_usage'].get(completion_key, 0) + completion_tokens
    
    def track_llm_error(self, model: str, error: str):
        """
        跟踪大模型错误
        
        Args:
            model: 模型名称
            error: 错误信息
        """
        if self.use_prometheus:
            self._metrics["errors"].labels(component='llm', error_type=error[:20]).inc()
        else:
            key = f"llm:{error[:20]}"
            self.counters['errors'][key] = self.counters['errors'].get(key, 0) + 1
    
    def update_active_sessions(self, count: int):
        """
        更新活跃会话数
        
        Args:
            count: 活跃会话数
        """
        if self.use_prometheus:
            self._metrics["active_sessions"].set(count)
        else:
            self.gauges['active_sessions'] = count
    
    def increment_session_count(self, status: str):
        """
        增加会话计数
        
        Args:
            status: 会话状态 (started/closed)
        """
        if self.use_prometheus:
            self._metrics["session_count"].labels(status=status).inc()
        else:
            self.counters['session_count'][status] = self.counters['session_count'].get(status, 0) + 1
    
    def record_session_duration(self, duration: float):
        """
        记录会话持续时间
        
        Args:
            duration: 会话持续时间（秒）
        """
        if self.use_prometheus:
            self._metrics["session_duration"].observe(duration)
        else:
            self.histograms['session_duration'].append(duration)
    
    def increment_chat_message_count(self, direction: str, msg_type: str):
        """
        增加聊天消息计数
        
        Args:
            direction: 消息方向 (received/sent)
            msg_type: 消息类型 (text/voice/image/sign)
        """
        if self.use_prometheus:
            self._metrics["message_count"].labels(direction=direction, type=msg_type).inc()
        else:
            key = f"{direction}:{msg_type}"
            self.counters['message_count'][key] = self.counters['message_count'].get(key, 0) + 1
    
    def track_multimodal_process(self, input_type: str, status: str, latency: float, size: int):
        """
        跟踪多模态处理
        
        Args:
            input_type: 输入类型 (voice/image/text/sign)
            status: 处理状态 (success/failure)
            latency: 处理延迟（秒）
            size: 输入数据大小（字节）
        """
        if self.use_prometheus:
            self._metrics["multimodal_processing"].labels(type=input_type, status=status).inc()
            self._metrics["multimodal_latency"].labels(type=input_type).observe(latency)
        else:
            key = f"{input_type}:{status}"
            self.counters['multimodal_processing'][key] = self.counters['multimodal_processing'].get(key, 0) + 1
            self.histograms['multimodal_latency'].append((input_type, latency))
    
    def update_system_metrics(self, cpu_percent: float, memory_bytes: int):
        """
        更新系统资源指标
        
        Args:
            cpu_percent: CPU使用率（百分比）
            memory_bytes: 内存使用量（字节）
        """
        if self.use_prometheus:
            self._metrics["cpu_usage"].set(cpu_percent)
            self._metrics["memory_usage"].set(memory_bytes)
        else:
            self.gauges['cpu_usage'] = cpu_percent
            self.gauges['memory_usage'] = memory_bytes
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        获取指标摘要，仅在非Prometheus模式下有效
        
        Returns:
            Dict[str, Any]: 指标摘要
        """
        if self.use_prometheus:
            return {"message": "使用Prometheus时不提供指标摘要，请使用Prometheus接口"}
        
        return {
            "counters": self.counters,
            "gauges": self.gauges,
            "histograms": {
                "llm_latency": len(self.histograms['llm_latency']),
                "session_duration": len(self.histograms['session_duration']),
                "multimodal_latency": len(self.histograms['multimodal_latency'])
            }
        }

# 创建度量收集器单例
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """
    获取度量收集器的单例实例
    
    Returns:
        MetricsCollector: 度量收集器实例
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

# 装饰器: 用于跟踪API请求
def track_request_metrics(endpoint: str, method: str = "POST"):
    """
    API请求度量跟踪装饰器
    
    Args:
        endpoint: API端点
        method: HTTP方法
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()
    def _init_request_metrics(self):
        """初始化请求相关指标"""
        # 请求计数器
        self._metrics["request_count"] = Counter(
            f"{self.metrics_prefix}_request_count_total",
            "API请求总数",
            ["method", "endpoint", "status"]
        )
        
        # 请求延迟直方图
        self._metrics["request_latency"] = Histogram(
            f"{self.metrics_prefix}_request_latency_seconds",
            "API请求延迟(秒)",
            ["method", "endpoint"],
            buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 20.0, float("inf"))
        )
        
        # 当前活跃请求数
        self._metrics["active_requests"] = Gauge(
            f"{self.metrics_prefix}_active_requests",
            "当前活跃请求数",
            ["endpoint"]
        )
        
        # 请求大小
        self._metrics["request_size"] = Summary(
            f"{self.metrics_prefix}_request_size_bytes",
            "请求大小(字节)",
            ["method", "endpoint"]
        )
        
        # 响应大小
        self._metrics["response_size"] = Summary(
            f"{self.metrics_prefix}_response_size_bytes",
            "响应大小(字节)",
            ["method", "endpoint"]
        )
    
    def _init_multimodal_metrics(self):
        """初始化多模态处理相关指标"""
        # 多模态处理计数
        self._metrics["multimodal_process_count"] = Counter(
            f"{self.metrics_prefix}_multimodal_process_total",
            "多模态处理总数",
            ["input_type", "status"]
        )
        
        # 多模态处理延迟
        self._metrics["multimodal_process_latency"] = Histogram(
            f"{self.metrics_prefix}_multimodal_process_latency_seconds",
            "多模态处理延迟(秒)",
            ["input_type"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float("inf"))
        )
        
        # 多模态输入大小
        self._metrics["multimodal_input_size"] = Summary(
            f"{self.metrics_prefix}_multimodal_input_size_bytes",
            "多模态输入大小(字节)",
            ["input_type"]
        )
    
    def _init_agent_metrics(self):
        """初始化智能体相关指标"""
        # 聊天消息计数
        self._metrics["chat_message_count"] = Counter(
            f"{self.metrics_prefix}_chat_message_total",
            "聊天消息总数",
            ["direction", "type"]  # direction: sent/received, type: text/voice/etc
        )
        
        # 会话计数
        self._metrics["session_count"] = Counter(
            f"{self.metrics_prefix}_session_total",
            "会话总数",
            ["status"]  # status: started/completed/failed
        )
        
        # 当前活跃会话
        self._metrics["active_sessions"] = Gauge(
            f"{self.metrics_prefix}_active_sessions",
            "当前活跃会话数"
        )
        
        # 会话时长
        self._metrics["session_duration"] = Histogram(
            f"{self.metrics_prefix}_session_duration_seconds",
            "会话时长(秒)",
            buckets=(30, 60, 120, 300, 600, 1200, 1800, 3600, float("inf"))
        )
        
        # LLM调用次数
        self._metrics["llm_call_count"] = Counter(
            f"{self.metrics_prefix}_llm_call_total",
            "LLM调用总数",
            ["model", "status", "query_type"]
        )
        
        # LLM调用延迟
        self._metrics["llm_call_latency"] = Histogram(
            f"{self.metrics_prefix}_llm_call_latency_seconds",
            "LLM调用延迟(秒)",
            ["model"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float("inf"))
        )
        
        # LLM输入token数
        self._metrics["llm_input_tokens"] = Summary(
            f"{self.metrics_prefix}_llm_input_tokens",
            "LLM输入token数",
            ["model"]
        )
        
        # LLM输出token数
        self._metrics["llm_output_tokens"] = Summary(
            f"{self.metrics_prefix}_llm_output_tokens",
            "LLM输出token数",
            ["model"]
        )
    
    def _init_integration_metrics(self):
        """初始化服务集成相关指标"""
        # 外部服务调用计数
        self._metrics["service_call_count"] = Counter(
            f"{self.metrics_prefix}_service_call_total",
            "外部服务调用总数",
            ["service", "method", "status"]
        )
        
        # 外部服务调用延迟
        self._metrics["service_call_latency"] = Histogram(
            f"{self.metrics_prefix}_service_call_latency_seconds",
            "外部服务调用延迟(秒)",
            ["service", "method"],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float("inf"))
        )
        
        # 四诊协调计数
        self._metrics["diagnosis_coordination_count"] = Counter(
            f"{self.metrics_prefix}_diagnosis_coordination_total",
            "四诊协调总数",
            ["mode", "status", "included_services"]
        )
        
        # 四诊协调延迟
        self._metrics["diagnosis_coordination_latency"] = Histogram(
            f"{self.metrics_prefix}_diagnosis_coordination_latency_seconds",
            "四诊协调延迟(秒)",
            ["mode"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, float("inf"))
        )
    
    def _init_resource_metrics(self):
        """初始化资源使用相关指标"""
        # 数据库操作计数
        self._metrics["db_operation_count"] = Counter(
            f"{self.metrics_prefix}_db_operation_total",
            "数据库操作总数",
            ["db_type", "operation", "status"]
        )
        
        # 数据库操作延迟
        self._metrics["db_operation_latency"] = Histogram(
            f"{self.metrics_prefix}_db_operation_latency_seconds",
            "数据库操作延迟(秒)",
            ["db_type", "operation"],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, float("inf"))
        )
        
        # 缓存命中率
        self._metrics["cache_hit_ratio"] = Gauge(
            f"{self.metrics_prefix}_cache_hit_ratio",
            "缓存命中率",
            ["cache_type"]
        )
        
        # 缓存操作计数
        self._metrics["cache_operation_count"] = Counter(
            f"{self.metrics_prefix}_cache_operation_total",
            "缓存操作总数",
            ["cache_type", "operation", "status"]
        )
    
    def track_request(self, method: str, endpoint: str, status_code: int, latency: float, 
                     request_size: int = 0, response_size: int = 0):
        """
        记录API请求指标
        
        Args:
            method: HTTP方法
            endpoint: API端点
            status_code: 状态码
            latency: 请求延迟(秒)
            request_size: 请求大小(字节)
            response_size: 响应大小(字节)
        """
        if not self.is_enabled:
            return
        
        status = "success" if 200 <= status_code < 400 else "failure"
        
        # 增加请求计数
        self._metrics["request_count"].labels(method=method, endpoint=endpoint, status=status).inc()
        
        # 记录请求延迟
        self._metrics["request_latency"].labels(method=method, endpoint=endpoint).observe(latency)
        
        # 记录请求大小
        if request_size > 0:
            self._metrics["request_size"].labels(method=method, endpoint=endpoint).observe(request_size)
        
        # 记录响应大小
        if response_size > 0:
            self._metrics["response_size"].labels(method=method, endpoint=endpoint).observe(response_size)
    
    def track_multimodal_process(self, input_type: str, status: str, latency: float, input_size: int = 0):
        """
        记录多模态处理指标
        
        Args:
            input_type: 输入类型 (voice, image, text, sign)
            status: 处理状态 (success, failure)
            latency: 处理延迟(秒)
            input_size: 输入大小(字节)
        """
        if not self.is_enabled:
            return
        
        # 增加处理计数
        self._metrics["multimodal_process_count"].labels(input_type=input_type, status=status).inc()
        
        # 记录处理延迟
        self._metrics["multimodal_process_latency"].labels(input_type=input_type).observe(latency)
        
        # 记录输入大小
        if input_size > 0:
            self._metrics["multimodal_input_size"].labels(input_type=input_type).observe(input_size)
    
    def track_llm_call(self, model: str, status: str, query_type: str, latency: float, 
                      input_tokens: int, output_tokens: int):
        """
        记录LLM调用指标
        
        Args:
            model: 模型名称
            status: 调用状态 (success, failure)
            query_type: 查询类型
            latency: 调用延迟(秒)
            input_tokens: 输入token数
            output_tokens: 输出token数
        """
        if not self.is_enabled:
            return
        
        # 增加调用计数
        self._metrics["llm_call_count"].labels(model=model, status=status, query_type=query_type).inc()
        
        # 记录调用延迟
        self._metrics["llm_call_latency"].labels(model=model).observe(latency)
        
        # 记录token数
        self._metrics["llm_input_tokens"].labels(model=model).observe(input_tokens)
        self._metrics["llm_output_tokens"].labels(model=model).observe(output_tokens)
    
    def track_service_call(self, service: str, method: str, status: str, latency: float):
        """
        记录外部服务调用指标
        
        Args:
            service: 服务名称
            method: 方法名称
            status: 调用状态 (success, failure)
            latency: 调用延迟(秒)
        """
        if not self.is_enabled:
            return
        
        # 增加调用计数
        self._metrics["service_call_count"].labels(service=service, method=method, status=status).inc()
        
        # 记录调用延迟
        self._metrics["service_call_latency"].labels(service=service, method=method).observe(latency)
    
    def track_diagnosis_coordination(self, mode: str, status: str, included_services: str, latency: float):
        """
        记录四诊协调指标
        
        Args:
            mode: 协调模式 (sequential, parallel)
            status: 协调状态 (success, failure)
            included_services: 包含的服务 (looking,listening,inquiry,palpation)
            latency: 协调延迟(秒)
        """
        if not self.is_enabled:
            return
        
        # 增加协调计数
        self._metrics["diagnosis_coordination_count"].labels(
            mode=mode, status=status, included_services=included_services
        ).inc()
        
        # 记录协调延迟
        self._metrics["diagnosis_coordination_latency"].labels(mode=mode).observe(latency)
    
    def track_db_operation(self, db_type: str, operation: str, status: str, latency: float):
        """
        记录数据库操作指标
        
        Args:
            db_type: 数据库类型 (postgres, mongodb, redis)
            operation: 操作类型 (query, insert, update, delete)
            status: 操作状态 (success, failure)
            latency: 操作延迟(秒)
        """
        if not self.is_enabled:
            return
        
        # 增加操作计数
        self._metrics["db_operation_count"].labels(db_type=db_type, operation=operation, status=status).inc()
        
        # 记录操作延迟
        self._metrics["db_operation_latency"].labels(db_type=db_type, operation=operation).observe(latency)
    
    def track_cache_operation(self, cache_type: str, operation: str, status: str, hit: bool = None):
        """
        记录缓存操作指标
        
        Args:
            cache_type: 缓存类型 (redis, local)
            operation: 操作类型 (get, set, delete)
            status: 操作状态 (success, failure)
            hit: 是否命中缓存
        """
        if not self.is_enabled:
            return
        
        # 增加操作计数
        self._metrics["cache_operation_count"].labels(
            cache_type=cache_type, operation=operation, status=status
        ).inc()
    
    def update_cache_hit_ratio(self, cache_type: str, ratio: float):
        """
        更新缓存命中率
        
        Args:
            cache_type: 缓存类型 (redis, local)
            ratio: 命中率 (0.0-1.0)
        """
        if not self.is_enabled:
            return
        
        self._metrics["cache_hit_ratio"].labels(cache_type=cache_type).set(ratio)
    
    def increment_active_requests(self, endpoint: str):
        """
        增加活跃请求计数
        
        Args:
            endpoint: API端点
        """
        if not self.is_enabled:
            return
        
        self._metrics["active_requests"].labels(endpoint=endpoint).inc()
    
    def decrement_active_requests(self, endpoint: str):
        """
        减少活跃请求计数
        
        Args:
            endpoint: API端点
        """
        if not self.is_enabled:
            return
        
        self._metrics["active_requests"].labels(endpoint=endpoint).dec()
    
    def update_active_sessions(self, count: int):
        """
        更新活跃会话数
        
        Args:
            count: 活跃会话数
        """
        if not self.is_enabled:
            return
        
        self._metrics["active_sessions"].set(count)
    
    def record_session_duration(self, duration: float):
        """
        记录会话时长
        
        Args:
            duration: 会话时长(秒)
        """
        if not self.is_enabled:
            return
        
        self._metrics["session_duration"].observe(duration)
    
    def increment_session_count(self, status: str):
        """
        增加会话计数
        
        Args:
            status: 会话状态 (started, completed, failed)
        """
        if not self.is_enabled:
            return
        
        self._metrics["session_count"].labels(status=status).inc()
    
    def increment_chat_message_count(self, direction: str, message_type: str):
        """
        增加聊天消息计数
        
        Args:
            direction: 消息方向 (sent, received)
            message_type: 消息类型 (text, voice, etc)
        """
        if not self.is_enabled:
            return
        
        self._metrics["chat_message_count"].labels(direction=direction, type=message_type).inc()

# 创建度量收集器单例
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """
    获取度量收集器的单例实例
    
    Returns:
        MetricsCollector: 度量收集器实例
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

# 装饰器: 用于跟踪API请求
def track_request_metrics(endpoint: str, method: str = "POST"):
    """
    API请求度量跟踪装饰器
    
    Args:
        endpoint: API端点
        method: HTTP方法
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()
            metrics.increment_active_requests(endpoint)
            
            try:
                result = await func(*args, **kwargs)
                status_code = 200  # 假设成功
                
                # 如果结果是一个响应对象，尝试获取状态码
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                
                request_size = 0
                response_size = 0
                
                # 尝试获取请求大小
                request = kwargs.get('request')
                if request and hasattr(request, 'content_length'):
                    request_size = request.content_length or 0
                
                # 尝试计算响应大小
                if hasattr(result, 'body') and hasattr(result.body, '__len__'):
                    response_size = len(result.body)
                
                latency = time.time() - start_time
                metrics.track_request(method, endpoint, status_code, latency, request_size, response_size)
                
                return result
            except Exception as e:
                latency = time.time() - start_time
                metrics.track_request(method, endpoint, 500, latency)
                raise e
            finally:
                metrics.decrement_active_requests(endpoint)
        
        return wrapper
    
    return decorator

# 装饰器: 用于跟踪LLM调用
def track_llm_metrics(model: str, query_type: str):
    """
    LLM调用度量跟踪装饰器
    
    Args:
        model: 模型名称
        query_type: 查询类型
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # 尝试提取token信息
                input_tokens = 0
                output_tokens = 0
                
                if isinstance(result, dict):
                    # 尝试从不同API返回格式中提取token信息
                    if 'usage' in result:
                        usage = result['usage']
                        input_tokens = usage.get('prompt_tokens', 0)
                        output_tokens = usage.get('completion_tokens', 0)
                    elif 'tokenUsage' in result:
                        token_usage = result['tokenUsage']
                        input_tokens = token_usage.get('inputTokens', 0)
                        output_tokens = token_usage.get('outputTokens', 0)
                
                latency = time.time() - start_time
                metrics.track_llm_call(model, "success", query_type, latency, input_tokens, output_tokens)
                
                return result
            except Exception as e:
                latency = time.time() - start_time
                metrics.track_llm_call(model, "failure", query_type, latency, 0, 0)
                raise e
        
        return wrapper
    
    return decorator

# 装饰器: 用于跟踪外部服务调用
def track_service_call_metrics(service: str, method: str):
    """
    外部服务调用度量跟踪装饰器
    
    Args:
        service: 服务名称
        method: 方法名称
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start_time
                metrics.track_service_call(service, method, "success", latency)
                return result
            except Exception as e:
                latency = time.time() - start_time
                metrics.track_service_call(service, method, "failure", latency)
                raise e
        
        return wrapper
    
    return decorator

# 装饰器: 用于跟踪数据库操作
def track_db_metrics(db_type: str, operation: str):
    """
    数据库操作度量跟踪装饰器
    
    Args:
        db_type: 数据库类型
        operation: 操作类型
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start_time
                metrics.track_db_operation(db_type, operation, "success", latency)
                return result
            except Exception as e:
                latency = time.time() - start_time
                metrics.track_db_operation(db_type, operation, "failure", latency)
                raise e
        
        return wrapper
    
    return decorator 