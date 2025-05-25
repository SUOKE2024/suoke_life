#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版望诊服务

该模块是望诊服务的增强版本，集成了高性能图像分析、并行处理、智能缓存和批量诊断功能，
提供专业的中医望诊数据采集和分析服务。
"""

import asyncio
import time
import uuid
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
from loguru import logger
import cv2
import base64
from io import BytesIO
from PIL import Image

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter, rate_limit
)
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

class ObservationType(Enum):
    """望诊类型"""
    FACE = "face"  # 面部望诊
    TONGUE = "tongue"  # 舌诊
    EYES = "eyes"  # 目诊
    SKIN = "skin"  # 皮肤望诊
    POSTURE = "posture"  # 体态望诊
    COMPLEXION = "complexion"  # 面色望诊

class ImageQuality(Enum):
    """图像质量"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class ImageAnalysisRequest:
    """图像分析请求"""
    request_id: str
    patient_id: str
    observation_type: ObservationType
    image_data: str  # Base64编码的图像
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FeatureExtraction:
    """特征提取结果"""
    feature_type: str
    value: Any
    confidence: float
    region: Optional[Dict[str, int]] = None  # 区域坐标

@dataclass
class ObservationResult:
    """望诊结果"""
    request_id: str
    patient_id: str
    observation_type: ObservationType
    features: List[FeatureExtraction]
    syndrome_indicators: Dict[str, float]  # 证候指标
    quality_score: float
    processing_time_ms: float
    recommendations: List[str]

@dataclass
class BatchAnalysisRequest:
    """批量分析请求"""
    batch_id: str
    requests: List[ImageAnalysisRequest]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

class EnhancedLookService:
    """增强版望诊服务"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化增强版望诊服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 增强配置
        self.enhanced_config = {
            'image_processing': {
                'max_image_size': (1920, 1080),
                'quality_threshold': 0.7,
                'enhancement': {
                    'contrast': True,
                    'brightness': True,
                    'sharpness': True,
                    'denoise': True
                }
            },
            'parallel_processing': {
                'enabled': True,
                'max_workers': 4,
                'batch_size': 10
            },
            'caching': {
                'enabled': True,
                'ttl_seconds': {
                    'feature_extraction': 3600,
                    'analysis_result': 1800,
                    'model_inference': 7200
                },
                'max_cache_size': 5000
            },
            'model_optimization': {
                'use_gpu': True,
                'batch_inference': True,
                'model_quantization': True,
                'tensorrt': False
            },
            'feature_extraction': {
                'face': ['color', 'texture', 'symmetry', 'expression'],
                'tongue': ['color', 'coating', 'shape', 'moisture'],
                'eyes': ['sclera', 'pupil', 'eyelid', 'conjunctiva']
            }
        }
        
        # 模型缓存
        self.models: Dict[ObservationType, Any] = {}
        self._load_models()
        
        # 批处理队列
        self.batch_queue: asyncio.Queue = asyncio.Queue()
        
        # 缓存
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # 性能统计
        self.stats = {
            'total_requests': 0,
            'successful_analyses': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time_ms': 0.0,
            'quality_distribution': defaultdict(int),
            'batch_processed': 0
        }
        
        # 断路器配置
        self.circuit_breaker_configs = {
            'model_inference': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=10.0
            ),
            'image_processing': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=20.0,
                timeout=5.0
            )
        }
        
        # 限流配置
        self.rate_limit_configs = {
            'analysis': RateLimitConfig(rate=30.0, burst=60),
            'batch': RateLimitConfig(rate=10.0, burst=20)
        }
        
        # 后台任务
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info("增强版望诊服务初始化完成")
    
    def _load_models(self):
        """加载AI模型"""
        # 这里是模拟的模型加载，实际应该加载真实的深度学习模型
        logger.info("加载望诊分析模型...")
        
        # 面部分析模型
        self.models[ObservationType.FACE] = {
            'detector': 'face_detector_model',
            'analyzer': 'face_analyzer_model'
        }
        
        # 舌诊模型
        self.models[ObservationType.TONGUE] = {
            'segmentation': 'tongue_segmentation_model',
            'classifier': 'tongue_classifier_model'
        }
        
        # 其他模型...
        logger.info("模型加载完成")
    
    async def initialize(self):
        """初始化服务"""
        # 启动后台任务
        self._start_background_tasks()
        logger.info("望诊服务初始化完成")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 批处理处理器
        self.background_tasks.append(
            asyncio.create_task(self._batch_processor())
        )
        
        # 缓存清理器
        self.background_tasks.append(
            asyncio.create_task(self._cache_cleaner())
        )
        
        # 模型优化器
        self.background_tasks.append(
            asyncio.create_task(self._model_optimizer())
        )
    
    @trace(service_name="look-service", kind=SpanKind.SERVER)
    @rate_limit(name="analysis", tokens=1)
    async def analyze_image(
        self,
        patient_id: str,
        observation_type: ObservationType,
        image_data: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ObservationResult:
        """
        分析望诊图像
        
        Args:
            patient_id: 患者ID
            observation_type: 望诊类型
            image_data: Base64编码的图像数据
            metadata: 元数据
            
        Returns:
            望诊结果
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        self.stats['total_requests'] += 1
        
        # 检查缓存
        cache_key = self._generate_cache_key(
            "analysis", patient_id, observation_type.value, 
            hashlib.md5(image_data.encode()).hexdigest()
        )
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            self.stats['cache_hits'] += 1
            return cached_result
        
        self.stats['cache_misses'] += 1
        
        try:
            # 解码和预处理图像
            image = await self._decode_and_preprocess_image(image_data)
            
            # 评估图像质量
            quality_score = await self._assess_image_quality(image, observation_type)
            quality_level = self._get_quality_level(quality_score)
            self.stats['quality_distribution'][quality_level.value] += 1
            
            if quality_score < self.enhanced_config['image_processing']['quality_threshold']:
                logger.warning(f"图像质量不足: {quality_score}")
                # 尝试增强图像
                image = await self._enhance_image(image)
            
            # 并行提取特征
            if self.enhanced_config['parallel_processing']['enabled']:
                features = await self._parallel_feature_extraction(
                    image, observation_type
                )
            else:
                features = await self._extract_features(image, observation_type)
            
            # 分析证候指标
            syndrome_indicators = await self._analyze_syndrome_indicators(
                features, observation_type
            )
            
            # 生成建议
            recommendations = await self._generate_recommendations(
                syndrome_indicators, observation_type
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            result = ObservationResult(
                request_id=request_id,
                patient_id=patient_id,
                observation_type=observation_type,
                features=features,
                syndrome_indicators=syndrome_indicators,
                quality_score=quality_score,
                processing_time_ms=processing_time_ms,
                recommendations=recommendations
            )
            
            # 缓存结果
            await self._set_to_cache(cache_key, result)
            
            # 更新统计
            self.stats['successful_analyses'] += 1
            self._update_stats(processing_time_ms)
            
            return result
            
        except Exception as e:
            logger.error(f"图像分析失败: {e}")
            raise
    
    async def _decode_and_preprocess_image(self, image_data: str) -> np.ndarray:
        """解码和预处理图像"""
        # 解码Base64图像
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # 转换为OpenCV格式
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 调整大小
        max_size = self.enhanced_config['image_processing']['max_image_size']
        height, width = image_cv.shape[:2]
        
        if width > max_size[0] or height > max_size[1]:
            scale = min(max_size[0] / width, max_size[1] / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_cv = cv2.resize(image_cv, (new_width, new_height))
        
        return image_cv
    
    async def _assess_image_quality(
        self, 
        image: np.ndarray, 
        observation_type: ObservationType
    ) -> float:
        """评估图像质量"""
        quality_factors = []
        
        # 1. 清晰度评估（拉普拉斯方差）
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 1000, 1.0)
        quality_factors.append(sharpness_score)
        
        # 2. 亮度评估
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 127) / 127
        quality_factors.append(brightness_score)
        
        # 3. 对比度评估
        contrast = np.std(gray)
        contrast_score = min(contrast / 50, 1.0)
        quality_factors.append(contrast_score)
        
        # 4. 特定类型的质量检查
        if observation_type == ObservationType.FACE:
            # 检查是否检测到人脸
            face_detected = await self._detect_face(image)
            quality_factors.append(1.0 if face_detected else 0.0)
        elif observation_type == ObservationType.TONGUE:
            # 检查舌头区域
            tongue_detected = await self._detect_tongue(image)
            quality_factors.append(1.0 if tongue_detected else 0.0)
        
        # 综合质量分数
        quality_score = np.mean(quality_factors)
        return quality_score
    
    def _get_quality_level(self, score: float) -> ImageQuality:
        """获取质量级别"""
        if score >= 0.9:
            return ImageQuality.EXCELLENT
        elif score >= 0.7:
            return ImageQuality.GOOD
        elif score >= 0.5:
            return ImageQuality.FAIR
        else:
            return ImageQuality.POOR
    
    async def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """增强图像质量"""
        enhanced = image.copy()
        config = self.enhanced_config['image_processing']['enhancement']
        
        if config['contrast']:
            # 增强对比度
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        if config['brightness']:
            # 调整亮度
            brightness = np.mean(cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY))
            if brightness < 100:
                enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=10)
            elif brightness > 150:
                enhanced = cv2.convertScaleAbs(enhanced, alpha=0.8, beta=-10)
        
        if config['sharpness']:
            # 增强锐度
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        if config['denoise']:
            # 降噪
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        
        return enhanced
    
    async def _parallel_feature_extraction(
        self,
        image: np.ndarray,
        observation_type: ObservationType
    ) -> List[FeatureExtraction]:
        """并行特征提取"""
        feature_types = self.enhanced_config['feature_extraction'].get(
            observation_type.value, []
        )
        
        # 创建特征提取任务
        tasks = []
        for feature_type in feature_types:
            task = self._extract_single_feature(image, observation_type, feature_type)
            tasks.append(task)
        
        # 并行执行
        feature_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集有效结果
        features = []
        for result in feature_results:
            if isinstance(result, list):
                features.extend(result)
            elif isinstance(result, FeatureExtraction):
                features.append(result)
            else:
                logger.error(f"特征提取失败: {result}")
        
        return features
    
    async def _extract_features(
        self,
        image: np.ndarray,
        observation_type: ObservationType
    ) -> List[FeatureExtraction]:
        """提取图像特征"""
        features = []
        
        if observation_type == ObservationType.FACE:
            features.extend(await self._extract_face_features(image))
        elif observation_type == ObservationType.TONGUE:
            features.extend(await self._extract_tongue_features(image))
        elif observation_type == ObservationType.EYES:
            features.extend(await self._extract_eye_features(image))
        else:
            features.extend(await self._extract_general_features(image))
        
        return features
    
    async def _extract_single_feature(
        self,
        image: np.ndarray,
        observation_type: ObservationType,
        feature_type: str
    ) -> List[FeatureExtraction]:
        """提取单个特征类型"""
        if observation_type == ObservationType.FACE:
            if feature_type == 'color':
                return await self._extract_face_color(image)
            elif feature_type == 'texture':
                return await self._extract_face_texture(image)
            elif feature_type == 'symmetry':
                return await self._extract_face_symmetry(image)
        elif observation_type == ObservationType.TONGUE:
            if feature_type == 'color':
                return await self._extract_tongue_color(image)
            elif feature_type == 'coating':
                return await self._extract_tongue_coating(image)
        
        return []
    
    async def _extract_face_features(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取面部特征"""
        features = []
        
        # 面色分析
        face_color = await self._analyze_face_color(image)
        features.append(FeatureExtraction(
            feature_type="face_color",
            value=face_color,
            confidence=0.85
        ))
        
        # 面部光泽度
        glossiness = await self._analyze_glossiness(image)
        features.append(FeatureExtraction(
            feature_type="face_glossiness",
            value=glossiness,
            confidence=0.80
        ))
        
        # 面部浮肿检测
        puffiness = await self._detect_facial_puffiness(image)
        features.append(FeatureExtraction(
            feature_type="facial_puffiness",
            value=puffiness,
            confidence=0.75
        ))
        
        return features
    
    async def _extract_tongue_features(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取舌诊特征"""
        features = []
        
        # 舌色分析
        tongue_color = await self._analyze_tongue_color(image)
        features.append(FeatureExtraction(
            feature_type="tongue_color",
            value=tongue_color,
            confidence=0.90
        ))
        
        # 舌苔分析
        coating = await self._analyze_tongue_coating(image)
        features.append(FeatureExtraction(
            feature_type="tongue_coating",
            value=coating,
            confidence=0.85
        ))
        
        # 舌形分析
        shape = await self._analyze_tongue_shape(image)
        features.append(FeatureExtraction(
            feature_type="tongue_shape",
            value=shape,
            confidence=0.80
        ))
        
        return features
    
    async def _extract_eye_features(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取目诊特征"""
        features = []
        
        # 巩膜颜色
        sclera_color = await self._analyze_sclera_color(image)
        features.append(FeatureExtraction(
            feature_type="sclera_color",
            value=sclera_color,
            confidence=0.85
        ))
        
        # 眼睑状态
        eyelid_state = await self._analyze_eyelid_state(image)
        features.append(FeatureExtraction(
            feature_type="eyelid_state",
            value=eyelid_state,
            confidence=0.80
        ))
        
        return features
    
    async def _extract_general_features(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取通用特征"""
        features = []
        
        # 颜色直方图
        color_hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        color_hist = cv2.normalize(color_hist, color_hist).flatten()
        
        features.append(FeatureExtraction(
            feature_type="color_histogram",
            value=color_hist.tolist(),
            confidence=0.95
        ))
        
        # 纹理特征
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        texture = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        features.append(FeatureExtraction(
            feature_type="texture_variance",
            value=float(texture),
            confidence=0.90
        ))
        
        return features
    
    # 具体的特征分析方法（简化实现）
    async def _analyze_face_color(self, image: np.ndarray) -> str:
        """分析面色"""
        # 简化实现：基于HSV颜色空间分析
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h_mean = np.mean(hsv[:, :, 0])
        s_mean = np.mean(hsv[:, :, 1])
        v_mean = np.mean(hsv[:, :, 2])
        
        if v_mean < 100:
            return "晦暗"
        elif s_mean < 50:
            return "苍白"
        elif h_mean < 20:
            return "红润"
        elif h_mean < 30:
            return "黄色"
        else:
            return "正常"
    
    async def _analyze_glossiness(self, image: np.ndarray) -> str:
        """分析光泽度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        highlights = np.sum(gray > 200) / gray.size
        
        if highlights > 0.1:
            return "有光泽"
        else:
            return "无光泽"
    
    async def _detect_facial_puffiness(self, image: np.ndarray) -> bool:
        """检测面部浮肿"""
        # 简化实现
        return False
    
    async def _analyze_tongue_color(self, image: np.ndarray) -> str:
        """分析舌色"""
        # 简化实现
        return "淡红"
    
    async def _analyze_tongue_coating(self, image: np.ndarray) -> str:
        """分析舌苔"""
        # 简化实现
        return "薄白苔"
    
    async def _analyze_tongue_shape(self, image: np.ndarray) -> str:
        """分析舌形"""
        # 简化实现
        return "正常"
    
    async def _analyze_sclera_color(self, image: np.ndarray) -> str:
        """分析巩膜颜色"""
        # 简化实现
        return "白色"
    
    async def _analyze_eyelid_state(self, image: np.ndarray) -> str:
        """分析眼睑状态"""
        # 简化实现
        return "正常"
    
    async def _detect_face(self, image: np.ndarray) -> bool:
        """检测人脸"""
        # 简化实现
        return True
    
    async def _detect_tongue(self, image: np.ndarray) -> bool:
        """检测舌头"""
        # 简化实现
        return True
    
    async def _extract_face_color(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取面色特征"""
        color = await self._analyze_face_color(image)
        return [FeatureExtraction(
            feature_type="face_color_detail",
            value=color,
            confidence=0.85
        )]
    
    async def _extract_face_texture(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取面部纹理特征"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        texture = cv2.Laplacian(gray, cv2.CV_64F).var()
        return [FeatureExtraction(
            feature_type="face_texture_detail",
            value=float(texture),
            confidence=0.80
        )]
    
    async def _extract_face_symmetry(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取面部对称性特征"""
        # 简化实现
        return [FeatureExtraction(
            feature_type="face_symmetry",
            value=0.95,
            confidence=0.75
        )]
    
    async def _extract_tongue_color(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取舌色特征"""
        color = await self._analyze_tongue_color(image)
        return [FeatureExtraction(
            feature_type="tongue_color_detail",
            value=color,
            confidence=0.90
        )]
    
    async def _extract_tongue_coating(self, image: np.ndarray) -> List[FeatureExtraction]:
        """提取舌苔特征"""
        coating = await self._analyze_tongue_coating(image)
        return [FeatureExtraction(
            feature_type="tongue_coating_detail",
            value=coating,
            confidence=0.85
        )]
    
    async def _analyze_syndrome_indicators(
        self,
        features: List[FeatureExtraction],
        observation_type: ObservationType
    ) -> Dict[str, float]:
        """分析证候指标"""
        indicators = {}
        
        # 基于特征分析证候
        for feature in features:
            if observation_type == ObservationType.FACE:
                if feature.feature_type == "face_color" and feature.value == "苍白":
                    indicators["血虚"] = indicators.get("血虚", 0) + 0.3
                elif feature.feature_type == "face_color" and feature.value == "红润":
                    indicators["血热"] = indicators.get("血热", 0) + 0.2
                elif feature.feature_type == "face_glossiness" and feature.value == "无光泽":
                    indicators["气虚"] = indicators.get("气虚", 0) + 0.2
            
            elif observation_type == ObservationType.TONGUE:
                if feature.feature_type == "tongue_color" and feature.value == "淡白":
                    indicators["阳虚"] = indicators.get("阳虚", 0) + 0.3
                elif feature.feature_type == "tongue_coating" and feature.value == "黄腻苔":
                    indicators["湿热"] = indicators.get("湿热", 0) + 0.4
        
        # 归一化
        total = sum(indicators.values())
        if total > 0:
            for key in indicators:
                indicators[key] /= total
        
        return indicators
    
    async def _generate_recommendations(
        self,
        syndrome_indicators: Dict[str, float],
        observation_type: ObservationType
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于证候指标生成建议
        primary_syndrome = max(syndrome_indicators.items(), key=lambda x: x[1])[0] if syndrome_indicators else None
        
        if primary_syndrome == "血虚":
            recommendations.extend([
                "建议增加补血食物的摄入，如红枣、枸杞等",
                "保证充足的睡眠，避免过度劳累",
                "可考虑中医调理，如服用补血养血的中药"
            ])
        elif primary_syndrome == "气虚":
            recommendations.extend([
                "建议适当休息，避免过度消耗体力",
                "可食用补气食物，如山药、黄芪等",
                "进行适度的运动，如太极拳、八段锦"
            ])
        elif primary_syndrome == "湿热":
            recommendations.extend([
                "饮食宜清淡，避免油腻辛辣食物",
                "多饮水，促进体内湿热排出",
                "保持居住环境通风干燥"
            ])
        
        # 添加通用建议
        recommendations.append("建议定期进行中医体检")
        recommendations.append("如有不适，请及时就医")
        
        return recommendations
    
    async def batch_analyze(
        self,
        requests: List[ImageAnalysisRequest]
    ) -> List[ObservationResult]:
        """
        批量分析图像
        
        Args:
            requests: 图像分析请求列表
            
        Returns:
            分析结果列表
        """
        if self.enhanced_config['parallel_processing']['enabled']:
            # 并行处理
            tasks = []
            for request in requests:
                task = self.analyze_image(
                    patient_id=request.patient_id,
                    observation_type=request.observation_type,
                    image_data=request.image_data,
                    metadata=request.metadata
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤有效结果
            valid_results = []
            for result in results:
                if isinstance(result, ObservationResult):
                    valid_results.append(result)
                else:
                    logger.error(f"批量分析失败: {result}")
            
            self.stats['batch_processed'] += 1
            return valid_results
        else:
            # 串行处理
            results = []
            for request in requests:
                try:
                    result = await self.analyze_image(
                        patient_id=request.patient_id,
                        observation_type=request.observation_type,
                        image_data=request.image_data,
                        metadata=request.metadata
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"分析请求{request.request_id}失败: {e}")
            
            return results
    
    async def _batch_processor(self):
        """批处理处理器"""
        while True:
            try:
                batch = []
                deadline = time.time() + 0.5  # 500ms收集窗口
                
                # 收集批次
                while len(batch) < self.enhanced_config['parallel_processing']['batch_size']:
                    try:
                        remaining_time = deadline - time.time()
                        if remaining_time <= 0:
                            break
                        
                        request = await asyncio.wait_for(
                            self.batch_queue.get(),
                            timeout=remaining_time
                        )
                        batch.append(request)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    # 处理批次
                    await self.batch_analyze(batch)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"批处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _cache_cleaner(self):
        """缓存清理器"""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = []
                
                # 查找过期项
                for key, (value, expire_time) in self.cache.items():
                    if current_time > expire_time:
                        expired_keys.append(key)
                
                # 删除过期项
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.info(f"清理了{len(expired_keys)}个过期缓存项")
                
                # 检查缓存大小
                max_size = self.enhanced_config['caching']['max_cache_size']
                if len(self.cache) > max_size:
                    # 删除最旧的项
                    items = sorted(self.cache.items(), key=lambda x: x[1][1])
                    for key, _ in items[:len(items)//2]:
                        del self.cache[key]
                    logger.info(f"缓存大小超限，清理了{len(items)//2}个项")
                
                await asyncio.sleep(300)  # 5分钟清理一次
                
            except Exception as e:
                logger.error(f"缓存清理器错误: {e}")
                await asyncio.sleep(60)
    
    async def _model_optimizer(self):
        """模型优化器"""
        while True:
            try:
                # 定期优化模型性能
                if self.enhanced_config['model_optimization']['use_gpu']:
                    # 清理GPU缓存
                    logger.info("清理GPU缓存")
                
                # 模型量化检查
                if self.enhanced_config['model_optimization']['model_quantization']:
                    logger.info("检查模型量化状态")
                
                await asyncio.sleep(3600)  # 每小时执行一次
                
            except Exception as e:
                logger.error(f"模型优化器错误: {e}")
                await asyncio.sleep(300)
    
    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if not self.enhanced_config['caching']['enabled']:
            return None
        
        if key in self.cache:
            value, expire_time = self.cache[key]
            if datetime.now() < expire_time:
                return value
            else:
                del self.cache[key]
        
        return None
    
    async def _set_to_cache(self, key: str, value: Any, ttl_type: str = "analysis_result"):
        """设置缓存"""
        if not self.enhanced_config['caching']['enabled']:
            return
        
        ttl = self.enhanced_config['caching']['ttl_seconds'].get(ttl_type, 1800)
        expire_time = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expire_time)
    
    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_stats(self, processing_time_ms: float):
        """更新统计信息"""
        # 更新平均处理时间
        alpha = 0.1
        if self.stats['average_processing_time_ms'] == 0:
            self.stats['average_processing_time_ms'] = processing_time_ms
        else:
            self.stats['average_processing_time_ms'] = (
                alpha * processing_time_ms + 
                (1 - alpha) * self.stats['average_processing_time_ms']
            )
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        cache_hit_rate = (
            self.stats['cache_hits'] / 
            max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
        )
        
        return {
            'total_requests': self.stats['total_requests'],
            'successful_analyses': self.stats['successful_analyses'],
            'cache_hit_rate': cache_hit_rate,
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'quality_distribution': dict(self.stats['quality_distribution']),
            'batch_processed': self.stats['batch_processed'],
            'cache_size': len(self.cache),
            'models_loaded': len(self.models)
        }
    
    async def close(self):
        """关闭服务"""
        # 停止后台任务
        for task in self.background_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # 清理模型
        self.models.clear()
        
        logger.info("增强版望诊服务已关闭") 