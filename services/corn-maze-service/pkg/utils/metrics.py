#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指标收集与监控模块
"""

import logging
import threading
import time
from typing import Dict, Any, Optional
from prometheus_client import start_http_server, Counter, Gauge, Histogram, Summary

# 初始化日志
logger = logging.getLogger(__name__)

# 定义指标
MAZE_CREATED_COUNTER = Counter('corn_maze_created_total', '创建的迷宫总数', ['maze_type', 'difficulty'])
MAZE_COMPLETION_COUNTER = Counter('corn_maze_completed_total', '完成的迷宫总数', ['maze_type', 'difficulty'])
KNOWLEDGE_NODE_VIEWED_COUNTER = Counter('corn_maze_knowledge_node_viewed_total', '查看的知识节点总数', ['category'])
CHALLENGE_COMPLETED_COUNTER = Counter('corn_maze_challenge_completed_total', '完成的挑战总数', ['type'])

# 性能指标
MAZE_GENERATION_TIME = Histogram('corn_maze_generation_seconds', '迷宫生成时间(秒)', ['maze_type', 'size'])
API_RESPONSE_TIME = Histogram('corn_maze_api_response_seconds', 'API响应时间(秒)', ['method'])

# 资源使用指标
ACTIVE_USERS_GAUGE = Gauge('corn_maze_active_users', '当前活跃用户数')
ACTIVE_MAZES_GAUGE = Gauge('corn_maze_active_mazes', '当前活跃迷宫数')
DB_CONNECTION_POOL_SIZE = Gauge('corn_maze_db_connection_pool_size', '数据库连接池大小')
DB_CONNECTION_POOL_USED = Gauge('corn_maze_db_connection_pool_used', '已使用的数据库连接数')

# 业务指标
AVG_COMPLETION_TIME = Summary('corn_maze_avg_completion_seconds', '平均迷宫完成时间(秒)', ['maze_type', 'difficulty'])
AVG_COMPLETION_STEPS = Summary('corn_maze_avg_completion_steps', '平均迷宫完成步数', ['maze_type', 'difficulty'])
AVG_KNOWLEDGE_DISCOVERED = Summary('corn_maze_avg_knowledge_discovered', '平均发现的知识点数', ['maze_type'])


def setup_metrics_server(port: int = 51057) -> threading.Thread:
    """
    启动指标HTTP服务器
    
    Args:
        port: 指标服务器端口
        
    Returns:
        threading.Thread: 指标服务器线程
    """
    logger.info(f"启动指标服务器在端口 {port}")
    
    try:
        start_http_server(port)
        logger.info(f"指标服务器成功启动在端口 {port}")
        
        # 启动健康检查更新线程
        health_thread = threading.Thread(target=_update_health_metrics, daemon=True)
        health_thread.start()
        
        return health_thread
    
    except Exception as e:
        logger.error(f"启动指标服务器失败: {str(e)}")
        # 返回一个空线程，这样调用者不会出错
        return threading.Thread()


def record_maze_creation(maze_type: str, difficulty: int) -> None:
    """记录迷宫创建指标"""
    MAZE_CREATED_COUNTER.labels(maze_type=maze_type, difficulty=str(difficulty)).inc()
    ACTIVE_MAZES_GAUGE.inc()


def record_maze_completion(maze_type: str, difficulty: int, time_spent: float, steps: int, knowledge_count: int) -> None:
    """记录迷宫完成指标"""
    MAZE_COMPLETION_COUNTER.labels(maze_type=maze_type, difficulty=str(difficulty)).inc()
    AVG_COMPLETION_TIME.labels(maze_type=maze_type, difficulty=str(difficulty)).observe(time_spent)
    AVG_COMPLETION_STEPS.labels(maze_type=maze_type, difficulty=str(difficulty)).observe(steps)
    AVG_KNOWLEDGE_DISCOVERED.labels(maze_type=maze_type).observe(knowledge_count)
    ACTIVE_MAZES_GAUGE.dec()


def record_knowledge_view(category: str) -> None:
    """记录知识节点查看指标"""
    KNOWLEDGE_NODE_VIEWED_COUNTER.labels(category=category).inc()


def record_challenge_completion(challenge_type: str) -> None:
    """记录挑战完成指标"""
    CHALLENGE_COMPLETED_COUNTER.labels(type=challenge_type).inc()


def track_api_time(method_name: str):
    """
    API响应时间装饰器
    
    Args:
        method_name: API方法名
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            API_RESPONSE_TIME.labels(method=method_name).observe(elapsed)
            return result
        return wrapper
    return decorator


def track_maze_generation_time(maze_type: str, size: str):
    """
    迷宫生成时间装饰器
    
    Args:
        maze_type: 迷宫类型
        size: 迷宫大小描述
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            MAZE_GENERATION_TIME.labels(maze_type=maze_type, size=size).observe(elapsed)
            return result
        return wrapper
    return decorator


def update_db_connection_metrics(pool_size: int, used: int) -> None:
    """更新数据库连接池指标"""
    DB_CONNECTION_POOL_SIZE.set(pool_size)
    DB_CONNECTION_POOL_USED.set(used)


def update_active_users(count: int) -> None:
    """更新活跃用户数指标"""
    ACTIVE_USERS_GAUGE.set(count)


def _update_health_metrics() -> None:
    """定期更新健康指标"""
    while True:
        # 这里可以添加系统健康检查逻辑
        # 例如检查数据库连接、内存使用等
        time.sleep(60)  # 每分钟更新一次