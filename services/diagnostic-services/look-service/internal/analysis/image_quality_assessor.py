#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像质量评估模块 - 用于评估和过滤低质量图像

本模块提供了一系列图像质量评估工具，用于在进行详细分析前评估图像质量，
过滤掉模糊、光照不足、过曝、角度不正确等低质量图像，提高分析准确性。
"""

import os
import io
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import cv2
from skimage.metrics import structural_similarity as ssim
from PIL import Image, ImageStat

logger = logging.getLogger(__name__)

class ImageQualityIssue(Enum):
    """图像质量问题类型枚举"""
    TOO_DARK = "图像过暗"
    TOO_BRIGHT = "图像过亮"
    BLURRY = "图像模糊"
    INCOMPLETE_TONGUE = "舌头不完整"
    LOW_RESOLUTION = "分辨率不足"
    COLOR_DISTORTION = "色彩失真"
    BAD_ANGLE = "拍摄角度不佳"
    NOISE = "噪点过多"
    OBJECT_OBSTRUCTION = "有物体遮挡"
    IMPROPER_LIGHTING = "光照不均匀"
    

@dataclass
class ImageQualityResult:
    """图像质量评估结果"""
    is_acceptable: bool
    quality_score: float  # 0.0-1.0
    issues: List[ImageQualityIssue]
    metrics: Dict[str, float]
    recommendations: List[str]


class ImageQualityAssessor:
    """图像质量评估器，用于判断图像是否满足分析要求"""
    
    def __init__(self, config: Dict = None):
        """
        初始化图像质量评估器
        
        Args:
            config: 配置字典，包含评估参数
        """
        self.config = config or {}
        
        # 基本阈值配置
        self.min_resolution = self.config.get('min_resolution', (640, 480))  # 最小分辨率
        self.max_resolution = self.config.get('max_resolution', (4096, 3072))  # 最大分辨率
        self.min_brightness = self.config.get('min_brightness', 40)  # 最小亮度
        self.max_brightness = self.config.get('max_brightness', 240)  # 最大亮度
        self.min_contrast = self.config.get('min_contrast', 30)  # 最小对比度
        self.blur_threshold = self.config.get('blur_threshold', 100)  # 模糊检测阈值
        self.min_face_size = self.config.get('min_face_size', 0.2)  # 最小人脸占比
        
        # 特定类型图像的参数
        self.tongue_params = self.config.get('tongue_parameters', {
            'tongue_min_area_ratio': 0.15,  # 舌头最小面积占比
            'red_channel_min': 50,  # 红色通道最小值
            'valid_area_min_ratio': 0.5  # 有效区域最小占比
        })
        
        # 图像类型特定检测器
        self.face_cascade = None
        self.has_face_detector = self.config.get('use_face_detector', True)
        if self.has_face_detector:
            try:
                cascade_path = self.config.get('face_cascade_path', 
                                              cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                logger.info(f"面部检测器已加载: {cascade_path}")
            except Exception as e:
                logger.warning(f"无法加载面部检测器: {str(e)}")
                self.has_face_detector = False
                
        # 亮度阈值
        self.brightness_min = self.config.get('brightness_min', 40)
        self.brightness_max = self.config.get('brightness_max', 220)
        
        # 锐度阈值
        self.sharpness_threshold = self.config.get('sharpness_threshold', 100)
        
        # 对比度阈值
        self.contrast_threshold = self.config.get('contrast_threshold', 50)
        
        # 颜色范围要求
        self.color_range_min = self.config.get('color_range_min', 50)
        
        # 噪声阈值
        self.noise_threshold = self.config.get('noise_threshold', 0.05)
        
        # 整体质量分数权重
        self.weights = {
            'brightness': self.config.get('weight_brightness', 0.2),
            'sharpness': self.config.get('weight_sharpness', 0.3), 
            'resolution': self.config.get('weight_resolution', 0.15),
            'contrast': self.config.get('weight_contrast', 0.15),
            'color': self.config.get('weight_color', 0.1),
            'noise': self.config.get('weight_noise', 0.1)
        }
        
        # 最低可接受分数
        self.min_acceptable_score = self.config.get('min_acceptable_score', 0.7)
        
        # 是否允许低质量图像进行分析
        self.allow_low_quality = self.config.get('allow_low_quality', False)
        
        logger.info("图像质量评估器初始化完成")
    
    def assess_image(self, image_data: bytes, image_type: str = 'general') -> Tuple[bool, Dict]:
        """
        评估图像质量
        
        Args:
            image_data: 图像二进制数据
            image_type: 图像类型，可以是 'general', 'tongue', 'face', 'body'
            
        Returns:
            Tuple[bool, Dict]: (图像是否合格, 详细评估结果)
        """
        try:
            # 将二进制数据转换为PIL图像
            pil_image = Image.open(io.BytesIO(image_data))
            
            # 转换为numpy数组用于OpenCV处理
            np_image = np.array(pil_image)
            
            # 确保图像是RGB格式
            if len(np_image.shape) == 2:  # 灰度图
                np_image = cv2.cvtColor(np_image, cv2.COLOR_GRAY2RGB)
            elif np_image.shape[2] == 4:  # RGBA图
                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGBA2RGB)
            
            # 转换为BGR用于OpenCV函数
            bgr_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            
            # 基本质量检查
            resolution_check = self._check_resolution(np_image)
            brightness_check = self._check_brightness(np_image)
            contrast_check = self._check_contrast(np_image)
            blur_check = self._check_blur(bgr_image)
            
            # 创建基本评估结果
            assessment = {
                'resolution': resolution_check,
                'brightness': brightness_check,
                'contrast': contrast_check,
                'blur': blur_check,
                'timestamp': time.time()
            }
            
            # 特定类型图像的检查
            if image_type == 'face':
                face_check = self._check_face(bgr_image)
                assessment['face'] = face_check
                
            elif image_type == 'tongue':
                tongue_check = self._check_tongue(bgr_image)
                assessment['tongue'] = tongue_check
                # 舌象图像特殊要求
                if not tongue_check['is_valid']:
                    return False, assessment
            
            # 决定图像是否合格
            is_valid = (
                resolution_check['is_valid'] and
                brightness_check['is_valid'] and
                contrast_check['is_valid'] and
                blur_check['is_valid']
            )
            
            if image_type == 'face' and 'face' in assessment:
                is_valid = is_valid and assessment['face']['is_valid']
            
            logger.info(
                f"图像质量评估完成",
                image_type=image_type,
                is_valid=is_valid,
                resolution=resolution_check['value'],
                brightness=brightness_check['value'],
                blur=blur_check['value']
            )
            
            return is_valid, assessment
            
        except Exception as e:
            logger.error(f"图像质量评估失败: {str(e)}")
            return False, {'error': str(e), 'is_valid': False}
    
    def _check_resolution(self, image: np.ndarray) -> Dict:
        """检查图像分辨率"""
        height, width = image.shape[:2]
        resolution = (width, height)
        
        is_valid = (
            width >= self.min_resolution[0] and
            height >= self.min_resolution[1] and
            width <= self.max_resolution[0] and
            height <= self.max_resolution[1]
        )
        
        return {
            'is_valid': is_valid,
            'value': resolution,
            'min': self.min_resolution,
            'max': self.max_resolution
        }
    
    def _check_brightness(self, image: np.ndarray) -> Dict:
        """检查图像亮度"""
        # 转换为HSV，计算V通道均值
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        brightness = np.mean(hsv[:, :, 2])
        
        is_valid = (
            brightness >= self.min_brightness and
            brightness <= self.max_brightness
        )
        
        return {
            'is_valid': is_valid,
            'value': float(brightness),
            'min': self.min_brightness,
            'max': self.max_brightness
        }
    
    def _check_contrast(self, image: np.ndarray) -> Dict:
        """检查图像对比度"""
        # 转换为灰度图
        if len(image.shape) > 2:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
            
        # 计算对比度(标准差)
        contrast = np.std(gray)
        
        is_valid = contrast >= self.min_contrast
        
        return {
            'is_valid': is_valid,
            'value': float(contrast),
            'min': self.min_contrast
        }
    
    def _check_blur(self, image: np.ndarray) -> Dict:
        """检查图像模糊度"""
        # 转换为灰度图
        if len(image.shape) > 2:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # 计算拉普拉斯变换的方差
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        is_valid = laplacian_var >= self.blur_threshold
        
        return {
            'is_valid': is_valid,
            'value': float(laplacian_var),
            'threshold': self.blur_threshold
        }
    
    def _check_face(self, image: np.ndarray) -> Dict:
        """检查人脸图像质量"""
        if not self.has_face_detector or self.face_cascade is None:
            # 没有人脸检测器，返回默认通过
            return {'is_valid': True, 'reason': 'no face detector available'}
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return {'is_valid': False, 'reason': 'no face detected'}
        
        # 检查人脸大小占比
        height, width = image.shape[:2]
        image_area = height * width
        
        max_face_area = 0
        for (x, y, w, h) in faces:
            face_area = w * h
            max_face_area = max(max_face_area, face_area)
        
        face_ratio = max_face_area / image_area
        is_valid = face_ratio >= self.min_face_size
        
        return {
            'is_valid': is_valid,
            'value': float(face_ratio),
            'min': self.min_face_size,
            'faces_detected': len(faces)
        }
    
    def _check_tongue(self, image: np.ndarray) -> Dict:
        """检查舌象图像质量"""
        # 舌象图像特殊检查
        height, width = image.shape[:2]
        image_area = height * width
        
        # 1. 检查红色通道强度
        r_channel = image[:, :, 2]  # OpenCV的BGR，索引2是红色通道
        mean_red = np.mean(r_channel)
        
        # 2. 检查舌头区域占比 (简化版，实际应使用分割模型)
        # 这里使用红色阈值粗略检测舌头区域
        red_mask = cv2.inRange(
            image,
            np.array([0, 0, self.tongue_params['red_channel_min']]),
            np.array([255, 255, 255])
        )
        tongue_area = np.count_nonzero(red_mask)
        tongue_ratio = tongue_area / image_area
        
        is_valid = (
            mean_red >= self.tongue_params['red_channel_min'] and
            tongue_ratio >= self.tongue_params['tongue_min_area_ratio']
        )
        
        return {
            'is_valid': is_valid,
            'red_value': float(mean_red),
            'min_red': self.tongue_params['red_channel_min'],
            'tongue_ratio': float(tongue_ratio),
            'min_ratio': self.tongue_params['tongue_min_area_ratio']
        }
    
    def get_improvement_suggestions(self, assessment: Dict) -> List[str]:
        """
        基于评估结果给出图像改进建议
        
        Args:
            assessment: 评估结果字典
            
        Returns:
            List[str]: 改进建议列表
        """
        suggestions = []
        
        # 分辨率问题
        if not assessment.get('resolution', {}).get('is_valid', True):
            resolution = assessment['resolution']['value']
            min_res = assessment['resolution']['min']
            max_res = assessment['resolution']['max']
            
            if resolution[0] < min_res[0] or resolution[1] < min_res[1]:
                suggestions.append(f"图像分辨率过低({resolution[0]}x{resolution[1]})，建议至少使用{min_res[0]}x{min_res[1]}的分辨率")
            elif resolution[0] > max_res[0] or resolution[1] > max_res[1]:
                suggestions.append(f"图像分辨率过高({resolution[0]}x{resolution[1]})，建议不超过{max_res[0]}x{max_res[1]}的分辨率")
        
        # 亮度问题
        if not assessment.get('brightness', {}).get('is_valid', True):
            brightness = assessment['brightness']['value']
            min_bright = assessment['brightness']['min']
            max_bright = assessment['brightness']['max']
            
            if brightness < min_bright:
                suggestions.append(f"图像亮度不足({brightness:.1f})，建议在光线充足的环境下拍摄")
            elif brightness > max_bright:
                suggestions.append(f"图像亮度过高({brightness:.1f})，建议避免强光直射和过度曝光")
        
        # 对比度问题
        if not assessment.get('contrast', {}).get('is_valid', True):
            contrast = assessment['contrast']['value']
            min_contrast = assessment['contrast']['min']
            suggestions.append(f"图像对比度不足({contrast:.1f})，建议调整拍摄环境或相机设置")
        
        # 模糊问题
        if not assessment.get('blur', {}).get('is_valid', True):
            blur = assessment['blur']['value']
            threshold = assessment['blur']['threshold']
            suggestions.append(f"图像模糊({blur:.1f})，建议保持相机稳定，确保拍摄对象清晰对焦")
        
        # 人脸检测问题
        if 'face' in assessment and not assessment['face'].get('is_valid', True):
            if assessment['face'].get('reason') == 'no face detected':
                suggestions.append("未检测到人脸，请确保面部在画面中央且光线充足")
            else:
                face_ratio = assessment['face'].get('value', 0)
                min_ratio = assessment['face'].get('min', 0)
                suggestions.append(f"人脸占比过小({face_ratio:.2f})，建议靠近拍摄，确保面部占据画面主要部分")
        
        # 舌象问题
        if 'tongue' in assessment and not assessment['tongue'].get('is_valid', True):
            red_value = assessment['tongue'].get('red_value', 0)
            min_red = assessment['tongue'].get('min_red', 0)
            tongue_ratio = assessment['tongue'].get('tongue_ratio', 0)
            min_ratio = assessment['tongue'].get('min_ratio', 0)
            
            if red_value < min_red:
                suggestions.append(f"舌头颜色不明显，建议在光线充足的环境下张口露出舌头拍摄")
            
            if tongue_ratio < min_ratio:
                suggestions.append(f"舌头占比过小({tongue_ratio:.2f})，建议靠近拍摄，确保舌头占据画面主要部分")
        
        return suggestions 

    def assess_image_quality(self, image: np.ndarray) -> ImageQualityResult:
        """
        评估图像质量
        
        Args:
            image: OpenCV格式的图像(BGR)
            
        Returns:
            图像质量评估结果
        """
        issues = []
        metrics = {}
        recommendations = []
        
        # 验证图像尺寸
        height, width = image.shape[:2]
        resolution_score = self._check_resolution(width, height, issues, recommendations)
        metrics['resolution_score'] = resolution_score
        
        # 检查亮度
        brightness_score = self._check_brightness(image, issues, recommendations)
        metrics['brightness_score'] = brightness_score
        
        # 检查锐度
        sharpness_score = self._check_sharpness(image, issues, recommendations)
        metrics['sharpness_score'] = sharpness_score
        
        # 检查对比度
        contrast_score = self._check_contrast(image, issues, recommendations)
        metrics['contrast_score'] = contrast_score
        
        # 检查色彩范围
        color_score = self._check_color_range(image, issues, recommendations)
        metrics['color_score'] = color_score
        
        # 检查噪声
        noise_score = self._check_noise(image, issues, recommendations)
        metrics['noise_score'] = noise_score
        
        # 计算总体质量分数
        quality_score = (
            self.weights['brightness'] * brightness_score +
            self.weights['sharpness'] * sharpness_score +
            self.weights['resolution'] * resolution_score +
            self.weights['contrast'] * contrast_score +
            self.weights['color'] * color_score +
            self.weights['noise'] * noise_score
        )
        
        # 判断图像是否可接受
        is_acceptable = quality_score >= self.min_acceptable_score or self.allow_low_quality
        
        # 如果质量太低，添加总体建议
        if not is_acceptable:
            recommendations.append("建议重新拍摄舌象图像，注意光线、对焦和角度")
            
        return ImageQualityResult(
            is_acceptable=is_acceptable,
            quality_score=quality_score,
            issues=issues,
            metrics=metrics,
            recommendations=recommendations
        )
        
    def _check_resolution(self, width: int, height: int, issues: List[ImageQualityIssue], 
                          recommendations: List[str]) -> float:
        """检查分辨率"""
        min_width, min_height = self.min_resolution
        
        if width < min_width or height < min_height:
            issues.append(ImageQualityIssue.LOW_RESOLUTION)
            recommendations.append(f"图像分辨率过低，建议至少使用 {min_width}x{min_height} 的分辨率")
            # 计算分数：实际分辨率与要求的比例
            actual_pixels = width * height
            required_pixels = min_width * min_height
            return min(1.0, actual_pixels / required_pixels)
            
        return 1.0
        
    def _check_brightness(self, image: np.ndarray, issues: List[ImageQualityIssue], 
                         recommendations: List[str]) -> float:
        """检查亮度"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 计算平均亮度
        avg_brightness = np.mean(gray)
        
        if avg_brightness < self.brightness_min:
            issues.append(ImageQualityIssue.TOO_DARK)
            recommendations.append("图像过暗，请在明亮环境下拍摄或调整曝光")
            return avg_brightness / self.brightness_min
            
        if avg_brightness > self.brightness_max:
            issues.append(ImageQualityIssue.TOO_BRIGHT)
            recommendations.append("图像过亮，请避免强光直射或降低曝光")
            return 1.0 - (avg_brightness - self.brightness_max) / (255 - self.brightness_max)
            
        # 检查光照均匀性
        std_brightness = np.std(gray)
        if std_brightness > 50:  # 如果标准差大，说明光照不均匀
            issues.append(ImageQualityIssue.IMPROPER_LIGHTING)
            recommendations.append("光照不均匀，请使用均匀柔和的光线")
            return 1.0 - min(1.0, (std_brightness - 50) / 50)
            
        return 1.0
        
    def _check_sharpness(self, image: np.ndarray, issues: List[ImageQualityIssue], 
                        recommendations: List[str]) -> float:
        """检查锐度（对焦质量）"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 计算拉普拉斯变换
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        # 计算锐度得分
        sharpness = np.var(lap)
        
        if sharpness < self.sharpness_threshold:
            issues.append(ImageQualityIssue.BLURRY)
            recommendations.append("图像模糊，请确保摄像头对焦正确")
            return sharpness / self.sharpness_threshold
            
        return 1.0
        
    def _check_contrast(self, image: np.ndarray, issues: List[ImageQualityIssue], 
                       recommendations: List[str]) -> float:
        """检查对比度"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 计算直方图
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        # 计算标准差作为对比度的估计
        contrast = np.std(gray)
        
        if contrast < self.contrast_threshold:
            issues.append(ImageQualityIssue.COLOR_DISTORTION)
            recommendations.append("图像对比度不足，请在适当光线下拍摄")
            return contrast / self.contrast_threshold
            
        return 1.0
        
    def _check_color_range(self, image: np.ndarray, issues: List[ImageQualityIssue], 
                          recommendations: List[str]) -> float:
        """检查色彩范围"""
        # 将图像转换到HSV空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # 计算色相和饱和度的范围
        h_range = np.max(hsv[:,:,0]) - np.min(hsv[:,:,0])
        s_range = np.max(hsv[:,:,1]) - np.min(hsv[:,:,1])
        
        color_range = (h_range + s_range) / 2
        
        if color_range < self.color_range_min:
            issues.append(ImageQualityIssue.COLOR_DISTORTION)
            recommendations.append("图像色彩范围不足，请检查相机色彩设置")
            return color_range / self.color_range_min
            
        return 1.0
        
    def _check_noise(self, image: np.ndarray, issues: List[ImageQualityIssue], 
                    recommendations: List[str]) -> float:
        """检查噪声水平"""
        # 使用高斯滤波器作为参考
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        # 计算原图与滤波后的差异
        diff = cv2.absdiff(image, blurred)
        noise_level = np.mean(diff) / 255.0
        
        if noise_level > self.noise_threshold:
            issues.append(ImageQualityIssue.NOISE)
            recommendations.append("图像噪点过多，请在光线充足处拍摄或使用更好的相机")
            return 1.0 - (noise_level - self.noise_threshold) / (1.0 - self.noise_threshold)
            
        return 1.0
    
    def detect_tongue_presence(self, image: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        检测图像中是否存在完整的舌头，并返回舌头的掩码
        
        Args:
            image: OpenCV格式的图像(BGR)
            
        Returns:
            (是否存在完整舌头, 舌头掩码)
        """
        # 转换到HSV空间，更容易分割舌头
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 舌头的颜色范围（红色到粉红色）
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # 创建掩码
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # 形态学操作改善掩码
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # 找到最大的连通区域，假设是舌头
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False, None
            
        # 找到最大的轮廓
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)
        
        # 检查面积是否足够大（舌头应该占据图像一定比例）
        height, width = image.shape[:2]
        image_area = height * width
        min_tongue_ratio = 0.05  # 舌头至少占图像5%
        
        if area < image_area * min_tongue_ratio:
            return False, None
            
        # 创建舌头掩码
        tongue_mask = np.zeros_like(mask)
        cv2.drawContours(tongue_mask, [max_contour], 0, 255, -1)
        
        # 检查是否在图像边缘（不完整）
        x, y, w, h = cv2.boundingRect(max_contour)
        is_on_edge = (x <= 5 or y <= 5 or x + w >= width - 5 or y + h >= height - 5)
        
        if is_on_edge:
            return False, tongue_mask
            
        return True, tongue_mask 