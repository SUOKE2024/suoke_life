#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import psycopg2
import time
from flask import Blueprint, jsonify, current_app

logger = logging.getLogger(__name__)

# 创建Blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    
    简单检查服务是否在运行
    
    Returns:
        JSON响应，状态为"up"表示服务正常运行
    """
    logger.debug("收到健康检查请求")
    return jsonify({
        "status": "up",
        "service": current_app.config.get('SERVICE_NAME', 'medical-service'),
        "version": current_app.config.get('SERVICE_VERSION', '0.1.0'),
        "timestamp": time.time()
    })

@health_bp.route('/readiness', methods=['GET'])
def readiness_check():
    """
    就绪检查端点
    
    检查服务是否已准备好处理请求，包括检查数据库连接等依赖服务
    
    Returns:
        JSON响应，包含各个依赖的状态
    """
    logger.debug("收到就绪检查请求")
    
    # 检查结果
    status = {
        "status": "ready",
        "service": current_app.config.get('SERVICE_NAME', 'medical-service'),
        "version": current_app.config.get('SERVICE_VERSION', '0.1.0'),
        "timestamp": time.time(),
        "dependencies": {
            "database": check_database_connection(),
            "external_services": check_external_services()
        }
    }
    
    # 如果任何依赖不可用，则服务不就绪
    if not all(dep["status"] == "up" for dep in status["dependencies"].values()):
        status["status"] = "not_ready"
        return jsonify(status), 503  # 返回503 Service Unavailable
    
    return jsonify(status)

@health_bp.route('/liveness', methods=['GET'])
def liveness_check():
    """
    活跃检查端点
    
    检查服务是否活跃，即没有死锁或其他会导致服务无法恢复的问题
    
    Returns:
        JSON响应，状态为"alive"表示服务正常活跃
    """
    logger.debug("收到活跃检查请求")
    
    # 这里可以添加更复杂的检查，如检查关键线程是否活跃
    # 现在我们只做一个简单的检查
    return jsonify({
        "status": "alive",
        "service": current_app.config.get('SERVICE_NAME', 'medical-service'),
        "version": current_app.config.get('SERVICE_VERSION', '0.1.0'),
        "timestamp": time.time()
    })

@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    指标端点
    
    提供基本的服务指标，适用于Prometheus抓取
    
    Returns:
        文本格式的Prometheus指标
    """
    logger.debug("收到指标请求")
    
    # 示例指标
    metrics_text = """
# HELP medical_service_requests_total 处理的请求总数
# TYPE medical_service_requests_total counter
medical_service_requests_total{method="GET"} 10
medical_service_requests_total{method="POST"} 5

# HELP medical_service_request_duration_seconds 请求处理时间直方图
# TYPE medical_service_request_duration_seconds histogram
medical_service_request_duration_seconds_bucket{le="0.1"} 8
medical_service_request_duration_seconds_bucket{le="0.5"} 12
medical_service_request_duration_seconds_bucket{le="1.0"} 14
medical_service_request_duration_seconds_bucket{le="+Inf"} 15
medical_service_request_duration_seconds_sum 5.2
medical_service_request_duration_seconds_count 15

# HELP medical_service_up 服务是否在运行
# TYPE medical_service_up gauge
medical_service_up 1
"""
    
    # 在实际实现中，这些指标应该动态生成
    return metrics_text, 200, {'Content-Type': 'text/plain; version=0.0.4'}

def check_database_connection():
    """
    检查数据库连接是否正常
    
    Returns:
        包含数据库连接状态的字典
    """
    try:
        db_config = current_app.config.get('DATABASE', {})
        conn = psycopg2.connect(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 5432),
            user=db_config.get('user', 'postgres'),
            password=db_config.get('password', 'postgres'),
            dbname=db_config.get('dbname', 'medical_service'),
            connect_timeout=3  # 设置连接超时时间为3秒
        )
        
        # 执行简单查询测试连接
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            result = cur.fetchone()
        
        conn.close()
        
        return {
            "status": "up",
            "latency_ms": int(time.time() * 1000) % 100  # 模拟延迟毫秒数
        }
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return {
            "status": "down",
            "error": str(e)
        }

def check_external_services():
    """
    检查外部服务连接是否正常
    
    Returns:
        包含外部服务连接状态的字典
    """
    # 这里应该实现对依赖服务的检查，例如通过gRPC调用检查健康状态
    # 为简化示例，我们直接返回模拟数据
    return {
        "status": "up",
        "services": {
            "health-data-service": "up",
            "med-knowledge": "up",
            "rag-service": "up"
        }
    } 