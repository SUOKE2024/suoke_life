"""
models - 索克生活项目模块
"""

import datetime
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

"""
五诊服务数据库模型

定义患者信息、诊断记录、分析结果等核心数据模型，
支持多种诊断类型的数据存储和查询。
"""


Base = declarative_base()


class Patient(Base):
    """患者信息表"""

    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, comment="患者姓名")
    gender = Column(String(10), nullable=False, comment="性别")
    age = Column(Integer, nullable=False, comment="年龄")
    birth_date = Column(DateTime, nullable=True, comment="出生日期")
    phone = Column(String(20), nullable=True, comment="联系电话")
    id_card = Column(String(20), nullable=True, comment="身份证号")
    address = Column(Text, nullable=True, comment="地址")

    # 中医相关信息
    constitution_type = Column(String(20), nullable=True, comment="体质类型")
    medical_history = Column(JSON, nullable=True, comment="病史")
    family_history = Column(JSON, nullable=True, comment="家族史")
    allergies = Column(JSON, nullable=True, comment="过敏史")
    current_medications = Column(JSON, nullable=True, comment="当前用药")

    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )
    is_active = Column(Boolean, default=True, comment="是否激活")

    # 关联关系
    diagnosis_sessions = relationship("DiagnosisSession", back_populates="patient")


class DiagnosisSession(Base):
    """诊断会话表"""

    __tablename__ = "diagnosis_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    session_type = Column(
        String(20), nullable=False, comment="会话类型：comprehensive / single"
    )
    status = Column(
        String(20), default="active", comment="状态：active / completed / cancelled"
    )

    # 诊断信息
    chief_complaint = Column(Text, nullable=True, comment="主诉")
    present_illness = Column(Text, nullable=True, comment="现病史")
    diagnosis_date = Column(DateTime, default=datetime.utcnow, comment="诊断日期")
    doctor_id = Column(String(50), nullable=True, comment="医生ID")

    # 综合诊断结果
    tcm_diagnosis = Column(String(200), nullable=True, comment="中医诊断")
    syndrome_pattern = Column(String(100), nullable=True, comment="证候模式")
    severity_level = Column(String(20), nullable=True, comment="严重程度")
    confidence_score = Column(Float, nullable=True, comment="置信度")

    # 治疗建议
    treatment_plan = Column(JSON, nullable=True, comment="治疗方案")
    lifestyle_advice = Column(JSON, nullable=True, comment="生活建议")
    follow_up_date = Column(DateTime, nullable=True, comment="复诊日期")

    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关联关系
    patient = relationship("Patient", back_populates="diagnosis_sessions")
    look_analyses = relationship("LookAnalysis", back_populates="session")
    listen_analyses = relationship("ListenAnalysis", back_populates="session")
    inquiry_analyses = relationship("InquiryAnalysis", back_populates="session")
    palpation_analyses = relationship("PalpationAnalysis", back_populates="session")
    calculation_analyses = relationship("CalculationAnalysis", back_populates="session")


class LookAnalysis(Base):
    """望诊分析结果表"""

    __tablename__ = "look_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("diagnosis_sessions.id"), nullable=False
    )
    analysis_type = Column(
        String(20), nullable=False, comment="分析类型：face / tongue / eye"
    )

    # 图像信息
    image_path = Column(String(500), nullable=True, comment="图像路径")
    image_metadata = Column(JSON, nullable=True, comment="图像元数据")

    # 分析结果
    analysis_result = Column(JSON, nullable=False, comment="分析结果")
    tcm_diagnosis = Column(String(200), nullable=True, comment="中医诊断")
    confidence_score = Column(Float, nullable=True, comment="置信度")

    # 具体特征
    complexion = Column(String(50), nullable=True, comment="面色")
    tongue_color = Column(String(50), nullable=True, comment="舌色")
    tongue_coating = Column(String(50), nullable=True, comment="舌苔")
    eye_luster = Column(String(50), nullable=True, comment="眼神")

    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    processing_time = Column(Float, nullable=True, comment="处理时间(秒)")

    # 关联关系
    session = relationship("DiagnosisSession", back_populates="look_analyses")


class ListenAnalysis(Base):
    """闻诊分析结果表"""

    __tablename__ = "listen_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("diagnosis_sessions.id"), nullable=False
    )
    analysis_type = Column(
        String(20), nullable=False, comment="分析类型：voice / breathing / cough"
    )

    # 音频信息
    audio_path = Column(String(500), nullable=True, comment="音频路径")
    audio_metadata = Column(JSON, nullable=True, comment="音频元数据")
    duration = Column(Float, nullable=True, comment="音频时长(秒)")

    # 分析结果
    analysis_result = Column(JSON, nullable=False, comment="分析结果")
    tcm_diagnosis = Column(String(200), nullable=True, comment="中医诊断")
    confidence_score = Column(Float, nullable=True, comment="置信度")

    # 具体特征
    voice_quality = Column(String(50), nullable=True, comment="声音质量")
    breathing_pattern = Column(String(50), nullable=True, comment="呼吸模式")
    cough_type = Column(String(50), nullable=True, comment="咳嗽类型")
    emotional_state = Column(String(50), nullable=True, comment="情绪状态")

    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    processing_time = Column(Float, nullable=True, comment="处理时间(秒)")

    # 关联关系
    session = relationship("DiagnosisSession", back_populates="listen_analyses")


class InquiryAnalysis(Base):
    """问诊分析结果表"""

    __tablename__ = "inquiry_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("diagnosis_sessions.id"), nullable=False
    )

    # 对话信息
    dialogue_history = Column(JSON, nullable=False, comment="对话历史")
    dialogue_duration = Column(Float, nullable=True, comment="对话时长(分钟)")

    # 分析结果
    extracted_symptoms = Column(JSON, nullable=False, comment="提取的症状")
    patient_profile = Column(JSON, nullable=True, comment="患者档案")
    syndrome_patterns = Column(JSON, nullable=True, comment="证候模式")
    tcm_diagnosis = Column(String(200), nullable=True, comment="中医诊断")
    confidence_score = Column(Float, nullable=True, comment="置信度")

    # 症状统计
    symptom_count = Column(Integer, default=0, comment="症状数量")
    severity_assessment = Column(String(50), nullable=True, comment="严重程度评估")

    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    processing_time = Column(Float, nullable=True, comment="处理时间(秒)")

    # 关联关系
    session = relationship("DiagnosisSession", back_populates="inquiry_analyses")


class PalpationAnalysis(Base):
    """切诊分析结果表"""

    __tablename__ = "palpation_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("diagnosis_sessions.id"), nullable=False
    )
    analysis_type = Column(
        String(20), nullable=False, comment="分析类型：pulse / abdomen / acupoint"
    )

    # 传感器数据
    sensor_data = Column(JSON, nullable=True, comment="传感器数据")
    data_quality = Column(String(20), nullable=True, comment="数据质量")

    # 分析结果
    analysis_result = Column(JSON, nullable=False, comment="分析结果")
    tcm_diagnosis = Column(String(200), nullable=True, comment="中医诊断")
    confidence_score = Column(Float, nullable=True, comment="置信度")

    # 脉象特征
    pulse_rate = Column(Float, nullable=True, comment="脉率")
    pulse_type = Column(String(50), nullable=True, comment="脉象类型")
    pulse_strength = Column(String(50), nullable=True, comment="脉力")
    pulse_rhythm = Column(String(50), nullable=True, comment="脉律")

    # 腹诊特征
    tenderness_points = Column(JSON, nullable=True, comment="压痛点")
    muscle_tension = Column(String(50), nullable=True, comment="肌肉紧张度")

    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    processing_time = Column(Float, nullable=True, comment="处理时间(秒)")

    # 关联关系
    session = relationship("DiagnosisSession", back_populates="palpation_analyses")


class CalculationAnalysis(Base):
    """算诊分析结果表"""

    __tablename__ = "calculation_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("diagnosis_sessions.id"), nullable=False
    )

    # 出生信息
    birth_info = Column(JSON, nullable=False, comment="出生信息")

    # 分析结果
    constitution_analysis = Column(JSON, nullable=False, comment="体质分析")
    meridian_flow = Column(JSON, nullable=False, comment="子午流注")
    five_elements = Column(JSON, nullable=True, comment="五运六气")
    bagua_analysis = Column(JSON, nullable=True, comment="八卦分析")

    # 核心结果
    primary_constitution = Column(String(50), nullable=True, comment="主要体质")
    secondary_constitution = Column(String(50), nullable=True, comment="次要体质")
    current_meridian = Column(String(50), nullable=True, comment="当前经络")
    overall_assessment = Column(Text, nullable=True, comment="综合评估")
    confidence_score = Column(Float, nullable=True, comment="置信度")

    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    processing_time = Column(Float, nullable=True, comment="处理时间(秒)")

    # 关联关系
    session = relationship("DiagnosisSession", back_populates="calculation_analyses")


class DiagnosisTemplate(Base):
    """诊断模板表"""

    __tablename__ = "diagnosis_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, comment="模板名称")
    category = Column(String(50), nullable=False, comment="分类")
    description = Column(Text, nullable=True, comment="描述")

    # 模板内容
    template_data = Column(JSON, nullable=False, comment="模板数据")
    symptoms = Column(JSON, nullable=True, comment="相关症状")
    diagnosis_criteria = Column(JSON, nullable=True, comment="诊断标准")
    treatment_options = Column(JSON, nullable=True, comment="治疗选项")

    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")
    success_rate = Column(Float, nullable=True, comment="成功率")

    # 系统字段
    created_by = Column(String(50), nullable=True, comment="创建者")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )
    is_active = Column(Boolean, default=True, comment="是否激活")


class SystemLog(Base):
    """系统日志表"""

    __tablename__ = "system_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(50), nullable=False, comment="服务名称")
    log_level = Column(String(20), nullable=False, comment="日志级别")
    message = Column(Text, nullable=False, comment="日志消息")

    # 上下文信息
    session_id = Column(UUID(as_uuid=True), nullable=True, comment="会话ID")
    user_id = Column(String(50), nullable=True, comment="用户ID")
    request_id = Column(String(100), nullable=True, comment="请求ID")

    # 性能信息
    processing_time = Column(Float, nullable=True, comment="处理时间")
    memory_usage = Column(Float, nullable=True, comment="内存使用")
    cpu_usage = Column(Float, nullable=True, comment="CPU使用")

    # 错误信息
    error_code = Column(String(50), nullable=True, comment="错误代码")
    error_details = Column(JSON, nullable=True, comment="错误详情")
    stack_trace = Column(Text, nullable=True, comment="堆栈跟踪")

    # 系统字段
    timestamp = Column(DateTime, default=datetime.utcnow, comment="时间戳")
    hostname = Column(String(100), nullable=True, comment="主机名")
    ip_address = Column(String(50), nullable=True, comment="IP地址")


class PerformanceMetric(Base):
    """性能指标表"""

    __tablename__ = "performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(50), nullable=False, comment="服务名称")
    metric_name = Column(String(100), nullable=False, comment="指标名称")
    metric_value = Column(Float, nullable=False, comment="指标值")
    metric_unit = Column(String(20), nullable=True, comment="单位")

    # 时间信息
    timestamp = Column(DateTime, default=datetime.utcnow, comment="时间戳")
    time_window = Column(String(20), nullable=True, comment="时间窗口")

    # 标签
    tags = Column(JSON, nullable=True, comment="标签")

    # 统计信息
    min_value = Column(Float, nullable=True, comment="最小值")
    max_value = Column(Float, nullable=True, comment="最大值")
    avg_value = Column(Float, nullable=True, comment="平均值")
    std_value = Column(Float, nullable=True, comment="标准差")
