#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI协调器 - 协调各个智能模块的高级AI系统
包含深度学习模型、预测算法、情感识别、健康预警等功能
"""

import logging
import time
import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


class AIModelType(Enum):
    """AI模型类型枚举"""
    BEHAVIOR_PREDICTION = "behavior_prediction"
    EMOTION_RECOGNITION = "emotion_recognition"
    HEALTH_RISK_ASSESSMENT = "health_risk_assessment"
    ACTIVITY_CLASSIFICATION = "activity_classification"
    ANOMALY_DETECTION = "anomaly_detection"
    PERSONALIZATION = "personalization"
    CONTEXT_UNDERSTANDING = "context_understanding"


class PredictionConfidence(Enum):
    """预测置信度枚举"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class AIModelResult:
    """AI模型结果"""
    model_type: AIModelType
    prediction: Any
    confidence: PredictionConfidence
    probability_scores: Dict[str, float]
    feature_importance: Dict[str, float]
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserContext:
    """用户上下文信息"""
    user_id: str
    current_activity: str
    location_context: Dict[str, Any]
    temporal_context: Dict[str, Any]
    sensor_context: Dict[str, Any]
    health_context: Dict[str, Any]
    emotional_state: Dict[str, Any]
    preferences: Dict[str, Any]
    historical_patterns: Dict[str, Any]


@dataclass
class HealthAlert:
    """健康警报"""
    alert_id: str
    user_id: str
    alert_type: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    recommendations: List[str]
    confidence: float
    timestamp: float
    expires_at: Optional[float] = None


class EmotionRecognitionModel:
    """情感识别模型"""
    
    def __init__(self):
        self.emotion_categories = [
            "happy", "sad", "angry", "anxious", "calm", 
            "excited", "tired", "stressed", "relaxed", "focused"
        ]
        self.feature_weights = {
            "voice_tone": 0.3,
            "movement_patterns": 0.25,
            "heart_rate_variability": 0.2,
            "interaction_patterns": 0.15,
            "environmental_factors": 0.1
        }
    
    def recognize_emotion(self, sensor_data: Dict[str, Any], 
                         behavioral_data: Dict[str, Any]) -> AIModelResult:
        """识别用户情感状态"""
        try:
            # 提取特征
            features = self._extract_emotion_features(sensor_data, behavioral_data)
            
            # 计算情感概率
            emotion_scores = self._calculate_emotion_scores(features)
            
            # 确定主要情感
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            # 计算置信度
            confidence = self._calculate_confidence(emotion_scores)
            
            return AIModelResult(
                model_type=AIModelType.EMOTION_RECOGNITION,
                prediction=primary_emotion[0],
                confidence=confidence,
                probability_scores=emotion_scores,
                feature_importance=self._calculate_feature_importance(features),
                timestamp=time.time(),
                metadata={
                    "emotion_distribution": emotion_scores,
                    "dominant_features": self._get_dominant_features(features)
                }
            )
            
        except Exception as e:
            logger.error(f"情感识别失败: {str(e)}")
            return self._get_default_emotion_result()
    
    def _extract_emotion_features(self, sensor_data: Dict[str, Any], 
                                 behavioral_data: Dict[str, Any]) -> Dict[str, float]:
        """提取情感特征"""
        features = {}
        
        # 语音特征
        if "microphone" in sensor_data:
            mic_data = sensor_data["microphone"]
            features["voice_energy"] = np.mean([d.get("values", [0])[0] for d in mic_data])
            features["voice_variability"] = np.std([d.get("values", [0])[0] for d in mic_data])
        
        # 运动模式特征
        if "accelerometer" in sensor_data:
            acc_data = sensor_data["accelerometer"]
            movement_intensity = np.mean([np.linalg.norm(d.get("values", [0, 0, 0])) for d in acc_data])
            features["movement_intensity"] = movement_intensity
            features["movement_variability"] = np.std([np.linalg.norm(d.get("values", [0, 0, 0])) for d in acc_data])
        
        # 心率变异性特征
        if "heart_rate" in sensor_data:
            hr_data = sensor_data["heart_rate"]
            hr_values = [d.get("values", [70])[0] for d in hr_data]
            features["heart_rate_avg"] = np.mean(hr_values)
            features["heart_rate_variability"] = np.std(hr_values)
        
        # 交互模式特征
        if "interaction_frequency" in behavioral_data:
            features["interaction_frequency"] = behavioral_data["interaction_frequency"]
        
        # 环境因素
        if "light" in sensor_data:
            light_data = sensor_data["light"]
            features["ambient_light"] = np.mean([d.get("values", [0])[0] for d in light_data])
        
        return features
    
    def _calculate_emotion_scores(self, features: Dict[str, float]) -> Dict[str, float]:
        """计算各种情感的概率分数"""
        scores = {}
        
        # 基于特征计算情感分数（简化的规则基础模型）
        movement_intensity = features.get("movement_intensity", 0)
        heart_rate_avg = features.get("heart_rate_avg", 70)
        heart_rate_var = features.get("heart_rate_variability", 5)
        voice_energy = features.get("voice_energy", 0.5)
        
        # 快乐 - 中等运动强度，稳定心率，活跃语音
        scores["happy"] = min(1.0, (
            (0.5 if 0.3 <= movement_intensity <= 0.7 else 0.2) +
            (0.3 if 60 <= heart_rate_avg <= 80 else 0.1) +
            (0.2 if voice_energy > 0.6 else 0.1)
        ))
        
        # 焦虑 - 高心率变异性，低运动强度
        scores["anxious"] = min(1.0, (
            (0.4 if heart_rate_var > 10 else 0.1) +
            (0.3 if movement_intensity < 0.2 else 0.1) +
            (0.3 if heart_rate_avg > 85 else 0.1)
        ))
        
        # 平静 - 低运动强度，稳定心率
        scores["calm"] = min(1.0, (
            (0.4 if movement_intensity < 0.3 else 0.1) +
            (0.4 if heart_rate_var < 5 else 0.1) +
            (0.2 if 60 <= heart_rate_avg <= 75 else 0.1)
        ))
        
        # 疲劳 - 低运动强度，低语音能量
        scores["tired"] = min(1.0, (
            (0.4 if movement_intensity < 0.2 else 0.1) +
            (0.3 if voice_energy < 0.3 else 0.1) +
            (0.3 if heart_rate_avg < 65 else 0.1)
        ))
        
        # 压力 - 高心率，高心率变异性
        scores["stressed"] = min(1.0, (
            (0.4 if heart_rate_avg > 90 else 0.1) +
            (0.4 if heart_rate_var > 15 else 0.1) +
            (0.2 if movement_intensity > 0.8 else 0.1)
        ))
        
        # 为其他情感设置默认分数
        for emotion in self.emotion_categories:
            if emotion not in scores:
                scores[emotion] = 0.1
        
        # 归一化分数
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v / total_score for k, v in scores.items()}
        
        return scores
    
    def _calculate_confidence(self, emotion_scores: Dict[str, float]) -> PredictionConfidence:
        """计算预测置信度"""
        max_score = max(emotion_scores.values())
        score_variance = np.var(list(emotion_scores.values()))
        
        if max_score > 0.7 and score_variance > 0.05:
            return PredictionConfidence.VERY_HIGH
        elif max_score > 0.6:
            return PredictionConfidence.HIGH
        elif max_score > 0.4:
            return PredictionConfidence.MEDIUM
        elif max_score > 0.3:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    def _calculate_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """计算特征重要性"""
        importance = {}
        total_features = len(features)
        
        for feature, value in features.items():
            # 基于特征值的变化程度计算重要性
            if "heart_rate" in feature:
                importance[feature] = 0.3
            elif "movement" in feature:
                importance[feature] = 0.25
            elif "voice" in feature:
                importance[feature] = 0.2
            else:
                importance[feature] = 0.1
        
        return importance
    
    def _get_dominant_features(self, features: Dict[str, float]) -> List[str]:
        """获取主导特征"""
        sorted_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)
        return [f[0] for f in sorted_features[:3]]
    
    def _get_default_emotion_result(self) -> AIModelResult:
        """获取默认情感识别结果"""
        return AIModelResult(
            model_type=AIModelType.EMOTION_RECOGNITION,
            prediction="calm",
            confidence=PredictionConfidence.LOW,
            probability_scores={"calm": 0.5, "unknown": 0.5},
            feature_importance={},
            timestamp=time.time()
        )


class HealthRiskAssessmentModel:
    """健康风险评估模型"""
    
    def __init__(self):
        self.risk_categories = [
            "cardiovascular", "metabolic", "mental_health", 
            "sleep_disorder", "stress_related", "injury_risk"
        ]
        self.risk_thresholds = {
            "heart_rate_high": 100,
            "heart_rate_low": 50,
            "movement_low": 0.1,
            "stress_high": 0.7,
            "sleep_insufficient": 6.0
        }
    
    def assess_health_risks(self, user_context: UserContext) -> List[HealthAlert]:
        """评估用户健康风险"""
        try:
            alerts = []
            
            # 心血管风险评估
            cv_alert = self._assess_cardiovascular_risk(user_context)
            if cv_alert:
                alerts.append(cv_alert)
            
            # 代谢风险评估
            metabolic_alert = self._assess_metabolic_risk(user_context)
            if metabolic_alert:
                alerts.append(metabolic_alert)
            
            # 心理健康风险评估
            mental_alert = self._assess_mental_health_risk(user_context)
            if mental_alert:
                alerts.append(mental_alert)
            
            # 睡眠障碍风险评估
            sleep_alert = self._assess_sleep_risk(user_context)
            if sleep_alert:
                alerts.append(sleep_alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"健康风险评估失败: {str(e)}")
            return []
    
    def _assess_cardiovascular_risk(self, user_context: UserContext) -> Optional[HealthAlert]:
        """评估心血管风险"""
        sensor_data = user_context.sensor_context
        
        if "heart_rate" not in sensor_data:
            return None
        
        hr_data = sensor_data["heart_rate"]
        if not hr_data:
            return None
        
        avg_hr = np.mean([d.get("values", [70])[0] for d in hr_data])
        hr_variability = np.std([d.get("values", [70])[0] for d in hr_data])
        
        # 检查异常心率
        if avg_hr > self.risk_thresholds["heart_rate_high"]:
            return HealthAlert(
                alert_id=f"cv_high_hr_{int(time.time())}",
                user_id=user_context.user_id,
                alert_type="cardiovascular",
                severity="medium",
                message=f"检测到心率偏高 ({avg_hr:.1f} bpm)，建议休息并监测",
                recommendations=[
                    "立即停止剧烈活动",
                    "深呼吸放松",
                    "如持续异常请咨询医生"
                ],
                confidence=0.8,
                timestamp=time.time(),
                expires_at=time.time() + 3600  # 1小时后过期
            )
        
        elif avg_hr < self.risk_thresholds["heart_rate_low"]:
            return HealthAlert(
                alert_id=f"cv_low_hr_{int(time.time())}",
                user_id=user_context.user_id,
                alert_type="cardiovascular",
                severity="medium",
                message=f"检测到心率偏低 ({avg_hr:.1f} bpm)，建议关注",
                recommendations=[
                    "适当增加活动量",
                    "检查是否有不适症状",
                    "如有异常请咨询医生"
                ],
                confidence=0.7,
                timestamp=time.time(),
                expires_at=time.time() + 3600
            )
        
        return None
    
    def _assess_metabolic_risk(self, user_context: UserContext) -> Optional[HealthAlert]:
        """评估代谢风险"""
        sensor_data = user_context.sensor_context
        temporal_data = user_context.temporal_context
        
        # 检查活动水平
        if "accelerometer" in sensor_data:
            acc_data = sensor_data["accelerometer"]
            movement_intensity = np.mean([
                np.linalg.norm(d.get("values", [0, 0, 0])) 
                for d in acc_data
            ])
            
            if movement_intensity < self.risk_thresholds["movement_low"]:
                return HealthAlert(
                    alert_id=f"metabolic_low_activity_{int(time.time())}",
                    user_id=user_context.user_id,
                    alert_type="metabolic",
                    severity="low",
                    message="检测到活动量不足，建议增加运动",
                    recommendations=[
                        "每天至少30分钟中等强度运动",
                        "多走路，少久坐",
                        "选择喜欢的运动方式"
                    ],
                    confidence=0.6,
                    timestamp=time.time(),
                    expires_at=time.time() + 7200  # 2小时后过期
                )
        
        return None
    
    def _assess_mental_health_risk(self, user_context: UserContext) -> Optional[HealthAlert]:
        """评估心理健康风险"""
        emotional_state = user_context.emotional_state
        
        if not emotional_state:
            return None
        
        # 检查负面情绪
        negative_emotions = ["sad", "angry", "anxious", "stressed"]
        negative_score = sum(
            emotional_state.get(emotion, 0) 
            for emotion in negative_emotions
        )
        
        if negative_score > 0.6:
            return HealthAlert(
                alert_id=f"mental_negative_emotion_{int(time.time())}",
                user_id=user_context.user_id,
                alert_type="mental_health",
                severity="medium",
                message="检测到负面情绪较强，建议关注心理健康",
                recommendations=[
                    "尝试放松技巧如深呼吸、冥想",
                    "与朋友或家人交流",
                    "考虑专业心理咨询",
                    "保持规律作息和适量运动"
                ],
                confidence=0.7,
                timestamp=time.time(),
                expires_at=time.time() + 1800  # 30分钟后过期
            )
        
        return None
    
    def _assess_sleep_risk(self, user_context: UserContext) -> Optional[HealthAlert]:
        """评估睡眠风险"""
        temporal_data = user_context.temporal_context
        
        # 检查睡眠时长
        sleep_duration = temporal_data.get("sleep_duration", 8.0)
        
        if sleep_duration < self.risk_thresholds["sleep_insufficient"]:
            return HealthAlert(
                alert_id=f"sleep_insufficient_{int(time.time())}",
                user_id=user_context.user_id,
                alert_type="sleep_disorder",
                severity="medium",
                message=f"睡眠时间不足 ({sleep_duration:.1f}小时)，建议改善睡眠",
                recommendations=[
                    "保持规律的睡眠时间",
                    "睡前避免使用电子设备",
                    "创造舒适的睡眠环境",
                    "避免睡前饮用咖啡因"
                ],
                confidence=0.8,
                timestamp=time.time(),
                expires_at=time.time() + 14400  # 4小时后过期
            )
        
        return None


class AICoordinator:
    """AI协调器主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.emotion_model = EmotionRecognitionModel()
        self.health_risk_model = HealthRiskAssessmentModel()
        
        # 模块引用
        self.sensor_manager = None
        self.intelligent_decision = None
        self.temporal_awareness = None
        self.environmental_intelligence = None
        
        # 数据存储
        self.user_contexts = {}  # user_id -> UserContext
        self.ai_results_history = defaultdict(deque)  # user_id -> deque of AIModelResult
        self.active_alerts = defaultdict(list)  # user_id -> List[HealthAlert]
        
        # 统计信息
        self.stats = {
            "total_predictions": 0,
            "emotion_recognitions": 0,
            "health_assessments": 0,
            "alerts_generated": 0,
            "start_time": time.time()
        }
        
        # 异步任务
        self.running = False
        self.coordination_task = None
    
    def set_module_references(self, sensor_manager, intelligent_decision, 
                            temporal_awareness, environmental_intelligence):
        """设置其他模块的引用"""
        self.sensor_manager = sensor_manager
        self.intelligent_decision = intelligent_decision
        self.temporal_awareness = temporal_awareness
        self.environmental_intelligence = environmental_intelligence
    
    async def start(self):
        """启动AI协调器"""
        try:
            self.running = True
            self.coordination_task = asyncio.create_task(self._coordination_loop())
            logger.info("AI协调器启动成功")
            
        except Exception as e:
            logger.error(f"AI协调器启动失败: {str(e)}")
            raise
    
    async def stop(self):
        """停止AI协调器"""
        try:
            self.running = False
            if self.coordination_task:
                self.coordination_task.cancel()
                try:
                    await self.coordination_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("AI协调器停止成功")
            
        except Exception as e:
            logger.error(f"AI协调器停止失败: {str(e)}")
    
    async def _coordination_loop(self):
        """AI协调主循环"""
        while self.running:
            try:
                # 更新用户上下文
                await self._update_user_contexts()
                
                # 执行AI分析
                await self._perform_ai_analysis()
                
                # 生成健康警报
                await self._generate_health_alerts()
                
                # 清理过期数据
                await self._cleanup_expired_data()
                
                # 等待下一个周期
                await asyncio.sleep(self.config.get("coordination_interval", 30))
                
            except Exception as e:
                logger.error(f"AI协调循环错误: {str(e)}")
                await asyncio.sleep(5)
    
    async def _update_user_contexts(self):
        """更新用户上下文信息"""
        try:
            # 这里应该从其他模块获取用户数据
            # 由于模块引用可能为None，我们使用模拟数据
            
            for user_id in self.config.get("active_users", []):
                context = UserContext(
                    user_id=user_id,
                    current_activity="unknown",
                    location_context={},
                    temporal_context={},
                    sensor_context={},
                    health_context={},
                    emotional_state={},
                    preferences={},
                    historical_patterns={}
                )
                
                # 如果有传感器管理器，获取传感器数据
                if self.sensor_manager:
                    try:
                        sensor_data = {}
                        for sensor_type in ["accelerometer", "heart_rate", "microphone"]:
                            readings = self.sensor_manager.get_readings(sensor_type, 10)
                            if readings:
                                sensor_data[sensor_type] = [
                                    {"values": r.values, "timestamp": r.timestamp} 
                                    for r in readings
                                ]
                        context.sensor_context = sensor_data
                    except:
                        pass
                
                # 如果有时间感知模块，获取时间上下文
                if self.temporal_awareness:
                    try:
                        time_context = self.temporal_awareness.get_time_context()
                        context.temporal_context = time_context
                    except:
                        pass
                
                self.user_contexts[user_id] = context
                
        except Exception as e:
            logger.error(f"更新用户上下文失败: {str(e)}")
    
    async def _perform_ai_analysis(self):
        """执行AI分析"""
        try:
            for user_id, context in self.user_contexts.items():
                # 情感识别
                if context.sensor_context:
                    emotion_result = self.emotion_model.recognize_emotion(
                        context.sensor_context, 
                        context.historical_patterns
                    )
                    
                    # 更新用户情感状态
                    context.emotional_state = emotion_result.probability_scores
                    
                    # 存储结果
                    self.ai_results_history[user_id].append(emotion_result)
                    if len(self.ai_results_history[user_id]) > 100:
                        self.ai_results_history[user_id].popleft()
                    
                    self.stats["emotion_recognitions"] += 1
                    self.stats["total_predictions"] += 1
                
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
    
    async def _generate_health_alerts(self):
        """生成健康警报"""
        try:
            for user_id, context in self.user_contexts.items():
                # 健康风险评估
                new_alerts = self.health_risk_model.assess_health_risks(context)
                
                for alert in new_alerts:
                    # 检查是否已存在相似警报
                    if not self._is_duplicate_alert(user_id, alert):
                        self.active_alerts[user_id].append(alert)
                        self.stats["alerts_generated"] += 1
                        
                        # 记录警报
                        logger.info(f"为用户 {user_id} 生成健康警报: {alert.message}")
                
                self.stats["health_assessments"] += 1
                
        except Exception as e:
            logger.error(f"生成健康警报失败: {str(e)}")
    
    def _is_duplicate_alert(self, user_id: str, new_alert: HealthAlert) -> bool:
        """检查是否为重复警报"""
        existing_alerts = self.active_alerts.get(user_id, [])
        
        for existing_alert in existing_alerts:
            if (existing_alert.alert_type == new_alert.alert_type and
                existing_alert.severity == new_alert.severity and
                time.time() - existing_alert.timestamp < 1800):  # 30分钟内
                return True
        
        return False
    
    async def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            current_time = time.time()
            
            # 清理过期警报
            for user_id in self.active_alerts:
                self.active_alerts[user_id] = [
                    alert for alert in self.active_alerts[user_id]
                    if alert.expires_at is None or alert.expires_at > current_time
                ]
            
        except Exception as e:
            logger.error(f"清理过期数据失败: {str(e)}")
    
    def get_user_emotional_state(self, user_id: str) -> Dict[str, Any]:
        """获取用户情感状态"""
        context = self.user_contexts.get(user_id)
        if context:
            return context.emotional_state
        return {}
    
    def get_user_health_alerts(self, user_id: str) -> List[HealthAlert]:
        """获取用户健康警报"""
        return self.active_alerts.get(user_id, [])
    
    def get_ai_insights(self, user_id: str) -> Dict[str, Any]:
        """获取AI洞察"""
        try:
            context = self.user_contexts.get(user_id)
            if not context:
                return {}
            
            recent_results = list(self.ai_results_history.get(user_id, []))[-10:]
            
            insights = {
                "emotional_state": context.emotional_state,
                "health_alerts": self.get_user_health_alerts(user_id),
                "recent_predictions": [
                    {
                        "type": result.model_type.value,
                        "prediction": result.prediction,
                        "confidence": result.confidence.value,
                        "timestamp": result.timestamp
                    }
                    for result in recent_results
                ],
                "risk_assessment": self._calculate_overall_risk(user_id),
                "recommendations": self._generate_personalized_recommendations(user_id)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"获取AI洞察失败: {str(e)}")
            return {}
    
    def _calculate_overall_risk(self, user_id: str) -> Dict[str, Any]:
        """计算整体风险评估"""
        alerts = self.get_user_health_alerts(user_id)
        
        risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in alerts:
            risk_levels[alert.severity] += 1
        
        # 计算整体风险分数
        overall_score = (
            risk_levels["low"] * 0.1 +
            risk_levels["medium"] * 0.3 +
            risk_levels["high"] * 0.6 +
            risk_levels["critical"] * 1.0
        )
        
        if overall_score >= 0.8:
            overall_level = "high"
        elif overall_score >= 0.4:
            overall_level = "medium"
        else:
            overall_level = "low"
        
        return {
            "overall_level": overall_level,
            "overall_score": overall_score,
            "risk_breakdown": risk_levels,
            "active_alerts_count": len(alerts)
        }
    
    def _generate_personalized_recommendations(self, user_id: str) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        context = self.user_contexts.get(user_id)
        if not context:
            return recommendations
        
        # 基于情感状态的建议
        emotional_state = context.emotional_state
        if emotional_state:
            dominant_emotion = max(emotional_state.items(), key=lambda x: x[1])
            
            if dominant_emotion[0] in ["stressed", "anxious"]:
                recommendations.extend([
                    "尝试深呼吸练习或冥想",
                    "考虑短暂休息或散步",
                    "听一些舒缓的音乐"
                ])
            elif dominant_emotion[0] == "tired":
                recommendations.extend([
                    "确保充足的睡眠",
                    "适当补充水分",
                    "考虑小憩片刻"
                ])
        
        # 基于健康警报的建议
        alerts = self.get_user_health_alerts(user_id)
        for alert in alerts:
            recommendations.extend(alert.recommendations)
        
        # 去重并限制数量
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:5]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "active_users": len(self.user_contexts),
            "total_active_alerts": sum(len(alerts) for alerts in self.active_alerts.values()),
            "average_predictions_per_minute": self.stats["total_predictions"] / max(uptime / 60, 1)
        } 