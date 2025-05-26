#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辨证分析引擎单元测试
"""

import json
import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from xiaoai.four_diagnosis.reasoning.syndrome_differentiation import SyndromeDifferentiationEngine

class TestSyndromeDifferentiationEngine(unittest.TestCase):
    """辨证分析引擎测试类"""
    
    def setUp(self):
        """测试前初始化"""
        # 测试配置
        self.test_config = {
            "methods": [
                "eight_principles",
                "zang_fu",
                "qi_blood_fluid"
            ],
            "confidence_threshold": 0.6,
            "weights": {
                "looking": 1.0,
                "listening": 1.0,
                "inquiry": 1.5,
                "palpation": 1.2
            }
        }
        
        # 创建辨证引擎实例
        self.diff_engine = SyndromeDifferentiationEngine(self.test_config)
        
        # 准备测试数据
        self.prepare_test_data()
    
    def prepare_test_data(self):
        """准备测试数据"""
        # 融合后的证候数据（模拟多模态融合结果）
        self.fused_data = {
            "success": True,
            "fusion_algorithm": "weighted",
            "syndromes": [
                {
                    "name": "脾气虚",
                    "score": 0.82,
                    "confidence": 0.78,
                    "supporting_features": [
                        {"name": "舌淡", "modality": "looking", "weight": 1.0},
                        {"name": "舌苔薄白", "modality": "looking", "weight": 0.9},
                        {"name": "乏力", "modality": "inquiry", "weight": 1.5},
                        {"name": "食欲不振", "modality": "inquiry", "weight": 1.4},
                        {"name": "腹胀", "modality": "inquiry", "weight": 1.3},
                        {"name": "大便溏薄", "modality": "inquiry", "weight": 1.2},
                        {"name": "脉缓弱", "modality": "palpation", "weight": 1.1}
                    ]
                },
                {
                    "name": "肝气郁结",
                    "score": 0.65,
                    "confidence": 0.7,
                    "supporting_features": [
                        {"name": "胁肋胀痛", "modality": "inquiry", "weight": 1.4},
                        {"name": "情志不畅", "modality": "inquiry", "weight": 1.3},
                        {"name": "脉弦", "modality": "palpation", "weight": 1.1}
                    ]
                },
                {
                    "name": "气虚",
                    "score": 0.75,
                    "confidence": 0.72,
                    "supporting_features": [
                        {"name": "舌淡", "modality": "looking", "weight": 1.0},
                        {"name": "乏力", "modality": "inquiry", "weight": 1.5},
                        {"name": "气短", "modality": "inquiry", "weight": 1.4},
                        {"name": "自汗", "modality": "inquiry", "weight": 1.2},
                        {"name": "脉虚弱", "modality": "palpation", "weight": 1.1}
                    ]
                }
            ],
            "modality_weights": {
                "looking": 0.9,
                "listening": 0.8,
                "inquiry": 1.5,
                "palpation": 1.2
            }
        }
    
    def test_analyze_syndromes(self):
        """测试辨证分析"""
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(self.fused_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertIn("methods", result)
        self.assertIn("syndromes", result)
        self.assertIn("constitution", result)
        
        # 检查辨证方法
        self.assertGreater(len(result["methods"]), 0)
        
        # 检查证候结果
        self.assertGreater(len(result["syndromes"]), 0)
        
        # 检查体质分析
        self.assertIsNotNone(result["constitution"])
    
    def test_eight_principles_analysis(self):
        """测试八纲辨证"""
        # 仅启用八纲辨证
        self.diff_engine.enabled_methods = ["eight_principles"]
        
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(self.fused_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["methods"], ["eight_principles"])
        
        # 检查是否有八纲证候
        has_eight_principles = False
        for syndrome in result["syndromes"]:
            if syndrome["category"] == "八纲辨证":
                has_eight_principles = True
                break
        
        self.assertTrue(has_eight_principles, "应该有八纲辨证结果")
    
    def test_zang_fu_analysis(self):
        """测试脏腑辨证"""
        # 仅启用脏腑辨证
        self.diff_engine.enabled_methods = ["zang_fu"]
        
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(self.fused_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["methods"], ["zang_fu"])
        
        # 检查是否有脏腑证候
        has_zang_fu = False
        for syndrome in result["syndromes"]:
            if syndrome["category"] == "脏腑辨证":
                has_zang_fu = True
                break
        
        self.assertTrue(has_zang_fu, "应该有脏腑辨证结果")
    
    def test_qi_blood_fluid_analysis(self):
        """测试气血津液辨证"""
        # 仅启用气血津液辨证
        self.diff_engine.enabled_methods = ["qi_blood_fluid"]
        
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(self.fused_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["methods"], ["qi_blood_fluid"])
        
        # 检查是否有气血津液证候
        has_qi_blood_fluid = False
        for syndrome in result["syndromes"]:
            if syndrome["category"] == "气血津液辨证":
                has_qi_blood_fluid = True
                break
        
        self.assertTrue(has_qi_blood_fluid, "应该有气血津液辨证结果")
    
    def test_constitution_analysis(self):
        """测试体质分析"""
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(self.fused_data)
        
        # 验证体质结果
        constitution = result["constitution"]
        self.assertIsNotNone(constitution)
        self.assertIn("name", constitution)
        self.assertIn("score", constitution)
        self.assertIn("confidence", constitution)
        self.assertIn("traits", constitution)
        self.assertIn("recommendations", constitution)
        
        # 验证体质类型
        self.assertIn(constitution["name"], [
            "平和质", "气虚质", "阳虚质", "阴虚质", 
            "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质"
        ])
    
    def test_syndrome_consistency(self):
        """测试证候一致性验证"""
        # 添加矛盾证候
        contradictory_data = self.fused_data.copy()
        contradictory_data["syndromes"].append({
            "name": "寒证",
            "score": 0.7,
            "confidence": 0.7,
            "supporting_features": [
                {"name": "畏寒", "modality": "inquiry", "weight": 1.4},
                {"name": "肢冷", "modality": "inquiry", "weight": 1.3},
                {"name": "舌淡", "modality": "looking", "weight": 1.0},
                {"name": "脉沉紧", "modality": "palpation", "weight": 1.1}
            ]
        })
        contradictory_data["syndromes"].append({
            "name": "热证",
            "score": 0.6,
            "confidence": 0.65,
            "supporting_features": [
                {"name": "口渴", "modality": "inquiry", "weight": 1.3},
                {"name": "发热", "modality": "inquiry", "weight": 1.4},
                {"name": "舌红", "modality": "looking", "weight": 1.0},
                {"name": "脉数", "modality": "palpation", "weight": 1.1}
            ]
        })
        
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(contradictory_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        
        # 检查是否排除了矛盾证候
        has_both = True
        syndrome_names = [s["name"] for s in result["syndromes"]]
        if "寒证" in syndrome_names and "热证" in syndrome_names:
            has_both = True
        else:
            has_both = False
        
        self.assertFalse(has_both, "寒证和热证不应同时存在")
    
    def test_empty_input(self):
        """测试空输入"""
        # 准备空数据
        empty_data = {
            "success": True,
            "syndromes": []
        }
        
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(empty_data)
        
        # 验证结果
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "无证候输入数据")
    
    def test_derive_core_mechanism(self):
        """测试核心病机推导"""
        # 执行辨证分析
        result = self.diff_engine.analyze_syndromes(self.fused_data)
        
        # 验证核心病机
        self.assertIn("core_mechanism", result)
        self.assertIsInstance(result["core_mechanism"], str)
        self.assertGreater(len(result["core_mechanism"]), 0)
    
    def test_treatment_principles(self):
        """测试治疗原则推导"""
        # 从测试数据提取证候信息
        syndromes = [
            {"name": "脾气虚"},
            {"name": "肝气郁结"}
        ]
        
        # 生成治疗原则
        principles = self.diff_engine.get_treatment_principles(syndromes)
        
        # 验证结果
        self.assertIsInstance(principles, list)
        self.assertGreater(len(principles), 0)
        self.assertIn("健脾益气", principles)
        self.assertIn("疏肝理气", principles)
    
    def test_performance(self):
        """性能测试"""
        start_time = time.time()
        
        # 执行50次辨证分析
        for _ in range(50):
            self.diff_engine.analyze_syndromes(self.fused_data)
        
        elapsed_time = time.time() - start_time
        
        # 打印性能结果
        print(f"\n辨证分析性能测试: 50次分析耗时 {elapsed_time:.2f} 秒, 平均每次 {elapsed_time/50*1000:.2f} 毫秒")
        
        # 验证性能 - 平均每次应当小于100毫秒（根据实际情况调整）
        self.assertLess(elapsed_time/50, 0.1, "辨证分析性能不达标")

if __name__ == '__main__':
    unittest.main() 