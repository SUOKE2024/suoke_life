"""
personalization_engine - 索克生活项目模块
"""

from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, List, Optional, Any, Tuple, Set

"""
个性化推荐引擎

基于用户画像、健康数据、行为模式和中医体质理论提供个性化健康建议
"""



class RecommendationType(Enum):
    """推荐类型"""
    HEALTH_ADVICE = "health_advice"
    DIET_PLAN = "diet_plan"
    EXERCISE_PLAN = "exercise_plan"
    TCM_THERAPY = "tcm_therapy"
    LIFESTYLE = "lifestyle"
    PREVENTION = "prevention"
    MEDICATION = "medication"
    CHECKUP = "checkup"

class PersonalityType(Enum):
    """个性类型"""
    CONSERVATIVE = "conservative"  # 保守型
    MODERATE = "moderate"         # 温和型
    AGGRESSIVE = "aggressive"     # 积极型
    CAUTIOUS = "cautious"        # 谨慎型

class HealthGoal(Enum):
    """健康目标"""
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    FITNESS = "fitness"
    STRESS_RELIEF = "stress_relief"
    SLEEP_IMPROVEMENT = "sleep_improvement"
    IMMUNITY_BOOST = "immunity_boost"
    CHRONIC_MANAGEMENT = "chronic_management"
    PREVENTION = "prevention"

@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    age: int
    gender: str
    height: float  # cm
    weight: float  # kg
    occupation: str
    lifestyle: str
    personality_type: PersonalityType
    health_goals: List[HealthGoal]
    medical_history: List[str]
    allergies: List[str]
    medications: List[str]
    preferences: Dict[str, Any]
    tcm_constitution: str  # 中医体质
    created_at: datetime
    updated_at: datetime

@dataclass
class HealthData:
    """健康数据"""
    user_id: str
    vital_signs: Dict[str, float]  # 生命体征
    lab_results: Dict[str, float]  # 化验结果
    symptoms: List[str]            # 症状
    sleep_data: Dict[str, Any]     # 睡眠数据
    activity_data: Dict[str, Any]  # 活动数据
    mood_data: Dict[str, Any]      # 情绪数据
    timestamp: datetime

@dataclass
class BehaviorPattern:
    """行为模式"""
    user_id: str
    query_patterns: List[str]      # 查询模式
    interaction_frequency: float   # 交互频率
    preferred_times: List[int]     # 偏好时间
    response_preferences: Dict[str, Any]  # 响应偏好
    engagement_level: float        # 参与度
    compliance_rate: float         # 依从性
    last_updated: datetime

@dataclass
class Recommendation:
    """推荐结果"""
    id: str
    user_id: str
    type: RecommendationType
    title: str
    content: str
    confidence: float
    priority: int
    reasoning: str
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None

class PersonalizationEngine:
    """个性化推荐引擎"""
    
    def __init__(
        self,
        user_profiles_db: Dict[str, UserProfile] = None,
        health_data_db: Dict[str, List[HealthData]] = None,
        behavior_patterns_db: Dict[str, BehaviorPattern] = None
    ):
        self.user_profiles = user_profiles_db or {}
        self.health_data = health_data_db or defaultdict(list)
        self.behavior_patterns = behavior_patterns_db or {}
        
        # 推荐模型
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.user_clusters = {}
        self.similarity_matrix = None
        
        # 中医体质推荐规则
        self.tcm_constitution_rules = self._load_tcm_rules()
        
        # 推荐缓存
        self.recommendation_cache: Dict[str, List[Recommendation]] = {}
        
        logger.info("个性化推荐引擎初始化完成")
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Recommendation]:
        """获取个性化推荐"""
        try:
            # 获取用户画像
            user_profile = await self.get_user_profile(user_id)
            if not user_profile:
                return await self._get_default_recommendations(query, limit)
            
            # 获取最新健康数据
            health_data = await self.get_latest_health_data(user_id)
            
            # 获取行为模式
            behavior_pattern = await self.get_behavior_pattern(user_id)
            
            # 生成推荐
            recommendations = []
            
            # 1. 基于中医体质的推荐
            tcm_recommendations = await self._get_tcm_recommendations(
                user_profile, health_data, query
            )
            recommendations.extend(tcm_recommendations)
            
            # 2. 基于健康目标的推荐
            goal_recommendations = await self._get_goal_based_recommendations(
                user_profile, health_data, query
            )
            recommendations.extend(goal_recommendations)
            
            # 3. 基于行为模式的推荐
            if behavior_pattern:
                behavior_recommendations = await self._get_behavior_based_recommendations(
                    user_profile, behavior_pattern, query
                )
                recommendations.extend(behavior_recommendations)
            
            # 4. 基于相似用户的推荐
            similar_recommendations = await self._get_collaborative_recommendations(
                user_id, query
            )
            recommendations.extend(similar_recommendations)
            
            # 5. 基于内容的推荐
            content_recommendations = await self._get_content_based_recommendations(
                user_profile, query
            )
            recommendations.extend(content_recommendations)
            
            # 排序和过滤
            recommendations = await self._rank_and_filter_recommendations(
                recommendations, user_profile, limit
            )
            
            # 缓存结果
            self.recommendation_cache[user_id] = recommendations
            
            logger.info(f"为用户 {user_id} 生成了 {len(recommendations)} 个个性化推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"生成个性化推荐失败: {e}")
            return await self._get_default_recommendations(query, limit)
    
    async def update_user_profile(
        self,
        user_id: str,
        profile_updates: Dict[str, Any]
    ) -> bool:
        """更新用户画像"""
        try:
            if user_id not in self.user_profiles:
                # 创建新用户画像
                profile = UserProfile(
                    user_id=user_id,
                    age=profile_updates.get("age", 30),
                    gender=profile_updates.get("gender", "unknown"),
                    height=profile_updates.get("height", 170.0),
                    weight=profile_updates.get("weight", 70.0),
                    occupation=profile_updates.get("occupation", ""),
                    lifestyle=profile_updates.get("lifestyle", ""),
                    personality_type=PersonalityType(
                        profile_updates.get("personality_type", "moderate")
                    ),
                    health_goals=[
                        HealthGoal(goal) for goal in profile_updates.get("health_goals", [])
                    ],
                    medical_history=profile_updates.get("medical_history", []),
                    allergies=profile_updates.get("allergies", []),
                    medications=profile_updates.get("medications", []),
                    preferences=profile_updates.get("preferences", {}),
                    tcm_constitution=profile_updates.get("tcm_constitution", "平和质"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.user_profiles[user_id] = profile
            else:
                # 更新现有画像
                profile = self.user_profiles[user_id]
                for key, value in profile_updates.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                profile.updated_at = datetime.now()
            
            # 清除缓存
            self.recommendation_cache.pop(user_id, None)
            
            logger.info(f"更新用户画像: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新用户画像失败: {e}")
            return False
    
    async def add_health_data(
        self,
        user_id: str,
        health_data: Dict[str, Any]
    ) -> bool:
        """添加健康数据"""
        try:
            data = HealthData(
                user_id=user_id,
                vital_signs=health_data.get("vital_signs", {}),
                lab_results=health_data.get("lab_results", {}),
                symptoms=health_data.get("symptoms", []),
                sleep_data=health_data.get("sleep_data", {}),
                activity_data=health_data.get("activity_data", {}),
                mood_data=health_data.get("mood_data", {}),
                timestamp=datetime.now()
            )
            
            self.health_data[user_id].append(data)
            
            # 保持最近30天的数据
            cutoff_date = datetime.now() - timedelta(days=30)
            self.health_data[user_id] = [
                d for d in self.health_data[user_id]
                if d.timestamp > cutoff_date
            ]
            
            # 清除缓存
            self.recommendation_cache.pop(user_id, None)
            
            logger.debug(f"添加健康数据: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加健康数据失败: {e}")
            return False
    
    async def update_behavior_pattern(
        self,
        user_id: str,
        interaction_data: Dict[str, Any]
    ) -> bool:
        """更新行为模式"""
        try:
            if user_id not in self.behavior_patterns:
                pattern = BehaviorPattern(
                    user_id=user_id,
                    query_patterns=[],
                    interaction_frequency=0.0,
                    preferred_times=[],
                    response_preferences={},
                    engagement_level=0.0,
                    compliance_rate=0.0,
                    last_updated=datetime.now()
                )
                self.behavior_patterns[user_id] = pattern
            else:
                pattern = self.behavior_patterns[user_id]
            
            # 更新查询模式
            if "query" in interaction_data:
                pattern.query_patterns.append(interaction_data["query"])
                if len(pattern.query_patterns) > 100:
                    pattern.query_patterns = pattern.query_patterns[-100:]
            
            # 更新交互频率
            if "interaction_time" in interaction_data:
                current_hour = datetime.now().hour
                pattern.preferred_times.append(current_hour)
                if len(pattern.preferred_times) > 100:
                    pattern.preferred_times = pattern.preferred_times[-100:]
            
            # 更新参与度
            if "engagement_score" in interaction_data:
                pattern.engagement_level = (
                    pattern.engagement_level * 0.9 + 
                    interaction_data["engagement_score"] * 0.1
                )
            
            # 更新依从性
            if "compliance_score" in interaction_data:
                pattern.compliance_rate = (
                    pattern.compliance_rate * 0.9 + 
                    interaction_data["compliance_score"] * 0.1
                )
            
            pattern.last_updated = datetime.now()
            
            logger.debug(f"更新行为模式: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新行为模式失败: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像"""
        return self.user_profiles.get(user_id)
    
    async def get_latest_health_data(self, user_id: str) -> Optional[HealthData]:
        """获取最新健康数据"""
        user_data = self.health_data.get(user_id, [])
        if user_data:
            return sorted(user_data, key=lambda x: x.timestamp, reverse=True)[0]
        return None
    
    async def get_behavior_pattern(self, user_id: str) -> Optional[BehaviorPattern]:
        """获取行为模式"""
        return self.behavior_patterns.get(user_id)
    
    async def _get_tcm_recommendations(
        self,
        user_profile: UserProfile,
        health_data: Optional[HealthData],
        query: str
    ) -> List[Recommendation]:
        """基于中医体质的推荐"""
        try:
            recommendations = []
            constitution = user_profile.tcm_constitution
            
            if constitution in self.tcm_constitution_rules:
                rules = self.tcm_constitution_rules[constitution]
                
                # 饮食推荐
                if "diet" in rules:
                    rec = Recommendation(
                        id=f"tcm_diet_{user_profile.user_id}_{datetime.now().timestamp()}",
                        user_id=user_profile.user_id,
                        type=RecommendationType.DIET_PLAN,
                        title=f"{constitution}饮食调理建议",
                        content=rules["diet"],
                        confidence=0.8,
                        priority=1,
                        reasoning=f"基于您的{constitution}体质特点",
                        metadata={"constitution": constitution, "type": "diet"},
                        created_at=datetime.now()
                    )
                    recommendations.append(rec)
                
                # 运动推荐
                if "exercise" in rules:
                    rec = Recommendation(
                        id=f"tcm_exercise_{user_profile.user_id}_{datetime.now().timestamp()}",
                        user_id=user_profile.user_id,
                        type=RecommendationType.EXERCISE_PLAN,
                        title=f"{constitution}运动养生建议",
                        content=rules["exercise"],
                        confidence=0.8,
                        priority=2,
                        reasoning=f"适合{constitution}体质的运动方式",
                        metadata={"constitution": constitution, "type": "exercise"},
                        created_at=datetime.now()
                    )
                    recommendations.append(rec)
                
                # 生活方式推荐
                if "lifestyle" in rules:
                    rec = Recommendation(
                        id=f"tcm_lifestyle_{user_profile.user_id}_{datetime.now().timestamp()}",
                        user_id=user_profile.user_id,
                        type=RecommendationType.LIFESTYLE,
                        title=f"{constitution}生活调理建议",
                        content=rules["lifestyle"],
                        confidence=0.7,
                        priority=3,
                        reasoning=f"基于{constitution}体质的生活调理",
                        metadata={"constitution": constitution, "type": "lifestyle"},
                        created_at=datetime.now()
                    )
                    recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成中医推荐失败: {e}")
            return []
    
    async def _get_goal_based_recommendations(
        self,
        user_profile: UserProfile,
        health_data: Optional[HealthData],
        query: str
    ) -> List[Recommendation]:
        """基于健康目标的推荐"""
        try:
            recommendations = []
            
            for goal in user_profile.health_goals:
                if goal == HealthGoal.WEIGHT_LOSS:
                    rec = await self._create_weight_loss_recommendation(user_profile, health_data)
                    if rec:
                        recommendations.append(rec)
                
                elif goal == HealthGoal.FITNESS:
                    rec = await self._create_fitness_recommendation(user_profile, health_data)
                    if rec:
                        recommendations.append(rec)
                
                elif goal == HealthGoal.STRESS_RELIEF:
                    rec = await self._create_stress_relief_recommendation(user_profile, health_data)
                    if rec:
                        recommendations.append(rec)
                
                elif goal == HealthGoal.SLEEP_IMPROVEMENT:
                    rec = await self._create_sleep_improvement_recommendation(user_profile, health_data)
                    if rec:
                        recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成目标推荐失败: {e}")
            return []
    
    async def _get_behavior_based_recommendations(
        self,
        user_profile: UserProfile,
        behavior_pattern: BehaviorPattern,
        query: str
    ) -> List[Recommendation]:
        """基于行为模式的推荐"""
        try:
            recommendations = []
            
            # 分析查询模式
            query_topics = self._analyze_query_patterns(behavior_pattern.query_patterns)
            
            # 基于偏好时间推荐
            preferred_hour = Counter(behavior_pattern.preferred_times).most_common(1)
            if preferred_hour:
                hour = preferred_hour[0][0]
                if 6 <= hour <= 10:
                    # 早晨活跃用户
                    rec = Recommendation(
                        id=f"morning_routine_{user_profile.user_id}_{datetime.now().timestamp()}",
                        user_id=user_profile.user_id,
                        type=RecommendationType.LIFESTYLE,
                        title="晨间健康习惯建议",
                        content="建议您在早晨进行适度运动，如太极拳或慢跑，有助于一天的精神状态。",
                        confidence=0.6,
                        priority=4,
                        reasoning="基于您的活跃时间模式",
                        metadata={"pattern": "morning_active"},
                        created_at=datetime.now()
                    )
                    recommendations.append(rec)
            
            # 基于参与度调整推荐
            if behavior_pattern.engagement_level < 0.5:
                # 低参与度用户，推荐简单易行的建议
                rec = Recommendation(
                    id=f"simple_advice_{user_profile.user_id}_{datetime.now().timestamp()}",
                    user_id=user_profile.user_id,
                    type=RecommendationType.HEALTH_ADVICE,
                    title="简单健康小贴士",
                    content="每天喝足够的水，保持充足睡眠，这些简单的习惯对健康很重要。",
                    confidence=0.7,
                    priority=5,
                    reasoning="为您推荐简单易行的健康建议",
                    metadata={"engagement": "low"},
                    created_at=datetime.now()
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成行为推荐失败: {e}")
            return []
    
    async def _get_collaborative_recommendations(
        self,
        user_id: str,
        query: str
    ) -> List[Recommendation]:
        """基于协同过滤的推荐"""
        try:
            recommendations = []
            
            # 找到相似用户
            similar_users = await self._find_similar_users(user_id)
            
            # 获取相似用户的成功推荐
            for similar_user_id, similarity in similar_users[:3]:
                if similar_user_id in self.recommendation_cache:
                    for rec in self.recommendation_cache[similar_user_id]:
                        # 创建基于相似用户的推荐
                        new_rec = Recommendation(
                            id=f"collab_{user_id}_{datetime.now().timestamp()}",
                            user_id=user_id,
                            type=rec.type,
                            title=f"推荐：{rec.title}",
                            content=rec.content,
                            confidence=rec.confidence * similarity,
                            priority=6,
                            reasoning=f"基于相似用户的成功经验",
                            metadata={"source": "collaborative", "similarity": similarity},
                            created_at=datetime.now()
                        )
                        recommendations.append(new_rec)
            
            return recommendations[:2]  # 限制数量
            
        except Exception as e:
            logger.error(f"生成协同推荐失败: {e}")
            return []
    
    async def _get_content_based_recommendations(
        self,
        user_profile: UserProfile,
        query: str
    ) -> List[Recommendation]:
        """基于内容的推荐"""
        try:
            recommendations = []
            
            # 基于查询内容匹配推荐
            if "减肥" in query or "瘦身" in query:
                rec = Recommendation(
                    id=f"content_weight_{user_profile.user_id}_{datetime.now().timestamp()}",
                    user_id=user_profile.user_id,
                    type=RecommendationType.DIET_PLAN,
                    title="科学减重方案",
                    content="建议采用均衡饮食配合适度运动的方式，避免极端节食。",
                    confidence=0.8,
                    priority=2,
                    reasoning="基于您的查询内容匹配",
                    metadata={"query_match": "weight_loss"},
                    created_at=datetime.now()
                )
                recommendations.append(rec)
            
            elif "失眠" in query or "睡眠" in query:
                rec = Recommendation(
                    id=f"content_sleep_{user_profile.user_id}_{datetime.now().timestamp()}",
                    user_id=user_profile.user_id,
                    type=RecommendationType.LIFESTYLE,
                    title="改善睡眠质量建议",
                    content="建议建立规律的作息时间，睡前避免使用电子设备，创造舒适的睡眠环境。",
                    confidence=0.8,
                    priority=1,
                    reasoning="基于您的睡眠相关咨询",
                    metadata={"query_match": "sleep"},
                    created_at=datetime.now()
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成内容推荐失败: {e}")
            return []
    
    async def _rank_and_filter_recommendations(
        self,
        recommendations: List[Recommendation],
        user_profile: UserProfile,
        limit: int
    ) -> List[Recommendation]:
        """排序和过滤推荐"""
        try:
            # 去重
            seen_titles = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec.title not in seen_titles:
                    seen_titles.add(rec.title)
                    unique_recommendations.append(rec)
            
            # 根据优先级和置信度排序
            unique_recommendations.sort(
                key=lambda x: (x.priority, -x.confidence)
            )
            
            # 个性化调整
            for rec in unique_recommendations:
                # 根据用户个性类型调整
                if user_profile.personality_type == PersonalityType.CONSERVATIVE:
                    if rec.type in [RecommendationType.MEDICATION, RecommendationType.TCM_THERAPY]:
                        rec.confidence *= 0.8
                elif user_profile.personality_type == PersonalityType.AGGRESSIVE:
                    if rec.type in [RecommendationType.EXERCISE_PLAN, RecommendationType.DIET_PLAN]:
                        rec.confidence *= 1.2
            
            # 重新排序
            unique_recommendations.sort(
                key=lambda x: (x.priority, -x.confidence)
            )
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"排序推荐失败: {e}")
            return recommendations[:limit]
    
    async def _get_default_recommendations(
        self,
        query: str,
        limit: int
    ) -> List[Recommendation]:
        """获取默认推荐"""
        try:
            default_recommendations = [
                Recommendation(
                    id=f"default_1_{datetime.now().timestamp()}",
                    user_id="unknown",
                    type=RecommendationType.HEALTH_ADVICE,
                    title="基础健康建议",
                    content="保持规律作息，均衡饮食，适度运动，定期体检。",
                    confidence=0.5,
                    priority=10,
                    reasoning="通用健康建议",
                    metadata={"type": "default"},
                    created_at=datetime.now()
                ),
                Recommendation(
                    id=f"default_2_{datetime.now().timestamp()}",
                    user_id="unknown",
                    type=RecommendationType.PREVENTION,
                    title="预防保健提醒",
                    content="注意个人卫生，避免过度疲劳，保持良好心态。",
                    confidence=0.5,
                    priority=11,
                    reasoning="基础预防建议",
                    metadata={"type": "default"},
                    created_at=datetime.now()
                )
            ]
            
            return default_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"生成默认推荐失败: {e}")
            return []
    
    async def _find_similar_users(self, user_id: str) -> List[Tuple[str, float]]:
        """找到相似用户"""
        try:
            target_profile = self.user_profiles.get(user_id)
            if not target_profile:
                return []
            
            similarities = []
            
            for other_user_id, other_profile in self.user_profiles.items():
                if other_user_id == user_id:
                    continue
                
                similarity = self._calculate_user_similarity(target_profile, other_profile)
                if similarity > 0.5:
                    similarities.append((other_user_id, similarity))
            
            return sorted(similarities, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"查找相似用户失败: {e}")
            return []
    
    def _calculate_user_similarity(
        self,
        profile1: UserProfile,
        profile2: UserProfile
    ) -> float:
        """计算用户相似度"""
        try:
            similarity_score = 0.0
            
            # 年龄相似度
            age_diff = abs(profile1.age - profile2.age)
            age_similarity = max(0, 1 - age_diff / 50)
            similarity_score += age_similarity * 0.2
            
            # 性别相似度
            gender_similarity = 1.0 if profile1.gender == profile2.gender else 0.0
            similarity_score += gender_similarity * 0.1
            
            # BMI相似度
            bmi1 = profile1.weight / ((profile1.height / 100) ** 2)
            bmi2 = profile2.weight / ((profile2.height / 100) ** 2)
            bmi_diff = abs(bmi1 - bmi2)
            bmi_similarity = max(0, 1 - bmi_diff / 10)
            similarity_score += bmi_similarity * 0.2
            
            # 健康目标相似度
            common_goals = set(profile1.health_goals) & set(profile2.health_goals)
            total_goals = set(profile1.health_goals) | set(profile2.health_goals)
            goal_similarity = len(common_goals) / len(total_goals) if total_goals else 0
            similarity_score += goal_similarity * 0.3
            
            # 中医体质相似度
            constitution_similarity = 1.0 if profile1.tcm_constitution == profile2.tcm_constitution else 0.0
            similarity_score += constitution_similarity * 0.2
            
            return similarity_score
            
        except Exception as e:
            logger.error(f"计算用户相似度失败: {e}")
            return 0.0
    
    def _analyze_query_patterns(self, query_patterns: List[str]) -> Dict[str, int]:
        """分析查询模式"""
        try:
            topics = defaultdict(int)
            
            for query in query_patterns:
                query_lower = query.lower()
                
                if any(word in query_lower for word in ["减肥", "瘦身", "体重"]):
                    topics["weight_management"] += 1
                
                if any(word in query_lower for word in ["失眠", "睡眠", "困"]):
                    topics["sleep"] += 1
                
                if any(word in query_lower for word in ["运动", "锻炼", "健身"]):
                    topics["exercise"] += 1
                
                if any(word in query_lower for word in ["饮食", "营养", "食物"]):
                    topics["nutrition"] += 1
                
                if any(word in query_lower for word in ["压力", "焦虑", "抑郁"]):
                    topics["mental_health"] += 1
            
            return dict(topics)
            
        except Exception as e:
            logger.error(f"分析查询模式失败: {e}")
            return {}
    
    async def _create_weight_loss_recommendation(
        self,
        user_profile: UserProfile,
        health_data: Optional[HealthData]
    ) -> Optional[Recommendation]:
        """创建减重推荐"""
        try:
            bmi = user_profile.weight / ((user_profile.height / 100) ** 2)
            
            if bmi > 24:  # 超重
                content = f"您的BMI为{bmi:.1f}，建议通过合理饮食控制和规律运动来减重。推荐每周减重0.5-1公斤。"
                confidence = 0.9
            else:
                content = "您的体重在正常范围内，建议保持现有的健康生活方式。"
                confidence = 0.7
            
            return Recommendation(
                id=f"weight_loss_{user_profile.user_id}_{datetime.now().timestamp()}",
                user_id=user_profile.user_id,
                type=RecommendationType.DIET_PLAN,
                title="个性化减重建议",
                content=content,
                confidence=confidence,
                priority=1,
                reasoning=f"基于您的BMI {bmi:.1f}",
                metadata={"bmi": bmi, "goal": "weight_loss"},
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"创建减重推荐失败: {e}")
            return None
    
    async def _create_fitness_recommendation(
        self,
        user_profile: UserProfile,
        health_data: Optional[HealthData]
    ) -> Optional[Recommendation]:
        """创建健身推荐"""
        try:
            age = user_profile.age
            
            if age < 30:
                content = "建议进行高强度间歇训练(HIIT)和力量训练，每周3-4次。"
            elif age < 50:
                content = "建议进行中等强度的有氧运动和力量训练，每周3次。"
            else:
                content = "建议进行低冲击的有氧运动，如游泳、太极拳，每周3次。"
            
            return Recommendation(
                id=f"fitness_{user_profile.user_id}_{datetime.now().timestamp()}",
                user_id=user_profile.user_id,
                type=RecommendationType.EXERCISE_PLAN,
                title="个性化健身计划",
                content=content,
                confidence=0.8,
                priority=2,
                reasoning=f"基于您的年龄 {age} 岁",
                metadata={"age": age, "goal": "fitness"},
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"创建健身推荐失败: {e}")
            return None
    
    async def _create_stress_relief_recommendation(
        self,
        user_profile: UserProfile,
        health_data: Optional[HealthData]
    ) -> Optional[Recommendation]:
        """创建压力缓解推荐"""
        try:
            content = "建议尝试冥想、深呼吸练习或瑜伽来缓解压力。每天15-20分钟的放松练习很有帮助。"
            
            return Recommendation(
                id=f"stress_relief_{user_profile.user_id}_{datetime.now().timestamp()}",
                user_id=user_profile.user_id,
                type=RecommendationType.LIFESTYLE,
                title="压力管理建议",
                content=content,
                confidence=0.8,
                priority=2,
                reasoning="基于您的压力缓解目标",
                metadata={"goal": "stress_relief"},
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"创建压力缓解推荐失败: {e}")
            return None
    
    async def _create_sleep_improvement_recommendation(
        self,
        user_profile: UserProfile,
        health_data: Optional[HealthData]
    ) -> Optional[Recommendation]:
        """创建睡眠改善推荐"""
        try:
            content = "建议保持规律的睡眠时间，睡前1小时避免使用电子设备，创造安静舒适的睡眠环境。"
            
            return Recommendation(
                id=f"sleep_improvement_{user_profile.user_id}_{datetime.now().timestamp()}",
                user_id=user_profile.user_id,
                type=RecommendationType.LIFESTYLE,
                title="睡眠质量改善建议",
                content=content,
                confidence=0.8,
                priority=1,
                reasoning="基于您的睡眠改善目标",
                metadata={"goal": "sleep_improvement"},
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"创建睡眠改善推荐失败: {e}")
            return None
    
    def _load_tcm_rules(self) -> Dict[str, Dict[str, str]]:
        """加载中医体质推荐规则"""
        return {
            "平和质": {
                "diet": "饮食宜清淡，营养均衡，五谷杂粮搭配，适量蛋白质。",
                "exercise": "适合各种运动，建议太极拳、八段锦等传统运动。",
                "lifestyle": "保持规律作息，心情舒畅，避免过度劳累。"
            },
            "气虚质": {
                "diet": "宜食补气食物，如人参、黄芪、山药、大枣等。",
                "exercise": "适合轻柔运动，如散步、太极拳，避免剧烈运动。",
                "lifestyle": "注意休息，避免过度劳累，保持心情愉快。"
            },
            "阳虚质": {
                "diet": "宜食温热食物，如羊肉、生姜、肉桂等，忌生冷。",
                "exercise": "适合温和运动，如慢跑、瑜伽，避免大汗淋漓。",
                "lifestyle": "注意保暖，避免受寒，适当晒太阳。"
            },
            "阴虚质": {
                "diet": "宜食滋阴食物，如银耳、百合、枸杞等，忌辛辣。",
                "exercise": "适合静态运动，如瑜伽、太极拳，避免大量出汗。",
                "lifestyle": "保持充足睡眠，避免熬夜，心情平和。"
            },
            "痰湿质": {
                "diet": "宜清淡饮食，多食化痰祛湿食物，如薏米、冬瓜等。",
                "exercise": "适合有氧运动，如游泳、慢跑，促进代谢。",
                "lifestyle": "保持环境干燥，避免潮湿，规律作息。"
            },
            "湿热质": {
                "diet": "宜清热利湿食物，如绿豆、苦瓜等，忌辛辣油腻。",
                "exercise": "适合游泳等水中运动，避免在炎热环境运动。",
                "lifestyle": "保持环境通风，避免湿热环境，心情平静。"
            },
            "血瘀质": {
                "diet": "宜食活血化瘀食物，如山楂、红花、桃仁等。",
                "exercise": "适合有氧运动，促进血液循环，如慢跑、游泳。",
                "lifestyle": "保持心情舒畅，避免久坐，适当按摩。"
            },
            "气郁质": {
                "diet": "宜食疏肝理气食物，如柑橘、玫瑰花茶等。",
                "exercise": "适合户外运动，如登山、跑步，释放压力。",
                "lifestyle": "保持心情愉快，多与人交流，避免独处。"
            },
            "特禀质": {
                "diet": "避免过敏原，饮食清淡，增强体质。",
                "exercise": "适合温和运动，增强免疫力，避免过敏环境。",
                "lifestyle": "避免接触过敏原，保持环境清洁，规律作息。"
            }
        } 