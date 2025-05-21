#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
面色分析器单元测试
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.analysis.face_analyzer import FaceAnalyzer, FaceColor, SkinMoisture, FaceFeatures


class TestFaceAnalyzer(unittest.TestCase):
    """面色分析器测试类"""

    def setUp(self):
        """测试设置"""
        # 创建面色分析器实例
        self.analyzer = FaceAnalyzer()
        
        # 创建测试图像
        self.test_image = self._create_test_image()
    
    def _create_test_image(self):
        """创建测试图像数据"""
        # 创建一个简单的100x100的彩色图像
        img = np.ones((100, 100, 3), dtype=np.uint8) * 200  # 浅灰色背景
        
        # 添加一个简单的面部图形（椭圆）
        cv2.ellipse(img, (50, 50), (30, 40), 0, 0, 360, (210, 170, 150), -1)  # 面部肤色
        
        # 添加眼睛
        cv2.circle(img, (35, 40), 5, (50, 50, 50), -1)  # 左眼
        cv2.circle(img, (65, 40), 5, (50, 50, 50), -1)  # 右眼
        
        # 添加嘴巴
        cv2.ellipse(img, (50, 65), (20, 10), 0, 0, 180, (150, 90, 90), 2)
        
        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    
    @patch('internal.model.model_factory.ModelFactory.get_model')
    def test_analyze_basic(self, mock_get_model):
        """测试基本分析功能"""
        # 模拟模型返回值
        mock_model = MagicMock()
        mock_model.predict.return_value = {
            "face_detected": True,
            "face_landmarks": {
                "left_eye": [(35, 40)],
                "right_eye": [(65, 40)],
                "nose": [(50, 50)],
                "mouth": [(50, 65)],
                "jaw": [(30, 80), (70, 80)]
            },
            "face_color": {
                "forehead": [210, 170, 150],
                "cheeks": [220, 175, 160],
                "nose": [215, 165, 155],
                "chin": [205, 168, 152]
            },
            "skin_analysis": {
                "moisture": "normal",
                "texture": "smooth",
                "pores": "minimal"
            }
        }
        mock_get_model.return_value = mock_model
        
        # 执行分析
        result = self.analyzer.analyze(self.test_image, user_id="test_user_1")
        
        # 验证结果
        self.assertEqual(result.user_id, "test_user_1")
        self.assertIsNotNone(result.image_id)
        self.assertIsNotNone(result.timestamp)
        self.assertIsNotNone(result.features)
        self.assertIn(result.features.face_color, list(FaceColor))
        self.assertIn(result.features.skin_moisture, list(SkinMoisture))
        self.assertGreater(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertIsNotNone(result.tcm_analysis)
        self.assertIn("constitution_tendency", result.tcm_analysis.get("summary", {}))
    
    def test_analyze_invalid_image(self):
        """测试无效图像"""
        from pkg.utils.exceptions import InvalidInputError
        
        # 创建无效的图像数据
        invalid_image = b"This is not an image data"
        
        # 验证是否抛出异常
        with self.assertRaises(InvalidInputError):
            self.analyzer.analyze(invalid_image, user_id="test_user_1")
    
    @patch('internal.model.model_factory.ModelFactory.get_model')
    def test_analyze_no_face(self, mock_get_model):
        """测试没有检测到人脸的情况"""
        from pkg.utils.exceptions import InvalidInputError
        
        # 模拟模型返回没有检测到人脸
        mock_model = MagicMock()
        mock_model.predict.return_value = {
            "face_detected": False
        }
        mock_get_model.return_value = mock_model
        
        # 验证是否抛出异常
        with self.assertRaises(InvalidInputError):
            self.analyzer.analyze(self.test_image, user_id="test_user_1")
    
    @patch('internal.model.model_factory.ModelFactory.get_model')
    def test_analyze_model_error(self, mock_get_model):
        """测试模型错误处理"""
        from pkg.utils.exceptions import ProcessingError
        
        # 模拟模型抛出异常
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Model prediction failed")
        mock_get_model.return_value = mock_model
        
        # 验证是否抛出异常
        with self.assertRaises(ProcessingError):
            self.analyzer.analyze(self.test_image, user_id="test_user_1")
    
    @patch('internal.model.model_factory.ModelFactory.get_model')
    def test_different_face_colors(self, mock_get_model):
        """测试不同面色类型"""
        mock_model = MagicMock()
        
        # 测试不同面色类型
        face_colors = {
            FaceColor.NORMAL: {"forehead": [210, 170, 150], "cheeks": [220, 175, 160]},
            FaceColor.RED: {"forehead": [230, 120, 120], "cheeks": [240, 130, 130]},
            FaceColor.PALE: {"forehead": [200, 200, 200], "cheeks": [210, 210, 210]},
            FaceColor.YELLOW: {"forehead": [230, 190, 110], "cheeks": [240, 200, 120]},
            FaceColor.DARK: {"forehead": [120, 110, 100], "cheeks": [130, 120, 110]},
            FaceColor.CYAN: {"forehead": [150, 190, 180], "cheeks": [160, 200, 190]}
        }
        
        for expected_color, color_values in face_colors.items():
            # 模拟模型返回特定面色
            mock_model.predict.return_value = {
                "face_detected": True,
                "face_landmarks": {
                    "left_eye": [(35, 40)],
                    "right_eye": [(65, 40)],
                    "nose": [(50, 50)],
                    "mouth": [(50, 65)]
                },
                "face_color": {
                    "forehead": color_values["forehead"],
                    "cheeks": color_values["cheeks"],
                    "nose": color_values["forehead"],
                    "chin": color_values["cheeks"]
                },
                "skin_analysis": {
                    "moisture": "normal",
                    "texture": "smooth"
                }
            }
            mock_get_model.return_value = mock_model
            
            # 执行分析
            result = self.analyzer.analyze(self.test_image, user_id="test_user_1")
            
            # 验证结果
            self.assertEqual(result.features.face_color, expected_color, 
                           f"Expected {expected_color} but got {result.features.face_color}")
    
    @patch('internal.model.model_factory.ModelFactory.get_model')
    def test_tcm_analysis_consistency(self, mock_get_model):
        """测试中医分析结果的一致性"""
        # 模拟模型返回值
        mock_model = MagicMock()
        mock_model.predict.return_value = {
            "face_detected": True,
            "face_landmarks": {
                "left_eye": [(35, 40)],
                "right_eye": [(65, 40)],
                "nose": [(50, 50)],
                "mouth": [(50, 65)]
            },
            "face_color": {
                "forehead": [230, 120, 120],  # 红色
                "cheeks": [240, 130, 130],
                "nose": [230, 125, 125],
                "chin": [225, 120, 120]
            },
            "skin_analysis": {
                "moisture": "dry",
                "texture": "rough"
            }
        }
        mock_get_model.return_value = mock_model
        
        # 执行分析
        result1 = self.analyzer.analyze(self.test_image, user_id="test_user_1")
        
        # 再次执行相同的分析
        result2 = self.analyzer.analyze(self.test_image, user_id="test_user_1")
        
        # 验证中医分析的一致性（对于相同的面色特征应该产生一致的中医分析）
        self.assertEqual(result1.features.face_color, result2.features.face_color)
        self.assertEqual(result1.features.skin_moisture, result2.features.skin_moisture)
        
        # 检查中医分析的关键部分是否一致
        self.assertEqual(
            result1.tcm_analysis["summary"]["constitution_tendency"],
            result2.tcm_analysis["summary"]["constitution_tendency"]
        )
    
    def test_generate_annotated_image(self):
        """测试是否生成标注图像"""
        # 执行分析
        result = self.analyzer.analyze(self.test_image, user_id="test_user_1")
        
        # 验证是否生成了标注图像
        self.assertIsNotNone(result.annotated_image)
        
        # 验证标注图像是否为有效的图像数据
        try:
            np_arr = np.frombuffer(result.annotated_image, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            self.assertIsNotNone(img)
            self.assertTrue(img.shape[0] > 0 and img.shape[1] > 0)
        except Exception as e:
            self.fail(f"标注图像无效: {str(e)}")


if __name__ == "__main__":
    unittest.main() 