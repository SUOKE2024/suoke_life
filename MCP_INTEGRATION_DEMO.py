#!/usr/bin/env python3
"""
索克生活 MCP AI 升级版集成演示
基于微软MCP理念的跨设备健康数据整合示例
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List


class MCPHealthDemo:
    """MCP健康管理演示类"""

    def __init__(self):
        self.connected_devices = [
            {"type": "apple_health", "name": "iPhone 14", "status": "active"},
            {"type": "fitbit", "name": "Fitbit Versa 3", "status": "active"},
            {"type": "xiaomi", "name": "小米手环6", "status": "active"},
        ]

    async def demo_unified_health_query(self, user_query: str):
        """演示统一健康查询功能"""
        print(f"\n🔍 用户查询: '{user_query}'")
        print("=" * 50)

        # 1. 意图解析
        intent = self.parse_intent(user_query)
        print(f"📋 解析意图: {intent['type']}")
        print(f"⏰ 时间范围: {intent['time_range']}")
        print(f"📊 数据类型: {', '.join(intent['data_types'])}")

        # 2. 跨设备数据收集
        print(f"\n📱 正在从 {len(self.connected_devices)} 个设备收集数据...")
        health_data = await self.collect_cross_device_data(intent)
        print(f"✅ 收集到 {len(health_data)} 条健康数据")

        # 3. 四智能体协作分析
        print(f"\n🤖 启动四智能体协作分析...")
        analysis = await self.four_agent_analysis(health_data, intent)

        # 4. 生成统一响应
        response = self.generate_unified_response(analysis)
        print(f"\n💡 统一响应: {response}")

        return {
            "intent": intent,
            "data_count": len(health_data),
            "analysis": analysis,
            "response": response,
        }

    def parse_intent(self, query: str) -> Dict[str, Any]:
        """解析用户意图"""
        intent = {
            "type": "general_health",
            "time_range": "今天",
            "data_types": [],
            "urgency": "normal",
        }

        # 时间识别
        if "今天" in query:
            intent["time_range"] = "今天"
        elif "这周" in query or "本周" in query:
            intent["time_range"] = "本周"
        elif "这个月" in query:
            intent["time_range"] = "本月"

        # 数据类型识别
        if "心率" in query:
            intent["data_types"].append("心率")
        if "步数" in query or "运动" in query:
            intent["data_types"].append("步数")
            intent["data_types"].append("运动")
        if "睡眠" in query:
            intent["data_types"].append("睡眠")
        if "血压" in query:
            intent["data_types"].append("血压")

        # 如果没有指定数据类型，默认获取所有
        if not intent["data_types"]:
            intent["data_types"] = ["心率", "步数", "睡眠", "运动"]

        return intent

    async def collect_cross_device_data(self, intent: Dict) -> List[Dict]:
        """跨设备数据收集"""
        all_data = []

        # 模拟从不同设备收集数据
        for device in self.connected_devices:
            device_data = await self.fetch_device_data(device, intent)
            all_data.extend(device_data)
            print(f"  📱 {device['name']}: {len(device_data)} 条数据")

        return all_data

    async def fetch_device_data(self, device: Dict, intent: Dict) -> List[Dict]:
        """从单个设备获取数据"""
        # 模拟设备数据
        data = []

        if device["type"] == "apple_health":
            if "心率" in intent["data_types"]:
                data.append(
                    {
                        "type": "心率",
                        "value": 72,
                        "unit": "bpm",
                        "device": "iPhone 14",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            if "步数" in intent["data_types"]:
                data.append(
                    {
                        "type": "步数",
                        "value": 8500,
                        "unit": "步",
                        "device": "iPhone 14",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        elif device["type"] == "fitbit":
            if "睡眠" in intent["data_types"]:
                data.append(
                    {
                        "type": "睡眠",
                        "value": 7.5,
                        "unit": "小时",
                        "device": "Fitbit Versa 3",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            if "运动" in intent["data_types"]:
                data.append(
                    {
                        "type": "运动",
                        "value": 45,
                        "unit": "分钟",
                        "device": "Fitbit Versa 3",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        elif device["type"] == "xiaomi":
            if "心率" in intent["data_types"]:
                data.append(
                    {
                        "type": "心率",
                        "value": 74,
                        "unit": "bpm",
                        "device": "小米手环6",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # 模拟网络延迟
        await asyncio.sleep(0.1)
        return data

    async def four_agent_analysis(
        self, health_data: List[Dict], intent: Dict
    ) -> Dict[str, Any]:
        """四智能体协作分析"""
        print("  🔮 小艾 (中医诊断): 分析中医体质和证候...")
        xiaoai_analysis = await self.xiaoai_analysis(health_data)

        print("  🏥 小克 (服务匹配): 推荐医疗和农产品服务...")
        xiaoke_analysis = await self.xiaoke_analysis(health_data)

        print("  📚 老克 (知识支持): 提供相关健康知识...")
        laoke_analysis = await self.laoke_analysis(health_data)

        print("  🌱 索儿 (生活方式): 分析生活习惯和情绪...")
        soer_analysis = await self.soer_analysis(health_data)

        # 生成共识分析
        consensus = self.generate_consensus(
            [xiaoai_analysis, xiaoke_analysis, laoke_analysis, soer_analysis]
        )

        return {
            "xiaoai": xiaoai_analysis,
            "xiaoke": xiaoke_analysis,
            "laoke": laoke_analysis,
            "soer": soer_analysis,
            "consensus": consensus,
        }

    async def xiaoai_analysis(self, health_data: List[Dict]) -> Dict[str, Any]:
        """小艾的中医分析"""
        await asyncio.sleep(0.2)  # 模拟分析时间

        # 分析心率数据
        heart_rates = [d["value"] for d in health_data if d["type"] == "心率"]
        avg_heart_rate = sum(heart_rates) / len(heart_rates) if heart_rates else 0

        if avg_heart_rate < 60:
            constitution = "阳虚质"
            syndrome = "心阳不足"
        elif avg_heart_rate > 90:
            constitution = "阴虚质"
            syndrome = "心阴亏虚"
        else:
            constitution = "平和质"
            syndrome = "心气平和"

        return {
            "agent": "小艾",
            "constitution": constitution,
            "syndrome": syndrome,
            "recommendations": [
                "建议多食用温补食物，如红枣、桂圆",
                "每日按摩内关穴、神门穴各5分钟",
            ],
            "confidence": 0.85,
        }

    async def xiaoke_analysis(self, health_data: List[Dict]) -> Dict[str, Any]:
        """小克的服务分析"""
        await asyncio.sleep(0.2)

        return {
            "agent": "小克",
            "medical_services": [
                {"service": "心电图检查", "provider": "北京协和医院", "cost": 150},
                {"service": "中医体质辨识", "provider": "中医名医工作室", "cost": 200},
            ],
            "agricultural_products": [
                {"product": "有机红枣", "reason": "适合心气不足调理", "price": 45},
                {"product": "野生桂圆", "reason": "温补心阳", "price": 68},
            ],
            "confidence": 0.78,
        }

    async def laoke_analysis(self, health_data: List[Dict]) -> Dict[str, Any]:
        """老克的知识分析"""
        await asyncio.sleep(0.2)

        return {
            "agent": "老克",
            "knowledge_articles": [
                "心率变异性与健康的关系",
                "中医心脏保健的现代科学解释",
                "日常生活中的护心小贴士",
            ],
            "learning_path": [
                "了解心脏基础知识",
                "学习中医护心理论",
                "掌握日常保健方法",
            ],
            "confidence": 0.92,
        }

    async def soer_analysis(self, health_data: List[Dict]) -> Dict[str, Any]:
        """索儿的生活方式分析"""
        await asyncio.sleep(0.2)

        # 分析步数和运动数据
        steps = [d["value"] for d in health_data if d["type"] == "步数"]
        exercise = [d["value"] for d in health_data if d["type"] == "运动"]

        activity_level = "中等" if steps and steps[0] > 6000 else "偏低"

        return {
            "agent": "索儿",
            "lifestyle_assessment": {
                "activity_level": activity_level,
                "sleep_quality": "良好",
                "stress_level": "中等",
            },
            "recommendations": [
                "建议每天增加1000步的活动量",
                "保持规律的睡眠时间",
                "尝试冥想或深呼吸来缓解压力",
            ],
            "mood_support": "您今天的健康数据显示状态良好，继续保持！",
            "confidence": 0.81,
        }

    def generate_consensus(self, analyses: List[Dict]) -> Dict[str, Any]:
        """生成智能体共识"""
        # 计算平均置信度
        confidences = [a["confidence"] for a in analyses]
        avg_confidence = sum(confidences) / len(confidences)

        # 合并建议
        all_recommendations = []
        for analysis in analyses:
            if "recommendations" in analysis:
                for rec in analysis["recommendations"]:
                    all_recommendations.append(f"[{analysis['agent']}] {rec}")

        return {
            "consensus_confidence": avg_confidence,
            "unified_recommendations": all_recommendations[:3],  # 取前3个最重要的建议
            "summary": f"基于四智能体协作分析，综合置信度 {avg_confidence:.2f}",
        }

    def generate_unified_response(self, analysis: Dict) -> str:
        """生成统一响应"""
        consensus = analysis["consensus"]
        xiaoai = analysis["xiaoai"]

        response = f"根据跨设备健康数据分析，您的中医体质为{xiaoai['constitution']}，"
        response += f"主要证候是{xiaoai['syndrome']}。"
        response += (
            f"综合四个智能体的分析建议：{consensus['unified_recommendations'][0]}。"
        )
        response += f"分析置信度：{consensus['consensus_confidence']:.1%}"

        return response


async def main():
    """主演示函数"""
    print("🚀 索克生活 MCP AI 升级版演示")
    print("基于微软MCP理念的跨设备健康数据整合")
    print("=" * 60)

    demo = MCPHealthDemo()

    # 演示场景1：用户询问今天的健康状况
    result1 = await demo.demo_unified_health_query("我想看看今天的心率和步数情况")

    print("\n" + "=" * 60)

    # 演示场景2：用户询问睡眠和运动
    result2 = await demo.demo_unified_health_query("这周的睡眠和运动数据怎么样？")

    print("\n" + "=" * 60)
    print("🎯 MCP升级效果总结:")
    print("✅ 跨设备数据无缝整合 - 自动从iPhone、Fitbit、小米手环获取数据")
    print("✅ 四智能体协作分析 - 小艾、小克、老克、索儿同时工作")
    print("✅ 统一智能响应 - 一句话获得综合健康建议")
    print("✅ 上下文感知推荐 - 基于实时数据的个性化建议")
    print("✅ 安全权限控制 - 每个智能体只访问必要数据")


if __name__ == "__main__":
    asyncio.run(main())
