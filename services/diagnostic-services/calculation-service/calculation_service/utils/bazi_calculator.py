"""
bazi_calculator - 索克生活项目模块
"""

from datetime import date

import lunardate

"""
八字计算器

用于计算生辰八字和五行分析
"""


class BaziCalculator:
    """八字计算器"""

    def __init__(self) -> None:
        """初始化计算器"""
        self.tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.dizhi = [
            "子",
            "丑",
            "寅",
            "卯",
            "辰",
            "巳",
            "午",
            "未",
            "申",
            "酉",
            "戌",
            "亥",
        ]

        # 天干五行属性
        self.tiangan_wuxing = {
            "甲": "木",
            "乙": "木",
            "丙": "火",
            "丁": "火",
            "戊": "土",
            "己": "土",
            "庚": "金",
            "辛": "金",
            "壬": "水",
            "癸": "水",
        }

        # 地支五行属性
        self.dizhi_wuxing = {
            "子": "水",
            "丑": "土",
            "寅": "木",
            "卯": "木",
            "辰": "土",
            "巳": "火",
            "午": "火",
            "未": "土",
            "申": "金",
            "酉": "金",
            "戌": "土",
            "亥": "水",
        }

        # 时辰对应地支
        self.hour_dizhi = {
            (23, 1): "子",
            (1, 3): "丑",
            (3, 5): "寅",
            (5, 7): "卯",
            (7, 9): "辰",
            (9, 11): "巳",
            (11, 13): "午",
            (13, 15): "未",
            (15, 17): "申",
            (17, 19): "酉",
            (19, 21): "戌",
            (21, 23): "亥",
        }

    def calculate_bazi(self, birth_date: date, birth_time: str | None = None) -> dict:
        """
        计算生辰八字

        Args:
            birth_date: 出生日期
            birth_time: 出生时间 (HH:MM格式)

        Returns:
            八字信息字典
        """
        # 转换为农历
        lunar_date = lunardate.LunarDate.fromSolarDate(
            birth_date.year, birth_date.month, birth_date.day
        )

        # 计算年柱
        year_ganzhi = self._get_year_ganzhi(birth_date.year)

        # 计算月柱
        month_ganzhi = self._get_month_ganzhi(birth_date.year, birth_date.month)

        # 计算日柱
        day_ganzhi = self._get_day_ganzhi(birth_date)

        # 计算时柱
        hour_ganzhi = (
            self._get_hour_ganzhi(birth_time, day_ganzhi) if birth_time else None
        )

        # 计算五行
        wuxing = self._calculate_wuxing(
            year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi
        )

        return {
            "year_ganzhi": year_ganzhi,
            "month_ganzhi": month_ganzhi,
            "day_ganzhi": day_ganzhi,
            "hour_ganzhi": hour_ganzhi,
            "lunar_date": {
                "year": lunar_date.year,
                "month": lunar_date.month,
                "day": lunar_date.day,
                "isleap": getattr(lunar_date, "isLeapMonth", False),
            },
            "wuxing": wuxing,
        }

    def _get_year_ganzhi(self, year: int) -> str:
        """获取年柱干支"""
        # 以1984年甲子为基准
        base_year = 1984
        year_diff = year - base_year

        tiangan_index = year_diff % 10
        dizhi_index = year_diff % 12

        return self.tiangan[tiangan_index] + self.dizhi[dizhi_index]

    def _get_month_ganzhi(self, year: int, month: int) -> str:
        """获取月柱干支"""
        # 月柱天干根据年干推算
        year_ganzhi = self._get_year_ganzhi(year)
        year_tiangan = year_ganzhi[0]

        # 月柱天干起法：甲己之年丙作首
        month_tiangan_start = {
            "甲": 2,
            "己": 2,  # 丙
            "乙": 4,
            "庚": 4,  # 戊
            "丙": 6,
            "辛": 6,  # 庚
            "丁": 8,
            "壬": 8,  # 壬
            "戊": 0,
            "癸": 0,  # 甲
        }

        start_index = month_tiangan_start[year_tiangan]
        month_tiangan_index = (start_index + month - 1) % 10

        # 月柱地支固定：寅月开始
        month_dizhi_index = (month + 1) % 12  # 正月为寅月

        return self.tiangan[month_tiangan_index] + self.dizhi[month_dizhi_index]

    def _get_day_ganzhi(self, birth_date: date) -> str:
        """获取日柱干支"""
        # 以1900年1月1日甲戌为基准
        base_date = date(1900, 1, 1)
        days_diff = (birth_date - base_date).days

        # 1900年1月1日为甲戌日，甲为0，戌为10
        tiangan_index = (days_diff + 0) % 10
        dizhi_index = (days_diff + 10) % 12

        return self.tiangan[tiangan_index] + self.dizhi[dizhi_index]

    def _get_hour_ganzhi(self, birth_time: str, day_ganzhi: str) -> str:
        """获取时柱干支"""
        if not birth_time:
            return None

        try:
            hour, minute = map(int, birth_time.split(":"))
        except (ValueError, AttributeError):
            return None

        # 确定时辰地支
        hour_dizhi = None
        for (start, end), dizhi in self.hour_dizhi.items():
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                hour_dizhi = dizhi
                break

        if not hour_dizhi:
            return None

        # 时柱天干根据日干推算
        day_tiangan = day_ganzhi[0]

        # 时柱天干起法：甲己还加甲
        hour_tiangan_start = {
            "甲": 0,
            "己": 0,  # 甲
            "乙": 2,
            "庚": 2,  # 丙
            "丙": 4,
            "辛": 4,  # 戊
            "丁": 6,
            "壬": 6,  # 庚
            "戊": 8,
            "癸": 8,  # 壬
        }

        start_index = hour_tiangan_start[day_tiangan]
        dizhi_index = self.dizhi.index(hour_dizhi)
        hour_tiangan_index = (start_index + dizhi_index) % 10

        return self.tiangan[hour_tiangan_index] + hour_dizhi

    def _calculate_wuxing(
        self,
        year_ganzhi: str,
        month_ganzhi: str,
        day_ganzhi: str,
        hour_ganzhi: str | None,
    ) -> dict:
        """计算五行分布"""
        wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

        # 统计各柱的五行
        for ganzhi in [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi]:
            if ganzhi:
                tiangan = ganzhi[0]
                dizhi = ganzhi[1]

                # 天干五行
                wuxing_count[self.tiangan_wuxing[tiangan]] += 1

                # 地支五行
                wuxing_count[self.dizhi_wuxing[dizhi]] += 1

        return {
            "wood": wuxing_count["木"],
            "fire": wuxing_count["火"],
            "earth": wuxing_count["土"],
            "metal": wuxing_count["金"],
            "water": wuxing_count["水"],
            "total": sum(wuxing_count.values()),
            "dominant_element": max(wuxing_count, key=wuxing_count.get),
            "weakest_element": min(wuxing_count, key=wuxing_count.get),
        }

    def analyze_constitution_from_bazi(self, bazi: dict) -> dict:
        """
        根据八字分析体质

        Args:
            bazi: 八字信息

        Returns:
            体质分析结果
        """
        wuxing = bazi["wuxing"]
        dominant = wuxing["dominant_element"]
        weakest = wuxing["weakest_element"]

        # 体质类型判断
        constitution_types = {
            "木": "木型体质",
            "火": "火型体质",
            "土": "土型体质",
            "金": "金型体质",
            "水": "水型体质",
        }

        constitution_type = constitution_types.get(dominant, "平和体质")

        # 体质特征
        constitution_characteristics = {
            "木型体质": ["性格急躁", "易怒", "筋骨强健", "面色青黄"],
            "火型体质": ["性格活泼", "易兴奋", "面色红润", "心火旺盛"],
            "土型体质": ["性格稳重", "消化良好", "肌肉丰满", "面色黄润"],
            "金型体质": ["性格刚毅", "皮肤白皙", "呼吸深长", "声音洪亮"],
            "水型体质": ["性格沉静", "骨骼强健", "面色黑润", "精力充沛"],
        }

        # 健康风险
        health_risks = {
            "木型体质": ["肝胆疾病", "筋骨损伤", "情志病"],
            "火型体质": ["心血管疾病", "失眠", "口疮"],
            "土型体质": ["脾胃疾病", "湿症", "肥胖"],
            "金型体质": ["肺部疾病", "皮肤病", "大肠疾病"],
            "水型体质": ["肾脏疾病", "骨关节病", "生殖系统疾病"],
        }

        # 调养建议
        care_advice = {
            "木型体质": ["疏肝理气", "调畅情志", "适度运动"],
            "火型体质": ["清心降火", "养心安神", "避免过度兴奋"],
            "土型体质": ["健脾化湿", "饮食清淡", "规律作息"],
            "金型体质": ["润肺止咳", "滋阴润燥", "避免辛燥"],
            "水型体质": ["补肾益精", "温阳散寒", "节制房事"],
        }

        return {
            "constitution_type": constitution_type,
            "dominant_element": dominant,
            "weakest_element": weakest,
            "characteristics": constitution_characteristics.get(constitution_type, []),
            "health_risks": health_risks.get(constitution_type, []),
            "care_advice": care_advice.get(constitution_type, []),
            "wuxing_balance": self._analyze_wuxing_balance(wuxing),
        }

    def _analyze_wuxing_balance(self, wuxing: dict) -> dict:
        """分析五行平衡状态"""
        total = wuxing["total"]
        if total == 0:
            return {"status": "无法分析", "description": "五行信息不完整"}

        # 计算各元素比例
        proportions = {
            element: count / total
            for element, count in wuxing.items()
            if element not in ["total", "dominant_element", "weakest_element"]
        }

        # 判断平衡状态
        max_prop = max(proportions.values())
        min_prop = min(proportions.values())

        if max_prop - min_prop <= 0.3:
            status = "平衡"
            description = "五行分布相对均衡，体质较为平和"
        elif max_prop >= 0.4:
            status = "偏盛"
            dominant = max(proportions, key=proportions.get)
            description = f"{dominant}行偏盛，需要适当抑制"
        elif min_prop <= 0.1:
            status = "偏虚"
            weakest = min(proportions, key=proportions.get)
            description = f"{weakest}行偏虚，需要适当补充"
        else:
            status = "轻微失衡"
            description = "五行略有失衡，注意调理"

        return {
            "status": status,
            "description": description,
            "proportions": proportions,
        }
