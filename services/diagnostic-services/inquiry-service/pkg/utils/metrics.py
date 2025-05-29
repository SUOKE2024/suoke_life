#!/usr/bin/env python

"""
度量收集器模块，负责收集和暴露服务指标
"""

import logging
import threading
import time
from typing import Any

from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server

logger = logging.getLogger(__name__)


class MetricsCollector:
    """度量收集器类，负责收集和暴露服务指标"""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/metrics",
        config: dict[str, Any] = None,
    ):
        """
        初始化度量收集器

        Args:
            host: 监听主机
            port: 监听端口
            path: 指标路径
            config: 配置信息
        """
        self.host = host
        self.port = port
        self.path = path
        self.config = config or {}

        # 是否已启动
        self.started = False

        # 初始化指标
        self._init_metrics()

        logger.info("度量收集器初始化完成")

    def _init_metrics(self):
        """初始化指标"""
        # 基本请求指标
        self.request_counter = Counter(
            "inquiry_service_requests_total", "问诊服务请求总数", ["method", "status"]
        )

        self.request_latency = Histogram(
            "inquiry_service_request_latency_seconds",
            "问诊服务请求延迟（秒）",
            ["method"],
            buckets=(0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0),
        )

        # 会话指标
        self.active_sessions = Gauge(
            "inquiry_service_active_sessions", "问诊服务当前活跃会话数"
        )

        self.session_duration = Histogram(
            "inquiry_service_session_duration_seconds",
            "问诊会话持续时间（秒）",
            buckets=(60, 300, 600, 1200, 1800, 3600, 7200),
        )

        # LLM响应指标
        self.llm_response_time = Histogram(
            "inquiry_service_llm_response_time_seconds",
            "LLM响应时间（秒）",
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0),
        )

        self.llm_tokens_input = Counter(
            "inquiry_service_llm_tokens_input_total", "LLM输入Token总数"
        )

        self.llm_tokens_output = Counter(
            "inquiry_service_llm_tokens_output_total", "LLM输出Token总数"
        )

        # 症状提取指标
        self.symptom_extraction_count = Counter(
            "inquiry_service_symptom_extraction_total", "症状提取次数"
        )

        self.symptoms_per_extraction = Histogram(
            "inquiry_service_symptoms_per_extraction",
            "每次提取的症状数量",
            buckets=(1, 2, 3, 5, 10, 15, 20),
        )

        self.symptom_extraction_accuracy = Gauge(
            "inquiry_service_symptom_extraction_accuracy", "症状提取准确率"
        )

        # TCM证型指标
        self.tcm_pattern_match_count = Counter(
            "inquiry_service_tcm_pattern_match_total", "TCM证型匹配次数"
        )

        self.tcm_pattern_match_confidence = Histogram(
            "inquiry_service_tcm_pattern_match_confidence",
            "TCM证型匹配置信度",
            buckets=(0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98),
        )

        # 健康风险评估指标
        self.health_risk_assessment_count = Counter(
            "inquiry_service_health_risk_assessment_total", "健康风险评估次数"
        )

        self.health_risks_per_assessment = Histogram(
            "inquiry_service_health_risks_per_assessment",
            "每次评估的健康风险数量",
            buckets=(1, 2, 3, 5, 8, 10),
        )

        # 系统指标
        self.system_memory_usage = Gauge(
            "inquiry_service_system_memory_usage_bytes", "问诊服务内存使用量（字节）"
        )

        self.system_cpu_usage = Gauge(
            "inquiry_service_system_cpu_usage_percent", "问诊服务CPU使用率（百分比）"
        )

        # 自定义指标
        self.custom_metrics = {}
        self._create_custom_metrics()

    def _create_custom_metrics(self):
        """创建自定义指标"""
        custom_metrics = self.config.get("custom_metrics", [])

        for metric in custom_metrics:
            name = metric.get("name")
            help_text = metric.get("help", f"Custom metric: {name}")
            metric_type = metric.get("type", "gauge")

            if not name:
                logger.warning("跳过未命名的自定义指标")
                continue

            # 指标名称标准化
            metric_name = f"inquiry_service_{name}"

            # 创建指标
            if metric_type.lower() == "counter":
                self.custom_metrics[name] = Counter(metric_name, help_text)
            elif metric_type.lower() == "gauge":
                self.custom_metrics[name] = Gauge(metric_name, help_text)
            elif metric_type.lower() == "histogram":
                buckets = metric.get("buckets", (0.1, 0.5, 1.0, 2.0, 5.0, 10.0))
                self.custom_metrics[name] = Histogram(
                    metric_name, help_text, buckets=buckets
                )
            elif metric_type.lower() == "summary":
                self.custom_metrics[name] = Summary(metric_name, help_text)
            else:
                logger.warning(f"未知的指标类型: {metric_type}, 默认使用Gauge")
                self.custom_metrics[name] = Gauge(metric_name, help_text)

            logger.info(f"已创建自定义指标: {name} ({metric_type})")

    def start(self):
        """启动度量收集器"""
        if self.started:
            logger.warning("度量收集器已经启动")
            return

        try:
            # 启动Prometheus HTTP服务器
            start_http_server(self.port, self.host)
            self.started = True
            logger.info(f"度量收集器已启动: http://{self.host}:{self.port}{self.path}")

            # 启动系统指标收集线程
            if self.config.get("collect_system_metrics", True):
                threading.Thread(
                    target=self._collect_system_metrics, daemon=True
                ).start()

        except Exception as e:
            logger.error(f"启动度量收集器失败: {e!s}")

    def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil
        except ImportError:
            logger.warning("未安装psutil，无法收集系统指标")
            return

        interval = self.config.get("collection_interval_seconds", 15)

        while True:
            try:
                # 收集进程内存使用情况
                process = psutil.Process()
                memory_info = process.memory_info()
                self.system_memory_usage.set(memory_info.rss)

                # 收集CPU使用情况
                cpu_percent = process.cpu_percent(interval=0.1)
                self.system_cpu_usage.set(cpu_percent)

            except Exception as e:
                logger.error(f"收集系统指标失败: {e!s}")

            # 等待下一个收集周期
            time.sleep(interval)

    def record_request(self, method: str, status: str, latency: float):
        """
        记录请求指标

        Args:
            method: 请求方法
            status: 请求状态
            latency: 请求延迟（秒）
        """
        self.request_counter.labels(method, status).inc()
        self.request_latency.labels(method).observe(latency)

    def set_active_sessions(self, count: int):
        """
        设置活跃会话数

        Args:
            count: 活跃会话数
        """
        self.active_sessions.set(count)

    def record_session_duration(self, duration: float):
        """
        记录会话持续时间

        Args:
            duration: 会话持续时间（秒）
        """
        self.session_duration.observe(duration)

    def record_llm_response(
        self, response_time: float, input_tokens: int, output_tokens: int
    ):
        """
        记录LLM响应指标

        Args:
            response_time: 响应时间（秒）
            input_tokens: 输入Token数
            output_tokens: 输出Token数
        """
        self.llm_response_time.observe(response_time)
        self.llm_tokens_input.inc(input_tokens)
        self.llm_tokens_output.inc(output_tokens)

    def record_symptom_extraction(self, symptom_count: int, accuracy: float = None):
        """
        记录症状提取指标

        Args:
            symptom_count: 提取的症状数量
            accuracy: 提取准确率
        """
        self.symptom_extraction_count.inc()
        self.symptoms_per_extraction.observe(symptom_count)

        if accuracy is not None:
            self.symptom_extraction_accuracy.set(accuracy)

    def record_tcm_pattern_match(self, confidence: float):
        """
        记录TCM证型匹配指标

        Args:
            confidence: 匹配置信度
        """
        self.tcm_pattern_match_count.inc()
        self.tcm_pattern_match_confidence.observe(confidence)

    def record_health_risk_assessment(self, risk_count: int):
        """
        记录健康风险评估指标

        Args:
            risk_count: 风险数量
        """
        self.health_risk_assessment_count.inc()
        self.health_risks_per_assessment.observe(risk_count)

    def record_custom_metric(self, name: str, value: float, increment: bool = False):
        """
        记录自定义指标

        Args:
            name: 指标名称
            value: 指标值
            increment: 是否增加计数器
        """
        if name not in self.custom_metrics:
            logger.warning(f"未定义的自定义指标: {name}")
            return

        metric = self.custom_metrics[name]

        if isinstance(metric, Counter):
            metric.inc(value)
        elif isinstance(metric, Gauge):
            metric.set(value)
        elif isinstance(metric, Histogram) or isinstance(metric, Summary):
            metric.observe(value)
        else:
            # 默认按Gauge处理
            metric.set(value)
