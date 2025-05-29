"""
医疗资源质量控制服务
负责医疗资源质量评估、服务效果跟踪、用户满意度监控等
"""

import asyncio
import json
import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """质量等级"""

    EXCELLENT = "excellent"  # 优秀 (90-100分)
    GOOD = "good"  # 良好 (80-89分)
    AVERAGE = "average"  # 一般 (70-79分)
    POOR = "poor"  # 较差 (60-69分)
    UNACCEPTABLE = "unacceptable"  # 不可接受 (<60分)


class QualityMetricType(Enum):
    """质量指标类型"""

    SERVICE_QUALITY = "service_quality"  # 服务质量
    RESOURCE_AVAILABILITY = "resource_availability"  # 资源可用性
    RESPONSE_TIME = "response_time"  # 响应时间
    ACCURACY = "accuracy"  # 准确性
    SATISFACTION = "satisfaction"  # 满意度
    EFFECTIVENESS = "effectiveness"  # 有效性
    SAFETY = "safety"  # 安全性
    COMPLIANCE = "compliance"  # 合规性


class FeedbackType(Enum):
    """反馈类型"""

    RATING = "rating"  # 评分反馈
    COMMENT = "comment"  # 评论反馈
    COMPLAINT = "complaint"  # 投诉反馈
    SUGGESTION = "suggestion"  # 建议反馈
    TESTIMONIAL = "testimonial"  # 推荐反馈


@dataclass
class QualityMetric:
    """质量指标"""

    metric_id: str
    metric_type: QualityMetricType
    resource_id: str
    resource_type: str
    value: float
    target_value: float
    unit: str
    timestamp: datetime
    measurement_period: timedelta
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceResult:
    """服务结果"""

    result_id: str
    service_type: str
    resource_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    outcome: str
    success: bool
    quality_score: float
    metrics: Dict[str, float]
    feedback: Optional[Dict[str, Any]] = None
    follow_up_required: bool = False


@dataclass
class UserFeedback:
    """用户反馈"""

    feedback_id: str
    user_id: str
    resource_id: str
    service_id: str
    feedback_type: FeedbackType
    rating: Optional[float]
    comment: Optional[str]
    timestamp: datetime
    sentiment_score: float
    categories: List[str]
    is_verified: bool = False
    response: Optional[str] = None


@dataclass
class QualityReport:
    """质量报告"""

    report_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[str, float]
    trends: Dict[str, List[float]]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityAlert:
    """质量预警"""

    alert_id: str
    alert_type: str
    severity: str
    resource_id: str
    metric_type: QualityMetricType
    current_value: float
    threshold_value: float
    description: str
    timestamp: datetime
    is_resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class ImprovementPlan:
    """改进计划"""

    plan_id: str
    resource_id: str
    issue_description: str
    improvement_actions: List[str]
    target_metrics: Dict[str, float]
    responsible_party: str
    start_date: datetime
    target_completion_date: datetime
    status: str
    progress: float = 0.0
    actual_completion_date: Optional[datetime] = None


class QualityControlService:
    """
    质量控制服务

    负责医疗资源质量评估、监控和改进
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_thresholds = config.get(
            "quality_thresholds",
            {
                QualityMetricType.SERVICE_QUALITY: 80.0,
                QualityMetricType.RESOURCE_AVAILABILITY: 90.0,
                QualityMetricType.RESPONSE_TIME: 5.0,  # 秒
                QualityMetricType.ACCURACY: 85.0,
                QualityMetricType.SATISFACTION: 80.0,
                QualityMetricType.EFFECTIVENESS: 75.0,
                QualityMetricType.SAFETY: 95.0,
                QualityMetricType.COMPLIANCE: 100.0,
            },
        )

        # 数据存储
        self.quality_metrics: Dict[str, List[QualityMetric]] = defaultdict(list)
        self.service_results: Dict[str, ServiceResult] = {}
        self.user_feedback: Dict[str, List[UserFeedback]] = defaultdict(list)
        self.quality_reports: List[QualityReport] = []
        self.quality_alerts: List[QualityAlert] = []
        self.improvement_plans: Dict[str, ImprovementPlan] = {}

        # 实时监控
        self.monitoring_enabled = True
        self.alert_queue = asyncio.Queue()
        self.metric_buffer = defaultdict(lambda: deque(maxlen=1000))

        # 统计数据
        self.quality_stats = {
            "total_evaluations": 0,
            "average_quality_score": 0.0,
            "quality_trends": defaultdict(list),
            "alert_counts": defaultdict(int),
            "improvement_success_rate": 0.0,
        }

        logger.info("质量控制服务初始化完成")

    async def record_quality_metric(
        self,
        resource_id: str,
        resource_type: str,
        metric_type: QualityMetricType,
        value: float,
        target_value: float = None,
        unit: str = "",
        metadata: Dict[str, Any] = None,
    ) -> str:
        """记录质量指标"""
        try:
            metric_id = (
                f"metric_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{resource_id}"
            )

            if target_value is None:
                target_value = self.quality_thresholds.get(metric_type, 80.0)

            metric = QualityMetric(
                metric_id=metric_id,
                metric_type=metric_type,
                resource_id=resource_id,
                resource_type=resource_type,
                value=value,
                target_value=target_value,
                unit=unit,
                timestamp=datetime.now(),
                measurement_period=timedelta(hours=1),
                metadata=metadata or {},
            )

            self.quality_metrics[resource_id].append(metric)
            self.metric_buffer[f"{resource_id}_{metric_type.value}"].append(value)

            # 检查是否需要预警
            await self._check_quality_alert(metric)

            # 更新统计
            self.quality_stats["total_evaluations"] += 1
            self._update_quality_trends(resource_id, metric_type, value)

            logger.info(f"记录质量指标: {resource_id} - {metric_type.value}: {value}")
            return metric_id

        except Exception as e:
            logger.error(f"记录质量指标失败: {e}")
            raise

    async def record_service_result(
        self,
        service_type: str,
        resource_id: str,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        outcome: str,
        success: bool,
        metrics: Dict[str, float] = None,
    ) -> str:
        """记录服务结果"""
        try:
            result_id = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"

            # 计算质量分数
            quality_score = await self._calculate_service_quality_score(
                service_type, metrics or {}, success
            )

            result = ServiceResult(
                result_id=result_id,
                service_type=service_type,
                resource_id=resource_id,
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                outcome=outcome,
                success=success,
                quality_score=quality_score,
                metrics=metrics or {},
                follow_up_required=quality_score < 70.0,
            )

            self.service_results[result_id] = result

            # 记录相关质量指标
            await self.record_quality_metric(
                resource_id=resource_id,
                resource_type="service",
                metric_type=QualityMetricType.SERVICE_QUALITY,
                value=quality_score,
            )

            logger.info(f"记录服务结果: {result_id} - 质量分数: {quality_score}")
            return result_id

        except Exception as e:
            logger.error(f"记录服务结果失败: {e}")
            raise

    async def collect_user_feedback(
        self,
        user_id: str,
        resource_id: str,
        service_id: str,
        feedback_type: FeedbackType,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> str:
        """收集用户反馈"""
        try:
            feedback_id = (
                f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            )

            # 情感分析
            sentiment_score = await self._analyze_sentiment(comment) if comment else 0.0

            # 分类标签
            categories = (
                await self._categorize_feedback(comment, rating) if comment else []
            )

            feedback = UserFeedback(
                feedback_id=feedback_id,
                user_id=user_id,
                resource_id=resource_id,
                service_id=service_id,
                feedback_type=feedback_type,
                rating=rating,
                comment=comment,
                timestamp=datetime.now(),
                sentiment_score=sentiment_score,
                categories=categories,
            )

            self.user_feedback[resource_id].append(feedback)

            # 更新满意度指标
            if rating is not None:
                await self.record_quality_metric(
                    resource_id=resource_id,
                    resource_type="feedback",
                    metric_type=QualityMetricType.SATISFACTION,
                    value=rating * 20,  # 转换为百分制
                    unit="分",
                )

            logger.info(f"收集用户反馈: {feedback_id} - 评分: {rating}")
            return feedback_id

        except Exception as e:
            logger.error(f"收集用户反馈失败: {e}")
            raise

    async def evaluate_resource_quality(
        self, resource_id: str, evaluation_period: timedelta = None
    ) -> Dict[str, Any]:
        """评估资源质量"""
        try:
            if evaluation_period is None:
                evaluation_period = timedelta(days=30)

            end_time = datetime.now()
            start_time = end_time - evaluation_period

            # 获取评估期间的指标
            metrics = self._get_metrics_in_period(resource_id, start_time, end_time)
            feedback = self._get_feedback_in_period(resource_id, start_time, end_time)
            results = self._get_results_in_period(resource_id, start_time, end_time)

            # 计算各维度分数
            quality_scores = {}

            # 服务质量分数
            if results:
                quality_scores["service_quality"] = statistics.mean(
                    [r.quality_score for r in results]
                )

            # 满意度分数
            if feedback:
                ratings = [f.rating * 20 for f in feedback if f.rating is not None]
                if ratings:
                    quality_scores["satisfaction"] = statistics.mean(ratings)

            # 可用性分数
            availability_metrics = [
                m
                for m in metrics
                if m.metric_type == QualityMetricType.RESOURCE_AVAILABILITY
            ]
            if availability_metrics:
                quality_scores["availability"] = statistics.mean(
                    [m.value for m in availability_metrics]
                )

            # 响应时间分数
            response_metrics = [
                m for m in metrics if m.metric_type == QualityMetricType.RESPONSE_TIME
            ]
            if response_metrics:
                avg_response_time = statistics.mean([m.value for m in response_metrics])
                # 响应时间越短分数越高
                quality_scores["response_time"] = max(0, 100 - avg_response_time * 10)

            # 计算综合质量分数
            if quality_scores:
                overall_score = statistics.mean(quality_scores.values())
                quality_level = self._determine_quality_level(overall_score)
            else:
                overall_score = 0.0
                quality_level = QualityLevel.UNACCEPTABLE

            evaluation_result = {
                "resource_id": resource_id,
                "evaluation_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                },
                "overall_score": overall_score,
                "quality_level": quality_level.value,
                "dimension_scores": quality_scores,
                "metrics_count": len(metrics),
                "feedback_count": len(feedback),
                "service_results_count": len(results),
                "recommendations": await self._generate_quality_recommendations(
                    resource_id, quality_scores, overall_score
                ),
            }

            logger.info(f"资源质量评估完成: {resource_id} - 综合分数: {overall_score}")
            return evaluation_result

        except Exception as e:
            logger.error(f"评估资源质量失败: {e}")
            raise

    async def generate_quality_report(
        self, report_type: str = "monthly", resource_ids: List[str] = None
    ) -> QualityReport:
        """生成质量报告"""
        try:
            # 确定报告周期
            end_time = datetime.now()
            if report_type == "daily":
                start_time = end_time - timedelta(days=1)
            elif report_type == "weekly":
                start_time = end_time - timedelta(weeks=1)
            elif report_type == "monthly":
                start_time = end_time - timedelta(days=30)
            elif report_type == "quarterly":
                start_time = end_time - timedelta(days=90)
            else:
                start_time = end_time - timedelta(days=30)

            report_id = (
                f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # 收集数据
            all_metrics = []
            all_feedback = []
            all_results = []

            target_resources = resource_ids or list(self.quality_metrics.keys())

            for resource_id in target_resources:
                all_metrics.extend(
                    self._get_metrics_in_period(resource_id, start_time, end_time)
                )
                all_feedback.extend(
                    self._get_feedback_in_period(resource_id, start_time, end_time)
                )
                all_results.extend(
                    self._get_results_in_period(resource_id, start_time, end_time)
                )

            # 计算整体指标
            overall_metrics = {}

            if all_results:
                overall_metrics["average_service_quality"] = statistics.mean(
                    [r.quality_score for r in all_results]
                )
                overall_metrics["service_success_rate"] = (
                    sum(1 for r in all_results if r.success) / len(all_results) * 100
                )

            if all_feedback:
                ratings = [f.rating * 20 for f in all_feedback if f.rating is not None]
                if ratings:
                    overall_metrics["average_satisfaction"] = statistics.mean(ratings)

            # 计算趋势
            trends = self._calculate_quality_trends(all_metrics, start_time, end_time)

            # 识别问题
            issues = await self._identify_quality_issues(
                all_metrics, all_feedback, all_results
            )

            # 生成建议
            recommendations = await self._generate_report_recommendations(
                overall_metrics, issues
            )

            # 计算综合分数
            if overall_metrics:
                overall_score = statistics.mean(overall_metrics.values())
            else:
                overall_score = 0.0

            quality_level = self._determine_quality_level(overall_score)

            report = QualityReport(
                report_id=report_id,
                report_type=report_type,
                period_start=start_time,
                period_end=end_time,
                overall_score=overall_score,
                quality_level=quality_level,
                metrics=overall_metrics,
                trends=trends,
                issues=issues,
                recommendations=recommendations,
            )

            self.quality_reports.append(report)

            logger.info(f"生成质量报告: {report_id} - 综合分数: {overall_score}")
            return report

        except Exception as e:
            logger.error(f"生成质量报告失败: {e}")
            raise

    async def create_improvement_plan(
        self,
        resource_id: str,
        issue_description: str,
        improvement_actions: List[str],
        target_metrics: Dict[str, float],
        responsible_party: str,
        target_completion_date: datetime,
    ) -> str:
        """创建改进计划"""
        try:
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{resource_id}"

            plan = ImprovementPlan(
                plan_id=plan_id,
                resource_id=resource_id,
                issue_description=issue_description,
                improvement_actions=improvement_actions,
                target_metrics=target_metrics,
                responsible_party=responsible_party,
                start_date=datetime.now(),
                target_completion_date=target_completion_date,
                status="planned",
            )

            self.improvement_plans[plan_id] = plan

            logger.info(f"创建改进计划: {plan_id} - 资源: {resource_id}")
            return plan_id

        except Exception as e:
            logger.error(f"创建改进计划失败: {e}")
            raise

    async def update_improvement_progress(
        self, plan_id: str, progress: float, status: str = None
    ):
        """更新改进进度"""
        try:
            if plan_id not in self.improvement_plans:
                raise ValueError(f"改进计划不存在: {plan_id}")

            plan = self.improvement_plans[plan_id]
            plan.progress = progress

            if status:
                plan.status = status

            if progress >= 100.0 and status != "completed":
                plan.status = "completed"
                plan.actual_completion_date = datetime.now()

            logger.info(f"更新改进进度: {plan_id} - 进度: {progress}%")

        except Exception as e:
            logger.error(f"更新改进进度失败: {e}")
            raise

    async def get_quality_dashboard(self) -> Dict[str, Any]:
        """获取质量控制仪表板数据"""
        try:
            # 计算关键指标
            recent_metrics = []
            recent_feedback = []
            recent_results = []

            cutoff_time = datetime.now() - timedelta(days=7)

            for resource_id in self.quality_metrics.keys():
                recent_metrics.extend(
                    self._get_metrics_in_period(
                        resource_id, cutoff_time, datetime.now()
                    )
                )
                recent_feedback.extend(
                    self._get_feedback_in_period(
                        resource_id, cutoff_time, datetime.now()
                    )
                )
                recent_results.extend(
                    self._get_results_in_period(
                        resource_id, cutoff_time, datetime.now()
                    )
                )

            # 活跃预警
            active_alerts = [
                alert for alert in self.quality_alerts if not alert.is_resolved
            ]

            # 进行中的改进计划
            active_plans = [
                plan
                for plan in self.improvement_plans.values()
                if plan.status in ["planned", "in_progress"]
            ]

            dashboard = {
                "overview": {
                    "total_resources_monitored": len(self.quality_metrics),
                    "total_evaluations": self.quality_stats["total_evaluations"],
                    "average_quality_score": self.quality_stats[
                        "average_quality_score"
                    ],
                    "active_alerts": len(active_alerts),
                    "active_improvement_plans": len(active_plans),
                },
                "recent_activity": {
                    "metrics_recorded": len(recent_metrics),
                    "feedback_collected": len(recent_feedback),
                    "services_evaluated": len(recent_results),
                },
                "quality_distribution": self._calculate_quality_distribution(),
                "top_issues": await self._get_top_quality_issues(),
                "improvement_success_rate": self.quality_stats[
                    "improvement_success_rate"
                ],
                "alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "severity": alert.severity,
                        "resource_id": alert.resource_id,
                        "description": alert.description,
                        "timestamp": alert.timestamp.isoformat(),
                    }
                    for alert in active_alerts[:10]  # 最近10个预警
                ],
            }

            return dashboard

        except Exception as e:
            logger.error(f"获取质量控制仪表板失败: {e}")
            raise

    # 私有方法

    async def _check_quality_alert(self, metric: QualityMetric):
        """检查质量预警"""
        try:
            threshold = self.quality_thresholds.get(metric.metric_type)
            if threshold is None:
                return

            # 检查是否低于阈值
            if metric.value < threshold:
                severity = "high" if metric.value < threshold * 0.8 else "medium"

                alert = QualityAlert(
                    alert_id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{metric.resource_id}",
                    alert_type="quality_threshold",
                    severity=severity,
                    resource_id=metric.resource_id,
                    metric_type=metric.metric_type,
                    current_value=metric.value,
                    threshold_value=threshold,
                    description=f"{metric.metric_type.value}指标低于阈值: {metric.value} < {threshold}",
                    timestamp=datetime.now(),
                )

                self.quality_alerts.append(alert)
                await self.alert_queue.put(alert)

                self.quality_stats["alert_counts"][metric.metric_type.value] += 1

                logger.warning(f"质量预警: {alert.description}")

        except Exception as e:
            logger.error(f"检查质量预警失败: {e}")

    async def _calculate_service_quality_score(
        self, service_type: str, metrics: Dict[str, float], success: bool
    ) -> float:
        """计算服务质量分数"""
        try:
            base_score = 80.0 if success else 40.0

            # 根据具体指标调整分数
            if "response_time" in metrics:
                response_time = metrics["response_time"]
                if response_time <= 2.0:
                    base_score += 10
                elif response_time <= 5.0:
                    base_score += 5
                elif response_time > 10.0:
                    base_score -= 10

            if "accuracy" in metrics:
                accuracy = metrics["accuracy"]
                base_score += (accuracy - 80) * 0.2

            if "completeness" in metrics:
                completeness = metrics["completeness"]
                base_score += (completeness - 80) * 0.1

            return max(0, min(100, base_score))

        except Exception as e:
            logger.error(f"计算服务质量分数失败: {e}")
            return 50.0

    async def _analyze_sentiment(self, comment: str) -> float:
        """分析评论情感"""
        try:
            # 简单的情感分析实现
            positive_words = ["好", "满意", "优秀", "专业", "及时", "有效", "推荐"]
            negative_words = ["差", "不满", "失望", "延误", "无效", "态度", "问题"]

            positive_count = sum(1 for word in positive_words if word in comment)
            negative_count = sum(1 for word in negative_words if word in comment)

            if positive_count + negative_count == 0:
                return 0.0

            sentiment = (positive_count - negative_count) / (
                positive_count + negative_count
            )
            return sentiment

        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return 0.0

    async def _categorize_feedback(self, comment: str, rating: float) -> List[str]:
        """分类反馈"""
        try:
            categories = []

            if rating is not None:
                if rating >= 4.0:
                    categories.append("positive")
                elif rating <= 2.0:
                    categories.append("negative")
                else:
                    categories.append("neutral")

            if comment:
                if any(word in comment for word in ["服务", "态度", "专业"]):
                    categories.append("service_quality")
                if any(word in comment for word in ["时间", "等待", "延误"]):
                    categories.append("timeliness")
                if any(word in comment for word in ["效果", "治疗", "康复"]):
                    categories.append("effectiveness")
                if any(word in comment for word in ["环境", "设施", "设备"]):
                    categories.append("facilities")

            return categories

        except Exception as e:
            logger.error(f"分类反馈失败: {e}")
            return []

    def _get_metrics_in_period(
        self, resource_id: str, start_time: datetime, end_time: datetime
    ) -> List[QualityMetric]:
        """获取时间段内的指标"""
        metrics = self.quality_metrics.get(resource_id, [])
        return [m for m in metrics if start_time <= m.timestamp <= end_time]

    def _get_feedback_in_period(
        self, resource_id: str, start_time: datetime, end_time: datetime
    ) -> List[UserFeedback]:
        """获取时间段内的反馈"""
        feedback = self.user_feedback.get(resource_id, [])
        return [f for f in feedback if start_time <= f.timestamp <= end_time]

    def _get_results_in_period(
        self, resource_id: str, start_time: datetime, end_time: datetime
    ) -> List[ServiceResult]:
        """获取时间段内的服务结果"""
        results = [
            r for r in self.service_results.values() if r.resource_id == resource_id
        ]
        return [r for r in results if start_time <= r.end_time <= end_time]

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """确定质量等级"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 70:
            return QualityLevel.AVERAGE
        elif score >= 60:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE

    async def _generate_quality_recommendations(
        self, resource_id: str, quality_scores: Dict[str, float], overall_score: float
    ) -> List[str]:
        """生成质量改进建议"""
        recommendations = []

        if overall_score < 70:
            recommendations.append("整体质量需要显著改进，建议制定综合改进计划")

        if "satisfaction" in quality_scores and quality_scores["satisfaction"] < 75:
            recommendations.append("用户满意度较低，建议加强服务培训和沟通技巧")

        if "response_time" in quality_scores and quality_scores["response_time"] < 70:
            recommendations.append("响应时间过长，建议优化流程和增加资源配置")

        if "availability" in quality_scores and quality_scores["availability"] < 85:
            recommendations.append("资源可用性不足，建议增加备用资源或优化调度")

        return recommendations

    def _update_quality_trends(
        self, resource_id: str, metric_type: QualityMetricType, value: float
    ):
        """更新质量趋势"""
        trend_key = f"{resource_id}_{metric_type.value}"
        self.quality_stats["quality_trends"][trend_key].append(
            {"timestamp": datetime.now().isoformat(), "value": value}
        )

        # 保持最近100个数据点
        if len(self.quality_stats["quality_trends"][trend_key]) > 100:
            self.quality_stats["quality_trends"][trend_key] = self.quality_stats[
                "quality_trends"
            ][trend_key][-100:]

    def _calculate_quality_trends(
        self, metrics: List[QualityMetric], start_time: datetime, end_time: datetime
    ) -> Dict[str, List[float]]:
        """计算质量趋势"""
        trends = defaultdict(list)

        # 按指标类型分组
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_type].append(metric)

        # 计算每种指标的趋势
        for metric_type, metric_list in metric_groups.items():
            # 按时间排序
            sorted_metrics = sorted(metric_list, key=lambda x: x.timestamp)
            values = [m.value for m in sorted_metrics]
            trends[metric_type.value] = values

        return dict(trends)

    async def _identify_quality_issues(
        self,
        metrics: List[QualityMetric],
        feedback: List[UserFeedback],
        results: List[ServiceResult],
    ) -> List[Dict[str, Any]]:
        """识别质量问题"""
        issues = []

        # 分析指标问题
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_type].append(metric.value)

        for metric_type, values in metric_groups.items():
            if values:
                avg_value = statistics.mean(values)
                threshold = self.quality_thresholds.get(metric_type, 80.0)

                if avg_value < threshold:
                    issues.append(
                        {
                            "type": "metric_below_threshold",
                            "metric_type": metric_type.value,
                            "average_value": avg_value,
                            "threshold": threshold,
                            "severity": (
                                "high" if avg_value < threshold * 0.8 else "medium"
                            ),
                        }
                    )

        # 分析反馈问题
        negative_feedback = [f for f in feedback if f.rating and f.rating <= 2.0]
        if len(negative_feedback) > len(feedback) * 0.2:  # 超过20%负面反馈
            issues.append(
                {
                    "type": "high_negative_feedback",
                    "negative_count": len(negative_feedback),
                    "total_count": len(feedback),
                    "percentage": len(negative_feedback) / len(feedback) * 100,
                    "severity": "high",
                }
            )

        # 分析服务失败问题
        failed_results = [r for r in results if not r.success]
        if len(failed_results) > len(results) * 0.1:  # 超过10%失败率
            issues.append(
                {
                    "type": "high_failure_rate",
                    "failed_count": len(failed_results),
                    "total_count": len(results),
                    "failure_rate": len(failed_results) / len(results) * 100,
                    "severity": "high",
                }
            )

        return issues

    async def _generate_report_recommendations(
        self, metrics: Dict[str, float], issues: List[Dict[str, Any]]
    ) -> List[str]:
        """生成报告建议"""
        recommendations = []

        # 基于问题生成建议
        for issue in issues:
            if issue["type"] == "metric_below_threshold":
                recommendations.append(
                    f"改进{issue['metric_type']}指标，当前值{issue['average_value']:.1f}低于阈值{issue['threshold']:.1f}"
                )
            elif issue["type"] == "high_negative_feedback":
                recommendations.append(
                    f"关注用户满意度，负面反馈比例达到{issue['percentage']:.1f}%"
                )
            elif issue["type"] == "high_failure_rate":
                recommendations.append(
                    f"降低服务失败率，当前失败率为{issue['failure_rate']:.1f}%"
                )

        # 基于整体表现生成建议
        if (
            "average_service_quality" in metrics
            and metrics["average_service_quality"] < 80
        ):
            recommendations.append("整体服务质量需要改进，建议加强培训和流程优化")

        if "service_success_rate" in metrics and metrics["service_success_rate"] < 90:
            recommendations.append("提高服务成功率，分析失败原因并制定预防措施")

        return recommendations

    def _calculate_quality_distribution(self) -> Dict[str, int]:
        """计算质量分布"""
        distribution = {level.value: 0 for level in QualityLevel}

        # 统计最近的质量评估结果
        recent_scores = []
        cutoff_time = datetime.now() - timedelta(days=30)

        for results in self.service_results.values():
            if results.end_time >= cutoff_time:
                recent_scores.append(results.quality_score)

        for score in recent_scores:
            level = self._determine_quality_level(score)
            distribution[level.value] += 1

        return distribution

    async def _get_top_quality_issues(self) -> List[Dict[str, Any]]:
        """获取主要质量问题"""
        issues = []

        # 统计预警频率
        alert_counts = defaultdict(int)
        recent_alerts = [
            a
            for a in self.quality_alerts
            if a.timestamp >= datetime.now() - timedelta(days=30)
        ]

        for alert in recent_alerts:
            alert_counts[alert.metric_type.value] += 1

        # 转换为问题列表
        for metric_type, count in sorted(
            alert_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            issues.append(
                {
                    "issue_type": metric_type,
                    "alert_count": count,
                    "description": f"{metric_type}相关问题",
                }
            )

        return issues
