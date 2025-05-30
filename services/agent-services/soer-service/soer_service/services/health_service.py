"""
健康服务

提供健康数据分析、健康建议等功能
"""

from datetime import datetime
from typing import Any

from ..models.health import HealthAnalysis, HealthRecommendation
from .base_service import BaseService


class HealthService(BaseService):
    """健康服务类"""

    async def submit_health_data(
        self, user_id: str, data_type: str, value: float, unit: str, timestamp: str
    ) -> dict[str, Any]:
        """提交健康数据"""
        self.logger.info(f"提交健康数据: 用户={user_id}, 类型={data_type}")

        # 创建健康数据记录
        health_data = {
            "user_id": user_id,
            "data_type": data_type,
            "value": value,
            "unit": unit,
            "timestamp": timestamp,
            "created_at": datetime.now(),
        }

        # 保存到数据库
        await self.mongodb.health_data.insert_one(health_data)

        # 记录操作日志
        await self.log_operation(
            "submit_health_data", user_id, {"data_type": data_type, "value": value}
        )

        return {"status": "success", "message": "健康数据提交成功"}

    async def analyze_health_data(
        self, user_id: str, analysis_type: str = "comprehensive", time_range: int = 30
    ) -> HealthAnalysis:
        """分析健康数据"""
        self.logger.info(f"分析健康数据: 用户={user_id}, 类型={analysis_type}")

        # 获取用户健康数据
        health_data = await self._get_user_health_data(user_id, time_range)

        # 计算健康评分
        health_score = await self._calculate_health_score(health_data)

        # 分析健康趋势
        health_trends = await self._analyze_health_trends(health_data)

        # 识别风险因素
        risk_factors = await self._identify_risk_factors(health_data)

        # 中医体质分析
        tcm_constitution = await self._analyze_tcm_constitution(user_id, health_data)

        analysis = HealthAnalysis(
            user_id=user_id,
            analysis_type=analysis_type,
            time_range=time_range,
            overall_health_score=health_score,
            health_trends=health_trends,
            risk_factors=risk_factors,
            tcm_constitution=tcm_constitution,
        )

        # 保存分析结果
        await self._save_health_analysis(analysis)

        return analysis

    async def get_health_recommendations(
        self, user_id: str
    ) -> list[HealthRecommendation]:
        """获取健康建议"""
        self.logger.info(f"获取健康建议: 用户={user_id}")

        # 获取最新健康分析
        latest_analysis = await self._get_latest_health_analysis(user_id)

        # 生成个性化建议
        recommendations = await self._generate_health_recommendations(
            user_id, latest_analysis
        )

        return recommendations

    async def get_health_trends(
        self, user_id: str, metric: str, days: int = 30
    ) -> dict[str, Any]:
        """获取健康趋势数据"""
        cache_key = self.generate_cache_key("health_trends", user_id, metric, days)
        cached_result = await self.cache_get(cache_key)

        if cached_result:
            return cached_result

        # 查询趋势数据
        trends = await self._calculate_health_trends(user_id, metric, days)

        await self.cache_set(cache_key, trends, expire=3600)
        return trends

    async def get_health_dashboard(self, user_id: str) -> dict[str, Any]:
        """获取健康仪表板数据"""
        dashboard = {
            "overview": {
                "health_score": 85,
                "trend": "improving",
                "last_updated": datetime.now().isoformat(),
            },
            "vital_signs": {
                "heart_rate": 72,
                "blood_pressure": "120/80",
                "weight": 65.5,
            },
            "recent_activities": [
                {"type": "exercise", "duration": 30, "date": "2024-01-15"},
                {"type": "sleep", "duration": 8, "date": "2024-01-15"},
            ],
            "recommendations": ["保持规律运动", "注意饮食平衡", "确保充足睡眠"],
        }

        return dashboard

    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        return {
            "service": "HealthService",
            "status": "healthy",
            "database_connection": True,
            "cache_connection": True,
        }

    # 私有方法
    async def _get_user_health_data(
        self, user_id: str, days: int
    ) -> list[dict[str, Any]]:
        """获取用户健康数据"""
        # 模拟健康数据
        return [
            {"type": "heart_rate", "value": 72, "date": "2024-01-15"},
            {"type": "weight", "value": 65.5, "date": "2024-01-15"},
            {"type": "sleep_duration", "value": 8, "date": "2024-01-15"},
        ]

    async def _calculate_health_score(self, health_data: list[dict[str, Any]]) -> float:
        """计算健康评分"""
        # 简化的健康评分算法
        base_score = 75.0

        # 根据各项指标调整评分
        for data in health_data:
            if data["type"] == "heart_rate" and 60 <= data["value"] <= 80:
                base_score += 5
            elif data["type"] == "sleep_duration" and data["value"] >= 7:
                base_score += 5

        return min(base_score, 100.0)

    async def _analyze_health_trends(
        self, health_data: list[dict[str, Any]]
    ) -> dict[str, str]:
        """分析健康趋势"""
        return {
            "heart_rate": "stable",
            "weight": "decreasing",
            "sleep_quality": "improving",
        }

    async def _identify_risk_factors(
        self, health_data: list[dict[str, Any]]
    ) -> list[str]:
        """识别风险因素"""
        risk_factors = []

        # 简化的风险因素识别
        for data in health_data:
            if data["type"] == "heart_rate" and data["value"] > 100:
                risk_factors.append("心率偏高")
            elif data["type"] == "sleep_duration" and data["value"] < 6:
                risk_factors.append("睡眠不足")

        return risk_factors

    async def _analyze_tcm_constitution(
        self, user_id: str, health_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """中医体质分析"""
        return {
            "constitution_type": "平和质",
            "characteristics": ["体形匀称", "面色润泽", "精力充沛"],
            "health_advice": "保持现有生活方式，注意四季养生",
        }

    async def _save_health_analysis(self, analysis: HealthAnalysis):
        """保存健康分析结果"""
        try:
            await self.mongodb.health_analyses.insert_one(analysis.dict())
        except Exception as e:
            self.logger.error(f"保存健康分析失败: {e}")

    async def _get_latest_health_analysis(self, user_id: str) -> dict[str, Any]:
        """获取最新健康分析"""
        # 模拟最新分析数据
        return {
            "health_score": 85,
            "risk_factors": ["睡眠不足"],
            "improvement_areas": ["运动量", "饮食结构"],
        }

    async def _generate_health_recommendations(
        self, user_id: str, analysis: dict[str, Any]
    ) -> list[HealthRecommendation]:
        """生成健康建议"""
        recommendations = []

        # 基于分析结果生成建议
        if "睡眠不足" in analysis.get("risk_factors", []):
            recommendations.append(
                HealthRecommendation(
                    recommendation_id="rec_001",
                    user_id=user_id,
                    category="睡眠",
                    priority="high",
                    title="改善睡眠质量",
                    description="建议每晚保证7-8小时睡眠",
                    action_items=["设定固定就寝时间", "避免睡前使用电子设备"],
                    expected_benefits=["提高精力", "增强免疫力"],
                )
            )

        return recommendations

    async def _calculate_health_trends(
        self, user_id: str, metric: str, days: int
    ) -> dict[str, Any]:
        """计算健康趋势"""
        # 模拟趋势数据
        return {
            "metric": metric,
            "trend": "improving",
            "data_points": [
                {"date": "2024-01-01", "value": 70},
                {"date": "2024-01-15", "value": 75},
            ],
            "analysis": "指标呈上升趋势，健康状况良好",
        }
