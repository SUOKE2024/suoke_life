"""
传感器数据分析服务
"""
import logging
from datetime import datetime, timedelta
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class SensorAnalysisService:
    """传感器数据分析服务"""

    def __init__(self, config: dict, repos):
        """初始化传感器数据分析服务

        Args:
            config: 配置信息
            repos: 存储库
        """
        self.config = config
        self.repos = repos
        logger.info("初始化传感器数据分析服务")

    async def analyze_sensor_data(self, user_id: str, sensor_data: dict[str, Any]) -> dict[str, Any]:
        """分析传感器数据

        对多种传感器数据进行综合分析，提取健康指标和见解

        Args:
            user_id: 用户ID
            sensor_data: 传感器数据

        Returns:
            分析结果，包含健康指标和见解
        """
        logger.info(f"为用户 {user_id} 分析传感器数据")

        # 提取各类传感器数据
        heart_rate_data = self._extract_sensor_type(sensor_data, "heart_rate")
        steps_data = self._extract_sensor_type(sensor_data, "steps")
        sleep_data = self._extract_sensor_type(sensor_data, "sleep")
        blood_pressure_data = self._extract_sensor_type(sensor_data, "blood_pressure")

        # 分析结果
        results = {"metrics": [], "insights": []}

        # 分析心率数据
        if heart_rate_data:
            heart_metrics, heart_insights = await self._analyze_heart_rate(user_id, heart_rate_data)
            results["metrics"].extend(heart_metrics)
            results["insights"].extend(heart_insights)

        # 分析步数数据
        if steps_data:
            steps_metrics, steps_insights = await self._analyze_steps(user_id, steps_data)
            results["metrics"].extend(steps_metrics)
            results["insights"].extend(steps_insights)

        # 分析睡眠数据
        if sleep_data:
            sleep_metrics, sleep_insights = await self._analyze_sleep(user_id, sleep_data)
            results["metrics"].extend(sleep_metrics)
            results["insights"].extend(sleep_insights)

        # 分析血压数据
        if blood_pressure_data:
            bp_metrics, bp_insights = await self._analyze_blood_pressure(user_id, blood_pressure_data)
            results["metrics"].extend(bp_metrics)
            results["insights"].extend(bp_insights)

        # 多指标融合分析
        if len(results["metrics"]) > 1:
            fusion_insights = await self._fusion_analysis(user_id, results["metrics"])
            results["insights"].extend(fusion_insights)

        # 保存分析结果
        await self._save_analysis_results(user_id, results)

        return results

    async def detect_abnormal_pattern(self, user_id: str, data_types: list[str],
                                  days: int = 30, sensitivity: float = 0.7) -> dict[str, Any]:
        """检测异常模式

        分析用户历史数据，检测异常健康模式

        Args:
            user_id: 用户ID
            data_types: 数据类型列表
            days: 分析的天数
            sensitivity: 敏感度（0-1）

        Returns:
            检测到的异常模式
        """
        logger.info(f"为用户 {user_id} 检测异常模式")

        # 获取历史数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 结果容器
        abnormal_patterns = []

        # 对每种数据类型检测异常
        for data_type in data_types:
            # 获取历史数据
            data = await self.repos.sensor_repo.get_historical_data(
                user_id, data_type, start_date, end_date
            )

            if not data or len(data) < 2:
                continue

            # 检测异常
            abnormalities = await self._detect_abnormalities(data_type, data, sensitivity)

            # 添加检测到的异常
            abnormal_patterns.extend(abnormalities)

        # 分析异常之间的关联
        if len(abnormal_patterns) > 1:
            correlated_patterns = await self._analyze_pattern_correlations(abnormal_patterns)
            abnormal_patterns.extend(correlated_patterns)

        return {"patterns": abnormal_patterns}

    async def predict_health_trend(self, user_id: str, metrics: list[str],
                                prediction_days: int = 30,
                                include_seasonal_factors: bool = True) -> dict[str, Any]:
        """预测健康趋势

        基于历史数据预测未来健康趋势

        Args:
            user_id: 用户ID
            metrics: 指标列表
            prediction_days: 预测天数
            include_seasonal_factors: 是否包含季节因素

        Returns:
            健康趋势预测结果
        """
        logger.info(f"为用户 {user_id} 预测健康趋势")

        # 获取用户体质类型（用于考虑季节性因素）
        user_profile = await self.repos.health_profile_repo.get_by_user_id(user_id)
        constitution_type = user_profile.tcm_constitution.primary_type if user_profile and user_profile.tcm_constitution else None

        # 结果容器
        predictions = []

        # 对每个指标进行预测
        for metric in metrics:
            # 获取历史数据
            history_days = max(90, prediction_days * 3)  # 至少需要90天的历史数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=history_days)

            # 获取历史数据
            data = await self.repos.sensor_repo.get_metric_history(
                user_id, metric, start_date, end_date
            )

            if not data or len(data) < history_days // 3:  # 数据点太少，无法预测
                continue

            # 预测趋势
            prediction = await self._predict_metric_trend(
                metric, data, prediction_days, constitution_type if include_seasonal_factors else None
            )

            if prediction:
                predictions.append(prediction)

        return {"predictions": predictions}

    def _extract_sensor_type(self, sensor_data: dict[str, Any], sensor_type: str) -> list[dict[str, Any]]:
        """从传感器数据中提取特定类型的数据

        Args:
            sensor_data: 传感器数据
            sensor_type: 传感器类型

        Returns:
            特定类型的传感器数据
        """
        for sensor in sensor_data.get("data", []):
            if sensor.get("sensor_type") == sensor_type:
                return sensor.get("data_points", [])
        return []

    async def _analyze_heart_rate(self, user_id: str, heart_rate_data: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """分析心率数据

        Args:
            user_id: 用户ID
            heart_rate_data: 心率数据

        Returns:
            心率指标和见解
        """
        metrics = []
        insights = []

        if not heart_rate_data:
            return metrics, insights

        try:
            # 提取心率值
            heart_rates = [point["values"].get("value", 0) for point in heart_rate_data if "values" in point]

            if not heart_rates:
                return metrics, insights

            # 计算统计值
            avg_hr = sum(heart_rates) / len(heart_rates)
            min(heart_rates)
            max_hr = max(heart_rates)

            # 获取用户之前的心率数据
            previous_data = await self.repos.sensor_repo.get_previous_period_avg(
                user_id, "heart_rate", datetime.now() - timedelta(days=7), 7
            )

            # 确定趋势
            trend = "stable"
            if previous_data and abs(avg_hr - previous_data) > 5:
                trend = "improving" if (avg_hr < previous_data and avg_hr > 60) or (avg_hr > previous_data and avg_hr < 60) else "declining"

            # 添加心率指标
            metrics.append({
                "metric_name": "平均心率",
                "current_value": round(avg_hr, 1),
                "reference_min": 60,
                "reference_max": 100,
                "interpretation": self._interpret_heart_rate(avg_hr),
                "trend": trend
            })

            # 添加心率变异性指标（如果数据足够）
            if len(heart_rates) >= 10:
                hrv = np.std(heart_rates)
                metrics.append({
                    "metric_name": "心率变异性",
                    "current_value": round(hrv, 1),
                    "reference_min": 20,
                    "reference_max": 60,
                    "interpretation": "正常" if 20 <= hrv <= 60 else "偏低" if hrv < 20 else "偏高",
                    "trend": "stable"  # 简化起见，这里不计算HRV趋势
                })

            # 生成见解
            if avg_hr < 60:
                insights.append({
                    "category": "心率",
                    "description": "心率偏低，可能表示休息状态良好或较好的心脏健康状况，但如果伴有乏力、头晕等症状，应咨询医生。",
                    "confidence": 0.8,
                    "suggestions": [
                        "适度增加有氧运动",
                        "确保充足的水分摄入",
                        "如有不适症状，请咨询医生"
                    ]
                })
            elif avg_hr > 100:
                insights.append({
                    "category": "心率",
                    "description": "静息心率偏高，可能表示压力大、缺乏运动或其他健康问题。",
                    "confidence": 0.8,
                    "suggestions": [
                        "学习放松技巧如深呼吸或冥想",
                        "增加规律的有氧运动",
                        "减少咖啡因和酒精摄入",
                        "如持续偏高，请咨询医生"
                    ]
                })
            elif max_hr > 120 and not any(point.get("metadata", {}).get("activity_type") for point in heart_rate_data):
                insights.append({
                    "category": "心率",
                    "description": "检测到心率短时间内明显升高，但未记录相关运动，可能与情绪波动或压力有关。",
                    "confidence": 0.7,
                    "suggestions": [
                        "关注压力管理",
                        "尝试放松技巧",
                        "保持规律作息"
                    ]
                })

        except Exception as e:
            logger.error(f"分析心率数据失败: {str(e)}")

        return metrics, insights

    async def _analyze_steps(self, user_id: str, steps_data: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """分析步数数据

        Args:
            user_id: 用户ID
            steps_data: 步数数据

        Returns:
            步数指标和见解
        """
        # 此处略去实现，返回示例结果
        metrics = [
            {
                "metric_name": "日均步数",
                "current_value": 8500,
                "reference_min": 7000,
                "reference_max": 10000,
                "interpretation": "良好",
                "trend": "stable"
            }
        ]

        insights = [
            {
                "category": "身体活动",
                "description": "步行量达到健康推荐水平，有助于维持心血管健康。",
                "confidence": 0.9,
                "suggestions": [
                    "继续保持当前活动水平",
                    "考虑增加一些中等强度的运动",
                    "确保活动分布均匀，避免久坐不动"
                ]
            }
        ]

        return metrics, insights

    async def _analyze_sleep(self, user_id: str, sleep_data: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """分析睡眠数据

        Args:
            user_id: 用户ID
            sleep_data: 睡眠数据

        Returns:
            睡眠指标和见解
        """
        # 此处略去实现，返回示例结果
        metrics = [
            {
                "metric_name": "睡眠时长",
                "current_value": 7.2,
                "reference_min": 7,
                "reference_max": 9,
                "interpretation": "正常",
                "trend": "stable"
            },
            {
                "metric_name": "睡眠效率",
                "current_value": 85,
                "reference_min": 85,
                "reference_max": 95,
                "interpretation": "正常",
                "trend": "improving"
            }
        ]

        insights = [
            {
                "category": "睡眠",
                "description": "睡眠时长和效率均在健康范围内，但深度睡眠比例略低。",
                "confidence": 0.85,
                "suggestions": [
                    "考虑在睡前30分钟关闭电子设备",
                    "保持规律的睡眠时间",
                    "睡前避免摄入咖啡因和酒精"
                ]
            }
        ]

        return metrics, insights

    async def _analyze_blood_pressure(self, user_id: str, bp_data: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """分析血压数据

        Args:
            user_id: 用户ID
            bp_data: 血压数据

        Returns:
            血压指标和见解
        """
        # 此处略去实现，返回示例结果
        metrics = [
            {
                "metric_name": "收缩压",
                "current_value": 125,
                "reference_min": 90,
                "reference_max": 120,
                "interpretation": "轻度偏高",
                "trend": "stable"
            },
            {
                "metric_name": "舒张压",
                "current_value": 80,
                "reference_min": 60,
                "reference_max": 80,
                "interpretation": "正常",
                "trend": "stable"
            }
        ]

        insights = [
            {
                "category": "心血管健康",
                "description": "收缩压轻度偏高，但舒张压正常，属于临界高血压范围。",
                "confidence": 0.8,
                "suggestions": [
                    "减少钠盐摄入",
                    "规律进行有氧运动",
                    "学习压力管理技巧",
                    "保持健康体重"
                ]
            }
        ]

        return metrics, insights

    async def _fusion_analysis(self, user_id: str, metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """融合分析

        对多种指标进行交叉分析，生成综合见解

        Args:
            user_id: 用户ID
            metrics: 健康指标列表

        Returns:
            融合分析见解
        """
        # 此处略去实现，返回示例结果
        return [
            {
                "category": "综合健康",
                "description": "心血管指标与睡眠质量存在相关性，血压轻度升高可能与睡眠质量下降有关。",
                "confidence": 0.75,
                "suggestions": [
                    "改善睡眠环境和习惯",
                    "晚间避免使用电子设备",
                    "睡前放松活动如热水浴或轻度拉伸"
                ]
            }
        ]

    async def _detect_abnormalities(self, data_type: str, data: list[dict[str, Any]],
                                sensitivity: float) -> list[dict[str, Any]]:
        """检测异常

        使用统计方法检测数据中的异常

        Args:
            data_type: 数据类型
            data: 数据列表
            sensitivity: 敏感度（0-1）

        Returns:
            检测到的异常
        """
        # 此处略去实现，返回示例结果
        return [
            {
                "pattern_type": "心率异常",
                "severity": 0.7,
                "description": "在过去30天内，夜间心率多次出现异常峰值",
                "detection_time": int(datetime.now().timestamp() * 1000),
                "related_metrics": ["心率", "睡眠质量"],
                "suggested_actions": [
                    "检查睡眠环境",
                    "避免睡前摄入咖啡因和酒精",
                    "尝试放松技巧如深呼吸或冥想"
                ],
                "requires_attention": True
            }
        ]

    async def _analyze_pattern_correlations(self, patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """分析模式相关性

        分析多个异常模式之间的相关性

        Args:
            patterns: 异常模式列表

        Returns:
            相关性分析结果
        """
        # 此处略去实现，返回示例结果
        return [
            {
                "pattern_type": "复合异常",
                "severity": 0.8,
                "description": "心率异常与睡眠中断模式高度相关，可能指示潜在的睡眠呼吸暂停",
                "detection_time": int(datetime.now().timestamp() * 1000),
                "related_metrics": ["心率", "睡眠质量", "血氧"],
                "suggested_actions": [
                    "咨询医生进行睡眠评估",
                    "考虑专业睡眠监测",
                    "改善睡眠姿势和环境"
                ],
                "requires_attention": True
            }
        ]

    async def _predict_metric_trend(self, metric: str, data: list[dict[str, Any]],
                               prediction_days: int,
                               constitution_type: str | None) -> dict[str, Any]:
        """预测指标趋势

        基于历史数据和时间序列分析预测未来趋势

        Args:
            metric: 指标名称
            data: 历史数据
            prediction_days: 预测天数
            constitution_type: 体质类型

        Returns:
            预测结果
        """
        # 此处略去实现，返回示例结果
        return {
            "metric": "心率",
            "points": [
                {
                    "timestamp": int((datetime.now() + timedelta(days=i)).timestamp() * 1000),
                    "predicted_value": 75 + i * 0.2,
                    "lower_bound": 72 + i * 0.2,
                    "upper_bound": 78 + i * 0.2
                } for i in range(1, prediction_days + 1, 5)  # 每5天一个点
            ],
            "influencing_factors": ["季节变化", "活动模式", "睡眠习惯"],
            "confidence": 0.75
        }

    def _interpret_heart_rate(self, heart_rate: float) -> str:
        """解释心率值

        Args:
            heart_rate: 心率值

        Returns:
            心率解释
        """
        if heart_rate < 50:
            return "明显偏低"
        elif 50 <= heart_rate < 60:
            return "偏低"
        elif 60 <= heart_rate <= 100:
            return "正常"
        elif 100 < heart_rate <= 110:
            return "偏高"
        else:
            return "明显偏高"

    async def _save_analysis_results(self, user_id: str, results: dict[str, Any]) -> None:
        """保存分析结果

        将分析结果保存到数据库

        Args:
            user_id: 用户ID
            results: 分析结果
        """
        try:
            await self.repos.analysis_repo.save_sensor_analysis(
                user_id,
                datetime.now(),
                results
            )
        except Exception as e:
            logger.error(f"保存分析结果失败: {str(e)}")
            # 这里可以添加失败重试逻辑
