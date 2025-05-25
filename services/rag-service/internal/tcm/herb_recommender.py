#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中药推荐器 - 智能中药推荐系统
支持方剂推荐、单味药推荐、安全性检查和个性化调整
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from loguru import logger

from .tcm_models import (
    ConstitutionType, SyndromeType, TreatmentPrinciple,
    HerbalFormula, SingleHerb, PatientProfile
)
from ..observability.metrics import MetricsCollector


class RecommendationType(str, Enum):
    """推荐类型"""
    FORMULA = "formula"              # 方剂推荐
    SINGLE_HERB = "single_herb"      # 单味药推荐
    COMBINATION = "combination"      # 组合推荐
    MODIFICATION = "modification"    # 加减推荐


class SafetyLevel(str, Enum):
    """安全等级"""
    SAFE = "safe"                    # 安全
    CAUTION = "caution"              # 谨慎使用
    WARNING = "warning"              # 警告
    CONTRAINDICATED = "contraindicated"  # 禁忌


@dataclass
class HerbData:
    """中药数据"""
    name: str
    pinyin: str
    latin_name: str
    category: str                    # 功效分类
    nature: str                      # 性味
    meridians: List[str]             # 归经
    functions: List[str]             # 功效
    indications: List[str]           # 主治
    dosage_range: Tuple[float, float]  # 用量范围(g)
    contraindications: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    drug_interactions: List[str] = field(default_factory=list)
    special_populations: Dict[str, str] = field(default_factory=dict)  # 特殊人群用药


@dataclass
class FormulaData:
    """方剂数据"""
    name: str
    source: str                      # 出处
    composition: Dict[str, float]    # 组成及用量
    functions: List[str]             # 功效
    indications: List[str]           # 主治
    syndrome_types: List[SyndromeType]  # 适用证型
    constitution_types: List[ConstitutionType]  # 适用体质
    modifications: Dict[str, Dict[str, float]] = field(default_factory=dict)  # 加减变化
    preparation_method: str = ""     # 制备方法
    administration: str = ""         # 服用方法
    contraindications: List[str] = field(default_factory=list)
    precautions: List[str] = field(default_factory=list)


@dataclass
class RecommendationResult:
    """推荐结果"""
    recommendation_type: RecommendationType
    primary_recommendation: Dict[str, Any]
    alternative_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    safety_assessment: Dict[str, Any] = field(default_factory=dict)
    dosage_guidance: Dict[str, str] = field(default_factory=dict)
    preparation_instructions: str = ""
    administration_guidance: str = ""
    precautions: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    monitoring_suggestions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    reasoning: str = ""


class HerbDatabase:
    """中药数据库"""
    
    def __init__(self):
        self.herbs = self._load_herb_data()
        self.formulas = self._load_formula_data()
        self.compatibility_rules = self._load_compatibility_rules()
        self.safety_database = self._load_safety_database()
    
    def _load_herb_data(self) -> Dict[str, HerbData]:
        """加载单味药数据"""
        # 这里应该从实际数据库或文件加载
        # 暂时返回一些示例数据
        herbs = {}
        
        # 示例：人参
        herbs["人参"] = HerbData(
            name="人参",
            pinyin="renshen",
            latin_name="Panax ginseng",
            category="补气药",
            nature="甘、微苦，微温",
            meridians=["脾", "肺", "心", "肾"],
            functions=["大补元气", "复脉固脱", "补脾益肺", "生津养血", "安神益智"],
            indications=["气虚欲脱", "脾肺气虚", "热病气虚津伤", "心神不安", "失眠多梦"],
            dosage_range=(3.0, 9.0),
            contraindications=["实热证", "湿热证"],
            side_effects=["过量可致兴奋、失眠、血压升高"],
            special_populations={
                "孕妇": "慎用",
                "儿童": "减量使用",
                "高血压患者": "谨慎使用"
            }
        )
        
        # 示例：黄芪
        herbs["黄芪"] = HerbData(
            name="黄芪",
            pinyin="huangqi",
            latin_name="Astragalus membranaceus",
            category="补气药",
            nature="甘，微温",
            meridians=["脾", "肺"],
            functions=["补气升阳", "固表止汗", "利水消肿", "生津养血", "行滞通痹"],
            indications=["气虚乏力", "中气下陷", "表虚自汗", "水肿", "血虚萎黄"],
            dosage_range=(9.0, 30.0),
            contraindications=["表实邪盛", "气滞湿阻", "热毒炽盛"],
            side_effects=["过量可致胸闷、腹胀"],
            special_populations={
                "孕妇": "可用",
                "儿童": "可用",
                "感冒发热": "禁用"
            }
        )
        
        # 可以继续添加更多中药数据...
        
        return herbs
    
    def _load_formula_data(self) -> Dict[str, FormulaData]:
        """加载方剂数据"""
        formulas = {}
        
        # 示例：四君子汤
        formulas["四君子汤"] = FormulaData(
            name="四君子汤",
            source="《太平惠民和剂局方》",
            composition={
                "人参": 9.0,
                "白术": 9.0,
                "茯苓": 9.0,
                "甘草": 6.0
            },
            functions=["益气健脾"],
            indications=["脾胃气虚", "面色萎白", "语声低微", "气短乏力", "食少便溏"],
            syndrome_types=[SyndromeType.SPLEEN_QI_DEFICIENCY],
            constitution_types=[ConstitutionType.QI_DEFICIENCY],
            modifications={
                "食欲不振": {"陈皮": 6.0, "砂仁": 3.0},
                "腹胀": {"木香": 6.0, "枳壳": 6.0},
                "便溏": {"山药": 15.0, "扁豆": 12.0}
            },
            preparation_method="水煎服",
            administration="每日1剂，分2次温服",
            contraindications=["实热证", "湿热证"],
            precautions=["服药期间忌食生冷、油腻食物"]
        )
        
        # 示例：六味地黄丸
        formulas["六味地黄丸"] = FormulaData(
            name="六味地黄丸",
            source="《小儿药证直诀》",
            composition={
                "熟地黄": 24.0,
                "山茱萸": 12.0,
                "山药": 12.0,
                "泽泻": 9.0,
                "茯苓": 9.0,
                "牡丹皮": 9.0
            },
            functions=["滋阴补肾"],
            indications=["肾阴虚", "腰膝酸软", "头晕耳鸣", "盗汗", "遗精", "消渴"],
            syndrome_types=[SyndromeType.KIDNEY_YIN_DEFICIENCY],
            constitution_types=[ConstitutionType.YIN_DEFICIENCY],
            modifications={
                "潮热盗汗": {"知母": 9.0, "黄柏": 6.0},
                "腰痛": {"杜仲": 12.0, "续断": 9.0},
                "耳鸣": {"磁石": 15.0, "石菖蒲": 6.0}
            },
            preparation_method="蜜丸或水煎服",
            administration="每日2次，每次6-9g",
            contraindications=["脾胃虚弱", "痰湿内盛"],
            precautions=["服药期间避免辛辣刺激食物"]
        )
        
        return formulas
    
    def _load_compatibility_rules(self) -> Dict[str, List[str]]:
        """加载配伍规律"""
        return {
            "十八反": [
                "甘草-甘遂", "甘草-大戟", "甘草-海藻", "甘草-芫花",
                "乌头-贝母", "乌头-瓜蒌", "乌头-半夏", "乌头-白蔹", "乌头-白及",
                "藜芦-人参", "藜芦-沙参", "藜芦-丹参", "藜芦-玄参", "藜芦-细辛", "藜芦-芍药"
            ],
            "十九畏": [
                "硫黄-朴硝", "水银-砒霜", "狼毒-密陀僧", "巴豆-牵牛",
                "丁香-郁金", "川乌-犀角", "牙硝-三棱", "官桂-石脂", "人参-五灵脂"
            ],
            "妊娠禁用": [
                "巴豆", "牵牛子", "大戟", "芫花", "甘遂", "商陆", "斑蝥", "蜈蚣",
                "水蛭", "虻虫", "干漆", "麝香", "三棱", "莪术", "水银", "砒石"
            ],
            "妊娠慎用": [
                "桃仁", "红花", "大黄", "枳实", "附子", "干姜", "肉桂"
            ]
        }
    
    def _load_safety_database(self) -> Dict[str, Dict[str, Any]]:
        """加载安全性数据库"""
        return {
            "特殊人群": {
                "孕妇": {
                    "禁用": ["巴豆", "牵牛子", "大戟", "芫花", "甘遂"],
                    "慎用": ["桃仁", "红花", "大黄", "枳实", "附子"],
                    "可用": ["人参", "黄芪", "当归", "白术", "茯苓"]
                },
                "儿童": {
                    "禁用": ["朱砂", "雄黄", "轻粉", "密陀僧"],
                    "慎用": ["大黄", "芒硝", "附子", "细辛"],
                    "减量": ["人参", "鹿茸", "冬虫夏草"]
                },
                "老年人": {
                    "慎用": ["大黄", "芒硝", "甘遂", "大戟"],
                    "减量": ["附子", "干姜", "肉桂"],
                    "适宜": ["人参", "黄芪", "山药", "茯苓"]
                }
            },
            "疾病禁忌": {
                "高血压": ["麻黄", "细辛", "人参"],
                "心脏病": ["麻黄", "附子", "干姜"],
                "肝病": ["何首乌", "大黄", "黄药子"],
                "肾病": ["马兜铃", "天仙藤", "青木香"],
                "糖尿病": ["甘草", "大枣", "蜂蜜"]
            }
        }


class SyndromeFormulaMapper:
    """证型-方剂映射器"""
    
    def __init__(self, formula_database: Dict[str, FormulaData]):
        self.formula_database = formula_database
        self.syndrome_formula_map = self._build_syndrome_formula_map()
    
    def _build_syndrome_formula_map(self) -> Dict[SyndromeType, List[str]]:
        """构建证型-方剂映射"""
        mapping = {}
        
        for formula_name, formula_data in self.formula_database.items():
            for syndrome_type in formula_data.syndrome_types:
                if syndrome_type not in mapping:
                    mapping[syndrome_type] = []
                mapping[syndrome_type].append(formula_name)
        
        return mapping
    
    def get_formulas_for_syndrome(self, syndrome_type: SyndromeType) -> List[str]:
        """获取证型对应的方剂"""
        return self.syndrome_formula_map.get(syndrome_type, [])


class CompatibilityChecker:
    """配伍检查器"""
    
    def __init__(self, compatibility_rules: Dict[str, List[str]]):
        self.compatibility_rules = compatibility_rules
    
    def check_compatibility(self, herbs: List[str]) -> Tuple[bool, List[str]]:
        """
        检查配伍禁忌
        
        Args:
            herbs: 中药列表
            
        Returns:
            (是否安全, 警告列表)
        """
        warnings = []
        is_safe = True
        
        # 检查十八反
        for rule in self.compatibility_rules.get("十八反", []):
            herb1, herb2 = rule.split("-")
            if herb1 in herbs and herb2 in herbs:
                warnings.append(f"十八反：{herb1}与{herb2}相反，禁止同用")
                is_safe = False
        
        # 检查十九畏
        for rule in self.compatibility_rules.get("十九畏", []):
            herb1, herb2 = rule.split("-")
            if herb1 in herbs and herb2 in herbs:
                warnings.append(f"十九畏：{herb1}与{herb2}相畏，慎重同用")
        
        return is_safe, warnings


class SafetyChecker:
    """安全性检查器"""
    
    def __init__(self, safety_database: Dict[str, Dict[str, Any]]):
        self.safety_database = safety_database
    
    def check_patient_safety(
        self,
        herbs: List[str],
        patient_profile: PatientProfile
    ) -> Tuple[SafetyLevel, List[str]]:
        """
        检查患者用药安全性
        
        Args:
            herbs: 中药列表
            patient_profile: 患者档案
            
        Returns:
            (安全等级, 警告列表)
        """
        warnings = []
        safety_level = SafetyLevel.SAFE
        
        # 检查特殊人群用药
        if patient_profile.is_pregnant:
            contraindicated = self.safety_database["特殊人群"]["孕妇"]["禁用"]
            cautioned = self.safety_database["特殊人群"]["孕妇"]["慎用"]
            
            for herb in herbs:
                if herb in contraindicated:
                    warnings.append(f"孕妇禁用：{herb}")
                    safety_level = SafetyLevel.CONTRAINDICATED
                elif herb in cautioned:
                    warnings.append(f"孕妇慎用：{herb}")
                    if safety_level == SafetyLevel.SAFE:
                        safety_level = SafetyLevel.CAUTION
        
        # 检查儿童用药
        if patient_profile.age < 18:
            contraindicated = self.safety_database["特殊人群"]["儿童"]["禁用"]
            cautioned = self.safety_database["特殊人群"]["儿童"]["慎用"]
            
            for herb in herbs:
                if herb in contraindicated:
                    warnings.append(f"儿童禁用：{herb}")
                    safety_level = SafetyLevel.CONTRAINDICATED
                elif herb in cautioned:
                    warnings.append(f"儿童慎用：{herb}")
                    if safety_level == SafetyLevel.SAFE:
                        safety_level = SafetyLevel.CAUTION
        
        # 检查老年人用药
        if patient_profile.age >= 65:
            cautioned = self.safety_database["特殊人群"]["老年人"]["慎用"]
            
            for herb in herbs:
                if herb in cautioned:
                    warnings.append(f"老年人慎用：{herb}")
                    if safety_level == SafetyLevel.SAFE:
                        safety_level = SafetyLevel.CAUTION
        
        # 检查疾病禁忌
        for condition in patient_profile.medical_conditions:
            if condition in self.safety_database["疾病禁忌"]:
                contraindicated_herbs = self.safety_database["疾病禁忌"][condition]
                for herb in herbs:
                    if herb in contraindicated_herbs:
                        warnings.append(f"{condition}患者禁用：{herb}")
                        safety_level = SafetyLevel.CONTRAINDICATED
        
        return safety_level, warnings


class PersonalizationEngine:
    """个性化引擎"""
    
    def __init__(self, herb_database: HerbDatabase):
        self.herb_database = herb_database
    
    def personalize_recommendation(
        self,
        base_formula: FormulaData,
        patient_profile: PatientProfile,
        syndrome_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        个性化调整方剂
        
        Args:
            base_formula: 基础方剂
            patient_profile: 患者档案
            syndrome_analysis: 辨证分析结果
            
        Returns:
            调整后的方剂组成
        """
        personalized_composition = base_formula.composition.copy()
        
        # 根据体质调整
        constitution_adjustments = self._get_constitution_adjustments(
            patient_profile.constitution_type,
            base_formula
        )
        
        # 根据症状调整
        symptom_adjustments = self._get_symptom_adjustments(
            patient_profile.symptoms,
            base_formula
        )
        
        # 根据年龄调整
        age_adjustments = self._get_age_adjustments(
            patient_profile.age,
            base_formula
        )
        
        # 应用调整
        for herb, dosage in constitution_adjustments.items():
            if herb in personalized_composition:
                personalized_composition[herb] *= dosage
            else:
                personalized_composition[herb] = dosage
        
        for herb, dosage in symptom_adjustments.items():
            if herb in personalized_composition:
                personalized_composition[herb] += dosage
            else:
                personalized_composition[herb] = dosage
        
        for herb, factor in age_adjustments.items():
            if herb in personalized_composition:
                personalized_composition[herb] *= factor
        
        return personalized_composition
    
    def _get_constitution_adjustments(
        self,
        constitution_type: ConstitutionType,
        base_formula: FormulaData
    ) -> Dict[str, float]:
        """根据体质获取调整"""
        adjustments = {}
        
        if constitution_type == ConstitutionType.QI_DEFICIENCY:
            # 气虚体质加强补气药
            if "人参" in base_formula.composition:
                adjustments["人参"] = 1.2
            if "黄芪" in base_formula.composition:
                adjustments["黄芪"] = 1.3
        
        elif constitution_type == ConstitutionType.YIN_DEFICIENCY:
            # 阴虚体质加强滋阴药
            if "熟地黄" in base_formula.composition:
                adjustments["熟地黄"] = 1.2
            if "麦冬" in base_formula.composition:
                adjustments["麦冬"] = 1.1
        
        elif constitution_type == ConstitutionType.YANG_DEFICIENCY:
            # 阳虚体质加强温阳药
            if "附子" in base_formula.composition:
                adjustments["附子"] = 1.1
            if "肉桂" in base_formula.composition:
                adjustments["肉桂"] = 1.2
        
        return adjustments
    
    def _get_symptom_adjustments(
        self,
        symptoms: List[str],
        base_formula: FormulaData
    ) -> Dict[str, float]:
        """根据症状获取调整"""
        adjustments = {}
        
        if "失眠" in symptoms:
            adjustments["酸枣仁"] = 12.0
            adjustments["龙骨"] = 15.0
        
        if "头痛" in symptoms:
            adjustments["川芎"] = 6.0
            adjustments["白芷"] = 9.0
        
        if "便秘" in symptoms:
            adjustments["大黄"] = 6.0
            adjustments["芒硝"] = 3.0
        
        if "腹泻" in symptoms:
            adjustments["白术"] = 12.0
            adjustments["茯苓"] = 15.0
        
        return adjustments
    
    def _get_age_adjustments(
        self,
        age: int,
        base_formula: FormulaData
    ) -> Dict[str, float]:
        """根据年龄获取调整"""
        adjustments = {}
        
        if age < 18:
            # 儿童减量
            for herb in base_formula.composition:
                adjustments[herb] = 0.5
        
        elif age >= 65:
            # 老年人适当减量
            for herb in base_formula.composition:
                adjustments[herb] = 0.8
        
        return adjustments


class HerbRecommender:
    """中药推荐器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.herb_database = HerbDatabase()
        self.syndrome_mapper = SyndromeFormulaMapper(self.herb_database.formulas)
        self.compatibility_checker = CompatibilityChecker(self.herb_database.compatibility_rules)
        self.safety_checker = SafetyChecker(self.herb_database.safety_database)
        self.personalization_engine = PersonalizationEngine(self.herb_database)
    
    async def recommend_formula(
        self,
        syndrome_type: SyndromeType,
        patient_profile: PatientProfile,
        syndrome_analysis: Dict[str, Any],
        recommendation_type: RecommendationType = RecommendationType.FORMULA
    ) -> RecommendationResult:
        """
        推荐方剂
        
        Args:
            syndrome_type: 证型
            patient_profile: 患者档案
            syndrome_analysis: 辨证分析结果
            recommendation_type: 推荐类型
            
        Returns:
            推荐结果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 获取候选方剂
            candidate_formulas = self.syndrome_mapper.get_formulas_for_syndrome(syndrome_type)
            
            if not candidate_formulas:
                logger.warning(f"未找到适用于证型 {syndrome_type} 的方剂")
                return self._create_empty_result(recommendation_type)
            
            # 选择最佳方剂
            best_formula_name = self._select_best_formula(
                candidate_formulas,
                patient_profile,
                syndrome_analysis
            )
            
            best_formula = self.herb_database.formulas[best_formula_name]
            
            # 个性化调整
            personalized_composition = self.personalization_engine.personalize_recommendation(
                best_formula,
                patient_profile,
                syndrome_analysis
            )
            
            # 安全性检查
            herbs_list = list(personalized_composition.keys())
            
            # 配伍检查
            compatibility_safe, compatibility_warnings = self.compatibility_checker.check_compatibility(herbs_list)
            
            # 患者安全性检查
            safety_level, safety_warnings = self.safety_checker.check_patient_safety(
                herbs_list,
                patient_profile
            )
            
            # 生成用药指导
            dosage_guidance = self._generate_dosage_guidance(personalized_composition)
            preparation_instructions = self._generate_preparation_instructions(best_formula)
            administration_guidance = self._generate_administration_guidance(best_formula)
            
            # 生成注意事项
            precautions = self._generate_precautions(best_formula, patient_profile)
            contraindications = self._generate_contraindications(best_formula, patient_profile)
            monitoring_suggestions = self._generate_monitoring_suggestions(best_formula, patient_profile)
            
            # 计算置信度
            confidence_score = self._calculate_confidence_score(
                best_formula,
                patient_profile,
                syndrome_analysis,
                safety_level
            )
            
            # 生成推理过程
            reasoning = self._generate_reasoning(
                syndrome_type,
                best_formula_name,
                personalized_composition,
                safety_level
            )
            
            # 生成备选推荐
            alternative_recommendations = self._generate_alternatives(
                candidate_formulas,
                best_formula_name,
                patient_profile
            )
            
            # 记录指标
            processing_time = asyncio.get_event_loop().time() - start_time
            await self._record_metrics(
                recommendation_type,
                syndrome_type,
                safety_level,
                confidence_score,
                processing_time
            )
            
            return RecommendationResult(
                recommendation_type=recommendation_type,
                primary_recommendation={
                    "formula_name": best_formula_name,
                    "composition": personalized_composition,
                    "functions": best_formula.functions,
                    "indications": best_formula.indications
                },
                alternative_recommendations=alternative_recommendations,
                safety_assessment={
                    "safety_level": safety_level.value,
                    "compatibility_safe": compatibility_safe,
                    "compatibility_warnings": compatibility_warnings,
                    "safety_warnings": safety_warnings
                },
                dosage_guidance=dosage_guidance,
                preparation_instructions=preparation_instructions,
                administration_guidance=administration_guidance,
                precautions=precautions,
                contraindications=contraindications,
                monitoring_suggestions=monitoring_suggestions,
                confidence_score=confidence_score,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"方剂推荐失败: {e}")
            await self.metrics_collector.increment_counter("herb_recommendation_errors")
            raise
    
    def _select_best_formula(
        self,
        candidate_formulas: List[str],
        patient_profile: PatientProfile,
        syndrome_analysis: Dict[str, Any]
    ) -> str:
        """选择最佳方剂"""
        if len(candidate_formulas) == 1:
            return candidate_formulas[0]
        
        # 简化的选择逻辑，实际应该更复杂
        scores = {}
        
        for formula_name in candidate_formulas:
            formula = self.herb_database.formulas[formula_name]
            score = 0.0
            
            # 体质匹配度
            if patient_profile.constitution_type in formula.constitution_types:
                score += 0.3
            
            # 症状匹配度
            symptom_matches = sum(
                1 for symptom in patient_profile.symptoms
                if any(symptom in indication for indication in formula.indications)
            )
            score += (symptom_matches / len(patient_profile.symptoms)) * 0.4
            
            # 安全性评分
            herbs_list = list(formula.composition.keys())
            safety_level, _ = self.safety_checker.check_patient_safety(herbs_list, patient_profile)
            
            if safety_level == SafetyLevel.SAFE:
                score += 0.3
            elif safety_level == SafetyLevel.CAUTION:
                score += 0.2
            elif safety_level == SafetyLevel.WARNING:
                score += 0.1
            # CONTRAINDICATED 不加分
            
            scores[formula_name] = score
        
        # 返回得分最高的方剂
        return max(scores, key=scores.get)
    
    def _create_empty_result(self, recommendation_type: RecommendationType) -> RecommendationResult:
        """创建空结果"""
        return RecommendationResult(
            recommendation_type=recommendation_type,
            primary_recommendation={},
            confidence_score=0.0,
            reasoning="未找到合适的推荐"
        )
    
    def _generate_dosage_guidance(self, composition: Dict[str, float]) -> Dict[str, str]:
        """生成用药指导"""
        guidance = {}
        
        for herb, dosage in composition.items():
            if herb in self.herb_database.herbs:
                herb_data = self.herb_database.herbs[herb]
                min_dose, max_dose = herb_data.dosage_range
                
                if dosage < min_dose:
                    guidance[herb] = f"{dosage}g (偏小，建议{min_dose}-{max_dose}g)"
                elif dosage > max_dose:
                    guidance[herb] = f"{dosage}g (偏大，建议{min_dose}-{max_dose}g)"
                else:
                    guidance[herb] = f"{dosage}g (正常范围)"
            else:
                guidance[herb] = f"{dosage}g"
        
        return guidance
    
    def _generate_preparation_instructions(self, formula: FormulaData) -> str:
        """生成制备指导"""
        if formula.preparation_method:
            return formula.preparation_method
        else:
            return "将上述药物加水适量，煎煮30分钟，取汁300ml"
    
    def _generate_administration_guidance(self, formula: FormulaData) -> str:
        """生成服用指导"""
        if formula.administration:
            return formula.administration
        else:
            return "每日1剂，分2次温服，饭后30分钟服用"
    
    def _generate_precautions(self, formula: FormulaData, patient_profile: PatientProfile) -> List[str]:
        """生成注意事项"""
        precautions = formula.precautions.copy()
        
        # 根据患者情况添加特殊注意事项
        if patient_profile.is_pregnant:
            precautions.append("孕妇用药需在医师指导下进行")
        
        if patient_profile.age < 18:
            precautions.append("儿童用药需严格控制剂量")
        
        if patient_profile.age >= 65:
            precautions.append("老年人用药需注意观察反应")
        
        return precautions
    
    def _generate_contraindications(self, formula: FormulaData, patient_profile: PatientProfile) -> List[str]:
        """生成禁忌症"""
        contraindications = formula.contraindications.copy()
        
        # 根据患者疾病添加禁忌
        for condition in patient_profile.medical_conditions:
            if condition == "高血压":
                contraindications.append("高血压患者慎用温热药物")
            elif condition == "糖尿病":
                contraindications.append("糖尿病患者避免含糖制剂")
        
        return contraindications
    
    def _generate_monitoring_suggestions(self, formula: FormulaData, patient_profile: PatientProfile) -> List[str]:
        """生成监测建议"""
        suggestions = []
        
        # 基础监测
        suggestions.append("服药期间注意观察症状变化")
        suggestions.append("如出现不适反应，及时停药并咨询医师")
        
        # 特殊人群监测
        if patient_profile.age >= 65:
            suggestions.append("老年人需密切监测血压、心率变化")
        
        if "肝病" in patient_profile.medical_conditions:
            suggestions.append("定期检查肝功能")
        
        if "肾病" in patient_profile.medical_conditions:
            suggestions.append("定期检查肾功能")
        
        return suggestions
    
    def _calculate_confidence_score(
        self,
        formula: FormulaData,
        patient_profile: PatientProfile,
        syndrome_analysis: Dict[str, Any],
        safety_level: SafetyLevel
    ) -> float:
        """计算置信度分数"""
        score = 0.0
        
        # 证型匹配度 (40%)
        if syndrome_analysis.get("primary_syndrome") in [s.value for s in formula.syndrome_types]:
            score += 0.4
        
        # 体质匹配度 (20%)
        if patient_profile.constitution_type in formula.constitution_types:
            score += 0.2
        
        # 症状匹配度 (20%)
        symptom_matches = sum(
            1 for symptom in patient_profile.symptoms
            if any(symptom in indication for indication in formula.indications)
        )
        if patient_profile.symptoms:
            score += (symptom_matches / len(patient_profile.symptoms)) * 0.2
        
        # 安全性 (20%)
        safety_scores = {
            SafetyLevel.SAFE: 0.2,
            SafetyLevel.CAUTION: 0.15,
            SafetyLevel.WARNING: 0.1,
            SafetyLevel.CONTRAINDICATED: 0.0
        }
        score += safety_scores.get(safety_level, 0.0)
        
        return min(score, 1.0)
    
    def _generate_reasoning(
        self,
        syndrome_type: SyndromeType,
        formula_name: str,
        composition: Dict[str, float],
        safety_level: SafetyLevel
    ) -> str:
        """生成推理过程"""
        reasoning = f"推荐理由：\n"
        reasoning += f"1. 根据辨证结果，患者证型为{syndrome_type.value}\n"
        reasoning += f"2. {formula_name}是治疗该证型的经典方剂\n"
        reasoning += f"3. 根据患者具体情况进行个性化调整\n"
        reasoning += f"4. 安全性评估：{safety_level.value}\n"
        reasoning += f"5. 方剂组成：{', '.join([f'{herb} {dose}g' for herb, dose in composition.items()])}"
        
        return reasoning
    
    def _generate_alternatives(
        self,
        candidate_formulas: List[str],
        selected_formula: str,
        patient_profile: PatientProfile
    ) -> List[Dict[str, Any]]:
        """生成备选推荐"""
        alternatives = []
        
        for formula_name in candidate_formulas:
            if formula_name != selected_formula:
                formula = self.herb_database.formulas[formula_name]
                alternatives.append({
                    "formula_name": formula_name,
                    "functions": formula.functions,
                    "indications": formula.indications,
                    "reason": "备选方案，可根据病情变化调整使用"
                })
        
        return alternatives[:3]  # 最多返回3个备选方案
    
    async def _record_metrics(
        self,
        recommendation_type: RecommendationType,
        syndrome_type: SyndromeType,
        safety_level: SafetyLevel,
        confidence_score: float,
        processing_time: float
    ):
        """记录指标"""
        await self.metrics_collector.record_histogram(
            "herb_recommendation_duration_seconds",
            processing_time,
            {
                "type": recommendation_type.value,
                "syndrome": syndrome_type.value,
                "safety": safety_level.value
            }
        )
        
        await self.metrics_collector.record_histogram(
            "herb_recommendation_confidence_score",
            confidence_score,
            {
                "type": recommendation_type.value,
                "syndrome": syndrome_type.value
            }
        )
        
        await self.metrics_collector.increment_counter(
            "herb_recommendation_requests_total",
            {
                "type": recommendation_type.value,
                "syndrome": syndrome_type.value,
                "safety": safety_level.value
            }
        ) 