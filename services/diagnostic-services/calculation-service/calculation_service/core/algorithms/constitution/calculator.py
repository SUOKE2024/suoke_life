"""
calculator - 索克生活项目模块
"""

from .data import (
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

"""
八字体质分析计算器

实现基于出生时间的体质分析核心算法
"""


    CONSTITUTION_DATA,
    TIANGAN_WUXING,
    DIZHI_WUXING,
    WUXING_RELATIONS,
    BAZI_STRENGTH_CRITERIA,
    BAZI_CONSTITUTION_MAP,
    SEASON_WUXING,
    CONSTITUTION_TREATMENT,
    CONSTITUTION_DISEASE_TENDENCY
)

class ConstitutionCalculator:
    """八字体质分析计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 月令对应地支
        self.month_dizhi = {
            1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳", 6: "午",
            7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥", 12: "子"
        }
        
        # 时辰对应地支
        self.hour_dizhi = {
            (23, 1): "子", (1, 3): "丑", (3, 5): "寅", (5, 7): "卯",
            (7, 9): "辰", (9, 11): "巳", (11, 13): "午", (13, 15): "未",
            (15, 17): "申", (17, 19): "酉", (19, 21): "戌", (21, 23): "亥"
        }
    
    def get_bazi(self, birth_datetime: datetime) -> Dict[str, str]:
        """
        计算八字
        
        Args:
            birth_datetime: 出生时间
            
        Returns:
            八字信息
        """
        year = birth_datetime.year
        month = birth_datetime.month
        day = birth_datetime.day
        hour = birth_datetime.hour
        
        # 计算年柱
        year_ganzhi = self._get_year_ganzhi(year)
        
        # 计算月柱
        month_ganzhi = self._get_month_ganzhi(year, month)
        
        # 计算日柱
        day_ganzhi = self._get_day_ganzhi(birth_datetime.date())
        
        # 计算时柱
        hour_ganzhi = self._get_hour_ganzhi(day_ganzhi[0], hour)
        
        return {
            "年柱": year_ganzhi,
            "月柱": month_ganzhi,
            "日柱": day_ganzhi,
            "时柱": hour_ganzhi,
            "年干": year_ganzhi[0],
            "年支": year_ganzhi[1],
            "月干": month_ganzhi[0],
            "月支": month_ganzhi[1],
            "日干": day_ganzhi[0],
            "日支": day_ganzhi[1],
            "时干": hour_ganzhi[0],
            "时支": hour_ganzhi[1]
        }
    
    def _get_year_ganzhi(self, year: int) -> str:
        """计算年柱干支"""
        # 以1984年甲子为基准
        base_year = 1984
        year_diff = year - base_year
        
        tiangan_index = year_diff % 10
        dizhi_index = year_diff % 12
        
        return self.tiangan[tiangan_index] + self.dizhi[dizhi_index]
    
    def _get_month_ganzhi(self, year: int, month: int) -> str:
        """计算月柱干支"""
        # 月支固定
        month_zhi = self.month_dizhi[month]
        
        # 月干根据年干推算
        year_ganzhi = self._get_year_ganzhi(year)
        year_gan = year_ganzhi[0]
        
        # 月干起法：甲己之年丙作首
        month_gan_start = {
            "甲": "丙", "己": "丙",
            "乙": "戊", "庚": "戊", 
            "丙": "庚", "辛": "庚",
            "丁": "壬", "壬": "壬",
            "戊": "甲", "癸": "甲"
        }
        
        start_gan = month_gan_start[year_gan]
        start_index = self.tiangan.index(start_gan)
        month_gan_index = (start_index + month - 1) % 10
        
        return self.tiangan[month_gan_index] + month_zhi
    
    def _get_day_ganzhi(self, birth_date: date) -> str:
        """计算日柱干支"""
        # 以1984年1月1日甲子日为基准
        base_date = date(1984, 1, 1)
        days_diff = (birth_date - base_date).days
        
        tiangan_index = days_diff % 10
        dizhi_index = days_diff % 12
        
        return self.tiangan[tiangan_index] + self.dizhi[dizhi_index]
    
    def _get_hour_ganzhi(self, day_gan: str, hour: int) -> str:
        """计算时柱干支"""
        # 确定时支
        hour_zhi = None
        for (start, end), zhi in self.hour_dizhi.items():
            if start > end:  # 跨日情况
                if hour >= start or hour < end:
                    hour_zhi = zhi
                    break
            else:
                if start <= hour < end:
                    hour_zhi = zhi
                    break
        
        if hour_zhi is None:
            hour_zhi = "子"  # 默认值
        
        # 时干根据日干推算
        hour_gan_start = {
            "甲": "甲", "己": "甲",
            "乙": "丙", "庚": "丙",
            "丙": "戊", "辛": "戊", 
            "丁": "庚", "壬": "庚",
            "戊": "壬", "癸": "壬"
        }
        
        start_gan = hour_gan_start[day_gan]
        start_index = self.tiangan.index(start_gan)
        hour_zhi_index = self.dizhi.index(hour_zhi)
        hour_gan_index = (start_index + hour_zhi_index) % 10
        
        return self.tiangan[hour_gan_index] + hour_zhi
    
    def analyze_wuxing_strength(self, bazi: Dict[str, str]) -> Dict[str, int]:
        """
        分析八字五行强弱
        
        Args:
            bazi: 八字信息
            
        Returns:
            五行强弱分析
        """
        wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        
        # 统计天干五行
        for gan_key in ["年干", "月干", "日干", "时干"]:
            gan = bazi[gan_key]
            wuxing = TIANGAN_WUXING[gan]
            wuxing_count[wuxing] += 1
        
        # 统计地支五行
        for zhi_key in ["年支", "月支", "日支", "时支"]:
            zhi = bazi[zhi_key]
            wuxing = DIZHI_WUXING[zhi]
            wuxing_count[wuxing] += 1
        
        return wuxing_count
    
    def determine_constitution_type(self, wuxing_strength: Dict[str, int], bazi: Dict[str, str]) -> str:
        """
        确定体质类型
        
        Args:
            wuxing_strength: 五行强弱
            bazi: 八字信息
            
        Returns:
            体质类型
        """
        # 找出最强和最弱的五行
        max_wuxing = max(wuxing_strength, key=wuxing_strength.get)
        min_wuxing = min(wuxing_strength, key=wuxing_strength.get)
        
        max_count = wuxing_strength[max_wuxing]
        min_count = wuxing_strength[min_wuxing]
        
        # 判断日主强弱
        day_gan = bazi["日干"]
        day_wuxing = TIANGAN_WUXING[day_gan]
        day_strength = wuxing_strength[day_wuxing]
        
        # 根据五行强弱确定体质
        if max_count >= 3:
            # 某五行过旺
            constitution_key = f"{max_wuxing}旺"
            if constitution_key in BAZI_CONSTITUTION_MAP:
                return BAZI_CONSTITUTION_MAP[constitution_key]["体质类型"]
            else:
                return f"{max_wuxing}质体质"
        elif min_count == 0:
            # 某五行缺失
            constitution_key = f"{min_wuxing}弱"
            if constitution_key in BAZI_CONSTITUTION_MAP:
                return BAZI_CONSTITUTION_MAP[constitution_key]["体质类型"]
            else:
                return f"{min_wuxing}虚体质"
        else:
            # 根据日主五行确定基本体质
            return f"{day_wuxing}质体质"
    
    def analyze_constitution(self, birth_datetime) -> Dict:
        """
        综合体质分析
        
        Args:
            birth_datetime: 出生时间（datetime对象或dict）
            
        Returns:
            体质分析结果
        """
        # 处理输入参数
        if isinstance(birth_datetime, dict):
            # 如果是dict，转换为datetime对象
            birth_dt = datetime(
                year=birth_datetime["year"],
                month=birth_datetime["month"],
                day=birth_datetime["day"],
                hour=birth_datetime.get("hour", 12)  # 默认中午12点
            )
        else:
            birth_dt = birth_datetime
        
        # 计算八字
        bazi = self.get_bazi(birth_dt)
        
        # 分析五行强弱
        wuxing_strength = self.analyze_wuxing_strength(bazi)
        
        # 确定体质类型
        constitution_type = self.determine_constitution_type(wuxing_strength, bazi)
        
        # 获取体质详细信息
        constitution_info = CONSTITUTION_DATA.get(constitution_type, {})
        
        # 分析季节影响
        birth_month = birth_dt.month
        birth_season = self._get_season(birth_month)
        season_influence = self._analyze_season_influence(constitution_type, birth_season)
        
        # 生成调理建议
        treatment_advice = CONSTITUTION_TREATMENT.get(constitution_type, {})
        
        # 疾病易感性分析
        disease_tendency = CONSTITUTION_DISEASE_TENDENCY.get(constitution_type, {})
        
        # 五行平衡分析
        balance_analysis = self._analyze_wuxing_balance(wuxing_strength)
        
        return {
            "出生时间": birth_dt.strftime("%Y年%m月%d日 %H时"),
            "八字信息": {
                "年柱": bazi["年柱"],
                "月柱": bazi["月柱"], 
                "日柱": bazi["日柱"],
                "时柱": bazi["时柱"]
            },
            "体质类型": constitution_type,  # 提升到顶层
            "体质分析": {
                "体质类型": constitution_type,
                "体质特征": constitution_info.get("体质特征", []),
                "易患疾病": constitution_info.get("易患疾病", []),
                "养生原则": constitution_info.get("养生原则", [])
            },
            "五行强弱": wuxing_strength,
            "五行分析": {
                "平衡状态": balance_analysis,
                "日主": f"{bazi['日干']}({TIANGAN_WUXING[bazi['日干']]})"
            },
            "调理建议": treatment_advice,
            "饮食宜忌": constitution_info.get("饮食宜忌", {}),
            "季节影响": season_influence,
            "疾病易感性": disease_tendency,
            "个性化建议": self._generate_personalized_advice(
                constitution_type, wuxing_strength, birth_season
            ),
            "养生要点": constitution_info.get("养生原则", [])
        }
    
    def calculate_bazi(self, year_or_birth_info, month=None, day=None, hour=None) -> Dict:
        """
        计算八字（兼容测试）
        
        Args:
            year_or_birth_info: 年份或出生信息字典
            month: 月份（当第一个参数是年份时使用）
            day: 日期（当第一个参数是年份时使用）
            hour: 小时（当第一个参数是年份时使用）
            
        Returns:
            八字信息
        """
        if isinstance(year_or_birth_info, dict):
            # 字典格式
            birth_info = year_or_birth_info
            birth_dt = datetime(
                year=birth_info["year"],
                month=birth_info["month"],
                day=birth_info["day"],
                hour=birth_info.get("hour", 12)
            )
        else:
            # 分别传递参数格式
            birth_dt = datetime(
                year=year_or_birth_info,
                month=month,
                day=day,
                hour=hour if hour is not None else 12
            )
        
        return self.get_bazi(birth_dt)
    
    def _get_season(self, month: int) -> str:
        """根据月份确定季节"""
        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"
    
    def _analyze_season_influence(self, constitution_type: str, birth_season: str) -> Dict:
        """分析季节对体质的影响"""
        constitution_info = CONSTITUTION_DATA.get(constitution_type, {})
        best_season = constitution_info.get("最佳季节", "")
        worst_season = constitution_info.get("不利季节", "")
        
        # 判断出生季节的影响
        if birth_season == best_season:
            influence = "有利"
            description = f"出生在{birth_season}季，与体质相合，先天禀赋较好"
        elif birth_season == worst_season:
            influence = "不利"
            description = f"出生在{birth_season}季，与体质相冲，需要特别调养"
        else:
            influence = "中性"
            description = f"出生在{birth_season}季，对体质影响中等"
        
        return {
            "出生季节": birth_season,
            "影响程度": influence,
            "影响描述": description,
            "最佳季节": best_season,
            "不利季节": worst_season,
            "季节调养": self._get_seasonal_advice(constitution_type, birth_season)
        }
    
    def _analyze_wuxing_balance(self, wuxing_strength: Dict[str, int]) -> str:
        """分析五行平衡状态"""
        total = sum(wuxing_strength.values())
        average = total / 5
        
        # 计算偏差
        deviations = {k: abs(v - average) for k, v in wuxing_strength.items()}
        max_deviation = max(deviations.values())
        
        if max_deviation <= 0.5:
            return "五行平衡"
        elif max_deviation <= 1.0:
            return "轻度失衡"
        elif max_deviation <= 1.5:
            return "中度失衡"
        else:
            return "严重失衡"
    
    def _get_seasonal_advice(self, constitution_type: str, season: str) -> List[str]:
        """获取季节性调养建议"""
        base_advice = {
            "春": ["疏肝理气", "适度运动", "调畅情志"],
            "夏": ["清心降火", "避免过热", "静心养神"],
            "秋": ["润肺养阴", "防燥护肤", "收敛精神"],
            "冬": ["温肾助阳", "避免寒凉", "早睡晚起"]
        }
        
        constitution_wuxing = constitution_type[0] if constitution_type.endswith("质体质") else ""
        season_wuxing = SEASON_WUXING.get(season, "")
        
        advice = base_advice.get(season, [])
        
        # 根据体质与季节的关系调整建议
        if constitution_wuxing == season_wuxing:
            advice.append(f"当季与体质相合，适宜进补调养")
        elif constitution_wuxing in WUXING_RELATIONS["相克"] and WUXING_RELATIONS["相克"][constitution_wuxing] == season_wuxing:
            advice.append(f"当季克制体质，需要特别注意防护")
        
        return advice
    
    def _generate_personalized_advice(self, constitution_type: str, wuxing_strength: Dict[str, int], birth_season: str) -> List[str]:
        """生成个性化建议"""
        advice = []
        
        # 基于体质类型的建议
        constitution_info = CONSTITUTION_DATA.get(constitution_type, {})
        advice.extend(constitution_info.get("养生原则", []))
        
        # 基于五行失衡的建议
        max_wuxing = max(wuxing_strength, key=wuxing_strength.get)
        min_wuxing = min(wuxing_strength, key=wuxing_strength.get)
        
        if wuxing_strength[max_wuxing] >= 3:
            advice.append(f"{max_wuxing}气过旺，需要适当泄耗")
        
        if wuxing_strength[min_wuxing] == 0:
            advice.append(f"缺乏{min_wuxing}气，需要适当补充")
        
        # 基于出生季节的建议
        seasonal_advice = self._get_seasonal_advice(constitution_type, birth_season)
        advice.extend(seasonal_advice)
        
        return list(set(advice))  # 去重
    
    def get_constitution_compatibility(self, person1_birth: datetime, person2_birth: datetime) -> Dict:
        """
        分析两人体质相配性
        
        Args:
            person1_birth: 第一人出生时间
            person2_birth: 第二人出生时间
            
        Returns:
            相配性分析结果
        """
        # 分析两人体质
        constitution1 = self.analyze_constitution(person1_birth)
        constitution2 = self.analyze_constitution(person2_birth)
        
        type1 = constitution1["体质类型"]
        type2 = constitution2["体质类型"]
        
        # 获取五行属性
        wuxing1 = type1[0] if type1.endswith("质体质") else ""
        wuxing2 = type2[0] if type2.endswith("质体质") else ""
        
        # 分析五行关系
        compatibility = self._analyze_wuxing_compatibility(wuxing1, wuxing2)
        
        return {
            "人员1": {
                "体质类型": type1,
                "五行属性": wuxing1
            },
            "人员2": {
                "体质类型": type2,
                "五行属性": wuxing2
            },
            "相配性": compatibility,
            "建议": self._get_compatibility_advice(wuxing1, wuxing2, compatibility)
        }
    
    def _analyze_wuxing_compatibility(self, wuxing1: str, wuxing2: str) -> str:
        """分析五行相配性"""
        if wuxing1 == wuxing2:
            return "同类相助"
        elif WUXING_RELATIONS["相生"].get(wuxing1) == wuxing2:
            return "相生互补"
        elif WUXING_RELATIONS["相生"].get(wuxing2) == wuxing1:
            return "相生互补"
        elif WUXING_RELATIONS["相克"].get(wuxing1) == wuxing2:
            return "相克制约"
        elif WUXING_RELATIONS["相克"].get(wuxing2) == wuxing1:
            return "相克制约"
        else:
            return "关系平和"
    
    def _get_compatibility_advice(self, wuxing1: str, wuxing2: str, compatibility: str) -> List[str]:
        """获取相配性建议"""
        advice_map = {
            "同类相助": [
                "体质相同，容易理解对方",
                "注意避免共同的体质弱点",
                "可以采用相同的养生方法"
            ],
            "相生互补": [
                "体质互补，相得益彰",
                "可以相互弥补体质不足",
                "建议多交流养生心得"
            ],
            "相克制约": [
                "体质相克，需要相互包容",
                "注意避免冲突和争执",
                "可以通过中间五行调和"
            ],
            "关系平和": [
                "体质关系平和，相处融洽",
                "可以相互学习不同的养生方法",
                "注意保持各自的体质特色"
            ]
        }
        
        return advice_map.get(compatibility, ["建议咨询专业医师"]) 