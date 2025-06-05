#!/usr/bin/env python3
"""
告警规则模块
Alert Rules Module
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """告警严重程度"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(Enum):
    """告警状态"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """告警规则"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    condition: str  # 条件表达式
    threshold: float
    duration: int  # 持续时间（秒）
    enabled: bool = True
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.annotations is None:
            self.annotations = {}


@dataclass
class Alert:
    """告警实例"""
    id: str
    rule_id: str
    name: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    start_time: float
    end_time: Optional[float] = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    value: Optional[float] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.annotations is None:
            self.annotations = {}


class MetricCollector:
    """指标收集器"""

    def __init__(self):
        """初始化指标收集器"""
        self._metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    async def record_metric(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """记录指标"""
        async with self._lock:
            if name not in self._metrics:
                self._metrics[name] = []

            metric_point = {
                "value": value,
                "timestamp": time.time(),
                "labels": labels or {}
            }

            self._metrics[name].append(metric_point)

            # 保持最近1000个数据点
            if len(self._metrics[name]) > 1000:
                self._metrics[name] = self._metrics[name][-1000:]


class AlertManager:
    """告警管理器"""

    def __init__(self, metric_collector: MetricCollector):
        """初始化告警管理器"""
        self.metric_collector = metric_collector
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self._running = False
        self._check_task: Optional[asyncio.Task] = None
        self._alert_handlers: List[Callable[[Alert], None]] = []

    def add_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self.rules[rule.id] = rule
        logger.info(f"添加告警规则: {rule.name}")


# 预定义告警规则
DEFAULT_ALERT_RULES = [
    AlertRule(
        id="high_error_rate",
        name="高错误率告警",
        description="智能体请求错误率过高",
        severity=AlertSeverity.CRITICAL,
        condition="agent_error_rate > 0.1",
        threshold=0.1,
        duration=60,
        labels={"component": "agent_manager"},
        annotations={"runbook": "检查智能体服务状态"}
    )
] 