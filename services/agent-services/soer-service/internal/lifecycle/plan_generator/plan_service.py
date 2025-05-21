"""
健康计划生成服务 - 基于体质和健康目标创建个性化健康计划
"""
import logging
import uuid
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Any

from internal.repository.models.health_plan import (
    HealthPlan, DietRecommendation, ExerciseRecommendation,
    SleepRecommendation, StressManagement, SupplementRecommendation,
    EnvironmentalSuggestion, DailySchedule, MonitoringPlan,
    ProgressMilestone
)
from internal.lifecycle.health_profile.profile_service import HealthProfileService

logger = logging.getLogger(__name__)


class HealthPlanService:
    """健康计划生成服务，负责基于体质和健康目标创建个性化健康计划"""
    
    def __init__(self, config: Dict, repos):
        """初始化健康计划服务
        
        Args:
            config: 配置信息
            repos: 存储库
        """
        self.config = config
        self.repos = repos
        logger.info("初始化健康计划服务")
        
        # 如果有健康计划仓库，则使用它
        self.plan_repo = getattr(repos, "health_plan_repo", None)
        
        # 健康画像服务
        self.health_profile_service = HealthProfileService(config, repos)
        
        # 食物和运动推荐数据库
        self.food_db = self._load_food_database()
        self.exercise_db = self._load_exercise_database()
    
    async def generate_plan(self, user_id: str, constitution_type: str, 
                        health_goals: List[str], preferences: Dict[str, List[str]],
                        current_season: str) -> HealthPlan:
        """生成健康计划
        
        根据用户体质类型、健康目标和偏好生成个性化健康计划
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_goals: 健康目标列表
            preferences: 偏好，如饮食限制、运动偏好等
            current_season: 当前季节
            
        Returns:
            生成的健康计划
        """
        logger.info(f"为用户 {user_id} 生成健康计划")
        
        # 获取用户健康画像
        health_profile = await self.health_profile_service.get_profile(user_id)
        
        # 生成计划ID
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        # 计划时间范围（默认3个月）
        start_date = datetime.now()
        end_date = start_date + timedelta(days=90)
        
        # 计划名称
        plan_name = self._generate_plan_name(constitution_type, health_goals)
        
        # 根据体质类型生成饮食建议
        diet_recommendations = await self._generate_diet_recommendations(
            constitution_type, current_season, preferences.get("diet_restrictions", []),
            health_profile
        )
        
        # 生成运动建议
        exercise_recommendations = await self._generate_exercise_recommendations(
            constitution_type, health_goals, preferences.get("exercise_preferences", []),
            health_profile
        )
        
        # 生成睡眠建议
        sleep_recommendations = await self._generate_sleep_recommendations(
            constitution_type, health_profile
        )
        
        # 生成压力管理建议
        stress_management = await self._generate_stress_management(
            constitution_type, health_profile
        )
        
        # 生成营养补充建议
        supplement_recommendations = await self._generate_supplement_recommendations(
            constitution_type, current_season, health_profile
        )
        
        # 生成环境建议
        environmental_suggestions = await self._generate_environmental_suggestions(
            constitution_type, current_season
        )
        
        # 生成日常作息建议
        daily_schedule = await self._generate_daily_schedule(
            constitution_type, health_profile
        )
        
        # 生成监测计划
        monitoring_plan = await self._generate_monitoring_plan(
            constitution_type, health_goals, health_profile
        )
        
        # 生成里程碑
        milestones = await self._generate_milestones(
            health_goals, start_date, end_date
        )
        
        # 预期结果
        expected_outcomes = await self._generate_expected_outcomes(
            constitution_type, health_goals, health_profile
        )
        
        # 计划调整触发条件
        adjustment_triggers = [
            "体质评估变化超过30%",
            "健康目标达成率低于50%",
            "身体指标出现异常变化",
            "用户主观感受明显恶化",
            "季节变换"
        ]
        
        # 生成计划标签
        tags = await self._generate_plan_tags(
            constitution_type, health_goals, current_season
        )
        
        # 创建健康计划
        health_plan = HealthPlan(
            plan_id=plan_id,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            plan_version="1.0",
            plan_name=plan_name,
            start_date=start_date,
            end_date=end_date,
            health_goals=health_goals,
            constitution_type=constitution_type,
            current_season=current_season,
            diet_recommendations=diet_recommendations,
            exercise_recommendations=exercise_recommendations,
            sleep_recommendations=sleep_recommendations,
            stress_management=stress_management,
            supplement_recommendations=supplement_recommendations,
            environmental_suggestions=environmental_suggestions,
            daily_schedule=daily_schedule,
            monitoring_plan=monitoring_plan,
            milestones=milestones,
            expected_outcomes=expected_outcomes,
            adjustment_triggers=adjustment_triggers,
            tags=tags
        )
        
        # 保存健康计划
        if self.plan_repo:
            try:
                await self.plan_repo.save(health_plan)
                logger.info(f"健康计划已保存, plan_id: {plan_id}")
            except Exception as e:
                logger.error(f"保存健康计划失败: {str(e)}")
        
        return health_plan
    
    async def get_plan(self, plan_id: str) -> Optional[HealthPlan]:
        """获取健康计划
        
        Args:
            plan_id: 计划ID
            
        Returns:
            健康计划或None
        """
        logger.info(f"获取健康计划 {plan_id}")
        return await self.plan_repo.get_by_id(plan_id)
    
    async def get_active_plan(self, user_id: str) -> Optional[HealthPlan]:
        """获取用户当前活跃的健康计划
        
        Args:
            user_id: 用户ID
            
        Returns:
            当前活跃的健康计划或None
        """
        logger.info(f"获取用户 {user_id} 当前活跃的健康计划")
        return await self.plan_repo.get_active_plan(user_id)
    
    async def get_plan_summary(self, plan_id: str) -> Dict[str, Any]:
        """获取健康计划摘要
        
        Args:
            plan_id: 计划ID
            
        Returns:
            健康计划摘要
        """
        logger.info(f"获取健康计划摘要 {plan_id}")
        
        plan = await self.get_plan(plan_id)
        if not plan:
            return {"error": "计划不存在"}
        
        summary = {
            "plan_id": plan.plan_id,
            "plan_name": plan.plan_name,
            "user_id": plan.user_id,
            "constitution_type": plan.constitution_type,
            "health_goals": plan.health_goals,
            "start_date": plan.start_date.isoformat(),
            "end_date": plan.end_date.isoformat() if plan.end_date else None,
            "current_season": plan.current_season,
            "key_recommendations": {
                "diet": [f"多吃: {', '.join(plan.diet_recommendations.recommended_foods[:3])}",
                        f"少吃: {', '.join(plan.diet_recommendations.avoid_foods[:3])}"],
                "exercise": [f"推荐运动: {', '.join(plan.exercise_recommendations.exercise_types[:3])}",
                            f"频率: 每周{plan.exercise_recommendations.weekly_frequency}次"],
                "sleep": [f"建议睡眠: {plan.sleep_recommendations.recommended_duration}小时",
                        f"就寝时间: {plan.sleep_recommendations.bedtime.strftime('%H:%M')}"]
            },
            "milestones": [
                {
                    "name": m.milestone_name,
                    "date": m.target_date.isoformat()
                } for m in plan.milestones[:3]
            ],
            "tags": plan.tags
        }
        
        return summary
    
    async def update_plan_progress(self, plan_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新健康计划进度
        
        Args:
            plan_id: 计划ID
            progress_data: 进度数据
            
        Returns:
            更新结果
        """
        logger.info(f"更新健康计划 {plan_id} 进度")
        
        plan = await self.get_plan(plan_id)
        if not plan:
            return {"error": "计划不存在"}
        
        # 更新进度
        # 此处略去实现，可根据需要添加
        
        return {"status": "success", "message": "进度已更新"}
    
    async def _generate_diet_recommendations(self, constitution_type: str, 
                                         current_season: str, 
                                         diet_restrictions: List[str]) -> DietRecommendation:
        """生成饮食建议
        
        基于体质类型、当前季节和饮食限制生成个性化饮食建议
        
        Args:
            constitution_type: 体质类型
            current_season: 当前季节
            diet_restrictions: 饮食限制
            
        Returns:
            饮食建议
        """
        # 获取体质食材数据库
        tcm_food_data = await self.repos.nutrition_repo.get_tcm_food_data(constitution_type)
        
        # 基于体质生成建议食物清单
        recommended_foods = tcm_food_data.get("recommended_foods", [])
        avoid_foods = tcm_food_data.get("avoid_foods", [])
        
        # 考虑季节因素
        seasonal_foods = await self.repos.nutrition_repo.get_seasonal_foods(current_season)
        
        # 合并并过滤建议食物
        recommended_foods = [food for food in recommended_foods if food in seasonal_foods.get("recommended", [])][:20]
        
        # 考虑饮食限制
        if diet_restrictions:
            # 从食物数据库获取受限食物
            restricted_foods = await self.repos.nutrition_repo.get_restricted_foods(diet_restrictions)
            # 过滤掉受限食物
            recommended_foods = [food for food in recommended_foods if food not in restricted_foods]
            # 添加受限食物到避免列表
            avoid_foods = list(set(avoid_foods + restricted_foods))
        
        # 生成食谱
        recipes = await self.repos.nutrition_repo.get_recipes_for_constitution(
            constitution_type, current_season, diet_restrictions
        )
        
        # 生成膳食分配比例
        meal_distribution = {
            "早餐": 0.3,
            "午餐": 0.4,
            "晚餐": 0.25,
            "加餐": 0.05
        }
        
        # 根据体质生成特殊饮食指导
        special_guidance = ""
        if constitution_type == "阳虚质":
            special_guidance = "饮食宜温热，避免生冷寒凉食物，建议少食多餐，增加温补食材。"
        elif constitution_type == "阴虚质":
            special_guidance = "饮食宜清淡滋润，避免辛辣燥热食物，建议增加水分摄入。"
        elif constitution_type == "痰湿质":
            special_guidance = "饮食宜清淡，少油腻，控制总热量，建议少食多餐，增加膳食纤维。"
        
        # 中医饮食原则
        tcm_principles = await self.repos.nutrition_repo.get_tcm_diet_principles(constitution_type)
        
        return DietRecommendation(
            food_category="综合推荐",
            recommended_foods=recommended_foods,
            avoid_foods=avoid_foods[:15],  # 限制避免食物列表长度
            meal_distribution=meal_distribution,
            portion_guidance="一般建议每餐七分饱，晚餐应清淡且避免过晚进食",
            special_guidance=special_guidance,
            tcm_principles=tcm_principles,
            recipes=recipes[:5]  # 限制食谱数量
        )
    
    async def _generate_exercise_recommendations(self, constitution_type: str, 
                                             health_goals: List[str],
                                             exercise_preferences: List[str],
                                             health_profile: Any) -> ExerciseRecommendation:
        """生成运动建议
        
        基于体质类型、健康目标和运动偏好生成个性化运动建议
        
        Args:
            constitution_type: 体质类型
            health_goals: 健康目标
            exercise_preferences: 运动偏好
            health_profile: 健康画像
            
        Returns:
            运动建议
        """
        # 根据体质类型推荐运动类型
        exercise_types = []
        
        # 默认值
        frequency = 3  # 每周3次
        duration = 30  # 每次30分钟
        intensity = "中等"
        
        # 根据体质调整推荐
        if constitution_type == "阳虚质":
            exercise_types = ["太极拳", "八段锦", "散步", "慢跑", "温水游泳"]
            intensity = "低到中等"
        elif constitution_type == "阴虚质":
            exercise_types = ["太极拳", "瑜伽", "散步", "游泳", "气功"]
            intensity = "低到中等"
            duration = 20  # 每次20分钟
        elif constitution_type == "痰湿质":
            exercise_types = ["快走", "慢跑", "游泳", "健身操", "骑车"]
            intensity = "中到高等"
            duration = 40  # 每次40分钟
            frequency = 4  # 每周4次
        elif constitution_type == "湿热质":
            exercise_types = ["游泳", "慢跑", "太极拳", "骑车", "健身操"]
            intensity = "中等"
        elif constitution_type == "气虚质":
            exercise_types = ["太极拳", "八段锦", "散步", "气功", "慢瑜伽"]
            intensity = "低等"
            duration = 20  # 每次20分钟
        elif constitution_type == "气郁质":
            exercise_types = ["快走", "慢跑", "瑜伽", "舞蹈", "拳击"]
            intensity = "中到高等"
        elif constitution_type == "血瘀质":
            exercise_types = ["慢跑", "游泳", "快走", "太极拳", "骑车"]
            intensity = "中等"
        elif constitution_type == "特禀质":
            exercise_types = ["室内散步", "低强度瑜伽", "太极拳", "气功", "游泳"]
            intensity = "低等"
            duration = 20  # 每次20分钟
        elif constitution_type == "平和质":
            exercise_types = ["慢跑", "游泳", "瑜伽", "太极拳", "跳绳", "登山", "球类运动"]
            intensity = "中到高等"
            duration = 40  # 每次40分钟
            frequency = 4  # 每周4次
        
        # 考虑用户偏好
        if exercise_preferences:
            # 优先选择用户偏好中的运动
            preferred_types = [exercise for exercise in exercise_types if exercise in exercise_preferences]
            # 如果有匹配的偏好，则使用偏好；否则保持原推荐
            if preferred_types:
                exercise_types = preferred_types + [e for e in exercise_types if e not in preferred_types]
        
        # 构建运动建议
        exercise_recommendations = ExerciseRecommendation(
            exercise_types=exercise_types[:5],  # 限制为前5项
            weekly_frequency=frequency,
            duration=duration,
            intensity=intensity
        )
        
        return exercise_recommendations
    
    async def _generate_sleep_recommendations(self, constitution_type: str, 
                                          health_profile: Any) -> SleepRecommendation:
        """生成睡眠建议
        
        基于体质类型和健康画像生成个性化睡眠建议
        
        Args:
            constitution_type: 体质类型
            health_profile: 健康画像
            
        Returns:
            睡眠建议
        """
        # 此处略去实现，返回默认的睡眠建议
        return SleepRecommendation(
            recommended_duration=7.5,
            bedtime=time(22, 30),
            wake_time=time(6, 0),
            pre_sleep_routine=["热水泡脚", "冥想放松", "阅读纸质书"],
            environment_tips=["保持安静", "温度适中", "避免强光"],
            avoid_activities=["使用电子设备", "激烈运动", "摄入咖啡因"],
            tcm_sleep_aids=["穴位按摩", "薰衣草精油", "枕芯菊花茶包"]
        )
    
    async def _generate_stress_management(self, constitution_type: str, 
                                       health_profile: Any) -> StressManagement:
        """生成压力管理建议
        
        基于体质类型和健康画像生成个性化压力管理建议
        
        Args:
            constitution_type: 体质类型
            health_profile: 健康画像
            
        Returns:
            压力管理建议
        """
        # 此处略去实现，返回默认的压力管理建议
        return StressManagement(
            relaxation_techniques=["深呼吸练习", "渐进性肌肉放松", "正念冥想"],
            meditation_practice={"type": "正念冥想", "duration": 15, "frequency": "每日"},
            emotional_regulation=["情绪日记", "认知重构", "接纳练习"],
            leisure_activities=["户外散步", "园艺", "绘画", "听音乐"],
            tcm_emotion_regulation=["肝郁调理", "心神安宁", "情志调和"]
        )
    
    async def _generate_supplement_recommendations(self, constitution_type: str, 
                                               current_season: str,
                                               health_profile: Any) -> SupplementRecommendation:
        """生成营养补充建议
        
        基于体质类型、当前季节和健康画像生成个性化营养补充建议
        
        Args:
            constitution_type: 体质类型
            current_season: 当前季节
            health_profile: 健康画像
            
        Returns:
            营养补充建议
        """
        # 此处略去实现，返回默认的营养补充建议
        return SupplementRecommendation(
            supplements=[
                {"name": "维生素D", "dosage": "1000IU", "frequency": "每日", "note": "早餐后服用"},
                {"name": "鱼油", "dosage": "1000mg", "frequency": "每日", "note": "餐后服用"}
            ],
            herbs=[
                {"name": "西洋参", "dosage": "3g", "frequency": "每日", "note": "早上服用"},
                {"name": "枸杞子", "dosage": "10g", "frequency": "每日", "note": "泡水饮用"}
            ],
            special_notes="请在医生或专业人士指导下使用补充剂和草药"
        )
    
    async def _generate_environmental_suggestions(self, constitution_type: str, 
                                              current_season: str) -> EnvironmentalSuggestion:
        """生成环境建议
        
        基于体质类型和当前季节生成个性化环境建议
        
        Args:
            constitution_type: 体质类型
            current_season: 当前季节
            
        Returns:
            环境建议
        """
        # 此处略去实现，返回默认的环境建议
        return EnvironmentalSuggestion(
            living_environment=["保持室内通风", "适当湿度控制", "使用空气净化器"],
            work_environment=["保持工作区整洁", "定期休息", "护眼措施"],
            seasonal_adjustments={
                "春季": ["增加户外活动", "防风防寒"],
                "夏季": ["防暑降温", "避免强烈阳光直射"],
                "秋季": ["预防感冒", "增加保暖"],
                "冬季": ["保暖防寒", "增加室内湿度"]
            },
            travel_suggestions=["根据目的地气候准备合适衣物", "携带必要健康用品", "避免过度疲劳"]
        )
    
    async def _generate_daily_schedule(self, constitution_type: str, 
                                    health_profile: Any) -> DailySchedule:
        """生成日常作息建议
        
        基于体质类型和健康画像生成个性化日常作息建议
        
        Args:
            constitution_type: 体质类型
            health_profile: 健康画像
            
        Returns:
            日常作息建议
        """
        # 此处略去实现，返回默认的日常作息建议
        return DailySchedule(
            weekday_schedule={
                "06:00-06:30": "起床洗漱",
                "06:30-07:00": "晨练",
                "07:00-07:30": "早餐",
                "12:00-13:00": "午餐+午休",
                "18:00-19:00": "晚餐",
                "21:00-22:00": "放松活动",
                "22:30": "就寝"
            },
            weekend_schedule={
                "07:00-07:30": "起床洗漱",
                "07:30-08:30": "晨练",
                "08:30-09:00": "早餐",
                "12:00-13:30": "午餐+午休",
                "18:00-19:00": "晚餐",
                "21:30-22:30": "放松活动",
                "23:00": "就寝"
            },
            key_timings={
                "起床": time(6, 0),
                "早餐": time(7, 0),
                "午餐": time(12, 0),
                "晚餐": time(18, 0),
                "就寝": time(22, 30)
            },
            tcm_timing_principles=[
                "子时(23:00-1:00)为胆经当令，宜熟睡",
                "卯时(5:00-7:00)为大肠经当令，宜排便",
                "辰时(7:00-9:00)为胃经当令，宜早餐",
                "午时(11:00-13:00)为心经当令，宜小憩",
                "酉时(17:00-19:00)为肾经当令，宜晚餐"
            ]
        )
    
    async def _generate_monitoring_plan(self, constitution_type: str, 
                                     health_goals: List[str],
                                     health_profile: Any) -> MonitoringPlan:
        """生成监测计划
        
        基于体质类型、健康目标和健康画像生成个性化监测计划
        
        Args:
            constitution_type: 体质类型
            health_goals: 健康目标
            health_profile: 健康画像
            
        Returns:
            监测计划
        """
        # 此处略去实现，返回默认的监测计划
        return MonitoringPlan(
            metrics_to_track=["体重", "睡眠时长", "步数", "心率", "情绪状态"],
            tracking_frequency={
                "体重": "每周一次",
                "睡眠时长": "每日",
                "步数": "每日", 
                "心率": "持续监测",
                "情绪状态": "每日"
            },
            target_values={
                "体重": "BMI 18.5-24.9",
                "睡眠时长": "7-8小时",
                "步数": "10000步/天",
                "心率": "60-100次/分钟",
                "情绪状态": "积极稳定"
            },
            warning_thresholds={
                "体重": "月变化超过3%",
                "睡眠时长": "连续3天低于6小时",
                "步数": "连续5天低于5000步",
                "心率": "静息心率超过100或低于50",
                "情绪状态": "连续3天消极情绪"
            }
        )
    
    async def _generate_milestones(self, health_goals: List[str], 
                               start_date: datetime,
                               end_date: datetime) -> List[ProgressMilestone]:
        """生成里程碑
        
        基于健康目标和计划时间范围生成里程碑
        
        Args:
            health_goals: 健康目标
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            里程碑列表
        """
        # 此处略去实现，返回默认的里程碑
        milestones = []
        
        # 计划持续天数
        duration_days = (end_date - start_date).days
        
        # 第一个月里程碑
        milestone1_date = start_date + timedelta(days=duration_days // 3)
        milestones.append(ProgressMilestone(
            milestone_name="第一阶段目标",
            target_date=milestone1_date,
            description="建立健康习惯，适应计划",
            metrics=[
                {"name": "计划执行率", "target": "70%"},
                {"name": "主观感受", "target": "有所改善"}
            ],
            rewards=["健康徽章", "积分奖励"]
        ))
        
        # 第二个月里程碑
        milestone2_date = start_date + timedelta(days=duration_days * 2 // 3)
        milestones.append(ProgressMilestone(
            milestone_name="第二阶段目标",
            target_date=milestone2_date,
            description="巩固健康习惯，观察改善",
            metrics=[
                {"name": "计划执行率", "target": "80%"},
                {"name": "健康指标", "target": "明显改善"}
            ],
            rewards=["健康勋章", "定制服务券"]
        ))
        
        # 最终里程碑
        milestones.append(ProgressMilestone(
            milestone_name="最终目标",
            target_date=end_date,
            description="实现健康转变，建立长期习惯",
            metrics=[
                {"name": "计划执行率", "target": "90%"},
                {"name": "健康目标", "target": "全面达成"}
            ],
            rewards=["健康大师勋章", "专业定制服务"]
        ))
        
        return milestones
    
    async def _generate_expected_outcomes(self, constitution_type: str, 
                                       health_goals: List[str],
                                       health_profile: Any) -> Dict[str, Any]:
        """生成预期结果
        
        基于体质类型、健康目标和健康画像生成预期结果
        
        Args:
            constitution_type: 体质类型
            health_goals: 健康目标
            health_profile: 健康画像
            
        Returns:
            预期结果
        """
        # 此处略去实现，返回默认的预期结果
        return {
            "physical_improvements": [
                "身体活力提升",
                "睡眠质量改善",
                "体重达到健康范围"
            ],
            "tcm_outcomes": [
                "体质偏颇减轻",
                "气血功能改善",
                "抵抗力增强"
            ],
            "lifestyle_changes": [
                "建立健康饮食习惯",
                "形成规律运动习惯",
                "学会有效压力管理"
            ],
            "timeframe": {
                "short_term": "1个月内感觉活力提升",
                "medium_term": "2-3个月内体质明显改善",
                "long_term": "3个月后体质逐步向平和质转变"
            }
        }
    
    async def _generate_plan_tags(self, constitution_type: str, 
                              health_goals: List[str],
                              current_season: str) -> List[str]:
        """生成计划标签
        
        基于体质类型、健康目标和当前季节生成计划标签
        
        Args:
            constitution_type: 体质类型
            health_goals: 健康目标
            current_season: 当前季节
            
        Returns:
            计划标签列表
        """
        tags = []
        
        # 添加体质相关标签
        if constitution_type == "阳虚质":
            tags.extend(["温补阳气", "固护阳气", "驱寒保暖"])
        elif constitution_type == "阴虚质":
            tags.extend(["滋阴清热", "养阴润燥", "清心安神"])
        elif constitution_type == "痰湿质":
            tags.extend(["化痰祛湿", "健脾利湿", "轻身减脂"])
        elif constitution_type == "气虚质":
            tags.extend(["补气健脾", "益气固表", "调理脾肺"])
        elif constitution_type == "血瘀质":
            tags.extend(["活血化瘀", "通络止痛", "改善循环"])
        elif constitution_type == "气郁质":
            tags.extend(["疏肝理气", "解郁安神", "情志调节"])
        
        # 添加季节相关标签
        if current_season == "春季":
            tags.append("春季养肝")
        elif current_season == "夏季":
            tags.append("夏季养心")
        elif current_season == "秋季":
            tags.append("秋季养肺")
        elif current_season == "冬季":
            tags.append("冬季养肾")
        
        # 添加健康目标相关标签
        for goal in health_goals:
            if "睡眠" in goal:
                tags.append("安神助眠")
            elif "体重" in goal:
                tags.append("轻身减重")
            elif "疲劳" in goal or "精力" in goal:
                tags.append("振奋精神")
            elif "免疫" in goal or "抵抗力" in goal:
                tags.append("增强卫气")
            elif "压力" in goal or "焦虑" in goal:
                tags.append("舒缓情志")
        
        # 限制标签数量
        return tags[:10]
    
    def _generate_plan_name(self, constitution_type: str, health_goals: List[str]) -> str:
        """生成计划名称
        
        Args:
            constitution_type: 体质类型
            health_goals: 健康目标列表
            
        Returns:
            计划名称
        """
        # 简化体质名称
        type_name = constitution_type.replace("质", "")
        
        # 根据主要健康目标生成名称
        if health_goals and len(health_goals) > 0:
            primary_goal = health_goals[0]
            if "减肥" in primary_goal or "体重" in primary_goal:
                return f"{type_name}型健康体重管理计划"
            elif "睡眠" in primary_goal:
                return f"{type_name}型优质睡眠提升计划"
            elif "压力" in primary_goal or "情绪" in primary_goal:
                return f"{type_name}型情绪平衡计划"
            elif "能量" in primary_goal or "精力" in primary_goal:
                return f"{type_name}型活力提升计划"
            elif "免疫" in primary_goal:
                return f"{type_name}型免疫力增强计划"
            else:
                return f"{type_name}型个性化健康计划"
        
        # 默认名称
        return f"{type_name}型平衡养生计划"
    
    def _load_food_database(self) -> Dict:
        """加载食物数据库
        
        Returns:
            食物数据库
        """
        # 从配置中加载食物数据库，实际项目中可能是从文件或数据库加载
        return self.config.get("nutrition", {}).get("constitutional_foods", {})
    
    def _load_exercise_database(self) -> Dict:
        """加载运动数据库
        
        Returns:
            运动数据库
        """
        # 从配置中加载运动数据库，实际项目中可能是从文件或数据库加载
        return {}