#!/usr/bin/env python
"""
test_tcm_pattern_mapper - 索克生活项目模块
"""


import json
import os
import unittest

from internal.tcm.pattern_mapping.pattern_mapper import PatternMapper

"""
中医证型映射器单元测试
"""


class TestTCMPatternMapper(unittest.TestCase):
    """证型映射器单元测试"""

    def setUp(self) -> None:
        """测试前准备工作"""
        # 创建临时测试配置
        self.test_config = {
            "tcm_knowledge": {
                "patterns_db_path": "./test_data/patterns.json",
                "symptoms_mapping_path": "./test_data/symptoms_mapping.json",
                "rules_path": "./test_data/rules.json",
                "confidence_threshold": 0.6,
                "max_patterns": 5,
            }
        }

        # 创建测试数据目录
        os.makedirs("./test_data", exist_ok=True)

        # 创建测试证型数据
        test_patterns = [
            {
                "id": "P001",
                "name": "肝郁脾虚证",
                "english_name": "Liver Qi Stagnation with Spleen Deficiency",
                "category": "复合证型",
                "description": "肝气郁结，脾气虚弱的证候",
                "main_symptoms": ["胸胁胀痛", "腹胀", "食欲不振", "情绪抑郁"],
                "tongue": "舌淡红，苔薄白",
                "pulse": "脉弦细",
            },
            {
                "id": "P002",
                "name": "肺气虚证",
                "english_name": "Lung Qi Deficiency",
                "category": "虚证",
                "description": "肺气不足的证候",
                "main_symptoms": ["气短", "乏力", "声音低微", "易感冒"],
                "tongue": "舌淡，苔薄白",
                "pulse": "脉虚弱",
            },
        ]

        with open("./test_data/patterns.json", "w", encoding="utf-8") as f:
            json.dump(test_patterns, f, ensure_ascii=False, indent=2)

        # 创建测试症状映射数据
        test_symptoms_mapping = [
            {
                "symptom_name": "胸胁胀痛",
                "pattern_associations": {"肝郁脾虚证": 0.9, "肝气郁结证": 0.8},
            },
            {
                "symptom_name": "腹胀",
                "pattern_associations": {"肝郁脾虚证": 0.8, "脾虚证": 0.7},
            },
            {
                "symptom_name": "气短",
                "pattern_associations": {"肺气虚证": 0.9, "心气虚证": 0.6},
            },
        ]

        with open("./test_data/symptoms_mapping.json", "w", encoding="utf-8") as f:
            json.dump(test_symptoms_mapping, f, ensure_ascii=False, indent=2)

        # 创建测试规则数据
        test_rules = [
            {
                "rule_id": "R001",
                "pattern_name": "肝郁脾虚证",
                "required_symptoms": ["胸胁胀痛", "腹胀"],
                "supporting_symptoms": {"食欲不振": 0.7, "情绪抑郁": 0.8},
                "minimum_required_count": 1,
                "minimum_supporting_score": 0.5,
                "tongue_rules": "舌淡红.*苔薄白",
                "pulse_rules": "脉弦细",
            },
            {
                "rule_id": "R002",
                "pattern_name": "肺气虚证",
                "required_symptoms": ["气短", "乏力"],
                "supporting_symptoms": {"声音低微": 0.6, "易感冒": 0.7},
                "minimum_required_count": 1,
                "minimum_supporting_score": 0.4,
                "tongue_rules": "舌淡.*苔薄白",
                "pulse_rules": "脉虚弱",
            },
        ]

        with open("./test_data/rules.json", "w", encoding="utf-8") as f:
            json.dump(test_rules, f, ensure_ascii=False, indent=2)

        # 初始化映射器
        self.pattern_mapper = PatternMapper(self.test_config)

    def tearDown(self) -> None:
        """测试结束后清理工作"""
        # 删除临时测试数据文件
        try:
            os.remove("./test_data/patterns.json")
            os.remove("./test_data/symptoms_mapping.json")
            os.remove("./test_data/rules.json")
            os.rmdir("./test_data")
        except FileNotFoundError:
            pass

    def test_apply_diagnosis_rules(self) -> None:
        """测试辨证规则应用"""
        # 准备测试症状
        symptoms = [
            {"name": "胸胁胀痛", "severity": "中度"},
            {"name": "腹胀", "severity": "轻度"},
            {"name": "食欲不振", "severity": "中度"},
        ]
        tongue_features = ["舌淡红", "苔薄白"]
        pulse_features = ["脉弦细"]

        # 执行规则应用
        pattern_scores1 = self.pattern_mapper._apply_diagnosis_rules(
            symptoms, tongue_features, pulse_features
        )

        # 验证结果
        self.assertIn("肝郁脾虚证", pattern_scores1)
        self.assertGreater(pattern_scores1["肝郁脾虚证"], 0.8)  # 应该有较高得分

        # 测试不匹配的情况
        symptoms2 = [{"name": "头痛", "severity": "轻度"}]
        pattern_scores2 = self.pattern_mapper._apply_diagnosis_rules(
            symptoms2, [], []
        )
        self.assertNotIn("肝郁脾虚证", pattern_scores2)  # 不应出现此证型

    def test_calculate_symptom_pattern_scores(self) -> None:
        """测试症状-证型关联分数计算"""
        # 准备测试症状
        symptoms = [
            {"name": "胸胁胀痛", "severity": "重度"},
            {"name": "腹胀", "severity": "中度"},
            {"name": "食欲不振", "severity": "轻度"},
        ]

        # 执行分数计算
        pattern_scores = self.pattern_mapper._calculate_symptom_pattern_scores(symptoms)

        # 验证结果
        self.assertIn("肝郁脾虚证", pattern_scores)
        self.assertGreater(pattern_scores["肝郁脾虚证"], 0.7)  # 应该有较高得分

    def test_combine_pattern_scores(self) -> None:
        """测试证型得分合并"""
        # 准备测试数据
        rule_scores = {"肝郁脾虚证": 0.8, "痰湿阻肺证": 0.5}
        symptom_scores = {"肝郁脾虚证": 0.9, "肺气虚证": 0.7}

        # 执行得分合并
        combined_scores = self.pattern_mapper._combine_pattern_scores(
            rule_scores, symptom_scores
        )

        # 验证结果
        self.assertIn("肝郁脾虚证", combined_scores)
        self.assertIn("肺气虚证", combined_scores)
        self.assertIn("痰湿阻肺证", combined_scores)

        # 验证合并逻辑
        # 肝郁脾虚证应该有最高得分（规则分数 * 0.6 + 症状分数 * 0.4）
        expected_score = 0.8 * 0.6 + 0.9 * 0.4
        self.assertAlmostEqual(combined_scores["肝郁脾虚证"], expected_score, places=6)

    def test_generate_tcm_patterns(self) -> None:
        """测试生成证型列表"""
        # 准备测试数据
        pattern_scores = {"肝郁脾虚证": 0.85, "肺气虚证": 0.75, "不存在的证型": 0.9}

        # 执行证型生成
        patterns = self.pattern_mapper._generate_tcm_patterns(pattern_scores)

        # 验证结果
        self.assertEqual(len(patterns), 2)  # 应该过滤掉不存在的证型
        self.assertEqual(patterns[0].pattern_name, "肝郁脾虚证")  # 按得分排序
        self.assertEqual(patterns[1].pattern_name, "肺气虚证")
        self.assertGreater(patterns[0].confidence, patterns[1].confidence)

        # 验证证型详细信息
        self.assertTrue(len(patterns[0].description) > 0)
        self.assertTrue(len(patterns[0].recommendations) > 0)

    def test_map_symptoms_to_patterns(self) -> None:
        """测试完整的症状到证型映射流程"""
        # 准备测试症状
        symptoms = [
            {"name": "胸胁胀痛", "severity": "重度"},
            {"name": "腹胀", "severity": "中度"},
            {"name": "食欲不振", "severity": "轻度"},
            {"name": "情绪抑郁", "severity": "中度"},
        ]
        tongue_features = ["舌淡红", "苔薄白"]
        pulse_features = ["脉弦细"]

        # 执行完整映射
        result = self.pattern_mapper.map_symptoms_to_patterns(
            symptoms, tongue_features, pulse_features
        )

        # 验证结果
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0].pattern_name, "肝郁脾虚证")
        self.assertGreater(result[0].confidence, 0.8)

        # 验证返回的证型对象
        pattern = result[0]
        self.assertTrue(hasattr(pattern, "pattern_id"))
        self.assertTrue(hasattr(pattern, "pattern_name"))
        self.assertTrue(hasattr(pattern, "confidence"))
        self.assertTrue(hasattr(pattern, "matched_symptoms"))
        self.assertTrue(hasattr(pattern, "description"))
        self.assertTrue(hasattr(pattern, "recommendations"))


if __name__ == "__main__":
    unittest.main()
