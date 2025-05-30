#!/usr/bin/env python

"""
中医证型映射器单元测试
"""

import json
import os
import unittest

from internal.model.dialogue_models import Symptom, SymptomDuration, SymptomSeverity
from internal.tcm.pattern_mapping.pattern_mapper import PatternMapper


class TestPatternMapper(unittest.TestCase):
    """证型映射器单元测试"""

    def setUp(self):
        """测试前准备工作"""
        # 创建临时测试配置
        self.test_config = {
            "similarity_threshold": 0.6,
            "min_symptom_count": 2,
            "tcm_rules_path": "test/data/tcm_rules_test.json",
            "symptom_mapping_path": "test/data/symptom_mapping_test.json",
            "tcm_patterns_path": "test/data/tcm_patterns_test.json",
        }

        # 确保测试数据目录存在
        os.makedirs("test/data", exist_ok=True)

        # 创建测试规则数据
        self.test_rules = [
            {
                "rule_id": "R001",
                "pattern_name": "肝郁脾虚证",
                "required_symptoms": ["胸胁胀痛", "脘腹胀满", "食欲不振"],
                "supporting_symptoms": {"易怒": 0.8, "疲倦乏力": 0.7, "嗳气": 0.6},
                "exclusion_symptoms": ["高热", "剧烈腹痛"],
                "minimum_required_count": 2,
                "minimum_supporting_score": 0.6,
            },
            {
                "rule_id": "R002",
                "pattern_name": "肺气虚证",
                "required_symptoms": ["气短", "自汗", "声音低弱"],
                "supporting_symptoms": {"疲倦乏力": 0.8, "易感冒": 0.7, "咳嗽": 0.6},
                "exclusion_symptoms": ["潮热", "烦躁"],
                "minimum_required_count": 2,
                "minimum_supporting_score": 0.5,
            },
        ]

        # 创建测试症状映射数据
        self.test_mappings = [
            {
                "symptom_name": "胸闷",
                "tcm_interpretations": [{"气机不畅": 0.8}, {"痰湿阻滞": 0.6}],
                "pattern_associations": {"肝郁脾虚证": 0.7, "痰湿阻肺证": 0.6},
            },
            {
                "symptom_name": "食欲不振",
                "tcm_interpretations": [{"脾胃运化失常": 0.9}],
                "pattern_associations": {"肝郁脾虚证": 0.8, "脾胃虚弱证": 0.9},
            },
            {
                "symptom_name": "气短",
                "tcm_interpretations": [{"肺气虚": 0.9}, {"心气虚": 0.7}],
                "pattern_associations": {"肺气虚证": 0.9, "心气虚证": 0.7},
            },
        ]

        # 创建测试证型数据
        self.test_patterns = [
            {
                "id": "P001",
                "name": "肝郁脾虚证",
                "english_name": "Liver Qi Stagnation with Spleen Deficiency",
                "category": "zang_fu",
                "description": "肝郁脾虚证是由于肝的疏泄功能失常，导致肝气郁结，横逆犯脾，影响脾的运化功能而形成的证候。",
                "main_symptoms": ["胸胁胀痛", "脘腹胀满", "嗳气", "食欲不振", "易怒"],
                "secondary_symptoms": ["舌淡红，苔薄白", "脉弦细"],
                "dietary_recommendations": ["宜食清淡易消化食物", "忌食辛辣刺激食物"],
                "lifestyle_recommendations": ["保持情绪稳定", "适当运动"],
            },
            {
                "id": "P002",
                "name": "肺气虚证",
                "english_name": "Lung Qi Deficiency",
                "category": "zang_fu",
                "description": "肺气虚证是由于肺的宣降功能减弱，肺气不足所形成的证候。",
                "main_symptoms": ["气短", "咳嗽无力", "声音低弱", "自汗", "易感冒"],
                "secondary_symptoms": ["舌淡胖，苔薄白", "脉虚弱"],
                "dietary_recommendations": ["宜食温补肺气食物", "避免生冷食物"],
                "lifestyle_recommendations": ["注意保暖", "避免过度劳累"],
            },
        ]

        # 写入测试数据到临时文件
        with open(self.test_config["tcm_rules_path"], "w", encoding="utf-8") as f:
            json.dump(self.test_rules, f, ensure_ascii=False, indent=2)

        with open(self.test_config["symptom_mapping_path"], "w", encoding="utf-8") as f:
            json.dump(self.test_mappings, f, ensure_ascii=False, indent=2)

        with open(self.test_config["tcm_patterns_path"], "w", encoding="utf-8") as f:
            json.dump(self.test_patterns, f, ensure_ascii=False, indent=2)

        # 创建测试对象
        self.pattern_mapper = PatternMapper(self.test_config)

    def tearDown(self):
        """测试结束后清理工作"""
        # 删除临时测试数据文件
        try:
            os.remove(self.test_config["tcm_rules_path"])
            os.remove(self.test_config["symptom_mapping_path"])
            os.remove(self.test_config["tcm_patterns_path"])
        except FileNotFoundError:
            pass

    def test_apply_diagnosis_rules(self):
        """测试辨证规则应用"""
        # 准备测试症状
        symptoms = [
            Symptom(name="胸胁胀痛", confidence=0.9),
            Symptom(name="脘腹胀满", confidence=0.8),
            Symptom(name="食欲不振", confidence=0.9),
            Symptom(name="易怒", confidence=0.7),
        ]

        # 调用待测试方法
        pattern_scores = self.pattern_mapper._apply_diagnosis_rules(symptoms)

        # 验证结果
        self.assertIn("肝郁脾虚证", pattern_scores)
        self.assertGreater(pattern_scores["肝郁脾虚证"], 0.7)  # 应该有较高得分

        # 测试不满足条件的情况
        symptoms2 = [
            Symptom(name="胸胁胀痛", confidence=0.9),
            Symptom(name="高热", confidence=0.8),  # 排除症状
        ]
        pattern_scores2 = self.pattern_mapper._apply_diagnosis_rules(symptoms2)
        self.assertNotIn("肝郁脾虚证", pattern_scores2)  # 不应出现此证型

    def test_calculate_symptom_pattern_scores(self):
        """测试症状-证型关联分数计算"""
        # 准备测试症状
        symptoms = [
            Symptom(name="胸闷", confidence=0.9),
            Symptom(name="食欲不振", confidence=0.8),
        ]

        # 调用待测试方法
        pattern_scores = self.pattern_mapper._calculate_symptom_pattern_scores(symptoms)

        # 验证结果
        self.assertIn("肝郁脾虚证", pattern_scores)
        self.assertGreater(pattern_scores["肝郁脾虚证"], 0.7)  # 应该有较高得分

    def test_combine_pattern_scores(self):
        """测试证型得分合并"""
        # 准备测试数据
        rule_scores = {"肝郁脾虚证": 0.8, "痰湿阻肺证": 0.5}
        symptom_scores = {"肝郁脾虚证": 0.7, "脾胃虚弱证": 0.6}

        # 调用待测试方法
        combined_scores = self.pattern_mapper._combine_pattern_scores(
            rule_scores, symptom_scores
        )

        # 验证结果
        self.assertEqual(len(combined_scores), 3)  # 三个证型
        self.assertIn("肝郁脾虚证", combined_scores)
        self.assertIn("痰湿阻肺证", combined_scores)
        self.assertIn("脾胃虚弱证", combined_scores)

        # 验证权重计算
        expected_score = 0.7 * 0.8 + 0.3 * 0.7  # 规则权重0.7，症状关联权重0.3
        self.assertAlmostEqual(combined_scores["肝郁脾虚证"], expected_score, places=6)

    def test_generate_tcm_patterns(self):
        """测试生成证型列表"""
        # 准备测试数据
        pattern_scores = {"肝郁脾虚证": 0.85, "肺气虚证": 0.75, "不存在的证型": 0.9}

        # 调用待测试方法
        patterns = self.pattern_mapper._generate_tcm_patterns(pattern_scores)

        # 验证结果
        self.assertEqual(len(patterns), 2)  # 只有2个证型在库中存在
        self.assertEqual(patterns[0].name, "肝郁脾虚证")  # 第一个应该是肝郁脾虚证
        self.assertEqual(patterns[1].name, "肺气虚证")  # 第二个应该是肺气虚证

        # 验证证型数据完整性
        self.assertEqual(patterns[0].score, 0.85)
        self.assertTrue(len(patterns[0].key_symptoms) > 0)
        self.assertTrue(len(patterns[0].recommendations) > 0)

    def test_map_symptoms_to_patterns(self):
        """测试完整的症状到证型映射流程"""
        # 准备测试症状
        symptoms = [
            Symptom(
                name="胸胁胀痛",
                description="右侧胸胁部有胀痛感",
                body_part="胸胁",
                severity=SymptomSeverity.MODERATE,
                duration=SymptomDuration.CHRONIC,
                duration_value=30,
                confidence=0.9,
            ),
            Symptom(
                name="脘腹胀满",
                description="胃脘部有胀满感，进食后加重",
                body_part="腹部",
                severity=SymptomSeverity.MODERATE,
                confidence=0.8,
            ),
            Symptom(
                name="食欲不振", description="没有胃口，不想吃东西", confidence=0.9
            ),
            Symptom(name="易怒", description="容易发脾气，情绪波动大", confidence=0.7),
        ]

        # 调用待测试方法
        result = self.pattern_mapper.map_symptoms_to_patterns(symptoms)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertTrue(len(result.patterns) > 0)
        self.assertEqual(result.primary_pattern.name, "肝郁脾虚证")
        self.assertGreater(result.confidence, 0.7)
        self.assertTrue(len(result.analysis) > 0)


if __name__ == "__main__":
    unittest.main()
