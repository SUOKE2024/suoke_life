from typing import Dict, List, Any, Optional, Union

"""
food_enums - 索克生活项目模块
"""

from enum import Enum

"""
食物相关枚举定义
从原始的food_agriculture_service.py中提取的枚举类型
"""



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
    """食物性质（中医理论）"""

    HOT = "hot"  # 热性
    WARM = "warm"  # 温性
    NEUTRAL = "neutral"  # 平性
    COOL = "cool"  # 凉性
    COLD = "cold"  # 寒性


class FoodTaste(Enum):
    """食物味道（中医五味）"""

    SWEET = "sweet"  # 甘味
    SOUR = "sour"  # 酸味
    BITTER = "bitter"  # 苦味
    SPICY = "spicy"  # 辛味
    SALTY = "salty"  # 咸味


class PreparationMethod(Enum):
    """烹饪方法"""

    RAW = "raw"  # 生食
    STEAMED = "steamed"  # 蒸
    BOILED = "boiled"  # 煮
    STIR_FRIED = "stir_fried"  # 炒
    BRAISED = "braised"  # 炖
    ROASTED = "roasted"  # 烤
    GRILLED = "grilled"  # 烧烤
    DEEP_FRIED = "deep_fried"  # 油炸
    SOUP = "soup"  # 汤
    PORRIDGE = "porridge"  # 粥
    TEA = "tea"  # 茶饮
    JUICE = "juice"  # 榨汁


class StorageMethod(Enum):
    """储存方法"""

    ROOM_TEMPERATURE = "room_temperature"  # 常温
    REFRIGERATED = "refrigerated"  # 冷藏
    FROZEN = "frozen"  # 冷冻
    DRIED = "dried"  # 干燥
    PICKLED = "pickled"  # 腌制
    CANNED = "canned"  # 罐装
    VACUUM_SEALED = "vacuum_sealed"  # 真空包装


class NutritionalComponent(Enum):
    """营养成分"""

    PROTEIN = "protein"  # 蛋白质
    CARBOHYDRATES = "carbohydrates"  # 碳水化合物
    FAT = "fat"  # 脂肪
    FIBER = "fiber"  # 纤维
    VITAMIN_A = "vitamin_a"  # 维生素A
    VITAMIN_B1 = "vitamin_b1"  # 维生素B1
    VITAMIN_B2 = "vitamin_b2"  # 维生素B2
    VITAMIN_B6 = "vitamin_b6"  # 维生素B6
    VITAMIN_B12 = "vitamin_b12"  # 维生素B12
    VITAMIN_C = "vitamin_c"  # 维生素C
    VITAMIN_D = "vitamin_d"  # 维生素D
    VITAMIN_E = "vitamin_e"  # 维生素E
    VITAMIN_K = "vitamin_k"  # 维生素K
    CALCIUM = "calcium"  # 钙
    IRON = "iron"  # 铁
    MAGNESIUM = "magnesium"  # 镁
    PHOSPHORUS = "phosphorus"  # 磷
    POTASSIUM = "potassium"  # 钾
    SODIUM = "sodium"  # 钠
    ZINC = "zinc"  # 锌
    SELENIUM = "selenium"  # 硒


class HealthBenefit(Enum):
    """健康功效"""

    IMMUNE_BOOST = "immune_boost"  # 增强免疫力
    ANTIOXIDANT = "antioxidant"  # 抗氧化
    ANTI_INFLAMMATORY = "anti_inflammatory"  # 抗炎
    DIGESTIVE_AID = "digestive_aid"  # 助消化
    HEART_HEALTH = "heart_health"  # 心脏健康
    BRAIN_HEALTH = "brain_health"  # 大脑健康
    BONE_HEALTH = "bone_health"  # 骨骼健康
    EYE_HEALTH = "eye_health"  # 眼部健康
    SKIN_HEALTH = "skin_health"  # 皮肤健康
    WEIGHT_MANAGEMENT = "weight_management"  # 体重管理
    BLOOD_SUGAR_CONTROL = "blood_sugar_control"  # 血糖控制
    CHOLESTEROL_CONTROL = "cholesterol_control"  # 胆固醇控制
    DETOXIFICATION = "detoxification"  # 排毒
    ENERGY_BOOST = "energy_boost"  # 提升能量
    STRESS_RELIEF = "stress_relief"  # 缓解压力
    SLEEP_AID = "sleep_aid"  # 助眠


class Contraindication(Enum):
    """禁忌症"""

    PREGNANCY = "pregnancy"  # 孕期
    BREASTFEEDING = "breastfeeding"  # 哺乳期
    DIABETES = "diabetes"  # 糖尿病
    HYPERTENSION = "hypertension"  # 高血压
    KIDNEY_DISEASE = "kidney_disease"  # 肾病
    LIVER_DISEASE = "liver_disease"  # 肝病
    HEART_DISEASE = "heart_disease"  # 心脏病
    ALLERGIES = "allergies"  # 过敏
    GOUT = "gout"  # 痛风
    GASTRITIS = "gastritis"  # 胃炎
    ULCER = "ulcer"  # 溃疡
    GALLSTONES = "gallstones"  # 胆结石
    THYROID_DISORDER = "thyroid_disorder"  # 甲状腺疾病
    AUTOIMMUNE_DISEASE = "autoimmune_disease"  # 自身免疫疾病
