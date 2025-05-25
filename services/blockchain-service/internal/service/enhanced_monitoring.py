#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强监控服务

该模块提供更详细的指标收集、实时性能分析、智能告警、
预测性维护等高级监控功能，全面提升系统可观测性。
"""

import asyncio
import logging
import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math
from collections import deque, defaultdict

from internal.model.config import AppConfig
from internal.service.monitoring_service import MonitoringService, MetricType


class AlertSeverity(Enum):
    """告警严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """告警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class TrendDirection(Enum):
    """趋势方向"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class Alert:
    """告警信息"""
    id: str
    metric_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    @property
    def duration(self) -> timedelta:
        """告警持续时间"""
        end_time = self.resolved_at or datetime.now()
        return end_time - self.timestamp


@dataclass
class MetricTrend:
    """指标趋势"""
    metric_name: str
    direction: TrendDirection
    slope: float
    confidence: float
    prediction: Optional[float] = None
    prediction_time: Optional[datetime] = None


@dataclass
class PerformanceInsight:
    """性能洞察"""
    insight_type: str
    title: str
    description: str
    impact: str
    recommendation: str
    confidence: float
    timestamp: datetime
    metrics_involved: List[str]


@dataclass
class SystemHealth:
    """系统健康状态"""
    overall_score: float
    component_scores: Dict[str, float]
    active_alerts: int
    critical_alerts: int
    trends: List[MetricTrend]
    insights: List[PerformanceInsight]
    timestamp: datetime


class EnhancedMonitoringService:
    """增强监控服务"""

    def __init__(self, config: AppConfig, base_monitoring: MonitoringService):
        """
        初始化增强监控服务
        
        Args:
            config: 应用配置对象
            base_monitoring: 基础监控服务
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.base_monitoring = base_monitoring
        
        # 告警配置
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_alert_history = 1000
        
        # 趋势分析配置
        self.trend_window = 50  # 趋势分析窗口
        self.trend_threshold = 0.1  # 趋势阈值
        
        # 性能洞察配置
        self.insight_rules: List[Callable] = []
        self.insights_history: List[PerformanceInsight] = []
        self.max_insights_history = 100
        
        # 预测配置
        self.prediction_enabled = True
        self.prediction_horizon = 300  # 预测时间范围（秒）
        
        # 监控状态
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.analysis_interval = 30  # 分析间隔（秒）
        
        # 回调函数
        self.alert_callbacks: List[Callable] = []
        self.insight_callbacks: List[Callable] = []
        
        # 初始化默认告警规则
        self._setup_default_alert_rules()
        
        # 初始化洞察规则
        self._setup_insight_rules()
        
        self.logger.info("增强监控服务初始化完成")
    
    async def start_monitoring(self):
        """启动增强监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("增强监控已启动")
    
    async def stop_monitoring(self):
        """停止增强监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("增强监控已停止")
    
    def add_alert_rule(
        self,
        metric_name: str,
        threshold: float,
        severity: AlertSeverity,
        condition: str = "greater_than",
        duration: int = 60,
        description: str = ""
    ):
        """
        添加告警规则
        
        Args:
            metric_name: 指标名称
            threshold: 阈值
            severity: 严重程度
            condition: 条件（greater_than, less_than, equals）
            duration: 持续时间（秒）
            description: 描述
        """
        self.alert_rules[metric_name] = {
            "threshold": threshold,
            "severity": severity,
            "condition": condition,
            "duration": duration,
            "description": description,
            "last_triggered": None,
            "consecutive_violations": 0
        }
        
        self.logger.info(f"添加告警规则: {metric_name} {condition} {threshold}")
    
    def remove_alert_rule(self, metric_name: str):
        """
        移除告警规则
        
        Args:
            metric_name: 指标名称
        """
        if metric_name in self.alert_rules:
            del self.alert_rules[metric_name]
            self.logger.info(f"移除告警规则: {metric_name}")
    
    def add_alert_callback(self, callback: Callable):
        """
        添加告警回调
        
        Args:
            callback: 回调函数
        """
        self.alert_callbacks.append(callback)
    
    def add_insight_callback(self, callback: Callable):
        """
        添加洞察回调
        
        Args:
            callback: 回调函数
        """
        self.insight_callbacks.append(callback)
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                # 执行告警检查
                await self._check_alerts()
                
                # 执行趋势分析
                await self._analyze_trends()
                
                # 生成性能洞察
                await self._generate_insights()
                
                # 清理过期数据
                await self._cleanup_old_data()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"监控循环错误: {str(e)}")
                await asyncio.sleep(10)
    
    async def _check_alerts(self):
        """检查告警"""
        current_metrics = self.base_monitoring.get_current_metrics()
        
        for metric_name, rule in self.alert_rules.items():
            if metric_name not in current_metrics:
                continue
            
            metric_value = current_metrics[metric_name]
            threshold = rule["threshold"]
            condition = rule["condition"]
            
            # 检查是否违反阈值
            violation = False
            if condition == "greater_than" and metric_value > threshold:
                violation = True
            elif condition == "less_than" and metric_value < threshold:
                violation = True
            elif condition == "equals" and abs(metric_value - threshold) < 0.001:
                violation = True
            
            if violation:
                rule["consecutive_violations"] += 1
                
                # 检查是否达到持续时间要求
                if rule["consecutive_violations"] * self.analysis_interval >= rule["duration"]:
                    await self._trigger_alert(metric_name, metric_value, rule)
            else:
                # 重置连续违反计数
                rule["consecutive_violations"] = 0
                
                # 检查是否需要解决现有告警
                await self._resolve_alert(metric_name)
    
    async def _trigger_alert(self, metric_name: str, value: float, rule: Dict[str, Any]):
        """
        触发告警
        
        Args:
            metric_name: 指标名称
            value: 当前值
            rule: 告警规则
        """
        alert_id = f"{metric_name}_{int(time.time())}"
        
        # 检查是否已有活跃告警
        existing_alert = None
        for alert in self.active_alerts.values():
            if alert.metric_name == metric_name and alert.status == AlertStatus.ACTIVE:
                existing_alert = alert
                break
        
        if existing_alert:
            return  # 已有活跃告警，不重复触发
        
        # 创建新告警
        alert = Alert(
            id=alert_id,
            metric_name=metric_name,
            severity=rule["severity"],
            status=AlertStatus.ACTIVE,
            message=self._generate_alert_message(metric_name, value, rule),
            value=value,
            threshold=rule["threshold"],
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # 限制历史记录大小
        if len(self.alert_history) > self.max_alert_history:
            self.alert_history = self.alert_history[-self.max_alert_history:]
        
        # 调用回调函数
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self.logger.error(f"告警回调执行失败: {str(e)}")
        
        self.logger.warning(f"触发告警: {alert.message}")
    
    async def _resolve_alert(self, metric_name: str):
        """
        解决告警
        
        Args:
            metric_name: 指标名称
        """
        alerts_to_resolve = []
        
        for alert_id, alert in self.active_alerts.items():
            if alert.metric_name == metric_name and alert.status == AlertStatus.ACTIVE:
                alerts_to_resolve.append(alert_id)
        
        for alert_id in alerts_to_resolve:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[alert_id]
            
            self.logger.info(f"解决告警: {alert.message}")
    
    def _generate_alert_message(self, metric_name: str, value: float, rule: Dict[str, Any]) -> str:
        """生成告警消息"""
        condition = rule["condition"]
        threshold = rule["threshold"]
        description = rule.get("description", "")
        
        if condition == "greater_than":
            condition_text = "超过"
        elif condition == "less_than":
            condition_text = "低于"
        else:
            condition_text = "等于"
        
        message = f"{metric_name} {condition_text} 阈值 {threshold}，当前值: {value:.2f}"
        
        if description:
            message += f" - {description}"
        
        return message
    
    async def _analyze_trends(self):
        """分析趋势"""
        metrics_data = self.base_monitoring.get_metrics_history()
        
        for metric_name, data_points in metrics_data.items():
            if len(data_points) < self.trend_window:
                continue
            
            # 获取最近的数据点
            recent_data = data_points[-self.trend_window:]
            values = [point.value for point in recent_data]
            timestamps = [point.timestamp.timestamp() for point in recent_data]
            
            # 计算趋势
            trend = self._calculate_trend(values, timestamps)
            
            # 预测未来值
            if self.prediction_enabled:
                prediction = self._predict_future_value(values, timestamps)
                trend.prediction = prediction
                trend.prediction_time = datetime.now() + timedelta(seconds=self.prediction_horizon)
    
    def _calculate_trend(self, values: List[float], timestamps: List[float]) -> MetricTrend:
        """
        计算趋势
        
        Args:
            values: 数值列表
            timestamps: 时间戳列表
            
        Returns:
            趋势信息
        """
        if len(values) < 2:
            return MetricTrend("", TrendDirection.STABLE, 0.0, 0.0)
        
        # 计算线性回归斜率
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)
        
        # 避免除零错误
        denominator = n * sum_x2 - sum_x * sum_x
        if abs(denominator) < 1e-10:
            slope = 0.0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # 计算相关系数（置信度）
        mean_x = sum_x / n
        mean_y = sum_y / n
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(timestamps, values))
        denominator_x = sum((x - mean_x) ** 2 for x in timestamps)
        denominator_y = sum((y - mean_y) ** 2 for y in values)
        
        if denominator_x * denominator_y == 0:
            confidence = 0.0
        else:
            confidence = abs(numerator / math.sqrt(denominator_x * denominator_y))
        
        # 确定趋势方向
        if abs(slope) < self.trend_threshold:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # 检查波动性
        if confidence < 0.5:
            direction = TrendDirection.VOLATILE
        
        return MetricTrend("", direction, slope, confidence)
    
    def _predict_future_value(self, values: List[float], timestamps: List[float]) -> Optional[float]:
        """
        预测未来值
        
        Args:
            values: 数值列表
            timestamps: 时间戳列表
            
        Returns:
            预测值
        """
        if len(values) < 3:
            return None
        
        try:
            # 使用简单的线性外推
            trend = self._calculate_trend(values, timestamps)
            
            if trend.confidence < 0.3:
                return None  # 置信度太低，不进行预测
            
            last_timestamp = timestamps[-1]
            future_timestamp = last_timestamp + self.prediction_horizon
            last_value = values[-1]
            
            predicted_value = last_value + trend.slope * self.prediction_horizon
            
            return predicted_value
            
        except Exception as e:
            self.logger.warning(f"预测计算失败: {str(e)}")
            return None
    
    async def _generate_insights(self):
        """生成性能洞察"""
        for rule in self.insight_rules:
            try:
                insights = rule()
                if insights:
                    for insight in insights:
                        self.insights_history.append(insight)
                        
                        # 调用回调函数
                        for callback in self.insight_callbacks:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(insight)
                                else:
                                    callback(insight)
                            except Exception as e:
                                self.logger.error(f"洞察回调执行失败: {str(e)}")
                        
                        self.logger.info(f"生成性能洞察: {insight.title}")
            
            except Exception as e:
                self.logger.error(f"洞察规则执行失败: {str(e)}")
        
        # 限制历史记录大小
        if len(self.insights_history) > self.max_insights_history:
            self.insights_history = self.insights_history[-self.max_insights_history:]
    
    async def _cleanup_old_data(self):
        """清理过期数据"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # 清理已解决的告警
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff_time or alert.status == AlertStatus.ACTIVE
        ]
        
        # 清理过期洞察
        self.insights_history = [
            insight for insight in self.insights_history
            if insight.timestamp > cutoff_time
        ]
    
    def _setup_default_alert_rules(self):
        """设置默认告警规则"""
        # CPU使用率告警
        self.add_alert_rule(
            "cpu_usage",
            80.0,
            AlertSeverity.HIGH,
            "greater_than",
            120,
            "CPU使用率过高"
        )
        
        # 内存使用率告警
        self.add_alert_rule(
            "memory_usage",
            85.0,
            AlertSeverity.HIGH,
            "greater_than",
            120,
            "内存使用率过高"
        )
        
        # 错误率告警
        self.add_alert_rule(
            "error_rate",
            0.05,
            AlertSeverity.MEDIUM,
            "greater_than",
            60,
            "错误率过高"
        )
        
        # 响应时间告警
        self.add_alert_rule(
            "response_time",
            5.0,
            AlertSeverity.MEDIUM,
            "greater_than",
            180,
            "响应时间过长"
        )
    
    def _setup_insight_rules(self):
        """设置洞察规则"""
        self.insight_rules.extend([
            self._check_performance_degradation,
            self._check_resource_optimization,
            self._check_error_patterns,
            self._check_capacity_planning
        ])
    
    def _check_performance_degradation(self) -> List[PerformanceInsight]:
        """检查性能退化"""
        insights = []
        
        # 检查响应时间趋势
        metrics_data = self.base_monitoring.get_metrics_history()
        response_time_data = metrics_data.get("response_time", [])
        
        if len(response_time_data) >= 20:
            recent_values = [point.value for point in response_time_data[-20:]]
            older_values = [point.value for point in response_time_data[-40:-20]] if len(response_time_data) >= 40 else []
            
            if older_values:
                recent_avg = statistics.mean(recent_values)
                older_avg = statistics.mean(older_values)
                
                if recent_avg > older_avg * 1.2:  # 响应时间增加20%以上
                    insights.append(PerformanceInsight(
                        insight_type="performance_degradation",
                        title="响应时间性能退化",
                        description=f"最近的平均响应时间 ({recent_avg:.2f}s) 比之前增加了 {((recent_avg - older_avg) / older_avg * 100):.1f}%",
                        impact="用户体验下降，系统性能退化",
                        recommendation="检查系统负载、数据库性能或网络状况",
                        confidence=0.8,
                        timestamp=datetime.now(),
                        metrics_involved=["response_time"]
                    ))
        
        return insights
    
    def _check_resource_optimization(self) -> List[PerformanceInsight]:
        """检查资源优化机会"""
        insights = []
        
        current_metrics = self.base_monitoring.get_current_metrics()
        cpu_usage = current_metrics.get("cpu_usage", 0)
        memory_usage = current_metrics.get("memory_usage", 0)
        
        # 检查资源使用不均衡
        if cpu_usage < 30 and memory_usage > 70:
            insights.append(PerformanceInsight(
                insight_type="resource_optimization",
                title="内存使用不均衡",
                description=f"CPU使用率较低 ({cpu_usage:.1f}%) 但内存使用率较高 ({memory_usage:.1f}%)",
                impact="资源配置不均衡，可能存在内存泄漏或配置问题",
                recommendation="检查内存使用情况，考虑调整缓存配置或修复内存泄漏",
                confidence=0.7,
                timestamp=datetime.now(),
                metrics_involved=["cpu_usage", "memory_usage"]
            ))
        
        elif cpu_usage > 70 and memory_usage < 30:
            insights.append(PerformanceInsight(
                insight_type="resource_optimization",
                title="CPU使用不均衡",
                description=f"CPU使用率较高 ({cpu_usage:.1f}%) 但内存使用率较低 ({memory_usage:.1f}%)",
                impact="CPU密集型负载，可能需要优化算法或增加并行处理",
                recommendation="优化CPU密集型操作，考虑增加缓存或并行处理",
                confidence=0.7,
                timestamp=datetime.now(),
                metrics_involved=["cpu_usage", "memory_usage"]
            ))
        
        return insights
    
    def _check_error_patterns(self) -> List[PerformanceInsight]:
        """检查错误模式"""
        insights = []
        
        metrics_data = self.base_monitoring.get_metrics_history()
        error_rate_data = metrics_data.get("error_rate", [])
        
        if len(error_rate_data) >= 10:
            recent_errors = [point.value for point in error_rate_data[-10:]]
            avg_error_rate = statistics.mean(recent_errors)
            
            if avg_error_rate > 0.02:  # 错误率超过2%
                insights.append(PerformanceInsight(
                    insight_type="error_pattern",
                    title="错误率异常",
                    description=f"最近的平均错误率为 {avg_error_rate:.3f} ({avg_error_rate*100:.1f}%)",
                    impact="系统稳定性下降，用户体验受影响",
                    recommendation="检查错误日志，分析错误原因并修复相关问题",
                    confidence=0.9,
                    timestamp=datetime.now(),
                    metrics_involved=["error_rate"]
                ))
        
        return insights
    
    def _check_capacity_planning(self) -> List[PerformanceInsight]:
        """检查容量规划"""
        insights = []
        
        # 检查趋势预测
        metrics_data = self.base_monitoring.get_metrics_history()
        
        for metric_name in ["cpu_usage", "memory_usage", "disk_usage"]:
            data = metrics_data.get(metric_name, [])
            
            if len(data) >= 50:
                values = [point.value for point in data[-50:]]
                timestamps = [point.timestamp.timestamp() for point in data[-50:]]
                
                trend = self._calculate_trend(values, timestamps)
                
                if trend.direction == TrendDirection.INCREASING and trend.confidence > 0.7:
                    # 预测何时达到80%
                    current_value = values[-1]
                    if current_value < 80 and trend.slope > 0:
                        time_to_80 = (80 - current_value) / (trend.slope * 3600)  # 转换为小时
                        
                        if time_to_80 < 168:  # 一周内
                            insights.append(PerformanceInsight(
                                insight_type="capacity_planning",
                                title=f"{metric_name} 容量预警",
                                description=f"{metric_name} 呈上升趋势，预计 {time_to_80:.1f} 小时后达到80%",
                                impact="可能导致系统性能下降或服务中断",
                                recommendation="考虑扩容或优化资源使用",
                                confidence=trend.confidence,
                                timestamp=datetime.now(),
                                metrics_involved=[metric_name]
                            ))
        
        return insights
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system"):
        """
        确认告警
        
        Args:
            alert_id: 告警ID
            acknowledged_by: 确认人
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            
            self.logger.info(f"告警已确认: {alert_id} by {acknowledged_by}")
    
    def suppress_alert(self, alert_id: str):
        """
        抑制告警
        
        Args:
            alert_id: 告警ID
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            
            self.logger.info(f"告警已抑制: {alert_id}")
    
    def get_system_health(self) -> SystemHealth:
        """
        获取系统健康状态
        
        Returns:
            系统健康状态
        """
        # 计算组件分数
        component_scores = {}
        current_metrics = self.base_monitoring.get_current_metrics()
        
        # CPU分数
        cpu_usage = current_metrics.get("cpu_usage", 0)
        component_scores["cpu"] = max(0, 1 - cpu_usage / 100)
        
        # 内存分数
        memory_usage = current_metrics.get("memory_usage", 0)
        component_scores["memory"] = max(0, 1 - memory_usage / 100)
        
        # 错误率分数
        error_rate = current_metrics.get("error_rate", 0)
        component_scores["errors"] = max(0, 1 - error_rate * 10)
        
        # 响应时间分数
        response_time = current_metrics.get("response_time", 0)
        component_scores["response"] = max(0, 1 - response_time / 10)
        
        # 计算总体分数
        overall_score = statistics.mean(component_scores.values()) if component_scores else 0.5
        
        # 统计告警
        active_alerts_count = len(self.active_alerts)
        critical_alerts_count = len([
            alert for alert in self.active_alerts.values()
            if alert.severity == AlertSeverity.CRITICAL
        ])
        
        # 获取趋势
        trends = []
        metrics_data = self.base_monitoring.get_metrics_history()
        for metric_name, data in metrics_data.items():
            if len(data) >= 20:
                values = [point.value for point in data[-20:]]
                timestamps = [point.timestamp.timestamp() for point in data[-20:]]
                trend = self._calculate_trend(values, timestamps)
                trend.metric_name = metric_name
                trends.append(trend)
        
        # 获取最近的洞察
        recent_insights = [
            insight for insight in self.insights_history
            if insight.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        return SystemHealth(
            overall_score=overall_score,
            component_scores=component_scores,
            active_alerts=active_alerts_count,
            critical_alerts=critical_alerts_count,
            trends=trends,
            insights=recent_insights,
            timestamp=datetime.now()
        )
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 50) -> List[Alert]:
        """
        获取告警历史
        
        Args:
            limit: 返回数量限制
            
        Returns:
            告警历史列表
        """
        return self.alert_history[-limit:] if limit > 0 else self.alert_history
    
    def get_insights(self, limit: int = 20) -> List[PerformanceInsight]:
        """
        获取性能洞察
        
        Args:
            limit: 返回数量限制
            
        Returns:
            性能洞察列表
        """
        return self.insights_history[-limit:] if limit > 0 else self.insights_history
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        获取监控状态
        
        Returns:
            监控状态信息
        """
        system_health = self.get_system_health()
        
        return {
            "is_monitoring": self.is_monitoring,
            "system_health": asdict(system_health),
            "alert_rules_count": len(self.alert_rules),
            "active_alerts_count": len(self.active_alerts),
            "insights_count": len(self.insights_history),
            "prediction_enabled": self.prediction_enabled,
            "analysis_interval": self.analysis_interval
        } 