import unittest
import cv2
import numpy as np
import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from internal.analysis.image_quality_assessor import ImageQualityAssessor


class TestImageQualityAssessor(unittest.TestCase):
    """图像质量评估器单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 模拟配置
        self.config = {
            'quality': {
                'min_resolution': [640, 480],
                'max_resolution': [4000, 3000],
                'min_brightness': 30,
                'max_brightness': 220,
                'min_contrast': 20,
                'blur_threshold': 100,
                'noise_threshold': 15
            }
        }
        
        self.assessor = ImageQualityAssessor(self.config)
        
        # 创建不同质量的测试图像
        # 正常图像
        self.normal_image = np.ones((1080, 1920, 3), dtype=np.uint8) * 150
        # 添加一些随机变化
        noise = np.random.randint(0, 50, size=(1080, 1920, 3), dtype=np.uint8)
        self.normal_image = cv2.addWeighted(self.normal_image, 0.8, noise, 0.2, 0)
        
        # 低分辨率图像
        self.low_res_image = np.ones((320, 240, 3), dtype=np.uint8) * 150
        
        # 过亮图像
        self.bright_image = np.ones((1080, 1920, 3), dtype=np.uint8) * 240
        
        # 过暗图像
        self.dark_image = np.ones((1080, 1920, 3), dtype=np.uint8) * 20
        
        # 低对比度图像
        self.low_contrast_image = np.ones((1080, 1920, 3), dtype=np.uint8) * 128
        # 添加很小的随机变化
        small_noise = np.random.randint(0, 10, size=(1080, 1920, 3), dtype=np.uint8)
        self.low_contrast_image = cv2.addWeighted(self.low_contrast_image, 0.9, small_noise, 0.1, 0)
        
        # 模糊图像 (通过高斯模糊创建)
        self.blurry_image = cv2.GaussianBlur(self.normal_image, (31, 31), 0)
        
        # 噪声图像
        self.noisy_image = np.ones((1080, 1920, 3), dtype=np.uint8) * 150
        noise = np.random.randint(0, 100, size=(1080, 1920, 3), dtype=np.uint8)
        self.noisy_image = cv2.addWeighted(self.noisy_image, 0.5, noise, 0.5, 0)

    def test_check_resolution(self):
        """测试分辨率检查功能"""
        # 正常分辨率
        result = self.assessor._check_resolution(self.normal_image)
        self.assertTrue(result['pass'])
        self.assertGreaterEqual(result['score'], 0.8)
        
        # 低分辨率
        result = self.assessor._check_resolution(self.low_res_image)
        self.assertFalse(result['pass'])
        self.assertLessEqual(result['score'], 0.5)
        
    def test_check_brightness(self):
        """测试亮度检查功能"""
        # 正常亮度
        result = self.assessor._check_brightness(self.normal_image)
        self.assertTrue(result['pass'])
        self.assertGreaterEqual(result['score'], 0.8)
        
        # 过亮
        result = self.assessor._check_brightness(self.bright_image)
        self.assertFalse(result['pass'])
        self.assertLessEqual(result['score'], 0.7)
        
        # 过暗
        result = self.assessor._check_brightness(self.dark_image)
        self.assertFalse(result['pass'])
        self.assertLessEqual(result['score'], 0.7)
        
    def test_check_contrast(self):
        """测试对比度检查功能"""
        # 正常对比度
        result = self.assessor._check_contrast(self.normal_image)
        self.assertTrue(result['pass'])
        self.assertGreaterEqual(result['score'], 0.7)
        
        # 低对比度
        result = self.assessor._check_contrast(self.low_contrast_image)
        self.assertFalse(result['pass'])
        self.assertLessEqual(result['score'], 0.6)
        
    def test_check_blur(self):
        """测试模糊检查功能"""
        # 清晰图像
        result = self.assessor._check_blur(self.normal_image)
        self.assertTrue(result['pass'])
        self.assertGreaterEqual(result['score'], 0.7)
        
        # 模糊图像
        result = self.assessor._check_blur(self.blurry_image)
        self.assertFalse(result['pass'])
        self.assertLessEqual(result['score'], 0.6)
        
    def test_check_noise(self):
        """测试噪声检查功能"""
        # 正常噪声水平
        result = self.assessor._check_noise(self.normal_image)
        self.assertTrue(result['pass'])
        self.assertGreaterEqual(result['score'], 0.7)
        
        # 高噪声水平
        result = self.assessor._check_noise(self.noisy_image)
        self.assertFalse(result['pass'])
        self.assertLessEqual(result['score'], 0.6)
        
    def test_assess_quality(self):
        """测试综合质量评估功能"""
        # 测试正常图像
        result = self.assessor.assess_quality(self.normal_image)
        self.assertTrue(result['overall_pass'])
        self.assertGreaterEqual(result['overall_score'], 0.7)
        self.assertIn('resolution', result['checks'])
        self.assertIn('brightness', result['checks'])
        self.assertIn('contrast', result['checks'])
        self.assertIn('blur', result['checks'])
        self.assertIn('noise', result['checks'])
        
        # 测试低质量图像
        result = self.assessor.assess_quality(self.low_res_image)
        self.assertFalse(result['overall_pass'])
        self.assertLessEqual(result['overall_score'], 0.6)
        
    def test_get_improvement_suggestions(self):
        """测试获取改进建议功能"""
        # 测试过亮图像
        result = self.assessor.assess_quality(self.bright_image)
        suggestions = self.assessor.get_improvement_suggestions(result)
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        brightness_suggestion = next((s for s in suggestions if '亮度' in s), None)
        self.assertIsNotNone(brightness_suggestion)
        
        # 测试多问题图像
        # 创建一个同时存在多个问题的图像
        multi_problem_image = self.low_res_image.copy()  # 低分辨率
        multi_problem_image = cv2.GaussianBlur(multi_problem_image, (15, 15), 0)  # 添加模糊
        
        result = self.assessor.assess_quality(multi_problem_image)
        suggestions = self.assessor.get_improvement_suggestions(result)
        self.assertGreater(len(suggestions), 1)  # 应该有多条建议
        
    def test_color_calibration(self):
        """测试色彩校准功能"""
        # 创建一个色偏的图像（偏蓝）
        color_shifted_image = self.normal_image.copy()
        color_shifted_image[:, :, 0] = np.clip(color_shifted_image[:, :, 0] * 1.3, 0, 255)  # 增加蓝色通道
        
        # 校准色彩
        calibrated_image = self.assessor.calibrate_colors(color_shifted_image)
        
        # 验证校准后的图像
        self.assertEqual(calibrated_image.shape, color_shifted_image.shape)
        
        # 验证校准是否改变了色偏
        # 计算校准前后的平均通道值
        before_mean = np.mean(color_shifted_image, axis=(0, 1))
        after_mean = np.mean(calibrated_image, axis=(0, 1))
        
        # 校准应该减少了蓝色通道的偏差
        blue_correction = abs(after_mean[0] - np.mean(after_mean)) < abs(before_mean[0] - np.mean(before_mean))
        self.assertTrue(blue_correction)
        
    def test_enhance_image(self):
        """测试图像增强功能"""
        # 测试暗图像的增强
        enhanced_dark = self.assessor.enhance_image(self.dark_image)
        self.assertEqual(enhanced_dark.shape, self.dark_image.shape)
        
        # 验证亮度是否提高
        before_brightness = np.mean(self.dark_image)
        after_brightness = np.mean(enhanced_dark)
        self.assertGreater(after_brightness, before_brightness)
        
        # 测试模糊图像的增强
        enhanced_blurry = self.assessor.enhance_image(self.blurry_image)
        self.assertEqual(enhanced_blurry.shape, self.blurry_image.shape)
        
        # 测试噪声图像的增强
        enhanced_noisy = self.assessor.enhance_image(self.noisy_image)
        self.assertEqual(enhanced_noisy.shape, self.noisy_image.shape)
        
        # 验证噪声是否减少
        before_std = np.std(self.noisy_image)
        after_std = np.std(enhanced_noisy)
        self.assertLess(after_std, before_std)
        

if __name__ == '__main__':
    unittest.main() 