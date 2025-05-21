#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康建议生成器单元测试
"""

import json
import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.four_diagnosis.recommendation.health_advisor import HealthAdvisor

class TestHealthAdvisor(unittest.TestCase):
    """健康建议生成器测试类"""
    
    def setUp(self):
        """测试前初始化"""
        # 测试配置
        self.test_config = {
            "max_recommendations": 10,
            "min_confidence": 0.6,
            "category_limits": {
                "diet": 3,
                "lifestyle": 2,
                "exercise": 2,
                "emotion": 2,
                "acupoint": 1,
                "prevention": 1,
                "medical": 1
            }
        }
        
        # 创建健康建议生成器实例
        self.advisor = HealthAdvisor(self.test_config)
        
        # 准备测试数据
        self.prepare_test_data()
    
    def prepare_test_data(self):
        """准备测试数据"""
        # 辨证分析结果数据
        self.diagnosis_data = {
            "success": True,
            "methods": ["eight_principles", "zang_fu", "qi_blood_fluid"],
            "syndromes": [
                {
                    "name": "脾气虚",
                    "score": 0.82,
                    "confidence": 0.78,
                    "category": "脏腑辨证",
                    "mechanism": "脾失健运",
                    "evidences": [
                        {"feature": "舌淡", "modality": "looking", "confidence": 0.85, "weight": 1.0},
                        {"feature": "乏力", "modality": "inquiry", "confidence": 0.9, "weight": 1.5},
                        {"feature": "食欲不振", "modality": "inquiry", "confidence": 0.85, "weight": 1.4},
                        {"feature": "腹胀", "modality": "inquiry", "confidence": 0.8, "weight": 1.3},
                        {"feature": "大便溏薄", "modality": "inquiry", "confidence": 0.75, "weight": 1.2}
                    ]
                },
                {
                    "name": "气虚",
                    "score": 0.75,
                    "confidence": 0.72,
                    "category": "气血津液辨证",
                    "mechanism": "气的生成不足或过度消耗",
                    "evidences": [
                        {"feature": "乏力", "modality": "inquiry", "confidence": 0.9, "weight": 1.5},
                        {"feature": "气短", "modality": "inquiry", "confidence": 0.85, "weight": 1.4},
                        {"feature": "自汗", "modality": "inquiry", "confidence": 0.8, "weight": 1.2}
                    ]
                }
            ],
            "constitution": {
                "name": "气虚质",
                "score": 0.8,
                "confidence": 0.75,
                "traits": [
                    {"name": "疲乏无力"},
                    {"name": "气短自汗"},
                    {"name": "语声低弱"},
                    {"name": "易感冒"},
                    {"name": "舌淡"}
                ],
                "recommendations": [
                    "健脾益气",
                    "适当休息",
                    "饮食规律",
                    "温和运动",
                    "避免过劳"
                ]
            },
            "core_mechanism": "脾失健运，气的生成不足或过度消耗"
        }
        
        # 肝郁证候数据
        self.liver_stagnation_data = {
            "success": True,
            "methods": ["eight_principles", "zang_fu", "qi_blood_fluid"],
            "syndromes": [
                {
                    "name": "肝气郁结",
                    "score": 0.8,
                    "confidence": 0.75,
                    "category": "脏腑辨证",
                    "mechanism": "肝失疏泄，气机郁滞",
                    "evidences": [
                        {"feature": "胁肋胀痛", "modality": "inquiry", "confidence": 0.8, "weight": 1.4},
                        {"feature": "情志不畅", "modality": "inquiry", "confidence": 0.85, "weight": 1.3},
                        {"feature": "善太息", "modality": "inquiry", "confidence": 0.75, "weight": 1.2}
                    ]
                },
                {
                    "name": "气滞",
                    "score": 0.7,
                    "confidence": 0.7,
                    "category": "气血津液辨证",
                    "mechanism": "气机不畅",
                    "evidences": [
                        {"feature": "胀痛", "modality": "inquiry", "confidence": 0.75, "weight": 1.3},
                        {"feature": "情志不畅", "modality": "inquiry", "confidence": 0.85, "weight": 1.4}
                    ]
                }
            ],
            "constitution": {
                "name": "气郁质",
                "score": 0.78,
                "confidence": 0.72,
                "traits": [
                    {"name": "情绪抑郁"},
                    {"name": "善太息"},
                    {"name": "胸胁胀痛"},
                    {"name": "性格内向"},
                    {"name": "郁郁寡欢"}
                ],
                "recommendations": [
                    "疏肝解郁",
                    "调节情绪",
                    "参加社交",
                    "适当运动",
                    "规律作息"
                ]
            },
            "core_mechanism": "肝失疏泄，气机郁滞"
        }
        
        # 脾胃湿热数据
        self.dampness_heat_data = {
            "success": True,
            "methods": ["eight_principles", "zang_fu", "qi_blood_fluid"],
            "syndromes": [
                {
                    "name": "脾胃湿热",
                    "score": 0.85,
                    "confidence": 0.8,
                    "category": "脏腑辨证",
                    "mechanism": "湿热内蕴脾胃",
                    "evidences": [
                        {"feature": "腹痛", "modality": "inquiry", "confidence": 0.85, "weight": 1.4},
                        {"feature": "口苦", "modality": "inquiry", "confidence": 0.8, "weight": 1.3},
                        {"feature": "口干", "modality": "inquiry", "confidence": 0.75, "weight": 1.2},
                        {"feature": "舌苔黄腻", "modality": "looking", "confidence": 0.9, "weight": 1.5}
                    ]
                }
            ],
            "constitution": {
                "name": "湿热质",
                "score": 0.82,
                "confidence": 0.78,
                "traits": [
                    {"name": "面垢油光"},
                    {"name": "易生痤疮"},
                    {"name": "口苦口臭"},
                    {"name": "大便黏滞"},
                    {"name": "尿黄"}
                ],
                "recommendations": [
                    "清热利湿",
                    "少食辛辣",
                    "保持通畅",
                    "心情舒畅",
                    "饮食清淡"
                ]
            },
            "core_mechanism": "湿热内蕴脾胃"
        }
    
    def test_generate_recommendations(self):
        """测试生成健康建议"""
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(self.diagnosis_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertIn("recommendations", result)
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
        self.assertLessEqual(len(result["recommendations"]), self.test_config["max_recommendations"])
        self.assertIn("processing_time_ms", result)
    
    def test_diet_recommendations(self):
        """测试饮食建议生成"""
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(self.diagnosis_data)
        
        # 查找饮食建议
        diet_recommendations = [r for r in result["recommendations"] if r["category"] == self.advisor.CATEGORY_DIET]
        
        # 验证结果
        self.assertGreater(len(diet_recommendations), 0)
        self.assertLessEqual(len(diet_recommendations), self.test_config["category_limits"]["diet"])
        
        # 检查是否有针对脾气虚的饮食建议
        has_spleen_diet = False
        for rec in diet_recommendations:
            if "山药" in rec["content"] or "大枣" in rec["content"] or "小米" in rec["content"]:
                has_spleen_diet = True
                break
        
        self.assertTrue(has_spleen_diet, "应该有针对脾气虚的饮食建议")
    
    def test_exercise_recommendations(self):
        """测试运动建议生成"""
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(self.diagnosis_data)
        
        # 查找运动建议
        exercise_recommendations = [r for r in result["recommendations"] if r["category"] == self.advisor.CATEGORY_EXERCISE]
        
        # 验证结果
        self.assertGreater(len(exercise_recommendations), 0)
        self.assertLessEqual(len(exercise_recommendations), self.test_config["category_limits"]["exercise"])
        
        # 检查是否有针对气虚的运动建议
        has_qi_exercise = False
        for rec in exercise_recommendations:
            if "缓和的运动" in rec["content"] or "太极" in rec["content"] or "八段锦" in rec["content"]:
                has_qi_exercise = True
                break
        
        self.assertTrue(has_qi_exercise, "应该有针对气虚的运动建议")
    
    def test_liver_stagnation_recommendations(self):
        """测试肝郁证候的健康建议"""
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(self.liver_stagnation_data)
        
        # 查找情志调养建议
        emotion_recommendations = [r for r in result["recommendations"] if r["category"] == self.advisor.CATEGORY_EMOTION]
        
        # 验证结果
        self.assertGreater(len(emotion_recommendations), 0)
        
        # 检查是否有针对肝郁的情志建议
        has_liver_emotion = False
        for rec in emotion_recommendations:
            if "情绪" in rec["content"] or "舒畅" in rec["content"]:
                has_liver_emotion = True
                break
        
        self.assertTrue(has_liver_emotion, "应该有针对肝郁的情志建议")
    
    def test_dampness_heat_recommendations(self):
        """测试脾胃湿热的健康建议"""
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(self.dampness_heat_data)
        
        # 查找饮食建议
        diet_recommendations = [r for r in result["recommendations"] if r["category"] == self.advisor.CATEGORY_DIET]
        
        # 验证结果
        self.assertGreater(len(diet_recommendations), 0)
        
        # 检查是否有针对脾胃湿热的饮食建议
        has_dampness_heat_diet = False
        for rec in diet_recommendations:
            if "清淡" in rec["content"] or "利湿" in rec["content"] or "薏米" in rec["content"]:
                has_dampness_heat_diet = True
                break
        
        self.assertTrue(has_dampness_heat_diet, "应该有针对脾胃湿热的饮食建议")
    
    def test_acupoint_recommendations(self):
        """测试穴位保健建议"""
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(self.liver_stagnation_data)
        
        # 查找穴位保健建议
        acupoint_recommendations = [r for r in result["recommendations"] if r["category"] == self.advisor.CATEGORY_ACUPOINT]
        
        # 验证结果
        self.assertLessEqual(len(acupoint_recommendations), self.test_config["category_limits"]["acupoint"])
        
        # 如果有穴位建议，检查是否有针对肝郁的穴位
        if acupoint_recommendations:
            has_liver_acupoint = False
            for rec in acupoint_recommendations:
                if "太冲" in rec["content"]:
                    has_liver_acupoint = True
                    break
            
            self.assertTrue(has_liver_acupoint, "应该有针对肝郁的穴位建议")
    
    def test_general_recommendations(self):
        """测试通用健康建议"""
        # 获取通用建议
        general_recs = self.advisor._generate_general_recommendations()
        
        # 验证结果
        self.assertTrue(general_recs["success"])
        self.assertIsInstance(general_recs["recommendations"], list)
        self.assertGreater(len(general_recs["recommendations"]), 0)
    
    def test_empty_input(self):
        """测试空输入"""
        # 准备空数据
        empty_data = {
            "success": True
        }
        
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(empty_data)
        
        # 验证是否返回通用建议
        self.assertTrue(result["success"])
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
    
    def test_recommendation_priority(self):
        """测试建议优先级排序"""
        # 执行健康建议生成
        result = self.advisor.generate_recommendations(self.diagnosis_data)
        
        # 验证建议按优先级排序
        recommendations = result["recommendations"]
        for i in range(len(recommendations) - 1):
            self.assertGreaterEqual(
                recommendations[i]["priority"],
                recommendations[i+1]["priority"],
                "建议应按优先级降序排列"
            )
    
    def test_targeted_recommendations(self):
        """测试针对性建议生成"""
        # 提取证候和体质
        syndrome_names = [s["name"] for s in self.diagnosis_data["syndromes"]]
        constitution_name = self.diagnosis_data["constitution"]["name"]
        
        # 生成针对性建议
        result = self.advisor._generate_targeted_recommendations(syndrome_names, constitution_name)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)
        
        # 检查每个建议是否包含必要字段
        for rec in result["recommendations"]:
            self.assertIn("category", rec)
            self.assertIn("content", rec)
            self.assertIn("priority", rec)
            self.assertIn("evidence", rec)
    
    def test_performance(self):
        """性能测试"""
        start_time = time.time()
        
        # 执行100次健康建议生成
        for _ in range(100):
            self.advisor.generate_recommendations(self.diagnosis_data)
        
        elapsed_time = time.time() - start_time
        
        # 打印性能结果
        print(f"\n健康建议生成性能测试: 100次生成耗时 {elapsed_time:.2f} 秒, 平均每次 {elapsed_time/100*1000:.2f} 毫秒")
        
        # 验证性能 - 平均每次应当小于30毫秒（根据实际情况调整）
        self.assertLess(elapsed_time/100, 0.03, "健康建议生成性能不达标")

if __name__ == '__main__':
    unittest.main() 