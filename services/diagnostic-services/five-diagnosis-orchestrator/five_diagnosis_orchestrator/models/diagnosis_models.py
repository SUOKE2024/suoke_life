"""
五诊系统数据模型
Five Diagnosis System Data Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import uuid


class DiagnosisType(str, Enum):
    """诊断类型"""
    CALCULATION = "calculation"  # 算诊
    LOOK = "look"               # 望诊
    LISTEN = "listen"           # 闻诊
    INQUIRY = "inquiry"         # 问诊
    PALPATION = "palpation"     # 切诊


class DiagnosisStatus(str, Enum):
    """诊断状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class SessionStatus(str, Enum):
    """会话状态"""
    CREATED = "created"
    STARTED = "started"
    DIAGNOSING = "diagnosing"
    FUSING = "fusing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """置信度等级"""
    VERY_LOW = "very_low"      # 0.0-0.3
    LOW = "low"                # 0.3-0.5
    MEDIUM = "medium"          # 0.5-0.7
    HIGH = "high"              # 0.7-0.9
    VERY_HIGH = "very_high"    # 0.9-1.0


@dataclass
class PatientInfo:
    """患者信息"""
    patient_id: str
    name: str
    age: int
    gender: str
    birth_date: datetime
    medical_history: List[str] = field(default_factory=list)
    current_symptoms: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    lifestyle: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosisInput:
    """诊断输入数据"""
    diagnosis_type: DiagnosisType
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiagnosisResult:
    """单个诊断结果"""
    diagnosis_type: DiagnosisType
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    findings: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    recommendations: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: DiagnosisStatus = DiagnosisStatus.PENDING
    error_message: Optional[str] = None


@dataclass
class FusedDiagnosisResult:
    """融合诊断结果"""
    session_id: str
    patient_info: PatientInfo
    individual_results: Dict[DiagnosisType, DiagnosisResult]
    
    # 融合分析结果
    primary_syndrome: str = ""
    secondary_syndromes: List[str] = field(default_factory=list)
    constitution_type: str = ""
    health_status: str = ""
    risk_factors: List[str] = field(default_factory=list)
    
    # 综合评估
    overall_confidence: float = 0.0
    consistency_score: float = 0.0  # 五诊结果一致性
    completeness_score: float = 0.0  # 诊断完整性
    
    # 诊断建议
    treatment_recommendations: List[str] = field(default_factory=list)
    lifestyle_recommendations: List[str] = field(default_factory=list)
    follow_up_recommendations: List[str] = field(default_factory=list)
    
    # 元数据
    fusion_algorithm_version: str = "1.0.0"
    total_processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiagnosisSession:
    """诊断会话"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_info: PatientInfo = None
    status: SessionStatus = SessionStatus.CREATED
    
    # 诊断配置
    enabled_diagnoses: List[DiagnosisType] = field(default_factory=lambda: list(DiagnosisType))
    diagnosis_timeout: int = 300  # 秒
    require_all_diagnoses: bool = False
    
    # 诊断结果
    diagnosis_results: Dict[DiagnosisType, DiagnosisResult] = field(default_factory=dict)
    fused_result: Optional[FusedDiagnosisResult] = None
    
    # 会话元数据
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: float = 0.0
    
    # 错误处理
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class DiagnosisRecommendation:
    """诊断建议"""
    category: str  # 治疗、生活方式、饮食、运动等
    priority: int  # 1-5，1为最高优先级
    title: str
    description: str
    evidence: List[str] = field(default_factory=list)  # 支持证据
    confidence: float = 0.0
    source_diagnoses: List[DiagnosisType] = field(default_factory=list)
    
    # 实施指导
    implementation_steps: List[str] = field(default_factory=list)
    duration: Optional[str] = None  # 建议持续时间
    frequency: Optional[str] = None  # 频率
    precautions: List[str] = field(default_factory=list)  # 注意事项


@dataclass
class DiagnosisMetrics:
    """诊断指标"""
    session_id: str
    
    # 性能指标
    total_processing_time: float = 0.0
    individual_processing_times: Dict[DiagnosisType, float] = field(default_factory=dict)
    fusion_processing_time: float = 0.0
    
    # 质量指标
    overall_confidence: float = 0.0
    individual_confidences: Dict[DiagnosisType, float] = field(default_factory=dict)
    consistency_score: float = 0.0
    completeness_score: float = 0.0
    
    # 成功率指标
    successful_diagnoses: int = 0
    failed_diagnoses: int = 0
    timeout_diagnoses: int = 0
    success_rate: float = 0.0
    
    # 资源使用
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiagnosisEvent:
    """诊断事件"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    event_type: str = ""  # session_started, diagnosis_completed, fusion_completed等
    diagnosis_type: Optional[DiagnosisType] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


# 辅助函数
def get_confidence_level(confidence: float) -> ConfidenceLevel:
    """根据置信度数值获取置信度等级"""
    if confidence < 0.3:
        return ConfidenceLevel.VERY_LOW
    elif confidence < 0.5:
        return ConfidenceLevel.LOW
    elif confidence < 0.7:
        return ConfidenceLevel.MEDIUM
    elif confidence < 0.9:
        return ConfidenceLevel.HIGH
    else:
        return ConfidenceLevel.VERY_HIGH


def calculate_success_rate(successful: int, total: int) -> float:
    """计算成功率"""
    if total == 0:
        return 0.0
    return successful / total


def merge_recommendations(recommendations: List[DiagnosisRecommendation]) -> List[DiagnosisRecommendation]:
    """合并相似的建议"""
    # 按类别和标题分组
    grouped = {}
    for rec in recommendations:
        key = f"{rec.category}:{rec.title}"
        if key not in grouped:
            grouped[key] = rec
        else:
            # 合并证据和来源
            grouped[key].evidence.extend(rec.evidence)
            grouped[key].source_diagnoses.extend(rec.source_diagnoses)
            # 取最高置信度
            grouped[key].confidence = max(grouped[key].confidence, rec.confidence)
    
    # 去重并排序
    result = list(grouped.values())
    for rec in result:
        rec.evidence = list(set(rec.evidence))
        rec.source_diagnoses = list(set(rec.source_diagnoses))
    
    return sorted(result, key=lambda x: (x.priority, -x.confidence)) 