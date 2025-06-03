"""
小克智能体核心模块
负责医疗资源的智能管理和协调
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..domain.models import (
    Appointment,
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

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """智能体状态"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    SCHEDULING = "scheduling"
    OPTIMIZING = "optimizing"

@dataclass
class ScheduleOptimization:
    """调度优化结果"""
    success: bool
    message: str
    suggestions: List[Dict[str, Any]]
    expected_improvement: float

@dataclass
class ResourceMatchResult:
    """资源匹配结果"""
    resource_id: str
    match_score: float
    reasoning: str
    availability: Dict[str, Any]

class XiaokeAgent:
    """
    小克智能体 - 医疗资源管理协调者

    小克是索克生活平台的医疗资源管理专家，具备以下核心能力：
    1. 智能资源匹配和推荐
    2. 预约调度优化
    3. 资源利用率分析
    4. 质量监控和优化
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

        # 智能体状态
        self.state = AgentState.IDLE
        self.last_optimization = None

        # 资源匹配算法配置
        self.matching_weights = config.get("matching_weights", {
            "specialty_match": 0.4,
            "location_proximity": 0.3,
            "availability": 0.2,
            "rating": 0.1
        })

        logger.info("小克智能体初始化完成")

    async def recommend_resources(
        self,
        user_id: str,
        symptoms: List[str],
        location: str,
        urgency: UrgencyLevel,
        max_results: int = 10,
    ) -> List[Recommendation]:
        """
        智能推荐医疗资源

        Args:
            user_id: 用户ID
            symptoms: 症状列表
            location: 用户位置
            urgency: 紧急程度
            max_results: 最大返回结果数

        Returns:
            List[Recommendation]: 推荐结果列表
        """
        self.state = AgentState.ANALYZING

        try:
            logger.info(f"开始为用户 {user_id} 推荐医疗资源")

            # 1. 获取用户偏好
            user_preferences = await self._get_user_preferences(user_id)

            # 2. 基于症状匹配医生
            doctors = await self._match_doctors_by_symptoms(symptoms, location)

            # 3. 推荐治疗方案
            treatments = await self._recommend_treatments(symptoms, urgency)

            # 4. 综合排序推荐
            recommendations = await self._rank_recommendations(
                doctors, treatments, user_preferences, urgency
            )

            # 5. 记录推荐结果用于优化
            await self._record_recommendation_result(
                user_id, symptoms, recommendations
            )

            logger.info(f"为用户 {user_id} 生成 {len(recommendations)} 个推荐")
            return recommendations[:max_results]

        except Exception as e:
            logger.error(f"资源推荐失败: {e}")
            raise
        finally:
            self.state = AgentState.IDLE

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

            # 2. 分析历史利用率
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
                message=f"成功生成 {len(suggestions)} 个优化建议",
                suggestions=suggestions,
                expected_improvement=expected_improvement,
            )

            self.last_optimization = datetime.now()
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

    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        try:
            user_profile = await self.user_repo.get_user_profile(user_id)
            return user_profile.get("preferences", {})
        except Exception:
            return {}

    async def _match_doctors_by_symptoms(
        self, symptoms: List[str], location: str
    ) -> List[Doctor]:
        """基于症状匹配医生"""
        try:
            # 根据症状确定相关科室
            relevant_specialties = self._map_symptoms_to_specialties(symptoms)
            
            # 搜索相关医生
            doctors = await self.resource_repo.search_doctors(
                specialties=relevant_specialties,
                location=location,
                available=True
            )
            
            return doctors
        except Exception as e:
            logger.error(f"医生匹配失败: {e}")
            return []

    def _map_symptoms_to_specialties(self, symptoms: List[str]) -> List[str]:
        """将症状映射到相关科室"""
        symptom_specialty_map = {
            "头痛": ["神经内科", "内科"],
            "发热": ["内科", "感染科"],
            "咳嗽": ["呼吸内科", "内科"],
            "胸痛": ["心内科", "胸外科"],
            "腹痛": ["消化内科", "普外科"],
            "关节痛": ["骨科", "风湿免疫科"],
            "皮疹": ["皮肤科"],
            "眼痛": ["眼科"],
            "耳痛": ["耳鼻喉科"],
        }
        
        specialties = set()
        for symptom in symptoms:
            if symptom in symptom_specialty_map:
                specialties.update(symptom_specialty_map[symptom])
        
        return list(specialties) if specialties else ["内科"]

    def _doctor_matches_symptoms(self, doctor: Doctor, symptoms: List[str]) -> bool:
        """判断医生是否匹配症状"""
        relevant_specialties = self._map_symptoms_to_specialties(symptoms)
        return any(specialty in doctor.specialties for specialty in relevant_specialties)

    async def _recommend_treatments(
        self, symptoms: List[str], urgency: UrgencyLevel
    ) -> List[Dict[str, Any]]:
        """推荐治疗方案"""
        treatments = []
        
        # 基于症状和紧急程度推荐治疗方案
        if urgency == UrgencyLevel.EMERGENCY:
            treatments.append({
                "type": "emergency_care",
                "description": "紧急医疗处理",
                "priority": 1.0
            })
        elif urgency == UrgencyLevel.HIGH:
            treatments.append({
                "type": "urgent_consultation",
                "description": "紧急门诊咨询",
                "priority": 0.8
            })
        else:
            treatments.append({
                "type": "regular_consultation",
                "description": "常规门诊咨询",
                "priority": 0.6
            })
            
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
        
        for doctor in doctors:
            score = self._calculate_doctor_score(doctor, user_preferences, urgency)
            
            recommendation = Recommendation(
                resource_type=ResourceType.DOCTOR,
                resource_id=doctor.id,
                title=f"推荐医生: {doctor.name}",
                description=f"{doctor.title} - {doctor.hospital} {doctor.department}",
                confidence_score=score,
                reasoning=f"基于专业匹配度和用户偏好计算得分: {score:.2f}",
                metadata={
                    "doctor_info": {
                        "name": doctor.name,
                        "title": doctor.title,
                        "hospital": doctor.hospital,
                        "department": doctor.department,
                        "rating": doctor.rating,
                        "experience": doctor.years_experience
                    }
                }
            )
            recommendations.append(recommendation)
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return recommendations

    def _calculate_doctor_score(
        self, doctor: Doctor, user_preferences: Dict[str, Any], urgency: UrgencyLevel
    ) -> float:
        """计算医生推荐得分"""
        score = 0.0
        
        # 基础评分（医生评分）
        score += doctor.rating * 0.3
        
        # 经验加分
        experience_score = min(doctor.years_experience / 20, 1.0)
        score += experience_score * 0.2
        
        # 可用性加分
        if doctor.available:
            score += 0.3
        
        # 紧急程度调整
        if urgency == UrgencyLevel.EMERGENCY:
            score += 0.2
        
        # 用户偏好调整
        preferred_hospital = user_preferences.get("preferred_hospital")
        if preferred_hospital and doctor.hospital == preferred_hospital:
            score += 0.1
            
        return min(score, 1.0)

    async def _get_resources_status(self, resource_ids: List[str]) -> List[Resource]:
        """获取资源状态"""
        resources = []
        for resource_id in resource_ids:
            try:
                resource = await self.resource_repo.get_resource(resource_id)
                if resource:
                    resources.append(resource)
            except Exception as e:
                logger.warning(f"获取资源 {resource_id} 状态失败: {e}")
        return resources

    async def _analyze_historical_utilization(
        self, resource_ids: List[str], date: datetime
    ) -> Dict[str, Any]:
        """分析历史利用率"""
        try:
            # 获取过去30天的利用率数据
            start_date = date - timedelta(days=30)
            utilization_data = await self.analytics_repo.get_utilization_data(
                resource_ids, start_date, date
            )
            return utilization_data
        except Exception as e:
            logger.error(f"分析历史利用率失败: {e}")
            return {}

    async def _forecast_demand(
        self, resource_ids: List[str], date: datetime
    ) -> Dict[str, float]:
        """预测需求"""
        try:
            # 简单的需求预测算法
            demand_forecast = {}
            for resource_id in resource_ids:
                # 基于历史数据预测（这里使用简化算法）
                historical_avg = await self.analytics_repo.get_average_demand(
                    resource_id, date - timedelta(days=30), date
                )
                # 考虑季节性因素
                seasonal_factor = self._get_seasonal_factor(date)
                predicted_demand = historical_avg * seasonal_factor
                demand_forecast[resource_id] = predicted_demand
            return demand_forecast
        except Exception as e:
            logger.error(f"需求预测失败: {e}")
            return {}

    def _get_seasonal_factor(self, date: datetime) -> float:
        """获取季节性因子"""
        # 简化的季节性调整
        month = date.month
        if month in [12, 1, 2]:  # 冬季
            return 1.2  # 冬季需求通常较高
        elif month in [6, 7, 8]:  # 夏季
            return 0.9  # 夏季需求通常较低
        else:
            return 1.0

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
            predicted_demand = demand_forecast.get(resource_id, 0)
            
            # 分析当前利用率
            current_utilization = historical_data.get(resource_id, {}).get("avg_utilization", 0)
            
            if current_utilization > 0.9:  # 过度利用
                suggestions.append({
                    "resource_id": resource_id,
                    "type": "increase_capacity",
                    "description": f"资源 {resource.name} 利用率过高({current_utilization:.1%})，建议增加容量",
                    "priority": "high",
                    "expected_impact": 0.2
                })
            elif current_utilization < 0.3:  # 利用不足
                suggestions.append({
                    "resource_id": resource_id,
                    "type": "optimize_schedule",
                    "description": f"资源 {resource.name} 利用率较低({current_utilization:.1%})，建议优化排班",
                    "priority": "medium",
                    "expected_impact": 0.15
                })
            
            # 基于需求预测的建议
            if predicted_demand > current_utilization * 1.5:
                suggestions.append({
                    "resource_id": resource_id,
                    "type": "prepare_for_demand",
                    "description": f"预测需求增长，建议提前准备资源",
                    "priority": "medium",
                    "expected_impact": 0.1
                })
        
        return suggestions

    def _calculate_expected_improvement(
        self, suggestions: List[Dict[str, Any]]
    ) -> float:
        """计算预期改进"""
        total_impact = sum(
            suggestion.get("expected_impact", 0) for suggestion in suggestions
        )
        return min(total_impact, 0.5)  # 最大改进50%

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
                "timestamp": datetime.now().isoformat(),
            }
            await self.analytics_repo.record_optimization_result(optimization_data)
            logger.debug(f"记录优化结果: {len(suggestions)} 个建议")
        except Exception as e:
            logger.error(f"记录优化结果失败: {e}")

    async def _record_recommendation_result(
        self,
        user_id: str,
        symptoms: List[str],
        recommendations: List[Recommendation],
    ):
        """记录推荐结果"""
        try:
            recommendation_data = {
                "user_id": user_id,
                "symptoms": symptoms,
                "recommendations": [
                    {
                        "resource_id": rec.resource_id,
                        "confidence_score": rec.confidence_score,
                        "reasoning": rec.reasoning
                    }
                    for rec in recommendations
                ],
                "timestamp": datetime.now().isoformat(),
            }
            await self.analytics_repo.record_recommendation_result(recommendation_data)
            logger.debug(f"记录推荐结果: {user_id}")
        except Exception as e:
            logger.error(f"记录推荐结果失败: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "state": self.state.value,
            "last_optimization": self.last_optimization.isoformat() if self.last_optimization else None,
            "config": {
                "matching_weights": self.matching_weights,
            },
            "capabilities": [
                "resource_recommendation",
                "schedule_optimization",
                "demand_forecasting",
                "utilization_analysis"
            ]
        }
