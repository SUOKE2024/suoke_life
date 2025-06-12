#!/usr/bin/env python3
"""
索克生活项目 - 快速性能监控演示
"""

import asyncio
import json
import logging
import random
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def quick_performance_demo():
    """快速性能监控演示"""
    print("📊 索克生活项目 - 性能监控演示")
    print("=" * 50)

    # 模拟监控数据收集
    monitoring_data = {
        "timestamp": datetime.now().isoformat(),
        "system_metrics": [],
        "service_metrics": [],
        "alerts": [],
    }

    # 收集系统指标
    logger.info("🔍 收集系统性能指标...")
    for i in range(5):
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": random.uniform(20, 80),
            "memory_usage": random.uniform(40, 75),
            "disk_usage": random.uniform(30, 60),
            "network_io": random.uniform(10, 100),
        }
        monitoring_data["system_metrics"].append(metrics)
        logger.info(
            f"  📈 CPU: {metrics['cpu_usage']:.1f}%, 内存: {metrics['memory_usage']:.1f}%"
        )
        await asyncio.sleep(0.5)

    # 收集服务指标
    logger.info("🔍 收集服务性能指标...")
    services = [
        "xiaoai-service",
        "xiaoke-service",
        "laoke-service",
        "soer-service",
        "api-gateway",
    ]

    for service in services:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "service_name": service,
            "response_time": random.uniform(0.2, 2.0),
            "requests_per_minute": random.randint(50, 200),
            "error_rate": random.uniform(0, 3),
            "status": "healthy",
        }

        if metrics["response_time"] > 1.5:
            metrics["status"] = "slow"
            monitoring_data["alerts"].append(
                {
                    "type": "performance",
                    "service": service,
                    "message": f"响应时间过长: {metrics['response_time']:.2f}s",
                }
            )

        monitoring_data["service_metrics"].append(metrics)
        logger.info(
            f"  🚀 {service}: {metrics['response_time']:.2f}s, {metrics['status']}"
        )
        await asyncio.sleep(0.3)

    # 生成报告
    report_file = (
        f"quick_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(monitoring_data, f, ensure_ascii=False, indent=2)

    # 显示摘要
    avg_cpu = sum(m["cpu_usage"] for m in monitoring_data["system_metrics"]) / len(
        monitoring_data["system_metrics"]
    )
    avg_memory = sum(
        m["memory_usage"] for m in monitoring_data["system_metrics"]
    ) / len(monitoring_data["system_metrics"])
    avg_response = sum(
        m["response_time"] for m in monitoring_data["service_metrics"]
    ) / len(monitoring_data["service_metrics"])

    print(f"\n✅ 性能监控演示完成!")
    print(f"📄 报告文件: {report_file}")
    print(f"\n📊 性能摘要:")
    print(f"  平均CPU使用率: {avg_cpu:.1f}%")
    print(f"  平均内存使用率: {avg_memory:.1f}%")
    print(f"  平均响应时间: {avg_response:.2f}s")
    print(f"  性能告警: {len(monitoring_data['alerts'])} 个")

    return report_file


if __name__ == "__main__":
    asyncio.run(quick_performance_demo())
