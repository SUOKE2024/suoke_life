#!/usr/bin/env python3
"""
监控模块 - 提供智能体监控和指标收集功能
"""

import time
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class XiaoaiMonitoring:
    """小艾监控系统"""

    def __init__(self, agent=None, enable_prometheus: bool = False):
        self.agent = agent
        self.enable_prometheus = enable_prometheus
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "avg_response_time": 0.0,
            "active_sessions": 0,
            "last_health_check": time.time(),
        }
        self.health_status = "healthy"

    def record_request(self, response_time: float, success: bool = True):
        """记录请求"""
        self.metrics["request_count"] += 1

        # 更新平均响应时间
        current_avg = self.metrics["avg_response_time"]
        count = self.metrics["request_count"]
        self.metrics["avg_response_time"] = (
            current_avg * (count - 1) + response_time
        ) / count

        if not success:
            self.metrics["error_count"] += 1

    def update_active_sessions(self, count: int):
        """更新活跃会话数"""
        self.metrics["active_sessions"] = count

    def update_agent_status(self, is_healthy: bool):
        """更新智能体状态"""
        self.health_status = "healthy" if is_healthy else "unhealthy"
        self.metrics["last_health_check"] = time.time()

    async def check_agent_health(self):
        """检查智能体健康状态"""
        try:
            if self.agent and hasattr(self.agent, 'get_health_status'):
                health_data = await self.agent.get_health_status()
                is_healthy = health_data.get("status") == "healthy"
            else:
                is_healthy = True

            self.update_agent_status(is_healthy)

        except Exception as e:
            logger.error(f"检查智能体健康状态失败: {e}")
            self.update_agent_status(False)

    def get_metrics_summary(self) -> dict[str, Any]:
        """获取指标摘要"""
        current_time = time.time()

        # 计算错误率
        error_rate = 0.0
        if self.metrics["request_count"] > 0:
            error_rate = (
                self.metrics["error_count"] / self.metrics["request_count"]
            ) * 100

        return {
            "status": self.health_status,
            "metrics": self.metrics.copy(),
            "error_rate": error_rate,
            "uptime": current_time - self.metrics["last_health_check"],
            "timestamp": current_time,
        }

    def get_health_report(self) -> dict[str, Any]:
        """获取健康报告"""
        metrics = self.get_metrics_summary()

        # 计算健康分数
        health_score = 100

        # 错误率影响
        error_rate = (
            self.metrics["error_count"] / max(self.metrics["request_count"], 1)
        ) * 100
        if error_rate > 10:
            health_score -= 30
        elif error_rate > 5:
            health_score -= 15

        # 响应时间影响
        if self.metrics["avg_response_time"] > 5:
            health_score -= 20
        elif self.metrics["avg_response_time"] > 2:
            health_score -= 10

        # 活跃会话数影响
        if self.metrics["active_sessions"] > 80:
            health_score -= 15

        # 确定健康状态
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "health_score": health_score,
            "metrics": metrics["metrics"],
            "error_rate": metrics["error_rate"],
            "recommendations": self._get_health_recommendations(health_score, metrics["metrics"]),
        }

    def _get_health_recommendations(
        self, health_score: int, metrics: dict[str, Any]
    ) -> list[str]:
        """获取健康建议"""
        recommendations = []

        if metrics["error_count"] > 0:
            error_rate = (
                metrics["error_count"] / max(metrics["request_count"], 1)
            ) * 100
            if error_rate > 5:
                recommendations.append(
                    f"错误率较高 ({error_rate:.1f}%),建议检查错误日志"
                )

        if metrics["avg_response_time"] > 2:
            recommendations.append(
                f"响应时间较慢 ({metrics['avg_response_time']:.2f}s),建议优化性能"
            )

        if metrics["active_sessions"] > 80:
            recommendations.append("活跃会话数较多,建议监控资源使用情况")

        if not recommendations:
            recommendations.append("系统运行正常")

        return recommendations


def setup_monitoring(agent=None) -> XiaoaiMonitoring:
    """设置监控"""
    try:
        monitoring = XiaoaiMonitoring(agent, enable_prometheus=True)

        # 将监控实例添加到应用状态
        if hasattr(agent, 'monitoring'):
            agent.monitoring = monitoring

        logger.info("监控系统设置完成")
        return monitoring

    except Exception as e:
        logger.error(f"设置监控失败: {e}")
        raise


# 全局监控实例
_monitoring_instance: XiaoaiMonitoring | None = None


def get_monitoring() -> XiaoaiMonitoring:
    """获取监控实例"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = XiaoaiMonitoring()
    return _monitoring_instance
