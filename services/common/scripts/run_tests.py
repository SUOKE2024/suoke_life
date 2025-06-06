"""
run_tests - 索克生活项目模块
"""

            from services.common.examples.integration_test_example import (
from pathlib import Path
import argparse
import asyncio
import logging
import sys
import time

#!/usr/bin/env python3
"""
索克生活平台通用组件测试运行脚本
提供便捷的测试执行和结果报告
"""


# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    async def run_load_balancer_tests(self):
        """运行负载均衡器测试"""
        logger.info("🔄 运行负载均衡器测试...")
        start_time = time.time()

        try:
                test_load_balancer,
            )

            await test_load_balancer()

            duration = time.time() - start_time
            self.test_results["load_balancer"] = {
                "status": "PASSED",
                "duration": duration,
                "message": "负载均衡器测试通过",
            }
            logger.info(f"✅ 负载均衡器测试通过 ({duration:.2f}s)")

        except Exception as e:
            duration = time.time() - start_time
            self.test_results["load_balancer"] = {
                "status": "FAILED",
                "duration": duration,
                "message": f"负载均衡器测试失败: {e!s}",
            }
            logger.error(f"❌ 负载均衡器测试失败: {e}")

    async def run_health_checker_tests(self):
        """运行健康检查器测试"""
        logger.info("🏥 运行健康检查器测试...")
        start_time = time.time()

        try:
                test_health_checker,
            )

            await test_health_checker()

            duration = time.time() - start_time
            self.test_results["health_checker"] = {
                "status": "PASSED",
                "duration": duration,
                "message": "健康检查器测试通过",
            }
            logger.info(f"✅ 健康检查器测试通过 ({duration:.2f}s)")

        except Exception as e:
            duration = time.time() - start_time
            self.test_results["health_checker"] = {
                "status": "FAILED",
                "duration": duration,
                "message": f"健康检查器测试失败: {e!s}",
            }
            logger.error(f"❌ 健康检查器测试失败: {e}")

    async def run_health_monitor_tests(self):
        """运行健康监控器测试"""
        logger.info("📊 运行健康监控器测试...")
        start_time = time.time()

        try:
                test_health_monitor,
            )

            await test_health_monitor()

            duration = time.time() - start_time
            self.test_results["health_monitor"] = {
                "status": "PASSED",
                "duration": duration,
                "message": "健康监控器测试通过",
            }
            logger.info(f"✅ 健康监控器测试通过 ({duration:.2f}s)")

        except Exception as e:
            duration = time.time() - start_time
            self.test_results["health_monitor"] = {
                "status": "FAILED",
                "duration": duration,
                "message": f"健康监控器测试失败: {e!s}",
            }
            logger.error(f"❌ 健康监控器测试失败: {e}")

    async def run_health_aggregator_tests(self):
        """运行健康聚合器测试"""
        logger.info("🔗 运行健康聚合器测试...")
        start_time = time.time()

        try:
                test_health_aggregator,
            )

            await test_health_aggregator()

            duration = time.time() - start_time
            self.test_results["health_aggregator"] = {
                "status": "PASSED",
                "duration": duration,
                "message": "健康聚合器测试通过",
            }
            logger.info(f"✅ 健康聚合器测试通过 ({duration:.2f}s)")

        except Exception as e:
            duration = time.time() - start_time
            self.test_results["health_aggregator"] = {
                "status": "FAILED",
                "duration": duration,
                "message": f"健康聚合器测试失败: {e!s}",
            }
            logger.error(f"❌ 健康聚合器测试失败: {e}")

    async def run_integration_tests(self):
        """运行集成测试"""
        logger.info("🎭 运行集成测试...")
        start_time = time.time()

        try:
                test_integrated_scenario,
            )

            await test_integrated_scenario()

            duration = time.time() - start_time
            self.test_results["integration"] = {
                "status": "PASSED",
                "duration": duration,
                "message": "集成测试通过",
            }
            logger.info(f"✅ 集成测试通过 ({duration:.2f}s)")

        except Exception as e:
            duration = time.time() - start_time
            self.test_results["integration"] = {
                "status": "FAILED",
                "duration": duration,
                "message": f"集成测试失败: {e!s}",
            }
            logger.error(f"❌ 集成测试失败: {e}")

    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始运行所有测试...")
        self.start_time = time.time()

        # 按顺序运行测试
        await self.run_load_balancer_tests()
        await asyncio.sleep(1)

        await self.run_health_checker_tests()
        await asyncio.sleep(1)

        await self.run_health_monitor_tests()
        await asyncio.sleep(1)

        await self.run_health_aggregator_tests()
        await asyncio.sleep(1)

        await self.run_integration_tests()

        self.end_time = time.time()
        self.print_test_summary()

    def print_test_summary(self):
        """打印测试摘要"""
        total_duration = (
            self.end_time - self.start_time if self.start_time and self.end_time else 0
        )

        print("\n" + "=" * 80)
        print("📋 索克生活平台通用组件测试报告")
        print("=" * 80)

        passed_count = 0
        failed_count = 0

        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(
                f"{status_icon} {test_name:20} | {result['status']:6} | {result['duration']:6.2f}s | {result['message']}"
            )

            if result["status"] == "PASSED":
                passed_count += 1
            else:
                failed_count += 1

        print("-" * 80)
        print("📊 测试统计:")
        print(f"   总计: {len(self.test_results)} 个测试")
        print(f"   通过: {passed_count} 个")
        print(f"   失败: {failed_count} 个")
        print(f"   总耗时: {total_duration:.2f} 秒")

        if failed_count == 0:
            print("\n🎉 所有测试通过！索克生活平台通用组件功能正常")
        else:
            print(f"\n⚠️  有 {failed_count} 个测试失败，请检查相关组件")

        print("=" * 80)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="索克生活平台通用组件测试运行器")
    parser.add_argument(
        "--test",
        choices=[
            "all",
            "load_balancer",
            "health_checker",
            "health_monitor",
            "health_aggregator",
            "integration",
        ],
        default="all",
        help="选择要运行的测试类型",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = TestRunner()

    try:
        if args.test == "all":
            await runner.run_all_tests()
        elif args.test == "load_balancer":
            await runner.run_load_balancer_tests()
            runner.print_test_summary()
        elif args.test == "health_checker":
            await runner.run_health_checker_tests()
            runner.print_test_summary()
        elif args.test == "health_monitor":
            await runner.run_health_monitor_tests()
            runner.print_test_summary()
        elif args.test == "health_aggregator":
            await runner.run_health_aggregator_tests()
            runner.print_test_summary()
        elif args.test == "integration":
            await runner.run_integration_tests()
            runner.print_test_summary()

    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试运行器异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
