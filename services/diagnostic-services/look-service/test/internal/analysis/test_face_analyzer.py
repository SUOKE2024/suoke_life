import unittest
import cv2
import numpy as np
import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from internal.analysis.face_analyzer import FaceAnalyzer
from internal.model.model_factory import ModelFactory


class TestFaceAnalyzer(unittest.TestCase):
    """面色分析器单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 模拟配置
        self.config = {
            'models': {
                'face_detection': {
                    'path': 'models/face_detection.onnx',
                    'input_size': [416, 416],
                    'confidence_threshold': 0.85
                },
                'face_landmarks': {
                    'path': 'models/face_landmarks.onnx',
                    'input_size': [192, 192]
                },
                'face_color': {
                    'path': 'models/face_color.onnx',
                    'input_size': [224, 224],
                    'classes': ['yellow', 'red', 'pale', 'blue', 'normal']
                },
                'skin_segmentation': {
                    'path': 'models/skin_segmentation.onnx',
                    'input_size': [256, 256]
                }
            },
            'face_regions': {
                'forehead': {'organ': '脾胃', 'description': '额头对应脾胃功能状态'},
                'nose': {'organ': '心', 'description': '鼻部对应心功能状态'},
                'left_cheek': {'organ': '肝', 'description': '左颊对应肝功能状态'},
                'right_cheek': {'organ': '肺', 'description': '右颊对应肺功能状态'},
                'chin': {'organ': '肾', 'description': '下巴对应肾功能状态'}
            }
        }
        
        # 使用模拟的ModelFactory
        with patch('internal.model.model_factory.ModelFactory') as MockModelFactory:
            self.mock_model_factory = MockModelFactory.return_value
            self.mock_model_factory.get_model.return_value = MagicMock()
            self.analyzer = FaceAnalyzer(self.config, model_factory=self.mock_model_factory)

    def test_preprocess_image(self):
        """测试图像预处理功能"""
        # 创建一个测试图像
        test_image = np.ones((300, 400, 3), dtype=np.uint8) * 255
        
        # 调用预处理方法
        processed_img = self.analyzer._preprocess_image(test_image, target_size=(416, 416))
        
        # 验证图像尺寸和数据类型
        self.assertEqual(processed_img.shape, (416, 416, 3))
        self.assertEqual(processed_img.dtype, np.float32)
        
    def test_detect_face(self):
        """测试人脸检测功能"""
        # 创建测试图像
        test_image = np.ones((416, 416, 3), dtype=np.uint8) * 255
        
        # 模拟人脸检测模型输出，返回边界框 [x, y, width, height, confidence]
        mock_detection = np.array([[100, 100, 200, 200, 0.98]])
        self.mock_model_factory.get_model().predict.return_value = mock_detection
        
        # 调用人脸检测方法
        faces = self.analyzer._detect_face(test_image)
        
        # 验证检测结果
        self.assertEqual(len(faces), 1)
        face = faces[0]
        self.assertEqual(face[0], 100)  # x
        self.assertEqual(face[1], 100)  # y
        self.assertEqual(face[2], 200)  # width
        self.assertEqual(face[3], 200)  # height
        self.assertEqual(face[4], 0.98)  # confidence
        
    def test_extract_landmarks(self):
        """测试人脸关键点提取功能"""
        # 创建测试人脸图像
        face_image = np.ones((192, 192, 3), dtype=np.uint8) * 200
        
        # 模拟关键点模型输出 (68个关键点, 每个关键点有x,y坐标)
        mock_landmarks = np.random.rand(68, 2)
        self.mock_model_factory.get_model().predict.return_value = mock_landmarks
        
        # 调用关键点提取方法
        landmarks = self.analyzer._extract_landmarks(face_image)
        
        # 验证提取结果
        self.assertEqual(landmarks.shape, (68, 2))
        
    def test_analyze_face_color(self):
        """测试面色分析功能"""
        # 创建测试人脸图像
        face_image = np.ones((224, 224, 3), dtype=np.uint8) * 180
        
        # 模拟面色分析模型输出 (颜色类别概率)
        mock_color_prediction = np.array([0.1, 0.05, 0.05, 0.1, 0.7])  # normal概率最高
        self.mock_model_factory.get_model().predict.return_value = mock_color_prediction
        
        # 调用面色分析方法
        color, confidence = self.analyzer._analyze_face_color(face_image)
        
        # 验证分析结果
        self.assertEqual(color, 'normal')
        self.assertEqual(confidence, 0.7)
        
    def test_analyze_face_regions(self):
        """测试面部区域分析功能"""
        # 创建测试人脸图像和人脸关键点
        face_image = np.ones((256, 256, 3), dtype=np.uint8) * 180
        landmarks = np.random.rand(68, 2) * 200 + 28  # 确保关键点在图像范围内
        
        # 模拟区域颜色预测 (各区域预测结果不同)
        def mock_predict_side_effect(img):
            # 基于输入图像的内容返回不同的预测结果
            if np.mean(img) > 170:  # 额头区域
                return np.array([0.7, 0.1, 0.1, 0.05, 0.05])  # yellow概率最高
            elif np.mean(img) > 160:  # 鼻子区域
                return np.array([0.1, 0.6, 0.1, 0.1, 0.1])  # red概率最高
            else:  # 其他区域
                return np.array([0.1, 0.1, 0.1, 0.1, 0.6])  # normal概率最高
                
        self.mock_model_factory.get_model().predict.side_effect = mock_predict_side_effect
        
        # 调用区域分析方法
        regions = self.analyzer._analyze_face_regions(face_image, landmarks)
        
        # 验证分析结果
        self.assertGreaterEqual(len(regions), 3)  # 至少分析了3个区域
        self.assertIn('region_name', regions[0])
        self.assertIn('color', regions[0])
        self.assertIn('feature', regions[0])
        self.assertIn('confidence', regions[0])
        
    def test_analyze_organ_correlations(self):
        """测试脏腑关联分析功能"""
        # 准备区域分析结果
        regions = [
            {'region_name': 'forehead', 'color': 'yellow', 'feature': 'shiny', 'confidence': 0.7},
            {'region_name': 'nose', 'color': 'red', 'feature': 'oily', 'confidence': 0.65},
            {'region_name': 'left_cheek', 'color': 'normal', 'feature': 'normal', 'confidence': 0.8},
            {'region_name': 'right_cheek', 'color': 'normal', 'feature': 'normal', 'confidence': 0.75},
            {'region_name': 'chin', 'color': 'pale', 'feature': 'dry', 'confidence': 0.6}
        ]
        
        # 调用脏腑关联分析方法
        correlations = self.analyzer._analyze_organ_correlations(regions)
        
        # 验证分析结果
        self.assertEqual(len(correlations), 5)  # 5个脏腑对应5个区域
        for corr in correlations:
            self.assertIn('organ_name', corr)
            self.assertIn('status', corr)
            self.assertIn('confidence', corr)
            self.assertIn('description', corr)
        
        # 验证特定器官的结果
        spleen_corr = next((c for c in correlations if c['organ_name'] == '脾胃'), None)
        self.assertIsNotNone(spleen_corr)
        self.assertGreater(spleen_corr['confidence'], 0.5)
            
    @patch('cv2.imread')
    def test_analyze_full_process(self, mock_imread):
        """测试完整面色分析流程"""
        # 模拟图像读取
        mock_image = np.ones((512, 512, 3), dtype=np.uint8) * 180
        mock_imread.return_value = mock_image
        
        # 模拟各个步骤的输出
        # 人脸检测
        self.analyzer._detect_face = MagicMock(return_value=[(100, 100, 300, 300, 0.98)])
        
        # 关键点提取
        mock_landmarks = np.random.rand(68, 2) * 300 + 100
        self.analyzer._extract_landmarks = MagicMock(return_value=mock_landmarks)
        
        # 面色分析
        self.analyzer._analyze_face_color = MagicMock(return_value=('normal', 0.85))
        
        # 区域分析
        mock_regions = [
            {'region_name': 'forehead', 'color': 'yellow', 'feature': 'shiny', 'confidence': 0.7},
            {'region_name': 'nose', 'color': 'red', 'feature': 'oily', 'confidence': 0.65},
            {'region_name': 'left_cheek', 'color': 'normal', 'feature': 'normal', 'confidence': 0.8},
            {'region_name': 'right_cheek', 'color': 'normal', 'feature': 'normal', 'confidence': 0.75},
            {'region_name': 'chin', 'color': 'pale', 'feature': 'dry', 'confidence': 0.6}
        ]
        self.analyzer._analyze_face_regions = MagicMock(return_value=mock_regions)
        
        # 脏腑关联
        mock_correlations = [
            {'organ_name': '脾胃', 'status': '湿热', 'confidence': 0.7, 'description': '脾胃湿热'},
            {'organ_name': '心', 'status': '心火旺', 'confidence': 0.65, 'description': '心火旺盛'},
            {'organ_name': '肝', 'status': '正常', 'confidence': 0.8, 'description': '肝功能正常'},
            {'organ_name': '肺', 'status': '正常', 'confidence': 0.75, 'description': '肺功能正常'},
            {'organ_name': '肾', 'status': '肾虚', 'confidence': 0.6, 'description': '肾气不足'}
        ]
        self.analyzer._analyze_organ_correlations = MagicMock(return_value=mock_correlations)
        
        # 体质关联分析
        self.analyzer._analyze_constitution = MagicMock(return_value=[
            {'constitution_type': '湿热质', 'confidence': 0.65, 'description': '面色偏黄红，形体偏胖'},
            {'constitution_type': '平和质', 'confidence': 0.25, 'description': '面色红润'}
        ])
        
        # 调用完整分析方法
        result = self.analyzer.analyze_face('dummy/path/to/image.jpg', 'comprehensive')
        
        # 验证结果包含所有必要字段
        self.assertIn('face_color', result)
        self.assertIn('regions', result)
        self.assertIn('features', result)
        self.assertIn('body_constitution', result)
        self.assertIn('organ_correlations', result)
        self.assertIn('analysis_summary', result)
        
        # 验证脏腑关联
        self.assertEqual(len(result['organ_correlations']), 5)
        self.assertEqual(result['organ_correlations'][0]['organ_name'], '脾胃')
        
        # 验证体质关联
        self.assertEqual(len(result['body_constitution']), 2)
        self.assertEqual(result['body_constitution'][0]['constitution_type'], '湿热质')


if __name__ == '__main__':
    unittest.main() 