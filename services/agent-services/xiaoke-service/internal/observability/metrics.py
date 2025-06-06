"""
metrics - 索克生活项目模块
"""

    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary
    from prometheus_client.exposition import pushadd_to_gateway
from functools import wraps
from threading import Lock
import logging
import os
import time

#!/usr/bin/env python

"""
小克服务指标采集模块
"""


# 尝试导入Prometheus客户端库，如果不可用则使用dummy实现
try:

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus客户端库未安装，将使用空实现")

    # 创建空类，使得代码能够继续运行，即使没有安装Prometheus
    class DummyMetric:
        """空指标类"""

        def __init__(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

        def inc(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

    # 模拟Prometheus客户端接口
    Counter = DummyMetric
    Histogram = DummyMetric
    Gauge = DummyMetric
    Summary = DummyMetric

    class CollectorRegistry:
        """模拟注册表"""

        def __init__(self, *args, **kwargs):
            pass

    def pushadd_to_gateway(*args, **kwargs):
        pass

logger = logging.getLogger(__name__)

class MetricsCollector:
    """服务指标收集器"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """单例模式，确保只有一个指标收集器实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化指标收集器"""
        if self._initialized:
            return

        # 创建指标注册表
        self.registry = CollectorRegistry()

        # 创建服务基础指标
        self.service_info = Gauge(
            "xiaoke_service_info", "小克服务信息", ["version"], registry=self.registry
        )

        # 创建请求计数器
        self.request_counter = Counter(
            "xiaoke_requests_total",
            "处理的请求总数",
            ["endpoint", "status"],
            registry=self.registry,
        )

        # 创建请求延迟直方图
        self.request_latency = Histogram(
            "xiaoke_request_latency_seconds",
            "请求延迟（秒）",
            ["endpoint"],
            registry=self.registry,
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
        )

        # 创建依赖健康状态指标
        self.dependency_status = Gauge(
            "xiaoke_dependency_status",
            "依赖服务健康状态",
            ["name"],
            registry=self.registry,
        )

        # 创建资源指标
        self.resource_gauge = Gauge(
            "xiaoke_resources", "资源状态", ["type"], registry=self.registry
        )

        # 创建产品推荐指标
        self.product_recommendations = Counter(
            "xiaoke_product_recommendations_total",
            "产品推荐总数",
            ["constitution_type", "category"],
            registry=self.registry,
        )

        # 创建支付交易指标
        self.payment_counter = Counter(
            "xiaoke_payments_total",
            "支付交易总数",
            ["payment_method", "status"],
            registry=self.registry,
        )

        # 创建ERP调用指标
        self.erp_api_calls = Counter(
            "xiaoke_erp_api_calls_total",
            "ERP API调用总数",
            ["endpoint", "status"],
            registry=self.registry,
        )

        # 创建ERP调用延迟指标
        self.erp_api_latency = Histogram(
            "xiaoke_erp_api_latency_seconds",
            "ERP API调用延迟（秒）",
            ["endpoint"],
            registry=self.registry,
            buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
        )

        # 创建数据库操作指标
        self.db_operations = Counter(
            "xiaoke_db_operations_total",
            "数据库操作总数",
            ["database", "operation", "status"],
            registry=self.registry,
        )

        # 创建数据库操作延迟指标
        self.db_operation_latency = Histogram(
            "xiaoke_db_operation_latency_seconds",
            "数据库操作延迟（秒）",
            ["database", "operation"],
            registry=self.registry,
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5),
        )

        # 设置服务信息
        version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.service_info.labels(version=version).set(1)

        # Push Gateway配置
        self.push_gateway_url = os.getenv("PROMETHEUS_PUSH_GATEWAY", "")
        self.push_job_name = os.getenv("PROMETHEUS_JOB_NAME", "xiaoke_service")
        self.push_interval = int(os.getenv("PROMETHEUS_PUSH_INTERVAL", "15"))

        # 设置初始化标志
        self._initialized = True

        logger.info("指标收集器已初始化")

    def record_request(self, endpoint, status="success", latency=None):
        """记录请求指标"""
        self.request_counter.labels(endpoint=endpoint, status=status).inc()
        if latency is not None:
            self.request_latency.labels(endpoint=endpoint).observe(latency)

    def set_dependency_status(self, name, status):
        """设置依赖健康状态"""
        self.dependency_status.labels(name=name).set(1 if status == "OK" else 0)

    def record_resource_count(self, resource_type, count):
        """记录资源数量"""
        self.resource_gauge.labels(type=resource_type).set(count)

    def record_product_recommendation(self, constitution_type, category):
        """记录产品推荐"""
        self.product_recommendations.labels(
            constitution_type=constitution_type, category=category
        ).inc()

    def record_payment(self, payment_method, status):
        """记录支付交易"""
        self.payment_counter.labels(payment_method=payment_method, status=status).inc()

    def record_erp_api_call(self, endpoint, status, latency=None):
        """记录ERP API调用"""
        self.erp_api_calls.labels(endpoint=endpoint, status=status).inc()
        if latency is not None:
            self.erp_api_latency.labels(endpoint=endpoint).observe(latency)

    def record_db_operation(self, database, operation, status, latency=None):
        """记录数据库操作"""
        self.db_operations.labels(
            database=database, operation=operation, status=status
        ).inc()
        if latency is not None:
            self.db_operation_latency.labels(
                database=database, operation=operation
            ).observe(latency)

    def push_to_gateway(self):
        """将指标推送到Prometheus Push Gateway"""
        if not PROMETHEUS_AVAILABLE or not self.push_gateway_url:
            return

        try:
            pushadd_to_gateway(
                gateway=self.push_gateway_url,
                job=self.push_job_name,
                registry=self.registry,
            )
            logger.debug(f"指标已推送到 {self.push_gateway_url}")
        except Exception as e:
            logger.error(f"推送指标失败: {e!s}", exc_info=True)

# 装饰器：测量方法执行时间并记录指标
def measure_time(endpoint_name):
    """测量方法执行时间并记录指标的装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = MetricsCollector()
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "failure"
                raise
            finally:
                latency = time.time() - start_time
                metrics.record_request(endpoint_name, status=status, latency=latency)

        return wrapper

    return decorator

# 导出单例实例以便全局使用
metrics = MetricsCollector()
