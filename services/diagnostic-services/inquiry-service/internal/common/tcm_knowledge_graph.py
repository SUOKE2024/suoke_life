"""
tcm_knowledge_graph - 索克生活项目模块
"""

from .base import BaseService
from .cache import CacheManager
from .exceptions import InquiryServiceError
from .metrics import MetricsCollector
from .utils import cached, timer
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

"""
中医知识图谱集成模块

该模块实现了中医知识图谱的集成和应用，包括：
- 症状到证型的智能映射
- 基于证型的方剂推荐
- 中医知识推理和查询
- 禁忌症检查
- 患者适应性评估
"""




class EntityType(Enum):
    """实体类型"""

    SYMPTOM = "symptom"  # 症状
    SYNDROME = "syndrome"  # 证型
    FORMULA = "formula"  # 方剂
    HERB = "herb"  # 中药
    MERIDIAN = "meridian"  # 经络
    ORGAN = "organ"  # 脏腑
    CONSTITUTION = "constitution"  # 体质


class RelationType(Enum):
    """关系类型"""

    SYMPTOM_INDICATES = "symptom_indicates"  # 症状指示证型
    SYNDROME_TREATS = "syndrome_treats"  # 证型治疗方剂
    FORMULA_CONTAINS = "formula_contains"  # 方剂包含中药
    HERB_AFFECTS = "herb_affects"  # 中药作用经络/脏腑
    MERIDIAN_CONNECTS = "meridian_connects"  # 经络连接脏腑
    CONSTITUTION_PRONE = "constitution_prone"  # 体质易患证型
    CONTRAINDICATION = "contraindication"  # 禁忌关系


@dataclass
class KnowledgeEntity:
    """知识实体"""

    id: str
    name: str
    entity_type: EntityType
    properties: dict[str, Any] = field(default_factory=dict)
    aliases: list[str] = field(default_factory=list)
    description: str = ""
    confidence: float = 1.0


@dataclass
class KnowledgeRelation:
    """知识关系"""

    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class InferenceResult:
    """推理结果"""

    entity_id: str
    entity_name: str
    confidence: float
    reasoning_path: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)


@dataclass
class TCMAnalysis:
    """中医分析结果"""

    patient_id: str
    symptoms: list[str]
    inferred_syndromes: list[InferenceResult]
    recommended_formulas: list[InferenceResult]
    constitution_analysis: InferenceResult | None = None
    meridian_analysis: list[str] = field(default_factory=list)
    treatment_principles: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    analysis_timestamp: datetime = field(default_factory=datetime.now)


class TCMKnowledgeGraph(BaseService):
    """中医知识图谱"""

    def __init__(
        self,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        config: dict[str, Any] | None = None,
    ):
        super().__init__()
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.config = config or {}

        # 配置参数
        self.confidence_threshold = self.config.get("confidence_threshold", 0.6)
        self.max_inference_depth = self.config.get("max_inference_depth", 3)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)

        # 知识图谱存储
        self.entities: dict[str, KnowledgeEntity] = {}
        self.relations: dict[str, KnowledgeRelation] = {}
        self.entity_index: dict[EntityType, set[str]] = {et: set() for et in EntityType}
        self.relation_index: dict[RelationType, set[str]] = {
            rt: set() for rt in RelationType
        }

        # 症状-证型映射缓存
        self.symptom_syndrome_cache: dict[str, list[InferenceResult]] = {}

        # 统计信息
        self.stats = {
            "total_entities": 0,
            "total_relations": 0,
            "inference_requests": 0,
            "successful_inferences": 0,
            "cache_hits": 0,
            "entity_type_counts": {et.value: 0 for et in EntityType},
            "relation_type_counts": {rt.value: 0 for rt in RelationType},
        }

        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self) -> None:
        """初始化知识库"""
        # 初始化基础中医知识
        self._load_basic_symptoms()
        self._load_basic_syndromes()
        self._load_basic_formulas()
        self._load_basic_herbs()
        self._load_basic_relations()

        self.logger.info("TCM knowledge graph initialized")

    def _load_basic_symptoms(self) -> None:
        """加载基础症状"""
        symptoms = [
            # 头部症状
            {
                "id": "headache",
                "name": "头痛",
                "aliases": ["头疼", "脑袋疼"],
                "properties": {"location": "head", "severity_range": [1, 10]},
            },
            {
                "id": "dizziness",
                "name": "头晕",
                "aliases": ["眩晕", "头昏"],
                "properties": {"location": "head", "type": "neurological"},
            },
            {
                "id": "tinnitus",
                "name": "耳鸣",
                "aliases": ["耳朵响"],
                "properties": {"location": "ear", "type": "sensory"},
            },
            # 消化系统症状
            {
                "id": "nausea",
                "name": "恶心",
                "aliases": ["想吐"],
                "properties": {"system": "digestive", "severity_range": [1, 10]},
            },
            {
                "id": "vomiting",
                "name": "呕吐",
                "aliases": ["吐"],
                "properties": {"system": "digestive", "severity_range": [1, 10]},
            },
            {
                "id": "abdominal_pain",
                "name": "腹痛",
                "aliases": ["肚子疼", "胃疼"],
                "properties": {"location": "abdomen", "severity_range": [1, 10]},
            },
            {
                "id": "diarrhea",
                "name": "腹泻",
                "aliases": ["拉肚子", "泄泻"],
                "properties": {"system": "digestive", "frequency": "multiple"},
            },
            {
                "id": "constipation",
                "name": "便秘",
                "aliases": ["大便干燥"],
                "properties": {"system": "digestive", "duration": "chronic"},
            },
            # 呼吸系统症状
            {
                "id": "cough",
                "name": "咳嗽",
                "aliases": ["咳"],
                "properties": {"system": "respiratory", "type": "reflex"},
            },
            {
                "id": "shortness_of_breath",
                "name": "气短",
                "aliases": ["呼吸困难", "喘"],
                "properties": {"system": "respiratory", "severity_range": [1, 10]},
            },
            {
                "id": "chest_tightness",
                "name": "胸闷",
                "aliases": ["胸部闷"],
                "properties": {"location": "chest", "system": "respiratory"},
            },
            # 循环系统症状
            {
                "id": "palpitation",
                "name": "心悸",
                "aliases": ["心慌", "心跳快"],
                "properties": {"system": "cardiovascular", "type": "rhythm"},
            },
            {
                "id": "chest_pain",
                "name": "胸痛",
                "aliases": ["胸部疼痛"],
                "properties": {"location": "chest", "severity_range": [1, 10]},
            },
            # 全身症状
            {
                "id": "fatigue",
                "name": "乏力",
                "aliases": ["疲劳", "没力气"],
                "properties": {"type": "systemic", "severity_range": [1, 10]},
            },
            {
                "id": "fever",
                "name": "发热",
                "aliases": ["发烧", "体温高"],
                "properties": {"type": "systemic", "measurable": True},
            },
            {
                "id": "night_sweats",
                "name": "盗汗",
                "aliases": ["夜间出汗"],
                "properties": {"time": "night", "type": "autonomic"},
            },
            # 睡眠症状
            {
                "id": "insomnia",
                "name": "失眠",
                "aliases": ["睡不着", "入睡困难"],
                "properties": {"type": "sleep", "severity_range": [1, 10]},
            },
            {
                "id": "dream_disturbed_sleep",
                "name": "多梦",
                "aliases": ["梦多"],
                "properties": {"type": "sleep", "quality": "poor"},
            },
        ]

        for symptom_data in symptoms:
            entity = KnowledgeEntity(
                id=symptom_data["id"],
                name=symptom_data["name"],
                entity_type=EntityType.SYMPTOM,
                aliases=symptom_data.get("aliases", []),
                properties=symptom_data.get("properties", {}),
            )
            self._add_entity(entity)

    def _load_basic_syndromes(self) -> None:
        """加载基础证型"""
        syndromes = [
            # 气血证型
            {
                "id": "qi_deficiency",
                "name": "气虚证",
                "properties": {"category": "qi_blood", "nature": "deficiency"},
            },
            {
                "id": "blood_deficiency",
                "name": "血虚证",
                "properties": {"category": "qi_blood", "nature": "deficiency"},
            },
            {
                "id": "qi_stagnation",
                "name": "气滞证",
                "properties": {"category": "qi_blood", "nature": "stagnation"},
            },
            {
                "id": "blood_stasis",
                "name": "血瘀证",
                "properties": {"category": "qi_blood", "nature": "stasis"},
            },
            # 阴阳证型
            {
                "id": "yang_deficiency",
                "name": "阳虚证",
                "properties": {"category": "yin_yang", "nature": "yang_deficiency"},
            },
            {
                "id": "yin_deficiency",
                "name": "阴虚证",
                "properties": {"category": "yin_yang", "nature": "yin_deficiency"},
            },
            # 脏腑证型
            {
                "id": "spleen_qi_deficiency",
                "name": "脾气虚证",
                "properties": {"organ": "spleen", "nature": "qi_deficiency"},
            },
            {
                "id": "kidney_yang_deficiency",
                "name": "肾阳虚证",
                "properties": {"organ": "kidney", "nature": "yang_deficiency"},
            },
            {
                "id": "heart_blood_deficiency",
                "name": "心血虚证",
                "properties": {"organ": "heart", "nature": "blood_deficiency"},
            },
            {
                "id": "liver_qi_stagnation",
                "name": "肝气郁结证",
                "properties": {"organ": "liver", "nature": "qi_stagnation"},
            },
            # 外感证型
            {
                "id": "wind_cold",
                "name": "风寒证",
                "properties": {"category": "external", "pathogen": ["wind", "cold"]},
            },
            {
                "id": "wind_heat",
                "name": "风热证",
                "properties": {"category": "external", "pathogen": ["wind", "heat"]},
            },
            # 湿热证型
            {
                "id": "damp_heat",
                "name": "湿热证",
                "properties": {"category": "damp_heat", "pathogen": ["damp", "heat"]},
            },
            {
                "id": "cold_damp",
                "name": "寒湿证",
                "properties": {"category": "cold_damp", "pathogen": ["cold", "damp"]},
            },
        ]

        for syndrome_data in syndromes:
            entity = KnowledgeEntity(
                id=syndrome_data["id"],
                name=syndrome_data["name"],
                entity_type=EntityType.SYNDROME,
                properties=syndrome_data.get("properties", {}),
            )
            self._add_entity(entity)

    def _load_basic_formulas(self) -> None:
        """加载基础方剂"""
        formulas = [
            # 补益方
            {
                "id": "si_jun_zi_tang",
                "name": "四君子汤",
                "properties": {"category": "tonifying", "target": "spleen_qi"},
            },
            {
                "id": "si_wu_tang",
                "name": "四物汤",
                "properties": {"category": "tonifying", "target": "blood"},
            },
            {
                "id": "ba_zhen_tang",
                "name": "八珍汤",
                "properties": {"category": "tonifying", "target": "qi_blood"},
            },
            # 理气方
            {
                "id": "xiao_yao_san",
                "name": "逍遥散",
                "properties": {"category": "qi_regulating", "target": "liver_qi"},
            },
            {
                "id": "gan_mai_da_zao_tang",
                "name": "甘麦大枣汤",
                "properties": {"category": "calming", "target": "heart_spirit"},
            },
            # 清热方
            {
                "id": "yin_qiao_san",
                "name": "银翘散",
                "properties": {"category": "heat_clearing", "target": "wind_heat"},
            },
            {
                "id": "ma_xing_shi_gan_tang",
                "name": "麻杏石甘汤",
                "properties": {"category": "heat_clearing", "target": "lung_heat"},
            },
            # 温里方
            {
                "id": "li_zhong_wan",
                "name": "理中丸",
                "properties": {"category": "warming", "target": "spleen_stomach"},
            },
            {
                "id": "si_ni_tang",
                "name": "四逆汤",
                "properties": {"category": "warming", "target": "yang_qi"},
            },
        ]

        for formula_data in formulas:
            entity = KnowledgeEntity(
                id=formula_data["id"],
                name=formula_data["name"],
                entity_type=EntityType.FORMULA,
                properties=formula_data.get("properties", {}),
            )
            self._add_entity(entity)

    def _load_basic_herbs(self) -> None:
        """加载基础中药"""
        herbs = [
            # 补气药
            {
                "id": "ren_shen",
                "name": "人参",
                "properties": {
                    "category": "qi_tonifying",
                    "nature": "warm",
                    "taste": "sweet",
                },
            },
            {
                "id": "huang_qi",
                "name": "黄芪",
                "properties": {
                    "category": "qi_tonifying",
                    "nature": "warm",
                    "taste": "sweet",
                },
            },
            {
                "id": "bai_zhu",
                "name": "白术",
                "properties": {
                    "category": "qi_tonifying",
                    "nature": "warm",
                    "taste": "sweet",
                },
            },
            # 补血药
            {
                "id": "dang_gui",
                "name": "当归",
                "properties": {
                    "category": "blood_tonifying",
                    "nature": "warm",
                    "taste": "sweet",
                },
            },
            {
                "id": "shu_di_huang",
                "name": "熟地黄",
                "properties": {
                    "category": "blood_tonifying",
                    "nature": "warm",
                    "taste": "sweet",
                },
            },
            # 理气药
            {
                "id": "chen_pi",
                "name": "陈皮",
                "properties": {
                    "category": "qi_regulating",
                    "nature": "warm",
                    "taste": "bitter",
                },
            },
            {
                "id": "chai_hu",
                "name": "柴胡",
                "properties": {
                    "category": "qi_regulating",
                    "nature": "cool",
                    "taste": "bitter",
                },
            },
            # 清热药
            {
                "id": "jin_yin_hua",
                "name": "金银花",
                "properties": {
                    "category": "heat_clearing",
                    "nature": "cold",
                    "taste": "sweet",
                },
            },
            {
                "id": "lian_qiao",
                "name": "连翘",
                "properties": {
                    "category": "heat_clearing",
                    "nature": "cool",
                    "taste": "bitter",
                },
            },
        ]

        for herb_data in herbs:
            entity = KnowledgeEntity(
                id=herb_data["id"],
                name=herb_data["name"],
                entity_type=EntityType.HERB,
                properties=herb_data.get("properties", {}),
            )
            self._add_entity(entity)

    def _load_basic_relations(self) -> None:
        """加载基础关系"""
        relations = [
            # 症状指示证型关系
            {
                "source": "fatigue",
                "target": "qi_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.8,
            },
            {
                "source": "shortness_of_breath",
                "target": "qi_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.7,
            },
            {
                "source": "palpitation",
                "target": "heart_blood_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.8,
            },
            {
                "source": "insomnia",
                "target": "heart_blood_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.7,
            },
            {
                "source": "dizziness",
                "target": "blood_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.6,
            },
            {
                "source": "abdominal_pain",
                "target": "spleen_qi_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.6,
            },
            {
                "source": "diarrhea",
                "target": "spleen_qi_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.7,
            },
            {
                "source": "headache",
                "target": "liver_qi_stagnation",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.6,
            },
            {
                "source": "chest_tightness",
                "target": "liver_qi_stagnation",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.5,
            },
            # 证型治疗方剂关系
            {
                "source": "qi_deficiency",
                "target": "si_jun_zi_tang",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.9,
            },
            {
                "source": "blood_deficiency",
                "target": "si_wu_tang",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.9,
            },
            {
                "source": "spleen_qi_deficiency",
                "target": "si_jun_zi_tang",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.8,
            },
            {
                "source": "heart_blood_deficiency",
                "target": "gan_mai_da_zao_tang",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.7,
            },
            {
                "source": "liver_qi_stagnation",
                "target": "xiao_yao_san",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.9,
            },
            {
                "source": "wind_heat",
                "target": "yin_qiao_san",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.9,
            },
            # 方剂包含中药关系
            {
                "source": "si_jun_zi_tang",
                "target": "ren_shen",
                "type": RelationType.FORMULA_CONTAINS,
                "weight": 1.0,
            },
            {
                "source": "si_jun_zi_tang",
                "target": "bai_zhu",
                "type": RelationType.FORMULA_CONTAINS,
                "weight": 1.0,
            },
            {
                "source": "si_wu_tang",
                "target": "dang_gui",
                "type": RelationType.FORMULA_CONTAINS,
                "weight": 1.0,
            },
            {
                "source": "si_wu_tang",
                "target": "shu_di_huang",
                "type": RelationType.FORMULA_CONTAINS,
                "weight": 1.0,
            },
            {
                "source": "xiao_yao_san",
                "target": "chai_hu",
                "type": RelationType.FORMULA_CONTAINS,
                "weight": 1.0,
            },
            {
                "source": "yin_qiao_san",
                "target": "jin_yin_hua",
                "type": RelationType.FORMULA_CONTAINS,
                "weight": 1.0,
            },
            {
                "source": "yin_qiao_san",
                "target": "lian_qiao",
                "type": RelationType.FORMULA_CONTAINS,
                "weight": 1.0,
            },
        ]

        for rel_data in relations:
            relation = KnowledgeRelation(
                id=f"{rel_data['source']}_{rel_data['type'].value}_{rel_data['target']}",
                source_id=rel_data["source"],
                target_id=rel_data["target"],
                relation_type=rel_data["type"],
                weight=rel_data["weight"],
            )
            self._add_relation(relation)

    def _add_entity(self, entity: KnowledgeEntity) -> None:
        """添加实体"""
        self.entities[entity.id] = entity
        self.entity_index[entity.entity_type].add(entity.id)
        self.stats["total_entities"] += 1
        self.stats["entity_type_counts"][entity.entity_type.value] += 1

    def _add_relation(self, relation: KnowledgeRelation) -> None:
        """添加关系"""
        self.relations[relation.id] = relation
        self.relation_index[relation.relation_type].add(relation.id)
        self.stats["total_relations"] += 1
        self.stats["relation_type_counts"][relation.relation_type.value] += 1

    @timer
    @cached(ttl=3600)
    async def analyze_symptoms(
        self, symptoms: list[str], patient_profile: dict[str, Any] | None = None
    ) -> TCMAnalysis:
        """分析症状并生成中医诊断"""
        try:
            self.stats["inference_requests"] += 1
            await self.metrics_collector.increment("tcm_analysis_requests")

            # 标准化症状名称
            normalized_symptoms = await self._normalize_symptoms(symptoms)

            # 推理证型
            inferred_syndromes = await self._infer_syndromes(normalized_symptoms)

            # 推荐方剂
            recommended_formulas = await self._recommend_formulas(inferred_syndromes)

            # 体质分析
            constitution_analysis = await self._analyze_constitution(
                normalized_symptoms, patient_profile
            )

            # 经络分析
            meridian_analysis = await self._analyze_meridians(normalized_symptoms)

            # 治疗原则
            treatment_principles = await self._generate_treatment_principles(
                inferred_syndromes
            )

            # 禁忌症检查
            contraindications = await self._check_contraindications(
                recommended_formulas, patient_profile
            )

            # 计算整体置信度
            confidence_score = await self._calculate_overall_confidence(
                inferred_syndromes, recommended_formulas
            )

            analysis = TCMAnalysis(
                patient_id=patient_profile.get("patient_id", "unknown")
                if patient_profile
                else "unknown",
                symptoms=normalized_symptoms,
                inferred_syndromes=inferred_syndromes,
                recommended_formulas=recommended_formulas,
                constitution_analysis=constitution_analysis,
                meridian_analysis=meridian_analysis,
                treatment_principles=treatment_principles,
                contraindications=contraindications,
                confidence_score=confidence_score,
            )

            self.stats["successful_inferences"] += 1
            await self.metrics_collector.increment("tcm_analysis_successful")

            return analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze symptoms: {e}")
            raise InquiryServiceError(f"TCM analysis failed: {e}")

    async def _normalize_symptoms(self, symptoms: list[str]) -> list[str]:
        """标准化症状名称"""
        normalized = []

        for symptom in symptoms:
            # 查找匹配的实体
            matched_entity = await self._find_symptom_entity(symptom)
            if matched_entity:
                normalized.append(matched_entity.id)
            else:
                # 如果找不到匹配的实体，保留原始症状
                normalized.append(symptom)

        return normalized

    async def _find_symptom_entity(self, symptom_text: str) -> KnowledgeEntity | None:
        """查找症状实体"""
        symptom_text = symptom_text.strip().lower()

        # 精确匹配
        for entity_id in self.entity_index[EntityType.SYMPTOM]:
            entity = self.entities[entity_id]
            if entity.name.lower() == symptom_text:
                return entity

            # 别名匹配
            for alias in entity.aliases:
                if alias.lower() == symptom_text:
                    return entity

        # 模糊匹配
        best_match = None
        best_similarity = 0.0

        for entity_id in self.entity_index[EntityType.SYMPTOM]:
            entity = self.entities[entity_id]
            similarity = await self._calculate_text_similarity(
                symptom_text, entity.name
            )

            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = entity

        return best_match

    async def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简化实现：基于字符重叠度
        set1 = set(text1)
        set2 = set(text2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    async def _infer_syndromes(self, symptoms: list[str]) -> list[InferenceResult]:
        """推理证型"""
        syndrome_scores: dict[str, float] = {}
        syndrome_evidence: dict[str, list[str]] = {}

        # 遍历每个症状，查找相关证型
        for symptom in symptoms:
            related_syndromes = await self._get_related_syndromes(symptom)

            for syndrome_id, weight in related_syndromes:
                if syndrome_id not in syndrome_scores:
                    syndrome_scores[syndrome_id] = 0.0
                    syndrome_evidence[syndrome_id] = []

                syndrome_scores[syndrome_id] += weight
                syndrome_evidence[syndrome_id].append(symptom)

        # 标准化分数
        max_score = max(syndrome_scores.values()) if syndrome_scores else 1.0
        for syndrome_id in syndrome_scores:
            syndrome_scores[syndrome_id] /= max_score

        # 生成推理结果
        results = []
        for syndrome_id, score in syndrome_scores.items():
            if score >= self.confidence_threshold:
                entity = self.entities.get(syndrome_id)
                if entity:
                    result = InferenceResult(
                        entity_id=syndrome_id,
                        entity_name=entity.name,
                        confidence=score,
                        supporting_evidence=syndrome_evidence[syndrome_id],
                        reasoning_path=[
                            f"症状 {symptom} 指示证型 {entity.name}"
                            for symptom in syndrome_evidence[syndrome_id]
                        ],
                    )
                    results.append(result)

        # 按置信度排序
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    async def _get_related_syndromes(self, symptom: str) -> list[tuple[str, float]]:
        """获取症状相关的证型"""
        related = []

        for relation_id in self.relation_index[RelationType.SYMPTOM_INDICATES]:
            relation = self.relations[relation_id]
            if relation.source_id == symptom:
                related.append((relation.target_id, relation.weight))

        return related

    async def _recommend_formulas(
        self, syndromes: list[InferenceResult]
    ) -> list[InferenceResult]:
        """推荐方剂"""
        formula_scores: dict[str, float] = {}
        formula_evidence: dict[str, list[str]] = {}

        for syndrome in syndromes:
            related_formulas = await self._get_related_formulas(syndrome.entity_id)

            for formula_id, weight in related_formulas:
                if formula_id not in formula_scores:
                    formula_scores[formula_id] = 0.0
                    formula_evidence[formula_id] = []

                # 考虑证型的置信度
                adjusted_weight = weight * syndrome.confidence
                formula_scores[formula_id] += adjusted_weight
                formula_evidence[formula_id].append(syndrome.entity_name)

        # 标准化分数
        max_score = max(formula_scores.values()) if formula_scores else 1.0
        for formula_id in formula_scores:
            formula_scores[formula_id] /= max_score

        # 生成推荐结果
        results = []
        for formula_id, score in formula_scores.items():
            if score >= self.confidence_threshold:
                entity = self.entities.get(formula_id)
                if entity:
                    result = InferenceResult(
                        entity_id=formula_id,
                        entity_name=entity.name,
                        confidence=score,
                        supporting_evidence=formula_evidence[formula_id],
                        reasoning_path=[
                            f"证型 {syndrome} 适用方剂 {entity.name}"
                            for syndrome in formula_evidence[formula_id]
                        ],
                    )
                    results.append(result)

        # 按置信度排序
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    async def _get_related_formulas(self, syndrome: str) -> list[tuple[str, float]]:
        """获取证型相关的方剂"""
        related = []

        for relation_id in self.relation_index[RelationType.SYNDROME_TREATS]:
            relation = self.relations[relation_id]
            if relation.source_id == syndrome:
                related.append((relation.target_id, relation.weight))

        return related

    async def _analyze_constitution(
        self, symptoms: list[str], patient_profile: dict[str, Any] | None
    ) -> InferenceResult | None:
        """分析体质"""
        # 简化实现：基于症状模式推断体质
        constitution_indicators = {
            "qi_deficiency_constitution": [
                "fatigue",
                "shortness_of_breath",
                "low_voice",
            ],
            "yang_deficiency_constitution": ["cold_limbs", "fatigue", "loose_stool"],
            "yin_deficiency_constitution": ["night_sweats", "dry_mouth", "insomnia"],
            "blood_stasis_constitution": [
                "dark_complexion",
                "fixed_pain",
                "dark_tongue",
            ],
            "phlegm_damp_constitution": ["obesity", "chest_tightness", "sticky_stool"],
        }

        best_constitution = None
        best_score = 0.0

        for constitution, indicators in constitution_indicators.items():
            score = sum(1 for indicator in indicators if indicator in symptoms)
            score /= len(indicators)  # 标准化

            if score > best_score:
                best_score = score
                best_constitution = constitution

        if best_constitution and best_score >= 0.3:
            return InferenceResult(
                entity_id=best_constitution,
                entity_name=best_constitution.replace("_", " ").title(),
                confidence=best_score,
                supporting_evidence=symptoms,
                reasoning_path=["基于症状模式推断体质类型"],
            )

        return None

    async def _analyze_meridians(self, symptoms: list[str]) -> list[str]:
        """分析经络"""
        # 简化实现：基于症状位置推断相关经络
        meridian_mapping = {
            "headache": ["足太阳膀胱经", "足少阳胆经"],
            "chest_pain": ["手厥阴心包经", "足厥阴肝经"],
            "abdominal_pain": ["足太阴脾经", "足阳明胃经"],
            "back_pain": ["足太阳膀胱经", "督脉"],
            "shoulder_pain": ["手太阳小肠经", "手少阳三焦经"],
        }

        involved_meridians = set()
        for symptom in symptoms:
            if symptom in meridian_mapping:
                involved_meridians.update(meridian_mapping[symptom])

        return list(involved_meridians)

    async def _generate_treatment_principles(
        self, syndromes: list[InferenceResult]
    ) -> list[str]:
        """生成治疗原则"""
        principles = []

        for syndrome in syndromes:
            syndrome_id = syndrome.entity_id
            entity = self.entities.get(syndrome_id)

            if entity and entity.properties:
                nature = entity.properties.get("nature")
                category = entity.properties.get("category")

                if nature == "deficiency":
                    principles.append("补虚扶正")
                elif nature == "stagnation":
                    principles.append("理气解郁")
                elif nature == "heat":
                    principles.append("清热泻火")
                elif nature == "cold":
                    principles.append("温阳散寒")

                if category == "qi_blood":
                    principles.append("调和气血")
                elif category == "yin_yang":
                    principles.append("平衡阴阳")

        # 去重并返回
        return list(set(principles))

    async def _check_contraindications(
        self, formulas: list[InferenceResult], patient_profile: dict[str, Any] | None
    ) -> list[str]:
        """检查禁忌症"""
        contraindications = []

        if not patient_profile:
            return contraindications

        # 检查年龄禁忌
        age = patient_profile.get("age", 0)
        if age < 18:
            contraindications.append("未成年人用药需谨慎")
        elif age > 65:
            contraindications.append("老年人用药需减量")

        # 检查妊娠禁忌
        if patient_profile.get("pregnancy"):
            contraindications.append("妊娠期禁用活血化瘀类药物")

        # 检查过敏史
        allergies = patient_profile.get("allergies", [])
        for formula in formulas:
            # 获取方剂中的药物
            herbs = await self._get_formula_herbs(formula.entity_id)
            for herb in herbs:
                if herb in allergies:
                    contraindications.append(f"对{herb}过敏，禁用含此药的方剂")

        return contraindications

    async def _get_formula_herbs(self, formula_id: str) -> list[str]:
        """获取方剂中的药物"""
        herbs = []

        for relation_id in self.relation_index[RelationType.FORMULA_CONTAINS]:
            relation = self.relations[relation_id]
            if relation.source_id == formula_id:
                herb_entity = self.entities.get(relation.target_id)
                if herb_entity:
                    herbs.append(herb_entity.name)

        return herbs

    async def _calculate_overall_confidence(
        self, syndromes: list[InferenceResult], formulas: list[InferenceResult]
    ) -> float:
        """计算整体置信度"""
        if not syndromes and not formulas:
            return 0.0

        syndrome_confidence = (
            sum(s.confidence for s in syndromes) / len(syndromes) if syndromes else 0.0
        )

        formula_confidence = (
            sum(f.confidence for f in formulas) / len(formulas) if formulas else 0.0
        )

        # 加权平均
        return syndrome_confidence * 0.6 + formula_confidence * 0.4

    @timer
    async def query_knowledge(
        self,
        entity_type: EntityType | None = None,
        relation_type: RelationType | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """查询知识图谱"""
        try:
            result = {"entities": [], "relations": [], "statistics": {}}

            # 查询实体
            if entity_type:
                entity_ids = self.entity_index.get(entity_type, set())
                for entity_id in entity_ids:
                    entity = self.entities[entity_id]
                    if self._match_filters(entity.properties, filters):
                        result["entities"].append(
                            {
                                "id": entity.id,
                                "name": entity.name,
                                "type": entity.entity_type.value,
                                "properties": entity.properties,
                            }
                        )

            # 查询关系
            if relation_type:
                relation_ids = self.relation_index.get(relation_type, set())
                for relation_id in relation_ids:
                    relation = self.relations[relation_id]
                    result["relations"].append(
                        {
                            "id": relation.id,
                            "source": relation.source_id,
                            "target": relation.target_id,
                            "type": relation.relation_type.value,
                            "weight": relation.weight,
                        }
                    )

            # 统计信息
            result["statistics"] = {
                "total_entities": len(result["entities"]),
                "total_relations": len(result["relations"]),
            }

            return result

        except Exception as e:
            self.logger.error(f"Failed to query knowledge: {e}")
            raise InquiryServiceError(f"Knowledge query failed: {e}")

    def _match_filters(
        self, properties: dict[str, Any], filters: dict[str, Any] | None
    ) -> bool:
        """匹配过滤条件"""
        if not filters:
            return True

        for key, value in filters.items():
            if key not in properties or properties[key] != value:
                return False

        return True

    async def get_statistics(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "knowledge_graph_stats": self.stats,
            "cache_stats": await self.cache_manager.get_stats(),
            "metrics": await self.metrics_collector.get_metrics(),
        }

    async def update_knowledge(
        self,
        entities: list[KnowledgeEntity] | None = None,
        relations: list[KnowledgeRelation] | None = None,
    ) -> dict[str, int]:
        """更新知识图谱"""
        try:
            added_entities = 0
            added_relations = 0

            if entities:
                for entity in entities:
                    self._add_entity(entity)
                    added_entities += 1

            if relations:
                for relation in relations:
                    self._add_relation(relation)
                    added_relations += 1

            self.logger.info(
                f"Updated knowledge graph: {added_entities} entities, {added_relations} relations"
            )

            return {
                "added_entities": added_entities,
                "added_relations": added_relations,
            }

        except Exception as e:
            self.logger.error(f"Failed to update knowledge: {e}")
            raise InquiryServiceError(f"Knowledge update failed: {e}")
