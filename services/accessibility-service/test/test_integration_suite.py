#!/usr/bin/env python3
"""
索克生活无障碍服务 - 集成测试套件

提供全面的集成测试，验证各模块间的协作和整体系统功能。
"""

import asyncio
import logging
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pytest

# 设置测试环境
os.environ["TESTING"] = "true"

logger = logging.getLogger(__name__)


class IntegrationTestSuite:
    """集成测试套件"""

    def __init__(self) -> None:
        self.test_results: List[Dict[str, Any]] = []
        self.setup_complete = False
        self.temp_dir = None

    async def setup_test_environment(self) -> None:
        """设置测试环境"""
        logger.info("设置集成测试环境...")

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="suoke_test_")

        # 模拟配置
        self.test_config = {
            "service": {
                "name": "accessibility-service-test",
                "version": "2.0.0-test",
                "debug": True,
            },
            "monitoring": {"enabled": True, "interval": 1},  # 快速测试
            "notifications": {
                "channels": {"console": {"type": "console", "enabled": True}}
            },
            "performance": {"monitoring_enabled": True, "monitoring_interval": 1},
        }

        self.setup_complete = True
        logger.info("测试环境设置完成")

    async def teardown_test_environment(self) -> None:
        """清理测试环境"""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir)

        logger.info("测试环境清理完成")

    def record_test_result(
        self, test_name: str, success: bool, duration: float, details: str = ""
    ):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "duration": duration,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name} ({duration:.2f}s)")
        if not success and details:
            logger.error(f"  详情: {details}")


@pytest.mark.asyncio
class TestServiceIntegration(IntegrationTestSuite):
    """服务集成测试"""

    async def test_service_lifecycle(self) -> None:
        """测试服务生命周期"""
        start_time = time.time()

        try:
            # 导入服务模块
            from internal.service.app import AccessibilityApp

            # 创建服务实例
            app = AccessibilityApp(self.test_config)

            # 测试初始化
            await app.initialize()
            assert app.initialized, "服务初始化失败"

            # 测试健康检查
            health_result = await app.health_check()
            assert health_result["healthy"], "健康检查失败"

            # 测试服务停止
            await app.shutdown()

            duration = time.time() - start_time
            self.record_test_result(
                "service_lifecycle", True, duration, "服务生命周期测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result("service_lifecycle", False, duration, str(e))
            raise

    async def test_monitoring_integration(self) -> None:
        """测试监控集成"""
        start_time = time.time()

        try:
            # 导入监控模块
            from internal.service.performance_optimizer import get_performance_optimizer
            from internal.service.web_dashboard import get_web_dashboard

            # 创建监控组件
            dashboard = get_web_dashboard(self.test_config)
            optimizer = get_performance_optimizer(self.test_config)

            # 测试性能指标收集
            stats = optimizer.get_comprehensive_stats()
            assert "current_metrics" in stats, "性能指标收集失败"
            assert stats["current_metrics"]["cpu_percent"] >= 0, "CPU指标无效"

            # 测试优化功能
            optimization_result = await optimizer.optimize_performance()
            assert "current_metrics" in optimization_result, "性能优化失败"

            duration = time.time() - start_time
            self.record_test_result(
                "monitoring_integration", True, duration, "监控集成测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result("monitoring_integration", False, duration, str(e))
            raise

    async def test_notification_integration(self) -> None:
        """测试通知集成"""
        start_time = time.time()

        try:
            # 导入通知模块
            from internal.service.enhanced_notification_system import (
                NotificationLevel,
                get_notification_manager,
            )

            # 创建通知管理器
            notification_manager = get_notification_manager(self.test_config)

            # 测试发送通知
            result = await notification_manager.send_notification(
                title="集成测试通知",
                content="这是一个集成测试通知消息",
                level=NotificationLevel.INFO,
            )

            assert len(result) > 0, "通知发送失败"
            assert any(result.values()), "所有通知渠道都失败"

            # 测试统计信息
            stats = notification_manager.get_statistics()
            assert stats["total_sent"] > 0, "通知统计异常"

            duration = time.time() - start_time
            self.record_test_result(
                "notification_integration", True, duration, "通知集成测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result("notification_integration", False, duration, str(e))
            raise

    async def test_cache_integration(self) -> None:
        """测试缓存集成"""
        start_time = time.time()

        try:
            from internal.service.performance_optimizer import get_performance_optimizer

            optimizer = get_performance_optimizer(self.test_config)
            cache = optimizer.cache_optimizer

            # 测试缓存操作
            test_key = "test_key"
            test_value = {"data": "test_data", "timestamp": time.time()}

            # 设置缓存
            cache.set(test_key, test_value)

            # 获取缓存
            cached_value = cache.get(test_key)
            assert cached_value == test_value, "缓存值不匹配"

            # 测试缓存统计
            stats = cache.get_stats()
            assert stats["hit_count"] > 0, "缓存命中统计异常"

            # 测试缓存删除
            cache.delete(test_key)
            deleted_value = cache.get(test_key)
            assert deleted_value is None, "缓存删除失败"

            duration = time.time() - start_time
            self.record_test_result(
                "cache_integration", True, duration, "缓存集成测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result("cache_integration", False, duration, str(e))
            raise

    async def test_concurrency_integration(self) -> None:
        """测试并发集成"""
        start_time = time.time()

        try:
            from internal.service.performance_optimizer import get_performance_optimizer

            optimizer = get_performance_optimizer(self.test_config)
            concurrency = optimizer.concurrency_optimizer

            # 测试并发任务提交
            def test_task(x):
                time.sleep(0.1)  # 模拟工作
                return x * 2

            # 提交多个任务
            tasks = []
            for i in range(5):
                task = concurrency.submit_task(test_task, i)
                tasks.append(task)

            # 等待所有任务完成
            results = await asyncio.gather(*tasks)
            expected_results = [i * 2 for i in range(5)]
            assert results == expected_results, "并发任务结果不正确"

            # 测试限流器
            limiter = concurrency.create_rate_limiter("test_limiter", 3, 1)

            # 测试限流
            allowed_count = 0
            for _ in range(5):
                if limiter.is_allowed():
                    allowed_count += 1

            assert allowed_count <= 3, "限流器未生效"

            duration = time.time() - start_time
            self.record_test_result(
                "concurrency_integration", True, duration, "并发集成测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result("concurrency_integration", False, duration, str(e))
            raise

    async def test_error_handling_integration(self) -> None:
        """测试错误处理集成"""
        start_time = time.time()

        try:
            from internal.service.enhanced_notification_system import (
                NotificationLevel,
                get_notification_manager,
            )

            notification_manager = get_notification_manager(self.test_config)

            # 测试错误通知
            await notification_manager.send_notification(
                title="错误处理测试",
                content="模拟系统错误",
                level=NotificationLevel.ERROR,
            )

            # 测试性能告警
            await notification_manager.send_performance_alert(
                metric_name="cpu_usage", current_value=95.0, threshold=80.0
            )

            # 验证通知统计
            stats = notification_manager.get_statistics()
            assert stats["total_sent"] >= 2, "错误通知发送失败"

            duration = time.time() - start_time
            self.record_test_result(
                "error_handling_integration", True, duration, "错误处理集成测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result(
                "error_handling_integration", False, duration, str(e)
            )
            raise


@pytest.mark.asyncio
class TestEndToEndScenarios(IntegrationTestSuite):
    """端到端场景测试"""

    async def test_full_monitoring_scenario(self) -> None:
        """测试完整监控场景"""
        start_time = time.time()

        try:
            # 模拟完整的监控流程
            from internal.service.enhanced_notification_system import (
                get_notification_manager,
            )
            from internal.service.performance_optimizer import get_performance_optimizer
            from internal.service.web_dashboard import get_web_dashboard

            # 初始化所有组件
            dashboard = get_web_dashboard(self.test_config)
            optimizer = get_performance_optimizer(self.test_config)
            notification_manager = get_notification_manager(self.test_config)

            # 设置组件关联
            dashboard.set_performance_monitor(optimizer)
            dashboard.set_alert_manager(notification_manager)

            # 模拟性能数据收集
            for _ in range(3):
                stats = optimizer.get_comprehensive_stats()
                assert "current_metrics" in stats, "性能数据收集失败"
                await asyncio.sleep(0.1)

            # 模拟告警触发
            await notification_manager.send_performance_alert(
                metric_name="memory_usage", current_value=85.0, threshold=80.0
            )

            # 验证整体状态
            health_result = await optimizer.health_check()
            assert "healthy" in health_result, "健康检查失败"

            duration = time.time() - start_time
            self.record_test_result(
                "full_monitoring_scenario", True, duration, "完整监控场景测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result("full_monitoring_scenario", False, duration, str(e))
            raise

    async def test_stress_scenario(self) -> None:
        """测试压力场景"""
        start_time = time.time()

        try:
            from internal.service.performance_optimizer import get_performance_optimizer

            optimizer = get_performance_optimizer(self.test_config)

            # 模拟高负载场景
            def cpu_intensive_task(n):
                # 模拟CPU密集型任务
                result = 0
                for i in range(n * 1000):
                    result += i**2
                return result

            # 提交大量任务
            tasks = []
            for i in range(10):
                task = optimizer.concurrency_optimizer.submit_task(
                    cpu_intensive_task, 100
                )
                tasks.append(task)

            # 等待任务完成
            results = await asyncio.gather(*tasks)
            assert len(results) == 10, "压力测试任务未全部完成"

            # 检查系统状态
            stats = optimizer.get_comprehensive_stats()
            assert stats["concurrency_stats"]["completed_tasks"] >= 10, "任务统计异常"

            # 执行性能优化
            optimization_result = await optimizer.optimize_performance()
            assert "memory_optimization" in optimization_result, "压力测试后优化失败"

            duration = time.time() - start_time
            self.record_test_result(
                "stress_scenario", True, duration, "压力场景测试通过"
            )

        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result("stress_scenario", False, duration, str(e))
            raise


class TestReportGenerator:
    """测试报告生成器"""

    def __init__(self, test_results: List[Dict[str, Any]]):
        self.test_results = test_results

    def generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        total_duration = sum(result["duration"] for result in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_detailed_report(self) -> str:
        """生成详细报告"""
        summary = self.generate_summary()

        report = f"""
# 索克生活无障碍服务集成测试报告

## 测试摘要
- **总测试数**: {summary['total_tests']}
- **通过测试**: {summary['passed_tests']}
- **失败测试**: {summary['failed_tests']}
- **成功率**: {summary['success_rate']:.1f}%
- **总耗时**: {summary['total_duration']:.2f}秒
- **平均耗时**: {summary['average_duration']:.2f}秒
- **测试时间**: {summary['timestamp']}

## 详细结果

"""

        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report += f"### {result['test_name']}\n"
            report += f"- **状态**: {status}\n"
            report += f"- **耗时**: {result['duration']:.2f}秒\n"
            report += f"- **时间**: {result['timestamp']}\n"

            if result["details"]:
                report += f"- **详情**: {result['details']}\n"

            report += "\n"

        return report

    def save_report(self, file_path: str):
        """保存报告到文件"""
        report = self.generate_detailed_report()

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"测试报告已保存: {file_path}")


async def run_integration_tests() -> None:
    """运行集成测试"""
    logger.info("开始运行集成测试套件...")

    # 创建测试套件
    service_tests = TestServiceIntegration()
    e2e_tests = TestEndToEndScenarios()

    all_results = []

    try:
        # 设置测试环境
        await service_tests.setup_test_environment()
        await e2e_tests.setup_test_environment()

        # 运行服务集成测试
        await service_tests.test_service_lifecycle()
        await service_tests.test_monitoring_integration()
        await service_tests.test_notification_integration()
        await service_tests.test_cache_integration()
        await service_tests.test_concurrency_integration()
        await service_tests.test_error_handling_integration()

        # 运行端到端测试
        await e2e_tests.test_full_monitoring_scenario()
        await e2e_tests.test_stress_scenario()

        # 收集所有结果
        all_results.extend(service_tests.test_results)
        all_results.extend(e2e_tests.test_results)

    except Exception as e:
        logger.error(f"集成测试执行失败: {e}")
        raise

    finally:
        # 清理测试环境
        await service_tests.teardown_test_environment()
        await e2e_tests.teardown_test_environment()

    # 生成测试报告
    report_generator = TestReportGenerator(all_results)
    summary = report_generator.generate_summary()

    # 保存报告
    report_file = (
        f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    report_generator.save_report(report_file)

    logger.info(f"集成测试完成: {summary['success_rate']:.1f}% 通过率")
    return summary, all_results


if __name__ == "__main__":
    # 运行集成测试
    asyncio.run(run_integration_tests())
