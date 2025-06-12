"""
analytics - 索克生活项目模块
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from user_service.config import get_settings
import json
import structlog

"""用户服务分析模块"""



logger = structlog.get_logger()


class HealthMetricType(Enum):
    """健康指标类型"""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    WEIGHT = "weight"
    STEPS = "steps"
    SLEEP = "sleep"
    EXERCISE = "exercise"
    NUTRITION = "nutrition"


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HealthInsight:
    """健康洞察"""
    metric_type: HealthMetricType
    insight_type: str
    title: str
    description: str
    risk_level: RiskLevel
    recommendations: List[str]
    confidence: float
    timestamp: datetime


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    age_group: str
    activity_level: str
    health_goals: List[str]
    risk_factors: List[str]
    preferences: Dict[str, Any]
    engagement_score: float
    last_updated: datetime


class HealthDataAnalyzer:
    """健康数据分析器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.settings = get_settings()

    def analyze_heart_rate_trends(self, heart_rate_data: List[Dict]) -> List[HealthInsight]:
        """分析心率趋势"""
        insights = []

        if not heart_rate_data:
            return insights

        # 计算平均心率
        avg_hr = sum(data["value"] for data in heart_rate_data) / len(heart_rate_data)

        # 检查异常心率
        high_hr_count = sum(1 for data in heart_rate_data if data["value"] > 100)
        low_hr_count = sum(1 for data in heart_rate_data if data["value"] < 60)

        if high_hr_count > len(heart_rate_data) * 0.3:
            insights.append(HealthInsight(
                metric_type = HealthMetricType.HEART_RATE,
                insight_type = "trend_analysis",
                title = "心率偏高趋势",
                description = f"您的心率在30%的时间内超过100次 / 分钟，平均心率为{avg_hr:.1f}次 / 分钟",
                risk_level = RiskLevel.MEDIUM,
                recommendations = [
                    "建议减少咖啡因摄入",
                    "增加有氧运动",
                    "保持充足睡眠",
                    "如持续异常请咨询医生"
                ],
                confidence = 0.8,
                timestamp = datetime.utcnow()
            ))

        if low_hr_count > len(heart_rate_data) * 0.2:
            insights.append(HealthInsight(
                metric_type = HealthMetricType.HEART_RATE,
                insight_type = "trend_analysis",
                title = "心率偏低趋势",
                description = f"您的心率在20%的时间内低于60次 / 分钟",
                risk_level = RiskLevel.LOW,
                recommendations = [
                    "这可能表明良好的心血管健康",
                    "如伴有头晕等症状请咨询医生"
                ],
                confidence = 0.7,
                timestamp = datetime.utcnow()
            ))

        return insights

    def analyze_sleep_patterns(self, sleep_data: List[Dict]) -> List[HealthInsight]:
        """分析睡眠模式"""
        insights = []

        if not sleep_data:
            return insights

        # 计算平均睡眠时长
        avg_sleep = sum(data["duration"] for data in sleep_data) / len(sleep_data)

        # 分析睡眠质量
        poor_sleep_count = sum(1 for data in sleep_data if data.get("quality", 0) < 3)

        if avg_sleep < 7:
            insights.append(HealthInsight(
                metric_type = HealthMetricType.SLEEP,
                insight_type = "duration_analysis",
                title = "睡眠不足",
                description = f"您的平均睡眠时长为{avg_sleep:.1f}小时，低于推荐的7 - 9小时",
                risk_level = RiskLevel.MEDIUM,
                recommendations = [
                    "建立规律的睡眠时间",
                    "睡前避免使用电子设备",
                    "创造舒适的睡眠环境",
                    "避免睡前饮用咖啡因"
                ],
                confidence = 0.9,
                timestamp = datetime.utcnow()
            ))

        if poor_sleep_count > len(sleep_data) * 0.4:
            insights.append(HealthInsight(
                metric_type = HealthMetricType.SLEEP,
                insight_type = "quality_analysis",
                title = "睡眠质量较差",
                description = "您有40%以上的夜晚睡眠质量评分较低",
                risk_level = RiskLevel.MEDIUM,
                recommendations = [
                    "检查睡眠环境是否安静舒适",
                    "考虑使用放松技巧",
                    "如持续问题请咨询睡眠专家"
                ],
                confidence = 0.8,
                timestamp = datetime.utcnow()
            ))

        return insights

    def analyze_activity_levels(self, activity_data: List[Dict]) -> List[HealthInsight]:
        """分析活动水平"""
        insights = []

        if not activity_data:
            return insights

        # 计算平均步数
        avg_steps = sum(data.get("steps", 0) for data in activity_data) / len(activity_data)

        # 分析活动趋势
        if avg_steps < 5000:
            insights.append(HealthInsight(
                metric_type = HealthMetricType.STEPS,
                insight_type = "activity_analysis",
                title = "活动量不足",
                description = f"您的平均日步数为{avg_steps:.0f}步，低于推荐的10000步",
                risk_level = RiskLevel.MEDIUM,
                recommendations = [
                    "尝试每天增加1000步",
                    "使用楼梯代替电梯",
                    "安排定期散步时间",
                    "设置活动提醒"
                ],
                confidence = 0.9,
                timestamp = datetime.utcnow()
            ))
        elif avg_steps > 12000:
            insights.append(HealthInsight(
                metric_type = HealthMetricType.STEPS,
                insight_type = "activity_analysis",
                title = "活动量优秀",
                description = f"您的平均日步数为{avg_steps:.0f}步，超过推荐标准",
                risk_level = RiskLevel.LOW,
                recommendations = [
                    "保持当前的活动水平",
                    "注意适当休息避免过度疲劳",
                    "可以尝试多样化的运动形式"
                ],
                confidence = 0.9,
                timestamp = datetime.utcnow()
            ))

        return insights

    def analyze_weight_trends(self, weight_data: List[Dict]) -> List[HealthInsight]:
        """分析体重趋势"""
        insights = []

        if len(weight_data) < 2:
            return insights

        # 计算体重变化趋势
        recent_weights = sorted(weight_data, key = lambda x: x["date"])[ - 7:]  # 最近7天
        if len(recent_weights)>=2:
            weight_change = recent_weights[ - 1]["value"] - recent_weights[0]["value"]

            if weight_change > 2:  # 一周增重超过2kg
                insights.append(HealthInsight(
                    metric_type = HealthMetricType.WEIGHT,
                    insight_type = "trend_analysis",
                    title = "体重快速增加",
                    description = f"最近一周体重增加了{weight_change:.1f}kg",
                    risk_level = RiskLevel.MEDIUM,
                    recommendations = [
                        "检查饮食习惯",
                        "增加运动量",
                        "监控水分摄入",
                        "如持续快速增重请咨询医生"
                    ],
                    confidence = 0.8,
                    timestamp = datetime.utcnow()
                ))
            elif weight_change < - 2:  # 一周减重超过2kg
                insights.append(HealthInsight(
                    metric_type = HealthMetricType.WEIGHT,
                    insight_type = "trend_analysis",
                    title = "体重快速下降",
                    description = f"最近一周体重减少了{abs(weight_change):.1f}kg",
                    risk_level = RiskLevel.MEDIUM,
                    recommendations = [
                        "确保营养摄入充足",
                        "检查是否有疾病症状",
                        "如非故意减重请咨询医生"
                    ],
                    confidence = 0.8,
                    timestamp = datetime.utcnow()
                ))

        return insights

    def generate_comprehensive_report(self, user_data: Dict) -> Dict[str, Any]:
        """生成综合健康报告"""
        all_insights = []

        # 分析各项健康数据
        if "heart_rate" in user_data:
            all_insights.extend(self.analyze_heart_rate_trends(user_data["heart_rate"]))

        if "sleep" in user_data:
            all_insights.extend(self.analyze_sleep_patterns(user_data["sleep"]))

        if "activity" in user_data:
            all_insights.extend(self.analyze_activity_levels(user_data["activity"]))

        if "weight" in user_data:
            all_insights.extend(self.analyze_weight_trends(user_data["weight"]))

        # 计算整体健康评分
        health_score = self._calculate_health_score(user_data, all_insights)

        # 生成个性化建议
        personalized_recommendations = self._generate_personalized_recommendations(all_insights)

        return {
            "health_score": health_score,
            "insights": [
                {
                    "metric_type": insight.metric_type.value,
                    "insight_type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "risk_level": insight.risk_level.value,
                    "recommendations": insight.recommendations,
                    "confidence": insight.confidence,
                    "timestamp": insight.timestamp.isoformat()
                }
                for insight in all_insights
            ],
            "recommendations": personalized_recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _calculate_health_score(self, user_data: Dict, insights: List[HealthInsight]) -> float:
        """计算健康评分"""
        base_score = 100.0

        # 根据洞察调整评分
        for insight in insights:
            if insight.risk_level==RiskLevel.CRITICAL:
                base_score-=20 * insight.confidence
            elif insight.risk_level==RiskLevel.HIGH:
                base_score-=15 * insight.confidence
            elif insight.risk_level==RiskLevel.MEDIUM:
                base_score-=10 * insight.confidence
            elif insight.risk_level==RiskLevel.LOW:
                base_score+=5 * insight.confidence

        return max(0, min(100, base_score))

    def _generate_personalized_recommendations(self, insights: List[HealthInsight]) -> List[str]:
        """生成个性化建议"""
        recommendations = set()

        # 收集所有建议
        for insight in insights:
            recommendations.update(insight.recommendations)

        # 按优先级排序（高风险的建议优先）
        prioritized = []
        for insight in sorted(insights, key = lambda x: x.risk_level.value, reverse = True):
            for rec in insight.recommendations:
                if rec not in prioritized:
                    prioritized.append(rec)

        return prioritized[:10]  # 返回前10个建议


class UserProfileAnalyzer:
    """用户画像分析器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.settings = get_settings()

    def analyze_user_behavior(self, user_id: str, activity_data: List[Dict]) -> UserProfile:
        """分析用户行为生成画像"""

        # 分析年龄组
        age_group = self._determine_age_group(activity_data)

        # 分析活动水平
        activity_level = self._determine_activity_level(activity_data)

        # 推断健康目标
        health_goals = self._infer_health_goals(activity_data)

        # 识别风险因素
        risk_factors = self._identify_risk_factors(activity_data)

        # 分析偏好
        preferences = self._analyze_preferences(activity_data)

        # 计算参与度评分
        engagement_score = self._calculate_engagement_score(activity_data)

        return UserProfile(
            user_id = user_id,
            age_group = age_group,
            activity_level = activity_level,
            health_goals = health_goals,
            risk_factors = risk_factors,
            preferences = preferences,
            engagement_score = engagement_score,
            last_updated = datetime.utcnow()
        )

    def _determine_age_group(self, activity_data: List[Dict]) -> str:
        """确定年龄组"""
        # 基于活动模式推断年龄组
        # 这里是简化的逻辑，实际应该基于更多数据
        avg_activity = sum(data.get("steps", 0) for data in activity_data) / len(activity_data) if activity_data else 0

        if avg_activity > 12000:
            return "young_adult"  # 年轻成人
        elif avg_activity > 8000:
            return "middle_aged"  # 中年
        else:
            return "senior"  # 老年

    def _determine_activity_level(self, activity_data: List[Dict]) -> str:
        """确定活动水平"""
        if not activity_data:
            return "sedentary"

        avg_steps = sum(data.get("steps", 0) for data in activity_data) / len(activity_data)

        if avg_steps < 5000:
            return "sedentary"  # 久坐
        elif avg_steps < 8000:
            return "lightly_active"  # 轻度活跃
        elif avg_steps < 12000:
            return "moderately_active"  # 中度活跃
        else:
            return "very_active"  # 高度活跃

    def _infer_health_goals(self, activity_data: List[Dict]) -> List[str]:
        """推断健康目标"""
        goals = []

        if not activity_data:
            return ["general_wellness"]

        avg_steps = sum(data.get("steps", 0) for data in activity_data) / len(activity_data)

        if avg_steps > 10000:
            goals.append("fitness_improvement")

        # 检查是否有规律的运动模式
        exercise_days = sum(1 for data in activity_data if data.get("exercise_minutes", 0) > 30)
        if exercise_days > len(activity_data) * 0.5:
            goals.append("weight_management")

        if not goals:
            goals.append("general_wellness")

        return goals

    def _identify_risk_factors(self, activity_data: List[Dict]) -> List[str]:
        """识别风险因素"""
        risk_factors = []

        if not activity_data:
            return risk_factors

        avg_steps = sum(data.get("steps", 0) for data in activity_data) / len(activity_data)

        if avg_steps < 5000:
            risk_factors.append("sedentary_lifestyle")

        # 检查睡眠不足
        sleep_data = [data for data in activity_data if "sleep_hours" in data]
        if sleep_data:
            avg_sleep = sum(data["sleep_hours"] for data in sleep_data) / len(sleep_data)
            if avg_sleep < 7:
                risk_factors.append("insufficient_sleep")

        return risk_factors

    def _analyze_preferences(self, activity_data: List[Dict]) -> Dict[str, Any]:
        """分析用户偏好"""
        preferences = {
            "preferred_activity_time": "morning",  # 默认
            "activity_consistency": 0.0,
            "data_tracking_frequency": "daily"
        }

        if not activity_data:
            return preferences

        # 分析活动一致性
        daily_steps = [data.get("steps", 0) for data in activity_data]
        if daily_steps:
            avg_steps = sum(daily_steps) / len(daily_steps)
            variance = sum((steps - avg_steps)**2 for steps in daily_steps) / len(daily_steps)
            consistency = max(0, 1 - (variance / (avg_steps**2)) if avg_steps > 0 else 0)
            preferences["activity_consistency"] = consistency

        return preferences

    def _calculate_engagement_score(self, activity_data: List[Dict]) -> float:
        """计算参与度评分"""
        if not activity_data:
            return 0.0

        # 基于数据记录频率和质量计算参与度
        data_completeness = len(activity_data) / 30  # 假设30天为基准

        # 检查数据质量
        quality_score = 0.0
        for data in activity_data:
            if data.get("steps", 0) > 0:
                quality_score+=0.3
            if data.get("sleep_hours", 0) > 0:
                quality_score+=0.3
            if data.get("exercise_minutes", 0) > 0:
                quality_score+=0.4

        quality_score = quality_score / len(activity_data) if activity_data else 0

        return min(1.0, (data_completeness * 0.6 + quality_score * 0.4))


class RecommendationEngine:
    """推荐引擎"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.settings = get_settings()

    def generate_personalized_recommendations(
        self,
        user_profile: UserProfile,
        health_insights: List[HealthInsight]
    ) -> List[Dict[str, Any]]:
        """生成个性化推荐"""
        recommendations = []

        # 基于活动水平的推荐
        if user_profile.activity_level=="sedentary":
            recommendations.append({
                "type": "activity",
                "title": "增加日常活动",
                "description": "从每天增加500步开始，逐步提高活动量",
                "priority": "high",
                "category": "fitness"
            })

        # 基于健康目标的推荐
        if "weight_management" in user_profile.health_goals:
            recommendations.append({
                "type": "nutrition",
                "title": "均衡饮食计划",
                "description": "建议咨询营养师制定个性化饮食计划",
                "priority": "medium",
                "category": "nutrition"
            })

        # 基于风险因素的推荐
        if "insufficient_sleep" in user_profile.risk_factors:
            recommendations.append({
                "type": "lifestyle",
                "title": "改善睡眠质量",
                "description": "建立规律的睡眠时间，创造良好的睡眠环境",
                "priority": "high",
                "category": "sleep"
            })

        # 基于健康洞察的推荐
        for insight in health_insights:
            if insight.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                recommendations.append({
                    "type": "health_alert",
                    "title": f"关注{insight.metric_type.value}",
                    "description": insight.description,
                    "priority": "critical",
                    "category": "health"
                })

        return recommendations[:10]  # 返回前10个推荐


# 全局实例
_health_analyzer: Optional[HealthDataAnalyzer] = None
_profile_analyzer: Optional[UserProfileAnalyzer] = None
_recommendation_engine: Optional[RecommendationEngine] = None


def get_health_analyzer() -> HealthDataAnalyzer:
    """获取健康数据分析器"""
    global _health_analyzer
    if not _health_analyzer:
        _health_analyzer = HealthDataAnalyzer()
    return _health_analyzer


def get_profile_analyzer() -> UserProfileAnalyzer:
    """获取用户画像分析器"""
    global _profile_analyzer
    if not _profile_analyzer:
        _profile_analyzer = UserProfileAnalyzer()
    return _profile_analyzer


def get_recommendation_engine() -> RecommendationEngine:
    """获取推荐引擎"""
    global _recommendation_engine
    if not _recommendation_engine:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine