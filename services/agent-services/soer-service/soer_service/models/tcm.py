"""
中医相关数据模型

包含体质、经络、中药等中医理论的数字化模型
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class TCMConstitution(str, Enum):
    """中医体质类型"""
    PING_HE = "平和质"  # 平和体质
    QI_XU = "气虚质"    # 气虚体质
    YANG_XU = "阳虚质"  # 阳虚体质
    YIN_XU = "阴虚质"   # 阴虚体质
    TAN_SHI = "痰湿质"  # 痰湿体质
    SHI_RE = "湿热质"   # 湿热体质
    XUE_YU = "血瘀质"   # 血瘀体质
    QI_YU = "气郁质"    # 气郁体质
    TE_BING = "特禀质"  # 特禀体质


class TCMElement(str, Enum):
    """五行元素"""
    WOOD = "木"    # 木
    FIRE = "火"    # 火
    EARTH = "土"   # 土
    METAL = "金"   # 金
    WATER = "水"   # 水


class TCMOrgan(str, Enum):
    """中医脏腑"""
    HEART = "心"      # 心
    LIVER = "肝"      # 肝
    SPLEEN = "脾"     # 脾
    LUNG = "肺"       # 肺
    KIDNEY = "肾"     # 肾
    PERICARDIUM = "心包"  # 心包
    TRIPLE_HEATER = "三焦"  # 三焦
    GALLBLADDER = "胆"    # 胆
    STOMACH = "胃"        # 胃
    SMALL_INTESTINE = "小肠"  # 小肠
    LARGE_INTESTINE = "大肠"  # 大肠
    BLADDER = "膀胱"      # 膀胱


class MeridianType(str, Enum):
    """经络类型"""
    TWELVE_REGULAR = "十二正经"
    EIGHT_EXTRAORDINARY = "奇经八脉"
    FIFTEEN_COLLATERALS = "十五络脉"


class ConstitutionAssessment(BaseModel):
    """体质评估"""
    assessment_id: str = Field(..., description="评估ID")
    user_id: str = Field(..., description="用户ID")
    assessment_date: datetime = Field(default_factory=datetime.now, description="评估日期")
    
    # 评估问卷结果
    questionnaire_scores: Dict[TCMConstitution, float] = Field(..., description="各体质得分")
    primary_constitution: TCMConstitution = Field(..., description="主要体质")
    secondary_constitution: Optional[TCMConstitution] = Field(None, description="次要体质")
    constitution_confidence: float = Field(..., ge=0, le=1, description="体质判断置信度")
    
    # 体质特征
    physical_characteristics: List[str] = Field(default_factory=list, description="体格特征")
    psychological_characteristics: List[str] = Field(default_factory=list, description="心理特征")
    pathological_tendencies: List[str] = Field(default_factory=list, description="发病倾向")
    
    # 调养建议
    lifestyle_recommendations: List[str] = Field(default_factory=list, description="生活起居建议")
    dietary_recommendations: List[str] = Field(default_factory=list, description="饮食调养建议")
    exercise_recommendations: List[str] = Field(default_factory=list, description="运动保健建议")
    emotional_recommendations: List[str] = Field(default_factory=list, description="情志调摄建议")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class MeridianPoint(BaseModel):
    """经络穴位"""
    point_id: str = Field(..., description="穴位ID")
    name: str = Field(..., description="穴位名称")
    pinyin: str = Field(..., description="拼音")
    english_name: Optional[str] = Field(None, description="英文名称")
    
    # 穴位分类
    meridian: TCMOrgan = Field(..., description="所属经络")
    meridian_type: MeridianType = Field(..., description="经络类型")
    point_category: str = Field(..., description="穴位分类")
    
    # 穴位定位
    location_description: str = Field(..., description="定位描述")
    anatomical_location: str = Field(..., description="解剖位置")
    coordinates: Optional[Dict[str, float]] = Field(None, description="坐标位置")
    
    # 穴位功效
    primary_functions: List[str] = Field(..., description="主要功效")
    indications: List[str] = Field(..., description="主治病症")
    contraindications: List[str] = Field(default_factory=list, description="禁忌症")
    
    # 操作方法
    acupuncture_method: Optional[str] = Field(None, description="针刺方法")
    moxibustion_method: Optional[str] = Field(None, description="艾灸方法")
    massage_method: Optional[str] = Field(None, description="按摩方法")
    
    # 配伍
    compatible_points: List[str] = Field(default_factory=list, description="配伍穴位")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class ChineseMedicine(BaseModel):
    """中药材"""
    medicine_id: str = Field(..., description="药材ID")
    name: str = Field(..., description="中文名称")
    pinyin: str = Field(..., description="拼音")
    latin_name: Optional[str] = Field(None, description="拉丁学名")
    aliases: List[str] = Field(default_factory=list, description="别名")
    
    # 药材属性
    nature: str = Field(..., description="性味")  # 如：寒、热、温、凉、平
    flavor: List[str] = Field(..., description="味")  # 如：甘、苦、辛、酸、咸
    meridian_tropism: List[TCMOrgan] = Field(..., description="归经")
    
    # 功效主治
    primary_effects: List[str] = Field(..., description="主要功效")
    indications: List[str] = Field(..., description="主治病症")
    contraindications: List[str] = Field(default_factory=list, description="禁忌")
    
    # 用法用量
    dosage_range: str = Field(..., description="用量范围")
    administration_methods: List[str] = Field(..., description="用法")
    
    # 配伍
    compatible_medicines: List[str] = Field(default_factory=list, description="配伍药材")
    incompatible_medicines: List[str] = Field(default_factory=list, description="相反药材")
    
    # 现代研究
    active_compounds: List[str] = Field(default_factory=list, description="有效成分")
    pharmacological_effects: List[str] = Field(default_factory=list, description="药理作用")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class TCMDiagnosis(BaseModel):
    """中医诊断"""
    diagnosis_id: str = Field(..., description="诊断ID")
    user_id: str = Field(..., description="用户ID")
    diagnosis_date: datetime = Field(default_factory=datetime.now, description="诊断日期")
    
    # 四诊信息
    inspection_findings: Dict[str, Any] = Field(default_factory=dict, description="望诊所见")
    auscultation_findings: Dict[str, Any] = Field(default_factory=dict, description="闻诊所见")
    inquiry_findings: Dict[str, Any] = Field(default_factory=dict, description="问诊所见")
    palpation_findings: Dict[str, Any] = Field(default_factory=dict, description="切诊所见")
    
    # 辨证结果
    syndrome_differentiation: str = Field(..., description="辨证结果")
    pathogenesis: str = Field(..., description="病机分析")
    constitution_analysis: TCMConstitution = Field(..., description="体质分析")
    
    # 治疗原则
    treatment_principle: str = Field(..., description="治疗原则")
    treatment_methods: List[str] = Field(..., description="治疗方法")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class TCMPrescription(BaseModel):
    """中医处方"""
    prescription_id: str = Field(..., description="处方ID")
    user_id: str = Field(..., description="用户ID")
    diagnosis_id: str = Field(..., description="关联诊断ID")
    prescription_name: str = Field(..., description="方剂名称")
    
    # 处方组成
    medicines: List[Dict[str, Union[str, float]]] = Field(..., description="药物组成")
    # 格式: [{"medicine_id": "xxx", "name": "xxx", "dosage": 10.0, "unit": "g"}]
    
    # 煎服方法
    preparation_method: str = Field(..., description="煎煮方法")
    administration_schedule: str = Field(..., description="服用方法")
    course_duration: str = Field(..., description="疗程")
    
    # 注意事项
    precautions: List[str] = Field(default_factory=list, description="注意事项")
    dietary_restrictions: List[str] = Field(default_factory=list, description="饮食禁忌")
    
    # 方解
    formula_analysis: Optional[str] = Field(None, description="方解")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class TCMTreatmentPlan(BaseModel):
    """中医治疗方案"""
    plan_id: str = Field(..., description="方案ID")
    user_id: str = Field(..., description="用户ID")
    diagnosis_id: str = Field(..., description="关联诊断ID")
    plan_name: str = Field(..., description="方案名称")
    
    # 治疗目标
    treatment_goals: List[str] = Field(..., description="治疗目标")
    expected_duration: str = Field(..., description="预期疗程")
    
    # 治疗方法
    herbal_prescription: Optional[str] = Field(None, description="中药处方ID")
    acupuncture_plan: List[str] = Field(default_factory=list, description="针灸方案")
    massage_plan: List[str] = Field(default_factory=list, description="推拿方案")
    cupping_plan: Optional[str] = Field(None, description="拔罐方案")
    moxibustion_plan: Optional[str] = Field(None, description="艾灸方案")
    
    # 生活调理
    lifestyle_adjustments: List[str] = Field(default_factory=list, description="生活调理")
    dietary_therapy: List[str] = Field(default_factory=list, description="食疗方案")
    exercise_therapy: List[str] = Field(default_factory=list, description="运动疗法")
    emotional_regulation: List[str] = Field(default_factory=list, description="情志调节")
    
    # 随访计划
    follow_up_schedule: List[Dict[str, Any]] = Field(default_factory=list, description="随访计划")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class TCMHealthAssessment(BaseModel):
    """中医健康评估"""
    assessment_id: str = Field(..., description="评估ID")
    user_id: str = Field(..., description="用户ID")
    assessment_type: str = Field(..., description="评估类型")
    
    # 评估结果
    overall_score: float = Field(..., ge=0, le=100, description="总体评分")
    constitution_score: float = Field(..., ge=0, le=100, description="体质评分")
    qi_blood_score: float = Field(..., ge=0, le=100, description="气血评分")
    organ_scores: Dict[TCMOrgan, float] = Field(..., description="脏腑评分")
    
    # 健康状态
    health_status: str = Field(..., description="健康状态")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    protective_factors: List[str] = Field(default_factory=list, description="保护因素")
    
    # 调养建议
    constitution_recommendations: List[str] = Field(default_factory=list, description="体质调养建议")
    seasonal_recommendations: List[str] = Field(default_factory=list, description="时令调养建议")
    preventive_recommendations: List[str] = Field(default_factory=list, description="预防保健建议")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


# 请求和响应模型
class ConstitutionAssessmentRequest(BaseModel):
    """体质评估请求"""
    questionnaire_answers: Dict[str, Any] = Field(..., description="问卷答案")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="附加信息")


class TCMConsultationRequest(BaseModel):
    """中医咨询请求"""
    symptoms: List[str] = Field(..., description="症状描述")
    duration: Optional[str] = Field(None, description="病程")
    severity: Optional[str] = Field(None, description="严重程度")
    triggers: Optional[List[str]] = Field(None, description="诱发因素")
    previous_treatments: Optional[List[str]] = Field(None, description="既往治疗")
    constitution_type: Optional[TCMConstitution] = Field(None, description="已知体质类型")


class MeridianAnalysisRequest(BaseModel):
    """经络分析请求"""
    symptoms: List[str] = Field(..., description="症状")
    affected_areas: List[str] = Field(..., description="不适部位")
    constitution_type: Optional[TCMConstitution] = Field(None, description="体质类型")


class TCMRecommendationResponse(BaseModel):
    """中医建议响应"""
    recommendation_id: str = Field(..., description="建议ID")
    recommendation_type: str = Field(..., description="建议类型")
    
    # 诊断分析
    syndrome_analysis: Optional[str] = Field(None, description="证候分析")
    constitution_analysis: Optional[str] = Field(None, description="体质分析")
    
    # 治疗建议
    herbal_recommendations: List[str] = Field(default_factory=list, description="中药建议")
    acupuncture_points: List[str] = Field(default_factory=list, description="针灸穴位")
    massage_techniques: List[str] = Field(default_factory=list, description="按摩手法")
    
    # 生活调理
    dietary_suggestions: List[str] = Field(default_factory=list, description="饮食建议")
    lifestyle_adjustments: List[str] = Field(default_factory=list, description="生活调理")
    exercise_recommendations: List[str] = Field(default_factory=list, description="运动建议")
    
    # 注意事项
    precautions: List[str] = Field(default_factory=list, description="注意事项")
    contraindications: List[str] = Field(default_factory=list, description="禁忌事项")
    
    # 随访建议
    follow_up_suggestions: List[str] = Field(default_factory=list, description="随访建议")
    
    confidence_score: float = Field(..., ge=0, le=1, description="建议置信度")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")