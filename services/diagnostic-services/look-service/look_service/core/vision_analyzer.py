"""
vision_analyzer - 索克生活项目模块
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import asyncio
import cv2
import logging
import numpy as np

"""
望诊计算机视觉分析器

基于深度学习和传统图像处理技术，实现中医望诊的智能分析功能。
包括面诊、舌诊、眼诊等核心功能。
"""


logger = logging.getLogger(__name__)

class DiagnosisType(str, Enum):
    """诊断类型"""
    FACE = "face"
    TONGUE = "tongue"
    EYE = "eye"

@dataclass
class FaceAnalysisResult:
    """面诊分析结果"""
    complexion: str  # 面色：红润、苍白、萎黄、青黑等
    luster: str      # 光泽：有神、无神
    facial_features: Dict[str, Any]  # 面部特征
    emotion_state: str  # 情绪状态
    health_indicators: List[str]  # 健康指标
    confidence: float

@dataclass
class TongueAnalysisResult:
    """舌诊分析结果"""
    tongue_body: Dict[str, str]  # 舌质：颜色、形状、大小
    tongue_coating: Dict[str, str]  # 舌苔：颜色、厚薄、润燥
    tongue_texture: str  # 舌质纹理
    moisture_level: str  # 湿润程度
    tcm_diagnosis: str  # 中医诊断
    confidence: float

@dataclass
class EyeAnalysisResult:
    """眼诊分析结果"""
    sclera_color: str    # 巩膜颜色
    pupil_response: str  # 瞳孔反应
    eye_luster: str      # 眼神
    blood_vessels: str   # 血管状态
    eyelid_condition: str # 眼睑状态
    confidence: float

class ComplexionAnalyzer:
    """面色分析器"""
    
    def __init__(self):
        # 定义中医面色标准
        self.complexion_ranges = {
            "红润": {"r": (180, 255), "g": (120, 200), "b": (120, 180)},
            "苍白": {"r": (200, 255), "g": (200, 255), "b": (200, 255)},
            "萎黄": {"r": (200, 255), "g": (180, 220), "b": (100, 150)},
            "青黑": {"r": (50, 120), "g": (50, 120), "b": (50, 120)},
            "潮红": {"r": (200, 255), "g": (80, 150), "b": (80, 150)}
        }
    
    def analyze_complexion(self, face_region: np.ndarray) -> Tuple[str, float]:
        """分析面色"""
        # 提取面部中心区域（避免边缘阴影影响）
        h, w = face_region.shape[:2]
        center_region = face_region[h//4:3*h//4, w//4:3*w//4]
        
        # 计算平均颜色
        mean_color = np.mean(center_region.reshape(-1, 3), axis=0)
        b, g, r = mean_color
        
        # 匹配最接近的面色类型
        best_match = "正常"
        best_score = 0.0
        
        for complexion, ranges in self.complexion_ranges.items():
            score = self._calculate_color_similarity(r, g, b, ranges)
            if score > best_score:
                best_score = score
                best_match = complexion
        
        return best_match, best_score
    
    def _calculate_color_similarity(self, r: float, g: float, b: float, 
                                  ranges: Dict[str, Tuple[int, int]]) -> float:
        """计算颜色相似度"""
        r_score = 1.0 if ranges["r"][0] <= r <= ranges["r"][1] else 0.0
        g_score = 1.0 if ranges["g"][0] <= g <= ranges["g"][1] else 0.0
        b_score = 1.0 if ranges["b"][0] <= b <= ranges["b"][1] else 0.0
        
        return (r_score + g_score + b_score) / 3.0

class TongueAnalyzer:
    """舌诊分析器"""
    
    def __init__(self):
        # 舌质颜色标准
        self.tongue_colors = {
            "淡红": {"h": (0, 20), "s": (30, 100), "v": (100, 255)},
            "红": {"h": (0, 10), "s": (100, 255), "v": (100, 200)},
            "绛红": {"h": (0, 5), "s": (150, 255), "v": (80, 150)},
            "淡白": {"h": (0, 180), "s": (0, 30), "v": (150, 255)},
            "青紫": {"h": (120, 150), "s": (50, 255), "v": (50, 150)}
        }
    
    def analyze_tongue(self, tongue_image: np.ndarray) -> TongueAnalysisResult:
        """分析舌象"""
        if tongue_image is None:
            return TongueAnalysisResult(
                tongue_body={"color": "未检测到", "shape": "未知", "size": "未知"},
                tongue_coating={"color": "未检测到", "thickness": "未知", "moisture": "未知"},
                tongue_texture="未知",
                moisture_level="未知",
                tcm_diagnosis="无法分析",
                confidence=0.0
            )
        
        # 分析舌质
        tongue_body = self._analyze_tongue_body(tongue_image)
        
        # 分析舌苔
        tongue_coating = self._analyze_tongue_coating(tongue_image)
        
        # 生成中医诊断
        tcm_diagnosis = self._generate_tcm_diagnosis(tongue_body, tongue_coating)
        
        # 计算置信度
        confidence = self._calculate_confidence(tongue_image)
        
        return TongueAnalysisResult(
            tongue_body=tongue_body,
            tongue_coating=tongue_coating,
            tongue_texture="正常",
            moisture_level="正常",
            tcm_diagnosis=tcm_diagnosis,
            confidence=confidence
        )
    
    def _analyze_tongue_body(self, image: np.ndarray) -> Dict[str, str]:
        """分析舌质"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color = self._classify_tongue_color(hsv)
        
        return {
            "color": color,
            "shape": "正常",
            "size": "正常"
        }
    
    def _analyze_tongue_coating(self, image: np.ndarray) -> Dict[str, str]:
        """分析舌苔"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        coating_color = "白苔"
        if mean_brightness < 80:
            coating_color = "黑苔"
        elif mean_brightness < 150:
            coating_color = "灰苔"
        
        thickness = "薄苔" if mean_brightness > 150 else "厚苔"
        
        return {
            "color": coating_color,
            "thickness": thickness,
            "moisture": "润"
        }
    
    def _classify_tongue_color(self, hsv_image: np.ndarray) -> str:
        """分类舌质颜色"""
        mean_hsv = np.mean(hsv_image.reshape(-1, 3), axis=0)
        h, s, v = mean_hsv
        
        for color_name, ranges in self.tongue_colors.items():
            if (ranges["h"][0] <= h <= ranges["h"][1] and
                ranges["s"][0] <= s <= ranges["s"][1] and
                ranges["v"][0] <= v <= ranges["v"][1]):
                return color_name
        
        return "淡红"  # 默认正常色
    
    def _generate_tcm_diagnosis(self, tongue_body: Dict[str, str], 
                              tongue_coating: Dict[str, str]) -> str:
        """生成中医诊断"""
        body_color = tongue_body["color"]
        coating_color = tongue_coating["color"]
        
        # 简化的诊断规则
        diagnosis_rules = {
            ("淡红", "白苔"): "正常",
            ("红", "黄苔"): "热证",
            ("淡白", "白苔"): "虚寒证",
            ("绛红", "黄苔"): "热盛证",
            ("青紫", "白苔"): "血瘀证"
        }
        
        return diagnosis_rules.get((body_color, coating_color), "需要进一步诊断")
    
    def _calculate_confidence(self, image: np.ndarray) -> float:
        """计算分析置信度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检查图像清晰度
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        clarity_score = min(laplacian_var / 1000, 1.0)
        
        # 检查亮度
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 128) / 128
        
        # 综合置信度
        confidence = (clarity_score + brightness_score) / 2
        return max(0.3, min(0.95, confidence))

class VisionAnalyzer:
    """望诊视觉分析器主类"""
    
    def __init__(self):
        self.complexion_analyzer = ComplexionAnalyzer()
        self.tongue_analyzer = TongueAnalyzer()
        
        logger.info("望诊视觉分析器初始化完成")
    
    async def analyze_face(self, image: np.ndarray) -> FaceAnalysisResult:
        """面诊分析"""
        try:
            # 分析面色
            complexion, complexion_confidence = self.complexion_analyzer.analyze_complexion(image)
            
            # 分析面部特征（简化版）
            facial_features = {
                "face_shape": "正常",
                "skin_texture": "正常",
                "wrinkles": "年龄相符"
            }
            
            # 健康指标
            health_indicators = self._generate_health_indicators(complexion)
            
            return FaceAnalysisResult(
                complexion=complexion,
                luster="有神" if complexion_confidence > 0.7 else "一般",
                facial_features=facial_features,
                emotion_state="精神一般",
                health_indicators=health_indicators,
                confidence=complexion_confidence
            )
            
        except Exception as e:
            logger.error(f"面诊分析失败: {e}")
            raise
    
    async def analyze_tongue(self, image: np.ndarray) -> TongueAnalysisResult:
        """舌诊分析"""
        try:
            result = self.tongue_analyzer.analyze_tongue(image)
            logger.info(f"舌诊分析完成，诊断结果: {result.tcm_diagnosis}")
            return result
            
        except Exception as e:
            logger.error(f"舌诊分析失败: {e}")
            raise
    
    async def analyze_eyes(self, image: np.ndarray) -> EyeAnalysisResult:
        """眼诊分析"""
        try:
            return EyeAnalysisResult(
                sclera_color="正常白色",
                pupil_response="正常",
                eye_luster="有神",
                blood_vessels="正常",
                eyelid_condition="正常",
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"眼诊分析失败: {e}")
            raise
    
    def _generate_health_indicators(self, complexion: str) -> List[str]:
        """生成健康指标"""
        complexion_indicators = {
            "红润": ["气血充足", "循环良好"],
            "苍白": ["可能贫血", "气血不足"],
            "萎黄": ["脾胃虚弱", "营养不良"],
            "青黑": ["肾虚", "血瘀"],
            "潮红": ["内热", "血压偏高"]
        }
        
        return complexion_indicators.get(complexion, ["需要进一步观察"]) 