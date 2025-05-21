#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情绪分析服务
负责分析用户输入（文本、语音等）中的情绪状态，并提供中医情志理论相关的情绪干预建议
"""
import logging
import json
import os
import base64
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class EmotionalService:
    """情绪分析服务"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化情绪分析服务"""
        logger.info("初始化情绪分析服务")
        self.config = config or {}
        
        # 初始化情绪分析模型和资源
        self.emotion_model = self._init_emotion_model()
        self.tcm_emotion_mappings = self._load_tcm_emotion_mappings()
        self.intervention_strategies = self._load_intervention_strategies()
        logger.info("情绪分析服务初始化完成")
    
    def _init_emotion_model(self) -> Any:
        """初始化情绪分析模型"""
        # TODO: 替换为实际模型加载逻辑
        # 这里仅为示例，实际实现应该加载预训练的情绪分析模型
        emotion_model = {
            "initialized": True,
            "version": "1.0.0"
        }
        return emotion_model
    
    def _load_tcm_emotion_mappings(self) -> Dict[str, Dict[str, Any]]:
        """加载中医情志理论与现代情绪分类的映射"""
        return {
            "怒": {
                "modern_emotions": ["愤怒", "恼火", "烦躁", "易怒"],
                "organ": "肝",
                "imbalance_symptoms": ["头痛", "目赤", "口苦", "胁痛", "失眠"],
                "balancing_elements": ["疏肝解郁", "平肝潜阳", "柔肝止痛"]
            },
            "喜": {
                "modern_emotions": ["快乐", "兴奋", "欣喜", "激动"],
                "organ": "心",
                "imbalance_symptoms": ["心悸", "失眠", "多梦", "健忘", "舌尖红"],
                "balancing_elements": ["静心安神", "养心清热", "宁心安志"]
            },
            "思": {
                "modern_emotions": ["思虑", "担忧", "反刍思考", "专注"],
                "organ": "脾",
                "imbalance_symptoms": ["食欲不振", "消化不良", "腹胀", "乏力"],
                "balancing_elements": ["健脾养胃", "解郁化滞", "宽中理气"]
            },
            "忧": {
                "modern_emotions": ["忧郁", "悲伤", "悲观", "低落"],
                "organ": "肺",
                "imbalance_symptoms": ["胸闷", "气短", "乏力", "食欲减退"],
                "balancing_elements": ["疏肝解郁", "养心安神", "理气开郁"]
            },
            "恐": {
                "modern_emotions": ["恐惧", "害怕", "焦虑", "紧张"],
                "organ": "肾",
                "imbalance_symptoms": ["心悸", "失眠", "易惊醒", "腰膝酸软"],
                "balancing_elements": ["补肾安神", "固本培元", "镇静安神"]
            },
            "惊": {
                "modern_emotions": ["惊吓", "震惊", "应激"],
                "organ": "心",
                "imbalance_symptoms": ["心悸", "惊恐不安", "失眠", "多汗"],
                "balancing_elements": ["安神定志", "平肝熄风", "滋阴潜阳"]
            },
            "悲": {
                "modern_emotions": ["悲伤", "哀痛", "伤感", "消沉"],
                "organ": "肺",
                "imbalance_symptoms": ["胸闷", "气短", "乏力", "食欲减退"],
                "balancing_elements": ["疏肝理气", "养心解郁", "培土生金"]
            }
        }
    
    def _load_intervention_strategies(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载情绪干预策略"""
        return {
            "怒": [
                {
                    "type": "breathing",
                    "name": "肝经疏导呼吸法",
                    "description": "采用4-7-8呼吸法，吸气4秒，屏息7秒，呼气8秒，关注肝经循行部位",
                    "effectiveness": 0.85,
                    "suitable_for": ["肝郁化火", "肝阳上亢"]
                },
                {
                    "type": "tea",
                    "name": "菊花茶",
                    "description": "菊花具有疏风清热、平肝明目的功效",
                    "effectiveness": 0.75,
                    "suitable_for": ["肝火旺盛", "目赤肿痛"]
                },
                {
                    "type": "activity",
                    "name": "八段锦",
                    "description": "通过舒缓的运动疏通经络，特别是侧身拉弓式可舒展肝胆经",
                    "effectiveness": 0.9,
                    "suitable_for": ["气机郁滞", "肝气郁结"]
                }
            ],
            "喜": [
                {
                    "type": "meditation",
                    "name": "心经安神冥想",
                    "description": "静坐冥想，专注于心口处，想象清凉之气进入心经",
                    "effectiveness": 0.8,
                    "suitable_for": ["心火亢盛", "心神不宁"]
                },
                {
                    "type": "tea",
                    "name": "莲子心茶",
                    "description": "具有清心除烦的功效",
                    "effectiveness": 0.7,
                    "suitable_for": ["心火上炎", "心神不宁"]
                }
            ],
            "思": [
                {
                    "type": "acupressure",
                    "name": "足三里穴按摩",
                    "description": "按揉足三里穴，有健脾和胃的作用",
                    "effectiveness": 0.85,
                    "suitable_for": ["脾虚", "消化不良"]
                },
                {
                    "type": "diet",
                    "name": "健脾养胃粥",
                    "description": "山药、大枣、莲子煮粥，具有健脾益气的功效",
                    "effectiveness": 0.75,
                    "suitable_for": ["脾虚湿盛", "食欲不振"]
                }
            ],
            "忧": [
                {
                    "type": "breathing",
                    "name": "肺经扩展呼吸",
                    "description": "深呼吸练习，重点关注胸部扩展",
                    "effectiveness": 0.9,
                    "suitable_for": ["肺气不足", "气短胸闷"]
                },
                {
                    "type": "activity",
                    "name": "太极拍打功",
                    "description": "轻拍胸部和上背部，疏通肺经",
                    "effectiveness": 0.8,
                    "suitable_for": ["肺气郁滞", "胸闷气短"]
                }
            ],
            "恐": [
                {
                    "type": "meditation",
                    "name": "肾元固摄冥想",
                    "description": "冥想时关注下丹田区域，呼吸时想象能量在肾区积聚",
                    "effectiveness": 0.85,
                    "suitable_for": ["肾气不固", "精神恍惚"]
                },
                {
                    "type": "diet",
                    "name": "核桃黑芝麻糊",
                    "description": "补肾益精食疗",
                    "effectiveness": 0.7,
                    "suitable_for": ["肾精不足", "心肾不交"]
                }
            ]
        }
    
    async def analyze_emotional_state(self, user_id: str, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析用户情绪状态
        
        Args:
            user_id: 用户ID
            inputs: 情绪输入数据，可包含文本、语音等
            
        Returns:
            Dict[str, Any]: 情绪分析结果
        """
        logger.info(f"分析用户 {user_id} 的情绪状态")
        
        # 分析各种输入中的情绪
        emotion_scores = {}
        primary_emotion = ""
        emotional_tendency = "stable"
        
        for input_data in inputs:
            input_type = input_data.get("input_type", "")
            data = input_data.get("data", b"")
            metadata = input_data.get("metadata", {})
            
            if input_type == "text":
                # 处理文本输入
                text_content = data.decode('utf-8') if isinstance(data, bytes) else str(data)
                text_emotion_scores = self._analyze_text_emotion(text_content)
                self._update_emotion_scores(emotion_scores, text_emotion_scores, weight=0.6)
                
            elif input_type == "voice":
                # 处理语音输入
                voice_emotion_scores = self._analyze_voice_emotion(data, metadata)
                self._update_emotion_scores(emotion_scores, voice_emotion_scores, weight=0.8)
                
            elif input_type == "physiological":
                # 处理生理指标
                physio_emotion_scores = self._analyze_physiological_data(data, metadata)
                self._update_emotion_scores(emotion_scores, physio_emotion_scores, weight=0.9)
        
        # 标准化情绪得分
        total_score = sum(emotion_scores.values()) or 1  # 避免除以零
        normalized_scores = {k: v/total_score for k, v in emotion_scores.items()}
        
        # 确定主要情绪和情绪倾向
        if normalized_scores:
            primary_emotion = max(normalized_scores, key=normalized_scores.get)
            emotional_tendency = self._determine_emotional_tendency(normalized_scores, user_id)
        
        # 分析情绪对健康的影响
        health_impact = self._analyze_health_impact(normalized_scores, primary_emotion, user_id)
        
        # 生成干预建议
        suggestions = self._generate_intervention_suggestions(normalized_scores, primary_emotion, health_impact)
        
        result = {
            "emotion_scores": normalized_scores,
            "primary_emotion": primary_emotion,
            "emotional_tendency": emotional_tendency,
            "health_impact": health_impact,
            "suggestions": suggestions
        }
        
        logger.info(f"用户 {user_id} 的情绪分析完成，主要情绪: {primary_emotion}")
        return result
    
    def _analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """分析文本中的情绪"""
        # TODO: 实现实际的文本情绪分析逻辑
        # 示例实现，实际应使用NLP模型进行分析
        keywords = {
            "愤怒": ["生气", "愤怒", "恼火", "烦躁", "不爽", "恨", "讨厌"],
            "快乐": ["开心", "高兴", "喜悦", "兴奋", "欣喜", "幸福", "满足"],
            "忧郁": ["难过", "悲伤", "伤心", "消沉", "低落", "痛苦", "忧伤"],
            "恐惧": ["害怕", "恐惧", "担心", "焦虑", "紧张", "惊恐", "惊慌"],
            "平静": ["平静", "放松", "安心", "平和", "舒适", "安宁", "淡定"]
        }
        
        scores = {"愤怒": 0.0, "快乐": 0.0, "忧郁": 0.0, "恐惧": 0.0, "平静": 0.1}  # 基础平静值
        
        # 简单的关键词匹配
        for emotion, words in keywords.items():
            for word in words:
                if word in text:
                    scores[emotion] += 0.2  # 每个关键词增加0.2分
        
        return scores
    
    def _analyze_voice_emotion(self, voice_data: bytes, metadata: Dict[str, str]) -> Dict[str, float]:
        """分析语音中的情绪"""
        # TODO: 实现实际的语音情绪分析逻辑
        # 示例实现，实际应使用音频分析模型
        
        # 假设metadata包含一些预处理特征
        pitch = float(metadata.get("pitch", "0.5"))
        volume = float(metadata.get("volume", "0.5"))
        speech_rate = float(metadata.get("speech_rate", "0.5"))
        
        scores = {
            "愤怒": 0.0,
            "快乐": 0.0,
            "忧郁": 0.0,
            "恐惧": 0.0,
            "平静": 0.0
        }
        
        # 基于音高、音量和语速的简单规则
        if pitch > 0.7 and volume > 0.7:  # 高音高音量
            if speech_rate > 0.7:  # 快速说话
                scores["愤怒"] = 0.7
                scores["快乐"] = 0.3
            else:
                scores["快乐"] = 0.7
        elif pitch < 0.3 and volume < 0.3:  # 低音低音量
            scores["忧郁"] = 0.8
        elif volume > 0.7 and speech_rate < 0.3:  # 高音量慢语速
            scores["恐惧"] = 0.6
        else:
            scores["平静"] = 0.6
        
        return scores
    
    def _analyze_physiological_data(self, data: bytes, metadata: Dict[str, str]) -> Dict[str, float]:
        """分析生理数据中的情绪指标"""
        # TODO: 实现实际的生理数据情绪分析逻辑
        # 示例实现，实际应基于心率变异性、皮肤电导率等指标
        
        # 假设metadata包含一些预处理指标
        heart_rate = float(metadata.get("heart_rate", "70"))
        hrv = float(metadata.get("hrv", "50"))  # 心率变异性
        eda = float(metadata.get("eda", "2"))  # 皮肤电导率
        
        scores = {
            "愤怒": 0.0,
            "快乐": 0.0,
            "忧郁": 0.0,
            "恐惧": 0.0,
            "平静": 0.0
        }
        
        # 基于生理指标的简单规则
        if heart_rate > 90 and eda > 5:  # 高心率高皮电
            if hrv < 30:  # 低心率变异性
                scores["愤怒"] = 0.8
            else:
                scores["快乐"] = 0.7
        elif heart_rate < 60 and eda < 1:  # 低心率低皮电
            scores["忧郁"] = 0.7
        elif heart_rate > 85 and hrv < 20:  # 高心率低变异性
            scores["恐惧"] = 0.8
        elif hrv > 60 and eda < 3:  # 高变异性适中皮电
            scores["平静"] = 0.9
        
        return scores
    
    def _update_emotion_scores(self, current_scores: Dict[str, float], 
                              new_scores: Dict[str, float], weight: float = 1.0) -> None:
        """更新累计的情绪得分"""
        for emotion, score in new_scores.items():
            if emotion in current_scores:
                current_scores[emotion] += score * weight
            else:
                current_scores[emotion] = score * weight
    
    def _determine_emotional_tendency(self, scores: Dict[str, float], user_id: str) -> str:
        """确定情绪趋势"""
        # TODO: 实现实际的情绪趋势分析逻辑
        # 这里需要历史情绪数据来对比，示例仅返回固定值
        
        # 实际实现应该查询用户历史情绪数据并进行比较
        # 由于缺少历史数据，这里假设一个结果
        
        # 将现代情绪映射到中医五志
        tcm_emotions = {
            "愤怒": "怒",
            "快乐": "喜",
            "忧郁": "忧",
            "恐惧": "恐",
            "平静": "平和"
        }
        
        # 检查是否有极端情绪
        max_score = max(scores.values()) if scores else 0
        if max_score > 0.7:
            return "fluctuating"  # 情绪波动大
        elif "平静" in scores and scores["平静"] > 0.5:
            return "improving"  # 趋于平静
        else:
            return "stable"  # 相对稳定
    
    def _analyze_health_impact(self, scores: Dict[str, float], 
                             primary_emotion: str, user_id: str) -> Dict[str, Any]:
        """分析情绪对健康的影响"""
        # 将现代情绪映射到中医五志
        emotion_mapping = {
            "愤怒": "怒",
            "快乐": "喜",
            "烦躁": "怒",
            "忧郁": "忧",
            "悲伤": "悲",
            "担忧": "思",
            "恐惧": "恐",
            "惊吓": "惊",
            "平静": "平和"
        }
        
        # 转换为中医情志分类
        tcm_emotion = emotion_mapping.get(primary_emotion, "平和")
        
        # 获取对应的中医理论解读
        tcm_info = self.tcm_emotion_mappings.get(tcm_emotion, {})
        
        # 构建健康影响分析
        health_impact = {
            "affected_systems": [],
            "tcm_interpretation": "",
            "severity": 0.0
        }
        
        if tcm_info:
            organ = tcm_info.get("organ", "")
            if organ:
                health_impact["affected_systems"].append(f"{organ}系统")
            
            # 根据情绪强度确定影响严重程度
            emotion_score = scores.get(primary_emotion, 0)
            health_impact["severity"] = min(1.0, emotion_score * 1.2)  # 稍微放大影响
            
            # 生成中医解读
            if emotion_score > 0.7:
                health_impact["tcm_interpretation"] = f"{tcm_emotion}气太过，可能导致{organ}气郁结"
                health_impact["severity"] = 0.8
            elif emotion_score > 0.4:
                health_impact["tcm_interpretation"] = f"{tcm_emotion}气偏盛，{organ}功能可能受到影响"
                health_impact["severity"] = 0.5
            else:
                health_impact["tcm_interpretation"] = f"{tcm_emotion}气基本平和，对{organ}影响轻微"
                health_impact["severity"] = 0.2
        
        return health_impact
    
    def _generate_intervention_suggestions(self, scores: Dict[str, float], 
                                        primary_emotion: str, 
                                        health_impact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成情绪干预建议"""
        suggestions = []
        
        # 情绪到中医五志的映射
        emotion_to_tcm = {
            "愤怒": "怒",
            "快乐": "喜", 
            "忧郁": "忧",
            "恐惧": "恐",
            "悲伤": "悲",
            "担忧": "思",
            "惊吓": "惊"
        }
        
        tcm_emotion = emotion_to_tcm.get(primary_emotion, "平和")
        severity = health_impact.get("severity", 0)
        
        # 获取相应情绪的干预策略
        strategies = self.intervention_strategies.get(tcm_emotion, [])
        
        # 根据情绪严重程度筛选合适的干预策略
        if severity > 0.7:  # 情绪强烈
            # 选择效果最好的策略
            strategies = sorted(strategies, key=lambda x: x.get("effectiveness", 0), reverse=True)
            if strategies:
                suggestions.append({
                    "intervention_type": strategies[0].get("type", ""),
                    "description": strategies[0].get("name", "") + "：" + strategies[0].get("description", ""),
                    "estimated_effectiveness": strategies[0].get("effectiveness", 0.5),
                    "is_urgent": True
                })
                
                # 再添加一个辅助策略
                if len(strategies) > 1:
                    suggestions.append({
                        "intervention_type": strategies[1].get("type", ""),
                        "description": strategies[1].get("name", "") + "：" + strategies[1].get("description", ""),
                        "estimated_effectiveness": strategies[1].get("effectiveness", 0.5),
                        "is_urgent": False
                    })
        elif severity > 0.4:  # 中等情绪
            # 选择均衡的策略
            for strategy in strategies[:2]:  # 最多两个建议
                suggestions.append({
                    "intervention_type": strategy.get("type", ""),
                    "description": strategy.get("name", "") + "：" + strategy.get("description", ""),
                    "estimated_effectiveness": strategy.get("effectiveness", 0.5),
                    "is_urgent": False
                })
        else:  # 轻微情绪
            # 一般维持策略
            if strategies:
                suggestions.append({
                    "intervention_type": strategies[0].get("type", ""),
                    "description": strategies[0].get("name", "") + "：" + strategy.get("description", ""),
                    "estimated_effectiveness": strategies[0].get("effectiveness", 0.5) * 0.8,  # 降低期望
                    "is_urgent": False
                })
        
        # 如果没有针对特定情绪的建议，提供通用建议
        if not suggestions:
            suggestions.append({
                "intervention_type": "general",
                "description": "平和心态调理：保持规律作息，适当运动，平衡饮食，保持心情愉悦",
                "estimated_effectiveness": 0.6,
                "is_urgent": False
            })
        
        return suggestions 