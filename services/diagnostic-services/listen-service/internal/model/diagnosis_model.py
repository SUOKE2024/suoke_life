#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
闻诊诊断结果模型
"""
import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class DiagnosticFeature:
    """诊断特征"""
    feature_name: str
    value: str
    confidence: float = 0.8
    category: str = "listen"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "feature_name": self.feature_name,
            "value": self.value,
            "confidence": self.confidence,
            "category": self.category
        }

@dataclass
class ListenDiagnosisResult:
    """闻诊诊断结果"""
    user_id: str
    session_id: str
    features: List[DiagnosticFeature] = field(default_factory=list)
    tcm_patterns: Dict[str, float] = field(default_factory=dict)
    constitution_relevance: Dict[str, float] = field(default_factory=dict)
    analysis_summary: str = ""
    confidence: float = 0.75
    timestamp: int = field(default_factory=lambda: int(time.time()))
    diagnosis_id: str = field(default_factory=lambda: f"listen_{uuid.uuid4().hex}")
    
    def add_feature(self, feature: DiagnosticFeature) -> None:
        """添加诊断特征"""
        self.features.append(feature)
    
    def add_tcm_pattern(self, pattern_name: str, relevance: float) -> None:
        """添加中医证型相关性"""
        self.tcm_patterns[pattern_name] = min(max(relevance, 0.0), 1.0)
    
    def add_constitution_relevance(self, constitution: str, relevance: float) -> None:
        """添加体质相关性"""
        self.constitution_relevance[constitution] = min(max(relevance, 0.0), 1.0)
    
    def set_analysis_summary(self, summary: str) -> None:
        """设置分析总结"""
        self.analysis_summary = summary
    
    def set_confidence(self, confidence: float) -> None:
        """设置置信度"""
        self.confidence = min(max(confidence, 0.0), 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "diagnosis_id": self.diagnosis_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "features": [feature.to_dict() for feature in self.features],
            "tcm_patterns": self.tcm_patterns,
            "constitution_relevance": self.constitution_relevance,
            "analysis_summary": self.analysis_summary,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListenDiagnosisResult':
        """从字典创建对象"""
        result = cls(
            user_id=data.get("user_id", ""),
            session_id=data.get("session_id", ""),
            analysis_summary=data.get("analysis_summary", ""),
            confidence=data.get("confidence", 0.75),
            timestamp=data.get("timestamp", int(time.time())),
            diagnosis_id=data.get("diagnosis_id", f"listen_{uuid.uuid4().hex}")
        )
        
        # 添加特征
        for feature_data in data.get("features", []):
            result.add_feature(DiagnosticFeature(
                feature_name=feature_data.get("feature_name", ""),
                value=feature_data.get("value", ""),
                confidence=feature_data.get("confidence", 0.8),
                category=feature_data.get("category", "listen")
            ))
        
        # 添加证型相关性
        for pattern, value in data.get("tcm_patterns", {}).items():
            result.add_tcm_pattern(pattern, value)
        
        # 添加体质相关性
        for constitution, value in data.get("constitution_relevance", {}).items():
            result.add_constitution_relevance(constitution, value)
        
        return result 