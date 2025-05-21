#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from enum import Enum


class DiagnosisStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class LookDiagnosis:
    """望诊结果"""
    facial_color: Optional[str] = None
    tongue_diagnosis: Optional[str] = None
    body_shape: Optional[str] = None
    complexion: Optional[str] = None
    abnormal_signs: List[str] = field(default_factory=list)


@dataclass
class ListenSmellDiagnosis:
    """闻诊结果"""
    voice_quality: Optional[str] = None
    breathing_sounds: Optional[str] = None
    odor: Optional[str] = None
    abnormal_sounds: List[str] = field(default_factory=list)


@dataclass
class InquiryDiagnosis:
    """问诊结果"""
    reported_symptoms: List[str] = field(default_factory=list)
    sleep_quality: Optional[str] = None
    diet_habits: Optional[str] = None
    emotional_state: Optional[str] = None
    pain_description: Optional[str] = None
    additional_information: Dict[str, str] = field(default_factory=dict)


@dataclass
class PalpationDiagnosis:
    """切诊结果"""
    pulse_diagnosis: Optional[str] = None
    pulse_qualities: List[str] = field(default_factory=list)
    abdominal_diagnosis: Optional[str] = None
    acupoint_tenderness: Dict[str, str] = field(default_factory=dict)
    other_findings: List[str] = field(default_factory=list)


@dataclass
class TCMDiagnosis:
    """中医诊断结果"""
    look: Optional[LookDiagnosis] = None
    listen_smell: Optional[ListenSmellDiagnosis] = None
    inquiry: Optional[InquiryDiagnosis] = None
    palpation: Optional[PalpationDiagnosis] = None
    pattern_differentiation: List[str] = field(default_factory=list)
    meridian_analysis: List[str] = field(default_factory=list)
    constitution_type: Optional[str] = None
    imbalances: List[str] = field(default_factory=list)


@dataclass
class LabTest:
    """实验室检测结果"""
    test_name: str
    result: str
    unit: str
    reference_range: str
    is_abnormal: bool = False


@dataclass
class WesternDiagnosis:
    """西医诊断结果"""
    possible_conditions: List[str] = field(default_factory=list)
    vital_signs: Dict[str, str] = field(default_factory=dict)
    lab_results: List[LabTest] = field(default_factory=list)
    clinical_analysis: Optional[str] = None
    confidence_score: int = 0  # 0-100
    differential_diagnosis: List[str] = field(default_factory=list)


@dataclass
class DiagnosisResult:
    """诊断结果"""
    id: str
    user_id: str
    diagnosis_time: datetime
    status: DiagnosisStatus
    tcm_diagnosis: Optional[TCMDiagnosis] = None
    western_diagnosis: Optional[WesternDiagnosis] = None
    integrated_diagnosis: Optional[str] = None
    health_advice: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create_pending(cls, user_id: str) -> 'DiagnosisResult':
        """创建待处理的诊断结果"""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            diagnosis_time=now,
            status=DiagnosisStatus.PROCESSING,
            created_at=now
        )
    
    def complete(self, tcm_diagnosis: Optional[TCMDiagnosis] = None,
                 western_diagnosis: Optional[WesternDiagnosis] = None,
                 integrated_diagnosis: Optional[str] = None,
                 health_advice: Optional[List[str]] = None) -> None:
        """完成诊断"""
        self.status = DiagnosisStatus.COMPLETED
        if tcm_diagnosis is not None:
            self.tcm_diagnosis = tcm_diagnosis
        if western_diagnosis is not None:
            self.western_diagnosis = western_diagnosis
        if integrated_diagnosis is not None:
            self.integrated_diagnosis = integrated_diagnosis
        if health_advice is not None:
            self.health_advice = health_advice
    
    def fail(self) -> None:
        """诊断失败"""
        self.status = DiagnosisStatus.FAILED


@dataclass
class DiagnosisRequest:
    """诊断请求"""
    id: str
    user_id: str
    chief_complaint: str
    symptoms: List[str] = field(default_factory=list)
    health_data: Dict[str, str] = field(default_factory=dict)
    diagnostic_methods: List[str] = field(default_factory=list)
    include_western_medicine: bool = True
    include_tcm: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, user_id: str, chief_complaint: str, symptoms: Optional[List[str]] = None,
               health_data: Optional[Dict[str, str]] = None, diagnostic_methods: Optional[List[str]] = None,
               include_western_medicine: bool = True, include_tcm: bool = True) -> 'DiagnosisRequest':
        """创建诊断请求"""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            chief_complaint=chief_complaint,
            symptoms=symptoms or [],
            health_data=health_data or {},
            diagnostic_methods=diagnostic_methods or [],
            include_western_medicine=include_western_medicine,
            include_tcm=include_tcm
        )