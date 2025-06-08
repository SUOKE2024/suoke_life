"""
entities - 索克生活项目模块
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any




class Constitution(BaseModel):
    """中医体质模型"""

    id: str
    name: str = Field(..., description = "体质名称,如'平和质'、'气虚质'")
    description: str = Field(..., description = "体质描述")
    characteristics: list[str] = Field(default_factory = list, description = "体质特征")
    symptoms: list[str] = Field(default_factory = list, description = "常见症状")
    preventions: list[str] = Field(default_factory = list, description = "预防建议")
    food_recommendations: list[str] = Field(default_factory = list, description = "食物推荐")
    food_avoidances: list[str] = Field(default_factory = list, description = "忌口食物")
    prevalence: float = Field(..., description = "人群分布比例")
    biomarker_correlations: list[str] = Field(default_factory = list, description = "相关生物标志物")
    western_medicine_correlations: list[str] = Field(default_factory = list, description = "西医相关性")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Symptom(BaseModel):
    """症状模型"""

    id: str
    name: str = Field(..., description = "症状名称")
    description: str = Field(..., description = "症状描述")
    related_syndromes: list[str] = Field(default_factory = list, description = "相关证型")
    related_diseases: list[str] = Field(default_factory = list, description = "相关疾病")
    related_constitutions: list[str] = Field(default_factory = list, description = "相关体质")
    western_medicine_explanation: str = Field("", description = "西医解释")
    differential_diagnosis: list[str] = Field(default_factory = list, description = "西医鉴别诊断")
    pathophysiology: str = Field("", description = "病理生理机制")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Acupoint(BaseModel):
    """穴位模型"""

    id: str
    name: str = Field(..., description = "穴位名称,如'足三里'")
    pinyin: str = Field("", description = "拼音,如'zusanli'")
    meridian: str = Field(..., description = "所属经络")
    location: str = Field(..., description = "位置描述")
    functions: list[str] = Field(default_factory = list, description = "功效")
    indications: list[str] = Field(default_factory = list, description = "主治症状")
    manipulation: str = Field("", description = "操作方法")
    cautions: list[str] = Field(default_factory = list, description = "注意事项")
    anatomical_structure: str = Field("", description = "解剖学结构")
    neural_connections: list[str] = Field(default_factory = list, description = "神经连接")
    research_evidence: list[str] = Field(default_factory = list, description = "研究证据")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Herb(BaseModel):
    """中药模型"""

    id: str
    name: str = Field(..., description = "中药名称")
    pinyin: str = Field("", description = "拼音")
    category: str = Field(..., description = "分类,如'解表药'")
    nature: str = Field(..., description = "药性,如'温'")
    flavor: str = Field(..., description = "味道,如'辛'")
    meridian_tropism: str = Field("", description = "归经")
    efficacy: str = Field(..., description = "功效")
    indications: list[str] = Field(default_factory = list, description = "主治")
    dosage: str = Field("", description = "用量")
    cautions: list[str] = Field(default_factory = list, description = "禁忌")
    common_pairs: list[str] = Field(default_factory = list, description = "常用配伍")
    modern_research: str = Field("", description = "现代研究")
    active_compounds: list[str] = Field(default_factory = list, description = "活性化合物")
    pharmacological_effects: list[str] = Field(default_factory = list, description = "药理作用")
    clinical_studies: list[str] = Field(default_factory = list, description = "临床研究")
    western_drug_interactions: list[str] = Field(default_factory = list, description = "西药相互作用")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DiagnosisEvidence(BaseModel):
    """诊断依据模型"""

    type: str = Field(..., description = "依据类型,如'tongue', 'pulse', 'symptom'")
    description: str = Field(..., description = "描述")
    weight: float = Field(1.0, description = "权重")


class DiagnosisStep(BaseModel):
    """诊断步骤模型"""

    step_number: int = Field(..., description = "步骤序号")
    description: str = Field(..., description = "步骤描述")
    evidence: list[DiagnosisEvidence] = Field(default_factory = list, description = "诊断依据")
    differential_points: list[str] = Field(default_factory = list, description = "鉴别要点")
    biomarker_references: list[str] = Field(default_factory = list, description = "生物标志物参考")


class DiagnosisPathway(BaseModel):
    """辨证路径模型"""

    id: str
    name: str = Field(..., description = "路径名称")
    description: str = Field(..., description = "路径描述")
    steps: list[DiagnosisStep] = Field(default_factory = list, description = "诊断步骤")
    western_medicine_alignment: str = Field("", description = "西医对应关系")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Syndrome(BaseModel):
    """证型模型"""

    id: str
    name: str = Field(..., description = "证型名称,如'肝郁脾虚证'")
    description: str = Field(..., description = "证型描述")
    key_symptoms: list[str] = Field(default_factory = list, description = "主要症状")
    tongue_features: list[str] = Field(default_factory = list, description = "舌象特征")
    pulse_features: list[str] = Field(default_factory = list, description = "脉象特征")
    western_correlations: list[str] = Field(default_factory = list, description = "西医相关性")
    biomarker_patterns: list[str] = Field(default_factory = list, description = "生物标志物模式")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Recommendation(BaseModel):
    """推荐模型"""

    id: str
    type: str = Field(..., description = "推荐类型")
    title: str = Field(..., description = "标题")
    description: str = Field(..., description = "描述")
    relevance_score: float = Field(..., description = "相关性评分")
    evidence: str = Field("", description = "证据来源")
    evidence_level: str = Field("", description = "证据级别")
    western_medicine_rationale: str = Field("", description = "西医理论依据")
    tcm_rationale: str = Field("", description = "中医理论依据")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Biomarker(BaseModel):
    """生物标志物模型"""

    id: str
    name: str = Field(..., description = "标志物名称")
    category: str = Field(..., description = "分类,如'炎症因子'、'代谢物'")
    description: str = Field(..., description = "描述")
    normal_range: str = Field(..., description = "正常范围")
    significance: str = Field(..., description = "临床意义")
    related_diseases: list[str] = Field(default_factory = list, description = "相关疾病")
    related_syndromes: list[str] = Field(default_factory = list, description = "相关证型")
    related_constitutions: list[str] = Field(default_factory = list, description = "相关体质")
    monitoring_frequency: str = Field("", description = "监测频率建议")
    intervention_thresholds: dict[str, str] = Field(default_factory = dict, description = "干预阈值")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WesternDisease(BaseModel):
    """西医疾病模型"""

    id: str
    name: str = Field(..., description = "疾病名称")
    icd_code: str = Field("", description = "ICD编码")
    description: str = Field(..., description = "描述")
    etiology: str = Field("", description = "病因学")
    pathophysiology: str = Field("", description = "病理生理学")
    risk_factors: list[str] = Field(default_factory = list, description = "危险因素")
    screening_methods: list[str] = Field(default_factory = list, description = "筛查方法")
    prevention_strategies: list[str] = Field(default_factory = list, description = "预防策略")
    tcm_correlations: list[str] = Field(default_factory = list, description = "中医相关性")
    early_signs: list[str] = Field(default_factory = list, description = "早期信号")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PreventionEvidence(BaseModel):
    """预防医学证据模型"""

    id: str
    title: str = Field(..., description = "标题")
    category: str = Field(..., description = "分类,如'饮食'、'运动'、'生活方式'")
    description: str = Field(..., description = "描述")
    evidence_level: str = Field(..., description = "证据级别,如'A'、'B'、'C'")
    source_type: str = Field(..., description = "来源类型,如'临床研究'、'流行病学'")
    source_details: str = Field(..., description = "来源详情")
    effectiveness: float = Field(..., description = "有效性评分")
    applicable_populations: list[str] = Field(default_factory = list, description = "适用人群")
    contraindications: list[str] = Field(default_factory = list, description = "禁忌")
    implementation_guide: str = Field("", description = "实施指南")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IntegratedTreatment(BaseModel):
    """中西医结合治疗方案模型"""

    id: str
    name: str = Field(..., description = "方案名称")
    target_condition: str = Field(..., description = "目标状况")
    description: str = Field(..., description = "方案描述")
    tcm_components: list[dict[str, Any]] = Field(default_factory = list, description = "中医组成部分")
    western_components: list[dict[str, Any]] = Field(
        default_factory = list, description = "西医组成部分"
    )
    integration_rationale: str = Field(..., description = "结合理由")
    expected_outcomes: list[str] = Field(default_factory = list, description = "预期效果")
    evidence_base: str = Field("", description = "证据基础")
    personalization_factors: list[str] = Field(default_factory = list, description = "个性化因素")
    monitoring_metrics: list[str] = Field(default_factory = list, description = "监测指标")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LifestyleIntervention(BaseModel):
    """生活方式干预模型"""

    id: str
    name: str = Field(..., description = "干预名称")
    category: str = Field(..., description = "分类,如'饮食'、'运动'、'睡眠'")
    description: str = Field(..., description = "描述")
    protocol: str = Field(..., description = "具体方案")
    scientific_basis: str = Field(..., description = "科学依据")
    tcm_principles: str = Field(..., description = "中医原理")
    suitable_constitutions: list[str] = Field(default_factory = list, description = "适合体质")
    contraindicated_constitutions: list[str] = Field(default_factory = list, description = "禁忌体质")
    health_metrics: list[str] = Field(default_factory = list, description = "健康指标")
    success_factors: list[str] = Field(default_factory = list, description = "成功因素")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SearchResult(BaseModel):
    """搜索结果模型"""

    id: str
    name: str
    entity_type: str = Field(..., description = "实体类型")
    brief: str = Field("", description = "简要描述")
    relevance_score: float


class PaginatedResponse(BaseModel):
    """分页响应基础模型"""

    total: int
    limit: int
    offset: int


class ConstitutionListResponse(PaginatedResponse):
    """体质列表响应"""

    data: list[Constitution]


class SymptomListResponse(PaginatedResponse):
    """症状列表响应"""

    data: list[Symptom]


class AcupointListResponse(PaginatedResponse):
    """穴位列表响应"""

    data: list[Acupoint]


class HerbListResponse(PaginatedResponse):
    """中药列表响应"""

    data: list[Herb]


class SyndromeListResponse(PaginatedResponse):
    """证型列表响应"""

    data: list[Syndrome]


class SearchResponse(PaginatedResponse):
    """搜索响应模型"""

    data: list[SearchResult]


class SyndromePathwaysResponse(BaseModel):
    """证型路径响应"""

    syndrome: Syndrome
    pathways: list[DiagnosisPathway]


class RecommendationListResponse(BaseModel):
    """推荐列表响应"""

    data: list[Recommendation]
    total: int


class BiomarkerListResponse(PaginatedResponse):
    """生物标志物列表响应"""

    data: list[Biomarker]


class WesternDiseaseListResponse(PaginatedResponse):
    """西医疾病列表响应"""

    data: list[WesternDisease]


class PreventionEvidenceListResponse(PaginatedResponse):
    """预防医学证据列表响应"""

    data: list[PreventionEvidence]


class IntegratedTreatmentListResponse(PaginatedResponse):
    """中西医结合治疗方案列表响应"""

    data: list[IntegratedTreatment]


class LifestyleInterventionListResponse(PaginatedResponse):
    """生活方式干预列表响应"""

    data: list[LifestyleIntervention]


class ErrorResponse(BaseModel):
    """错误响应模型"""

    code: str
    message: str
    details: dict | None = None
    request_id: str | None = None
