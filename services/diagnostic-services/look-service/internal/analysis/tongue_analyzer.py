#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
舌象分析引擎
提供舌象图像分析功能，包括舌质、舌苔特征识别与体质关联分析
"""

import io
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

from internal.model.model_factory import ModelFactory
from internal.repository.analysis_repository import AnalysisRepository
from internal.analysis.image_quality_assessor import ImageQualityAssessor

# 配置日志
logger = logging.getLogger(__name__)

class TongueColorType(Enum):
    """舌色类型枚举"""
    PALE = "淡白"           # 淡白舌
    LIGHT_RED = "淡红"      # 淡红舌
    RED = "红"              # 红舌
    CRIMSON = "深红"        # 深红舌
    PURPLE = "紫"           # 紫舌
    BLUE_PURPLE = "青紫"    # 青紫舌


class TongueShapeType(Enum):
    """舌形类型枚举"""
    NORMAL = "正常"         # 正常舌
    THIN = "瘦"             # 瘦舌
    FAT = "胖"              # 胖舌
    TEETH_MARKED = "齿痕"   # 齿痕舌
    CRACKED = "裂纹"        # 裂纹舌
    THORNY = "芒刺"         # 芒刺舌


class CoatingColorType(Enum):
    """舌苔颜色类型枚举"""
    WHITE = "白"            # 白苔
    THIN_WHITE = "薄白"     # 薄白苔
    THICK_WHITE = "厚白"    # 厚白苔
    YELLOW = "黄"           # 黄苔
    GRAY = "灰"             # 灰苔
    BLACK = "黑"            # 黑苔


class CoatingTextureType(Enum):
    """舌苔质地类型枚举"""
    THIN = "薄"             # 薄苔
    THICK = "厚"            # 厚苔
    GREASY = "腻"           # 腻苔
    DRY = "干"              # 干苔
    MOIST = "润"            # 润苔
    SLIPPERY = "滑"         # 滑苔
    ROUGH = "糙"            # 糙苔


class TongueRegion(Enum):
    """舌部区域枚举，对应五脏"""
    TIP = "舌尖"            # 舌尖-心
    CENTER = "舌中"         # 舌中-脾胃
    ROOT = "舌根"           # 舌根-肾
    LEFT_EDGE = "左缘"      # 左缘-肝胆
    RIGHT_EDGE = "右缘"     # 右缘-肺


@dataclass
class FeatureLocation:
    """特征位置"""
    feature_name: str       # 特征名称
    x_min: float            # 左上角x坐标
    y_min: float            # 左上角y坐标
    x_max: float            # 右下角x坐标
    y_max: float            # 右下角y坐标
    confidence: float       # 置信度


@dataclass
class ConstitutionCorrelation:
    """体质关联"""
    constitution_type: str  # 体质类型
    confidence: float       # 置信度
    description: str        # 描述


@dataclass
class TongueAnalysisResult:
    """舌象分析结果"""
    request_id: str                        # 请求ID
    tongue_color: TongueColorType          # 舌色
    tongue_shape: TongueShapeType          # 舌形
    coating_color: CoatingColorType        # 苔色
    coating_distribution: str              # 苔布
    features: List[str]                    # 特征列表
    locations: List[FeatureLocation]       # 特征位置
    body_constitution: List[ConstitutionCorrelation]  # 体质关联
    metrics: Dict[str, float]              # 量化指标
    analysis_summary: str                  # 分析总结
    analysis_id: str                       # 分析记录ID
    timestamp: int                         # 时间戳


class TongueSegmentationModel(nn.Module):
    """舌象分割模型"""
    def __init__(self):
        super(TongueSegmentationModel, self).__init__()
        # 模型结构定义 (U-Net或其他分割模型)
        # 此处简化，实际实现应包含完整的模型架构
        
    def forward(self, x):
        # 前向传播逻辑
        # 此处简化，实际实现应包含完整的前向传播逻辑
        return x


class TongueFeatureModel(nn.Module):
    """舌象特征识别模型"""
    def __init__(self):
        super(TongueFeatureModel, self).__init__()
        # 模型结构定义 (CNN分类器或特征提取器)
        # 此处简化，实际实现应包含完整的模型架构
        
    def forward(self, x):
        # 前向传播逻辑
        # 此处简化，实际实现应包含完整的前向传播逻辑
        return x


class TongueAnalyzer:
    """舌象分析器，处理舌象分析的核心逻辑"""
    
    def __init__(
        self, 
        config: Dict, 
        model_factory: ModelFactory,
        analysis_repository: Optional[AnalysisRepository] = None
    ):
        """
        初始化舌象分析器
        
        Args:
            config: 配置字典
            model_factory: 模型工厂
            analysis_repository: 分析结果存储库
        """
        self.config = config
        self.model_factory = model_factory
        self.analysis_repository = analysis_repository
        
        # 初始化图像质量评估器
        quality_config = self.config.get('image_quality', {})
        self.quality_assessor = ImageQualityAssessor(quality_config)
        
        # 版本信息
        self.version = self.config.get('version', '1.0.0')
        
        # 加载模型
        self._load_models()
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Resize(self.input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # 体质关联映射表
        self.constitution_mapping = {
            TongueColorType.PALE: ["气虚质", "阳虚质"],
            TongueColorType.LIGHT_RED: ["平和质"],
            TongueColorType.RED: ["阴虚质", "湿热质"],
            TongueColorType.CRIMSON: ["阴虚质"],
            TongueColorType.PURPLE: ["血瘀质"],
            TongueColorType.BLUE_PURPLE: ["血瘀质", "寒湿质"],
            TongueShapeType.THIN: ["气虚质", "阴虚质"],
            TongueShapeType.FAT: ["痰湿质", "阳虚质"],
            TongueShapeType.TEETH_MARKED: ["气虚质", "痰湿质"],
            TongueShapeType.CRACKED: ["阴虚质"],
            TongueShapeType.THORNY: ["热证"],
            CoatingColorType.WHITE: ["寒证"],
            CoatingColorType.YELLOW: ["热证"],
            CoatingColorType.GRAY: ["寒湿质"],
            CoatingColorType.BLACK: ["寒证", "热证"]
        }
        
        # 体质描述
        self.constitution_descriptions = {
            "平和质": "平和质体质平衡，舌象表现为舌体正常大小，舌色淡红，舌苔薄白",
            "气虚质": "气虚质常见舌体胖大，边有齿痕，舌色淡白，舌苔薄白",
            "阳虚质": "阳虚质常见舌体胖大，边有齿痕，舌色淡白或淡紫，舌苔白滑",
            "阴虚质": "阴虚质常见舌体瘦小，舌色红或深红，舌面有裂纹，少苔或无苔",
            "痰湿质": "痰湿质常见舌体胖大，边有齿痕，舌苔厚腻",
            "湿热质": "湿热质常见舌色偏红，舌苔黄腻",
            "血瘀质": "血瘀质常见舌色紫暗或有瘀点瘀斑，舌下络脉紫暗",
            "气郁质": "气郁质舌象多变，可见舌体瘦小，舌色偏暗",
            "特禀质": "特禀质舌象因个体特异性而异"
        }
        
        logger.info(f"TongueAnalyzer initialized on {self.device} device")
    
    def _load_models(self):
        """加载模型"""
        try:
            if not self.model_path.exists():
                logger.error(f"Model path {self.model_path} does not exist")
                raise FileNotFoundError(f"Model path {self.model_path} does not exist")
            
            # 加载分割模型和特征识别模型
            # 此处简化，实际实现应包含完整的模型加载逻辑
            self.segmentation_model = TongueSegmentationModel()
            self.feature_model = TongueFeatureModel()
            
            # 模拟加载权重文件
            # self.segmentation_model.load_state_dict(torch.load(self.model_path / "segmentation.pth"))
            # self.feature_model.load_state_dict(torch.load(self.model_path / "feature.pth"))
            
            # 量化模型（如果需要）
            if self.quantized:
                # 此处简化，实际实现应包含完整的量化逻辑
                pass
            
            # 将模型移动到设备
            self.segmentation_model.to(self.device)
            self.feature_model.to(self.device)
            
            # 设置为评估模式
            self.segmentation_model.eval()
            self.feature_model.eval()
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise
    
    def preprocess_image(self, image_data: Union[bytes, np.ndarray]) -> torch.Tensor:
        """
        预处理图像
        
        Args:
            image_data: 图像数据，可以是字节或numpy数组
            
        Returns:
            预处理后的图像张量
        """
        try:
            if isinstance(image_data, bytes):
                # 从字节加载图像
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
            else:
                # 从numpy数组加载图像
                image = Image.fromarray(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB))
            
            # 应用变换
            tensor = self.transform(image)
            # 添加批次维度
            tensor = tensor.unsqueeze(0)
            # 移动到设备
            tensor = tensor.to(self.device)
            
            return tensor
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise
    
    def segment_tongue(self, image_tensor: torch.Tensor) -> np.ndarray:
        """
        分割舌象区域
        
        Args:
            image_tensor: 输入图像张量
            
        Returns:
            舌象分割掩码
        """
        try:
            with torch.no_grad():
                # 此处简化，实际实现应包含完整的分割逻辑
                # mask = self.segmentation_model(image_tensor)
                # mask = mask.squeeze().cpu().numpy()
                
                # 模拟分割结果
                mask = np.zeros((self.input_size[0], self.input_size[1]), dtype=np.uint8)
                # 模拟一个椭圆形舌头区域
                center = (self.input_size[0] // 2, self.input_size[1] // 2)
                axes = (self.input_size[0] // 3, self.input_size[1] // 4)
                cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
                
                return mask
                
        except Exception as e:
            logger.error(f"Tongue segmentation failed: {e}")
            raise
    
    def extract_tongue_features(self, image_tensor: torch.Tensor, mask: np.ndarray) -> Dict:
        """
        提取舌象特征
        
        Args:
            image_tensor: 输入图像张量
            mask: 舌象分割掩码
            
        Returns:
            舌象特征字典
        """
        try:
            # 将图像张量转换为numpy数组
            image_np = image_tensor.squeeze().cpu().numpy().transpose(1, 2, 0)
            # 反归一化
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            image_np = std * image_np + mean
            image_np = np.clip(image_np, 0, 1) * 255
            image_np = image_np.astype(np.uint8)
            
            # 应用掩码
            masked_image = cv2.bitwise_and(image_np, image_np, mask=mask)
            
            # 此处简化，实际实现应包含完整的特征提取逻辑
            # with torch.no_grad():
            #     features = self.feature_model(image_tensor)
            
            # 模拟特征提取结果
            # 舌色分析 (基于HSV色彩空间)
            hsv_image = cv2.cvtColor(masked_image, cv2.COLOR_RGB2HSV)
            # 计算H、S、V通道的均值
            h_mean = np.mean(hsv_image[:, :, 0][mask > 0])
            s_mean = np.mean(hsv_image[:, :, 1][mask > 0])
            v_mean = np.mean(hsv_image[:, :, 2][mask > 0])
            
            # 根据HSV值确定舌色
            if v_mean < 100:
                tongue_color = TongueColorType.BLUE_PURPLE
            elif h_mean < 10 and s_mean > 150:
                tongue_color = TongueColorType.CRIMSON
            elif h_mean < 20 and s_mean > 100:
                tongue_color = TongueColorType.RED
            elif v_mean < 150 and s_mean < 50:
                tongue_color = TongueColorType.PALE
            else:
                tongue_color = TongueColorType.LIGHT_RED
            
            # 舌形分析 (简化版)
            tongue_shape = TongueShapeType.NORMAL
            # 模拟一些特征
            has_teeth_marks = np.random.random() > 0.7
            has_cracks = np.random.random() > 0.8
            
            if has_teeth_marks:
                tongue_shape = TongueShapeType.TEETH_MARKED
            elif has_cracks:
                tongue_shape = TongueShapeType.CRACKED
            
            # 苔色分析 (简化版)
            # 模拟苔色检测
            coating_color = CoatingColorType.THIN_WHITE
            if np.random.random() > 0.7:
                coating_color = CoatingColorType.YELLOW
            
            # 苔布分析
            coating_distribution = "均匀"
            if np.random.random() > 0.8:
                coating_distribution = "部分脱落"
            
            # 特征列表
            features = []
            if tongue_color == TongueColorType.PALE:
                features.append("淡白")
            elif tongue_color == TongueColorType.RED or tongue_color == TongueColorType.CRIMSON:
                features.append("红舌")
            
            if tongue_shape == TongueShapeType.TEETH_MARKED:
                features.append("齿痕")
            elif tongue_shape == TongueShapeType.CRACKED:
                features.append("裂纹")
            
            if coating_color == CoatingColorType.YELLOW:
                features.append("黄苔")
            elif coating_color == CoatingColorType.THIN_WHITE:
                features.append("薄白苔")
            
            if coating_distribution != "均匀":
                features.append("苔布不均")
            
            # 特征位置 (简化版)
            locations = []
            # 模拟一些特征位置
            if "齿痕" in features:
                locations.append(FeatureLocation(
                    feature_name="齿痕",
                    x_min=100.0,
                    y_min=150.0,
                    x_max=200.0,
                    y_max=250.0,
                    confidence=0.85
                ))
            
            if "裂纹" in features:
                locations.append(FeatureLocation(
                    feature_name="裂纹",
                    x_min=220.0,
                    y_min=180.0,
                    x_max=320.0,
                    y_max=220.0,
                    confidence=0.78
                ))
            
            # 量化指标
            metrics = {
                "舌色饱和度": s_mean / 255.0,
                "舌色亮度": v_mean / 255.0,
                "舌体完整度": 0.95 if len(features) < 2 else 0.8
            }
            
            return {
                "tongue_color": tongue_color,
                "tongue_shape": tongue_shape,
                "coating_color": coating_color,
                "coating_distribution": coating_distribution,
                "features": features,
                "locations": locations,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise
    
    def correlate_with_constitution(self, features: Dict) -> List[ConstitutionCorrelation]:
        """
        关联体质特征
        
        Args:
            features: 舌象特征字典
            
        Returns:
            体质关联列表
        """
        # 计数器，记录每种体质的相关性
        constitution_counter = {
            "平和质": 0.0,
            "气虚质": 0.0,
            "阳虚质": 0.0,
            "阴虚质": 0.0,
            "痰湿质": 0.0,
            "湿热质": 0.0,
            "血瘀质": 0.0,
            "气郁质": 0.0,
            "特禀质": 0.0
        }
        
        # 检查舌色关联
        if features["tongue_color"] in self.constitution_mapping:
            for constitution in self.constitution_mapping[features["tongue_color"]]:
                constitution_counter[constitution] += 1.0
        
        # 检查舌形关联
        if features["tongue_shape"] in self.constitution_mapping:
            for constitution in self.constitution_mapping[features["tongue_shape"]]:
                constitution_counter[constitution] += 1.0
        
        # 检查苔色关联
        if features["coating_color"] in self.constitution_mapping:
            for constitution in self.constitution_mapping[features["coating_color"]]:
                # 这里"寒证"和"热证"不是直接的体质类型，需要映射
                if constitution == "寒证":
                    constitution_counter["阳虚质"] += 0.7
                    constitution_counter["寒湿质"] += 0.7
                elif constitution == "热证":
                    constitution_counter["阴虚质"] += 0.7
                    constitution_counter["湿热质"] += 0.7
                else:
                    constitution_counter[constitution] += 1.0
        
        # 特殊规则
        if features["tongue_color"] == TongueColorType.LIGHT_RED and \
           features["tongue_shape"] == TongueShapeType.NORMAL and \
           features["coating_color"] == CoatingColorType.THIN_WHITE and \
           features["coating_distribution"] == "均匀":
            constitution_counter["平和质"] += 2.0
        
        # 归一化并生成关联列表
        total = sum(constitution_counter.values())
        if total > 0:
            constitution_counter = {k: v / total for k, v in constitution_counter.items()}
        
        # 排序并选择前3个最相关的体质
        top_constitutions = sorted(constitution_counter.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 生成关联列表
        correlations = []
        for constitution, confidence in top_constitutions:
            if confidence > 0.1:  # 只保留置信度大于0.1的体质关联
                correlations.append(ConstitutionCorrelation(
                    constitution_type=constitution,
                    confidence=confidence,
                    description=self.constitution_descriptions.get(constitution, "")
                ))
        
        return correlations
    
    def generate_analysis_summary(self, features: Dict, body_constitution: List[ConstitutionCorrelation]) -> str:
        """
        生成分析总结
        
        Args:
            features: 舌象特征字典
            body_constitution: 体质关联列表
            
        Returns:
            分析总结文本
        """
        # 构建分析总结
        summary = f"舌诊分析显示，舌色为{features['tongue_color'].value}，"
        summary += f"舌形为{features['tongue_shape'].value}，"
        summary += f"舌苔为{features['coating_color'].value}，分布{features['coating_distribution']}。"
        
        if features["features"]:
            summary += f"特征包括：{', '.join(features['features'])}。"
        
        if body_constitution:
            summary += f"综合分析，最可能的体质类型为{body_constitution[0].constitution_type}"
            if len(body_constitution) > 1:
                summary += f"，其次为{body_constitution[1].constitution_type}"
            summary += "。"
            
            # 添加主要体质的描述
            summary += f"{body_constitution[0].description}。"
        
        return summary
    
    def analyze(
        self, 
        image_data: bytes, 
        user_id: str, 
        save_result: bool = False,
        save_visualizations: bool = True
    ) -> TongueAnalysisResult:
        """
        分析舌象图像
        
        Args:
            image_data: 舌象图像数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            save_visualizations: 是否保存可视化结果
            
        Returns:
            TongueAnalysisResult: 分析结果
        """
        start_time = time.time()
        
        # 生成请求ID和分析ID
        request_id = str(uuid.uuid4())
        analysis_id = str(uuid.uuid4()) if save_result else ""
        
        # 检查图像质量
        is_valid_image, quality_assessment = self.quality_assessor.assess_image(
            image_data, 
            image_type='tongue'
        )
        
        if not is_valid_image:
            # 图像质量不合格，返回错误结果
            suggestions = self.quality_assessor.get_improvement_suggestions(quality_assessment)
            suggestions_str = "; ".join(suggestions)
            
            error_message = f"图像质量不合格: {suggestions_str}"
            logger.warning(
                "舌象图像质量检查未通过", 
                user_id=user_id,
                quality=quality_assessment,
                suggestions=suggestions
            )
            
            raise ProcessingError(error_message, "IMAGE_QUALITY_ERROR", quality_assessment)
        
        try:
            logger.info(f"Starting tongue analysis for user {user_id}")
            
            # 预处理图像
            image_tensor = self.preprocess_image(image_data)
            
            # 分割舌象区域
            mask = self.segment_tongue(image_tensor)
            
            # 提取舌象特征
            features = self.extract_tongue_features(image_tensor, mask)
            
            # 关联体质
            body_constitution = self.correlate_with_constitution(features)
            
            # 生成分析总结
            analysis_summary = self.generate_analysis_summary(features, body_constitution)
            
            # 构建分析结果
            result = TongueAnalysisResult(
                request_id=request_id,
                tongue_color=features["tongue_color"],
                tongue_shape=features["tongue_shape"],
                coating_color=features["coating_color"],
                coating_distribution=features["coating_distribution"],
                features=features["features"],
                locations=features["locations"],
                body_constitution=body_constitution,
                metrics=features["metrics"],
                analysis_summary=analysis_summary,
                analysis_id=analysis_id,
                timestamp=int(start_time)
            )
            
            logger.info(f"Tongue analysis completed for user {user_id}, result_id: {analysis_id}")
            
            # 保存结果 (此处省略实际存储逻辑)
            if save_result:
                logger.info(f"Saving analysis result {analysis_id}")
                # 实际应用中应当调用数据存储层保存结果
            
            return result
            
        except Exception as e:
            logger.error(f"Tongue analysis failed: {e}")
            raise 