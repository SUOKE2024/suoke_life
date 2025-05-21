#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from enum import Enum


class TreatmentPlanStatus(str, Enum):
    """治疗方案状态"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


@dataclass
class HerbalComponent:
    """中药成分"""
    herb_name: str
    quantity: str
    unit: str
    preparation: Optional[str] = None  # 例如：生用、炒用等


@dataclass
class HerbalPrescription:
    """中药处方"""
    name: str
    components: List[HerbalComponent] = field(default_factory=list)
    preparation_method: Optional[str] = None
    dosage_instruction: Optional[str] = None
    duration: Optional[str] = None
    precautions: List[str] = field(default_factory=list)


@dataclass
class AcupunctureTreatment:
    """针灸治疗"""
    acupoints: List[str] = field(default_factory=list)
    technique: Optional[str] = None
    duration: Optional[str] = None
    frequency: Optional[str] = None
    total_sessions: int = 0


@dataclass
class TuinaTreatment:
    """推拿治疗"""
    techniques: List[str] = field(default_factory=list)
    target_areas: List[str] = field(default_factory=list)
    duration: Optional[str] = None
    frequency: Optional[str] = None
    total_sessions: int = 0


@dataclass
class OtherTCMTherapy:
    """其他中医疗法"""
    therapy_name: str
    description: Optional[str] = None
    application_method: Optional[str] = None
    duration: Optional[str] = None
    frequency: Optional[str] = None


@dataclass
class TCMTreatment:
    """中医治疗方案"""
    herbal_prescriptions: List[HerbalPrescription] = field(default_factory=list)
    acupuncture_treatments: List[AcupunctureTreatment] = field(default_factory=list)
    tuina_treatments: List[TuinaTreatment] = field(default_factory=list)
    other_therapies: List[OtherTCMTherapy] = field(default_factory=list)


@dataclass
class MedicationPrescription:
    """药物处方"""
    medication_name: str
    dosage: str
    route: str  # 口服、静脉注射等
    frequency: str
    duration: str
    side_effects: List[str] = field(default_factory=list)
    precautions: List[str] = field(default_factory=list)


@dataclass
class MedicalProcedure:
    """医疗程序"""
    procedure_name: str
    description: Optional[str] = None
    location: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    preparation: Optional[str] = None
    aftercare: Optional[str] = None


@dataclass
class TestPlan:
    """检测计划"""
    test_name: str
    purpose: Optional[str] = None
    facility: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    preparation: Optional[str] = None


@dataclass
class Referral:
    """转诊推荐"""
    specialist_type: str
    reason: Optional[str] = None
    urgency: str = "ROUTINE"  # "ROUTINE", "URGENT", "EMERGENCY"
    preferred_facility: Optional[str] = None


@dataclass
class WesternTreatment:
    """西医治疗方案"""
    medications: List[MedicationPrescription] = field(default_factory=list)
    procedures: List[MedicalProcedure] = field(default_factory=list)
    tests: List[TestPlan] = field(default_factory=list)
    referrals: List[Referral] = field(default_factory=list)


@dataclass
class DietaryRecommendation:
    """饮食建议"""
    foods_to_consume: List[str] = field(default_factory=list)
    foods_to_avoid: List[str] = field(default_factory=list)
    meal_pattern: Optional[str] = None
    dietary_principles: List[str] = field(default_factory=list)
    recipes: List[str] = field(default_factory=list)


@dataclass
class ExerciseRecommendation:
    """运动建议"""
    exercise_types: List[str] = field(default_factory=list)
    intensity: Optional[str] = None
    duration: Optional[str] = None
    frequency: Optional[str] = None
    precautions: List[str] = field(default_factory=list)


@dataclass
class SleepRecommendation:
    """睡眠建议"""
    recommended_sleep_duration: Optional[str] = None
    sleep_hygiene_tips: List[str] = field(default_factory=list)
    bedtime_routine: Optional[str] = None


@dataclass
class StressManagement:
    """压力管理"""
    relaxation_techniques: List[str] = field(default_factory=list)
    mindfulness_practices: List[str] = field(default_factory=list)
    daily_routine_adjustment: Optional[str] = None


@dataclass
class LifestyleAdjustment:
    """生活方式调整"""
    dietary: List[DietaryRecommendation] = field(default_factory=list)
    exercise: Optional[ExerciseRecommendation] = None
    sleep: Optional[SleepRecommendation] = None
    stress_management: Optional[StressManagement] = None
    other_recommendations: List[str] = field(default_factory=list)


@dataclass
class FollowUpAppointment:
    """随访预约"""
    appointment_type: str
    scheduled_time: Optional[datetime] = None
    provider: Optional[str] = None
    purpose: Optional[str] = None


@dataclass
class FollowUpPlan:
    """随访计划"""
    appointments: List[FollowUpAppointment] = field(default_factory=list)
    monitoring_parameters: List[str] = field(default_factory=list)
    self_assessment_guide: Optional[str] = None
    warning_signs: List[str] = field(default_factory=list)


@dataclass
class TreatmentPlan:
    """治疗方案"""
    id: str
    user_id: str
    diagnosis_id: str
    created_at: datetime
    updated_at: datetime
    status: TreatmentPlanStatus
    tcm_treatment: Optional[TCMTreatment] = None
    western_treatment: Optional[WesternTreatment] = None
    lifestyle_adjustment: Optional[LifestyleAdjustment] = None
    follow_up_plan: Optional[FollowUpPlan] = None
    
    @classmethod
    def create(cls, user_id: str, diagnosis_id: str) -> 'TreatmentPlan':
        """创建新的治疗方案"""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            diagnosis_id=diagnosis_id,
            created_at=now,
            updated_at=now,
            status=TreatmentPlanStatus.ACTIVE
        )
    
    def update_status(self, status: TreatmentPlanStatus) -> None:
        """更新治疗方案状态"""
        self.status = status
        self.updated_at = datetime.now()
    
    def update_tcm_treatment(self, tcm_treatment: TCMTreatment) -> None:
        """更新中医治疗方案"""
        self.tcm_treatment = tcm_treatment
        self.updated_at = datetime.now()
    
    def update_western_treatment(self, western_treatment: WesternTreatment) -> None:
        """更新西医治疗方案"""
        self.western_treatment = western_treatment
        self.updated_at = datetime.now()
    
    def update_lifestyle_adjustment(self, lifestyle_adjustment: LifestyleAdjustment) -> None:
        """更新生活方式调整建议"""
        self.lifestyle_adjustment = lifestyle_adjustment
        self.updated_at = datetime.now()
    
    def update_follow_up_plan(self, follow_up_plan: FollowUpPlan) -> None:
        """更新随访计划"""
        self.follow_up_plan = follow_up_plan
        self.updated_at = datetime.now() 