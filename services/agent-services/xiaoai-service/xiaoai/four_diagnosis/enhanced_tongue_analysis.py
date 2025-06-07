#!/usr/bin/env python3
"""
增强舌象分析模块 - 提供智能舌象分析功能
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class TongueBodyColor(Enum):
    """舌体颜色"""
    PALE = "淡"
    NORMAL = "淡红"
    RED = "红"
    PURPLE = "紫"


class TongueCoatingColor(Enum):
    """舌苔颜色"""
    WHITE = "白"
    YELLOW = "黄"
    GRAY = "灰"
    BLACK = "黑"


class TongueCoatingThickness(Enum):
    """舌苔厚薄"""
    THIN = "薄"
    THICK = "厚"


class TongueTexture(Enum):
    """舌质纹理"""
    NORMAL = "正常"
    TEETH_MARKS = "齿痕"
    CRACKS = "裂纹"


@dataclass
class TongueFeatures:
    """舌象特征"""
    body_color: TongueBodyColor
    coating_color: TongueCoatingColor
    coating_thickness: TongueCoatingThickness
    texture: TongueTexture
    moisture: str
    body_color_confidence: float = 0.8
    coating_color_confidence: float = 0.8
    coating_thickness_confidence: float = 0.8
    texture_confidence: float = 0.8


class EnhancedTongueAnalyzer:
    """增强舌象分析器"""

    def __init__(self):
        """初始化分析器"""
        self.syndrome_mapping = {
            "淡白薄": {
                "syndrome": "气虚证",
                "confidence": 0.85,
                "description": "舌质淡白，苔薄，多见于气虚证",
            },
            "红黄厚": {
                "syndrome": "湿热证",
                "confidence": 0.90,
                "description": "舌质红，苔黄厚，多见于湿热证",
            },
            "紫暗薄": {
                "syndrome": "血瘀证",
                "confidence": 0.88,
                "description": "舌质紫暗，苔薄，多见于血瘀证",
            },
        }

        logger.info("增强舌象分析器初始化完成")

    async def analyze_tongue(
        self,
        image_data: bytes | None = None,
        manual_features: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """分析舌象"""
        try:
            # 提取特征
            if manual_features:
                features = self._parse_manual_features(manual_features)
            else:
                features = self._extract_features_from_image(image_data)

            # 分析证候
            syndrome_analysis = await self._analyze_syndrome(features)

            # 分析体质
            constitution_analysis = await self._analyze_constitution(features)

            # 生成建议
            suggestions = self._generate_suggestions(features, syndrome_analysis)

            # 计算整体置信度
            overall_confidence = self._calculate_overall_confidence(features)

            return {
                "features": {
                    "body_color": features.body_color.value,
                    "coating_color": features.coating_color.value,
                    "coating_thickness": features.coating_thickness.value,
                    "texture": features.texture.value,
                    "moisture": features.moisture,
                },
                "syndrome": syndrome_analysis,
                "constitution": constitution_analysis,
                "suggestions": suggestions,
                "confidence": overall_confidence,
                "analysis_time": time.time(),
            }

        except Exception as e:
            logger.error(f"舌象分析失败: {e}")
            return {
                "error": str(e),
                "features": {},
                "syndrome": {"syndrome": "分析失败", "confidence": 0.0},
                "constitution": {"constitution": "未知", "confidence": 0.0},
                "suggestions": ["建议重新拍摄舌象或咨询专业中医师"],
                "confidence": 0.0,
                "analysis_time": time.time(),
            }

    def _parse_manual_features(self, manual_features: dict[str, Any]) -> TongueFeatures:
        """解析手动输入的特征"""
        try:
            return TongueFeatures(
                body_color=TongueBodyColor(manual_features.get("body_color", "淡红")),
                coating_color=TongueCoatingColor(manual_features.get("coating_color", "白")),
                coating_thickness=TongueCoatingThickness(manual_features.get("coating_thickness", "薄")),
                texture=TongueTexture(manual_features.get("texture", "正常")),
                moisture=manual_features.get("moisture", "润"),
                body_color_confidence=manual_features.get("body_color_confidence", 1.0),
                coating_color_confidence=manual_features.get("coating_color_confidence", 1.0),
                coating_thickness_confidence=manual_features.get("coating_thickness_confidence", 1.0),
                texture_confidence=manual_features.get("texture_confidence", 1.0),
            )
        except Exception as e:
            logger.warning(f"解析手动特征失败: {e}")
            return TongueFeatures(
                body_color=TongueBodyColor.NORMAL,
                coating_color=TongueCoatingColor.WHITE,
                coating_thickness=TongueCoatingThickness.THIN,
                texture=TongueTexture.NORMAL,
                moisture="润",
            )

    def _extract_features_from_image(self, image_data: bytes | None) -> TongueFeatures:
        """从图像提取特征"""
        # 模拟图像分析
        if image_data:
            logger.info("正在分析舌象图像...")
            # 这里应该是实际的图像处理逻辑
            return TongueFeatures(
                body_color=TongueBodyColor.NORMAL,
                coating_color=TongueCoatingColor.WHITE,
                coating_thickness=TongueCoatingThickness.THIN,
                texture=TongueTexture.NORMAL,
                moisture="润",
                body_color_confidence=0.8,
                coating_color_confidence=0.8,
                coating_thickness_confidence=0.8,
                texture_confidence=0.8,
            )
        else:
            # 默认特征
            return TongueFeatures(
                body_color=TongueBodyColor.NORMAL,
                coating_color=TongueCoatingColor.WHITE,
                coating_thickness=TongueCoatingThickness.THIN,
                texture=TongueTexture.NORMAL,
                moisture="润",
            )

    async def _analyze_syndrome(self, features: TongueFeatures) -> dict[str, Any]:
        """分析证候"""
        try:
            # 构建特征键
            key = f"{features.body_color.value}{features.coating_color.value}{features.coating_thickness.value}"

            if key in self.syndrome_mapping:
                syndrome_info = self.syndrome_mapping[key].copy()
                # 调整置信度基于特征置信度
                avg_confidence = (
                    features.body_color_confidence
                    + features.coating_color_confidence
                    + features.coating_thickness_confidence
                ) / 3
                syndrome_info["confidence"] *= avg_confidence
                return syndrome_info
            else:
                # 基于单个特征的推理
                return self._infer_syndrome_from_features(features)

        except Exception as e:
            logger.error(f"证候分析失败: {e}")
            return {
                "syndrome": "证候不明",
                "confidence": 0.0,
                "description": "无法确定证候类型",
            }

    def _infer_syndrome_from_features(self, features: TongueFeatures) -> dict[str, Any]:
        """基于特征推理证候"""
        # 简化的推理逻辑
        if features.body_color == TongueBodyColor.PALE:
            return {
                "syndrome": "气虚证",
                "confidence": 0.7,
                "description": "舌质淡白，提示气虚",
            }
        elif features.body_color == TongueBodyColor.RED:
            return {
                "syndrome": "热证",
                "confidence": 0.7,
                "description": "舌质红，提示热证",
            }
        elif features.body_color == TongueBodyColor.PURPLE:
            return {
                "syndrome": "血瘀证",
                "confidence": 0.7,
                "description": "舌质紫暗，提示血瘀",
            }
        else:
            return {
                "syndrome": "平和",
                "confidence": 0.6,
                "description": "舌象基本正常",
            }

    async def _analyze_constitution(self, features: TongueFeatures) -> dict[str, Any]:
        """分析体质"""
        try:
            constitution_scores = {
                "平和质": 0.5,
                "气虚质": 0.0,
                "阳虚质": 0.0,
                "阴虚质": 0.0,
                "痰湿质": 0.0,
                "湿热质": 0.0,
                "血瘀质": 0.0,
                "气郁质": 0.0,
                "特禀质": 0.0,
            }

            # 根据舌体颜色调整分数
            if features.body_color == TongueBodyColor.PALE:
                constitution_scores["气虚质"] += 0.3
                constitution_scores["阳虚质"] += 0.2
            elif features.body_color == TongueBodyColor.RED:
                constitution_scores["阴虚质"] += 0.3
                constitution_scores["湿热质"] += 0.2
            elif features.body_color == TongueBodyColor.PURPLE:
                constitution_scores["血瘀质"] += 0.4

            # 根据舌苔调整分数
            if features.coating_color == TongueCoatingColor.YELLOW:
                constitution_scores["湿热质"] += 0.2
            elif features.coating_thickness == TongueCoatingThickness.THICK:
                constitution_scores["痰湿质"] += 0.3

            # 根据纹理调整分数
            if features.texture == TongueTexture.TEETH_MARKS:
                constitution_scores["气虚质"] += 0.2
                constitution_scores["痰湿质"] += 0.2

            # 确定主要体质
            main_constitution = max(constitution_scores.items(), key=lambda x: x[1])

            return {
                "constitution": main_constitution[0],
                "confidence": main_constitution[1],
                "all_scores": constitution_scores,
                "description": self._get_constitution_description(main_constitution[0]),
            }

        except Exception as e:
            logger.error(f"体质分析失败: {e}")
            return {
                "constitution": "平和质",
                "confidence": 0.5,
                "all_scores": {},
                "description": "体质分析失败",
            }

    def _get_constitution_description(self, constitution: str) -> str:
        """获取体质描述"""
        descriptions = {
            "平和质": "体质平和，身体健康",
            "气虚质": "气虚体质，容易疲劳，需要补气",
            "阳虚质": "阳虚体质，畏寒怕冷，需要温阳",
            "阴虚质": "阴虚体质，容易上火，需要滋阴",
            "痰湿质": "痰湿体质，容易肥胖，需要化痰除湿",
            "湿热质": "湿热体质，容易长痘，需要清热利湿",
            "血瘀质": "血瘀体质，容易淤血，需要活血化瘀",
            "气郁质": "气郁体质，情绪不稳，需要疏肝理气",
            "特禀质": "特禀体质，过敏体质，需要特殊调理",
        }
        return descriptions.get(constitution, "体质类型未知")

    def _generate_suggestions(
        self,
        features: TongueFeatures,
        syndrome_analysis: dict[str, Any],
    ) -> list[str]:
        """生成建议"""
        try:
            suggestions = []

            # 基于证候的建议
            syndrome = syndrome_analysis.get("syndrome", "")

            if "气虚" in syndrome:
                suggestions.extend([
                    "建议补中益气，可适量食用人参、黄芪等",
                    "避免过度劳累，保证充足睡眠",
                    "适当进行缓和运动，如太极拳",
                ])
            elif "血瘀" in syndrome:
                suggestions.extend([
                    "建议活血化瘀，可适量食用当归、川芎等",
                    "适当运动，促进血液循环",
                    "避免久坐久立",
                ])
            elif "湿热" in syndrome:
                suggestions.extend([
                    "建议清热利湿，饮食宜清淡",
                    "避免辛辣油腻食物",
                    "保持环境通风干燥",
                ])

            # 基于舌象特征的建议
            if features.coating_thickness == TongueCoatingThickness.THICK:
                suggestions.append("舌苔较厚，建议清淡饮食，避免油腻")

            if features.texture == TongueTexture.TEETH_MARKS:
                suggestions.append("舌有齿痕，提示脾气虚弱，建议健脾益气")

            if features.moisture == "燥":
                suggestions.append("舌质偏燥，建议多饮水，滋阴润燥")

            # 通用建议
            suggestions.extend([
                "保持口腔卫生，定期刷牙",
                "饮食规律，营养均衡",
                "如有不适，建议咨询专业中医师",
            ])

            return suggestions[:6]  # 限制建议数量

        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            return ["建议咨询专业中医师进行详细诊断"]

    def _calculate_overall_confidence(self, features: TongueFeatures) -> float:
        """计算整体置信度"""
        try:
            confidences = [
                features.body_color_confidence,
                features.coating_color_confidence,
                features.coating_thickness_confidence,
                features.texture_confidence,
            ]
            return sum(confidences) / len(confidences)
        except Exception:
            return 0.5


# 全局分析器实例
_tongue_analyzer: EnhancedTongueAnalyzer | None = None


async def get_tongue_analyzer() -> EnhancedTongueAnalyzer:
    """获取舌象分析器实例"""
    global _tongue_analyzer
    if _tongue_analyzer is None:
        _tongue_analyzer = EnhancedTongueAnalyzer()
    return _tongue_analyzer


async def cleanup_tongue_analyzer():
    """清理分析器资源"""
    global _tongue_analyzer
    if _tongue_analyzer:
        _tongue_analyzer = None
        logger.info("舌象分析器资源已清理")
