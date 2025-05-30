#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱推理引擎 - 基于中医理论的智能推理和决策支持系统
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
import networkx as nx
import numpy as np
from collections import defaultdict, deque
import re


class ReasoningType(Enum):
    """推理类型"""
    SYNDROME_DIFFERENTIATION = "syndrome_differentiation"  # 辨证论治
    FORMULA_COMPOSITION = "formula_composition"            # 方剂配伍
    HERB_COMPATIBILITY = "herb_compatibility"              # 药物配伍
    CONSTITUTION_ANALYSIS = "constitution_analysis"        # 体质分析
    TREATMENT_PLANNING = "treatment_planning"              # 治疗规划
    PREVENTION_STRATEGY = "prevention_strategy"            # 预防策略
    LIFESTYLE_GUIDANCE = "lifestyle_guidance"              # 生活指导
    PROGNOSIS_PREDICTION = "prognosis_prediction"          # 预后预测


class ConfidenceLevel(Enum):
    """置信度级别"""
    VERY_LOW = "very_low"      # 很低 (0-0.2)
    LOW = "low"                # 低 (0.2-0.4)
    MEDIUM = "medium"          # 中等 (0.4-0.6)
    HIGH = "high"              # 高 (0.6-0.8)
    VERY_HIGH = "very_high"    # 很高 (0.8-1.0)


class EvidenceType(Enum):
    """证据类型"""
    SYMPTOM = "symptom"                    # 症状
    SIGN = "sign"                          # 体征
    TONGUE = "tongue"                      # 舌象
    PULSE = "pulse"                        # 脉象
    CONSTITUTION = "constitution"          # 体质
    LIFESTYLE = "lifestyle"                # 生活方式
    ENVIRONMENT = "environment"            # 环境因素
    MEDICAL_HISTORY = "medical_history"    # 病史
    LAB_RESULT = "lab_result"             # 检验结果


@dataclass
class Evidence:
    """证据"""
    id: str
    type: EvidenceType
    name: str
    value: Union[str, float, bool]
    confidence: float
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningRule:
    """推理规则"""
    id: str
    name: str
    description: str
    reasoning_type: ReasoningType
    conditions: List[Dict[str, Any]]  # 条件列表
    conclusions: List[Dict[str, Any]]  # 结论列表
    confidence_weight: float = 1.0
    priority: int = 1
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResult:
    """推理结果"""
    id: str
    reasoning_type: ReasoningType
    conclusion: str
    confidence: float
    confidence_level: ConfidenceLevel
    evidence_used: List[Evidence]
    rules_applied: List[str]
    reasoning_chain: List[str]
    recommendations: List[str] = field(default_factory=list)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeNode:
    """知识节点"""
    id: str
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class KnowledgeRelation:
    """知识关系"""
    id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0


class KnowledgeReasoningEngine:
    """知识图谱推理引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化推理引擎
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 知识图谱
        self.knowledge_graph = nx.MultiDiGraph()
        
        # 推理规则
        self.reasoning_rules: Dict[str, ReasoningRule] = {}
        
        # 中医知识库
        self.tcm_knowledge = self._init_tcm_knowledge()
        
        # 推理历史
        self.reasoning_history: List[ReasoningResult] = []
        
        # 缓存
        self.reasoning_cache: Dict[str, ReasoningResult] = {}
        
        # 统计信息
        self.stats = {
            "total_reasonings": 0,
            "reasonings_by_type": defaultdict(int),
            "average_confidence": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def _init_tcm_knowledge(self) -> Dict[str, Any]:
        """初始化中医知识库"""
        return {
            # 五脏六腑
            "organs": {
                "heart": {
                    "name": "心",
                    "functions": ["主血脉", "主神明"],
                    "emotions": ["喜"],
                    "related_organs": ["小肠", "肾"],
                    "pathological_changes": ["心气虚", "心血虚", "心阳虚", "心阴虚", "心火亢盛"]
                },
                "liver": {
                    "name": "肝",
                    "functions": ["主疏泄", "主藏血"],
                    "emotions": ["怒"],
                    "related_organs": ["胆", "脾"],
                    "pathological_changes": ["肝气郁结", "肝火上炎", "肝阳上亢", "肝血虚", "肝阴虚"]
                },
                "spleen": {
                    "name": "脾",
                    "functions": ["主运化", "主升清", "主统血"],
                    "emotions": ["思"],
                    "related_organs": ["胃", "肺"],
                    "pathological_changes": ["脾气虚", "脾阳虚", "脾不统血", "湿困脾土"]
                },
                "lung": {
                    "name": "肺",
                    "functions": ["主气", "主宣发肃降", "主通调水道"],
                    "emotions": ["悲"],
                    "related_organs": ["大肠", "肾"],
                    "pathological_changes": ["肺气虚", "肺阴虚", "肺热", "肺燥"]
                },
                "kidney": {
                    "name": "肾",
                    "functions": ["主藏精", "主水", "主纳气"],
                    "emotions": ["恐"],
                    "related_organs": ["膀胱", "心"],
                    "pathological_changes": ["肾阳虚", "肾阴虚", "肾精不足", "肾气虚"]
                }
            },
            
            # 病理因素
            "pathogenic_factors": {
                "wind": {"name": "风", "nature": "阳邪", "characteristics": ["善行数变", "为百病之长"]},
                "cold": {"name": "寒", "nature": "阴邪", "characteristics": ["易伤阳气", "主收引"]},
                "heat": {"name": "热", "nature": "阳邪", "characteristics": ["易伤阴液", "主升散"]},
                "dampness": {"name": "湿", "nature": "阴邪", "characteristics": ["重浊粘腻", "易阻气机"]},
                "dryness": {"name": "燥", "nature": "阳邪", "characteristics": ["干涩", "易伤津液"]},
                "fire": {"name": "火", "nature": "阳邪", "characteristics": ["炎上", "易伤阴血"]}
            },
            
            # 证型分类
            "syndrome_patterns": {
                "qi_deficiency": {
                    "name": "气虚证",
                    "symptoms": ["乏力", "气短", "声音低微", "自汗", "脉虚"],
                    "tongue": ["舌淡", "苔薄白"],
                    "treatment_principle": "补气"
                },
                "blood_deficiency": {
                    "name": "血虚证",
                    "symptoms": ["面色苍白", "头晕", "心悸", "失眠", "脉细"],
                    "tongue": ["舌淡", "苔薄"],
                    "treatment_principle": "补血"
                },
                "yin_deficiency": {
                    "name": "阴虚证",
                    "symptoms": ["五心烦热", "盗汗", "口干", "失眠", "脉细数"],
                    "tongue": ["舌红", "苔少"],
                    "treatment_principle": "滋阴"
                },
                "yang_deficiency": {
                    "name": "阳虚证",
                    "symptoms": ["畏寒", "四肢冰冷", "精神萎靡", "腰膝酸软", "脉沉迟"],
                    "tongue": ["舌淡", "苔白"],
                    "treatment_principle": "温阳"
                }
            },
            
            # 方剂配伍
            "formula_patterns": {
                "four_gentlemen": {
                    "name": "四君子汤",
                    "composition": ["人参", "白术", "茯苓", "甘草"],
                    "functions": ["益气健脾"],
                    "indications": ["脾胃气虚证"]
                },
                "four_substances": {
                    "name": "四物汤",
                    "composition": ["当归", "川芎", "白芍", "熟地黄"],
                    "functions": ["补血调血"],
                    "indications": ["血虚证"]
                },
                "six_gentlemen": {
                    "name": "六君子汤",
                    "composition": ["人参", "白术", "茯苓", "甘草", "陈皮", "半夏"],
                    "functions": ["益气健脾", "燥湿化痰"],
                    "indications": ["脾胃气虚兼痰湿证"]
                }
            },
            
            # 体质类型
            "constitution_types": {
                "balanced": {
                    "name": "平和质",
                    "characteristics": ["体形匀称", "面色润泽", "精力充沛"],
                    "susceptible_diseases": [],
                    "health_guidance": ["维持现状", "适度运动", "规律作息"]
                },
                "qi_deficiency": {
                    "name": "气虚质",
                    "characteristics": ["容易疲劳", "气短懒言", "易出汗"],
                    "susceptible_diseases": ["感冒", "胃下垂", "子宫脱垂"],
                    "health_guidance": ["补气食物", "适量运动", "避免过劳"]
                },
                "yang_deficiency": {
                    "name": "阳虚质",
                    "characteristics": ["怕冷", "手脚冰凉", "精神不振"],
                    "susceptible_diseases": ["腹泻", "阳痿", "水肿"],
                    "health_guidance": ["温阳食物", "避免寒凉", "适当运动"]
                }
            }
        }
    
    async def initialize(self):
        """初始化推理引擎"""
        logger.info("Initializing knowledge reasoning engine")
        
        # 构建知识图谱
        await self._build_knowledge_graph()
        
        # 加载推理规则
        await self._load_reasoning_rules()
        
        logger.info("Knowledge reasoning engine initialized successfully")
    
    async def _build_knowledge_graph(self):
        """构建知识图谱"""
        # 添加脏腑节点
        for organ_id, organ_info in self.tcm_knowledge["organs"].items():
            self.knowledge_graph.add_node(
                organ_id,
                type="organ",
                name=organ_info["name"],
                functions=organ_info["functions"],
                emotions=organ_info["emotions"]
            )
        
        # 添加病理因素节点
        for factor_id, factor_info in self.tcm_knowledge["pathogenic_factors"].items():
            self.knowledge_graph.add_node(
                factor_id,
                type="pathogenic_factor",
                name=factor_info["name"],
                nature=factor_info["nature"],
                characteristics=factor_info["characteristics"]
            )
        
        # 添加证型节点
        for syndrome_id, syndrome_info in self.tcm_knowledge["syndrome_patterns"].items():
            self.knowledge_graph.add_node(
                syndrome_id,
                type="syndrome",
                name=syndrome_info["name"],
                symptoms=syndrome_info["symptoms"],
                treatment_principle=syndrome_info["treatment_principle"]
            )
        
        # 添加方剂节点
        for formula_id, formula_info in self.tcm_knowledge["formula_patterns"].items():
            self.knowledge_graph.add_node(
                formula_id,
                type="formula",
                name=formula_info["name"],
                composition=formula_info["composition"],
                functions=formula_info["functions"]
            )
        
        # 添加体质节点
        for constitution_id, constitution_info in self.tcm_knowledge["constitution_types"].items():
            self.knowledge_graph.add_node(
                constitution_id,
                type="constitution",
                name=constitution_info["name"],
                characteristics=constitution_info["characteristics"],
                susceptible_diseases=constitution_info["susceptible_diseases"]
            )
        
        # 添加关系
        await self._add_knowledge_relationships()
    
    async def _add_knowledge_relationships(self):
        """添加知识关系"""
        # 脏腑相关关系
        organ_relations = [
            ("heart", "kidney", "heart_kidney_interaction", {"type": "mutual_support"}),
            ("liver", "spleen", "liver_spleen_interaction", {"type": "mutual_restraint"}),
            ("lung", "kidney", "lung_kidney_interaction", {"type": "mutual_support"}),
            ("spleen", "lung", "spleen_lung_interaction", {"type": "mother_child"}),
            ("liver", "heart", "liver_heart_interaction", {"type": "mother_child"})
        ]
        
        for source, target, relation_type, properties in organ_relations:
            self.knowledge_graph.add_edge(source, target, type=relation_type, **properties)
        
        # 证型与治疗原则关系
        syndrome_treatment_relations = [
            ("qi_deficiency", "tonify_qi", "treatment", {"method": "补气"}),
            ("blood_deficiency", "tonify_blood", "treatment", {"method": "补血"}),
            ("yin_deficiency", "nourish_yin", "treatment", {"method": "滋阴"}),
            ("yang_deficiency", "warm_yang", "treatment", {"method": "温阳"})
        ]
        
        for syndrome, treatment, relation_type, properties in syndrome_treatment_relations:
            if not self.knowledge_graph.has_node(treatment):
                self.knowledge_graph.add_node(treatment, type="treatment_principle")
            self.knowledge_graph.add_edge(syndrome, treatment, type=relation_type, **properties)
        
        # 方剂与证型关系
        formula_syndrome_relations = [
            ("four_gentlemen", "qi_deficiency", "treats", {"efficacy": 0.9}),
            ("four_substances", "blood_deficiency", "treats", {"efficacy": 0.9}),
            ("six_gentlemen", "qi_deficiency", "treats", {"efficacy": 0.8})
        ]
        
        for formula, syndrome, relation_type, properties in formula_syndrome_relations:
            self.knowledge_graph.add_edge(formula, syndrome, type=relation_type, **properties)
    
    async def _load_reasoning_rules(self):
        """加载推理规则"""
        # 辨证论治规则
        syndrome_rules = [
            ReasoningRule(
                id="qi_deficiency_rule",
                name="气虚证辨证规则",
                description="基于症状识别气虚证",
                reasoning_type=ReasoningType.SYNDROME_DIFFERENTIATION,
                conditions=[
                    {"type": "symptom", "name": "乏力", "operator": "present"},
                    {"type": "symptom", "name": "气短", "operator": "present"},
                    {"type": "pulse", "name": "脉虚", "operator": "present"}
                ],
                conclusions=[
                    {"syndrome": "气虚证", "confidence": 0.8}
                ],
                confidence_weight=0.9
            ),
            ReasoningRule(
                id="blood_deficiency_rule",
                name="血虚证辨证规则",
                description="基于症状识别血虚证",
                reasoning_type=ReasoningType.SYNDROME_DIFFERENTIATION,
                conditions=[
                    {"type": "symptom", "name": "面色苍白", "operator": "present"},
                    {"type": "symptom", "name": "头晕", "operator": "present"},
                    {"type": "pulse", "name": "脉细", "operator": "present"}
                ],
                conclusions=[
                    {"syndrome": "血虚证", "confidence": 0.8}
                ],
                confidence_weight=0.9
            ),
            ReasoningRule(
                id="yin_deficiency_rule",
                name="阴虚证辨证规则",
                description="基于症状识别阴虚证",
                reasoning_type=ReasoningType.SYNDROME_DIFFERENTIATION,
                conditions=[
                    {"type": "symptom", "name": "五心烦热", "operator": "present"},
                    {"type": "symptom", "name": "盗汗", "operator": "present"},
                    {"type": "pulse", "name": "脉细数", "operator": "present"}
                ],
                conclusions=[
                    {"syndrome": "阴虚证", "confidence": 0.8}
                ],
                confidence_weight=0.9
            )
        ]
        
        # 方剂配伍规则
        formula_rules = [
            ReasoningRule(
                id="four_gentlemen_rule",
                name="四君子汤配伍规则",
                description="气虚证选用四君子汤",
                reasoning_type=ReasoningType.FORMULA_COMPOSITION,
                conditions=[
                    {"type": "syndrome", "name": "气虚证", "operator": "diagnosed"}
                ],
                conclusions=[
                    {"formula": "四君子汤", "confidence": 0.9}
                ],
                confidence_weight=0.9
            ),
            ReasoningRule(
                id="four_substances_rule",
                name="四物汤配伍规则",
                description="血虚证选用四物汤",
                reasoning_type=ReasoningType.FORMULA_COMPOSITION,
                conditions=[
                    {"type": "syndrome", "name": "血虚证", "operator": "diagnosed"}
                ],
                conclusions=[
                    {"formula": "四物汤", "confidence": 0.9}
                ],
                confidence_weight=0.9
            )
        ]
        
        # 体质分析规则
        constitution_rules = [
            ReasoningRule(
                id="qi_deficiency_constitution_rule",
                name="气虚质体质分析规则",
                description="基于症状和体征识别气虚质",
                reasoning_type=ReasoningType.CONSTITUTION_ANALYSIS,
                conditions=[
                    {"type": "symptom", "name": "容易疲劳", "operator": "present"},
                    {"type": "symptom", "name": "气短懒言", "operator": "present"},
                    {"type": "symptom", "name": "易出汗", "operator": "present"}
                ],
                conclusions=[
                    {"constitution": "气虚质", "confidence": 0.8}
                ],
                confidence_weight=0.8
            )
        ]
        
        # 添加所有规则
        all_rules = syndrome_rules + formula_rules + constitution_rules
        for rule in all_rules:
            self.reasoning_rules[rule.id] = rule
    
    async def perform_reasoning(
        self,
        evidence_list: List[Evidence],
        reasoning_type: Optional[ReasoningType] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ReasoningResult]:
        """
        执行推理
        
        Args:
            evidence_list: 证据列表
            reasoning_type: 推理类型（可选，如果不指定则尝试所有类型）
            context: 上下文信息
            
        Returns:
            推理结果列表
        """
        logger.info(f"Performing reasoning with {len(evidence_list)} evidence items")
        
        # 生成缓存键
        cache_key = self._generate_cache_key(evidence_list, reasoning_type, context)
        
        # 检查缓存
        if cache_key in self.reasoning_cache:
            self.stats["cache_hits"] += 1
            return [self.reasoning_cache[cache_key]]
        
        self.stats["cache_misses"] += 1
        
        # 执行推理
        results = []
        
        if reasoning_type:
            # 执行特定类型的推理
            result = await self._perform_specific_reasoning(evidence_list, reasoning_type, context)
            if result:
                results.append(result)
        else:
            # 执行所有类型的推理
            for rt in ReasoningType:
                result = await self._perform_specific_reasoning(evidence_list, rt, context)
                if result:
                    results.append(result)
        
        # 更新统计信息
        self.stats["total_reasonings"] += len(results)
        for result in results:
            self.stats["reasonings_by_type"][result.reasoning_type.value] += 1
        
        # 缓存结果
        if results:
            self.reasoning_cache[cache_key] = results[0]
            self.reasoning_history.extend(results)
        
        logger.info(f"Reasoning completed with {len(results)} results")
        return results
    
    async def _perform_specific_reasoning(
        self,
        evidence_list: List[Evidence],
        reasoning_type: ReasoningType,
        context: Optional[Dict[str, Any]]
    ) -> Optional[ReasoningResult]:
        """执行特定类型的推理"""
        # 获取适用的规则
        applicable_rules = [
            rule for rule in self.reasoning_rules.values()
            if rule.enabled and rule.reasoning_type == reasoning_type
        ]
        
        if not applicable_rules:
            return None
        
        # 评估规则
        rule_results = []
        for rule in applicable_rules:
            result = await self._evaluate_rule(rule, evidence_list, context)
            if result:
                rule_results.append(result)
        
        if not rule_results:
            return None
        
        # 合并结果
        return await self._merge_rule_results(rule_results, reasoning_type, evidence_list)
    
    async def _evaluate_rule(
        self,
        rule: ReasoningRule,
        evidence_list: List[Evidence],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """评估单个规则"""
        # 检查条件
        satisfied_conditions = 0
        total_conditions = len(rule.conditions)
        
        for condition in rule.conditions:
            if await self._check_condition(condition, evidence_list, context):
                satisfied_conditions += 1
        
        # 计算满足度
        satisfaction_rate = satisfied_conditions / total_conditions if total_conditions > 0 else 0
        
        # 如果满足度达到阈值，返回结果
        if satisfaction_rate >= 0.6:  # 可配置的阈值
            confidence = satisfaction_rate * rule.confidence_weight
            return {
                "rule": rule,
                "satisfaction_rate": satisfaction_rate,
                "confidence": confidence,
                "conclusions": rule.conclusions
            }
        
        return None
    
    async def _check_condition(
        self,
        condition: Dict[str, Any],
        evidence_list: List[Evidence],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """检查条件是否满足"""
        condition_type = condition.get("type")
        condition_name = condition.get("name")
        operator = condition.get("operator", "present")
        
        # 查找匹配的证据
        matching_evidence = [
            e for e in evidence_list
            if e.type.value == condition_type and condition_name in e.name
        ]
        
        if operator == "present":
            return len(matching_evidence) > 0
        elif operator == "absent":
            return len(matching_evidence) == 0
        elif operator == "value_gt":
            threshold = condition.get("threshold", 0)
            return any(
                isinstance(e.value, (int, float)) and e.value > threshold
                for e in matching_evidence
            )
        elif operator == "value_lt":
            threshold = condition.get("threshold", 0)
            return any(
                isinstance(e.value, (int, float)) and e.value < threshold
                for e in matching_evidence
            )
        elif operator == "diagnosed":
            # 检查是否已经诊断出某个证型
            if context and "diagnosed_syndromes" in context:
                return condition_name in context["diagnosed_syndromes"]
        
        return False
    
    async def _merge_rule_results(
        self,
        rule_results: List[Dict[str, Any]],
        reasoning_type: ReasoningType,
        evidence_list: List[Evidence]
    ) -> ReasoningResult:
        """合并规则结果"""
        # 按置信度排序
        rule_results.sort(key=lambda x: x["confidence"], reverse=True)
        
        # 选择最佳结果
        best_result = rule_results[0]
        
        # 构建推理链
        reasoning_chain = []
        rules_applied = []
        
        for result in rule_results:
            rule = result["rule"]
            rules_applied.append(rule.id)
            reasoning_chain.append(f"应用规则: {rule.name} (置信度: {result['confidence']:.2f})")
        
        # 提取结论
        conclusions = best_result["conclusions"]
        main_conclusion = ""
        recommendations = []
        
        if conclusions:
            if reasoning_type == ReasoningType.SYNDROME_DIFFERENTIATION:
                main_conclusion = f"诊断为: {conclusions[0].get('syndrome', '未知证型')}"
                recommendations = self._get_syndrome_recommendations(conclusions[0].get('syndrome'))
            elif reasoning_type == ReasoningType.FORMULA_COMPOSITION:
                main_conclusion = f"推荐方剂: {conclusions[0].get('formula', '未知方剂')}"
                recommendations = self._get_formula_recommendations(conclusions[0].get('formula'))
            elif reasoning_type == ReasoningType.CONSTITUTION_ANALYSIS:
                main_conclusion = f"体质类型: {conclusions[0].get('constitution', '未知体质')}"
                recommendations = self._get_constitution_recommendations(conclusions[0].get('constitution'))
        
        # 计算置信度级别
        confidence = best_result["confidence"]
        confidence_level = self._get_confidence_level(confidence)
        
        # 生成替代方案
        alternatives = []
        for i, result in enumerate(rule_results[1:3]):  # 最多3个替代方案
            alt_conclusions = result["conclusions"]
            if alt_conclusions:
                alternatives.append({
                    "rank": i + 2,
                    "conclusion": alt_conclusions[0],
                    "confidence": result["confidence"],
                    "rule": result["rule"].name
                })
        
        return ReasoningResult(
            id=str(uuid.uuid4()),
            reasoning_type=reasoning_type,
            conclusion=main_conclusion,
            confidence=confidence,
            confidence_level=confidence_level,
            evidence_used=evidence_list,
            rules_applied=rules_applied,
            reasoning_chain=reasoning_chain,
            recommendations=recommendations,
            alternatives=alternatives
        )
    
    def _get_syndrome_recommendations(self, syndrome: str) -> List[str]:
        """获取证型相关建议"""
        syndrome_recommendations = {
            "气虚证": [
                "建议补气治疗，可选用四君子汤",
                "注意休息，避免过度劳累",
                "饮食宜清淡，多食补气食物如山药、大枣",
                "适当运动，如太极拳、八段锦"
            ],
            "血虚证": [
                "建议补血治疗，可选用四物汤",
                "多食补血食物如红枣、桂圆、阿胶",
                "保证充足睡眠",
                "避免过度用眼和思虑"
            ],
            "阴虚证": [
                "建议滋阴治疗，可选用六味地黄丸",
                "多食滋阴食物如银耳、百合、枸杞",
                "避免熬夜，保持心情平静",
                "减少辛辣刺激性食物"
            ],
            "阳虚证": [
                "建议温阳治疗，可选用金匮肾气丸",
                "多食温阳食物如羊肉、韭菜、生姜",
                "注意保暖，避免寒凉",
                "适当运动以助阳气"
            ]
        }
        
        return syndrome_recommendations.get(syndrome, ["请咨询专业中医师"])
    
    def _get_formula_recommendations(self, formula: str) -> List[str]:
        """获取方剂相关建议"""
        formula_recommendations = {
            "四君子汤": [
                "适用于脾胃气虚证",
                "服用时间：饭前30分钟温服",
                "注意事项：忌食生冷油腻",
                "疗程：一般2-4周"
            ],
            "四物汤": [
                "适用于血虚证",
                "服用时间：饭后1小时温服",
                "注意事项：月经期间停服",
                "疗程：一般4-6周"
            ],
            "六君子汤": [
                "适用于脾胃气虚兼痰湿证",
                "服用时间：饭前30分钟温服",
                "注意事项：忌食甜腻食物",
                "疗程：一般3-6周"
            ]
        }
        
        return formula_recommendations.get(formula, ["请遵医嘱服用"])
    
    def _get_constitution_recommendations(self, constitution: str) -> List[str]:
        """获取体质相关建议"""
        constitution_recommendations = {
            "气虚质": [
                "饮食调养：多食补气食物，如人参、黄芪、山药",
                "运动调养：适宜柔和运动，如散步、太极拳",
                "起居调养：规律作息，避免过度劳累",
                "情志调养：保持乐观情绪，避免过度思虑"
            ],
            "阳虚质": [
                "饮食调养：多食温热食物，如羊肉、生姜、肉桂",
                "运动调养：适宜温和运动，避免大汗淋漓",
                "起居调养：注意保暖，避免寒凉环境",
                "情志调养：保持积极心态，避免恐惧情绪"
            ],
            "阴虚质": [
                "饮食调养：多食滋阴食物，如银耳、百合、枸杞",
                "运动调养：适宜静态运动，如瑜伽、冥想",
                "起居调养：避免熬夜，保持充足睡眠",
                "情志调养：保持心情平静，避免急躁"
            ]
        }
        
        return constitution_recommendations.get(constitution, ["请咨询专业中医师"])
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """获取置信度级别"""
        if confidence >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_cache_key(
        self,
        evidence_list: List[Evidence],
        reasoning_type: Optional[ReasoningType],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """生成缓存键"""
        # 创建证据的哈希
        evidence_str = "|".join([
            f"{e.type.value}:{e.name}:{e.value}:{e.confidence}"
            for e in sorted(evidence_list, key=lambda x: x.id)
        ])
        
        # 添加推理类型
        type_str = reasoning_type.value if reasoning_type else "all"
        
        # 添加上下文
        context_str = json.dumps(context, sort_keys=True) if context else ""
        
        # 生成哈希
        import hashlib
        combined_str = f"{evidence_str}|{type_str}|{context_str}"
        return hashlib.md5(combined_str.encode()).hexdigest()
    
    async def explain_reasoning(self, result: ReasoningResult) -> Dict[str, Any]:
        """解释推理过程"""
        explanation = {
            "reasoning_type": result.reasoning_type.value,
            "conclusion": result.conclusion,
            "confidence": result.confidence,
            "confidence_level": result.confidence_level.value,
            "evidence_analysis": [],
            "rule_analysis": [],
            "knowledge_graph_paths": [],
            "alternative_explanations": []
        }
        
        # 分析证据
        for evidence in result.evidence_used:
            explanation["evidence_analysis"].append({
                "type": evidence.type.value,
                "name": evidence.name,
                "value": evidence.value,
                "confidence": evidence.confidence,
                "relevance": self._calculate_evidence_relevance(evidence, result)
            })
        
        # 分析规则
        for rule_id in result.rules_applied:
            if rule_id in self.reasoning_rules:
                rule = self.reasoning_rules[rule_id]
                explanation["rule_analysis"].append({
                    "rule_name": rule.name,
                    "description": rule.description,
                    "confidence_weight": rule.confidence_weight,
                    "conditions": rule.conditions,
                    "conclusions": rule.conclusions
                })
        
        # 查找知识图谱路径
        explanation["knowledge_graph_paths"] = await self._find_knowledge_paths(result)
        
        # 分析替代解释
        for alt in result.alternatives:
            explanation["alternative_explanations"].append({
                "conclusion": alt["conclusion"],
                "confidence": alt["confidence"],
                "reason": f"基于规则: {alt['rule']}"
            })
        
        return explanation
    
    def _calculate_evidence_relevance(self, evidence: Evidence, result: ReasoningResult) -> float:
        """计算证据相关性"""
        # 简单的相关性计算，可以根据需要改进
        base_relevance = evidence.confidence
        
        # 根据证据类型调整相关性
        type_weights = {
            EvidenceType.SYMPTOM: 1.0,
            EvidenceType.SIGN: 0.9,
            EvidenceType.TONGUE: 0.8,
            EvidenceType.PULSE: 0.8,
            EvidenceType.CONSTITUTION: 0.7,
            EvidenceType.LIFESTYLE: 0.6,
            EvidenceType.ENVIRONMENT: 0.5,
            EvidenceType.MEDICAL_HISTORY: 0.8,
            EvidenceType.LAB_RESULT: 0.9
        }
        
        weight = type_weights.get(evidence.type, 0.5)
        return base_relevance * weight
    
    async def _find_knowledge_paths(self, result: ReasoningResult) -> List[Dict[str, Any]]:
        """查找知识图谱路径"""
        paths = []
        
        # 根据推理类型查找相关路径
        if result.reasoning_type == ReasoningType.SYNDROME_DIFFERENTIATION:
            # 查找症状到证型的路径
            for evidence in result.evidence_used:
                if evidence.type == EvidenceType.SYMPTOM:
                    # 在知识图谱中查找相关路径
                    # 这里简化处理，实际应该使用图算法
                    paths.append({
                        "source": evidence.name,
                        "target": result.conclusion,
                        "path_length": 2,
                        "confidence": evidence.confidence
                    })
        
        return paths
    
    async def get_reasoning_statistics(self) -> Dict[str, Any]:
        """获取推理统计信息"""
        # 计算平均置信度
        if self.reasoning_history:
            total_confidence = sum(r.confidence for r in self.reasoning_history)
            self.stats["average_confidence"] = total_confidence / len(self.reasoning_history)
        
        return {
            "total_reasonings": self.stats["total_reasonings"],
            "reasonings_by_type": dict(self.stats["reasonings_by_type"]),
            "average_confidence": self.stats["average_confidence"],
            "cache_hit_rate": self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0,
            "knowledge_graph_nodes": self.knowledge_graph.number_of_nodes(),
            "knowledge_graph_edges": self.knowledge_graph.number_of_edges(),
            "reasoning_rules": len(self.reasoning_rules),
            "reasoning_history_size": len(self.reasoning_history)
        }
    
    async def add_reasoning_rule(self, rule: ReasoningRule) -> bool:
        """添加推理规则"""
        try:
            self.reasoning_rules[rule.id] = rule
            logger.info(f"Added reasoning rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding reasoning rule: {e}")
            return False
    
    async def remove_reasoning_rule(self, rule_id: str) -> bool:
        """移除推理规则"""
        try:
            if rule_id in self.reasoning_rules:
                del self.reasoning_rules[rule_id]
                logger.info(f"Removed reasoning rule: {rule_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing reasoning rule: {e}")
            return False
    
    async def update_knowledge_graph(
        self,
        nodes: List[KnowledgeNode],
        relations: List[KnowledgeRelation]
    ) -> bool:
        """更新知识图谱"""
        try:
            # 添加节点
            for node in nodes:
                self.knowledge_graph.add_node(
                    node.id,
                    type=node.type,
                    name=node.name,
                    **node.properties
                )
            
            # 添加关系
            for relation in relations:
                self.knowledge_graph.add_edge(
                    relation.source_id,
                    relation.target_id,
                    type=relation.relation_type,
                    weight=relation.weight,
                    **relation.properties
                )
            
            logger.info(f"Updated knowledge graph with {len(nodes)} nodes and {len(relations)} relations")
            return True
            
        except Exception as e:
            logger.error(f"Error updating knowledge graph: {e}")
            return False
    
    async def query_knowledge_graph(
        self,
        query_type: str,
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """查询知识图谱"""
        results = []
        
        try:
            if query_type == "find_related_nodes":
                node_id = parameters.get("node_id")
                relation_type = parameters.get("relation_type")
                
                if node_id in self.knowledge_graph:
                    for neighbor in self.knowledge_graph.neighbors(node_id):
                        edge_data = self.knowledge_graph.get_edge_data(node_id, neighbor)
                        if not relation_type or any(
                            data.get("type") == relation_type
                            for data in edge_data.values()
                        ):
                            results.append({
                                "node_id": neighbor,
                                "node_data": self.knowledge_graph.nodes[neighbor],
                                "edge_data": edge_data
                            })
            
            elif query_type == "find_shortest_path":
                source = parameters.get("source")
                target = parameters.get("target")
                
                if source in self.knowledge_graph and target in self.knowledge_graph:
                    try:
                        path = nx.shortest_path(self.knowledge_graph, source, target)
                        results.append({
                            "path": path,
                            "length": len(path) - 1
                        })
                    except nx.NetworkXNoPath:
                        results.append({"path": None, "length": -1})
            
            elif query_type == "find_nodes_by_type":
                node_type = parameters.get("node_type")
                
                for node_id, node_data in self.knowledge_graph.nodes(data=True):
                    if node_data.get("type") == node_type:
                        results.append({
                            "node_id": node_id,
                            "node_data": node_data
                        })
        
        except Exception as e:
            logger.error(f"Error querying knowledge graph: {e}")
        
        return results
    
    async def clear_reasoning_cache(self):
        """清理推理缓存"""
        self.reasoning_cache.clear()
        logger.info("Reasoning cache cleared")
    
    async def export_reasoning_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        reasoning_type: Optional[ReasoningType] = None
    ) -> List[Dict[str, Any]]:
        """导出推理历史"""
        filtered_history = self.reasoning_history
        
        # 应用时间过滤
        if start_time:
            filtered_history = [r for r in filtered_history if r.timestamp >= start_time]
        
        if end_time:
            filtered_history = [r for r in filtered_history if r.timestamp <= end_time]
        
        # 应用类型过滤
        if reasoning_type:
            filtered_history = [r for r in filtered_history if r.reasoning_type == reasoning_type]
        
        # 转换为字典格式
        export_data = []
        for result in filtered_history:
            export_data.append({
                "id": result.id,
                "reasoning_type": result.reasoning_type.value,
                "conclusion": result.conclusion,
                "confidence": result.confidence,
                "confidence_level": result.confidence_level.value,
                "evidence_count": len(result.evidence_used),
                "rules_applied": result.rules_applied,
                "reasoning_chain": result.reasoning_chain,
                "recommendations": result.recommendations,
                "alternatives_count": len(result.alternatives),
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata
            })
        
        return export_data
    
    async def auto_learn_rules(self):
        """从推理历史自动挖掘新规则"""
        # 简化示例：统计高频证据-结论对，自动生成规则
        evidence_conclusion_count = {}
        for result in self.reasoning_history:
            key = tuple(sorted([(e.type.value, e.name) for e in result.evidence_used])) + (result.conclusion,)
            evidence_conclusion_count[key] = evidence_conclusion_count.get(key, 0) + 1
        for key, count in evidence_conclusion_count.items():
            if count > 3:  # 阈值可配置
                # 自动生成规则
                evidence_list = [{'type': t, 'name': n} for t, n in key[:-1]]
                conclusion = key[-1]
                rule = ReasoningRule(
                    id=str(uuid.uuid4()),
                    name=f"AutoLearned-{conclusion}",
                    description="自动学习生成",
                    reasoning_type=ReasoningType.SYNDROME_DIFFERENTIATION,
                    conditions=evidence_list,
                    conclusions=[{'conclusion': conclusion}],
                    confidence_weight=0.8,
                    priority=2,
                    enabled=True
                )
                self.reasoning_rules[rule.id] = rule
        logger.info("推理规则自动学习完成")

    async def auto_evolve_knowledge(self):
        """根据推理结果自动补全知识图谱"""
        # 简化示例：将高置信度结论补全到知识图谱
        for result in self.reasoning_history:
            if result.confidence > 0.85:
                # 假设conclusion为节点名
                if not self.knowledge_graph.has_node(result.conclusion):
                    self.knowledge_graph.add_node(result.conclusion, type='auto_evolved')
        logger.info("知识图谱自进化完成") 