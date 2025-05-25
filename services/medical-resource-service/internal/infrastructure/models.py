"""
数据库模型定义
定义医疗资源服务相关的数据表结构
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text, JSON,
    ForeignKey, Enum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class ConstitutionType(PyEnum):
    """体质类型"""
    BALANCED = "平和质"
    QI_DEFICIENCY = "气虚质"
    YANG_DEFICIENCY = "阳虚质"
    YIN_DEFICIENCY = "阴虚质"
    PHLEGM_DAMPNESS = "痰湿质"
    DAMP_HEAT = "湿热质"
    BLOOD_STASIS = "血瘀质"
    QI_STAGNATION = "气郁质"
    SPECIAL_DIATHESIS = "特禀质"

class ResourceType(PyEnum):
    """资源类型"""
    TCM_DOCTOR = "中医师"
    MODERN_DOCTOR = "现代医生"
    MEDICAL_FACILITY = "医疗机构"
    EQUIPMENT = "医疗设备"
    MEDICINE = "药材"
    AGRICULTURAL_PRODUCT = "农产品"
    WELLNESS_DESTINATION = "养生目的地"
    TREATMENT_PROGRAM = "治疗方案"

class AppointmentStatus(PyEnum):
    """预约状态"""
    PENDING = "待确认"
    CONFIRMED = "已确认"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"
    NO_SHOW = "未到场"

class QualityLevel(PyEnum):
    """质量等级"""
    EXCELLENT = "优秀"
    GOOD = "良好"
    AVERAGE = "一般"
    POOR = "较差"
    UNACCEPTABLE = "不可接受"

# 医疗资源表
class MedicalResource(Base):
    """医疗资源基础表"""
    __tablename__ = "medical_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, comment="资源名称")
    resource_type = Column(Enum(ResourceType), nullable=False, comment="资源类型")
    description = Column(Text, comment="资源描述")
    
    # 基本信息
    location = Column(String(500), comment="位置信息")
    contact_info = Column(JSON, comment="联系信息")
    operating_hours = Column(JSON, comment="营业时间")
    
    # 质量信息
    quality_level = Column(Enum(QualityLevel), default=QualityLevel.AVERAGE, comment="质量等级")
    rating = Column(Float, default=0.0, comment="评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    
    # 可用性
    is_available = Column(Boolean, default=True, comment="是否可用")
    capacity = Column(Integer, comment="容量")
    current_load = Column(Integer, default=0, comment="当前负载")
    
    # 价格信息
    base_price = Column(Float, comment="基础价格")
    price_unit = Column(String(50), comment="价格单位")
    
    # 专业信息
    specialties = Column(JSON, comment="专业领域")
    constitution_suitability = Column(JSON, comment="适合体质")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    appointments = relationship("Appointment", back_populates="resource")
    quality_assessments = relationship("QualityAssessment", back_populates="resource")
    
    __table_args__ = (
        Index('idx_resource_type', 'resource_type'),
        Index('idx_resource_location', 'location'),
        Index('idx_resource_available', 'is_available'),
        Index('idx_resource_quality', 'quality_level'),
    )

# 医生资源表
class DoctorResource(Base):
    """医生资源表"""
    __tablename__ = "doctor_resources"
    
    id = Column(UUID(as_uuid=True), ForeignKey('medical_resources.id'), primary_key=True)
    
    # 医生基本信息
    title = Column(String(100), comment="职称")
    department = Column(String(100), comment="科室")
    hospital = Column(String(200), comment="所属医院")
    
    # 专业信息
    medical_license = Column(String(100), comment="医师执业证号")
    years_of_experience = Column(Integer, comment="从业年限")
    education_background = Column(String(500), comment="教育背景")
    
    # 中医相关
    tcm_specialties = Column(JSON, comment="中医专长")
    famous_tcm_doctor = Column(Boolean, default=False, comment="是否名老中医")
    
    # 预约信息
    appointment_duration = Column(Integer, default=30, comment="预约时长（分钟）")
    max_daily_appointments = Column(Integer, default=20, comment="每日最大预约数")
    advance_booking_days = Column(Integer, default=30, comment="提前预约天数")
    
    # 关系
    resource = relationship("MedicalResource", foreign_keys=[id])

# 预约表
class Appointment(Base):
    """预约表"""
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, comment="用户ID")
    resource_id = Column(UUID(as_uuid=True), ForeignKey('medical_resources.id'), nullable=False)
    
    # 预约信息
    appointment_date = Column(Date, nullable=False, comment="预约日期")
    appointment_time = Column(String(10), nullable=False, comment="预约时间")
    duration_minutes = Column(Integer, default=30, comment="预约时长")
    
    # 状态信息
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, comment="预约状态")
    priority = Column(Integer, default=1, comment="优先级")
    
    # 用户信息
    constitution_type = Column(Enum(ConstitutionType), comment="体质类型")
    symptoms = Column(JSON, comment="症状描述")
    special_requirements = Column(Text, comment="特殊要求")
    
    # 费用信息
    estimated_cost = Column(Float, comment="预估费用")
    actual_cost = Column(Float, comment="实际费用")
    
    # 结果信息
    diagnosis = Column(Text, comment="诊断结果")
    treatment_plan = Column(JSON, comment="治疗方案")
    prescription = Column(JSON, comment="处方信息")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, comment="完成时间")
    
    # 关系
    resource = relationship("MedicalResource", back_populates="appointments")
    quality_assessment = relationship("QualityAssessment", back_populates="appointment", uselist=False)
    
    __table_args__ = (
        Index('idx_appointment_user', 'user_id'),
        Index('idx_appointment_resource', 'resource_id'),
        Index('idx_appointment_date', 'appointment_date'),
        Index('idx_appointment_status', 'status'),
        UniqueConstraint('resource_id', 'appointment_date', 'appointment_time', name='uq_resource_datetime'),
    )

# 质量评估表
class QualityAssessment(Base):
    """质量评估表"""
    __tablename__ = "quality_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey('medical_resources.id'), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey('appointments.id'))
    user_id = Column(UUID(as_uuid=True), nullable=False, comment="评估用户ID")
    
    # 评估维度
    effectiveness_score = Column(Float, comment="效果评分")
    satisfaction_score = Column(Float, comment="满意度评分")
    safety_score = Column(Float, comment="安全性评分")
    cost_effectiveness_score = Column(Float, comment="成本效益评分")
    
    # 综合评分
    overall_score = Column(Float, nullable=False, comment="综合评分")
    quality_level = Column(Enum(QualityLevel), comment="质量等级")
    
    # 详细反馈
    feedback_text = Column(Text, comment="文字反馈")
    improvement_suggestions = Column(Text, comment="改进建议")
    
    # 标签
    tags = Column(JSON, comment="评价标签")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关系
    resource = relationship("MedicalResource", back_populates="quality_assessments")
    appointment = relationship("Appointment", back_populates="quality_assessment")
    
    __table_args__ = (
        Index('idx_quality_resource', 'resource_id'),
        Index('idx_quality_user', 'user_id'),
        Index('idx_quality_score', 'overall_score'),
        Index('idx_quality_level', 'quality_level'),
    )

# 中医知识表
class TCMKnowledge(Base):
    """中医知识表"""
    __tablename__ = "tcm_knowledge"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    title = Column(String(200), nullable=False, comment="标题")
    category = Column(String(100), nullable=False, comment="类别")
    subcategory = Column(String(100), comment="子类别")
    
    # 内容信息
    content = Column(Text, nullable=False, comment="内容")
    summary = Column(Text, comment="摘要")
    keywords = Column(JSON, comment="关键词")
    
    # 适用信息
    constitution_types = Column(JSON, comment="适用体质")
    symptoms = Column(JSON, comment="适用症状")
    syndromes = Column(JSON, comment="适用证候")
    
    # 来源信息
    source = Column(String(200), comment="来源")
    author = Column(String(100), comment="作者")
    reference = Column(Text, comment="参考文献")
    
    # 质量信息
    reliability_score = Column(Float, default=0.0, comment="可靠性评分")
    usage_count = Column(Integer, default=0, comment="使用次数")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index('idx_tcm_category', 'category'),
        Index('idx_tcm_title', 'title'),
        Index('idx_tcm_reliability', 'reliability_score'),
    )

# 食疗方案表
class FoodTherapy(Base):
    """食疗方案表"""
    __tablename__ = "food_therapy"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    name = Column(String(200), nullable=False, comment="方案名称")
    description = Column(Text, comment="方案描述")
    
    # 食材信息
    ingredients = Column(JSON, nullable=False, comment="食材列表")
    preparation_method = Column(Text, comment="制作方法")
    serving_size = Column(String(100), comment="份量")
    
    # 营养信息
    nutrition_facts = Column(JSON, comment="营养成分")
    calories_per_serving = Column(Float, comment="每份热量")
    
    # 适用信息
    constitution_types = Column(JSON, comment="适用体质")
    health_benefits = Column(JSON, comment="健康功效")
    contraindications = Column(JSON, comment="禁忌症")
    
    # 季节性
    suitable_seasons = Column(JSON, comment="适宜季节")
    
    # 难度和时间
    difficulty_level = Column(String(50), comment="难度等级")
    preparation_time = Column(Integer, comment="制作时间（分钟）")
    
    # 评价信息
    rating = Column(Float, default=0.0, comment="评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index('idx_food_therapy_name', 'name'),
        Index('idx_food_therapy_rating', 'rating'),
    )

# 养生目的地表
class WellnessDestination(Base):
    """养生目的地表"""
    __tablename__ = "wellness_destinations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    name = Column(String(200), nullable=False, comment="目的地名称")
    description = Column(Text, comment="描述")
    location = Column(String(500), nullable=False, comment="位置")
    
    # 养生类型
    wellness_types = Column(JSON, comment="养生类型")
    natural_features = Column(JSON, comment="自然特色")
    
    # 设施信息
    facilities = Column(JSON, comment="设施列表")
    accommodation = Column(JSON, comment="住宿信息")
    
    # 适用信息
    constitution_suitability = Column(JSON, comment="适合体质")
    recommended_duration = Column(JSON, comment="推荐时长")
    best_seasons = Column(JSON, comment="最佳季节")
    
    # 价格信息
    price_range = Column(String(100), comment="价格区间")
    package_options = Column(JSON, comment="套餐选项")
    
    # 评价信息
    rating = Column(Float, default=0.0, comment="评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    
    # 可用性
    is_available = Column(Boolean, default=True, comment="是否可用")
    capacity = Column(Integer, comment="容量")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index('idx_wellness_name', 'name'),
        Index('idx_wellness_location', 'location'),
        Index('idx_wellness_rating', 'rating'),
        Index('idx_wellness_available', 'is_available'),
    )

# 用户健康档案表
class UserHealthProfile(Base):
    """用户健康档案表"""
    __tablename__ = "user_health_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, comment="用户ID")
    
    # 基本信息
    constitution_type = Column(Enum(ConstitutionType), comment="体质类型")
    constitution_score = Column(JSON, comment="体质评分详情")
    
    # 健康状态
    current_symptoms = Column(JSON, comment="当前症状")
    chronic_conditions = Column(JSON, comment="慢性疾病")
    allergies = Column(JSON, comment="过敏史")
    medications = Column(JSON, comment="当前用药")
    
    # 生活方式
    lifestyle_factors = Column(JSON, comment="生活方式因素")
    dietary_preferences = Column(JSON, comment="饮食偏好")
    exercise_habits = Column(JSON, comment="运动习惯")
    
    # 健康目标
    health_goals = Column(JSON, comment="健康目标")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index('idx_health_profile_user', 'user_id'),
        Index('idx_health_profile_constitution', 'constitution_type'),
    ) 