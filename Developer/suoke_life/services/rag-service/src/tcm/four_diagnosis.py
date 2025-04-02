from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import numpy as np
from loguru import logger
import cv2
from pathlib import Path
import urllib.request
import tempfile
import os

class DiagnosisType(Enum):
    """四诊类型"""
    LOOK = "望诊"    # 望诊
    LISTEN = "闻诊"  # 闻诊
    ASK = "问诊"     # 问诊
    TOUCH = "切诊"   # 切诊

class TongueColor(Enum):
    """舌色"""
    PALE = "淡白"
    LIGHT_RED = "淡红"
    RED = "红"
    CRIMSON = "绛"
    PURPLE = "紫"
    BLUE = "青"

class TongueCoating(Enum):
    """舌苔"""
    THIN = "薄苔"
    THICK = "厚苔"
    WHITE = "白苔"
    YELLOW = "黄苔"
    GREY = "灰苔"
    BLACK = "黑苔"

class PulseType(Enum):
    """脉象"""
    FLOATING = "浮"  # 浮脉
    SINKING = "沉"   # 沉脉
    SLOW = "迟"      # 迟脉
    RAPID = "数"     # 数脉
    SLIPPERY = "滑"  # 滑脉
    ROUGH = "涩"     # 涩脉
    WIRY = "弦"      # 弦脉
    SOFT = "软"      # 软脉
    WEAK = "弱"      # 弱脉
    LARGE = "洪"     # 洪脉
    TIGHT = "紧"     # 紧脉
    FAINT = "微"     # 微脉
    EMPTY = "虚"     # 虚脉
    FULL = "实"      # 实脉
    LONG = "长"      # 长脉
    SHORT = "短"     # 短脉
    THREADY = "细"   # 细脉
    CHOPPY = "涩"    # 涩脉（与ROUGH相同）

@dataclass
class TongueData:
    """舌诊数据"""
    color: TongueColor
    coating: TongueCoating
    moisture: float  # 0-1，表示湿润度
    shape: str      # 舌体形态描述
    cracks: bool    # 是否有裂纹
    spots: bool     # 是否有斑点
    image_url: Optional[str] = None  # 舌照图片URL
    
@dataclass
class PulseLocation:
    """脉诊部位"""
    position: str   # 部位名称
    pulse_type: PulseType  # 脉象类型
    strength: float  # 脉力 (0-1)
    depth: float     # 深度 (0-1，0为最浅，1为最深)
    
@dataclass
class PulseData:
    """脉诊数据"""
    left_cun: PulseType  # 左寸
    left_guan: PulseType # 左关
    left_chi: PulseType  # 左尺
    right_cun: PulseType # 右寸
    right_guan: PulseType# 右关
    right_chi: PulseType # 右尺
    rhythm: str          # 脉律
    strength: float      # 0-1，表示脉力
    frequency: int = 0   # 脉率，每分钟次数
    regularity: float = 1.0  # 规律性 (0-1)
    width: float = 0.5   # 脉宽 (0-1)
    depth_score: float = 0.5  # 脉象深浅度 (0-1)
    
    def to_locations(self) -> List[PulseLocation]:
        """转换为脉位集合"""
        return [
            PulseLocation("左寸", self.left_cun, self.strength, self.depth_score),
            PulseLocation("左关", self.left_guan, self.strength, self.depth_score),
            PulseLocation("左尺", self.left_chi, self.strength, self.depth_score),
            PulseLocation("右寸", self.right_cun, self.strength, self.depth_score),
            PulseLocation("右关", self.right_guan, self.strength, self.depth_score),
            PulseLocation("右尺", self.right_chi, self.strength, self.depth_score),
        ]

@dataclass
class FourDiagnosticData:
    """四诊数据"""
    patient_id: str
    timestamp: datetime
    # 望诊数据
    tongue_data: TongueData
    face_color: str
    body_shape: str
    movement: str
    # 闻诊数据
    voice: str
    breath: str
    odor: str
    # 问诊数据
    chief_complaint: str
    history: Dict[str, str]
    # 切诊数据
    pulse_data: PulseData
    body_temperature: float
    skin_texture: str

class FourDiagnosticProcessor:
    def __init__(self):
        """初始化四诊数据处理器"""
        self.diagnostic_weights = {
            DiagnosisType.LOOK: 0.3,
            DiagnosisType.LISTEN: 0.2,
            DiagnosisType.ASK: 0.3,
            DiagnosisType.TOUCH: 0.2
        }
        # 舌色参考颜色值 (BGR格式)
        self.tongue_color_references = {
            TongueColor.PALE: np.array([200, 180, 180]),
            TongueColor.LIGHT_RED: np.array([160, 120, 190]),
            TongueColor.RED: np.array([120, 90, 200]),
            TongueColor.CRIMSON: np.array([100, 70, 210]),
            TongueColor.PURPLE: np.array([150, 90, 150]),
            TongueColor.BLUE: np.array([180, 120, 100])
        }
        # 舌苔参考颜色值 (BGR格式)
        self.coating_color_references = {
            TongueCoating.WHITE: np.array([230, 230, 230]),
            TongueCoating.YELLOW: np.array([160, 200, 220]),
            TongueCoating.GREY: np.array([150, 150, 150]),
            TongueCoating.BLACK: np.array([70, 70, 70])
        }
        
        # 脉象与证型关联映射
        self.pulse_pattern_mapping = {
            PulseType.FLOATING: ["表证", "风邪", "气虚"],
            PulseType.SINKING: ["里证", "寒证", "沉重感"],
            PulseType.SLOW: ["寒证", "阳虚", "气滞"],
            PulseType.RAPID: ["热证", "阴虚", "气促"],
            PulseType.SLIPPERY: ["痰湿", "食积", "妊娠"],
            PulseType.ROUGH: ["血虚", "气血亏虚", "津液不足"],
            PulseType.WIRY: ["肝胆病证", "疼痛", "寒热往来"],
            PulseType.SOFT: ["气虚", "湿证", "虚寒"],
            PulseType.WEAK: ["气血两虚", "脾肾亏虚"],
            PulseType.LARGE: ["热证", "阳盛", "气血壅盛"],
            PulseType.TIGHT: ["寒证", "痛证", "饮食停滞"],
            PulseType.FAINT: ["气血亏虚", "元气将脱"],
            PulseType.EMPTY: ["血虚", "元气不足"],
            PulseType.FULL: ["实证", "邪气盛"],
            PulseType.LONG: ["气血和调", "心气盛"],
            PulseType.SHORT: ["气血不足", "心气虚"],
            PulseType.THREADY: ["细脉", "气血两虚"],
            PulseType.CHOPPY: ["涩脉", "气血两虚"]
        }
        
        # 脉位与脏腑对应关系
        self.pulse_location_organ_mapping = {
            "左寸": ["心", "心包"],
            "左关": ["肝", "胆"],
            "左尺": ["肾阴", "膀胱"],
            "右寸": ["肺", "大肠"],
            "右关": ["脾", "胃"],
            "右尺": ["肾阳", "小肠"]
        }
        
    def process_tongue_image(self, image_url: str) -> Optional[TongueData]:
        """处理舌诊图像
        
        Args:
            image_url: 舌照图片URL或本地路径
            
        Returns:
            TongueData: 舌诊数据对象，包含舌色、舌苔、湿润度等信息
        """
        try:
            # 1. 加载图像
            image = self._load_image(image_url)
            if image is None:
                logger.error(f"无法加载图像: {image_url}")
                return None
                
            # 2. 图像预处理
            preprocessed_image = self._preprocess_image(image)
            
            # 3. 舌体分割
            tongue_mask, success = self._segment_tongue(preprocessed_image)
            if not success:
                logger.error("舌体分割失败")
                return None
                
            # 应用掩码提取舌体区域
            tongue_region = cv2.bitwise_and(preprocessed_image, preprocessed_image, mask=tongue_mask)
            
            # 4. 舌色识别
            tongue_color = self._analyze_tongue_color(tongue_region, tongue_mask)
            
            # 5. 舌苔分析
            coating_type, coating_mask = self._analyze_tongue_coating(tongue_region, tongue_mask)
            
            # 6. 舌体形态分析
            shape, cracks, spots = self._analyze_tongue_shape(tongue_region, tongue_mask)
            
            # 7. 舌体湿润度分析
            moisture = self._analyze_moisture(tongue_region, tongue_mask)
            
            # 8. 构建舌诊数据对象
            tongue_data = TongueData(
                color=tongue_color,
                coating=coating_type,
                moisture=moisture,
                shape=shape,
                cracks=cracks,
                spots=spots,
                image_url=image_url
            )
            
            logger.info(f"舌诊分析完成: {tongue_data}")
            return tongue_data
            
        except Exception as e:
            logger.error(f"舌诊图像处理错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _load_image(self, image_url: str) -> Optional[np.ndarray]:
        """加载图像，支持URL和本地路径
        
        Args:
            image_url: 图像URL或本地路径
            
        Returns:
            np.ndarray: 加载的图像数据
        """
        try:
            # 检查是否为URL
            if image_url.startswith(('http://', 'https://')):
                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_path = tmp_file.name
                
                # 下载图像
                urllib.request.urlretrieve(image_url, tmp_path)
                
                # 读取图像
                image = cv2.imread(tmp_path)
                
                # 删除临时文件
                os.unlink(tmp_path)
            else:
                # 读取本地图像
                image = cv2.imread(image_url)
                
            if image is None:
                logger.error(f"无法读取图像: {image_url}")
                return None
                
            return image
            
        except Exception as e:
            logger.error(f"图像加载错误: {e}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """图像预处理
        
        Args:
            image: 原始图像
            
        Returns:
            np.ndarray: 预处理后的图像
        """
        try:
            # 调整图像大小至标准尺寸
            resized = cv2.resize(image, (640, 480))
            
            # 去噪
            denoised = cv2.fastNlMeansDenoisingColored(resized, None, 10, 10, 7, 21)
            
            # 增强对比度
            lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl, a, b))
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"图像预处理错误: {e}")
            # 如果处理失败，返回原图
            return image
    
    def _segment_tongue(self, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        """舌体分割
        
        Args:
            image: 预处理后的图像
            
        Returns:
            Tuple[np.ndarray, bool]: 舌体掩码和分割是否成功
        """
        try:
            # 转换到HSV色彩空间，有利于分割舌体
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 舌体颜色范围 (红色到粉红色范围)
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            # 创建掩码
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2
            
            # 应用形态学操作改善掩码质量
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # 找到最大连通区域 (假设为舌体)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return np.zeros_like(mask), False
                
            # 找到最大轮廓
            max_contour = max(contours, key=cv2.contourArea)
            
            # 创建空白掩码
            refined_mask = np.zeros_like(mask)
            
            # 填充最大轮廓
            cv2.drawContours(refined_mask, [max_contour], 0, 255, -1)
            
            # 应用高斯模糊平滑边缘
            refined_mask = cv2.GaussianBlur(refined_mask, (5, 5), 0)
            
            # 二值化
            _, refined_mask = cv2.threshold(refined_mask, 127, 255, cv2.THRESH_BINARY)
            
            return refined_mask, True
            
        except Exception as e:
            logger.error(f"舌体分割错误: {e}")
            return np.zeros_like(image[:,:,0]), False
    
    def _analyze_tongue_color(self, image: np.ndarray, mask: np.ndarray) -> TongueColor:
        """分析舌色
        
        Args:
            image: 舌体区域图像
            mask: 舌体掩码
            
        Returns:
            TongueColor: 识别的舌色
        """
        try:
            # 获取舌体非舌苔区域 (边缘区域更能反映舌色)
            # 对掩码进行腐蚀操作去除边缘
            kernel = np.ones((15, 15), np.uint8)
            eroded_mask = cv2.erode(mask, kernel, iterations=1)
            
            # 舌体边缘 = 原掩码 - 腐蚀掩码
            edge_mask = cv2.subtract(mask, eroded_mask)
            
            # 提取边缘区域的颜色
            edge_region = cv2.bitwise_and(image, image, mask=edge_mask)
            
            # 计算非零像素的平均颜色
            non_zero_pixels = edge_region[edge_mask > 0]
            if len(non_zero_pixels) == 0:
                return TongueColor.LIGHT_RED  # 默认舌色
                
            avg_color = np.mean(non_zero_pixels, axis=0)
            
            # 寻找最接近的舌色
            min_dist = float('inf')
            closest_color = TongueColor.LIGHT_RED
            
            for color, ref_value in self.tongue_color_references.items():
                dist = np.linalg.norm(avg_color - ref_value)
                if dist < min_dist:
                    min_dist = dist
                    closest_color = color
                    
            return closest_color
            
        except Exception as e:
            logger.error(f"舌色分析错误: {e}")
            return TongueColor.LIGHT_RED  # 默认舌色
    
    def _analyze_tongue_coating(self, image: np.ndarray, mask: np.ndarray) -> Tuple[TongueCoating, np.ndarray]:
        """分析舌苔
        
        Args:
            image: 舌体区域图像
            mask: 舌体掩码
            
        Returns:
            Tuple[TongueCoating, np.ndarray]: 舌苔类型和舌苔掩码
        """
        try:
            # 转换到灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 应用掩码
            masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
            
            # 获取有效像素值
            valid_pixels = masked_gray[mask > 0]
            if len(valid_pixels) == 0:
                return TongueCoating.THIN, np.zeros_like(mask)
                
            # 使用OTSU自适应阈值
            _, coating_mask = cv2.threshold(
                masked_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            
            # 计算舌苔覆盖比例
            coating_area = np.sum(coating_mask > 0)
            tongue_area = np.sum(mask > 0)
            coverage_ratio = coating_area / tongue_area if tongue_area > 0 else 0
            
            # 确定舌苔厚度
            coating_type = TongueCoating.THICK if coverage_ratio > 0.4 else TongueCoating.THIN
            
            # 计算舌苔区域的平均颜色
            coating_region = cv2.bitwise_and(image, image, mask=coating_mask)
            non_zero_pixels = coating_region[coating_mask > 0]
            if len(non_zero_pixels) == 0:
                return coating_type, coating_mask
                
            avg_color = np.mean(non_zero_pixels, axis=0)
            
            # 寻找最接近的舌苔颜色
            min_dist = float('inf')
            closest_coating = TongueCoating.WHITE
            
            for coating, ref_value in self.coating_color_references.items():
                if coating in [TongueCoating.THIN, TongueCoating.THICK]:
                    continue  # 跳过厚度类型
                    
                dist = np.linalg.norm(avg_color - ref_value)
                if dist < min_dist:
                    min_dist = dist
                    closest_coating = coating
            
            # 组合厚度和颜色
            if coating_type == TongueCoating.THICK and closest_coating != TongueCoating.WHITE:
                return closest_coating, coating_mask
            else:
                return closest_coating, coating_mask
            
        except Exception as e:
            logger.error(f"舌苔分析错误: {e}")
            return TongueCoating.THIN, np.zeros_like(mask)
    
    def _analyze_tongue_shape(self, image: np.ndarray, mask: np.ndarray) -> Tuple[str, bool, bool]:
        """分析舌体形态
        
        Args:
            image: 舌体区域图像
            mask: 舌体掩码
            
        Returns:
            Tuple[str, bool, bool]: 舌体形态描述、是否有裂纹、是否有斑点
        """
        try:
            # 找到轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return "普通舌", False, False
                
            # 获取最大轮廓
            contour = max(contours, key=cv2.contourArea)
            
            # 计算长宽比和面积
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            area = cv2.contourArea(contour)
            hull_area = cv2.contourArea(cv2.convexHull(contour))
            solidity = float(area) / hull_area if hull_area > 0 else 0
            
            # 确定舌体形态
            shape = "普通舌"
            if aspect_ratio < 0.6:
                shape = "瘦舌"
            elif aspect_ratio > 1.2:
                shape = "胖舌"
                
            if solidity < 0.8:
                shape = "歪斜舌" if "舌" in shape else shape + "歪斜"
                
            # 检测裂纹
            # 转换到灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
            
            # 使用Canny边缘检测
            edges = cv2.Canny(masked_gray, 50, 150)
            
            # 用于检测直线的霍夫变换
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=40, maxLineGap=10)
            has_cracks = lines is not None and len(lines) > 5
            
            # 检测斑点
            # 增强对比度
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced_gray = clahe.apply(masked_gray)
            
            # 寻找局部颜色异常区域
            _, binary = cv2.threshold(enhanced_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            spot_contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            # 过滤小斑点
            spot_contours = [c for c in spot_contours if 10 < cv2.contourArea(c) < 100]
            has_spots = len(spot_contours) > 3
            
            return shape, has_cracks, has_spots
            
        except Exception as e:
            logger.error(f"舌体形态分析错误: {e}")
            return "普通舌", False, False
    
    def _analyze_moisture(self, image: np.ndarray, mask: np.ndarray) -> float:
        """分析舌体湿润度
        
        Args:
            image: 舌体区域图像
            mask: 舌体掩码
            
        Returns:
            float: 湿润度得分 (0-1)
        """
        try:
            # 转换到HSV色彩空间
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 提取饱和度通道（S通道）
            _, s, v = cv2.split(hsv)
            
            # 应用掩码
            masked_s = cv2.bitwise_and(s, s, mask=mask)
            masked_v = cv2.bitwise_and(v, v, mask=mask)
            
            # 计算饱和度平均值和亮度平均值
            valid_pixels_s = masked_s[mask > 0]
            valid_pixels_v = masked_v[mask > 0]
            
            if len(valid_pixels_s) == 0 or len(valid_pixels_v) == 0:
                return 0.5  # 默认中等湿润度
                
            avg_saturation = np.mean(valid_pixels_s)
            avg_value = np.mean(valid_pixels_v)
            
            # 归一化到0-1范围
            # 亮度高和饱和度低通常表示更湿润的舌头
            saturation_factor = 1.0 - (avg_saturation / 255.0)
            value_factor = avg_value / 255.0
            
            # 计算加权得分
            moisture_score = (saturation_factor * 0.7) + (value_factor * 0.3)
            moisture_score = max(0.0, min(1.0, moisture_score))
            
            return moisture_score
            
        except Exception as e:
            logger.error(f"湿润度分析错误: {e}")
            return 0.5  # 默认中等湿润度
            
    def _analyze_tongue_data(self, tongue_data: TongueData) -> Dict[str, Any]:
        """分析舌诊数据"""
        try:
            results = {
                "color": tongue_data.color.value,
                "coating": tongue_data.coating.value,
                "moisture": tongue_data.moisture,
                "shape": tongue_data.shape,
                "cracks": tongue_data.cracks,
                "spots": tongue_data.spots,
                "indications": []
            }
            
            # 根据舌色添加指征
            if tongue_data.color == TongueColor.PALE:
                results["indications"].append("气血亏虚")
            elif tongue_data.color == TongueColor.RED:
                results["indications"].append("热证")
            elif tongue_data.color == TongueColor.CRIMSON:
                results["indications"].append("热重证")
            elif tongue_data.color == TongueColor.PURPLE:
                results["indications"].append("瘀血证")
            elif tongue_data.color == TongueColor.BLUE:
                results["indications"].append("寒证")
                
            # 根据舌苔添加指征
            if tongue_data.coating == TongueCoating.WHITE:
                results["indications"].append("表证或寒证")
            elif tongue_data.coating == TongueCoating.YELLOW:
                results["indications"].append("里证或热证")
            elif tongue_data.coating == TongueCoating.GREY:
                results["indications"].append("寒湿或痰浊")
            elif tongue_data.coating == TongueCoating.BLACK:
                results["indications"].append("重症热证或寒证")
                
            # 根据湿润度添加指征
            if tongue_data.moisture < 0.3:
                results["indications"].append("津液亏少")
            elif tongue_data.moisture > 0.7:
                results["indications"].append("水湿内停")
                
            # 根据形态添加指征
            if "瘦" in tongue_data.shape:
                results["indications"].append("气血不足")
            elif "胖" in tongue_data.shape:
                results["indications"].append("水湿内盛")
                
            # 根据裂纹和斑点添加指征
            if tongue_data.cracks:
                results["indications"].append("阴虚")
            if tongue_data.spots:
                results["indications"].append("热毒")
                
            return results
            
        except Exception as e:
            logger.error(f"舌诊数据分析错误: {e}")
            return {
                "color": "未知",
                "coating": "未知",
                "moisture": 0.5,
                "indications": ["分析失败"]
            }
            
    def analyze_pulse_data(self, pulse_data: PulseData) -> Dict[str, Any]:
        """分析脉诊数据
        
        Args:
            pulse_data: 脉诊数据对象
            
        Returns:
            Dict[str, Any]: 分析结果，包含各项评分和证型推断
        """
        try:
            # 转换为位置列表
            locations = pulse_data.to_locations()
            
            # 基本评分
            rhythm_score = self._calculate_rhythm_score(pulse_data.rhythm)
            balance_score = self._calculate_balance_score(pulse_data)
            quality_score = self._calculate_quality_score(pulse_data)
            regularity_score = pulse_data.regularity
            
            # 脉率评分
            rate_score = self._calculate_rate_score(pulse_data.frequency)
            
            # 脉象特征向量化
            pulse_features = {
                "rhythm_score": rhythm_score,
                "strength_score": pulse_data.strength,
                "balance_score": balance_score,
                "quality_score": quality_score,
                "regularity_score": regularity_score,
                "rate_score": rate_score,
                "width_score": self._normalize_width_score(pulse_data.width),
                "depth_score": self._normalize_depth_score(pulse_data.depth_score)
            }
            
            # 综合脉象得分
            overall_score = np.mean(list(pulse_features.values()))
            
            # 脉象证型分析
            pattern_analysis = self._analyze_pulse_patterns(pulse_data)
            
            # 脏腑关联分析
            organ_analysis = self._analyze_pulse_organs(pulse_data)
            
            # 异常脉象组合分析
            combination_analysis = self._analyze_pulse_combinations(pulse_data)
            
            return {
                "scores": pulse_features,
                "overall_score": float(overall_score),
                "patterns": pattern_analysis,
                "organ_relations": organ_analysis,
                "combinations": combination_analysis,
                "summary": self._generate_pulse_summary(pulse_data, overall_score)
            }
            
        except Exception as e:
            logger.error(f"脉诊数据分析错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "scores": {
                    "overall_score": 0.0
                },
                "patterns": [],
                "error": str(e)
            }
            
    def _calculate_rhythm_score(self, rhythm: str) -> float:
        """计算脉律得分"""
        rhythm_scores = {
            "均匀": 1.0,
            "不均匀": 0.5,
            "结代": 0.3,
            "促": 0.4,
            "缓": 0.7,
            "代": 0.2,
            "革": 0.3,
            "动": 0.4,
            "伏": 0.5
        }
        return rhythm_scores.get(rhythm, 0.5)
        
    def _calculate_rate_score(self, frequency: int) -> float:
        """计算脉率得分
        
        Args:
            frequency: 每分钟脉搏次数
            
        Returns:
            float: 脉率评分 (0-1)
        """
        # 正常脉率：60-90次/分钟
        if frequency == 0:  # 未提供脉率
            return 0.5
        
        if 60 <= frequency <= 90:
            return 1.0
        elif frequency < 60:
            # 脉率过慢
            return max(0.0, 0.5 + (frequency - 40) / 40)
        else:
            # 脉率过快
            return max(0.0, 1.0 - (frequency - 90) / 60)
        
    def _normalize_width_score(self, width: float) -> float:
        """归一化脉宽评分
        
        Args:
            width: 原始脉宽值 (0-1)
            
        Returns:
            float: 归一化后的评分
        """
        # 正常脉宽约为0.4-0.6
        if 0.4 <= width <= 0.6:
            return 1.0
        elif width < 0.4:
            # 脉窄
            return 0.5 + width
        else:
            # 脉宽
            return 1.5 - width
    
    def _normalize_depth_score(self, depth: float) -> float:
        """归一化脉深评分
        
        Args:
            depth: 原始脉深值 (0-1，0表示最浅，1表示最深)
            
        Returns:
            float: 归一化后的评分
        """
        # 正常脉深约为0.3-0.7
        if 0.3 <= depth <= 0.7:
            return 1.0
        elif depth < 0.3:
            # 脉浅
            return 0.5 + depth
        else:
            # 脉深
            return 1.5 - depth
            
    def _calculate_balance_score(self, pulse_data: PulseData) -> float:
        """计算脉象平衡得分
        
        Args:
            pulse_data: 脉诊数据
            
        Returns:
            float: 脉象平衡得分 (0-1)
        """
        try:
            # 比较左右脉
            left_types = [pulse_data.left_cun, pulse_data.left_guan, pulse_data.left_chi]
            right_types = [pulse_data.right_cun, pulse_data.right_guan, pulse_data.right_chi]
            
            # 计算对称性
            symmetry_score = sum(1 for l, r in zip(left_types, right_types) if l == r) / 3
            
            # 计算各脉位间的协调性
            harmony_left = self._calculate_positions_harmony(left_types)
            harmony_right = self._calculate_positions_harmony(right_types)
            
            # 左右手整体协调性
            overall_harmony = (harmony_left + harmony_right) / 2
            
            # 综合评分
            return (symmetry_score * 0.6) + (overall_harmony * 0.4)
            
        except Exception as e:
            logger.error(f"脉象平衡评分错误: {e}")
            return 0.5
    
    def _calculate_positions_harmony(self, pulse_types: List[PulseType]) -> float:
        """计算脉位间协调度
        
        Args:
            pulse_types: 一侧三个脉位的类型
            
        Returns:
            float: 协调度评分 (0-1)
        """
        # 某些脉象组合被认为更协调
        harmonious_combinations = [
            {PulseType.FLOATING, PulseType.SLIPPERY, PulseType.RAPID},  # 常见于阳热证
            {PulseType.SINKING, PulseType.SLOW, PulseType.TIGHT},       # 常见于阴寒证
            {PulseType.WIRY, PulseType.RAPID, PulseType.SLIPPERY},      # 常见于肝胆热证
            {PulseType.FLOATING, PulseType.EMPTY, PulseType.WEAK},      # 常见于气血虚证
        ]
        
        pulse_set = set(pulse_types)
        
        # 如果完全匹配一种协调组合，得分高
        for combo in harmonious_combinations:
            if pulse_set.issubset(combo):
                return 0.9
                
        # 如果大部分匹配
        max_overlap = max(len(pulse_set.intersection(combo)) for combo in harmonious_combinations)
        
        # 根据最大重叠度计算协调性
        harmony_score = max_overlap / 3
        
        return harmony_score
            
    def _calculate_quality_score(self, pulse_data: PulseData) -> float:
        """计算脉象质量得分
        
        Args:
            pulse_data: 脉诊数据
            
        Returns:
            float: 脉象质量得分 (0-1)
        """
        try:
            # 定义健康脉象特征
            healthy_features = {
                PulseType.FLOATING: 0.1,  # 健康脉略浮
                PulseType.SLIPPERY: 0.2,  # 健康脉略滑
                PulseType.LONG: 0.1,      # 健康脉略长
                PulseType.SOFT: 0.1       # 健康脉略软
            }
            
            # 不健康脉象特征
            unhealthy_features = {
                PulseType.FAINT: -0.2,    # 微脉多见于重症
                PulseType.TIGHT: -0.1,    # 紧脉多见于寒证或痛证
                PulseType.ROUGH: -0.1,    # 涩脉多见于血虚
                PulseType.WEAK: -0.2      # 弱脉多见于虚证
            }
            
            # 统计各类脉象
            pulse_counts = {}
            all_pulses = [
                pulse_data.left_cun, pulse_data.left_guan, pulse_data.left_chi,
                pulse_data.right_cun, pulse_data.right_guan, pulse_data.right_chi
            ]
            
            for pulse in all_pulses:
                pulse_counts[pulse] = pulse_counts.get(pulse, 0) + 1
            
            # 基础评分为0.5
            base_score = 0.5
            
            # 加上健康特征得分
            for pulse_type, weight in healthy_features.items():
                count = pulse_counts.get(pulse_type, 0)
                base_score += (count / 6) * weight
                
            # 减去不健康特征得分
            for pulse_type, weight in unhealthy_features.items():
                count = pulse_counts.get(pulse_type, 0)
                base_score += (count / 6) * weight
            
            # 确保得分在0-1范围内
            final_score = max(0.0, min(1.0, base_score))
            
            # 调整脉率因素
            if hasattr(pulse_data, "frequency") and pulse_data.frequency > 0:
                rate_factor = self._calculate_rate_score(pulse_data.frequency)
                final_score = (final_score * 0.7) + (rate_factor * 0.3)
                
            # 调整规律性因素
            if hasattr(pulse_data, "regularity"):
                final_score = (final_score * 0.8) + (pulse_data.regularity * 0.2)
            
            return final_score
            
        except Exception as e:
            logger.error(f"脉象质量评分错误: {e}")
            return 0.5
            
    def _analyze_pulse_patterns(self, pulse_data: PulseData) -> List[Dict[str, Any]]:
        """分析脉象对应的证型
        
        Args:
            pulse_data: 脉诊数据
            
        Returns:
            List[Dict[str, Any]]: 证型列表，包含证型名称和可能性
        """
        try:
            # 统计各类脉象及位置
            pulse_types = {}
            
            # 各脉位的脉象
            positions = {
                "左寸": pulse_data.left_cun,
                "左关": pulse_data.left_guan,
                "左尺": pulse_data.left_chi,
                "右寸": pulse_data.right_cun,
                "右关": pulse_data.right_guan,
                "右尺": pulse_data.right_chi
            }
            
            # 按脉象类型分组
            for position, pulse_type in positions.items():
                if pulse_type not in pulse_types:
                    pulse_types[pulse_type] = []
                pulse_types[pulse_type].append(position)
            
            # 收集证型与关联脉位
            patterns = []
            
            for pulse_type, pos_list in pulse_types.items():
                # 获取该脉象对应的证型
                if pulse_type in self.pulse_pattern_mapping:
                    for pattern in self.pulse_pattern_mapping[pulse_type]:
                        # 计算该证型的可能性 (脉位数量/总脉位)
                        probability = len(pos_list) / 6
                        
                        # 整合相同证型
                        existing = next((p for p in patterns if p["name"] == pattern), None)
                        if existing:
                            existing["probability"] = max(existing["probability"], probability)
                            existing["positions"].extend(pos_list)
                            # 去重
                            existing["positions"] = list(set(existing["positions"]))
                            # 增加脉象类型
                            existing["pulse_types"].append(pulse_type.value)
                            existing["pulse_types"] = list(set(existing["pulse_types"]))
                        else:
                            patterns.append({
                                "name": pattern,
                                "probability": probability,
                                "positions": pos_list,
                                "pulse_types": [pulse_type.value]
                            })
            
            # 排序并返回前5个最可能的证型
            sorted_patterns = sorted(patterns, key=lambda x: x["probability"], reverse=True)
            return sorted_patterns[:5]
            
        except Exception as e:
            logger.error(f"脉象证型分析错误: {e}")
            return []
            
    def _analyze_pulse_organs(self, pulse_data: PulseData) -> List[Dict[str, Any]]:
        """分析脉象对应的脏腑关联
        
        Args:
            pulse_data: 脉诊数据
            
        Returns:
            List[Dict[str, Any]]: 脏腑关联列表
        """
        try:
            # 各脉位的脉象
            positions = {
                "左寸": pulse_data.left_cun,
                "左关": pulse_data.left_guan,
                "左尺": pulse_data.left_chi,
                "右寸": pulse_data.right_cun,
                "右关": pulse_data.right_guan,
                "右尺": pulse_data.right_chi
            }
            
            # 异常脉象类型
            abnormal_types = [
                PulseType.RAPID, PulseType.SLOW, PulseType.WIRY, 
                PulseType.TIGHT, PulseType.WEAK, PulseType.FAINT,
                PulseType.EMPTY, PulseType.ROUGH
            ]
            
            organ_relations = []
            
            for position, pulse_type in positions.items():
                # 如果是异常脉象，添加对应的脏腑关联
                if pulse_type in abnormal_types:
                    # 获取对应的脏腑
                    organs = self.pulse_location_organ_mapping.get(position, [])
                    
                    # 寒热虚实判断
                    condition = ""
                    if pulse_type in [PulseType.RAPID, PulseType.LARGE, PulseType.FULL]:
                        condition = "热" if pulse_type == PulseType.RAPID else "实"
                    elif pulse_type in [PulseType.SLOW, PulseType.TIGHT]:
                        condition = "寒"
                    elif pulse_type in [PulseType.WEAK, PulseType.FAINT, PulseType.EMPTY]:
                        condition = "虚"
                    elif pulse_type == PulseType.WIRY:
                        condition = "郁"
                    elif pulse_type == PulseType.ROUGH:
                        condition = "虚"
                    
                    for organ in organs:
                        organ_relations.append({
                            "organ": organ,
                            "position": position,
                            "pulse_type": pulse_type.value,
                            "condition": condition,
                            "description": f"{organ}{condition}" if condition else organ
                        })
            
            return organ_relations
            
        except Exception as e:
            logger.error(f"脉象脏腑关联分析错误: {e}")
            return []
    
    def _analyze_pulse_combinations(self, pulse_data: PulseData) -> List[Dict[str, str]]:
        """分析特殊脉象组合
        
        Args:
            pulse_data: 脉诊数据
            
        Returns:
            List[Dict[str, str]]: 脉象组合分析结果
        """
        try:
            combinations = []
            
            # 寸关尺各脉位的脉象
            left_pulses = [pulse_data.left_cun, pulse_data.left_guan, pulse_data.left_chi]
            right_pulses = [pulse_data.right_cun, pulse_data.right_guan, pulse_data.right_chi]
            
            # 特殊组合1：浮数脉 - 表热证
            if (PulseType.FLOATING in left_pulses or PulseType.FLOATING in right_pulses) and \
               (PulseType.RAPID in left_pulses or PulseType.RAPID in right_pulses):
                combinations.append({
                    "name": "浮数脉",
                    "indication": "表热证，如风热感冒，肺炎初期"
                })
                
            # 特殊组合2：沉迟脉 - 里寒证
            if (PulseType.SINKING in left_pulses or PulseType.SINKING in right_pulses) and \
               (PulseType.SLOW in left_pulses or PulseType.SLOW in right_pulses):
                combinations.append({
                    "name": "沉迟脉",
                    "indication": "里寒证，如脾胃虚寒，阳虚证"
                })
                
            # 特殊组合3：弦滑脉 - 肝胆湿热
            if (PulseType.WIRY in left_pulses or PulseType.WIRY in right_pulses) and \
               (PulseType.SLIPPERY in left_pulses or PulseType.SLIPPERY in right_pulses):
                combinations.append({
                    "name": "弦滑脉",
                    "indication": "肝胆湿热，胆道疾病"
                })
                
            # 特殊组合4：细涩脉 - 血虚证
            has_weak = PulseType.WEAK in left_pulses or PulseType.WEAK in right_pulses
            has_rough = PulseType.ROUGH in left_pulses or PulseType.ROUGH in right_pulses
            has_empty = PulseType.EMPTY in left_pulses or PulseType.EMPTY in right_pulses
            
            if (has_weak or has_empty) and has_rough:
                combinations.append({
                    "name": "细涩脉",
                    "indication": "血虚证，如贫血，妇女月经不调"
                })
                
            # 特殊组合5：浮大脉 - 阳盛发热
            if (PulseType.FLOATING in left_pulses or PulseType.FLOATING in right_pulses) and \
               (PulseType.LARGE in left_pulses or PulseType.LARGE in right_pulses):
                combinations.append({
                    "name": "浮大脉",
                    "indication": "阳盛发热，外感热病"
                })
                
            # 特殊组合6：沉紧脉 - 寒疼痛
            if (PulseType.SINKING in left_pulses or PulseType.SINKING in right_pulses) and \
               (PulseType.TIGHT in left_pulses or PulseType.TIGHT in right_pulses):
                combinations.append({
                    "name": "沉紧脉",
                    "indication": "寒性疼痛，如腹痛腰痛"
                })
                
            return combinations
            
        except Exception as e:
            logger.error(f"脉象组合分析错误: {e}")
            return []
    
    def _generate_pulse_summary(self, pulse_data: PulseData, overall_score: float) -> str:
        """生成脉诊总结
        
        Args:
            pulse_data: 脉诊数据
            overall_score: 综合评分
            
        Returns:
            str: 脉诊总结描述
        """
        try:
            # 统计各脉位的类型
            positions = {
                "左寸": pulse_data.left_cun,
                "左关": pulse_data.left_guan,
                "左尺": pulse_data.left_chi,
                "右寸": pulse_data.right_cun,
                "右关": pulse_data.right_guan,
                "右尺": pulse_data.right_chi
            }
            
            # 找出出现频率最高的脉象类型
            pulse_counts = {}
            for pulse_type in positions.values():
                pulse_counts[pulse_type] = pulse_counts.get(pulse_type, 0) + 1
                
            dominant_pulses = sorted(pulse_counts.items(), key=lambda x: x[1], reverse=True)
            
            # 构建描述
            dominant_type = dominant_pulses[0][0] if dominant_pulses else None
            summary_parts = []
            
            # 总体描述
            if dominant_type:
                if pulse_counts[dominant_type] >= 4:  # 如果某种脉象出现在大多数位置
                    summary_parts.append(f"以{dominant_type.value}脉为主")
                else:
                    pulse_types = []
                    for i, (pulse_type, _) in enumerate(dominant_pulses[:3]):
                        if i >= 2 or pulse_counts[pulse_type] < 2:
                            break
                        pulse_types.append(pulse_type.value)
                    
                    if pulse_types:
                        summary_parts.append(f"兼见{'、'.join(pulse_types)}脉")
            
            # 添加脉律描述
            rhythm_desc = f"脉律{pulse_data.rhythm}" if pulse_data.rhythm else ""
            if rhythm_desc:
                summary_parts.append(rhythm_desc)
                
            # 添加脉率描述
            if pulse_data.frequency > 0:
                rate_desc = ""
                if pulse_data.frequency < 60:
                    rate_desc = "脉率缓慢"
                elif pulse_data.frequency > 90:
                    rate_desc = "脉率偏快"
                else:
                    rate_desc = "脉率正常"
                    
                if rate_desc:
                    summary_parts.append(rate_desc)
            
            # 添加整体评估
            if overall_score >= 0.8:
                summary_parts.append("脉象基本正常")
            elif overall_score >= 0.6:
                summary_parts.append("脉象稍有异常")
            elif overall_score >= 0.4:
                summary_parts.append("脉象明显异常")
            else:
                summary_parts.append("脉象严重异常")
                
            return "，".join(summary_parts) + "。"
            
        except Exception as e:
            logger.error(f"脉诊总结生成错误: {e}")
            return "脉象分析异常。"

    def analyze_four_diagnostic_data(
        self,
        data: FourDiagnosticData
    ) -> Dict[str, Any]:
        """分析四诊数据，实现四诊合参模型
        
        Args:
            data: 四诊数据对象
            
        Returns:
            Dict[str, Any]: 分析结果，包含证型、健康状况评分和个性化建议
        """
        try:
            # 1. 各诊法单独分析
            # 望诊分析
            look_score = self._analyze_look_diagnosis(data)
            
            # 闻诊分析
            listen_score = self._analyze_listen_diagnosis(data)
            
            # 问诊分析
            ask_score = self._analyze_ask_diagnosis(data)
            
            # 切诊分析
            touch_score = self._analyze_touch_diagnosis(data)
            
            # 2. 综合健康得分计算 - 使用加权平均
            total_score = (
                look_score * self.diagnostic_weights[DiagnosisType.LOOK] +
                listen_score * self.diagnostic_weights[DiagnosisType.LISTEN] +
                ask_score * self.diagnostic_weights[DiagnosisType.ASK] +
                touch_score * self.diagnostic_weights[DiagnosisType.TOUCH]
            )
            
            # 3. 四诊合参证型分析
            tcm_patterns = self._analyze_tcm_patterns(data, {
                "look_score": look_score,
                "listen_score": listen_score,
                "ask_score": ask_score,
                "touch_score": touch_score
            })
            
            # 4. 形成具体的健康指标
            health_indices = self._calculate_health_indices(data, tcm_patterns)
            
            # 5. 生成个性化建议
            recommendations = self._generate_comprehensive_recommendations(
                tcm_patterns, 
                total_score, 
                health_indices
            )
            
            # 6. 返回完整分析结果
            return {
                "total_health_score": float(total_score),
                "diagnostic_scores": {
                    "look": float(look_score),
                    "listen": float(listen_score),
                    "ask": float(ask_score),
                    "touch": float(touch_score)
                },
                "tongue_analysis": self._analyze_tongue_data(data.tongue_data),
                "pulse_analysis": self.analyze_pulse_data(data.pulse_data),
                "tcm_patterns": tcm_patterns,
                "health_indices": health_indices,
                "recommendations": recommendations,
                "timestamp": data.timestamp.isoformat(),
                "patient_id": data.patient_id
            }
        except Exception as e:
            logger.error(f"Error analyzing four diagnostic data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "patient_id": data.patient_id,
                "timestamp": data.timestamp.isoformat() if hasattr(data, "timestamp") else None
            }
            
    def _analyze_tcm_patterns(self, data: FourDiagnosticData, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """四诊合参证型分析
        
        Args:
            data: 四诊数据
            scores: 各诊法得分
            
        Returns:
            List[Dict[str, Any]]: 证型列表，包含证型名称、可能性和证据
        """
        try:
            # 证型特征映射
            pattern_features = {
                "阴虚": {
                    "tongue": [TongueColor.RED, TongueColor.CRIMSON],
                    "pulse": [PulseType.RAPID, PulseType.THREADY],
                    "symptoms": ["口干", "手足心热", "盗汗", "失眠", "五心烦热"],
                    "face": ["潮红", "颧红"],
                    "voice": ["嘶哑"]
                },
                "阳虚": {
                    "tongue": [TongueColor.PALE],
                    "pulse": [PulseType.WEAK, PulseType.SLOW],
                    "symptoms": ["畏寒", "肢冷", "腰膝酸软", "神疲", "小便清长"],
                    "face": ["苍白", "萎黄"],
                    "voice": ["低微"]
                },
                "气虚": {
                    "tongue": [TongueColor.PALE],
                    "pulse": [PulseType.EMPTY, PulseType.WEAK],
                    "symptoms": ["疲乏", "气短", "自汗", "食欲不振", "大便溏"],
                    "face": ["萎黄"],
                    "voice": ["低弱"]
                },
                "血虚": {
                    "tongue": [TongueColor.PALE],
                    "pulse": [PulseType.THREADY, PulseType.WEAK],
                    "symptoms": ["面色苍白", "唇甲淡白", "头晕", "心悸", "失眠"],
                    "face": ["苍白"],
                    "voice": ["低微"]
                },
                "痰湿": {
                    "tongue": [TongueCoating.THICK, TongueCoating.WHITE],
                    "pulse": [PulseType.SLIPPERY, PulseType.SOFT],
                    "symptoms": ["胸闷", "痰多", "恶心", "头重", "乏力"],
                    "face": ["浮肿"],
                    "voice": ["重浊"]
                },
                "湿热": {
                    "tongue": [TongueCoating.YELLOW, TongueColor.RED],
                    "pulse": [PulseType.SLIPPERY, PulseType.RAPID],
                    "symptoms": ["口苦", "小便黄赤", "大便粘滞", "身重", "胸闷脘痞"],
                    "face": ["黄红"],
                    "voice": ["重浊"]
                },
                "血瘀": {
                    "tongue": [TongueColor.PURPLE],
                    "pulse": [PulseType.CHOPPY, PulseType.WIRY],
                    "symptoms": ["刺痛", "肿块", "瘀斑", "经行不畅", "唇暗"],
                    "face": ["暗淡"],
                    "voice": ["低沉"]
                },
                "气滞": {
                    "tongue": [],
                    "pulse": [PulseType.WIRY],
                    "symptoms": ["胸胁胀痛", "情志不畅", "嗳气", "脘腹胀满", "痛势移动"],
                    "face": ["晦暗"],
                    "voice": ["叹息"]
                },
                "肝阳上亢": {
                    "tongue": [TongueColor.RED],
                    "pulse": [PulseType.WIRY, PulseType.RAPID],
                    "symptoms": ["头痛", "眩晕", "面红", "烦躁易怒", "口苦"],
                    "face": ["红赤"],
                    "voice": ["高亢"]
                },
                "脾胃虚弱": {
                    "tongue": [TongueColor.PALE, TongueCoating.THIN],
                    "pulse": [PulseType.WEAK, PulseType.SOFT],
                    "symptoms": ["食欲不振", "腹胀", "大便溏薄", "疲倦", "浮肿"],
                    "face": ["萎黄"],
                    "voice": ["低微"]
                }
            }
            
            # 分析证型
            patterns_scores = {}
            
            # 检查主诉中的症状
            for pattern_name, features in pattern_features.items():
                score = 0.0
                evidence = []
                
                # 检查舌象
                if hasattr(data, "tongue_data") and data.tongue_data:
                    if data.tongue_data.color in features["tongue"]:
                        score += 0.2
                        evidence.append(f"舌色: {data.tongue_data.color.value}")
                    if data.tongue_data.coating in features["tongue"]:
                        score += 0.2
                        evidence.append(f"舌苔: {data.tongue_data.coating.value}")
                
                # 检查脉象
                pulse_match = False
                if hasattr(data, "pulse_data") and data.pulse_data:
                    for pulse_type in features["pulse"]:
                        if (pulse_type == data.pulse_data.left_cun or 
                            pulse_type == data.pulse_data.left_guan or 
                            pulse_type == data.pulse_data.left_chi or
                            pulse_type == data.pulse_data.right_cun or
                            pulse_type == data.pulse_data.right_guan or
                            pulse_type == data.pulse_data.right_chi):
                            score += 0.2
                            evidence.append(f"脉象: {pulse_type.value}")
                            pulse_match = True
                            break
                
                # 检查症状
                symptom_count = 0
                for symptom in features["symptoms"]:
                    if symptom in data.chief_complaint:
                        symptom_count += 1
                        evidence.append(f"症状: {symptom}")
                
                # 根据症状数量计分
                if symptom_count >= 3:
                    score += 0.4
                elif symptom_count > 0:
                    score += 0.2 * (symptom_count / 3)
                
                # 检查面色
                for face_color in features["face"]:
                    if face_color in data.face_color:
                        score += 0.1
                        evidence.append(f"面色: {face_color}")
                        break
                
                # 检查声音
                for voice_type in features["voice"]:
                    if voice_type in data.voice:
                        score += 0.1
                        evidence.append(f"声音: {voice_type}")
                        break
                
                # 只有当有足够证据时才考虑该证型
                if score > 0.3:
                    patterns_scores[pattern_name] = {
                        "score": score,
                        "evidence": evidence
                    }
            
            # 对证型进行排序并返回可能性最大的几个
            sorted_patterns = sorted(
                [{"name": k, "probability": v["score"], "evidence": v["evidence"]} 
                 for k, v in patterns_scores.items()],
                key=lambda x: x["probability"], 
                reverse=True
            )
            
            # 限制返回数量，只返回可能性较大的证型
            return [p for p in sorted_patterns if p["probability"] > 0.3][:3]
            
        except Exception as e:
            logger.error(f"证型分析错误: {e}")
            return []
    
    def _calculate_health_indices(self, data: FourDiagnosticData, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算健康指标
        
        Args:
            data: 四诊数据
            patterns: 证型分析结果
            
        Returns:
            Dict[str, Any]: 健康指标
        """
        try:
            # 基础指标
            indices = {
                "气血指数": 0.7,
                "阴阳平衡": 0.7,
                "脏腑功能": 0.7,
                "精神状态": 0.7,
                "代谢功能": 0.7
            }
            
            # 根据舌诊调整气血指数
            if data.tongue_data:
                if data.tongue_data.color == TongueColor.PALE:
                    indices["气血指数"] -= 0.2  # 淡白舌多为气血不足
                elif data.tongue_data.color == TongueColor.RED:
                    indices["气血指数"] -= 0.1  # 红舌为血热
            
            # 根据脉诊调整阴阳平衡
            if data.pulse_data:
                if data.pulse_data.frequency > 90:
                    indices["阴阳平衡"] -= 0.2  # 脉率快多为阳盛阴虚
                elif data.pulse_data.frequency < 60:
                    indices["阴阳平衡"] -= 0.1  # 脉率慢多为阳虚
            
            # 根据体温调整阴阳平衡
            if data.body_temperature > 37.5:
                indices["阴阳平衡"] -= 0.2  # 发热多为阳盛
            elif data.body_temperature < 36.0:
                indices["阴阳平衡"] -= 0.3  # 低温多为阳虚
            
            # 根据证型调整各项指标
            for pattern in patterns:
                pattern_name = pattern["name"]
                probability = pattern["probability"]
                
                # 根据不同证型调整指标
                if pattern_name == "阴虚":
                    indices["阴阳平衡"] -= 0.1 * probability
                    indices["代谢功能"] -= 0.1 * probability
                elif pattern_name == "阳虚":
                    indices["阴阳平衡"] -= 0.1 * probability
                    indices["代谢功能"] -= 0.2 * probability
                elif pattern_name == "气虚":
                    indices["气血指数"] -= 0.2 * probability
                    indices["脏腑功能"] -= 0.1 * probability
                elif pattern_name == "血虚":
                    indices["气血指数"] -= 0.2 * probability
                elif pattern_name == "痰湿":
                    indices["代谢功能"] -= 0.2 * probability
                    indices["脏腑功能"] -= 0.1 * probability
                elif pattern_name == "湿热":
                    indices["脏腑功能"] -= 0.2 * probability
                    indices["代谢功能"] -= 0.1 * probability
                elif pattern_name == "血瘀":
                    indices["气血指数"] -= 0.2 * probability
                    indices["代谢功能"] -= 0.1 * probability
                elif pattern_name == "气滞":
                    indices["气血指数"] -= 0.1 * probability
                    indices["精神状态"] -= 0.2 * probability
                elif pattern_name == "肝阳上亢":
                    indices["阴阳平衡"] -= 0.2 * probability
                    indices["精神状态"] -= 0.2 * probability
                elif pattern_name == "脾胃虚弱":
                    indices["脏腑功能"] -= 0.3 * probability
                    indices["代谢功能"] -= 0.2 * probability
            
            # 确保所有指标在合理范围内（0.1-1.0）
            for key in indices:
                indices[key] = max(0.1, min(1.0, indices[key]))
            
            # 计算总体健康指数
            indices["总体健康指数"] = sum(indices.values()) / len(indices)
            
            # 添加健康状态描述
            health_status = "亚健康"
            if indices["总体健康指数"] >= 0.8:
                health_status = "健康"
            elif indices["总体健康指数"] <= 0.4:
                health_status = "不健康"
                
            indices["健康状态"] = health_status
            
            return indices
            
        except Exception as e:
            logger.error(f"健康指标计算错误: {e}")
            return {
                "气血指数": 0.5,
                "阴阳平衡": 0.5,
                "脏腑功能": 0.5,
                "精神状态": 0.5,
                "代谢功能": 0.5,
                "总体健康指数": 0.5,
                "健康状态": "未知"
            }
    
    def _generate_comprehensive_recommendations(
        self, 
        patterns: List[Dict[str, Any]], 
        health_score: float,
        health_indices: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成综合建议
        
        Args:
            patterns: 证型分析结果
            health_score: 健康得分
            health_indices: 健康指标
            
        Returns:
            Dict[str, Any]: 建议内容
        """
        try:
            # 基于证型的生活调理建议
            lifestyle_by_pattern = {
                "阴虚": [
                    "避免熬夜和过度劳累",
                    "多食养阴食物如银耳、百合、芝麻",
                    "保持情绪平和，避免过度兴奋",
                    "适当进行太极、瑜伽等柔和运动"
                ],
                "阳虚": [
                    "注意保暖，特别是腰腹部",
                    "饮食宜温热，可多食羊肉、生姜等温阳食物",
                    "适当进行舒缓运动，增强体质",
                    "保持规律作息，早睡早起"
                ],
                "气虚": [
                    "合理安排作息，避免过度劳累",
                    "饮食宜清淡易消化，可多食山药、薏米等健脾益气食物",
                    "适当进行气功、散步等轻度运动",
                    "保持心情舒畅，避免情绪波动过大"
                ],
                "血虚": [
                    "合理膳食，增加富含铁质和蛋白质的食物",
                    "保证充足睡眠，提高睡眠质量",
                    "避免过度劳累和紧张情绪",
                    "可适当食用桂圆、红枣等补血食物"
                ],
                "痰湿": [
                    "饮食宜清淡，少食多餐",
                    "避免过食肥甘厚腻食物",
                    "加强体育锻炼，增加户外活动",
                    "保持情绪舒畅，避免忧思郁结"
                ],
                "湿热": [
                    "饮食宜清淡，避免辛辣刺激性食物",
                    "多饮水，增加新鲜蔬果摄入",
                    "保持环境通风，减少潮湿环境暴露",
                    "适当运动，增强体质"
                ],
                "血瘀": [
                    "注意保暖，避免受寒",
                    "饮食宜温，可适当食用红枣、桃仁等活血食物",
                    "保持规律运动，促进血液循环",
                    "避免久坐久站，经常变换姿势"
                ],
                "气滞": [
                    "保持情绪舒畅，避免郁怒",
                    "适当进行深呼吸和舒展运动",
                    "饮食规律，避免暴饮暴食",
                    "可食用陈皮、香橼等理气食物"
                ],
                "肝阳上亢": [
                    "保持心情舒畅，避免暴怒",
                    "饮食宜清淡，避免辛辣刺激性食物",
                    "保证充足睡眠，早睡早起",
                    "可适当食用菊花、决明子等平肝潜阳食物"
                ],
                "脾胃虚弱": [
                    "饮食规律，少食多餐",
                    "食物宜温热易消化，避免生冷食物",
                    "适当活动，增强体质",
                    "保持心情舒畅，避免过度思虑"
                ]
            }
            
            # 基于健康指数的饮食建议
            diet_recommendations = []
            
            if health_indices["气血指数"] < 0.5:
                diet_recommendations.extend([
                    "增加富含铁质的食物，如菠菜、瘦肉、红枣",
                    "适当食用黑豆、黑米等黑色食物补益肾精",
                    "增加优质蛋白质摄入，如鱼、瘦肉、鸡蛋"
                ])
            
            if health_indices["脏腑功能"] < 0.5:
                diet_recommendations.extend([
                    "增加膳食纤维摄入，如燕麦、紫薯、全谷物",
                    "减少精制糖和油脂摄入",
                    "多食新鲜蔬果，增加维生素和矿物质摄入"
                ])
            
            if health_indices["代谢功能"] < 0.5:
                diet_recommendations.extend([
                    "适当增加温性食物，如生姜、胡椒",
                    "控制总热量摄入，避免过饱",
                    "规律饮食，不要暴饮暴食"
                ])
            
            # 基于健康得分的锻炼建议
            exercise_recommendations = []
            
            if health_score >= 0.7:
                exercise_recommendations.extend([
                    "可进行中等强度有氧运动，如快走、慢跑、游泳",
                    "每周锻炼3-5次，每次30-60分钟",
                    "配合适当的力量训练，增强肌肉力量"
                ])
            elif health_score >= 0.4:
                exercise_recommendations.extend([
                    "选择低强度有氧运动，如散步、太极、瑜伽",
                    "每周锻炼2-3次，每次20-30分钟",
                    "避免剧烈运动，以舒缓运动为主"
                ])
            else:
                exercise_recommendations.extend([
                    "以静养为主，可进行呼吸调息、八段锦等养生功法",
                    "根据自身情况进行短时间的轻度活动",
                    "避免过度劳累，注意劳逸结合"
                ])
            
            # 生成证型特异性建议
            lifestyle_recommendations = []
            if patterns:
                # 获取主要证型
                main_pattern = patterns[0]["name"]
                if main_pattern in lifestyle_by_pattern:
                    lifestyle_recommendations = lifestyle_by_pattern[main_pattern]
                
                # 如果有第二证型，添加其建议
                if len(patterns) > 1:
                    second_pattern = patterns[1]["name"]
                    if second_pattern in lifestyle_by_pattern:
                        # 避免重复建议
                        additional = [rec for rec in lifestyle_by_pattern[second_pattern]
                                     if rec not in lifestyle_recommendations]
                        lifestyle_recommendations.extend(additional[:2])  # 只添加前两条
            
            # 如果没有证型特异性建议，使用默认建议
            if not lifestyle_recommendations:
                lifestyle_recommendations = [
                    "保持规律作息，早睡早起",
                    "合理膳食，均衡营养",
                    "适当运动，增强体质",
                    "保持心情舒畅，避免过度紧张"
                ]
            
            # 返回综合建议
            return {
                "生活方式建议": lifestyle_recommendations,
                "饮食建议": diet_recommendations[:3],  # 限制建议数量
                "运动建议": exercise_recommendations,
                "其他注意事项": [
                    "定期进行健康检查",
                    "保持良好的作息习惯",
                    "适当调整情绪，保持心态平和"
                ]
            }
            
        except Exception as e:
            logger.error(f"建议生成错误: {e}")
            return {
                "生活方式建议": ["保持规律作息，早睡早起"],
                "饮食建议": ["合理膳食，均衡营养"],
                "运动建议": ["适当运动，增强体质"],
                "其他注意事项": ["定期进行健康检查"]
            }

    def _analyze_look_diagnosis(self, data: FourDiagnosticData) -> float:
        """分析望诊数据"""
        try:
            # 舌诊评分 - 基于舌诊分析结果
            tongue_data = self._analyze_tongue_data(data.tongue_data)
            # 计算舌诊得分，基于舌质和舌苔状态
            tongue_score = 0.7  # 默认基础分
            
            # 根据舌色调整分数
            if data.tongue_data.color in [TongueColor.LIGHT_RED]:
                tongue_score = 0.9  # 淡红舌为正常
            elif data.tongue_data.color in [TongueColor.PALE]:
                tongue_score = 0.5  # 淡白舌多为气血虚
            elif data.tongue_data.color in [TongueColor.RED, TongueColor.CRIMSON]:
                tongue_score = 0.4  # 红舌、绛舌多为热证
            elif data.tongue_data.color in [TongueColor.PURPLE, TongueColor.BLUE]:
                tongue_score = 0.3  # 紫舌、青舌多为瘀血或寒证
                
            # 根据舌苔调整分数
            if data.tongue_data.coating in [TongueCoating.THIN, TongueCoating.WHITE]:
                tongue_score = tongue_score * 0.9  # 薄白苔接近正常
            elif data.tongue_data.coating in [TongueCoating.YELLOW]:
                tongue_score = tongue_score * 0.7  # 黄苔多为热证
            elif data.tongue_data.coating in [TongueCoating.GREY, TongueCoating.BLACK]:
                tongue_score = tongue_score * 0.5  # 灰苔、黑苔多为重症
                
            # 根据特殊症状进一步调整
            if data.tongue_data.cracks:
                tongue_score = tongue_score * 0.8  # 裂纹多为阴虚
            if data.tongue_data.spots:
                tongue_score = tongue_score * 0.7  # 斑点多为热毒
            
            # 面色评分
            face_color_scores = {
                "红": 0.5,      # 面红多为热证
                "白": 0.4,      # 面白多为气血虚
                "黄": 0.6,      # 面黄多为脾虚
                "青": 0.3,      # 面青多为肝病或痛证
                "黑": 0.2,      # 面黑多为肾虚或水气凌心
                "淡红": 0.9,    # 淡红润泽为正常
                "暗红": 0.4,    # 暗红多为血瘀
                "苍白": 0.3,    # 苍白多为血虚
                "萎黄": 0.4,    # 萎黄多为脾胃虚弱
                "黧黑": 0.3     # 黧黑多为肾虚
            }
            face_score = face_color_scores.get(data.face_color, 0.5)
            
            # 形体评分
            body_shape_scores = {
                "健壮": 0.9,    # 体格健壮
                "消瘦": 0.5,    # 消瘦多为气血亏虚
                "肥胖": 0.6,    # 肥胖多为痰湿
                "浮肿": 0.3,    # 浮肿多为水湿内停
                "干瘦": 0.4,    # 干瘦多为阴虚
                "虚胖": 0.5,    # 虚胖多为脾虚
                "匀称": 1.0,    # 身材匀称
                "畸形": 0.2     # 畸形多为先天不足
            }
            shape_score = body_shape_scores.get(data.body_shape, 0.5)
            
            # 动态评分 - 根据动作、姿态等
            movement_scores = {
                "灵活": 0.9,     # 动作灵活协调
                "迟缓": 0.5,     # 动作迟缓多为气血不足
                "震颤": 0.3,     # 震颤多为肝风内动
                "痉挛": 0.2,     # 痉挛多为热极生风
                "瘫痪": 0.1,     # 瘫痪多为气血瘀阻
                "倦怠": 0.6,     # 倦怠多为气虚
                "躁动": 0.4,     # 躁动多为热证
                "正常": 1.0,     # 正常活动
                "失调": 0.3      # 失调多为脏腑功能紊乱
            }
            movement_score = movement_scores.get(data.movement, 0.5)
            
            # 综合评分 - 加权平均
            look_score = (tongue_score * 0.4 + face_score * 0.3 + 
                         shape_score * 0.2 + movement_score * 0.1)
            
            return look_score
            
        except Exception as e:
            logger.error(f"Error analyzing look diagnosis: {e}")
            return 0.5  # 返回中性分数
            
    def _analyze_listen_diagnosis(self, data: FourDiagnosticData) -> float:
        """分析闻诊数据"""
        try:
            # 声音评分
            voice_scores = {
                "洪亮": 0.9,     # 声音洪亮有力为正常
                "低微": 0.5,     # 声音低微多为气虚
                "嘶哑": 0.4,     # 嘶哑多为肺热或阴虚
                "哭泣": 0.3,     # 哭泣声多为痛证或情志异常
                "急促": 0.4,     # 声急促多为热证
                "缓慢": 0.5,     # 声缓慢多为寒证
                "断续": 0.3,     # 断续声多为气短
                "粗粝": 0.4,     # 粗粝声多为肺络不利
                "细弱": 0.5,     # 细弱声多为气血不足
                "重浊": 0.4,     # 重浊声多为痰湿内盛
                "虚怯": 0.5,     # 虚怯声多为正气不足
                "正常": 0.9      # 正常声音
            }
            voice_score = voice_scores.get(data.voice, 0.5)
            
            # 呼吸评分
            breath_scores = {
                "平稳": 0.9,     # 呼吸平稳均匀为正常
                "喘促": 0.3,     # 喘促多为肺气上逆
                "气短": 0.4,     # 气短多为肺气虚弱
                "粗大": 0.4,     # 粗大呼吸多为热证
                "微弱": 0.5,     # 微弱呼吸多为元气虚弱
                "哮鸣": 0.3,     # 哮鸣多为痰阻气道
                "鼾声": 0.5,     # 鼾声多为痰湿内盛
                "细长": 0.6,     # 细长呼吸多为气阴两虚
                "不规则": 0.3,   # 不规则呼吸多为气机紊乱
                "深长": 0.7,     # 深长呼吸多为肺功能良好
                "正常": 0.9      # 正常呼吸
            }
            breath_score = breath_scores.get(data.breath, 0.5)
            
            # 气味评分
            odor_scores = {
                "无异味": 1.0,   # 无明显异味为正常
                "腥臭": 0.3,     # 腥臭多为热毒
                "酸臭": 0.4,     # 酸臭多为胃热或肝郁
                "腐臭": 0.2,     # 腐臭多为热毒壅盛
                "尿臊": 0.3,     # 尿臊多为肾虚
                "鱼腥": 0.4,     # 鱼腥多为湿热
                "甜腻": 0.5,     # 甜腻多为脾胃湿热
                "霉臭": 0.3,     # 霉臭多为痰湿
                "粪臭": 0.2,     # 粪臭多为肠腑热结
                "正常": 0.9      # 正常气味
            }
            odor_score = odor_scores.get(data.odor, 0.5)
            
            # 综合评分 - 加权平均
            listen_score = (voice_score * 0.4 + breath_score * 0.4 + odor_score * 0.2)
            
            return listen_score
            
        except Exception as e:
            logger.error(f"Error analyzing listen diagnosis: {e}")
            return 0.5  # 返回中性分数
            
    def _analyze_ask_diagnosis(self, data: FourDiagnosticData) -> float:
        """分析问诊数据"""
        try:
            # 初始化关键词权重表
            symptom_weights = {
                # 头部症状
                "头痛": {"weight": -0.1, "patterns": ["风热", "肝阳上亢", "痰浊", "气虚"]},
                "头晕": {"weight": -0.1, "patterns": ["肝阳上亢", "气血虚", "痰湿"]},
                "失眠": {"weight": -0.1, "patterns": ["心神不宁", "阴虚火旺", "胃不和"]},
                
                # 胸腹症状
                "胸闷": {"weight": -0.1, "patterns": ["气滞", "痰阻", "心气虚"]},
                "胸痛": {"weight": -0.2, "patterns": ["气滞血瘀", "寒凝", "热毒"]},
                "腹痛": {"weight": -0.2, "patterns": ["寒凝", "湿阻", "食滞", "气滞血瘀"]},
                "腹胀": {"weight": -0.1, "patterns": ["脾虚", "气滞", "湿阻"]},
                
                # 消化症状
                "恶心": {"weight": -0.1, "patterns": ["胃气上逆", "肝胃不和"]},
                "呕吐": {"weight": -0.2, "patterns": ["胃热", "食滞", "痰饮"]},
                "便秘": {"weight": -0.1, "patterns": ["肠燥", "气虚", "气滞"]},
                "腹泻": {"weight": -0.2, "patterns": ["脾虚", "湿热", "寒湿"]},
                
                # 全身症状
                "发热": {"weight": -0.2, "patterns": ["外感风热", "阴虚内热"]},
                "畏寒": {"weight": -0.1, "patterns": ["阳虚", "外感风寒"]},
                "乏力": {"weight": -0.1, "patterns": ["气虚", "脾虚"]},
                "盗汗": {"weight": -0.1, "patterns": ["阴虚"]},
                "浮肿": {"weight": -0.2, "patterns": ["脾虚", "肾虚"]},
                
                # 情志症状
                "烦躁": {"weight": -0.1, "patterns": ["肝郁化火", "心火亢盛"]},
                "抑郁": {"weight": -0.1, "patterns": ["肝气郁结", "心脾两虚"]},
                "易怒": {"weight": -0.1, "patterns": ["肝火上炎", "肝胆湿热"]},
                "易惊": {"weight": -0.1, "patterns": ["心虚胆怯"]},
                
                # 正面关键词
                "精神好": {"weight": 0.2, "patterns": ["正气充足"]},
                "食欲佳": {"weight": 0.1, "patterns": ["脾胃功能良好"]},
                "睡眠好": {"weight": 0.1, "patterns": ["心神安宁"]},
                "大便调": {"weight": 0.1, "patterns": ["肠道通畅"]},
                "小便调": {"weight": 0.1, "patterns": ["膀胱气化正常"]}
            }
            
            # 主诉分析
            chief_complaint_score = 0.7  # 默认基础分
            found_symptoms = []
            
            # 查找主诉中的症状关键词
            for symptom, info in symptom_weights.items():
                if symptom in data.chief_complaint:
                    chief_complaint_score += info["weight"]
                    found_symptoms.extend(info["patterns"])
            
            # 确保分数在合理范围内
            chief_complaint_score = max(0.1, min(1.0, chief_complaint_score))
            
            # 病史分析
            # 定义病史类别权重
            history_category_weights = {
                "过敏史": 0.1,
                "手术史": 0.1,
                "家族史": 0.05,
                "既往病史": 0.2,
                "用药史": 0.15,
                "现病史": 0.4
            }
            
            # 定义病史严重程度评分
            history_severity = {
                "轻": 0.8,
                "中": 0.6,
                "重": 0.4,
                "极重": 0.2
            }
            
            history_score = 0.0
            history_count = 0
            
            # 分析各项病史
            for category, content in data.history.items():
                if not content:  # 跳过空内容
                    continue
                    
                # 获取类别权重
                category_weight = history_category_weights.get(category, 0.1)
                
                # 默认为中度严重性
                severity = "中"
                for sev, _ in history_severity.items():
                    if sev in content:
                        severity = sev
                        break
                        
                # 计算该类别得分
                category_score = history_severity.get(severity, 0.6)
                
                # 添加到总分
                history_score += category_score * category_weight
                history_count += 1
                
            # 如果没有病史记录，给予满分
            if history_count == 0:
                history_score = 1.0
            else:
                # 归一化病史得分
                history_score = history_score / sum(weight for weight in history_category_weights.values() 
                                                if any(cat in key for cat in history_category_weights.keys() 
                                                      for key in data.history.keys()))
            
            # 综合评分 - 加权平均
            ask_score = chief_complaint_score * 0.6 + history_score * 0.4
            
            # 记录发现的证型
            if found_symptoms:
                logger.info(f"问诊发现的可能证型: {set(found_symptoms)}")
            
            return ask_score
            
        except Exception as e:
            logger.error(f"Error analyzing ask diagnosis: {e}")
            return 0.5  # 返回中性分数
            
    def _analyze_touch_diagnosis(self, data: FourDiagnosticData) -> float:
        """分析切诊数据"""
        try:
            # 脉诊分析
            pulse_analysis = self.analyze_pulse_data(data.pulse_data)
            # 从脉象分析结果中提取overall_score作为脉诊评分
            pulse_score = pulse_analysis.get("overall_score", 0.5)
            
            # 温度评分
            temp_score = self._analyze_temperature(data.body_temperature)
            
            # 皮肤评分
            skin_texture_scores = {
                "润滑": 0.9,     # 皮肤润滑为正常
                "粗糙": 0.5,     # 皮肤粗糙多为血虚或风燥
                "干燥": 0.4,     # 皮肤干燥多为阴虚或血虚
                "湿润": 0.7,     # 皮肤湿润多为湿热体质
                "紧绷": 0.6,     # 皮肤紧绷多为水湿
                "松弛": 0.5,     # 皮肤松弛多为气虚
                "滑腻": 0.6,     # 皮肤滑腻多为痰湿
                "粘腻": 0.4,     # 皮肤粘腻多为湿热
                "厚重": 0.5,     # 皮肤厚重多为痰湿
                "薄弱": 0.4,     # 皮肤薄弱多为气血两虚
                "正常": 0.9      # 正常皮肤
            }
            skin_score = skin_texture_scores.get(data.skin_texture, 0.5)
            
            # 综合评分 - 加权平均
            touch_score = (pulse_score * 0.6 + temp_score * 0.2 + skin_score * 0.2)
            
            return touch_score
            
        except Exception as e:
            logger.error(f"Error analyzing touch diagnosis: {e}")
            return 0.5  # 返回中性分数
            
    def _analyze_temperature(self, temperature: float) -> float:
        """分析体温"""
        try:
            # 正常体温范围：36.3-37.2℃
            if 36.3 <= temperature <= 37.2:
                return 1.0
            elif temperature < 36.3:
                # 低于正常体温
                if temperature < 35.5:
                    return 0.3  # 显著低温，多为阳虚严重
                else:
                    return 0.6  # 轻度低温，多为阳气不足
            else:
                # 高于正常体温
                if temperature >= 39.0:
                    return 0.1  # 高热，多为热毒炽盛
                elif temperature >= 38.0:
                    return 0.3  # 中度发热，多为热邪较重
                else:
                    return 0.6  # 微热，多为轻度热邪
                    
        except Exception as e:
            logger.error(f"Error analyzing temperature: {e}")
            return 0.5  # 返回中性分数
            
    def _generate_recommendations(self, total_score: float) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if total_score < 0.3:
            recommendations.extend([
                "建议及时就医",
                "注意休息，避免劳累",
                "清淡饮食，忌食辛辣刺激"
            ])
        elif total_score < 0.6:
            recommendations.extend([
                "适当调整作息时间",
                "注意饮食均衡",
                "保持适度运动"
            ])
        else:
            recommendations.extend([
                "继续保持良好的生活习惯",
                "定期进行健康检查",
                "适量运动，保持愉悦心情"
            ])
            
        return recommendations 