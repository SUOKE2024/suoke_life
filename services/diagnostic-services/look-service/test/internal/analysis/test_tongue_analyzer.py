#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
舌象分析器单元测试
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import io
from pathlib import Path

import numpy as np
import torch
import pytest
from PIL import Image
import cv2

# 将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from internal.analysis.tongue_analyzer import (
    TongueAnalyzer, 
    TongueColorType, 
    TongueShapeType, 
    CoatingColorType,
    FeatureLocation,
    ConstitutionCorrelation
)
from internal.model.model_factory import ModelFactory


class TestTongueAnalyzer(unittest.TestCase):
    """舌象分析器测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 模拟配置
        self.config = {
            'models': {
                'tongue_segmentation': {
                    'path': 'models/tongue_segmentation.onnx',
                    'input_size': [256, 256],
                    'confidence_threshold': 0.85
                },
                'tongue_color': {
                    'path': 'models/tongue_color.onnx',
                    'input_size': [224, 224],
                    'classes': ['pale', 'red', 'purple', 'normal']
                },
                'coating_analysis': {
                    'path': 'models/coating.onnx',
                    'input_size': [224, 224],
                    'classes': ['thin', 'thick', 'greasy', 'none']
                }
            }
        }
        
        # 使用模拟的ModelFactory
        with patch('internal.model.model_factory.ModelFactory') as MockModelFactory:
            self.mock_model_factory = MockModelFactory.return_value
            self.mock_model_factory.get_model.return_value = MagicMock()
            self.analyzer = TongueAnalyzer(self.config, model_factory=self.mock_model_factory)
        
        # 创建一个模拟图像
        self.test_image = np.ones((300, 300, 3), dtype=np.uint8) * 255  # 白色图像
        # 添加一个简单的舌头形状 (红色矩形)
        self.test_image[100:200, 100:200, 0] = 200  # 红色通道
        self.test_image[100:200, 100:200, 1:3] = 100  # 绿色和蓝色通道
        
        # 将NumPy数组转换为PIL图像
        pil_image = Image.fromarray(self.test_image)
        
        # 将PIL图像转换为字节对象
        img_byte_array = io.BytesIO()
        pil_image.save(img_byte_array, format='PNG')
        self.image_bytes = img_byte_array.getvalue()

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.analyzer.device, "cpu")
        self.assertEqual(self.analyzer.confidence_threshold, 0.6)
        self.assertEqual(self.analyzer.input_size, (224, 224))
        self.assertEqual(self.analyzer.batch_size, 1)
        self.assertEqual(self.analyzer.quantized, False)

    def test_preprocess_image(self):
        """测试图像预处理"""
        # 从字节对象创建PIL图像
        pil_image = Image.open(io.BytesIO(self.image_bytes))
        
        # 预处理图像
        preprocessed = self.analyzer._preprocess_image(pil_image)
        
        # 验证预处理后的图像形状
        self.assertEqual(preprocessed.shape[0], 3)  # 通道数
        self.assertEqual(preprocessed.shape[1:], self.analyzer.input_size)
        
        # 验证预处理后的图像值范围 (应该在[-1,1]或[0,1]之间)
        self.assertTrue(torch.all(preprocessed <= 1.0))
        self.assertTrue(torch.all(preprocessed >= -1.0))

    def test_analyze(self):
        """测试舌象分析功能"""
        # 使用模拟的图像分析
        result = self.analyzer.analyze(
            image_data=self.image_bytes,
            user_id="test_user_123",
            save_result=False
        )
        
        # 验证基本结果
        self.assertIsNotNone(result.request_id)
        self.assertEqual(result.tongue_color, TongueColorType.LIGHT_RED)  # 淡红
        self.assertEqual(result.tongue_shape, TongueShapeType.NORMAL)  # 正常
        self.assertEqual(result.coating_color, CoatingColorType.WHITE)  # 白
        self.assertIsNotNone(result.analysis_summary)
        
        # 验证分析ID (save_result=False时应为空)
        self.assertEqual(result.analysis_id, "")
        
        # 验证时间戳
        self.assertIsNotNone(result.timestamp)
        
        # 验证特征列表不为空
        self.assertGreater(len(result.features), 0)

    def test_analyze_with_save(self):
        """测试带保存的舌象分析功能"""
        # 模拟存储库保存方法
        mock_repository = MagicMock()
        mock_repository.save_tongue_analysis.return_value = "test_analysis_id_12345"
        
        # 替换分析器的存储库
        self.analyzer.repository = mock_repository
        
        # 使用模拟的图像分析并保存
        result = self.analyzer.analyze(
            image_data=self.image_bytes,
            user_id="test_user_123",
            save_result=True
        )
        
        # 验证分析ID被设置
        self.assertEqual(result.analysis_id, "test_analysis_id_12345")
        
        # 验证存储库的save_tongue_analysis方法被调用
        mock_repository.save_tongue_analysis.assert_called_once()
        
        # 验证传递给存储库的数据
        save_data = mock_repository.save_tongue_analysis.call_args[0][0]
        self.assertEqual(save_data["user_id"], "test_user_123")
        self.assertEqual(save_data["tongue_color"], "淡红")
        self.assertEqual(save_data["tongue_shape"], "正常")
        self.assertEqual(save_data["coating_color"], "白")

    def test_get_tongue_color(self):
        """测试获取舌色功能"""
        # 模拟不同的预测结果
        predictions = {
            torch.tensor([0.8, 0.1, 0.05, 0.03, 0.02]): TongueColorType.PALE,
            torch.tensor([0.1, 0.75, 0.1, 0.03, 0.02]): TongueColorType.LIGHT_RED,
            torch.tensor([0.1, 0.1, 0.75, 0.03, 0.02]): TongueColorType.RED,
            torch.tensor([0.1, 0.1, 0.05, 0.7, 0.05]): TongueColorType.CRIMSON,
            torch.tensor([0.1, 0.1, 0.05, 0.05, 0.7]): TongueColorType.PURPLE,
        }
        
        for prediction, expected_color in predictions.items():
            color = self.analyzer._get_tongue_color(prediction)
            self.assertEqual(color, expected_color, f"Expected {expected_color} for {prediction}")

    def test_get_tongue_shape(self):
        """测试获取舌形功能"""
        # 模拟不同的预测结果
        predictions = {
            torch.tensor([0.8, 0.1, 0.1]): TongueShapeType.NORMAL,
            torch.tensor([0.1, 0.8, 0.1]): TongueShapeType.THIN,
            torch.tensor([0.1, 0.1, 0.8]): TongueShapeType.FAT,
        }
        
        for prediction, expected_shape in predictions.items():
            shape = self.analyzer._get_tongue_shape(prediction)
            self.assertEqual(shape, expected_shape, f"Expected {expected_shape} for {prediction}")

    def test_low_confidence_handling(self):
        """测试处理低置信度的情况"""
        # 创建一个低置信度的模型预测
        low_confidence_model = MagicMock()
        low_confidence_model.return_value = torch.tensor([
            [0.3, 0.3, 0.2, 0.1, 0.1],  # 所有类别的置信度都低于阈值
            [0.4, 0.3, 0.3],  
            [0.4, 0.4, 0.2],  
        ])
        
        # 替换分析器的模型
        self.analyzer.model = low_confidence_model
        
        # 提高置信度阈值
        self.analyzer.confidence_threshold = 0.5
        
        # 使用模拟的图像分析
        result = self.analyzer.analyze(
            image_data=self.image_bytes,
            user_id="test_user_123",
            save_result=False
        )
        
        # 验证分析结果包含低置信度的警告
        self.assertIn("低置信度", result.analysis_summary)
        
        # 检查特征列表中的不确定性标记
        self.assertTrue(any("不确定" in feature for feature in result.features))

    @patch('internal.analysis.tongue_analyzer.np.random.rand')
    def test_generate_mock_locations(self, mock_rand):
        """测试生成模拟位置功能"""
        # 设置随机函数的返回值
        mock_rand.side_effect = [0.2, 0.3, 0.4, 0.5, 0.8]
        
        # 生成模拟位置
        locations = self.analyzer._generate_mock_locations()
        
        # 验证至少生成了一个位置
        self.assertGreater(len(locations), 0)
        
        # 验证位置对象的格式
        for loc in locations:
            self.assertIsInstance(loc, FeatureLocation)
            self.assertTrue(0 <= loc.x_min <= 1)
            self.assertTrue(0 <= loc.y_min <= 1)
            self.assertTrue(loc.x_min < loc.x_max <= 1)
            self.assertTrue(loc.y_min < loc.y_max <= 1)
            self.assertTrue(0 <= loc.confidence <= 1)

    def test_generate_constitution_correlations(self):
        """测试生成体质关联功能"""
        # 测试不同的舌色类型
        for tongue_color in TongueColorType:
            # 调用方法
            correlations = self.analyzer._generate_constitution_correlations(
                tongue_color=tongue_color,
                tongue_shape=TongueShapeType.NORMAL,
                coating_color=CoatingColorType.WHITE
            )
            
            # 验证至少生成了一个关联
            self.assertGreater(len(correlations), 0)
            
            # 验证关联对象的格式
            for corr in correlations:
                self.assertIsInstance(corr, ConstitutionCorrelation)
                self.assertTrue(0 <= corr.confidence <= 1)
                self.assertGreater(len(corr.description), 0)

    def test_segment_tongue(self):
        """测试舌头分割功能"""
        # 创建测试图像
        test_image = np.ones((256, 256, 3), dtype=np.uint8) * 255
        
        # 模拟分割模型输出
        mock_segmentation = np.zeros((256, 256), dtype=np.uint8)
        mock_segmentation[50:200, 50:200] = 1  # 舌头区域
        
        # 设置模型返回值
        self.mock_model_factory.get_model().predict.return_value = mock_segmentation
        
        # 调用分割方法
        segmented, mask = self.analyzer._segment_tongue(test_image)
        
        # 验证分割结果
        self.assertEqual(mask.shape, (256, 256))
        self.assertTrue(np.any(segmented))  # 确保分割后的图像不为空
        
    def test_analyze_tongue_color(self):
        """测试舌色分析功能"""
        # 创建测试舌头图像
        tongue_image = np.ones((224, 224, 3), dtype=np.uint8) * 150
        
        # 模拟模型输出概率
        model_output = np.array([0.1, 0.2, 0.3, 0.4])  # normal类别概率最高
        self.mock_model_factory.get_model().predict.return_value = model_output
        
        # 调用舌色分析方法
        color, confidence = self.analyzer._analyze_tongue_color(tongue_image)
        
        # 验证输出
        self.assertEqual(color, 'normal')
        self.assertEqual(confidence, 0.4)
        
    def test_analyze_tongue_shape(self):
        """测试舌形分析功能"""
        # 创建舌头掩码
        tongue_mask = np.zeros((256, 256), dtype=np.uint8)
        # 创建一个瘦长型舌头区域
        tongue_mask[50:200, 100:150] = 1
        
        # 调用舌形分析方法
        shape, metrics = self.analyzer._analyze_tongue_shape(tongue_mask)
        
        # 验证输出
        self.assertIsNotNone(shape)
        self.assertIsInstance(metrics, dict)
        self.assertIn('width_height_ratio', metrics)
        
    def test_analyze_coating(self):
        """测试舌苔分析功能"""
        # 创建测试舌头图像
        tongue_image = np.ones((224, 224, 3), dtype=np.uint8) * 200
        tongue_mask = np.zeros((224, 224), dtype=np.uint8)
        tongue_mask[50:200, 50:200] = 1  # 舌头区域
        
        # 模拟模型输出概率
        model_output = np.array([0.1, 0.7, 0.1, 0.1])  # thick类别概率最高
        self.mock_model_factory.get_model().predict.return_value = model_output
        
        # 调用舌苔分析方法
        coating_type, distribution, confidence = self.analyzer._analyze_coating(tongue_image, tongue_mask)
        
        # 验证输出
        self.assertEqual(coating_type, 'thick')
        self.assertIsNotNone(distribution)
        self.assertEqual(confidence, 0.7)
        
    @patch('cv2.imread')
    def test_analyze_full_process(self, mock_imread):
        """测试完整分析流程"""
        # 模拟图像读取
        mock_image = np.ones((512, 512, 3), dtype=np.uint8) * 180
        mock_imread.return_value = mock_image
        
        # 模拟各个步骤的输出
        # 舌头分割
        mock_mask = np.zeros((256, 256), dtype=np.uint8)
        mock_mask[50:200, 50:200] = 1
        self.analyzer._segment_tongue = MagicMock(return_value=(mock_image, mock_mask))
        
        # 舌色分析
        self.analyzer._analyze_tongue_color = MagicMock(return_value=('normal', 0.85))
        
        # 舌形分析
        self.analyzer._analyze_tongue_shape = MagicMock(return_value=('normal', {'width_height_ratio': 1.2}))
        
        # 舌苔分析
        self.analyzer._analyze_coating = MagicMock(return_value=('thin', 'center', 0.75))
        
        # 体质关联分析
        self.analyzer._analyze_constitution = MagicMock(return_value=[
            {'constitution_type': '平和质', 'confidence': 0.65, 'description': '舌象正常，体质平和'},
            {'constitution_type': '气虚质', 'confidence': 0.25, 'description': '舌淡胖，苔薄白'}
        ])
        
        # 调用完整分析方法
        result = self.analyzer.analyze_tongue('dummy/path/to/image.jpg', 'comprehensive')
        
        # 验证结果包含所有必要字段
        self.assertIn('tongue_color', result)
        self.assertIn('tongue_shape', result)
        self.assertIn('coating_color', result)
        self.assertIn('coating_distribution', result)
        self.assertIn('features', result)
        self.assertIn('body_constitution', result)
        self.assertIn('metrics', result)
        self.assertIn('analysis_summary', result)
        
        # 验证体质关联
        self.assertEqual(len(result['body_constitution']), 2)
        self.assertEqual(result['body_constitution'][0]['constitution_type'], '平和质')


if __name__ == '__main__':
    unittest.main() 