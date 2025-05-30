#!/usr/bin/env python3
"""
指标收集器
负责收集和上报服务指标, 包括请求量、延迟、错误率等
"""

import logging
import threading
import time
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)

# 常量定义
MAX_ERROR_HISTORY = 10  # 最大错误历史记录数
MAX_LATENCY_RECORDS = 100  # 最大延迟记录数


class MetricsCollector:
    """指标收集器, 负责收集和上报服务指标"""

    _instance = None

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化指标收集器"""
        if self._initialized:
            return

        # 指标存储
        self.metrics = defaultdict(int)
        self.latency_metrics = defaultdict(list)
        self.error_metrics = defaultdict(list)

        # 线程锁
        self.lock = threading.RLock()

        # 是否启用指标收集
        self.enabled = True

        # 上报线程
        self.report_thread = None

        self._initialized = True

        logger.info("指标收集器初始化完成")

    def start_reporting(self, report_interval: int = 60):
        """启动指标上报线程"""
        if not self.enabled:
            logger.info("指标收集已禁用, 不启动上报线程")
            return

        if self.report_thread and self.report_thread.is_alive():
            logger.warning("指标上报线程已在运行")
            return

        def _report_metrics():
            """上报指标的内部函数"""
            while self.enabled:
                try:
                    self._report_metrics()
                    time.sleep(report_interval)
                except Exception as e:
                    logger.error(f"指标上报失败: {e!s}")
                    time.sleep(report_interval)

        thread = threading.Thread(target=_report_metrics, daemon=True)
        thread.start()
        logger.info(f"指标上报线程已启动, 上报间隔: {report_interval}秒")

    def _report_metrics(self):
        """上报指标到监控系统"""
        # 这里可以实现对接具体的监控系统, 如Prometheus、Grafana等
        if not self.enabled:
            return

        with self.lock:
            # 获取当前指标快照
            metrics_snapshot = dict(self.metrics)
            latency_snapshot = {k: list(v) for k, v in self.latency_metrics.items()}
            error_snapshot = {k: list(v) for k, v in self.error_metrics.items()}

        # 构建指标数据
        {
            "timestamp": int(time.time()),
            "metrics": metrics_snapshot,
            "latency": latency_snapshot,
            "errors": error_snapshot,
        }

        try:
            # 这里应该实现实际的指标上报到监控系统
            pass
        except Exception as e:
            logger.error(f"上报指标到监控系统失败: {e!s}")

    def increment_counter(self, name: str, value: int = 1, tags: dict[str, str] | None = None):
        """增加计数器指标"""
        if not self.enabled:
            return

        metric_key = self._build_metric_key(name, tags)
        with self.lock:
            self.metrics[metric_key] += value

    def record_latency(self, operation: str, latency: float):
        """
        记录延迟指标

        Args:
            operation: 操作名称
            latency: 延迟时间(秒)
        """
        if not self.enabled:
            return

        with self.lock:
            self.latency_metrics[operation].append({
                "timestamp": int(time.time()),
                "latency": latency
            })

            # 保持最近的记录
            if len(self.latency_metrics[operation]) > MAX_LATENCY_RECORDS:
                self.latency_metrics[operation].pop(0)

    def record_ai_latency(self, model: str, latency: float):
        """
        记录AI模型延迟

        Args:
            model: 模型名称
            latency: 延迟时间(秒)
        """
        if not self.enabled:
            return

        with self.lock:
            metric_key = f"ai_latency_{model}"
            self.latency_metrics[metric_key].append({
                "timestamp": int(time.time()),
                "latency": latency,
                "model": model
            })

            # 保持最近的记录
            if len(self.latency_metrics[metric_key]) > MAX_LATENCY_RECORDS:
                self.latency_metrics[metric_key].pop(0)

    def record_error(self, operation: str, error_type: str, error_message: str):
        """记录错误指标"""
        if not self.enabled:
            return

        with self.lock:
            error_key = f"{operation}_{error_type}"
            self.metrics[f"error_{error_key}"] += 1

            # 记录错误详情
            error_list = self.error_metrics[error_key]
            error_list.append({"timestamp": int(time.time()), "message": error_message})

            if len(error_list) > MAX_ERROR_HISTORY:
                error_list.pop(0)

    def get_metrics(self) -> dict[str, Any]:
        """获取所有指标"""
        with self.lock:
            return {
                "counters": dict(self.metrics),
                "latency": {k: list(v) for k, v in self.latency_metrics.items()},
                "errors": {k: list(v) for k, v in self.error_metrics.items()},
            }

    def _build_metric_key(self, name: str, tags: dict[str, str] | None = None) -> str:
        """构建指标键"""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"


def track_ai_performance(model: str | None = None, query_type: str = "general"):
    """
    装饰器: 跟踪AI性能指标

    Args:
        model: 模型名称, 如果为None则使用函数内指定的模型
        query_type: 查询类型
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            if not metrics.enabled:
                return func(*args, **kwargs)

            start_time = time.time()
            operation_name = f"ai_{func.__name__}_{query_type}"

            try:
                result = func(*args, **kwargs)

                # 记录成功指标
                latency = time.time() - start_time
                metrics.increment_counter(f"ai_requests_{query_type}")
                metrics.record_latency(operation_name, latency)

                # 如果结果包含元数据, 尝试记录令牌使用情况
                if isinstance(result, tuple) and len(result) > 1:
                    metadata = result[1]
                    if isinstance(metadata, dict) and "tokens_used" in metadata:
                        metrics.increment_counter(
                            "ai_tokens_used",
                            metadata["tokens_used"],
                            {"model": model or "unknown", "query_type": query_type}
                        )

                return result

            except Exception as e:
                # 记录错误指标
                latency = time.time() - start_time
                metrics.record_error(operation_name, type(e).__name__, str(e))
                metrics.record_latency(operation_name, latency)
                raise

        return wrapper
    return decorator


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器实例"""
    return MetricsCollector()
