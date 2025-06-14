"""
recommendation - 索克生活项目模块
"""

from datetime import datetime

"""
推荐服务

提供算诊推荐相关的业务逻辑
"""


class RecommendationService:
    """推荐服务"""

    def __init__(self) -> None:
        """初始化服务"""
        pass

    async def generate_lifestyle_recommendations(
        self,
        constitution_type: str,
        current_symptoms: list[str] | None = None,
        season: str | None = None,
    ) -> dict:
        """
        生成生活方式推荐

        Args:
            constitution_type: 体质类型
            current_symptoms: 当前症状
            season: 季节

        Returns:
            生活方式推荐
        """
        recommendations = {
            "diet": [],
            "exercise": [],
            "lifestyle": [],
            "precautions": [],
        }

        # 根据体质类型生成推荐
        if "木型" in constitution_type:
            recommendations["diet"] = ["多食酸味食物", "少食辛辣", "适量饮绿茶"]
            recommendations["exercise"] = ["太极拳", "瑜伽", "散步"]
            recommendations["lifestyle"] = ["保持心情舒畅", "规律作息", "避免熬夜"]

        elif "火型" in constitution_type:
            recommendations["diet"] = ["清淡饮食", "多食苦味食物", "避免辛辣"]
            recommendations["exercise"] = ["游泳", "慢跑", "静坐"]
            recommendations["lifestyle"] = ["保持心境平和", "避免过度兴奋", "充足睡眠"]

        elif "土型" in constitution_type:
            recommendations["diet"] = ["健脾食物", "少食甜腻", "规律饮食"]
            recommendations["exercise"] = ["八段锦", "五禽戏", "适度运动"]
            recommendations["lifestyle"] = ["避免过度思虑", "保持乐观", "定时定量"]

        elif "金型" in constitution_type:
            recommendations["diet"] = ["润肺食物", "少食辛燥", "多饮温水"]
            recommendations["exercise"] = ["呼吸操", "慢走", "气功"]
            recommendations["lifestyle"] = ["保护呼吸道", "避免感冒", "注意保暖"]

        elif "水型" in constitution_type:
            recommendations["diet"] = ["补肾食物", "温热饮食", "少食寒凉"]
            recommendations["exercise"] = ["慢跑", "游泳", "腰部锻炼"]
            recommendations["lifestyle"] = ["节制房事", "保暖防寒", "充足休息"]

        return {
            "constitution_type": constitution_type,
            "recommendations": recommendations,
            "generated_time": datetime.utcnow().isoformat(),
        }

    async def generate_treatment_recommendations(
        self, condition: str, constitution_type: str, optimal_times: list[str]
    ) -> dict:
        """
        生成治疗推荐

        Args:
            condition: 病症
            constitution_type: 体质类型
            optimal_times: 最佳治疗时间

        Returns:
            治疗推荐
        """
        return {
            "condition": condition,
            "constitution_type": constitution_type,
            "treatment_methods": ["针灸", "推拿", "中药"],
            "optimal_times": optimal_times,
            "duration": "2 - 4周",
            "precautions": ["避免过度劳累", "保持心情愉悦"],
            "generated_time": datetime.utcnow().isoformat(),
        }

    async def generate_seasonal_recommendations(
        self, season: str, constitution_type: str
    ) -> dict:
        """
        生成季节性推荐

        Args:
            season: 季节
            constitution_type: 体质类型

        Returns:
            季节性推荐
        """
        seasonal_advice = {
            "春": {
                "diet": ["疏肝理气食物", "绿色蔬菜", "少食酸味"],
                "exercise": ["踏青", "放风筝", "舒展运动"],
                "lifestyle": ["早睡早起", "调畅情志", "防风保暖"],
            },
            "夏": {
                "diet": ["清热解暑", "苦味食物", "少食温热"],
                "exercise": ["游泳", "早晚运动", "避免中暑"],
                "lifestyle": ["午休", "心境平和", "防暑降温"],
            },
            "秋": {
                "diet": ["润燥养肺", "白色食物", "少食辛辣"],
                "exercise": ["登高", "深呼吸", "适度运动"],
                "lifestyle": ["早睡早起", "保护呼吸道", "防燥润肺"],
            },
            "冬": {
                "diet": ["温补肾阳", "黑色食物", "少食寒凉"],
                "exercise": ["室内运动", "保暖锻炼", "避免大汗"],
                "lifestyle": ["早睡晚起", "保暖防寒", "藏精养神"],
            },
        }

        advice = seasonal_advice.get(season, seasonal_advice["春"])

        return {
            "season": season,
            "constitution_type": constitution_type,
            "seasonal_advice": advice,
            "generated_time": datetime.utcnow().isoformat(),
        }
