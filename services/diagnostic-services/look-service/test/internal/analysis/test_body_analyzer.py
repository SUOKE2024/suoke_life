#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
形体分析器测试模块

测试body_analyzer.py中的BodyAnalyzer类及其分析方法。
"""

import os
import uuid
import base64
import unittest
from unittest.mock import patch, MagicMock

import numpy as np
from PIL import Image
import cv2

# 添加项目根目录到Python路径
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from internal.analysis.body_analyzer import BodyAnalyzer, BodyFeature, PostureAnalysis, BodyAnalysisResult
from pkg.utils.exceptions import InvalidInputError, ProcessingError


class TestBodyAnalyzer(unittest.TestCase):
    """测试BodyAnalyzer类"""

    def setUp(self):
        """测试准备：创建分析器实例和测试图像"""
        # 创建分析器配置
        self.config = {
            "models": {
                "body_analysis": {
                    "path": "./models/body_analyzer",
                    "version": "v1.0.0",
                    "batch_size": 1,
                    "device": "cpu",
                    "threshold": 0.6,
                    "input_size": [384, 384]
                }
            },
            "feature_analysis": {
                "body_shape": {
                    "enabled": True,
                    "detect_points": ["shoulders", "chest", "waist", "hips", "legs"],
                    "body_ratio_analysis": True
                }
            }
        }
        
        # 使用mock模型工厂
        self.model_factory_mock = MagicMock()
        self.model_mock = MagicMock()
        self.model_factory_mock.get_body_model.return_value = self.model_mock
        
        # 创建分析器实例
        self.analyzer = BodyAnalyzer(self.config, self.model_factory_mock)
        
        # 创建测试图像 (100x200 像素的模拟人体图像)
        self.test_image = np.zeros((200, 100, 3), dtype=np.uint8)
        # 添加简单的人体轮廓 (头、身体、腿)
        cv2.circle(self.test_image, (50, 40), 20, (255, 200, 150), -1)  # 头部
        cv2.rectangle(self.test_image, (30, 60), (70, 120), (255, 200, 150), -1)  # 身体
        cv2.rectangle(self.test_image, (35, 120), (55, 190), (255, 200, 150), -1)  # 左腿
        cv2.rectangle(self.test_image, (55, 120), (75, 190), (255, 200, 150), -1)  # 右腿
        
        # 编码为二进制
        _, self.test_image_binary = cv2.imencode('.jpg', self.test_image)
        self.test_image_bytes = self.test_image_binary.tobytes()
        
        # 用户ID
        self.test_user_id = "test-user-123"

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.analyzer.threshold, 0.6)
        self.assertEqual(self.analyzer.input_size, [384, 384])
        self.assertTrue(self.analyzer.enabled)
        self.assertEqual(self.analyzer.detect_points, ["shoulders", "chest", "waist", "hips", "legs"])
        self.assertTrue(self.analyzer.body_ratio_analysis)
        
    def test_preprocess_image(self):
        """测试图像预处理"""
        processed = self.analyzer._preprocess_image(self.test_image)
        self.assertEqual(processed.shape[0], 384)  # 高度应该是384
        self.assertEqual(processed.shape[1], 384)  # 宽度应该是384
        self.assertEqual(processed.shape[2], 3)    # 通道数应该是3

    def test_analyze_with_valid_image(self):
        """测试使用有效图像进行分析"""
        # 设置模型的模拟返回值
        self.model_mock.predict.return_value = {
            "body_type": "均匀型",
            "keypoints": {
                "shoulders": {"x": 0.5, "y": 0.2, "confidence": 0.95},
                "chest": {"x": 0.5, "y": 0.3, "confidence": 0.93},
                "waist": {"x": 0.5, "y": 0.4, "confidence": 0.92},
                "hips": {"x": 0.5, "y": 0.5, "confidence": 0.94},
                "legs": {"x": 0.5, "y": 0.8, "confidence": 0.91}
            },
            "posture": [
                {"aspect": "肩部", "status": "正常", "confidence": 0.89},
                {"aspect": "脊柱", "status": "正直", "confidence": 0.92},
                {"aspect": "腰胯", "status": "平衡", "confidence": 0.87}
            ],
            "features": [
                {"name": "肩宽", "value": "中等", "confidence": 0.91},
                {"name": "胸腰比", "value": "协调", "confidence": 0.88},
                {"name": "下肢长度", "value": "适中", "confidence": 0.90}
            ],
            "tcm_constitution": [
                {"type": "平和质", "confidence": 0.75, "description": "体型匀称，肌肉适中"}
            ]
        }
        
        # 执行分析
        result = self.analyzer.analyze(self.test_image_bytes, self.test_user_id)
        
        # 验证结果
        self.assertIsInstance(result, BodyAnalysisResult)
        self.assertEqual(result.body_type, "均匀型")
        self.assertEqual(len(result.features), 3)
        self.assertEqual(result.features[0].feature_name, "肩宽")
        self.assertEqual(result.features[0].value, "中等")
        self.assertAlmostEqual(result.features[0].confidence, 0.91)
        
        self.assertEqual(len(result.posture), 3)
        self.assertEqual(result.posture[0].posture_aspect, "肩部")
        self.assertEqual(result.posture[0].status, "正常")
        
        self.assertEqual(len(result.body_constitution), 1)
        self.assertEqual(result.body_constitution[0].constitution_type, "平和质")
        self.assertAlmostEqual(result.body_constitution[0].confidence, 0.75)

    def test_analyze_with_invalid_image(self):
        """测试使用无效图像进行分析"""
        # 准备无效图像
        invalid_image = b"not an image"
        
        # 验证是否抛出异常
        with self.assertRaises(InvalidInputError):
            self.analyzer.analyze(invalid_image, self.test_user_id)

    def test_analyze_with_empty_image(self):
        """测试使用空图像进行分析"""
        # 验证是否抛出异常
        with self.assertRaises(InvalidInputError):
            self.analyzer.analyze(b"", self.test_user_id)

    def test_analyze_with_model_error(self):
        """测试模型错误处理"""
        # 设置模型抛出异常
        self.model_mock.predict.side_effect = Exception("Model prediction failed")
        
        # 验证是否抛出处理异常
        with self.assertRaises(ProcessingError):
            self.analyzer.analyze(self.test_image_bytes, self.test_user_id)

    def test_generate_body_analysis_summary(self):
        """测试生成体态分析总结"""
        # 创建模拟分析结果
        features = [
            BodyFeature(feature_name="肩宽", value="宽阔", confidence=0.9),
            BodyFeature(feature_name="胸腰比", value="匀称", confidence=0.85)
        ]
        
        posture = [
            PostureAnalysis(posture_aspect="站姿", status="挺拔", confidence=0.88, suggestion="保持良好"),
            PostureAnalysis(posture_aspect="脊柱", status="偏左", confidence=0.75, suggestion="注意调整")
        ]
        
        # 生成总结
        summary = self.analyzer._generate_body_analysis_summary("壮实型", features, posture)
        
        # 验证总结
        self.assertIn("壮实型", summary)
        self.assertIn("肩宽", summary)
        self.assertIn("宽阔", summary)
        self.assertIn("胸腰比", summary)
        self.assertIn("匀称", summary)
        self.assertIn("站姿", summary)
        self.assertIn("脊柱", summary)
        self.assertIn("偏左", summary)


if __name__ == '__main__':
    unittest.main() 