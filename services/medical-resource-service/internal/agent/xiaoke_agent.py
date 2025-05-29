"""
小克智能体核心模块
负责医疗资源的智能管理和协调
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from ..domain.models import (
    Appointment,
    ConstitutionType,
    Doctor,
    Recommendation,
    Resource,
    ResourceType,
    UrgencyLevel,
)
from ..repository.analytics_repository import AnalyticsRepository
from ..repository.resource_repository import ResourceRepository
from ..repository.user_repository import UserRepository
from .decision_engine import DecisionEngine
from .learning_module import LearningModule

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """智能体状态"""

    IDLE = "idle"
    ANALYZING = "analyzing"
    SCHEDULING = "scheduling"
    LEARNING = "learning"
    OPTIMIZING = "optimizing"


@dataclass
class ConstitutionAnalysis:
    """体质分析结果"""

    primary_type: ConstitutionType
    secondary_type: Optional[ConstitutionType]
    confidence_score: float
    analysis_summary: str
    recommendations: List[str]
    constitution_scores: Dict[str, float]


@dataclass
class ScheduleOptimization:
    """调度优化结果"""

    success: bool
    message: str
    suggestions: List[Dict[str, Any]]
    expected_improvement: float


class XiaokeAgent:
    """
    小克智能体 - 医疗资源管理协调者

    小克是索克生活平台的医疗资源管理专家，具备以下核心能力：
    1. 中医体质辨识和分析
    2. 智能资源匹配和推荐
    3. 预约调度优化
    4. 持续学习和自我优化
    """

    def __init__(
        self,
        resource_repository: ResourceRepository,
        user_repository: UserRepository,
        analytics_repository: AnalyticsRepository,
        config: Dict[str, Any],
    ):
        self.resource_repo = resource_repository
        self.user_repo = user_repository
        self.analytics_repo = analytics_repository
        self.config = config

        # 初始化核心组件
        self.decision_engine = DecisionEngine(config.get("decision_engine", {}))
        self.learning_module = LearningModule(config.get("learning", {}))

        # 智能体状态
        self.state = AgentState.IDLE
        self.last_optimization = None

        # 体质特征向量 (基于中医理论)
        self.constitution_features = self._initialize_constitution_features()

        # 症状-体质映射知识库
        self.symptom_constitution_mapping = self._load_symptom_mapping()

        logger.info("小克智能体初始化完成")

    def _initialize_constitution_features(self) -> Dict[str, np.ndarray]:
        """初始化体质特征向量"""
        # 基于中医九种体质的特征向量
        # 每个维度代表不同的生理特征 (气血、阴阳、脏腑等)
        features = {
            "平和质": np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            "气虚质": np.array([0.3, 1.0, 0.8, 0.7, 0.6, 0.8, 0.7, 0.8]),
            "阳虚质": np.array([0.5, 0.3, 0.8, 0.6, 0.4, 0.7, 0.6, 0.7]),
            "阴虚质": np.array([0.8, 0.4, 0.3, 0.8, 0.7, 0.5, 0.8, 0.6]),
            "痰湿质": np.array([0.6, 0.8, 0.7, 0.4, 0.3, 0.9, 0.5, 0.7]),
            "湿热质": np.array([0.7, 0.6, 0.4, 0.3, 0.8, 0.8, 0.6, 0.5]),
            "血瘀质": np.array([0.4, 0.7, 0.6, 0.5, 0.3, 0.6, 0.4, 0.8]),
            "气郁质": np.array([0.5, 0.8, 0.7, 0.6, 0.4, 0.5, 0.3, 0.7]),
            "特禀质": np.array([0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.3]),
        }
        return features

    def _load_symptom_mapping(self) -> Dict[str, List[Tuple[str, float]]]:
        """加载症状-体质映射知识库"""
        # 症状到体质的映射权重 (症状 -> [(体质, 权重), ...])
        mapping = {
            "乏力": [("气虚质", 0.8), ("阳虚质", 0.6)],
            "怕冷": [("阳虚质", 0.9), ("气虚质", 0.5)],
            "口干": [("阴虚质", 0.8), ("湿热质", 0.6)],
            "失眠": [("阴虚质", 0.7), ("气郁质", 0.6)],
            "便秘": [("阴虚质", 0.6), ("湿热质", 0.5)],
            "腹胀": [("痰湿质", 0.7), ("气郁质", 0.5)],
            "头痛": [("血瘀质", 0.6), ("气郁质", 0.5)],
            "易感冒": [("气虚质", 0.8), ("特禀质", 0.7)],
            "过敏": [("特禀质", 0.9)],
            "情绪低落": [("气郁质", 0.8)],
            "烦躁": [("湿热质", 0.7), ("阴虚质", 0.5)],
            "肥胖": [("痰湿质", 0.8)],
            "面色暗": [("血瘀质", 0.7)],
            "舌苔厚腻": [("痰湿质", 0.8), ("湿热质", 0.6)],
        }
        return mapping

    async def analyze_constitution(
        self,
        user_id: str,
        symptoms: List[str],
        health_data: Dict[str, Any],
        lifestyle_info: str = "",
    ) -> ConstitutionAnalysis:
        """
        分析用户体质

        Args:
            user_id: 用户ID
            symptoms: 症状列表
            health_data: 健康数据
            lifestyle_info: 生活方式信息

        Returns:
            ConstitutionAnalysis: 体质分析结果
        """
        self.state = AgentState.ANALYZING

        try:
            logger.info(f"开始为用户 {user_id} 进行体质分析")

            # 1. 基于症状的体质评分
            symptom_scores = self._analyze_symptoms(symptoms)

            # 2. 基于健康数据的体质评分
            health_scores = self._analyze_health_data(health_data)

            # 3. 基于生活方式的体质评分
            lifestyle_scores = self._analyze_lifestyle(lifestyle_info)

            # 4. 综合评分
            final_scores = self._combine_scores(
                symptom_scores, health_scores, lifestyle_scores
            )

            # 5. 确定主要和次要体质类型
            primary_type, secondary_type = self._determine_constitution_types(
                final_scores
            )

            # 6. 计算置信度
            confidence_score = self._calculate_confidence(final_scores)

            # 7. 生成分析总结和建议
            analysis_summary = self._generate_analysis_summary(
                primary_type, secondary_type, final_scores
            )
            recommendations = await self._generate_constitution_recommendations(
                primary_type, secondary_type, symptoms
            )

            # 8. 记录分析结果用于学习
            await self._record_analysis_for_learning(
                user_id, symptoms, health_data, final_scores
            )

            result = ConstitutionAnalysis(
                primary_type=primary_type,
                secondary_type=secondary_type,
                confidence_score=confidence_score,
                analysis_summary=analysis_summary,
                recommendations=recommendations,
                constitution_scores={k: float(v) for k, v in final_scores.items()},
            )

            logger.info(f"用户 {user_id} 体质分析完成: {primary_type.value}")
            return result

        except Exception as e:
            logger.error(f"体质分析失败: {e}")
            raise
        finally:
            self.state = AgentState.IDLE

    def _analyze_symptoms(self, symptoms: List[str]) -> Dict[str, float]:
        """基于症状分析体质"""
        scores = {
            const.value: 0.0
            for const in ConstitutionType
            if const != ConstitutionType.CONSTITUTION_TYPE_UNSPECIFIED
        }

        for symptom in symptoms:
            if symptom in self.symptom_constitution_mapping:
                for constitution, weight in self.symptom_constitution_mapping[symptom]:
                    if constitution in scores:
                        scores[constitution] += weight

        # 归一化
        max_score = max(scores.values()) if scores.values() else 1.0
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}

        return scores

    def _analyze_health_data(self, health_data: Dict[str, Any]) -> Dict[str, float]:
        """基于健康数据分析体质"""
        scores = {
            const.value: 0.0
            for const in ConstitutionType
            if const != ConstitutionType.CONSTITUTION_TYPE_UNSPECIFIED
        }

        # 基于血压、心率、BMI等指标推断体质倾向
        if "blood_pressure" in health_data:
            bp = health_data["blood_pressure"]
            if isinstance(bp, dict) and "systolic" in bp and "diastolic" in bp:
                systolic = bp["systolic"]
                diastolic = bp["diastolic"]

                if systolic < 110 or diastolic < 70:
                    scores["气虚质"] += 0.3
                    scores["阳虚质"] += 0.2
                elif systolic > 140 or diastolic > 90:
                    scores["湿热质"] += 0.3
                    scores["血瘀质"] += 0.2

        if "heart_rate" in health_data:
            hr = health_data["heart_rate"]
            if hr < 60:
                scores["阳虚质"] += 0.2
            elif hr > 100:
                scores["阴虚质"] += 0.2
                scores["湿热质"] += 0.1

        if "bmi" in health_data:
            bmi = health_data["bmi"]
            if bmi > 28:
                scores["痰湿质"] += 0.4
            elif bmi < 18.5:
                scores["气虚质"] += 0.3
                scores["阴虚质"] += 0.2

        return scores

    def _analyze_lifestyle(self, lifestyle_info: str) -> Dict[str, float]:
        """基于生活方式分析体质"""
        scores = {
            const.value: 0.0
            for const in ConstitutionType
            if const != ConstitutionType.CONSTITUTION_TYPE_UNSPECIFIED
        }

        if not lifestyle_info:
            return scores

        lifestyle_lower = lifestyle_info.lower()

        # 饮食习惯
        if any(word in lifestyle_lower for word in ["喜冷饮", "冷食", "生冷"]):
            scores["阳虚质"] += 0.2
        if any(word in lifestyle_lower for word in ["辛辣", "油腻", "烧烤"]):
            scores["湿热质"] += 0.3

        # 运动习惯
        if any(word in lifestyle_lower for word in ["久坐", "不运动", "缺乏运动"]):
            scores["痰湿质"] += 0.2
            scores["气虚质"] += 0.1

        # 睡眠习惯
        if any(word in lifestyle_lower for word in ["熬夜", "失眠", "睡眠不足"]):
            scores["阴虚质"] += 0.3
            scores["气郁质"] += 0.2

        # 情绪状态
        if any(word in lifestyle_lower for word in ["压力大", "焦虑", "抑郁"]):
            scores["气郁质"] += 0.4

        return scores

    def _combine_scores(
        self,
        symptom_scores: Dict[str, float],
        health_scores: Dict[str, float],
        lifestyle_scores: Dict[str, float],
    ) -> Dict[str, float]:
        """综合各项评分"""
        # 权重配置
        weights = {"symptom": 0.5, "health": 0.3, "lifestyle": 0.2}

        final_scores = {}
        all_constitutions = (
            set(symptom_scores.keys())
            | set(health_scores.keys())
            | set(lifestyle_scores.keys())
        )

        for constitution in all_constitutions:
            score = (
                symptom_scores.get(constitution, 0.0) * weights["symptom"]
                + health_scores.get(constitution, 0.0) * weights["health"]
                + lifestyle_scores.get(constitution, 0.0) * weights["lifestyle"]
            )
            final_scores[constitution] = score

        return final_scores

    def _determine_constitution_types(
        self, scores: Dict[str, float]
    ) -> Tuple[ConstitutionType, Optional[ConstitutionType]]:
        """确定主要和次要体质类型"""
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # 主要体质
        primary_name = sorted_scores[0][0]
        primary_type = ConstitutionType[primary_name.upper().replace("质", "")]

        # 次要体质 (如果分数差距不大)
        secondary_type = None
        if len(sorted_scores) > 1:
            primary_score = sorted_scores[0][1]
            secondary_score = sorted_scores[1][1]

            if secondary_score > 0.3 and (primary_score - secondary_score) < 0.2:
                secondary_name = sorted_scores[1][0]
                secondary_type = ConstitutionType[
                    secondary_name.upper().replace("质", "")
                ]

        return primary_type, secondary_type

    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """计算分析置信度"""
        if not scores:
            return 0.0

        sorted_scores = sorted(scores.values(), reverse=True)
        max_score = sorted_scores[0]

        if len(sorted_scores) == 1:
            return min(max_score, 1.0)

        # 基于最高分与次高分的差距计算置信度
        second_score = sorted_scores[1]
        confidence = max_score - second_score + 0.5

        return min(confidence, 1.0)

    def _generate_analysis_summary(
        self,
        primary_type: ConstitutionType,
        secondary_type: Optional[ConstitutionType],
        scores: Dict[str, float],
    ) -> str:
        """生成分析总结"""
        summary = (
            f"根据症状分析和健康数据评估，您的主要体质类型为{primary_type.value}。"
        )

        if secondary_type:
            summary += f"同时具有{secondary_type.value}的特征。"

        # 添加体质特点描述
        constitution_descriptions = {
            ConstitutionType.PING_HE: "体质平和，身体健康状态良好",
            ConstitutionType.QI_XU: "气虚体质，容易疲劳，需要补气调理",
            ConstitutionType.YANG_XU: "阳虚体质，怕冷，需要温阳补肾",
            ConstitutionType.YIN_XU: "阴虚体质，容易上火，需要滋阴润燥",
            ConstitutionType.TAN_SHI: "痰湿体质，容易肥胖，需要化痰祛湿",
            ConstitutionType.SHI_RE: "湿热体质，容易长痘，需要清热利湿",
            ConstitutionType.XUE_YU: "血瘀体质，血液循环不畅，需要活血化瘀",
            ConstitutionType.QI_YU: "气郁体质，情绪容易波动，需要疏肝理气",
            ConstitutionType.TE_BING: "特禀体质，容易过敏，需要调节免疫",
        }

        if primary_type in constitution_descriptions:
            summary += f" {constitution_descriptions[primary_type]}。"

        return summary

    async def _generate_constitution_recommendations(
        self,
        primary_type: ConstitutionType,
        secondary_type: Optional[ConstitutionType],
        symptoms: List[str],
    ) -> List[str]:
        """生成体质调理建议"""
        recommendations = []

        # 基于主要体质的建议
        primary_recommendations = self._get_constitution_recommendations(primary_type)
        recommendations.extend(primary_recommendations)

        # 基于次要体质的建议
        if secondary_type:
            secondary_recommendations = self._get_constitution_recommendations(
                secondary_type
            )
            # 避免重复建议
            for rec in secondary_recommendations:
                if rec not in recommendations:
                    recommendations.append(rec)

        # 基于具体症状的建议
        symptom_recommendations = self._get_symptom_recommendations(symptoms)
        recommendations.extend(symptom_recommendations)

        return recommendations[:10]  # 限制建议数量

    def _get_constitution_recommendations(
        self, constitution_type: ConstitutionType
    ) -> List[str]:
        """获取特定体质的调理建议"""
        recommendations_map = {
            ConstitutionType.QI_XU: [
                "适当进行有氧运动，如散步、太极拳",
                "多食用补气食物，如山药、红枣、黄芪",
                "保证充足睡眠，避免过度劳累",
                "可考虑中医补气调理",
            ],
            ConstitutionType.YANG_XU: [
                "注意保暖，避免受寒",
                "多食用温热性食物，如生姜、桂圆、羊肉",
                "适当运动增强体质",
                "可考虑温阳补肾的中医调理",
            ],
            ConstitutionType.YIN_XU: [
                "多食用滋阴食物，如银耳、百合、枸杞",
                "避免熬夜，保持规律作息",
                "减少辛辣刺激性食物",
                "可考虑滋阴润燥的中医调理",
            ],
            ConstitutionType.TAN_SHI: [
                "控制体重，适当减肥",
                "多食用祛湿食物，如薏米、冬瓜、茯苓",
                "增加运动量，促进新陈代谢",
                "可考虑化痰祛湿的中医调理",
            ],
            ConstitutionType.SHI_RE: [
                "清淡饮食，避免油腻辛辣",
                "多食用清热食物，如绿豆、苦瓜、菊花茶",
                "保持心情舒畅，避免情绪激动",
                "可考虑清热利湿的中医调理",
            ],
            ConstitutionType.XUE_YU: [
                "适当运动，促进血液循环",
                "多食用活血食物，如山楂、红花、当归",
                "避免久坐，定期活动",
                "可考虑活血化瘀的中医调理",
            ],
            ConstitutionType.QI_YU: [
                "保持心情愉快，学会情绪调节",
                "多食用疏肝理气食物，如玫瑰花茶、柑橘",
                "适当运动，如瑜伽、太极",
                "可考虑疏肝理气的中医调理",
            ],
            ConstitutionType.TE_BING: [
                "避免接触过敏原",
                "增强免疫力，规律作息",
                "饮食清淡，避免易过敏食物",
                "可考虑调节免疫的中医调理",
            ],
        }

        return recommendations_map.get(constitution_type, [])

    def _get_symptom_recommendations(self, symptoms: List[str]) -> List[str]:
        """基于症状获取针对性建议"""
        recommendations = []

        symptom_advice = {
            "失眠": "建议睡前避免使用电子设备，可尝试冥想或听轻音乐",
            "便秘": "增加膳食纤维摄入，多喝水，适当运动",
            "头痛": "注意休息，避免压力过大，可进行头部按摩",
            "乏力": "保证充足睡眠，适当补充维生素B族",
            "口干": "多喝水，避免辛辣食物，可含服润喉片",
        }

        for symptom in symptoms:
            if symptom in symptom_advice:
                recommendations.append(symptom_advice[symptom])

        return recommendations

    async def _record_analysis_for_learning(
        self,
        user_id: str,
        symptoms: List[str],
        health_data: Dict[str, Any],
        scores: Dict[str, float],
    ):
        """记录分析结果用于机器学习"""
        try:
            analysis_data = {
                "user_id": user_id,
                "symptoms": symptoms,
                "health_data": health_data,
                "constitution_scores": scores,
                "timestamp": datetime.now(),
            }

            await self.analytics_repo.record_constitution_analysis(analysis_data)

            # 触发学习模块更新
            await self.learning_module.update_constitution_model(analysis_data)

        except Exception as e:
            logger.warning(f"记录分析数据失败: {e}")

    async def optimize_schedule(
        self,
        resource_ids: List[str],
        optimization_date: datetime,
        optimization_weights: Dict[str, float],
    ) -> ScheduleOptimization:
        """
        优化资源调度

        Args:
            resource_ids: 需要优化的资源ID列表
            optimization_date: 优化日期
            optimization_weights: 优化权重配置

        Returns:
            ScheduleOptimization: 优化结果
        """
        self.state = AgentState.OPTIMIZING

        try:
            logger.info(f"开始优化 {len(resource_ids)} 个资源的调度")

            # 1. 获取资源当前状态
            resources = await self._get_resources_status(resource_ids)

            # 2. 分析历史数据
            historical_data = await self._analyze_historical_utilization(
                resource_ids, optimization_date
            )

            # 3. 预测需求
            demand_forecast = await self._forecast_demand(
                resource_ids, optimization_date
            )

            # 4. 生成优化建议
            suggestions = await self._generate_optimization_suggestions(
                resources, historical_data, demand_forecast, optimization_weights
            )

            # 5. 计算预期改进
            expected_improvement = self._calculate_expected_improvement(suggestions)

            # 6. 记录优化结果
            await self._record_optimization_result(
                resource_ids, suggestions, expected_improvement
            )

            result = ScheduleOptimization(
                success=True,
                message=f"成功生成 {len(suggestions)} 条优化建议",
                suggestions=suggestions,
                expected_improvement=expected_improvement,
            )

            logger.info(f"调度优化完成，预期改进: {expected_improvement:.2%}")
            return result

        except Exception as e:
            logger.error(f"调度优化失败: {e}")
            return ScheduleOptimization(
                success=False,
                message=f"优化失败: {str(e)}",
                suggestions=[],
                expected_improvement=0.0,
            )
        finally:
            self.state = AgentState.IDLE

    async def _get_resources_status(self, resource_ids: List[str]) -> List[Resource]:
        """获取资源状态"""
        resources = []
        for resource_id in resource_ids:
            resource = await self.resource_repo.get_by_id(resource_id)
            if resource:
                resources.append(resource)
        return resources

    async def _analyze_historical_utilization(
        self, resource_ids: List[str], date: datetime
    ) -> Dict[str, Any]:
        """分析历史利用率"""
        # 分析过去30天的利用率数据
        start_date = date - timedelta(days=30)
        end_date = date

        utilization_data = await self.analytics_repo.get_resource_utilization(
            resource_ids, start_date, end_date
        )

        return utilization_data

    async def _forecast_demand(
        self, resource_ids: List[str], date: datetime
    ) -> Dict[str, float]:
        """预测需求"""
        # 使用机器学习模型预测未来需求
        forecast = {}

        for resource_id in resource_ids:
            # 获取历史预约数据
            historical_appointments = await self.analytics_repo.get_appointment_history(
                resource_id, date - timedelta(days=90), date
            )

            # 使用时间序列预测
            predicted_demand = await self.learning_module.predict_demand(
                resource_id, historical_appointments, date
            )

            forecast[resource_id] = predicted_demand

        return forecast

    async def _generate_optimization_suggestions(
        self,
        resources: List[Resource],
        historical_data: Dict[str, Any],
        demand_forecast: Dict[str, float],
        weights: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        for resource in resources:
            resource_id = resource.id

            # 当前利用率
            current_utilization = historical_data.get(resource_id, {}).get(
                "utilization", 0.0
            )

            # 预测需求
            predicted_demand = demand_forecast.get(resource_id, 0.0)

            # 生成建议
            if current_utilization < 0.6 and predicted_demand > current_utilization:
                # 利用率低但需求增长，建议增加营销
                suggestions.append(
                    {
                        "resource_id": resource_id,
                        "suggestion_type": "increase_marketing",
                        "description": f"资源 {resource.name} 利用率较低({current_utilization:.1%})，但预测需求上升，建议加强推广",
                        "impact_score": 0.7,
                        "parameters": {
                            "current_utilization": current_utilization,
                            "predicted_demand": predicted_demand,
                        },
                    }
                )

            elif current_utilization > 0.9:
                # 利用率过高，建议扩容或分流
                suggestions.append(
                    {
                        "resource_id": resource_id,
                        "suggestion_type": "capacity_expansion",
                        "description": f"资源 {resource.name} 利用率过高({current_utilization:.1%})，建议扩容或分流",
                        "impact_score": 0.8,
                        "parameters": {
                            "current_utilization": current_utilization,
                            "recommended_capacity_increase": 0.2,
                        },
                    }
                )

            elif abs(predicted_demand - current_utilization) > 0.3:
                # 需求预测与当前利用率差异较大，建议调整调度策略
                suggestions.append(
                    {
                        "resource_id": resource_id,
                        "suggestion_type": "schedule_adjustment",
                        "description": f"资源 {resource.name} 预测需求与当前利用率差异较大，建议调整调度策略",
                        "impact_score": 0.6,
                        "parameters": {
                            "current_utilization": current_utilization,
                            "predicted_demand": predicted_demand,
                            "adjustment_direction": (
                                "increase"
                                if predicted_demand > current_utilization
                                else "decrease"
                            ),
                        },
                    }
                )

        return suggestions

    def _calculate_expected_improvement(
        self, suggestions: List[Dict[str, Any]]
    ) -> float:
        """计算预期改进"""
        if not suggestions:
            return 0.0

        total_impact = sum(
            suggestion.get("impact_score", 0.0) for suggestion in suggestions
        )
        average_impact = total_impact / len(suggestions)

        return min(average_impact, 1.0)

    async def _record_optimization_result(
        self,
        resource_ids: List[str],
        suggestions: List[Dict[str, Any]],
        expected_improvement: float,
    ):
        """记录优化结果"""
        try:
            optimization_data = {
                "resource_ids": resource_ids,
                "suggestions": suggestions,
                "expected_improvement": expected_improvement,
                "timestamp": datetime.now(),
            }

            await self.analytics_repo.record_optimization(optimization_data)

        except Exception as e:
            logger.warning(f"记录优化结果失败: {e}")

    async def recommend_resources(
        self,
        user_id: str,
        constitution: ConstitutionType,
        symptoms: List[str],
        location: str,
        urgency: UrgencyLevel,
        max_results: int = 10,
    ) -> List[Recommendation]:
        """
        推荐医疗资源

        Args:
            user_id: 用户ID
            constitution: 用户体质
            symptoms: 症状列表
            location: 位置偏好
            urgency: 紧急程度
            max_results: 最大结果数

        Returns:
            List[Recommendation]: 推荐列表
        """
        try:
            logger.info(f"为用户 {user_id} 推荐医疗资源")

            # 1. 获取用户历史偏好
            user_preferences = await self._get_user_preferences(user_id)

            # 2. 基于体质匹配医生
            suitable_doctors = await self._match_doctors_by_constitution(
                constitution, symptoms, location
            )

            # 3. 基于症状推荐治疗方案
            treatment_options = await self._recommend_treatments(
                constitution, symptoms, urgency
            )

            # 4. 综合评分和排序
            recommendations = await self._rank_recommendations(
                suitable_doctors, treatment_options, user_preferences, urgency
            )

            return recommendations[:max_results]

        except Exception as e:
            logger.error(f"资源推荐失败: {e}")
            return []

    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        try:
            user_data = await self.user_repo.get_user_preferences(user_id)
            return user_data or {}
        except Exception:
            return {}

    async def _match_doctors_by_constitution(
        self, constitution: ConstitutionType, symptoms: List[str], location: str
    ) -> List[Doctor]:
        """基于体质匹配医生"""
        # 查找专长对应体质的中医师
        doctors = await self.resource_repo.find_doctors_by_constitution_specialty(
            constitution, location
        )

        # 基于症状进一步筛选
        filtered_doctors = []
        for doctor in doctors:
            if self._doctor_matches_symptoms(doctor, symptoms):
                filtered_doctors.append(doctor)

        return filtered_doctors

    def _doctor_matches_symptoms(self, doctor: Doctor, symptoms: List[str]) -> bool:
        """判断医生是否匹配症状"""
        doctor_specialties = [spec.lower() for spec in doctor.specialties]

        # 简单的关键词匹配
        symptom_keywords = {
            "失眠": ["神经", "精神", "睡眠"],
            "头痛": ["神经", "头痛", "疼痛"],
            "胃痛": ["消化", "胃肠", "脾胃"],
            "咳嗽": ["呼吸", "肺", "咳嗽"],
            "腰痛": ["骨科", "腰椎", "疼痛"],
        }

        for symptom in symptoms:
            if symptom in symptom_keywords:
                keywords = symptom_keywords[symptom]
                if any(
                    keyword in specialty
                    for specialty in doctor_specialties
                    for keyword in keywords
                ):
                    return True

        return True  # 默认匹配

    async def _recommend_treatments(
        self, constitution: ConstitutionType, symptoms: List[str], urgency: UrgencyLevel
    ) -> List[Dict[str, Any]]:
        """推荐治疗方案"""
        treatments = []

        # 基于体质推荐中医治疗
        if constitution != ConstitutionType.CONSTITUTION_TYPE_UNSPECIFIED:
            tcm_treatment = {
                "type": "中医调理",
                "description": f"针对{constitution.value}的中医辨证论治",
                "effectiveness_score": 0.8,
                "duration_days": 30,
            }
            treatments.append(tcm_treatment)

        # 基于症状推荐现代医学治疗
        for symptom in symptoms:
            if symptom in ["头痛", "发热", "咳嗽"]:
                modern_treatment = {
                    "type": "现代医学",
                    "description": f"针对{symptom}的现代医学治疗",
                    "effectiveness_score": 0.7,
                    "duration_days": 7,
                }
                treatments.append(modern_treatment)

        # 根据紧急程度调整推荐
        if urgency in [UrgencyLevel.HIGH, UrgencyLevel.EMERGENCY]:
            emergency_treatment = {
                "type": "急诊处理",
                "description": "紧急情况建议立即就医",
                "effectiveness_score": 0.9,
                "duration_days": 1,
            }
            treatments.insert(0, emergency_treatment)

        return treatments

    async def _rank_recommendations(
        self,
        doctors: List[Doctor],
        treatments: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        urgency: UrgencyLevel,
    ) -> List[Recommendation]:
        """对推荐结果进行排序"""
        recommendations = []

        # 医生推荐
        for i, doctor in enumerate(doctors):
            score = self._calculate_doctor_score(doctor, user_preferences, urgency)

            recommendation = Recommendation(
                id=f"doctor_{doctor.id}",
                resource_type=ResourceType.DOCTOR,
                resource_id=doctor.id,
                title=f"推荐医生: {doctor.name}",
                description=f"{doctor.title} - {doctor.hospital}",
                confidence_score=score,
                reasoning=f"基于体质匹配和专业特长推荐",
                metadata={
                    "doctor_name": doctor.name,
                    "hospital": doctor.hospital,
                    "specialties": doctor.specialties,
                    "rating": str(doctor.rating),
                },
            )
            recommendations.append(recommendation)

        # 治疗方案推荐
        for i, treatment in enumerate(treatments):
            recommendation = Recommendation(
                id=f"treatment_{i}",
                resource_type=ResourceType.FACILITY,  # 假设治疗需要医疗机构
                resource_id="",
                title=f"推荐治疗: {treatment['type']}",
                description=treatment["description"],
                confidence_score=treatment["effectiveness_score"],
                reasoning="基于体质和症状的治疗方案推荐",
                metadata={
                    "treatment_type": treatment["type"],
                    "duration_days": str(treatment["duration_days"]),
                },
            )
            recommendations.append(recommendation)

        # 按置信度排序
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)

        return recommendations

    def _calculate_doctor_score(
        self, doctor: Doctor, user_preferences: Dict[str, Any], urgency: UrgencyLevel
    ) -> float:
        """计算医生推荐分数"""
        score = 0.0

        # 基础评分 (医生评级)
        score += doctor.rating * 0.3

        # 经验加分
        experience_score = min(doctor.years_experience / 20.0, 1.0)
        score += experience_score * 0.2

        # 用户偏好匹配
        if user_preferences.get("prefer_tcm") and doctor.tcm_specialist:
            score += 0.2

        if user_preferences.get("prefer_hospital") == doctor.hospital:
            score += 0.1

        # 紧急程度调整
        if urgency in [UrgencyLevel.HIGH, UrgencyLevel.EMERGENCY]:
            # 紧急情况优先推荐可立即接诊的医生
            score += 0.2

        return min(score, 1.0)

    def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "state": self.state.value,
            "last_optimization": (
                self.last_optimization.isoformat() if self.last_optimization else None
            ),
            "constitution_types_supported": len(self.constitution_features),
            "symptom_mappings_loaded": len(self.symptom_constitution_mapping),
        }
