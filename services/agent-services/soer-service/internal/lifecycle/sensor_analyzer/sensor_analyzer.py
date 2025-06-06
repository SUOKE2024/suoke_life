"""
sensor_analyzer - 索克生活项目模块
"""

from typing import Any
import logging
import time

#!/usr/bin/env python3
"""
传感器数据分析器
"""


logger = logging.getLogger(__name__)

class SensorAnalyzer:
    """传感器数据分析器，负责分析来自各种设备的传感器数据"""

    def __init__(self):
        """初始化传感器分析器"""
        logger.info("初始化传感器数据分析器")

        # 分析阈值配置
        self.thresholds = {
            "heart_rate": {
                "low": 50,
                "high": 100,
                "very_high": 120
            },
            "blood_pressure": {
                "systolic_high": 140,
                "systolic_low": 90,
                "diastolic_high": 90,
                "diastolic_low": 60
            },
            "blood_oxygen": {
                "low": 95
            },
            "sleep": {
                "min_deep": 0.2,  # 深睡比例最低20%
                "min_duration": 7  # 最低时长7小时
            },
            "steps": {
                "daily_target": 8000
            },
            "stress": {
                "high": 70
            }
        }

    def analyze_data(self, user_id: str, sensor_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        分析传感器数据

        Args:
            user_id: 用户ID
            sensor_data: 传感器数据列表

        Returns:
            Dict[str, Any]: 分析结果
        """
        logger.info(f"开始分析用户 {user_id} 的传感器数据")

        # 初始化结果
        result = {
            "user_id": user_id,
            "timestamp": int(time.time()),
            "metrics": [],
            "insights": []
        }

        # 按传感器类型分组数据
        data_by_type = {}
        for data in sensor_data:
            sensor_type = data.get("sensor_type", "unknown")
            if sensor_type not in data_by_type:
                data_by_type[sensor_type] = []
            data_by_type[sensor_type].append(data)

        # 处理心率数据
        if "heart_rate" in data_by_type:
            self._analyze_heart_rate(data_by_type["heart_rate"], result)

        # 处理血压数据
        if "blood_pressure" in data_by_type:
            self._analyze_blood_pressure(data_by_type["blood_pressure"], result)

        # 处理血氧数据
        if "blood_oxygen" in data_by_type:
            self._analyze_blood_oxygen(data_by_type["blood_oxygen"], result)

        # 处理睡眠数据
        if "sleep" in data_by_type:
            self._analyze_sleep(data_by_type["sleep"], result)

        # 处理步数数据
        if "steps" in data_by_type:
            self._analyze_steps(data_by_type["steps"], result)

        # 处理压力数据
        if "stress" in data_by_type:
            self._analyze_stress(data_by_type["stress"], result)

        # 整合见解和建议
        self._generate_insights(result)

        logger.info(f"传感器数据分析完成，生成 {len(result['metrics'])} 个指标和 {len(result['insights'])} 条见解")
        return result

    def _analyze_heart_rate(self, heart_rate_data: list[dict[str, Any]], result: dict[str, Any]) -> None:
        """分析心率数据"""
        values = []

        # 提取所有心率值
        for data in heart_rate_data:
            for data_point in data.get("data_points", []):
                if "values" in data_point and "bpm" in data_point["values"]:
                    values.append(data_point["values"]["bpm"])

        if not values:
            return

        # 计算统计值
        avg_hr = np.mean(values)
        min_hr = np.min(values)
        max_hr = np.max(values)

        # 添加指标
        result["metrics"].append({
            "name": "平均心率",
            "value": round(avg_hr, 1),
            "unit": "bpm",
            "ref_min": self.thresholds["heart_rate"]["low"],
            "ref_max": self.thresholds["heart_rate"]["high"],
            "interpretation": self._interpret_heart_rate(avg_hr),
            "trend": "stable"  # 需要历史数据才能确定趋势
        })

        result["metrics"].append({
            "name": "最大心率",
            "value": round(max_hr, 1),
            "unit": "bpm",
            "ref_min": 0,
            "ref_max": self.thresholds["heart_rate"]["very_high"],
            "interpretation": "正常" if max_hr < self.thresholds["heart_rate"]["very_high"] else "偏高",
            "trend": "stable"
        })

        result["metrics"].append({
            "name": "最低心率",
            "value": round(min_hr, 1),
            "unit": "bpm",
            "ref_min": self.thresholds["heart_rate"]["low"] - 10,
            "ref_max": self.thresholds["heart_rate"]["high"],
            "interpretation": "正常" if min_hr > self.thresholds["heart_rate"]["low"] - 10 else "偏低",
            "trend": "stable"
        })

        # 心率变异性分析（需要原始数据）
        # TODO: 实现心率变异性分析

    def _interpret_heart_rate(self, heart_rate: float) -> str:
        """解释心率数值"""
        if heart_rate < self.thresholds["heart_rate"]["low"]:
            return "偏低，可能表示休息状态良好或心脏功能偏慢"
        elif heart_rate > self.thresholds["heart_rate"]["high"]:
            if heart_rate > self.thresholds["heart_rate"]["very_high"]:
                return "明显偏高，可能表示运动后恢复不足、压力大或其他问题"
            return "偏高，可能表示活动量大、情绪波动或轻度压力"
        else:
            return "正常范围，心脏功能良好"

    def _analyze_blood_pressure(self, bp_data: list[dict[str, Any]], result: dict[str, Any]) -> None:
        """分析血压数据"""
        systolic_values = []
        diastolic_values = []

        # 提取所有血压值
        for data in bp_data:
            for data_point in data.get("data_points", []):
                if "values" in data_point:
                    values = data_point["values"]
                    if "systolic" in values and "diastolic" in values:
                        systolic_values.append(values["systolic"])
                        diastolic_values.append(values["diastolic"])

        if not systolic_values or not diastolic_values:
            return

        # 计算统计值
        avg_systolic = np.mean(systolic_values)
        avg_diastolic = np.mean(diastolic_values)

        # 添加指标
        result["metrics"].append({
            "name": "平均收缩压",
            "value": round(avg_systolic, 1),
            "unit": "mmHg",
            "ref_min": self.thresholds["blood_pressure"]["systolic_low"],
            "ref_max": self.thresholds["blood_pressure"]["systolic_high"],
            "interpretation": self._interpret_blood_pressure(avg_systolic, True),
            "trend": "stable"
        })

        result["metrics"].append({
            "name": "平均舒张压",
            "value": round(avg_diastolic, 1),
            "unit": "mmHg",
            "ref_min": self.thresholds["blood_pressure"]["diastolic_low"],
            "ref_max": self.thresholds["blood_pressure"]["diastolic_high"],
            "interpretation": self._interpret_blood_pressure(avg_diastolic, False),
            "trend": "stable"
        })

    def _interpret_blood_pressure(self, value: float, is_systolic: bool) -> str:
        """解释血压数值"""
        if is_systolic:
            if value < self.thresholds["blood_pressure"]["systolic_low"]:
                return "偏低，可能表示低血压"
            elif value > self.thresholds["blood_pressure"]["systolic_high"]:
                return "偏高，可能表示高血压风险"
            else:
                return "正常范围"
        else:
            if value < self.thresholds["blood_pressure"]["diastolic_low"]:
                return "偏低，可能表示低血压"
            elif value > self.thresholds["blood_pressure"]["diastolic_high"]:
                return "偏高，可能表示高血压风险"
            else:
                return "正常范围"

    def _analyze_blood_oxygen(self, blood_oxygen_data: list[dict[str, Any]], result: dict[str, Any]) -> None:
        """分析血氧数据"""
        values = []

        # 提取所有血氧值
        for data in blood_oxygen_data:
            for data_point in data.get("data_points", []):
                if "values" in data_point and "spo2" in data_point["values"]:
                    values.append(data_point["values"]["spo2"])

        if not values:
            return

        # 计算统计值
        avg_spo2 = np.mean(values)
        min_spo2 = np.min(values)

        # 添加指标
        result["metrics"].append({
            "name": "平均血氧饱和度",
            "value": round(avg_spo2, 1),
            "unit": "%",
            "ref_min": self.thresholds["blood_oxygen"]["low"],
            "ref_max": 100,
            "interpretation": "正常" if avg_spo2 >= self.thresholds["blood_oxygen"]["low"] else "偏低",
            "trend": "stable"
        })

        result["metrics"].append({
            "name": "最低血氧饱和度",
            "value": round(min_spo2, 1),
            "unit": "%",
            "ref_min": self.thresholds["blood_oxygen"]["low"] - 2,
            "ref_max": 100,
            "interpretation": "正常" if min_spo2 >= self.thresholds["blood_oxygen"]["low"] - 2 else "偏低",
            "trend": "stable"
        })

    def _analyze_sleep(self, sleep_data: list[dict[str, Any]], result: dict[str, Any]) -> None:
        """分析睡眠数据"""
        total_duration = 0
        deep_sleep_duration = 0
        rem_sleep_duration = 0
        light_sleep_duration = 0
        awake_duration = 0
        sleep_count = 0

        # 提取睡眠数据
        for data in sleep_data:
            for data_point in data.get("data_points", []):
                if "values" not in data_point:
                    continue

                values = data_point["values"]

                if "duration" in values:
                    total_duration += values["duration"]
                    sleep_count += 1

                if "deep_sleep" in values:
                    deep_sleep_duration += values["deep_sleep"]

                if "rem_sleep" in values:
                    rem_sleep_duration += values["rem_sleep"]

                if "light_sleep" in values:
                    light_sleep_duration += values["light_sleep"]

                if "awake" in values:
                    awake_duration += values["awake"]

        if sleep_count == 0:
            return

        # 计算平均值
        avg_duration = total_duration / sleep_count
        avg_deep_sleep = deep_sleep_duration / sleep_count
        rem_sleep_duration / sleep_count
        light_sleep_duration / sleep_count
        avg_awake = awake_duration / sleep_count

        # 计算深睡比例
        if avg_duration > 0:
            deep_sleep_ratio = avg_deep_sleep / avg_duration
        else:
            deep_sleep_ratio = 0

        # 添加指标
        result["metrics"].append({
            "name": "平均睡眠时长",
            "value": round(avg_duration / 3600, 1),  # 转换为小时
            "unit": "小时",
            "ref_min": self.thresholds["sleep"]["min_duration"],
            "ref_max": 9,
            "interpretation": "正常" if avg_duration / 3600 >= self.thresholds["sleep"]["min_duration"] else "不足",
            "trend": "stable"
        })

        result["metrics"].append({
            "name": "深睡眠比例",
            "value": round(deep_sleep_ratio * 100, 1),
            "unit": "%",
            "ref_min": self.thresholds["sleep"]["min_deep"] * 100,
            "ref_max": 30,
            "interpretation": "正常" if deep_sleep_ratio >= self.thresholds["sleep"]["min_deep"] else "偏低",
            "trend": "stable"
        })

        # 睡眠效率
        if avg_duration > 0:
            sleep_efficiency = 1 - (avg_awake / avg_duration)
            result["metrics"].append({
                "name": "睡眠效率",
                "value": round(sleep_efficiency * 100, 1),
                "unit": "%",
                "ref_min": 85,
                "ref_max": 100,
                "interpretation": "正常" if sleep_efficiency >= 0.85 else "偏低",
                "trend": "stable"
            })

    def _analyze_steps(self, steps_data: list[dict[str, Any]], result: dict[str, Any]) -> None:
        """分析步数数据"""
        daily_steps = {}

        # 按天统计步数
        for data in steps_data:
            for data_point in data.get("data_points", []):
                if "values" not in data_point or "steps" not in data_point["values"]:
                    continue

                # 提取日期（忽略时间部分）
                timestamp = data_point.get("timestamp", 0)
                date = time.strftime("%Y-%m-%d", time.localtime(timestamp / 1000 if timestamp > 1e10 else timestamp))

                steps = data_point["values"]["steps"]

                if date not in daily_steps:
                    daily_steps[date] = 0
                daily_steps[date] += steps

        if not daily_steps:
            return

        # 计算平均步数
        avg_steps = sum(daily_steps.values()) / len(daily_steps)
        max_steps = max(daily_steps.values()) if daily_steps else 0

        # 添加指标
        result["metrics"].append({
            "name": "平均每日步数",
            "value": round(avg_steps),
            "unit": "步",
            "ref_min": self.thresholds["steps"]["daily_target"] / 2,
            "ref_max": self.thresholds["steps"]["daily_target"],
            "interpretation": self._interpret_steps(avg_steps),
            "trend": "stable"
        })

        result["metrics"].append({
            "name": "最高单日步数",
            "value": round(max_steps),
            "unit": "步",
            "ref_min": self.thresholds["steps"]["daily_target"],
            "ref_max": self.thresholds["steps"]["daily_target"] * 1.5,
            "interpretation": "达标" if max_steps >= self.thresholds["steps"]["daily_target"] else "未达标",
            "trend": "stable"
        })

    def _interpret_steps(self, steps: float) -> str:
        """解释步数"""
        if steps < self.thresholds["steps"]["daily_target"] / 2:
            return "活动量不足，建议增加日常活动"
        elif steps < self.thresholds["steps"]["daily_target"]:
            return "活动量一般，可以适当增加"
        else:
            return "活动量充足，保持良好习惯"

    def _analyze_stress(self, stress_data: list[dict[str, Any]], result: dict[str, Any]) -> None:
        """分析压力数据"""
        values = []

        # 提取所有压力值
        for data in stress_data:
            for data_point in data.get("data_points", []):
                if "values" in data_point and "stress_level" in data_point["values"]:
                    values.append(data_point["values"]["stress_level"])

        if not values:
            return

        # 计算统计值
        avg_stress = np.mean(values)
        max_stress = np.max(values)

        # 添加指标
        result["metrics"].append({
            "name": "平均压力水平",
            "value": round(avg_stress, 1),
            "unit": "分",
            "ref_min": 0,
            "ref_max": self.thresholds["stress"]["high"],
            "interpretation": self._interpret_stress(avg_stress),
            "trend": "stable"
        })

        result["metrics"].append({
            "name": "最高压力水平",
            "value": round(max_stress, 1),
            "unit": "分",
            "ref_min": 0,
            "ref_max": 100,
            "interpretation": self._interpret_stress(max_stress),
            "trend": "stable"
        })

    def _interpret_stress(self, stress: float) -> str:
        """解释压力水平"""
        if stress < 30:
            return "压力水平低，状态良好"
        elif stress < self.thresholds["stress"]["high"]:
            return "压力水平中等，状态可接受"
        else:
            return "压力水平高，建议放松减压"

    def _generate_insights(self, result: dict[str, Any]) -> None:
        """生成见解和建议"""
        metrics = result.get("metrics", [])
        if not metrics:
            return

        # 心率相关见解
        heart_rate_metrics = [m for m in metrics if "心率" in m["name"]]
        if heart_rate_metrics:
            avg_hr = next((m for m in heart_rate_metrics if m["name"] == "平均心率"), None)
            if avg_hr and avg_hr["value"] > self.thresholds["heart_rate"]["high"]:
                result["insights"].append({
                    "category": "心脏健康",
                    "description": "您的平均心率偏高，可能表示休息不足或压力较大",
                    "confidence": 0.8,
                    "suggestions": [
                        "尝试增加深呼吸和放松练习",
                        "确保充足的睡眠时间",
                        "减少咖啡因等刺激性物质摄入",
                        "定期进行温和的有氧运动"
                    ]
                })

        # 睡眠相关见解
        sleep_metrics = [m for m in metrics if "睡眠" in m["name"] or "深睡" in m["name"]]
        if sleep_metrics:
            sleep_duration = next((m for m in sleep_metrics if m["name"] == "平均睡眠时长"), None)
            deep_sleep = next((m for m in sleep_metrics if m["name"] == "深睡眠比例"), None)

            if sleep_duration and sleep_duration["value"] < self.thresholds["sleep"]["min_duration"]:
                result["insights"].append({
                    "category": "睡眠健康",
                    "description": "您的平均睡眠时长不足，可能影响白天表现和长期健康",
                    "confidence": 0.85,
                    "suggestions": [
                        "尝试固定的睡眠时间表",
                        "睡前1小时避免使用电子设备",
                        "营造安静、黑暗、凉爽的睡眠环境",
                        "睡前可以尝试热水浴或冥想"
                    ]
                })

            if deep_sleep and deep_sleep["value"] < self.thresholds["sleep"]["min_deep"] * 100:
                result["insights"].append({
                    "category": "睡眠质量",
                    "description": "您的深睡眠比例偏低，可能影响身体恢复和记忆巩固",
                    "confidence": 0.75,
                    "suggestions": [
                        "白天适度运动，避免睡前剧烈运动",
                        "睡前减少蓝光暴露",
                        "保持规律作息，避免熬夜",
                        "睡前避免重餐和过多液体摄入"
                    ]
                })

        # 活动量相关见解
        steps_metrics = [m for m in metrics if "步数" in m["name"]]
        if steps_metrics:
            avg_steps = next((m for m in steps_metrics if m["name"] == "平均每日步数"), None)
            if avg_steps and avg_steps["value"] < self.thresholds["steps"]["daily_target"]:
                result["insights"].append({
                    "category": "身体活动",
                    "description": "您的日常活动量低于推荐水平，可能影响代谢健康",
                    "confidence": 0.82,
                    "suggestions": [
                        "尝试每天步行至少30分钟",
                        "减少久坐时间，每小时起身活动5分钟",
                        "寻找感兴趣的活动形式，如跳舞、游泳或骑车",
                        "使用活动追踪器设定每日步数目标"
                    ]
                })

        # 压力相关见解
        stress_metrics = [m for m in metrics if "压力" in m["name"]]
        if stress_metrics:
            avg_stress = next((m for m in stress_metrics if m["name"] == "平均压力水平"), None)
            if avg_stress and avg_stress["value"] > self.thresholds["stress"]["high"]:
                result["insights"].append({
                    "category": "压力管理",
                    "description": "您的压力水平持续偏高，可能对身心健康造成负面影响",
                    "confidence": 0.78,
                    "suggestions": [
                        "尝试冥想、瑜伽或太极等放松方法",
                        "保持规律的身体活动",
                        "合理安排工作与休息时间",
                        "寻求社交支持，与朋友家人分享感受",
                        "考虑限制工作时间，确保有足够的个人时间"
                    ]
                })
