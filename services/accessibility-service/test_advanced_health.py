#!/usr/bin/env python3
"""
高级健康检查测试脚本
测试扩展的健康检查功能和告警系统
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from internal.service.advanced_health_check import (
    AlertManager,
    AlertRule,
    AlertSeverity,
    DiskSpaceHealthChecker,
    MemoryLeakHealthChecker,
    NetworkHealthChecker,
    ProcessHealthChecker,
    console_notification_handler,
    global_alert_manager,
    log_notification_handler,
    run_health_check_with_alerts,
    setup_advanced_health_checks,
    setup_default_alert_rules,
)
from internal.service.health_check import (
    get_health_summary,
    global_health_manager,
    setup_default_health_checks,
)


async def test_network_health_checker():
    """测试网络健康检查器"""
    print("🌐 测试网络健康检查器...")

    # 创建网络检查器
    endpoints = [
        "https://www.baidu.com",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",  # 故意失败的端点
        "https://nonexistent-domain-12345.com",  # 不存在的域名
    ]

    checker = NetworkHealthChecker(endpoints, timeout=3.0)
    result = await checker.check()

    print(f"  状态: {result.status.value}")
    print(f"  消息: {result.message}")
    print(f"  检查耗时: {result.duration:.2f}秒")

    if result.details:
        print("  端点详情:")
        for endpoint, info in result.details.get("endpoints", {}).items():
            status_icon = "✅" if info.get("success", False) else "❌"
            print(f"    {status_icon} {endpoint}: {info}")

    print("  ✅ 网络健康检查器测试完成\n")


async def test_disk_space_checker():
    """测试磁盘空间检查器"""
    print("💾 测试磁盘空间检查器...")

    # 创建磁盘空间检查器
    checker = DiskSpaceHealthChecker(
        paths=["/", "/tmp"] if sys.platform != "win32" else ["C:\\"],
        warning_threshold=70.0,
        critical_threshold=85.0,
    )

    result = await checker.check()

    print(f"  状态: {result.status.value}")
    print(f"  消息: {result.message}")

    if result.details and "disks" in result.details:
        print("  磁盘详情:")
        for path, info in result.details["disks"].items():
            if "error" not in info:
                print(
                    f"    {path}: {info['usage_percent']}% "
                    f"({info['used_gb']:.1f}GB / {info['total_gb']:.1f}GB)"
                )
            else:
                print(f"    {path}: 错误 - {info['error']}")

    print("  ✅ 磁盘空间检查器测试完成\n")


async def test_process_checker():
    """测试进程检查器"""
    print("🔄 测试进程检查器...")

    # 创建进程检查器
    required_processes = ["python", "python3", "nonexistent-process-12345"]
    checker = ProcessHealthChecker(required_processes)

    result = await checker.check()

    print(f"  状态: {result.status.value}")
    print(f"  消息: {result.message}")

    if result.details and "processes" in result.details:
        print("  进程详情:")
        for proc_name, info in result.details["processes"].items():
            status_icon = "✅" if info["running"] else "❌"
            print(f"    {status_icon} {proc_name}: {info['status']}")

    print("  ✅ 进程检查器测试完成\n")


async def test_memory_leak_checker():
    """测试内存泄漏检查器"""
    print("🧠 测试内存泄漏检查器...")

    # 创建内存泄漏检查器
    checker = MemoryLeakHealthChecker(threshold_mb=500.0)

    # 多次检查以建立历史记录
    for i in range(3):
        result = await checker.check()
        print(f"  检查 {i+1}: {result.status.value} - {result.message}")

        if i < 2:  # 不是最后一次
            await asyncio.sleep(0.5)

    if result.details:
        print(f"  当前内存: {result.details['current_memory_mb']}MB")
        print(f"  内存趋势: {result.details['memory_trend']}")
        print(f"  历史记录点: {result.details['history_points']}")

    print("  ✅ 内存泄漏检查器测试完成\n")


async def test_alert_system():
    """测试告警系统"""
    print("🚨 测试告警系统...")

    # 创建告警管理器
    alert_manager = AlertManager()

    # 添加测试告警规则
    test_rule = AlertRule(
        name="test_alert",
        condition="any_unhealthy or degraded_count >= 1",
        severity=AlertSeverity.WARNING,
        message_template="测试告警: 发现 {unhealthy_count} 个严重问题和 {degraded_count} 个警告",
        cooldown_seconds=10,
    )

    alert_manager.add_alert_rule(test_rule)
    alert_manager.add_notification_handler(console_notification_handler)

    # 模拟健康检查结果
    from internal.service.health_check import HealthCheckResult, HealthStatus

    mock_results = [
        HealthCheckResult(
            name="test_check_1", status=HealthStatus.HEALTHY, message="正常"
        ),
        HealthCheckResult(
            name="test_check_2", status=HealthStatus.DEGRADED, message="性能下降"
        ),
        HealthCheckResult(
            name="test_check_3", status=HealthStatus.UNHEALTHY, message="严重问题"
        ),
    ]

    # 评估告警
    await alert_manager.evaluate_alerts(mock_results)

    # 获取告警摘要
    summary = alert_manager.get_alert_summary()
    print(f"  活跃告警: {summary['active_alerts']}")
    print(f"  告警规则: {summary['enabled_rules']}/{summary['total_rules']}")

    # 显示活跃告警
    active_alerts = alert_manager.get_active_alerts()
    for alert in active_alerts:
        print(f"  📢 {alert.rule_name}: {alert.message}")

    print("  ✅ 告警系统测试完成\n")


async def test_integrated_health_system():
    """测试集成健康系统"""
    print("🏥 测试集成健康系统...")

    # 设置基础健康检查
    config = Config()
    setup_default_health_checks(config=config)

    # 设置高级健康检查
    setup_advanced_health_checks()

    # 设置告警规则
    setup_default_alert_rules()

    print("  📋 已设置的健康检查器:")
    for checker in global_health_manager.checkers:
        print(f"    - {checker.name}")

    # 运行完整的健康检查和告警评估
    print("\n  🔍 执行健康检查...")
    health = await run_health_check_with_alerts()

    print(f"  整体状态: {health.overall_status.value}")
    print(f"  检查项目: {len(health.checks)}")

    # 显示检查结果
    for check in health.checks:
        status_icons = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "unknown": "❓",
        }
        icon = status_icons.get(check.status.value, "❓")
        print(f"    {icon} {check.name}: {check.message}")

    # 显示告警摘要
    alert_summary = global_alert_manager.get_alert_summary()
    if alert_summary["active_alerts"] > 0:
        print(f"\n  🚨 活跃告警: {alert_summary['active_alerts']}")
        for alert in global_alert_manager.get_active_alerts():
            print(f"    - [{alert.severity.value}] {alert.message}")
    else:
        print("\n  ✅ 无活跃告警")

    print("  ✅ 集成健康系统测试完成\n")


async def test_performance_impact():
    """测试性能影响"""
    print("⚡ 测试性能影响...")

    # 测试多次健康检查的性能
    start_time = time.time()

    for i in range(5):
        health = await global_health_manager.check_health()
        print(f"  检查 {i+1}: {len(health.checks)} 项检查完成")

    total_time = time.time() - start_time
    avg_time = total_time / 5

    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  平均耗时: {avg_time:.2f}秒/次")
    print(
        f"  性能评估: {'优秀' if avg_time < 2 else '良好' if avg_time < 5 else '需要优化'}"
    )

    print("  ✅ 性能影响测试完成\n")


async def main():
    """主测试函数"""
    print("🚀 开始高级健康检查测试...\n")

    try:
        # 运行各项测试
        await test_network_health_checker()
        await test_disk_space_checker()
        await test_process_checker()
        await test_memory_leak_checker()
        await test_alert_system()
        await test_integrated_health_system()
        await test_performance_impact()

        print("🎉 所有高级健康检查测试完成！")

        # 最终统计
        print("\n📊 最终统计:")
        health_summary = get_health_summary()
        print(f"  健康检查器数量: {len(global_health_manager.checkers)}")
        print(f"  告警规则数量: {len(global_alert_manager.alert_rules)}")
        print(f"  系统运行时间: {health_summary.get('uptime', 0):.1f}秒")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

        logger.error("An error occurred", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
