"""
食农结合服务模块
实现食疗与农业结合的健康管理功能
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..domain.models import ConstitutionType

logger = logging.getLogger(__name__)


class SeasonType(Enum):
    """季节类型"""

    SPRING = "spring"  # 春季
    SUMMER = "summer"  # 夏季
    AUTUMN = "autumn"  # 秋季
    WINTER = "winter"  # 冬季


class FoodCategory(Enum):
    """食物类别"""

    GRAINS = "grains"  # 谷物类
    VEGETABLES = "vegetables"  # 蔬菜类
    FRUITS = "fruits"  # 水果类
    PROTEINS = "proteins"  # 蛋白质类
    HERBS = "herbs"  # 药食同源类
    DAIRY = "dairy"  # 乳制品类
    NUTS_SEEDS = "nuts_seeds"  # 坚果种子类
    BEVERAGES = "beverages"  # 饮品类


class FoodNature(Enum):
    """食物性质"""

    HOT = "hot"  # 热性
    WARM = "warm"  # 温性
    NEUTRAL = "neutral"  # 平性
    COOL = "cool"  # 凉性
    COLD = "cold"  # 寒性


class FoodTaste(Enum):
    """食物味道"""

    SWEET = "sweet"  # 甘味
    SOUR = "sour"  # 酸味
    BITTER = "bitter"  # 苦味
    SPICY = "spicy"  # 辛味
    SALTY = "salty"  # 咸味


class AgricultureType(Enum):
    """农业类型"""

    ORGANIC = "organic"  # 有机农业
    TRADITIONAL = "traditional"  # 传统农业
    HYDROPONIC = "hydroponic"  # 水培农业
    GREENHOUSE = "greenhouse"  # 温室农业
    PERMACULTURE = "permaculture"  # 永续农业


class CultivationMethod(Enum):
    """种植方法"""

    SOIL_BASED = "soil_based"  # 土壤种植
    SOILLESS = "soilless"  # 无土栽培
    AQUAPONICS = "aquaponics"  # 鱼菜共生
    VERTICAL = "vertical"  # 垂直农业
    COMPANION = "companion"  # 伴生种植


@dataclass
class NutritionalInfo:
    """营养信息"""

    calories_per_100g: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    vitamins: Dict[str, float]
    minerals: Dict[str, float]
    antioxidants: List[str]
    glycemic_index: Optional[int] = None


@dataclass
class FoodItem:
    """食物项目"""

    food_id: str
    name: str
    category: FoodCategory
    nature: FoodNature
    taste: FoodTaste
    meridian_tropism: List[str]  # 归经
    nutritional_info: NutritionalInfo
    health_benefits: List[str]
    contraindications: List[str]
    seasonal_availability: List[SeasonType]
    preparation_methods: List[str]
    storage_tips: str
    origin_region: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FoodTherapyPlan:
    """食疗方案"""

    plan_id: str
    name: str
    target_constitution: ConstitutionType
    target_symptoms: List[str]
    duration_days: int
    daily_meals: Dict[str, List[str]]  # 早中晚餐食物
    preparation_instructions: List[str]
    expected_benefits: List[str]
    precautions: List[str]
    progress_indicators: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgriculturalProduct:
    """农产品"""

    product_id: str
    name: str
    variety: str
    agriculture_type: AgricultureType
    cultivation_method: CultivationMethod
    growing_region: str
    planting_date: datetime
    harvest_date: Optional[datetime]
    quality_grade: str
    certification: List[str]  # 认证信息
    traceability_code: str
    nutritional_analysis: NutritionalInfo
    pesticide_residue: Dict[str, float]
    heavy_metals: Dict[str, float]
    supplier_info: Dict[str, Any]
    price_per_kg: float
    availability_status: str


@dataclass
class NutritionalAnalysis:
    """营养分析"""

    analysis_id: str
    user_id: str
    constitution_type: ConstitutionType
    current_symptoms: List[str]
    dietary_preferences: List[str]
    allergies: List[str]
    daily_calorie_needs: float
    macro_nutrient_ratios: Dict[str, float]
    micro_nutrient_needs: Dict[str, float]
    recommended_foods: List[str]
    foods_to_avoid: List[str]
    meal_timing_suggestions: Dict[str, str]
    hydration_needs: float
    supplement_recommendations: List[str]
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class PlantingGuidance:
    """种植指导"""

    guidance_id: str
    crop_name: str
    variety: str
    region: str
    season: SeasonType
    soil_requirements: Dict[str, Any]
    climate_conditions: Dict[str, Any]
    planting_schedule: Dict[str, str]
    care_instructions: List[str]
    pest_management: List[str]
    harvest_timing: str
    yield_expectations: Dict[str, float]
    quality_optimization: List[str]
    post_harvest_handling: List[str]
    created_at: datetime = field(default_factory=datetime.now)


class FoodAgricultureService:
    """
    食农结合服务

    提供食疗推荐、农产品管理、营养分析等功能
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # 食物数据库
        self.food_database: Dict[str, FoodItem] = {}

        # 食疗方案库
        self.therapy_plans: Dict[str, FoodTherapyPlan] = {}

        # 农产品数据库
        self.agricultural_products: Dict[str, AgriculturalProduct] = {}

        # 种植指导库
        self.planting_guidance: Dict[str, PlantingGuidance] = {}

        # 体质-食物映射
        self.constitution_food_mapping = self._initialize_constitution_food_mapping()

        # 症状-食疗映射
        self.symptom_therapy_mapping = self._initialize_symptom_therapy_mapping()

        # 季节性食材推荐
        self.seasonal_recommendations = self._initialize_seasonal_recommendations()

        # 初始化数据
        self._initialize_food_database()
        self._initialize_therapy_plans()
        self._initialize_agricultural_products()
        self._initialize_planting_guidance()

        logger.info("食农结合服务初始化完成")

    def _initialize_constitution_food_mapping(
        self,
    ) -> Dict[ConstitutionType, Dict[str, List[str]]]:
        """初始化体质-食物映射"""
        mapping = {
            ConstitutionType.BALANCED: {
                "recommended": ["小米", "山药", "莲子", "百合", "银耳", "苹果", "梨"],
                "beneficial": ["五谷杂粮", "时令蔬菜", "新鲜水果", "优质蛋白"],
                "avoid": ["过于寒凉", "过于燥热", "过度加工食品"],
            },
            ConstitutionType.QI_DEFICIENCY: {
                "recommended": [
                    "人参",
                    "黄芪",
                    "大枣",
                    "山药",
                    "小米",
                    "糯米",
                    "牛肉",
                    "鸡肉",
                ],
                "beneficial": ["补气食材", "温性食物", "易消化食品", "营养丰富食物"],
                "avoid": ["生冷食物", "难消化食品", "过度辛辣", "空腹运动"],
            },
            ConstitutionType.YANG_DEFICIENCY: {
                "recommended": [
                    "羊肉",
                    "韭菜",
                    "生姜",
                    "肉桂",
                    "核桃",
                    "栗子",
                    "红枣",
                    "桂圆",
                ],
                "beneficial": ["温热性食物", "补阳食材", "高热量食品", "温性香料"],
                "avoid": ["寒凉食物", "生冷饮品", "苦寒药物", "过度清淡"],
            },
            ConstitutionType.YIN_DEFICIENCY: {
                "recommended": [
                    "银耳",
                    "百合",
                    "枸杞",
                    "沙参",
                    "麦冬",
                    "梨",
                    "甘蔗",
                    "蜂蜜",
                ],
                "beneficial": ["滋阴食材", "润燥食物", "清淡食品", "富含水分食物"],
                "avoid": ["辛辣食物", "煎炸食品", "温燥食材", "过度温补"],
            },
            ConstitutionType.PHLEGM_DAMPNESS: {
                "recommended": [
                    "薏米",
                    "冬瓜",
                    "白萝卜",
                    "陈皮",
                    "茯苓",
                    "荷叶",
                    "山楂",
                    "柠檬",
                ],
                "beneficial": ["化痰食材", "利湿食物", "清淡食品", "高纤维食物"],
                "avoid": ["油腻食物", "甜腻食品", "生冷食物", "过咸食品"],
            },
            ConstitutionType.DAMP_HEAT: {
                "recommended": [
                    "绿豆",
                    "苦瓜",
                    "冬瓜",
                    "薏米",
                    "莲子心",
                    "菊花",
                    "金银花",
                    "竹叶",
                ],
                "beneficial": ["清热食材", "利湿食物", "苦味食品", "清淡食物"],
                "avoid": ["辛辣食物", "油腻食品", "甜腻食物", "温热食材"],
            },
            ConstitutionType.BLOOD_STASIS: {
                "recommended": [
                    "山楂",
                    "红花",
                    "桃仁",
                    "当归",
                    "川芎",
                    "红糖",
                    "黑木耳",
                    "洋葱",
                ],
                "beneficial": ["活血食材", "行气食物", "温性食品", "富含维E食物"],
                "avoid": ["寒凉食物", "油腻食品", "过咸食物", "凝血食材"],
            },
            ConstitutionType.QI_STAGNATION: {
                "recommended": [
                    "柑橘",
                    "佛手",
                    "玫瑰花",
                    "茉莉花",
                    "薄荷",
                    "柠檬",
                    "橙子",
                    "柚子",
                ],
                "beneficial": ["理气食材", "芳香食物", "疏肝食品", "清香食物"],
                "avoid": ["油腻食物", "难消化食品", "过甜食物", "刺激性食物"],
            },
            ConstitutionType.ALLERGIC: {
                "recommended": [
                    "灵芝",
                    "银耳",
                    "百合",
                    "蜂蜜",
                    "胡萝卜",
                    "南瓜",
                    "紫苏",
                    "生姜",
                ],
                "beneficial": ["抗过敏食材", "增强免疫食物", "温和食品", "天然食材"],
                "avoid": ["易过敏食物", "添加剂食品", "刺激性食物", "发物"],
            },
        }
        return mapping

    def _initialize_symptom_therapy_mapping(self) -> Dict[str, Dict[str, Any]]:
        """初始化症状-食疗映射"""
        mapping = {
            "乏力": {
                "primary_foods": ["人参", "黄芪", "大枣", "山药", "小米"],
                "therapy_type": "补气养血",
                "preparation": "煮粥、炖汤、泡茶",
                "duration": "2-4周",
                "frequency": "每日1-2次",
            },
            "怕冷": {
                "primary_foods": ["生姜", "肉桂", "羊肉", "韭菜", "核桃"],
                "therapy_type": "温阳散寒",
                "preparation": "炖煮、热饮、温食",
                "duration": "1-3个月",
                "frequency": "每日2-3次",
            },
            "口干": {
                "primary_foods": ["梨", "甘蔗", "蜂蜜", "银耳", "百合"],
                "therapy_type": "滋阴润燥",
                "preparation": "生食、炖汤、泡水",
                "duration": "2-6周",
                "frequency": "每日多次",
            },
            "失眠": {
                "primary_foods": ["酸枣仁", "龙眼肉", "百合", "莲子", "小麦"],
                "therapy_type": "安神定志",
                "preparation": "煮粥、泡茶、炖汤",
                "duration": "4-8周",
                "frequency": "晚餐后1次",
            },
            "便秘": {
                "primary_foods": ["香蕉", "蜂蜜", "芝麻", "核桃", "菠菜"],
                "therapy_type": "润肠通便",
                "preparation": "生食、榨汁、炒制",
                "duration": "1-2周",
                "frequency": "每日1-2次",
            },
            "腹胀": {
                "primary_foods": ["山楂", "陈皮", "萝卜", "生姜", "薄荷"],
                "therapy_type": "理气消胀",
                "preparation": "泡茶、煮汤、生食",
                "duration": "1-3周",
                "frequency": "餐后1次",
            },
            "头痛": {
                "primary_foods": ["菊花", "薄荷", "川芎", "白芷", "天麻"],
                "therapy_type": "疏风止痛",
                "preparation": "泡茶、煮汤、炖制",
                "duration": "2-4周",
                "frequency": "每日2次",
            },
            "易感冒": {
                "primary_foods": ["黄芪", "党参", "枸杞", "大枣", "生姜"],
                "therapy_type": "益气固表",
                "preparation": "煮汤、泡茶、炖制",
                "duration": "3-6个月",
                "frequency": "每日1次",
            },
        }
        return mapping

    def _initialize_seasonal_recommendations(
        self,
    ) -> Dict[SeasonType, Dict[str, List[str]]]:
        """初始化季节性食材推荐"""
        recommendations = {
            SeasonType.SPRING: {
                "vegetables": [
                    "韭菜",
                    "菠菜",
                    "芹菜",
                    "豆苗",
                    "春笋",
                    "荠菜",
                    "马兰头",
                ],
                "fruits": ["草莓", "樱桃", "杏", "李子", "枇杷"],
                "herbs": ["柴胡", "薄荷", "桑叶", "菊花", "蒲公英"],
                "grains": ["小麦", "大麦", "燕麦"],
                "principles": ["疏肝理气", "升发阳气", "清热解毒"],
            },
            SeasonType.SUMMER: {
                "vegetables": [
                    "冬瓜",
                    "苦瓜",
                    "丝瓜",
                    "黄瓜",
                    "茄子",
                    "番茄",
                    "绿豆芽",
                ],
                "fruits": ["西瓜", "甜瓜", "桃子", "李子", "杨梅", "荔枝"],
                "herbs": ["金银花", "菊花", "薄荷", "荷叶", "竹叶"],
                "grains": ["绿豆", "薏米", "小米"],
                "principles": ["清热解暑", "利湿消肿", "养心安神"],
            },
            SeasonType.AUTUMN: {
                "vegetables": ["白萝卜", "莲藕", "山药", "百合", "银耳", "梨", "柿子"],
                "fruits": ["苹果", "梨", "柿子", "石榴", "柚子", "橘子"],
                "herbs": ["沙参", "麦冬", "玉竹", "石斛", "枸杞"],
                "grains": ["糯米", "粳米", "芝麻"],
                "principles": ["滋阴润燥", "养肺护肤", "收敛固涩"],
            },
            SeasonType.WINTER: {
                "vegetables": ["白菜", "萝卜", "土豆", "胡萝卜", "洋葱", "韭黄"],
                "fruits": ["橘子", "柚子", "苹果", "梨", "香蕉"],
                "herbs": ["当归", "黄芪", "党参", "枸杞", "红枣"],
                "grains": ["黑米", "红豆", "黑豆", "核桃"],
                "principles": ["温阳补肾", "养血安神", "固精保元"],
            },
        }
        return recommendations

    def _initialize_food_database(self):
        """初始化食物数据库"""
        foods = [
            FoodItem(
                food_id="F001",
                name="山药",
                category=FoodCategory.VEGETABLES,
                nature=FoodNature.NEUTRAL,
                taste=FoodTaste.SWEET,
                meridian_tropism=["脾", "肺", "肾"],
                nutritional_info=NutritionalInfo(
                    calories_per_100g=56,
                    protein=1.9,
                    carbohydrates=12.4,
                    fat=0.2,
                    fiber=0.8,
                    vitamins={"A": 3, "C": 4, "B1": 0.05, "B2": 0.02},
                    minerals={"Ca": 16, "P": 34, "Fe": 0.3, "K": 213},
                    antioxidants=["多酚", "黏液质", "薯蓣皂苷"],
                ),
                health_benefits=["健脾益胃", "滋肾益精", "益肺止咳", "降血糖"],
                contraindications=["湿盛中满者慎用"],
                seasonal_availability=[SeasonType.AUTUMN, SeasonType.WINTER],
                preparation_methods=["蒸煮", "炖汤", "煮粥", "炒制"],
                storage_tips="阴凉干燥处保存，避免阳光直射",
                origin_region="河南、山东、河北",
            ),
            FoodItem(
                food_id="F002",
                name="枸杞",
                category=FoodCategory.HERBS,
                nature=FoodNature.NEUTRAL,
                taste=FoodTaste.SWEET,
                meridian_tropism=["肝", "肾"],
                nutritional_info=NutritionalInfo(
                    calories_per_100g=258,
                    protein=13.9,
                    carbohydrates=64.1,
                    fat=1.5,
                    fiber=16.9,
                    vitamins={"A": 1625, "C": 48, "E": 1.86},
                    minerals={"Ca": 112, "Fe": 8.4, "Zn": 1.56},
                    antioxidants=["枸杞多糖", "玉米黄质", "β-胡萝卜素"],
                ),
                health_benefits=["滋补肝肾", "明目", "润肺", "抗衰老"],
                contraindications=["外邪实热者不宜"],
                seasonal_availability=[SeasonType.SUMMER, SeasonType.AUTUMN],
                preparation_methods=["泡茶", "煮粥", "炖汤", "直接食用"],
                storage_tips="密封保存，防潮防虫",
                origin_region="宁夏、青海、新疆",
            ),
            FoodItem(
                food_id="F003",
                name="薏米",
                category=FoodCategory.GRAINS,
                nature=FoodNature.COOL,
                taste=FoodTaste.SWEET,
                meridian_tropism=["脾", "胃", "肺"],
                nutritional_info=NutritionalInfo(
                    calories_per_100g=357,
                    protein=12.8,
                    carbohydrates=71.1,
                    fat=3.3,
                    fiber=2.0,
                    vitamins={"B1": 0.22, "B2": 0.15, "E": 2.08},
                    minerals={"Ca": 72, "P": 242, "Fe": 3.6, "K": 238},
                    antioxidants=["薏苡仁酯", "薏苡仁多糖"],
                ),
                health_benefits=["健脾利湿", "清热排脓", "美白肌肤", "抗肿瘤"],
                contraindications=["孕妇慎用", "便秘者少食"],
                seasonal_availability=[SeasonType.SUMMER, SeasonType.AUTUMN],
                preparation_methods=["煮粥", "炖汤", "磨粉", "泡茶"],
                storage_tips="干燥通风处保存",
                origin_region="福建、河北、辽宁",
            ),
            FoodItem(
                food_id="F004",
                name="银耳",
                category=FoodCategory.HERBS,
                nature=FoodNature.NEUTRAL,
                taste=FoodTaste.SWEET,
                meridian_tropism=["肺", "胃", "肾"],
                nutritional_info=NutritionalInfo(
                    calories_per_100g=200,
                    protein=10.0,
                    carbohydrates=67.3,
                    fat=1.4,
                    fiber=30.4,
                    vitamins={"D": 2.1, "B2": 0.14},
                    minerals={"Ca": 36, "P": 369, "Fe": 4.1},
                    antioxidants=["银耳多糖", "银耳酸性多糖"],
                ),
                health_benefits=["滋阴润肺", "养胃生津", "美容养颜", "增强免疫"],
                contraindications=["外感风寒者不宜"],
                seasonal_availability=[SeasonType.AUTUMN, SeasonType.WINTER],
                preparation_methods=["炖汤", "煮粥", "凉拌", "制作甜品"],
                storage_tips="干燥密封保存，泡发后尽快食用",
                origin_region="四川、云南、贵州",
            ),
            FoodItem(
                food_id="F005",
                name="生姜",
                category=FoodCategory.HERBS,
                nature=FoodNature.WARM,
                taste=FoodTaste.SPICY,
                meridian_tropism=["肺", "脾", "胃"],
                nutritional_info=NutritionalInfo(
                    calories_per_100g=41,
                    protein=1.8,
                    carbohydrates=8.5,
                    fat=0.3,
                    fiber=2.7,
                    vitamins={"C": 4, "B6": 0.16},
                    minerals={"Ca": 27, "Mg": 43, "K": 415},
                    antioxidants=["姜辣素", "姜烯酚", "姜酮"],
                ),
                health_benefits=["温中散寒", "化痰止咳", "解毒", "止呕"],
                contraindications=["阴虚内热者慎用"],
                seasonal_availability=[SeasonType.AUTUMN, SeasonType.WINTER],
                preparation_methods=["切片泡茶", "炒菜调味", "煮汤", "腌制"],
                storage_tips="阴凉通风处保存，可冷藏",
                origin_region="山东、河南、四川",
            ),
        ]

        for food in foods:
            self.food_database[food.food_id] = food

    def _initialize_therapy_plans(self):
        """初始化食疗方案"""
        plans = [
            FoodTherapyPlan(
                plan_id="TP001",
                name="气虚体质调理方案",
                target_constitution=ConstitutionType.QI_DEFICIENCY,
                target_symptoms=["乏力", "气短", "易感冒"],
                duration_days=30,
                daily_meals={
                    "breakfast": ["小米粥", "山药", "大枣"],
                    "lunch": ["黄芪炖鸡", "胡萝卜", "白米饭"],
                    "dinner": ["党参汤", "蒸蛋", "青菜"],
                },
                preparation_instructions=[
                    "小米粥：小米50g，大枣5颗，煮粥30分钟",
                    "黄芪炖鸡：黄芪30g，鸡肉200g，炖煮1小时",
                    "党参汤：党参20g，瘦肉100g，煮汤45分钟",
                ],
                expected_benefits=["改善乏力", "增强体质", "提高免疫力"],
                precautions=["避免生冷食物", "规律饮食", "适量运动"],
                progress_indicators=["精神状态改善", "食欲增加", "感冒次数减少"],
            ),
            FoodTherapyPlan(
                plan_id="TP002",
                name="阳虚体质温补方案",
                target_constitution=ConstitutionType.YANG_DEFICIENCY,
                target_symptoms=["怕冷", "手脚冰凉", "精神不振"],
                duration_days=45,
                daily_meals={
                    "breakfast": ["生姜红糖茶", "核桃粥", "温牛奶"],
                    "lunch": ["羊肉汤", "韭菜炒蛋", "糯米饭"],
                    "dinner": ["肉桂炖排骨", "红枣银耳汤", "小米粥"],
                },
                preparation_instructions=[
                    "生姜红糖茶：生姜3片，红糖15g，开水冲泡",
                    "羊肉汤：羊肉150g，当归10g，生姜5片，炖煮1.5小时",
                    "肉桂炖排骨：排骨300g，肉桂5g，炖煮1小时",
                ],
                expected_benefits=["改善怕冷", "温暖四肢", "提升阳气"],
                precautions=["避免寒凉食物", "保暖防寒", "适度温补"],
                progress_indicators=["体温回升", "精神改善", "手脚温暖"],
            ),
            FoodTherapyPlan(
                plan_id="TP003",
                name="阴虚体质滋润方案",
                target_constitution=ConstitutionType.YIN_DEFICIENCY,
                target_symptoms=["口干", "盗汗", "五心烦热"],
                duration_days=60,
                daily_meals={
                    "breakfast": ["银耳莲子粥", "蜂蜜水", "百合"],
                    "lunch": ["沙参玉竹汤", "清蒸鱼", "绿叶蔬菜"],
                    "dinner": ["枸杞炖瘦肉", "梨汤", "小米粥"],
                },
                preparation_instructions=[
                    "银耳莲子粥：银耳10g，莲子20g，大米50g，煮粥40分钟",
                    "沙参玉竹汤：沙参15g，玉竹15g，瘦肉100g，炖煮1小时",
                    "枸杞炖瘦肉：枸杞20g，瘦肉150g，炖煮45分钟",
                ],
                expected_benefits=["滋阴润燥", "清热降火", "改善口干"],
                precautions=["避免辛辣食物", "多饮水", "保持心情平静"],
                progress_indicators=["口干减轻", "盗汗改善", "皮肤润泽"],
            ),
        ]

        for plan in plans:
            self.therapy_plans[plan.plan_id] = plan

    def _initialize_agricultural_products(self):
        """初始化农产品数据"""
        products = [
            AgriculturalProduct(
                product_id="AP001",
                name="有机山药",
                variety="铁棍山药",
                agriculture_type=AgricultureType.ORGANIC,
                cultivation_method=CultivationMethod.SOIL_BASED,
                growing_region="河南焦作",
                planting_date=datetime(2024, 3, 15),
                harvest_date=datetime(2024, 10, 20),
                quality_grade="特级",
                certification=["有机认证", "绿色食品认证"],
                traceability_code="ORG-SY-2024-001",
                nutritional_analysis=NutritionalInfo(
                    calories_per_100g=56,
                    protein=1.9,
                    carbohydrates=12.4,
                    fat=0.2,
                    fiber=0.8,
                    vitamins={"A": 3, "C": 4, "B1": 0.05},
                    minerals={"Ca": 16, "P": 34, "Fe": 0.3},
                    antioxidants=["薯蓣皂苷", "多酚"],
                ),
                pesticide_residue={},  # 有机产品无农药残留
                heavy_metals={"Pb": 0.01, "Cd": 0.005, "Hg": 0.001},
                supplier_info={
                    "name": "焦作有机农场",
                    "contact": "0391-1234567",
                    "address": "河南省焦作市温县",
                },
                price_per_kg=25.0,
                availability_status="充足",
            ),
            AgriculturalProduct(
                product_id="AP002",
                name="宁夏枸杞",
                variety="宁杞1号",
                agriculture_type=AgricultureType.TRADITIONAL,
                cultivation_method=CultivationMethod.SOIL_BASED,
                growing_region="宁夏中宁",
                planting_date=datetime(2024, 4, 1),
                harvest_date=datetime(2024, 8, 15),
                quality_grade="一级",
                certification=["地理标志保护产品"],
                traceability_code="NX-GQ-2024-002",
                nutritional_analysis=NutritionalInfo(
                    calories_per_100g=258,
                    protein=13.9,
                    carbohydrates=64.1,
                    fat=1.5,
                    fiber=16.9,
                    vitamins={"A": 1625, "C": 48, "E": 1.86},
                    minerals={"Ca": 112, "Fe": 8.4, "Zn": 1.56},
                    antioxidants=["枸杞多糖", "玉米黄质"],
                ),
                pesticide_residue={"有机磷": 0.01, "有机氯": 0.005},
                heavy_metals={"Pb": 0.02, "Cd": 0.01, "Hg": 0.002},
                supplier_info={
                    "name": "中宁枸杞合作社",
                    "contact": "0955-5678901",
                    "address": "宁夏中宁县枸杞产业园",
                },
                price_per_kg=80.0,
                availability_status="充足",
            ),
            AgriculturalProduct(
                product_id="AP003",
                name="有机薏米",
                variety="大粒薏米",
                agriculture_type=AgricultureType.ORGANIC,
                cultivation_method=CultivationMethod.SOIL_BASED,
                growing_region="福建建宁",
                planting_date=datetime(2024, 5, 10),
                harvest_date=datetime(2024, 9, 25),
                quality_grade="特级",
                certification=["有机认证", "地理标志产品"],
                traceability_code="ORG-YM-2024-003",
                nutritional_analysis=NutritionalInfo(
                    calories_per_100g=357,
                    protein=12.8,
                    carbohydrates=71.1,
                    fat=3.3,
                    fiber=2.0,
                    vitamins={"B1": 0.22, "B2": 0.15, "E": 2.08},
                    minerals={"Ca": 72, "P": 242, "Fe": 3.6},
                    antioxidants=["薏苡仁酯", "薏苡仁多糖"],
                ),
                pesticide_residue={},  # 有机产品
                heavy_metals={"Pb": 0.015, "Cd": 0.008, "Hg": 0.001},
                supplier_info={
                    "name": "建宁有机农业基地",
                    "contact": "0598-2345678",
                    "address": "福建省建宁县有机农业园区",
                },
                price_per_kg=18.0,
                availability_status="充足",
            ),
        ]

        for product in products:
            self.agricultural_products[product.product_id] = product

    def _initialize_planting_guidance(self):
        """初始化种植指导"""
        guidance_list = [
            PlantingGuidance(
                guidance_id="PG001",
                crop_name="山药",
                variety="铁棍山药",
                region="华北地区",
                season=SeasonType.SPRING,
                soil_requirements={
                    "type": "沙壤土",
                    "ph": "6.0-7.0",
                    "organic_matter": ">2%",
                    "drainage": "良好",
                },
                climate_conditions={
                    "temperature": "15-25°C",
                    "humidity": "60-70%",
                    "rainfall": "600-800mm",
                    "sunshine": "充足",
                },
                planting_schedule={
                    "播种期": "3月中下旬",
                    "出苗期": "4月上旬",
                    "块茎形成期": "6-8月",
                    "收获期": "10月下旬",
                },
                care_instructions=[
                    "定期浇水，保持土壤湿润",
                    "及时除草，避免杂草竞争",
                    "适时追肥，以有机肥为主",
                    "搭架支撑，防止倒伏",
                    "病虫害防治，以预防为主",
                ],
                pest_management=[
                    "炭疽病：选用抗病品种，合理密植",
                    "根腐病：改善排水，避免积水",
                    "蚜虫：生物防治，天敌控制",
                    "地下害虫：土壤处理，物理防治",
                ],
                harvest_timing="叶片变黄，茎蔓枯萎时收获",
                yield_expectations={
                    "亩产量": "1500-2000kg",
                    "商品率": "85-90%",
                    "优质率": "70-80%",
                },
                quality_optimization=[
                    "控制氮肥用量，提高品质",
                    "适时收获，避免过早过晚",
                    "正确储存，保持品质",
                    "分级包装，提高商品价值",
                ],
                post_harvest_handling=[
                    "清洗去土，晾干表面",
                    "分级筛选，去除病伤",
                    "包装储存，控制温湿度",
                    "冷链运输，保持新鲜",
                ],
            ),
            PlantingGuidance(
                guidance_id="PG002",
                crop_name="枸杞",
                variety="宁杞1号",
                region="西北地区",
                season=SeasonType.SPRING,
                soil_requirements={
                    "type": "沙质壤土",
                    "ph": "7.0-8.5",
                    "盐分": "<0.3%",
                    "排水": "良好",
                },
                climate_conditions={
                    "temperature": "昼夜温差大",
                    "humidity": "干燥",
                    "rainfall": "200-400mm",
                    "sunshine": "充足，日照时间长",
                },
                planting_schedule={
                    "栽植期": "3-4月或10-11月",
                    "萌芽期": "4月上旬",
                    "开花期": "5-9月",
                    "果实成熟期": "7-10月",
                },
                care_instructions=[
                    "合理修剪，保持树形",
                    "适量灌溉，避免积水",
                    "科学施肥，有机无机结合",
                    "病虫害防治，综合管理",
                    "适时采收，分批进行",
                ],
                pest_management=[
                    "枸杞蚜虫：生物防治为主",
                    "枸杞红瘿蚊：清园处理",
                    "枸杞木虱：药剂防治",
                    "根腐病：改善排水条件",
                ],
                harvest_timing="果实呈红色，果肉饱满时采收",
                yield_expectations={
                    "亩产量": "150-200kg（干果）",
                    "盛果期": "第3-4年",
                    "经济寿命": "15-20年",
                },
                quality_optimization=[
                    "控制产量，提高品质",
                    "适时采收，保证成熟度",
                    "科学干制，保持营养",
                    "规范包装，提升价值",
                ],
                post_harvest_handling=[
                    "及时采收，避免过熟",
                    "清洗分级，去除杂质",
                    "科学干制，控制温度",
                    "密封包装，防潮防虫",
                ],
            ),
        ]

        for guidance in guidance_list:
            self.planting_guidance[guidance.guidance_id] = guidance

    async def recommend_food_therapy(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        user_preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """推荐食疗方案"""
        try:
            recommendations = {
                "constitution_based": [],
                "symptom_based": [],
                "seasonal": [],
                "comprehensive_plan": None,
                "dietary_guidelines": [],
                "precautions": [],
            }

            # 基于体质的推荐
            constitution_foods = self.constitution_food_mapping.get(
                constitution_type, {}
            )
            if constitution_foods:
                recommendations["constitution_based"] = {
                    "recommended_foods": constitution_foods.get("recommended", []),
                    "beneficial_categories": constitution_foods.get("beneficial", []),
                    "foods_to_avoid": constitution_foods.get("avoid", []),
                }

            # 基于症状的推荐
            symptom_therapies = []
            for symptom in symptoms:
                if symptom in self.symptom_therapy_mapping:
                    therapy = self.symptom_therapy_mapping[symptom]
                    symptom_therapies.append({"symptom": symptom, "therapy": therapy})
            recommendations["symptom_based"] = symptom_therapies

            # 季节性推荐
            current_season = self._get_current_season()
            seasonal_foods = self.seasonal_recommendations.get(current_season, {})
            recommendations["seasonal"] = seasonal_foods

            # 查找匹配的食疗方案
            matching_plans = []
            for plan in self.therapy_plans.values():
                if plan.target_constitution == constitution_type:
                    symptom_match = any(
                        symptom in plan.target_symptoms for symptom in symptoms
                    )
                    if symptom_match or not symptoms:
                        matching_plans.append(plan)

            if matching_plans:
                # 选择最匹配的方案
                best_plan = max(
                    matching_plans,
                    key=lambda p: len(set(p.target_symptoms) & set(symptoms)),
                )
                recommendations["comprehensive_plan"] = {
                    "plan_id": best_plan.plan_id,
                    "name": best_plan.name,
                    "duration_days": best_plan.duration_days,
                    "daily_meals": best_plan.daily_meals,
                    "preparation_instructions": best_plan.preparation_instructions,
                    "expected_benefits": best_plan.expected_benefits,
                    "precautions": best_plan.precautions,
                }

            # 生成饮食指导
            recommendations["dietary_guidelines"] = self._generate_dietary_guidelines(
                constitution_type, symptoms, user_preferences
            )

            # 生成注意事项
            recommendations["precautions"] = self._generate_precautions(
                constitution_type, symptoms
            )

            return recommendations

        except Exception as e:
            logger.error(f"食疗推荐失败: {e}")
            return {"error": str(e)}

    async def get_seasonal_ingredients(
        self, season: SeasonType = None, region: str = None
    ) -> Dict[str, Any]:
        """获取季节性食材推荐"""
        try:
            if not season:
                season = self._get_current_season()

            seasonal_data = self.seasonal_recommendations.get(season, {})

            # 获取当季食材详情
            ingredient_details = {}
            for category, ingredients in seasonal_data.items():
                if category != "principles":
                    ingredient_details[category] = []
                    for ingredient in ingredients:
                        # 查找食材详情
                        food_detail = self._find_food_by_name(ingredient)
                        if food_detail:
                            ingredient_details[category].append(
                                {
                                    "name": ingredient,
                                    "nature": food_detail.nature.value,
                                    "taste": food_detail.taste.value,
                                    "benefits": food_detail.health_benefits,
                                    "preparation": food_detail.preparation_methods,
                                }
                            )
                        else:
                            ingredient_details[category].append(
                                {
                                    "name": ingredient,
                                    "nature": "unknown",
                                    "taste": "unknown",
                                    "benefits": [],
                                    "preparation": [],
                                }
                            )

            # 获取相关农产品
            seasonal_products = []
            for product in self.agricultural_products.values():
                if season in [
                    SeasonType.SPRING,
                    SeasonType.SUMMER,
                ] and product.planting_date.month in [3, 4, 5, 6]:
                    seasonal_products.append(
                        {
                            "name": product.name,
                            "variety": product.variety,
                            "region": product.growing_region,
                            "quality": product.quality_grade,
                            "price": product.price_per_kg,
                            "availability": product.availability_status,
                        }
                    )
                elif (
                    season in [SeasonType.AUTUMN, SeasonType.WINTER]
                    and product.harvest_date
                    and product.harvest_date.month in [9, 10, 11, 12]
                ):
                    seasonal_products.append(
                        {
                            "name": product.name,
                            "variety": product.variety,
                            "region": product.growing_region,
                            "quality": product.quality_grade,
                            "price": product.price_per_kg,
                            "availability": product.availability_status,
                        }
                    )

            return {
                "season": season.value,
                "principles": seasonal_data.get("principles", []),
                "ingredients": ingredient_details,
                "available_products": seasonal_products,
                "cooking_suggestions": self._get_seasonal_cooking_suggestions(season),
                "health_tips": self._get_seasonal_health_tips(season),
            }

        except Exception as e:
            logger.error(f"获取季节性食材失败: {e}")
            return {"error": str(e)}

    async def analyze_nutrition(
        self,
        user_id: str,
        constitution_type: ConstitutionType,
        current_symptoms: List[str],
        dietary_preferences: List[str] = None,
        allergies: List[str] = None,
        age: int = None,
        gender: str = None,
        activity_level: str = "moderate",
    ) -> NutritionalAnalysis:
        """营养分析"""
        try:
            # 计算每日热量需求
            daily_calories = self._calculate_daily_calorie_needs(
                age, gender, activity_level
            )

            # 计算宏量营养素比例
            macro_ratios = self._calculate_macro_nutrient_ratios(constitution_type)

            # 计算微量营养素需求
            micro_needs = self._calculate_micro_nutrient_needs(
                age, gender, constitution_type
            )

            # 推荐食物
            recommended_foods = self._get_recommended_foods_for_nutrition(
                constitution_type, current_symptoms, dietary_preferences, allergies
            )

            # 需要避免的食物
            foods_to_avoid = self._get_foods_to_avoid(
                constitution_type, current_symptoms, allergies
            )

            # 用餐时间建议
            meal_timing = self._get_meal_timing_suggestions(constitution_type)

            # 水分需求
            hydration_needs = self._calculate_hydration_needs(age, activity_level)

            # 补充剂推荐
            supplements = self._get_supplement_recommendations(
                constitution_type, current_symptoms, age, gender
            )

            analysis = NutritionalAnalysis(
                analysis_id=f"NA_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                constitution_type=constitution_type,
                current_symptoms=current_symptoms,
                dietary_preferences=dietary_preferences or [],
                allergies=allergies or [],
                daily_calorie_needs=daily_calories,
                macro_nutrient_ratios=macro_ratios,
                micro_nutrient_needs=micro_needs,
                recommended_foods=recommended_foods,
                foods_to_avoid=foods_to_avoid,
                meal_timing_suggestions=meal_timing,
                hydration_needs=hydration_needs,
                supplement_recommendations=supplements,
            )

            return analysis

        except Exception as e:
            logger.error(f"营养分析失败: {e}")
            raise

    async def get_planting_guidance(
        self, crop_name: str, region: str = None, season: SeasonType = None
    ) -> Dict[str, Any]:
        """获取种植指导"""
        try:
            if not season:
                season = self._get_current_season()

            # 查找匹配的种植指导
            matching_guidance = []
            for guidance in self.planting_guidance.values():
                if guidance.crop_name == crop_name:
                    if not region or guidance.region == region:
                        if guidance.season == season:
                            matching_guidance.append(guidance)

            if not matching_guidance:
                return {
                    "error": f"未找到 {crop_name} 在 {region or '当前地区'} {season.value} 季节的种植指导"
                }

            # 选择最匹配的指导
            best_guidance = matching_guidance[0]

            # 获取相关农产品信息
            related_products = []
            for product in self.agricultural_products.values():
                if crop_name in product.name:
                    related_products.append(
                        {
                            "name": product.name,
                            "variety": product.variety,
                            "quality": product.quality_grade,
                            "price": product.price_per_kg,
                            "supplier": product.supplier_info.get("name", ""),
                            "certification": product.certification,
                        }
                    )

            return {
                "guidance": {
                    "crop_name": best_guidance.crop_name,
                    "variety": best_guidance.variety,
                    "region": best_guidance.region,
                    "season": best_guidance.season.value,
                    "soil_requirements": best_guidance.soil_requirements,
                    "climate_conditions": best_guidance.climate_conditions,
                    "planting_schedule": best_guidance.planting_schedule,
                    "care_instructions": best_guidance.care_instructions,
                    "pest_management": best_guidance.pest_management,
                    "harvest_timing": best_guidance.harvest_timing,
                    "yield_expectations": best_guidance.yield_expectations,
                    "quality_optimization": best_guidance.quality_optimization,
                    "post_harvest_handling": best_guidance.post_harvest_handling,
                },
                "related_products": related_products,
                "market_information": self._get_market_information(crop_name),
                "success_tips": self._get_planting_success_tips(crop_name),
            }

        except Exception as e:
            logger.error(f"获取种植指导失败: {e}")
            return {"error": str(e)}

    async def search_agricultural_products(
        self,
        product_name: str = None,
        agriculture_type: AgricultureType = None,
        region: str = None,
        quality_grade: str = None,
        max_price: float = None,
    ) -> List[Dict[str, Any]]:
        """搜索农产品"""
        try:
            results = []

            for product in self.agricultural_products.values():
                # 应用搜索条件
                if product_name and product_name.lower() not in product.name.lower():
                    continue
                if agriculture_type and product.agriculture_type != agriculture_type:
                    continue
                if region and region.lower() not in product.growing_region.lower():
                    continue
                if quality_grade and product.quality_grade != quality_grade:
                    continue
                if max_price and product.price_per_kg > max_price:
                    continue

                # 添加到结果
                results.append(
                    {
                        "product_id": product.product_id,
                        "name": product.name,
                        "variety": product.variety,
                        "agriculture_type": product.agriculture_type.value,
                        "cultivation_method": product.cultivation_method.value,
                        "region": product.growing_region,
                        "quality_grade": product.quality_grade,
                        "certification": product.certification,
                        "price_per_kg": product.price_per_kg,
                        "availability": product.availability_status,
                        "supplier": product.supplier_info,
                        "nutritional_highlights": self._get_nutritional_highlights(
                            product.nutritional_analysis
                        ),
                        "safety_info": {
                            "pesticide_residue": product.pesticide_residue,
                            "heavy_metals": product.heavy_metals,
                        },
                        "traceability": product.traceability_code,
                    }
                )

            # 按价格排序
            results.sort(key=lambda x: x["price_per_kg"])

            return results

        except Exception as e:
            logger.error(f"搜索农产品失败: {e}")
            return []

    def _get_current_season(self) -> SeasonType:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return SeasonType.SPRING
        elif month in [6, 7, 8]:
            return SeasonType.SUMMER
        elif month in [9, 10, 11]:
            return SeasonType.AUTUMN
        else:
            return SeasonType.WINTER

    def _find_food_by_name(self, name: str) -> Optional[FoodItem]:
        """根据名称查找食物"""
        for food in self.food_database.values():
            if name in food.name or food.name in name:
                return food
        return None

    def _generate_dietary_guidelines(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        user_preferences: Dict[str, Any] = None,
    ) -> List[str]:
        """生成饮食指导"""
        guidelines = []

        # 基于体质的指导
        if constitution_type == ConstitutionType.QI_DEFICIENCY:
            guidelines.extend(
                [
                    "多食用补气食材，如人参、黄芪、大枣",
                    "选择易消化的食物，避免生冷",
                    "规律饮食，少食多餐",
                    "适量摄入优质蛋白质",
                ]
            )
        elif constitution_type == ConstitutionType.YANG_DEFICIENCY:
            guidelines.extend(
                [
                    "多食用温热性食物，如羊肉、生姜",
                    "避免寒凉食物和冷饮",
                    "适量食用坚果类食品",
                    "餐前可饮用温开水",
                ]
            )
        elif constitution_type == ConstitutionType.YIN_DEFICIENCY:
            guidelines.extend(
                [
                    "多食用滋阴润燥食物，如银耳、百合",
                    "避免辛辣燥热食物",
                    "增加水分摄入",
                    "选择清淡烹饪方式",
                ]
            )

        # 基于症状的指导
        if "失眠" in symptoms:
            guidelines.append("晚餐避免咖啡因，可食用安神食材")
        if "便秘" in symptoms:
            guidelines.append("增加膳食纤维摄入，多饮水")
        if "乏力" in symptoms:
            guidelines.append("保证充足的营养摄入，适量补充维生素B族")

        return guidelines

    def _generate_precautions(
        self, constitution_type: ConstitutionType, symptoms: List[str]
    ) -> List[str]:
        """生成注意事项"""
        precautions = [
            "食疗需要持续进行，不可急于求成",
            "如有严重症状，请及时就医",
            "个体差异较大，如有不适请停止使用",
        ]

        # 基于体质的注意事项
        if constitution_type == ConstitutionType.YANG_DEFICIENCY:
            precautions.append("温补不可过度，避免上火")
        elif constitution_type == ConstitutionType.YIN_DEFICIENCY:
            precautions.append("滋阴食材性质偏凉，脾胃虚寒者慎用")
        elif constitution_type == ConstitutionType.PHLEGM_DAMPNESS:
            precautions.append("避免油腻甜腻食物，以免加重痰湿")

        return precautions

    def _get_seasonal_cooking_suggestions(self, season: SeasonType) -> List[str]:
        """获取季节性烹饪建议"""
        suggestions = {
            SeasonType.SPRING: [
                "多用蒸煮方式，保持食材鲜嫩",
                "适量添加芳香调料，如薄荷、柠檬",
                "减少油腻，增加清淡菜品",
            ],
            SeasonType.SUMMER: [
                "多用凉拌、清蒸方式",
                "增加汤水类食品",
                "适量使用清热食材",
            ],
            SeasonType.AUTUMN: [
                "多用炖煮方式，滋润养肺",
                "适量添加润燥食材",
                "注意食材搭配平衡",
            ],
            SeasonType.WINTER: [
                "多用炖煮、煲汤方式",
                "适量添加温热香料",
                "增加热量摄入",
            ],
        }
        return suggestions.get(season, [])

    def _get_seasonal_health_tips(self, season: SeasonType) -> List[str]:
        """获取季节性健康提示"""
        tips = {
            SeasonType.SPRING: [
                "注意疏肝理气，保持心情舒畅",
                "适量运动，促进阳气升发",
                "预防春季过敏",
            ],
            SeasonType.SUMMER: [
                "注意防暑降温，避免中暑",
                "保持充足水分摄入",
                "避免过度贪凉",
            ],
            SeasonType.AUTUMN: [
                "注意润肺防燥，预防呼吸道疾病",
                "适量进补，为冬季做准备",
                "保持皮肤湿润",
            ],
            SeasonType.WINTER: [
                "注意保暖，预防感冒",
                "适量温补，增强体质",
                "保持室内空气流通",
            ],
        }
        return tips.get(season, [])

    def _calculate_daily_calorie_needs(
        self, age: int = None, gender: str = None, activity_level: str = "moderate"
    ) -> float:
        """计算每日热量需求"""
        if not age or not gender:
            return 2000.0  # 默认值

        # 基础代谢率计算（Harris-Benedict公式）
        if gender.lower() == "male":
            bmr = (
                88.362 + (13.397 * 70) + (4.799 * 170) - (5.677 * age)
            )  # 假设体重70kg，身高170cm
        else:
            bmr = (
                447.593 + (9.247 * 60) + (3.098 * 160) - (4.330 * age)
            )  # 假设体重60kg，身高160cm

        # 活动系数
        activity_factors = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }

        factor = activity_factors.get(activity_level, 1.55)
        return bmr * factor

    def _calculate_macro_nutrient_ratios(
        self, constitution_type: ConstitutionType
    ) -> Dict[str, float]:
        """计算宏量营养素比例"""
        # 基于体质的营养素比例调整
        base_ratios = {"carbohydrates": 0.55, "protein": 0.20, "fat": 0.25}

        if constitution_type == ConstitutionType.QI_DEFICIENCY:
            # 气虚体质需要更多蛋白质
            base_ratios["protein"] = 0.25
            base_ratios["carbohydrates"] = 0.50
            base_ratios["fat"] = 0.25
        elif constitution_type == ConstitutionType.YANG_DEFICIENCY:
            # 阳虚体质需要更多脂肪
            base_ratios["fat"] = 0.30
            base_ratios["carbohydrates"] = 0.50
            base_ratios["protein"] = 0.20
        elif constitution_type == ConstitutionType.PHLEGM_DAMPNESS:
            # 痰湿体质需要减少脂肪
            base_ratios["fat"] = 0.20
            base_ratios["carbohydrates"] = 0.55
            base_ratios["protein"] = 0.25

        return base_ratios

    def _calculate_micro_nutrient_needs(
        self,
        age: int = None,
        gender: str = None,
        constitution_type: ConstitutionType = None,
    ) -> Dict[str, float]:
        """计算微量营养素需求"""
        # 基础需求量（每日推荐摄入量）
        base_needs = {
            "vitamin_a": 800,  # μg
            "vitamin_c": 100,  # mg
            "vitamin_d": 10,  # μg
            "vitamin_e": 14,  # mg
            "calcium": 800,  # mg
            "iron": 12,  # mg
            "zinc": 15,  # mg
            "selenium": 50,  # μg
        }

        # 根据性别和年龄调整
        if gender and gender.lower() == "female":
            base_needs["iron"] = 20  # 女性需要更多铁

        if age and age > 50:
            base_needs["calcium"] = 1000  # 老年人需要更多钙
            base_needs["vitamin_d"] = 15

        # 根据体质调整
        if constitution_type == ConstitutionType.QI_DEFICIENCY:
            base_needs["iron"] *= 1.2
            base_needs["vitamin_c"] *= 1.1
        elif constitution_type == ConstitutionType.YIN_DEFICIENCY:
            base_needs["vitamin_a"] *= 1.2
            base_needs["vitamin_e"] *= 1.1

        return base_needs

    def _get_recommended_foods_for_nutrition(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        dietary_preferences: List[str] = None,
        allergies: List[str] = None,
    ) -> List[str]:
        """获取营养推荐食物"""
        recommended = []

        # 基于体质的推荐
        constitution_foods = self.constitution_food_mapping.get(constitution_type, {})
        recommended.extend(constitution_foods.get("recommended", []))

        # 基于症状的推荐
        for symptom in symptoms:
            if symptom in self.symptom_therapy_mapping:
                therapy = self.symptom_therapy_mapping[symptom]
                recommended.extend(therapy.get("primary_foods", []))

        # 过滤过敏食物
        if allergies:
            recommended = [
                food
                for food in recommended
                if not any(allergen in food for allergen in allergies)
            ]

        # 去重
        return list(set(recommended))

    def _get_foods_to_avoid(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        allergies: List[str] = None,
    ) -> List[str]:
        """获取需要避免的食物"""
        avoid_foods = []

        # 基于体质的避免食物
        constitution_foods = self.constitution_food_mapping.get(constitution_type, {})
        avoid_foods.extend(constitution_foods.get("avoid", []))

        # 添加过敏食物
        if allergies:
            avoid_foods.extend(allergies)

        return list(set(avoid_foods))

    def _get_meal_timing_suggestions(
        self, constitution_type: ConstitutionType
    ) -> Dict[str, str]:
        """获取用餐时间建议"""
        base_timing = {
            "breakfast": "7:00-8:00",
            "lunch": "12:00-13:00",
            "dinner": "18:00-19:00",
        }

        if constitution_type == ConstitutionType.QI_DEFICIENCY:
            base_timing["snack_morning"] = "10:00"
            base_timing["snack_afternoon"] = "15:00"
        elif constitution_type == ConstitutionType.PHLEGM_DAMPNESS:
            base_timing["dinner"] = "17:00-18:00"  # 早一点晚餐

        return base_timing

    def _calculate_hydration_needs(
        self, age: int = None, activity_level: str = "moderate"
    ) -> float:
        """计算水分需求（升/天）"""
        base_needs = 2.0  # 基础需求2升

        if activity_level in ["active", "very_active"]:
            base_needs += 0.5

        if age and age > 65:
            base_needs += 0.3  # 老年人需要更多水分

        return base_needs

    def _get_supplement_recommendations(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        age: int = None,
        gender: str = None,
    ) -> List[str]:
        """获取补充剂推荐"""
        supplements = []

        # 基于体质的补充剂
        if constitution_type == ConstitutionType.QI_DEFICIENCY:
            supplements.extend(["维生素B族", "铁剂", "蛋白质粉"])
        elif constitution_type == ConstitutionType.YIN_DEFICIENCY:
            supplements.extend(["维生素A", "维生素E", "胶原蛋白"])
        elif constitution_type == ConstitutionType.YANG_DEFICIENCY:
            supplements.extend(["维生素D", "钙镁片", "辅酶Q10"])

        # 基于症状的补充剂
        if "失眠" in symptoms:
            supplements.append("褪黑素")
        if "乏力" in symptoms:
            supplements.append("维生素B12")
        if "易感冒" in symptoms:
            supplements.append("维生素C")

        # 基于年龄和性别
        if age and age > 50:
            supplements.append("钙片")
        if gender and gender.lower() == "female":
            supplements.append("叶酸")

        return list(set(supplements))

    def _get_market_information(self, crop_name: str) -> Dict[str, Any]:
        """获取市场信息"""
        # 模拟市场信息
        return {
            "current_price_range": "15-30元/kg",
            "market_trend": "稳中有升",
            "demand_level": "高",
            "supply_status": "充足",
            "quality_requirements": ["有机认证", "无农药残留", "规格统一"],
            "main_markets": ["一线城市", "健康食品市场", "中医药市场"],
        }

    def _get_planting_success_tips(self, crop_name: str) -> List[str]:
        """获取种植成功技巧"""
        general_tips = [
            "选择适宜的品种和种植时间",
            "做好土壤改良和施肥工作",
            "建立完善的灌溉系统",
            "实施综合病虫害防治",
            "注重产品质量和安全",
            "建立销售渠道和品牌",
        ]

        # 可以根据具体作物添加特定技巧
        if crop_name == "山药":
            general_tips.extend(
                ["选择深厚疏松的沙壤土", "做好排水防涝工作", "适时搭架支撑"]
            )
        elif crop_name == "枸杞":
            general_tips.extend(
                ["选择光照充足的地块", "控制灌溉量，避免积水", "及时修剪整形"]
            )

        return general_tips

    def _get_nutritional_highlights(
        self, nutritional_info: NutritionalInfo
    ) -> List[str]:
        """获取营养亮点"""
        highlights = []

        if nutritional_info.protein > 10:
            highlights.append(f"高蛋白质 ({nutritional_info.protein}g/100g)")
        if nutritional_info.fiber > 5:
            highlights.append(f"高纤维 ({nutritional_info.fiber}g/100g)")
        if nutritional_info.vitamins.get("C", 0) > 50:
            highlights.append(f"富含维生素C ({nutritional_info.vitamins['C']}mg/100g)")
        if nutritional_info.antioxidants:
            highlights.append(
                f"富含抗氧化物质: {', '.join(nutritional_info.antioxidants[:3])}"
            )

        return highlights

    def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "food_database_size": len(self.food_database),
            "therapy_plans_count": len(self.therapy_plans),
            "agricultural_products_count": len(self.agricultural_products),
            "planting_guidance_count": len(self.planting_guidance),
            "constitution_types_supported": len(self.constitution_food_mapping),
            "symptoms_covered": len(self.symptom_therapy_mapping),
            "seasonal_recommendations": len(self.seasonal_recommendations),
        }
