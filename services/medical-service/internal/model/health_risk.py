#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from enum import Enum


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


@dataclass
class DiseaseRisk:
    """疾病风险"""
    disease_name: str
    risk_score: int  # 0-100
    risk_level: RiskLevel
    risk_factors: List[str] = field(default_factory=list)
    preventive_measures: List[str] = field(default_factory=list)


@dataclass
class ConstitutionRisk:
    """体质风险（TCM视角）"""
    constitution_type: str
    imbalances: List[str] = field(default_factory=list)
    vulnerable_systems: List[str] = field(default_factory=list)
    protective_measures: List[str] = field(default_factory=list)


@dataclass
class HealthRiskAssessment:
    """健康风险评估"""
    id: str
    user_id: str
    assessment_date: datetime
    overall_risk_score: int  # 0-100
    risk_level: RiskLevel
    disease_risks: List[DiseaseRisk] = field(default_factory=list)
    constitution_risk: Optional[ConstitutionRisk] = None
    prevention_recommendations: List[str] = field(default_factory=list)
    lifestyle_recommendations: List[str] = field(default_factory=list)
    recommended_screenings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, user_id: str, overall_risk_score: int, 
               risk_level: RiskLevel) -> 'HealthRiskAssessment':
        """创建新的健康风险评估"""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            assessment_date=now,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            created_at=now
        )
    
    def add_disease_risk(self, disease_risk: DiseaseRisk) -> None:
        """添加疾病风险"""
        self.disease_risks.append(disease_risk)
    
    def update_constitution_risk(self, constitution_risk: ConstitutionRisk) -> None:
        """更新体质风险"""
        self.constitution_risk = constitution_risk
    
    def add_prevention_recommendation(self, recommendation: str) -> None:
        """添加预防建议"""
        self.prevention_recommendations.append(recommendation)
    
    def add_lifestyle_recommendation(self, recommendation: str) -> None:
        """添加生活方式建议"""
        self.lifestyle_recommendations.append(recommendation)
    
    def add_recommended_screening(self, screening: str) -> None:
        """添加建议筛查"""
        self.recommended_screenings.append(screening)


@dataclass
class HealthRiskAssessmentRequest:
    """健康风险评估请求"""
    id: str
    user_id: str
    health_data: Dict[str, str] = field(default_factory=dict)
    family_history: List[str] = field(default_factory=list)
    lifestyle_factors: Dict[str, str] = field(default_factory=dict)
    environmental_factors: List[str] = field(default_factory=list)
    include_genetic_analysis: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, user_id: str, health_data: Optional[Dict[str, str]] = None,
               family_history: Optional[List[str]] = None, 
               lifestyle_factors: Optional[Dict[str, str]] = None,
               environmental_factors: Optional[List[str]] = None,
               include_genetic_analysis: bool = False) -> 'HealthRiskAssessmentRequest':
        """创建健康风险评估请求"""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            health_data=health_data or {},
            family_history=family_history or [],
            lifestyle_factors=lifestyle_factors or {},
            environmental_factors=environmental_factors or [],
            include_genetic_analysis=include_genetic_analysis
        ) 