"""
中医诊断数据模型

定义中医闻诊相关的数据结构，包括体质分析、情绪识别、脏腑功能评估等。
基于传统中医理论和现代数据科学方法。
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.types import PositiveFloat, confloat


class ConstitutionType(str, Enum):
    """中医体质类型（九种体质）"""

    BALANCED = "平和质"  # 平和质
    QI_DEFICIENCY = "气虚质"  # 气虚质
    YANG_DEFICIENCY = "阳虚质"  # 阳虚质
    YIN_DEFICIENCY = "阴虚质"  # 阴虚质
    PHLEGM_DAMPNESS = "痰湿质"  # 痰湿质
    DAMP_HEAT = "湿热质"  # 湿热质
    BLOOD_STASIS = "血瘀质"  # 血瘀质
    QI_STAGNATION = "气郁质"  # 气郁质
    SPECIAL = "特禀质"  # 特禀质


class EmotionState(str, Enum):
    """五志情绪状态"""

    JOY = "喜"  # 喜（心）
    ANGER = "怒"  # 怒（肝）
    WORRY = "忧"  # 忧（肺）
    THOUGHT = "思"  # 思（脾）
    FEAR = "恐"  # 恐（肾）
    CALM = "平静"  # 平静状态


class OrganType(str, Enum):
    """五脏六腑"""

    HEART = "心"  # 心
    LIVER = "肝"  # 肝
    SPLEEN = "脾"  # 脾
    LUNG = "肺"  # 肺
    KIDNEY = "肾"  # 肾
    GALLBLADDER = "胆"  # 胆
    STOMACH = "胃"  # 胃
    SMALL_INTESTINE = "小肠"  # 小肠
    LARGE_INTESTINE = "大肠"  # 大肠
    BLADDER = "膀胱"  # 膀胱
    TRIPLE_HEATER = "三焦"  # 三焦


class SoundQuality(str, Enum):
    """声音质量特征"""

    CLEAR = "清"  # 清
    TURBID = "浊"  # 浊
    HIGH = "高"  # 高
    LOW = "低"  # 低
    STRONG = "强"  # 强
    WEAK = "弱"  # 弱
    SMOOTH = "滑"  # 滑
    ROUGH = "涩"  # 涩


class ConstitutionAnalysis(BaseModel):
    """体质分析结果"""

    model_config = ConfigDict(validate_assignment=True)

    primary_type: ConstitutionType = Field(..., description="主要体质类型")

    secondary_type: ConstitutionType | None = Field(
        default=None, description="次要体质类型（兼夹体质）"
    )

    confidence_score: confloat(ge=0.0, le=1.0) = Field(
        ..., description="体质判断置信度"
    )

    type_scores: dict[ConstitutionType, float] = Field(
        default_factory=dict, description="各体质类型得分"
    )

    characteristics: list[str] = Field(default_factory=list, description="体质特征描述")

    risk_factors: list[str] = Field(default_factory=list, description="易患疾病风险")


class EmotionAnalysis(BaseModel):
    """情绪分析结果"""

    model_config = ConfigDict(validate_assignment=True)

    primary_emotion: EmotionState = Field(..., description="主要情绪状态")

    emotion_intensity: confloat(ge=0.0, le=1.0) = Field(..., description="情绪强度")

    emotion_scores: dict[EmotionState, float] = Field(
        default_factory=dict, description="各情绪状态得分"
    )

    stability: confloat(ge=0.0, le=1.0) = Field(default=0.5, description="情绪稳定性")

    related_organs: list[OrganType] = Field(
        default_factory=list, description="相关脏腑"
    )


class OrganSoundMapping(BaseModel):
    """脏腑声音对应关系"""

    model_config = ConfigDict(validate_assignment=True)

    organ: OrganType = Field(..., description="脏腑类型")

    sound_characteristics: list[SoundQuality] = Field(
        default_factory=list, description="声音特征"
    )

    frequency_range: tuple[float, float] | None = Field(
        default=None, description="频率范围 (Hz)"
    )

    energy_level: confloat(ge=0.0, le=1.0) = Field(default=0.5, description="能量水平")

    health_score: confloat(ge=0.0, le=1.0) = Field(..., description="健康评分")

    abnormal_indicators: list[str] = Field(default_factory=list, description="异常指标")


class OrganAnalysis(BaseModel):
    """脏腑功能分析"""

    model_config = ConfigDict(validate_assignment=True)

    organ_scores: dict[OrganType, float] = Field(
        default_factory=dict, description="各脏腑功能评分"
    )

    organ_mappings: list[OrganSoundMapping] = Field(
        default_factory=list, description="脏腑声音对应分析"
    )

    overall_health: confloat(ge=0.0, le=1.0) = Field(..., description="整体健康评分")

    weak_organs: list[OrganType] = Field(
        default_factory=list, description="功能偏弱的脏腑"
    )

    strong_organs: list[OrganType] = Field(
        default_factory=list, description="功能较强的脏腑"
    )


class TCMRecommendation(BaseModel):
    """中医调理建议"""

    model_config = ConfigDict(validate_assignment=True)

    category: str = Field(..., description="建议类别（饮食、运动、作息等）")

    content: str = Field(..., description="具体建议内容")

    priority: int = Field(default=1, ge=1, le=5, description="优先级（1-5，5最高）")

    duration: str | None = Field(default=None, description="建议执行时长")

    contraindications: list[str] = Field(default_factory=list, description="禁忌事项")


class TCMDiagnosis(BaseModel):
    """中医诊断结果"""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # 基础诊断信息
    diagnosis_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="诊断唯一标识"
    )

    # 体质分析
    constitution_type: str = Field(..., description="主要体质类型")

    constitution_analysis: ConstitutionAnalysis | None = Field(
        default=None, description="详细体质分析"
    )

    # 情绪分析
    emotion_state: str = Field(..., description="主要情绪状态")

    emotion_analysis: EmotionAnalysis | None = Field(
        default=None, description="详细情绪分析"
    )

    # 脏腑分析
    organ_analysis: dict[str, Any] = Field(
        default_factory=dict, description="脏腑功能分析结果"
    )

    organ_details: OrganAnalysis | None = Field(
        default=None, description="详细脏腑分析"
    )

    # 综合评估
    confidence_score: confloat(ge=0.0, le=1.0) = Field(
        ..., description="整体诊断置信度"
    )

    health_score: confloat(ge=0.0, le=1.0) = Field(default=0.8, description="健康评分")

    # 分析方法和详细信息
    analysis_method: str = Field(default="hybrid", description="分析方法")

    detailed_scores: dict[str, float] | None = Field(
        default=None, description="详细评分"
    )

    # 建议和调理
    recommendations: list[str] = Field(default_factory=list, description="调理建议")

    detailed_recommendations: list[TCMRecommendation] = Field(
        default_factory=list, description="详细调理建议"
    )

    # 风险评估
    risk_assessment: dict[str, Any] | None = Field(
        default=None, description="健康风险评估"
    )

    # 元数据
    timestamp: float = Field(
        default_factory=lambda: datetime.now().timestamp(), description="诊断时间戳"
    )

    processing_time: float | None = Field(default=None, description="处理时间（秒）")

    error_message: str | None = Field(default=None, description="错误信息（如果有）")

    # 数据来源
    audio_features_used: list[str] = Field(
        default_factory=list, description="使用的音频特征类型"
    )

    model_versions: dict[str, str] | None = Field(
        default=None, description="使用的模型版本"
    )

    @field_validator("constitution_type")
    @classmethod
    def validate_constitution_type(cls, v):
        """验证体质类型"""
        valid_types = [t.value for t in ConstitutionType] + ["未知"]
        if v not in valid_types:
            raise ValueError(f"无效的体质类型: {v}")
        return v

    @field_validator("emotion_state")
    @classmethod
    def validate_emotion_state(cls, v):
        """验证情绪状态"""
        valid_states = [s.value for s in EmotionState] + ["未知"]
        if v not in valid_states:
            raise ValueError(f"无效的情绪状态: {v}")
        return v


class TCMAnalysisRequest(BaseModel):
    """中医分析请求"""

    model_config = ConfigDict(validate_assignment=True)

    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="请求唯一标识"
    )

    # 分析选项
    enable_constitution_analysis: bool = Field(default=True, description="启用体质分析")

    enable_emotion_analysis: bool = Field(default=True, description="启用情绪分析")

    enable_organ_analysis: bool = Field(default=True, description="启用脏腑分析")

    # 分析参数
    analysis_method: str = Field(
        default="hybrid", description="分析方法（traditional/ml_enhanced/hybrid）"
    )

    confidence_threshold: confloat(ge=0.0, le=1.0) = Field(
        default=0.6, description="置信度阈值"
    )

    # 用户信息
    user_age: int | None = Field(default=None, ge=0, le=150, description="用户年龄")

    user_gender: str | None = Field(default=None, description="用户性别")

    user_region: str | None = Field(default=None, description="用户地区（方言影响）")

    # 历史信息
    previous_diagnosis: str | None = Field(default=None, description="既往诊断")

    health_conditions: list[str] = Field(
        default_factory=list, description="已知健康状况"
    )

    # 时间戳
    timestamp: datetime = Field(default_factory=datetime.now, description="请求时间")


class TCMAnalysisResponse(BaseModel):
    """中医分析响应"""

    model_config = ConfigDict(validate_assignment=True)

    request_id: str = Field(..., description="对应的请求ID")

    success: bool = Field(default=True, description="分析是否成功")

    diagnosis: TCMDiagnosis | None = Field(default=None, description="中医诊断结果")

    processing_time: PositiveFloat = Field(..., description="处理时间（秒）")

    # 质量指标
    data_quality_score: confloat(ge=0.0, le=1.0) = Field(
        default=1.0, description="数据质量评分"
    )

    analysis_completeness: confloat(ge=0.0, le=1.0) = Field(
        default=1.0, description="分析完整性"
    )

    # 错误信息
    error_message: str | None = Field(default=None, description="错误信息")

    warnings: list[str] = Field(default_factory=list, description="警告信息")

    # 时间戳
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class TCMKnowledgeBase(BaseModel):
    """中医知识库条目"""

    model_config = ConfigDict(validate_assignment=True)

    entry_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="条目ID"
    )

    category: str = Field(..., description="知识类别")

    title: str = Field(..., description="标题")

    content: str = Field(..., description="内容")

    tags: list[str] = Field(default_factory=list, description="标签")

    source: str = Field(..., description="来源")

    reliability_score: confloat(ge=0.0, le=1.0) = Field(
        default=0.8, description="可靠性评分"
    )

    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    updated_at: datetime | None = Field(default=None, description="更新时间")
