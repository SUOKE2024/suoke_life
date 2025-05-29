"""
山水养生服务模块
实现山水养生旅游和健康管理功能
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..domain.models import ConstitutionType, ResourceType

logger = logging.getLogger(__name__)


class WellnessType(Enum):
    """养生类型"""

    MOUNTAIN_THERAPY = "mountain_therapy"  # 山地疗养
    WATER_THERAPY = "water_therapy"  # 水疗养生
    FOREST_BATHING = "forest_bathing"  # 森林浴
    HOT_SPRING = "hot_spring"  # 温泉疗养
    SEASIDE_THERAPY = "seaside_therapy"  # 海滨疗养
    HIGHLAND_THERAPY = "highland_therapy"  # 高原疗养
    MEDITATION_RETREAT = "meditation_retreat"  # 禅修静养


class ClimateType(Enum):
    """气候类型"""

    TEMPERATE = "temperate"  # 温带
    SUBTROPICAL = "subtropical"  # 亚热带
    TROPICAL = "tropical"  # 热带
    CONTINENTAL = "continental"  # 大陆性
    OCEANIC = "oceanic"  # 海洋性
    HIGHLAND = "highland"  # 高原
    DESERT = "desert"  # 沙漠


class ActivityLevel(Enum):
    """活动强度"""

    LOW = "low"  # 低强度
    MODERATE = "moderate"  # 中等强度
    HIGH = "high"  # 高强度
    EXTREME = "extreme"  # 极限强度


@dataclass
class WellnessDestination:
    """养生目的地"""

    destination_id: str
    name: str
    location: str
    coordinates: Dict[str, float]
    wellness_types: List[WellnessType]
    climate_type: ClimateType
    altitude: int
    constitution_benefits: List[ConstitutionType]
    therapeutic_features: List[str]
    natural_resources: List[str]
    facilities: List[str]
    best_seasons: List[str]
    activity_levels: List[ActivityLevel]
    accommodation_types: List[str]
    rating: float
    price_range: str
    accessibility: str


@dataclass
class WellnessProgram:
    """养生项目"""

    program_id: str
    name: str
    destination_id: str
    duration_days: int
    wellness_type: WellnessType
    target_constitution: List[ConstitutionType]
    health_benefits: List[str]
    daily_activities: List[Dict[str, Any]]
    dietary_plan: Dict[str, Any]
    therapeutic_treatments: List[str]
    equipment_needed: List[str]
    difficulty_level: ActivityLevel
    group_size_limit: int
    price_per_person: float
    includes: List[str]
    excludes: List[str]


@dataclass
class WellnessRecommendation:
    """养生推荐"""

    recommendation_id: str
    user_id: str
    constitution_type: ConstitutionType
    health_goals: List[str]
    recommended_destinations: List[WellnessDestination]
    recommended_programs: List[WellnessProgram]
    optimal_duration: int
    best_travel_time: str
    preparation_suggestions: List[str]
    health_precautions: List[str]
    estimated_benefits: Dict[str, float]
    created_at: datetime


@dataclass
class WellnessExperience:
    """养生体验"""

    experience_id: str
    user_id: str
    destination_id: str
    program_id: str
    start_date: datetime
    end_date: datetime
    health_metrics_before: Dict[str, float]
    health_metrics_after: Dict[str, float]
    satisfaction_rating: float
    feedback: str
    improvements_noted: List[str]
    recommendations_for_future: List[str]


class WellnessTourismService:
    """
    山水养生服务

    提供个性化的山水养生旅游推荐和健康管理服务
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # 初始化养生目的地数据库
        self.destinations = self._initialize_destinations()

        # 初始化养生项目数据库
        self.programs = self._initialize_programs()

        # 体质-养生类型映射
        self.constitution_wellness_map = self._build_constitution_wellness_map()

        # 季节-目的地映射
        self.seasonal_destination_map = self._build_seasonal_destination_map()

        logger.info("山水养生服务初始化完成")

    def _initialize_destinations(self) -> Dict[str, WellnessDestination]:
        """初始化养生目的地数据库"""
        destinations = {}

        # 山地疗养目的地
        destinations["泰山"] = WellnessDestination(
            destination_id="dest_001",
            name="泰山养生基地",
            location="山东泰安",
            coordinates={"lat": 36.2544, "lng": 117.1011},
            wellness_types=[
                WellnessType.MOUNTAIN_THERAPY,
                WellnessType.MEDITATION_RETREAT,
            ],
            climate_type=ClimateType.TEMPERATE,
            altitude=1545,
            constitution_benefits=[ConstitutionType.QI_XU, ConstitutionType.YANG_XU],
            therapeutic_features=["负氧离子丰富", "山地气候", "日出观赏", "古树参天"],
            natural_resources=["山泉水", "药用植物", "矿物质", "清新空气"],
            facilities=["养生酒店", "禅修中心", "健身步道", "中医馆"],
            best_seasons=["春", "夏", "秋"],
            activity_levels=[ActivityLevel.LOW, ActivityLevel.MODERATE],
            accommodation_types=["山景酒店", "养生民宿", "禅修院"],
            rating=4.8,
            price_range="中高端",
            accessibility="便利",
        )

        destinations["九寨沟"] = WellnessDestination(
            destination_id="dest_002",
            name="九寨沟水疗养生谷",
            location="四川阿坝",
            coordinates={"lat": 33.2197, "lng": 103.9249},
            wellness_types=[WellnessType.WATER_THERAPY, WellnessType.FOREST_BATHING],
            climate_type=ClimateType.HIGHLAND,
            altitude=2000,
            constitution_benefits=[ConstitutionType.YIN_XU, ConstitutionType.SHI_RE],
            therapeutic_features=["高原湖泊", "瀑布负离子", "原始森林", "藏医文化"],
            natural_resources=["高原湖水", "天然矿泉", "野生药材", "纯净空气"],
            facilities=["水疗中心", "森林步道", "藏医院", "生态酒店"],
            best_seasons=["夏", "秋"],
            activity_levels=[ActivityLevel.LOW, ActivityLevel.MODERATE],
            accommodation_types=["生态酒店", "藏式客栈", "森林小屋"],
            rating=4.9,
            price_range="高端",
            accessibility="一般",
        )

        # 温泉疗养目的地
        destinations["腾冲"] = WellnessDestination(
            destination_id="dest_003",
            name="腾冲温泉养生谷",
            location="云南保山",
            coordinates={"lat": 25.0186, "lng": 98.4951},
            wellness_types=[WellnessType.HOT_SPRING, WellnessType.MOUNTAIN_THERAPY],
            climate_type=ClimateType.SUBTROPICAL,
            altitude=1640,
            constitution_benefits=[ConstitutionType.YANG_XU, ConstitutionType.XUE_YU],
            therapeutic_features=["天然温泉", "火山地貌", "硫磺泉", "地热资源"],
            natural_resources=["温泉水", "火山泥", "地热蒸汽", "药用温泉"],
            facilities=["温泉度假村", "火山公园", "中医温泉馆", "养生餐厅"],
            best_seasons=["秋", "冬", "春"],
            activity_levels=[ActivityLevel.LOW, ActivityLevel.MODERATE],
            accommodation_types=["温泉酒店", "度假村", "民族客栈"],
            rating=4.7,
            price_range="中高端",
            accessibility="便利",
        )

        # 海滨疗养目的地
        destinations["三亚"] = WellnessDestination(
            destination_id="dest_004",
            name="三亚海滨养生度假区",
            location="海南三亚",
            coordinates={"lat": 18.2479, "lng": 109.5146},
            wellness_types=[WellnessType.SEASIDE_THERAPY, WellnessType.WATER_THERAPY],
            climate_type=ClimateType.TROPICAL,
            altitude=5,
            constitution_benefits=[
                ConstitutionType.YANG_XU,
                ConstitutionType.QI_YU,
                ConstitutionType.PING_HE,
            ],
            therapeutic_features=["海水浴", "沙滩日光浴", "海风疗法", "椰林氧吧"],
            natural_resources=["海水", "海沙", "海风", "热带植物"],
            facilities=["海滨度假村", "海水浴场", "沙滩瑜伽", "海鲜餐厅"],
            best_seasons=["秋", "冬", "春"],
            activity_levels=[
                ActivityLevel.LOW,
                ActivityLevel.MODERATE,
                ActivityLevel.HIGH,
            ],
            accommodation_types=["海景酒店", "度假村", "民宿"],
            rating=4.6,
            price_range="中高端",
            accessibility="便利",
        )

        # 森林疗养目的地
        destinations["长白山"] = WellnessDestination(
            destination_id="dest_005",
            name="长白山森林康养基地",
            location="吉林延边",
            coordinates={"lat": 42.0180, "lng": 128.0565},
            wellness_types=[WellnessType.FOREST_BATHING, WellnessType.HIGHLAND_THERAPY],
            climate_type=ClimateType.CONTINENTAL,
            altitude=2189,
            constitution_benefits=[
                ConstitutionType.QI_XU,
                ConstitutionType.YIN_XU,
                ConstitutionType.TE_BING,
            ],
            therapeutic_features=["原始森林", "天池圣水", "高山植物", "朝鲜族文化"],
            natural_resources=["森林空气", "天池水", "野生人参", "山珍药材"],
            facilities=["森林木屋", "康养中心", "民俗村", "药材基地"],
            best_seasons=["夏", "秋"],
            activity_levels=[ActivityLevel.MODERATE, ActivityLevel.HIGH],
            accommodation_types=["森林木屋", "康养酒店", "民俗客栈"],
            rating=4.8,
            price_range="中端",
            accessibility="一般",
        )

        return destinations

    def _initialize_programs(self) -> Dict[str, WellnessProgram]:
        """初始化养生项目数据库"""
        programs = {}

        # 泰山养生项目
        programs["泰山禅修养生"] = WellnessProgram(
            program_id="prog_001",
            name="泰山禅修养生7日游",
            destination_id="dest_001",
            duration_days=7,
            wellness_type=WellnessType.MEDITATION_RETREAT,
            target_constitution=[ConstitutionType.QI_XU, ConstitutionType.QI_YU],
            health_benefits=["补气养神", "调节情绪", "改善睡眠", "增强体质"],
            daily_activities=[
                {
                    "day": 1,
                    "morning": "登山健步",
                    "afternoon": "禅修入门",
                    "evening": "养生茶道",
                },
                {
                    "day": 2,
                    "morning": "日出观赏",
                    "afternoon": "太极练习",
                    "evening": "经络按摩",
                },
                {
                    "day": 3,
                    "morning": "森林漫步",
                    "afternoon": "静坐冥想",
                    "evening": "中医讲座",
                },
                {
                    "day": 4,
                    "morning": "山泉取水",
                    "afternoon": "书法养心",
                    "evening": "药膳品鉴",
                },
                {
                    "day": 5,
                    "morning": "登顶祈福",
                    "afternoon": "养生功法",
                    "evening": "星空冥想",
                },
                {
                    "day": 6,
                    "morning": "采药识草",
                    "afternoon": "禅茶一味",
                    "evening": "养生总结",
                },
                {
                    "day": 7,
                    "morning": "晨练收功",
                    "afternoon": "体验分享",
                    "evening": "告别仪式",
                },
            ],
            dietary_plan={
                "breakfast": "五谷杂粮粥、素食点心",
                "lunch": "山野菜、豆腐料理、药膳汤",
                "dinner": "清淡素食、养生茶饮",
                "special": "每日一款体质调理茶",
            },
            therapeutic_treatments=["中医体质辨识", "经络按摩", "拔罐刮痧", "艾灸调理"],
            equipment_needed=["舒适登山鞋", "运动服装", "防晒用品", "水杯"],
            difficulty_level=ActivityLevel.LOW,
            group_size_limit=20,
            price_per_person=3800.0,
            includes=["住宿", "餐饮", "导师费", "活动费", "保险"],
            excludes=["交通费", "个人消费", "额外治疗费"],
        )

        # 九寨沟水疗项目
        programs["九寨水疗净化"] = WellnessProgram(
            program_id="prog_002",
            name="九寨沟水疗净化5日游",
            destination_id="dest_002",
            duration_days=5,
            wellness_type=WellnessType.WATER_THERAPY,
            target_constitution=[ConstitutionType.YIN_XU, ConstitutionType.SHI_RE],
            health_benefits=["滋阴润燥", "清热解毒", "净化身心", "美容养颜"],
            daily_activities=[
                {
                    "day": 1,
                    "morning": "湖边晨练",
                    "afternoon": "水疗体验",
                    "evening": "藏医咨询",
                },
                {
                    "day": 2,
                    "morning": "瀑布负离子浴",
                    "afternoon": "森林瑜伽",
                    "evening": "藏式按摩",
                },
                {
                    "day": 3,
                    "morning": "高原湖泊游",
                    "afternoon": "水中冥想",
                    "evening": "篝火晚会",
                },
                {
                    "day": 4,
                    "morning": "药浴体验",
                    "afternoon": "湖心岛静修",
                    "evening": "星空观赏",
                },
                {
                    "day": 5,
                    "morning": "晨光水疗",
                    "afternoon": "总结分享",
                    "evening": "告别晚宴",
                },
            ],
            dietary_plan={
                "breakfast": "青稞粥、酥油茶、藏式点心",
                "lunch": "高原蔬菜、牦牛肉、野菌汤",
                "dinner": "清淡藏餐、滋阴汤品",
                "special": "每日高原矿泉水补充",
            },
            therapeutic_treatments=["藏医诊断", "药浴疗法", "藏式按摩", "水疗SPA"],
            equipment_needed=["保暖衣物", "防晒霜", "墨镜", "泳衣"],
            difficulty_level=ActivityLevel.LOW,
            group_size_limit=15,
            price_per_person=5200.0,
            includes=["住宿", "餐饮", "水疗费", "导游费", "保险"],
            excludes=["交通费", "个人消费", "高原反应药物"],
        )

        # 腾冲温泉项目
        programs["腾冲温泉调理"] = WellnessProgram(
            program_id="prog_003",
            name="腾冲温泉调理养生6日游",
            destination_id="dest_003",
            duration_days=6,
            wellness_type=WellnessType.HOT_SPRING,
            target_constitution=[ConstitutionType.YANG_XU, ConstitutionType.XUE_YU],
            health_benefits=["温阳散寒", "活血化瘀", "舒筋活络", "美肌养颜"],
            daily_activities=[
                {
                    "day": 1,
                    "morning": "温泉初体验",
                    "afternoon": "火山地质游",
                    "evening": "中医咨询",
                },
                {
                    "day": 2,
                    "morning": "硫磺泉浴",
                    "afternoon": "火山泥疗",
                    "evening": "傣族歌舞",
                },
                {
                    "day": 3,
                    "morning": "药用温泉",
                    "afternoon": "温泉瑜伽",
                    "evening": "温泉夜浴",
                },
                {
                    "day": 4,
                    "morning": "地热蒸浴",
                    "afternoon": "温泉按摩",
                    "evening": "篝火晚会",
                },
                {
                    "day": 5,
                    "morning": "温泉太极",
                    "afternoon": "温泉冥想",
                    "evening": "温泉茶道",
                },
                {
                    "day": 6,
                    "morning": "温泉告别浴",
                    "afternoon": "体验总结",
                    "evening": "欢送晚宴",
                },
            ],
            dietary_plan={
                "breakfast": "云南米线、豆浆、包子",
                "lunch": "云南菜、温补汤品、野菜",
                "dinner": "清淡滇菜、温阳药膳",
                "special": "每日温泉水煮茶",
            },
            therapeutic_treatments=["温泉浴疗", "火山泥疗", "中医推拿", "艾灸调理"],
            equipment_needed=["泳衣", "拖鞋", "浴巾", "防滑鞋"],
            difficulty_level=ActivityLevel.LOW,
            group_size_limit=18,
            price_per_person=4200.0,
            includes=["住宿", "餐饮", "温泉费", "治疗费", "保险"],
            excludes=["交通费", "个人消费", "额外SPA费用"],
        )

        return programs

    def _build_constitution_wellness_map(
        self,
    ) -> Dict[ConstitutionType, List[WellnessType]]:
        """构建体质-养生类型映射"""
        constitution_map = {
            ConstitutionType.QI_XU: [
                WellnessType.MOUNTAIN_THERAPY,
                WellnessType.FOREST_BATHING,
                WellnessType.MEDITATION_RETREAT,
            ],
            ConstitutionType.YANG_XU: [
                WellnessType.HOT_SPRING,
                WellnessType.MOUNTAIN_THERAPY,
                WellnessType.SEASIDE_THERAPY,
            ],
            ConstitutionType.YIN_XU: [
                WellnessType.WATER_THERAPY,
                WellnessType.FOREST_BATHING,
                WellnessType.HIGHLAND_THERAPY,
            ],
            ConstitutionType.TAN_SHI: [
                WellnessType.MOUNTAIN_THERAPY,
                WellnessType.SEASIDE_THERAPY,
                WellnessType.FOREST_BATHING,
            ],
            ConstitutionType.SHI_RE: [
                WellnessType.WATER_THERAPY,
                WellnessType.HIGHLAND_THERAPY,
                WellnessType.FOREST_BATHING,
            ],
            ConstitutionType.XUE_YU: [
                WellnessType.HOT_SPRING,
                WellnessType.MOUNTAIN_THERAPY,
                WellnessType.SEASIDE_THERAPY,
            ],
            ConstitutionType.QI_YU: [
                WellnessType.MEDITATION_RETREAT,
                WellnessType.FOREST_BATHING,
                WellnessType.SEASIDE_THERAPY,
            ],
            ConstitutionType.TE_BING: [
                WellnessType.HIGHLAND_THERAPY,
                WellnessType.FOREST_BATHING,
                WellnessType.MEDITATION_RETREAT,
            ],
            ConstitutionType.PING_HE: [
                WellnessType.MOUNTAIN_THERAPY,
                WellnessType.WATER_THERAPY,
                WellnessType.SEASIDE_THERAPY,
                WellnessType.FOREST_BATHING,
            ],
        }

        return constitution_map

    def _build_seasonal_destination_map(self) -> Dict[str, List[str]]:
        """构建季节-目的地映射"""
        seasonal_map = {
            "春": ["泰山", "腾冲", "三亚"],
            "夏": ["九寨沟", "长白山", "泰山"],
            "秋": ["泰山", "九寨沟", "腾冲", "长白山", "三亚"],
            "冬": ["腾冲", "三亚"],
        }

        return seasonal_map

    async def generate_wellness_recommendation(
        self,
        user_id: str,
        constitution_type: ConstitutionType,
        health_goals: List[str],
        preferences: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> WellnessRecommendation:
        """生成养生推荐"""
        try:
            # 获取适合的养生类型
            suitable_wellness_types = self.constitution_wellness_map.get(
                constitution_type, []
            )

            # 获取当前季节
            current_season = self._get_current_season()

            # 筛选适合的目的地
            recommended_destinations = self._filter_destinations(
                suitable_wellness_types, current_season, preferences, constraints
            )

            # 筛选适合的项目
            recommended_programs = self._filter_programs(
                recommended_destinations, constitution_type, health_goals, constraints
            )

            # 计算最优时长
            optimal_duration = self._calculate_optimal_duration(
                constitution_type, health_goals, constraints
            )

            # 生成最佳旅行时间
            best_travel_time = self._generate_best_travel_time(
                recommended_destinations, current_season
            )

            # 生成准备建议
            preparation_suggestions = self._generate_preparation_suggestions(
                constitution_type, recommended_destinations
            )

            # 生成健康注意事项
            health_precautions = self._generate_health_precautions(
                constitution_type, recommended_destinations
            )

            # 估算健康效益
            estimated_benefits = self._estimate_health_benefits(
                constitution_type, recommended_programs
            )

            recommendation = WellnessRecommendation(
                recommendation_id=f"wellness_rec_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                constitution_type=constitution_type,
                health_goals=health_goals,
                recommended_destinations=recommended_destinations,
                recommended_programs=recommended_programs,
                optimal_duration=optimal_duration,
                best_travel_time=best_travel_time,
                preparation_suggestions=preparation_suggestions,
                health_precautions=health_precautions,
                estimated_benefits=estimated_benefits,
                created_at=datetime.now(),
            )

            logger.info(f"为用户 {user_id} 生成养生推荐")
            return recommendation

        except Exception as e:
            logger.error(f"生成养生推荐失败: {e}")
            raise

    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month

        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"

    def _filter_destinations(
        self,
        suitable_wellness_types: List[WellnessType],
        current_season: str,
        preferences: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> List[WellnessDestination]:
        """筛选适合的目的地"""
        filtered_destinations = []

        # 获取季节性目的地
        seasonal_destinations = self.seasonal_destination_map.get(current_season, [])

        for dest_name, destination in self.destinations.items():
            # 检查季节适宜性
            if dest_name not in seasonal_destinations:
                continue

            # 检查养生类型匹配
            if not any(
                wt in destination.wellness_types for wt in suitable_wellness_types
            ):
                continue

            # 检查预算约束
            budget_limit = constraints.get("budget", "不限")
            if budget_limit != "不限":
                if budget_limit == "经济" and destination.price_range in ["高端"]:
                    continue
                elif budget_limit == "中等" and destination.price_range in ["高端"]:
                    continue

            # 检查活动强度偏好
            activity_preference = preferences.get("activity_level", "中等")
            if (
                activity_preference == "轻松"
                and ActivityLevel.HIGH in destination.activity_levels
            ):
                continue
            elif (
                activity_preference == "挑战"
                and ActivityLevel.LOW in destination.activity_levels
            ):
                continue

            # 检查交通便利性要求
            accessibility_requirement = preferences.get("accessibility", "不限")
            if (
                accessibility_requirement == "便利"
                and destination.accessibility != "便利"
            ):
                continue

            filtered_destinations.append(destination)

        # 按评分排序
        filtered_destinations.sort(key=lambda x: x.rating, reverse=True)

        return filtered_destinations[:5]  # 返回前5个推荐

    def _filter_programs(
        self,
        destinations: List[WellnessDestination],
        constitution_type: ConstitutionType,
        health_goals: List[str],
        constraints: Dict[str, Any],
    ) -> List[WellnessProgram]:
        """筛选适合的项目"""
        filtered_programs = []

        destination_ids = [dest.destination_id for dest in destinations]

        for program_name, program in self.programs.items():
            # 检查目的地匹配
            if program.destination_id not in destination_ids:
                continue

            # 检查体质匹配
            if constitution_type not in program.target_constitution:
                continue

            # 检查时长约束
            max_duration = constraints.get("max_duration_days", 14)
            if program.duration_days > max_duration:
                continue

            # 检查预算约束
            max_budget = constraints.get("max_budget_per_person", 10000)
            if program.price_per_person > max_budget:
                continue

            # 检查健康目标匹配
            goal_match = any(
                goal in " ".join(program.health_benefits) for goal in health_goals
            )
            if health_goals and not goal_match:
                continue

            filtered_programs.append(program)

        return filtered_programs

    def _calculate_optimal_duration(
        self,
        constitution_type: ConstitutionType,
        health_goals: List[str],
        constraints: Dict[str, Any],
    ) -> int:
        """计算最优时长"""
        base_duration = 5  # 基础5天

        # 根据体质调整
        if constitution_type in [ConstitutionType.QI_XU, ConstitutionType.YANG_XU]:
            base_duration += 2  # 虚证需要更长时间调理

        # 根据健康目标调整
        if "慢性病调理" in health_goals:
            base_duration += 3
        elif "亚健康改善" in health_goals:
            base_duration += 1

        # 考虑约束
        max_duration = constraints.get("max_duration_days", 14)

        return min(base_duration, max_duration)

    def _generate_best_travel_time(
        self, destinations: List[WellnessDestination], current_season: str
    ) -> str:
        """生成最佳旅行时间"""
        if not destinations:
            return f"{current_season}季适宜"

        # 统计目的地的最佳季节
        season_count = {}
        for dest in destinations:
            for season in dest.best_seasons:
                season_count[season] = season_count.get(season, 0) + 1

        if season_count:
            best_season = max(season_count.items(), key=lambda x: x[1])[0]
            return f"{best_season}季最佳，{current_season}季也适宜"

        return f"{current_season}季适宜"

    def _generate_preparation_suggestions(
        self,
        constitution_type: ConstitutionType,
        destinations: List[WellnessDestination],
    ) -> List[str]:
        """生成准备建议"""
        suggestions = []

        # 基于体质的建议
        if constitution_type == ConstitutionType.QI_XU:
            suggestions.extend(
                [
                    "出行前一周开始调理作息，保证充足睡眠",
                    "准备补气类中药或保健品",
                    "选择舒适的运动装备",
                ]
            )
        elif constitution_type == ConstitutionType.YANG_XU:
            suggestions.extend(
                ["准备保暖衣物，避免受寒", "携带温阳类药物或食品", "选择温和的活动项目"]
            )
        elif constitution_type == ConstitutionType.YIN_XU:
            suggestions.extend(
                ["准备滋阴润燥的护肤品", "携带充足的水分补充", "避免过度暴晒和剧烈运动"]
            )

        # 基于目的地的建议
        if destinations:
            for dest in destinations[:2]:  # 只考虑前2个目的地
                if dest.altitude > 1500:
                    suggestions.append("高海拔地区，准备防高原反应药物")

                if WellnessType.HOT_SPRING in dest.wellness_types:
                    suggestions.append("准备泳衣和防滑拖鞋")

                if WellnessType.MOUNTAIN_THERAPY in dest.wellness_types:
                    suggestions.append("准备舒适的登山鞋和运动装备")

        return list(set(suggestions))  # 去重

    def _generate_health_precautions(
        self,
        constitution_type: ConstitutionType,
        destinations: List[WellnessDestination],
    ) -> List[str]:
        """生成健康注意事项"""
        precautions = []

        # 基于体质的注意事项
        if constitution_type == ConstitutionType.YANG_XU:
            precautions.extend(
                ["避免长时间接触冷水", "注意保暖，防止受寒", "不宜过度疲劳"]
            )
        elif constitution_type == ConstitutionType.YIN_XU:
            precautions.extend(["避免长时间暴晒", "注意补充水分", "避免过度出汗"])
        elif constitution_type == ConstitutionType.SHI_RE:
            precautions.extend(["避免高温环境", "注意清淡饮食", "避免辛辣刺激食物"])

        # 基于目的地的注意事项
        if destinations:
            for dest in destinations[:2]:
                if dest.climate_type == ClimateType.HIGHLAND:
                    precautions.append("注意防范高原反应")

                if dest.climate_type == ClimateType.TROPICAL:
                    precautions.append("注意防晒和防蚊虫")

                if WellnessType.HOT_SPRING in dest.wellness_types:
                    precautions.append("温泉浸泡时间不宜过长")

        return list(set(precautions))

    def _estimate_health_benefits(
        self, constitution_type: ConstitutionType, programs: List[WellnessProgram]
    ) -> Dict[str, float]:
        """估算健康效益"""
        benefits = {
            "体质改善": 0.0,
            "精神状态": 0.0,
            "睡眠质量": 0.0,
            "免疫力": 0.0,
            "压力缓解": 0.0,
        }

        if not programs:
            return benefits

        # 基于项目类型估算效益
        for program in programs[:3]:  # 考虑前3个项目
            if program.wellness_type == WellnessType.MEDITATION_RETREAT:
                benefits["精神状态"] += 0.3
                benefits["压力缓解"] += 0.4
                benefits["睡眠质量"] += 0.2
            elif program.wellness_type == WellnessType.HOT_SPRING:
                benefits["体质改善"] += 0.3
                benefits["压力缓解"] += 0.3
                benefits["睡眠质量"] += 0.2
            elif program.wellness_type == WellnessType.FOREST_BATHING:
                benefits["免疫力"] += 0.3
                benefits["精神状态"] += 0.2
                benefits["压力缓解"] += 0.3
            elif program.wellness_type == WellnessType.MOUNTAIN_THERAPY:
                benefits["体质改善"] += 0.4
                benefits["免疫力"] += 0.3
                benefits["精神状态"] += 0.2

        # 基于体质调整效益
        if constitution_type == ConstitutionType.QI_XU:
            benefits["体质改善"] *= 1.2
            benefits["免疫力"] *= 1.1
        elif constitution_type == ConstitutionType.QI_YU:
            benefits["精神状态"] *= 1.3
            benefits["压力缓解"] *= 1.2

        # 确保效益值在合理范围内
        for key in benefits:
            benefits[key] = min(benefits[key], 1.0)

        return benefits

    async def record_wellness_experience(
        self,
        user_id: str,
        destination_id: str,
        program_id: str,
        experience_data: Dict[str, Any],
    ) -> WellnessExperience:
        """记录养生体验"""
        try:
            experience = WellnessExperience(
                experience_id=f"exp_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                destination_id=destination_id,
                program_id=program_id,
                start_date=experience_data.get("start_date"),
                end_date=experience_data.get("end_date"),
                health_metrics_before=experience_data.get("health_metrics_before", {}),
                health_metrics_after=experience_data.get("health_metrics_after", {}),
                satisfaction_rating=experience_data.get("satisfaction_rating", 0.0),
                feedback=experience_data.get("feedback", ""),
                improvements_noted=experience_data.get("improvements_noted", []),
                recommendations_for_future=experience_data.get(
                    "recommendations_for_future", []
                ),
            )

            logger.info(f"记录用户 {user_id} 的养生体验")
            return experience

        except Exception as e:
            logger.error(f"记录养生体验失败: {e}")
            raise

    async def get_destination_details(
        self, destination_id: str
    ) -> Optional[WellnessDestination]:
        """获取目的地详情"""
        for destination in self.destinations.values():
            if destination.destination_id == destination_id:
                return destination
        return None

    async def get_program_details(self, program_id: str) -> Optional[WellnessProgram]:
        """获取项目详情"""
        for program in self.programs.values():
            if program.program_id == program_id:
                return program
        return None

    async def search_destinations(
        self,
        wellness_type: Optional[WellnessType] = None,
        climate_type: Optional[ClimateType] = None,
        price_range: Optional[str] = None,
        season: Optional[str] = None,
    ) -> List[WellnessDestination]:
        """搜索目的地"""
        results = []

        for destination in self.destinations.values():
            # 养生类型筛选
            if wellness_type and wellness_type not in destination.wellness_types:
                continue

            # 气候类型筛选
            if climate_type and destination.climate_type != climate_type:
                continue

            # 价格范围筛选
            if price_range and destination.price_range != price_range:
                continue

            # 季节筛选
            if season and season not in destination.best_seasons:
                continue

            results.append(destination)

        # 按评分排序
        results.sort(key=lambda x: x.rating, reverse=True)

        return results

    def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "total_destinations": len(self.destinations),
            "total_programs": len(self.programs),
            "wellness_types": list(
                set(
                    wt.value
                    for dest in self.destinations.values()
                    for wt in dest.wellness_types
                )
            ),
            "climate_types": list(
                set(dest.climate_type.value for dest in self.destinations.values())
            ),
            "constitution_coverage": list(self.constitution_wellness_map.keys()),
            "seasonal_coverage": list(self.seasonal_destination_map.keys()),
            "price_ranges": list(
                set(dest.price_range for dest in self.destinations.values())
            ),
            "average_rating": sum(dest.rating for dest in self.destinations.values())
            / len(self.destinations),
        }
