#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境智能模块 - 智能环境感知和分析系统
包含环境状态识别、环境变化预测、多模态环境分析、环境适应性建议等功能
"""

import logging
import time
import asyncio
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """环境类型枚举"""
    INDOOR_HOME = "indoor_home"
    INDOOR_OFFICE = "indoor_office"
    INDOOR_PUBLIC = "indoor_public"
    OUTDOOR_URBAN = "outdoor_urban"
    OUTDOOR_NATURE = "outdoor_nature"
    VEHICLE = "vehicle"
    UNKNOWN = "unknown"


class EnvironmentCondition(Enum):
    """环境状况枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    HAZARDOUS = "hazardous"


class WeatherCondition(Enum):
    """天气状况枚举"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    STORMY = "stormy"
    UNKNOWN = "unknown"


@dataclass
class EnvironmentReading:
    """环境读数数据结构"""
    timestamp: float
    location: Dict[str, float]  # lat, lon, alt
    temperature: float
    humidity: float
    pressure: float
    light_level: float
    noise_level: float
    air_quality: Optional[float] = None
    uv_index: Optional[float] = None
    wind_speed: Optional[float] = None
    visibility: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentAnalysis:
    """环境分析结果"""
    environment_type: EnvironmentType
    condition: EnvironmentCondition
    weather: WeatherCondition
    comfort_score: float  # 0-1
    safety_score: float   # 0-1
    accessibility_score: float  # 0-1
    recommendations: List[str]
    alerts: List[str]
    confidence: float
    analysis_time: float


@dataclass
class EnvironmentPattern:
    """环境模式"""
    pattern_id: str
    location_cluster: Dict[str, float]  # 位置聚类中心
    typical_conditions: Dict[str, float]  # 典型环境条件
    time_patterns: List[Tuple[int, int]]  # 时间模式
    frequency: int
    last_seen: float
    confidence: float


class EnvironmentClassifier:
    """环境分类器"""
    
    def __init__(self):
        self.classification_rules = self._initialize_classification_rules()
        self.location_patterns = defaultdict(list)  # 位置模式缓存
    
    def _initialize_classification_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化环境分类规则"""
        return {
            "indoor_home": {
                "temperature_range": (18, 28),
                "humidity_range": (30, 70),
                "light_range": (10, 500),
                "noise_range": (20, 60),
                "stability_threshold": 0.8,  # 环境稳定性阈值
                "indicators": ["stable_temperature", "low_noise", "controlled_lighting"]
            },
            "indoor_office": {
                "temperature_range": (20, 26),
                "humidity_range": (40, 60),
                "light_range": (200, 800),
                "noise_range": (30, 70),
                "stability_threshold": 0.7,
                "indicators": ["consistent_lighting", "moderate_noise", "climate_controlled"]
            },
            "indoor_public": {
                "temperature_range": (18, 30),
                "humidity_range": (30, 80),
                "light_range": (100, 1000),
                "noise_range": (40, 85),
                "stability_threshold": 0.5,
                "indicators": ["variable_conditions", "higher_noise", "public_lighting"]
            },
            "outdoor_urban": {
                "temperature_range": (-10, 45),
                "humidity_range": (20, 90),
                "light_range": (0, 100000),
                "noise_range": (50, 90),
                "stability_threshold": 0.3,
                "indicators": ["variable_weather", "traffic_noise", "natural_light"]
            },
            "outdoor_nature": {
                "temperature_range": (-20, 40),
                "humidity_range": (30, 95),
                "light_range": (0, 120000),
                "noise_range": (20, 60),
                "stability_threshold": 0.4,
                "indicators": ["natural_conditions", "low_noise", "variable_light"]
            },
            "vehicle": {
                "temperature_range": (15, 30),
                "humidity_range": (30, 70),
                "light_range": (10, 1000),
                "noise_range": (60, 85),
                "stability_threshold": 0.6,
                "indicators": ["controlled_climate", "engine_noise", "variable_light"]
            }
        }
    
    def classify_environment(self, reading: EnvironmentReading, 
                           historical_data: List[EnvironmentReading]) -> EnvironmentType:
        """分类环境类型"""
        try:
            scores = {}
            
            # 计算每种环境类型的匹配分数
            for env_type, rules in self.classification_rules.items():
                score = self._calculate_environment_score(reading, rules, historical_data)
                scores[env_type] = score
            
            # 选择得分最高的环境类型
            best_match = max(scores.items(), key=lambda x: x[1])
            
            if best_match[1] > 0.5:  # 置信度阈值
                return EnvironmentType(best_match[0])
            else:
                return EnvironmentType.UNKNOWN
                
        except Exception as e:
            logger.error(f"环境分类失败: {str(e)}")
            return EnvironmentType.UNKNOWN
    
    def _calculate_environment_score(self, reading: EnvironmentReading, 
                                   rules: Dict[str, Any], 
                                   historical_data: List[EnvironmentReading]) -> float:
        """计算环境类型匹配分数"""
        score = 0.0
        
        # 温度匹配
        temp_range = rules["temperature_range"]
        if temp_range[0] <= reading.temperature <= temp_range[1]:
            score += 0.2
        else:
            # 计算偏离程度
            deviation = min(abs(reading.temperature - temp_range[0]), 
                          abs(reading.temperature - temp_range[1]))
            score += max(0, 0.2 - deviation / 20.0)
        
        # 湿度匹配
        humidity_range = rules["humidity_range"]
        if humidity_range[0] <= reading.humidity <= humidity_range[1]:
            score += 0.2
        else:
            deviation = min(abs(reading.humidity - humidity_range[0]), 
                          abs(reading.humidity - humidity_range[1]))
            score += max(0, 0.2 - deviation / 30.0)
        
        # 光线匹配
        light_range = rules["light_range"]
        if light_range[0] <= reading.light_level <= light_range[1]:
            score += 0.2
        else:
            # 对数尺度计算光线偏离
            log_reading = math.log10(max(1, reading.light_level))
            log_min = math.log10(max(1, light_range[0]))
            log_max = math.log10(max(1, light_range[1]))
            
            if log_reading < log_min:
                deviation = log_min - log_reading
            else:
                deviation = log_reading - log_max
            
            score += max(0, 0.2 - deviation / 2.0)
        
        # 噪音匹配
        noise_range = rules["noise_range"]
        if noise_range[0] <= reading.noise_level <= noise_range[1]:
            score += 0.2
        else:
            deviation = min(abs(reading.noise_level - noise_range[0]), 
                          abs(reading.noise_level - noise_range[1]))
            score += max(0, 0.2 - deviation / 20.0)
        
        # 稳定性分析
        if len(historical_data) >= 5:
            stability_score = self._calculate_stability(historical_data)
            expected_stability = rules["stability_threshold"]
            stability_match = 1.0 - abs(stability_score - expected_stability)
            score += stability_match * 0.2
        
        return min(1.0, score)
    
    def _calculate_stability(self, historical_data: List[EnvironmentReading]) -> float:
        """计算环境稳定性"""
        if len(historical_data) < 2:
            return 0.5
        
        # 计算各项指标的变异系数
        temps = [r.temperature for r in historical_data[-10:]]
        humidities = [r.humidity for r in historical_data[-10:]]
        lights = [r.light_level for r in historical_data[-10:]]
        noises = [r.noise_level for r in historical_data[-10:]]
        
        stability_scores = []
        
        for values in [temps, humidities, lights, noises]:
            if len(values) > 1:
                mean_val = np.mean(values)
                std_val = np.std(values)
                cv = std_val / mean_val if mean_val > 0 else 1.0
                stability = max(0, 1.0 - cv)
                stability_scores.append(stability)
        
        return np.mean(stability_scores) if stability_scores else 0.5


class WeatherAnalyzer:
    """天气分析器"""
    
    def __init__(self):
        self.weather_patterns = self._initialize_weather_patterns()
    
    def _initialize_weather_patterns(self) -> Dict[str, Dict[str, Any]]:
        """初始化天气模式"""
        return {
            "sunny": {
                "light_threshold": 10000,
                "humidity_max": 60,
                "pressure_range": (1010, 1030),
                "temperature_factor": 1.0
            },
            "cloudy": {
                "light_threshold": 5000,
                "humidity_range": (50, 80),
                "pressure_range": (1000, 1020),
                "temperature_factor": 0.9
            },
            "rainy": {
                "light_threshold": 2000,
                "humidity_min": 80,
                "pressure_max": 1010,
                "temperature_factor": 0.8
            },
            "snowy": {
                "light_threshold": 3000,
                "humidity_range": (70, 90),
                "temperature_max": 2,
                "pressure_range": (990, 1020)
            },
            "foggy": {
                "light_threshold": 1000,
                "humidity_min": 85,
                "visibility_max": 1000,
                "temperature_factor": 0.9
            },
            "stormy": {
                "light_threshold": 1500,
                "humidity_min": 75,
                "pressure_max": 1000,
                "wind_speed_min": 15
            }
        }
    
    def analyze_weather(self, reading: EnvironmentReading, 
                       historical_data: List[EnvironmentReading]) -> WeatherCondition:
        """分析天气状况"""
        try:
            # 只对户外环境进行天气分析
            if reading.metadata.get("environment_type") not in ["outdoor_urban", "outdoor_nature"]:
                return WeatherCondition.UNKNOWN
            
            scores = {}
            
            for weather_type, pattern in self.weather_patterns.items():
                score = self._calculate_weather_score(reading, pattern)
                scores[weather_type] = score
            
            # 选择得分最高的天气类型
            best_match = max(scores.items(), key=lambda x: x[1])
            
            if best_match[1] > 0.6:
                return WeatherCondition(best_match[0])
            else:
                return WeatherCondition.UNKNOWN
                
        except Exception as e:
            logger.error(f"天气分析失败: {str(e)}")
            return WeatherCondition.UNKNOWN
    
    def _calculate_weather_score(self, reading: EnvironmentReading, 
                               pattern: Dict[str, Any]) -> float:
        """计算天气模式匹配分数"""
        score = 0.0
        factors = 0
        
        # 光线强度
        if "light_threshold" in pattern:
            if reading.light_level >= pattern["light_threshold"]:
                score += 1.0
            else:
                score += reading.light_level / pattern["light_threshold"]
            factors += 1
        
        # 湿度
        if "humidity_min" in pattern:
            if reading.humidity >= pattern["humidity_min"]:
                score += 1.0
            else:
                score += reading.humidity / pattern["humidity_min"]
            factors += 1
        
        if "humidity_max" in pattern:
            if reading.humidity <= pattern["humidity_max"]:
                score += 1.0
            else:
                score += pattern["humidity_max"] / reading.humidity
            factors += 1
        
        if "humidity_range" in pattern:
            h_min, h_max = pattern["humidity_range"]
            if h_min <= reading.humidity <= h_max:
                score += 1.0
            else:
                deviation = min(abs(reading.humidity - h_min), abs(reading.humidity - h_max))
                score += max(0, 1.0 - deviation / 20.0)
            factors += 1
        
        # 气压
        if "pressure_range" in pattern:
            p_min, p_max = pattern["pressure_range"]
            if p_min <= reading.pressure <= p_max:
                score += 1.0
            else:
                deviation = min(abs(reading.pressure - p_min), abs(reading.pressure - p_max))
                score += max(0, 1.0 - deviation / 20.0)
            factors += 1
        
        if "pressure_max" in pattern:
            if reading.pressure <= pattern["pressure_max"]:
                score += 1.0
            else:
                score += pattern["pressure_max"] / reading.pressure
            factors += 1
        
        # 温度
        if "temperature_max" in pattern:
            if reading.temperature <= pattern["temperature_max"]:
                score += 1.0
            else:
                score += max(0, 1.0 - (reading.temperature - pattern["temperature_max"]) / 10.0)
            factors += 1
        
        # 风速
        if "wind_speed_min" in pattern and reading.wind_speed is not None:
            if reading.wind_speed >= pattern["wind_speed_min"]:
                score += 1.0
            else:
                score += reading.wind_speed / pattern["wind_speed_min"]
            factors += 1
        
        # 能见度
        if "visibility_max" in pattern and reading.visibility is not None:
            if reading.visibility <= pattern["visibility_max"]:
                score += 1.0
            else:
                score += pattern["visibility_max"] / reading.visibility
            factors += 1
        
        return score / factors if factors > 0 else 0.0


class ComfortAnalyzer:
    """舒适度分析器"""
    
    def __init__(self):
        self.comfort_models = self._initialize_comfort_models()
    
    def _initialize_comfort_models(self) -> Dict[str, Dict[str, Any]]:
        """初始化舒适度模型"""
        return {
            "thermal_comfort": {
                "optimal_temp": 22.0,
                "optimal_humidity": 50.0,
                "temp_tolerance": 3.0,
                "humidity_tolerance": 15.0,
                "weight": 0.4
            },
            "visual_comfort": {
                "optimal_light": 500.0,
                "min_light": 100.0,
                "max_light": 2000.0,
                "weight": 0.3
            },
            "acoustic_comfort": {
                "optimal_noise": 40.0,
                "max_comfortable": 60.0,
                "max_tolerable": 80.0,
                "weight": 0.2
            },
            "air_quality": {
                "excellent_threshold": 50,
                "good_threshold": 100,
                "moderate_threshold": 150,
                "weight": 0.1
            }
        }
    
    def calculate_comfort_score(self, reading: EnvironmentReading) -> float:
        """计算综合舒适度评分"""
        try:
            total_score = 0.0
            total_weight = 0.0
            
            # 热舒适度
            thermal_score = self._calculate_thermal_comfort(reading)
            thermal_weight = self.comfort_models["thermal_comfort"]["weight"]
            total_score += thermal_score * thermal_weight
            total_weight += thermal_weight
            
            # 视觉舒适度
            visual_score = self._calculate_visual_comfort(reading)
            visual_weight = self.comfort_models["visual_comfort"]["weight"]
            total_score += visual_score * visual_weight
            total_weight += visual_weight
            
            # 声学舒适度
            acoustic_score = self._calculate_acoustic_comfort(reading)
            acoustic_weight = self.comfort_models["acoustic_comfort"]["weight"]
            total_score += acoustic_score * acoustic_weight
            total_weight += acoustic_weight
            
            # 空气质量舒适度
            if reading.air_quality is not None:
                air_score = self._calculate_air_quality_comfort(reading)
                air_weight = self.comfort_models["air_quality"]["weight"]
                total_score += air_score * air_weight
                total_weight += air_weight
            
            return total_score / total_weight if total_weight > 0 else 0.5
            
        except Exception as e:
            logger.error(f"舒适度计算失败: {str(e)}")
            return 0.5
    
    def _calculate_thermal_comfort(self, reading: EnvironmentReading) -> float:
        """计算热舒适度"""
        model = self.comfort_models["thermal_comfort"]
        
        # 温度舒适度
        temp_diff = abs(reading.temperature - model["optimal_temp"])
        temp_score = max(0, 1.0 - temp_diff / model["temp_tolerance"])
        
        # 湿度舒适度
        humidity_diff = abs(reading.humidity - model["optimal_humidity"])
        humidity_score = max(0, 1.0 - humidity_diff / model["humidity_tolerance"])
        
        # 综合热舒适度
        return (temp_score + humidity_score) / 2.0
    
    def _calculate_visual_comfort(self, reading: EnvironmentReading) -> float:
        """计算视觉舒适度"""
        model = self.comfort_models["visual_comfort"]
        
        light = reading.light_level
        
        if light < model["min_light"]:
            # 光线不足
            return light / model["min_light"]
        elif light <= model["optimal_light"]:
            # 理想范围
            return 1.0
        elif light <= model["max_light"]:
            # 可接受范围
            excess = light - model["optimal_light"]
            max_excess = model["max_light"] - model["optimal_light"]
            return 1.0 - (excess / max_excess) * 0.3
        else:
            # 过亮
            return max(0.2, 1.0 - (light - model["max_light"]) / model["max_light"])
    
    def _calculate_acoustic_comfort(self, reading: EnvironmentReading) -> float:
        """计算声学舒适度"""
        model = self.comfort_models["acoustic_comfort"]
        
        noise = reading.noise_level
        
        if noise <= model["optimal_noise"]:
            return 1.0
        elif noise <= model["max_comfortable"]:
            excess = noise - model["optimal_noise"]
            max_excess = model["max_comfortable"] - model["optimal_noise"]
            return 1.0 - (excess / max_excess) * 0.3
        elif noise <= model["max_tolerable"]:
            excess = noise - model["max_comfortable"]
            max_excess = model["max_tolerable"] - model["max_comfortable"]
            return 0.7 - (excess / max_excess) * 0.5
        else:
            return max(0.1, 0.2 - (noise - model["max_tolerable"]) / 50.0)
    
    def _calculate_air_quality_comfort(self, reading: EnvironmentReading) -> float:
        """计算空气质量舒适度"""
        if reading.air_quality is None:
            return 0.5
        
        model = self.comfort_models["air_quality"]
        aqi = reading.air_quality
        
        if aqi <= model["excellent_threshold"]:
            return 1.0
        elif aqi <= model["good_threshold"]:
            return 0.8
        elif aqi <= model["moderate_threshold"]:
            return 0.6
        else:
            return max(0.2, 0.6 - (aqi - model["moderate_threshold"]) / 100.0)


class SafetyAnalyzer:
    """安全性分析器"""
    
    def __init__(self):
        self.safety_thresholds = self._initialize_safety_thresholds()
    
    def _initialize_safety_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """初始化安全阈值"""
        return {
            "temperature": {
                "extreme_cold": -10,
                "cold": 5,
                "hot": 35,
                "extreme_hot": 45
            },
            "humidity": {
                "very_dry": 20,
                "very_humid": 90
            },
            "noise": {
                "hearing_damage": 85,
                "very_loud": 80,
                "loud": 70
            },
            "air_quality": {
                "unhealthy": 150,
                "very_unhealthy": 200,
                "hazardous": 300
            },
            "uv_index": {
                "high": 6,
                "very_high": 8,
                "extreme": 11
            },
            "wind_speed": {
                "strong": 10,
                "very_strong": 15,
                "dangerous": 25
            }
        }
    
    def calculate_safety_score(self, reading: EnvironmentReading) -> Tuple[float, List[str]]:
        """计算安全评分和警告"""
        try:
            safety_factors = []
            alerts = []
            
            # 温度安全性
            temp_safety, temp_alerts = self._check_temperature_safety(reading.temperature)
            safety_factors.append(temp_safety)
            alerts.extend(temp_alerts)
            
            # 湿度安全性
            humidity_safety, humidity_alerts = self._check_humidity_safety(reading.humidity)
            safety_factors.append(humidity_safety)
            alerts.extend(humidity_alerts)
            
            # 噪音安全性
            noise_safety, noise_alerts = self._check_noise_safety(reading.noise_level)
            safety_factors.append(noise_safety)
            alerts.extend(noise_alerts)
            
            # 空气质量安全性
            if reading.air_quality is not None:
                air_safety, air_alerts = self._check_air_quality_safety(reading.air_quality)
                safety_factors.append(air_safety)
                alerts.extend(air_alerts)
            
            # UV指数安全性
            if reading.uv_index is not None:
                uv_safety, uv_alerts = self._check_uv_safety(reading.uv_index)
                safety_factors.append(uv_safety)
                alerts.extend(uv_alerts)
            
            # 风速安全性
            if reading.wind_speed is not None:
                wind_safety, wind_alerts = self._check_wind_safety(reading.wind_speed)
                safety_factors.append(wind_safety)
                alerts.extend(wind_alerts)
            
            # 计算综合安全评分
            overall_safety = np.mean(safety_factors) if safety_factors else 0.5
            
            return overall_safety, alerts
            
        except Exception as e:
            logger.error(f"安全性分析失败: {str(e)}")
            return 0.5, ["安全性分析异常"]
    
    def _check_temperature_safety(self, temperature: float) -> Tuple[float, List[str]]:
        """检查温度安全性"""
        thresholds = self.safety_thresholds["temperature"]
        alerts = []
        
        if temperature <= thresholds["extreme_cold"]:
            alerts.append(f"极端低温警告: {temperature}°C，存在冻伤风险")
            return 0.1, alerts
        elif temperature <= thresholds["cold"]:
            alerts.append(f"低温警告: {temperature}°C，注意保暖")
            return 0.4, alerts
        elif temperature >= thresholds["extreme_hot"]:
            alerts.append(f"极端高温警告: {temperature}°C，存在中暑风险")
            return 0.1, alerts
        elif temperature >= thresholds["hot"]:
            alerts.append(f"高温警告: {temperature}°C，注意防暑")
            return 0.4, alerts
        else:
            return 1.0, alerts
    
    def _check_humidity_safety(self, humidity: float) -> Tuple[float, List[str]]:
        """检查湿度安全性"""
        thresholds = self.safety_thresholds["humidity"]
        alerts = []
        
        if humidity <= thresholds["very_dry"]:
            alerts.append(f"极度干燥: {humidity}%，可能引起呼吸道不适")
            return 0.6, alerts
        elif humidity >= thresholds["very_humid"]:
            alerts.append(f"极度潮湿: {humidity}%，可能影响散热")
            return 0.6, alerts
        else:
            return 1.0, alerts
    
    def _check_noise_safety(self, noise_level: float) -> Tuple[float, List[str]]:
        """检查噪音安全性"""
        thresholds = self.safety_thresholds["noise"]
        alerts = []
        
        if noise_level >= thresholds["hearing_damage"]:
            alerts.append(f"危险噪音: {noise_level}dB，可能损害听力")
            return 0.2, alerts
        elif noise_level >= thresholds["very_loud"]:
            alerts.append(f"噪音过大: {noise_level}dB，建议使用听力保护")
            return 0.5, alerts
        elif noise_level >= thresholds["loud"]:
            alerts.append(f"噪音较大: {noise_level}dB，可能影响专注")
            return 0.7, alerts
        else:
            return 1.0, alerts
    
    def _check_air_quality_safety(self, air_quality: float) -> Tuple[float, List[str]]:
        """检查空气质量安全性"""
        thresholds = self.safety_thresholds["air_quality"]
        alerts = []
        
        if air_quality >= thresholds["hazardous"]:
            alerts.append(f"空气质量危险: AQI {air_quality}，避免户外活动")
            return 0.1, alerts
        elif air_quality >= thresholds["very_unhealthy"]:
            alerts.append(f"空气质量很不健康: AQI {air_quality}，敏感人群避免外出")
            return 0.3, alerts
        elif air_quality >= thresholds["unhealthy"]:
            alerts.append(f"空气质量不健康: AQI {air_quality}，减少户外活动")
            return 0.5, alerts
        else:
            return 1.0, alerts
    
    def _check_uv_safety(self, uv_index: float) -> Tuple[float, List[str]]:
        """检查UV指数安全性"""
        thresholds = self.safety_thresholds["uv_index"]
        alerts = []
        
        if uv_index >= thresholds["extreme"]:
            alerts.append(f"极强紫外线: UV指数 {uv_index}，避免外出或做好防护")
            return 0.3, alerts
        elif uv_index >= thresholds["very_high"]:
            alerts.append(f"很强紫外线: UV指数 {uv_index}，必须做好防护")
            return 0.5, alerts
        elif uv_index >= thresholds["high"]:
            alerts.append(f"强紫外线: UV指数 {uv_index}，建议防晒")
            return 0.7, alerts
        else:
            return 1.0, alerts
    
    def _check_wind_safety(self, wind_speed: float) -> Tuple[float, List[str]]:
        """检查风速安全性"""
        thresholds = self.safety_thresholds["wind_speed"]
        alerts = []
        
        if wind_speed >= thresholds["dangerous"]:
            alerts.append(f"危险大风: {wind_speed}m/s，避免户外活动")
            return 0.2, alerts
        elif wind_speed >= thresholds["very_strong"]:
            alerts.append(f"强风: {wind_speed}m/s，注意安全")
            return 0.5, alerts
        elif wind_speed >= thresholds["strong"]:
            alerts.append(f"大风: {wind_speed}m/s，小心行走")
            return 0.7, alerts
        else:
            return 1.0, alerts


class AccessibilityAnalyzer:
    """无障碍性分析器"""
    
    def __init__(self):
        self.accessibility_factors = self._initialize_accessibility_factors()
    
    def _initialize_accessibility_factors(self) -> Dict[str, Dict[str, Any]]:
        """初始化无障碍因素"""
        return {
            "visual_accessibility": {
                "min_light": 200,  # 最低照明要求
                "optimal_light": 500,
                "max_glare": 2000,
                "weight": 0.4
            },
            "auditory_accessibility": {
                "max_background_noise": 65,  # 最大背景噪音
                "optimal_noise": 45,
                "weight": 0.3
            },
            "mobility_accessibility": {
                "temperature_comfort": (18, 26),
                "humidity_comfort": (40, 60),
                "wind_limit": 8,
                "weight": 0.3
            }
        }
    
    def calculate_accessibility_score(self, reading: EnvironmentReading, 
                                    environment_type: EnvironmentType) -> Tuple[float, List[str]]:
        """计算无障碍性评分"""
        try:
            accessibility_scores = []
            recommendations = []
            
            # 视觉无障碍性
            visual_score, visual_recs = self._analyze_visual_accessibility(reading)
            accessibility_scores.append(visual_score * self.accessibility_factors["visual_accessibility"]["weight"])
            recommendations.extend(visual_recs)
            
            # 听觉无障碍性
            auditory_score, auditory_recs = self._analyze_auditory_accessibility(reading)
            accessibility_scores.append(auditory_score * self.accessibility_factors["auditory_accessibility"]["weight"])
            recommendations.extend(auditory_recs)
            
            # 行动无障碍性
            mobility_score, mobility_recs = self._analyze_mobility_accessibility(reading, environment_type)
            accessibility_scores.append(mobility_score * self.accessibility_factors["mobility_accessibility"]["weight"])
            recommendations.extend(mobility_recs)
            
            overall_score = sum(accessibility_scores)
            
            return overall_score, recommendations
            
        except Exception as e:
            logger.error(f"无障碍性分析失败: {str(e)}")
            return 0.5, ["无障碍性分析异常"]
    
    def _analyze_visual_accessibility(self, reading: EnvironmentReading) -> Tuple[float, List[str]]:
        """分析视觉无障碍性"""
        factors = self.accessibility_factors["visual_accessibility"]
        recommendations = []
        
        light = reading.light_level
        
        if light < factors["min_light"]:
            score = light / factors["min_light"]
            recommendations.append(f"光线不足({light:.0f} lux)，建议增加照明")
        elif light <= factors["optimal_light"]:
            score = 1.0
        elif light <= factors["max_glare"]:
            excess = light - factors["optimal_light"]
            max_excess = factors["max_glare"] - factors["optimal_light"]
            score = 1.0 - (excess / max_excess) * 0.3
            if score < 0.8:
                recommendations.append(f"光线过强({light:.0f} lux)，建议调节照明或使用遮光")
        else:
            score = 0.4
            recommendations.append(f"强烈眩光({light:.0f} lux)，建议使用遮光设备")
        
        return score, recommendations
    
    def _analyze_auditory_accessibility(self, reading: EnvironmentReading) -> Tuple[float, List[str]]:
        """分析听觉无障碍性"""
        factors = self.accessibility_factors["auditory_accessibility"]
        recommendations = []
        
        noise = reading.noise_level
        
        if noise <= factors["optimal_noise"]:
            score = 1.0
        elif noise <= factors["max_background_noise"]:
            excess = noise - factors["optimal_noise"]
            max_excess = factors["max_background_noise"] - factors["optimal_noise"]
            score = 1.0 - (excess / max_excess) * 0.4
            if score < 0.8:
                recommendations.append(f"背景噪音较高({noise:.0f} dB)，建议使用降噪设备")
        else:
            score = 0.4
            recommendations.append(f"噪音过大({noise:.0f} dB)，严重影响听觉辅助设备效果")
        
        return score, recommendations
    
    def _analyze_mobility_accessibility(self, reading: EnvironmentReading, 
                                      environment_type: EnvironmentType) -> Tuple[float, List[str]]:
        """分析行动无障碍性"""
        factors = self.accessibility_factors["mobility_accessibility"]
        recommendations = []
        scores = []
        
        # 温度舒适度
        temp_range = factors["temperature_comfort"]
        if temp_range[0] <= reading.temperature <= temp_range[1]:
            temp_score = 1.0
        else:
            deviation = min(abs(reading.temperature - temp_range[0]), 
                          abs(reading.temperature - temp_range[1]))
            temp_score = max(0.3, 1.0 - deviation / 10.0)
            if temp_score < 0.7:
                recommendations.append(f"温度不适({reading.temperature:.1f}°C)，可能影响行动能力")
        scores.append(temp_score)
        
        # 湿度舒适度
        humidity_range = factors["humidity_comfort"]
        if humidity_range[0] <= reading.humidity <= humidity_range[1]:
            humidity_score = 1.0
        else:
            deviation = min(abs(reading.humidity - humidity_range[0]), 
                          abs(reading.humidity - humidity_range[1]))
            humidity_score = max(0.4, 1.0 - deviation / 20.0)
            if humidity_score < 0.7:
                recommendations.append(f"湿度不适({reading.humidity:.0f}%)，可能影响舒适度")
        scores.append(humidity_score)
        
        # 风速影响（仅户外）
        if environment_type in [EnvironmentType.OUTDOOR_URBAN, EnvironmentType.OUTDOOR_NATURE]:
            if reading.wind_speed is not None:
                if reading.wind_speed <= factors["wind_limit"]:
                    wind_score = 1.0
                else:
                    wind_score = max(0.2, 1.0 - (reading.wind_speed - factors["wind_limit"]) / 10.0)
                    if wind_score < 0.7:
                        recommendations.append(f"风速过大({reading.wind_speed:.1f} m/s)，可能影响行走稳定性")
                scores.append(wind_score)
        
        overall_score = np.mean(scores) if scores else 0.5
        return overall_score, recommendations


class EnvironmentalIntelligenceEngine:
    """环境智能引擎核心类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化环境智能引擎
        
        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("environmental_intelligence", {}).get("enabled", True)
        
        # 分析器组件
        self.environment_classifier = EnvironmentClassifier()
        self.weather_analyzer = WeatherAnalyzer()
        self.comfort_analyzer = ComfortAnalyzer()
        self.safety_analyzer = SafetyAnalyzer()
        self.accessibility_analyzer = AccessibilityAnalyzer()
        
        # 数据存储
        self.environment_history = defaultdict(deque)  # user_id -> deque of readings
        self.analysis_cache = {}  # 分析结果缓存
        
        # 统计信息
        self.stats = {
            "total_analyses": 0,
            "environment_types": defaultdict(int),
            "weather_conditions": defaultdict(int),
            "safety_alerts": 0,
            "comfort_scores": []
        }
        
        logger.info(f"环境智能引擎初始化完成 - 启用: {self.enabled}")
    
    def analyze_environment(self, user_id: str, reading: EnvironmentReading) -> EnvironmentAnalysis:
        """
        分析环境状况
        
        Args:
            user_id: 用户ID
            reading: 环境读数
            
        Returns:
            环境分析结果
        """
        if not self.enabled:
            return self._create_default_analysis()
        
        try:
            # 获取历史数据
            historical_data = list(self.environment_history[user_id])
            
            # 环境类型分类
            environment_type = self.environment_classifier.classify_environment(reading, historical_data)
            
            # 天气分析
            weather_condition = self.weather_analyzer.analyze_weather(reading, historical_data)
            
            # 舒适度分析
            comfort_score = self.comfort_analyzer.calculate_comfort_score(reading)
            
            # 安全性分析
            safety_score, safety_alerts = self.safety_analyzer.calculate_safety_score(reading)
            
            # 无障碍性分析
            accessibility_score, accessibility_recs = self.accessibility_analyzer.calculate_accessibility_score(
                reading, environment_type
            )
            
            # 确定整体环境状况
            condition = self._determine_environment_condition(comfort_score, safety_score, accessibility_score)
            
            # 生成综合建议
            recommendations = self._generate_recommendations(
                environment_type, weather_condition, comfort_score, 
                safety_score, accessibility_score, accessibility_recs
            )
            
            # 计算置信度
            confidence = self._calculate_analysis_confidence(historical_data, environment_type)
            
            # 创建分析结果
            analysis = EnvironmentAnalysis(
                environment_type=environment_type,
                condition=condition,
                weather=weather_condition,
                comfort_score=comfort_score,
                safety_score=safety_score,
                accessibility_score=accessibility_score,
                recommendations=recommendations,
                alerts=safety_alerts,
                confidence=confidence,
                analysis_time=time.time()
            )
            
            # 存储历史数据
            self._store_reading(user_id, reading)
            
            # 更新统计信息
            self._update_stats(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"环境分析失败: {str(e)}")
            return self._create_default_analysis()
    
    def _create_default_analysis(self) -> EnvironmentAnalysis:
        """创建默认分析结果"""
        return EnvironmentAnalysis(
            environment_type=EnvironmentType.UNKNOWN,
            condition=EnvironmentCondition.MODERATE,
            weather=WeatherCondition.UNKNOWN,
            comfort_score=0.5,
            safety_score=0.5,
            accessibility_score=0.5,
            recommendations=["环境分析暂不可用"],
            alerts=[],
            confidence=0.0,
            analysis_time=time.time()
        )
    
    def _determine_environment_condition(self, comfort_score: float, 
                                       safety_score: float, 
                                       accessibility_score: float) -> EnvironmentCondition:
        """确定环境状况等级"""
        overall_score = (comfort_score + safety_score + accessibility_score) / 3.0
        
        if overall_score >= 0.9:
            return EnvironmentCondition.EXCELLENT
        elif overall_score >= 0.7:
            return EnvironmentCondition.GOOD
        elif overall_score >= 0.5:
            return EnvironmentCondition.MODERATE
        elif overall_score >= 0.3:
            return EnvironmentCondition.POOR
        else:
            return EnvironmentCondition.HAZARDOUS
    
    def _generate_recommendations(self, environment_type: EnvironmentType,
                                weather: WeatherCondition,
                                comfort_score: float,
                                safety_score: float,
                                accessibility_score: float,
                                accessibility_recs: List[str]) -> List[str]:
        """生成环境建议"""
        recommendations = []
        
        # 基于环境类型的建议
        if environment_type == EnvironmentType.OUTDOOR_URBAN:
            recommendations.append("户外城市环境，注意交通安全和空气质量")
        elif environment_type == EnvironmentType.OUTDOOR_NATURE:
            recommendations.append("自然环境，注意天气变化和地形安全")
        elif environment_type == EnvironmentType.INDOOR_OFFICE:
            recommendations.append("办公环境，注意照明和通风")
        
        # 基于天气的建议
        if weather == WeatherCondition.RAINY:
            recommendations.append("雨天，注意防滑和保持干燥")
        elif weather == WeatherCondition.SUNNY:
            recommendations.append("晴天，注意防晒和补水")
        elif weather == WeatherCondition.SNOWY:
            recommendations.append("雪天，注意保暖和防滑")
        
        # 基于舒适度的建议
        if comfort_score < 0.6:
            recommendations.append("环境舒适度较低，建议调整环境设置或更换位置")
        
        # 基于安全性的建议
        if safety_score < 0.7:
            recommendations.append("环境安全性需要关注，请采取相应防护措施")
        
        # 添加无障碍建议
        recommendations.extend(accessibility_recs)
        
        return recommendations[:5]  # 限制建议数量
    
    def _calculate_analysis_confidence(self, historical_data: List[EnvironmentReading], 
                                     environment_type: EnvironmentType) -> float:
        """计算分析置信度"""
        base_confidence = 0.5
        
        # 基于历史数据量的置信度
        data_confidence = min(1.0, len(historical_data) / 20.0)
        
        # 基于环境类型确定性的置信度
        type_confidence = 0.8 if environment_type != EnvironmentType.UNKNOWN else 0.3
        
        # 综合置信度
        overall_confidence = (base_confidence + data_confidence + type_confidence) / 3.0
        
        return min(1.0, overall_confidence)
    
    def _store_reading(self, user_id: str, reading: EnvironmentReading):
        """存储环境读数"""
        self.environment_history[user_id].append(reading)
        
        # 保持最近100个读数
        if len(self.environment_history[user_id]) > 100:
            self.environment_history[user_id].popleft()
    
    def _update_stats(self, analysis: EnvironmentAnalysis):
        """更新统计信息"""
        self.stats["total_analyses"] += 1
        self.stats["environment_types"][analysis.environment_type.value] += 1
        self.stats["weather_conditions"][analysis.weather.value] += 1
        self.stats["safety_alerts"] += len(analysis.alerts)
        self.stats["comfort_scores"].append(analysis.comfort_score)
        
        # 保持最近1000个舒适度评分
        if len(self.stats["comfort_scores"]) > 1000:
            self.stats["comfort_scores"] = self.stats["comfort_scores"][-1000:]
    
    def get_environment_trends(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """获取环境趋势分析"""
        try:
            historical_data = list(self.environment_history[user_id])
            if not historical_data:
                return {"error": "无历史数据"}
            
            # 过滤指定时间范围内的数据
            cutoff_time = time.time() - hours * 3600
            recent_data = [r for r in historical_data if r.timestamp >= cutoff_time]
            
            if not recent_data:
                return {"error": "指定时间范围内无数据"}
            
            # 计算趋势
            trends = {
                "temperature_trend": self._calculate_trend([r.temperature for r in recent_data]),
                "humidity_trend": self._calculate_trend([r.humidity for r in recent_data]),
                "light_trend": self._calculate_trend([r.light_level for r in recent_data]),
                "noise_trend": self._calculate_trend([r.noise_level for r in recent_data]),
                "data_points": len(recent_data),
                "time_range": f"{hours}小时"
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"环境趋势分析失败: {str(e)}")
            return {"error": "趋势分析失败"}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算数值趋势"""
        if len(values) < 2:
            return "stable"
        
        # 计算线性回归斜率
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # 计算相对变化率
        mean_value = np.mean(values)
        relative_slope = slope / mean_value if mean_value != 0 else 0
        
        if relative_slope > 0.05:
            return "increasing"
        elif relative_slope < -0.05:
            return "decreasing"
        else:
            return "stable"
    
    def predict_environment_change(self, user_id: str, hours_ahead: int = 1) -> Dict[str, Any]:
        """预测环境变化"""
        try:
            historical_data = list(self.environment_history[user_id])
            if len(historical_data) < 5:
                return {"error": "数据不足，无法预测"}
            
            # 简单的线性预测
            recent_data = historical_data[-10:]  # 使用最近10个数据点
            
            predictions = {}
            
            # 预测各项指标
            for metric in ["temperature", "humidity", "light_level", "noise_level"]:
                values = [getattr(r, metric) for r in recent_data]
                predicted_value = self._predict_value(values, hours_ahead)
                predictions[f"{metric}_prediction"] = predicted_value
            
            # 预测置信度
            confidence = min(1.0, len(recent_data) / 10.0)
            
            return {
                "predictions": predictions,
                "confidence": confidence,
                "prediction_time": hours_ahead,
                "based_on_points": len(recent_data)
            }
            
        except Exception as e:
            logger.error(f"环境预测失败: {str(e)}")
            return {"error": "预测失败"}
    
    def _predict_value(self, values: List[float], steps_ahead: int) -> float:
        """预测数值"""
        if len(values) < 2:
            return values[-1] if values else 0.0
        
        # 简单线性外推
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        
        # 预测未来值
        future_x = len(values) + steps_ahead - 1
        predicted_value = coeffs[0] * future_x + coeffs[1]
        
        return float(predicted_value)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = dict(self.stats)
        
        # 计算平均舒适度
        if self.stats["comfort_scores"]:
            stats["average_comfort"] = np.mean(self.stats["comfort_scores"])
        else:
            stats["average_comfort"] = 0.0
        
        # 转换defaultdict为普通dict
        stats["environment_types"] = dict(stats["environment_types"])
        stats["weather_conditions"] = dict(stats["weather_conditions"])
        
        # 移除原始评分列表（太大）
        del stats["comfort_scores"]
        
        return {
            "enabled": self.enabled,
            "total_users": len(self.environment_history),
            **stats
        } 