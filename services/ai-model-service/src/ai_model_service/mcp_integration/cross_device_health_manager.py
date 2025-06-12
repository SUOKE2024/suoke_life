"""
跨设备健康数据管理器
基于微软MCP AI升级版理念，实现跨应用、跨设备的健康数据无缝整合
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import aiohttp
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from ...communication_service.event_bus.core.agent_event_types import (
    LaokeEvents,
    SoerEvents,
    XiaoaiEvents,
    XiaokeEvents,
)
from ...communication_service.event_bus.core.event_bus import SuokeEventBus
from ..core.base_service import BaseAIService
from ..models.health_data import DeviceInfo, HealthDataPoint

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """设备类型枚举"""

    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    XIAOMI_HEALTH = "xiaomi_health"
    HUAWEI_HEALTH = "huawei_health"
    SAMSUNG_HEALTH = "samsung_health"
    POLAR = "polar"
    WITHINGS = "withings"
    OURA = "oura"


@dataclass
class HealthIntent:
    """健康意图数据类"""

    intent_type: str
    time_range: Optional[tuple] = None
    data_types: List[str] = None
    devices: List[str] = None
    analysis_level: str = "basic"  # basic, detailed, comprehensive
    urgency: str = "normal"  # low, normal, high, emergency


class CrossDeviceHealthManager(BaseAIService):
    """跨设备健康数据管理器"""

    def __init__(self, event_bus: SuokeEventBus, db_session: AsyncSession):
        super().__init__()
        self.event_bus = event_bus
        self.db_session = db_session
        self.device_connectors = {}
        self.nlp_processor = None
        self.health_analyzer = None
        self._initialize_connectors()

    def _initialize_connectors(self):
        """初始化设备连接器"""
        self.device_connectors = {
            DeviceType.APPLE_HEALTH: AppleHealthConnector(),
            DeviceType.GOOGLE_FIT: GoogleFitConnector(),
            DeviceType.FITBIT: FitbitConnector(),
            DeviceType.GARMIN: GarminConnector(),
            DeviceType.XIAOMI_HEALTH: XiaomiHealthConnector(),
            DeviceType.HUAWEI_HEALTH: HuaweiHealthConnector(),
            DeviceType.SAMSUNG_HEALTH: SamsungHealthConnector(),
            DeviceType.POLAR: PolarConnector(),
            DeviceType.WITHINGS: WithingsConnector(),
            DeviceType.OURA: OuraConnector(),
        }

    async def unified_health_query(
        self, user_id: str, user_request: str
    ) -> Dict[str, Any]:
        """统一健康数据查询 - MCP核心功能"""
        try:
            logger.info(f"处理用户 {user_id} 的健康查询: {user_request}")

            # 1. 自然语言理解用户意图
            intent = await self.parse_health_intent(user_request)
            logger.info(f"解析意图: {intent}")

            # 2. 跨设备数据获取
            health_data = await self.gather_cross_device_data(user_id, intent)
            logger.info(f"收集到 {len(health_data)} 条健康数据")

            # 3. 四智能体协作分析
            analysis = await self.collaborative_analysis(user_id, health_data, intent)

            # 4. 生成统一响应
            unified_response = await self.generate_unified_response(analysis, intent)

            # 5. 触发相关事件
            await self._trigger_relevant_events(user_id, intent, analysis)

            return {
                "success": True,
                "intent": intent.__dict__,
                "data_summary": {
                    "total_data_points": len(health_data),
                    "devices_involved": list(
                        set(d.get("device_type") for d in health_data)
                    ),
                    "time_range": intent.time_range,
                },
                "analysis": analysis,
                "unified_response": unified_response,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"统一健康查询失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def parse_health_intent(self, user_request: str) -> HealthIntent:
        """解析用户健康意图"""
        # 使用NLP模型解析用户意图
        intent_data = {
            "intent_type": "general_health_query",
            "time_range": None,
            "data_types": [],
            "devices": [],
            "analysis_level": "basic",
            "urgency": "normal",
        }

        # 时间范围识别
        if "今天" in user_request or "今日" in user_request:
            intent_data["time_range"] = (
                datetime.now().replace(hour=0, minute=0, second=0),
                datetime.now(),
            )
        elif "这周" in user_request or "本周" in user_request:
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            intent_data["time_range"] = (start_of_week, today)
        elif "这个月" in user_request or "本月" in user_request:
            today = datetime.now()
            start_of_month = today.replace(day=1)
            intent_data["time_range"] = (start_of_month, today)

        # 数据类型识别
        if "心率" in user_request or "心跳" in user_request:
            intent_data["data_types"].append("heart_rate")
        if "血压" in user_request:
            intent_data["data_types"].append("blood_pressure")
        if "步数" in user_request or "运动" in user_request:
            intent_data["data_types"].append("steps")
            intent_data["data_types"].append("activity")
        if "睡眠" in user_request:
            intent_data["data_types"].append("sleep")
        if "体重" in user_request:
            intent_data["data_types"].append("weight")

        # 分析级别识别
        if "详细" in user_request or "深入" in user_request:
            intent_data["analysis_level"] = "detailed"
        elif "全面" in user_request or "综合" in user_request:
            intent_data["analysis_level"] = "comprehensive"

        # 紧急程度识别
        if "紧急" in user_request or "急" in user_request:
            intent_data["urgency"] = "emergency"
        elif "重要" in user_request:
            intent_data["urgency"] = "high"

        return HealthIntent(**intent_data)

    async def gather_cross_device_data(
        self, user_id: str, intent: HealthIntent
    ) -> List[Dict[str, Any]]:
        """跨设备数据收集"""
        all_health_data = []

        # 获取用户已连接的设备
        connected_devices = await self.get_user_connected_devices(user_id)

        # 并行从所有设备获取数据
        data_tasks = []
        for device_info in connected_devices:
            device_type = DeviceType(device_info["device_type"])
            if device_type in self.device_connectors:
                connector = self.device_connectors[device_type]
                task = self.fetch_device_data(connector, user_id, device_info, intent)
                data_tasks.append(task)

        # 等待所有数据获取完成
        device_data_results = await asyncio.gather(*data_tasks, return_exceptions=True)

        # 整合所有设备数据
        for result in device_data_results:
            if isinstance(result, Exception):
                logger.warning(f"设备数据获取失败: {result}")
                continue
            if result:
                all_health_data.extend(result)

        # 数据去重和标准化
        standardized_data = await self.standardize_health_data(all_health_data)

        return standardized_data

    async def fetch_device_data(
        self, connector, user_id: str, device_info: Dict, intent: HealthIntent
    ) -> List[Dict[str, Any]]:
        """从单个设备获取数据"""
        try:
            # 根据意图确定数据获取参数
            fetch_params = {
                "user_id": user_id,
                "device_info": device_info,
                "data_types": intent.data_types or ["all"],
                "time_range": intent.time_range,
                "max_records": 1000,
            }

            # 调用设备连接器获取数据
            device_data = await connector.fetch_health_data(**fetch_params)

            # 添加设备信息到每条数据
            for data_point in device_data:
                data_point["device_type"] = device_info["device_type"]
                data_point["device_id"] = device_info["device_id"]
                data_point["source"] = "cross_device_integration"

            return device_data

        except Exception as e:
            logger.error(f"从设备 {device_info['device_type']} 获取数据失败: {e}")
            return []

    async def collaborative_analysis(
        self, user_id: str, health_data: List[Dict], intent: HealthIntent
    ) -> Dict[str, Any]:
        """四智能体协作分析"""
        analysis_results = {}

        # 根据分析级别决定参与的智能体
        participating_agents = ["xiaoai"]  # 小艾总是参与健康分析

        if intent.analysis_level in ["detailed", "comprehensive"]:
            participating_agents.extend(["xiaoke", "soer"])

        if intent.analysis_level == "comprehensive":
            participating_agents.append("laoke")

        # 并行启动智能体分析
        analysis_tasks = []

        if "xiaoai" in participating_agents:
            # 小艾：中医诊断分析
            task = self.xiaoai_health_analysis(user_id, health_data, intent)
            analysis_tasks.append(("xiaoai", task))

        if "xiaoke" in participating_agents:
            # 小克：服务资源分析
            task = self.xiaoke_service_analysis(user_id, health_data, intent)
            analysis_tasks.append(("xiaoke", task))

        if "laoke" in participating_agents:
            # 老克：知识支持分析
            task = self.laoke_knowledge_analysis(user_id, health_data, intent)
            analysis_tasks.append(("laoke", task))

        if "soer" in participating_agents:
            # 索儿：生活方式分析
            task = self.soer_lifestyle_analysis(user_id, health_data, intent)
            analysis_tasks.append(("soer", task))

        # 收集所有分析结果
        for agent_name, task in analysis_tasks:
            try:
                result = await task
                analysis_results[agent_name] = result
            except Exception as e:
                logger.error(f"{agent_name} 分析失败: {e}")
                analysis_results[agent_name] = {"success": False, "error": str(e)}

        # 智能体间交叉验证和共识决策
        if len(analysis_results) > 1:
            consensus = await self.generate_consensus_analysis(analysis_results)
            analysis_results["consensus"] = consensus

        return analysis_results

    async def xiaoai_health_analysis(
        self, user_id: str, health_data: List[Dict], intent: HealthIntent
    ) -> Dict[str, Any]:
        """小艾的中医健康分析"""
        # 发布事件给小艾智能体
        await self.event_bus.publish(
            XiaoaiEvents.CROSS_DEVICE_HEALTH_ANALYSIS_STARTED,
            {
                "user_id": user_id,
                "health_data": health_data,
                "intent": intent.__dict__,
                "analysis_type": "tcm_comprehensive",
            },
        )

        # 模拟小艾的分析结果（实际应该从小艾服务获取）
        return {
            "agent": "xiaoai",
            "analysis_type": "tcm_diagnosis",
            "constitution_analysis": {
                "primary_constitution": "气虚质",
                "secondary_constitution": "湿热质",
                "confidence": 0.85,
            },
            "syndrome_differentiation": {
                "main_syndrome": "脾胃虚弱",
                "secondary_syndrome": "肝郁气滞",
                "confidence": 0.78,
            },
            "recommendations": [
                {
                    "type": "dietary_therapy",
                    "content": "建议多食用健脾益气的食物，如山药、薏米、红枣",
                    "priority": "high",
                },
                {
                    "type": "acupoint_massage",
                    "content": "每日按摩足三里、脾俞穴各5分钟",
                    "priority": "medium",
                },
            ],
            "confidence": 0.82,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def xiaoke_service_analysis(
        self, user_id: str, health_data: List[Dict], intent: HealthIntent
    ) -> Dict[str, Any]:
        """小克的服务资源分析"""
        await self.event_bus.publish(
            XiaokeEvents.HEALTH_SERVICE_MATCHING_STARTED,
            {
                "user_id": user_id,
                "health_data_summary": self.summarize_health_data(health_data),
                "intent": intent.__dict__,
            },
        )

        return {
            "agent": "xiaoke",
            "analysis_type": "service_recommendation",
            "recommended_services": [
                {
                    "service_type": "health_checkup",
                    "provider": "北京协和医院",
                    "estimated_cost": 1200,
                    "urgency": "medium",
                },
                {
                    "service_type": "tcm_consultation",
                    "provider": "中医名医工作室",
                    "estimated_cost": 300,
                    "urgency": "low",
                },
            ],
            "agricultural_products": [
                {
                    "product": "有机山药",
                    "reason": "适合脾胃虚弱体质调理",
                    "supplier": "山东有机农场",
                }
            ],
            "confidence": 0.75,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def laoke_knowledge_analysis(
        self, user_id: str, health_data: List[Dict], intent: HealthIntent
    ) -> Dict[str, Any]:
        """老克的知识支持分析"""
        await self.event_bus.publish(
            LaokeEvents.HEALTH_KNOWLEDGE_SEARCH_STARTED,
            {
                "user_id": user_id,
                "health_context": self.extract_health_context(health_data),
                "knowledge_level": intent.analysis_level,
            },
        )

        return {
            "agent": "laoke",
            "analysis_type": "knowledge_support",
            "relevant_knowledge": [
                {
                    "topic": "脾胃虚弱的现代医学解释",
                    "content": "脾胃虚弱在现代医学中对应消化功能减弱...",
                    "source": "中医现代化研究",
                },
                {
                    "topic": "气虚质的生活调理",
                    "content": "气虚质人群应注意规律作息，适量运动...",
                    "source": "中医体质学",
                },
            ],
            "learning_path": [
                "了解中医体质理论",
                "学习脾胃调理方法",
                "掌握日常养生技巧",
            ],
            "confidence": 0.88,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def soer_lifestyle_analysis(
        self, user_id: str, health_data: List[Dict], intent: HealthIntent
    ) -> Dict[str, Any]:
        """索儿的生活方式分析"""
        await self.event_bus.publish(
            SoerEvents.LIFESTYLE_COMPREHENSIVE_ANALYSIS_STARTED,
            {
                "user_id": user_id,
                "health_data": health_data,
                "analysis_scope": "cross_device_integration",
            },
        )

        return {
            "agent": "soer",
            "analysis_type": "lifestyle_optimization",
            "lifestyle_assessment": {
                "sleep_quality": 0.65,
                "exercise_level": 0.45,
                "stress_level": 0.75,
                "diet_quality": 0.55,
            },
            "improvement_plan": [
                {
                    "area": "sleep_optimization",
                    "actions": ["建立固定睡眠时间", "睡前1小时避免电子设备"],
                    "target_improvement": 0.2,
                },
                {
                    "area": "stress_management",
                    "actions": ["每日10分钟冥想", "工作间隙深呼吸练习"],
                    "target_improvement": 0.3,
                },
            ],
            "personalized_goals": [
                "30天内改善睡眠质量至0.8以上",
                "降低压力水平至0.5以下",
            ],
            "confidence": 0.79,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def generate_consensus_analysis(
        self, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成智能体共识分析"""
        # 提取所有智能体的建议
        all_recommendations = []
        confidence_scores = []

        for agent, result in analysis_results.items():
            if result.get("success", True) and "recommendations" in result:
                for rec in result["recommendations"]:
                    rec["source_agent"] = agent
                    all_recommendations.append(rec)

            if "confidence" in result:
                confidence_scores.append(result["confidence"])

        # 计算共识置信度
        consensus_confidence = np.mean(confidence_scores) if confidence_scores else 0.0

        # 生成综合建议
        consensus_recommendations = await self.merge_recommendations(
            all_recommendations
        )

        return {
            "consensus_confidence": consensus_confidence,
            "participating_agents": list(analysis_results.keys()),
            "consensus_recommendations": consensus_recommendations,
            "analysis_summary": "基于四智能体协作分析，形成综合健康管理建议",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def merge_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """合并智能体建议"""
        # 按类型分组建议
        grouped_recs = {}
        for rec in recommendations:
            rec_type = rec.get("type", "general")
            if rec_type not in grouped_recs:
                grouped_recs[rec_type] = []
            grouped_recs[rec_type].append(rec)

        # 生成合并后的建议
        merged_recommendations = []
        for rec_type, recs in grouped_recs.items():
            if len(recs) == 1:
                merged_recommendations.append(recs[0])
            else:
                # 多个智能体有相同类型建议，进行合并
                merged_rec = {
                    "type": rec_type,
                    "content": f"综合{len(recs)}个智能体建议："
                    + "; ".join([r["content"] for r in recs]),
                    "priority": max(
                        [r.get("priority", "low") for r in recs],
                        key=lambda x: ["low", "medium", "high"].index(x),
                    ),
                    "supporting_agents": [r["source_agent"] for r in recs],
                    "consensus_strength": len(recs)
                    / len(set(r["source_agent"] for r in recommendations)),
                }
                merged_recommendations.append(merged_rec)

        return merged_recommendations

    async def generate_unified_response(
        self, analysis: Dict[str, Any], intent: HealthIntent
    ) -> str:
        """生成统一响应"""
        response_parts = []

        # 添加分析概述
        if "consensus" in analysis:
            consensus = analysis["consensus"]
            response_parts.append(
                f"基于跨设备数据分析，置信度 {consensus['consensus_confidence']:.2f}"
            )

        # 添加主要发现
        if "xiaoai" in analysis and analysis["xiaoai"].get("success", True):
            xiaoai_result = analysis["xiaoai"]
            if "constitution_analysis" in xiaoai_result:
                constitution = xiaoai_result["constitution_analysis"]
                response_parts.append(
                    f"中医体质分析：{constitution['primary_constitution']}"
                )

        # 添加关键建议
        if "consensus" in analysis:
            recommendations = analysis["consensus"].get("consensus_recommendations", [])
            if recommendations:
                high_priority_recs = [
                    r for r in recommendations if r.get("priority") == "high"
                ]
                if high_priority_recs:
                    response_parts.append(
                        f"重要建议：{high_priority_recs[0]['content']}"
                    )

        # 组合响应
        if response_parts:
            return "。".join(response_parts) + "。"
        else:
            return "已完成跨设备健康数据分析，请查看详细报告。"

    async def _trigger_relevant_events(
        self, user_id: str, intent: HealthIntent, analysis: Dict[str, Any]
    ):
        """触发相关事件"""
        # 根据分析结果触发相应事件
        if intent.urgency == "emergency":
            await self.event_bus.publish(
                "health.emergency.cross_device_analysis_completed",
                {
                    "user_id": user_id,
                    "analysis_summary": analysis,
                    "requires_immediate_attention": True,
                },
            )

        # 如果发现异常模式，触发预警
        if "consensus" in analysis:
            consensus_confidence = analysis["consensus"].get("consensus_confidence", 0)
            if consensus_confidence < 0.5:
                await self.event_bus.publish(
                    "health.analysis.low_confidence_warning",
                    {
                        "user_id": user_id,
                        "confidence": consensus_confidence,
                        "requires_manual_review": True,
                    },
                )

    # 辅助方法
    async def get_user_connected_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户已连接的设备"""
        # 这里应该从数据库查询用户的设备信息
        # 暂时返回模拟数据
        return [
            {
                "device_type": "apple_health",
                "device_id": "iphone_12",
                "status": "active",
            },
            {
                "device_type": "fitbit",
                "device_id": "fitbit_versa_3",
                "status": "active",
            },
            {
                "device_type": "xiaomi_health",
                "device_id": "mi_band_6",
                "status": "active",
            },
        ]

    async def standardize_health_data(self, raw_data: List[Dict]) -> List[Dict]:
        """标准化健康数据"""
        standardized = []
        for data_point in raw_data:
            # 数据标准化逻辑
            standardized_point = {
                "timestamp": data_point.get("timestamp"),
                "data_type": data_point.get("data_type"),
                "value": data_point.get("value"),
                "unit": data_point.get("unit"),
                "device_type": data_point.get("device_type"),
                "device_id": data_point.get("device_id"),
                "quality_score": data_point.get("quality_score", 1.0),
                "source": data_point.get("source", "unknown"),
            }
            standardized.append(standardized_point)
        return standardized

    def summarize_health_data(self, health_data: List[Dict]) -> Dict[str, Any]:
        """总结健康数据"""
        summary = {
            "total_points": len(health_data),
            "data_types": list(
                set(d.get("data_type") for d in health_data if d.get("data_type"))
            ),
            "devices": list(
                set(d.get("device_type") for d in health_data if d.get("device_type"))
            ),
            "time_span": None,
        }

        # 计算时间跨度
        timestamps = [d.get("timestamp") for d in health_data if d.get("timestamp")]
        if timestamps:
            timestamps = [
                datetime.fromisoformat(ts) if isinstance(ts, str) else ts
                for ts in timestamps
            ]
            summary["time_span"] = {
                "start": min(timestamps).isoformat(),
                "end": max(timestamps).isoformat(),
            }

        return summary

    def extract_health_context(self, health_data: List[Dict]) -> Dict[str, Any]:
        """提取健康上下文"""
        context = {"primary_concerns": [], "data_patterns": {}, "anomalies": []}

        # 分析数据模式
        for data_point in health_data:
            data_type = data_point.get("data_type")
            if data_type:
                if data_type not in context["data_patterns"]:
                    context["data_patterns"][data_type] = []
                context["data_patterns"][data_type].append(data_point.get("value"))

        return context


# 设备连接器基类和具体实现
class BaseDeviceConnector:
    """设备连接器基类"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        """获取健康数据"""
        raise NotImplementedError


class AppleHealthConnector(BaseDeviceConnector):
    """Apple Health 连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        # 模拟Apple Health数据获取
        return [
            {
                "data_type": "heart_rate",
                "value": 72,
                "unit": "bpm",
                "timestamp": datetime.utcnow().isoformat(),
                "quality_score": 0.95,
            },
            {
                "data_type": "steps",
                "value": 8500,
                "unit": "count",
                "timestamp": datetime.utcnow().isoformat(),
                "quality_score": 0.98,
            },
        ]


class GoogleFitConnector(BaseDeviceConnector):
    """Google Fit 连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        # 模拟Google Fit数据获取
        return [
            {
                "data_type": "activity",
                "value": 45,
                "unit": "minutes",
                "timestamp": datetime.utcnow().isoformat(),
                "quality_score": 0.92,
            }
        ]


class FitbitConnector(BaseDeviceConnector):
    """Fitbit 连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        # 模拟Fitbit数据获取
        return [
            {
                "data_type": "sleep",
                "value": 7.5,
                "unit": "hours",
                "timestamp": datetime.utcnow().isoformat(),
                "quality_score": 0.88,
            }
        ]


class GarminConnector(BaseDeviceConnector):
    """Garmin 连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        return []


class XiaomiHealthConnector(BaseDeviceConnector):
    """小米健康连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        return []


class HuaweiHealthConnector(BaseDeviceConnector):
    """华为健康连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        return []


class SamsungHealthConnector(BaseDeviceConnector):
    """三星健康连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        return []


class PolarConnector(BaseDeviceConnector):
    """Polar 连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        return []


class WithingsConnector(BaseDeviceConnector):
    """Withings 连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        return []


class OuraConnector(BaseDeviceConnector):
    """Oura 连接器"""

    async def fetch_health_data(self, **kwargs) -> List[Dict[str, Any]]:
        return []
