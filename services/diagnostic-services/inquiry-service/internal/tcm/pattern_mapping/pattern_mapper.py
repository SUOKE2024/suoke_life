#!/usr/bin/env python

"""
中医证型映射引擎
负责将现代症状描述映射到传统中医证型体系
"""

import json
import logging
import os

from internal.model.dialogue_models import Symptom, TCMPattern, TCMPatternMappingResult
from internal.model.tcm_models import (
    DetailedTCMPattern,
    SymptomTCMMapping,
    TCMDiagnosisRule,
)


class PatternMapper:
    """
    证型映射器
    将症状映射到相应的中医证型，基于规则匹配和语义相似度
    """

    def __init__(self, config: dict = None):
        """
        初始化证型映射器

        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger(__name__)

        if config is None:
            config = {}

        # 从配置中加载设置
        self.similarity_threshold = config.get("similarity_threshold", 0.7)
        self.min_symptom_count = config.get("min_symptom_count", 2)

        # 规则库文件路径
        rules_path = config.get(
            "tcm_rules_path", os.path.join("config", "tcm_rules.json")
        )
        mapping_path = config.get(
            "symptom_mapping_path", os.path.join("config", "symptom_mapping.json")
        )
        patterns_path = config.get(
            "tcm_patterns_path", os.path.join("config", "tcm_patterns.json")
        )

        # 加载中医知识库
        self.diagnosis_rules = self._load_diagnosis_rules(rules_path)
        self.symptom_mappings = self._load_symptom_mappings(mapping_path)
        self.tcm_patterns = self._load_tcm_patterns(patterns_path)

        self.logger.info(
            f"证型映射器初始化完成，加载了 {len(self.diagnosis_rules)} 条辨证规则"
        )

    def _load_diagnosis_rules(self, path: str) -> dict[str, TCMDiagnosisRule]:
        """
        加载中医辨证规则

        Args:
            path: 规则文件路径

        Returns:
            规则字典，键为规则ID
        """
        try:
            with open(path, encoding="utf-8") as f:
                rules_data = json.load(f)

            rules = {}
            for rule_data in rules_data:
                rule_id = rule_data.get("rule_id")
                rule = TCMDiagnosisRule(
                    rule_id=rule_id,
                    pattern_name=rule_data.get("pattern_name"),
                    required_symptoms=set(rule_data.get("required_symptoms", [])),
                    supporting_symptoms=rule_data.get("supporting_symptoms", {}),
                    exclusion_symptoms=set(rule_data.get("exclusion_symptoms", [])),
                    minimum_required_count=rule_data.get("minimum_required_count", 1),
                    minimum_supporting_score=rule_data.get(
                        "minimum_supporting_score", 0.0
                    ),
                    tongue_rules=rule_data.get("tongue_rules"),
                    pulse_rules=rule_data.get("pulse_rules"),
                )
                rules[rule_id] = rule

            self.logger.info(f"成功加载 {len(rules)} 条中医辨证规则")
            return rules

        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"加载中医辨证规则失败: {e!s}，将使用默认值")
            return {}

    def _load_symptom_mappings(self, path: str) -> dict[str, SymptomTCMMapping]:
        """
        加载症状映射表

        Args:
            path: 映射文件路径

        Returns:
            映射字典，键为现代症状名称
        """
        try:
            with open(path, encoding="utf-8") as f:
                mappings_data = json.load(f)

            mappings = {}
            for mapping_data in mappings_data:
                symptom_name = mapping_data.get("symptom_name")
                mapping = SymptomTCMMapping(
                    symptom_name=symptom_name,
                    tcm_interpretations=mapping_data.get("tcm_interpretations", []),
                    pattern_associations=mapping_data.get("pattern_associations", {}),
                )
                mappings[symptom_name] = mapping

            self.logger.info(f"成功加载 {len(mappings)} 条症状映射")
            return mappings

        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"加载症状映射失败: {e!s}，将使用默认值")
            return {}

    def _load_tcm_patterns(self, path: str) -> dict[str, DetailedTCMPattern]:
        """
        加载中医证型详情

        Args:
            path: 证型文件路径

        Returns:
            证型字典，键为证型ID
        """
        try:
            with open(path, encoding="utf-8") as f:
                patterns_data = json.load(f)

            patterns = {}
            for pattern_data in patterns_data:
                pattern_id = pattern_data.get("id")
                pattern = DetailedTCMPattern(**pattern_data)
                patterns[pattern_id] = pattern

            self.logger.info(f"成功加载 {len(patterns)} 条中医证型")
            return patterns

        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"加载中医证型失败: {e!s}，将使用默认值")
            return {}

    def map_symptoms_to_patterns(
        self, symptoms: list[Symptom]
    ) -> TCMPatternMappingResult:
        """
        将症状映射到中医证型

        Args:
            symptoms: 症状列表

        Returns:
            证型映射结果
        """
        self.logger.info(f"开始将 {len(symptoms)} 个症状映射到中医证型")

        if not symptoms:
            self.logger.warning("没有提供症状信息")
            return TCMPatternMappingResult(patterns=[], confidence=0.0)

        # 应用辨证规则匹配证型
        pattern_scores = self._apply_diagnosis_rules(symptoms)

        # 基于症状-证型关联计算证型得分
        symptom_pattern_scores = self._calculate_symptom_pattern_scores(symptoms)

        # 合并两种方法的结果
        combined_scores = self._combine_pattern_scores(
            pattern_scores, symptom_pattern_scores
        )

        # 生成最终证型列表
        tcm_patterns = self._generate_tcm_patterns(combined_scores)

        # 找出主要证型
        primary_pattern = tcm_patterns[0] if tcm_patterns else None

        # 生成证型分析报告
        analysis = self._generate_pattern_analysis(symptoms, tcm_patterns)

        # 计算整体置信度
        confidence = self._calculate_overall_confidence(tcm_patterns, symptoms)

        result = TCMPatternMappingResult(
            patterns=tcm_patterns,
            primary_pattern=primary_pattern,
            confidence=confidence,
            analysis=analysis,
        )

        self.logger.info(
            f"完成证型映射，找到 {len(tcm_patterns)} 个相关证型，主要证型: {primary_pattern.name if primary_pattern else 'None'}"
        )
        return result

    def _apply_diagnosis_rules(self, symptoms: list[Symptom]) -> dict[str, float]:
        """
        应用辨证规则

        Args:
            symptoms: 症状列表

        Returns:
            证型得分字典，键为证型名称，值为得分（0-1）
        """
        pattern_scores = {}
        symptom_names = {s.name.lower() for s in symptoms}

        # 遍历所有辨证规则
        for rule_id, rule in self.diagnosis_rules.items():
            pattern_name = rule.pattern_name

            # 计算必备症状匹配数量
            required_matched = symptom_names.intersection(rule.required_symptoms)
            required_match_count = len(required_matched)

            # 如果必备症状不足，则跳过此规则
            if required_match_count < rule.minimum_required_count:
                continue

            # 检查是否存在排除症状
            if symptom_names.intersection(rule.exclusion_symptoms):
                continue

            # 计算支持症状得分
            supporting_score = 0.0
            for symptom_name, weight in rule.supporting_symptoms.items():
                if symptom_name.lower() in symptom_names:
                    supporting_score += weight

            # 如果支持症状得分不足，则跳过此规则
            if supporting_score < rule.minimum_supporting_score:
                continue

            # 计算规则匹配总分
            required_ratio = required_match_count / max(1, len(rule.required_symptoms))
            total_score = 0.6 * required_ratio + 0.4 * min(
                1.0, supporting_score / max(1.0, rule.minimum_supporting_score * 2)
            )

            # 更新证型得分
            if pattern_name in pattern_scores:
                pattern_scores[pattern_name] = max(
                    pattern_scores[pattern_name], total_score
                )
            else:
                pattern_scores[pattern_name] = total_score

        return pattern_scores

    def _calculate_symptom_pattern_scores(
        self, symptoms: list[Symptom]
    ) -> dict[str, float]:
        """
        基于症状-证型关联计算证型得分

        Args:
            symptoms: 症状列表

        Returns:
            证型得分字典，键为证型名称，值为得分（0-1）
        """
        pattern_scores = {}

        # 遍历所有症状
        for symptom in symptoms:
            symptom_name = symptom.name.lower()

            # 如果症状存在于映射表中
            if symptom_name in self.symptom_mappings:
                mapping = self.symptom_mappings[symptom_name]

                # 更新证型得分
                for pattern_name, weight in mapping.pattern_associations.items():
                    pattern_scores[pattern_name] = (
                        pattern_scores.get(pattern_name, 0.0)
                        + weight * symptom.confidence
                    )

        # 归一化得分，确保最高分不超过1.0
        max_score = max(pattern_scores.values(), default=0.0)
        if max_score > 0:
            for pattern_name in pattern_scores:
                pattern_scores[pattern_name] /= max_score

        return pattern_scores

    def _combine_pattern_scores(
        self, rule_scores: dict[str, float], symptom_scores: dict[str, float]
    ) -> dict[str, float]:
        """
        合并规则匹配和症状关联的证型得分

        Args:
            rule_scores: 规则匹配得分
            symptom_scores: 症状关联得分

        Returns:
            合并后的证型得分
        """
        combined_scores = {}

        # 合并所有证型
        all_patterns = set(list(rule_scores.keys()) + list(symptom_scores.keys()))

        for pattern_name in all_patterns:
            rule_score = rule_scores.get(pattern_name, 0.0)
            symptom_score = symptom_scores.get(pattern_name, 0.0)

            # 加权合并，规则匹配权重更高
            combined_scores[pattern_name] = 0.7 * rule_score + 0.3 * symptom_score

        return combined_scores

    def _generate_tcm_patterns(
        self, pattern_scores: dict[str, float]
    ) -> list[TCMPattern]:
        """
        根据证型得分生成证型列表

        Args:
            pattern_scores: 证型得分字典

        Returns:
            证型对象列表，按得分降序排列
        """
        tcm_patterns = []

        # 按得分降序排列证型
        sorted_patterns = sorted(
            pattern_scores.items(), key=lambda x: x[1], reverse=True
        )

        # 转换为TCMPattern对象
        for pattern_name, score in sorted_patterns:
            # 如果得分低于阈值，则忽略
            if score < self.similarity_threshold:
                continue

            # 查找证型详细信息
            pattern_id = None
            description = ""
            key_symptoms = []
            recommendations = []
            found = False

            # 从证型库中查找详细信息
            for pid, detailed_pattern in self.tcm_patterns.items():
                if detailed_pattern.name == pattern_name:
                    pattern_id = pid
                    description = detailed_pattern.description
                    key_symptoms = detailed_pattern.main_symptoms
                    recommendations = (
                        detailed_pattern.dietary_recommendations
                        + detailed_pattern.lifestyle_recommendations
                    )
                    found = True
                    break

            # 只有找到证型详细信息时才添加到结果中
            if found:
                # 创建TCMPattern对象
                tcm_pattern = TCMPattern(
                    name=pattern_name,
                    score=score,
                    key_symptoms=key_symptoms,
                    description=description,
                    recommendations=recommendations,
                )
                tcm_patterns.append(tcm_pattern)
            else:
                self.logger.warning(
                    f"证型 '{pattern_name}' 在证型库中未找到详细信息，已跳过"
                )

        return tcm_patterns

    def _generate_pattern_analysis(
        self, symptoms: list[Symptom], patterns: list[TCMPattern]
    ) -> str:
        """
        生成证型分析报告

        Args:
            symptoms: 症状列表
            patterns: 证型列表

        Returns:
            证型分析文本
        """
        if not patterns:
            return "无法确定明确的中医证型，可能需要更多的症状信息。"

        primary_pattern = patterns[0]

        analysis = f"根据您的症状表现，主要表现为{primary_pattern.name}。"

        # 添加证型描述
        if primary_pattern.description:
            analysis += f"\n\n{primary_pattern.description}"

        # 添加症状与证型的关联分析
        symptom_analysis = "\n\n您的主要症状对应分析如下："
        for symptom in symptoms[:5]:  # 只分析前5个主要症状
            symptom_analysis += f"\n- {symptom.name}"

            # 查找症状的中医解释
            if symptom.name.lower() in self.symptom_mappings:
                mapping = self.symptom_mappings[symptom.name.lower()]
                if mapping.tcm_interpretations:
                    top_interpretation = mapping.tcm_interpretations[0]
                    for interp_name, interp_weight in top_interpretation.items():
                        symptom_analysis += f"，从中医角度看可能反映了{interp_name}"
                        break

        analysis += symptom_analysis

        # 如果有多个证型，添加兼夹证型分析
        if len(patterns) > 1:
            secondary_patterns = [p.name for p in patterns[1:3]]  # 取排名第2、3的证型
            analysis += f"\n\n同时兼夹有{', '.join(secondary_patterns)}的表现。"

        # 添加治疗原则和建议
        if primary_pattern.recommendations:
            analysis += "\n\n治疗调养建议："
            for i, rec in enumerate(
                primary_pattern.recommendations[:5]
            ):  # 最多显示5条建议
                analysis += f"\n{i + 1}. {rec}"

        return analysis

    def _calculate_overall_confidence(
        self, patterns: list[TCMPattern], symptoms: list[Symptom]
    ) -> float:
        """
        计算整体置信度

        Args:
            patterns: 证型列表
            symptoms: 症状列表

        Returns:
            置信度（0-1）
        """
        if not patterns:
            return 0.0

        # 基于主要证型得分
        primary_score = patterns[0].score if patterns else 0.0

        # 基于症状数量（症状越多，置信度越高）
        symptom_factor = min(1.0, len(symptoms) / 7.0)  # 假设7个以上症状可获得满分

        # 基于症状置信度平均值
        symptom_confidence_avg = sum(s.confidence for s in symptoms) / max(
            1, len(symptoms)
        )

        # 综合计算
        overall_confidence = (
            0.5 * primary_score + 0.3 * symptom_factor + 0.2 * symptom_confidence_avg
        )

        return overall_confidence
