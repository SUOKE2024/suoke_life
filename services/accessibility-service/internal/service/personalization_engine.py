#!/usr/bin/env python

"""
个性化适应引擎 - 用户个性化学习和适应系统
包含用户偏好学习、适应性调整、个性化推荐、学习算法等功能
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PersonalizationType(Enum):
    """个性化类型枚举"""

    INTERFACE_PREFERENCES = "interface_preferences"
    ACCESSIBILITY_SETTINGS = "accessibility_settings"
    BEHAVIORAL_PATTERNS = "behavioral_patterns"
    HEALTH_PREFERENCES = "health_preferences"
    NOTIFICATION_PREFERENCES = "notification_preferences"
    INTERACTION_STYLE = "interaction_style"
    LEARNING_STYLE = "learning_style"
    ASSISTANCE_LEVEL = "assistance_level"


class AdaptationStrategy(Enum):
    """适应策略枚举"""

    GRADUAL_ADJUSTMENT = "gradual_adjustment"
    IMMEDIATE_CHANGE = "immediate_change"
    USER_CONFIRMATION = "user_confirmation"
    AUTOMATIC_LEARNING = "automatic_learning"
    HYBRID_APPROACH = "hybrid_approach"


@dataclass
class UserPreference:
    """用户偏好数据结构"""

    preference_id: str
    user_id: str
    preference_type: PersonalizationType
    preference_key: str
    preference_value: Any
    confidence: float
    frequency: int
    last_updated: float
    source: str  # "explicit", "implicit", "inferred"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationAction:
    """适应性动作"""

    action_id: str
    user_id: str
    action_type: str
    parameters: dict[str, Any]
    strategy: AdaptationStrategy
    confidence: float
    expected_benefit: float
    timestamp: float
    executed: bool = False
    user_feedback: str | None = None


@dataclass
class LearningSession:
    """学习会话"""

    session_id: str
    user_id: str
    start_time: float
    end_time: float | None
    interactions: list[dict[str, Any]]
    learned_preferences: list[UserPreference]
    adaptation_actions: list[AdaptationAction]
    session_quality: float
    metadata: dict[str, Any] = field(default_factory=dict)


class PreferenceLearner:
    """偏好学习器"""

    def __init__(self) -> None:
        self.learning_algorithms = {
            "frequency_based": self._frequency_based_learning,
            "pattern_recognition": self._pattern_recognition_learning,
            "collaborative_filtering": self._collaborative_filtering_learning,
            "reinforcement_learning": self._reinforcement_learning,
        }
        self.user_interaction_history = defaultdict(deque)
        self.preference_patterns = defaultdict(dict)

    def learn_from_interaction(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> list[UserPreference]:
        """从用户交互中学习偏好"""
        try:
            # 记录交互历史
            self.user_interaction_history[user_id].append(
                {**interaction_data, "timestamp": time.time()}
            )

            # 保持最近1000个交互记录
            if len(self.user_interaction_history[user_id]) > 1000:
                self.user_interaction_history[user_id].popleft()

            learned_preferences = []

            # 应用不同的学习算法
            for algorithm_name, algorithm_func in self.learning_algorithms.items():
                try:
                    preferences = algorithm_func(user_id, interaction_data)
                    learned_preferences.extend(preferences)
                except Exception as e:
                    logger.error(f"学习算法 {algorithm_name} 执行失败: {e!s}")

            return learned_preferences

        except Exception as e:
            logger.error(f"偏好学习失败: {e!s}")
            return []

    def _frequency_based_learning(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> list[UserPreference]:
        """基于频率的学习"""
        preferences = []

        # 分析用户操作频率
        action_type = interaction_data.get("action_type")
        if action_type:
            # 统计操作频率
            pattern_key = f"action_frequency_{action_type}"
            if pattern_key not in self.preference_patterns[user_id]:
                self.preference_patterns[user_id][pattern_key] = {
                    "count": 0,
                    "total_time": 0,
                }

            self.preference_patterns[user_id][pattern_key]["count"] += 1
            self.preference_patterns[user_id][pattern_key][
                "total_time"
            ] += interaction_data.get("duration", 0)

            # 如果频率足够高，创建偏好
            if self.preference_patterns[user_id][pattern_key]["count"] >= 5:
                preference = UserPreference(
                    preference_id=f"freq_{user_id}_{action_type}_{int(time.time())}",
                    user_id=user_id,
                    preference_type=PersonalizationType.BEHAVIORAL_PATTERNS,
                    preference_key=f"preferred_action_{action_type}",
                    preference_value=True,
                    confidence=min(
                        1.0,
                        self.preference_patterns[user_id][pattern_key]["count"] / 20.0,
                    ),
                    frequency=self.preference_patterns[user_id][pattern_key]["count"],
                    last_updated=time.time(),
                    source="implicit",
                )
                preferences.append(preference)

        return preferences

    def _pattern_recognition_learning(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> list[UserPreference]:
        """模式识别学习"""
        preferences = []

        # 分析时间模式
        current_hour = datetime.now().hour
        action_type = interaction_data.get("action_type")

        if action_type:
            time_pattern_key = f"time_pattern_{action_type}"
            if time_pattern_key not in self.preference_patterns[user_id]:
                self.preference_patterns[user_id][time_pattern_key] = defaultdict(int)

            self.preference_patterns[user_id][time_pattern_key][current_hour] += 1

            # 找出最常用的时间段
            time_counts = self.preference_patterns[user_id][time_pattern_key]
            if sum(time_counts.values()) >= 10:  # 至少10次记录
                most_common_hour = max(time_counts.items(), key=lambda x: x[1])

                if most_common_hour[1] >= 3:  # 至少3次在同一时间
                    preference = UserPreference(
                        preference_id=f"pattern_{user_id}_{action_type}_time_{int(time.time())}",
                        user_id=user_id,
                        preference_type=PersonalizationType.BEHAVIORAL_PATTERNS,
                        preference_key=f"preferred_time_{action_type}",
                        preference_value=most_common_hour[0],
                        confidence=most_common_hour[1] / sum(time_counts.values()),
                        frequency=most_common_hour[1],
                        last_updated=time.time(),
                        source="inferred",
                    )
                    preferences.append(preference)

        return preferences

    def _collaborative_filtering_learning(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> list[UserPreference]:
        """协同过滤学习"""
        preferences = []

        # 简化的协同过滤：基于相似用户的偏好
        # 在实际实现中，这里会比较复杂的相似度计算

        user_profile = self._get_user_profile(user_id)
        similar_users = self._find_similar_users(user_id, user_profile)

        for similar_user_id in similar_users[:3]:  # 取前3个相似用户
            similar_preferences = self._get_user_preferences(similar_user_id)

            for pref in similar_preferences:
                # 如果当前用户没有这个偏好，可能推荐
                if not self._user_has_preference(user_id, pref.preference_key):
                    collaborative_preference = UserPreference(
                        preference_id=f"collab_{user_id}_{pref.preference_key}_{int(time.time())}",
                        user_id=user_id,
                        preference_type=pref.preference_type,
                        preference_key=pref.preference_key,
                        preference_value=pref.preference_value,
                        confidence=pref.confidence * 0.7,  # 降低置信度
                        frequency=1,
                        last_updated=time.time(),
                        source="collaborative",
                        metadata={"source_user": similar_user_id},
                    )
                    preferences.append(collaborative_preference)

        return preferences

    def _reinforcement_learning(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> list[UserPreference]:
        """强化学习"""
        preferences = []

        # 基于用户反馈调整偏好
        feedback = interaction_data.get("user_feedback")
        if feedback:
            action_type = interaction_data.get("action_type")

            if feedback in ["positive", "like", "helpful"]:
                # 正面反馈，增强相关偏好
                preference = UserPreference(
                    preference_id=f"rl_pos_{user_id}_{action_type}_{int(time.time())}",
                    user_id=user_id,
                    preference_type=PersonalizationType.INTERACTION_STYLE,
                    preference_key=f"positive_feedback_{action_type}",
                    preference_value=True,
                    confidence=0.8,
                    frequency=1,
                    last_updated=time.time(),
                    source="explicit",
                    metadata={"feedback": feedback},
                )
                preferences.append(preference)

            elif feedback in ["negative", "dislike", "unhelpful"]:
                # 负面反馈，创建避免偏好
                preference = UserPreference(
                    preference_id=f"rl_neg_{user_id}_{action_type}_{int(time.time())}",
                    user_id=user_id,
                    preference_type=PersonalizationType.INTERACTION_STYLE,
                    preference_key=f"avoid_{action_type}",
                    preference_value=True,
                    confidence=0.9,
                    frequency=1,
                    last_updated=time.time(),
                    source="explicit",
                    metadata={"feedback": feedback},
                )
                preferences.append(preference)

        return preferences

    def _get_user_profile(self, user_id: str) -> dict[str, Any]:
        """获取用户档案"""
        interactions = list(self.user_interaction_history[user_id])

        if not interactions:
            return {}

        # 计算用户特征
        action_types = [
            i.get("action_type") for i in interactions if i.get("action_type")
        ]
        most_common_actions = {}
        for action in action_types:
            most_common_actions[action] = most_common_actions.get(action, 0) + 1

        return {
            "total_interactions": len(interactions),
            "common_actions": most_common_actions,
            "activity_hours": [
                datetime.fromtimestamp(i["timestamp"]).hour for i in interactions
            ],
            "avg_session_duration": np.mean(
                [i.get("duration", 0) for i in interactions]
            ),
        }

    def _find_similar_users(
        self, user_id: str, user_profile: dict[str, Any]
    ) -> list[str]:
        """找到相似用户"""
        # 简化实现：返回一些模拟的相似用户
        # 在实际实现中，这里会有复杂的相似度计算
        return [f"user_{i}" for i in range(1, 4) if f"user_{i}" != user_id]

    def _get_user_preferences(self, user_id: str) -> list[UserPreference]:
        """获取用户偏好（模拟）"""
        # 在实际实现中，这里会从数据库获取
        return []

    def _user_has_preference(self, user_id: str, preference_key: str) -> bool:
        """检查用户是否已有某个偏好"""
        # 在实际实现中，这里会检查数据库
        return False


class AdaptationEngine:
    """适应引擎"""

    def __init__(self) -> None:
        self.adaptation_rules = self._initialize_adaptation_rules()
        self.user_adaptations = defaultdict(list)
        self.adaptation_history = defaultdict(deque)

    def _initialize_adaptation_rules(self) -> dict[str, dict[str, Any]]:
        """初始化适应规则"""
        return {
            "interface_brightness": {
                "trigger_conditions": ["low_light_environment", "user_squinting"],
                "adaptation_action": "increase_brightness",
                "strategy": AdaptationStrategy.GRADUAL_ADJUSTMENT,
                "parameters": {"increment": 10, "max_value": 100},
            },
            "font_size": {
                "trigger_conditions": ["reading_difficulty", "zoom_usage"],
                "adaptation_action": "increase_font_size",
                "strategy": AdaptationStrategy.USER_CONFIRMATION,
                "parameters": {"increment": 2, "max_value": 24},
            },
            "notification_frequency": {
                "trigger_conditions": ["notification_dismissal", "stress_indicators"],
                "adaptation_action": "reduce_notifications",
                "strategy": AdaptationStrategy.AUTOMATIC_LEARNING,
                "parameters": {"reduction_factor": 0.8, "min_frequency": 0.1},
            },
            "assistance_level": {
                "trigger_conditions": [
                    "user_expertise_increase",
                    "successful_completions",
                ],
                "adaptation_action": "reduce_assistance",
                "strategy": AdaptationStrategy.GRADUAL_ADJUSTMENT,
                "parameters": {"reduction_step": 0.1, "min_level": 0.2},
            },
            "interaction_style": {
                "trigger_conditions": ["user_preference_change", "feedback_patterns"],
                "adaptation_action": "adjust_interaction_style",
                "strategy": AdaptationStrategy.HYBRID_APPROACH,
                "parameters": {"adaptation_rate": 0.1},
            },
        }

    def evaluate_adaptation_needs(
        self,
        user_id: str,
        user_context: dict[str, Any],
        user_preferences: list[UserPreference],
    ) -> list[AdaptationAction]:
        """评估适应需求"""
        try:
            adaptation_actions = []

            for rule_name, rule in self.adaptation_rules.items():
                if self._check_trigger_conditions(
                    rule["trigger_conditions"], user_context
                ):
                    action = self._create_adaptation_action(
                        user_id, rule_name, rule, user_context, user_preferences
                    )
                    if action:
                        adaptation_actions.append(action)

            # 根据优先级排序
            adaptation_actions.sort(key=lambda x: x.expected_benefit, reverse=True)

            return adaptation_actions[:5]  # 最多返回5个适应动作

        except Exception as e:
            logger.error(f"评估适应需求失败: {e!s}")
            return []

    def _check_trigger_conditions(
        self, conditions: list[str], user_context: dict[str, Any]
    ) -> bool:
        """检查触发条件"""
        for condition in conditions:
            if condition == "low_light_environment":
                light_level = (
                    user_context.get("sensor_data", {}).get("light", {}).get("lux", 500)
                )
                if light_level < 100:
                    return True

            elif condition == "user_squinting":
                # 模拟检测：基于摄像头数据或用户行为
                facial_data = user_context.get("facial_analysis", {})
                if facial_data.get("squinting_detected", False):
                    return True

            elif condition == "reading_difficulty":
                # 基于阅读时间和错误率
                reading_stats = user_context.get("reading_stats", {})
                if reading_stats.get("avg_reading_time", 0) > 120:  # 超过2分钟
                    return True

            elif condition == "zoom_usage":
                # 检查用户是否频繁使用缩放
                zoom_usage = user_context.get("zoom_usage_count", 0)
                if zoom_usage > 5:  # 最近使用超过5次
                    return True

            elif condition == "notification_dismissal":
                # 检查通知被快速关闭的频率
                notification_stats = user_context.get("notification_stats", {})
                dismissal_rate = notification_stats.get("quick_dismissal_rate", 0)
                if dismissal_rate > 0.7:  # 70%的通知被快速关闭
                    return True

            elif condition == "stress_indicators":
                # 基于生理指标检测压力
                stress_level = user_context.get("stress_level", 0)
                if stress_level > 0.7:
                    return True

        return False

    def _create_adaptation_action(
        self,
        user_id: str,
        rule_name: str,
        rule: dict[str, Any],
        user_context: dict[str, Any],
        user_preferences: list[UserPreference],
    ) -> AdaptationAction | None:
        """创建适应动作"""
        try:
            # 计算期望收益
            expected_benefit = self._calculate_expected_benefit(
                rule_name, user_context, user_preferences
            )

            # 计算置信度
            confidence = self._calculate_adaptation_confidence(rule_name, user_context)

            action = AdaptationAction(
                action_id=f"adapt_{user_id}_{rule_name}_{int(time.time())}",
                user_id=user_id,
                action_type=rule["adaptation_action"],
                parameters=rule["parameters"].copy(),
                strategy=rule["strategy"],
                confidence=confidence,
                expected_benefit=expected_benefit,
                timestamp=time.time(),
            )

            return action

        except Exception as e:
            logger.error(f"创建适应动作失败: {e!s}")
            return None

    def _calculate_expected_benefit(
        self,
        rule_name: str,
        user_context: dict[str, Any],
        user_preferences: list[UserPreference],
    ) -> float:
        """计算期望收益"""
        base_benefit = 0.5

        # 基于用户偏好调整收益
        relevant_preferences = [
            p
            for p in user_preferences
            if rule_name in p.preference_key or p.preference_key in rule_name
        ]

        if relevant_preferences:
            pref_benefit = np.mean([p.confidence for p in relevant_preferences])
            base_benefit = (base_benefit + pref_benefit) / 2

        # 基于历史成功率调整
        # 在实际实现中，这里会查询历史适应效果

        return min(1.0, base_benefit)

    def _calculate_adaptation_confidence(
        self, rule_name: str, user_context: dict[str, Any]
    ) -> float:
        """计算适应置信度"""
        base_confidence = 0.6

        # 基于数据质量调整置信度
        data_quality = user_context.get("data_quality", 0.5)
        confidence = base_confidence * data_quality

        # 基于历史成功率调整
        # 在实际实现中，这里会考虑历史适应成功率

        return min(1.0, confidence)

    async def execute_adaptation(self, action: AdaptationAction) -> bool:
        """执行适应动作"""
        try:
            if action.strategy == AdaptationStrategy.IMMEDIATE_CHANGE:
                # 立即执行
                success = await self._apply_adaptation(action)
                action.executed = success
                return success

            elif action.strategy == AdaptationStrategy.GRADUAL_ADJUSTMENT:
                # 逐步调整
                success = await self._apply_gradual_adaptation(action)
                action.executed = success
                return success

            elif action.strategy == AdaptationStrategy.USER_CONFIRMATION:
                # 需要用户确认
                # 在实际实现中，这里会显示确认对话框
                logger.info(f"需要用户确认适应动作: {action.action_type}")
                return False  # 等待用户确认

            elif action.strategy == AdaptationStrategy.AUTOMATIC_LEARNING:
                # 自动学习模式
                success = await self._apply_learning_adaptation(action)
                action.executed = success
                return success

            elif action.strategy == AdaptationStrategy.HYBRID_APPROACH:
                # 混合方法
                success = await self._apply_hybrid_adaptation(action)
                action.executed = success
                return success

            return False

        except Exception as e:
            logger.error(f"执行适应动作失败: {e!s}")
            return False

    async def _apply_adaptation(self, action: AdaptationAction) -> bool:
        """应用适应"""
        logger.info(f"执行适应动作: {action.action_type} for user {action.user_id}")

        # 在实际实现中，这里会调用相应的系统API
        # 例如调整界面设置、修改通知频率等

        # 记录适应历史
        self.adaptation_history[action.user_id].append(
            {"action": action, "timestamp": time.time(), "success": True}
        )

        return True

    async def _apply_gradual_adaptation(self, action: AdaptationAction) -> bool:
        """应用逐步适应"""
        # 分多步执行适应
        steps = action.parameters.get("steps", 3)

        for step in range(steps):
            # 每步执行部分适应
            partial_action = AdaptationAction(
                action_id=f"{action.action_id}_step_{step}",
                user_id=action.user_id,
                action_type=action.action_type,
                parameters={**action.parameters, "step": step, "total_steps": steps},
                strategy=AdaptationStrategy.IMMEDIATE_CHANGE,
                confidence=action.confidence,
                expected_benefit=action.expected_benefit / steps,
                timestamp=time.time(),
            )

            await self._apply_adaptation(partial_action)
            await asyncio.sleep(1)  # 步骤间延迟

        return True

    async def _apply_learning_adaptation(self, action: AdaptationAction) -> bool:
        """应用学习适应"""
        # 基于学习算法调整参数
        learning_rate = action.parameters.get("adaptation_rate", 0.1)

        # 在实际实现中，这里会使用机器学习算法
        # 根据用户反馈和行为数据调整适应参数

        return await self._apply_adaptation(action)

    async def _apply_hybrid_adaptation(self, action: AdaptationAction) -> bool:
        """应用混合适应"""
        # 结合多种策略
        if action.confidence > 0.8:
            # 高置信度，直接执行
            return await self._apply_adaptation(action)
        else:
            # 低置信度，逐步执行
            return await self._apply_gradual_adaptation(action)


class PersonalizationEngine:
    """个性化引擎核心类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化个性化引擎

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("personalization_engine", {}).get("enabled", True)

        # 子模块
        self.preference_learner = PreferenceLearner()
        self.adaptation_engine = AdaptationEngine()

        # 数据存储
        self.user_preferences = defaultdict(list)  # user_id -> List[UserPreference]
        self.learning_sessions = defaultdict(list)  # user_id -> List[LearningSession]
        self.active_adaptations = defaultdict(list)  # user_id -> List[AdaptationAction]

        # 统计信息
        self.stats = {
            "total_interactions": 0,
            "preferences_learned": 0,
            "adaptations_executed": 0,
            "user_satisfaction": defaultdict(float),
            "learning_accuracy": 0.0,
        }

        logger.info(f"个性化引擎初始化完成 - 启用: {self.enabled}")

    async def process_user_interaction(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        处理用户交互

        Args:
            user_id: 用户ID
            interaction_data: 交互数据

        Returns:
            处理结果
        """
        if not self.enabled:
            return {"status": "disabled"}

        try:
            # 学习用户偏好
            learned_preferences = self.preference_learner.learn_from_interaction(
                user_id, interaction_data
            )

            # 更新用户偏好
            for preference in learned_preferences:
                self._update_user_preference(user_id, preference)

            # 评估适应需求
            user_context = interaction_data.get("context", {})
            adaptation_actions = self.adaptation_engine.evaluate_adaptation_needs(
                user_id, user_context, self.user_preferences[user_id]
            )

            # 执行适应动作
            executed_adaptations = []
            for action in adaptation_actions:
                if await self.adaptation_engine.execute_adaptation(action):
                    executed_adaptations.append(action)
                    self.active_adaptations[user_id].append(action)

            # 更新统计信息
            self.stats["total_interactions"] += 1
            self.stats["preferences_learned"] += len(learned_preferences)
            self.stats["adaptations_executed"] += len(executed_adaptations)

            return {
                "status": "success",
                "learned_preferences": len(learned_preferences),
                "executed_adaptations": len(executed_adaptations),
                "recommendations": self._generate_personalized_recommendations(user_id),
            }

        except Exception as e:
            logger.error(f"处理用户交互失败: {e!s}")
            return {"status": "error", "message": str(e)}

    def _update_user_preference(self, user_id: str, new_preference: UserPreference):
        """更新用户偏好"""
        existing_preferences = self.user_preferences[user_id]

        # 查找是否已存在相同的偏好
        existing_pref = None
        for pref in existing_preferences:
            if pref.preference_key == new_preference.preference_key:
                existing_pref = pref
                break

        if existing_pref:
            # 更新现有偏好
            existing_pref.preference_value = new_preference.preference_value
            existing_pref.confidence = (
                existing_pref.confidence + new_preference.confidence
            ) / 2
            existing_pref.frequency += 1
            existing_pref.last_updated = time.time()
        else:
            # 添加新偏好
            self.user_preferences[user_id].append(new_preference)

        # 保持偏好数量限制
        if len(self.user_preferences[user_id]) > 100:
            # 移除最旧的偏好
            self.user_preferences[user_id].sort(key=lambda x: x.last_updated)
            self.user_preferences[user_id] = self.user_preferences[user_id][-100:]

    def _generate_personalized_recommendations(self, user_id: str) -> list[str]:
        """生成个性化推荐"""
        recommendations = []

        user_prefs = self.user_preferences[user_id]
        if not user_prefs:
            return recommendations

        # 基于偏好生成推荐
        high_confidence_prefs = [p for p in user_prefs if p.confidence > 0.7]

        for pref in high_confidence_prefs[:5]:  # 取前5个高置信度偏好
            if pref.preference_type == PersonalizationType.INTERFACE_PREFERENCES:
                recommendations.append(f"建议调整界面设置: {pref.preference_key}")
            elif pref.preference_type == PersonalizationType.ACCESSIBILITY_SETTINGS:
                recommendations.append(f"建议启用无障碍功能: {pref.preference_key}")
            elif pref.preference_type == PersonalizationType.BEHAVIORAL_PATTERNS:
                recommendations.append(f"基于您的使用习惯: {pref.preference_key}")

        return recommendations

    def get_user_profile(self, user_id: str) -> dict[str, Any]:
        """获取用户档案"""
        preferences = self.user_preferences[user_id]
        adaptations = self.active_adaptations[user_id]

        # 按类型分组偏好
        preferences_by_type = defaultdict(list)
        for pref in preferences:
            preferences_by_type[pref.preference_type.value].append(
                {
                    "key": pref.preference_key,
                    "value": pref.preference_value,
                    "confidence": pref.confidence,
                    "frequency": pref.frequency,
                }
            )

        return {
            "user_id": user_id,
            "total_preferences": len(preferences),
            "preferences_by_type": dict(preferences_by_type),
            "active_adaptations": len(adaptations),
            "personalization_level": self._calculate_personalization_level(user_id),
            "satisfaction_score": self.stats["user_satisfaction"].get(user_id, 0.0),
        }

    def _calculate_personalization_level(self, user_id: str) -> float:
        """计算个性化水平"""
        preferences = self.user_preferences[user_id]
        if not preferences:
            return 0.0

        # 基于偏好数量和置信度计算
        total_confidence = sum(p.confidence for p in preferences)
        avg_confidence = total_confidence / len(preferences)

        # 基于偏好类型多样性
        unique_types = len({p.preference_type for p in preferences})
        type_diversity = unique_types / len(PersonalizationType)

        # 综合评分
        personalization_level = (avg_confidence + type_diversity) / 2
        return min(1.0, personalization_level)

    def record_user_feedback(
        self, user_id: str, adaptation_id: str, feedback: str, rating: float
    ):
        """记录用户反馈"""
        try:
            # 找到对应的适应动作
            for adaptation in self.active_adaptations[user_id]:
                if adaptation.action_id == adaptation_id:
                    adaptation.user_feedback = feedback
                    break

            # 更新用户满意度
            current_satisfaction = self.stats["user_satisfaction"][user_id]
            self.stats["user_satisfaction"][user_id] = (
                current_satisfaction + rating
            ) / 2

            logger.info(
                f"用户 {user_id} 对适应 {adaptation_id} 的反馈: {feedback} (评分: {rating})"
            )

        except Exception as e:
            logger.error(f"记录用户反馈失败: {e!s}")

    def export_user_preferences(self, user_id: str) -> dict[str, Any]:
        """导出用户偏好"""
        preferences = self.user_preferences[user_id]

        export_data = {
            "user_id": user_id,
            "export_timestamp": time.time(),
            "preferences": [
                {
                    "preference_id": p.preference_id,
                    "preference_type": p.preference_type.value,
                    "preference_key": p.preference_key,
                    "preference_value": p.preference_value,
                    "confidence": p.confidence,
                    "frequency": p.frequency,
                    "last_updated": p.last_updated,
                    "source": p.source,
                    "metadata": p.metadata,
                }
                for p in preferences
            ],
        }

        return export_data

    def import_user_preferences(
        self, user_id: str, import_data: dict[str, Any]
    ) -> bool:
        """导入用户偏好"""
        try:
            preferences_data = import_data.get("preferences", [])

            imported_preferences = []
            for pref_data in preferences_data:
                preference = UserPreference(
                    preference_id=pref_data["preference_id"],
                    user_id=user_id,
                    preference_type=PersonalizationType(pref_data["preference_type"]),
                    preference_key=pref_data["preference_key"],
                    preference_value=pref_data["preference_value"],
                    confidence=pref_data["confidence"],
                    frequency=pref_data["frequency"],
                    last_updated=pref_data["last_updated"],
                    source=pref_data["source"],
                    metadata=pref_data.get("metadata", {}),
                )
                imported_preferences.append(preference)

            self.user_preferences[user_id] = imported_preferences
            logger.info(f"成功导入用户 {user_id} 的 {len(imported_preferences)} 个偏好")

            return True

        except Exception as e:
            logger.error(f"导入用户偏好失败: {e!s}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        total_users = len(self.user_preferences)
        avg_satisfaction = (
            np.mean(list(self.stats["user_satisfaction"].values()))
            if self.stats["user_satisfaction"]
            else 0.0
        )

        return {
            "enabled": self.enabled,
            "total_users": total_users,
            "average_satisfaction": avg_satisfaction,
            "total_preferences": sum(
                len(prefs) for prefs in self.user_preferences.values()
            ),
            "total_adaptations": sum(
                len(adaptations) for adaptations in self.active_adaptations.values()
            ),
            **dict(self.stats),
        }

    async def shutdown(self) -> None:
        """关闭个性化引擎"""
        logger.info("正在关闭个性化引擎...")

        # 保存用户偏好到持久化存储
        # 在实际实现中，这里会保存到数据库

        logger.info("个性化引擎已关闭")
