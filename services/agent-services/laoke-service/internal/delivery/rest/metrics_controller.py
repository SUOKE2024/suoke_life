"""
metrics_controller - 索克生活项目模块
"""

from fastapi import APIRouter, Response
from pkg.utils.config import Config
from pkg.utils.logger import get_logger
from prometheus_client import (
import os
import psutil
import time

#!/usr/bin/env python

"""
Prometheus指标控制器
"""


    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)


# 创建指标注册表
registry = CollectorRegistry(auto_describe=True)

# 创建指标对象
# 请求计数器
http_requests_total = Counter(
    'http_requests_total',
    '总HTTP请求数',
    ['method', 'endpoint', 'status'],
    registry=registry
)

# 请求延迟直方图
http_request_duration_ms = Histogram(
    'http_request_duration_ms',
    'HTTP请求处理时间(毫秒)',
    ['method', 'endpoint'],
    buckets=(1, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000, 7500, 10000),
    registry=registry
)

# API错误计数器
api_errors_total = Counter(
    'api_errors_total',
    'API错误总数',
    ['endpoint', 'error_type'],
    registry=registry
)

# 系统指标
process_cpu_usage = Gauge(
    'process_cpu_usage',
    '进程CPU使用率百分比',
    registry=registry
)

process_memory_usage = Gauge(
    'process_memory_usage',
    '进程内存使用率百分比',
    registry=registry
)

system_cpu_usage = Gauge(
    'system_cpu_usage',
    '系统CPU使用率百分比',
    registry=registry
)

system_memory_usage = Gauge(
    'system_memory_usage',
    '系统内存使用率百分比',
    registry=registry
)

process_info = Info(
    'process_info',
    '进程信息',
    registry=registry
)

# Agent特有指标
knowledge_search_latency = Histogram(
    'knowledge_search_latency_ms',
    '知识检索延迟(毫秒)',
    buckets=(1, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000),
    registry=registry
)

content_moderation_total = Counter(
    'content_moderation_total',
    '内容审核总次数',
    ['result'],
    registry=registry
)

npc_interaction_total = Counter(
    'npc_interaction_total',
    'NPC交互总次数',
    registry=registry
)

active_learning_paths = Gauge(
    'active_learning_paths',
    '当前活跃的学习路径数',
    registry=registry
)

knowledge_contribution_total = Counter(
    'knowledge_contribution_total',
    '知识贡献总数',
    ['status'],
    registry=registry
)

# 获取配置
config = Config()
logger = get_logger(__name__)

# 创建路由器
router = APIRouter(tags=["指标"])

# 进程信息初始化
process = psutil.Process(os.getpid())
process_info.info({
    'pid': str(process.pid),
    'name': process.name(),
    'username': process.username(),
    'service_name': config.get("service.name", "laoke-service"),
    'service_version': config.get("service.version", "unknown"),
    'start_time': str(int(process.create_time())),
    'python_version': config.get("service.python_version", "unknown")
})

# 最后一次指标更新时间
last_metrics_update = 0


async def update_system_metrics():
    """更新系统指标"""
    global last_metrics_update

    # 限制更新频率，防止频繁更新影响性能
    current_time = time.time()
    if current_time - last_metrics_update < 2:  # 至少2秒才更新一次
        return

    # 更新系统指标
    try:
        # 进程指标
        process_cpu_usage.set(process.cpu_percent())
        process_memory_usage.set(process.memory_percent())

        # 系统指标
        system_cpu_usage.set(psutil.cpu_percent())
        system_memory_usage.set(psutil.virtual_memory().percent)

        # 更新时间
        last_metrics_update = current_time
    except Exception as e:
        logger.error(f"更新系统指标失败: {str(e)}")


@router.get("/metrics", summary="Prometheus指标")
async def metrics():
    """
    提供Prometheus监控指标

    返回:
        Response: 包含指标数据的响应
    """
    # 更新系统指标
    await update_system_metrics()

    # 生成指标数据
    metrics_data = generate_latest(registry)

    # 返回指标
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


# 中间件函数，用于记录请求指标
async def metrics_middleware(request, call_next):
    """
    请求指标中间件
    """
    # 获取请求路径和方法
    path = request.url.path
    method = request.method

    # 开始计时
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    duration_ms = (time.time() - start_time) * 1000

    # 记录请求计数和处理时间
    http_requests_total.labels(method=method, endpoint=path, status=response.status_code).inc()
    http_request_duration_ms.labels(method=method, endpoint=path).observe(duration_ms)

    # 如果是错误响应，记录错误
    if response.status_code >= 400:
        error_type = "client_error" if response.status_code < 500 else "server_error"
        api_errors_total.labels(endpoint=path, error_type=error_type).inc()

    return response


def increment_counter(name, labels=None):
    """
    增加计数器

    参数:
        name: 计数器名称
        labels: 标签值字典
    """
    labels = labels or {}

    if name == "knowledge_search_total":
        http_requests_total.labels(method="GET", endpoint="/api/knowledge/search", status=200).inc()
    elif name == "knowledge_search_error":
        api_errors_total.labels(endpoint="/api/knowledge/search", error_type="search_error").inc()
    elif name == "content_moderation_total":
        content_moderation_total.labels(result="total").inc()
    elif name == "content_moderation_approved":
        content_moderation_total.labels(result="approved").inc()
    elif name == "content_moderation_rejected":
        content_moderation_total.labels(result="rejected").inc()
    elif name == "content_moderation_error":
        content_moderation_total.labels(result="error").inc()
        api_errors_total.labels(endpoint="/api/community/moderate", error_type="moderation_error").inc()
    elif name == "npc_interaction_total":
        npc_interaction_total.inc()
    elif name == "npc_interaction_error":
        api_errors_total.labels(endpoint="/api/npc/interact", error_type="interaction_error").inc()
    elif name == "contribution_evaluation_total":
        knowledge_contribution_total.labels(status="evaluated").inc()
    elif name == "contribution_evaluation_error":
        knowledge_contribution_total.labels(status="error").inc()
        api_errors_total.labels(endpoint="/api/knowledge/evaluate", error_type="evaluation_error").inc()
    elif name == "learning_path_request_total":
        http_requests_total.labels(method="GET", endpoint="/api/learning/paths", status=200).inc()
    elif name == "learning_path_request_error":
        api_errors_total.labels(endpoint="/api/learning/paths", error_type="path_error").inc()
    elif name == "trending_content_request_total":
        http_requests_total.labels(method="GET", endpoint="/api/community/trending", status=200).inc()
    elif name == "trending_content_request_error":
        api_errors_total.labels(endpoint="/api/community/trending", error_type="trending_error").inc()
    elif name == "educational_content_request_total":
        http_requests_total.labels(method="GET", endpoint="/api/education/courses", status=200).inc()
    elif name == "educational_content_request_error":
        api_errors_total.labels(endpoint="/api/education/courses", error_type="courses_error").inc()


def observe_latency(name, value_ms):
    """
    记录延迟指标

    参数:
        name: 指标名称
        value_ms: 延迟值(毫秒)
    """
    if name == "knowledge_search_latency":
        knowledge_search_latency.observe(value_ms)
    elif name == "http_request_duration":
        # 已在中间件中处理
        pass
