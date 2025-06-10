"""
business - 索克生活项目模块
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any
import logging



logger = logging.getLogger(__name__)

class BusinessMetricsMonitor:
    """业务指标监控器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.metrics = defaultdict(int)
        self.events = []

    def record_user_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """记录用户行为"""
        event = {
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.events.append(event)
        self.metrics[f"user_action_{action}"] += 1

        logger.info(f"用户行为记录: {user_id} - {action}")

    def record_diagnosis_request(self, user_id: str, diagnosis_type: str):
        """记录诊断请求"""
        self.record_user_action(user_id, "diagnosis_request", {"type": diagnosis_type})
        self.metrics["total_diagnosis_requests"] += 1

    def record_agent_interaction(self, user_id: str, agent_name: str, interaction_type: str):
        """记录智能体交互"""
        self.record_user_action(user_id, "agent_interaction", {
            "agent": agent_name,
            "type": interaction_type
        })
        self.metrics[f"agent_{agent_name}_interactions"] += 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        return {
            "metrics": dict(self.metrics),
            "total_events": len(self.events),
            "timestamp": datetime.utcnow().isoformat()
        }
