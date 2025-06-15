#!/usr/bin/env python3
"""
性能告警测试脚本
测试性能阈值管理和告警功能
"""

import asyncio
import random
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from internal.service.performance_alerting import (
    AlertLevel,
    MetricSnapshot,
    MetricType,
    PerformanceThresholdManager,
    ThresholdRule,
    ThresholdType,
    console_performance_alert_handler,
    get_performance_alert_summary,
    get_performance_alerts,
    global_performance_threshold_manager,
    log_performance_alert_handler,
    record_performance_metric,
    setup_default_performance_thresholds,
)


async def test_static_threshold():
    """测试静态阈值"""
    print("📊 测试静态阈值...")

    # 创建阈值管理器
    manager = PerformanceThresholdManager()

    # 添加静态阈值规则
    rule = ThresholdRule(
        name="test_cpu_high",
        metric_name="cpu_usage",
        threshold_type=ThresholdType.STATIC,
        alert_level=AlertLevel.WARNING,
        value=80.0,
        comparison=">",
        duration_seconds=5,
        description="CPU使用率过高",
    )

    manager.add_threshold_rule(rule)
    manager.add_alert_callback(console_performance_alert_handler)

    # 模拟正常数据
    for i in range(5):
        snapshot = MetricSnapshot(
            name="cpu_usage",
            value=60.0 + random.uniform(-5, 5),
            timestamp=time.time(),
            metric_type=MetricType.GAUGE,
        )
        manager.record_metric(snapshot)
        await asyncio.sleep(0.1)

    print("  记录正常CPU数据...")
    await manager.evaluate_thresholds()
    print(f"  活跃告警: {len(manager.get_active_alerts())}")

    # 模拟异常数据
    for i in range(8):
        snapshot = MetricSnapshot(
            name="cpu_usage",
            value=85.0 + random.uniform(-2, 5),
            timestamp=time.time(),
            metric_type=MetricType.GAUGE,
        )
        manager.record_metric(snapshot)
        await asyncio.sleep(0.7)  # 确保超过持续时间

    print("  记录异常CPU数据...")
    await manager.evaluate_thresholds()

    alerts = manager.get_active_alerts()
    print(f"  活跃告警: {len(alerts)}")
    for alert in alerts:
        print(f"    - {alert.rule_name}: {alert.message}")

    print("  ✅ 静态阈值测试完成\n")


async def test_integrated_performance_alerting():
    """测试集成性能告警"""
    print("🔧 测试集成性能告警...")

    # 设置默认阈值
    setup_default_performance_thresholds()

    print("  📋 已设置的阈值规则:")
    for rule in global_performance_threshold_manager.threshold_rules:
        print(f"    - {rule.name}: {rule.description}")

    # 模拟各种性能指标
    print("\n  📊 模拟性能数据...")

    # CPU数据
    for i in range(10):
        cpu_value = 70 + i * 2  # 逐渐增加
        record_performance_metric(
            "cpu_percent", cpu_value, metric_type=MetricType.GAUGE
        )
        await asyncio.sleep(0.1)

    # 内存数据
    for i in range(10):
        memory_value = 85 + i * 1  # 逐渐增加到超过阈值
        record_performance_metric(
            "memory_percent", memory_value, metric_type=MetricType.GAUGE
        )
        await asyncio.sleep(0.1)

    # 评估阈值
    print("  🔍 评估性能阈值...")
    await global_performance_threshold_manager.evaluate_thresholds()

    # 显示结果
    alerts = get_performance_alerts()
    summary = get_performance_alert_summary()

    print("\n  📊 告警摘要:")
    print(f"    活跃告警: {summary['active_alerts']}")
    print(f"    启用规则: {summary['enabled_rules']}/{summary['total_rules']}")

    if alerts:
        print("\n  🚨 活跃告警详情:")
        for alert in alerts:
            print(
                f"    - [{alert.alert_level.value}] {alert.rule_name}: {alert.message}"
            )
    else:
        print("\n  ✅ 无活跃告警")

    print("  ✅ 集成性能告警测试完成\n")


async def main():
    """主测试函数"""
    print("🚀 开始性能告警测试...\n")

    try:
        # 运行各项测试
        await test_static_threshold()
        await test_integrated_performance_alerting()

        print("🎉 所有性能告警测试完成！")

        # 最终统计
        print("\n📊 最终统计:")
        summary = get_performance_alert_summary()
        print(f"  全局告警规则: {summary['total_rules']}")
        print(f"  活跃告警: {summary['active_alerts']}")
        print(f"  告警历史: {summary['alert_history_count']}")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

        logger.error("An error occurred", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
