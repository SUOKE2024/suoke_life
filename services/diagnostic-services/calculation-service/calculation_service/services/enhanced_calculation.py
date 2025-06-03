"""
增强的算诊服务

基于传统中医理论和现代算法，实现更精确的中医算诊功能。
包括子午流注、八字体质、五运六气、八卦配属等核心算法。
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import calendar
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

class ConstitutionType(str, Enum):
    """体质类型"""
    BALANCED = "平和质"
    QI_DEFICIENCY = "气虚质"
    YANG_DEFICIENCY = "阳虚质"
    YIN_DEFICIENCY = "阴虚质"
    PHLEGM_DAMPNESS = "痰湿质"
    DAMP_HEAT = "湿热质"
    BLOOD_STASIS = "血瘀质"
    QI_STAGNATION = "气郁质"
    SPECIAL = "特禀质"

class Element(str, Enum):
    """五行"""
    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"

class Organ(str, Enum):
    """脏腑"""
    LIVER = "肝"
    HEART = "心"
    SPLEEN = "脾"
    LUNG = "肺"
    KIDNEY = "肾"
    GALLBLADDER = "胆"
    SMALL_INTESTINE = "小肠"
    STOMACH = "胃"
    LARGE_INTESTINE = "大肠"
    BLADDER = "膀胱"
    TRIPLE_HEATER = "三焦"
    PERICARDIUM = "心包"

@dataclass
class BirthInfo:
    """出生信息"""
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    gender: str = "男"  # 男/女
    location: Optional[str] = None

@dataclass
class MeridianFlow:
    """子午流注信息"""
    time_period: str      # 时辰
    primary_organ: Organ  # 主要脏腑
    secondary_organ: Organ # 次要脏腑
    element: Element      # 对应五行
    energy_level: str     # 能量水平
    recommendations: List[str]  # 养生建议

@dataclass
class ConstitutionAnalysis:
    """体质分析结果"""
    primary_constitution: ConstitutionType
    secondary_constitution: Optional[ConstitutionType]
    constitution_scores: Dict[ConstitutionType, float]
    characteristics: List[str]
    health_tendencies: List[str]
    lifestyle_recommendations: List[str]
    dietary_recommendations: List[str]
    exercise_recommendations: List[str]
    confidence: float

@dataclass
class FiveElementsAnalysis:
    """五运六气分析结果"""
    birth_element: Element
    current_element: Element
    element_balance: Dict[Element, float]
    seasonal_influence: str
    climate_adaptation: List[str]
    health_predictions: List[str]
    preventive_measures: List[str]
    confidence: float

@dataclass
class BaguaAnalysis:
    """八卦分析结果"""
    birth_gua: str        # 出生卦象
    current_gua: str      # 当前卦象
    personality_traits: List[str]
    life_tendencies: List[str]
    health_aspects: List[str]
    fortune_guidance: List[str]
    confidence: float

@dataclass
class ComprehensiveCalculation:
    """综合算诊结果"""
    birth_info: BirthInfo
    meridian_flow: MeridianFlow
    constitution_analysis: ConstitutionAnalysis
    five_elements_analysis: FiveElementsAnalysis
    bagua_analysis: BaguaAnalysis
    overall_assessment: str
    priority_recommendations: List[str]
    confidence: float

class MeridianFlowCalculator:
    """子午流注计算器"""
    
    def __init__(self):
        # 十二时辰对应的脏腑
        self.meridian_schedule = {
            "子时": (23, 1, Organ.GALLBLADDER, Element.WOOD),
            "丑时": (1, 3, Organ.LIVER, Element.WOOD),
            "寅时": (3, 5, Organ.LUNG, Element.METAL),
            "卯时": (5, 7, Organ.LARGE_INTESTINE, Element.METAL),
            "辰时": (7, 9, Organ.STOMACH, Element.EARTH),
            "巳时": (9, 11, Organ.SPLEEN, Element.EARTH),
            "午时": (11, 13, Organ.HEART, Element.FIRE),
            "未时": (13, 15, Organ.SMALL_INTESTINE, Element.FIRE),
            "申时": (15, 17, Organ.BLADDER, Element.WATER),
            "酉时": (17, 19, Organ.KIDNEY, Element.WATER),
            "戌时": (19, 21, Organ.PERICARDIUM, Element.FIRE),
            "亥时": (21, 23, Organ.TRIPLE_HEATER, Element.FIRE)
        }
        
        # 脏腑养生建议
        self.organ_recommendations = {
            Organ.LIVER: [
                "保持心情舒畅，避免愤怒",
                "适当运动，促进气血流通",
                "少食辛辣，多食青色食物"
            ],
            Organ.HEART: [
                "保持平和心态，避免过度兴奋",
                "适量运动，不宜剧烈",
                "多食红色食物，如红枣、枸杞"
            ],
            Organ.SPLEEN: [
                "规律饮食，细嚼慢咽",
                "避免过思，保持心情愉快",
                "多食黄色食物，如小米、南瓜"
            ],
            Organ.LUNG: [
                "深呼吸，多到空气清新处",
                "避免悲伤，保持乐观",
                "多食白色食物，如梨、百合"
            ],
            Organ.KIDNEY: [
                "避免过度劳累，保证充足睡眠",
                "节制房事，保养精气",
                "多食黑色食物，如黑豆、黑芝麻"
            ]
        }
    
    def calculate_current_flow(self, current_time: datetime = None) -> MeridianFlow:
        """计算当前时刻的子午流注"""
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        
        # 确定当前时辰
        for time_name, (start_hour, end_hour, organ, element) in self.meridian_schedule.items():
            if start_hour <= hour < end_hour or (start_hour > end_hour and (hour >= start_hour or hour < end_hour)):
                # 计算能量水平
                energy_level = self._calculate_energy_level(hour, start_hour, end_hour)
                
                # 获取次要脏腑（相表里关系）
                secondary_organ = self._get_paired_organ(organ)
                
                # 获取养生建议
                recommendations = self.organ_recommendations.get(organ, [])
                
                return MeridianFlow(
                    time_period=time_name,
                    primary_organ=organ,
                    secondary_organ=secondary_organ,
                    element=element,
                    energy_level=energy_level,
                    recommendations=recommendations
                )
        
        # 默认返回（不应该到达这里）
        return MeridianFlow(
            time_period="未知",
            primary_organ=Organ.HEART,
            secondary_organ=Organ.SMALL_INTESTINE,
            element=Element.FIRE,
            energy_level="正常",
            recommendations=[]
        )
    
    def _calculate_energy_level(self, current_hour: int, start_hour: int, end_hour: int) -> str:
        """计算能量水平"""
        # 计算在时辰内的相对位置
        if start_hour <= end_hour:
            duration = end_hour - start_hour
            elapsed = current_hour - start_hour
        else:  # 跨日时辰
            duration = (24 - start_hour) + end_hour
            if current_hour >= start_hour:
                elapsed = current_hour - start_hour
            else:
                elapsed = (24 - start_hour) + current_hour
        
        relative_position = elapsed / duration
        
        # 能量曲线：开始低，中间高，结束低
        energy_curve = math.sin(relative_position * math.pi)
        
        if energy_curve > 0.7:
            return "旺盛"
        elif energy_curve > 0.3:
            return "正常"
        else:
            return "较弱"
    
    def _get_paired_organ(self, organ: Organ) -> Organ:
        """获取表里相配的脏腑"""
        pairs = {
            Organ.LIVER: Organ.GALLBLADDER,
            Organ.GALLBLADDER: Organ.LIVER,
            Organ.HEART: Organ.SMALL_INTESTINE,
            Organ.SMALL_INTESTINE: Organ.HEART,
            Organ.SPLEEN: Organ.STOMACH,
            Organ.STOMACH: Organ.SPLEEN,
            Organ.LUNG: Organ.LARGE_INTESTINE,
            Organ.LARGE_INTESTINE: Organ.LUNG,
            Organ.KIDNEY: Organ.BLADDER,
            Organ.BLADDER: Organ.KIDNEY,
            Organ.PERICARDIUM: Organ.TRIPLE_HEATER,
            Organ.TRIPLE_HEATER: Organ.PERICARDIUM
        }
        return pairs.get(organ, organ)

class ConstitutionCalculator:
    """体质计算器"""
    
    def __init__(self):
        # 天干地支与体质的对应关系
        self.heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 五行与体质的对应
        self.element_constitution = {
            Element.WOOD: [ConstitutionType.QI_STAGNATION, ConstitutionType.BALANCED],
            Element.FIRE: [ConstitutionType.YIN_DEFICIENCY, ConstitutionType.DAMP_HEAT],
            Element.EARTH: [ConstitutionType.PHLEGM_DAMPNESS, ConstitutionType.QI_DEFICIENCY],
            Element.METAL: [ConstitutionType.QI_DEFICIENCY, ConstitutionType.SPECIAL],
            Element.WATER: [ConstitutionType.YANG_DEFICIENCY, ConstitutionType.BLOOD_STASIS]
        }
        
        # 体质特征描述
        self.constitution_characteristics = {
            ConstitutionType.BALANCED: [
                "体形匀称，面色红润",
                "精力充沛，睡眠良好",
                "性格开朗，适应力强"
            ],
            ConstitutionType.QI_DEFICIENCY: [
                "容易疲劳，气短懒言",
                "面色偏白，容易出汗",
                "抵抗力较弱，易感冒"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "畏寒怕冷，手足不温",
                "精神不振，睡眠偏多",
                "大便溏薄，小便清长"
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                "形体偏瘦，手足心热",
                "面色潮红，眼睛干涩",
                "口燥咽干，喜冷饮"
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                "形体肥胖，腹部肥满",
                "面部皮肤油脂较多",
                "容易困倦，身重不爽"
            ],
            ConstitutionType.DAMP_HEAT: [
                "面垢油腻，容易生痤疮",
                "口苦口干，身重困倦",
                "大便黏腻，小便短黄"
            ],
            ConstitutionType.BLOOD_STASIS: [
                "肤色晦暗，色素沉着",
                "容易健忘，性情急躁",
                "皮肤粗糙，易生瘀斑"
            ],
            ConstitutionType.QI_STAGNATION: [
                "形体偏瘦，情绪不稳定",
                "容易紧张焦虑，多愁善感",
                "胸闷不舒，喜叹息"
            ],
            ConstitutionType.SPECIAL: [
                "先天禀赋不足",
                "容易过敏，适应力差",
                "遗传性疾病倾向"
            ]
        }
    
    def calculate_constitution(self, birth_info: BirthInfo) -> ConstitutionAnalysis:
        """计算体质类型"""
        # 计算八字
        year_stem, year_branch = self._get_year_stem_branch(birth_info.year)
        month_stem, month_branch = self._get_month_stem_branch(birth_info.year, birth_info.month)
        day_stem, day_branch = self._get_day_stem_branch(birth_info.year, birth_info.month, birth_info.day)
        hour_stem, hour_branch = self._get_hour_stem_branch(day_stem, birth_info.hour)
        
        # 分析五行强弱
        element_scores = self._analyze_five_elements(
            [year_stem, month_stem, day_stem, hour_stem],
            [year_branch, month_branch, day_branch, hour_branch]
        )
        
        # 计算体质得分
        constitution_scores = self._calculate_constitution_scores(element_scores, birth_info)
        
        # 确定主要体质
        primary_constitution = max(constitution_scores, key=constitution_scores.get)
        
        # 确定次要体质
        sorted_constitutions = sorted(constitution_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_constitution = sorted_constitutions[1][0] if len(sorted_constitutions) > 1 and sorted_constitutions[1][1] > 0.3 else None
        
        # 获取特征描述
        characteristics = self.constitution_characteristics.get(primary_constitution, [])
        
        # 生成健康倾向
        health_tendencies = self._generate_health_tendencies(primary_constitution)
        
        # 生成建议
        lifestyle_recommendations = self._generate_lifestyle_recommendations(primary_constitution)
        dietary_recommendations = self._generate_dietary_recommendations(primary_constitution)
        exercise_recommendations = self._generate_exercise_recommendations(primary_constitution)
        
        # 计算置信度
        confidence = self._calculate_constitution_confidence(constitution_scores)
        
        return ConstitutionAnalysis(
            primary_constitution=primary_constitution,
            secondary_constitution=secondary_constitution,
            constitution_scores=constitution_scores,
            characteristics=characteristics,
            health_tendencies=health_tendencies,
            lifestyle_recommendations=lifestyle_recommendations,
            dietary_recommendations=dietary_recommendations,
            exercise_recommendations=exercise_recommendations,
            confidence=confidence
        )
    
    def _get_year_stem_branch(self, year: int) -> Tuple[str, str]:
        """获取年份的天干地支"""
        # 以1984年甲子年为基准
        base_year = 1984
        offset = (year - base_year) % 60
        
        stem_index = offset % 10
        branch_index = offset % 12
        
        return self.heavenly_stems[stem_index], self.earthly_branches[branch_index]
    
    def _get_month_stem_branch(self, year: int, month: int) -> Tuple[str, str]:
        """获取月份的天干地支"""
        # 月支固定
        month_branches = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
        month_branch = month_branches[month - 1]
        
        # 月干根据年干推算
        year_stem, _ = self._get_year_stem_branch(year)
        year_stem_index = self.heavenly_stems.index(year_stem)
        
        # 月干起法：甲己之年丙作首
        month_stem_base = {0: 2, 1: 2, 2: 4, 3: 4, 4: 6, 5: 6, 6: 8, 7: 8, 8: 0, 9: 0}
        base_index = month_stem_base[year_stem_index]
        month_stem_index = (base_index + month - 1) % 10
        
        return self.heavenly_stems[month_stem_index], month_branch
    
    def _get_day_stem_branch(self, year: int, month: int, day: int) -> Tuple[str, str]:
        """获取日期的天干地支"""
        # 计算从基准日期的天数差
        base_date = datetime(1984, 1, 1)  # 甲子日
        target_date = datetime(year, month, day)
        days_diff = (target_date - base_date).days
        
        stem_index = days_diff % 10
        branch_index = days_diff % 12
        
        return self.heavenly_stems[stem_index], self.earthly_branches[branch_index]
    
    def _get_hour_stem_branch(self, day_stem: str, hour: int) -> Tuple[str, str]:
        """获取时辰的天干地支"""
        # 时支固定
        hour_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        hour_branch_index = (hour + 1) // 2 % 12
        hour_branch = hour_branches[hour_branch_index]
        
        # 时干根据日干推算
        day_stem_index = self.heavenly_stems.index(day_stem)
        hour_stem_base = {0: 0, 1: 0, 2: 2, 3: 2, 4: 4, 5: 4, 6: 6, 7: 6, 8: 8, 9: 8}
        base_index = hour_stem_base[day_stem_index]
        hour_stem_index = (base_index + hour_branch_index) % 10
        
        return self.heavenly_stems[hour_stem_index], hour_branch
    
    def _analyze_five_elements(self, stems: List[str], branches: List[str]) -> Dict[Element, float]:
        """分析五行强弱"""
        # 天干五行
        stem_elements = {
            "甲": Element.WOOD, "乙": Element.WOOD,
            "丙": Element.FIRE, "丁": Element.FIRE,
            "戊": Element.EARTH, "己": Element.EARTH,
            "庚": Element.METAL, "辛": Element.METAL,
            "壬": Element.WATER, "癸": Element.WATER
        }
        
        # 地支五行
        branch_elements = {
            "子": Element.WATER, "丑": Element.EARTH, "寅": Element.WOOD,
            "卯": Element.WOOD, "辰": Element.EARTH, "巳": Element.FIRE,
            "午": Element.FIRE, "未": Element.EARTH, "申": Element.METAL,
            "酉": Element.METAL, "戌": Element.EARTH, "亥": Element.WATER
        }
        
        element_counts = defaultdict(float)
        
        # 统计天干五行
        for stem in stems:
            element = stem_elements.get(stem)
            if element:
                element_counts[element] += 1.0
        
        # 统计地支五行
        for branch in branches:
            element = branch_elements.get(branch)
            if element:
                element_counts[element] += 0.8  # 地支权重稍低
        
        # 归一化
        total = sum(element_counts.values())
        if total > 0:
            for element in element_counts:
                element_counts[element] /= total
        
        return dict(element_counts)
    
    def _calculate_constitution_scores(self, element_scores: Dict[Element, float], 
                                     birth_info: BirthInfo) -> Dict[ConstitutionType, float]:
        """计算体质得分"""
        constitution_scores = defaultdict(float)
        
        # 基于五行分布计算体质倾向
        for element, score in element_scores.items():
            constitutions = self.element_constitution.get(element, [])
            for constitution in constitutions:
                constitution_scores[constitution] += score
        
        # 性别调整
        if birth_info.gender == "女":
            constitution_scores[ConstitutionType.YIN_DEFICIENCY] *= 1.2
            constitution_scores[ConstitutionType.BLOOD_STASIS] *= 1.1
        else:
            constitution_scores[ConstitutionType.YANG_DEFICIENCY] *= 1.1
            constitution_scores[ConstitutionType.QI_DEFICIENCY] *= 1.1
        
        # 季节调整（出生月份）
        season_adjustment = {
            ConstitutionType.YANG_DEFICIENCY: [12, 1, 2],  # 冬季出生
            ConstitutionType.YIN_DEFICIENCY: [6, 7, 8],    # 夏季出生
            ConstitutionType.PHLEGM_DAMPNESS: [3, 4, 5],   # 春季出生
            ConstitutionType.DAMP_HEAT: [6, 7, 8, 9]       # 夏秋出生
        }
        
        for constitution, months in season_adjustment.items():
            if birth_info.month in months:
                constitution_scores[constitution] *= 1.15
        
        # 归一化
        total = sum(constitution_scores.values())
        if total > 0:
            for constitution in constitution_scores:
                constitution_scores[constitution] /= total
        
        return dict(constitution_scores)
    
    def _generate_health_tendencies(self, constitution: ConstitutionType) -> List[str]:
        """生成健康倾向"""
        tendencies = {
            ConstitutionType.QI_DEFICIENCY: [
                "容易感冒，抵抗力弱",
                "消化功能较弱",
                "容易疲劳，精神不振"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "容易腹泻，消化不良",
                "手足冰冷，怕寒",
                "性功能可能偏弱"
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                "容易上火，口干舌燥",
                "失眠多梦",
                "皮肤干燥，便秘"
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                "容易肥胖，代谢缓慢",
                "血脂血糖偏高风险",
                "关节沉重，活动不利"
            ],
            ConstitutionType.DAMP_HEAT: [
                "容易长痘，皮肤油腻",
                "口苦口臭",
                "泌尿系统易感染"
            ],
            ConstitutionType.BLOOD_STASIS: [
                "循环系统问题风险",
                "容易健忘，注意力不集中",
                "皮肤容易瘀斑"
            ],
            ConstitutionType.QI_STAGNATION: [
                "情绪波动大，易抑郁",
                "消化系统功能紊乱",
                "乳腺增生等问题"
            ]
        }
        
        return tendencies.get(constitution, ["体质平和，健康状况良好"])
    
    def _generate_lifestyle_recommendations(self, constitution: ConstitutionType) -> List[str]:
        """生成生活方式建议"""
        recommendations = {
            ConstitutionType.QI_DEFICIENCY: [
                "保证充足睡眠，避免熬夜",
                "避免过度劳累，适当休息",
                "保持心情愉快，避免过度思虑"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "注意保暖，特别是腰腹部",
                "避免生冷食物和环境",
                "适当晒太阳，补充阳气"
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                "避免熬夜，保证睡眠质量",
                "避免过度用眼和用脑",
                "保持环境湿润，避免干燥"
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                "控制体重，避免久坐",
                "保持环境干燥通风",
                "规律作息，避免贪睡"
            ],
            ConstitutionType.DAMP_HEAT: [
                "保持皮肤清洁，避免油腻",
                "避免潮湿闷热环境",
                "戒烟限酒，清淡饮食"
            ]
        }
        
        return recommendations.get(constitution, ["保持规律作息，适度运动"])
    
    def _generate_dietary_recommendations(self, constitution: ConstitutionType) -> List[str]:
        """生成饮食建议"""
        recommendations = {
            ConstitutionType.QI_DEFICIENCY: [
                "多食补气食物：人参、黄芪、大枣",
                "避免生冷，温热饮食",
                "少食多餐，细嚼慢咽"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "多食温阳食物：羊肉、韭菜、生姜",
                "避免寒凉食物",
                "适当食用坚果类"
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                "多食滋阴食物：银耳、百合、枸杞",
                "避免辛辣燥热食物",
                "多饮水，适量食用水果"
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                "清淡饮食，少油少盐",
                "多食健脾化湿食物：薏米、冬瓜",
                "控制甜食和油腻食物"
            ],
            ConstitutionType.DAMP_HEAT: [
                "清热利湿食物：绿豆、苦瓜",
                "避免辛辣油腻食物",
                "多饮水，少饮酒"
            ]
        }
        
        return recommendations.get(constitution, ["均衡饮食，营养搭配"])
    
    def _generate_exercise_recommendations(self, constitution: ConstitutionType) -> List[str]:
        """生成运动建议"""
        recommendations = {
            ConstitutionType.QI_DEFICIENCY: [
                "适合缓和运动：太极拳、八段锦",
                "避免剧烈运动，防止耗气",
                "运动后注意休息"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "适合温和的有氧运动",
                "避免大汗淋漓的运动",
                "运动时注意保暖"
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                "适合静态运动：瑜伽、冥想",
                "避免大量出汗的运动",
                "运动后及时补充水分"
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                "适合有氧运动：快走、游泳",
                "增加运动量，促进代谢",
                "坚持规律运动"
            ],
            ConstitutionType.DAMP_HEAT: [
                "适合出汗的运动，排除湿热",
                "避免在闷热环境运动",
                "运动后及时清洁"
            ]
        }
        
        return recommendations.get(constitution, ["适度运动，循序渐进"])
    
    def _calculate_constitution_confidence(self, scores: Dict[ConstitutionType, float]) -> float:
        """计算体质分析置信度"""
        if not scores:
            return 0.5
        
        # 基于最高分与次高分的差距
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            confidence = (sorted_scores[0] - sorted_scores[1]) + 0.5
        else:
            confidence = sorted_scores[0] + 0.3
        
        return max(0.6, min(0.95, confidence))

class EnhancedCalculationService:
    """增强的算诊服务"""
    
    def __init__(self):
        self.meridian_calculator = MeridianFlowCalculator()
        self.constitution_calculator = ConstitutionCalculator()
        
        logger.info("增强算诊服务初始化完成")
    
    async def comprehensive_calculation(self, birth_info: BirthInfo, 
                                      current_time: datetime = None) -> ComprehensiveCalculation:
        """综合算诊分析"""
        try:
            if current_time is None:
                current_time = datetime.now()
            
            # 子午流注分析
            meridian_flow = self.meridian_calculator.calculate_current_flow(current_time)
            
            # 体质分析
            constitution_analysis = self.constitution_calculator.calculate_constitution(birth_info)
            
            # 五运六气分析（简化实现）
            five_elements_analysis = self._analyze_five_elements_simplified(birth_info, current_time)
            
            # 八卦分析（简化实现）
            bagua_analysis = self._analyze_bagua_simplified(birth_info)
            
            # 综合评估
            overall_assessment = self._generate_overall_assessment(
                constitution_analysis, five_elements_analysis, meridian_flow
            )
            
            # 优先建议
            priority_recommendations = self._generate_priority_recommendations(
                constitution_analysis, meridian_flow, five_elements_analysis
            )
            
            # 综合置信度
            confidence = self._calculate_overall_confidence(
                constitution_analysis.confidence,
                five_elements_analysis.confidence,
                bagua_analysis.confidence
            )
            
            result = ComprehensiveCalculation(
                birth_info=birth_info,
                meridian_flow=meridian_flow,
                constitution_analysis=constitution_analysis,
                five_elements_analysis=five_elements_analysis,
                bagua_analysis=bagua_analysis,
                overall_assessment=overall_assessment,
                priority_recommendations=priority_recommendations,
                confidence=confidence
            )
            
            logger.info(f"综合算诊完成，主要体质: {constitution_analysis.primary_constitution}")
            return result
            
        except Exception as e:
            logger.error(f"综合算诊失败: {e}")
            raise
    
    def _analyze_five_elements_simplified(self, birth_info: BirthInfo, 
                                        current_time: datetime) -> FiveElementsAnalysis:
        """简化的五运六气分析"""
        # 根据出生年份确定主运
        year_element_cycle = [Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER]
        birth_element = year_element_cycle[(birth_info.year - 1984) % 5]
        
        # 根据当前时间确定当前运气
        current_element = year_element_cycle[(current_time.year - 1984) % 5]
        
        # 五行平衡分析
        element_balance = {
            Element.WOOD: 0.2,
            Element.FIRE: 0.2,
            Element.EARTH: 0.2,
            Element.METAL: 0.2,
            Element.WATER: 0.2
        }
        
        # 根据出生元素调整
        element_balance[birth_element] += 0.3
        
        # 季节影响
        season_elements = {
            (3, 4, 5): Element.WOOD,    # 春
            (6, 7, 8): Element.FIRE,    # 夏
            (9, 10, 11): Element.METAL, # 秋
            (12, 1, 2): Element.WATER   # 冬
        }
        
        current_month = current_time.month
        seasonal_element = None
        for months, element in season_elements.items():
            if current_month in months:
                seasonal_element = element
                break
        
        seasonal_influence = f"当前{seasonal_element.value}旺季，宜调养{seasonal_element.value}脏"
        
        return FiveElementsAnalysis(
            birth_element=birth_element,
            current_element=current_element,
            element_balance=element_balance,
            seasonal_influence=seasonal_influence,
            climate_adaptation=["根据季节调整作息", "顺应自然规律"],
            health_predictions=["注意季节性疾病预防"],
            preventive_measures=["加强体质锻炼", "合理膳食"],
            confidence=0.7
        )
    
    def _analyze_bagua_simplified(self, birth_info: BirthInfo) -> BaguaAnalysis:
        """简化的八卦分析"""
        # 根据出生年份确定卦象
        bagua_names = ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"]
        birth_gua = bagua_names[birth_info.year % 8]
        
        # 当前卦象（简化）
        current_gua = bagua_names[datetime.now().year % 8]
        
        # 卦象特征
        gua_traits = {
            "乾": ["刚健", "领导力强", "积极进取"],
            "坤": ["柔顺", "包容性强", "稳重踏实"],
            "震": ["活跃", "行动力强", "容易冲动"],
            "巽": ["温和", "适应性强", "善于沟通"],
            "坎": ["智慧", "深沉", "容易多虑"],
            "离": ["热情", "外向", "容易急躁"],
            "艮": ["稳重", "专注", "有时固执"],
            "兑": ["开朗", "善交际", "情绪化"]
        }
        
        personality_traits = gua_traits.get(birth_gua, ["平和"])
        
        return BaguaAnalysis(
            birth_gua=birth_gua,
            current_gua=current_gua,
            personality_traits=personality_traits,
            life_tendencies=["顺应自然", "和谐发展"],
            health_aspects=["注意心理健康", "保持情绪平衡"],
            fortune_guidance=["把握机遇", "稳步前进"],
            confidence=0.6
        )
    
    def _generate_overall_assessment(self, constitution: ConstitutionAnalysis,
                                   five_elements: FiveElementsAnalysis,
                                   meridian_flow: MeridianFlow) -> str:
        """生成综合评估"""
        assessment_parts = []
        
        # 体质评估
        assessment_parts.append(f"您的主要体质为{constitution.primary_constitution.value}")
        
        if constitution.secondary_constitution:
            assessment_parts.append(f"兼有{constitution.secondary_constitution.value}倾向")
        
        # 五行评估
        assessment_parts.append(f"出生五行属{five_elements.birth_element.value}")
        
        # 当前时辰评估
        assessment_parts.append(f"当前{meridian_flow.time_period}，{meridian_flow.primary_organ.value}经当令")
        
        return "，".join(assessment_parts) + "。"
    
    def _generate_priority_recommendations(self, constitution: ConstitutionAnalysis,
                                         meridian_flow: MeridianFlow,
                                         five_elements: FiveElementsAnalysis) -> List[str]:
        """生成优先建议"""
        recommendations = []
        
        # 体质相关建议（取前2条）
        recommendations.extend(constitution.lifestyle_recommendations[:2])
        
        # 时辰相关建议（取第1条）
        if meridian_flow.recommendations:
            recommendations.append(meridian_flow.recommendations[0])
        
        # 季节相关建议
        recommendations.append(five_elements.seasonal_influence)
        
        return recommendations[:4]  # 限制为4条优先建议
    
    def _calculate_overall_confidence(self, *confidences: float) -> float:
        """计算综合置信度"""
        if not confidences:
            return 0.5
        
        return sum(confidences) / len(confidences) 