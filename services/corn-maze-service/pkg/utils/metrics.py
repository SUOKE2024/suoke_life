#!/usr/bin/env python3

"""
监控指标模块 - 增强版本
"""

from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime
import functools
import logging
import time
from typing import Any

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Info,
        Summary,
        start_http_server,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Prometheus指标定义
if PROMETHEUS_AVAILABLE:
    # 迷宫操作计数器
    maze_operations_total = Counter(
        'maze_operations_total',
        'Total number of maze operations',
        ['operation', 'maze_type', 'status']
    )

    # 迷宫生成时间直方图
    maze_generation_duration = Histogram(
        'maze_generation_duration_seconds',
        'Time spent generating mazes',
        ['maze_type', 'difficulty'],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
    )

    # API请求时间直方图
    api_request_duration = Histogram(
        'api_request_duration_seconds',
        'Time spent processing API requests',
        ['method', 'endpoint', 'status'],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    )

    # 缓存操作计数器
    cache_operations_total = Counter(
        'cache_operations_total',
        'Total number of cache operations',
        ['operation', 'backend', 'status']
    )

    # 数据库操作计数器
    db_operations_total = Counter(
        'db_operations_total',
        'Total number of database operations',
        ['operation', 'table', 'status']
    )

    # 活跃迷宫数量
    active_mazes_gauge = Gauge(
        'active_mazes_total',
        'Number of active mazes',
        ['maze_type']
    )

    # 用户活跃度
    active_users_gauge = Gauge(
        'active_users_total',
        'Number of active users'
    )

    # 错误计数器
    errors_total = Counter(
        'errors_total',
        'Total number of errors',
        ['component', 'error_type', 'severity']
    )

    # 系统信息
    system_info = Info(
        'system_info',
        'System information'
    )

    # 缓存命中率
    cache_hit_rate = Gauge(
        'cache_hit_rate',
        'Cache hit rate',
        ['cache_type']
    )

    # 内存使用量
    memory_usage_bytes = Gauge(
        'memory_usage_bytes',
        'Memory usage in bytes',
        ['component']
    )

    # 响应时间摘要
    response_time_summary = Summary(
        'response_time_seconds',
        'Response time summary',
        ['service', 'method']
    )

    # 并发连接数
    concurrent_connections = Gauge(
        'concurrent_connections',
        'Number of concurrent connections'
    )

    # 队列长度
    queue_length = Gauge(
        'queue_length',
        'Length of processing queues',
        ['queue_type']
    )

else:
    # 如果Prometheus不可用，创建空的指标对象
    class DummyMetric:
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def info(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
        def time(self): return self
        def __enter__(self): return self
        def __exit__(self, *args): pass

    maze_operations_total = DummyMetric()
    maze_generation_duration = DummyMetric()
    api_request_duration = DummyMetric()
    cache_operations_total = DummyMetric()
    db_operations_total = DummyMetric()
    active_mazes_gauge = DummyMetric()
    active_users_gauge = DummyMetric()
    errors_total = DummyMetric()
    system_info = DummyMetric()
    cache_hit_rate = DummyMetric()
    memory_usage_bytes = DummyMetric()
    response_time_summary = DummyMetric()
    concurrent_connections = DummyMetric()
    queue_length = DummyMetric()

# 内存中的指标存储（用于非Prometheus环境）
_metrics_store: dict[str, Any] = {
    "maze_operations": defaultdict(int),
    "generation_times": deque(maxlen=1000),
    "api_requests": defaultdict(lambda: deque(maxlen=100)),
    "cache_operations": defaultdict(int),
    "db_operations": defaultdict(int),
    "errors": defaultdict(int),
    "system_stats": {},
    "performance_data": defaultdict(list)
}

# 性能监控数据
_performance_tracker = {
    "slow_operations": deque(maxlen=100),  # 慢操作记录
    "error_patterns": defaultdict(int),    # 错误模式统计
    "resource_usage": deque(maxlen=1000),  # 资源使用历史
}

def start_metrics_server(port: int = 8000):
    """启动Prometheus指标服务器"""
    if PROMETHEUS_AVAILABLE:
        try:
            start_http_server(port)
            logger.info(f"Prometheus指标服务器已启动，端口: {port}")

            # 设置系统信息
            system_info.info({
                'version': '1.0.0',
                'service': 'corn-maze-service',
                'python_version': '3.9+',
                'started_at': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"启动Prometheus指标服务器失败: {e!s}")
    else:
        logger.warning("Prometheus不可用，指标服务器未启动")

def maze_generation_time(func: Callable) -> Callable:
    """迷宫生成时间装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        maze_type = kwargs.get('maze_type', 'unknown')
        difficulty = kwargs.get('difficulty', 0)

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            # 记录Prometheus指标
            maze_generation_duration.labels(
                maze_type=maze_type,
                difficulty=str(difficulty)
            ).observe(duration)

            # 记录内存指标
            _metrics_store["generation_times"].append({
                "maze_type": maze_type,
                "difficulty": difficulty,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "success": True
            })

            # 检查是否为慢操作
            if duration > 5.0:  # 超过5秒认为是慢操作
                _performance_tracker["slow_operations"].append({
                    "operation": "maze_generation",
                    "maze_type": maze_type,
                    "difficulty": difficulty,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                })

            logger.info(f"迷宫生成完成，类型: {maze_type}, 难度: {difficulty}, 耗时: {duration:.2f}秒")
            return result

        except Exception as e:
            duration = time.time() - start_time
            record_maze_generation_error(maze_type, "generation_failed")

            # 记录失败的生成尝试
            _metrics_store["generation_times"].append({
                "maze_type": maze_type,
                "difficulty": difficulty,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            })

            logger.error(f"迷宫生成失败，类型: {maze_type}, 难度: {difficulty}, 耗时: {duration:.2f}秒, 错误: {e!s}")
            raise

    return wrapper

def api_request_time(endpoint: str):
    """API请求时间装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = getattr(func, '__name__', 'unknown')
            status = 'success'

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                status = 'error'
                # 记录错误模式
                error_pattern = f"{method}:{type(e).__name__}"
                _performance_tracker["error_patterns"][error_pattern] += 1
                raise

            finally:
                duration = time.time() - start_time

                # 记录Prometheus指标
                api_request_duration.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).observe(duration)

                response_time_summary.labels(
                    service='maze_service',
                    method=method
                ).observe(duration)

                # 记录内存指标
                key = f"{method}:{endpoint}"
                _metrics_store["api_requests"][key].append({
                    "duration": duration,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                })

                # 检查慢请求
                if duration > 2.0:  # 超过2秒认为是慢请求
                    _performance_tracker["slow_operations"].append({
                        "operation": "api_request",
                        "method": method,
                        "endpoint": endpoint,
                        "duration": duration,
                        "status": status,
                        "timestamp": datetime.now().isoformat()
                    })

        return wrapper
    return decorator

def record_maze_operation(operation: str, maze_type: str, difficulty: int):
    """记录迷宫操作"""
    maze_operations_total.labels(
        operation=operation,
        maze_type=maze_type,
        status='success'
    ).inc()

    # 内存指标
    key = f"{operation}:{maze_type}"
    _metrics_store["maze_operations"][key] += 1

def record_maze_error(operation: str, error_type: str):
    """记录迷宫操作错误"""
    maze_operations_total.labels(
        operation=operation,
        maze_type='unknown',
        status='error'
    ).inc()

    errors_total.labels(
        component='maze_service',
        error_type=error_type,
        severity='error'
    ).inc()

    # 内存指标
    key = f"{operation}:{error_type}"
    _metrics_store["errors"][key] += 1

def record_maze_generation_error(maze_type: str, error_type: str):
    """记录迷宫生成错误"""
    errors_total.labels(
        component='maze_generator',
        error_type=error_type,
        severity='error'
    ).inc()

    # 内存指标
    key = f"generation:{maze_type}:{error_type}"
    _metrics_store["errors"][key] += 1

def record_maze_creation(maze_type: str, difficulty: int):
    """记录迷宫创建"""
    maze_operations_total.labels(
        operation='create',
        maze_type=maze_type,
        status='success'
    ).inc()

    # 内存指标
    key = f"create:{maze_type}:{difficulty}"
    _metrics_store["maze_operations"][key] += 1

def record_cache_operation(operation: str, backend: str, status: str = 'success'):
    """记录缓存操作"""
    cache_operations_total.labels(
        operation=operation,
        backend=backend,
        status=status
    ).inc()

    # 内存指标
    key = f"{operation}:{backend}:{status}"
    _metrics_store["cache_operations"][key] += 1

def record_db_operation(operation: str, table: str, status: str = 'success'):
    """记录数据库操作"""
    db_operations_total.labels(
        operation=operation,
        table=table,
        status=status
    ).inc()

    # 内存指标
    key = f"{operation}:{table}:{status}"
    _metrics_store["db_operations"][key] += 1

def update_active_mazes_count(maze_type: str, count: int):
    """更新活跃迷宫数量"""
    active_mazes_gauge.labels(maze_type=maze_type).set(count)

    # 内存指标
    _metrics_store["system_stats"][f"active_mazes_{maze_type}"] = count

def update_active_users_count(count: int):
    """更新活跃用户数量"""
    active_users_gauge.set(count)

    # 内存指标
    _metrics_store["system_stats"]["active_users"] = count

def update_cache_hit_rate(cache_type: str, hit_rate: float):
    """更新缓存命中率"""
    cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)

    # 内存指标
    _metrics_store["system_stats"][f"cache_hit_rate_{cache_type}"] = hit_rate

def update_memory_usage(component: str, bytes_used: int):
    """更新内存使用量"""
    memory_usage_bytes.labels(component=component).set(bytes_used)

    # 内存指标
    _metrics_store["system_stats"][f"memory_usage_{component}"] = bytes_used

def update_concurrent_connections(count: int):
    """更新并发连接数"""
    concurrent_connections.set(count)
    _metrics_store["system_stats"]["concurrent_connections"] = count

def update_queue_length(queue_type: str, length: int):
    """更新队列长度"""
    queue_length.labels(queue_type=queue_type).set(length)
    _metrics_store["system_stats"][f"queue_length_{queue_type}"] = length

def get_metrics_summary() -> dict[str, Any]:
    """获取指标摘要"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "prometheus_available": PROMETHEUS_AVAILABLE,
        "metrics_store": dict(_metrics_store),
        "performance_tracker": dict(_performance_tracker)
    }

    # 计算生成时间统计
    if _metrics_store["generation_times"]:
        successful_times = [item["duration"] for item in _metrics_store["generation_times"] if item.get("success", True)]
        if successful_times:
            summary["generation_stats"] = {
                "count": len(successful_times),
                "avg_duration": sum(successful_times) / len(successful_times),
                "min_duration": min(successful_times),
                "max_duration": max(successful_times),
                "p95_duration": _calculate_percentile(successful_times, 95),
                "p99_duration": _calculate_percentile(successful_times, 99)
            }

    # 计算错误率
    total_operations = sum(_metrics_store["maze_operations"].values())
    total_errors = sum(_metrics_store["errors"].values())
    if total_operations > 0:
        summary["error_rate"] = total_errors / (total_operations + total_errors)
    else:
        summary["error_rate"] = 0.0

    # 计算API性能统计
    api_stats = {}
    for endpoint, requests in _metrics_store["api_requests"].items():
        if requests:
            durations = [req["duration"] for req in requests]
            success_count = len([req for req in requests if req["status"] == "success"])
            api_stats[endpoint] = {
                "total_requests": len(requests),
                "success_rate": success_count / len(requests),
                "avg_duration": sum(durations) / len(durations),
                "p95_duration": _calculate_percentile(durations, 95)
            }
    summary["api_stats"] = api_stats

    # 慢操作统计
    summary["slow_operations_count"] = len(_performance_tracker["slow_operations"])
    summary["top_error_patterns"] = dict(sorted(
        _performance_tracker["error_patterns"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10])

    return summary

def _calculate_percentile(data: list[float], percentile: int) -> float:
    """计算百分位数"""
    if not data:
        return 0.0

    sorted_data = sorted(data)
    index = int((percentile / 100.0) * len(sorted_data))
    if index >= len(sorted_data):
        index = len(sorted_data) - 1
    return sorted_data[index]

def reset_metrics():
    """重置内存中的指标"""
    global _metrics_store, _performance_tracker
    _metrics_store = {
        "maze_operations": defaultdict(int),
        "generation_times": deque(maxlen=1000),
        "api_requests": defaultdict(lambda: deque(maxlen=100)),
        "cache_operations": defaultdict(int),
        "db_operations": defaultdict(int),
        "errors": defaultdict(int),
        "system_stats": {},
        "performance_data": defaultdict(list)
    }
    _performance_tracker = {
        "slow_operations": deque(maxlen=100),
        "error_patterns": defaultdict(int),
        "resource_usage": deque(maxlen=1000),
    }
    logger.info("指标已重置")

# 性能监控装饰器
def monitor_performance(component: str):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = _get_memory_usage()

            try:
                result = await func(*args, **kwargs)
                status = 'success'
                return result

            except Exception as e:
                status = 'error'
                errors_total.labels(
                    component=component,
                    error_type=type(e).__name__,
                    severity='error'
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                end_memory = _get_memory_usage()
                memory_delta = end_memory - start_memory

                # 记录性能数据
                perf_data = {
                    "component": component,
                    "function": func.__name__,
                    "duration": duration,
                    "memory_delta": memory_delta,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                }

                _metrics_store["performance_data"][component].append(perf_data)

                # 保持最近1000条记录
                if len(_metrics_store["performance_data"][component]) > 1000:
                    _metrics_store["performance_data"][component] = _metrics_store["performance_data"][component][-1000:]

                # 记录资源使用
                _performance_tracker["resource_usage"].append({
                    "timestamp": datetime.now().isoformat(),
                    "memory_usage": end_memory,
                    "active_operations": len(_metrics_store["performance_data"])
                })

                logger.debug(f"{component}.{func.__name__} - 耗时: {duration:.3f}s, 内存变化: {memory_delta}MB")

                # 更新内存使用量
                update_memory_usage(component, end_memory)

        return wrapper
    return decorator

def _get_memory_usage() -> int:
    """获取当前内存使用量（字节）"""
    try:
        import os

        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss
    except:
        return 0

# 健康检查相关指标
def record_health_check(component: str, status: str, duration: float):
    """记录健康检查结果"""
    health_check_duration = Histogram(
        'health_check_duration_seconds',
        'Health check duration',
        ['component', 'status']
    ) if PROMETHEUS_AVAILABLE else DummyMetric()

    health_check_duration.labels(component=component, status=status).observe(duration)

    # 内存指标
    key = f"health_check:{component}:{status}"
    _metrics_store["system_stats"][key] = {
        "duration": duration,
        "timestamp": datetime.now().isoformat()
    }

# 业务指标
def record_user_action(action: str, user_id: str, maze_type: str = None):
    """记录用户行为"""
    user_actions_total = Counter(
        'user_actions_total',
        'Total user actions',
        ['action', 'maze_type']
    ) if PROMETHEUS_AVAILABLE else DummyMetric()

    user_actions_total.labels(action=action, maze_type=maze_type or 'unknown').inc()

    # 内存指标
    key = f"user_action:{action}:{maze_type or 'unknown'}"
    _metrics_store["maze_operations"][key] += 1
