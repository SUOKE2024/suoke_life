"""
中医服务类

专注于集成其他中医微服务，为索儿智能体提供中医健康管理功能
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .base_service import BaseService
from ..clients.tcm_client import TCMServiceClient
from ..models.tcm import TCMConstitution, TCMRecommendationResponse


class TCMService(BaseService):
    """中医服务类 - 专注于集成其他中医微服务"""

    def __init__(self):
        super().__init__()
        self.tcm_client = TCMServiceClient()
        self.consultation_collection = "tcm_consultations"
        self.integration_collection = "tcm_integrations"

    async def get_user_tcm_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户中医档案（整合多个服务的信息）"""
        try:
            # 并发获取用户的中医相关信息
            constitution_data = await self.tcm_client.get_user_constitution(user_id)
            health_data = await self.tcm_client.get_user_health_data(user_id)
            
            # 整合用户中医档案
            tcm_profile = {
                "user_id": user_id,
                "constitution": constitution_data,
                "health_status": health_data,
                "last_updated": datetime.now(),
                "profile_completeness": self._calculate_profile_completeness(constitution_data, health_data)
            }
            
            # 缓存用户档案
            if self.redis:
                await self.redis.set(
                    f"tcm_profile:{user_id}", 
                    json.dumps(tcm_profile, default=str), 
                    ex=3600  # 1小时缓存
                )
            
            await self.log_operation("get_user_tcm_profile", True, {"user_id": user_id})
            return tcm_profile
            
        except Exception as e:
            await self.log_operation("get_user_tcm_profile", False, {"error": str(e)})
            return {}

    async def get_personalized_tcm_advice(self, user_id: str, symptoms: List[str] = None, 
                                        context: Dict[str, Any] = None) -> TCMRecommendationResponse:
        """获取个性化中医建议"""
        try:
            # 获取用户中医档案
            tcm_profile = await self.get_user_tcm_profile(user_id)
            
            # 获取体质信息
            constitution_type = None
            if tcm_profile.get("constitution"):
                constitution_type = tcm_profile["constitution"].get("primary_constitution")
            
            # 根据症状获取建议
            recommendations = {}
            
            if symptoms:
                # 获取经络分析
                meridian_analysis = await self.tcm_client.get_meridian_analysis(
                    symptoms, context.get("affected_areas", []) if context else []
                )
                recommendations["meridian"] = meridian_analysis
                
                # 获取中药建议
                herbal_recommendations = await self.tcm_client.get_herbal_recommendations(
                    symptoms, constitution_type
                )
                recommendations["herbal"] = herbal_recommendations
                
                # 获取穴位建议
                if symptoms:
                    acupuncture_points = await self.tcm_client.get_acupuncture_points(
                        symptoms[0], constitution_type
                    )
                    recommendations["acupuncture"] = acupuncture_points
            
            # 获取体质调养建议
            if constitution_type:
                constitution_advice = await self.tcm_client.get_constitution_recommendations(
                    constitution_type, tcm_profile.get("health_status", {})
                )
                recommendations["constitution"] = constitution_advice
                
                # 获取时令养生建议
                seasonal_guidance = await self.tcm_client.get_seasonal_guidance(constitution_type)
                recommendations["seasonal"] = seasonal_guidance
            
            # 生成综合建议响应
            response = self._create_tcm_recommendation_response(
                user_id, symptoms or [], recommendations, constitution_type
            )
            
            # 保存咨询记录
            if self.mongodb:
                consultation_record = {
                    "user_id": user_id,
                    "symptoms": symptoms or [],
                    "context": context or {},
                    "recommendations": response.dict(),
                    "created_at": datetime.now()
                }
                await self.mongodb[self.consultation_collection].insert_one(consultation_record)
            
            await self.log_operation("get_personalized_tcm_advice", True, {"user_id": user_id})
            return response
            
        except Exception as e:
            await self.log_operation("get_personalized_tcm_advice", False, {"error": str(e)})
            # 返回默认建议
            return self._create_default_tcm_response(user_id)

    async def get_tcm_health_insights(self, user_id: str) -> Dict[str, Any]:
        """获取中医健康洞察"""
        try:
            # 获取综合中医健康评估
            assessment = await self.tcm_client.get_tcm_health_assessment(user_id)
            
            # 分析健康趋势
            insights = {
                "user_id": user_id,
                "assessment_summary": assessment,
                "health_trends": await self._analyze_tcm_health_trends(user_id),
                "risk_factors": await self._identify_tcm_risk_factors(assessment),
                "improvement_suggestions": await self._generate_improvement_suggestions(assessment),
                "next_steps": await self._recommend_next_steps(assessment),
                "generated_at": datetime.now()
            }
            
            await self.log_operation("get_tcm_health_insights", True, {"user_id": user_id})
            return insights
            
        except Exception as e:
            await self.log_operation("get_tcm_health_insights", False, {"error": str(e)})
            return {}

    async def search_tcm_knowledge_for_user(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """为用户搜索相关的中医知识"""
        try:
            # 获取用户体质信息以个性化搜索
            tcm_profile = await self.get_user_tcm_profile(user_id)
            constitution_type = None
            if tcm_profile.get("constitution"):
                constitution_type = tcm_profile["constitution"].get("primary_constitution")
            
            # 搜索中医知识
            search_results = await self.tcm_client.search_tcm_knowledge(query)
            
            # 根据用户体质过滤和排序结果
            personalized_results = self._personalize_search_results(
                search_results, constitution_type
            )
            
            # 记录搜索历史
            if self.mongodb:
                search_record = {
                    "user_id": user_id,
                    "query": query,
                    "results_count": len(personalized_results),
                    "constitution_type": constitution_type,
                    "created_at": datetime.now()
                }
                await self.mongodb["tcm_search_history"].insert_one(search_record)
            
            await self.log_operation("search_tcm_knowledge_for_user", True, {"user_id": user_id, "query": query})
            return personalized_results
            
        except Exception as e:
            await self.log_operation("search_tcm_knowledge_for_user", False, {"error": str(e)})
            return []

    async def get_daily_tcm_guidance(self, user_id: str) -> Dict[str, Any]:
        """获取每日中医养生指导"""
        try:
            # 检查缓存
            cache_key = f"daily_tcm_guidance:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
            if self.redis:
                cached_guidance = await self.redis.get(cache_key)
                if cached_guidance:
                    return json.loads(cached_guidance)
            
            # 获取用户体质信息
            tcm_profile = await self.get_user_tcm_profile(user_id)
            constitution_type = tcm_profile.get("constitution", {}).get("primary_constitution")
            
            if not constitution_type:
                constitution_type = "平和质"  # 默认体质
            
            # 获取时令养生指导
            seasonal_guidance = await self.tcm_client.get_seasonal_guidance(constitution_type)
            
            # 生成每日指导
            daily_guidance = {
                "user_id": user_id,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "constitution_type": constitution_type,
                "morning_routine": self._generate_morning_routine(constitution_type, seasonal_guidance),
                "dietary_suggestions": self._generate_daily_diet_suggestions(constitution_type, seasonal_guidance),
                "exercise_recommendations": self._generate_daily_exercise(constitution_type, seasonal_guidance),
                "evening_routine": self._generate_evening_routine(constitution_type, seasonal_guidance),
                "mindfulness_practice": self._generate_mindfulness_practice(constitution_type),
                "health_tips": self._generate_daily_health_tips(constitution_type, seasonal_guidance)
            }
            
            # 缓存每日指导
            if self.redis:
                await self.redis.set(cache_key, json.dumps(daily_guidance, default=str), ex=86400)  # 24小时
            
            await self.log_operation("get_daily_tcm_guidance", True, {"user_id": user_id})
            return daily_guidance
            
        except Exception as e:
            await self.log_operation("get_daily_tcm_guidance", False, {"error": str(e)})
            return {}

    def _calculate_profile_completeness(self, constitution_data: Dict[str, Any], 
                                      health_data: Dict[str, Any]) -> float:
        """计算档案完整度"""
        completeness = 0.0
        
        if constitution_data:
            completeness += 0.5
        if health_data and health_data.get("recent_data"):
            completeness += 0.3
        if health_data and health_data.get("symptoms"):
            completeness += 0.2
            
        return min(completeness, 1.0)

    def _create_tcm_recommendation_response(self, user_id: str, symptoms: List[str], 
                                          recommendations: Dict[str, Any], 
                                          constitution_type: Optional[str]) -> TCMRecommendationResponse:
        """创建中医建议响应"""
        
        # 提取各类建议
        herbal_recs = recommendations.get("herbal", {}).get("recommended_herbs", [])
        acupuncture_points = [point.get("name", "") for point in recommendations.get("acupuncture", [])]
        constitution_advice = recommendations.get("constitution", {})
        
        return TCMRecommendationResponse(
            recommendation_id=str(uuid.uuid4()),
            recommendation_type="comprehensive_tcm_advice",
            syndrome_analysis=self._analyze_syndrome_from_recommendations(recommendations),
            constitution_analysis=f"根据您的{constitution_type}体质特点" if constitution_type else "建议进行体质评估",
            herbal_recommendations=herbal_recs[:5],  # 限制数量
            acupuncture_points=acupuncture_points[:8],
            massage_techniques=self._extract_massage_techniques(recommendations),
            dietary_suggestions=constitution_advice.get("dietary", [])[:5],
            lifestyle_adjustments=constitution_advice.get("lifestyle", [])[:5],
            exercise_recommendations=constitution_advice.get("exercise", [])[:3],
            precautions=self._generate_precautions(recommendations),
            contraindications=self._extract_contraindications(recommendations),
            follow_up_suggestions=["建议定期体质评估", "关注症状变化", "保持健康生活方式"],
            confidence_score=self._calculate_recommendation_confidence(recommendations)
        )

    def _create_default_tcm_response(self, user_id: str) -> TCMRecommendationResponse:
        """创建默认中医建议响应"""
        return TCMRecommendationResponse(
            recommendation_id=str(uuid.uuid4()),
            recommendation_type="general_tcm_advice",
            syndrome_analysis="建议进行详细的中医体质评估",
            constitution_analysis="暂无体质信息，建议完善个人档案",
            herbal_recommendations=["建议咨询专业中医师"],
            acupuncture_points=[],
            massage_techniques=["适当按摩太阳穴", "按摩足三里穴"],
            dietary_suggestions=["饮食清淡", "规律进餐", "多喝温水"],
            lifestyle_adjustments=["保持规律作息", "适度运动", "心情愉悦"],
            exercise_recommendations=["散步", "太极拳", "八段锦"],
            precautions=["如有不适请及时就医"],
            contraindications=["避免自行用药"],
            follow_up_suggestions=["建议进行体质评估", "完善健康档案"],
            confidence_score=0.3
        )

    async def _analyze_tcm_health_trends(self, user_id: str) -> Dict[str, Any]:
        """分析中医健康趋势"""
        # 这里可以分析用户的历史数据趋势
        return {
            "trend_direction": "stable",
            "key_changes": [],
            "recommendations": ["继续保持良好的生活习惯"]
        }

    async def _identify_tcm_risk_factors(self, assessment: Dict[str, Any]) -> List[str]:
        """识别中医风险因素"""
        risk_factors = []
        
        if assessment.get("constitution"):
            constitution = assessment["constitution"].get("primary_constitution")
            if constitution in ["气虚质", "阳虚质"]:
                risk_factors.append("体质偏虚，需注意保养")
            elif constitution in ["湿热质", "痰湿质"]:
                risk_factors.append("湿热体质，需注意清热化湿")
        
        return risk_factors

    async def _generate_improvement_suggestions(self, assessment: Dict[str, Any]) -> List[str]:
        """生成改善建议"""
        return [
            "保持规律的作息时间",
            "根据体质调整饮食结构",
            "适当进行体质相应的运动",
            "定期进行中医体检"
        ]

    async def _recommend_next_steps(self, assessment: Dict[str, Any]) -> List[str]:
        """推荐下一步行动"""
        return [
            "建议3个月后复查体质状况",
            "可考虑咨询专业中医师",
            "继续记录健康数据"
        ]

    def _personalize_search_results(self, results: List[Dict[str, Any]], 
                                  constitution_type: Optional[str]) -> List[Dict[str, Any]]:
        """个性化搜索结果"""
        if not constitution_type:
            return results
        
        # 根据体质类型调整搜索结果的相关性
        for result in results:
            if constitution_type in result.get("content", ""):
                result["relevance_score"] = result.get("relevance_score", 0.5) + 0.3
        
        # 按相关性排序
        return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)

    def _generate_morning_routine(self, constitution_type: str, seasonal_data: Dict[str, Any]) -> List[str]:
        """生成晨起养生建议"""
        base_routine = ["早起后喝一杯温水", "适当伸展身体"]
        
        if constitution_type == "阳虚质":
            base_routine.append("可适当晒太阳")
        elif constitution_type == "阴虚质":
            base_routine.append("避免过早起床")
            
        return base_routine

    def _generate_daily_diet_suggestions(self, constitution_type: str, seasonal_data: Dict[str, Any]) -> List[str]:
        """生成每日饮食建议"""
        base_diet = ["饮食清淡", "定时定量"]
        
        if constitution_type == "湿热质":
            base_diet.extend(["多食清热利湿食物", "避免辛辣油腻"])
        elif constitution_type == "气虚质":
            base_diet.extend(["适当补气食物", "如山药、大枣"])
            
        return base_diet

    def _generate_daily_exercise(self, constitution_type: str, seasonal_data: Dict[str, Any]) -> List[str]:
        """生成每日运动建议"""
        if constitution_type == "气虚质":
            return ["散步30分钟", "太极拳", "避免剧烈运动"]
        elif constitution_type == "阳虚质":
            return ["适度有氧运动", "避免大汗淋漓"]
        else:
            return ["适度运动", "保持活力"]

    def _generate_evening_routine(self, constitution_type: str, seasonal_data: Dict[str, Any]) -> List[str]:
        """生成晚间养生建议"""
        return ["睡前泡脚", "避免过度用眼", "保持心情平静"]

    def _generate_mindfulness_practice(self, constitution_type: str) -> List[str]:
        """生成正念练习建议"""
        if constitution_type == "气郁质":
            return ["深呼吸练习", "冥想10分钟", "听舒缓音乐"]
        else:
            return ["简单冥想", "感恩练习"]

    def _generate_daily_health_tips(self, constitution_type: str, seasonal_data: Dict[str, Any]) -> List[str]:
        """生成每日健康小贴士"""
        return [
            f"今日体质养生重点：{constitution_type}体质需要...",
            "保持心情愉悦，有助于气血调和",
            "适当的运动是最好的养生方式"
        ]

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "service": "TCMService",
            "status": "healthy",
            "mongodb_connected": self.mongodb is not None,
            "redis_connected": self.redis is not None
        }

        # 检查中医微服务连接状态
        tcm_services_status = await self.tcm_client.health_check()
        status.update(tcm_services_status)

        # 测试数据库连接
        if self.mongodb:
            try:
                await self.mongodb.command("ping")
                status["mongodb_ping"] = True
            except Exception:
                status["mongodb_ping"] = False
                status["status"] = "degraded"

        return status