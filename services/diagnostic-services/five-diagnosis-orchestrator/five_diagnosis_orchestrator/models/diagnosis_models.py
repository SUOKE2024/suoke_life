"""
五诊协同诊断数据模型

定义诊断过程中使用的所有数据结构和模型
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, validator


class DiagnosisType(Enum):
    """诊断类型枚举"""
    LOOK = "look"              # 望诊
    LISTEN = "listen"          # 闻诊  
    INQUIRY = "inquiry"        # 问诊
    PALPATION = "palpation"    # 切诊
    CALCULATION = "calculation" # 算诊


class SessionStatus(Enum):
    """会话状态枚举"""
    CREATED = "created"        # 已创建
    RUNNING = "running"        # 运行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"    # 已取消


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"        # 健康
    SUB_HEALTHY = "sub_healthy" # 亚健康
    MILD_DISCOMFORT = "mild_discomfort"  # 轻度不适
    NEEDS_ATTENTION = "needs_attention"   # 需要关注
    REQUIRES_TREATMENT = "requires_treatment"  # 需要治疗


@dataclass
class PatientInfo:
    """患者信息"""
    patient_id: str
    name: str = ""
    age: int = 0
    gender: str = ""  # "男" 或 "女"
    height: Optional[float] = None  # 身高(cm)
    weight: Optional[float] = None  # 体重(kg)
    occupation: str = ""
    location: str = ""
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    emergency_contact: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def bmi(self) -> Optional[float]:
        """计算BMI"""
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100
            return round(self.weight / (height_m**2), 2)
        return None
    
    @property
    def age_group(self) -> str:
        """年龄组"""
        if self.age < 18:
            return "青少年"
        elif self.age < 35:
            return "青年"
        elif self.age < 60:
            return "中年"
        else:
            return "老年"


@dataclass
class DiagnosisInput:
    """诊断输入数据"""
    diagnosis_type: DiagnosisType
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """验证输入数据"""
        if not self.data:
            raise ValueError("诊断输入数据不能为空")


@dataclass
class DiagnosisResult:
    """单个诊断结果"""
    diagnosis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    diagnosis_type: DiagnosisType = DiagnosisType.INQUIRY
    session_id: str = ""
    patient_id: str = ""
    
    # 诊断结果
    confidence: float = 0.0  # 置信度 (0-1)
    features: Dict[str, Any] = field(default_factory=dict)  # 提取的特征
    raw_result: Dict[str, Any] = field(default_factory=dict)  # 原始结果
    
    # 元数据
    processing_time: float = 0.0  # 处理时间(秒)
    model_version: str = ""
    status: str = "pending"  # pending, processing, completed, failed
    error_message: str = ""
    
    # 时间戳
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """验证结果数据"""
        if not 0<=self.confidence<=1:
            raise ValueError("置信度必须在0-1之间")
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status=="completed"
    
    @property
    def is_high_confidence(self) -> bool:
        """是否高置信度"""
        return self.confidence>=0.8


@dataclass
class DiagnosisRecommendation:
    """诊断建议"""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""  # treatment, lifestyle, diet, exercise, follow_up
    priority: str = "medium"  # critical, high, medium, low
    title: str = ""
    description: str = ""
    rationale: str = ""  # 建议依据
    
    # 实施信息
    implementation_steps: List[str] = field(default_factory=list)
    duration: str = ""
    frequency: str = ""
    
    # 安全信息
    precautions: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    
    # 监测信息
    expected_outcomes: List[str] = field(default_factory=list)
    monitoring_indicators: List[str] = field(default_factory=list)
    
    # 元数据
    confidence: float = 0.0
    evidence_level: str = "expert_opinion"
    source_diagnoses: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FusedDiagnosisResult:
    """融合诊断结果"""
    session_id: str
    patient_info: PatientInfo
    individual_results: Dict[DiagnosisType, DiagnosisResult] = field(default_factory=dict)
    
    # 融合结果
    primary_syndrome: str = ""  # 主要证型
    secondary_syndromes: List[str] = field(default_factory=list)  # 次要证型
    constitution_type: str = ""  # 体质类型
    health_status: str = ""  # 健康状态
    risk_factors: List[str] = field(default_factory=list)  # 风险因素
    
    # 置信度和质量指标
    overall_confidence: float = 0.0  # 整体置信度
    consistency_score: float = 0.0   # 一致性分数
    completeness_score: float = 0.0  # 完整性分数
    
    # 建议
    treatment_recommendations: List[str] = field(default_factory=list)
    lifestyle_recommendations: List[str] = field(default_factory=list)
    follow_up_recommendations: List[str] = field(default_factory=list)
    
    # 详细分析
    syndrome_analysis: Dict[str, Any] = field(default_factory=dict)
    constitution_analysis: Dict[str, Any] = field(default_factory=dict)
    symptom_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    fusion_method: str = "hybrid"
    total_processing_time: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def diagnosis_count(self) -> int:
        """诊断数量"""
        return len(self.individual_results)
    
    @property
    def is_high_quality(self) -> bool:
        """是否高质量结果"""
        return (self.overall_confidence>=0.7 and 
                self.consistency_score>=0.6 and 
                self.completeness_score>=0.6)
    
    @property
    def quality_grade(self) -> str:
        """质量等级"""
        if self.is_high_quality:
            return "优秀"
        elif self.overall_confidence>=0.5 and self.consistency_score>=0.4:
            return "良好"
        elif self.overall_confidence>=0.3:
            return "一般"
        else:
            return "较差"


@dataclass
class DiagnosisSession:
    """诊断会话"""
    session_id: str
    patient_info: PatientInfo
    enabled_diagnoses: List[DiagnosisType] = field(default_factory=list)
    
    # 会话状态
    status: SessionStatus = SessionStatus.CREATED
    progress: float = 0.0  # 进度 (0-1)
    
    # 诊断结果
    diagnosis_results: Dict[DiagnosisType, DiagnosisResult] = field(default_factory=dict)
    fused_result: Optional[FusedDiagnosisResult] = None
    
    # 配置
    diagnosis_timeout: int = 300  # 诊断超时时间(秒)
    require_all_diagnoses: bool = False  # 是否要求所有诊断完成
    
    # 错误和警告
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # 时间戳
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[float] = None
    
    @property
    def is_active(self) -> bool:
        """是否活跃会话"""
        return self.status in [SessionStatus.CREATED, SessionStatus.RUNNING]
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status==SessionStatus.COMPLETED
    
    @property
    def completion_rate(self) -> float:
        """完成率"""
        if not self.enabled_diagnoses:
            return 0.0
        return len(self.diagnosis_results) / len(self.enabled_diagnoses)
    
    def update_progress(self) -> None:
        """更新进度"""
        self.progress = self.completion_rate


@dataclass
class DiagnosisEvent:
    """诊断事件"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    event_type: str = ""  # session_created, diagnosis_started, diagnosis_completed, etc.
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Pydantic模型用于API接口
class PatientInfoModel(BaseModel):
    """患者信息API模型"""
    patient_id: str = Field(..., description="患者ID")
    name: str = Field("", description="姓名")
    age: int = Field(0, ge=0, le=150, description="年龄")
    gender: str = Field("", description="性别")
    height: Optional[float] = Field(None, ge=0, le=300, description="身高(cm)")
    weight: Optional[float] = Field(None, ge=0, le=500, description="体重(kg)")
    occupation: str = Field("", description="职业")
    location: str = Field("", description="地区")
    medical_history: List[str] = Field(default_factory=list, description="病史")
    current_medications: List[str] = Field(default_factory=list, description="当前用药")
    allergies: List[str] = Field(default_factory=list, description="过敏史")
    emergency_contact: str = Field("", description="紧急联系人")
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['男', '女', 'male', 'female', 'M', 'F']:
            raise ValueError('性别必须是: 男, 女, male, female, M, F')
        return v


class DiagnosisInputModel(BaseModel):
    """诊断输入API模型"""
    diagnosis_type: str = Field(..., description="诊断类型")
    data: Dict[str, Any] = Field(..., description="诊断数据")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    @validator('diagnosis_type')
    def validate_diagnosis_type(cls, v):
        valid_types = [dt.value for dt in DiagnosisType]
        if v not in valid_types:
            raise ValueError(f'诊断类型必须是: {valid_types}')
        return v


class DiagnosisResultModel(BaseModel):
    """诊断结果API模型"""
    diagnosis_id: str = Field(..., description="诊断ID")
    diagnosis_type: str = Field(..., description="诊断类型")
    session_id: str = Field(..., description="会话ID")
    patient_id: str = Field(..., description="患者ID")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    features: Dict[str, Any] = Field(default_factory=dict, description="特征")
    raw_result: Dict[str, Any] = Field(default_factory=dict, description="原始结果")
    processing_time: float = Field(0.0, ge=0, description="处理时间")
    model_version: str = Field("", description="模型版本")
    status: str = Field("pending", description="状态")
    error_message: str = Field("", description="错误信息")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class FusedDiagnosisResultModel(BaseModel):
    """融合诊断结果API模型"""
    session_id: str = Field(..., description="会话ID")
    patient_info: PatientInfoModel = Field(..., description="患者信息")
    primary_syndrome: str = Field("", description="主要证型")
    secondary_syndromes: List[str] = Field(default_factory=list, description="次要证型")
    constitution_type: str = Field("", description="体质类型")
    health_status: str = Field("", description="健康状态")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    overall_confidence: float = Field(0.0, ge=0, le=1, description="整体置信度")
    consistency_score: float = Field(0.0, ge=0, le=1, description="一致性分数")
    completeness_score: float = Field(0.0, ge=0, le=1, description="完整性分数")
    treatment_recommendations: List[str] = Field(default_factory=list, description="治疗建议")
    lifestyle_recommendations: List[str] = Field(default_factory=list, description="生活方式建议")
    follow_up_recommendations: List[str] = Field(default_factory=list, description="随访建议")
    syndrome_analysis: Dict[str, Any] = Field(default_factory=dict, description="证型分析")
    constitution_analysis: Dict[str, Any] = Field(default_factory=dict, description="体质分析")
    symptom_analysis: Dict[str, Any] = Field(default_factory=dict, description="症状分析")
    fusion_method: str = Field("hybrid", description="融合方法")
    total_processing_time: float = Field(0.0, ge=0, description="总处理时间")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DiagnosisSessionModel(BaseModel):
    """诊断会话API模型"""
    session_id: str = Field(..., description="会话ID")
    patient_info: PatientInfoModel = Field(..., description="患者信息")
    enabled_diagnoses: List[str] = Field(..., description="启用的诊断类型")
    status: str = Field("created", description="会话状态")
    progress: float = Field(0.0, ge=0, le=1, description="进度")
    diagnosis_timeout: int = Field(300, ge=30, le=3600, description="诊断超时时间")
    require_all_diagnoses: bool = Field(False, description="是否要求所有诊断完成")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[float] = None
    
    @validator('enabled_diagnoses')
    def validate_enabled_diagnoses(cls, v):
        valid_types = [dt.value for dt in DiagnosisType]
        for diagnosis_type in v:
            if diagnosis_type not in valid_types:
                raise ValueError(f'诊断类型必须是: {valid_types}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = [status.value for status in SessionStatus]
        if v not in valid_statuses:
            raise ValueError(f'会话状态必须是: {valid_statuses}')
        return v


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    patient_info: PatientInfoModel = Field(..., description="患者信息")
    enabled_diagnoses: List[str] = Field(..., min_items=1, description="启用的诊断类型")
    diagnosis_timeout: int = Field(300, ge=30, le=3600, description="诊断超时时间")
    require_all_diagnoses: bool = Field(False, description="是否要求所有诊断完成")


class StartDiagnosisRequest(BaseModel):
    """开始诊断请求"""
    session_id: str = Field(..., description="会话ID")
    diagnosis_inputs: List[DiagnosisInputModel] = Field(..., min_items=1, description="诊断输入")


class SessionStatusResponse(BaseModel):
    """会话状态响应"""
    session_id: str = Field(..., description="会话ID")
    status: str = Field(..., description="会话状态")
    progress: float = Field(..., description="进度")
    enabled_diagnoses: List[str] = Field(..., description="启用的诊断类型")
    completed_diagnoses: List[str] = Field(..., description="已完成的诊断类型")
    created_at: datetime = Field(..., description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    total_duration: Optional[float] = Field(None, description="总耗时")
    errors: List[str] = Field(..., description="错误列表")
    warnings: List[str] = Field(..., description="警告列表")


class SystemMetricsResponse(BaseModel):
    """系统指标响应"""
    total_sessions: int = Field(..., description="总会话数")
    successful_sessions: int = Field(..., description="成功会话数")
    failed_sessions: int = Field(..., description="失败会话数")
    success_rate: float = Field(..., description="成功率")
    average_processing_time: float = Field(..., description="平均处理时间")
    active_sessions: int = Field(..., description="活跃会话数")
    service_availability: Dict[str, bool] = Field(..., description="服务可用性")


# 工具函数
def create_patient_info_from_dict(data: Dict[str, Any]) -> PatientInfo:
    """从字典创建患者信息"""
    return PatientInfo(
        patient_id=data.get('patient_id', ''),
        name=data.get('name', ''),
        age=data.get('age', 0),
        gender=data.get('gender', ''),
        height=data.get('height'),
        weight=data.get('weight'),
        occupation=data.get('occupation', ''),
        location=data.get('location', ''),
        medical_history=data.get('medical_history', []),
        current_medications=data.get('current_medications', []),
        allergies=data.get('allergies', []),
        emergency_contact=data.get('emergency_contact', '')
    )


def create_diagnosis_input_from_dict(data: Dict[str, Any]) -> DiagnosisInput:
    """从字典创建诊断输入"""
    diagnosis_type_str = data.get('diagnosis_type', '')
    diagnosis_type = DiagnosisType(diagnosis_type_str)
    
    return DiagnosisInput(
        diagnosis_type=diagnosis_type,
        data=data.get('data', {}),
        metadata=data.get('metadata', {})
    )


def diagnosis_result_to_dict(result: DiagnosisResult) -> Dict[str, Any]:
    """诊断结果转换为字典"""
    return {
        'diagnosis_id': result.diagnosis_id,
        'diagnosis_type': result.diagnosis_type.value,
        'session_id': result.session_id,
        'patient_id': result.patient_id,
        'confidence': result.confidence,
        'features': result.features,
        'raw_result': result.raw_result,
        'processing_time': result.processing_time,
        'model_version': result.model_version,
        'status': result.status,
        'error_message': result.error_message,
        'created_at': result.created_at.isoformat(),
        'completed_at': result.completed_at.isoformat() if result.completed_at else None
    }


def fused_result_to_dict(result: FusedDiagnosisResult) -> Dict[str, Any]:
    """融合结果转换为字典"""
    return {
        'session_id': result.session_id,
        'patient_info': {
            'patient_id': result.patient_info.patient_id,
            'name': result.patient_info.name,
            'age': result.patient_info.age,
            'gender': result.patient_info.gender,
            'height': result.patient_info.height,
            'weight': result.patient_info.weight,
            'bmi': result.patient_info.bmi
        },
        'primary_syndrome': result.primary_syndrome,
        'secondary_syndromes': result.secondary_syndromes,
        'constitution_type': result.constitution_type,
        'health_status': result.health_status,
        'risk_factors': result.risk_factors,
        'overall_confidence': result.overall_confidence,
        'consistency_score': result.consistency_score,
        'completeness_score': result.completeness_score,
        'quality_grade': result.quality_grade,
        'treatment_recommendations': result.treatment_recommendations,
        'lifestyle_recommendations': result.lifestyle_recommendations,
        'follow_up_recommendations': result.follow_up_recommendations,
        'syndrome_analysis': result.syndrome_analysis,
        'constitution_analysis': result.constitution_analysis,
        'symptom_analysis': result.symptom_analysis,
        'fusion_method': result.fusion_method,
        'total_processing_time': result.total_processing_time,
        'created_at': result.created_at.isoformat()
    }