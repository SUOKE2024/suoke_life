#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""TCM辨证推理引擎实现"""

import logging
import time
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field

# 导入Proto定义
from xiaoai_service.protos import four_diagnosis_pb2 as diagnosis_pb

logger = logging.getLogger(__name__)


@dataclass
class SyndromeRule:
    """辨证规则"""
    syndrome_name: str
    required_features: List[str]
    optional_features: List[str]
    contra_features: List[str]
    min_required: int
    weight: float = 1.0


@dataclass
class ConstitutionRule:
    """体质规则"""
    constitution_name: str
    required_features: List[str]
    optional_features: List[str]
    contra_features: List[str]
    min_required: int
    weight: float = 1.0


class TCMReasoningEngine:
    """TCM辨证推理引擎"""
    
    def __init__(self):
        """初始化TCM辨证推理引擎"""
        # 加载辨证规则
        self.syndrome_rules = self._load_syndrome_rules()
        
        # 加载体质规则
        self.constitution_rules = self._load_constitution_rules()
    
    async def analyze_fusion_result(self, fusion_result: diagnosis_pb.FusionResult) -> Tuple[diagnosis_pb.SyndromeAnalysisResult, diagnosis_pb.ConstitutionAnalysisResult]:
        """
        分析融合结果
        
        Args:
            fusion_result: 融合结果
            
        Returns:
            辨证分析结果和体质分析结果
        """
        # 提取特征
        features = self._extract_features(fusion_result)
        
        # 进行辨证分析
        syndrome_result = await self._analyze_syndrome(features, fusion_result)
        
        # 进行体质分析
        constitution_result = await self._analyze_constitution(features, fusion_result)
        
        return syndrome_result, constitution_result
    
    def _extract_features(self, fusion_result: diagnosis_pb.FusionResult) -> Dict[str, Dict[str, Any]]:
        """
        从融合结果中提取特征
        
        Args:
            fusion_result: 融合结果
            
        Returns:
            特征字典，格式为 {特征名: {值: 值, 置信度: 置信度, ...}}
        """
        features = {}
        
        # 遍历所有融合特征
        for feature in fusion_result.fused_features.features:
            features[feature.feature_name] = {
                "value": feature.feature_value,
                "confidence": feature.confidence,
                "source": feature.source,
                "category": feature.category
            }
        
        return features
    
    async def _analyze_syndrome(self, features: Dict[str, Dict[str, Any]], fusion_result: diagnosis_pb.FusionResult) -> diagnosis_pb.SyndromeAnalysisResult:
        """
        进行辨证分析
        
        Args:
            features: 特征字典
            fusion_result: 融合结果
            
        Returns:
            辨证分析结果
        """
        # 创建辨证分析结果
        result = diagnosis_pb.SyndromeAnalysisResult(
            analysis_id=str(uuid.uuid4()),
            user_id=fusion_result.user_id,
            session_id=fusion_result.session_id,
            created_at=int(time.time())
        )
        
        # 计算每个辨证规则的得分
        syndrome_scores = {}
        
        for rule in self.syndrome_rules:
            score, matched_features, missing_features = self._calculate_syndrome_score(rule, features)
            
            if score > 0:
                syndrome_scores[rule.syndrome_name] = {
                    "score": score,
                    "matched_features": matched_features,
                    "missing_features": missing_features
                }
        
        # 根据得分排序
        sorted_syndromes = sorted(syndrome_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        # 取得分最高的前三个
        top_syndromes = sorted_syndromes[:3]
        
        # 添加到结果中
        for syndrome_name, syndrome_data in top_syndromes:
            syndrome_result = diagnosis_pb.SyndromeResult(
                syndrome_name=syndrome_name,
                confidence=min(syndrome_data["score"], 1.0),
                description=self._get_syndrome_description(syndrome_name)
            )
            
            # 添加匹配的特征
            for feature_name in syndrome_data["matched_features"]:
                syndrome_result.matched_features.append(feature_name)
            
            # 添加缺失的特征
            for feature_name in syndrome_data["missing_features"]:
                syndrome_result.missing_features.append(feature_name)
            
            result.syndromes.append(syndrome_result)
        
        # 计算整体置信度
        if top_syndromes:
            result.overall_confidence = top_syndromes[0][1]["score"]
        else:
            result.overall_confidence = 0.0
        
        # 添加诊断总结
        if top_syndromes:
            top_syndrome_name = top_syndromes[0][0]
            result.summary = f"根据四诊分析，患者主要表现为{top_syndrome_name}证"
            
            if len(top_syndromes) > 1:
                result.summary += f"，兼有{top_syndromes[1][0]}证"
            
            result.summary += f"。主要依据是"
            
            # 添加主要依据
            matched_features = top_syndromes[0][1]["matched_features"]
            if matched_features:
                result.summary += f"{', '.join(matched_features[:3])}"
                
            result.summary += "等症状表现。"
        else:
            result.summary = "未能明确判断辨证类型，建议进一步完善四诊资料。"
        
        return result
    
    async def _analyze_constitution(self, features: Dict[str, Dict[str, Any]], fusion_result: diagnosis_pb.FusionResult) -> diagnosis_pb.ConstitutionAnalysisResult:
        """
        进行体质分析
        
        Args:
            features: 特征字典
            fusion_result: 融合结果
            
        Returns:
            体质分析结果
        """
        # 创建体质分析结果
        result = diagnosis_pb.ConstitutionAnalysisResult(
            analysis_id=str(uuid.uuid4()),
            user_id=fusion_result.user_id,
            session_id=fusion_result.session_id,
            created_at=int(time.time())
        )
        
        # 计算每个体质规则的得分
        constitution_scores = {}
        
        for rule in self.constitution_rules:
            score, matched_features, missing_features = self._calculate_constitution_score(rule, features)
            
            constitution_scores[rule.constitution_name] = {
                "score": score,
                "matched_features": matched_features,
                "missing_features": missing_features
            }
        
        # 添加到结果中
        for constitution_name, constitution_data in constitution_scores.items():
            # 只添加得分大于0.3的体质
            if constitution_data["score"] > 0.3:
                constitution_result = diagnosis_pb.ConstitutionResult(
                    constitution_name=constitution_name,
                    confidence=min(constitution_data["score"], 1.0),
                    description=self._get_constitution_description(constitution_name)
                )
                
                # 添加匹配的特征
                for feature_name in constitution_data["matched_features"]:
                    constitution_result.matched_features.append(feature_name)
                
                # 添加缺失的特征
                for feature_name in constitution_data["missing_features"]:
                    constitution_result.missing_features.append(feature_name)
                
                result.constitutions.append(constitution_result)
        
        # 排序
        result.constitutions.sort(key=lambda x: x.confidence, reverse=True)
        
        # 判断主要体质
        if result.constitutions:
            result.primary_constitution = result.constitutions[0].constitution_name
            result.overall_confidence = result.constitutions[0].confidence
        else:
            result.primary_constitution = "平和质"
            result.overall_confidence = 0.6
        
        # 添加体质总结
        if result.constitutions:
            primary_constitution = result.constitutions[0].constitution_name
            result.summary = f"根据四诊分析，患者主要体质类型为{primary_constitution}"
            
            if len(result.constitutions) > 1 and result.constitutions[1].confidence > 0.5:
                result.summary += f"，兼有{result.constitutions[1].constitution_name}体质倾向"
            
            result.summary += "。"
        else:
            result.summary = "患者基本表现为平和质体质特征。"
        
        return result
    
    def _calculate_syndrome_score(self, rule: SyndromeRule, features: Dict[str, Dict[str, Any]]) -> Tuple[float, List[str], List[str]]:
        """
        计算辨证规则的得分
        
        Args:
            rule: 辨证规则
            features: 特征字典
            
        Returns:
            得分、匹配的特征列表、缺失的特征列表
        """
        matched_required = []
        matched_optional = []
        matched_contra = []
        missing_required = []
        
        # 检查必要特征
        for feature_name in rule.required_features:
            if feature_name in features:
                matched_required.append(feature_name)
            else:
                missing_required.append(feature_name)
        
        # 检查可选特征
        for feature_name in rule.optional_features:
            if feature_name in features:
                matched_optional.append(feature_name)
        
        # 检查矛盾特征
        for feature_name in rule.contra_features:
            if feature_name in features:
                matched_contra.append(feature_name)
        
        # 计算得分
        if len(matched_required) < rule.min_required:
            return 0.0, matched_required + matched_optional, missing_required
        
        # 基础得分：必要特征匹配比例
        base_score = len(matched_required) / len(rule.required_features)
        
        # 加分：可选特征匹配比例
        optional_bonus = 0.0
        if rule.optional_features:
            optional_bonus = 0.3 * (len(matched_optional) / len(rule.optional_features))
        
        # 减分：矛盾特征
        contra_penalty = 0.0
        if rule.contra_features:
            contra_penalty = 0.5 * (len(matched_contra) / len(rule.contra_features))
        
        # 最终得分
        final_score = (base_score + optional_bonus - contra_penalty) * rule.weight
        
        return max(0.0, final_score), matched_required + matched_optional, missing_required
    
    def _calculate_constitution_score(self, rule: ConstitutionRule, features: Dict[str, Dict[str, Any]]) -> Tuple[float, List[str], List[str]]:
        """
        计算体质规则的得分
        
        Args:
            rule: 体质规则
            features: 特征字典
            
        Returns:
            得分、匹配的特征列表、缺失的特征列表
        """
        # 与辨证得分计算类似
        matched_required = []
        matched_optional = []
        matched_contra = []
        missing_required = []
        
        # 检查必要特征
        for feature_name in rule.required_features:
            if feature_name in features:
                matched_required.append(feature_name)
            else:
                missing_required.append(feature_name)
        
        # 检查可选特征
        for feature_name in rule.optional_features:
            if feature_name in features:
                matched_optional.append(feature_name)
        
        # 检查矛盾特征
        for feature_name in rule.contra_features:
            if feature_name in features:
                matched_contra.append(feature_name)
        
        # 计算得分
        if len(matched_required) < rule.min_required:
            # 体质评分更宽松，即使不满足最低要求也可以有得分
            base_score = 0.3 * (len(matched_required) / max(1, len(rule.required_features)))
            return base_score, matched_required + matched_optional, missing_required
        
        # 基础得分：必要特征匹配比例
        base_score = len(matched_required) / len(rule.required_features)
        
        # 加分：可选特征匹配比例
        optional_bonus = 0.0
        if rule.optional_features:
            optional_bonus = 0.3 * (len(matched_optional) / len(rule.optional_features))
        
        # 减分：矛盾特征
        contra_penalty = 0.0
        if rule.contra_features:
            contra_penalty = 0.5 * (len(matched_contra) / len(rule.contra_features))
        
        # 最终得分
        final_score = (base_score + optional_bonus - contra_penalty) * rule.weight
        
        return max(0.0, final_score), matched_required + matched_optional, missing_required
    
    def _get_syndrome_description(self, syndrome_name: str) -> str:
        """
        获取辨证描述
        
        Args:
            syndrome_name: 辨证名称
            
        Returns:
            辨证描述
        """
        # 这里应该从数据库或配置中获取描述
        # 简单起见，这里使用硬编码的描述
        descriptions = {
            "肝郁气滞": "情志不畅，肝气郁结，气机不畅，表现为胸胁胀痛、情绪不稳、嗳气叹息等症状。",
            "肝阳上亢": "肝阳偏亢，上扰清窍，表现为头痛头晕、面红目赤、烦躁易怒、失眠等症状。",
            "肝血不足": "肝血亏虚，不能濡养筋脉，表现为眩晕目眩、肢体麻木、指甲不荣、月经量少等症状。",
            "脾气虚弱": "脾气亏虚，运化无力，表现为食少腹胀、大便溏薄、肢体倦怠、面色萎黄等症状。",
            "脾阳不足": "脾阳不振，温运失职，表现为脘腹冷痛、喜温喜按、大便溏泄、形寒肢冷等症状。",
            "胃阴不足": "胃阴亏虚，胃失濡养，表现为口干烦渴、饥不欲食、胃脘灼热、大便干结等症状。",
            "肺气不足": "肺气虚弱，宣降失职，表现为气短懒言、声低气怯、易感冒、自汗等症状。",
            "肺阴不足": "肺阴亏虚，肺失濡养，表现为干咳少痰、口干咽燥、潮热盗汗、五心烦热等症状。",
            "肾阳不足": "肾阳虚衰，温煦失职，表现为腰膝酸冷、畏寒肢冷、小便清长、性功能减退等症状。",
            "肾阴不足": "肾阴亏虚，阴不制阳，表现为腰膝酸软、五心烦热、失眠多梦、盗汗遗精等症状。",
            "心血不足": "心血亏虚，不能养心安神，表现为心悸怔忡、失眠多梦、面色苍白、健忘等症状。",
            "心阴不足": "心阴亏虚，阴不制阳，表现为心烦失眠、心悸不安、口干舌燥、潮热盗汗等症状。",
            "痰湿阻滞": "痰湿内停，阻滞气机，表现为胸闷脘胀、痰多、头重如裹、乏力嗜睡等症状。",
            "湿热内蕴": "湿热互结，内蕴不解，表现为口苦黏腻、胸闷不舒、小便短赤、大便粘滞等症状。",
            "气滞血瘀": "气机不畅，血行不畅，表现为胸胁刺痛、脘腹胀痛、舌质紫暗、有瘀点瘀斑等症状。",
            "血瘀内阻": "血行不畅，瘀血内阻，表现为刺痛固定、肌肤甲错、舌质紫暗、瘀斑瘀点等症状。"
        }
        
        return descriptions.get(syndrome_name, f"{syndrome_name}证是中医辨证分型的一种，具体表现因人而异。")
    
    def _get_constitution_description(self, constitution_name: str) -> str:
        """
        获取体质描述
        
        Args:
            constitution_name: 体质名称
            
        Returns:
            体质描述
        """
        # 这里应该从数据库或配置中获取描述
        # 简单起见，这里使用硬编码的描述
        descriptions = {
            "平和质": "体态匀称，面色红润，精力充沛，性格平和，对外界环境适应能力强，抗病能力强，很少生病。",
            "气虚质": "体形偏瘦或肥胖，面色淡白，平素语音低弱，气短懒言，容易疲劳，易出汗，舌淡红苔薄白。",
            "阳虚质": "体形偏瘦或肥胖，面色淡白，怕冷，手足不温，精神不振，大便溏薄，小便清长，舌淡胖嫩苔薄白。",
            "阴虚质": "体形偏瘦，面色潮红，口干咽燥，手足心热，容易出汗，大便干燥，小便短黄，舌红少苔。",
            "痰湿质": "体形肥胖，腹部肥满松软，面色淡黄或萎黄，多汗且黏，胸闷脘胀，困倦乏力，舌淡胖边有齿痕苔白腻。",
            "湿热质": "体形偏胖，面垢油光，口干口苦，大便黏滞不爽，小便短黄，舌红苔黄腻。",
            "血瘀质": "面色晦暗，唇色偏暗，肌肤甲错，容易瘀斑，口唇发紫，舌质紫暗有瘀点瘀斑。",
            "气郁质": "体形偏瘦，面色晦暗，情绪不稳，容易焦虑抑郁，多愁善感，胸胁胀满，舌淡红苔薄白。",
            "特禀质": "先天禀赋不足，容易过敏，对药物、食物、季节变化等因素反应敏感，具有特殊体质特点。"
        }
        
        return descriptions.get(constitution_name, f"{constitution_name}是中医体质辨识的一种类型，具有特定的生理病理特点。")
    
    def _load_syndrome_rules(self) -> List[SyndromeRule]:
        """
        加载辨证规则
        
        Returns:
            辨证规则列表
        """
        # 这里应该从数据库或配置文件中加载规则
        # 简单起见，这里使用硬编码的规则
        rules = [
            SyndromeRule(
                syndrome_name="肝郁气滞",
                required_features=["胸胁胀痛", "情绪不稳", "嗳气叹息", "胁肋不适"],
                optional_features=["脉弦", "舌淡红", "月经不调", "乳房胀痛"],
                contra_features=["肢体冰冷", "腹泻"],
                min_required=2,
                weight=1.0
            ),
            SyndromeRule(
                syndrome_name="脾气虚弱",
                required_features=["食欲不振", "腹胀", "大便溏薄", "倦怠乏力"],
                optional_features=["面色萎黄", "舌淡胖", "肢体困重", "浮肿"],
                contra_features=["口干口苦", "便秘"],
                min_required=2,
                weight=1.0
            ),
            SyndromeRule(
                syndrome_name="肾阳不足",
                required_features=["腰膝酸冷", "畏寒肢冷", "小便清长", "神疲乏力"],
                optional_features=["夜尿频多", "性功能减退", "面色晦暗", "舌淡胖嫩"],
                contra_features=["口渴", "潮热盗汗", "手足心热"],
                min_required=2,
                weight=1.0
            ),
            SyndromeRule(
                syndrome_name="痰湿阻滞",
                required_features=["胸闷脘胀", "痰多", "头重如裹", "乏力嗜睡"],
                optional_features=["恶心呕吐", "肥胖", "舌苔厚腻", "面色淡黄"],
                contra_features=["口干舌燥", "大便干结"],
                min_required=2,
                weight=1.0
            ),
            SyndromeRule(
                syndrome_name="气滞血瘀",
                required_features=["胸胁刺痛", "脘腹胀痛", "舌质紫暗", "瘀点瘀斑"],
                optional_features=["月经不调", "经血有块", "口唇暗淡", "肌肤甲错"],
                contra_features=["面色红润", "精力充沛"],
                min_required=2,
                weight=1.0
            ),
            # 可以添加更多规则
        ]
        
        return rules
    
    def _load_constitution_rules(self) -> List[ConstitutionRule]:
        """
        加载体质规则
        
        Returns:
            体质规则列表
        """
        # 这里应该从数据库或配置文件中加载规则
        # 简单起见，这里使用硬编码的规则
        rules = [
            ConstitutionRule(
                constitution_name="平和质",
                required_features=["面色红润", "精力充沛", "食欲良好", "睡眠良好"],
                optional_features=["体态匀称", "性格平和", "舌色淡红", "脉和缓有力"],
                contra_features=["易疲劳", "面色苍白", "怕冷", "多汗"],
                min_required=3,
                weight=1.0
            ),
            ConstitutionRule(
                constitution_name="气虚质",
                required_features=["易疲劳", "气短懒言", "声音低弱", "自汗"],
                optional_features=["面色淡白", "舌淡胖嫩", "食欲不振", "大便溏薄"],
                contra_features=["面色红润", "精力充沛", "舌红少苔"],
                min_required=2,
                weight=1.0
            ),
            ConstitutionRule(
                constitution_name="阳虚质",
                required_features=["怕冷", "手足不温", "面色淡白", "小便清长"],
                optional_features=["腰膝酸冷", "大便溏薄", "舌淡胖嫩", "脉沉细"],
                contra_features=["潮热", "手足心热", "口干舌燥"],
                min_required=2,
                weight=1.0
            ),
            ConstitutionRule(
                constitution_name="阴虚质",
                required_features=["手足心热", "口干", "潮热", "舌红少苔"],
                optional_features=["盗汗", "大便干结", "五心烦热", "脉细数"],
                contra_features=["怕冷", "手足不温", "舌淡胖嫩"],
                min_required=2,
                weight=1.0
            ),
            ConstitutionRule(
                constitution_name="痰湿质",
                required_features=["体形肥胖", "胸闷脘胀", "痰多", "头重如裹"],
                optional_features=["恶心呕吐", "舌苔厚腻", "面色淡黄", "困倦乏力"],
                contra_features=["体形偏瘦", "口干舌燥", "大便干结"],
                min_required=2,
                weight=1.0
            ),
            ConstitutionRule(
                constitution_name="气郁质",
                required_features=["情绪不稳", "胸胁胀满", "烦闷不乐", "叹气"],
                optional_features=["失眠多梦", "食欲不振", "月经不调", "舌淡红苔薄"],
                contra_features=["性格开朗", "精力充沛", "食欲良好"],
                min_required=2,
                weight=1.0
            ),
            # 可以添加更多规则
        ]
        
        return rules 