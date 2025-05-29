#!/usr/bin/env python

"""
中医证型映射器
负责将各种诊断结果映射到中医证型
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TCMPattern:
    """中医证型"""

    name: str
    element: str  # 五行属性
    nature: str  # 寒热虚实
    confidence: float
    description: str
    supporting_findings: list[str]


class TCMPatternMapper:
    """中医证型映射器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化中医证型映射器

        Args:
            config: 配置信息
        """
        self.config = config

        # 初始化证型库
        self.pattern_database = self._init_pattern_database()

        # 初始化症状-证型映射
        self.symptom_pattern_mapping = self._init_symptom_mapping()

        # 初始化五行关系
        self.five_elements = self._init_five_elements()

        logger.info("中医证型映射器初始化完成")

    def _init_pattern_database(self) -> dict[str, dict[str, Any]]:
        """初始化证型数据库"""
        return {
            # 表证
            "wind_cold_exterior": {
                "name": "风寒表证",
                "element": "金",
                "nature": "寒实",
                "description": "风寒外袭，卫表不固，营卫失和",
                "key_symptoms": ["恶寒重", "发热轻", "无汗", "头身疼痛", "鼻塞流涕"],
                "pulse": ["浮", "紧"],
                "tongue": "苔薄白",
            },
            "wind_heat_exterior": {
                "name": "风热表证",
                "element": "火",
                "nature": "热实",
                "description": "风热外袭，卫表不和，肺失宣降",
                "key_symptoms": ["发热重", "恶寒轻", "有汗", "咽喉肿痛", "口渴"],
                "pulse": ["浮", "数"],
                "tongue": "舌尖红，苔薄黄",
            },
            # 里证
            "spleen_qi_deficiency": {
                "name": "脾气虚证",
                "element": "土",
                "nature": "虚",
                "description": "脾失健运，气血生化不足",
                "key_symptoms": ["食少纳呆", "腹胀", "便溏", "倦怠乏力", "面色萎黄"],
                "pulse": ["缓", "弱"],
                "tongue": "舌淡，苔白",
            },
            "kidney_yang_deficiency": {
                "name": "肾阳虚证",
                "element": "水",
                "nature": "虚寒",
                "description": "肾阳不足，命门火衰，温煦失职",
                "key_symptoms": ["腰膝酸软", "畏寒肢冷", "小便清长", "夜尿频多", "性功能减退"],
                "pulse": ["沉", "迟", "弱"],
                "tongue": "舌淡胖，苔白",
            },
            "liver_yin_deficiency": {
                "name": "肝阴虚证",
                "element": "木",
                "nature": "虚热",
                "description": "肝阴不足，虚火上炎",
                "key_symptoms": ["头晕目眩", "两目干涩", "胁肋隐痛", "手足心热", "口燥咽干"],
                "pulse": ["弦", "细", "数"],
                "tongue": "舌红少苔",
            },
            "heart_blood_deficiency": {
                "name": "心血虚证",
                "element": "火",
                "nature": "虚",
                "description": "心血不足，心神失养",
                "key_symptoms": ["心悸怔忡", "失眠多梦", "健忘", "面色淡白", "头晕目眩"],
                "pulse": ["细", "弱"],
                "tongue": "舌淡",
            },
            # 寒热错杂
            "upper_heat_lower_cold": {
                "name": "上热下寒证",
                "element": "水火",
                "nature": "寒热错杂",
                "description": "上焦有热，下焦有寒，寒热错杂",
                "key_symptoms": ["口舌生疮", "咽喉肿痛", "腹部冷痛", "大便溏泄", "小便清长"],
                "pulse": ["上部数", "下部迟"],
                "tongue": "舌尖红，舌根白",
            },
            # 痰湿证
            "phlegm_dampness_obstruction": {
                "name": "痰湿阻滞证",
                "element": "土",
                "nature": "实",
                "description": "脾失健运，痰湿内生，阻滞气机",
                "key_symptoms": ["身重困倦", "胸闷", "痰多", "纳呆", "大便黏滞"],
                "pulse": ["滑", "缓"],
                "tongue": "舌胖大，苔白腻",
            },
            "phlegm_heat": {
                "name": "痰热证",
                "element": "火土",
                "nature": "热实",
                "description": "痰郁化热，痰热互结",
                "key_symptoms": ["咳嗽痰黄", "胸闷", "口苦", "大便秘结", "心烦易怒"],
                "pulse": ["滑", "数"],
                "tongue": "舌红，苔黄腻",
            },
            # 瘀血证
            "blood_stasis": {
                "name": "血瘀证",
                "element": "多变",
                "nature": "实",
                "description": "血行不畅，瘀血内阻",
                "key_symptoms": ["刺痛固定", "痛处拒按", "面色黧黑", "肌肤甲错", "舌下络脉曲张"],
                "pulse": ["涩", "结", "代"],
                "tongue": "舌暗或有瘀斑",
            },
            # 气滞证
            "liver_qi_stagnation": {
                "name": "肝气郁结证",
                "element": "木",
                "nature": "实",
                "description": "情志不遂，肝失疏泄，气机郁滞",
                "key_symptoms": ["胸胁胀满", "善太息", "情志抑郁", "易怒", "月经不调"],
                "pulse": ["弦"],
                "tongue": "舌淡红",
            },
            # 湿热证
            "damp_heat_spleen_stomach": {
                "name": "脾胃湿热证",
                "element": "土火",
                "nature": "热实",
                "description": "湿热蕴结脾胃，运化失常",
                "key_symptoms": ["脘腹痞满", "恶心呕吐", "口苦口黏", "大便黏滞", "小便黄赤"],
                "pulse": ["滑", "数"],
                "tongue": "舌红，苔黄腻",
            },
            "damp_heat_liver_gallbladder": {
                "name": "肝胆湿热证",
                "element": "木火",
                "nature": "热实",
                "description": "湿热蕴结肝胆，疏泄失常",
                "key_symptoms": ["胁肋胀痛", "口苦", "黄疸", "小便黄赤", "带下黄臭"],
                "pulse": ["弦", "滑", "数"],
                "tongue": "舌红，苔黄腻",
            },
        }

    def _init_symptom_mapping(self) -> dict[str, list[str]]:
        """初始化症状-证型映射"""
        return {
            # 脉象映射
            "浮脉": ["wind_cold_exterior", "wind_heat_exterior"],
            "沉脉": ["kidney_yang_deficiency", "blood_stasis"],
            "迟脉": ["kidney_yang_deficiency", "upper_heat_lower_cold"],
            "数脉": ["wind_heat_exterior", "liver_yin_deficiency", "phlegm_heat"],
            "滑脉": ["phlegm_dampness_obstruction", "phlegm_heat", "damp_heat_spleen_stomach"],
            "涩脉": ["blood_stasis", "heart_blood_deficiency"],
            "弦脉": ["liver_qi_stagnation", "liver_yin_deficiency", "damp_heat_liver_gallbladder"],
            "细脉": ["heart_blood_deficiency", "liver_yin_deficiency"],
            "弱脉": ["spleen_qi_deficiency", "kidney_yang_deficiency", "heart_blood_deficiency"],
            "紧脉": ["wind_cold_exterior"],
            "缓脉": ["spleen_qi_deficiency", "phlegm_dampness_obstruction"],
            # 腹诊映射
            "上腹胀满": ["liver_qi_stagnation", "phlegm_dampness_obstruction"],
            "下腹冷痛": ["kidney_yang_deficiency", "upper_heat_lower_cold"],
            "右胁胀痛": ["liver_qi_stagnation", "damp_heat_liver_gallbladder"],
            "脐周压痛": ["spleen_qi_deficiency", "blood_stasis"],
            "全腹胀满": ["phlegm_dampness_obstruction", "liver_qi_stagnation"],
            # 皮肤触诊映射
            "皮肤干燥": ["liver_yin_deficiency", "heart_blood_deficiency"],
            "皮肤冰冷": ["kidney_yang_deficiency", "upper_heat_lower_cold"],
            "皮肤潮湿": ["phlegm_dampness_obstruction", "damp_heat_spleen_stomach"],
            "皮肤粗糙": ["blood_stasis", "heart_blood_deficiency"],
            "皮肤发黄": ["damp_heat_spleen_stomach", "damp_heat_liver_gallbladder"],
        }

    def _init_five_elements(self) -> dict[str, dict[str, Any]]:
        """初始化五行关系"""
        return {
            "木": {
                "organ": "肝胆",
                "emotion": "怒",
                "season": "春",
                "generates": "火",  # 生
                "restrains": "土",  # 克
                "generated_by": "水",  # 被生
                "restrained_by": "金",  # 被克
            },
            "火": {
                "organ": "心小肠",
                "emotion": "喜",
                "season": "夏",
                "generates": "土",
                "restrains": "金",
                "generated_by": "木",
                "restrained_by": "水",
            },
            "土": {
                "organ": "脾胃",
                "emotion": "思",
                "season": "长夏",
                "generates": "金",
                "restrains": "水",
                "generated_by": "火",
                "restrained_by": "木",
            },
            "金": {
                "organ": "肺大肠",
                "emotion": "悲",
                "season": "秋",
                "generates": "水",
                "restrains": "木",
                "generated_by": "土",
                "restrained_by": "火",
            },
            "水": {
                "organ": "肾膀胱",
                "emotion": "恐",
                "season": "冬",
                "generates": "木",
                "restrains": "火",
                "generated_by": "金",
                "restrained_by": "土",
            },
        }

    def map_to_tcm_patterns(
        self,
        pulse_findings: list[dict[str, Any]],
        abdominal_findings: list[dict[str, Any]],
        skin_findings: list[dict[str, Any]],
    ) -> list[TCMPattern]:
        """
        将诊断发现映射到中医证型

        Args:
            pulse_findings: 脉诊发现
            abdominal_findings: 腹诊发现
            skin_findings: 皮肤触诊发现

        Returns:
            中医证型列表
        """
        try:
            # 收集所有症状
            symptoms = self._collect_symptoms(pulse_findings, abdominal_findings, skin_findings)

            # 计算每个证型的匹配度
            pattern_scores = {}

            for symptom in symptoms:
                # 查找与症状相关的证型
                related_patterns = self.symptom_pattern_mapping.get(symptom, [])

                for pattern_key in related_patterns:
                    if pattern_key not in pattern_scores:
                        pattern_scores[pattern_key] = {"score": 0, "matched_symptoms": []}

                    pattern_scores[pattern_key]["score"] += 1
                    pattern_scores[pattern_key]["matched_symptoms"].append(symptom)

            # 转换为TCMPattern对象
            tcm_patterns = []

            for pattern_key, score_info in pattern_scores.items():
                if pattern_key in self.pattern_database:
                    pattern_def = self.pattern_database[pattern_key]

                    # 计算置信度
                    key_symptoms = pattern_def.get("key_symptoms", [])
                    matched_key_symptoms = len([s for s in symptoms if s in key_symptoms])

                    confidence = (score_info["score"] * 0.3 + matched_key_symptoms * 0.7) / max(
                        len(key_symptoms), 1
                    )
                    confidence = min(confidence, 0.95)  # 限制最大置信度

                    if confidence > 0.3:  # 置信度阈值
                        tcm_pattern = TCMPattern(
                            name=pattern_def["name"],
                            element=pattern_def["element"],
                            nature=pattern_def["nature"],
                            confidence=confidence,
                            description=pattern_def["description"],
                            supporting_findings=score_info["matched_symptoms"],
                        )
                        tcm_patterns.append(tcm_pattern)

            # 应用五行关系调整
            tcm_patterns = self._apply_five_elements_theory(tcm_patterns)

            # 按置信度排序
            tcm_patterns.sort(key=lambda x: x.confidence, reverse=True)

            # 返回前5个最可能的证型
            return tcm_patterns[:5]

        except Exception as e:
            logger.exception(f"映射中医证型失败: {e!s}")
            return []

    def _collect_symptoms(
        self,
        pulse_findings: list[dict[str, Any]],
        abdominal_findings: list[dict[str, Any]],
        skin_findings: list[dict[str, Any]],
    ) -> list[str]:
        """收集所有症状"""
        symptoms = []

        # 收集脉象症状
        for finding in pulse_findings:
            pulse_type = finding.get("type", "")
            if pulse_type:
                # 转换脉象类型为中文
                pulse_name_map = {
                    "FLOATING": "浮脉",
                    "SUNKEN": "沉脉",
                    "SLOW": "迟脉",
                    "RAPID": "数脉",
                    "SLIPPERY": "滑脉",
                    "ROUGH": "涩脉",
                    "WIRY": "弦脉",
                    "THREADY": "细脉",
                    "WEAK": "弱脉",
                    "TIGHT": "紧脉",
                    "MODERATE": "缓脉",
                }
                chinese_name = pulse_name_map.get(pulse_type, "")
                if chinese_name:
                    symptoms.append(chinese_name)

        # 收集腹诊症状
        for finding in abdominal_findings:
            finding_type = finding.get("finding_type", "")
            region = finding.get("region_id", "")

            # 转换为症状描述
            if finding_type == "tenderness" and region:
                region_map = {
                    "epigastric": "上腹",
                    "umbilical": "脐周",
                    "hypogastric": "下腹",
                    "right_hypochondriac": "右胁",
                    "left_hypochondriac": "左胁",
                }
                region_name = region_map.get(region, region)
                symptoms.append(f"{region_name}压痛")

            elif finding_type == "distension":
                if region == "whole_abdomen":
                    symptoms.append("全腹胀满")
                else:
                    region_name = region_map.get(region, region)
                    symptoms.append(f"{region_name}胀满")

        # 收集皮肤触诊症状
        for finding in skin_findings:
            finding_type = finding.get("finding_type", "")

            symptom_map = {
                "dry_skin": "皮肤干燥",
                "cold_skin": "皮肤冰冷",
                "moist_skin": "皮肤潮湿",
                "rough_texture": "皮肤粗糙",
                "yellow_color": "皮肤发黄",
            }

            if finding_type in symptom_map:
                symptoms.append(symptom_map[finding_type])

        return symptoms

    def _apply_five_elements_theory(self, patterns: list[TCMPattern]) -> list[TCMPattern]:
        """应用五行理论调整证型"""
        # 如果只有一个证型，不需要调整
        if len(patterns) <= 1:
            return patterns

        # 检查证型之间的五行关系
        adjusted_patterns = patterns.copy()

        for i, pattern1 in enumerate(patterns):
            for j, pattern2 in enumerate(patterns):
                if i != j:
                    element1 = pattern1.element
                    element2 = pattern2.element

                    # 如果存在相生关系，增强置信度
                    if element1 in self.five_elements:
                        if self.five_elements[element1]["generates"] == element2:
                            # 母病及子
                            adjusted_patterns[j] = TCMPattern(
                                name=pattern2.name,
                                element=pattern2.element,
                                nature=pattern2.nature,
                                confidence=min(pattern2.confidence * 1.1, 0.95),
                                description=pattern2.description,
                                supporting_findings=pattern2.supporting_findings
                                + [f"{pattern1.name}(母病及子)"],
                            )
                        elif self.five_elements[element1]["generated_by"] == element2:
                            # 子病及母
                            adjusted_patterns[i] = TCMPattern(
                                name=pattern1.name,
                                element=pattern1.element,
                                nature=pattern1.nature,
                                confidence=min(pattern1.confidence * 1.05, 0.95),
                                description=pattern1.description,
                                supporting_findings=pattern1.supporting_findings
                                + [f"{pattern2.name}(子病及母)"],
                            )

                    # 如果存在相克关系，可能需要调整
                    if element1 in self.five_elements:
                        if self.five_elements[element1]["restrains"] == element2:
                            # 相乘（过度克制）
                            if pattern1.confidence > 0.7:
                                adjusted_patterns[j] = TCMPattern(
                                    name=pattern2.name,
                                    element=pattern2.element,
                                    nature=pattern2.nature,
                                    confidence=min(pattern2.confidence * 1.05, 0.95),
                                    description=pattern2.description,
                                    supporting_findings=pattern2.supporting_findings
                                    + [f"{pattern1.name}(相乘)"],
                                )

        return adjusted_patterns

    def get_treatment_principles(self, patterns: list[TCMPattern]) -> list[str]:
        """
        根据证型获取治疗原则

        Args:
            patterns: 中医证型列表

        Returns:
            治疗原则列表
        """
        principles = []

        for pattern in patterns[:2]:  # 取前两个主要证型
            if pattern.nature == "虚":
                principles.append(f"补益{pattern.name.replace('证', '')}")
            elif pattern.nature == "实":
                principles.append(f"祛除{pattern.name.replace('证', '')}")
            elif pattern.nature == "虚寒":
                principles.append(f"温补{pattern.name.replace('证', '')}")
            elif pattern.nature == "虚热":
                principles.append(f"滋阴清{pattern.name.replace('证', '')}")
            elif pattern.nature == "热实":
                principles.append(f"清热泻{pattern.name.replace('证', '')}")
            elif pattern.nature == "寒实":
                principles.append(f"温散{pattern.name.replace('证', '')}")
            elif pattern.nature == "寒热错杂":
                principles.append("清上温下，调和寒热")

        # 根据五行关系添加治疗原则
        if len(patterns) >= 2:
            element1 = patterns[0].element
            element2 = patterns[1].element

            if element1 in self.five_elements and element2 in self.five_elements:
                if self.five_elements[element1]["generates"] == element2:
                    principles.append(
                        "培土生金" if element1 == "土" and element2 == "金" else "滋水涵木"
                    )
                elif self.five_elements[element1]["restrains"] == element2:
                    principles.append(
                        "抑木扶土" if element1 == "木" and element2 == "土" else "泻南补北"
                    )

        return list(set(principles))  # 去重
