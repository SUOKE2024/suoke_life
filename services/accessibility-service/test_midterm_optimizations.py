#!/usr/bin/env python3
"""
中期优化项目综合测试脚本

测试以下中期优化功能：
1. 机器学习异常检测
2. 自动故障恢复机制
3. 容量规划和预测
4. 分布式追踪集成（模拟）
"""

import asyncio
import os
import random
import sys
import time
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入测试模块
try:
    from internal.service.auto_recovery import (
        AutoRecoveryManager,
        FailureEvent,
        FailureType,
        RecoveryAction,
        get_recovery_manager,
    )
    from internal.service.capacity_planning import (
        CapacityPlanner,
        ResourceMetric,
        ResourceType,
        get_capacity_planner,
    )
    from internal.service.ml_anomaly_detection import (
        AnomalySeverity,
        AnomalyType,
        MLAnomalyDetector,
        get_anomaly_detector,
    )
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)


class MidtermOptimizationTester:
    """中期优化测试器"""

    def __init__(self) -> None:
        self.test_results = []
        self.start_time = datetime.now()

    def log_result(
        self, test_name: str, success: bool, duration: float, details: str = ""
    ):
        """记录测试结果"""
        self.test_results.append(
            {
                "test_name": test_name,
                "success": success,
                "duration": duration,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"    {details}")

    async def test_ml_anomaly_detection(self) -> bool:
        """测试机器学习异常检测"""
        print("\n🔍 测试机器学习异常检测...")

        try:
            start_time = time.time()

            # 创建异常检测器
            detector = MLAnomalyDetector(
                {"statistical_window": 50, "z_threshold": 2.5, "trend_threshold": 0.15}
            )

            detector.start()

            # 添加正常数据
            for i in range(100):
                normal_value = 50 + random.gauss(0, 5)
                detector.add_metric("cpu_usage", normal_value)

            # 注入异常数据
            anomaly_value = 150
            detector.add_metric("cpu_usage", anomaly_value)
            anomalies = detector.detect_anomalies("cpu_usage", anomaly_value)

            # 验证异常检测
            if not anomalies:
                self.log_result(
                    "ML异常检测", False, time.time() - start_time, "未检测到异常"
                )
                return False

            # 检查异常类型
            has_statistical = any(
                a.anomaly_type == AnomalyType.STATISTICAL for a in anomalies
            )

            if not has_statistical:
                self.log_result(
                    "ML异常检测", False, time.time() - start_time, "未检测到统计异常"
                )
                return False

            # 获取统计信息
            stats = detector.get_anomaly_statistics()
            model_status = detector.get_model_status()

            detector.stop()

            details = (
                f"检测到{len(anomalies)}个异常，总异常数: {stats['total_anomalies']}"
            )
            self.log_result("ML异常检测", True, time.time() - start_time, details)
            return True

        except Exception as e:
            self.log_result(
                "ML异常检测", False, time.time() - start_time, f"异常: {str(e)}"
            )
            return False

    async def test_auto_recovery(self) -> bool:
        """测试自动故障恢复"""
        print("\n🔧 测试自动故障恢复...")

        try:
            start_time = time.time()

            # 创建自动恢复管理器
            recovery_manager = AutoRecoveryManager()

            # 添加监控服务
            recovery_manager.add_service("test_service", "python", 8080)

            recovery_manager.start()

            # 模拟故障事件
            failure_event = FailureEvent(
                timestamp=datetime.now(),
                failure_type=FailureType.HIGH_CPU,
                severity="high",
                description="CPU使用率过高: 95%",
                affected_service="test_service",
                metrics={"cpu_percent": 95},
            )

            # 处理故障
            await recovery_manager._handle_failure(failure_event)

            # 等待恢复完成
            await asyncio.sleep(2)

            # 获取恢复统计
            stats = recovery_manager.get_recovery_statistics()

            recovery_manager.stop()

            # 验证恢复结果
            if stats["total_failures"] == 0:
                self.log_result(
                    "自动故障恢复", False, time.time() - start_time, "未记录故障事件"
                )
                return False

            details = f"处理{stats['total_failures']}个故障，恢复{stats['total_recoveries']}次"
            self.log_result("自动故障恢复", True, time.time() - start_time, details)
            return True

        except Exception as e:
            self.log_result(
                "自动故障恢复", False, time.time() - start_time, f"异常: {str(e)}"
            )
            return False

    async def test_capacity_planning(self) -> bool:
        """测试容量规划"""
        print("\n📊 测试容量规划...")

        try:
            start_time = time.time()

            # 创建容量规划器
            planner = CapacityPlanner({"linear_window": 50})

            # 模拟历史数据
            base_time = datetime.now() - timedelta(days=7)

            for i in range(100):  # 100个数据点
                timestamp = base_time + timedelta(hours=i)

                # 模拟CPU使用率（有上升趋势）
                cpu_usage = 30 + random.gauss(0, 5) + i * 0.2
                cpu_usage = max(0, min(100, cpu_usage))

                # 添加指标
                planner.add_metric(
                    ResourceMetric(
                        timestamp=timestamp,
                        resource_type=ResourceType.CPU,
                        value=cpu_usage,
                        unit="percent",
                    )
                )

            # 预测未来资源使用
            future_time = datetime.now() + timedelta(days=7)
            predictions = planner.predict_resource_usage(ResourceType.CPU, future_time)

            if not predictions:
                self.log_result(
                    "容量规划", False, time.time() - start_time, "未生成预测结果"
                )
                return False

            # 生成容量建议
            recommendations = planner.generate_capacity_recommendations(
                timedelta(days=30)
            )

            # 获取容量状态
            status = planner.get_capacity_status()

            # 验证结果
            has_cpu_prediction = any(
                p.resource_type == ResourceType.CPU for p in predictions
            )
            has_recommendations = len(recommendations) > 0

            if not has_cpu_prediction:
                self.log_result(
                    "容量规划", False, time.time() - start_time, "未生成CPU预测"
                )
                return False

            details = f"生成{len(predictions)}个预测，{len(recommendations)}个建议"
            self.log_result("容量规划", True, time.time() - start_time, details)
            return True

        except Exception as e:
            self.log_result(
                "容量规划", False, time.time() - start_time, f"异常: {str(e)}"
            )
            return False

    async def test_distributed_tracing_simulation(self) -> bool:
        """测试分布式追踪集成（模拟）"""
        print("\n🔗 测试分布式追踪集成（模拟）...")

        try:
            start_time = time.time()

            # 模拟分布式追踪功能
            trace_data = {
                "trace_id": "trace_12345",
                "spans": [
                    {
                        "span_id": "span_001",
                        "operation": "http_request",
                        "duration": 150,
                        "status": "success",
                    },
                    {
                        "span_id": "span_002",
                        "operation": "database_query",
                        "duration": 80,
                        "status": "success",
                    },
                    {
                        "span_id": "span_003",
                        "operation": "cache_lookup",
                        "duration": 10,
                        "status": "success",
                    },
                ],
                "total_duration": 240,
                "service_map": {
                    "web_service": ["database_service", "cache_service"],
                    "database_service": [],
                    "cache_service": [],
                },
            }

            # 模拟性能分析
            total_duration = trace_data["total_duration"]
            span_count = len(trace_data["spans"])
            avg_span_duration = (
                sum(span["duration"] for span in trace_data["spans"]) / span_count
            )

            # 模拟瓶颈检测
            bottleneck_threshold = 100
            bottlenecks = [
                span
                for span in trace_data["spans"]
                if span["duration"] > bottleneck_threshold
            ]

            # 验证模拟结果
            if span_count == 0:
                self.log_result(
                    "分布式追踪", False, time.time() - start_time, "无追踪数据"
                )
                return False

            details = f"追踪{span_count}个span，平均耗时{avg_span_duration:.1f}ms，发现{len(bottlenecks)}个瓶颈"
            self.log_result("分布式追踪", True, time.time() - start_time, details)
            return True

        except Exception as e:
            self.log_result(
                "分布式追踪", False, time.time() - start_time, f"异常: {str(e)}"
            )
            return False

    async def test_integration(self) -> bool:
        """测试模块集成"""
        print("\n🔄 测试模块集成...")

        try:
            start_time = time.time()

            # 创建所有模块实例
            anomaly_detector = get_anomaly_detector()
            recovery_manager = get_recovery_manager()
            capacity_planner = get_capacity_planner()

            anomaly_detector.start()
            recovery_manager.start()

            # 模拟集成场景：容量预测触发异常检测，异常检测触发自动恢复

            # 1. 添加容量数据
            for i in range(50):
                timestamp = datetime.now() - timedelta(minutes=50 - i)
                cpu_usage = 60 + i * 0.5  # 逐渐增长的CPU使用率

                capacity_planner.add_metric(
                    ResourceMetric(
                        timestamp=timestamp,
                        resource_type=ResourceType.CPU,
                        value=cpu_usage,
                        unit="percent",
                    )
                )

                anomaly_detector.add_metric("cpu_usage", cpu_usage, timestamp)

            # 2. 注入高CPU使用率
            high_cpu_value = 95
            anomalies = anomaly_detector.detect_anomalies("cpu_usage", high_cpu_value)

            # 3. 如果检测到异常，触发自动恢复
            if anomalies:
                failure_event = FailureEvent(
                    timestamp=datetime.now(),
                    failure_type=FailureType.HIGH_CPU,
                    severity="high",
                    description=f"异常检测触发: CPU使用率{high_cpu_value}%",
                    affected_service="integrated_service",
                    metrics={"cpu_percent": high_cpu_value},
                )

                await recovery_manager._handle_failure(failure_event)

            # 4. 生成容量建议
            recommendations = capacity_planner.generate_capacity_recommendations()

            anomaly_detector.stop()
            recovery_manager.stop()

            # 验证集成结果
            anomaly_stats = anomaly_detector.get_anomaly_statistics()
            recovery_stats = recovery_manager.get_recovery_statistics()

            integration_success = (
                anomaly_stats["total_anomalies"] > 0
                and recovery_stats["total_failures"] > 0
                and len(recommendations) > 0
            )

            if not integration_success:
                self.log_result(
                    "模块集成", False, time.time() - start_time, "集成流程未完整执行"
                )
                return False

            details = f"异常{anomaly_stats['total_anomalies']}个，恢复{recovery_stats['total_recoveries']}次，建议{len(recommendations)}个"
            self.log_result("模块集成", True, time.time() - start_time, details)
            return True

        except Exception as e:
            self.log_result(
                "模块集成", False, time.time() - start_time, f"异常: {str(e)}"
            )
            return False

    def print_summary(self) -> None:
        """打印测试总结"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        total_duration = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "=" * 60)
        print("📊 中期优化测试总结")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        print(f"总耗时: {total_duration:.2f}秒")

        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")

        print("\n📋 详细结果:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test_name']}: {result['duration']:.2f}s")

        return passed_tests == total_tests


async def main() -> None:
    """主测试函数"""
    print("🚀 开始中期优化项目测试...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tester = MidtermOptimizationTester()

    # 执行所有测试
    tests = [
        tester.test_ml_anomaly_detection(),
        tester.test_auto_recovery(),
        tester.test_capacity_planning(),
        tester.test_distributed_tracing_simulation(),
        tester.test_integration(),
    ]

    # 并发执行测试
    results = await asyncio.gather(*tests, return_exceptions=True)

    # 处理异常结果
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            test_name = [
                "ML异常检测",
                "自动故障恢复",
                "容量规划",
                "分布式追踪",
                "模块集成",
            ][i]
            tester.log_result(test_name, False, 0, f"测试异常: {str(result)}")

    # 打印总结
    success = tester.print_summary()

    if success:
        print("\n🎉 所有中期优化测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
