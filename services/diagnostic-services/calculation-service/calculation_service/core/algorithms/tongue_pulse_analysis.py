"""
舌脉象计算模型
实现中医舌诊和脉诊的数字化分析算法
"""

import cv2
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TongueColor(Enum):
    """舌色分类"""
    PALE = "淡白"
    LIGHT_RED = "淡红"
    RED = "红"
    CRIMSON = "绛"
    PURPLE = "紫"
    BLUE_PURPLE = "青紫"

class TongueCoating(Enum):
    """舌苔分类"""
    THIN_WHITE = "薄白"
    THICK_WHITE = "厚白"
    THIN_YELLOW = "薄黄"
    THICK_YELLOW = "厚黄"
    GREASY = "腻苔"
    DRY = "燥苔"
    PEELED = "剥苔"
    MIRROR = "镜面舌"

class PulseType(Enum):
    """脉象分类"""
    FLOATING = "浮脉"
    DEEP = "沉脉"
    SLOW = "迟脉"
    RAPID = "数脉"
    WEAK = "弱脉"
    STRONG = "强脉"
    SLIPPERY = "滑脉"
    ROUGH = "涩脉"
    WIRY = "弦脉"
    TIGHT = "紧脉"

@dataclass
class TongueAnalysisResult:
    """舌诊分析结果"""
    color: TongueColor
    coating: TongueCoating
    texture: str
    moisture: float
    thickness: float
    color_confidence: float
    coating_confidence: float
    abnormal_areas: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class PulseAnalysisResult:
    """脉诊分析结果"""
    pulse_type: PulseType
    rate: float  # 脉率（次/分钟）
    rhythm: str  # 节律
    strength: float  # 脉力
    depth: float  # 脉位
    width: float  # 脉宽
    confidence: float
    waveform_features: Dict[str, float]
    timestamp: datetime

class TongueImageAnalyzer:
    """舌象图像分析器"""
    
    def __init__(self):
        self.color_ranges = self._init_color_ranges()
        self.feature_extractors = self._init_feature_extractors()
    
    def _init_color_ranges(self) -> Dict[TongueColor, Dict[str, Tuple]]:
        """初始化舌色HSV范围"""
        return {
            TongueColor.PALE: {
                'hsv_lower': (0, 0, 200),
                'hsv_upper': (180, 30, 255)
            },
            TongueColor.LIGHT_RED: {
                'hsv_lower': (0, 30, 150),
                'hsv_upper': (10, 100, 220)
            },
            TongueColor.RED: {
                'hsv_lower': (0, 100, 100),
                'hsv_upper': (10, 255, 200)
            },
            TongueColor.CRIMSON: {
                'hsv_lower': (0, 150, 80),
                'hsv_upper': (8, 255, 180)
            },
            TongueColor.PURPLE: {
                'hsv_lower': (120, 50, 50),
                'hsv_upper': (160, 255, 200)
            },
            TongueColor.BLUE_PURPLE: {
                'hsv_lower': (100, 100, 50),
                'hsv_upper': (130, 255, 150)
            }
        }
    
    def _init_feature_extractors(self) -> Dict[str, Any]:
        """初始化特征提取器"""
        return {
            'texture_analyzer': cv2.createLBPHFaceRecognizer(),
            'edge_detector': cv2.Canny,
            'contour_finder': cv2.findContours
        }
    
    def analyze_tongue_image(self, image: np.ndarray) -> TongueAnalysisResult:
        """分析舌象图像"""
        try:
            # 预处理图像
            processed_image = self._preprocess_image(image)
            
            # 舌体分割
            tongue_mask = self._segment_tongue(processed_image)
            
            # 颜色分析
            color, color_confidence = self._analyze_color(processed_image, tongue_mask)
            
            # 舌苔分析
            coating, coating_confidence = self._analyze_coating(processed_image, tongue_mask)
            
            # 纹理分析
            texture = self._analyze_texture(processed_image, tongue_mask)
            
            # 湿润度分析
            moisture = self._analyze_moisture(processed_image, tongue_mask)
            
            # 厚度分析
            thickness = self._analyze_thickness(processed_image, tongue_mask)
            
            # 异常区域检测
            abnormal_areas = self._detect_abnormal_areas(processed_image, tongue_mask)
            
            return TongueAnalysisResult(
                color=color,
                coating=coating,
                texture=texture,
                moisture=moisture,
                thickness=thickness,
                color_confidence=color_confidence,
                coating_confidence=coating_confidence,
                abnormal_areas=abnormal_areas,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"舌象分析失败: {e}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """图像预处理"""
        # 高斯滤波去噪
        denoised = cv2.GaussianBlur(image, (5, 5), 0)
        
        # 直方图均衡化
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        lab[:, :, 0] = cv2.equalizeHist(lab[:, :, 0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def _segment_tongue(self, image: np.ndarray) -> np.ndarray:
        """舌体分割"""
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 基于颜色的初步分割
        lower_bound = np.array([0, 20, 50])
        upper_bound = np.array([20, 255, 255])
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # 形态学操作
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # 找到最大连通区域
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros_like(mask)
            cv2.fillPoly(mask, [largest_contour], 255)
        
        return mask
    
    def _analyze_color(self, image: np.ndarray, mask: np.ndarray) -> Tuple[TongueColor, float]:
        """分析舌色"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        masked_hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        
        best_match = TongueColor.LIGHT_RED
        best_confidence = 0.0
        
        for color, ranges in self.color_ranges.items():
            color_mask = cv2.inRange(masked_hsv, ranges['hsv_lower'], ranges['hsv_upper'])
            match_ratio = np.sum(color_mask > 0) / np.sum(mask > 0)
            
            if match_ratio > best_confidence:
                best_confidence = match_ratio
                best_match = color
        
        return best_match, best_confidence
    
    def _analyze_coating(self, image: np.ndarray, mask: np.ndarray) -> Tuple[TongueCoating, float]:
        """分析舌苔"""
        # 转换到LAB色彩空间进行苔质分析
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        masked_lab = cv2.bitwise_and(lab, lab, mask=mask)
        
        # 计算亮度和色度特征
        l_channel = masked_lab[:, :, 0][mask > 0]
        a_channel = masked_lab[:, :, 1][mask > 0]
        b_channel = masked_lab[:, :, 2][mask > 0]
        
        avg_lightness = np.mean(l_channel)
        avg_a = np.mean(a_channel)
        avg_b = np.mean(b_channel)
        
        # 基于特征值判断苔质
        if avg_lightness > 180:
            if avg_b < 130:
                coating = TongueCoating.THIN_WHITE
            else:
                coating = TongueCoating.THICK_WHITE
        elif avg_b > 140:
            if avg_lightness > 150:
                coating = TongueCoating.THIN_YELLOW
            else:
                coating = TongueCoating.THICK_YELLOW
        else:
            coating = TongueCoating.GREASY
        
        # 计算置信度
        confidence = min(1.0, abs(avg_lightness - 128) / 128)
        
        return coating, confidence
    
    def _analyze_texture(self, image: np.ndarray, mask: np.ndarray) -> str:
        """分析舌质纹理"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # 计算LBP特征
        lbp = self._calculate_lbp(masked_gray)
        
        # 计算纹理特征
        contrast = np.std(masked_gray[mask > 0])
        
        if contrast < 20:
            return "光滑"
        elif contrast < 40:
            return "正常"
        else:
            return "粗糙"
    
    def _calculate_lbp(self, image: np.ndarray) -> np.ndarray:
        """计算局部二值模式"""
        rows, cols = image.shape
        lbp = np.zeros_like(image)
        
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                center = image[i, j]
                code = 0
                code |= (image[i-1, j-1] >= center) << 7
                code |= (image[i-1, j] >= center) << 6
                code |= (image[i-1, j+1] >= center) << 5
                code |= (image[i, j+1] >= center) << 4
                code |= (image[i+1, j+1] >= center) << 3
                code |= (image[i+1, j] >= center) << 2
                code |= (image[i+1, j-1] >= center) << 1
                code |= (image[i, j-1] >= center) << 0
                lbp[i, j] = code
        
        return lbp
    
    def _analyze_moisture(self, image: np.ndarray, mask: np.ndarray) -> float:
        """分析湿润度"""
        # 基于图像的反射特性分析湿润度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # 计算高光区域比例
        highlight_threshold = np.percentile(masked_gray[mask > 0], 90)
        highlight_mask = masked_gray > highlight_threshold
        highlight_ratio = np.sum(highlight_mask) / np.sum(mask > 0)
        
        # 湿润度评分 (0-1)
        moisture_score = min(1.0, highlight_ratio * 2)
        
        return moisture_score
    
    def _analyze_thickness(self, image: np.ndarray, mask: np.ndarray) -> float:
        """分析舌体厚度"""
        # 基于边缘检测和轮廓分析估算厚度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.5
        
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 计算轮廓的凸包
        hull = cv2.convexHull(largest_contour)
        hull_area = cv2.contourArea(hull)
        contour_area = cv2.contourArea(largest_contour)
        
        # 厚度指标 (凸度)
        thickness_ratio = contour_area / hull_area if hull_area > 0 else 0.5
        
        return thickness_ratio
    
    def _detect_abnormal_areas(self, image: np.ndarray, mask: np.ndarray) -> List[Dict[str, Any]]:
        """检测异常区域"""
        abnormal_areas = []
        
        # 颜色异常检测
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 检测瘀点（深色斑点）
        dark_spots = self._detect_dark_spots(hsv, mask)
        abnormal_areas.extend(dark_spots)
        
        # 检测裂纹
        cracks = self._detect_cracks(image, mask)
        abnormal_areas.extend(cracks)
        
        return abnormal_areas
    
    def _detect_dark_spots(self, hsv_image: np.ndarray, mask: np.ndarray) -> List[Dict[str, Any]]:
        """检测瘀点"""
        # 检测深色区域
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 80])
        dark_mask = cv2.inRange(hsv_image, lower_dark, upper_dark)
        dark_mask = cv2.bitwise_and(dark_mask, mask)
        
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        spots = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 10 < area < 500:  # 过滤噪声和过大区域
                x, y, w, h = cv2.boundingRect(contour)
                spots.append({
                    'type': '瘀点',
                    'location': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                    'area': float(area),
                    'severity': 'mild' if area < 100 else 'moderate'
                })
        
        return spots
    
    def _detect_cracks(self, image: np.ndarray, mask: np.ndarray) -> List[Dict[str, Any]]:
        """检测裂纹"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用形态学操作检测线状结构
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
        tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
        
        # 阈值化
        _, crack_mask = cv2.threshold(tophat, 10, 255, cv2.THRESH_BINARY)
        crack_mask = cv2.bitwise_and(crack_mask, mask)
        
        contours, _ = cv2.findContours(crack_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cracks = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 20:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = max(w, h) / min(w, h)
                if aspect_ratio > 3:  # 长条形状
                    cracks.append({
                        'type': '裂纹',
                        'location': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                        'length': float(max(w, h)),
                        'severity': 'mild' if max(w, h) < 50 else 'moderate'
                    })
        
        return cracks

class PulseWaveformAnalyzer:
    """脉象波形分析器"""
    
    def __init__(self, sampling_rate: int = 1000):
        self.sampling_rate = sampling_rate
        self.feature_extractors = self._init_feature_extractors()
    
    def _init_feature_extractors(self) -> Dict[str, Any]:
        """初始化特征提取器"""
        return {
            'peak_detector': self._detect_peaks,
            'frequency_analyzer': self._analyze_frequency,
            'morphology_analyzer': self._analyze_morphology
        }
    
    def analyze_pulse_waveform(self, waveform: np.ndarray, duration: float) -> PulseAnalysisResult:
        """分析脉象波形"""
        try:
            # 预处理波形
            processed_waveform = self._preprocess_waveform(waveform)
            
            # 检测脉搏峰值
            peaks = self._detect_peaks(processed_waveform)
            
            # 计算脉率
            pulse_rate = self._calculate_pulse_rate(peaks, duration)
            
            # 分析节律
            rhythm = self._analyze_rhythm(peaks)
            
            # 分析脉力
            strength = self._analyze_strength(processed_waveform, peaks)
            
            # 分析脉位
            depth = self._analyze_depth(processed_waveform)
            
            # 分析脉宽
            width = self._analyze_width(processed_waveform, peaks)
            
            # 提取波形特征
            waveform_features = self._extract_waveform_features(processed_waveform, peaks)
            
            # 分类脉象类型
            pulse_type, confidence = self._classify_pulse_type(waveform_features)
            
            return PulseAnalysisResult(
                pulse_type=pulse_type,
                rate=pulse_rate,
                rhythm=rhythm,
                strength=strength,
                depth=depth,
                width=width,
                confidence=confidence,
                waveform_features=waveform_features,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"脉象分析失败: {e}")
            raise
    
    def _preprocess_waveform(self, waveform: np.ndarray) -> np.ndarray:
        """波形预处理"""
        # 去除基线漂移
        from scipy import signal
        
        # 高通滤波去除基线漂移
        b, a = signal.butter(4, 0.5 / (self.sampling_rate / 2), 'high')
        filtered = signal.filtfilt(b, a, waveform)
        
        # 低通滤波去除高频噪声
        b, a = signal.butter(4, 20 / (self.sampling_rate / 2), 'low')
        filtered = signal.filtfilt(b, a, filtered)
        
        # 归一化
        filtered = (filtered - np.min(filtered)) / (np.max(filtered) - np.min(filtered))
        
        return filtered
    
    def _detect_peaks(self, waveform: np.ndarray) -> np.ndarray:
        """检测脉搏峰值"""
        from scipy.signal import find_peaks
        
        # 设置峰值检测参数
        height = np.mean(waveform) + 0.3 * np.std(waveform)
        distance = int(0.4 * self.sampling_rate)  # 最小间隔400ms
        
        peaks, _ = find_peaks(waveform, height=height, distance=distance)
        
        return peaks
    
    def _calculate_pulse_rate(self, peaks: np.ndarray, duration: float) -> float:
        """计算脉率"""
        if len(peaks) < 2:
            return 0.0
        
        # 计算平均心跳间隔
        intervals = np.diff(peaks) / self.sampling_rate
        avg_interval = np.mean(intervals)
        
        # 转换为每分钟次数
        pulse_rate = 60.0 / avg_interval if avg_interval > 0 else 0.0
        
        return pulse_rate
    
    def _analyze_rhythm(self, peaks: np.ndarray) -> str:
        """分析节律"""
        if len(peaks) < 3:
            return "无法判断"
        
        # 计算心跳间隔变异性
        intervals = np.diff(peaks) / self.sampling_rate
        cv = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0
        
        if cv < 0.05:
            return "规整"
        elif cv < 0.15:
            return "基本规整"
        else:
            return "不规整"
    
    def _analyze_strength(self, waveform: np.ndarray, peaks: np.ndarray) -> float:
        """分析脉力"""
        if len(peaks) == 0:
            return 0.0
        
        # 计算峰值幅度的平均值
        peak_amplitudes = waveform[peaks]
        avg_amplitude = np.mean(peak_amplitudes)
        
        # 归一化到0-1范围
        strength = min(1.0, avg_amplitude)
        
        return strength
    
    def _analyze_depth(self, waveform: np.ndarray) -> float:
        """分析脉位（深浅）"""
        # 基于波形的基线水平分析脉位
        baseline = np.percentile(waveform, 10)
        peak_level = np.percentile(waveform, 90)
        
        # 深度指标
        depth = (baseline + peak_level) / 2
        
        return depth
    
    def _analyze_width(self, waveform: np.ndarray, peaks: np.ndarray) -> float:
        """分析脉宽"""
        if len(peaks) == 0:
            return 0.0
        
        widths = []
        for peak in peaks:
            # 找到峰值一半高度的宽度
            half_height = waveform[peak] / 2
            
            # 向左搜索
            left = peak
            while left > 0 and waveform[left] > half_height:
                left -= 1
            
            # 向右搜索
            right = peak
            while right < len(waveform) - 1 and waveform[right] > half_height:
                right += 1
            
            width = (right - left) / self.sampling_rate
            widths.append(width)
        
        return np.mean(widths) if widths else 0.0
    
    def _extract_waveform_features(self, waveform: np.ndarray, peaks: np.ndarray) -> Dict[str, float]:
        """提取波形特征"""
        features = {}
        
        if len(peaks) > 0:
            # 峰值特征
            peak_amplitudes = waveform[peaks]
            features['peak_amplitude_mean'] = float(np.mean(peak_amplitudes))
            features['peak_amplitude_std'] = float(np.std(peak_amplitudes))
            
            # 间隔特征
            if len(peaks) > 1:
                intervals = np.diff(peaks) / self.sampling_rate
                features['interval_mean'] = float(np.mean(intervals))
                features['interval_std'] = float(np.std(intervals))
                features['interval_cv'] = float(np.std(intervals) / np.mean(intervals))
            
            # 波形形态特征
            features['skewness'] = float(self._calculate_skewness(waveform))
            features['kurtosis'] = float(self._calculate_kurtosis(waveform))
            
            # 频域特征
            freq_features = self._analyze_frequency(waveform)
            features.update(freq_features)
        
        return features
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """计算偏度"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """计算峰度"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def _analyze_frequency(self, waveform: np.ndarray) -> Dict[str, float]:
        """频域分析"""
        from scipy.fft import fft, fftfreq
        
        # 计算FFT
        fft_values = fft(waveform)
        frequencies = fftfreq(len(waveform), 1/self.sampling_rate)
        
        # 计算功率谱密度
        psd = np.abs(fft_values) ** 2
        
        # 提取频域特征
        features = {}
        
        # 主频率
        dominant_freq_idx = np.argmax(psd[:len(psd)//2])
        features['dominant_frequency'] = float(frequencies[dominant_freq_idx])
        
        # 频谱重心
        positive_freqs = frequencies[:len(frequencies)//2]
        positive_psd = psd[:len(psd)//2]
        features['spectral_centroid'] = float(np.sum(positive_freqs * positive_psd) / np.sum(positive_psd))
        
        # 频谱带宽
        centroid = features['spectral_centroid']
        features['spectral_bandwidth'] = float(np.sqrt(np.sum(((positive_freqs - centroid) ** 2) * positive_psd) / np.sum(positive_psd)))
        
        return features
    
    def _classify_pulse_type(self, features: Dict[str, float]) -> Tuple[PulseType, float]:
        """分类脉象类型"""
        # 基于特征的简单分类规则
        pulse_rate = 60.0 / features.get('interval_mean', 1.0) if features.get('interval_mean', 0) > 0 else 60.0
        amplitude = features.get('peak_amplitude_mean', 0.5)
        variability = features.get('interval_cv', 0.1)
        
        confidence = 0.8  # 默认置信度
        
        # 脉率分类
        if pulse_rate < 60:
            pulse_type = PulseType.SLOW
        elif pulse_rate > 100:
            pulse_type = PulseType.RAPID
        # 脉力分类
        elif amplitude < 0.3:
            pulse_type = PulseType.WEAK
        elif amplitude > 0.7:
            pulse_type = PulseType.STRONG
        # 节律分类
        elif variability > 0.15:
            pulse_type = PulseType.ROUGH
        elif variability < 0.05:
            pulse_type = PulseType.SLIPPERY
        else:
            pulse_type = PulseType.FLOATING  # 默认
            confidence = 0.5
        
        return pulse_type, confidence

class TonguePulseCalculationEngine:
    """舌脉象计算引擎"""
    
    def __init__(self):
        self.tongue_analyzer = TongueImageAnalyzer()
        self.pulse_analyzer = PulseWaveformAnalyzer()
        self.syndrome_classifier = self._init_syndrome_classifier()
    
    def _init_syndrome_classifier(self) -> Dict[str, Any]:
        """初始化证候分类器"""
        return {
            'rules': self._load_syndrome_rules(),
            'weights': self._load_feature_weights()
        }
    
    def _load_syndrome_rules(self) -> Dict[str, Dict[str, Any]]:
        """加载证候分类规则"""
        return {
            '气虚证': {
                'tongue_color': [TongueColor.PALE],
                'tongue_coating': [TongueCoating.THIN_WHITE],
                'pulse_type': [PulseType.WEAK, PulseType.DEEP],
                'pulse_rate_range': (50, 80),
                'confidence_threshold': 0.7
            },
            '血瘀证': {
                'tongue_color': [TongueColor.PURPLE, TongueColor.BLUE_PURPLE],
                'tongue_coating': [TongueCoating.THIN_WHITE, TongueCoating.THIN_YELLOW],
                'pulse_type': [PulseType.ROUGH, PulseType.WIRY],
                'pulse_rate_range': (60, 100),
                'confidence_threshold': 0.8
            },
            '湿热证': {
                'tongue_color': [TongueColor.RED],
                'tongue_coating': [TongueCoating.THICK_YELLOW, TongueCoating.GREASY],
                'pulse_type': [PulseType.SLIPPERY, PulseType.RAPID],
                'pulse_rate_range': (80, 120),
                'confidence_threshold': 0.75
            },
            '阴虚证': {
                'tongue_color': [TongueColor.RED, TongueColor.CRIMSON],
                'tongue_coating': [TongueCoating.PEELED, TongueCoating.MIRROR],
                'pulse_type': [PulseType.RAPID, PulseType.WEAK],
                'pulse_rate_range': (80, 110),
                'confidence_threshold': 0.8
            }
        }
    
    def _load_feature_weights(self) -> Dict[str, float]:
        """加载特征权重"""
        return {
            'tongue_color': 0.3,
            'tongue_coating': 0.25,
            'pulse_type': 0.3,
            'pulse_rate': 0.15
        }
    
    def comprehensive_analysis(self, 
                             tongue_image: Optional[np.ndarray] = None,
                             pulse_waveform: Optional[np.ndarray] = None,
                             pulse_duration: float = 30.0) -> Dict[str, Any]:
        """综合分析舌脉象"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'tongue_analysis': None,
            'pulse_analysis': None,
            'syndrome_classification': None,
            'recommendations': []
        }
        
        try:
            # 舌诊分析
            if tongue_image is not None:
                tongue_result = self.tongue_analyzer.analyze_tongue_image(tongue_image)
                results['tongue_analysis'] = {
                    'color': tongue_result.color.value,
                    'coating': tongue_result.coating.value,
                    'texture': tongue_result.texture,
                    'moisture': tongue_result.moisture,
                    'thickness': tongue_result.thickness,
                    'color_confidence': tongue_result.color_confidence,
                    'coating_confidence': tongue_result.coating_confidence,
                    'abnormal_areas': tongue_result.abnormal_areas
                }
            
            # 脉诊分析
            if pulse_waveform is not None:
                pulse_result = self.pulse_analyzer.analyze_pulse_waveform(pulse_waveform, pulse_duration)
                results['pulse_analysis'] = {
                    'pulse_type': pulse_result.pulse_type.value,
                    'rate': pulse_result.rate,
                    'rhythm': pulse_result.rhythm,
                    'strength': pulse_result.strength,
                    'depth': pulse_result.depth,
                    'width': pulse_result.width,
                    'confidence': pulse_result.confidence,
                    'waveform_features': pulse_result.waveform_features
                }
            
            # 证候分类
            if results['tongue_analysis'] or results['pulse_analysis']:
                syndrome_result = self._classify_syndrome(results['tongue_analysis'], results['pulse_analysis'])
                results['syndrome_classification'] = syndrome_result
                
                # 生成建议
                recommendations = self._generate_recommendations(syndrome_result)
                results['recommendations'] = recommendations
            
            return results
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            results['error'] = str(e)
            return results
    
    def _classify_syndrome(self, tongue_analysis: Optional[Dict], pulse_analysis: Optional[Dict]) -> Dict[str, Any]:
        """证候分类"""
        syndrome_scores = {}
        
        for syndrome, rules in self.syndrome_classifier['rules'].items():
            score = 0.0
            matched_features = []
            
            # 舌色匹配
            if tongue_analysis and 'color' in tongue_analysis:
                tongue_color = TongueColor(tongue_analysis['color'])
                if tongue_color in rules['tongue_color']:
                    score += self.syndrome_classifier['weights']['tongue_color']
                    matched_features.append(f"舌色: {tongue_color.value}")
            
            # 舌苔匹配
            if tongue_analysis and 'coating' in tongue_analysis:
                tongue_coating = TongueCoating(tongue_analysis['coating'])
                if tongue_coating in rules['tongue_coating']:
                    score += self.syndrome_classifier['weights']['tongue_coating']
                    matched_features.append(f"舌苔: {tongue_coating.value}")
            
            # 脉象匹配
            if pulse_analysis and 'pulse_type' in pulse_analysis:
                pulse_type = PulseType(pulse_analysis['pulse_type'])
                if pulse_type in rules['pulse_type']:
                    score += self.syndrome_classifier['weights']['pulse_type']
                    matched_features.append(f"脉象: {pulse_type.value}")
            
            # 脉率匹配
            if pulse_analysis and 'rate' in pulse_analysis:
                pulse_rate = pulse_analysis['rate']
                min_rate, max_rate = rules['pulse_rate_range']
                if min_rate <= pulse_rate <= max_rate:
                    score += self.syndrome_classifier['weights']['pulse_rate']
                    matched_features.append(f"脉率: {pulse_rate:.1f}次/分")
            
            syndrome_scores[syndrome] = {
                'score': score,
                'matched_features': matched_features,
                'confidence': score >= rules['confidence_threshold']
            }
        
        # 排序并返回最可能的证候
        sorted_syndromes = sorted(syndrome_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        return {
            'primary_syndrome': sorted_syndromes[0][0] if sorted_syndromes else None,
            'primary_score': sorted_syndromes[0][1]['score'] if sorted_syndromes else 0.0,
            'all_syndromes': dict(sorted_syndromes),
            'confidence': sorted_syndromes[0][1]['confidence'] if sorted_syndromes else False
        }
    
    def _generate_recommendations(self, syndrome_result: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        primary_syndrome = syndrome_result.get('primary_syndrome')
        
        if not primary_syndrome:
            recommendations.append("建议进一步检查以明确诊断")
            return recommendations
        
        # 基于证候的建议
        syndrome_recommendations = {
            '气虚证': [
                "建议补气养血，可考虑四君子汤加减",
                "注意休息，避免过度劳累",
                "饮食宜清淡易消化，多食用山药、大枣等补气食物"
            ],
            '血瘀证': [
                "建议活血化瘀，可考虑血府逐瘀汤加减",
                "适当运动，促进血液循环",
                "避免久坐久立，注意保暖"
            ],
            '湿热证': [
                "建议清热利湿，可考虑甘露消毒丹加减",
                "饮食宜清淡，避免辛辣油腻食物",
                "保持环境通风干燥"
            ],
            '阴虚证': [
                "建议滋阴润燥，可考虑六味地黄丸加减",
                "避免熬夜，保证充足睡眠",
                "多食用银耳、百合等滋阴食物"
            ]
        }
        
        if primary_syndrome in syndrome_recommendations:
            recommendations.extend(syndrome_recommendations[primary_syndrome])
        
        # 添加置信度说明
        confidence = syndrome_result.get('confidence', False)
        if not confidence:
            recommendations.append("注意：诊断置信度较低，建议结合其他检查方法")
        
        return recommendations 