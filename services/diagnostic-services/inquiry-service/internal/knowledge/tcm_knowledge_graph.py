"""
tcm_knowledge_graph - 索克生活项目模块
"""

from ..common.base import BaseService
from ..common.cache import cached
from ..common.exceptions import InquiryServiceError
from ..common.metrics import counter, memory_optimized, timer
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger
from typing import Any

#! / usr / bin / env python3

"""
中医知识图谱集成模块

该模块实现中医知识图谱的集成和应用，包括症状 - 证型映射、
方剂推荐、知识推理和智能诊断辅助。
"""





class TCMEntityType(Enum):
    """中医实体类型"""

    SYMPTOM = "symptom"  # 症状
    SYNDROME = "syndrome"  # 证型
    FORMULA = "formula"  # 方剂
    HERB = "herb"  # 中药
    MERIDIAN = "meridian"  # 经络
    ORGAN = "organ"  # 脏腑
    CONSTITUTION = "constitution"  # 体质


class RelationType(Enum):
    """关系类型"""

    SYMPTOM_INDICATES = "symptom_indicates"  # 症状指示
    SYNDROME_TREATS = "syndrome_treats"  # 证型治疗
    FORMULA_CONTAINS = "formula_contains"  # 方剂包含
    HERB_AFFECTS = "herb_affects"  # 中药作用
    MERIDIAN_CONNECTS = "meridian_connects"  # 经络连接
    ORGAN_RELATES = "organ_relates"  # 脏腑关联


@dataclass
class TCMEntity:
    """中医实体"""

    id: str
    name: str
    entity_type: TCMEntityType
    properties: dict[str, Any]
    aliases: list[str] = field(default_factory = list)
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory = dict)


@dataclass
class TCMRelation:
    """中医关系"""

    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float
    properties: dict[str, Any] = field(default_factory = dict)
    confidence: float = 1.0


@dataclass
class SyndromeMapping:
    """证型映射"""

    syndrome_id: str
    syndrome_name: str
    match_score: float
    supporting_symptoms: list[str]
    confidence: float
    reasoning: str
    metadata: dict[str, Any] = field(default_factory = dict)


@dataclass
class FormulaRecommendation:
    """方剂推荐"""

    formula_id: str
    formula_name: str
    recommendation_score: float
    applicable_syndromes: list[str]
    herb_composition: list[dict[str, Any]]
    contraindications: list[str]
    confidence: float
    reasoning: str


class TCMKnowledgeGraph(BaseService):
    """中医知识图谱"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化中医知识图谱

        Args:
            config: 配置信息
        """
        super().__init__(config)

        # 实体存储
        self.entities: dict[str, TCMEntity] = {}
        self.entity_index: dict[TCMEntityType, set[str]] = {
            entity_type: set() for entity_type in TCMEntityType
        }

        # 关系存储
        self.relations: dict[str, TCMRelation] = {}
        self.relation_index: dict[str, set[str]] = {}  # entity_id-> relation_ids

        # 症状 - 证型映射规则
        self.syndrome_rules: dict[str, dict[str, Any]] = {}

        # 方剂数据库
        self.formula_database: dict[str, dict[str, Any]] = {}

        # 推理引擎配置
        self.inference_config = {
            "min_confidence_threshold": 0.6,
            "max_inference_depth": 3,
            "weight_decay_factor": 0.8,
            "syndrome_match_threshold": 0.7,
        }

        # 性能统计
        self.stats = {
            "total_entities": 0,
            "total_relations": 0,
            "syndrome_mappings": 0,
            "formula_recommendations": 0,
            "inference_queries": 0,
        }

        self._initialize_knowledge_base()

        logger.info("中医知识图谱初始化完成")

    def _initialize_knowledge_base(self)-> None:
        """初始化知识库"""
        # 初始化基础症状实体
        self._load_symptom_entities()

        # 初始化证型实体
        self._load_syndrome_entities()

        # 初始化方剂实体
        self._load_formula_entities()

        # 初始化关系
        self._load_relations()

        # 初始化推理规则
        self._load_inference_rules()

    def _load_symptom_entities(self)-> None:
        """加载症状实体"""
        symptoms = [
            {
                "id": "symptom_headache",
                "name": "头痛",
                "aliases": ["头疼", "脑袋疼", "偏头痛"],
                "properties": {
                    "location": "头部",
                    "nature": "疼痛",
                    "severity_range": [1, 10],
                    "common_triggers": ["风寒", "肝阳上亢", "血瘀"],
                },
            },
            {
                "id": "symptom_fatigue",
                "name": "乏力",
                "aliases": ["疲劳", "无力", "倦怠"],
                "properties": {
                    "location": "全身",
                    "nature": "虚弱",
                    "related_organs": ["脾", "肾", "心"],
                    "common_causes": ["气虚", "血虚", "阳虚"],
                },
            },
            {
                "id": "symptom_insomnia",
                "name": "失眠",
                "aliases": ["睡不着", "入睡困难", "多梦"],
                "properties": {
                    "location": "神志",
                    "nature": "睡眠障碍",
                    "related_organs": ["心", "肝", "肾"],
                    "patterns": ["心肾不交", "肝郁化火", "心脾两虚"],
                },
            },
        ]

        for symptom_data in symptoms:
            entity = TCMEntity(
                id = symptom_data["id"],
                name = symptom_data["name"],
                entity_type = TCMEntityType.SYMPTOM,
                properties = symptom_data["properties"],
                aliases = symptom_data["aliases"],
            )
            self._add_entity(entity)

    def _load_syndrome_entities(self)-> None:
        """加载证型实体"""
        syndromes = [
            {
                "id": "syndrome_qi_deficiency",
                "name": "气虚证",
                "properties": {
                    "category": "虚证",
                    "main_symptoms": ["乏力", "气短", "懒言"],
                    "tongue": "淡胖",
                    "pulse": "虚弱",
                    "treatment_principle": "补气",
                    "representative_formula": "四君子汤",
                },
            },
            {
                "id": "syndrome_blood_stasis",
                "name": "血瘀证",
                "properties": {
                    "category": "实证",
                    "main_symptoms": ["疼痛", "肿块", "瘀斑"],
                    "tongue": "紫暗",
                    "pulse": "涩",
                    "treatment_principle": "活血化瘀",
                    "representative_formula": "血府逐瘀汤",
                },
            },
            {
                "id": "syndrome_liver_qi_stagnation",
                "name": "肝气郁结证",
                "properties": {
                    "category": "气机失调",
                    "main_symptoms": ["胸胁胀痛", "情志抑郁", "善太息"],
                    "tongue": "薄白苔",
                    "pulse": "弦",
                    "treatment_principle": "疏肝理气",
                    "representative_formula": "逍遥散",
                },
            },
        ]

        for syndrome_data in syndromes:
            entity = TCMEntity(
                id = syndrome_data["id"],
                name = syndrome_data["name"],
                entity_type = TCMEntityType.SYNDROME,
                properties = syndrome_data["properties"],
            )
            self._add_entity(entity)

    def _load_formula_entities(self)-> None:
        """加载方剂实体"""
        formulas = [
            {
                "id": "formula_sijunzi",
                "name": "四君子汤",
                "properties": {
                    "category": "补益剂",
                    "subcategory": "补气剂",
                    "composition": [
                        {"herb": "人参", "dosage": "9g", "role": "君药"},
                        {"herb": "白术", "dosage": "9g", "role": "臣药"},
                        {"herb": "茯苓", "dosage": "9g", "role": "佐药"},
                        {"herb": "甘草", "dosage": "6g", "role": "使药"},
                    ],
                    "functions": ["益气健脾"],
                    "indications": ["脾胃气虚证"],
                    "contraindications": ["阴虚内热", "实热证"],
                },
            },
            {
                "id": "formula_xiaoyao",
                "name": "逍遥散",
                "properties": {
                    "category": "和解剂",
                    "subcategory": "调和肝脾剂",
                    "composition": [
                        {"herb": "柴胡", "dosage": "9g", "role": "君药"},
                        {"herb": "当归", "dosage": "9g", "role": "臣药"},
                        {"herb": "白芍", "dosage": "9g", "role": "臣药"},
                        {"herb": "白术", "dosage": "9g", "role": "佐药"},
                        {"herb": "茯苓", "dosage": "9g", "role": "佐药"},
                        {"herb": "薄荷", "dosage": "3g", "role": "佐药"},
                        {"herb": "生姜", "dosage": "3g", "role": "佐药"},
                        {"herb": "甘草", "dosage": "6g", "role": "使药"},
                    ],
                    "functions": ["疏肝解郁", "健脾和血"],
                    "indications": ["肝郁脾虚证"],
                    "contraindications": ["阴虚血热"],
                },
            },
        ]

        for formula_data in formulas:
            entity = TCMEntity(
                id = formula_data["id"],
                name = formula_data["name"],
                entity_type = TCMEntityType.FORMULA,
                properties = formula_data["properties"],
            )
            self._add_entity(entity)

    def _load_relations(self)-> None:
        """加载关系"""
        relations = [
            # 症状指示证型
            {
                "source": "symptom_fatigue",
                "target": "syndrome_qi_deficiency",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.8,
                "properties": {"strength": "strong", "specificity": "moderate"},
            },
            {
                "source": "symptom_headache",
                "target": "syndrome_liver_qi_stagnation",
                "type": RelationType.SYMPTOM_INDICATES,
                "weight": 0.6,
                "properties": {"strength": "moderate", "specificity": "low"},
            },
            # 证型治疗方剂
            {
                "source": "syndrome_qi_deficiency",
                "target": "formula_sijunzi",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.9,
                "properties": {"efficacy": "high", "safety": "high"},
            },
            {
                "source": "syndrome_liver_qi_stagnation",
                "target": "formula_xiaoyao",
                "type": RelationType.SYNDROME_TREATS,
                "weight": 0.85,
                "properties": {"efficacy": "high", "safety": "high"},
            },
        ]

        for rel_data in relations:
            relation = TCMRelation(
                id = f"rel_{rel_data['source']}_{rel_data['target']}",
                source_id = rel_data["source"],
                target_id = rel_data["target"],
                relation_type = rel_data["type"],
                weight = rel_data["weight"],
                properties = rel_data["properties"],
            )
            self._add_relation(relation)

    def _load_inference_rules(self)-> None:
        """加载推理规则"""
        self.syndrome_rules = {
            "qi_deficiency_pattern": {
                "required_symptoms": ["乏力"],
                "supporting_symptoms": ["气短", "懒言", "自汗"],
                "exclusion_symptoms": ["发热", "口渴"],
                "min_symptom_count": 2,
                "confidence_threshold": 0.7,
            },
            "blood_stasis_pattern": {
                "required_symptoms": ["疼痛"],
                "supporting_symptoms": ["肿块", "瘀斑", "舌质紫暗"],
                "exclusion_symptoms": ["畏寒", "腹泻"],
                "min_symptom_count": 2,
                "confidence_threshold": 0.6,
            },
        }

    def _add_entity(self, entity: TCMEntity):
        """添加实体"""
        self.entities[entity.id] = entity
        self.entity_index[entity.entity_type].add(entity.id)
        self.stats["total_entities"] + = 1

    def _add_relation(self, relation: TCMRelation):
        """添加关系"""
        self.relations[relation.id] = relation

        # 更新关系索引
        if relation.source_id not in self.relation_index:
            self.relation_index[relation.source_id] = set()
        if relation.target_id not in self.relation_index:
            self.relation_index[relation.target_id] = set()

        self.relation_index[relation.source_id].add(relation.id)
        self.relation_index[relation.target_id].add(relation.id)

        self.stats["total_relations"] + = 1

    @timer("tcm_kg.map_symptoms_to_syndromes")
    @counter("tcm_kg.syndrome_mappings")
    async def map_symptoms_to_syndromes(
        self,
        symptoms: list[dict[str, Any]],
        patient_context: dict[str, Any] | None = None,
    )-> list[SyndromeMapping]:
        """
        将症状映射到证型

        Args:
            symptoms: 症状列表
            patient_context: 患者上下文信息

        Returns:
            证型映射列表
        """
        try:
            syndrome_mappings = []

            # 获取所有证型实体
            syndrome_entities = [
                self.entities[entity_id]
                for entity_id in self.entity_index[TCMEntityType.SYNDROME]
            ]

            for syndrome in syndrome_entities:
                mapping = await self._calculate_syndrome_mapping(
                    syndrome, symptoms, patient_context
                )

                if (
                    mapping.match_score
                    > = self.inference_config["syndrome_match_threshold"]
                ):
                    syndrome_mappings.append(mapping)

            # 按匹配分数排序
            syndrome_mappings.sort(key = lambda x: x.match_score, reverse = True)

            self.stats["syndrome_mappings"] + = len(syndrome_mappings)

            logger.debug(f"症状映射完成，找到 {len(syndrome_mappings)} 个匹配证型")
            return syndrome_mappings

        except Exception as e:
            logger.error(f"症状映射失败: {e}")
            raise InquiryServiceError(f"症状映射失败: {e}")

    async def _calculate_syndrome_mapping(
        self,
        syndrome: TCMEntity,
        symptoms: list[dict[str, Any]],
        patient_context: dict[str, Any] | None,
    )-> SyndromeMapping:
        """计算证型映射"""
        symptom_names = [s.get("name", "") for s in symptoms]
        syndrome_props = syndrome.properties

        # 计算症状匹配度
        required_symptoms = syndrome_props.get("main_symptoms", [])
        supporting_symptoms = syndrome_props.get("supporting_symptoms", [])

        # 必需症状匹配
        required_matches = sum(
            1
            for req_symptom in required_symptoms
            if any(req_symptom in symptom_name for symptom_name in symptom_names)
        )

        # 支持症状匹配
        supporting_matches = sum(
            1
            for sup_symptom in supporting_symptoms
            if any(sup_symptom in symptom_name for symptom_name in symptom_names)
        )

        # 计算匹配分数
        required_score = required_matches / max(len(required_symptoms), 1)
        supporting_score = supporting_matches / max(len(supporting_symptoms), 1)

        # 综合分数
        match_score = 0.7 * required_score + 0.3 * supporting_score

        # 考虑患者上下文
        if patient_context:
            context_bonus = await self._calculate_context_bonus(
                syndrome, patient_context
            )
            match_score = min(match_score + context_bonus, 1.0)

        # 计算置信度
        confidence = self._calculate_mapping_confidence(
            match_score, required_matches, supporting_matches
        )

        # 生成推理说明
        reasoning = self._generate_mapping_reasoning(
            syndrome, required_matches, supporting_matches, symptom_names
        )

        return SyndromeMapping(
            syndrome_id = syndrome.id,
            syndrome_name = syndrome.name,
            match_score = match_score,
            supporting_symptoms = symptom_names,
            confidence = confidence,
            reasoning = reasoning,
        )

    async def _calculate_context_bonus(
        self, syndrome: TCMEntity, patient_context: dict[str, Any]
    )-> float:
        """计算上下文加分"""
        bonus = 0.0

        # 年龄因素
        age = patient_context.get("age", 0)
        if (syndrome.name in ["气虚证", "阳虚证"] and age > 60) or (
            syndrome.name in ["肝气郁结证"] and 20 < = age < = 50
        ):
            bonus + = 0.1

        # 性别因素
        gender = patient_context.get("gender", "")
        if syndrome.name == "肝气郁结证" and gender == "female":
            bonus + = 0.05

        # 体质因素
        constitution = patient_context.get("constitution", "")
        if constitution and syndrome.name in constitution:
            bonus + = 0.15

        return bonus

    def _calculate_mapping_confidence(
        self, match_score: float, required_matches: int, supporting_matches: int
    )-> float:
        """计算映射置信度"""
        base_confidence = match_score

        # 必需症状匹配加分
        if required_matches > 0:
            base_confidence + = 0.1

        # 支持症状匹配加分
        if supporting_matches > = 2:
            base_confidence + = 0.05

        return min(base_confidence, 1.0)

    def _generate_mapping_reasoning(
        self,
        syndrome: TCMEntity,
        required_matches: int,
        supporting_matches: int,
        symptom_names: list[str],
    )-> str:
        """生成映射推理说明"""
        reasoning_parts = []

        if required_matches > 0:
            reasoning_parts.append(f"匹配主要症状 {required_matches} 个")

        if supporting_matches > 0:
            reasoning_parts.append(f"匹配支持症状 {supporting_matches} 个")

        syndrome_props = syndrome.properties
        if "treatment_principle" in syndrome_props:
            reasoning_parts.append(f"治疗原则：{syndrome_props['treatment_principle']}")

        return "；".join(reasoning_parts)

    @timer("tcm_kg.recommend_formulas")
    @counter("tcm_kg.formula_recommendations")
    async def recommend_formulas(
        self,
        syndrome_mappings: list[SyndromeMapping],
        patient_context: dict[str, Any] | None = None,
    )-> list[FormulaRecommendation]:
        """
        推荐方剂

        Args:
            syndrome_mappings: 证型映射列表
            patient_context: 患者上下文信息

        Returns:
            方剂推荐列表
        """
        try:
            formula_recommendations = []

            for syndrome_mapping in syndrome_mappings:
                # 查找治疗该证型的方剂
                related_formulas = await self._find_related_formulas(
                    syndrome_mapping.syndrome_id
                )

                for formula_id, relation_weight in related_formulas:
                    formula = self.entities.get(formula_id)
                    if not formula:
                        continue

                    # 计算推荐分数
                    recommendation_score = await self._calculate_recommendation_score(
                        formula, syndrome_mapping, relation_weight, patient_context
                    )

                    # 检查禁忌症
                    contraindications = await self._check_contraindications(
                        formula, patient_context
                    )

                    # 生成推荐说明
                    reasoning = await self._generate_recommendation_reasoning(
                        formula, syndrome_mapping, recommendation_score
                    )

                    recommendation = FormulaRecommendation(
                        formula_id = formula.id,
                        formula_name = formula.name,
                        recommendation_score = recommendation_score,
                        applicable_syndromes = [syndrome_mapping.syndrome_name],
                        herb_composition = formula.properties.get("composition", []),
                        contraindications = contraindications,
                        confidence = syndrome_mapping.confidence * relation_weight,
                        reasoning = reasoning,
                    )

                    formula_recommendations.append(recommendation)

            # 去重并排序
            formula_recommendations = self._deduplicate_recommendations(
                formula_recommendations
            )
            formula_recommendations.sort(
                key = lambda x: x.recommendation_score, reverse = True
            )

            self.stats["formula_recommendations"] + = len(formula_recommendations)

            logger.debug(f"方剂推荐完成，推荐 {len(formula_recommendations)} 个方剂")
            return formula_recommendations

        except Exception as e:
            logger.error(f"方剂推荐失败: {e}")
            raise InquiryServiceError(f"方剂推荐失败: {e}")

    async def _find_related_formulas(self, syndrome_id: str)-> list[tuple[str, float]]:
        """查找相关方剂"""
        related_formulas = []

        # 查找直接治疗关系
        relation_ids = self.relation_index.get(syndrome_id, set())

        for relation_id in relation_ids:
            relation = self.relations[relation_id]

            if (
                relation.relation_type == RelationType.SYNDROME_TREATS
                and relation.source_id == syndrome_id
            ):
                related_formulas.append((relation.target_id, relation.weight))

        return related_formulas

    async def _calculate_recommendation_score(
        self,
        formula: TCMEntity,
        syndrome_mapping: SyndromeMapping,
        relation_weight: float,
        patient_context: dict[str, Any] | None,
    )-> float:
        """计算推荐分数"""
        base_score = syndrome_mapping.match_score * relation_weight

        # 考虑方剂特性
        formula_props = formula.properties

        # 安全性加分
        if formula_props.get("safety") == "high":
            base_score + = 0.1

        # 经典方剂加分
        if "经典" in formula.name or "汤" in formula.name:
            base_score + = 0.05

        # 患者适应性
        if patient_context:
            adaptation_score = await self._calculate_patient_adaptation(
                formula, patient_context
            )
            base_score + = adaptation_score

        return min(base_score, 1.0)

    async def _calculate_patient_adaptation(
        self, formula: TCMEntity, patient_context: dict[str, Any]
    )-> float:
        """计算患者适应性"""
        adaptation = 0.0

        # 年龄适应性
        age = patient_context.get("age", 0)
        formula_props = formula.properties

        if age > 65 and "补益" in formula_props.get("category", ""):
            adaptation + = 0.1
        elif age < 18 and "清热" in formula_props.get("category", ""):
            adaptation - = 0.1

        # 体质适应性
        constitution = patient_context.get("constitution", "")
        if constitution:
            if (
                "虚" in constitution and "补" in formula_props.get("functions", [])
            ) or ("热" in constitution and "清" in formula_props.get("functions", [])):
                adaptation + = 0.15

        return adaptation

    async def _check_contraindications(
        self, formula: TCMEntity, patient_context: dict[str, Any] | None
    )-> list[str]:
        """检查禁忌症"""
        contraindications = []

        formula_contraindications = formula.properties.get("contraindications", [])

        if patient_context:
            # 检查年龄禁忌
            age = patient_context.get("age", 0)
            if age < 18 and "孕妇禁用" not in formula_contraindications:
                if any("热" in contra for contra in formula_contraindications):
                    contraindications.append("儿童慎用热性药物")

            # 检查性别禁忌
            gender = patient_context.get("gender", "")
            if gender == "female":
                pregnancy = patient_context.get("pregnancy", False)
                if pregnancy and "孕妇禁用" in formula_contraindications:
                    contraindications.append("孕妇禁用")

            # 检查疾病禁忌
            diseases = patient_context.get("diseases", [])
            for disease in diseases:
                if disease in formula_contraindications:
                    contraindications.append(f"{disease}患者禁用")

        return contraindications

    async def _generate_recommendation_reasoning(
        self,
        formula: TCMEntity,
        syndrome_mapping: SyndromeMapping,
        recommendation_score: float,
    )-> str:
        """生成推荐说明"""
        reasoning_parts = []

        # 证型匹配说明
        reasoning_parts.append(f"针对{syndrome_mapping.syndrome_name}")

        # 方剂功效说明
        functions = formula.properties.get("functions", [])
        if functions:
            reasoning_parts.append(f"功效：{', '.join(functions)}")

        # 推荐强度说明
        if recommendation_score > = 0.8:
            reasoning_parts.append("强烈推荐")
        elif recommendation_score > = 0.6:
            reasoning_parts.append("推荐")
        else:
            reasoning_parts.append("可考虑")

        return "；".join(reasoning_parts)

    def _deduplicate_recommendations(
        self, recommendations: list[FormulaRecommendation]
    )-> list[FormulaRecommendation]:
        """去重推荐"""
        seen_formulas = set()
        deduplicated = []

        for rec in recommendations:
            if rec.formula_id not in seen_formulas:
                seen_formulas.add(rec.formula_id)
                deduplicated.append(rec)
            else:
                # 合并相同方剂的适用证型
                for existing_rec in deduplicated:
                    if existing_rec.formula_id == rec.formula_id:
                        existing_rec.applicable_syndromes.extend(
                            rec.applicable_syndromes
                        )
                        # 取较高的推荐分数
                        existing_rec.recommendation_score = max(
                            existing_rec.recommendation_score, rec.recommendation_score
                        )
                        break

        return deduplicated

    @cached(ttl = 600)
    async def query_entity_relations(
        self,
        entity_id: str,
        relation_types: list[RelationType] | None = None,
        max_depth: int = 2,
    )-> dict[str, Any]:
        """
        查询实体关系

        Args:
            entity_id: 实体ID
            relation_types: 关系类型过滤
            max_depth: 最大查询深度

        Returns:
            关系查询结果
        """
        try:
            self.stats["inference_queries"] + = 1

            result = {
                "entity": self.entities.get(entity_id),
                "relations": [],
                "connected_entities": [],
            }

            if not result["entity"]:
                return result

            # 递归查询关系
            visited = set()
            relations_found = await self._recursive_relation_query(
                entity_id, relation_types, max_depth, visited
            )

            result["relations"] = relations_found
            result["connected_entities"] = [
                self.entities[eid] for eid in visited if eid ! = entity_id
            ]

            return result

        except Exception as e:
            logger.error(f"关系查询失败: {e}")
            raise InquiryServiceError(f"关系查询失败: {e}")

    async def _recursive_relation_query(
        self,
        entity_id: str,
        relation_types: list[RelationType] | None,
        depth: int,
        visited: set[str],
    )-> list[TCMRelation]:
        """递归查询关系"""
        if depth < = 0 or entity_id in visited:
            return []

        visited.add(entity_id)
        relations_found = []

        relation_ids = self.relation_index.get(entity_id, set())

        for relation_id in relation_ids:
            relation = self.relations[relation_id]

            # 类型过滤
            if relation_types and relation.relation_type not in relation_types:
                continue

            relations_found.append(relation)

            # 递归查询连接的实体
            if depth > 1:
                next_entity_id = (
                    relation.target_id
                    if relation.source_id == entity_id
                    else relation.source_id
                )

                sub_relations = await self._recursive_relation_query(
                    next_entity_id, relation_types, depth - 1, visited
                )
                relations_found.extend(sub_relations)

        return relations_found

    @memory_optimized
    async def get_knowledge_stats(self)-> dict[str, Any]:
        """获取知识图谱统计"""
        entity_stats = {}
        for entity_type in TCMEntityType:
            entity_stats[entity_type.value] = len(self.entity_index[entity_type])

        relation_stats = {}
        for relation_type in RelationType:
            count = sum(
                1
                for rel in self.relations.values()
                if rel.relation_type == relation_type
            )
            relation_stats[relation_type.value] = count

        return {
            * *self.stats,
            "entity_stats": entity_stats,
            "relation_stats": relation_stats,
            "knowledge_coverage": {
                "symptoms": len(self.entity_index[TCMEntityType.SYMPTOM]),
                "syndromes": len(self.entity_index[TCMEntityType.SYNDROME]),
                "formulas": len(self.entity_index[TCMEntityType.FORMULA]),
            },
        }

    async def update_entity(self, entity: TCMEntity):
        """更新实体"""
        if entity.id in self.entities:
            old_entity = self.entities[entity.id]
            self.entity_index[old_entity.entity_type].discard(entity.id)

        self._add_entity(entity)
        logger.info(f"实体已更新: {entity.id}")

    async def update_relation(self, relation: TCMRelation):
        """更新关系"""
        if relation.id in self.relations:
            old_relation = self.relations[relation.id]
            self.relation_index[old_relation.source_id].discard(relation.id)
            self.relation_index[old_relation.target_id].discard(relation.id)

        self._add_relation(relation)
        logger.info(f"关系已更新: {relation.id}")
