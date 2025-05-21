#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医证型模型
定义中医证型相关的数据结构和操作
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class YinYangType(str, Enum):
    """阴阳分类"""
    YIN = "yin"  # 阴证
    YANG = "yang"  # 阳证
    MIXED = "mixed"  # 阴阳错杂
    UNKNOWN = "unknown"  # 未知


class DeficiencyExcessType(str, Enum):
    """虚实分类"""
    DEFICIENCY = "deficiency"  # 虚证
    EXCESS = "excess"  # 实证
    MIXED = "mixed"  # 虚实夹杂
    UNKNOWN = "unknown"  # 未知


class ColdHeatType(str, Enum):
    """寒热分类"""
    COLD = "cold"  # 寒证
    HEAT = "heat"  # 热证
    MIXED = "mixed"  # 寒热错杂
    UNKNOWN = "unknown"  # 未知


class ExteriorInteriorType(str, Enum):
    """表里分类"""
    EXTERIOR = "exterior"  # 表证
    INTERIOR = "interior"  # 里证
    HALF_EXTERIOR_INTERIOR = "half_exterior_interior"  # 半表半里
    UNKNOWN = "unknown"  # 未知


@dataclass
class TCMPattern:
    """中医证型模型"""
    name: str  # 证型名称
    name_zh: Optional[str] = None  # 中文名称
    description: Optional[str] = None  # 证型描述
    categories: Dict[str, Any] = field(default_factory=dict)  # 证型分类
    key_symptoms: List[str] = field(default_factory=list)  # 主症
    secondary_symptoms: List[str] = field(default_factory=list)  # 次症
    tongue_diagnosis: Optional[str] = None  # 舌诊
    pulse_diagnosis: Optional[str] = None  # 脉诊
    treatment_principles: Optional[str] = None  # 治疗原则
    recommended_formulas: List[str] = field(default_factory=list)  # 推荐方剂
    recommended_herbs: List[str] = field(default_factory=list)  # 推荐中草药
    related_patterns: List[str] = field(default_factory=list)  # 相关证型
    confidence: float = 1.0  # 匹配置信度
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "name_zh": self.name_zh,
            "description": self.description,
            "categories": self.categories,
            "key_symptoms": self.key_symptoms,
            "secondary_symptoms": self.secondary_symptoms,
            "tongue_diagnosis": self.tongue_diagnosis,
            "pulse_diagnosis": self.pulse_diagnosis,
            "treatment_principles": self.treatment_principles,
            "recommended_formulas": self.recommended_formulas,
            "recommended_herbs": self.recommended_herbs,
            "related_patterns": self.related_patterns,
            "confidence": self.confidence,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TCMPattern':
        """从字典创建证型对象"""
        return cls(
            name=data["name"],
            name_zh=data.get("name_zh"),
            description=data.get("description"),
            categories=data.get("categories", {}),
            key_symptoms=data.get("key_symptoms", []),
            secondary_symptoms=data.get("secondary_symptoms", []),
            tongue_diagnosis=data.get("tongue_diagnosis"),
            pulse_diagnosis=data.get("pulse_diagnosis"),
            treatment_principles=data.get("treatment_principles"),
            recommended_formulas=data.get("recommended_formulas", []),
            recommended_herbs=data.get("recommended_herbs", []),
            related_patterns=data.get("related_patterns", []),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {})
        )
    
    @staticmethod
    def from_llm_response(llm_response: Dict[str, Any]) -> List['TCMPattern']:
        """
        从LLM响应中提取结构化证型
        
        Args:
            llm_response: LLM响应的结构化数据
            
        Returns:
            结构化证型列表
        """
        patterns = []
        
        for pattern_data in llm_response.get("patterns", []):
            try:
                # 创建TCMPattern对象
                pattern = TCMPattern.from_dict(pattern_data)
                patterns.append(pattern)
            except (KeyError, ValueError) as e:
                # 处理错误，跳过无效数据
                print(f"提取证型时出错: {e}, 数据: {pattern_data}")
                continue
                
        return patterns


@dataclass
class DiagnosisResult:
    """诊断结果"""
    primary_patterns: List[TCMPattern] = field(default_factory=list)  # 主要证型
    secondary_patterns: List[TCMPattern] = field(default_factory=list)  # 次要证型
    analysis: Optional[str] = None  # 辨证分析
    confidence: float = 0.0  # 整体置信度
    symptoms_mapping: Dict[str, List[str]] = field(default_factory=dict)  # 症状-证型映射
    recommendations: Dict[str, Any] = field(default_factory=dict)  # 建议
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "primary_patterns": [pattern.to_dict() for pattern in self.primary_patterns],
            "secondary_patterns": [pattern.to_dict() for pattern in self.secondary_patterns],
            "analysis": self.analysis,
            "confidence": self.confidence,
            "symptoms_mapping": self.symptoms_mapping,
            "recommendations": self.recommendations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagnosisResult':
        """从字典创建诊断结果对象"""
        primary_patterns = [
            TCMPattern.from_dict(pattern_data)
            for pattern_data in data.get("primary_patterns", [])
        ]
        
        secondary_patterns = [
            TCMPattern.from_dict(pattern_data)
            for pattern_data in data.get("secondary_patterns", [])
        ]
        
        return cls(
            primary_patterns=primary_patterns,
            secondary_patterns=secondary_patterns,
            analysis=data.get("analysis"),
            confidence=data.get("confidence", 0.0),
            symptoms_mapping=data.get("symptoms_mapping", {}),
            recommendations=data.get("recommendations", {})
        ) 