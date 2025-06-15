#!/usr/bin/env python3
"""
测试改进功能脚本
验证错误处理、性能监控、健康检查等新功能
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from internal.service.error_handling import (
    ErrorCategory,
    ErrorSeverity,
    async_error_handler,
    error_handler,
    global_error_handler,
    handle_configuration_error,
    handle_model_loading_error,
)
from internal.service.health_check import (
    ConfigurationHealthChecker,
    SystemResourceHealthChecker,
    check_service_health,
    get_health_summary,
    global_health_manager,
    setup_default_health_checks,
)
from internal.service.performance_monitor import (
    PerformanceCollector,
    PerformanceMonitor,
)


def test_error_handling() -> None:
    """测试错误处理功能"""
    print("🔧 测试错误处理功能...")

    # 测试基本错误处理
    try:
        raise ValueError("这是一个测试错误")
    except Exception as e:
        error_info = global_error_handler.handle_error(
            error=e,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context={"test": "error_handling"},
            recovery_suggestion="这是一个测试，可以忽略",
        )
        print(f"  ✅ 错误处理成功: {error_info.error_id}")

    # 测试装饰器
    @error_handler(
        category=ErrorCategory.DATA_PROCESSING,
        severity=ErrorSeverity.LOW,
        recovery_suggestion="重试操作",
    )
    def test_function() -> None:
        raise RuntimeError("装饰器测试错误")

    result = test_function()
    print(f"  ✅ 装饰器错误处理: {result}")

    # 获取错误统计
    stats = global_error_handler.get_error_stats()
    print(f"  📊 错误统计: {stats}")

    print("  ✅ 错误处理功能测试完成\n")


def test_performance_monitoring() -> None:
    """测试性能监控功能"""
    print("📊 测试性能监控功能...")

    # 创建性能收集器
    collector = PerformanceCollector()

    # 测试计数器
    collector.record_counter("test_counter", 1, {"type": "test"})
    collector.record_counter("test_counter", 2, {"type": "test"})
    print("  ✅ 计数器记录")

    # 测试仪表盘
    collector.record_gauge("test_gauge", 75.5, {"unit": "percent"})
    print("  ✅ 仪表盘记录")

    # 测试直方图
    for i in range(5):
        collector.record_histogram("test_histogram", i * 0.1, {"operation": "test"})
    print("  ✅ 直方图记录")

    # 测试计时器
    start_time = time.time()
    time.sleep(0.1)
    duration = time.time() - start_time
    collector.record_timer("test_timer", duration, {"function": "test"})
    print("  ✅ 计时器记录")

    # 获取指标
    metrics = collector.get_metrics("test_counter")
    print(f"  📊 获取指标: {metrics['name'] if metrics else '无数据'}")

    print("  ✅ 性能监控功能测试完成\n")


async def test_health_checks() -> None:
    """测试健康检查功能"""
    print("🏥 测试健康检查功能...")

    # 设置健康检查
    config = Config()
    setup_default_health_checks(config=config)

    # 添加自定义检查器
    global_health_manager.add_checker(SystemResourceHealthChecker())

    # 执行健康检查
    health = await check_service_health()
    print(f"  ✅ 整体健康状态: {health.overall_status.value}")
    print(f"  📊 检查项目数: {len(health.checks)}")

    for check in health.checks:
        status_icon = (
            "✅"
            if check.status.value == "healthy"
            else "⚠️" if check.status.value == "degraded" else "❌"
        )
        print(f"    {status_icon} {check.name}: {check.status.value} - {check.message}")

    # 获取健康摘要
    summary = get_health_summary()
    print(f"  📈 服务运行时间: {summary['uptime']:.1f}秒")

    print("  ✅ 健康检查功能测试完成\n")


def test_integration() -> None:
    """测试功能集成"""
    print("🔗 测试功能集成...")

    # 组合使用错误处理和性能监控
    collector = PerformanceCollector()

    @error_handler(
        category=ErrorCategory.DATA_PROCESSING,
        severity=ErrorSeverity.MEDIUM,
        reraise=False,
    )
    def integrated_function(should_fail=False):
        start_time = time.time()
        try:
            if should_fail:
                raise ValueError("集成测试错误")
            time.sleep(0.05)
            return "集成测试成功"
        finally:
            duration = time.time() - start_time
            collector.record_timer("integrated_function", duration)

    # 测试成功情况
    result1 = integrated_function(should_fail=False)
    print(f"  ✅ 集成测试（成功）: {result1}")

    # 测试失败情况
    result2 = integrated_function(should_fail=True)
    print(f"  ✅ 集成测试（失败处理）: {result2}")

    print("  ✅ 功能集成测试完成\n")


async def main() -> None:
    """主测试函数"""
    print("🚀 开始测试改进功能...\n")

    try:
        # 运行各项测试
        test_error_handling()
        test_performance_monitoring()
        await test_health_checks()
        test_integration()

        print("🎉 所有改进功能测试完成！")

        # 显示最终统计
        print("\n📊 最终统计:")

        # 错误统计
        error_stats = global_error_handler.get_error_stats()
        print(f"  错误处理: {error_stats['total_errors']} 个错误已处理")

        # 健康检查统计
        health_summary = get_health_summary()
        print(f"  健康检查: {len(health_summary['checks'])} 项检查")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

        logger.error("An error occurred", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
