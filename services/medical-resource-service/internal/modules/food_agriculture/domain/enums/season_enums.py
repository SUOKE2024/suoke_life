"""
季节相关枚举定义
"""

from enum import Enum


class SeasonType(Enum):
    """季节类型"""

    SPRING = "spring"  # 春季
    SUMMER = "summer"  # 夏季
    AUTUMN = "autumn"  # 秋季
    WINTER = "winter"  # 冬季


class SeasonalCharacteristic(Enum):
    """季节特征"""

    # 春季特征
    SPRING_GROWTH = "spring_growth"  # 春生
    SPRING_WARMING = "spring_warming"  # 春暖
    SPRING_RENEWAL = "spring_renewal"  # 春回

    # 夏季特征
    SUMMER_HEAT = "summer_heat"  # 夏热
    SUMMER_GROWTH = "summer_growth"  # 夏长
    SUMMER_ABUNDANCE = "summer_abundance"  # 夏盛

    # 秋季特征
    AUTUMN_COOL = "autumn_cool"  # 秋凉
    AUTUMN_HARVEST = "autumn_harvest"  # 秋收
    AUTUMN_DRYNESS = "autumn_dryness"  # 秋燥

    # 冬季特征
    WINTER_COLD = "winter_cold"  # 冬寒
    WINTER_STORAGE = "winter_storage"  # 冬藏
    WINTER_STILLNESS = "winter_stillness"  # 冬静


class SeasonalHealthFocus(Enum):
    """季节养生重点"""

    # 春季养生
    SPRING_LIVER_CARE = "spring_liver_care"  # 春养肝
    SPRING_DETOX = "spring_detox"  # 春排毒
    SPRING_ENERGY_BOOST = "spring_energy_boost"  # 春升阳

    # 夏季养生
    SUMMER_HEART_CARE = "summer_heart_care"  # 夏养心
    SUMMER_COOLING = "summer_cooling"  # 夏清热
    SUMMER_HYDRATION = "summer_hydration"  # 夏补水

    # 秋季养生
    AUTUMN_LUNG_CARE = "autumn_lung_care"  # 秋养肺
    AUTUMN_MOISTENING = "autumn_moistening"  # 秋润燥
    AUTUMN_IMMUNITY = "autumn_immunity"  # 秋增免疫

    # 冬季养生
    WINTER_KIDNEY_CARE = "winter_kidney_care"  # 冬养肾
    WINTER_WARMING = "winter_warming"  # 冬温阳
    WINTER_NOURISHING = "winter_nourishing"  # 冬滋补


class SeasonalFoodPreference(Enum):
    """季节饮食偏好"""

    # 春季饮食
    SPRING_FRESH_GREENS = "spring_fresh_greens"  # 春食新绿
    SPRING_LIGHT_FOODS = "spring_light_foods"  # 春食清淡
    SPRING_SPROUTS = "spring_sprouts"  # 春食芽菜

    # 夏季饮食
    SUMMER_COOLING_FOODS = "summer_cooling_foods"  # 夏食清凉
    SUMMER_HYDRATING = "summer_hydrating"  # 夏食多汁
    SUMMER_LIGHT_COOKING = "summer_light_cooking"  # 夏烹清爽

    # 秋季饮食
    AUTUMN_MOISTENING_FOODS = "autumn_moistening_foods"  # 秋食润燥
    AUTUMN_NOURISHING = "autumn_nourishing"  # 秋食滋养
    AUTUMN_WARMING_FOODS = "autumn_warming_foods"  # 秋食温润

    # 冬季饮食
    WINTER_WARMING_FOODS = "winter_warming_foods"  # 冬食温热
    WINTER_NOURISHING_FOODS = "winter_nourishing_foods"  # 冬食滋补
    WINTER_ROOT_VEGETABLES = "winter_root_vegetables"  # 冬食根茎


class SeasonalCookingMethod(Enum):
    """季节烹饪方法"""

    # 春季烹饪
    SPRING_STEAMING = "spring_steaming"  # 春蒸
    SPRING_BLANCHING = "spring_blanching"  # 春焯
    SPRING_LIGHT_STIR_FRY = "spring_light_stir_fry"  # 春炒

    # 夏季烹饪
    SUMMER_COLD_DISHES = "summer_cold_dishes"  # 夏凉拌
    SUMMER_LIGHT_SOUP = "summer_light_soup"  # 夏清汤
    SUMMER_GRILLING = "summer_grilling"  # 夏烧烤

    # 秋季烹饪
    AUTUMN_BRAISING = "autumn_braising"  # 秋炖
    AUTUMN_ROASTING = "autumn_roasting"  # 秋烤
    AUTUMN_SOUP_MAKING = "autumn_soup_making"  # 秋煲汤

    # 冬季烹饪
    WINTER_SLOW_COOKING = "winter_slow_cooking"  # 冬慢炖
    WINTER_HOT_POT = "winter_hot_pot"  # 冬火锅
    WINTER_WARMING_SOUP = "winter_warming_soup"  # 冬热汤
