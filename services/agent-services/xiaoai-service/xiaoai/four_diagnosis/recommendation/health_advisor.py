#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康建议生成器
基于辨证结果生成个性化健康建议
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class HealthRecommendation:
    """健康建议数据类"""
    category: str  # 建议类别
    content: str  # 建议内容
    priority: int  # 优先级，1-5，5最高
    evidence: List[str] = field(default_factory=list)  # 支持该建议的依据
    references: List[str] = field(default_factory=list)  # 参考来源

class HealthAdvisor:
    """
    健康建议生成器
    基于辨证分析结果生成个性化健康建议
    """
    
    # 建议类别
    CATEGORY_DIET = "diet"  # 饮食调养
    CATEGORY_LIFESTYLE = "lifestyle"  # 起居调养
    CATEGORY_EXERCISE = "exercise"  # 运动调养
    CATEGORY_EMOTION = "emotion"  # 情志调养
    CATEGORY_ACUPOINT = "acupoint"  # 穴位保健
    CATEGORY_PREVENTION = "prevention"  # 预防保健
    CATEGORY_MEDICAL = "medical"  # 医疗建议
    
    def __init__(self, config: Dict = None):
        """
        初始化健康建议生成器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 建议数量配置
        self.max_recommendations = self.config.get("max_recommendations", 10)
        self.min_confidence = self.config.get("min_confidence", 0.6)
        
        # 按类别的建议数量
        self.category_limits = {
            self.CATEGORY_DIET: self.config.get("category_limits.diet", 3),
            self.CATEGORY_LIFESTYLE: self.config.get("category_limits.lifestyle", 2),
            self.CATEGORY_EXERCISE: self.config.get("category_limits.exercise", 2),
            self.CATEGORY_EMOTION: self.config.get("category_limits.emotion", 2),
            self.CATEGORY_ACUPOINT: self.config.get("category_limits.acupoint", 1),
            self.CATEGORY_PREVENTION: self.config.get("category_limits.prevention", 1),
            self.CATEGORY_MEDICAL: self.config.get("category_limits.medical", 1)
        }
        
        # 加载知识库
        self.recommendation_knowledge = self._load_recommendation_knowledge()
        
        logger.info("健康建议生成器初始化完成")
    
    def _load_recommendation_knowledge(self) -> Dict[str, Dict]:
        """加载健康建议知识库"""
        # 实际应用中从数据库或知识库加载
        # 这里使用示例数据
        knowledge = {
            # 饮食建议
            "脾胃湿热饮食": {
                "category": self.CATEGORY_DIET,
                "target_syndromes": ["脾胃湿热"],
                "target_constitutions": ["湿热质"],
                "recommendations": [
                    {
                        "content": "饮食宜清淡，少食辛辣、油腻、煎炸食物",
                        "priority": 5,
                        "references": ["《中医饮食营养学》"]
                    },
                    {
                        "content": "适量食用薏米、赤小豆、冬瓜、苦瓜、黄瓜等利湿食物",
                        "priority": 4,
                        "references": ["《中医饮食疗法》"]
                    },
                    {
                        "content": "可选用山楂、决明子、白茅根等泡水代茶饮",
                        "priority": 3,
                        "references": ["《中医四季养生学》"]
                    }
                ]
            },
            "肝气郁结饮食": {
                "category": self.CATEGORY_DIET,
                "target_syndromes": ["肝气郁结"],
                "target_constitutions": ["气郁质"],
                "recommendations": [
                    {
                        "content": "饮食宜清淡，忌食辛辣刺激、煎炸食物",
                        "priority": 4,
                        "references": ["《中医食疗与养生》"]
                    },
                    {
                        "content": "多食用柑橘、佛手、玫瑰花、白萝卜等具有疏肝理气功效的食材",
                        "priority": 4,
                        "references": ["《中医饮食保健学》"]
                    }
                ]
            },
            "气虚饮食": {
                "category": self.CATEGORY_DIET,
                "target_syndromes": ["气虚", "脾气虚", "肺气虚"],
                "target_constitutions": ["气虚质"],
                "recommendations": [
                    {
                        "content": "饮食宜温热，少食生冷；多食用山药、大枣、小米、糯米等健脾益气食物",
                        "priority": 5,
                        "references": ["《中医饮食养生学》"]
                    },
                    {
                        "content": "适量食用鸡肉、羊肉、牛肉等具有补气功效的食材",
                        "priority": 4,
                        "references": ["《中医饮食调养学》"]
                    }
                ]
            },
            
            # 起居建议
            "调畅情志": {
                "category": self.CATEGORY_LIFESTYLE,
                "target_syndromes": ["肝气郁结"],
                "target_constitutions": ["气郁质"],
                "recommendations": [
                    {
                        "content": "保持规律作息，早睡早起，避免熬夜",
                        "priority": 4,
                        "references": ["《中医养生学》"]
                    },
                    {
                        "content": "注意调畅情志，保持心情舒畅，避免情绪波动过大",
                        "priority": 5,
                        "references": ["《黄帝内经·素问》"]
                    }
                ]
            },
            "湿热起居": {
                "category": self.CATEGORY_LIFESTYLE,
                "target_syndromes": ["脾胃湿热"],
                "target_constitutions": ["湿热质"],
                "recommendations": [
                    {
                        "content": "注意环境干燥通风，避免潮湿环境",
                        "priority": 4,
                        "references": ["《中医养生学》"]
                    },
                    {
                        "content": "保持充足睡眠，避免熬夜",
                        "priority": 3,
                        "references": ["《黄帝内经·素问》"]
                    }
                ]
            },
            
            # 运动建议
            "气虚运动": {
                "category": self.CATEGORY_EXERCISE,
                "target_syndromes": ["气虚", "脾气虚"],
                "target_constitutions": ["气虚质"],
                "recommendations": [
                    {
                        "content": "选择缓和的运动，如八段锦、太极拳、慢走等，避免剧烈运动",
                        "priority": 4,
                        "references": ["《中医运动养生学》"]
                    },
                    {
                        "content": "运动量宜小勿大，注意运动后及时休息",
                        "priority": 4,
                        "references": ["《中医运动疗法》"]
                    }
                ]
            },
            "肝郁运动": {
                "category": self.CATEGORY_EXERCISE,
                "target_syndromes": ["肝气郁结"],
                "target_constitutions": ["气郁质"],
                "recommendations": [
                    {
                        "content": "适当进行有氧运动，如快走、慢跑、游泳等，有助于疏肝解郁",
                        "priority": 4,
                        "references": ["《中医运动养生学》"]
                    },
                    {
                        "content": "可尝试呼吸运动，如腹式呼吸，帮助调节情绪",
                        "priority": 3,
                        "references": ["《中医情志养生学》"]
                    }
                ]
            },
            
            # 情志调养
            "肝郁情志": {
                "category": self.CATEGORY_EMOTION,
                "target_syndromes": ["肝气郁结"],
                "target_constitutions": ["气郁质"],
                "recommendations": [
                    {
                        "content": "保持心情舒畅，避免情绪抑郁、焦虑",
                        "priority": 5,
                        "references": ["《中医心理学》"]
                    },
                    {
                        "content": "学习简单的冥想或放松技巧，如深呼吸、肌肉放松等",
                        "priority": 4,
                        "references": ["《中医心身健康学》"]
                    }
                ]
            },
            "心脾情志": {
                "category": self.CATEGORY_EMOTION,
                "target_syndromes": ["心脾两虚"],
                "target_constitutions": ["气虚质"],
                "recommendations": [
                    {
                        "content": "保持情绪稳定，避免过度思虑、忧愁",
                        "priority": 4,
                        "references": ["《中医情志养生学》"]
                    },
                    {
                        "content": "增加社交活动，避免孤独",
                        "priority": 3,
                        "references": ["《中医心理调节学》"]
                    }
                ]
            },
            
            # 穴位保健
            "肝郁穴位": {
                "category": self.CATEGORY_ACUPOINT,
                "target_syndromes": ["肝气郁结"],
                "target_constitutions": ["气郁质"],
                "recommendations": [
                    {
                        "content": "按摩太冲穴（位于足背第一、二跖骨结合部前方凹陷处），每日两次，每次3-5分钟，有助于疏肝解郁",
                        "priority": 4,
                        "references": ["《中医穴位养生学》"]
                    }
                ]
            },
            "脾胃穴位": {
                "category": self.CATEGORY_ACUPOINT,
                "target_syndromes": ["脾胃湿热", "脾气虚"],
                "target_constitutions": ["湿热质", "气虚质"],
                "recommendations": [
                    {
                        "content": "按摩足三里穴（外膝眼下三寸，胫骨外侧一横指处），每日两次，每次5分钟，有助于健脾益气",
                        "priority": 4,
                        "references": ["《中医穴位保健指南》"]
                    }
                ]
            },
            
            # 预防保健
            "一般预防": {
                "category": self.CATEGORY_PREVENTION,
                "target_syndromes": [],  # 通用建议
                "target_constitutions": [],
                "recommendations": [
                    {
                        "content": "定期进行健康检查，建立健康档案",
                        "priority": 3,
                        "references": ["《预防医学》"]
                    },
                    {
                        "content": "保持良好的个人卫生习惯，勤洗手",
                        "priority": 3,
                        "references": ["《预防医学》"]
                    }
                ]
            },
            
            # 医疗建议
            "就医建议": {
                "category": self.CATEGORY_MEDICAL,
                "target_syndromes": [],  # 通用建议
                "target_constitutions": [],
                "recommendations": [
                    {
                        "content": "如症状持续或加重，请及时就医咨询专业医生",
                        "priority": 5,
                        "references": ["《临床医学》"]
                    }
                ]
            }
        }
        
        return knowledge
    
    def generate_recommendations(self, diagnosis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成健康建议
        
        Args:
            diagnosis_data: 辨证分析结果
            
        Returns:
            Dict: 健康建议列表
        """
        start_time = time.time()
        
        try:
            # 提取证候和体质信息
            syndromes = diagnosis_data.get("syndromes", [])
            constitution = diagnosis_data.get("constitution", None)
            
            # 如果缺少必要信息，返回通用建议
            if not syndromes and not constitution:
                logger.warning("无辨证或体质信息，返回通用健康建议")
                return self._generate_general_recommendations()
            
            # 提取证候和体质名称
            syndrome_names = [s["name"] for s in syndromes]
            constitution_name = constitution["name"] if constitution else None
            
            # 生成针对性建议
            recommendations = self._generate_targeted_recommendations(
                syndrome_names, constitution_name
            )
            
            # 添加通用建议
            general_recs = self._generate_general_recommendations()["recommendations"]
            recommendations["recommendations"].extend(general_recs)
            
            # 按优先级排序并限制数量
            recommendations["recommendations"].sort(key=lambda x: x["priority"], reverse=True)
            recommendations["recommendations"] = recommendations["recommendations"][:self.max_recommendations]
            
            # 添加处理时间
            recommendations["processing_time_ms"] = int((time.time() - start_time) * 1000)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成健康建议失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": [],
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def _generate_targeted_recommendations(self, syndrome_names: List[str], 
                                       constitution_name: Optional[str]) -> Dict[str, Any]:
        """生成针对性健康建议"""
        # 按类别收集建议
        category_recommendations = {
            category: [] for category in self.category_limits.keys()
        }
        
        # 遍历知识库，匹配证候和体质
        for rec_key, rec_data in self.recommendation_knowledge.items():
            category = rec_data["category"]
            target_syndromes = rec_data["target_syndromes"]
            target_constitutions = rec_data["target_constitutions"]
            
            # 检查是否匹配当前证候或体质
            syndrome_match = not target_syndromes or any(s in syndrome_names for s in target_syndromes)
            constitution_match = not target_constitutions or (constitution_name and constitution_name in target_constitutions)
            
            # 如果匹配，添加建议
            if syndrome_match or constitution_match:
                for rec in rec_data["recommendations"]:
                    # 构建建议对象
                    recommendation = {
                        "category": category,
                        "content": rec["content"],
                        "priority": rec["priority"],
                        "evidence": []
                    }
                    
                    # 添加证据
                    if syndrome_match and target_syndromes:
                        matched_syndromes = [s for s in target_syndromes if s in syndrome_names]
                        if matched_syndromes:
                            recommendation["evidence"].extend([f"证候: {s}" for s in matched_syndromes])
                    
                    if constitution_match and constitution_name:
                        recommendation["evidence"].append(f"体质: {constitution_name}")
                    
                    # 添加参考来源
                    if "references" in rec:
                        recommendation["references"] = rec["references"]
                    
                    # 添加到相应类别
                    category_recommendations[category].append(recommendation)
        
        # 整合所有建议，控制每个类别的数量
        all_recommendations = []
        for category, recs in category_recommendations.items():
            # 按优先级排序
            recs.sort(key=lambda x: x["priority"], reverse=True)
            # 限制数量
            limit = self.category_limits.get(category, 2)
            all_recommendations.extend(recs[:limit])
        
        return {
            "success": True,
            "recommendations": all_recommendations
        }
    
    def _generate_general_recommendations(self) -> Dict[str, Any]:
        """生成通用健康建议"""
        general_recommendations = []
        
        # 添加预防保健建议
        if "一般预防" in self.recommendation_knowledge:
            for rec in self.recommendation_knowledge["一般预防"]["recommendations"]:
                general_recommendations.append({
                    "category": self.CATEGORY_PREVENTION,
                    "content": rec["content"],
                    "priority": rec["priority"],
                    "evidence": ["通用建议"],
                    "references": rec.get("references", [])
                })
        
        # 添加医疗建议
        if "就医建议" in self.recommendation_knowledge:
            for rec in self.recommendation_knowledge["就医建议"]["recommendations"]:
                general_recommendations.append({
                    "category": self.CATEGORY_MEDICAL,
                    "content": rec["content"],
                    "priority": rec["priority"],
                    "evidence": ["通用建议"],
                    "references": rec.get("references", [])
                })
        
        return {
            "success": True,
            "recommendations": general_recommendations
        } 