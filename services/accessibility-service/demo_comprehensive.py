#!/usr/bin/env python3
"""
无障碍服务综合演示脚本
展示所有改进功能的集成效果
"""

import asyncio
import random
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from internal.service.advanced_health_check import (
    global_alert_manager,
    run_health_check_with_alerts,
    setup_advanced_health_checks,
    setup_default_alert_rules,
)
from internal.service.error_handling import (
    ErrorCategory,
    ErrorHandler,
    ErrorSeverity,
    error_handler,
)
from internal.service.health_check import (
    global_health_manager,
    setup_default_health_checks,
)
from internal.service.performance_alerting import (
    MetricType,
    get_performance_alert_summary,
    get_performance_alerts,
    global_performance_threshold_manager,
    record_performance_metric,
    setup_default_performance_thresholds,
)
from internal.service.performance_monitor import PerformanceCollector


class ComprehensiveDemo:
    """综合演示类"""

    def __init__(self):
        self.config = Config()
        self.performance_collector = PerformanceCollector()
        self.error_handler = ErrorHandler()
        self.demo_start_time = time.time()

    async def initialize_systems(self):
        """初始化所有系统"""
        print("🚀 初始化无障碍服务系统...")

        # 初始化基础健康检查
        setup_default_health_checks(config=self.config)
        print("  ✅ 基础健康检查系统已初始化")

        # 初始化高级健康检查
        setup_advanced_health_checks()
        print("  ✅ 高级健康检查系统已初始化")

        # 初始化告警规则
        setup_default_alert_rules()
        print("  ✅ 健康告警规则已设置")

        # 初始化性能阈值
        setup_default_performance_thresholds()
        print("  ✅ 性能告警阈值已设置")

        print("  📊 系统组件统计:")
        print(f"    - 健康检查器: {len(global_health_manager.checkers)}")
        print(f"    - 健康告警规则: {len(global_alert_manager.alert_rules)}")
        print(
            f"    - 性能告警规则: {len(global_performance_threshold_manager.threshold_rules)}"
        )
        print()

    async def simulate_normal_operations(self):
        """模拟正常运行状态"""
        print("📈 模拟正常运行状态...")

        # 模拟正常的性能指标
        for i in range(10):
            # CPU使用率
            cpu_usage = 30 + random.uniform(-5, 10)
            record_performance_metric(
                "cpu_percent", cpu_usage, metric_type=MetricType.GAUGE
            )

            # 内存使用率
            memory_usage = 45 + random.uniform(-5, 5)
            record_performance_metric(
                "memory_percent", memory_usage, metric_type=MetricType.GAUGE
            )

            # 响应时间
            response_time = 100 + random.gauss(0, 15)
            record_performance_metric(
                "response_time", max(0, response_time), metric_type=MetricType.TIMER
            )

            # 错误率
            error_rate = random.uniform(0, 2)
            record_performance_metric(
                "error_rate", error_rate, metric_type=MetricType.GAUGE
            )

            await asyncio.sleep(0.2)

        print("  ✅ 正常运行数据已记录")

        # 执行健康检查
        health = await run_health_check_with_alerts()
        print(f"  📊 健康状态: {health.overall_status.value}")

        # 评估性能阈值
        await global_performance_threshold_manager.evaluate_thresholds()
        perf_summary = get_performance_alert_summary()
        print(f"  📊 性能告警: {perf_summary['active_alerts']} 个活跃")
        print()

    async def simulate_performance_issues(self):
        """模拟性能问题"""
        print("⚠️ 模拟性能问题...")

        # 模拟CPU使用率过高
        print("  🔥 模拟CPU使用率过高...")
        for i in range(8):
            cpu_usage = 85 + random.uniform(-3, 8)
            record_performance_metric(
                "cpu_percent", cpu_usage, metric_type=MetricType.GAUGE
            )
            await asyncio.sleep(0.5)

        # 模拟内存使用率过高
        print("  🧠 模拟内存使用率过高...")
        for i in range(6):
            memory_usage = 92 + random.uniform(-2, 5)
            record_performance_metric(
                "memory_percent", memory_usage, metric_type=MetricType.GAUGE
            )
            await asyncio.sleep(0.4)

        # 模拟响应时间异常
        print("  🐌 模拟响应时间异常...")
        for i in range(10):
            response_time = 500 + random.uniform(0, 200)
            record_performance_metric(
                "response_time", response_time, metric_type=MetricType.TIMER
            )
            await asyncio.sleep(0.3)

        # 评估性能阈值
        await global_performance_threshold_manager.evaluate_thresholds()

        # 显示告警
        perf_alerts = get_performance_alerts()
        if perf_alerts:
            print(f"  🚨 触发了 {len(perf_alerts)} 个性能告警:")
            for alert in perf_alerts:
                print(
                    f"    - [{alert.alert_level.value}] {alert.rule_name}: {alert.message}"
                )

        print()

    async def simulate_system_failures(self):
        """模拟系统故障"""
        print("❌ 模拟系统故障...")

        # 执行健康检查（会检测到网络和进程问题）
        health = await run_health_check_with_alerts()

        print("  📊 健康检查结果:")
        print(f"    整体状态: {health.overall_status.value}")

        failed_checks = [
            check
            for check in health.checks
            if check.status.value in ["unhealthy", "degraded"]
        ]
        if failed_checks:
            print(f"    问题检查项: {len(failed_checks)}")
            for check in failed_checks:
                status_icon = "❌" if check.status.value == "unhealthy" else "⚠️"
                print(f"      {status_icon} {check.name}: {check.message}")

        # 显示健康告警
        health_alerts = global_alert_manager.get_active_alerts()
        if health_alerts:
            print(f"  🚨 健康告警: {len(health_alerts)} 个活跃")
            for alert in health_alerts:
                print(
                    f"    - [{alert.severity.value}] {alert.rule_name}: {alert.message}"
                )

        print()

    @error_handler(ErrorCategory.UNKNOWN, "演示错误处理")
    async def simulate_error_handling(self):
        """模拟错误处理"""
        print("🛠️ 模拟错误处理...")

        # 模拟不同类型的错误
        try:
            # 模拟网络错误
            raise ConnectionError("网络连接失败")
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.HIGH
            )

        try:
            # 模拟配置错误
            raise ValueError("配置参数无效")
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.CONFIGURATION, ErrorSeverity.MEDIUM
            )

        try:
            # 模拟AI模型错误
            raise RuntimeError("AI模型推理失败")
        except Exception as e:
            self.error_handler.handle_error(
                e, ErrorCategory.MODEL_LOADING, ErrorSeverity.HIGH
            )

        # 显示错误统计
        error_stats = self.error_handler.get_error_stats()
        print("  📊 错误统计:")
        print(f"    总错误数: {error_stats['total_errors']}")
        print(f"    错误类别: {len(error_stats['error_by_category'])}")
        print(f"    最近错误: {error_stats['recent_errors']}")

        # 显示最近错误
        recent_errors = self.error_handler.get_recent_errors(limit=3)
        if recent_errors:
            print("  🔍 最近错误:")
            for error in recent_errors:
                print(
                    f"    - [{error.severity.value}] {error.category.value}: {error.message}"
                )

        print()

    async def demonstrate_performance_monitoring(self):
        """演示性能监控"""
        print("📊 演示性能监控...")

        # 记录各种性能指标
        metrics_data = {
            "request_count": (1000, MetricType.COUNTER),
            "active_connections": (50, MetricType.GAUGE),
            "queue_size": (25, MetricType.GAUGE),
            "processing_time": (150, MetricType.TIMER),
            "success_rate": (98.5, MetricType.GAUGE),
            "throughput": (500, MetricType.GAUGE),
        }

        for metric_name, (value, metric_type) in metrics_data.items():
            # 添加一些随机变化
            actual_value = value + random.uniform(-value * 0.1, value * 0.1)
            record_performance_metric(
                metric_name, actual_value, metric_type=metric_type
            )

            # 记录到性能收集器
            if metric_type == MetricType.COUNTER:
                self.performance_collector.record_counter(metric_name, actual_value)
            elif metric_type == MetricType.GAUGE:
                self.performance_collector.record_gauge(metric_name, actual_value)
            elif metric_type == MetricType.TIMER:
                self.performance_collector.record_timer(metric_name, actual_value)

        # 显示性能统计
        print("  📈 性能指标已记录:")
        for metric_name in metrics_data.keys():
            stats = global_performance_threshold_manager.get_metric_statistics(
                metric_name
            )
            if "error" not in stats:
                print(
                    f"    - {metric_name}: 当前={stats['latest']:.2f}, 均值={stats['mean']:.2f}"
                )

        print()

    async def show_comprehensive_status(self):
        """显示综合状态"""
        print("📋 系统综合状态报告")
        print("=" * 50)

        # 运行时间
        uptime = time.time() - self.demo_start_time
        print(f"运行时间: {uptime:.1f} 秒")

        # 健康状态
        health = await global_health_manager.check_health()
        print(f"健康状态: {health.overall_status.value}")
        print(f"健康检查项: {len(health.checks)} 个")

        healthy_count = sum(1 for c in health.checks if c.status.value == "healthy")
        print(f"健康率: {healthy_count/len(health.checks)*100:.1f}%")

        # 告警状态
        health_alert_summary = global_alert_manager.get_alert_summary()
        perf_alert_summary = get_performance_alert_summary()

        total_active_alerts = (
            health_alert_summary["active_alerts"] + perf_alert_summary["active_alerts"]
        )
        print(f"活跃告警: {total_active_alerts} 个")
        print(f"  - 健康告警: {health_alert_summary['active_alerts']}")
        print(f"  - 性能告警: {perf_alert_summary['active_alerts']}")

        # 错误统计
        error_stats = self.error_handler.get_error_stats()
        print(f"错误处理: {error_stats['total_errors']} 个错误已处理")

        # 性能概览
        print(
            f"性能监控: {len(global_performance_threshold_manager.threshold_rules)} 个规则活跃"
        )

        print("=" * 50)
        print()

    async def cleanup_demo_data(self):
        """清理演示数据"""
        print("🧹 清理演示数据...")

        # 清理告警
        global_alert_manager.active_alerts.clear()
        global_performance_threshold_manager.active_alerts.clear()

        # 清理错误历史
        self.error_handler.error_history.clear()

        print("  ✅ 演示数据已清理")
        print()


async def main():
    """主演示函数"""
    print("🎭 无障碍服务综合功能演示")
    print("=" * 60)
    print()

    demo = ComprehensiveDemo()

    try:
        # 初始化系统
        await demo.initialize_systems()

        # 演示正常运行
        await demo.simulate_normal_operations()

        # 演示性能监控
        await demo.demonstrate_performance_monitoring()

        # 演示性能问题
        await demo.simulate_performance_issues()

        # 演示系统故障
        await demo.simulate_system_failures()

        # 演示错误处理
        await demo.simulate_error_handling()

        # 显示综合状态
        await demo.show_comprehensive_status()

        print("🎉 综合演示完成！")
        print()
        print("📊 演示总结:")
        print("  ✅ 健康检查系统 - 多维度监控")
        print("  ✅ 高级告警系统 - 智能告警引擎")
        print("  ✅ 性能监控系统 - 实时性能追踪")
        print("  ✅ 错误处理系统 - 统一错误管理")
        print("  ✅ 集成监控平台 - 全方位系统监控")
        print()
        print("🚀 系统已准备好为'索克生活'提供企业级无障碍服务！")

        # 清理演示数据
        await demo.cleanup_demo_data()

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")

        logger.error("An error occurred", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
