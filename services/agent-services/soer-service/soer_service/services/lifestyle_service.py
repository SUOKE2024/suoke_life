"""
生活方式服务类

处理运动计划、睡眠分析、压力管理等生活方式相关的业务逻辑
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from statistics import mean

from .base_service import BaseService
from ..models.lifestyle import ExercisePlan, SleepAnalysis, StressAssessment


class LifestyleService(BaseService):
    """生活方式服务类"""

    def __init__(self):
        super().__init__()
        self.exercise_collection = "exercise_plans"
        self.sleep_collection = "sleep_data"
        self.stress_collection = "stress_assessments"
        self.activity_collection = "activity_logs"

    async def create_exercise_plan(self, user_id: str, goals: Dict[str, Any], preferences: Dict[str, Any]) -> ExercisePlan:
        """创建个性化运动计划"""
        try:
            # 获取用户档案
            user_profile = await self._get_user_profile(user_id)
            
            # 分析用户健康状况
            health_status = await self._assess_fitness_level(user_id)
            
            # 生成运动计划
            plan = await self._generate_exercise_plan(user_profile, goals, preferences, health_status)
            
            exercise_plan = ExercisePlan(
                plan_id=str(uuid.uuid4()),
                user_id=user_id,
                plan_name=f"个性化运动计划 - {datetime.now().strftime('%Y%m%d')}",
                **plan,
                created_at=datetime.now()
            )

            # 保存运动计划
            if self.mongodb:
                await self.mongodb[self.exercise_collection].insert_one(exercise_plan.dict())

            await self.log_operation("create_exercise_plan", True, {"user_id": user_id})
            return exercise_plan

        except Exception as e:
            await self.log_operation("create_exercise_plan", False, {"error": str(e)})
            raise

    async def analyze_sleep_data(self, user_id: str, sleep_data: Dict[str, Any]) -> SleepAnalysis:
        """分析睡眠数据"""
        try:
            # 获取历史睡眠数据
            sleep_history = await self._get_sleep_history(user_id, days=30)
            
            # 分析睡眠质量
            quality_analysis = self._analyze_sleep_quality(sleep_data, sleep_history)
            
            # 分析睡眠模式
            pattern_analysis = self._analyze_sleep_patterns(sleep_history)
            
            # 生成睡眠建议
            recommendations = self._generate_sleep_recommendations(quality_analysis, pattern_analysis)

            sleep_analysis = SleepAnalysis(
                analysis_id=str(uuid.uuid4()),
                user_id=user_id,
                sleep_date=sleep_data.get("date", datetime.now().date()),
                sleep_duration=sleep_data.get("duration", 0),
                sleep_efficiency=quality_analysis.get("efficiency", 0),
                deep_sleep_percentage=sleep_data.get("deep_sleep_percentage", 0),
                rem_sleep_percentage=sleep_data.get("rem_sleep_percentage", 0),
                wake_up_count=sleep_data.get("wake_up_count", 0),
                sleep_quality_score=quality_analysis.get("quality_score", 0),
                recommendations=recommendations,
                sleep_debt=pattern_analysis.get("sleep_debt", 0),
                consistency_score=pattern_analysis.get("consistency_score", 0),
                created_at=datetime.now()
            )

            # 保存分析结果
            if self.mongodb:
                await self.mongodb[self.sleep_collection].insert_one(sleep_analysis.dict())

            await self.log_operation("analyze_sleep_data", True, {"user_id": user_id})
            return sleep_analysis

        except Exception as e:
            await self.log_operation("analyze_sleep_data", False, {"error": str(e)})
            raise

    async def assess_stress_level(self, user_id: str, assessment_data: Dict[str, Any]) -> StressAssessment:
        """评估压力水平"""
        try:
            # 计算压力评分
            stress_score = self._calculate_stress_score(assessment_data)
            
            # 分析压力来源
            stress_sources = self._identify_stress_sources(assessment_data)
            
            # 获取历史压力数据
            stress_history = await self._get_stress_history(user_id, days=30)
            
            # 分析压力趋势
            stress_trend = self._analyze_stress_trend(stress_history, stress_score)
            
            # 生成压力管理建议
            management_strategies = self._generate_stress_management_strategies(
                stress_score, stress_sources, assessment_data
            )

            stress_assessment = StressAssessment(
                assessment_id=str(uuid.uuid4()),
                user_id=user_id,
                stress_level=self._categorize_stress_level(stress_score),
                stress_score=stress_score,
                stress_sources=stress_sources,
                physical_symptoms=assessment_data.get("physical_symptoms", []),
                emotional_symptoms=assessment_data.get("emotional_symptoms", []),
                behavioral_symptoms=assessment_data.get("behavioral_symptoms", []),
                coping_strategies=assessment_data.get("current_coping", []),
                management_recommendations=management_strategies,
                stress_trend=stress_trend,
                created_at=datetime.now()
            )

            # 保存评估结果
            if self.mongodb:
                await self.mongodb[self.stress_collection].insert_one(stress_assessment.dict())

            await self.log_operation("assess_stress_level", True, {"user_id": user_id})
            return stress_assessment

        except Exception as e:
            await self.log_operation("assess_stress_level", False, {"error": str(e)})
            raise

    async def get_lifestyle_recommendations(self, user_id: str) -> Dict[str, Any]:
        """获取生活方式建议"""
        try:
            # 获取用户档案
            user_profile = await self._get_user_profile(user_id)
            
            # 获取最新的分析数据
            latest_sleep = await self._get_latest_sleep_analysis(user_id)
            latest_stress = await self._get_latest_stress_assessment(user_id)
            latest_exercise = await self._get_latest_exercise_plan(user_id)
            
            # 分析活动水平
            activity_analysis = await self._analyze_activity_level(user_id)

            recommendations = {
                "exercise": self._get_exercise_recommendations(user_profile, latest_exercise, activity_analysis),
                "sleep": self._get_sleep_recommendations(user_profile, latest_sleep),
                "stress_management": self._get_stress_management_recommendations(user_profile, latest_stress),
                "nutrition": self._get_lifestyle_nutrition_recommendations(user_profile),
                "work_life_balance": self._get_work_life_balance_recommendations(user_profile),
                "social_wellness": self._get_social_wellness_recommendations(user_profile),
                "mindfulness": self._get_mindfulness_recommendations(user_profile, latest_stress),
                "habit_formation": self._get_habit_formation_recommendations(user_profile)
            }

            await self.log_operation("get_lifestyle_recommendations", True, {"user_id": user_id})
            return recommendations

        except Exception as e:
            await self.log_operation("get_lifestyle_recommendations", False, {"error": str(e)})
            return {}

    async def track_activity(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """记录活动数据"""
        try:
            activity_record = {
                "record_id": str(uuid.uuid4()),
                "user_id": user_id,
                "activity_type": activity_data.get("type", "other"),
                "duration": activity_data.get("duration", 0),
                "intensity": activity_data.get("intensity", "moderate"),
                "calories_burned": activity_data.get("calories_burned", 0),
                "steps": activity_data.get("steps", 0),
                "distance": activity_data.get("distance", 0),
                "heart_rate_avg": activity_data.get("heart_rate_avg"),
                "heart_rate_max": activity_data.get("heart_rate_max"),
                "notes": activity_data.get("notes", ""),
                "timestamp": datetime.now()
            }

            # 保存活动记录
            if self.mongodb:
                await self.mongodb[self.activity_collection].insert_one(activity_record)

            # 更新每日活动统计
            daily_stats = await self._update_daily_activity_stats(user_id, activity_record)

            # 检查目标完成情况
            goal_progress = await self._check_activity_goals(user_id, daily_stats)

            await self.log_operation("track_activity", True, {"user_id": user_id})
            return {
                "record_id": activity_record["record_id"],
                "daily_stats": daily_stats,
                "goal_progress": goal_progress,
                "recommendations": self._get_activity_feedback(activity_record, daily_stats)
            }

        except Exception as e:
            await self.log_operation("track_activity", False, {"error": str(e)})
            raise

    async def _generate_exercise_plan(self, user_profile: Dict[str, Any], goals: Dict[str, Any], 
                                    preferences: Dict[str, Any], health_status: Dict[str, Any]) -> Dict[str, Any]:
        """生成个性化运动计划"""
        
        # 确定运动频率和强度
        fitness_level = health_status.get("fitness_level", "beginner")
        weekly_frequency = self._determine_exercise_frequency(fitness_level, goals)
        
        # 生成运动类型组合
        exercise_types = self._select_exercise_types(goals, preferences, fitness_level)
        
        # 创建周计划
        weekly_schedule = self._create_weekly_schedule(exercise_types, weekly_frequency, preferences)
        
        # 设置进阶计划
        progression_plan = self._create_progression_plan(fitness_level, goals)

        return {
            "goal_type": goals.get("primary_goal", "general_fitness"),
            "fitness_level": fitness_level,
            "duration_weeks": goals.get("duration_weeks", 12),
            "weekly_frequency": weekly_frequency,
            "exercise_types": exercise_types,
            "weekly_schedule": weekly_schedule,
            "progression_plan": progression_plan,
            "equipment_needed": self._determine_equipment_needs(exercise_types),
            "safety_guidelines": self._get_safety_guidelines(health_status),
            "progress_tracking": self._define_progress_metrics(goals)
        }

    def _analyze_sleep_quality(self, sleep_data: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析睡眠质量"""
        duration = sleep_data.get("duration", 0)
        efficiency = sleep_data.get("efficiency", 0)
        deep_sleep = sleep_data.get("deep_sleep_percentage", 0)
        rem_sleep = sleep_data.get("rem_sleep_percentage", 0)
        
        # 计算质量评分
        duration_score = min(100, max(0, (duration - 4) / 4 * 100)) if duration > 0 else 0
        efficiency_score = efficiency
        deep_sleep_score = min(100, deep_sleep / 20 * 100)
        rem_sleep_score = min(100, rem_sleep / 25 * 100)
        
        quality_score = mean([duration_score, efficiency_score, deep_sleep_score, rem_sleep_score])
        
        return {
            "quality_score": quality_score,
            "efficiency": efficiency,
            "duration_adequacy": "adequate" if duration >= 7 else "insufficient",
            "sleep_architecture": "normal" if deep_sleep >= 15 and rem_sleep >= 20 else "suboptimal"
        }

    def _calculate_stress_score(self, assessment_data: Dict[str, Any]) -> float:
        """计算压力评分"""
        # 基于问卷回答计算压力评分
        stress_indicators = assessment_data.get("stress_indicators", {})
        
        score = 0.0
        total_questions = 0
        
        for question, answer in stress_indicators.items():
            if isinstance(answer, (int, float)):
                score += answer
                total_questions += 1
            elif isinstance(answer, str):
                # 转换文本答案为数值
                score += self._convert_text_to_score(answer)
                total_questions += 1
        
        return (score / total_questions * 20) if total_questions > 0 else 0

    def _categorize_stress_level(self, stress_score: float) -> str:
        """分类压力水平"""
        if stress_score < 20:
            return "low"
        elif stress_score < 40:
            return "mild"
        elif stress_score < 60:
            return "moderate"
        elif stress_score < 80:
            return "high"
        else:
            return "severe"

    def _generate_stress_management_strategies(self, stress_score: float, stress_sources: List[str], 
                                             assessment_data: Dict[str, Any]) -> List[str]:
        """生成压力管理策略"""
        strategies = []
        
        # 基于压力水平推荐策略
        if stress_score >= 60:
            strategies.extend([
                "考虑寻求专业心理健康支持",
                "实施每日冥想或深呼吸练习",
                "建立严格的睡眠时间表"
            ])
        
        if stress_score >= 40:
            strategies.extend([
                "增加规律的体育锻炼",
                "练习渐进性肌肉放松",
                "限制咖啡因摄入"
            ])
        
        # 基于压力来源推荐策略
        if "work" in stress_sources:
            strategies.extend([
                "设置工作边界和休息时间",
                "学习时间管理技巧",
                "与上级讨论工作负荷"
            ])
        
        if "relationships" in stress_sources:
            strategies.extend([
                "改善沟通技巧",
                "设置健康的人际边界",
                "寻求关系咨询"
            ])
        
        if "financial" in stress_sources:
            strategies.extend([
                "制定预算计划",
                "寻求财务咨询",
                "探索增加收入的机会"
            ])
        
        return list(set(strategies))  # 去重

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "service": "LifestyleService",
            "status": "healthy",
            "mongodb_connected": self.mongodb is not None,
            "redis_connected": self.redis is not None
        }

        # 测试数据库连接
        if self.mongodb:
            try:
                await self.mongodb.command("ping")
                status["mongodb_ping"] = True
            except Exception:
                status["mongodb_ping"] = False
                status["status"] = "degraded"

        return status