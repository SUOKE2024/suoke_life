"""
多模态数据处理器

处理语音、图像、文本等多种模态的输入数据，为五诊协调提供统一的数据接口
"""

import asyncio
import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import io
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Union

from PIL import Image
import librosa
import numpy as np
import speech_recognition as sr
from transformers import pipeline

from ..config.settings import get_settings
from ..utils.exceptions import ProcessingError, UnsupportedFormatError
from ..utils.validators import validate_file_format, validate_file_size

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """模态类型枚举"""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    SENSOR = "sensor"


class ProcessingStatus(Enum):
    """处理状态枚举"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ModalityInput:
    """模态输入数据"""

    modality_type: ModalityType
    data: Union[str, bytes, np.ndarray]
    metadata: Dict[str, Any] = field(default_factory=dict)
    format: Optional[str] = None
    encoding: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProcessingResult:
    """处理结果"""

    modality_type: ModalityType
    status: ProcessingStatus
    processed_data: Dict[str, Any] = field(default_factory=dict)
    features: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    processing_time_ms: int = 0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MultimodalProcessor:
    """多模态数据处理器"""

    def __init__(self):
        self.settings = get_settings()
        self.processors = {}
        self.accessibility_enabled = True

    async def initialize(self) -> None:
        """初始化处理器"""
        logger.info("初始化多模态数据处理器...")

        try:
            # 初始化各模态处理器
            await self._initialize_text_processor()
            await self._initialize_audio_processor()
            await self._initialize_image_processor()
            await self._initialize_accessibility_services()

            logger.info("多模态数据处理器初始化完成")

        except Exception as e:
            logger.error(f"多模态处理器初始化失败: {e}")
            raise ProcessingError(f"无法初始化多模态处理器: {e}")

    async def _initialize_text_processor(self) -> None:
        """初始化文本处理器"""
        try:
            # 初始化NLP管道
            self.processors["text"] = {
                "sentiment": pipeline(
                    "sentiment-analysis",
                    model="uer/roberta-base-finetuned-dianping-chinese",
                ),
                "ner": pipeline("ner", model="ckiplab/bert-base-chinese-ner"),
                "emotion": pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                ),
            }
            logger.info("文本处理器初始化完成")
        except Exception as e:
            logger.warning(f"文本处理器初始化失败: {e}")
            self.processors["text"] = {}

    async def _initialize_audio_processor(self) -> None:
        """初始化音频处理器"""
        try:
            # 初始化语音识别器
            self.processors["audio"] = {
                "recognizer": sr.Recognizer(),
                "microphone": (sr.Microphone() if sr.Microphone.list_microphone_names() else None),
            }

            # 调整识别器参数
            recognizer = self.processors["audio"]["recognizer"]
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8

            logger.info("音频处理器初始化完成")
        except Exception as e:
            logger.warning(f"音频处理器初始化失败: {e}")
            self.processors["audio"] = {}

    async def _initialize_image_processor(self) -> None:
        """初始化图像处理器"""
        try:
            # 初始化图像分析管道
            self.processors["image"] = {
                "object_detection": pipeline("object-detection", model="facebook/detr-resnet-50"),
                "image_classification": pipeline(
                    "image-classification", model="google/vit-base-patch16-224"
                ),
                "face_detection": None,  # 可以集成face_recognition库
            }
            logger.info("图像处理器初始化完成")
        except Exception as e:
            logger.warning(f"图像处理器初始化失败: {e}")
            self.processors["image"] = {}

    async def _initialize_accessibility_services(self) -> None:
        """初始化无障碍服务"""
        try:
            self.processors["accessibility"] = {
                "tts": None,  # 文本转语音
                "stt": None,  # 语音转文本
                "sign_language": None,  # 手语识别
                "braille": None,  # 盲文转换
            }

            # 尝试初始化TTS服务
            try:
                import pyttsx3

                tts_engine = pyttsx3.init()
                tts_engine.setProperty("rate", 150)  # 语速
                tts_engine.setProperty("volume", 0.8)  # 音量
                self.processors["accessibility"]["tts"] = tts_engine
                logger.info("TTS服务初始化完成")
            except Exception as e:
                logger.warning(f"TTS服务初始化失败: {e}")

            logger.info("无障碍服务初始化完成")
        except Exception as e:
            logger.warning(f"无障碍服务初始化失败: {e}")
            self.processors["accessibility"] = {}

    async def process_multimodal_input(
        self, inputs: List[ModalityInput], user_id: str, session_id: str
    ) -> List[ProcessingResult]:
        """处理多模态输入"""
        logger.info(f"开始处理多模态输入 - 用户: {user_id}, 会话: {session_id}")

        results = []

        # 并行处理各模态数据
        tasks = []
        for input_data in inputs:
            task = self._process_single_modality(input_data, user_id, session_id)
            tasks.append(task)

        processing_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        for i, result in enumerate(processing_results):
            if isinstance(result, Exception):
                error_result = ProcessingResult(
                    modality_type=inputs[i].modality_type,
                    status=ProcessingStatus.FAILED,
                    error_message=str(result),
                )
                results.append(error_result)
            else:
                results.append(result)

        logger.info(
            f"多模态输入处理完成 - 成功: {sum(1 for r in results if r.status==ProcessingStatus.COMPLETED)}/{len(results)}"
        )

        return results

    async def _process_single_modality(
        self, input_data: ModalityInput, user_id: str, session_id: str
    ) -> ProcessingResult:
        """处理单一模态数据"""
        start_time = datetime.now()

        try:
            # 验证输入数据
            await self._validate_input(input_data)

            # 根据模态类型选择处理方法
            if input_data.modality_type == ModalityType.TEXT:
                result = await self._process_text(input_data)
            elif input_data.modality_type == ModalityType.AUDIO:
                result = await self._process_audio(input_data)
            elif input_data.modality_type == ModalityType.IMAGE:
                result = await self._process_image(input_data)
            elif input_data.modality_type == ModalityType.VIDEO:
                result = await self._process_video(input_data)
            elif input_data.modality_type == ModalityType.SENSOR:
                result = await self._process_sensor(input_data)
            else:
                raise UnsupportedFormatError(f"不支持的模态类型: {input_data.modality_type}")

            # 计算处理时间
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            result.processing_time_ms = processing_time
            result.status = ProcessingStatus.COMPLETED

            return result

        except Exception as e:
            logger.error(f"模态处理失败 - 类型: {input_data.modality_type.value}, 错误: {e}")
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return ProcessingResult(
                modality_type=input_data.modality_type,
                status=ProcessingStatus.FAILED,
                error_message=str(e),
                processing_time_ms=processing_time,
            )

    async def _validate_input(self, input_data: ModalityInput) -> None:
        """验证输入数据"""
        if not input_data.data:
            raise ValueError("输入数据不能为空")

        # 验证文件格式
        if input_data.format:
            await validate_file_format(input_data.modality_type.value, input_data.format)

        # 验证文件大小
        if isinstance(input_data.data, bytes):
            await validate_file_size(len(input_data.data))

    async def _process_text(self, input_data: ModalityInput) -> ProcessingResult:
        """处理文本数据"""
        text = (
            input_data.data if isinstance(input_data.data, str) else input_data.data.decode("utf-8")
        )

        processed_data = {
            "original_text": text,
            "text_length": len(text),
            "language": self._detect_language(text),
        }

        features = {}

        # 情感分析
        if "sentiment" in self.processors.get("text", {}):
            try:
                sentiment_result = self.processors["text"]["sentiment"](text)
                features["sentiment"] = {
                    "label": sentiment_result[0]["label"],
                    "score": sentiment_result[0]["score"],
                }
            except Exception as e:
                logger.warning(f"情感分析失败: {e}")

        # 命名实体识别
        if "ner" in self.processors.get("text", {}):
            try:
                ner_result = self.processors["text"]["ner"](text)
                entities = []
                for entity in ner_result:
                    if entity["score"] > 0.5:  # 置信度阈值
                        entities.append(
                            {
                                "text": entity["word"],
                                "label": entity["entity"],
                                "confidence": entity["score"],
                            }
                        )
                features["entities"] = entities
            except Exception as e:
                logger.warning(f"命名实体识别失败: {e}")

        # 情绪分析
        if "emotion" in self.processors.get("text", {}):
            try:
                emotion_result = self.processors["text"]["emotion"](text)
                features["emotion"] = {
                    "label": emotion_result[0]["label"],
                    "score": emotion_result[0]["score"],
                }
            except Exception as e:
                logger.warning(f"情绪分析失败: {e}")

        # 提取中医相关关键词
        features["tcm_keywords"] = self._extract_tcm_keywords(text)

        # 计算整体置信度
        confidence = self._calculate_text_confidence(features)

        return ProcessingResult(
            modality_type=ModalityType.TEXT,
            status=ProcessingStatus.PROCESSING,
            processed_data=processed_data,
            features=features,
            confidence=confidence,
        )

    async def _process_audio(self, input_data: ModalityInput) -> ProcessingResult:
        """处理音频数据"""
        audio_data = input_data.data

        processed_data = {
            "format": input_data.format or "unknown",
            "duration": 0,
            "sample_rate": 0,
        }

        features = {}

        try:
            # 如果是字节数据，保存为临时文件
            if isinstance(audio_data, bytes):
                with tempfile.NamedTemporaryFile(
                    suffix=f".{input_data.format or 'wav'}", delete=False
                ) as temp_file:
                    temp_file.write(audio_data)
                    temp_file_path = temp_file.name
            else:
                temp_file_path = audio_data  # 假设是文件路径

            try:
                # 使用librosa加载音频
                y, sr = librosa.load(temp_file_path, sr=None)
                processed_data["duration"] = len(y) / sr
                processed_data["sample_rate"] = sr

                # 提取音频特征
                features.update(await self._extract_audio_features(y, sr))

                # 语音转文本
                if "recognizer" in self.processors.get("audio", {}):
                    transcription = await self._speech_to_text(temp_file_path)
                    if transcription:
                        features["transcription"] = transcription
                        # 对转录文本进行进一步分析
                        text_input = ModalityInput(
                            modality_type=ModalityType.TEXT, data=transcription
                        )
                        text_result = await self._process_text(text_input)
                        features["text_analysis"] = text_result.features

            finally:
                # 清理临时文件
                if isinstance(audio_data, bytes) and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"音频处理失败: {e}")
            features["error"] = str(e)

        # 计算置信度
        confidence = self._calculate_audio_confidence(features)

        return ProcessingResult(
            modality_type=ModalityType.AUDIO,
            status=ProcessingStatus.PROCESSING,
            processed_data=processed_data,
            features=features,
            confidence=confidence,
        )

    async def _process_image(self, input_data: ModalityInput) -> ProcessingResult:
        """处理图像数据"""
        image_data = input_data.data

        processed_data = {
            "format": input_data.format or "unknown",
            "size": (0, 0),
            "mode": "unknown",
        }

        features = {}

        try:
            # 加载图像
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                # Base64编码的图像
                if image_data.startswith("data:image"):
                    # 移除data URL前缀
                    image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                raise ValueError("不支持的图像数据格式")

            processed_data["size"] = image.size
            processed_data["mode"] = image.mode

            # 图像分类
            if "image_classification" in self.processors.get("image", {}):
                try:
                    classification_result = self.processors["image"]["image_classification"](image)
                    features["classification"] = [
                        {"label": item["label"], "score": item["score"]}
                        for item in classification_result[:5]  # 取前5个结果
                    ]
                except Exception as e:
                    logger.warning(f"图像分类失败: {e}")

            # 目标检测
            if "object_detection" in self.processors.get("image", {}):
                try:
                    detection_result = self.processors["image"]["object_detection"](image)
                    objects = []
                    for obj in detection_result:
                        if obj["score"] > 0.5:  # 置信度阈值
                            objects.append(
                                {
                                    "label": obj["label"],
                                    "score": obj["score"],
                                    "box": obj["box"],
                                }
                            )
                    features["objects"] = objects
                except Exception as e:
                    logger.warning(f"目标检测失败: {e}")

            # 提取图像统计特征
            features.update(await self._extract_image_features(image))

            # 中医相关分析（如舌象、面色等）
            features["tcm_analysis"] = await self._analyze_tcm_image(image, input_data.metadata)

        except Exception as e:
            logger.error(f"图像处理失败: {e}")
            features["error"] = str(e)

        # 计算置信度
        confidence = self._calculate_image_confidence(features)

        return ProcessingResult(
            modality_type=ModalityType.IMAGE,
            status=ProcessingStatus.PROCESSING,
            processed_data=processed_data,
            features=features,
            confidence=confidence,
        )

    async def _process_video(self, input_data: ModalityInput) -> ProcessingResult:
        """处理视频数据"""
        # 视频处理的基本实现
        processed_data = {
            "format": input_data.format or "unknown",
            "duration": 0,
            "frame_count": 0,
        }

        features = {"video_analysis": "视频处理功能待实现"}

        return ProcessingResult(
            modality_type=ModalityType.VIDEO,
            status=ProcessingStatus.PROCESSING,
            processed_data=processed_data,
            features=features,
            confidence=0.5,
        )

    async def _process_sensor(self, input_data: ModalityInput) -> ProcessingResult:
        """处理传感器数据"""
        sensor_data = input_data.data

        processed_data = {
            "sensor_type": input_data.metadata.get("sensor_type", "unknown"),
            "data_points": 0,
        }

        features = {}

        try:
            if isinstance(sensor_data, (list, np.ndarray)):
                data_array = np.array(sensor_data)
                processed_data["data_points"] = len(data_array)

                # 基本统计特征
                features["statistics"] = {
                    "mean": float(np.mean(data_array)),
                    "std": float(np.std(data_array)),
                    "min": float(np.min(data_array)),
                    "max": float(np.max(data_array)),
                }

                # 根据传感器类型进行特定分析
                sensor_type = input_data.metadata.get("sensor_type", "")
                if "heart_rate" in sensor_type.lower():
                    features["heart_rate_analysis"] = await self._analyze_heart_rate(data_array)
                elif "blood_pressure" in sensor_type.lower():
                    features["blood_pressure_analysis"] = await self._analyze_blood_pressure(
                        data_array
                    )
                elif "temperature" in sensor_type.lower():
                    features["temperature_analysis"] = await self._analyze_temperature(data_array)

        except Exception as e:
            logger.error(f"传感器数据处理失败: {e}")
            features["error"] = str(e)

        confidence = self._calculate_sensor_confidence(features)

        return ProcessingResult(
            modality_type=ModalityType.SENSOR,
            status=ProcessingStatus.PROCESSING,
            processed_data=processed_data,
            features=features,
            confidence=confidence,
        )

    def _detect_language(self, text: str) -> str:
        """检测文本语言"""
        # 简单的中英文检测
        chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
        if chinese_chars > len(text) * 0.3:
            return "zh"
        return "en"

    def _extract_tcm_keywords(self, text: str) -> List[str]:
        """提取中医相关关键词"""
        tcm_keywords = [
            # 症状
            "头痛",
            "眩晕",
            "失眠",
            "心悸",
            "胸闷",
            "咳嗽",
            "气短",
            "乏力",
            "食欲不振",
            "腹胀",
            "便秘",
            "腹泻",
            "尿频",
            "尿急",
            "腰痛",
            "关节痛",
            # 舌象
            "舌红",
            "舌淡",
            "舌紫",
            "苔厚",
            "苔薄",
            "苔腻",
            "苔黄",
            "苔白",
            # 脉象
            "脉弦",
            "脉滑",
            "脉数",
            "脉迟",
            "脉细",
            "脉弱",
            "脉沉",
            "脉浮",
            # 体质
            "阳虚",
            "阴虚",
            "气虚",
            "血虚",
            "痰湿",
            "湿热",
            "血瘀",
            "气郁",
            # 情绪
            "烦躁",
            "抑郁",
            "焦虑",
            "易怒",
            "善太息",
            "多梦",
            "健忘",
        ]

        found_keywords = []
        for keyword in tcm_keywords:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords

    async def _extract_audio_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """提取音频特征"""
        features = {}

        try:
            # 基本特征
            features["zero_crossing_rate"] = float(np.mean(librosa.feature.zero_crossing_rate(y)))
            features["spectral_centroid"] = float(
                np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            )
            features["spectral_rolloff"] = float(
                np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            )

            # MFCC特征
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features["mfcc_mean"] = np.mean(mfccs, axis=1).tolist()
            features["mfcc_std"] = np.std(mfccs, axis=1).tolist()

            # 音量分析
            rms = librosa.feature.rms(y=y)
            features["rms_mean"] = float(np.mean(rms))
            features["rms_std"] = float(np.std(rms))

            # 语音活动检测
            intervals = librosa.effects.split(y, top_db=20)
            features["speech_segments"] = len(intervals)
            features["speech_ratio"] = sum(end - start for start, end in intervals) / len(y)

        except Exception as e:
            logger.warning(f"音频特征提取失败: {e}")
            features["extraction_error"] = str(e)

        return features

    async def _speech_to_text(self, audio_file_path: str) -> Optional[str]:
        """语音转文本"""
        try:
            recognizer = self.processors["audio"]["recognizer"]

            with sr.AudioFile(audio_file_path) as source:
                audio = recognizer.record(source)

            # 尝试多种识别引擎
            try:
                # 使用Google识别（需要网络）
                text = recognizer.recognize_google(audio, language="zh-CN")
                return text
            except sr.UnknownValueError:
                logger.warning("Google语音识别无法理解音频")
            except sr.RequestError:
                logger.warning("Google语音识别服务不可用")

            try:
                # 使用Sphinx识别（离线）
                text = recognizer.recognize_sphinx(audio, language="zh-CN")
                return text
            except sr.UnknownValueError:
                logger.warning("Sphinx语音识别无法理解音频")
            except sr.RequestError:
                logger.warning("Sphinx语音识别服务不可用")

        except Exception as e:
            logger.error(f"语音转文本失败: {e}")

        return None

    async def _extract_image_features(self, image: Image.Image) -> Dict[str, Any]:
        """提取图像特征"""
        features = {}

        try:
            # 转换为RGB模式
            if image.mode != "RGB":
                image = image.convert("RGB")

            # 转换为numpy数组
            img_array = np.array(image)

            # 颜色特征
            features["color_mean"] = np.mean(img_array, axis=(0, 1)).tolist()
            features["color_std"] = np.std(img_array, axis=(0, 1)).tolist()

            # 亮度特征
            gray = np.mean(img_array, axis=2)
            features["brightness_mean"] = float(np.mean(gray))
            features["brightness_std"] = float(np.std(gray))

            # 对比度
            features["contrast"] = float(np.std(gray))

            # 图像质量评估
            features["sharpness"] = self._calculate_sharpness(gray)
            features["noise_level"] = self._estimate_noise_level(gray)

        except Exception as e:
            logger.warning(f"图像特征提取失败: {e}")
            features["extraction_error"] = str(e)

        return features

    def _calculate_sharpness(self, gray_image: np.ndarray) -> float:
        """计算图像清晰度"""
        try:
            # 使用Laplacian算子计算清晰度
            from scipy import ndimage

            laplacian = ndimage.laplace(gray_image)
            return float(np.var(laplacian))
        except Exception:
            return 0.0

    def _estimate_noise_level(self, gray_image: np.ndarray) -> float:
        """估计图像噪声水平"""
        try:
            # 使用高频成分估计噪声
            from scipy import ndimage

            high_freq = ndimage.gaussian_filter(gray_image, sigma=1) - gray_image
            return float(np.std(high_freq))
        except Exception:
            return 0.0

    async def _analyze_tcm_image(
        self, image: Image.Image, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """中医图像分析"""
        analysis = {}

        image_type = metadata.get("image_type", "")

        if "tongue" in image_type.lower():
            # 舌象分析
            analysis = await self._analyze_tongue_image(image)
        elif "face" in image_type.lower():
            # 面色分析
            analysis = await self._analyze_face_image(image)
        elif "pulse" in image_type.lower():
            # 脉象图分析（如果有相关设备）
            analysis = await self._analyze_pulse_image(image)
        else:
            analysis = {"type": "general", "description": "通用图像分析"}

        return analysis

    async def _analyze_tongue_image(self, image: Image.Image) -> Dict[str, Any]:
        """舌象图像分析"""
        # 这里应该实现专业的舌象分析算法
        # 目前提供基础的颜色分析

        if image.mode != "RGB":
            image = image.convert("RGB")

        img_array = np.array(image)

        # 简单的颜色分析
        mean_color = np.mean(img_array, axis=(0, 1))

        analysis = {
            "type": "tongue",
            "color_analysis": {
                "red_component": float(mean_color[0]),
                "green_component": float(mean_color[1]),
                "blue_component": float(mean_color[2]),
            },
        }

        # 基于颜色判断舌质
        if mean_color[0] > 150 and mean_color[1] < 100:
            analysis["tongue_color"] = "红"
        elif mean_color[0] < 120 and mean_color[1] > 100:
            analysis["tongue_color"] = "淡"
        else:
            analysis["tongue_color"] = "淡红"

        return analysis

    async def _analyze_face_image(self, image: Image.Image) -> Dict[str, Any]:
        """面色图像分析"""
        if image.mode != "RGB":
            image = image.convert("RGB")

        img_array = np.array(image)
        mean_color = np.mean(img_array, axis=(0, 1))

        analysis = {
            "type": "face",
            "color_analysis": {
                "red_component": float(mean_color[0]),
                "green_component": float(mean_color[1]),
                "blue_component": float(mean_color[2]),
            },
        }

        # 基于颜色判断面色
        if mean_color[0] > 140 and mean_color[1] > 120:
            analysis["face_color"] = "红润"
        elif mean_color[0] < 100:
            analysis["face_color"] = "苍白"
        elif mean_color[1] > mean_color[0]:
            analysis["face_color"] = "萎黄"
        else:
            analysis["face_color"] = "正常"

        return analysis

    async def _analyze_pulse_image(self, image: Image.Image) -> Dict[str, Any]:
        """脉象图分析"""
        return {"type": "pulse", "description": "脉象图分析功能待实现"}

    async def _analyze_heart_rate(self, data: np.ndarray) -> Dict[str, Any]:
        """心率数据分析"""
        return {
            "average_hr": float(np.mean(data)),
            "hr_variability": float(np.std(data)),
            "min_hr": float(np.min(data)),
            "max_hr": float(np.max(data)),
        }

    async def _analyze_blood_pressure(self, data: np.ndarray) -> Dict[str, Any]:
        """血压数据分析"""
        # 假设数据格式为 [收缩压, 舒张压] 对
        if len(data) >= 2:
            systolic = data[0::2] if len(data) > 2 else [data[0]]
            diastolic = data[1::2] if len(data) > 2 else [data[1]]

            return {
                "systolic_mean": float(np.mean(systolic)),
                "diastolic_mean": float(np.mean(diastolic)),
                "pulse_pressure": float(np.mean(systolic) - np.mean(diastolic)),
            }

        return {"error": "血压数据格式不正确"}

    async def _analyze_temperature(self, data: np.ndarray) -> Dict[str, Any]:
        """体温数据分析"""
        return {
            "average_temp": float(np.mean(data)),
            "temp_variation": float(np.std(data)),
            "fever_episodes": int(np.sum(data > 37.5)),
        }

    def _calculate_text_confidence(self, features: Dict[str, Any]) -> float:
        """计算文本处理置信度"""
        confidence = 0.5  # 基础置信度

        if "sentiment" in features:
            confidence += features["sentiment"]["score"] * 0.2

        if "entities" in features and features["entities"]:
            confidence += min(len(features["entities"]) * 0.1, 0.3)

        if "tcm_keywords" in features and features["tcm_keywords"]:
            confidence += min(len(features["tcm_keywords"]) * 0.05, 0.2)

        return min(confidence, 1.0)

    def _calculate_audio_confidence(self, features: Dict[str, Any]) -> float:
        """计算音频处理置信度"""
        confidence = 0.3  # 基础置信度

        if "transcription" in features:
            confidence += 0.4

        if "speech_ratio" in features:
            confidence += features["speech_ratio"] * 0.3

        return min(confidence, 1.0)

    def _calculate_image_confidence(self, features: Dict[str, Any]) -> float:
        """计算图像处理置信度"""
        confidence = 0.4  # 基础置信度

        if "classification" in features and features["classification"]:
            max_score = max(item["score"] for item in features["classification"])
            confidence += max_score * 0.3

        if "objects" in features and features["objects"]:
            confidence += min(len(features["objects"]) * 0.1, 0.3)

        return min(confidence, 1.0)

    def _calculate_sensor_confidence(self, features: Dict[str, Any]) -> float:
        """计算传感器数据置信度"""
        confidence = 0.6  # 传感器数据通常比较可靠

        if "statistics" in features:
            confidence += 0.2

        if any(key.endswith("_analysis") for key in features.keys()):
            confidence += 0.2

        return min(confidence, 1.0)

    # 无障碍服务方法
    async def text_to_speech(self, text: str, language: str = "zh") -> Optional[bytes]:
        """文本转语音（无障碍服务）"""
        if not self.accessibility_enabled:
            return None

        try:
            tts_engine = self.processors.get("accessibility", {}).get("tts")
            if tts_engine:
                # 保存到临时文件
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file_path = temp_file.name

                tts_engine.save_to_file(text, temp_file_path)
                tts_engine.runAndWait()

                # 读取音频数据
                with open(temp_file_path, "rb") as f:
                    audio_data = f.read()

                # 清理临时文件
                os.unlink(temp_file_path)

                return audio_data

        except Exception as e:
            logger.error(f"文本转语音失败: {e}")

        return None

    async def speech_to_text_accessibility(self, audio_data: bytes) -> Optional[str]:
        """语音转文本（无障碍服务）"""
        if not self.accessibility_enabled:
            return None

        try:
            audio_input = ModalityInput(
                modality_type=ModalityType.AUDIO, data=audio_data, format="wav"
            )

            result = await self._process_audio(audio_input)
            return result.features.get("transcription")

        except Exception as e:
            logger.error(f"无障碍语音转文本失败: {e}")

        return None
