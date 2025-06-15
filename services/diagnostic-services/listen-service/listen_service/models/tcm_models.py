"""
中医相关数据模型

定义中医诊断和分析相关的数据结构。
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, validator


class ConstitutionType(str, Enum):
    """体质类型（九种体质）"""
    BALANCED = "平和质"           # 平和质
    QI_DEFICIENCY = "气虚质"      # 气虚质
    YANG_DEFICIENCY = "阳虚质"    # 阳虚质
    YIN_DEFICIENCY = "阴虚质"     # 阴虚质
    PHLEGM_DAMPNESS = "痰湿质"    # 痰湿质
    DAMP_HEAT = "湿热质"         # 湿热质
    BLOOD_STASIS = "血瘀质"      # 血瘀质
    QI_STAGNATION = "气郁质"     # 气郁质
    SPECIAL = "特禀质"           # 特禀质


class EmotionState(str, Enum):
    """情志状态（五志）"""
    JOY = "喜"      # 喜（心志）
    ANGER = "怒"    # 怒（肝志）
    WORRY = "思"    # 思（脾志）
    SADNESS = "忧"  # 忧（肺志）
    FEAR = "恐"     # 恐（肾志）
    BALANCED = "平和"  # 情志平和


class VoiceQuality(str, Enum):
    """声音质量"""
    CLEAR = "清亮"      # 清亮
    HOARSE = "嘶哑"     # 嘶哑
    WEAK = "微弱"       # 微弱
    ROUGH = "粗糙"      # 粗糙
    TREMBLING = "颤抖"  # 颤抖
    NASAL = "鼻音"      # 鼻音


class SpeechPattern(str, Enum):
    """语音模式"""
    FLUENT = "流利"        # 流利
    HESITANT = "犹豫"      # 犹豫
    RAPID = "急促"         # 急促
    SLOW = "缓慢"          # 缓慢
    INTERRUPTED = "断续"   # 断续


class VoiceCharacteristics(BaseModel):
    """声音特征"""
    pitch_range: Tuple[float, float] = Field(..., description="音调范围（Hz）")
    volume_level: float = Field(..., description="音量水平", ge=0, le=1)
    clarity_score: float = Field(..., description="清晰度评分", ge=0, le=1)
    stability_score: float = Field(..., description="稳定性评分", ge=0, le=1)
    speech_rate: float = Field(..., description="语速（词/分钟）", ge=0)
    tremor_level: float = Field(..., description="颤抖程度", ge=0, le=1)
    breath_pattern: str = Field(..., description="呼吸模式")
    voice_quality: VoiceQuality = Field(..., description="声音质量")
    emotional_tone: str = Field(..., description="情感色调")
    
    @validator('pitch_range')
    def validate_pitch_range(cls, v):
        if v[0] < 0 or v[1] < 0 or v[0] > v[1]:
            raise ValueError('音调范围无效')
        return v


class OrganFunction(BaseModel):
    """脏腑功能"""
    organ: str = Field(..., description="脏腑名称")
    function_score: float = Field(..., description="功能评分", ge=0, le=1)
    status: str = Field(..., description="功能状态")
    indicators: List[str] = Field(default_factory=list, description="功能指标")
    
    @validator('organ')
    def validate_organ(cls, v):
        valid_organs = ["心", "肝", "脾", "肺", "肾", "heart", "liver", "spleen", "lung", "kidney"]
        if v not in valid_organs:
            raise ValueError(f'无效的脏腑名称: {v}')
        return v


class ConstitutionAnalysis(BaseModel):
    """体质分析"""
    primary_constitution: ConstitutionType = Field(..., description="主要体质")
    secondary_constitution: Optional[ConstitutionType] = Field(None, description="次要体质")
    constitution_scores: Dict[ConstitutionType, float] = Field(..., description="体质评分")
    confidence_score: float = Field(..., description="置信度", ge=0, le=1)
    characteristics: List[str] = Field(default_factory=list, description="体质特征")
    
    @validator('constitution_scores')
    def validate_scores(cls, v):
        for score in v.values():
            if not 0 <= score <= 1:
                raise ValueError('体质评分必须在0-1之间')
        return v


class EmotionAnalysis(BaseModel):
    """情志分析"""
    primary_emotion: EmotionState = Field(..., description="主要情志")
    emotion_scores: Dict[EmotionState, float] = Field(..., description="情志评分")
    emotional_balance: float = Field(..., description="情志平衡度", ge=0, le=1)
    stress_level: float = Field(..., description="压力水平", ge=0, le=1)
    emotional_indicators: List[str] = Field(default_factory=list, description="情志指标")
    
    @validator('emotion_scores')
    def validate_emotion_scores(cls, v):
        for score in v.values():
            if not 0 <= score <= 1:
                raise ValueError('情志评分必须在0-1之间')
        return v


class TCMPattern(BaseModel):
    """中医证型"""
    pattern_name: str = Field(..., description="证型名称")
    pattern_score: float = Field(..., description="证型评分", ge=0, le=1)
    symptoms: List[str] = Field(default_factory=list, description="相关症状")
    treatment_principles: List[str] = Field(default_factory=list, description="治疗原则")


class TCMRecommendation(BaseModel):
    """中医调理建议"""
    category: str = Field(..., description="建议类别")
    content: str = Field(..., description="建议内容")
    priority: int = Field(..., description="优先级", ge=1, le=5)
    duration: Optional[str] = Field(None, description="建议持续时间")
    precautions: List[str] = Field(default_factory=list, description="注意事项")


class TCMDiagnosis(BaseModel):
    """中医诊断结果"""
    voice_characteristics: VoiceCharacteristics = Field(..., description="声音特征")
    constitution_type: Optional[ConstitutionType] = Field(None, description="体质类型")
    emotion_state: Optional[EmotionState] = Field(None, description="情志状态")
    organ_functions: List[OrganFunction] = Field(default_factory=list, description="脏腑功能")
    
    # 详细分析
    constitution_analysis: Optional[ConstitutionAnalysis] = Field(None, description="体质分析")
    emotion_analysis: Optional[EmotionAnalysis] = Field(None, description="情志分析")
    patterns: List[TCMPattern] = Field(default_factory=list, description="证型分析")
    
    # 建议和评估
    recommendations: List[str] = Field(default_factory=list, description="调理建议")
    detailed_recommendations: List[TCMRecommendation] = Field(default_factory=list, description="详细建议")
    confidence_score: float = Field(..., description="诊断置信度", ge=0, le=1)
    analysis_timestamp: float = Field(..., description="分析时间戳")
    
    # 附加信息
    notes: Optional[str] = Field(None, description="诊断备注")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="随访建议")


class TCMKnowledgeBase(BaseModel):
    """中医知识库"""
    constitution_descriptions: Dict[ConstitutionType, str] = Field(..., description="体质描述")
    emotion_descriptions: Dict[EmotionState, str] = Field(..., description="情志描述")
    organ_functions_descriptions: Dict[str, str] = Field(..., description="脏腑功能描述")
    pattern_database: List[TCMPattern] = Field(default_factory=list, description="证型数据库")
    
    @classmethod
    def get_default_knowledge_base(cls) -> "TCMKnowledgeBase":
        """获取默认知识库"""
        return cls(
            constitution_descriptions={
                ConstitutionType.BALANCED: "体形匀称健壮，面色润泽，精力充沛，脏腑功能状态强健壮实",
                ConstitutionType.QI_DEFICIENCY: "元气不足，以疲乏、气短、自汗等气虚表现为主要特征",
                ConstitutionType.YANG_DEFICIENCY: "阳气不足，以畏寒怕冷、手足不温等虚寒表现为主要特征",
                ConstitutionType.YIN_DEFICIENCY: "阴液亏少，以口燥咽干、手足心热等虚热表现为主要特征",
                ConstitutionType.PHLEGM_DAMPNESS: "痰湿凝聚，以形体肥胖、腹部肥满、口黏苔腻等痰湿表现为主要特征",
                ConstitutionType.DAMP_HEAT: "湿热内蕴，以面垢油腻、口苦、苔黄腻等湿热表现为主要特征",
                ConstitutionType.BLOOD_STASIS: "血行不畅，以肤色晦黯、舌质紫黯等血瘀表现为主要特征",
                ConstitutionType.QI_STAGNATION: "气机郁滞，以神情抑郁、忧虑脆弱等气郁表现为主要特征",
                ConstitutionType.SPECIAL: "先天失常，以生理缺陷、过敏反应等为主要特征"
            },
            emotion_descriptions={
                EmotionState.JOY: "心志过度，表现为兴奋过度、心神不宁",
                EmotionState.ANGER: "肝气郁结，表现为易怒、烦躁、情绪波动",
                EmotionState.WORRY: "脾气虚弱，表现为思虑过度、忧愁不解",
                EmotionState.SADNESS: "肺气不宣，表现为悲伤、忧郁、气短",
                EmotionState.FEAR: "肾气不足，表现为恐惧、惊慌、胆怯",
                EmotionState.BALANCED: "情志调和，心情平静，情绪稳定"
            },
            organ_functions_descriptions={
                "heart": "心主血脉，藏神，主神明，开窍于舌",
                "liver": "肝主疏泄，藏血，主筋，开窍于目",
                "spleen": "脾主运化，统血，主肌肉，开窍于口",
                "lung": "肺主气，司呼吸，主宣发肃降，开窍于鼻",
                "kidney": "肾主水，藏精，主骨生髓，开窍于耳"
            }
        )


class TCMAnalysisConfig(BaseModel):
    """中医分析配置"""
    enable_constitution_analysis: bool = Field(default=True, description="启用体质分析")
    enable_emotion_analysis: bool = Field(default=True, description="启用情志分析")
    enable_organ_analysis: bool = Field(default=True, description="启用脏腑分析")
    enable_pattern_analysis: bool = Field(default=False, description="启用证型分析")
    
    # 分析参数
    constitution_threshold: float = Field(default=0.6, description="体质判定阈值", ge=0, le=1)
    emotion_threshold: float = Field(default=0.5, description="情志判定阈值", ge=0, le=1)
    organ_threshold: float = Field(default=0.4, description="脏腑功能阈值", ge=0, le=1)
    
    # 置信度设置
    min_confidence: float = Field(default=0.3, description="最小置信度", ge=0, le=1)
    high_confidence: float = Field(default=0.8, description="高置信度阈值", ge=0, le=1)
    
    # 知识库设置
    use_knowledge_base: bool = Field(default=True, description="使用知识库")
    knowledge_base_version: str = Field(default="1.0", description="知识库版本")


class TCMAnalysisResult(BaseModel):
    """中医分析结果"""
    request_id: str = Field(..., description="请求ID")
    diagnosis: TCMDiagnosis = Field(..., description="中医诊断")
    analysis_config: TCMAnalysisConfig = Field(..., description="分析配置")
    processing_time: float = Field(..., description="处理时间", ge=0)
    timestamp: float = Field(..., description="分析时间戳")
    
    # 质量评估
    data_quality: str = Field(..., description="数据质量评估")
    reliability_score: float = Field(..., description="可靠性评分", ge=0, le=1)
    
    # 元数据
    analyzer_version: str = Field(default="1.0.0", description="分析器版本")
    model_version: str = Field(default="1.0.0", description="模型版本")