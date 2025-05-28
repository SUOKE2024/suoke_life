#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标收集器
负责收集和上报服务指标，包括请求量、延迟、错误率等
"""

import time
import logging
import functools
from typing import Dict, Any, Optional, Callable
import threading
import json

from .config_loader import get_config

logger = logging.getLogger(__name__)


class MetricsCollector:
    """指标收集器，负责收集和上报服务指标"""

    _instance = None

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化指标收集器"""
        if self._initialized:
            return

        self.config = get_config()

        # 服务名称
        self.service_name = self.config.get("service.name", "xiaoke-service")

        # 是否启用指标收集
        self.enabled = self.config.get("metrics.enabled", True)

        # 请求计数
        self.request_counts = {}
        self.request_count_lock = threading.Lock()

        # 错误计数
        self.error_counts = {}
        self.error_count_lock = threading.Lock()

        # 延迟数据
        self.latencies = {}
        self.latency_lock = threading.Lock()

        # LLM指标
        self.llm_metrics = {
            "latency": {},
            "tokens": {"prompt": {}, "completion": {}},
            "errors": {},
        }
        self.llm_metrics_lock = threading.Lock()

        # 活跃会话数
        self.active_sessions = 0
        self.active_sessions_lock = threading.Lock()

        # 运行状态
        self.is_running = True

        # 启动指标上报线程
        self._start_reporting_thread()

        self._initialized = True
        logger.info("指标收集器初始化完成")

    def _start_reporting_thread(self):
        """启动指标上报线程"""
        if not self.enabled:
            logger.info("指标收集已禁用，不启动上报线程")
            return

        report_interval = self.config.get(
            "metrics.report_interval", 60
        )  # 默认60秒上报一次

        def _report_metrics():
            while self.is_running:
                try:
                    self._report_metrics()
                except Exception as e:
                    logger.error(f"上报指标失败: {str(e)}")
                time.sleep(report_interval)

        # 启动后台线程
        thread = threading.Thread(target=_report_metrics, daemon=True)
        thread.start()
        logger.info(f"指标上报线程已启动，上报间隔: {report_interval}秒")

    def _report_metrics(self):
        """上报指标到监控系统"""
        # 这里可以实现对接具体的监控系统，如Prometheus、Grafana等
        if not self.enabled:
            return

        # 构建指标数据
        metrics_data = {
            "service": self.service_name,
            "timestamp": int(time.time()),
            "request_counts": dict(self.request_counts),
            "error_counts": dict(self.error_counts),
            "latencies": dict(self.latencies),
            "llm_metrics": dict(self.llm_metrics),
            "active_sessions": self.active_sessions,
        }

        # 暂时只记录日志
        logger.debug(f"服务指标: {json.dumps(metrics_data)}")

        # TODO: 实现实际的指标上报

    def increment_request_count(self, request_type: str = "general"):
        """
        增加请求计数

        Args:
            request_type: 请求类型
        """
        if not self.enabled:
            return

        with self.request_count_lock:
            self.request_counts[request_type] = (
                self.request_counts.get(request_type, 0) + 1
            )

    def increment_error_count(self, error_type: str, error_details: str = None):
        """
        增加错误计数

        Args:
            error_type: 错误类型
            error_details: 错误详情
        """
        if not self.enabled:
            return

        with self.error_count_lock:
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # 记录错误日志
        if error_details:
            logger.error(f"错误 {error_type}: {error_details}")

    def record_latency(self, operation: str, latency: float):
        """
        记录操作延迟

        Args:
            operation: 操作名称
            latency: 延迟时间（秒）
        """
        if not self.enabled:
            return

        with self.latency_lock:
            if operation not in self.latencies:
                self.latencies[operation] = {
                    "count": 0,
                    "total": 0.0,
                    "min": float("inf"),
                    "max": 0.0,
                }

            stats = self.latencies[operation]
            stats["count"] += 1
            stats["total"] += latency
            stats["min"] = min(stats["min"], latency)
            stats["max"] = max(stats["max"], latency)

    def track_llm_latency(self, model: str, latency: float):
        """
        记录LLM请求延迟

        Args:
            model: 模型名称
            latency: 延迟时间（秒）
        """
        if not self.enabled:
            return

        with self.llm_metrics_lock:
            if model not in self.llm_metrics["latency"]:
                self.llm_metrics["latency"][model] = {
                    "count": 0,
                    "total": 0.0,
                    "min": float("inf"),
                    "max": 0.0,
                }

            stats = self.llm_metrics["latency"][model]
            stats["count"] += 1
            stats["total"] += latency
            stats["min"] = min(stats["min"], latency)
            stats["max"] = max(stats["max"], latency)

    def track_llm_token_usage(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ):
        """
        记录LLM令牌使用情况

        Args:
            model: 模型名称
            prompt_tokens: 提示令牌数
            completion_tokens: 完成令牌数
        """
        if not self.enabled:
            return

        with self.llm_metrics_lock:
            # 记录提示令牌
            if model not in self.llm_metrics["tokens"]["prompt"]:
                self.llm_metrics["tokens"]["prompt"][model] = 0
            self.llm_metrics["tokens"]["prompt"][model] += prompt_tokens

            # 记录完成令牌
            if model not in self.llm_metrics["tokens"]["completion"]:
                self.llm_metrics["tokens"]["completion"][model] = 0
            self.llm_metrics["tokens"]["completion"][model] += completion_tokens

    def track_llm_error(self, model: str, error_message: str):
        """
        记录LLM错误

        Args:
            model: 模型名称
            error_message: 错误消息
        """
        if not self.enabled:
            return

        with self.llm_metrics_lock:
            if model not in self.llm_metrics["errors"]:
                self.llm_metrics["errors"][model] = {"count": 0, "messages": []}

            self.llm_metrics["errors"][model]["count"] += 1

            # 只保留最近的10条错误消息
            error_list = self.llm_metrics["errors"][model]["messages"]
            error_list.append({"timestamp": int(time.time()), "message": error_message})

            if len(error_list) > 10:
                error_list.pop(0)

    def update_active_sessions(self, session_count: int):
        """
        更新活跃会话数

        Args:
            session_count: 当前活跃会话数
        """
        if not self.enabled:
            return

        with self.active_sessions_lock:
            self.active_sessions = session_count

    def shutdown(self):
        """关闭指标收集器"""
        self.is_running = False
        logger.info("指标收集器已关闭")


def get_metrics_collector() -> MetricsCollector:
    """
    获取指标收集器实例

    Returns:
        MetricsCollector: 指标收集器实例
    """
    return MetricsCollector()


def track_llm_metrics(model: str = None, query_type: str = None):
    """
    跟踪LLM指标的装饰器

    Args:
        model: 模型名称，如果为None则使用函数内指定的模型
        query_type: 查询类型
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()

            # 确定使用的模型
            actual_model = model
            if not actual_model and "model" in kwargs:
                actual_model = kwargs["model"]

            try:
                # 调用原始函数
                result = await func(*args, **kwargs)

                # 记录延迟
                latency = time.time() - start_time
                operation_name = f"{func.__name__}"
                if query_type:
                    operation_name = f"{operation_name}_{query_type}"

                metrics.record_latency(operation_name, latency)

                # 如果结果包含元数据，尝试记录令牌使用情况
                if isinstance(result, tuple) and len(result) > 1:
                    metadata = result[1]
                    if isinstance(metadata, dict) and "token_count" in metadata:
                        token_data = metadata["token_count"]
                        used_model = metadata.get("model", actual_model)
                        metrics.track_llm_token_usage(
                            used_model,
                            token_data.get("prompt", 0),
                            token_data.get("completion", 0),
                        )

                return result

            except Exception as e:
                # 记录错误
                metrics.increment_error_count("llm_error", str(e))
                if actual_model:
                    metrics.track_llm_error(actual_model, str(e))
                raise

        return wrapper

    return decorator
