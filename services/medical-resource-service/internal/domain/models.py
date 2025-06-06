"""
models - 索克生活项目模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

"""
医疗资源微服务领域模型定义
"""



class ResourceType(Enum):
    """资源类型"""

    DOCTOR = "doctor"
    FACILITY = "facility"
    EQUIPMENT = "equipment"
    MEDICINE = "medicine"


# ConstitutionType removed - no longer using TCM constitution analysis


class AppointmentStatus(Enum):
    """预约状态"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class UrgencyLevel(Enum):
    """紧急程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


class ResourceStatus(Enum):
    """资源状态"""

    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


@dataclass
class Location:
    """地理位置"""

    address: str
    latitude: float
    longitude: float
    city: str
    province: str
    country: str = "中国"


@dataclass
class TimeSlot:
    """时间段"""

    start_time: datetime
    end_time: datetime
    available: bool = True
    booked_by: Optional[str] = None  # 预约用户ID


@dataclass
class Schedule:
    """排班表"""

    available_slots: List[TimeSlot] = field(default_factory=list)
    booked_slots: List[TimeSlot] = field(default_factory=list)

    def add_available_slot(self, start_time: datetime, end_time: datetime):
        """添加可用时间段"""
        slot = TimeSlot(start_time=start_time, end_time=end_time, available=True)
        self.available_slots.append(slot)

    def book_slot(self, start_time: datetime, end_time: datetime, user_id: str) -> bool:
        """预约时间段"""
        for slot in self.available_slots:
            if (
                slot.start_time <= start_time < slot.end_time
                and slot.start_time < end_time <= slot.end_time
                and slot.available
            ):

                # 创建预约时间段
                booked_slot = TimeSlot(
                    start_time=start_time,
                    end_time=end_time,
                    available=False,
                    booked_by=user_id,
                )
                self.booked_slots.append(booked_slot)

                # 更新可用时间段
                slot.available = False
                return True
        return False

    def get_available_slots(self, date: datetime) -> List[TimeSlot]:
        """获取指定日期的可用时间段"""
        return [
            slot
            for slot in self.available_slots
            if slot.start_time.date() == date.date() and slot.available
        ]


@dataclass
class Resource:
    """医疗资源基类"""

    id: str = field(default_factory=lambda: str(uuid4()))
    type: ResourceType = ResourceType.DOCTOR
    name: str = ""
    description: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    available: bool = True
    status: ResourceStatus = ResourceStatus.AVAILABLE
    location: Optional[Location] = None
    schedule: Schedule = field(default_factory=Schedule)
    specialties: List[str] = field(default_factory=list)
    rating: float = 0.0
    total_reviews: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_rating(self, new_rating: float):
        """更新评分"""
        total_score = self.rating * self.total_reviews + new_rating
        self.total_reviews += 1
        self.rating = total_score / self.total_reviews
        self.updated_at = datetime.now()

    def add_specialty(self, specialty: str):
        """添加专长"""
        if specialty not in self.specialties:
            self.specialties.append(specialty)
            self.updated_at = datetime.now()


@dataclass
class Doctor(Resource):
    """医生资源"""

    title: str = ""  # 职称
    years_experience: int = 0
    hospital: str = ""
    department: str = ""
    total_patients: int = 0
    certifications: List[str] = field(default_factory=list)
    bio: str = ""
    # TCM-related fields removed
    consultation_fee: float = 0.0
    languages: List[str] = field(default_factory=lambda: ["中文"])

    def __post_init__(self):
        self.type = ResourceType.DOCTOR

    # TCM constitution methods removed


@dataclass
class MedicalFacility(Resource):
    """医疗机构"""

    facility_type: str = ""  # 医院、诊所、体检中心等
    license_number: str = ""
    operating_hours: Dict[str, str] = field(default_factory=dict)
    services: List[str] = field(default_factory=list)
    equipment_list: List[str] = field(default_factory=list)
    bed_count: int = 0
    emergency_service: bool = False
    parking_available: bool = False
    wheelchair_accessible: bool = False

    def __post_init__(self):
        self.type = ResourceType.FACILITY

    def is_open(self, check_time: datetime) -> bool:
        """检查是否营业"""
        day_name = check_time.strftime("%A").lower()
        if day_name in self.operating_hours:
            hours = self.operating_hours[day_name]
            if hours == "closed":
                return False
            # 简单的时间检查逻辑
            return True
        return False


@dataclass
class MedicalEquipment(Resource):
    """医疗设备"""

    equipment_type: str = ""
    model: str = ""
    manufacturer: str = ""
    installation_date: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    max_concurrent_usage: int = 1
    current_usage: int = 0
    calibration_status: str = "valid"

    def __post_init__(self):
        self.type = ResourceType.EQUIPMENT

    def is_available_for_booking(self) -> bool:
        """检查是否可预约"""
        return (
            self.available
            and self.status == ResourceStatus.AVAILABLE
            and self.current_usage < self.max_concurrent_usage
        )

    def book_equipment(self) -> bool:
        """预约设备"""
        if self.is_available_for_booking():
            self.current_usage += 1
            if self.current_usage >= self.max_concurrent_usage:
                self.status = ResourceStatus.BUSY
            return True
        return False

    def release_equipment(self):
        """释放设备"""
        if self.current_usage > 0:
            self.current_usage -= 1
            if self.current_usage < self.max_concurrent_usage:
                self.status = ResourceStatus.AVAILABLE


@dataclass
class Medicine(Resource):
    """药材资源"""

    medicine_type: str = ""  # 中药、西药
    category: str = ""  # 分类
    origin: str = ""  # 产地
    batch_number: str = ""
    production_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    stock_quantity: int = 0
    unit: str = "克"
    price_per_unit: float = 0.0
    storage_conditions: str = ""
    contraindications: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.type = ResourceType.MEDICINE

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expiry_date:
            return datetime.now() > self.expiry_date
        return False

    def is_in_stock(self, required_quantity: int = 1) -> bool:
        """检查库存是否充足"""
        return self.stock_quantity >= required_quantity

    def consume_stock(self, quantity: int) -> bool:
        """消耗库存"""
        if self.is_in_stock(quantity):
            self.stock_quantity -= quantity
            self.updated_at = datetime.now()
            return True
        return False


@dataclass
class Appointment:
    """预约"""

    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.DOCTOR
    appointment_time: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.PENDING
    notes: str = ""
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    symptoms: str = ""
    # user_constitution field removed
    diagnosis: str = ""
    treatment_plan: str = ""
    prescription: str = ""
    follow_up_date: Optional[datetime] = None
    cost: float = 0.0
    payment_status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def confirm(self):
        """确认预约"""
        self.status = AppointmentStatus.CONFIRMED
        self.updated_at = datetime.now()

    def cancel(self, reason: str = ""):
        """取消预约"""
        self.status = AppointmentStatus.CANCELLED
        if reason:
            self.notes += f"\n取消原因: {reason}"
        self.updated_at = datetime.now()

    def complete(
        self, diagnosis: str = "", treatment_plan: str = "", prescription: str = ""
    ):
        """完成预约"""
        self.status = AppointmentStatus.COMPLETED
        if diagnosis:
            self.diagnosis = diagnosis
        if treatment_plan:
            self.treatment_plan = treatment_plan
        if prescription:
            self.prescription = prescription
        self.updated_at = datetime.now()

    def is_upcoming(self) -> bool:
        """检查是否为即将到来的预约"""
        return (
            self.status in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
            and self.appointment_time > datetime.now()
        )

    def is_overdue(self) -> bool:
        """检查是否过期"""
        return (
            self.status in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
            and self.appointment_time < datetime.now()
        )


@dataclass
class Recommendation:
    """推荐"""

    id: str = field(default_factory=lambda: str(uuid4()))
    resource_type: ResourceType = ResourceType.DOCTOR
    resource_id: str = ""
    title: str = ""
    description: str = ""
    confidence_score: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def is_high_confidence(self) -> bool:
        """检查是否为高置信度推荐"""
        return self.confidence_score >= 0.8


@dataclass
class TreatmentPlan:
    """治疗方案"""

    id: str = field(default_factory=lambda: str(uuid4()))
    patient_id: str = ""
    doctor_id: str = ""
    # constitution_type field removed
    symptoms: List[str] = field(default_factory=list)
    diagnosis: str = ""
    treatment_type: str = ""  # 中医、西医、综合
    treatment_methods: List[str] = field(default_factory=list)
    medications: List[Dict[str, Any]] = field(default_factory=list)
    lifestyle_recommendations: List[str] = field(default_factory=list)
    dietary_recommendations: List[str] = field(default_factory=list)
    exercise_recommendations: List[str] = field(default_factory=list)
    duration_days: int = 0
    follow_up_schedule: List[datetime] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    precautions: List[str] = field(default_factory=list)
    cost_estimate: float = 0.0
    effectiveness_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_medication(
        self, medicine_id: str, dosage: str, frequency: str, duration: str
    ):
        """添加药物"""
        medication = {
            "medicine_id": medicine_id,
            "dosage": dosage,
            "frequency": frequency,
            "duration": duration,
            "added_at": datetime.now().isoformat(),
        }
        self.medications.append(medication)
        self.updated_at = datetime.now()

    def add_follow_up(self, follow_up_date: datetime):
        """添加随访日期"""
        self.follow_up_schedule.append(follow_up_date)
        self.updated_at = datetime.now()


@dataclass
class ResourceUtilization:
    """资源利用率"""

    resource_id: str
    resource_name: str
    resource_type: ResourceType
    date: datetime
    total_capacity: int
    used_capacity: int
    utilization_rate: float
    peak_hours: List[str] = field(default_factory=list)
    average_wait_time: float = 0.0

    @property
    def is_overutilized(self) -> bool:
        """检查是否过度利用"""
        return self.utilization_rate > 0.9

    @property
    def is_underutilized(self) -> bool:
        """检查是否利用不足"""
        return self.utilization_rate < 0.3


@dataclass
class QualityMetrics:
    """质量指标"""

    resource_id: str
    resource_type: ResourceType
    period_start: datetime
    period_end: datetime
    patient_satisfaction: float = 0.0
    treatment_success_rate: float = 0.0
    average_wait_time: float = 0.0
    no_show_rate: float = 0.0
    cancellation_rate: float = 0.0
    complaint_count: int = 0
    compliment_count: int = 0

    @property
    def overall_quality_score(self) -> float:
        """计算综合质量评分"""
        # 简单的加权平均
        weights = {
            "satisfaction": 0.3,
            "success_rate": 0.3,
            "wait_time": 0.2,  # 反向权重
            "reliability": 0.2,  # 基于取消率和缺席率
        }

        reliability_score = 1.0 - (self.no_show_rate + self.cancellation_rate) / 2
        wait_time_score = max(0, 1.0 - self.average_wait_time / 60)  # 假设60分钟为最差

        score = (
            self.patient_satisfaction * weights["satisfaction"]
            + self.treatment_success_rate * weights["success_rate"]
            + wait_time_score * weights["wait_time"]
            + reliability_score * weights["reliability"]
        )

        return min(max(score, 0.0), 1.0)


@dataclass
class HealthProfile:
    """健康档案"""

    user_id: str
    # constitution fields removed
    constitution_confidence: float = 0.0
    chronic_conditions: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    family_history: List[str] = field(default_factory=list)
    lifestyle_factors: Dict[str, Any] = field(default_factory=dict)
    vital_signs: Dict[str, float] = field(default_factory=dict)
    lab_results: Dict[str, Any] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)
    health_goals: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    # update_constitution method removed

    def add_chronic_condition(self, condition: str):
        """添加慢性疾病"""
        if condition not in self.chronic_conditions:
            self.chronic_conditions.append(condition)
            self.last_updated = datetime.now()

    def add_allergy(self, allergy: str):
        """添加过敏信息"""
        if allergy not in self.allergies:
            self.allergies.append(allergy)
            self.last_updated = datetime.now()


# 工厂函数
def create_doctor(
    name: str,
    title: str,
    hospital: str,
    department: str,
    specialties: List[str],
) -> Doctor:
    """创建医生实例"""
    doctor = Doctor(
        name=name,
        title=title,
        hospital=hospital,
        department=department,
        specialties=specialties,
    )
    return doctor


def create_appointment(
    user_id: str,
    resource_id: str,
    appointment_time: datetime,
    duration_minutes: int = 30,
    symptoms: str = "",
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM,
) -> Appointment:
    """创建预约实例"""
    appointment = Appointment(
        user_id=user_id,
        resource_id=resource_id,
        appointment_time=appointment_time,
        duration_minutes=duration_minutes,
        symptoms=symptoms,
        urgency=urgency,
    )
    return appointment


def create_treatment_plan(
    patient_id: str,
    doctor_id: str,
    symptoms: List[str],
    treatment_type: str = "综合",
) -> TreatmentPlan:
    """创建治疗方案实例"""
    plan = TreatmentPlan(
        patient_id=patient_id,
        doctor_id=doctor_id,
        symptoms=symptoms,
        treatment_type=treatment_type,
    )
    return plan
