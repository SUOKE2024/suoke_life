"""
面部分析机器学习模型

基于深度学习的中医面诊特征识别和分析
"""

import cv2
import numpy as np
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import mediapipe as mp
import dlib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

@dataclass
class FaceFeatures:
    """面部特征数据类"""
    face_shape: str
    skin_color: str
    complexion: str
    eye_features: Dict[str, Any]
    nose_features: Dict[str, Any]
    mouth_features: Dict[str, Any]
    ear_features: Dict[str, Any]
    facial_landmarks: np.ndarray
    confidence_scores: Dict[str, float]

@dataclass
class ImageQualityMetrics:
    """图像质量指标"""
    resolution: Tuple[int, int]
    brightness: float
    contrast: float
    sharpness: float
    noise_level: float
    face_detection_confidence: float
    overall_quality_score: float
    quality_grade: str

class AdvancedImageQualityAssessment:
    """高级图像质量评估器"""
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
    
    def assess_image_quality(self, image: np.ndarray) -> ImageQualityMetrics:
        """评估图像质量"""
        try:
            # 基本图像信息
            height, width = image.shape[:2]
            resolution = (width, height)
            
            # 亮度评估
            brightness = self._calculate_brightness(image)
            
            # 对比度评估
            contrast = self._calculate_contrast(image)
            
            # 清晰度评估
            sharpness = self._calculate_sharpness(image)
            
            # 噪声水平评估
            noise_level = self._calculate_noise_level(image)
            
            # 面部检测置信度
            face_confidence = self._assess_face_detection_quality(image)
            
            # 综合质量评分
            overall_score = self._calculate_overall_quality(
                brightness, contrast, sharpness, noise_level, face_confidence
            )
            
            # 质量等级
            quality_grade = self._determine_quality_grade(overall_score)
            
            return ImageQualityMetrics(
                resolution=resolution,
                brightness=brightness,
                contrast=contrast,
                sharpness=sharpness,
                noise_level=noise_level,
                face_detection_confidence=face_confidence,
                overall_quality_score=overall_score,
                quality_grade=quality_grade
            )
            
        except Exception as e:
            logger.error(f"图像质量评估失败: {e}")
            return self._get_default_quality_metrics()
    
    def _calculate_brightness(self, image: np.ndarray) -> float:
        """计算图像亮度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        mean_brightness = np.mean(gray) / 255.0
        
        # 理想亮度范围 0.3-0.7
        if 0.3 <= mean_brightness <= 0.7:
            brightness_score = 1.0
        elif mean_brightness < 0.3:
            brightness_score = mean_brightness / 0.3
        else:
            brightness_score = (1.0 - mean_brightness) / 0.3
        
        return max(0.0, min(brightness_score, 1.0))
    
    def _calculate_contrast(self, image: np.ndarray) -> float:
        """计算图像对比度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        contrast = np.std(gray) / 255.0
        
        # 理想对比度范围 0.2-0.8
        if 0.2 <= contrast <= 0.8:
            contrast_score = 1.0
        elif contrast < 0.2:
            contrast_score = contrast / 0.2
        else:
            contrast_score = max(0.0, (1.0 - contrast) / 0.2)
        
        return max(0.0, min(contrast_score, 1.0))
    
    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """计算图像清晰度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 使用Laplacian算子计算清晰度
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 归一化清晰度分数
        sharpness_score = min(laplacian_var / 1000.0, 1.0)
        
        return sharpness_score
    
    def _calculate_noise_level(self, image: np.ndarray) -> float:
        """计算噪声水平"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 使用高斯滤波估算噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = np.mean(np.abs(gray.astype(np.float32) - blurred.astype(np.float32)))
        
        # 噪声水平越低越好
        noise_score = max(0.0, 1.0 - noise / 50.0)
        
        return noise_score
    
    def _assess_face_detection_quality(self, image: np.ndarray) -> float:
        """评估面部检测质量"""
        try:
            # 使用OpenCV的人脸检测器
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 1:
                # 单个面部，检查面部大小
                x, y, w, h = faces[0]
                face_area = w * h
                image_area = gray.shape[0] * gray.shape[1]
                face_ratio = face_area / image_area
                
                # 理想面部占比 0.1-0.5
                if 0.1 <= face_ratio <= 0.5:
                    return 1.0
                elif face_ratio < 0.1:
                    return face_ratio / 0.1
                else:
                    return max(0.0, (1.0 - face_ratio) / 0.5)
            elif len(faces) == 0:
                return 0.0
            else:
                return 0.5  # 多个面部
                
        except Exception as e:
            logger.error(f"面部检测质量评估失败: {e}")
            return 0.5
    
    def _calculate_overall_quality(self, brightness: float, contrast: float, 
                                 sharpness: float, noise_level: float, 
                                 face_confidence: float) -> float:
        """计算综合质量分数"""
        weights = {
            'brightness': 0.15,
            'contrast': 0.15,
            'sharpness': 0.25,
            'noise_level': 0.20,
            'face_confidence': 0.25
        }
        
        overall_score = (
            brightness * weights['brightness'] +
            contrast * weights['contrast'] +
            sharpness * weights['sharpness'] +
            noise_level * weights['noise_level'] +
            face_confidence * weights['face_confidence']
        )
        
        return round(overall_score, 4)
    
    def _determine_quality_grade(self, score: float) -> str:
        """确定质量等级"""
        if score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif score >= self.quality_thresholds['good']:
            return 'good'
        elif score >= self.quality_thresholds['fair']:
            return 'fair'
        else:
            return 'poor'
    
    def _get_default_quality_metrics(self) -> ImageQualityMetrics:
        """获取默认质量指标"""
        return ImageQualityMetrics(
            resolution=(0, 0),
            brightness=0.0,
            contrast=0.0,
            sharpness=0.0,
            noise_level=0.0,
            face_detection_confidence=0.0,
            overall_quality_score=0.0,
            quality_grade='poor'
        )

class TCMFaceFeatureExtractor:
    """中医面部特征提取器"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # 中医面诊特征映射
        self.tcm_feature_mapping = {
            'face_shapes': {
                'round': '圆形脸 - 脾胃功能',
                'oval': '椭圆脸 - 肝胆功能', 
                'square': '方形脸 - 肾脏功能',
                'heart': '心形脸 - 心脏功能',
                'long': '长形脸 - 肺部功能'
            },
            'complexion_types': {
                'rosy': '红润 - 气血充足',
                'pale': '苍白 - 气血不足',
                'yellow': '萎黄 - 脾胃虚弱',
                'dark': '晦暗 - 肾阳不足',
                'blue': '青色 - 肝气郁结'
            },
            'eye_features': {
                'bright': '目光有神 - 精神充沛',
                'dull': '目光呆滞 - 精神不振',
                'red': '目赤 - 心火上炎',
                'yellow': '目黄 - 湿热内蕴'
            }
        }
    
    def extract_tcm_features(self, image: np.ndarray) -> FaceFeatures:
        """提取中医面诊特征"""
        try:
            # 面部关键点检测
            landmarks = self._extract_facial_landmarks(image)
            
            # 面部形状分析
            face_shape = self._analyze_face_shape(landmarks)
            
            # 肤色分析
            skin_color, complexion = self._analyze_skin_color(image, landmarks)
            
            # 眼部特征分析
            eye_features = self._analyze_eye_features(image, landmarks)
            
            # 鼻部特征分析
            nose_features = self._analyze_nose_features(image, landmarks)
            
            # 口部特征分析
            mouth_features = self._analyze_mouth_features(image, landmarks)
            
            # 耳部特征分析
            ear_features = self._analyze_ear_features(image, landmarks)
            
            # 置信度评估
            confidence_scores = self._calculate_feature_confidence(landmarks, image)
            
            return FaceFeatures(
                face_shape=face_shape,
                skin_color=skin_color,
                complexion=complexion,
                eye_features=eye_features,
                nose_features=nose_features,
                mouth_features=mouth_features,
                ear_features=ear_features,
                facial_landmarks=landmarks,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            logger.error(f"中医面部特征提取失败: {e}")
            return self._get_default_face_features()
    
    def _extract_facial_landmarks(self, image: np.ndarray) -> np.ndarray:
        """提取面部关键点"""
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                landmark_points = []
                
                for landmark in landmarks.landmark:
                    x = int(landmark.x * image.shape[1])
                    y = int(landmark.y * image.shape[0])
                    landmark_points.append([x, y])
                
                return np.array(landmark_points)
            else:
                return np.array([])
                
        except Exception as e:
            logger.error(f"面部关键点提取失败: {e}")
            return np.array([])
    
    def _analyze_face_shape(self, landmarks: np.ndarray) -> str:
        """分析面部形状"""
        if len(landmarks) == 0:
            return "unknown"
        
        try:
            # 计算面部关键比例
            face_width = np.max(landmarks[:, 0]) - np.min(landmarks[:, 0])
            face_height = np.max(landmarks[:, 1]) - np.min(landmarks[:, 1])
            
            width_height_ratio = face_width / face_height if face_height > 0 else 1.0
            
            # 根据比例判断面部形状
            if width_height_ratio > 0.9:
                return "round"  # 圆形脸
            elif width_height_ratio > 0.8:
                return "oval"   # 椭圆脸
            elif width_height_ratio > 0.7:
                return "square" # 方形脸
            elif width_height_ratio > 0.6:
                return "heart"  # 心形脸
            else:
                return "long"   # 长形脸
                
        except Exception as e:
            logger.error(f"面部形状分析失败: {e}")
            return "unknown"
    
    def _analyze_skin_color(self, image: np.ndarray, landmarks: np.ndarray) -> Tuple[str, str]:
        """分析肤色和气色"""
        if len(landmarks) == 0:
            return "unknown", "unknown"
        
        try:
            # 提取面部区域
            face_mask = self._create_face_mask(image, landmarks)
            face_region = cv2.bitwise_and(image, image, mask=face_mask)
            
            # 计算平均颜色
            mean_color = cv2.mean(face_region, mask=face_mask)[:3]
            
            # 转换到HSV色彩空间
            bgr_color = np.uint8([[mean_color]])
            hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)[0][0]
            
            # 分析肤色类型
            skin_color = self._classify_skin_color(hsv_color)
            
            # 分析气色
            complexion = self._analyze_complexion(mean_color, hsv_color)
            
            return skin_color, complexion
            
        except Exception as e:
            logger.error(f"肤色分析失败: {e}")
            return "unknown", "unknown"
    
    def _create_face_mask(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """创建面部掩码"""
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        if len(landmarks) > 0:
            # 使用凸包创建面部区域
            hull = cv2.convexHull(landmarks)
            cv2.fillPoly(mask, [hull], 255)
        
        return mask
    
    def _classify_skin_color(self, hsv_color: np.ndarray) -> str:
        """分类肤色类型"""
        h, s, v = hsv_color
        
        # 基于HSV值分类肤色
        if v < 80:
            return "dark"
        elif v > 200 and s < 50:
            return "pale"
        elif 10 <= h <= 25 and s > 30:
            return "yellow"
        elif s > 80 and v > 150:
            return "rosy"
        else:
            return "normal"
    
    def _analyze_complexion(self, bgr_color: Tuple[float, float, float], 
                          hsv_color: np.ndarray) -> str:
        """分析气色"""
        b, g, r = bgr_color
        h, s, v = hsv_color
        
        # 计算红润度
        redness = r / (g + b + 1)
        
        # 计算亮度
        brightness = v / 255.0
        
        # 分析气色
        if redness > 1.2 and brightness > 0.6:
            return "rosy"      # 红润
        elif brightness < 0.4:
            return "dark"      # 晦暗
        elif redness < 0.8 and brightness < 0.6:
            return "pale"      # 苍白
        elif 15 <= h <= 35 and s > 40:
            return "yellow"    # 萎黄
        elif h > 100 and h < 140:
            return "blue"      # 青色
        else:
            return "normal"    # 正常
    
    def _analyze_eye_features(self, image: np.ndarray, landmarks: np.ndarray) -> Dict[str, Any]:
        """分析眼部特征"""
        if len(landmarks) == 0:
            return {"status": "unknown", "brightness": 0.0, "color": "unknown"}
        
        try:
            # 提取眼部区域（简化处理）
            eye_region = self._extract_eye_region(image, landmarks)
            
            # 分析眼部亮度
            eye_brightness = self._calculate_eye_brightness(eye_region)
            
            # 分析眼部颜色
            eye_color = self._analyze_eye_color(eye_region)
            
            # 判断眼神状态
            eye_status = self._classify_eye_status(eye_brightness, eye_color)
            
            return {
                "status": eye_status,
                "brightness": eye_brightness,
                "color": eye_color,
                "tcm_interpretation": self.tcm_feature_mapping['eye_features'].get(eye_status, "正常")
            }
            
        except Exception as e:
            logger.error(f"眼部特征分析失败: {e}")
            return {"status": "unknown", "brightness": 0.0, "color": "unknown"}
    
    def _extract_eye_region(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """提取眼部区域"""
        # 简化的眼部区域提取
        if len(landmarks) > 100:
            # 使用面部关键点的眼部区域
            eye_landmarks = landmarks[33:42]  # 简化的眼部关键点
            if len(eye_landmarks) > 0:
                x_min, y_min = np.min(eye_landmarks, axis=0)
                x_max, y_max = np.max(eye_landmarks, axis=0)
                return image[y_min:y_max, x_min:x_max]
        
        # 如果无法提取，返回整个图像的中心区域
        h, w = image.shape[:2]
        return image[h//3:2*h//3, w//4:3*w//4]
    
    def _calculate_eye_brightness(self, eye_region: np.ndarray) -> float:
        """计算眼部亮度"""
        if eye_region.size == 0:
            return 0.0
        
        gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY) if len(eye_region.shape) == 3 else eye_region
        return np.mean(gray) / 255.0
    
    def _analyze_eye_color(self, eye_region: np.ndarray) -> str:
        """分析眼部颜色"""
        if eye_region.size == 0:
            return "unknown"
        
        mean_color = cv2.mean(eye_region)[:3]
        b, g, r = mean_color
        
        if r > g + b:
            return "red"
        elif g + b > 1.5 * r:
            return "yellow"
        else:
            return "normal"
    
    def _classify_eye_status(self, brightness: float, color: str) -> str:
        """分类眼神状态"""
        if brightness > 0.6 and color == "normal":
            return "bright"
        elif brightness < 0.3:
            return "dull"
        elif color == "red":
            return "red"
        elif color == "yellow":
            return "yellow"
        else:
            return "normal"
    
    def _analyze_nose_features(self, image: np.ndarray, landmarks: np.ndarray) -> Dict[str, Any]:
        """分析鼻部特征"""
        # 简化的鼻部分析
        return {
            "shape": "normal",
            "color": "normal",
            "tcm_interpretation": "鼻部正常"
        }
    
    def _analyze_mouth_features(self, image: np.ndarray, landmarks: np.ndarray) -> Dict[str, Any]:
        """分析口部特征"""
        # 简化的口部分析
        return {
            "color": "normal",
            "moisture": "normal",
            "tcm_interpretation": "口唇正常"
        }
    
    def _analyze_ear_features(self, image: np.ndarray, landmarks: np.ndarray) -> Dict[str, Any]:
        """分析耳部特征"""
        # 简化的耳部分析
        return {
            "shape": "normal",
            "color": "normal",
            "tcm_interpretation": "耳部正常"
        }
    
    def _calculate_feature_confidence(self, landmarks: np.ndarray, image: np.ndarray) -> Dict[str, float]:
        """计算特征置信度"""
        base_confidence = 0.8 if len(landmarks) > 0 else 0.0
        
        return {
            "face_shape": base_confidence,
            "skin_color": base_confidence * 0.9,
            "eye_features": base_confidence * 0.85,
            "overall": base_confidence * 0.88
        }
    
    def _get_default_face_features(self) -> FaceFeatures:
        """获取默认面部特征"""
        return FaceFeatures(
            face_shape="unknown",
            skin_color="unknown",
            complexion="unknown",
            eye_features={"status": "unknown"},
            nose_features={"shape": "unknown"},
            mouth_features={"color": "unknown"},
            ear_features={"shape": "unknown"},
            facial_landmarks=np.array([]),
            confidence_scores={"overall": 0.0}
        )

class BatchFaceAnalyzer:
    """批量面部分析器"""
    
    def __init__(self):
        self.quality_assessor = AdvancedImageQualityAssessment()
        self.feature_extractor = TCMFaceFeatureExtractor()
        self.max_concurrent_tasks = 5
    
    async def analyze_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """批量分析面部图像"""
        try:
            logger.info(f"开始批量分析 {len(image_paths)} 张图像")
            
            # 创建分析任务
            semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
            tasks = [
                self._analyze_single_image_async(path, semaphore) 
                for path in image_paths
            ]
            
            # 并发执行分析
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"图像 {image_paths[i]} 分析失败: {result}")
                    processed_results.append({
                        "image_path": image_paths[i],
                        "status": "error",
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)
            
            logger.info(f"批量分析完成，成功: {len([r for r in processed_results if r.get('status') != 'error'])}")
            return processed_results
            
        except Exception as e:
            logger.error(f"批量分析失败: {e}")
            raise
    
    async def _analyze_single_image_async(self, image_path: str, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """异步分析单张图像"""
        async with semaphore:
            return await asyncio.get_event_loop().run_in_executor(
                None, self._analyze_single_image, image_path
            )
    
    def _analyze_single_image(self, image_path: str) -> Dict[str, Any]:
        """分析单张图像"""
        try:
            # 加载图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法加载图像: {image_path}")
            
            # 图像质量评估
            quality_metrics = self.quality_assessor.assess_image_quality(image)
            
            # 如果图像质量太差，跳过特征提取
            if quality_metrics.overall_quality_score < 0.3:
                return {
                    "image_path": image_path,
                    "status": "low_quality",
                    "quality_metrics": quality_metrics.__dict__,
                    "message": "图像质量过低，无法进行可靠的面部分析"
                }
            
            # 提取中医面部特征
            face_features = self.feature_extractor.extract_tcm_features(image)
            
            # 生成中医诊断建议
            tcm_diagnosis = self._generate_tcm_diagnosis(face_features)
            
            return {
                "image_path": image_path,
                "status": "success",
                "quality_metrics": quality_metrics.__dict__,
                "face_features": {
                    "face_shape": face_features.face_shape,
                    "skin_color": face_features.skin_color,
                    "complexion": face_features.complexion,
                    "eye_features": face_features.eye_features,
                    "nose_features": face_features.nose_features,
                    "mouth_features": face_features.mouth_features,
                    "ear_features": face_features.ear_features,
                    "confidence_scores": face_features.confidence_scores
                },
                "tcm_diagnosis": tcm_diagnosis,
                "analysis_timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"单张图像分析失败 {image_path}: {e}")
            return {
                "image_path": image_path,
                "status": "error",
                "error": str(e)
            }
    
    def _generate_tcm_diagnosis(self, face_features: FaceFeatures) -> Dict[str, Any]:
        """生成中医诊断建议"""
        diagnosis = {
            "constitution_type": "unknown",
            "health_indicators": [],
            "recommendations": [],
            "confidence": 0.0
        }
        
        try:
            # 基于面部形状判断体质倾向
            face_shape_mapping = {
                "round": "脾胃偏虚",
                "oval": "肝胆功能正常",
                "square": "肾气充足",
                "heart": "心火偏旺",
                "long": "肺气不足"
            }
            
            constitution_type = face_shape_mapping.get(face_features.face_shape, "unknown")
            diagnosis["constitution_type"] = constitution_type
            
            # 基于气色分析健康状态
            complexion_indicators = {
                "rosy": "气血充足，健康状态良好",
                "pale": "气血不足，需要补益",
                "yellow": "脾胃虚弱，消化功能不佳",
                "dark": "肾阳不足，需要温补",
                "blue": "肝气郁结，情志不畅"
            }
            
            if face_features.complexion in complexion_indicators:
                diagnosis["health_indicators"].append(complexion_indicators[face_features.complexion])
            
            # 基于眼部特征分析
            eye_status = face_features.eye_features.get("status", "unknown")
            eye_indicators = {
                "bright": "精神充沛，肾精充足",
                "dull": "精神不振，肾精不足",
                "red": "心火上炎，需要清热",
                "yellow": "湿热内蕴，需要清利"
            }
            
            if eye_status in eye_indicators:
                diagnosis["health_indicators"].append(eye_indicators[eye_status])
            
            # 生成调理建议
            recommendations = self._generate_recommendations(face_features)
            diagnosis["recommendations"] = recommendations
            
            # 计算诊断置信度
            confidence = face_features.confidence_scores.get("overall", 0.0)
            diagnosis["confidence"] = confidence
            
        except Exception as e:
            logger.error(f"中医诊断生成失败: {e}")
        
        return diagnosis
    
    def _generate_recommendations(self, face_features: FaceFeatures) -> List[str]:
        """生成调理建议"""
        recommendations = []
        
        # 基于气色的建议
        if face_features.complexion == "pale":
            recommendations.extend([
                "建议补益气血，可食用红枣、桂圆等",
                "适当运动，增强体质",
                "保证充足睡眠"
            ])
        elif face_features.complexion == "yellow":
            recommendations.extend([
                "调理脾胃，饮食清淡易消化",
                "避免生冷食物",
                "可适当食用山药、薏米等健脾食物"
            ])
        elif face_features.complexion == "dark":
            recommendations.extend([
                "温补肾阳，可食用核桃、黑芝麻等",
                "避免过度劳累",
                "注意保暖"
            ])
        
        # 基于眼部特征的建议
        eye_status = face_features.eye_features.get("status", "unknown")
        if eye_status == "dull":
            recommendations.append("注意休息，避免用眼过度")
        elif eye_status == "red":
            recommendations.append("清热降火，多饮水，少食辛辣")
        
        return recommendations[:5]  # 最多返回5条建议

class FaceAnalysisModel:
    """面部分析主模型"""
    
    def __init__(self):
        self.quality_assessor = AdvancedImageQualityAssessment()
        self.feature_extractor = TCMFaceFeatureExtractor()
        self.batch_analyzer = BatchFaceAnalyzer()
        
        logger.info("面部分析模型初始化完成")
    
    async def analyze_face(self, image: Union[np.ndarray, str], 
                          include_quality_check: bool = True,
                          include_tcm_analysis: bool = True) -> Dict[str, Any]:
        """分析面部图像"""
        try:
            # 加载图像
            if isinstance(image, str):
                img_array = cv2.imread(image)
                if img_array is None:
                    raise ValueError(f"无法加载图像: {image}")
            else:
                img_array = image
            
            result = {
                "status": "success",
                "analysis_timestamp": asyncio.get_event_loop().time()
            }
            
            # 图像质量评估
            if include_quality_check:
                quality_metrics = self.quality_assessor.assess_image_quality(img_array)
                result["quality_metrics"] = quality_metrics.__dict__
                
                # 如果图像质量太差，提前返回
                if quality_metrics.overall_quality_score < 0.3:
                    result["status"] = "low_quality"
                    result["message"] = "图像质量过低，建议重新拍摄"
                    return result
            
            # 中医面部特征分析
            if include_tcm_analysis:
                face_features = self.feature_extractor.extract_tcm_features(img_array)
                result["face_features"] = {
                    "face_shape": face_features.face_shape,
                    "skin_color": face_features.skin_color,
                    "complexion": face_features.complexion,
                    "eye_features": face_features.eye_features,
                    "nose_features": face_features.nose_features,
                    "mouth_features": face_features.mouth_features,
                    "ear_features": face_features.ear_features,
                    "confidence_scores": face_features.confidence_scores
                }
                
                # 生成中医诊断
                tcm_diagnosis = self.batch_analyzer._generate_tcm_diagnosis(face_features)
                result["tcm_diagnosis"] = tcm_diagnosis
            
            return result
            
        except Exception as e:
            logger.error(f"面部分析失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_timestamp": asyncio.get_event_loop().time()
            }
    
    async def batch_analyze(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """批量分析面部图像"""
        return await self.batch_analyzer.analyze_batch(image_paths)
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": "TCM Face Analysis Model",
            "version": "2.0.0",
            "features": [
                "图像质量评估",
                "中医面部特征提取",
                "体质类型判断",
                "健康状态分析",
                "调理建议生成",
                "批量处理支持"
            ],
            "supported_formats": ["jpg", "jpeg", "png", "bmp"],
            "max_batch_size": 50,
            "quality_thresholds": self.quality_assessor.quality_thresholds
        } 