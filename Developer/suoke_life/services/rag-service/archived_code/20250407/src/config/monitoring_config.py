"""
监控和日志配置
"""

import os
from typing import Dict, Any

# 日志配置
LOG_CONFIG = {
    "LOG_PATH": os.getenv("LOG_PATH", "logs"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "LOG_FORMAT": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    "LOG_ROTATION": "1 day",
    "LOG_RETENTION": {
        "INFO": "30 days",
        "ERROR": "90 days",
        "DEBUG": "7 days"
    }
}

# Prometheus监控配置
PROMETHEUS_CONFIG = {
    "METRICS_PORT": int(os.getenv("METRICS_PORT", 9090)),
    "METRICS_PATH": "/metrics",
    "BUCKETS": {
        "DEFAULT": (0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf')),
        "VECTOR_SEARCH": (0.01, 0.05, 0.1, 0.5, 1.0, float('inf')),
        "LLM_API": (0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
    }
}

# 告警阈值配置
ALERT_CONFIG = {
    "ERROR_RATE_THRESHOLD": float(os.getenv("ERROR_RATE_THRESHOLD", 0.1)),
    "LATENCY_THRESHOLD": float(os.getenv("LATENCY_THRESHOLD", 5.0)),
    "CACHE_HIT_RATE_THRESHOLD": float(os.getenv("CACHE_HIT_RATE_THRESHOLD", 0.7)),
    "CHECK_INTERVAL": int(os.getenv("ALERT_CHECK_INTERVAL", 300))  # 5分钟
}

# 健康检查配置
HEALTH_CHECK_CONFIG = {
    "TIMEOUT": int(os.getenv("HEALTH_CHECK_TIMEOUT", 5)),
    "COMPONENTS": [
        "vector_store",
        "knowledge_graph",
        "llm_service",
        "cache"
    ]
}

def get_monitoring_config() -> Dict[str, Any]:
    """
    获取完整的监控配置
    """
    return {
        "log": LOG_CONFIG,
        "prometheus": PROMETHEUS_CONFIG,
        "alert": ALERT_CONFIG,
        "health_check": HEALTH_CHECK_CONFIG
    } 