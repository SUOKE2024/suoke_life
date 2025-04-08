"""
知识图谱结构定义
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    # 基础节点类型
    BASE = "Base"
    # 传统中医节点类型
    TCM = "TCM"
    HERB = "Herb"
    PRESCRIPTION = "Prescription"
    SYMPTOM = "Symptom"
    CONSTITUTION = "Constitution"
    ACUPOINT = "Acupoint"
    DIAGNOSIS = "Diagnosis"
    TCM_KNOWLEDGE = "TCMKnowledge"
    # 现代医学节点类型
    MODERN_MEDICINE = "ModernMedicine"
    # 扩展节点类型
    PRECISION_MEDICINE = "PrecisionMedicine"
    MULTIMODAL_HEALTH = "MultimodalHealth"
    ENVIRONMENTAL_HEALTH = "EnvironmentalHealth"
    MENTAL_HEALTH = "MentalHealth"


class RelationshipType(str, Enum):
    # 中医关系
    TREATS = "TREATS"
    CONTAINS = "CONTAINS"
    BELONGS_TO = "BELONGS_TO"
    INDICATES = "INDICATES"
    LOCATED_AT = "LOCATED_AT"
    CONNECTED_TO = "CONNECTED_TO"
    AFFECTS = "AFFECTS"
    # 现代医学关系
    CAUSES = "CAUSES"
    PREVENTS = "PREVENTS"
    DIAGNOSES = "DIAGNOSES"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    # 扩展关系
    INTERACTS_WITH = "INTERACTS_WITH"
    MEASURED_BY = "MEASURED_BY"
    INFLUENCED_BY = "INFLUENCED_BY"
    ANALYZED_BY = "ANALYZED_BY"
    RISK_FACTOR_FOR = "RISK_FACTOR_FOR"
    PROTECTIVE_FOR = "PROTECTIVE_FOR"
    BIOMARKER_OF = "BIOMARKER_OF"
    CONTRAINDICATES = "CONTRAINDICATES"


# 基础节点模型
class BaseNodeModel(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    summary: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: str = "published"
    vector_id: Optional[str] = None
    node_type: NodeType = NodeType.BASE


# 精准医学节点模型
class PrecisionMedicineNode(BaseNodeModel):
    node_type: NodeType = NodeType.PRECISION_MEDICINE
    study_type: str
    confidence_level: str
    relevant_genes: List[str] = Field(default_factory=list)
    snp_references: List[str] = Field(default_factory=list)
    sample_size: Optional[int] = None
    population_groups: List[str] = Field(default_factory=list)
    heritability: Optional[float] = None
    technical_platform: Optional[str] = None
    nutrient_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    drug_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    disease_associations: List[Dict[str, Any]] = Field(default_factory=list)
    environmental_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    personalization_factors: List[str] = Field(default_factory=list)
    recommendation_algorithm: Optional[str] = None
    applicable_biomarkers: List[str] = Field(default_factory=list)
    
    def get_text_for_embedding(self) -> str:
        """生成用于嵌入向量的文本表示"""
        texts = [f"{self.title}. {self.content}"]
        
        if self.relevant_genes:
            texts.append(f"相关基因: {', '.join(self.relevant_genes)}")
            
        if self.disease_associations:
            disease_texts = [f"{da['disease']}(风险因子:{da['risk_factor']})" 
                           for da in self.disease_associations]
            texts.append(f"疾病关联: {', '.join(disease_texts)}")
            
        if self.nutrient_interactions:
            nutrient_texts = [f"{ni['nutrient']}({ni['effect']})" 
                            for ni in self.nutrient_interactions]
            texts.append(f"营养素相互作用: {', '.join(nutrient_texts)}")
            
        if self.drug_interactions:
            drug_texts = [f"{di['drug']}({di['effect']})" 
                        for di in self.drug_interactions]
            texts.append(f"药物相互作用: {', '.join(drug_texts)}")
            
        return ". ".join(texts)


# 多模态健康节点模型
class MultimodalHealthNode(BaseNodeModel):
    node_type: NodeType = NodeType.MULTIMODAL_HEALTH
    modality_type: str
    analysis_method: str
    data_requirements: List[str] = Field(default_factory=list)
    privacy_considerations: Optional[str] = None
    image_features: List[Dict[str, Any]] = Field(default_factory=list)
    audio_features: List[Dict[str, Any]] = Field(default_factory=list)
    wearable_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    environmental_factors: List[Dict[str, Any]] = Field(default_factory=list)
    data_fusion_techniques: List[str] = Field(default_factory=list)
    machine_learning_summary: Optional[str] = None
    validation_results: Optional[str] = None
    limitations_and_caveats: Optional[str] = None
    
    def get_text_for_embedding(self) -> str:
        """生成用于嵌入向量的文本表示"""
        texts = [f"{self.title}. {self.content}"]
        
        texts.append(f"数据模态: {self.modality_type}. 分析方法: {self.analysis_method}")
        
        if self.data_requirements:
            texts.append(f"数据要求: {', '.join(self.data_requirements)}")
            
        if self.image_features:
            feature_texts = [f"{feature['feature']}({feature['significance']})" 
                           for feature in self.image_features]
            texts.append(f"图像特征: {', '.join(feature_texts)}")
            
        if self.audio_features:
            feature_texts = [f"{feature['feature']}({feature['significance']})" 
                           for feature in self.audio_features]
            texts.append(f"音频特征: {', '.join(feature_texts)}")
            
        if self.wearable_metrics:
            metric_texts = [f"{metric['metric']}({', '.join(metric.get('correlated_conditions', []))})" 
                          for metric in self.wearable_metrics]
            texts.append(f"可穿戴设备指标: {', '.join(metric_texts)}")
            
        return ". ".join(texts)


# 环境健康节点模型
class EnvironmentalHealthNode(BaseNodeModel):
    node_type: NodeType = NodeType.ENVIRONMENTAL_HEALTH
    environmental_factor: str
    factor_type: str
    exposure_routes: List[str] = Field(default_factory=list)
    spatial_scale: str
    temporal_pattern: str
    health_effects: List[Dict[str, Any]] = Field(default_factory=list)
    measurement_methods: List[str] = Field(default_factory=list)
    monitoring_guidelines: Optional[str] = None
    safety_standards: List[Dict[str, Any]] = Field(default_factory=list)
    prevention_strategies: List[str] = Field(default_factory=list)
    remedial_actions: List[str] = Field(default_factory=list)
    policy_recommendations: List[str] = Field(default_factory=list)
    seasonal_variations: Optional[str] = None
    weather_dependence: Optional[str] = None
    climate_change_implications: Optional[str] = None
    
    def get_text_for_embedding(self) -> str:
        """生成用于嵌入向量的文本表示"""
        texts = [f"{self.title}. {self.content}"]
        
        texts.append(f"环境因素: {self.environmental_factor}, 类型: {self.factor_type}")
        
        if self.exposure_routes:
            texts.append(f"暴露途径: {', '.join(self.exposure_routes)}")
            
        if self.health_effects:
            effect_texts = [f"{effect['effect']}(靶系统:{effect['target_system']})" 
                          for effect in self.health_effects]
            texts.append(f"健康影响: {', '.join(effect_texts)}")
            
        if self.prevention_strategies:
            texts.append(f"预防策略: {', '.join(self.prevention_strategies)}")
            
        if self.seasonal_variations:
            texts.append(f"季节性变化: {self.seasonal_variations}")
            
        if self.climate_change_implications:
            texts.append(f"气候变化影响: {self.climate_change_implications}")
            
        return ". ".join(texts)


# 心理健康节点模型
class MentalHealthNode(BaseNodeModel):
    node_type: NodeType = NodeType.MENTAL_HEALTH
    psychology_domain: str
    theoretical_framework: Optional[str] = None
    applicable_age_groups: List[str] = Field(default_factory=list)
    cultural_considerations: Optional[str] = None
    cbt_techniques: List[str] = Field(default_factory=list)
    thought_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    emotion_regulation_strategies: List[str] = Field(default_factory=list)
    trigger_management_techniques: List[str] = Field(default_factory=list)
    stressors_identified: List[str] = Field(default_factory=list)
    coping_mechanisms: List[str] = Field(default_factory=list)
    resilience_building_practices: List[str] = Field(default_factory=list)
    assessment_tools: List[Dict[str, Any]] = Field(default_factory=list)
    intervention_approaches: List[str] = Field(default_factory=list)
    treatment_protocols: Optional[str] = None
    effectiveness_data: Optional[str] = None
    recommended_duration: Optional[str] = None
    follow_up_procedures: Optional[str] = None
    
    def get_text_for_embedding(self) -> str:
        """生成用于嵌入向量的文本表示"""
        texts = [f"{self.title}. {self.content}"]
        
        texts.append(f"心理学领域: {self.psychology_domain}")
        
        if self.theoretical_framework:
            texts.append(f"理论框架: {self.theoretical_framework}")
            
        if self.applicable_age_groups:
            texts.append(f"适用年龄组: {', '.join(self.applicable_age_groups)}")
            
        if self.thought_patterns:
            pattern_texts = [f"{tp['pattern']}→{tp['alternative']}" 
                           for tp in self.thought_patterns]
            texts.append(f"思维模式: {', '.join(pattern_texts)}")
            
        if self.emotion_regulation_strategies:
            texts.append(f"情绪调节策略: {', '.join(self.emotion_regulation_strategies)}")
            
        if self.intervention_approaches:
            texts.append(f"干预方法: {', '.join(self.intervention_approaches)}")
            
        if self.treatment_protocols:
            texts.append(f"治疗方案: {self.treatment_protocols}")
            
        return ". ".join(texts)


# 中医养生知识节点模型
class TCMNode(BaseNodeModel):
    node_type: NodeType = NodeType.TCM_KNOWLEDGE
    constitution_type: Optional[str] = None
    season: Optional[str] = None
    source_type: str
    classic_reference: Optional[str] = None
    herbs: List[Dict[str, Any]] = Field(default_factory=list)
    prescriptions: List[Dict[str, Any]] = Field(default_factory=list)
    dietary_recommendations: List[str] = Field(default_factory=list)
    lifestyle_adjustments: List[str] = Field(default_factory=list)
    exercise_techniques: List[str] = Field(default_factory=list)
    meridians: List[str] = Field(default_factory=list)
    five_elements: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    cautions: List[str] = Field(default_factory=list)
    modern_research: Optional[str] = None
    clinical_evidence: Optional[str] = None
    
    def get_text_for_embedding(self) -> str:
        """生成用于嵌入向量的文本表示"""
        texts = [f"{self.title}. {self.content}"]
        
        if self.constitution_type:
            texts.append(f"体质类型: {self.constitution_type}")
            
        if self.season:
            texts.append(f"季节/节气: {self.season}")
            
        texts.append(f"资料类型: {self.source_type}")
        
        if self.classic_reference:
            texts.append(f"经典文献: {self.classic_reference}")
            
        if self.herbs:
            herb_texts = [f"{herb['name']}({herb.get('property', '')})" 
                         for herb in self.herbs]
            texts.append(f"相关药材: {', '.join(herb_texts)}")
            
        if self.prescriptions:
            prescription_texts = [f"{p['name']}({p.get('function', '')})" 
                                for p in self.prescriptions]
            texts.append(f"相关方剂: {', '.join(prescription_texts)}")
            
        if self.dietary_recommendations:
            texts.append(f"饮食建议: {', '.join(self.dietary_recommendations)}")
            
        if self.lifestyle_adjustments:
            texts.append(f"生活调整: {', '.join(self.lifestyle_adjustments)}")
            
        if self.five_elements:
            texts.append(f"五行: {', '.join(self.five_elements)}")
            
        if self.clinical_evidence:
            texts.append(f"临床证据: {self.clinical_evidence}")
            
        return ". ".join(texts)


# 节点类型联合类型
NodeUnion = Union[
    BaseNodeModel, 
    PrecisionMedicineNode, 
    MultimodalHealthNode, 
    EnvironmentalHealthNode, 
    MentalHealthNode,
    TCMNode
]


# 关系模型
class RelationshipModel(BaseModel):
    from_id: str
    to_id: str
    type: RelationshipType
    properties: Dict[str, Any] = Field(default_factory=dict)


# 知识图谱查询过滤器
class KnowledgeGraphFilter(BaseModel):
    node_types: Optional[List[NodeType]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    relation_types: Optional[List[RelationshipType]] = None
    text_query: Optional[str] = None
    limit: int = 100