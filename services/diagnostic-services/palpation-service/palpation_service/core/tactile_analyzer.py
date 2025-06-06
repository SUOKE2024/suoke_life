"""
tactile_analyzer - 索克生活项目模块
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from scipy.stats import skew, kurtosis
from typing import Dict, List, Tuple, Optional, Any
import asyncio
import logging
import numpy as np
import scipy.signal

"""
切诊触觉分析器

基于传感器数据和信号处理技术，实现中医切诊的智能分析功能。
包括脉象分析、腹诊、按压诊断等核心功能。
"""


logger = logging.getLogger(__name__)

class PalpationType(str, Enum):
    """切诊类型"""
    PULSE = "脉诊"
    ABDOMEN = "腹诊"
    ACUPOINT = "穴位"
    SKIN = "皮肤"

class PulseType(str, Enum):
    """脉象类型"""
    NORMAL = "平脉"
    RAPID = "数脉"
    SLOW = "迟脉"
    STRONG = "洪脉"
    WEAK = "细脉"
    SLIPPERY = "滑脉"
    ROUGH = "涩脉"
    WIRY = "弦脉"
    TIGHT = "紧脉"
    FLOATING = "浮脉"
    DEEP = "沉脉"

@dataclass
class PulseSignal:
    """脉搏信号数据"""
    timestamp: np.ndarray  # 时间戳
    amplitude: np.ndarray  # 振幅
    pressure: np.ndarray   # 压力
    sample_rate: float     # 采样率
    duration: float        # 持续时间

@dataclass
class PulseAnalysisResult:
    """脉象分析结果"""
    pulse_rate: float      # 脉率（次/分钟）
    pulse_type: PulseType  # 脉象类型
    rhythm_regularity: str # 节律规整性
    pulse_strength: str    # 脉力
    pulse_tension: str     # 脉张力
    pulse_depth: str       # 脉位
    waveform_features: Dict[str, float]  # 波形特征
    tcm_diagnosis: str     # 中医诊断
    confidence: float

@dataclass
class AbdomenAnalysisResult:
    """腹诊分析结果"""
    tenderness_points: List[Tuple[float, float]]  # 压痛点坐标
    muscle_tension: str    # 肌肉紧张度
    organ_enlargement: Dict[str, str]  # 脏器肿大
    masses: List[Dict[str, Any]]  # 肿块
    bowel_sounds: str      # 肠鸣音
    tcm_diagnosis: str     # 中医诊断
    confidence: float

@dataclass
class AcupointAnalysisResult:
    """穴位分析结果"""
    point_name: str        # 穴位名称
    sensitivity: str       # 敏感性
    temperature: str       # 温度
    texture: str           # 质地
    elasticity: str        # 弹性
    tcm_indication: str    # 中医指征
    confidence: float

@dataclass
class TactileAnalysisResult:
    """触觉分析综合结果"""
    pulse_analysis: Optional[PulseAnalysisResult]
    abdomen_analysis: Optional[AbdomenAnalysisResult]
    acupoint_analyses: List[AcupointAnalysisResult]
    overall_diagnosis: str
    recommendations: List[str]
    confidence: float

class PulseAnalyzer:
    """脉象分析器"""
    
    def __init__(self):
        # 脉象特征阈值
        self.pulse_thresholds = {
            "rate": {
                "slow": 60,      # 迟脉
                "normal_low": 60,
                "normal_high": 100,
                "rapid": 100     # 数脉
            },
            "amplitude": {
                "weak": 0.3,     # 细脉
                "normal": 0.7,
                "strong": 1.2    # 洪脉
            },
            "regularity": {
                "regular": 0.1,
                "irregular": 0.3
            }
        }
        
        # 脉象诊断模式
        self.pulse_patterns = {
            "气虚": {"rate": "slow", "amplitude": "weak", "depth": "deep"},
            "阳虚": {"rate": "slow", "amplitude": "weak", "depth": "deep", "tension": "soft"},
            "阴虚": {"rate": "rapid", "amplitude": "weak", "depth": "floating"},
            "血瘀": {"rate": "normal", "amplitude": "normal", "type": "rough"},
            "痰湿": {"rate": "slow", "amplitude": "normal", "type": "slippery"},
            "肝郁": {"rate": "normal", "amplitude": "normal", "type": "wiry"},
            "心火": {"rate": "rapid", "amplitude": "strong", "depth": "floating"}
        }
    
    def analyze_pulse(self, pulse_signal: PulseSignal) -> PulseAnalysisResult:
        """分析脉象"""
        # 预处理信号
        filtered_signal = self._preprocess_signal(pulse_signal)
        
        # 检测脉搏峰值
        peaks = self._detect_pulse_peaks(filtered_signal)
        
        # 计算脉率
        pulse_rate = self._calculate_pulse_rate(peaks, pulse_signal.sample_rate)
        
        # 分析脉象特征
        pulse_features = self._extract_pulse_features(filtered_signal, peaks)
        
        # 识别脉象类型
        pulse_type = self._classify_pulse_type(pulse_features)
        
        # 分析节律规整性
        rhythm_regularity = self._analyze_rhythm(peaks)
        
        # 分析脉力
        pulse_strength = self._analyze_pulse_strength(pulse_features)
        
        # 分析脉张力
        pulse_tension = self._analyze_pulse_tension(pulse_features)
        
        # 分析脉位
        pulse_depth = self._analyze_pulse_depth(pulse_features)
        
        # 中医诊断
        tcm_diagnosis = self._generate_pulse_diagnosis(
            pulse_rate, pulse_type, pulse_strength, pulse_depth
        )
        
        # 计算置信度
        confidence = self._calculate_pulse_confidence(pulse_signal, peaks)
        
        return PulseAnalysisResult(
            pulse_rate=pulse_rate,
            pulse_type=pulse_type,
            rhythm_regularity=rhythm_regularity,
            pulse_strength=pulse_strength,
            pulse_tension=pulse_tension,
            pulse_depth=pulse_depth,
            waveform_features=pulse_features,
            tcm_diagnosis=tcm_diagnosis,
            confidence=confidence
        )
    
    def _preprocess_signal(self, pulse_signal: PulseSignal) -> np.ndarray:
        """预处理脉搏信号"""
        # 带通滤波（0.5-5Hz）
        nyquist = pulse_signal.sample_rate / 2
        low = 0.5 / nyquist
        high = 5.0 / nyquist
        
        b, a = scipy.signal.butter(4, [low, high], btype='band')
        filtered = scipy.signal.filtfilt(b, a, pulse_signal.amplitude)
        
        # 去除基线漂移
        baseline = scipy.signal.savgol_filter(filtered, 51, 3)
        filtered = filtered - baseline
        
        return filtered
    
    def _detect_pulse_peaks(self, signal: np.ndarray) -> np.ndarray:
        """检测脉搏峰值"""
        # 使用自适应阈值检测峰值
        threshold = np.std(signal) * 0.5
        min_distance = int(0.4 * len(signal) / 60)  # 最小间隔（假设最大150bpm）
        
        peaks, _ = scipy.signal.find_peaks(
            signal, 
            height=threshold,
            distance=min_distance
        )
        
        return peaks
    
    def _calculate_pulse_rate(self, peaks: np.ndarray, sample_rate: float) -> float:
        """计算脉率"""
        if len(peaks) < 2:
            return 0.0
        
        # 计算平均心跳间隔
        intervals = np.diff(peaks) / sample_rate
        avg_interval = np.mean(intervals)
        
        # 转换为每分钟次数
        pulse_rate = 60.0 / avg_interval
        
        return pulse_rate
    
    def _extract_pulse_features(self, signal: np.ndarray, peaks: np.ndarray) -> Dict[str, float]:
        """提取脉象特征"""
        features = {}
        
        if len(peaks) < 2:
            return features
        
        # 振幅特征
        features['mean_amplitude'] = np.mean(signal[peaks])
        features['amplitude_std'] = np.std(signal[peaks])
        features['max_amplitude'] = np.max(signal[peaks])
        
        # 间隔特征
        intervals = np.diff(peaks)
        features['mean_interval'] = np.mean(intervals)
        features['interval_std'] = np.std(intervals)
        features['interval_cv'] = features['interval_std'] / features['mean_interval']
        
        # 波形特征
        if len(peaks) > 0:
            # 提取单个脉搏波形
            pulse_waves = []
            for i in range(len(peaks) - 1):
                start = peaks[i]
                end = peaks[i + 1]
                wave = signal[start:end]
                if len(wave) > 10:  # 确保波形足够长
                    pulse_waves.append(wave)
            
            if pulse_waves:
                # 计算平均波形
                min_len = min(len(wave) for wave in pulse_waves)
                normalized_waves = [wave[:min_len] for wave in pulse_waves]
                avg_wave = np.mean(normalized_waves, axis=0)
                
                # 波形形状特征
                features['wave_skewness'] = skew(avg_wave)
                features['wave_kurtosis'] = kurtosis(avg_wave)
                features['wave_energy'] = np.sum(avg_wave ** 2)
        
        return features
    
    def _classify_pulse_type(self, features: Dict[str, float]) -> PulseType:
        """分类脉象类型"""
        if not features:
            return PulseType.NORMAL
        
        mean_amplitude = features.get('mean_amplitude', 0)
        interval_cv = features.get('interval_cv', 0)
        wave_skewness = features.get('wave_skewness', 0)
        
        # 基于特征分类脉象
        if mean_amplitude > 1.0:
            return PulseType.STRONG  # 洪脉
        elif mean_amplitude < 0.3:
            return PulseType.WEAK    # 细脉
        elif interval_cv > 0.2:
            return PulseType.ROUGH   # 涩脉
        elif wave_skewness > 0.5:
            return PulseType.SLIPPERY  # 滑脉
        elif wave_skewness < -0.5:
            return PulseType.WIRY    # 弦脉
        else:
            return PulseType.NORMAL  # 平脉
    
    def _analyze_rhythm(self, peaks: np.ndarray) -> str:
        """分析节律规整性"""
        if len(peaks) < 3:
            return "无法判断"
        
        intervals = np.diff(peaks)
        cv = np.std(intervals) / np.mean(intervals)
        
        if cv < 0.1:
            return "规律"
        elif cv < 0.2:
            return "基本规律"
        else:
            return "不规律"
    
    def _analyze_pulse_strength(self, features: Dict[str, float]) -> str:
        """分析脉力"""
        amplitude = features.get('mean_amplitude', 0)
        
        if amplitude > 1.0:
            return "有力"
        elif amplitude < 0.3:
            return "无力"
        else:
            return "正常"
    
    def _analyze_pulse_tension(self, features: Dict[str, float]) -> str:
        """分析脉张力"""
        wave_kurtosis = features.get('wave_kurtosis', 0)
        
        if wave_kurtosis > 1.0:
            return "紧张"
        elif wave_kurtosis < -1.0:
            return "松弛"
        else:
            return "正常"
    
    def _analyze_pulse_depth(self, features: Dict[str, float]) -> str:
        """分析脉位"""
        # 这里需要结合压力传感器数据
        # 暂时基于振幅特征估计
        amplitude = features.get('mean_amplitude', 0)
        
        if amplitude > 0.8:
            return "浮"
        elif amplitude < 0.4:
            return "沉"
        else:
            return "中"
    
    def _generate_pulse_diagnosis(self, pulse_rate: float, pulse_type: PulseType,
                                pulse_strength: str, pulse_depth: str) -> str:
        """生成脉象中医诊断"""
        # 基于脉象特征组合诊断
        if pulse_rate < 60 and pulse_strength == "无力":
            return "气虚证"
        elif pulse_rate < 60 and pulse_depth == "沉":
            return "阳虚证"
        elif pulse_rate > 100 and pulse_strength == "无力":
            return "阴虚证"
        elif pulse_type == PulseType.WIRY:
            return "肝郁证"
        elif pulse_type == PulseType.SLIPPERY:
            return "痰湿证"
        elif pulse_type == PulseType.ROUGH:
            return "血瘀证"
        elif pulse_rate > 100 and pulse_strength == "有力":
            return "实热证"
        else:
            return "正常"
    
    def _calculate_pulse_confidence(self, pulse_signal: PulseSignal, 
                                  peaks: np.ndarray) -> float:
        """计算脉象分析置信度"""
        # 基于信号质量和检测稳定性
        if len(peaks) < 3:
            return 0.3
        
        # 信噪比
        signal_power = np.mean(pulse_signal.amplitude ** 2)
        noise_power = np.var(pulse_signal.amplitude)
        snr = signal_power / max(noise_power, 1e-10)
        snr_score = min(snr / 10, 1.0)
        
        # 检测稳定性
        intervals = np.diff(peaks)
        stability = 1.0 / (1.0 + np.std(intervals) / np.mean(intervals))
        
        confidence = (snr_score + stability) / 2
        return max(0.4, min(0.95, confidence))

class AbdomenAnalyzer:
    """腹诊分析器"""
    
    def __init__(self):
        # 腹部区域定义
        self.abdomen_regions = {
            "右上腹": (0.7, 0.3),   # 肝区
            "上腹": (0.5, 0.3),     # 胃区
            "左上腹": (0.3, 0.3),   # 脾区
            "右腹": (0.7, 0.5),     # 升结肠
            "脐周": (0.5, 0.5),     # 小肠
            "左腹": (0.3, 0.5),     # 降结肠
            "右下腹": (0.7, 0.7),   # 阑尾区
            "下腹": (0.5, 0.7),     # 膀胱区
            "左下腹": (0.3, 0.7)    # 乙状结肠
        }
    
    def analyze_abdomen(self, pressure_data: np.ndarray, 
                       coordinates: List[Tuple[float, float]]) -> AbdomenAnalysisResult:
        """分析腹诊数据"""
        # 检测压痛点
        tenderness_points = self._detect_tenderness_points(pressure_data, coordinates)
        
        # 分析肌肉紧张度
        muscle_tension = self._analyze_muscle_tension(pressure_data)
        
        # 检测脏器肿大
        organ_enlargement = self._detect_organ_enlargement(pressure_data, coordinates)
        
        # 检测肿块
        masses = self._detect_masses(pressure_data, coordinates)
        
        # 分析肠鸣音（需要音频数据）
        bowel_sounds = "正常"  # 简化处理
        
        # 中医诊断
        tcm_diagnosis = self._generate_abdomen_diagnosis(
            tenderness_points, muscle_tension, organ_enlargement
        )
        
        # 计算置信度
        confidence = self._calculate_abdomen_confidence(pressure_data)
        
        return AbdomenAnalysisResult(
            tenderness_points=tenderness_points,
            muscle_tension=muscle_tension,
            organ_enlargement=organ_enlargement,
            masses=masses,
            bowel_sounds=bowel_sounds,
            tcm_diagnosis=tcm_diagnosis,
            confidence=confidence
        )
    
    def _detect_tenderness_points(self, pressure_data: np.ndarray,
                                coordinates: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """检测压痛点"""
        tenderness_points = []
        
        # 寻找压力异常高的点
        threshold = np.mean(pressure_data) + 2 * np.std(pressure_data)
        
        for i, pressure in enumerate(pressure_data):
            if pressure > threshold and i < len(coordinates):
                tenderness_points.append(coordinates[i])
        
        return tenderness_points
    
    def _analyze_muscle_tension(self, pressure_data: np.ndarray) -> str:
        """分析肌肉紧张度"""
        baseline_pressure = np.median(pressure_data)
        
        if baseline_pressure > np.mean(pressure_data) + np.std(pressure_data):
            return "紧张"
        elif baseline_pressure < np.mean(pressure_data) - np.std(pressure_data):
            return "松弛"
        else:
            return "正常"
    
    def _detect_organ_enlargement(self, pressure_data: np.ndarray,
                                coordinates: List[Tuple[float, float]]) -> Dict[str, str]:
        """检测脏器肿大"""
        enlargement = {}
        
        # 简化的脏器肿大检测
        for region, (x, y) in self.abdomen_regions.items():
            # 找到该区域的压力数据
            region_pressures = []
            for i, (coord_x, coord_y) in enumerate(coordinates):
                if abs(coord_x - x) < 0.1 and abs(coord_y - y) < 0.1:
                    region_pressures.append(pressure_data[i])
            
            if region_pressures:
                avg_pressure = np.mean(region_pressures)
                if avg_pressure > np.mean(pressure_data) + np.std(pressure_data):
                    enlargement[region] = "肿大"
        
        return enlargement
    
    def _detect_masses(self, pressure_data: np.ndarray,
                      coordinates: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """检测肿块"""
        masses = []
        
        # 使用聚类方法检测肿块
        high_pressure_indices = np.where(
            pressure_data > np.mean(pressure_data) + 1.5 * np.std(pressure_data)
        )[0]
        
        if len(high_pressure_indices) > 0:
            # 简化的肿块检测
            for idx in high_pressure_indices:
                if idx < len(coordinates):
                    mass = {
                        "location": coordinates[idx],
                        "size": "小",
                        "hardness": "中等",
                        "mobility": "可移动"
                    }
                    masses.append(mass)
        
        return masses
    
    def _generate_abdomen_diagnosis(self, tenderness_points: List[Tuple[float, float]],
                                  muscle_tension: str, 
                                  organ_enlargement: Dict[str, str]) -> str:
        """生成腹诊中医诊断"""
        if len(tenderness_points) > 3:
            return "腹部瘀滞"
        elif muscle_tension == "紧张":
            return "肝气郁结"
        elif "右上腹" in organ_enlargement:
            return "肝胆湿热"
        elif "上腹" in organ_enlargement:
            return "脾胃不和"
        elif muscle_tension == "松弛":
            return "脾虚气陷"
        else:
            return "正常"
    
    def _calculate_abdomen_confidence(self, pressure_data: np.ndarray) -> float:
        """计算腹诊分析置信度"""
        # 基于数据质量和一致性
        if len(pressure_data) < 10:
            return 0.4
        
        # 数据变异性
        cv = np.std(pressure_data) / np.mean(pressure_data)
        consistency_score = 1.0 / (1.0 + cv)
        
        # 数据完整性
        completeness_score = min(len(pressure_data) / 50, 1.0)
        
        confidence = (consistency_score + completeness_score) / 2
        return max(0.5, min(0.9, confidence))

class TactileAnalyzer:
    """触觉分析器主类"""
    
    def __init__(self):
        self.pulse_analyzer = PulseAnalyzer()
        self.abdomen_analyzer = AbdomenAnalyzer()
        
        logger.info("切诊触觉分析器初始化完成")
    
    async def analyze_pulse(self, pulse_signal: PulseSignal) -> PulseAnalysisResult:
        """脉象分析"""
        try:
            result = self.pulse_analyzer.analyze_pulse(pulse_signal)
            logger.info(f"脉象分析完成，诊断: {result.tcm_diagnosis}")
            return result
        except Exception as e:
            logger.error(f"脉象分析失败: {e}")
            raise
    
    async def analyze_abdomen(self, pressure_data: np.ndarray,
                            coordinates: List[Tuple[float, float]]) -> AbdomenAnalysisResult:
        """腹诊分析"""
        try:
            result = self.abdomen_analyzer.analyze_abdomen(pressure_data, coordinates)
            logger.info(f"腹诊分析完成，诊断: {result.tcm_diagnosis}")
            return result
        except Exception as e:
            logger.error(f"腹诊分析失败: {e}")
            raise
    
    async def comprehensive_analysis(self, 
                                   pulse_signal: Optional[PulseSignal] = None,
                                   abdomen_data: Optional[Tuple[np.ndarray, List[Tuple[float, float]]]] = None,
                                   acupoint_data: Optional[List[Dict[str, Any]]] = None) -> TactileAnalysisResult:
        """综合触觉分析"""
        try:
            # 脉象分析
            pulse_analysis = None
            if pulse_signal:
                pulse_analysis = await self.analyze_pulse(pulse_signal)
            
            # 腹诊分析
            abdomen_analysis = None
            if abdomen_data:
                pressure_data, coordinates = abdomen_data
                abdomen_analysis = await self.analyze_abdomen(pressure_data, coordinates)
            
            # 穴位分析
            acupoint_analyses = []
            if acupoint_data:
                for point_data in acupoint_data:
                    acupoint_analysis = self._analyze_acupoint(point_data)
                    acupoint_analyses.append(acupoint_analysis)
            
            # 综合诊断
            overall_diagnosis = self._generate_overall_diagnosis(
                pulse_analysis, abdomen_analysis, acupoint_analyses
            )
            
            # 生成建议
            recommendations = self._generate_recommendations(
                pulse_analysis, abdomen_analysis, acupoint_analyses
            )
            
            # 计算综合置信度
            confidence = self._calculate_overall_confidence(
                pulse_analysis, abdomen_analysis, acupoint_analyses
            )
            
            result = TactileAnalysisResult(
                pulse_analysis=pulse_analysis,
                abdomen_analysis=abdomen_analysis,
                acupoint_analyses=acupoint_analyses,
                overall_diagnosis=overall_diagnosis,
                recommendations=recommendations,
                confidence=confidence
            )
            
            logger.info(f"综合切诊分析完成，诊断: {overall_diagnosis}")
            return result
            
        except Exception as e:
            logger.error(f"综合切诊分析失败: {e}")
            raise
    
    def _analyze_acupoint(self, point_data: Dict[str, Any]) -> AcupointAnalysisResult:
        """分析穴位"""
        point_name = point_data.get("name", "未知穴位")
        pressure = point_data.get("pressure", 0)
        temperature = point_data.get("temperature", 36.5)
        
        # 分析敏感性
        sensitivity = "正常"
        if pressure > 1.5:
            sensitivity = "敏感"
        elif pressure < 0.5:
            sensitivity = "迟钝"
        
        # 分析温度
        temp_status = "正常"
        if temperature > 37.0:
            temp_status = "偏热"
        elif temperature < 36.0:
            temp_status = "偏凉"
        
        # 中医指征
        tcm_indication = self._get_acupoint_indication(point_name, sensitivity, temp_status)
        
        return AcupointAnalysisResult(
            point_name=point_name,
            sensitivity=sensitivity,
            temperature=temp_status,
            texture="正常",
            elasticity="正常",
            tcm_indication=tcm_indication,
            confidence=0.7
        )
    
    def _get_acupoint_indication(self, point_name: str, sensitivity: str, temperature: str) -> str:
        """获取穴位中医指征"""
        # 简化的穴位诊断
        if sensitivity == "敏感":
            if "胃" in point_name:
                return "胃气不和"
            elif "肝" in point_name:
                return "肝气郁结"
            else:
                return "气血瘀滞"
        elif temperature == "偏热":
            return "局部热证"
        elif temperature == "偏凉":
            return "阳气不足"
        else:
            return "正常"
    
    def _generate_overall_diagnosis(self, pulse_analysis: Optional[PulseAnalysisResult],
                                  abdomen_analysis: Optional[AbdomenAnalysisResult],
                                  acupoint_analyses: List[AcupointAnalysisResult]) -> str:
        """生成综合诊断"""
        diagnoses = []
        
        if pulse_analysis:
            diagnoses.append(pulse_analysis.tcm_diagnosis)
        
        if abdomen_analysis:
            diagnoses.append(abdomen_analysis.tcm_diagnosis)
        
        # 统计最常见的诊断
        diagnosis_counts = defaultdict(int)
        for diagnosis in diagnoses:
            if diagnosis != "正常":
                diagnosis_counts[diagnosis] += 1
        
        if diagnosis_counts:
            return max(diagnosis_counts, key=diagnosis_counts.get)
        else:
            return "正常"
    
    def _generate_recommendations(self, pulse_analysis: Optional[PulseAnalysisResult],
                                abdomen_analysis: Optional[AbdomenAnalysisResult],
                                acupoint_analyses: List[AcupointAnalysisResult]) -> List[str]:
        """生成治疗建议"""
        recommendations = []
        
        if pulse_analysis and pulse_analysis.tcm_diagnosis != "正常":
            if "气虚" in pulse_analysis.tcm_diagnosis:
                recommendations.append("建议补气养血，适当休息")
            elif "阳虚" in pulse_analysis.tcm_diagnosis:
                recommendations.append("建议温阳补肾，注意保暖")
            elif "阴虚" in pulse_analysis.tcm_diagnosis:
                recommendations.append("建议滋阴润燥，避免熬夜")
        
        if abdomen_analysis and abdomen_analysis.tcm_diagnosis != "正常":
            if "肝气郁结" in abdomen_analysis.tcm_diagnosis:
                recommendations.append("建议疏肝理气，保持心情舒畅")
            elif "脾胃不和" in abdomen_analysis.tcm_diagnosis:
                recommendations.append("建议健脾和胃，饮食规律")
        
        # 穴位建议
        for acupoint in acupoint_analyses:
            if acupoint.sensitivity == "敏感":
                recommendations.append(f"建议针对{acupoint.point_name}进行调理")
        
        return list(set(recommendations))  # 去重
    
    def _calculate_overall_confidence(self, pulse_analysis: Optional[PulseAnalysisResult],
                                    abdomen_analysis: Optional[AbdomenAnalysisResult],
                                    acupoint_analyses: List[AcupointAnalysisResult]) -> float:
        """计算综合置信度"""
        confidences = []
        
        if pulse_analysis:
            confidences.append(pulse_analysis.confidence)
        
        if abdomen_analysis:
            confidences.append(abdomen_analysis.confidence)
        
        for acupoint in acupoint_analyses:
            confidences.append(acupoint.confidence)
        
        if confidences:
            return np.mean(confidences)
        else:
            return 0.5 