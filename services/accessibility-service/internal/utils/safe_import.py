"""
安全导入工具模块
提供健壮的模块导入机制
"""

import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


def safe_import(
    module_name: str, fallback: Any = None, attribute: str | None = None
) -> Any:
    """
    安全导入模块或模块属性

    Args:
        module_name: 模块名称
        fallback: 导入失败时的回退值
        attribute: 要导入的属性名称

    Returns:
        导入的模块或属性，失败时返回fallback
    """
    try:
        module = importlib.import_module(module_name)
        if attribute:
            return getattr(module, attribute, fallback)
        return module
    except ImportError as e:
        logger.warning(f"模块 {module_name} 导入失败: {e}")
        return fallback
    except AttributeError as e:
        logger.warning(f"属性 {attribute} 在模块 {module_name} 中不存在: {e}")
        return fallback


class MockHealthManager:
    """健康检查管理器的Mock实现"""

    async def check_health(self):
        return {
            "overall_status": "healthy",
            "services": {},
            "timestamp": 0,
            "mock": True,
        }


class MockPerformanceCollector:
    """性能收集器的Mock实现"""

    async def collect_metrics(self):
        return {"cpu_usage": 0.0, "memory_usage": 0.0, "timestamp": 0, "mock": True}


class MockAlertManager:
    """告警管理器的Mock实现"""

    async def get_active_alerts(self):
        return []

    async def send_alert(self, alert):
        logger.info(f"Mock alert: {alert}")


# 预定义的回退实现
FALLBACK_IMPLEMENTATIONS = {
    "optimized_health_manager": MockHealthManager(),
    "optimized_performance_collector": MockPerformanceCollector(),
    "performance_alert_manager": MockAlertManager(),
}
