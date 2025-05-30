#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱增强器
支持中医知识图谱的构建、查询、推理和动态更新
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Literal
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
from loguru import logger
from datetime import datetime

from ..observability.metrics import MetricsCollector
from ..tcm.tcm_models import (
    ConstitutionType, SyndromeType, TreatmentPrinciple,
    HerbalFormula, SingleHerb
)


class NodeType(str, Enum):
    """节点类型"""
    SYMPTOM = "symptom"                    # 症状
    SYNDROME = "syndrome"                  # 证型
    CONSTITUTION = "constitution"          # 体质
    HERB = "herb"                         # 中药
    FORMULA = "formula"                   # 方剂
    ORGAN = "organ"                       # 脏腑
    MERIDIAN = "meridian"                 # 经络
    ACUPOINT = "acupoint"                 # 穴位
    DISEASE = "disease"                   # 疾病
    TREATMENT = "treatment"               # 治疗方法
    PRINCIPLE = "principle"               # 治疗原则
    CONCEPT = "concept"                   # 概念


class RelationType(str, Enum):
    """关系类型"""
    CAUSES = "causes"                     # 导致
    TREATS = "treats"                     # 治疗
    CONTAINS = "contains"                 # 包含
    BELONGS_TO = "belongs_to"             # 属于
    SIMILAR_TO = "similar_to"             # 相似于
    OPPOSITE_TO = "opposite_to"           # 相对于
    ENHANCES = "enhances"                 # 增强
    INHIBITS = "inhibits"                 # 抑制
    LOCATED_IN = "located_in"             # 位于
    CONNECTS_TO = "connects_to"           # 连接到
    MANIFESTS_AS = "manifests_as"         # 表现为
    DIAGNOSED_BY = "diagnosed_by"         # 诊断依据
    COMPOSED_OF = "composed_of"           # 组成
    COMPATIBLE_WITH = "compatible_with"   # 配伍
    INCOMPATIBLE_WITH = "incompatible_with"  # 相克


@dataclass
class KGNode:
    """知识图谱节点"""
    id: str
    name: str
    type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    confidence: float = 1.0
    source: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class KGRelation:
    """知识图谱关系"""
    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: str = ""
    created_at: str = ""


@dataclass
class KGQuery:
    """知识图谱查询"""
    query_type: str
    entities: List[str] = field(default_factory=list)
    relations: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    max_depth: int = 3
    max_results: int = 100


@dataclass
class KGQueryResult:
    """知识图谱查询结果"""
    nodes: List[KGNode] = field(default_factory=list)
    relations: List[KGRelation] = field(default_factory=list)
    paths: List[List[str]] = field(default_factory=list)
    reasoning_chain: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditRecord:
    entity_id: str
    entity_type: str
    action: Literal['add', 'update', 'delete', 'crowdsource']
    status: Literal['pending', 'approved', 'rejected']
    submitter: str
    reviewer: str = ''
    comment: str = ''
    timestamp: str = ''


class TCMKnowledgeBase:
    """中医知识库"""
    
    def __init__(self):
        self.symptoms = self._load_symptoms()
        self.syndromes = self._load_syndromes()
        self.constitutions = self._load_constitutions()
        self.herbs = self._load_herbs()
        self.formulas = self._load_formulas()
        self.organs = self._load_organs()
        self.meridians = self._load_meridians()
        self.acupoints = self._load_acupoints()
        self.diseases = self._load_diseases()
        self.treatments = self._load_treatments()
    
    def _load_symptoms(self) -> Dict[str, Dict[str, Any]]:
        """加载症状知识"""
        return {
            "头痛": {
                "type": "symptom",
                "category": "头部症状",
                "severity_levels": ["轻微", "中度", "严重"],
                "related_organs": ["肝", "肾", "心"],
                "common_syndromes": ["肝阳上亢", "肾精不足", "血瘀"],
                "description": "头部疼痛，可为胀痛、刺痛、隐痛等"
            },
            "失眠": {
                "type": "symptom",
                "category": "神志症状",
                "severity_levels": ["偶发", "频发", "持续"],
                "related_organs": ["心", "肝", "脾", "肾"],
                "common_syndromes": ["心肾不交", "肝郁化火", "脾虚"],
                "description": "入睡困难或睡眠质量差"
            },
            "疲劳": {
                "type": "symptom",
                "category": "全身症状",
                "severity_levels": ["轻度", "中度", "重度"],
                "related_organs": ["脾", "肾", "心"],
                "common_syndromes": ["脾气虚", "肾阳虚", "气血两虚"],
                "description": "身体乏力，精神不振"
            }
        }
    
    def _load_syndromes(self) -> Dict[str, Dict[str, Any]]:
        """加载证型知识"""
        return {
            "脾气虚": {
                "type": "syndrome",
                "category": "虚证",
                "main_symptoms": ["食欲不振", "腹胀", "便溏", "乏力"],
                "tongue": "舌淡苔白",
                "pulse": "脉缓弱",
                "treatment_principle": "健脾益气",
                "common_formulas": ["四君子汤", "补中益气汤"],
                "description": "脾脏功能虚弱，运化失常"
            },
            "肾阴虚": {
                "type": "syndrome",
                "category": "虚证",
                "main_symptoms": ["腰膝酸软", "头晕耳鸣", "潮热盗汗"],
                "tongue": "舌红少苔",
                "pulse": "脉细数",
                "treatment_principle": "滋阴补肾",
                "common_formulas": ["六味地黄丸", "左归丸"],
                "description": "肾阴不足，虚热内生"
            }
        }
    
    def _load_constitutions(self) -> Dict[str, Dict[str, Any]]:
        """加载体质知识"""
        return {
            "气虚质": {
                "type": "constitution",
                "characteristics": ["气短懒言", "乏力", "易感冒", "自汗"],
                "psychological": ["内向", "情绪不稳定"],
                "adaptation": ["不耐受风、寒、暑、湿邪"],
                "common_diseases": ["感冒", "胃下垂", "子宫脱垂"],
                "regulation": ["补气", "健脾", "益肺"],
                "suitable_herbs": ["人参", "黄芪", "白术", "甘草"],
                "description": "元气不足，以疲乏、气短为主要特征"
            },
            "阴虚质": {
                "type": "constitution",
                "characteristics": ["手足心热", "口燥咽干", "喜冷饮"],
                "psychological": ["性情急躁", "外向好动"],
                "adaptation": ["不耐受暑、热、燥邪"],
                "common_diseases": ["失眠", "便秘", "更年期综合征"],
                "regulation": ["滋阴", "清热", "养血"],
                "suitable_herbs": ["沙参", "麦冬", "石斛", "玉竹"],
                "description": "阴液亏少，以口燥咽干、手足心热为主要特征"
            }
        }
    
    def _load_herbs(self) -> Dict[str, Dict[str, Any]]:
        """加载中药知识"""
        return {
            "人参": {
                "type": "herb",
                "category": "补气药",
                "nature": "温",
                "flavor": "甘、微苦",
                "meridians": ["脾", "肺", "心", "肾"],
                "effects": ["大补元气", "复脉固脱", "补脾益肺", "生津养血"],
                "indications": ["气虚欲脱", "脾肺气虚", "津伤口渴"],
                "contraindications": ["实热证", "湿热证"],
                "dosage": "3-9g",
                "processing": ["生晒参", "红参", "白参"],
                "description": "补气第一要药"
            },
            "黄芪": {
                "type": "herb",
                "category": "补气药",
                "nature": "微温",
                "flavor": "甘",
                "meridians": ["脾", "肺"],
                "effects": ["补气升阳", "固表止汗", "利水消肿", "托疮生肌"],
                "indications": ["气虚乏力", "中气下陷", "表虚自汗"],
                "contraindications": ["表实邪盛", "气滞湿阻"],
                "dosage": "9-30g",
                "processing": ["生黄芪", "炙黄芪"],
                "description": "补气固表要药"
            }
        }
    
    def _load_formulas(self) -> Dict[str, Dict[str, Any]]:
        """加载方剂知识"""
        return {
            "四君子汤": {
                "type": "formula",
                "category": "补益剂",
                "composition": {
                    "人参": "9g",
                    "白术": "9g",
                    "茯苓": "9g",
                    "甘草": "6g"
                },
                "effects": ["益气健脾"],
                "indications": ["脾胃气虚证"],
                "symptoms": ["面色萎白", "语声低微", "气短乏力", "食少便溏"],
                "contraindications": ["邪实证"],
                "modifications": {
                    "六君子汤": "加陈皮、半夏",
                    "香砂六君子汤": "加木香、砂仁"
                },
                "description": "补气健脾的基础方"
            },
            "六味地黄丸": {
                "type": "formula",
                "category": "补益剂",
                "composition": {
                    "熟地黄": "24g",
                    "山茱萸": "12g",
                    "山药": "12g",
                    "泽泻": "9g",
                    "茯苓": "9g",
                    "牡丹皮": "9g"
                },
                "effects": ["滋阴补肾"],
                "indications": ["肾阴虚证"],
                "symptoms": ["腰膝酸软", "头晕耳鸣", "遗精盗汗"],
                "contraindications": ["脾虚便溏"],
                "modifications": {
                    "知柏地黄丸": "加知母、黄柏",
                    "杞菊地黄丸": "加枸杞子、菊花"
                },
                "description": "滋阴补肾的代表方"
            }
        }
    
    def _load_organs(self) -> Dict[str, Dict[str, Any]]:
        """加载脏腑知识"""
        return {
            "心": {
                "type": "organ",
                "category": "五脏",
                "functions": ["主血脉", "主神志"],
                "emotions": ["喜"],
                "season": "夏",
                "element": "火",
                "paired_organ": "小肠",
                "opening": "舌",
                "tissue": "血脉",
                "common_diseases": ["心悸", "失眠", "健忘"],
                "description": "心为君主之官，主血脉和神志"
            },
            "脾": {
                "type": "organ",
                "category": "五脏",
                "functions": ["主运化", "主升清", "主统血"],
                "emotions": ["思"],
                "season": "长夏",
                "element": "土",
                "paired_organ": "胃",
                "opening": "口",
                "tissue": "肌肉",
                "common_diseases": ["腹胀", "便溏", "乏力"],
                "description": "脾为后天之本，主运化水谷精微"
            }
        }
    
    def _load_meridians(self) -> Dict[str, Dict[str, Any]]:
        """加载经络知识"""
        return {
            "手太阴肺经": {
                "type": "meridian",
                "category": "十二正经",
                "organ": "肺",
                "element": "金",
                "flow_time": "3-5时",
                "acupoints_count": 11,
                "main_acupoints": ["中府", "云门", "天府", "侠白", "尺泽", "孔最", "列缺", "经渠", "太渊", "鱼际", "少商"],
                "pathway": "起于中焦，下络大肠，还循胃口，上膈属肺",
                "functions": ["主气", "司呼吸", "通调水道"],
                "common_diseases": ["咳嗽", "气喘", "胸痛"],
                "description": "肺经主气，司呼吸，为十二经脉之首"
            }
        }
    
    def _load_acupoints(self) -> Dict[str, Dict[str, Any]]:
        """加载穴位知识"""
        return {
            "太渊": {
                "type": "acupoint",
                "meridian": "手太阴肺经",
                "category": "原穴",
                "location": "腕掌侧横纹桡侧，桡动脉搏动处",
                "functions": ["补肺益气", "通经活络"],
                "indications": ["咳嗽", "气喘", "胸痛", "腕臂痛"],
                "needling": "直刺0.2-0.3寸，避开动脉",
                "contraindications": ["孕妇慎用"],
                "description": "肺经原穴，脉会太渊"
            }
        }
    
    def _load_diseases(self) -> Dict[str, Dict[str, Any]]:
        """加载疾病知识"""
        return {
            "感冒": {
                "type": "disease",
                "category": "外感病",
                "etiology": ["风邪侵袭"],
                "pathogenesis": ["卫表不固", "正气不足"],
                "classification": ["风寒感冒", "风热感冒", "暑湿感冒"],
                "symptoms": ["恶寒发热", "头痛", "鼻塞", "咳嗽"],
                "treatment_principles": ["解表散邪"],
                "common_formulas": ["桂枝汤", "麻黄汤", "银翘散"],
                "prevention": ["增强体质", "避风寒"],
                "description": "外感风邪引起的常见疾病"
            }
        }
    
    def _load_treatments(self) -> Dict[str, Dict[str, Any]]:
        """加载治疗方法知识"""
        return {
            "针灸": {
                "type": "treatment",
                "category": "外治法",
                "principles": ["疏通经络", "调和阴阳", "扶正祛邪"],
                "methods": ["毫针刺法", "艾灸法", "拔罐法", "刮痧法"],
                "indications": ["痛证", "瘫痪", "内科杂病"],
                "contraindications": ["出血性疾病", "皮肤感染"],
                "advantages": ["无副作用", "疗效确切"],
                "description": "通过刺激穴位调节人体功能"
            }
        }


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self, knowledge_base: TCMKnowledgeBase):
        self.kb = knowledge_base
        self.graph = nx.MultiDiGraph()
        self.nodes: Dict[str, KGNode] = {}
        self.relations: Dict[str, KGRelation] = {}
    
    async def build_graph(self) -> nx.MultiDiGraph:
        """构建知识图谱"""
        logger.info("开始构建中医知识图谱")
        
        # 添加节点
        await self._add_symptom_nodes()
        await self._add_syndrome_nodes()
        await self._add_constitution_nodes()
        await self._add_herb_nodes()
        await self._add_formula_nodes()
        await self._add_organ_nodes()
        await self._add_meridian_nodes()
        await self._add_acupoint_nodes()
        await self._add_disease_nodes()
        await self._add_treatment_nodes()
        
        # 添加关系
        await self._add_symptom_relations()
        await self._add_syndrome_relations()
        await self._add_constitution_relations()
        await self._add_herb_relations()
        await self._add_formula_relations()
        await self._add_organ_relations()
        await self._add_meridian_relations()
        await self._add_treatment_relations()
        
        logger.info(f"知识图谱构建完成，节点数: {len(self.nodes)}, 关系数: {len(self.relations)}")
        return self.graph
    
    async def _add_symptom_nodes(self):
        """添加症状节点"""
        for name, data in self.kb.symptoms.items():
            node = KGNode(
                id=f"symptom_{name}",
                name=name,
                type=NodeType.SYMPTOM,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_syndrome_nodes(self):
        """添加证型节点"""
        for name, data in self.kb.syndromes.items():
            node = KGNode(
                id=f"syndrome_{name}",
                name=name,
                type=NodeType.SYNDROME,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_constitution_nodes(self):
        """添加体质节点"""
        for name, data in self.kb.constitutions.items():
            node = KGNode(
                id=f"constitution_{name}",
                name=name,
                type=NodeType.CONSTITUTION,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_herb_nodes(self):
        """添加中药节点"""
        for name, data in self.kb.herbs.items():
            node = KGNode(
                id=f"herb_{name}",
                name=name,
                type=NodeType.HERB,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_formula_nodes(self):
        """添加方剂节点"""
        for name, data in self.kb.formulas.items():
            node = KGNode(
                id=f"formula_{name}",
                name=name,
                type=NodeType.FORMULA,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_organ_nodes(self):
        """添加脏腑节点"""
        for name, data in self.kb.organs.items():
            node = KGNode(
                id=f"organ_{name}",
                name=name,
                type=NodeType.ORGAN,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_meridian_nodes(self):
        """添加经络节点"""
        for name, data in self.kb.meridians.items():
            node = KGNode(
                id=f"meridian_{name}",
                name=name,
                type=NodeType.MERIDIAN,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_acupoint_nodes(self):
        """添加穴位节点"""
        for name, data in self.kb.acupoints.items():
            node = KGNode(
                id=f"acupoint_{name}",
                name=name,
                type=NodeType.ACUPOINT,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_disease_nodes(self):
        """添加疾病节点"""
        for name, data in self.kb.diseases.items():
            node = KGNode(
                id=f"disease_{name}",
                name=name,
                type=NodeType.DISEASE,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_treatment_nodes(self):
        """添加治疗方法节点"""
        for name, data in self.kb.treatments.items():
            node = KGNode(
                id=f"treatment_{name}",
                name=name,
                type=NodeType.TREATMENT,
                properties=data,
                description=data.get("description", "")
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)
    
    async def _add_symptom_relations(self):
        """添加症状相关关系"""
        for symptom_name, symptom_data in self.kb.symptoms.items():
            symptom_id = f"symptom_{symptom_name}"
            
            # 症状与脏腑的关系
            for organ in symptom_data.get("related_organs", []):
                organ_id = f"organ_{organ}"
                if organ_id in self.nodes:
                    self._add_relation(
                        symptom_id, organ_id, RelationType.LOCATED_IN,
                        {"description": f"{symptom_name}与{organ}相关"}
                    )
            
            # 症状与证型的关系
            for syndrome in symptom_data.get("common_syndromes", []):
                syndrome_id = f"syndrome_{syndrome}"
                if syndrome_id in self.nodes:
                    self._add_relation(
                        syndrome_id, symptom_id, RelationType.MANIFESTS_AS,
                        {"description": f"{syndrome}表现为{symptom_name}"}
                    )
    
    async def _add_syndrome_relations(self):
        """添加证型相关关系"""
        for syndrome_name, syndrome_data in self.kb.syndromes.items():
            syndrome_id = f"syndrome_{syndrome_name}"
            
            # 证型与方剂的关系
            for formula in syndrome_data.get("common_formulas", []):
                formula_id = f"formula_{formula}"
                if formula_id in self.nodes:
                    self._add_relation(
                        formula_id, syndrome_id, RelationType.TREATS,
                        {"description": f"{formula}治疗{syndrome_name}"}
                    )
    
    async def _add_constitution_relations(self):
        """添加体质相关关系"""
        for constitution_name, constitution_data in self.kb.constitutions.items():
            constitution_id = f"constitution_{constitution_name}"
            
            # 体质与中药的关系
            for herb in constitution_data.get("suitable_herbs", []):
                herb_id = f"herb_{herb}"
                if herb_id in self.nodes:
                    self._add_relation(
                        herb_id, constitution_id, RelationType.ENHANCES,
                        {"description": f"{herb}适合{constitution_name}"}
                    )
    
    async def _add_herb_relations(self):
        """添加中药相关关系"""
        for herb_name, herb_data in self.kb.herbs.items():
            herb_id = f"herb_{herb_name}"
            
            # 中药与经络的关系
            for meridian in herb_data.get("meridians", []):
                meridian_id = f"meridian_手太阴{meridian}经" if meridian in ["肺"] else f"meridian_{meridian}"
                # 简化处理，实际应该有完整的经络映射
                organ_id = f"organ_{meridian}"
                if organ_id in self.nodes:
                    self._add_relation(
                        herb_id, organ_id, RelationType.ENHANCES,
                        {"description": f"{herb_name}归{meridian}经"}
                    )
    
    async def _add_formula_relations(self):
        """添加方剂相关关系"""
        for formula_name, formula_data in self.kb.formulas.items():
            formula_id = f"formula_{formula_name}"
            
            # 方剂与中药的关系
            for herb, dosage in formula_data.get("composition", {}).items():
                herb_id = f"herb_{herb}"
                if herb_id in self.nodes:
                    self._add_relation(
                        formula_id, herb_id, RelationType.CONTAINS,
                        {"dosage": dosage, "description": f"{formula_name}含有{herb}"}
                    )
    
    async def _add_organ_relations(self):
        """添加脏腑相关关系"""
        for organ_name, organ_data in self.kb.organs.items():
            organ_id = f"organ_{organ_name}"
            
            # 脏腑与经络的关系
            if organ_name == "肺":
                meridian_id = f"meridian_手太阴肺经"
                if meridian_id in self.nodes:
                    self._add_relation(
                        organ_id, meridian_id, RelationType.CONNECTS_TO,
                        {"description": f"{organ_name}与手太阴肺经相连"}
                    )
    
    async def _add_meridian_relations(self):
        """添加经络相关关系"""
        for meridian_name, meridian_data in self.kb.meridians.items():
            meridian_id = f"meridian_{meridian_name}"
            
            # 经络与穴位的关系
            for acupoint in meridian_data.get("main_acupoints", []):
                acupoint_id = f"acupoint_{acupoint}"
                if acupoint_id in self.nodes:
                    self._add_relation(
                        meridian_id, acupoint_id, RelationType.CONTAINS,
                        {"description": f"{meridian_name}包含{acupoint}穴"}
                    )
    
    async def _add_treatment_relations(self):
        """添加治疗方法相关关系"""
        # 针灸与穴位的关系
        treatment_id = "treatment_针灸"
        if treatment_id in self.nodes:
            for acupoint_name in self.kb.acupoints.keys():
                acupoint_id = f"acupoint_{acupoint_name}"
                if acupoint_id in self.nodes:
                    self._add_relation(
                        treatment_id, acupoint_id, RelationType.CONTAINS,
                        {"description": f"针灸使用{acupoint_name}穴"}
                    )
    
    def _add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        properties: Dict[str, Any] = None
    ):
        """添加关系"""
        relation_id = f"{source_id}_{relation_type.value}_{target_id}"
        
        relation = KGRelation(
            id=relation_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties or {}
        )
        
        self.relations[relation_id] = relation
        self.graph.add_edge(
            source_id, target_id,
            key=relation_type.value,
            **relation.__dict__
        )


class KnowledgeGraphQuerier:
    """知识图谱查询器"""
    
    def __init__(self, graph: nx.MultiDiGraph, nodes: Dict[str, KGNode], relations: Dict[str, KGRelation]):
        self.graph = graph
        self.nodes = nodes
        self.relations = relations
    
    async def query(self, kg_query: KGQuery) -> KGQueryResult:
        """执行知识图谱查询"""
        try:
            result = KGQueryResult()
            
            if kg_query.query_type == "find_related":
                result = await self._find_related_entities(kg_query)
            elif kg_query.query_type == "find_path":
                result = await self._find_paths(kg_query)
            elif kg_query.query_type == "reasoning":
                result = await self._perform_reasoning(kg_query)
            elif kg_query.query_type == "similarity":
                result = await self._find_similar_entities(kg_query)
            else:
                logger.warning(f"未知的查询类型: {kg_query.query_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"知识图谱查询失败: {e}")
            return KGQueryResult()
    
    async def _find_related_entities(self, kg_query: KGQuery) -> KGQueryResult:
        """查找相关实体"""
        result = KGQueryResult()
        
        for entity in kg_query.entities:
            # 查找匹配的节点
            matching_nodes = self._find_nodes_by_name(entity)
            
            for node_id in matching_nodes:
                if node_id in self.graph:
                    # 获取邻居节点
                    neighbors = list(self.graph.neighbors(node_id))
                    predecessors = list(self.graph.predecessors(node_id))
                    
                    all_related = set(neighbors + predecessors)
                    
                    # 添加相关节点
                    for related_id in all_related:
                        if related_id in self.nodes:
                            result.nodes.append(self.nodes[related_id])
                    
                    # 添加相关关系
                    for neighbor in neighbors:
                        edges = self.graph.get_edge_data(node_id, neighbor)
                        for edge_data in edges.values():
                            if edge_data['id'] in self.relations:
                                result.relations.append(self.relations[edge_data['id']])
                    
                    for predecessor in predecessors:
                        edges = self.graph.get_edge_data(predecessor, node_id)
                        for edge_data in edges.values():
                            if edge_data['id'] in self.relations:
                                result.relations.append(self.relations[edge_data['id']])
        
        result.confidence = 0.8
        return result
    
    async def _find_paths(self, kg_query: KGQuery) -> KGQueryResult:
        """查找路径"""
        result = KGQueryResult()
        
        if len(kg_query.entities) >= 2:
            source_nodes = self._find_nodes_by_name(kg_query.entities[0])
            target_nodes = self._find_nodes_by_name(kg_query.entities[1])
            
            for source_id in source_nodes:
                for target_id in target_nodes:
                    try:
                        # 查找最短路径
                        if nx.has_path(self.graph, source_id, target_id):
                            path = nx.shortest_path(self.graph, source_id, target_id)
                            result.paths.append(path)
                            
                            # 添加路径上的节点和关系
                            for node_id in path:
                                if node_id in self.nodes:
                                    result.nodes.append(self.nodes[node_id])
                            
                            for i in range(len(path) - 1):
                                edges = self.graph.get_edge_data(path[i], path[i + 1])
                                for edge_data in edges.values():
                                    if edge_data['id'] in self.relations:
                                        result.relations.append(self.relations[edge_data['id']])
                    
                    except nx.NetworkXNoPath:
                        continue
        
        result.confidence = 0.7
        return result
    
    async def _perform_reasoning(self, kg_query: KGQuery) -> KGQueryResult:
        """执行推理"""
        result = KGQueryResult()
        reasoning_chain = []
        
        # 简单的推理示例：症状 -> 证型 -> 治疗
        for entity in kg_query.entities:
            matching_nodes = self._find_nodes_by_name(entity)
            
            for node_id in matching_nodes:
                node = self.nodes.get(node_id)
                if not node:
                    continue
                
                reasoning_chain.append(f"起始实体: {node.name} ({node.type.value})")
                
                # 如果是症状，查找相关证型
                if node.type == NodeType.SYMPTOM:
                    syndrome_nodes = self._find_related_by_type(node_id, NodeType.SYNDROME)
                    for syndrome_id in syndrome_nodes:
                        syndrome = self.nodes.get(syndrome_id)
                        if syndrome:
                            reasoning_chain.append(f"可能证型: {syndrome.name}")
                            result.nodes.append(syndrome)
                            
                            # 查找治疗方剂
                            formula_nodes = self._find_related_by_type(syndrome_id, NodeType.FORMULA)
                            for formula_id in formula_nodes:
                                formula = self.nodes.get(formula_id)
                                if formula:
                                    reasoning_chain.append(f"推荐方剂: {formula.name}")
                                    result.nodes.append(formula)
                
                # 如果是体质，查找适合的中药
                elif node.type == NodeType.CONSTITUTION:
                    herb_nodes = self._find_related_by_type(node_id, NodeType.HERB)
                    for herb_id in herb_nodes:
                        herb = self.nodes.get(herb_id)
                        if herb:
                            reasoning_chain.append(f"适合中药: {herb.name}")
                            result.nodes.append(herb)
        
        result.reasoning_chain = reasoning_chain
        result.confidence = 0.6
        return result
    
    async def _find_similar_entities(self, kg_query: KGQuery) -> KGQueryResult:
        """查找相似实体"""
        result = KGQueryResult()
        
        for entity in kg_query.entities:
            matching_nodes = self._find_nodes_by_name(entity)
            
            for node_id in matching_nodes:
                node = self.nodes.get(node_id)
                if not node:
                    continue
                
                # 查找同类型的节点
                similar_nodes = []
                for other_id, other_node in self.nodes.items():
                    if other_node.type == node.type and other_id != node_id:
                        # 简单的相似度计算（基于共同邻居）
                        common_neighbors = set(self.graph.neighbors(node_id)) & set(self.graph.neighbors(other_id))
                        if len(common_neighbors) > 0:
                            similarity = len(common_neighbors) / max(
                                len(list(self.graph.neighbors(node_id))),
                                len(list(self.graph.neighbors(other_id))),
                                1
                            )
                            similar_nodes.append((other_node, similarity))
                
                # 按相似度排序
                similar_nodes.sort(key=lambda x: x[1], reverse=True)
                
                # 添加最相似的节点
                for similar_node, similarity in similar_nodes[:kg_query.max_results]:
                    result.nodes.append(similar_node)
                    result.metadata[similar_node.id] = {"similarity": similarity}
        
        result.confidence = 0.5
        return result
    
    def _find_nodes_by_name(self, name: str) -> List[str]:
        """根据名称查找节点"""
        matching_nodes = []
        
        for node_id, node in self.nodes.items():
            if node.name == name or name in node.aliases:
                matching_nodes.append(node_id)
        
        return matching_nodes
    
    def _find_related_by_type(self, node_id: str, target_type: NodeType) -> List[str]:
        """查找特定类型的相关节点"""
        related_nodes = []
        
        # 查找直接邻居
        neighbors = list(self.graph.neighbors(node_id))
        predecessors = list(self.graph.predecessors(node_id))
        
        all_related = set(neighbors + predecessors)
        
        for related_id in all_related:
            related_node = self.nodes.get(related_id)
            if related_node and related_node.type == target_type:
                related_nodes.append(related_id)
        
        return related_nodes


class KnowledgeGraphEnhancer:
    """知识图谱增强器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.knowledge_base = TCMKnowledgeBase()
        self.builder = KnowledgeGraphBuilder(self.knowledge_base)
        self.graph = None
        self.querier = None
        self.audit_records: List[AuditRecord] = []
    
    async def initialize(self):
        """初始化知识图谱"""
        logger.info("初始化知识图谱增强器")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 构建知识图谱
            self.graph = await self.builder.build_graph()
            
            # 初始化查询器
            self.querier = KnowledgeGraphQuerier(
                self.graph,
                self.builder.nodes,
                self.builder.relations
            )
            
            # 记录指标
            build_time = asyncio.get_event_loop().time() - start_time
            await self.metrics_collector.record_histogram(
                "kg_build_duration_seconds",
                build_time
            )
            
            await self.metrics_collector.record_gauge(
                "kg_nodes_total",
                len(self.builder.nodes)
            )
            
            await self.metrics_collector.record_gauge(
                "kg_relations_total",
                len(self.builder.relations)
            )
            
            logger.info("知识图谱增强器初始化完成")
            
        except Exception as e:
            logger.error(f"知识图谱初始化失败: {e}")
            raise
    
    async def enhance_query(
        self,
        query: str,
        entities: List[str],
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        使用知识图谱增强查询
        
        Args:
            query: 原始查询
            entities: 识别的实体
            max_depth: 最大查询深度
            
        Returns:
            增强信息
        """
        if not self.querier:
            logger.warning("知识图谱未初始化")
            return {}
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            enhancement = {
                "related_entities": [],
                "reasoning_paths": [],
                "similar_concepts": [],
                "treatment_suggestions": [],
                "knowledge_context": []
            }
            
            # 查找相关实体
            related_query = KGQuery(
                query_type="find_related",
                entities=entities,
                max_depth=max_depth
            )
            related_result = await self.querier.query(related_query)
            
            for node in related_result.nodes:
                enhancement["related_entities"].append({
                    "name": node.name,
                    "type": node.type.value,
                    "description": node.description,
                    "confidence": node.confidence
                })
            
            # 执行推理
            reasoning_query = KGQuery(
                query_type="reasoning",
                entities=entities
            )
            reasoning_result = await self.querier.query(reasoning_query)
            enhancement["reasoning_paths"] = reasoning_result.reasoning_chain
            
            # 查找相似概念
            similarity_query = KGQuery(
                query_type="similarity",
                entities=entities,
                max_results=5
            )
            similarity_result = await self.querier.query(similarity_query)
            
            for node in similarity_result.nodes:
                similarity = similarity_result.metadata.get(node.id, {}).get("similarity", 0)
                enhancement["similar_concepts"].append({
                    "name": node.name,
                    "type": node.type.value,
                    "similarity": similarity
                })
            
            # 生成治疗建议
            treatment_suggestions = self._generate_treatment_suggestions(
                entities, related_result, reasoning_result
            )
            enhancement["treatment_suggestions"] = treatment_suggestions
            
            # 添加知识上下文
            knowledge_context = self._generate_knowledge_context(
                entities, related_result
            )
            enhancement["knowledge_context"] = knowledge_context
            
            # 记录指标
            processing_time = asyncio.get_event_loop().time() - start_time
            await self.metrics_collector.record_histogram(
                "kg_enhancement_duration_seconds",
                processing_time
            )
            
            await self.metrics_collector.increment_counter(
                "kg_enhancement_requests_total",
                {"entity_count": str(len(entities))}
            )
            
            return enhancement
            
        except Exception as e:
            logger.error(f"知识图谱增强失败: {e}")
            return {}
    
    def _generate_treatment_suggestions(
        self,
        entities: List[str],
        related_result: KGQueryResult,
        reasoning_result: KGQueryResult
    ) -> List[Dict[str, Any]]:
        """生成治疗建议"""
        suggestions = []
        
        # 从推理结果中提取方剂建议
        for node in reasoning_result.nodes:
            if node.type == NodeType.FORMULA:
                suggestions.append({
                    "type": "formula",
                    "name": node.name,
                    "description": node.description,
                    "confidence": 0.7
                })
            elif node.type == NodeType.HERB:
                suggestions.append({
                    "type": "herb",
                    "name": node.name,
                    "description": node.description,
                    "confidence": 0.6
                })
        
        # 从相关结果中提取治疗方法
        for node in related_result.nodes:
            if node.type == NodeType.TREATMENT:
                suggestions.append({
                    "type": "treatment",
                    "name": node.name,
                    "description": node.description,
                    "confidence": 0.5
                })
        
        return suggestions
    
    def _generate_knowledge_context(
        self,
        entities: List[str],
        related_result: KGQueryResult
    ) -> List[str]:
        """生成知识上下文"""
        context = []
        
        # 添加实体相关的背景知识
        for node in related_result.nodes:
            if node.type == NodeType.ORGAN:
                context.append(f"{node.name}的功能：{node.properties.get('functions', [])}")
            elif node.type == NodeType.SYNDROME:
                context.append(f"{node.name}的主要症状：{node.properties.get('main_symptoms', [])}")
            elif node.type == NodeType.CONSTITUTION:
                context.append(f"{node.name}的特征：{node.properties.get('characteristics', [])}")
        
        return context[:10]  # 限制上下文数量
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        if not self.graph:
            return {}
        
        stats = {
            "nodes_count": len(self.builder.nodes),
            "relations_count": len(self.builder.relations),
            "node_types": {},
            "relation_types": {},
            "graph_density": nx.density(self.graph),
            "connected_components": nx.number_weakly_connected_components(self.graph)
        }
        
        # 统计节点类型
        for node in self.builder.nodes.values():
            node_type = node.type.value
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1
        
        # 统计关系类型
        for relation in self.builder.relations.values():
            relation_type = relation.relation_type.value
            stats["relation_types"][relation_type] = stats["relation_types"].get(relation_type, 0) + 1
        
        return stats
    
    def submit_crowdsourced_knowledge(self, entity: KGNode, submitter: str):
        """用户众包补充知识，待专家审核"""
        record = AuditRecord(
            entity_id=entity.id,
            entity_type=entity.type.value,
            action='crowdsource',
            status='pending',
            submitter=submitter,
            timestamp=str(datetime.now())
        )
        self.audit_records.append(record)
        logger.info(f"收到众包知识补充，待审核: {entity.name}")
    
    def expert_review(self, entity_id: str, approve: bool, reviewer: str, comment: str = ""):
        """专家审核知识节点或关系"""
        for record in self.audit_records:
            if record.entity_id == entity_id and record.status == 'pending':
                record.status = 'approved' if approve else 'rejected'
                record.reviewer = reviewer
                record.comment = comment
                record.timestamp = str(datetime.now())
                logger.info(f"专家审核{'通过' if approve else '拒绝'}: {entity_id}")
                break 