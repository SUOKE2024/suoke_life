"""
helpers - 索克生活项目模块
"""

from datetime import date, datetime

"""
辅助工具函数

提供各种辅助计算和工具函数
"""


def calculate_age(
    birth_year: int, birth_month: int, birth_day: int, reference_date: datetime = None
) -> int:
    """
    计算年龄

    Args:
        birth_year: 出生年份
        birth_month: 出生月份
        birth_day: 出生日期
        reference_date: 参考日期，默认为当前日期

    Returns:
        年龄
    """
    if reference_date is None:
        reference_date = datetime.now()

    birth_date = date(birth_year, birth_month, birth_day)
    ref_date = (
        reference_date.date()
        if isinstance(reference_date, datetime)
        else reference_date
    )

    age = ref_date.year - birth_date.year

    # 检查是否还没到生日
    if (ref_date.month, ref_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def get_zodiac_sign(birth_month: int, birth_day: int) -> str:
    """
    获取星座

    Args:
        birth_month: 出生月份
        birth_day: 出生日期

    Returns:
        星座名称
    """
    zodiac_dates = [
        (1, 20, "水瓶座"),
        (2, 19, "双鱼座"),
        (3, 21, "白羊座"),
        (4, 20, "金牛座"),
        (5, 21, "双子座"),
        (6, 21, "巨蟹座"),
        (7, 23, "狮子座"),
        (8, 23, "处女座"),
        (9, 23, "天秤座"),
        (10, 23, "天蝎座"),
        (11, 22, "射手座"),
        (12, 22, "摩羯座"),
    ]

    for i, (month, day, sign) in enumerate(zodiac_dates):
        if birth_month == month and birth_day <= day:
            return sign
        elif birth_month == month - 1 if month > 1 else 12:
            prev_month, prev_day, prev_sign = (
                zodiac_dates[i - 1] if i > 0 else zodiac_dates[-1]
            )
            if birth_day > prev_day:
                return sign

    return "摩羯座"  # 默认返回


def get_chinese_zodiac(birth_year: int) -> str:
    """
    获取生肖

    Args:
        birth_year: 出生年份

    Returns:
        生肖名称
    """
    zodiac_animals = [
        "鼠",
        "牛",
        "虎",
        "兔",
        "龙",
        "蛇",
        "马",
        "羊",
        "猴",
        "鸡",
        "狗",
        "猪",
    ]
    return zodiac_animals[(birth_year - 1900) % 12]


def get_season_by_month(month: int) -> str:
    """
    根据月份获取季节

    Args:
        month: 月份

    Returns:
        季节名称
    """
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:
        return "冬季"


def get_time_period(hour: int) -> str:
    """
    根据小时获取时段

    Args:
        hour: 小时（0 - 23）

    Returns:
        时段名称
    """
    if 6 <= hour < 12:
        return "上午"
    elif 12 <= hour < 18:
        return "下午"
    elif 18 <= hour < 22:
        return "晚上"
    else:
        return "深夜"


def convert_to_chinese_hour(hour: int) -> str:
    """
    将24小时制转换为中国传统时辰

    Args:
        hour: 小时（0 - 23）

    Returns:
        时辰名称
    """
    time_periods = [
        "子时",
        "丑时",
        "寅时",
        "卯时",
        "辰时",
        "巳时",
        "午时",
        "未时",
        "申时",
        "酉时",
        "戌时",
        "亥时",
    ]

    # 子时是23:00 - 1:00，需要特殊处理
    if hour == 23:
        return "子时"
    else:
        return time_periods[(hour + 1) // 2]


def get_wuxing_by_year(year: int) -> str:
    """
    根据年份获取五行属性

    Args:
        year: 年份

    Returns:
        五行属性
    """
    year_mod = year % 10
    wuxing_map = {
        0: "金",
        1: "金",
        2: "水",
        3: "水",
        4: "木",
        5: "木",
        6: "火",
        7: "火",
        8: "土",
        9: "土",
    }
    return wuxing_map[year_mod]


def calculate_lunar_age(birth_year: int, current_year: int) -> int:
    """
    计算虚岁

    Args:
        birth_year: 出生年份
        current_year: 当前年份

    Returns:
        虚岁
    """
    return current_year - birth_year + 1


def is_leap_year(year: int) -> bool:
    """
    判断是否为闰年

    Args:
        year: 年份

    Returns:
        是否为闰年
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def get_days_in_month(year: int, month: int) -> int:
    """
    获取指定年月的天数

    Args:
        year: 年份
        month: 月份

    Returns:
        天数
    """
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if month == 2 and is_leap_year(year):
        return 29
    else:
        return days_in_month[month - 1]


def format_duration(seconds: float) -> str:
    """
    格式化时间间隔

    Args:
        seconds: 秒数

    Returns:
        格式化的时间字符串
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}毫秒"
    elif seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误

    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值

    Returns:
        除法结果
    """
    if denominator == 0:
        return default
    return numerator / denominator


def normalize_score(score: float, min_score: float, max_score: float) -> float:
    """
    标准化分数到0 - 1范围

    Args:
        score: 原始分数
        min_score: 最小分数
        max_score: 最大分数

    Returns:
        标准化后的分数
    """
    if max_score == min_score:
        return 0.5

    normalized = (score - min_score) / (max_score - min_score)
    return max(0.0, min(1.0, normalized))


def get_health_level(score: float) -> str:
    """
    根据分数获取健康等级

    Args:
        score: 健康分数（0 - 100）

    Returns:
        健康等级
    """
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "一般"
    elif score >= 60:
        return "偏差"
    else:
        return "较差"
