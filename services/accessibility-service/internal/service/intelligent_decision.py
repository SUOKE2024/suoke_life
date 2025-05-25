#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能决策模块 - 基于多传感器数据的智能决策系统
包含用户行为模式学习、个性化推荐、智能自动化等功能
"""

import logging
import time
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """决策类型枚举"""
    ACCESSIBILITY_ADJUSTMENT = "accessibility_adjustment"
    AUTOMATION_TRIGGER = "automation_trigger"
    HEALTH_RECOMMENDATION = "health_recommendation"
    ENVIRONMENT_OPTIMIZATION = "environment_optimization"
    USER_ASSISTANCE = "user_assistance"
    SAFETY_ALERT = "safety_alert"


class ConfidenceLevel(Enum):
    """置信度级别枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class DecisionContext:
    """决策上下文"""
    user_id: str
    timestamp: float
    sensor_data: Dict[str, Any]
    location_data: Dict[str, Any]
    user_preferences: Dict[str, Any]
    historical_patterns: Dict[str, Any]
    current_activity: str
    environment_state: Dict[str, Any]


@dataclass
class Decision:
    """决策结果"""
    decision_id: str
    decision_type: DecisionType
    action: str
    parameters: Dict[str, Any]
    confidence: ConfidenceLevel
    reasoning: str
    priority: int  # 1-10, 10为最高优先级
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserBehaviorPattern:
    """用户行为模式"""
    pattern_id: str
    user_id: str
    pattern_type: str
    frequency: float
    time_patterns: List[Dict[str, Any]]
    location_patterns: List[Dict[str, Any]]
    sensor_patterns: Dict[str, List[float]]
    confidence: float
    last_updated: float


class BehaviorLearningEngine:
    """行为学习引擎"""
    
    def __init__(self):
        self.user_patterns = {}  # user_id -> List[UserBehaviorPattern]
        self.activity_classifiers = {}
        self.pattern_templates = self._initialize_pattern_templates()
    
    def _initialize_pattern_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化行为模式模板"""
        return {
            "morning_routine": {
                "time_range": [(6, 9)],  # 6-9点
                "typical_sensors": ["accelerometer", "light", "microphone"],
                "activity_sequence": ["wake_up", "personal_care", "breakfast"]
            },
            "work_session": {
                "time_range": [(9, 12), (14, 18)],
                "typical_sensors": ["light", "microphone", "proximity"],
                "activity_sequence": ["computer_work", "meetings", "breaks"]
            },
            "exercise_routine": {
                "time_range": [(6, 8), (18, 21)],
                "typical_sensors": ["accelerometer", "heart_rate", "gps"],
                "activity_sequence": ["warm_up", "exercise", "cool_down"]
            },
            "evening_routine": {
                "time_range": [(19, 23)],
                "typical_sensors": ["light", "temperature", "microphone"],
                "activity_sequence": ["dinner", "relaxation", "preparation_for_sleep"]
            }
        }
    
    def learn_from_data(self, user_id: str, sensor_data: Dict[str, Any], 
                       location_data: Dict[str, Any], activity: str):
        """从数据中学习用户行为模式"""
        try:
            current_time = datetime.now()
            
            # 提取时间特征
            time_features = {
                "hour": current_time.hour,
                "day_of_week": current_time.weekday(),
                "is_weekend": current_time.weekday() >= 5
            }
            
            # 提取传感器特征
            sensor_features = self._extract_sensor_features(sensor_data)
            
            # 提取位置特征
            location_features = self._extract_location_features(location_data)
            
            # 更新或创建行为模式
            self._update_behavior_patterns(
                user_id, activity, time_features, 
                sensor_features, location_features
            )
            
        except Exception as e:
            logger.error(f"行为学习失败: {str(e)}")
    
    def _extract_sensor_features(self, sensor_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """提取传感器特征"""
        features = {}
        
        for sensor_type, data in sensor_data.items():
            if isinstance(data, list) and data:
                # 计算统计特征
                values = [d.get("values", [0])[0] if isinstance(d, dict) else d for d in data]
                features[sensor_type] = [
                    np.mean(values),
                    np.std(values),
                    np.min(values),
                    np.max(values)
                ]
        
        return features
    
    def _extract_location_features(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取位置特征"""
        if not location_data:
            return {}
        
        return {
            "location_type": location_data.get("location_type", "unknown"),
            "accuracy": location_data.get("accuracy", 0),
            "indoor_info": location_data.get("indoor_info", {})
        }
    
    def _update_behavior_patterns(self, user_id: str, activity: str,
                                time_features: Dict[str, Any],
                                sensor_features: Dict[str, List[float]],
                                location_features: Dict[str, Any]):
        """更新用户行为模式"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = []
        
        # 查找现有模式或创建新模式
        existing_pattern = None
        for pattern in self.user_patterns[user_id]:
            if (pattern.pattern_type == activity and 
                self._is_similar_time_pattern(pattern.time_patterns, time_features)):
                existing_pattern = pattern
                break
        
        if existing_pattern:
            # 更新现有模式
            self._update_existing_pattern(existing_pattern, time_features, 
                                        sensor_features, location_features)
        else:
            # 创建新模式
            new_pattern = self._create_new_pattern(
                user_id, activity, time_features, 
                sensor_features, location_features
            )
            self.user_patterns[user_id].append(new_pattern)
    
    def _is_similar_time_pattern(self, existing_patterns: List[Dict[str, Any]], 
                                new_features: Dict[str, Any]) -> bool:
        """判断时间模式是否相似"""
        for pattern in existing_patterns:
            hour_diff = abs(pattern.get("hour", 0) - new_features.get("hour", 0))
            if hour_diff <= 2:  # 2小时内认为相似
                return True
        return False
    
    def _update_existing_pattern(self, pattern: UserBehaviorPattern,
                               time_features: Dict[str, Any],
                               sensor_features: Dict[str, List[float]],
                               location_features: Dict[str, Any]):
        """更新现有行为模式"""
        # 更新频率
        pattern.frequency += 1
        
        # 更新时间模式
        pattern.time_patterns.append(time_features)
        if len(pattern.time_patterns) > 100:  # 保持最近100个记录
            pattern.time_patterns = pattern.time_patterns[-100:]
        
        # 更新位置模式
        if location_features:
            pattern.location_patterns.append(location_features)
            if len(pattern.location_patterns) > 100:
                pattern.location_patterns = pattern.location_patterns[-100:]
        
        # 更新传感器模式
        for sensor_type, features in sensor_features.items():
            if sensor_type not in pattern.sensor_patterns:
                pattern.sensor_patterns[sensor_type] = []
            pattern.sensor_patterns[sensor_type].extend(features)
            if len(pattern.sensor_patterns[sensor_type]) > 400:  # 保持最近400个特征
                pattern.sensor_patterns[sensor_type] = pattern.sensor_patterns[sensor_type][-400:]
        
        # 更新置信度
        pattern.confidence = min(1.0, pattern.confidence + 0.01)
        pattern.last_updated = time.time()
    
    def _create_new_pattern(self, user_id: str, activity: str,
                          time_features: Dict[str, Any],
                          sensor_features: Dict[str, List[float]],
                          location_features: Dict[str, Any]) -> UserBehaviorPattern:
        """创建新的行为模式"""
        pattern_id = f"{user_id}_{activity}_{int(time.time())}"
        
        return UserBehaviorPattern(
            pattern_id=pattern_id,
            user_id=user_id,
            pattern_type=activity,
            frequency=1.0,
            time_patterns=[time_features],
            location_patterns=[location_features] if location_features else [],
            sensor_patterns=sensor_features,
            confidence=0.1,
            last_updated=time.time()
        )
    
    def predict_next_activity(self, user_id: str, current_context: Dict[str, Any]) -> Optional[str]:
        """预测用户下一个活动"""
        if user_id not in self.user_patterns:
            return None
        
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # 找到当前时间最可能的活动
        best_match = None
        best_score = 0.0
        
        for pattern in self.user_patterns[user_id]:
            score = self._calculate_pattern_match_score(pattern, current_hour, current_context)
            if score > best_score:
                best_score = score
                best_match = pattern
        
        return best_match.pattern_type if best_match and best_score > 0.5 else None
    
    def _calculate_pattern_match_score(self, pattern: UserBehaviorPattern, 
                                     current_hour: int, context: Dict[str, Any]) -> float:
        """计算模式匹配分数"""
        score = 0.0
        
        # 时间匹配分数
        time_scores = []
        for time_pattern in pattern.time_patterns:
            hour_diff = abs(time_pattern.get("hour", 0) - current_hour)
            time_score = max(0, 1.0 - hour_diff / 12.0)  # 12小时内线性衰减
            time_scores.append(time_score)
        
        if time_scores:
            score += np.mean(time_scores) * 0.4
        
        # 频率分数
        frequency_score = min(1.0, pattern.frequency / 10.0)  # 10次以上认为是稳定模式
        score += frequency_score * 0.3
        
        # 置信度分数
        score += pattern.confidence * 0.3
        
        return score
    
    def get_user_patterns(self, user_id: str) -> List[UserBehaviorPattern]:
        """获取用户行为模式"""
        return self.user_patterns.get(user_id, [])


class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self):
        self.recommendation_rules = self._initialize_recommendation_rules()
        self.user_feedback = defaultdict(list)  # user_id -> feedback history
    
    def _initialize_recommendation_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化推荐规则"""
        return {
            "low_light_environment": {
                "condition": lambda ctx: ctx.sensor_data.get("light", {}).get("lux", 1000) < 50,
                "recommendation": {
                    "action": "adjust_screen_brightness",
                    "parameters": {"brightness": "high", "contrast": "high"},
                    "reasoning": "检测到低光环境，建议提高屏幕亮度和对比度"
                }
            },
            "high_noise_environment": {
                "condition": lambda ctx: ctx.sensor_data.get("microphone", {}).get("volume_db", 0) > 70,
                "recommendation": {
                    "action": "enable_visual_notifications",
                    "parameters": {"vibration": True, "visual_alerts": True},
                    "reasoning": "检测到高噪音环境，建议启用视觉和振动通知"
                }
            },
            "motion_detected": {
                "condition": lambda ctx: ctx.sensor_data.get("accelerometer", {}).get("is_moving", False),
                "recommendation": {
                    "action": "enable_motion_assistance",
                    "parameters": {"stabilization": True, "large_buttons": True},
                    "reasoning": "检测到设备移动，建议启用运动辅助功能"
                }
            },
            "outdoor_location": {
                "condition": lambda ctx: ctx.location_data.get("location_type") == "outdoor",
                "recommendation": {
                    "action": "enable_outdoor_mode",
                    "parameters": {"gps_guidance": True, "weather_alerts": True},
                    "reasoning": "检测到户外环境，建议启用户外模式"
                }
            },
            "work_hours": {
                "condition": lambda ctx: 9 <= datetime.fromtimestamp(ctx.timestamp).hour <= 17,
                "recommendation": {
                    "action": "enable_work_mode",
                    "parameters": {"focus_mode": True, "minimal_distractions": True},
                    "reasoning": "工作时间，建议启用专注模式"
                }
            }
        }
    
    def generate_recommendations(self, context: DecisionContext) -> List[Decision]:
        """生成个性化推荐"""
        recommendations = []
        
        try:
            # 基于规则的推荐
            rule_recommendations = self._apply_recommendation_rules(context)
            recommendations.extend(rule_recommendations)
            
            # 基于用户历史的推荐
            pattern_recommendations = self._generate_pattern_based_recommendations(context)
            recommendations.extend(pattern_recommendations)
            
            # 基于健康数据的推荐
            health_recommendations = self._generate_health_recommendations(context)
            recommendations.extend(health_recommendations)
            
            # 去重和排序
            recommendations = self._deduplicate_and_rank_recommendations(recommendations)
            
        except Exception as e:
            logger.error(f"生成推荐失败: {str(e)}")
        
        return recommendations
    
    def _apply_recommendation_rules(self, context: DecisionContext) -> List[Decision]:
        """应用推荐规则"""
        recommendations = []
        
        for rule_name, rule in self.recommendation_rules.items():
            try:
                if rule["condition"](context):
                    decision = Decision(
                        decision_id=f"rule_{rule_name}_{int(time.time())}",
                        decision_type=DecisionType.ACCESSIBILITY_ADJUSTMENT,
                        action=rule["recommendation"]["action"],
                        parameters=rule["recommendation"]["parameters"],
                        confidence=ConfidenceLevel.MEDIUM,
                        reasoning=rule["recommendation"]["reasoning"],
                        priority=5,
                        metadata={"rule_name": rule_name}
                    )
                    recommendations.append(decision)
            except Exception as e:
                logger.error(f"规则 {rule_name} 执行失败: {str(e)}")
        
        return recommendations
    
    def _generate_pattern_based_recommendations(self, context: DecisionContext) -> List[Decision]:
        """基于用户模式生成推荐"""
        recommendations = []
        
        # 这里可以基于用户的历史行为模式生成推荐
        # 例如：如果用户通常在这个时间进行某个活动，推荐相关的辅助功能
        
        current_hour = datetime.fromtimestamp(context.timestamp).hour
        
        if 6 <= current_hour <= 9:  # 早晨
            decision = Decision(
                decision_id=f"pattern_morning_{int(time.time())}",
                decision_type=DecisionType.USER_ASSISTANCE,
                action="enable_morning_assistance",
                parameters={"voice_guidance": True, "schedule_reminder": True},
                confidence=ConfidenceLevel.MEDIUM,
                reasoning="基于时间模式，建议启用晨间辅助功能",
                priority=4
            )
            recommendations.append(decision)
        
        elif 22 <= current_hour or current_hour <= 6:  # 夜晚
            decision = Decision(
                decision_id=f"pattern_night_{int(time.time())}",
                decision_type=DecisionType.ACCESSIBILITY_ADJUSTMENT,
                action="enable_night_mode",
                parameters={"dark_theme": True, "reduced_brightness": True},
                confidence=ConfidenceLevel.HIGH,
                reasoning="基于时间模式，建议启用夜间模式",
                priority=6
            )
            recommendations.append(decision)
        
        return recommendations
    
    def _generate_health_recommendations(self, context: DecisionContext) -> List[Decision]:
        """基于健康数据生成推荐"""
        recommendations = []
        
        # 基于心率数据的推荐
        heart_rate_data = context.sensor_data.get("heart_rate", {})
        if heart_rate_data:
            hr_value = heart_rate_data.get("values", [70])[0]
            
            if hr_value > 100:  # 心率过高
                decision = Decision(
                    decision_id=f"health_hr_high_{int(time.time())}",
                    decision_type=DecisionType.HEALTH_RECOMMENDATION,
                    action="suggest_relaxation",
                    parameters={"breathing_exercise": True, "calm_environment": True},
                    confidence=ConfidenceLevel.HIGH,
                    reasoning=f"检测到心率偏高({hr_value} BPM)，建议进行放松活动",
                    priority=7
                )
                recommendations.append(decision)
        
        # 基于活动水平的推荐
        motion_data = context.sensor_data.get("accelerometer", {})
        if motion_data and motion_data.get("activity_level") == "stationary":
            # 检查是否长时间静坐
            decision = Decision(
                decision_id=f"health_activity_{int(time.time())}",
                decision_type=DecisionType.HEALTH_RECOMMENDATION,
                action="suggest_movement",
                parameters={"movement_reminder": True, "exercise_suggestions": True},
                confidence=ConfidenceLevel.MEDIUM,
                reasoning="检测到长时间静坐，建议适当活动",
                priority=5
            )
            recommendations.append(decision)
        
        return recommendations
    
    def _deduplicate_and_rank_recommendations(self, recommendations: List[Decision]) -> List[Decision]:
        """去重和排序推荐"""
        # 按动作类型去重
        seen_actions = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec.action not in seen_actions:
                seen_actions.add(rec.action)
                unique_recommendations.append(rec)
        
        # 按优先级排序
        unique_recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return unique_recommendations[:5]  # 最多返回5个推荐
    
    def record_feedback(self, user_id: str, decision_id: str, feedback: str, rating: int):
        """记录用户反馈"""
        feedback_entry = {
            "decision_id": decision_id,
            "feedback": feedback,
            "rating": rating,  # 1-5分
            "timestamp": time.time()
        }
        self.user_feedback[user_id].append(feedback_entry)
        
        # 保持最近100条反馈
        if len(self.user_feedback[user_id]) > 100:
            self.user_feedback[user_id] = self.user_feedback[user_id][-100:]


class IntelligentDecisionEngine:
    """智能决策引擎核心类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能决策引擎
        
        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("intelligent_decision", {}).get("enabled", True)
        
        # 子模块
        self.behavior_engine = BehaviorLearningEngine()
        self.recommendation_engine = RecommendationEngine()
        
        # 决策历史
        self.decision_history = defaultdict(deque)  # user_id -> deque of decisions
        self.active_decisions = {}  # decision_id -> Decision
        
        # 统计信息
        self.stats = {
            "total_decisions": 0,
            "decisions_by_type": defaultdict(int),
            "average_confidence": 0.0,
            "user_satisfaction": defaultdict(float)
        }
        
        logger.info(f"智能决策引擎初始化完成 - 启用: {self.enabled}")
    
    async def make_decision(self, context: DecisionContext) -> List[Decision]:
        """
        基于上下文做出智能决策
        
        Args:
            context: 决策上下文
            
        Returns:
            决策列表
        """
        if not self.enabled:
            return []
        
        try:
            # 学习用户行为
            self.behavior_engine.learn_from_data(
                context.user_id,
                context.sensor_data,
                context.location_data,
                context.current_activity
            )
            
            # 生成推荐
            recommendations = self.recommendation_engine.generate_recommendations(context)
            
            # 生成安全警报
            safety_decisions = self._generate_safety_decisions(context)
            
            # 生成自动化决策
            automation_decisions = self._generate_automation_decisions(context)
            
            # 合并所有决策
            all_decisions = recommendations + safety_decisions + automation_decisions
            
            # 过滤和优化决策
            final_decisions = self._filter_and_optimize_decisions(all_decisions, context)
            
            # 记录决策
            for decision in final_decisions:
                self._record_decision(context.user_id, decision)
            
            # 更新统计信息
            self._update_stats(final_decisions)
            
            logger.info(f"为用户 {context.user_id} 生成了 {len(final_decisions)} 个决策")
            return final_decisions
            
        except Exception as e:
            logger.error(f"智能决策失败: {str(e)}")
            return []
    
    def _generate_safety_decisions(self, context: DecisionContext) -> List[Decision]:
        """生成安全相关的决策"""
        safety_decisions = []
        
        # 检查GPS精度
        gps_data = context.sensor_data.get("gps", {})
        if gps_data and gps_data.get("accuracy_meters", 0) > 50:
            decision = Decision(
                decision_id=f"safety_gps_{int(time.time())}",
                decision_type=DecisionType.SAFETY_ALERT,
                action="warn_low_gps_accuracy",
                parameters={"accuracy": gps_data.get("accuracy_meters")},
                confidence=ConfidenceLevel.HIGH,
                reasoning="GPS精度较低，可能影响导航准确性",
                priority=8
            )
            safety_decisions.append(decision)
        
        # 检查环境温度
        temp_data = context.sensor_data.get("temperature", {})
        if temp_data:
            temp_value = temp_data.get("values", [20])[0]
            if temp_value > 35 or temp_value < 5:
                decision = Decision(
                    decision_id=f"safety_temp_{int(time.time())}",
                    decision_type=DecisionType.SAFETY_ALERT,
                    action="warn_extreme_temperature",
                    parameters={"temperature": temp_value},
                    confidence=ConfidenceLevel.HIGH,
                    reasoning=f"检测到极端温度({temp_value}°C)，请注意安全",
                    priority=9
                )
                safety_decisions.append(decision)
        
        return safety_decisions
    
    def _generate_automation_decisions(self, context: DecisionContext) -> List[Decision]:
        """生成自动化决策"""
        automation_decisions = []
        
        # 预测下一个活动并准备相应的自动化
        predicted_activity = self.behavior_engine.predict_next_activity(
            context.user_id, context.sensor_data
        )
        
        if predicted_activity:
            decision = Decision(
                decision_id=f"auto_prepare_{int(time.time())}",
                decision_type=DecisionType.AUTOMATION_TRIGGER,
                action="prepare_for_activity",
                parameters={"activity": predicted_activity, "auto_adjust": True},
                confidence=ConfidenceLevel.MEDIUM,
                reasoning=f"预测用户即将进行{predicted_activity}，准备相应设置",
                priority=4
            )
            automation_decisions.append(decision)
        
        # 基于环境自动调整
        light_data = context.sensor_data.get("light", {})
        if light_data:
            lux = light_data.get("lux", 500)
            current_hour = datetime.fromtimestamp(context.timestamp).hour
            
            if lux < 10 and 6 <= current_hour <= 22:  # 白天但很暗
                decision = Decision(
                    decision_id=f"auto_light_{int(time.time())}",
                    decision_type=DecisionType.AUTOMATION_TRIGGER,
                    action="auto_adjust_display",
                    parameters={"brightness": "increase", "contrast": "enhance"},
                    confidence=ConfidenceLevel.HIGH,
                    reasoning="检测到光线不足，自动调整显示设置",
                    priority=6
                )
                automation_decisions.append(decision)
        
        return automation_decisions
    
    def _filter_and_optimize_decisions(self, decisions: List[Decision], 
                                     context: DecisionContext) -> List[Decision]:
        """过滤和优化决策"""
        if not decisions:
            return []
        
        # 过滤过期的决策
        current_time = time.time()
        valid_decisions = [
            d for d in decisions 
            if d.expires_at is None or d.expires_at > current_time
        ]
        
        # 过滤重复的决策（基于用户最近的决策历史）
        recent_decisions = list(self.decision_history[context.user_id])[-10:]
        recent_actions = {d.action for d in recent_decisions}
        
        filtered_decisions = []
        for decision in valid_decisions:
            # 如果是高优先级决策或者最近没有执行过相同动作
            if decision.priority >= 7 or decision.action not in recent_actions:
                filtered_decisions.append(decision)
        
        # 按优先级排序
        filtered_decisions.sort(key=lambda x: x.priority, reverse=True)
        
        # 限制决策数量
        return filtered_decisions[:3]  # 最多返回3个决策
    
    def _record_decision(self, user_id: str, decision: Decision):
        """记录决策"""
        self.decision_history[user_id].append(decision)
        if len(self.decision_history[user_id]) > 100:
            self.decision_history[user_id].popleft()
        
        self.active_decisions[decision.decision_id] = decision
    
    def _update_stats(self, decisions: List[Decision]):
        """更新统计信息"""
        self.stats["total_decisions"] += len(decisions)
        
        for decision in decisions:
            self.stats["decisions_by_type"][decision.decision_type.value] += 1
        
        if decisions:
            confidence_values = {
                ConfidenceLevel.LOW: 0.25,
                ConfidenceLevel.MEDIUM: 0.5,
                ConfidenceLevel.HIGH: 0.75,
                ConfidenceLevel.VERY_HIGH: 1.0
            }
            
            avg_confidence = np.mean([
                confidence_values.get(d.confidence, 0.5) for d in decisions
            ])
            
            # 更新平均置信度
            total_decisions = self.stats["total_decisions"]
            current_avg = self.stats["average_confidence"]
            self.stats["average_confidence"] = (
                (current_avg * (total_decisions - len(decisions)) + 
                 avg_confidence * len(decisions)) / total_decisions
            )
    
    def get_user_behavior_patterns(self, user_id: str) -> List[UserBehaviorPattern]:
        """获取用户行为模式"""
        return self.behavior_engine.get_user_patterns(user_id)
    
    def record_decision_feedback(self, user_id: str, decision_id: str, 
                               feedback: str, rating: int):
        """记录决策反馈"""
        self.recommendation_engine.record_feedback(user_id, decision_id, feedback, rating)
        
        # 更新用户满意度
        if user_id in self.stats["user_satisfaction"]:
            current_rating = self.stats["user_satisfaction"][user_id]
            self.stats["user_satisfaction"][user_id] = (current_rating + rating) / 2
        else:
            self.stats["user_satisfaction"][user_id] = rating
    
    def get_decision_history(self, user_id: str, limit: int = 20) -> List[Decision]:
        """获取决策历史"""
        if user_id in self.decision_history:
            history = list(self.decision_history[user_id])
            return history[-limit:] if len(history) > limit else history
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "enabled": self.enabled,
            "total_users": len(self.decision_history),
            "active_decisions": len(self.active_decisions),
            **dict(self.stats)
        } 