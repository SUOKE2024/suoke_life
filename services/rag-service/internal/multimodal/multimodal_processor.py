#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
多模态处理器
支持文本、图像、音频等多种模态的处理、特征提取和融合
"""

import asyncio
import base64
import io
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from PIL import Image
import cv2
from loguru import logger

from ..observability.metrics import MetricsCollector


class ModalityType(str, Enum):
    """模态类型"""
    TEXT = "text"                      # 文本
    IMAGE = "image"                    # 图像
    AUDIO = "audio"                    # 音频
    VIDEO = "video"                    # 视频
    STRUCTURED = "structured"          # 结构化数据
    SENSOR = "sensor"                  # 传感器数据


class ProcessingTask(str, Enum):
    """处理任务类型"""
    FEATURE_EXTRACTION = "feature_extraction"    # 特征提取
    CLASSIFICATION = "classification"            # 分类
    DETECTION = "detection"                      # 检测
    SEGMENTATION = "segmentation"                # 分割
    RECOGNITION = "recognition"                  # 识别
    ANALYSIS = "analysis"                        # 分析
    FUSION = "fusion"                           # 融合


@dataclass
class ModalityData:
    """模态数据"""
    modality_type: ModalityType
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    features: Optional[np.ndarray] = None
    confidence: float = 1.0
    source: str = ""
    timestamp: str = ""


@dataclass
class ProcessingResult:
    """处理结果"""
    task_type: ProcessingTask
    modality_type: ModalityType
    result: Any
    features: Optional[np.ndarray] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


@dataclass
class FusionResult:
    """融合结果"""
    fused_features: np.ndarray
    modality_weights: Dict[ModalityType, float] = field(default_factory=dict)
    fusion_confidence: float = 0.0
    fusion_method: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        self.supported_tasks = [
            ProcessingTask.FEATURE_EXTRACTION,
            ProcessingTask.CLASSIFICATION,
            ProcessingTask.ANALYSIS
        ]
    
    async def process(
        self,
        text_data: ModalityData,
        task: ProcessingTask,
        **kwargs
    ) -> ProcessingResult:
        """处理文本数据"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if task == ProcessingTask.FEATURE_EXTRACTION:
                result = await self._extract_text_features(text_data.data)
            elif task == ProcessingTask.CLASSIFICATION:
                result = await self._classify_text(text_data.data)
            elif task == ProcessingTask.ANALYSIS:
                result = await self._analyze_text(text_data.data)
            else:
                raise ValueError(f"不支持的文本处理任务: {task}")
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                task_type=task,
                modality_type=ModalityType.TEXT,
                result=result,
                confidence=0.8,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"文本处理失败: {e}")
            return ProcessingResult(
                task_type=task,
                modality_type=ModalityType.TEXT,
                result=None,
                confidence=0.0
            )
    
    async def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """提取文本特征"""
        features = {
            "length": len(text),
            "word_count": len(text.split()),
            "char_count": len(text),
            "sentence_count": text.count('。') + text.count('！') + text.count('？'),
            "contains_medical_terms": self._contains_medical_terms(text),
            "sentiment": self._analyze_sentiment(text),
            "keywords": self._extract_keywords(text),
            "entities": self._extract_entities(text)
        }
        return features
    
    async def _classify_text(self, text: str) -> Dict[str, Any]:
        """文本分类"""
        # 简化的中医文本分类
        categories = {
            "症状描述": 0.0,
            "体质咨询": 0.0,
            "方剂询问": 0.0,
            "养生保健": 0.0,
            "疾病咨询": 0.0
        }
        
        # 基于关键词的简单分类
        if any(word in text for word in ['疼', '痛', '不舒服', '症状']):
            categories["症状描述"] = 0.8
        elif any(word in text for word in ['体质', '是什么体质']):
            categories["体质咨询"] = 0.8
        elif any(word in text for word in ['方剂', '汤', '丸', '散']):
            categories["方剂询问"] = 0.8
        elif any(word in text for word in ['养生', '保健', '调理']):
            categories["养生保健"] = 0.8
        else:
            categories["疾病咨询"] = 0.6
        
        return {
            "categories": categories,
            "predicted_category": max(categories, key=categories.get),
            "confidence": max(categories.values())
        }
    
    async def _analyze_text(self, text: str) -> Dict[str, Any]:
        """文本分析"""
        analysis = {
            "complexity": self._calculate_complexity(text),
            "readability": self._calculate_readability(text),
            "medical_relevance": self._calculate_medical_relevance(text),
            "urgency_level": self._assess_urgency(text),
            "emotional_tone": self._analyze_emotional_tone(text)
        }
        return analysis
    
    def _contains_medical_terms(self, text: str) -> bool:
        """检查是否包含医学术语"""
        medical_terms = [
            '症状', '疾病', '治疗', '药物', '中药', '方剂',
            '体质', '辨证', '脏腑', '经络', '穴位', '针灸'
        ]
        return any(term in text for term in medical_terms)
    
    def _analyze_sentiment(self, text: str) -> str:
        """情感分析"""
        positive_words = ['好', '舒服', '改善', '有效', '满意']
        negative_words = ['痛', '难受', '不舒服', '严重', '担心']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化的关键词提取
        import jieba
        words = jieba.cut(text)
        keywords = [word for word in words if len(word) > 1]
        return keywords[:10]  # 返回前10个关键词
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """实体提取"""
        entities = []
        
        # 简化的实体识别
        medical_entities = [
            '头痛', '失眠', '疲劳', '腹痛', '咳嗽',
            '人参', '黄芪', '当归', '甘草',
            '四君子汤', '六味地黄丸'
        ]
        
        for entity in medical_entities:
            if entity in text:
                entities.append({
                    "text": entity,
                    "type": "medical_term",
                    "confidence": 0.8
                })
        
        return entities
    
    def _calculate_complexity(self, text: str) -> float:
        """计算文本复杂度"""
        # 基于字符数、词汇数等计算复杂度
        char_count = len(text)
        word_count = len(text.split())
        
        complexity = min((char_count / 100 + word_count / 20) / 2, 1.0)
        return complexity
    
    def _calculate_readability(self, text: str) -> float:
        """计算可读性"""
        # 简化的可读性计算
        avg_word_length = len(text) / max(len(text.split()), 1)
        readability = max(0, 1 - (avg_word_length - 2) / 10)
        return min(readability, 1.0)
    
    def _calculate_medical_relevance(self, text: str) -> float:
        """计算医学相关性"""
        medical_terms = [
            '症状', '疾病', '治疗', '药物', '中药', '方剂',
            '体质', '辨证', '脏腑', '经络', '穴位', '针灸'
        ]
        
        relevance = sum(1 for term in medical_terms if term in text) / len(medical_terms)
        return min(relevance, 1.0)
    
    def _assess_urgency(self, text: str) -> str:
        """评估紧急程度"""
        urgent_keywords = ['急', '严重', '紧急', '疼痛', '出血']
        moderate_keywords = ['不舒服', '担心', '问题']
        
        if any(keyword in text for keyword in urgent_keywords):
            return "high"
        elif any(keyword in text for keyword in moderate_keywords):
            return "medium"
        else:
            return "low"
    
    def _analyze_emotional_tone(self, text: str) -> Dict[str, float]:
        """分析情感色调"""
        emotions = {
            "anxiety": 0.0,
            "concern": 0.0,
            "hope": 0.0,
            "satisfaction": 0.0
        }
        
        anxiety_words = ['担心', '焦虑', '害怕', '紧张']
        concern_words = ['关心', '在意', '注意']
        hope_words = ['希望', '期待', '想要']
        satisfaction_words = ['满意', '好', '舒服', '有效']
        
        for word in anxiety_words:
            if word in text:
                emotions["anxiety"] += 0.2
        
        for word in concern_words:
            if word in text:
                emotions["concern"] += 0.2
        
        for word in hope_words:
            if word in text:
                emotions["hope"] += 0.2
        
        for word in satisfaction_words:
            if word in text:
                emotions["satisfaction"] += 0.2
        
        # 归一化
        for emotion in emotions:
            emotions[emotion] = min(emotions[emotion], 1.0)
        
        return emotions


class ImageProcessor:
    """图像处理器"""
    
    def __init__(self):
        self.supported_tasks = [
            ProcessingTask.FEATURE_EXTRACTION,
            ProcessingTask.CLASSIFICATION,
            ProcessingTask.DETECTION,
            ProcessingTask.ANALYSIS
        ]
    
    async def process(
        self,
        image_data: ModalityData,
        task: ProcessingTask,
        **kwargs
    ) -> ProcessingResult:
        """处理图像数据"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 预处理图像
            image = self._preprocess_image(image_data.data)
            
            if task == ProcessingTask.FEATURE_EXTRACTION:
                result = await self._extract_image_features(image)
            elif task == ProcessingTask.CLASSIFICATION:
                result = await self._classify_image(image)
            elif task == ProcessingTask.DETECTION:
                result = await self._detect_objects(image)
            elif task == ProcessingTask.ANALYSIS:
                result = await self._analyze_image(image)
            else:
                raise ValueError(f"不支持的图像处理任务: {task}")
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                task_type=task,
                modality_type=ModalityType.IMAGE,
                result=result,
                confidence=0.7,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"图像处理失败: {e}")
            return ProcessingResult(
                task_type=task,
                modality_type=ModalityType.IMAGE,
                result=None,
                confidence=0.0
            )
    
    def _preprocess_image(self, image_data: Any) -> np.ndarray:
        """预处理图像"""
        if isinstance(image_data, str):
            # Base64编码的图像
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image = np.array(image)
        elif isinstance(image_data, Image.Image):
            image = np.array(image_data)
        elif isinstance(image_data, np.ndarray):
            image = image_data
        else:
            raise ValueError("不支持的图像数据格式")
        
        # 转换为RGB格式
        if len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    
    async def _extract_image_features(self, image: np.ndarray) -> Dict[str, Any]:
        """提取图像特征"""
        features = {
            "shape": image.shape,
            "mean_color": np.mean(image, axis=(0, 1)).tolist(),
            "brightness": np.mean(image),
            "contrast": np.std(image),
            "edges": self._detect_edges(image),
            "texture": self._analyze_texture(image),
            "color_distribution": self._analyze_color_distribution(image)
        }
        return features
    
    async def _classify_image(self, image: np.ndarray) -> Dict[str, Any]:
        """图像分类"""
        # 简化的医学图像分类
        categories = {
            "舌象": 0.0,
            "脉象": 0.0,
            "面色": 0.0,
            "皮肤": 0.0,
            "其他": 0.5
        }
        
        # 基于颜色和纹理的简单分类
        mean_color = np.mean(image, axis=(0, 1))
        
        # 舌象通常偏红色
        if mean_color[0] > mean_color[1] and mean_color[0] > mean_color[2]:
            categories["舌象"] = 0.6
        
        # 简化分类逻辑
        predicted_category = max(categories, key=categories.get)
        
        return {
            "categories": categories,
            "predicted_category": predicted_category,
            "confidence": max(categories.values())
        }
    
    async def _detect_objects(self, image: np.ndarray) -> Dict[str, Any]:
        """目标检测"""
        # 简化的目标检测
        detections = []
        
        # 检测人脸区域（简化）
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            detections.append({
                "class": "face",
                "bbox": [x, y, w, h],
                "confidence": 0.8
            })
        
        return {
            "detections": detections,
            "detection_count": len(detections)
        }
    
    async def _analyze_image(self, image: np.ndarray) -> Dict[str, Any]:
        """图像分析"""
        analysis = {
            "quality": self._assess_image_quality(image),
            "medical_relevance": self._assess_medical_relevance(image),
            "diagnostic_value": self._assess_diagnostic_value(image),
            "clarity": self._assess_clarity(image)
        }
        return analysis
    
    def _detect_edges(self, image: np.ndarray) -> int:
        """边缘检测"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return int(np.sum(edges > 0))
    
    def _analyze_texture(self, image: np.ndarray) -> Dict[str, float]:
        """纹理分析"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 计算纹理特征
        texture_features = {
            "variance": float(np.var(gray)),
            "entropy": self._calculate_entropy(gray),
            "smoothness": float(1 - 1 / (1 + np.var(gray)))
        }
        
        return texture_features
    
    def _analyze_color_distribution(self, image: np.ndarray) -> Dict[str, Any]:
        """颜色分布分析"""
        # 计算颜色直方图
        hist_r = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([image], [2], None, [256], [0, 256])
        
        return {
            "dominant_colors": self._find_dominant_colors(image),
            "color_variance": {
                "r": float(np.var(hist_r)),
                "g": float(np.var(hist_g)),
                "b": float(np.var(hist_b))
            }
        }
    
    def _find_dominant_colors(self, image: np.ndarray, k: int = 3) -> List[List[int]]:
        """查找主要颜色"""
        # 简化的主要颜色提取
        pixels = image.reshape(-1, 3)
        
        # 使用K-means聚类（简化版本）
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(pixels)
        
        dominant_colors = kmeans.cluster_centers_.astype(int).tolist()
        return dominant_colors
    
    def _calculate_entropy(self, image: np.ndarray) -> float:
        """计算图像熵"""
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = hist.flatten()
        hist = hist[hist > 0]  # 移除零值
        
        # 归一化
        hist = hist / np.sum(hist)
        
        # 计算熵
        entropy = -np.sum(hist * np.log2(hist))
        return float(entropy)
    
    def _assess_image_quality(self, image: np.ndarray) -> float:
        """评估图像质量"""
        # 基于清晰度、亮度、对比度评估质量
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 拉普拉斯方差（清晰度）
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 亮度
        brightness = np.mean(gray)
        
        # 对比度
        contrast = np.std(gray)
        
        # 综合评分
        quality = min((laplacian_var / 1000 + brightness / 255 + contrast / 128) / 3, 1.0)
        return quality
    
    def _assess_medical_relevance(self, image: np.ndarray) -> float:
        """评估医学相关性"""
        # 简化的医学相关性评估
        # 基于颜色分布、纹理等特征
        
        # 检查是否有皮肤色调
        mean_color = np.mean(image, axis=(0, 1))
        skin_tone_score = 0.0
        
        # 简单的皮肤色调检测
        if 100 < mean_color[0] < 200 and 80 < mean_color[1] < 180 and 60 < mean_color[2] < 160:
            skin_tone_score = 0.5
        
        # 纹理复杂度
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        texture_complexity = np.std(gray) / 255
        
        relevance = (skin_tone_score + texture_complexity) / 2
        return min(relevance, 1.0)
    
    def _assess_diagnostic_value(self, image: np.ndarray) -> float:
        """评估诊断价值"""
        # 基于图像质量和医学相关性
        quality = self._assess_image_quality(image)
        relevance = self._assess_medical_relevance(image)
        
        diagnostic_value = (quality * 0.6 + relevance * 0.4)
        return diagnostic_value
    
    def _assess_clarity(self, image: np.ndarray) -> float:
        """评估清晰度"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 归一化清晰度分数
        clarity = min(laplacian_var / 1000, 1.0)
        return clarity


class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        self.supported_tasks = [
            ProcessingTask.FEATURE_EXTRACTION,
            ProcessingTask.RECOGNITION,
            ProcessingTask.ANALYSIS
        ]
    
    async def process(
        self,
        audio_data: ModalityData,
        task: ProcessingTask,
        **kwargs
    ) -> ProcessingResult:
        """处理音频数据"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if task == ProcessingTask.FEATURE_EXTRACTION:
                result = await self._extract_audio_features(audio_data.data)
            elif task == ProcessingTask.RECOGNITION:
                result = await self._recognize_speech(audio_data.data)
            elif task == ProcessingTask.ANALYSIS:
                result = await self._analyze_audio(audio_data.data)
            else:
                raise ValueError(f"不支持的音频处理任务: {task}")
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                task_type=task,
                modality_type=ModalityType.AUDIO,
                result=result,
                confidence=0.6,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"音频处理失败: {e}")
            return ProcessingResult(
                task_type=task,
                modality_type=ModalityType.AUDIO,
                result=None,
                confidence=0.0
            )
    
    async def _extract_audio_features(self, audio_data: Any) -> Dict[str, Any]:
        """提取音频特征"""
        # 简化的音频特征提取
        features = {
            "duration": self._get_duration(audio_data),
            "sample_rate": self._get_sample_rate(audio_data),
            "energy": self._calculate_energy(audio_data),
            "pitch": self._extract_pitch(audio_data),
            "spectral_features": self._extract_spectral_features(audio_data)
        }
        return features
    
    async def _recognize_speech(self, audio_data: Any) -> Dict[str, Any]:
        """语音识别"""
        # 简化的语音识别
        recognition_result = {
            "text": "这是模拟的语音识别结果",
            "confidence": 0.8,
            "language": "zh-CN",
            "words": [
                {"word": "这是", "confidence": 0.9, "start_time": 0.0, "end_time": 0.5},
                {"word": "模拟的", "confidence": 0.8, "start_time": 0.5, "end_time": 1.0},
                {"word": "语音识别", "confidence": 0.9, "start_time": 1.0, "end_time": 1.8},
                {"word": "结果", "confidence": 0.8, "start_time": 1.8, "end_time": 2.2}
            ]
        }
        return recognition_result
    
    async def _analyze_audio(self, audio_data: Any) -> Dict[str, Any]:
        """音频分析"""
        analysis = {
            "voice_quality": self._assess_voice_quality(audio_data),
            "emotional_state": self._analyze_emotional_state(audio_data),
            "health_indicators": self._extract_health_indicators(audio_data),
            "speech_patterns": self._analyze_speech_patterns(audio_data)
        }
        return analysis
    
    def _get_duration(self, audio_data: Any) -> float:
        """获取音频时长"""
        # 简化实现
        return 5.0  # 假设5秒
    
    def _get_sample_rate(self, audio_data: Any) -> int:
        """获取采样率"""
        # 简化实现
        return 44100  # 标准采样率
    
    def _calculate_energy(self, audio_data: Any) -> float:
        """计算音频能量"""
        # 简化实现
        return 0.5
    
    def _extract_pitch(self, audio_data: Any) -> Dict[str, float]:
        """提取音调特征"""
        return {
            "fundamental_frequency": 150.0,
            "pitch_variance": 20.0,
            "pitch_range": 100.0
        }
    
    def _extract_spectral_features(self, audio_data: Any) -> Dict[str, float]:
        """提取频谱特征"""
        return {
            "spectral_centroid": 2000.0,
            "spectral_bandwidth": 1500.0,
            "spectral_rolloff": 8000.0,
            "zero_crossing_rate": 0.1
        }
    
    def _assess_voice_quality(self, audio_data: Any) -> Dict[str, float]:
        """评估声音质量"""
        return {
            "clarity": 0.8,
            "stability": 0.7,
            "strength": 0.6,
            "roughness": 0.2
        }
    
    def _analyze_emotional_state(self, audio_data: Any) -> Dict[str, float]:
        """分析情感状态"""
        return {
            "calm": 0.6,
            "anxious": 0.3,
            "excited": 0.1,
            "sad": 0.2
        }
    
    def _extract_health_indicators(self, audio_data: Any) -> Dict[str, Any]:
        """提取健康指标"""
        return {
            "breathing_pattern": "normal",
            "voice_fatigue": 0.2,
            "throat_condition": "healthy",
            "respiratory_health": 0.8
        }
    
    def _analyze_speech_patterns(self, audio_data: Any) -> Dict[str, float]:
        """分析语音模式"""
        return {
            "speech_rate": 150.0,  # 每分钟词数
            "pause_frequency": 0.1,
            "articulation_clarity": 0.8,
            "fluency": 0.9
        }


class MultimodalFuser:
    """多模态融合器"""
    
    def __init__(self):
        self.fusion_methods = {
            "early_fusion": self._early_fusion,
            "late_fusion": self._late_fusion,
            "attention_fusion": self._attention_fusion,
            "weighted_fusion": self._weighted_fusion
        }
    
    async def fuse_modalities(
        self,
        modality_results: List[ProcessingResult],
        fusion_method: str = "weighted_fusion",
        **kwargs
    ) -> FusionResult:
        """融合多模态结果"""
        try:
            if fusion_method not in self.fusion_methods:
                raise ValueError(f"不支持的融合方法: {fusion_method}")
            
            fusion_func = self.fusion_methods[fusion_method]
            result = await fusion_func(modality_results, **kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"多模态融合失败: {e}")
            return FusionResult(
                fused_features=np.array([]),
                fusion_confidence=0.0
            )
    
    async def _early_fusion(
        self,
        modality_results: List[ProcessingResult],
        **kwargs
    ) -> FusionResult:
        """早期融合"""
        # 特征级融合
        all_features = []
        modality_weights = {}
        
        for result in modality_results:
            if result.features is not None:
                all_features.append(result.features.flatten())
                modality_weights[result.modality_type] = result.confidence
        
        if all_features:
            fused_features = np.concatenate(all_features)
        else:
            fused_features = np.array([])
        
        fusion_confidence = np.mean(list(modality_weights.values())) if modality_weights else 0.0
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            fusion_confidence=fusion_confidence,
            fusion_method="early_fusion"
        )
    
    async def _late_fusion(
        self,
        modality_results: List[ProcessingResult],
        **kwargs
    ) -> FusionResult:
        """后期融合"""
        # 决策级融合
        decisions = []
        modality_weights = {}
        
        for result in modality_results:
            if result.result is not None:
                decisions.append(result.confidence)
                modality_weights[result.modality_type] = result.confidence
        
        if decisions:
            # 简单的投票机制
            fused_confidence = np.mean(decisions)
            fused_features = np.array([fused_confidence])
        else:
            fused_features = np.array([])
            fused_confidence = 0.0
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            fusion_confidence=fused_confidence,
            fusion_method="late_fusion"
        )
    
    async def _attention_fusion(
        self,
        modality_results: List[ProcessingResult],
        **kwargs
    ) -> FusionResult:
        """注意力融合"""
        # 基于注意力机制的融合
        attention_weights = self._calculate_attention_weights(modality_results)
        
        weighted_features = []
        modality_weights = {}
        
        for i, result in enumerate(modality_results):
            if result.features is not None:
                weight = attention_weights[i]
                weighted_feature = result.features.flatten() * weight
                weighted_features.append(weighted_feature)
                modality_weights[result.modality_type] = weight
        
        if weighted_features:
            fused_features = np.sum(weighted_features, axis=0)
        else:
            fused_features = np.array([])
        
        fusion_confidence = np.sum(attention_weights) / len(attention_weights) if attention_weights else 0.0
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            fusion_confidence=fusion_confidence,
            fusion_method="attention_fusion"
        )
    
    async def _weighted_fusion(
        self,
        modality_results: List[ProcessingResult],
        **kwargs
    ) -> FusionResult:
        """加权融合"""
        # 基于置信度的加权融合
        weights = [result.confidence for result in modality_results]
        total_weight = sum(weights) if weights else 1.0
        
        normalized_weights = [w / total_weight for w in weights] if total_weight > 0 else []
        
        weighted_features = []
        modality_weights = {}
        
        for i, result in enumerate(modality_results):
            if result.features is not None and i < len(normalized_weights):
                weight = normalized_weights[i]
                weighted_feature = result.features.flatten() * weight
                weighted_features.append(weighted_feature)
                modality_weights[result.modality_type] = weight
        
        if weighted_features:
            fused_features = np.sum(weighted_features, axis=0)
        else:
            fused_features = np.array([])
        
        fusion_confidence = np.mean(weights) if weights else 0.0
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            fusion_confidence=fusion_confidence,
            fusion_method="weighted_fusion"
        )
    
    def _calculate_attention_weights(self, modality_results: List[ProcessingResult]) -> List[float]:
        """计算注意力权重"""
        # 简化的注意力权重计算
        confidences = [result.confidence for result in modality_results]
        
        if not confidences:
            return []
        
        # 使用softmax计算注意力权重
        exp_confidences = np.exp(np.array(confidences))
        attention_weights = exp_confidences / np.sum(exp_confidences)
        
        return attention_weights.tolist()


class MultimodalProcessor:
    """多模态处理器主类"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.text_processor = TextProcessor()
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.fuser = MultimodalFuser()
        
        self.processors = {
            ModalityType.TEXT: self.text_processor,
            ModalityType.IMAGE: self.image_processor,
            ModalityType.AUDIO: self.audio_processor
        }
    
    async def process_multimodal_data(
        self,
        modality_data_list: List[ModalityData],
        tasks: Dict[ModalityType, ProcessingTask],
        fusion_method: str = "weighted_fusion"
    ) -> Dict[str, Any]:
        """
        处理多模态数据
        
        Args:
            modality_data_list: 多模态数据列表
            tasks: 每种模态的处理任务
            fusion_method: 融合方法
            
        Returns:
            处理结果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 并行处理各模态数据
            processing_tasks = []
            
            for modality_data in modality_data_list:
                modality_type = modality_data.modality_type
                task = tasks.get(modality_type, ProcessingTask.FEATURE_EXTRACTION)
                
                if modality_type in self.processors:
                    processor = self.processors[modality_type]
                    processing_task = processor.process(modality_data, task)
                    processing_tasks.append(processing_task)
            
            # 等待所有处理任务完成
            processing_results = await asyncio.gather(*processing_tasks, return_exceptions=True)
            
            # 过滤成功的结果
            valid_results = [
                result for result in processing_results
                if isinstance(result, ProcessingResult) and result.result is not None
            ]
            
            # 多模态融合
            fusion_result = None
            if len(valid_results) > 1:
                fusion_result = await self.fuser.fuse_modalities(
                    valid_results, fusion_method
                )
            
            # 构建最终结果
            final_result = {
                "modality_results": {
                    result.modality_type.value: {
                        "task": result.task_type.value,
                        "result": result.result,
                        "confidence": result.confidence,
                        "processing_time": result.processing_time
                    }
                    for result in valid_results
                },
                "fusion_result": {
                    "fused_features_shape": fusion_result.fused_features.shape if fusion_result else None,
                    "modality_weights": fusion_result.modality_weights if fusion_result else {},
                    "fusion_confidence": fusion_result.fusion_confidence if fusion_result else 0.0,
                    "fusion_method": fusion_result.fusion_method if fusion_result else None
                } if fusion_result else None,
                "processing_summary": {
                    "total_modalities": len(modality_data_list),
                    "successful_modalities": len(valid_results),
                    "fusion_applied": fusion_result is not None
                }
            }
            
            # 记录指标
            total_time = asyncio.get_event_loop().time() - start_time
            await self._record_metrics(modality_data_list, valid_results, total_time)
            
            return final_result
            
        except Exception as e:
            logger.error(f"多模态处理失败: {e}")
            return {
                "error": str(e),
                "modality_results": {},
                "fusion_result": None
            }
    
    async def extract_unified_features(
        self,
        modality_data_list: List[ModalityData]
    ) -> np.ndarray:
        """
        提取统一的多模态特征
        
        Args:
            modality_data_list: 多模态数据列表
            
        Returns:
            统一特征向量
        """
        try:
            # 为所有模态提取特征
            tasks = {
                modality_data.modality_type: ProcessingTask.FEATURE_EXTRACTION
                for modality_data in modality_data_list
            }
            
            result = await self.process_multimodal_data(
                modality_data_list, tasks, "early_fusion"
            )
            
            if result.get("fusion_result") and result["fusion_result"]["fused_features_shape"]:
                return result["fusion_result"]["fused_features"]
            else:
                return np.array([])
                
        except Exception as e:
            logger.error(f"统一特征提取失败: {e}")
            return np.array([])
    
    async def _record_metrics(
        self,
        modality_data_list: List[ModalityData],
        processing_results: List[ProcessingResult],
        total_time: float
    ):
        """记录指标"""
        await self.metrics_collector.record_histogram(
            "multimodal_processing_duration_seconds",
            total_time,
            {"modality_count": str(len(modality_data_list))}
        )
        
        await self.metrics_collector.record_gauge(
            "multimodal_success_rate",
            len(processing_results) / len(modality_data_list) if modality_data_list else 0
        )
        
        # 记录各模态的处理指标
        for result in processing_results:
            await self.metrics_collector.record_histogram(
                "modality_processing_duration_seconds",
                result.processing_time,
                {
                    "modality": result.modality_type.value,
                    "task": result.task_type.value
                }
            )
            
            await self.metrics_collector.record_histogram(
                "modality_confidence_score",
                result.confidence,
                {"modality": result.modality_type.value}
            )
        
        await self.metrics_collector.increment_counter(
            "multimodal_processing_requests_total",
            {"modality_count": str(len(modality_data_list))}
        ) 