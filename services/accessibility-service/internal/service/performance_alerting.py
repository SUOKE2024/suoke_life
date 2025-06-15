#!/usr/bin/env python3
"""
性能告警机制模块
基于性能监控数据实现智能告警和阈值管理
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ThresholdType(Enum):
    """阈值类型"""

    STATIC = "static"  # 静态阈值
    DYNAMIC = "dynamic"  # 动态阈值
    PERCENTILE = "percentile"  # 百分位数阈值
    TREND = "trend"  # 趋势阈值


class AlertLevel(Enum):
    """告警级别"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ThresholdRule:
    """阈值规则"""

    name: str
    metric_name: str
    threshold_type: ThresholdType
    alert_level: AlertLevel
    value: float | dict[str, float]  # 静态值或动态配置
    comparison: str = ">"  # >, <, >=, <=, ==, !=
    duration_seconds: int = 60  # 持续时间
    enabled: bool = True
    tags_filter: dict[str, str] | None = None
    description: str = ""


@dataclass
class PerformanceAlert:
    """性能告警"""

    rule_name: str
    metric_name: str
    current_value: float
    threshold_value: float
    alert_level: AlertLevel
    message: str
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)
    duration: float = 0.0
    resolved: bool = False
    resolved_at: float | None = None


@dataclass
class MetricSnapshot:
    """指标快照"""

    name: str
    value: float
    timestamp: float
    tags: dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


class PerformanceThresholdManager:
    """性能阈值管理器"""

    def __init__(self, history_size: int = 1000):
        self.threshold_rules: list[ThresholdRule] = []
        self.metric_history: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_size)
        )
        self.active_alerts: list[PerformanceAlert] = []
        self.alert_history: deque = deque(maxlen=10000)
        self.alert_callbacks: list[Callable] = []
        self.last_evaluation_time = time.time()

    def add_threshold_rule(self, rule: ThresholdRule):
        """添加阈值规则"""
        self.threshold_rules.append(rule)
        logger.info(f"添加性能阈值规则: {rule.name}")

    def remove_threshold_rule(self, rule_name: str):
        """移除阈值规则"""
        self.threshold_rules = [r for r in self.threshold_rules if r.name != rule_name]
        logger.info(f"移除性能阈值规则: {rule_name}")

    def add_alert_callback(self, callback: Callable):
        """添加告警回调"""
        self.alert_callbacks.append(callback)

    def record_metric(self, snapshot: MetricSnapshot):
        """记录指标数据"""
        key = self._make_metric_key(snapshot.name, snapshot.tags)
        self.metric_history[key].append(snapshot)

    def _make_metric_key(self, name: str, tags: dict[str, str]) -> str:
        """生成指标键"""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"

    async def evaluate_thresholds(self) -> None:
        """评估阈值"""
        current_time = time.time()

        for rule in self.threshold_rules:
            if not rule.enabled:
                continue

            try:
                await self._evaluate_single_rule(rule, current_time)
            except Exception as e:
                logger.error(f"评估阈值规则失败 {rule.name}: {e}")

        self.last_evaluation_time = current_time

    async def _evaluate_single_rule(self, rule: ThresholdRule, current_time: float):
        """评估单个规则"""
        # 获取匹配的指标
        matching_metrics = self._get_matching_metrics(rule)

        if not matching_metrics:
            return

        for metric_key, snapshots in matching_metrics.items():
            if not snapshots:
                continue

            # 计算阈值
            threshold_value = self._calculate_threshold(rule, snapshots)
            if threshold_value is None:
                continue

            # 获取当前值
            current_value = self._get_current_value(rule, snapshots)

            # 检查是否违反阈值
            if self._check_threshold_violation(
                current_value, threshold_value, rule.comparison
            ):
                # 检查持续时间
                if self._check_duration(rule, snapshots, current_time):
                    await self._trigger_alert(
                        rule,
                        metric_key,
                        current_value,
                        threshold_value,
                        snapshots[-1].tags,
                    )
            else:
                # 检查是否需要解决告警
                self._resolve_alert(rule.name, metric_key)

    def _get_matching_metrics(
        self, rule: ThresholdRule
    ) -> dict[str, list[MetricSnapshot]]:
        """获取匹配规则的指标"""
        matching = {}

        for metric_key, snapshots in self.metric_history.items():
            # 检查指标名称
            if not metric_key.startswith(rule.metric_name):
                continue

            # 检查标签过滤
            if rule.tags_filter:
                # 从metric_key中提取标签
                if "{" in metric_key:
                    tag_part = metric_key.split("{")[1].rstrip("}")
                    tags = dict(
                        item.split("=") for item in tag_part.split(",") if "=" in item
                    )
                else:
                    tags = {}

                # 检查是否匹配过滤条件
                if not all(tags.get(k) == v for k, v in rule.tags_filter.items()):
                    continue

            matching[metric_key] = list(snapshots)

        return matching

    def _calculate_threshold(
        self, rule: ThresholdRule, snapshots: list[MetricSnapshot]
    ) -> float | None:
        """计算阈值"""
        if rule.threshold_type == ThresholdType.STATIC:
            return float(rule.value)

        elif rule.threshold_type == ThresholdType.DYNAMIC:
            # 基于历史数据的动态阈值
            if len(snapshots) < 10:  # 需要足够的历史数据
                return None

            values = [s.value for s in snapshots[-100:]]  # 最近100个数据点
            mean = statistics.mean(values)
            std = statistics.stdev(values) if len(values) > 1 else 0

            # 动态阈值 = 均值 + N倍标准差
            multiplier = (
                rule.value.get("std_multiplier", 2.0)
                if isinstance(rule.value, dict)
                else 2.0
            )
            return mean + multiplier * std

        elif rule.threshold_type == ThresholdType.PERCENTILE:
            # 百分位数阈值
            if len(snapshots) < 10:
                return None

            values = [s.value for s in snapshots[-100:]]
            percentile = (
                rule.value.get("percentile", 95) if isinstance(rule.value, dict) else 95
            )

            # 计算百分位数
            sorted_values = sorted(values)
            index = int(len(sorted_values) * percentile / 100)
            return sorted_values[min(index, len(sorted_values) - 1)]

        elif rule.threshold_type == ThresholdType.TREND:
            # 趋势阈值
            if len(snapshots) < 20:
                return None

            # 计算趋势斜率
            recent_values = [s.value for s in snapshots[-20:]]
            x = list(range(len(recent_values)))

            # 简单线性回归计算斜率
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(recent_values)
            sum_xy = sum(x[i] * recent_values[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

            # 趋势阈值
            trend_threshold = (
                rule.value.get("slope_threshold", 0.1)
                if isinstance(rule.value, dict)
                else 0.1
            )
            return trend_threshold

        return None

    def _get_current_value(
        self, rule: ThresholdRule, snapshots: list[MetricSnapshot]
    ) -> float:
        """获取当前值"""
        if rule.threshold_type == ThresholdType.TREND:
            # 对于趋势，返回计算的斜率
            if len(snapshots) < 20:
                return 0.0

            recent_values = [s.value for s in snapshots[-20:]]
            x = list(range(len(recent_values)))

            n = len(x)
            sum_x = sum(x)
            sum_y = sum(recent_values)
            sum_xy = sum(x[i] * recent_values[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope
        else:
            # 返回最新值
            return snapshots[-1].value if snapshots else 0.0

    def _check_threshold_violation(
        self, current_value: float, threshold_value: float, comparison: str
    ) -> bool:
        """检查阈值违反"""
        if comparison == ">":
            return current_value > threshold_value
        elif comparison == "<":
            return current_value < threshold_value
        elif comparison == ">=":
            return current_value >= threshold_value
        elif comparison == "<=":
            return current_value <= threshold_value
        elif comparison == "==":
            return abs(current_value - threshold_value) < 1e-6
        elif comparison == "!=":
            return abs(current_value - threshold_value) >= 1e-6
        return False

    def _check_duration(
        self, rule: ThresholdRule, snapshots: list[MetricSnapshot], current_time: float
    ) -> bool:
        """检查持续时间"""
        if rule.duration_seconds <= 0:
            return True

        # 检查在指定时间内是否持续违反阈值
        violation_start_time = current_time - rule.duration_seconds

        for snapshot in reversed(snapshots):
            if snapshot.timestamp < violation_start_time:
                break

            threshold_value = self._calculate_threshold(rule, snapshots)
            if threshold_value is None:
                return False

            current_value = snapshot.value
            if rule.threshold_type == ThresholdType.TREND:
                # 趋势检查需要特殊处理
                return True

            if not self._check_threshold_violation(
                current_value, threshold_value, rule.comparison
            ):
                return False

        return True

    async def _trigger_alert(
        self,
        rule: ThresholdRule,
        metric_key: str,
        current_value: float,
        threshold_value: float,
        tags: dict[str, str],
    ):
        """触发告警"""
        # 检查是否已存在相同告警
        existing_alert = self._find_active_alert(rule.name, metric_key)
        if existing_alert:
            return

        # 创建告警
        alert = PerformanceAlert(
            rule_name=rule.name,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            alert_level=rule.alert_level,
            message=self._format_alert_message(rule, current_value, threshold_value),
            tags=tags,
        )

        # 记录告警
        self.active_alerts.append(alert)
        self.alert_history.append(alert)

        # 发送通知
        await self._send_alert_notifications(alert)

        logger.warning(f"性能告警触发: {alert.rule_name} - {alert.message}")

    def _find_active_alert(
        self, rule_name: str, metric_key: str
    ) -> PerformanceAlert | None:
        """查找活跃告警"""
        for alert in self.active_alerts:
            if alert.rule_name == rule_name and metric_key in str(alert.tags):
                return alert
        return None

    def _resolve_alert(self, rule_name: str, metric_key: str):
        """解决告警"""
        current_time = time.time()

        for alert in self.active_alerts:
            if (
                alert.rule_name == rule_name
                and metric_key in str(alert.tags)
                and not alert.resolved
            ):
                alert.resolved = True
                alert.resolved_at = current_time
                logger.info(f"性能告警已解决: {rule_name}")

        # 移除已解决的告警
        self.active_alerts = [a for a in self.active_alerts if not a.resolved]

    def _format_alert_message(
        self, rule: ThresholdRule, current_value: float, threshold_value: float
    ) -> str:
        """格式化告警消息"""
        if rule.threshold_type == ThresholdType.TREND:
            return f"{rule.description or rule.metric_name} 趋势异常: 斜率 {current_value:.4f} {rule.comparison} {threshold_value:.4f}"
        else:
            return f"{rule.description or rule.metric_name} 阈值告警: {current_value:.2f} {rule.comparison} {threshold_value:.2f}"

    async def _send_alert_notifications(self, alert: PerformanceAlert):
        """发送告警通知"""
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"发送性能告警通知失败: {e}")

    def get_active_alerts(self) -> list[PerformanceAlert]:
        """获取活跃告警"""
        return self.active_alerts.copy()

    def get_alert_summary(self) -> dict[str, Any]:
        """获取告警摘要"""
        return {
            "active_alerts": len(self.active_alerts),
            "total_rules": len(self.threshold_rules),
            "enabled_rules": sum(1 for r in self.threshold_rules if r.enabled),
            "alert_history_count": len(self.alert_history),
            "alerts_by_level": {
                level.value: sum(
                    1 for a in self.active_alerts if a.alert_level == level
                )
                for level in AlertLevel
            },
            "last_evaluation": self.last_evaluation_time,
        }

    def get_metric_statistics(
        self, metric_name: str, tags: dict[str, str] = None
    ) -> dict[str, Any]:
        """获取指标统计"""
        metric_key = self._make_metric_key(metric_name, tags or {})
        snapshots = self.metric_history.get(metric_key, [])

        if not snapshots:
            return {"error": "指标数据不存在"}

        values = [s.value for s in snapshots]

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "latest": values[-1],
            "latest_timestamp": snapshots[-1].timestamp,
        }


# 通知处理器
async def console_performance_alert_handler(alert: PerformanceAlert):
    """控制台性能告警处理器"""
    level_icons = {
        AlertLevel.INFO: "ℹ️",
        AlertLevel.WARNING: "⚠️",
        AlertLevel.CRITICAL: "🚨",
        AlertLevel.EMERGENCY: "🆘",
    }

    icon = level_icons.get(alert.alert_level, "📊")
    print(f"{icon} [PERF-{alert.alert_level.value.upper()}] {alert.message}")


async def log_performance_alert_handler(alert: PerformanceAlert):
    """日志性能告警处理器"""
    log_levels = {
        AlertLevel.INFO: logging.INFO,
        AlertLevel.WARNING: logging.WARNING,
        AlertLevel.CRITICAL: logging.ERROR,
        AlertLevel.EMERGENCY: logging.CRITICAL,
    }

    level = log_levels.get(alert.alert_level, logging.WARNING)
    logger.log(level, f"PERF-ALERT [{alert.rule_name}]: {alert.message}")


# 全局性能阈值管理器
global_performance_threshold_manager = PerformanceThresholdManager()


def setup_default_performance_thresholds() -> None:
    """设置默认性能阈值"""
    rules = [
        # CPU使用率阈值
        ThresholdRule(
            name="high_cpu_usage",
            metric_name="cpu_percent",
            threshold_type=ThresholdType.STATIC,
            alert_level=AlertLevel.WARNING,
            value=80.0,
            comparison=">",
            duration_seconds=300,
            description="CPU使用率过高",
        ),
        # 内存使用率阈值
        ThresholdRule(
            name="high_memory_usage",
            metric_name="memory_percent",
            threshold_type=ThresholdType.STATIC,
            alert_level=AlertLevel.CRITICAL,
            value=90.0,
            comparison=">",
            duration_seconds=180,
            description="内存使用率过高",
        ),
        # 响应时间动态阈值
        ThresholdRule(
            name="slow_response_time",
            metric_name="response_time",
            threshold_type=ThresholdType.DYNAMIC,
            alert_level=AlertLevel.WARNING,
            value={"std_multiplier": 3.0},
            comparison=">",
            duration_seconds=120,
            description="响应时间异常",
        ),
        # 错误率阈值
        ThresholdRule(
            name="high_error_rate",
            metric_name="error_rate",
            threshold_type=ThresholdType.PERCENTILE,
            alert_level=AlertLevel.CRITICAL,
            value={"percentile": 95},
            comparison=">",
            duration_seconds=60,
            description="错误率过高",
        ),
        # 内存增长趋势
        ThresholdRule(
            name="memory_leak_trend",
            metric_name="memory_usage",
            threshold_type=ThresholdType.TREND,
            alert_level=AlertLevel.WARNING,
            value={"slope_threshold": 0.5},  # MB/分钟
            comparison=">",
            duration_seconds=600,
            description="内存泄漏趋势",
        ),
    ]

    for rule in rules:
        global_performance_threshold_manager.add_threshold_rule(rule)

    # 添加默认通知处理器
    global_performance_threshold_manager.add_alert_callback(
        console_performance_alert_handler
    )
    global_performance_threshold_manager.add_alert_callback(
        log_performance_alert_handler
    )

    logger.info("默认性能阈值规则已设置")


async def start_performance_monitoring() -> None:
    """启动性能监控"""
    while True:
        try:
            await global_performance_threshold_manager.evaluate_thresholds()
            await asyncio.sleep(30)  # 每30秒评估一次
        except Exception as e:
            logger.error(f"性能监控评估失败: {e}")
            await asyncio.sleep(60)  # 出错时等待更长时间


def record_performance_metric(
    name: str,
    value: float,
    tags: dict[str, str] = None,
    metric_type: MetricType = MetricType.GAUGE,
):
    """记录性能指标"""
    snapshot = MetricSnapshot(
        name=name,
        value=value,
        timestamp=time.time(),
        tags=tags or {},
        metric_type=metric_type,
    )
    global_performance_threshold_manager.record_metric(snapshot)


def get_performance_alerts() -> list[PerformanceAlert]:
    """获取性能告警"""
    return global_performance_threshold_manager.get_active_alerts()


def get_performance_alert_summary() -> dict[str, Any]:
    """获取性能告警摘要"""
    return global_performance_threshold_manager.get_alert_summary()
