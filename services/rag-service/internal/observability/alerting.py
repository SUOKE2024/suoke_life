#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级监控告警系统 - 支持智能异常检测、预测性维护、自动化运维
"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from loguru import logger

from .metrics import MetricsCollector
from .tracing import trace_operation, SpanKind

class AlertSeverity(str, Enum):
    """告警严重程度"""
    INFO = "info"                           # 信息
    WARNING = "warning"                     # 警告
    ERROR = "error"                         # 错误
    CRITICAL = "critical"                   # 严重
    EMERGENCY = "emergency"                 # 紧急

class AlertStatus(str, Enum):
    """告警状态"""
    ACTIVE = "active"                       # 活跃
    ACKNOWLEDGED = "acknowledged"           # 已确认
    RESOLVED = "resolved"                   # 已解决
    SUPPRESSED = "suppressed"               # 已抑制

class AlertType(str, Enum):
    """告警类型"""
    THRESHOLD = "threshold"                 # 阈值告警
    ANOMALY = "anomaly"                     # 异常检测
    TREND = "trend"                         # 趋势分析
    CORRELATION = "correlation"             # 关联分析
    PREDICTION = "prediction"               # 预测告警
    HEALTH_CHECK = "health_check"           # 健康检查
    PERFORMANCE = "performance"             # 性能告警
    SECURITY = "security"                   # 安全告警

@dataclass
class AlertRule:
    """告警规则"""
    id: str
    name: str
    description: str
    type: AlertType
    severity: AlertSeverity
    metric_name: str
    condition: str                          # 条件表达式
    threshold: Optional[float] = None
    duration: int = 60                      # 持续时间（秒）
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    
    # 高级配置
    evaluation_interval: int = 30           # 评估间隔（秒）
    recovery_threshold: Optional[float] = None  # 恢复阈值
    suppression_duration: int = 300         # 抑制时间（秒）
    max_alerts_per_hour: int = 10          # 每小时最大告警数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "severity": self.severity.value,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "duration": self.duration,
            "enabled": self.enabled,
            "tags": self.tags,
            "evaluation_interval": self.evaluation_interval,
            "recovery_threshold": self.recovery_threshold,
            "suppression_duration": self.suppression_duration,
            "max_alerts_per_hour": self.max_alerts_per_hour
        }

@dataclass
class Alert:
    """告警实例"""
    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    metric_name: str
    metric_value: float
    threshold: Optional[float]
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    acknowledged_at: Optional[float] = None
    acknowledged_by: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "acknowledged_at": self.acknowledged_at,
            "acknowledged_by": self.acknowledged_by,
            "tags": self.tags,
            "metadata": self.metadata
        }

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self, window_size: int = 100, sensitivity: float = 2.0):
        self.window_size = window_size
        self.sensitivity = sensitivity  # 标准差倍数
        self.data_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_data_point(self, metric_name: str, value: float, timestamp: float):
        """添加数据点"""
        self.data_windows[metric_name].append((timestamp, value))
    
    def detect_anomaly(self, metric_name: str, current_value: float) -> Tuple[bool, float]:
        """检测异常"""
        if metric_name not in self.data_windows:
            return False, 0.0
        
        window = self.data_windows[metric_name]
        if len(window) < 10:  # 需要足够的历史数据
            return False, 0.0
        
        # 提取数值
        values = [v for _, v in window]
        
        # 计算统计指标
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        if stdev == 0:
            return False, 0.0
        
        # 计算Z分数
        z_score = abs(current_value - mean) / stdev
        
        # 判断是否异常
        is_anomaly = z_score > self.sensitivity
        
        return is_anomaly, z_score

class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.data_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_data_point(self, metric_name: str, value: float, timestamp: float):
        """添加数据点"""
        self.data_windows[metric_name].append((timestamp, value))
    
    def analyze_trend(self, metric_name: str) -> Tuple[str, float]:
        """分析趋势"""
        if metric_name not in self.data_windows:
            return "unknown", 0.0
        
        window = self.data_windows[metric_name]
        if len(window) < 10:
            return "insufficient_data", 0.0
        
        # 提取时间和数值
        timestamps = [t for t, _ in window]
        values = [v for _, v in window]
        
        # 计算线性回归斜率
        n = len(values)
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * v for i, v in enumerate(values))
        sum_x2 = sum(i * i for i in range(n))
        
        # 斜率计算
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # 判断趋势
        if abs(slope) < 0.001:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return trend, slope

class PredictiveAnalyzer:
    """预测分析器"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_data_point(self, metric_name: str, value: float, timestamp: float):
        """添加数据点"""
        self.data_windows[metric_name].append((timestamp, value))
    
    def predict_future_value(self, metric_name: str, future_minutes: int = 30) -> Optional[float]:
        """预测未来值"""
        if metric_name not in self.data_windows:
            return None
        
        window = self.data_windows[metric_name]
        if len(window) < 20:
            return None
        
        # 简单线性预测
        values = [v for _, v in window]
        n = len(values)
        
        # 计算趋势
        x = list(range(n))
        y = values
        
        # 线性回归
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # 预测未来值
        future_x = n + (future_minutes / 5)  # 假设每5分钟一个数据点
        predicted_value = slope * future_x + intercept
        
        return predicted_value
    
    def predict_threshold_breach(
        self, 
        metric_name: str, 
        threshold: float, 
        future_minutes: int = 60
    ) -> Tuple[bool, Optional[float]]:
        """预测阈值突破"""
        predicted_value = self.predict_future_value(metric_name, future_minutes)
        
        if predicted_value is None:
            return False, None
        
        will_breach = predicted_value > threshold
        return will_breach, predicted_value

class AlertManager:
    """告警管理器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector
        
        # 告警规则和实例
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # 分析器
        self.anomaly_detector = AnomalyDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.predictive_analyzer = PredictiveAnalyzer()
        
        # 通知器
        self.notifiers: List[Callable] = []
        
        # 抑制管理
        self.suppressed_rules: Dict[str, float] = {}  # rule_id -> until_timestamp
        self.alert_counts: Dict[str, List[float]] = defaultdict(list)  # rule_id -> timestamps
        
        # 后台任务
        self._evaluation_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # 配置
        self.evaluation_interval = 30  # 评估间隔（秒）
        self.history_retention_days = 30  # 历史保留天数
        
        # 运行状态
        self.running = False
    
    async def start(self):
        """启动告警管理器"""
        if self.running:
            return
        
        self.running = True
        
        # 启动后台任务
        self._evaluation_task = asyncio.create_task(self._evaluation_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("告警管理器已启动")
    
    async def stop(self):
        """停止告警管理器"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止后台任务
        if self._evaluation_task:
            self._evaluation_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        logger.info("告警管理器已停止")
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.id] = rule
        logger.info(f"添加告警规则: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除告警规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            # 解决相关的活跃告警
            alerts_to_resolve = [
                alert_id for alert_id, alert in self.active_alerts.items()
                if alert.rule_id == rule_id
            ]
            for alert_id in alerts_to_resolve:
                self.resolve_alert(alert_id)
            
            logger.info(f"移除告警规则: {rule_id}")
            return True
        return False
    
    def add_notifier(self, notifier: Callable):
        """添加通知器"""
        self.notifiers.append(notifier)
    
    async def evaluate_metric(self, metric_name: str, value: float, timestamp: float):
        """评估指标"""
        # 添加到分析器
        self.anomaly_detector.add_data_point(metric_name, value, timestamp)
        self.trend_analyzer.add_data_point(metric_name, value, timestamp)
        self.predictive_analyzer.add_data_point(metric_name, value, timestamp)
        
        # 评估相关规则
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            if rule.metric_name == metric_name or rule.metric_name == "*":
                await self._evaluate_rule(rule, metric_name, value, timestamp)
    
    @trace_operation("alert.evaluate_rule", SpanKind.INTERNAL)
    async def _evaluate_rule(self, rule: AlertRule, metric_name: str, value: float, timestamp: float):
        """评估单个规则"""
        try:
            # 检查抑制状态
            if self._is_rule_suppressed(rule.id):
                return
            
            # 检查频率限制
            if not self._check_rate_limit(rule.id):
                return
            
            triggered = False
            alert_message = ""
            metadata = {}
            
            # 根据规则类型进行评估
            if rule.type == AlertType.THRESHOLD:
                triggered, alert_message = self._evaluate_threshold(rule, value)
            
            elif rule.type == AlertType.ANOMALY:
                is_anomaly, z_score = self.anomaly_detector.detect_anomaly(metric_name, value)
                triggered = is_anomaly
                alert_message = f"检测到异常: Z分数={z_score:.2f}"
                metadata["z_score"] = z_score
            
            elif rule.type == AlertType.TREND:
                trend, slope = self.trend_analyzer.analyze_trend(metric_name)
                if "increasing" in rule.condition and trend == "increasing":
                    triggered = True
                    alert_message = f"检测到上升趋势: 斜率={slope:.4f}"
                elif "decreasing" in rule.condition and trend == "decreasing":
                    triggered = True
                    alert_message = f"检测到下降趋势: 斜率={slope:.4f}"
                metadata["trend"] = trend
                metadata["slope"] = slope
            
            elif rule.type == AlertType.PREDICTION:
                will_breach, predicted_value = self.predictive_analyzer.predict_threshold_breach(
                    metric_name, rule.threshold or 0, 30
                )
                triggered = will_breach
                if predicted_value is not None:
                    alert_message = f"预测阈值突破: 预测值={predicted_value:.2f}"
                    metadata["predicted_value"] = predicted_value
            
            # 处理告警
            if triggered:
                await self._create_alert(rule, metric_name, value, alert_message, metadata)
            else:
                # 检查是否需要解决现有告警
                await self._check_alert_recovery(rule, metric_name, value)
            
        except Exception as e:
            logger.error(f"评估规则失败 {rule.name}: {e}")
    
    def _evaluate_threshold(self, rule: AlertRule, value: float) -> Tuple[bool, str]:
        """评估阈值规则"""
        if rule.threshold is None:
            return False, ""
        
        condition = rule.condition.lower()
        threshold = rule.threshold
        
        if ">" in condition:
            triggered = value > threshold
            message = f"值 {value} 超过阈值 {threshold}"
        elif "<" in condition:
            triggered = value < threshold
            message = f"值 {value} 低于阈值 {threshold}"
        elif "=" in condition:
            triggered = abs(value - threshold) < 0.001
            message = f"值 {value} 等于阈值 {threshold}"
        else:
            triggered = False
            message = ""
        
        return triggered, message
    
    def _is_rule_suppressed(self, rule_id: str) -> bool:
        """检查规则是否被抑制"""
        if rule_id in self.suppressed_rules:
            if time.time() < self.suppressed_rules[rule_id]:
                return True
            else:
                del self.suppressed_rules[rule_id]
        return False
    
    def _check_rate_limit(self, rule_id: str) -> bool:
        """检查频率限制"""
        rule = self.rules.get(rule_id)
        if not rule:
            return False
        
        current_time = time.time()
        hour_ago = current_time - 3600
        
        # 清理旧的时间戳
        self.alert_counts[rule_id] = [
            ts for ts in self.alert_counts[rule_id] if ts > hour_ago
        ]
        
        # 检查是否超过限制
        return len(self.alert_counts[rule_id]) < rule.max_alerts_per_hour
    
    async def _create_alert(
        self, 
        rule: AlertRule, 
        metric_name: str, 
        value: float, 
        message: str,
        metadata: Dict[str, Any]
    ):
        """创建告警"""
        # 检查是否已存在相同的活跃告警
        existing_alert_id = f"{rule.id}_{metric_name}"
        if existing_alert_id in self.active_alerts:
            # 更新现有告警
            alert = self.active_alerts[existing_alert_id]
            alert.metric_value = value
            alert.updated_at = time.time()
            alert.metadata.update(metadata)
            return
        
        # 创建新告警
        alert = Alert(
            id=existing_alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            message=message,
            metric_name=metric_name,
            metric_value=value,
            threshold=rule.threshold,
            tags=rule.tags.copy(),
            metadata=metadata
        )
        
        # 添加到活跃告警
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)
        
        # 记录告警计数
        self.alert_counts[rule.id].append(time.time())
        
        # 发送通知
        await self._send_notifications(alert)
        
        # 记录指标
        if self.metrics_collector:
            await self.metrics_collector.increment_counter(
                "alerts_created",
                {
                    "rule_id": rule.id,
                    "severity": rule.severity.value,
                    "type": rule.type.value
                }
            )
        
        logger.warning(f"创建告警: {alert.rule_name} - {alert.message}")
    
    async def _check_alert_recovery(self, rule: AlertRule, metric_name: str, value: float):
        """检查告警恢复"""
        alert_id = f"{rule.id}_{metric_name}"
        if alert_id not in self.active_alerts:
            return
        
        alert = self.active_alerts[alert_id]
        if alert.status != AlertStatus.ACTIVE:
            return
        
        # 检查恢复条件
        recovered = False
        
        if rule.type == AlertType.THRESHOLD and rule.recovery_threshold is not None:
            condition = rule.condition.lower()
            recovery_threshold = rule.recovery_threshold
            
            if ">" in condition:
                recovered = value <= recovery_threshold
            elif "<" in condition:
                recovered = value >= recovery_threshold
        
        if recovered:
            await self.resolve_alert(alert_id)
    
    async def resolve_alert(self, alert_id: str, resolved_by: Optional[str] = None):
        """解决告警"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = time.time()
        alert.updated_at = time.time()
        
        # 从活跃告警中移除
        del self.active_alerts[alert_id]
        
        # 发送恢复通知
        await self._send_recovery_notifications(alert)
        
        # 记录指标
        if self.metrics_collector:
            await self.metrics_collector.increment_counter(
                "alerts_resolved",
                {"rule_id": alert.rule_id, "severity": alert.severity.value}
            )
        
        logger.info(f"解决告警: {alert.rule_name}")
        return True
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """确认告警"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = time.time()
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = time.time()
        
        logger.info(f"确认告警: {alert.rule_name} by {acknowledged_by}")
        return True
    
    def suppress_rule(self, rule_id: str, duration_minutes: int):
        """抑制规则"""
        until_timestamp = time.time() + (duration_minutes * 60)
        self.suppressed_rules[rule_id] = until_timestamp
        
        logger.info(f"抑制规则: {rule_id} for {duration_minutes} minutes")
    
    async def _send_notifications(self, alert: Alert):
        """发送通知"""
        for notifier in self.notifiers:
            try:
                await notifier(alert, "created")
            except Exception as e:
                logger.error(f"发送告警通知失败: {e}")
    
    async def _send_recovery_notifications(self, alert: Alert):
        """发送恢复通知"""
        for notifier in self.notifiers:
            try:
                await notifier(alert, "resolved")
            except Exception as e:
                logger.error(f"发送恢复通知失败: {e}")
    
    async def _evaluation_loop(self):
        """评估循环"""
        while self.running:
            try:
                await asyncio.sleep(self.evaluation_interval)
                
                # 这里可以添加定期评估逻辑
                # 例如：检查健康状态、预测分析等
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"评估循环错误: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                
                current_time = time.time()
                retention_threshold = current_time - (self.history_retention_days * 24 * 3600)
                
                # 清理历史告警
                self.alert_history = [
                    alert for alert in self.alert_history
                    if alert.created_at > retention_threshold
                ]
                
                # 清理告警计数
                hour_ago = current_time - 3600
                for rule_id in list(self.alert_counts.keys()):
                    self.alert_counts[rule_id] = [
                        ts for ts in self.alert_counts[rule_id] if ts > hour_ago
                    ]
                    if not self.alert_counts[rule_id]:
                        del self.alert_counts[rule_id]
                
                logger.info("完成告警历史清理")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环错误: {e}")
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """获取活跃告警"""
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """获取告警统计"""
        total_rules = len(self.rules)
        active_alerts = len(self.active_alerts)
        
        # 按严重程度统计
        severity_counts = defaultdict(int)
        for alert in self.active_alerts.values():
            severity_counts[alert.severity.value] += 1
        
        # 按规则统计
        rule_counts = defaultdict(int)
        for alert in self.active_alerts.values():
            rule_counts[alert.rule_id] += 1
        
        # 最近24小时告警数
        day_ago = time.time() - 86400
        recent_alerts = len([
            alert for alert in self.alert_history
            if alert.created_at > day_ago
        ])
        
        return {
            "total_rules": total_rules,
            "active_alerts": active_alerts,
            "recent_alerts_24h": recent_alerts,
            "severity_distribution": dict(severity_counts),
            "rule_distribution": dict(rule_counts),
            "suppressed_rules": len(self.suppressed_rules)
        }

# 通知器实现
class WebhookNotifier:
    """Webhook通知器"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def __call__(self, alert: Alert, action: str):
        """发送Webhook通知"""
        import aiohttp
        
        payload = {
            "action": action,
            "alert": alert.to_dict(),
            "timestamp": time.time()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook通知发送成功: {alert.id}")
                    else:
                        logger.error(f"Webhook通知发送失败: {response.status}")
        except Exception as e:
            logger.error(f"Webhook通知异常: {e}")

class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self, smtp_config: Dict[str, Any], recipients: List[str]):
        self.smtp_config = smtp_config
        self.recipients = recipients
    
    async def __call__(self, alert: Alert, action: str):
        """发送邮件通知"""
        # 这里应该实现实际的邮件发送逻辑
        logger.info(f"邮件通知: {action} - {alert.rule_name}")

# 全局告警管理器实例
_alert_manager: Optional[AlertManager] = None

def initialize_alert_manager(
    metrics_collector: Optional[MetricsCollector] = None
) -> AlertManager:
    """初始化告警管理器"""
    global _alert_manager
    _alert_manager = AlertManager(metrics_collector)
    return _alert_manager

def get_alert_manager() -> Optional[AlertManager]:
    """获取告警管理器实例"""
    return _alert_manager

# 便捷函数
def create_threshold_rule(
    rule_id: str,
    name: str,
    metric_name: str,
    threshold: float,
    condition: str = ">",
    severity: AlertSeverity = AlertSeverity.WARNING
) -> AlertRule:
    """创建阈值告警规则"""
    return AlertRule(
        id=rule_id,
        name=name,
        description=f"{metric_name} {condition} {threshold}",
        type=AlertType.THRESHOLD,
        severity=severity,
        metric_name=metric_name,
        condition=condition,
        threshold=threshold
    )

def create_anomaly_rule(
    rule_id: str,
    name: str,
    metric_name: str,
    severity: AlertSeverity = AlertSeverity.WARNING
) -> AlertRule:
    """创建异常检测告警规则"""
    return AlertRule(
        id=rule_id,
        name=name,
        description=f"异常检测: {metric_name}",
        type=AlertType.ANOMALY,
        severity=severity,
        metric_name=metric_name,
        condition="anomaly"
    ) 