#!/usr/bin/env python3
"""
多模态融合引擎测试
"""

import json
import sys
import time
import unittest
from pathlib import Path

# 将项目根目录添加到Python路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from xiaoai.four_diagnosis.fusion.multimodal_fusion import (
    ModalityFeature,
    MultimodalFusionEngine,
)


class TestMultimodalFusionEngine(unittest.TestCase):
    """多模态融合引擎测试类"""

    def setUp(self):
        """测试前初始化"""
        # 测试配置
        self.test_config = {
            "algorithm": "weighted",
            "confidence_threshold": 0.6,
            "weights": {
                "looking": 1.0,
                "listening": 1.0,
                "inquiry": 1.5,
                "palpation": 1.2
            }
        }

        self.fusion_engine = MultimodalFusionEngine(self.test_config)

        # 准备测试数据
        self.prepare_test_data()

    def prepare_test_data(self):
        """准备测试数据"""
        # 望诊数据
        self.looking_data = {
            "type": "LOOKING",
            "diagnosis_id": "look-12345",
            "source_service": "look-service",
            "confidence": 0.85,
            "features": [
                {
                    "name": "舌淡红",
                    "value": 0.8,
                    "confidence": 0.85,
                    "category": "tongue_color"
                },
                {
                    "name": "舌苔薄白",
                    "value": 0.75,
                    "confidence": 0.8,
                    "category": "tongue_coating"
                },
                {
                    "name": "脸色偏白",
                    "value": 0.65,
                    "confidence": 0.7,
                    "category": "face_color"
                }
            ],
            "detailed_result": json.dumps({"tongue_color": "pale_red"}),
            "timestamp": int(time.time())
        }

        # 闻诊数据
        self.listening_data = {
            "type": "LISTENING",
            "diagnosis_id": "listen-12345",
            "source_service": "listen-service",
            "confidence": 0.8,
            "features": [
                {
                    "name": "声音低弱",
                    "value": 0.7,
                    "confidence": 0.75,
                    "category": "voice_strength"
                },
                {
                    "name": "语速缓慢",
                    "value": 0.65,
                    "confidence": 0.7,
                    "category": "speech_rate"
                }
            ],
            "detailed_result": json.dumps({"voice_analysis": "weak"}),
            "timestamp": int(time.time())
        }

        # 问诊数据
        self.inquiry_data = {
            "type": "INQUIRY",
            "diagnosis_id": "inquiry-12345",
            "source_service": "inquiry-service",
            "confidence": 0.9,
            "features": [
                {
                    "name": "乏力",
                    "value": 0.85,
                    "confidence": 0.9,
                    "category": "symptoms"
                },
                {
                    "name": "食欲不振",
                    "value": 0.8,
                    "confidence": 0.85,
                    "category": "symptoms"
                },
                {
                    "name": "腹胀",
                    "value": 0.75,
                    "confidence": 0.8,
                    "category": "symptoms"
                },
                {
                    "name": "大便溏薄",
                    "value": 0.7,
                    "confidence": 0.75,
                    "category": "symptoms"
                }
            ],
            "detailed_result": json.dumps({"chief_complaint": "乏力,食欲不振"}),
            "timestamp": int(time.time())
        }

        # 切诊数据
        self.palpation_data = {
            "type": "PALPATION",
            "diagnosis_id": "palpation-12345",
            "source_service": "palpation-service",
            "confidence": 0.75,
            "features": [
                {
                    "name": "脉缓弱",
                    "value": 0.7,
                    "confidence": 0.75,
                    "category": "pulse"
                }
            ],
            "detailed_result": json.dumps({"pulse_type": "slow_weak"}),
            "timestamp": int(time.time())
        }

        # 组合所有诊断数据
        self.diagnosis_results = [
            self.looking_data,
            self.listening_data,
            self.inquiry_data,
            self.palpation_data
        ]

    def test_fusion_weighted(self):
        """测试加权融合算法"""
        self.fusion_engine.fusion_algorithm = "weighted"

        result = self.fusion_engine.fuse_diagnosis_data(self.diagnosis_results)

        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["fusion_algorithm"], "weighted")
        self.assertIsInstance(result["syndromes"], list)
        self.assertGreater(len(result["syndromes"]), 0)
        self.assertGreater(result["confidence"], 0.5)

        # 检查是否有脾气虚证候(根据测试数据应该出现)
        has_spleen_qi_deficiency = False
        for syndrome in result["syndromes"]:
            if syndrome["name"] == "脾气虚":
                has_spleen_qi_deficiency = True
                break

        self.assertTrue(has_spleen_qi_deficiency, "应该识别出脾气虚证候")

    def test_fusion_attention(self):
        """测试注意力机制融合算法"""
        self.fusion_engine.fusion_algorithm = "attention"

        result = self.fusion_engine.fuse_diagnosis_data(self.diagnosis_results)

        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["fusion_algorithm"], "attention")
        self.assertIsInstance(result["syndromes"], list)
        self.assertGreater(len(result["syndromes"]), 0)
        self.assertGreater(result["confidence"], 0.5)

    def test_fusion_ensemble(self):
        """测试集成融合算法"""
        self.fusion_engine.fusion_algorithm = "ensemble"

        result = self.fusion_engine.fuse_diagnosis_data(self.diagnosis_results)

        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["fusion_algorithm"], "ensemble")
        self.assertIsInstance(result["syndromes"], list)
        self.assertGreater(len(result["syndromes"]), 0)
        self.assertGreater(result["confidence"], 0.5)

    def test_fusion_cross_modal(self):
        """测试跨模态融合算法"""
        self.fusion_engine.fusion_algorithm = "cross_modal"

        result = self.fusion_engine.fuse_diagnosis_data(self.diagnosis_results)

        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["fusion_algorithm"], "cross_modal")
        self.assertIsInstance(result["syndromes"], list)
        self.assertGreater(len(result["syndromes"]), 0)
        self.assertGreater(result["confidence"], 0.5)

    def test_empty_input(self):
        """测试空输入"""
        result = self.fusion_engine.fuse_diagnosis_data([])

        # 验证结果
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "无输入数据")

    def test_modality_weights_adjustment(self):
        """测试模态权重调整"""
        # 修改一个模态的置信度
        low_confidence_data = self.looking_data.copy()
        low_confidence_data["confidence"] = 0.4

        modified_results = [
            low_confidence_data,
            self.listening_data,
            self.inquiry_data,
            self.palpation_data
        ]

        result = self.fusion_engine.fuse_diagnosis_data(modified_results)

        # 验证结果
        self.assertTrue(result["success"])

        weights = result["modality_weights"]
        self.assertLess(weights["looking"], weights["inquiry"])

    def test_feature_extraction(self):
        """测试特征提取"""
        features = self.fusion_engine._extract_features(self.diagnosis_results)

        # 验证提取的特征
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)

        # 检查所有特征是否都是ModalityFeature类型
        for feature in features:
            self.assertIsInstance(feature, ModalityFeature)

    def test_performance(self):
        """性能测试"""
        start_time = time.time()

        for _ in range(100):
            self.fusion_engine.fuse_diagnosis_data(self.diagnosis_results)

        elapsed_time = time.time() - start_time

        # 打印性能结果
        print(f"\n融合性能测试: 100次融合耗时 {elapsed_time:.2f} 秒, 平均每次 {elapsed_time/100*1000:.2f} 毫秒")

        self.assertLess(elapsed_time/100, 0.05, "融合性能不达标")

if __name__ == '__main__':
    unittest.main()
