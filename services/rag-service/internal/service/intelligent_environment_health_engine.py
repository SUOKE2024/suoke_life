"""
intelligent_environment_health_engine - 索克生活项目模块
"""

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
import asyncio
import json
import logging
import math

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能环境健康引擎

提供环境健康管理服务，体现"山水养生"理念，包括：
- 环境质量监测与评估
- 地理位置健康因素分析
- 季节性养生指导
- 自然疗法推荐
- 居住环境优化建议
- 环境污染防护策略
"""




class EnvironmentType(str, Enum):
    """环境类型"""
    INDOOR = "indoor"                       # 室内环境
    OUTDOOR = "outdoor"                     # 室外环境
    WORKPLACE = "workplace"                 # 工作环境
    NATURAL = "natural"                     # 自然环境
    URBAN = "urban"                         # 城市环境
    RURAL = "rural"                         # 乡村环境


class AirQualityLevel(str, Enum):
    """空气质量等级"""
    EXCELLENT = "excellent"                 # 优
    GOOD = "good"                          # 良
    MODERATE = "moderate"                  # 轻度污染
    UNHEALTHY_SENSITIVE = "unhealthy_sensitive"  # 中度污染
    UNHEALTHY = "unhealthy"                # 重度污染
    HAZARDOUS = "hazardous"                # 严重污染


class WaterQualityLevel(str, Enum):
    """水质等级"""
    EXCELLENT = "excellent"                 # 优质
    GOOD = "good"                          # 良好
    ACCEPTABLE = "acceptable"              # 可接受
    POOR = "poor"                          # 较差
    UNSAFE = "unsafe"                      # 不安全


class SeasonType(str, Enum):
    """季节类型"""
    SPRING = "spring"                       # 春季
    SUMMER = "summer"                       # 夏季
    AUTUMN = "autumn"                       # 秋季
    WINTER = "winter"                       # 冬季


class SolarTerm(str, Enum):
    """二十四节气"""
    LICHUN = "lichun"                       # 立春
    YUSHUI = "yushui"                       # 雨水
    JINGZHE = "jingzhe"                     # 惊蛰
    CHUNFEN = "chunfen"                     # 春分
    QINGMING = "qingming"                   # 清明
    GUYU = "guyu"                           # 谷雨
    LIXIA = "lixia"                         # 立夏
    XIAOMAN = "xiaoman"                     # 小满
    MANGZHONG = "mangzhong"                 # 芒种
    XIAZHI = "xiazhi"                       # 夏至
    XIAOSHU = "xiaoshu"                     # 小暑
    DASHU = "dashu"                         # 大暑
    LIQIU = "liqiu"                         # 立秋
    CHUSHU = "chushu"                       # 处暑
    BAILU = "bailu"                         # 白露
    QIUFEN = "qiufen"                       # 秋分
    HANLU = "hanlu"                         # 寒露
    SHUANGJIANG = "shuangjiang"             # 霜降
    LIDONG = "lidong"                       # 立冬
    XIAOXUE = "xiaoxue"                     # 小雪
    DAXUE = "daxue"                         # 大雪
    DONGZHI = "dongzhi"                     # 冬至
    XIAOHAN = "xiaohan"                     # 小寒
    DAHAN = "dahan"                         # 大寒


class NaturalTherapyType(str, Enum):
    """自然疗法类型"""
    FOREST_BATHING = "forest_bathing"       # 森林浴
    OCEAN_THERAPY = "ocean_therapy"         # 海洋疗法
    HOT_SPRING = "hot_spring"               # 温泉疗法
    MOUNTAIN_THERAPY = "mountain_therapy"   # 高山疗法
    DESERT_THERAPY = "desert_therapy"       # 沙漠疗法
    LAKE_THERAPY = "lake_therapy"           # 湖泊疗法
    GARDEN_THERAPY = "garden_therapy"       # 园艺疗法
    SUNLIGHT_THERAPY = "sunlight_therapy"   # 日光疗法


class HealthRiskLevel(str, Enum):
    """健康风险等级"""
    LOW = "low"                             # 低风险
    MODERATE = "moderate"                   # 中等风险
    HIGH = "high"                           # 高风险
    VERY_HIGH = "very_high"                 # 极高风险


@dataclass
class EnvironmentData:
    """环境数据"""
    location: str
    environment_type: EnvironmentType
    timestamp: datetime
    
    # 空气质量数据
    aqi: Optional[int] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    o3: Optional[float] = None
    
    # 气象数据
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None
    visibility: Optional[float] = None
    uv_index: Optional[int] = None
    
    # 水质数据
    water_ph: Optional[float] = None
    water_tds: Optional[float] = None
    water_chlorine: Optional[float] = None
    
    # 噪音数据
    noise_level: Optional[float] = None
    
    # 地理数据
    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    vegetation_coverage: Optional[float] = None


@dataclass
class HealthRisk:
    """健康风险"""
    risk_id: str
    risk_type: str
    risk_level: HealthRiskLevel
    description: str
    affected_population: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    prevention_measures: List[str] = field(default_factory=list)
    duration_estimate: Optional[str] = None


@dataclass
class SeasonalAdvice:
    """季节性建议"""
    season: SeasonType
    solar_term: Optional[SolarTerm] = None
    health_focus: List[str] = field(default_factory=list)
    dietary_advice: List[str] = field(default_factory=list)
    exercise_advice: List[str] = field(default_factory=list)
    lifestyle_advice: List[str] = field(default_factory=list)
    tcm_principles: List[str] = field(default_factory=list)
    common_diseases: List[str] = field(default_factory=list)
    prevention_tips: List[str] = field(default_factory=list)


@dataclass
class NaturalTherapy:
    """自然疗法"""
    therapy_id: str
    therapy_type: NaturalTherapyType
    name: str
    description: str
    benefits: List[str] = field(default_factory=list)
    suitable_conditions: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    duration: Optional[str] = None
    frequency: Optional[str] = None
    location_requirements: List[str] = field(default_factory=list)
    preparation_steps: List[str] = field(default_factory=list)
    safety_precautions: List[str] = field(default_factory=list)


@dataclass
class EnvironmentAssessment:
    """环境健康评估"""
    assessment_id: str
    user_id: str
    location: str
    assessment_date: datetime
    environment_data: EnvironmentData
    
    # 评估结果
    air_quality_level: AirQualityLevel
    water_quality_level: Optional[WaterQualityLevel] = None
    overall_health_score: float = 0.0
    
    # 风险评估
    identified_risks: List[HealthRisk] = field(default_factory=list)
    risk_summary: Dict[str, int] = field(default_factory=dict)
    
    # 建议
    immediate_actions: List[str] = field(default_factory=list)
    long_term_recommendations: List[str] = field(default_factory=list)
    natural_therapy_suggestions: List[NaturalTherapy] = field(default_factory=list)
    
    # 季节性指导
    seasonal_advice: Optional[SeasonalAdvice] = None


class EnvironmentMonitor:
    """环境监测器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.air_quality_thresholds = self._load_air_quality_thresholds()
        self.water_quality_standards = self._load_water_quality_standards()
    
    def _load_air_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """加载空气质量阈值"""
        return {
            "pm25": {
                "excellent": 12,
                "good": 35,
                "moderate": 55,
                "unhealthy_sensitive": 150,
                "unhealthy": 250,
                "hazardous": 500
            },
            "pm10": {
                "excellent": 50,
                "good": 150,
                "moderate": 250,
                "unhealthy_sensitive": 350,
                "unhealthy": 420,
                "hazardous": 600
            },
            "aqi": {
                "excellent": 50,
                "good": 100,
                "moderate": 150,
                "unhealthy_sensitive": 200,
                "unhealthy": 300,
                "hazardous": 500
            }
        }
    
    def _load_water_quality_standards(self) -> Dict[str, Dict[str, float]]:
        """加载水质标准"""
        return {
            "ph": {
                "excellent": (7.0, 8.5),
                "good": (6.5, 9.0),
                "acceptable": (6.0, 9.5),
                "poor": (5.5, 10.0),
                "unsafe": (0.0, 5.5)
            },
            "tds": {
                "excellent": 150,
                "good": 300,
                "acceptable": 500,
                "poor": 1000,
                "unsafe": 2000
            }
        }
    
    @trace_operation("environment_monitor.assess_air_quality", SpanKind.INTERNAL)
    async def assess_air_quality(self, environment_data: EnvironmentData) -> AirQualityLevel:
        """评估空气质量"""
        try:
            if environment_data.aqi is not None:
                return self._classify_aqi(environment_data.aqi)
            elif environment_data.pm25 is not None:
                return self._classify_pm25(environment_data.pm25)
            else:
                self.logger.warning("缺少空气质量数据")
                return AirQualityLevel.MODERATE
                
        except Exception as e:
            self.logger.error(f"空气质量评估失败: {e}")
            return AirQualityLevel.MODERATE
    
    def _classify_aqi(self, aqi: int) -> AirQualityLevel:
        """根据AQI分类空气质量"""
        thresholds = self.air_quality_thresholds["aqi"]
        
        if aqi <= thresholds["excellent"]:
            return AirQualityLevel.EXCELLENT
        elif aqi <= thresholds["good"]:
            return AirQualityLevel.GOOD
        elif aqi <= thresholds["moderate"]:
            return AirQualityLevel.MODERATE
        elif aqi <= thresholds["unhealthy_sensitive"]:
            return AirQualityLevel.UNHEALTHY_SENSITIVE
        elif aqi <= thresholds["unhealthy"]:
            return AirQualityLevel.UNHEALTHY
        else:
            return AirQualityLevel.HAZARDOUS
    
    def _classify_pm25(self, pm25: float) -> AirQualityLevel:
        """根据PM2.5分类空气质量"""
        thresholds = self.air_quality_thresholds["pm25"]
        
        if pm25 <= thresholds["excellent"]:
            return AirQualityLevel.EXCELLENT
        elif pm25 <= thresholds["good"]:
            return AirQualityLevel.GOOD
        elif pm25 <= thresholds["moderate"]:
            return AirQualityLevel.MODERATE
        elif pm25 <= thresholds["unhealthy_sensitive"]:
            return AirQualityLevel.UNHEALTHY_SENSITIVE
        elif pm25 <= thresholds["unhealthy"]:
            return AirQualityLevel.UNHEALTHY
        else:
            return AirQualityLevel.HAZARDOUS
    
    @trace_operation("environment_monitor.assess_water_quality", SpanKind.INTERNAL)
    async def assess_water_quality(self, environment_data: EnvironmentData) -> Optional[WaterQualityLevel]:
        """评估水质"""
        try:
            if environment_data.water_ph is None and environment_data.water_tds is None:
                return None
            
            ph_level = self._classify_ph(environment_data.water_ph) if environment_data.water_ph else WaterQualityLevel.GOOD
            tds_level = self._classify_tds(environment_data.water_tds) if environment_data.water_tds else WaterQualityLevel.GOOD
            
            # 取较差的等级
            levels = [ph_level, tds_level]
            level_order = [WaterQualityLevel.EXCELLENT, WaterQualityLevel.GOOD, 
                          WaterQualityLevel.ACCEPTABLE, WaterQualityLevel.POOR, WaterQualityLevel.UNSAFE]
            
            for level in reversed(level_order):
                if level in levels:
                    return level
            
            return WaterQualityLevel.GOOD
            
        except Exception as e:
            self.logger.error(f"水质评估失败: {e}")
            return WaterQualityLevel.GOOD
    
    def _classify_ph(self, ph: float) -> WaterQualityLevel:
        """根据pH值分类水质"""
        standards = self.water_quality_standards["ph"]
        
        if standards["excellent"][0] <= ph <= standards["excellent"][1]:
            return WaterQualityLevel.EXCELLENT
        elif standards["good"][0] <= ph <= standards["good"][1]:
            return WaterQualityLevel.GOOD
        elif standards["acceptable"][0] <= ph <= standards["acceptable"][1]:
            return WaterQualityLevel.ACCEPTABLE
        elif standards["poor"][0] <= ph <= standards["poor"][1]:
            return WaterQualityLevel.POOR
        else:
            return WaterQualityLevel.UNSAFE
    
    def _classify_tds(self, tds: float) -> WaterQualityLevel:
        """根据TDS分类水质"""
        standards = self.water_quality_standards["tds"]
        
        if tds <= standards["excellent"]:
            return WaterQualityLevel.EXCELLENT
        elif tds <= standards["good"]:
            return WaterQualityLevel.GOOD
        elif tds <= standards["acceptable"]:
            return WaterQualityLevel.ACCEPTABLE
        elif tds <= standards["poor"]:
            return WaterQualityLevel.POOR
        else:
            return WaterQualityLevel.UNSAFE


class GeographicHealthAnalyzer:
    """地理健康分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.geographic_health_data = self._load_geographic_health_data()
    
    def _load_geographic_health_data(self) -> Dict[str, Any]:
        """加载地理健康数据"""
        return {
            "altitude_effects": {
                "sea_level": {"benefits": ["稳定气压", "充足氧气"], "risks": ["湿度较高"]},
                "low_altitude": {"benefits": ["适宜居住", "交通便利"], "risks": ["空气污染"]},
                "medium_altitude": {"benefits": ["空气清新", "紫外线适中"], "risks": ["气压变化"]},
                "high_altitude": {"benefits": ["空气纯净", "紫外线强"], "risks": ["缺氧", "紫外线过强"]}
            },
            "climate_zones": {
                "tropical": {"benefits": ["温暖湿润", "植被丰富"], "risks": ["传染病风险", "高温高湿"]},
                "subtropical": {"benefits": ["四季分明", "适宜居住"], "risks": ["梅雨季节", "台风"]},
                "temperate": {"benefits": ["气候温和", "四季变化"], "risks": ["季节性疾病", "温差大"]},
                "cold": {"benefits": ["空气清新", "低过敏原"], "risks": ["严寒", "维生素D缺乏"]}
            },
            "vegetation_benefits": {
                "forest": ["净化空气", "调节湿度", "减少噪音", "心理舒缓"],
                "grassland": ["开阔视野", "空气流通", "运动空间"],
                "wetland": ["调节气候", "净化水质", "生物多样性"],
                "desert": ["干燥气候", "日照充足", "低过敏原"]
            }
        }
    
    @trace_operation("geographic_analyzer.analyze_location_health", SpanKind.INTERNAL)
    async def analyze_location_health(self, environment_data: EnvironmentData) -> Dict[str, Any]:
        """分析地理位置健康因素"""
        try:
            analysis = {
                "altitude_analysis": await self._analyze_altitude_effects(environment_data.altitude),
                "climate_analysis": await self._analyze_climate_effects(environment_data),
                "vegetation_analysis": await self._analyze_vegetation_effects(environment_data.vegetation_coverage),
                "uv_analysis": await self._analyze_uv_effects(environment_data.uv_index),
                "overall_score": 0.0,
                "recommendations": []
            }
            
            # 计算综合评分
            analysis["overall_score"] = await self._calculate_geographic_score(analysis)
            
            # 生成建议
            analysis["recommendations"] = await self._generate_geographic_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"地理健康分析失败: {e}")
            return {"error": str(e)}
    
    async def _analyze_altitude_effects(self, altitude: Optional[float]) -> Dict[str, Any]:
        """分析海拔影响"""
        if altitude is None:
            return {"category": "unknown", "effects": []}
        
        if altitude < 200:
            category = "sea_level"
        elif altitude < 1000:
            category = "low_altitude"
        elif altitude < 3000:
            category = "medium_altitude"
        else:
            category = "high_altitude"
        
        effects = self.geographic_health_data["altitude_effects"].get(category, {})
        
        return {
            "category": category,
            "altitude": altitude,
            "benefits": effects.get("benefits", []),
            "risks": effects.get("risks", [])
        }
    
    async def _analyze_climate_effects(self, environment_data: EnvironmentData) -> Dict[str, Any]:
        """分析气候影响"""
        # 简化的气候分类逻辑
        if environment_data.temperature is None:
            return {"category": "unknown", "effects": []}
        
        temp = environment_data.temperature
        humidity = environment_data.humidity or 50
        
        if temp > 25 and humidity > 70:
            category = "tropical"
        elif temp > 15 and temp <= 25:
            category = "subtropical"
        elif temp > 5 and temp <= 15:
            category = "temperate"
        else:
            category = "cold"
        
        effects = self.geographic_health_data["climate_zones"].get(category, {})
        
        return {
            "category": category,
            "temperature": temp,
            "humidity": humidity,
            "benefits": effects.get("benefits", []),
            "risks": effects.get("risks", [])
        }
    
    async def _analyze_vegetation_effects(self, vegetation_coverage: Optional[float]) -> Dict[str, Any]:
        """分析植被影响"""
        if vegetation_coverage is None:
            return {"category": "unknown", "benefits": []}
        
        if vegetation_coverage > 70:
            category = "forest"
        elif vegetation_coverage > 30:
            category = "grassland"
        elif vegetation_coverage > 10:
            category = "wetland"
        else:
            category = "desert"
        
        benefits = self.geographic_health_data["vegetation_benefits"].get(category, [])
        
        return {
            "category": category,
            "coverage": vegetation_coverage,
            "benefits": benefits
        }
    
    async def _analyze_uv_effects(self, uv_index: Optional[int]) -> Dict[str, Any]:
        """分析紫外线影响"""
        if uv_index is None:
            return {"level": "unknown", "recommendations": []}
        
        if uv_index <= 2:
            level = "low"
            recommendations = ["可以安全户外活动", "注意维生素D补充"]
        elif uv_index <= 5:
            level = "moderate"
            recommendations = ["适度防晒", "避免长时间暴晒"]
        elif uv_index <= 7:
            level = "high"
            recommendations = ["必须防晒", "避免中午户外活动"]
        elif uv_index <= 10:
            level = "very_high"
            recommendations = ["强烈防晒", "尽量室内活动"]
        else:
            level = "extreme"
            recommendations = ["避免户外活动", "全面防护"]
        
        return {
            "level": level,
            "index": uv_index,
            "recommendations": recommendations
        }
    
    async def _calculate_geographic_score(self, analysis: Dict[str, Any]) -> float:
        """计算地理健康评分"""
        score = 70.0  # 基础分
        
        # 海拔加分
        altitude_analysis = analysis.get("altitude_analysis", {})
        if altitude_analysis.get("category") in ["low_altitude", "medium_altitude"]:
            score += 10
        elif altitude_analysis.get("category") == "sea_level":
            score += 5
        
        # 植被加分
        vegetation_analysis = analysis.get("vegetation_analysis", {})
        coverage = vegetation_analysis.get("coverage", 0)
        if coverage > 50:
            score += 15
        elif coverage > 20:
            score += 10
        elif coverage > 10:
            score += 5
        
        # UV指数调整
        uv_analysis = analysis.get("uv_analysis", {})
        uv_level = uv_analysis.get("level", "unknown")
        if uv_level == "moderate":
            score += 5
        elif uv_level in ["high", "very_high", "extreme"]:
            score -= 10
        
        return min(100.0, max(0.0, score))
    
    async def _generate_geographic_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成地理健康建议"""
        recommendations = []
        
        # 基于海拔的建议
        altitude_analysis = analysis.get("altitude_analysis", {})
        if altitude_analysis.get("category") == "high_altitude":
            recommendations.extend([
                "注意高原反应预防",
                "增加水分摄入",
                "避免剧烈运动"
            ])
        
        # 基于植被的建议
        vegetation_analysis = analysis.get("vegetation_analysis", {})
        if vegetation_analysis.get("coverage", 0) > 50:
            recommendations.extend([
                "充分利用自然环境进行森林浴",
                "进行户外有氧运动",
                "享受自然空气净化效果"
            ])
        
        # 基于UV的建议
        uv_analysis = analysis.get("uv_analysis", {})
        recommendations.extend(uv_analysis.get("recommendations", []))
        
        return recommendations


class SeasonalWellnessAdvisor:
    """季节性养生顾问"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seasonal_data = self._load_seasonal_wellness_data()
        self.solar_terms_data = self._load_solar_terms_data()
    
    def _load_seasonal_wellness_data(self) -> Dict[SeasonType, Dict[str, Any]]:
        """加载季节性养生数据"""
        return {
            SeasonType.SPRING: {
                "health_focus": ["养肝", "疏肝理气", "预防过敏", "增强免疫"],
                "dietary_advice": ["多食绿色蔬菜", "适量酸味食物", "少食辛辣", "清淡饮食"],
                "exercise_advice": ["户外运动", "太极拳", "瑜伽", "慢跑"],
                "lifestyle_advice": ["早睡早起", "保持心情舒畅", "适度春捂", "预防感冒"],
                "tcm_principles": ["春养肝", "疏肝解郁", "养阳气"],
                "common_diseases": ["过敏性疾病", "呼吸道感染", "肝气郁结"],
                "prevention_tips": ["注意保暖", "避免过敏原", "调节情绪"]
            },
            SeasonType.SUMMER: {
                "health_focus": ["养心", "清热解暑", "防中暑", "调节情绪"],
                "dietary_advice": ["清淡饮食", "多食苦味", "充足水分", "新鲜果蔬"],
                "exercise_advice": ["游泳", "早晚运动", "避免烈日", "室内运动"],
                "lifestyle_advice": ["晚睡早起", "午休", "防晒", "保持凉爽"],
                "tcm_principles": ["夏养心", "清心火", "养阴液"],
                "common_diseases": ["中暑", "肠胃疾病", "皮肤病", "心血管疾病"],
                "prevention_tips": ["防暑降温", "饮食卫生", "情绪调节"]
            },
            SeasonType.AUTUMN: {
                "health_focus": ["养肺", "润燥", "增强抵抗力", "预防感冒"],
                "dietary_advice": ["润燥食物", "白色食物", "适量辛味", "滋阴润肺"],
                "exercise_advice": ["登山", "慢跑", "太极", "呼吸练习"],
                "lifestyle_advice": ["早睡早起", "保暖", "情绪稳定", "预防干燥"],
                "tcm_principles": ["秋养肺", "润燥养阴", "收敛神气"],
                "common_diseases": ["呼吸道疾病", "皮肤干燥", "情绪低落"],
                "prevention_tips": ["保湿润燥", "适时添衣", "调节情绪"]
            },
            SeasonType.WINTER: {
                "health_focus": ["养肾", "藏精", "保暖", "增强体质"],
                "dietary_advice": ["温补食物", "黑色食物", "适量咸味", "滋阴补肾"],
                "exercise_advice": ["室内运动", "适度锻炼", "避免大汗", "保暖运动"],
                "lifestyle_advice": ["早睡晚起", "保暖", "静养", "避风寒"],
                "tcm_principles": ["冬养肾", "藏精纳气", "温阳补肾"],
                "common_diseases": ["感冒", "关节疾病", "心血管疾病", "抑郁"],
                "prevention_tips": ["保暖防寒", "适度运动", "情绪调节"]
            }
        }
    
    def _load_solar_terms_data(self) -> Dict[SolarTerm, Dict[str, Any]]:
        """加载二十四节气数据"""
        return {
            SolarTerm.LICHUN: {
                "period": "2月3-5日",
                "characteristics": "阳气初生，万物复苏",
                "health_focus": ["疏肝理气", "预防春困"],
                "dietary_advice": ["韭菜", "春笋", "豆芽", "绿茶"],
                "lifestyle_advice": ["早睡早起", "适度春捂", "心情舒畅"]
            },
            SolarTerm.YUSHUI: {
                "period": "2月18-20日",
                "characteristics": "雨水增多，湿气加重",
                "health_focus": ["健脾祛湿", "养护脾胃"],
                "dietary_advice": ["薏米", "红豆", "山药", "茯苓"],
                "lifestyle_advice": ["防湿保暖", "适度运动", "调节情绪"]
            },
            # 可以继续添加其他节气...
        }
    
    @trace_operation("seasonal_advisor.get_seasonal_advice", SpanKind.INTERNAL)
    async def get_seasonal_advice(self, current_date: datetime) -> SeasonalAdvice:
        """获取季节性建议"""
        try:
            season = self._determine_season(current_date)
            solar_term = self._determine_solar_term(current_date)
            
            seasonal_data = self.seasonal_data.get(season, {})
            
            advice = SeasonalAdvice(
                season=season,
                solar_term=solar_term,
                health_focus=seasonal_data.get("health_focus", []),
                dietary_advice=seasonal_data.get("dietary_advice", []),
                exercise_advice=seasonal_data.get("exercise_advice", []),
                lifestyle_advice=seasonal_data.get("lifestyle_advice", []),
                tcm_principles=seasonal_data.get("tcm_principles", []),
                common_diseases=seasonal_data.get("common_diseases", []),
                prevention_tips=seasonal_data.get("prevention_tips", [])
            )
            
            return advice
            
        except Exception as e:
            self.logger.error(f"获取季节性建议失败: {e}")
            return SeasonalAdvice(season=SeasonType.SPRING)
    
    def _determine_season(self, date: datetime) -> SeasonType:
        """确定季节"""
        month = date.month
        
        if month in [3, 4, 5]:
            return SeasonType.SPRING
        elif month in [6, 7, 8]:
            return SeasonType.SUMMER
        elif month in [9, 10, 11]:
            return SeasonType.AUTUMN
        else:
            return SeasonType.WINTER
    
    def _determine_solar_term(self, date: datetime) -> Optional[SolarTerm]:
        """确定节气（简化版本）"""
        # 这里可以实现更精确的节气计算
        month = date.month
        day = date.day
        
        # 简化的节气判断
        if month == 2 and day >= 3:
            return SolarTerm.LICHUN
        elif month == 2 and day >= 18:
            return SolarTerm.YUSHUI
        # 可以继续添加其他节气的判断逻辑
        
        return None


class NaturalTherapyRecommender:
    """自然疗法推荐器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.therapy_database = self._load_therapy_database()
    
    def _load_therapy_database(self) -> Dict[NaturalTherapyType, NaturalTherapy]:
        """加载自然疗法数据库"""
        return {
            NaturalTherapyType.FOREST_BATHING: NaturalTherapy(
                therapy_id="forest_bathing_001",
                therapy_type=NaturalTherapyType.FOREST_BATHING,
                name="森林浴疗法",
                description="在森林环境中进行的自然疗法，通过呼吸新鲜空气、接触自然来改善身心健康",
                benefits=[
                    "降低压力激素水平",
                    "增强免疫系统功能",
                    "改善情绪状态",
                    "降低血压",
                    "提高注意力",
                    "促进睡眠质量"
                ],
                suitable_conditions=[
                    "压力过大",
                    "焦虑抑郁",
                    "免疫力低下",
                    "高血压",
                    "失眠",
                    "注意力不集中"
                ],
                contraindications=[
                    "严重心脏病",
                    "急性感染",
                    "严重过敏体质"
                ],
                duration="30分钟-2小时",
                frequency="每周2-3次",
                location_requirements=[
                    "森林覆盖率>70%",
                    "空气质量良好",
                    "安静环境",
                    "无污染源"
                ],
                preparation_steps=[
                    "选择合适的森林环境",
                    "穿着舒适的服装",
                    "关闭电子设备",
                    "准备充足的水"
                ],
                safety_precautions=[
                    "注意防虫",
                    "避免迷路",
                    "注意天气变化",
                    "结伴同行"
                ]
            ),
            NaturalTherapyType.OCEAN_THERAPY: NaturalTherapy(
                therapy_id="ocean_therapy_001",
                therapy_type=NaturalTherapyType.OCEAN_THERAPY,
                name="海洋疗法",
                description="利用海洋环境的自然因素进行的康复治疗",
                benefits=[
                    "改善呼吸系统功能",
                    "增强皮肤健康",
                    "促进血液循环",
                    "缓解关节疼痛",
                    "提高心肺功能",
                    "减轻压力"
                ],
                suitable_conditions=[
                    "呼吸系统疾病",
                    "皮肤疾病",
                    "关节炎",
                    "循环系统疾病",
                    "压力综合征"
                ],
                contraindications=[
                    "开放性伤口",
                    "严重心脏病",
                    "癫痫",
                    "严重皮肤过敏"
                ],
                duration="30分钟-1小时",
                frequency="每周1-2次",
                location_requirements=[
                    "清洁的海滩",
                    "水质良好",
                    "安全的海域",
                    "适宜的气候"
                ]
            ),
            NaturalTherapyType.HOT_SPRING: NaturalTherapy(
                therapy_id="hot_spring_001",
                therapy_type=NaturalTherapyType.HOT_SPRING,
                name="温泉疗法",
                description="利用天然温泉水的热力和矿物质进行的治疗",
                benefits=[
                    "促进血液循环",
                    "缓解肌肉疲劳",
                    "改善关节功能",
                    "促进新陈代谢",
                    "缓解压力",
                    "改善睡眠"
                ],
                suitable_conditions=[
                    "关节炎",
                    "肌肉疲劳",
                    "循环不良",
                    "压力过大",
                    "失眠",
                    "慢性疼痛"
                ],
                contraindications=[
                    "急性炎症",
                    "严重心脏病",
                    "高血压",
                    "妊娠期",
                    "皮肤感染"
                ],
                duration="15-30分钟",
                frequency="每周1-2次"
            ),
            NaturalTherapyType.MOUNTAIN_THERAPY: NaturalTherapy(
                therapy_id="mountain_therapy_001",
                therapy_type=NaturalTherapyType.MOUNTAIN_THERAPY,
                name="高山疗法",
                description="利用高山环境的清新空气和自然景观进行的康复治疗",
                benefits=[
                    "改善呼吸功能",
                    "增强心肺功能",
                    "提高血氧饱和度",
                    "增强体质",
                    "改善情绪",
                    "增强免疫力"
                ],
                suitable_conditions=[
                    "呼吸系统疾病",
                    "心肺功能不佳",
                    "免疫力低下",
                    "情绪低落",
                    "体质虚弱"
                ],
                contraindications=[
                    "严重心脏病",
                    "严重贫血",
                    "急性感染",
                    "严重高血压"
                ],
                duration="1-3小时",
                frequency="每月1-2次"
            )
        }
    
    @trace_operation("therapy_recommender.recommend_therapies", SpanKind.INTERNAL)
    async def recommend_natural_therapies(
        self,
        user_conditions: List[str],
        environment_data: EnvironmentData,
        user_preferences: Dict[str, Any] = None
    ) -> List[NaturalTherapy]:
        """推荐自然疗法"""
        try:
            suitable_therapies = []
            
            for therapy_type, therapy in self.therapy_database.items():
                # 检查适应症匹配
                if self._check_condition_match(user_conditions, therapy.suitable_conditions):
                    # 检查环境适宜性
                    if await self._check_environment_suitability(environment_data, therapy):
                        # 检查用户偏好
                        if self._check_user_preferences(therapy, user_preferences):
                            suitable_therapies.append(therapy)
            
            # 按适宜度排序
            suitable_therapies.sort(
                key=lambda t: self._calculate_therapy_score(t, user_conditions, environment_data),
                reverse=True
            )
            
            return suitable_therapies[:5]  # 返回前5个推荐
            
        except Exception as e:
            self.logger.error(f"自然疗法推荐失败: {e}")
            return []
    
    def _check_condition_match(self, user_conditions: List[str], suitable_conditions: List[str]) -> bool:
        """检查病症匹配"""
        if not user_conditions:
            return True
        
        # 简化的匹配逻辑
        for condition in user_conditions:
            for suitable in suitable_conditions:
                if condition.lower() in suitable.lower() or suitable.lower() in condition.lower():
                    return True
        return False
    
    async def _check_environment_suitability(self, environment_data: EnvironmentData, therapy: NaturalTherapy) -> bool:
        """检查环境适宜性"""
        # 根据疗法类型检查环境条件
        if therapy.therapy_type == NaturalTherapyType.FOREST_BATHING:
            return (environment_data.vegetation_coverage or 0) > 50
        elif therapy.therapy_type == NaturalTherapyType.OCEAN_THERAPY:
            # 需要海洋环境，这里简化处理
            return environment_data.environment_type == EnvironmentType.NATURAL
        elif therapy.therapy_type == NaturalTherapyType.MOUNTAIN_THERAPY:
            return (environment_data.altitude or 0) > 500
        
        return True
    
    def _check_user_preferences(self, therapy: NaturalTherapy, user_preferences: Dict[str, Any]) -> bool:
        """检查用户偏好"""
        if not user_preferences:
            return True
        
        # 检查用户是否有特定的疗法偏好
        preferred_therapies = user_preferences.get("preferred_therapies", [])
        if preferred_therapies and therapy.therapy_type.value not in preferred_therapies:
            return False
        
        # 检查禁忌症
        contraindications = user_preferences.get("contraindications", [])
        for contraindication in contraindications:
            if contraindication in therapy.contraindications:
                return False
        
        return True
    
    def _calculate_therapy_score(
        self,
        therapy: NaturalTherapy,
        user_conditions: List[str],
        environment_data: EnvironmentData
    ) -> float:
        """计算疗法适宜度评分"""
        score = 0.0
        
        # 基础分
        score += 50.0
        
        # 适应症匹配度
        if user_conditions:
            match_count = 0
            for condition in user_conditions:
                for suitable in therapy.suitable_conditions:
                    if condition.lower() in suitable.lower():
                        match_count += 1
            score += match_count * 10
        
        # 环境适宜度
        if therapy.therapy_type == NaturalTherapyType.FOREST_BATHING:
            score += (environment_data.vegetation_coverage or 0) * 0.5
        elif therapy.therapy_type == NaturalTherapyType.MOUNTAIN_THERAPY:
            if environment_data.altitude and environment_data.altitude > 500:
                score += 20
        
        # 空气质量加分
        if environment_data.aqi and environment_data.aqi < 100:
            score += 15
        
        return score


class IntelligentEnvironmentHealthEngine:
    """智能环境健康引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
        
        # 核心组件
        self.environment_monitor: Optional[EnvironmentMonitor] = None
        self.geographic_analyzer: Optional[GeographicHealthAnalyzer] = None
        self.seasonal_advisor: Optional[SeasonalWellnessAdvisor] = None
        self.therapy_recommender: Optional[NaturalTherapyRecommender] = None
        
        # 数据存储
        self.environment_data: Dict[str, EnvironmentData] = {}
        self.assessments: Dict[str, EnvironmentAssessment] = {}
        self.therapy_sessions: Dict[str, List[NaturalTherapy]] = defaultdict(list)
        
        # 性能优化
        self._assessment_cache = {}
        self._cache_ttl = config.get("cache_ttl", 1800)  # 缓存30分钟
        self._max_cache_size = config.get("max_cache_size", 500)
        
        # 健康状态
        self._is_healthy = True
        self._last_error: Optional[Exception] = None
        self._error_count = 0
        self._max_errors = config.get("max_errors", 10)
        
        # 引擎协同
        self._data_bus = None
        self._engine_manager = None
        
        # 指标收集
        if self.metrics_collector:
            self.metrics_collector.register_counter(
                "environment_assessments_total",
                "Total number of environment assessments conducted"
            )
            self.metrics_collector.register_counter(
                "therapy_recommendations_total",
                "Total number of therapy recommendations generated"
            )
            self.metrics_collector.register_counter(
                "environment_engine_errors_total",
                "Total number of environment engine errors"
            )
            self.metrics_collector.register_histogram(
                "environment_assessment_duration_seconds",
                "Duration of environment assessments in seconds"
            )
            self.metrics_collector.register_gauge(
                "current_air_quality_index",
                "Current air quality index"
            )
    
    async def initialize(self):
        """初始化引擎"""
        try:
            await self._initialize_components()
            self._is_healthy = True
            self._error_count = 0
            self.logger.info("智能环境健康引擎初始化完成")
        except Exception as e:
            self._is_healthy = False
            self._last_error = e
            self._error_count += 1
            self.logger.error(f"环境健康引擎初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 清理缓存
            self._assessment_cache.clear()
            
            # 保存重要数据
            await self._save_critical_data()
            
            self.logger.info("智能环境健康引擎清理完成")
        except Exception as e:
            self.logger.error(f"环境健康引擎清理失败: {e}")
    
    async def _initialize_components(self):
        """初始化组件"""
        try:
            self.environment_monitor = EnvironmentMonitor()
            self.geographic_analyzer = GeographicHealthAnalyzer()
            self.seasonal_advisor = SeasonalWellnessAdvisor()
            self.therapy_recommender = NaturalTherapyRecommender()
            
            # 初始化组件
            await self.environment_monitor.initialize()
            await self.geographic_analyzer.initialize()
            await self.seasonal_advisor.initialize()
            await self.therapy_recommender.initialize()
            
        except Exception as e:
            self.logger.error(f"环境健康引擎组件初始化失败: {e}")
            raise
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查核心组件
            if not all([
                self.environment_monitor, 
                self.geographic_analyzer, 
                self.seasonal_advisor, 
                self.therapy_recommender
            ]):
                return False
            
            # 检查错误计数
            if self._error_count >= self._max_errors:
                return False
            
            # 执行简单的功能测试
            test_location = {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "city": "北京"
            }
            
            # 测试环境监测功能
            env_data = await self.environment_monitor.collect_environment_data(test_location)
            if not env_data:
                return False
            
            # 测试地理分析功能
            geo_analysis = await self.geographic_analyzer.analyze_geographic_health(test_location)
            if not geo_analysis:
                return False
            
            self._is_healthy = True
            return True
            
        except Exception as e:
            self._is_healthy = False
            self._last_error = e
            self._error_count += 1
            self.logger.error(f"环境健康引擎健康检查失败: {e}")
            return False
    
    def set_data_bus(self, data_bus):
        """设置数据总线"""
        self._data_bus = data_bus
        
        # 订阅相关数据
        if data_bus:
            data_bus.subscribe("weather_data", self._on_weather_data_updated)
            data_bus.subscribe("air_quality_data", self._on_air_quality_updated)
            data_bus.subscribe("user_location", self._on_user_location_updated)
    
    def set_engine_manager(self, engine_manager):
        """设置引擎管理器"""
        self._engine_manager = engine_manager
    
    async def _on_weather_data_updated(self, topic: str, data: Any):
        """处理天气数据更新"""
        try:
            if isinstance(data, dict) and "location" in data:
                location = data["location"]
                
                # 更新环境数据
                if location in self.environment_data:
                    env_data = self.environment_data[location]
                    env_data.weather_data = data.get("weather", {})
                    
                    # 重新评估环境健康
                    await self._reassess_environment_health(location)
                    
        except Exception as e:
            self.logger.error(f"处理天气数据更新失败: {e}")
    
    async def _on_air_quality_updated(self, topic: str, data: Any):
        """处理空气质量数据更新"""
        try:
            if isinstance(data, dict) and "location" in data:
                location = data["location"]
                aqi = data.get("aqi", 0)
                
                # 更新指标
                if self.metrics_collector:
                    self.metrics_collector.set_gauge("current_air_quality_index", aqi)
                
                # 如果空气质量恶化，发送警告
                if aqi > 150:  # 不健康级别
                    await self._send_air_quality_warning(location, aqi)
                    
        except Exception as e:
            self.logger.error(f"处理空气质量数据更新失败: {e}")
    
    async def _on_user_location_updated(self, topic: str, data: Any):
        """处理用户位置更新"""
        try:
            if isinstance(data, dict) and "user_id" in data:
                user_id = data["user_id"]
                location = data.get("location", {})
                
                # 为新位置生成环境健康建议
                if location:
                    await self._generate_location_based_recommendations(user_id, location)
                    
        except Exception as e:
            self.logger.error(f"处理用户位置更新失败: {e}")
    
    async def _reassess_environment_health(self, location: str):
        """重新评估环境健康"""
        try:
            if location in self.environment_data:
                env_data = self.environment_data[location]
                
                # 重新进行环境评估
                assessment = await self.assess_environment_health(location, env_data.__dict__)
                
                # 发布更新通知
                if self._data_bus:
                    await self._data_bus.publish_data(
                        f"environment_assessment_updated:{location}",
                        {
                            "location": location,
                            "assessment": assessment.__dict__,
                            "updated_at": datetime.now().isoformat()
                        }
                    )
                    
        except Exception as e:
            self.logger.error(f"重新评估环境健康失败: {e}")
    
    async def _send_air_quality_warning(self, location: str, aqi: int):
        """发送空气质量警告"""
        try:
            warning_message = {
                "type": "air_quality_warning",
                "location": location,
                "aqi": aqi,
                "level": "unhealthy" if aqi < 200 else "hazardous",
                "recommendations": [
                    "减少户外活动",
                    "佩戴防护口罩",
                    "关闭门窗",
                    "使用空气净化器"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            if self._data_bus:
                await self._data_bus.publish_data("air_quality_warning", warning_message)
                
        except Exception as e:
            self.logger.error(f"发送空气质量警告失败: {e}")
    
    async def _generate_location_based_recommendations(self, user_id: str, location: Dict[str, Any]):
        """生成基于位置的建议"""
        try:
            # 收集位置环境数据
            env_data = await self.environment_monitor.collect_environment_data(location)
            
            # 进行地理健康分析
            geo_analysis = await self.geographic_analyzer.analyze_geographic_health(location)
            
            # 生成建议
            recommendations = []
            
            # 基于海拔的建议
            altitude = location.get("altitude", 0)
            if altitude > 2500:
                recommendations.extend([
                    "注意高原反应，适当休息",
                    "增加水分摄入",
                    "避免剧烈运动"
                ])
            
            # 基于气候的建议
            climate = geo_analysis.get("climate_type")
            if climate == "tropical":
                recommendations.extend([
                    "注意防暑降温",
                    "及时补充电解质",
                    "避免长时间暴晒"
                ])
            
            # 发布位置建议
            if recommendations and self._data_bus:
                await self._data_bus.publish_data(
                    f"location_health_recommendations:{user_id}",
                    {
                        "user_id": user_id,
                        "location": location,
                        "recommendations": recommendations,
                        "generated_at": datetime.now().isoformat()
                    }
                )
                
        except Exception as e:
            self.logger.error(f"生成基于位置的建议失败: {e}")
    
    async def _save_critical_data(self):
        """保存关键数据"""
        try:
            critical_data = {
                "environment_data_count": len(self.environment_data),
                "assessments_count": len(self.assessments),
                "therapy_sessions_count": sum(len(sessions) for sessions in self.therapy_sessions.values()),
                "total_locations": len(self.environment_data),
                "last_save": datetime.now().isoformat()
            }
            
            self.logger.info(f"保存环境健康引擎关键数据: {critical_data}")
            
        except Exception as e:
            self.logger.error(f"保存关键数据失败: {e}")
    
    @trace_operation("environment_engine.assess_health", SpanKind.INTERNAL)
    async def assess_environment_health(
        self,
        location: str,
        environment_data: Dict[str, Any]
    ) -> EnvironmentAssessment:
        """评估环境健康"""
        
        start_time = datetime.now()
        
        try:
            # 检查缓存
            cache_key = f"env_assessment_{location}_{hash(str(environment_data))}"
            if cache_key in self._assessment_cache:
                cached_result = self._assessment_cache[cache_key]
                if (datetime.now() - cached_result["timestamp"]).seconds < self._cache_ttl:
                    self.logger.info(f"从缓存返回位置 {location} 的环境评估")
                    return cached_result["assessment"]
            
            # 创建环境数据对象
            env_data = EnvironmentData(
                location=location,
                timestamp=datetime.now(),
                air_quality=environment_data.get("air_quality", {}),
                water_quality=environment_data.get("water_quality", {}),
                noise_level=environment_data.get("noise_level", 0),
                temperature=environment_data.get("temperature", 20),
                humidity=environment_data.get("humidity", 50),
                uv_index=environment_data.get("uv_index", 5),
                vegetation_coverage=environment_data.get("vegetation_coverage", 0.3),
                altitude=environment_data.get("altitude", 0)
            )
            
            # 保存环境数据
            self.environment_data[location] = env_data
            
            # 进行环境监测
            air_quality_assessment = await self.environment_monitor.assess_air_quality(env_data.air_quality)
            water_quality_assessment = await self.environment_monitor.assess_water_quality(env_data.water_quality)
            
            # 进行地理健康分析
            geographic_analysis = await self.geographic_analyzer.analyze_geographic_health({
                "latitude": environment_data.get("latitude", 0),
                "longitude": environment_data.get("longitude", 0),
                "altitude": env_data.altitude,
                "vegetation_coverage": env_data.vegetation_coverage
            })
            
            # 获取季节性建议
            seasonal_advice = await self.seasonal_advisor.get_seasonal_advice(datetime.now())
            
            # 推荐自然疗法
            therapy_recommendations = await self.therapy_recommender.recommend_natural_therapies(
                env_data, geographic_analysis
            )
            
            # 识别健康风险
            health_risks = await self._identify_health_risks(env_data)
            
            # 计算综合评分
            overall_score = await self._calculate_overall_score(
                air_quality_assessment, water_quality_assessment, geographic_analysis
            )
            
            # 创建评估结果
            assessment = EnvironmentAssessment(
                location=location,
                assessment_date=datetime.now(),
                overall_score=overall_score,
                air_quality_level=air_quality_assessment.get("level", "unknown"),
                water_quality_level=water_quality_assessment.get("level", "unknown"),
                health_risks=health_risks,
                seasonal_advice=seasonal_advice,
                therapy_recommendations=therapy_recommendations,
                geographic_factors=geographic_analysis
            )
            
            # 保存评估结果
            self.assessments[location] = assessment
            
            # 缓存结果
            if len(self._assessment_cache) >= self._max_cache_size:
                oldest_key = min(self._assessment_cache.keys(), 
                               key=lambda k: self._assessment_cache[k]["timestamp"])
                del self._assessment_cache[oldest_key]
            
            self._assessment_cache[cache_key] = {
                "assessment": assessment,
                "timestamp": datetime.now()
            }
            
            # 记录指标
            processing_time = (datetime.now() - start_time).total_seconds()
            if self.metrics_collector:
                self.metrics_collector.increment_counter("environment_assessments_total")
                self.metrics_collector.record_histogram(
                    "environment_assessment_duration_seconds",
                    processing_time
                )
            
            # 发布评估完成事件
            if self._data_bus:
                await self._data_bus.publish_data(
                    f"environment_assessment_completed:{location}",
                    {
                        "location": location,
                        "assessment_id": f"env_assess_{location}_{int(start_time.timestamp())}",
                        "overall_score": overall_score,
                        "air_quality_level": assessment.air_quality_level,
                        "health_risks_count": len(health_risks),
                        "completed_at": datetime.now().isoformat()
                    }
                )
            
            self.logger.info(f"位置 {location} 环境健康评估完成，耗时 {processing_time:.2f}秒")
            return assessment
            
        except Exception as e:
            self._error_count += 1
            self._last_error = e
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("environment_engine_errors_total")
            
            self.logger.error(f"环境健康评估失败: {e}")
            raise
    
    async def _identify_health_risks(self, env_data: EnvironmentData) -> List[HealthRisk]:
        """识别健康风险"""
        risks = []
        
        # 空气质量风险
        aqi = env_data.air_quality.get("aqi", 0)
        if aqi > 100:
            risk_level = "high" if aqi > 200 else "moderate"
            risks.append(HealthRisk(
                risk_type="air_pollution",
                severity=risk_level,
                description=f"空气质量指数 {aqi}，可能影响呼吸系统健康",
                recommendations=["减少户外活动", "佩戴防护口罩"]
            ))
        
        # 紫外线风险
        if env_data.uv_index > 7:
            risks.append(HealthRisk(
                risk_type="uv_exposure",
                severity="moderate",
                description=f"紫外线指数 {env_data.uv_index}，紫外线强烈",
                recommendations=["使用防晒霜", "避免长时间暴晒", "佩戴遮阳帽"]
            ))
        
        # 噪音风险
        if env_data.noise_level > 70:
            risks.append(HealthRisk(
                risk_type="noise_pollution",
                severity="moderate",
                description=f"噪音水平 {env_data.noise_level}dB，可能影响听力和睡眠",
                recommendations=["使用耳塞", "选择安静环境休息"]
            ))
        
        return risks
    
    async def _calculate_overall_score(
        self,
        air_quality: Dict[str, Any],
        water_quality: Dict[str, Any],
        geographic_analysis: Dict[str, Any]
    ) -> float:
        """计算综合评分"""
        
        # 空气质量评分 (40%)
        air_score = air_quality.get("score", 50) / 100.0
        
        # 水质评分 (20%)
        water_score = water_quality.get("score", 50) / 100.0
        
        # 地理环境评分 (40%)
        geo_score = geographic_analysis.get("health_score", 50) / 100.0
        
        # 加权计算
        overall_score = (air_score * 0.4 + water_score * 0.2 + geo_score * 0.4) * 100
        
        return round(overall_score, 1)
    
    async def get_health_recommendations(self, user_id: str) -> Dict[str, Any]:
        """获取健康建议"""
        try:
            recommendations = {
                "environment": [],
                "seasonal": [],
                "therapy": [],
                "lifestyle": []
            }
            
            # 获取用户最近的环境评估
            user_assessments = [
                assessment for assessment in self.assessments.values()
                if assessment.assessment_date >= datetime.now() - timedelta(days=7)
            ]
            
            if user_assessments:
                latest_assessment = max(user_assessments, key=lambda x: x.assessment_date)
                
                # 环境建议
                for risk in latest_assessment.health_risks:
                    recommendations["environment"].extend(risk.recommendations)
                
                # 季节性建议
                if latest_assessment.seasonal_advice:
                    recommendations["seasonal"] = latest_assessment.seasonal_advice.get("recommendations", [])
                
                # 自然疗法建议
                for therapy in latest_assessment.therapy_recommendations:
                    recommendations["therapy"].append({
                        "therapy_type": therapy.therapy_type,
                        "description": therapy.description,
                        "benefits": therapy.benefits
                    })
            
            # 从其他引擎获取协同建议
            if self._engine_manager:
                try:
                    nutrition_response = await self._engine_manager.execute_request(
                        engine_type="nutrition",
                        method_name="get_collaborative_recommendations",
                        user_id=user_id
                    )
                    if nutrition_response.success:
                        nutrition_recs = nutrition_response.result.get("environment", [])
                        recommendations["lifestyle"].extend(nutrition_recs)
                except Exception as e:
                    self.logger.warning(f"获取营养协同建议失败: {e}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"获取健康建议失败: {e}")
            return {"error": str(e)}


def initialize_environment_health_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentEnvironmentHealthEngine:
    """初始化智能环境健康引擎"""
    return IntelligentEnvironmentHealthEngine(config, metrics_collector)


# 全局引擎实例
_environment_health_engine: Optional[IntelligentEnvironmentHealthEngine] = None


def get_environment_health_engine() -> Optional[IntelligentEnvironmentHealthEngine]:
    """获取全局环境健康引擎实例"""
    return _environment_health_engine 