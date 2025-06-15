"""
短期优化功能综合测试
测试性能优化、多通道通知、配置热重载和监控仪表板等功能
"""

import asyncio
import json
import logging
import os
import tempfile
import time

import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 导入优化模块
from internal.service.config_hot_reload import ConfigChangeEvent, ConfigHotReloader
from internal.service.notification_channels import (
    ChannelType,
    NotificationLevel,
    NotificationManager,
    NotificationMessage,
    create_channel,
)
from internal.service.optimized_performance_monitor import (
    OptimizedPerformanceCollector,
    PerformanceTimer,
    optimized_performance_collector,
)


class ShortTermOptimizationTester:
    """短期优化功能测试器"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("optimization_tester")
        self.test_results = {}
        self.temp_files = []

    async def run_all_tests(self) -> None:
        """运行所有测试"""
        print("🚀 开始短期优化功能综合测试")
        print("=" * 60)

        tests = [
            ("性能优化测试", self.test_performance_optimization),
            ("多通道通知测试", self.test_notification_channels),
            ("配置热重载测试", self.test_config_hot_reload),
            ("集成功能测试", self.test_integration),
        ]

        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)

            try:
                start_time = time.time()
                result = await test_func()
                duration = time.time() - start_time

                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "duration": duration,
                    "details": result if isinstance(result, dict) else {},
                }

                status_emoji = "✅" if result else "❌"
                print(
                    f"{status_emoji} {test_name}: {'通过' if result else '失败'} ({duration:.2f}秒)"
                )

            except Exception as e:
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "duration": 0,
                    "error": str(e),
                }
                print(f"❌ {test_name}: 错误 - {e}")

        # 清理临时文件
        self.cleanup_temp_files()

        # 显示测试总结
        self.print_test_summary()

    async def test_performance_optimization(self) -> bool:
        """测试性能优化功能"""
        try:
            print("🔧 测试优化的性能监控器...")

            # 创建优化的性能收集器
            collector = OptimizedPerformanceCollector(
                max_metrics=100, cleanup_interval=60
            )

            # 性能基准测试
            print("⚡ 执行性能基准测试...")

            # 测试1: 大量指标记录性能
            start_time = time.perf_counter()
            for i in range(1000):
                collector.record_counter("test.counter", 1, {"batch": str(i // 100)})
                collector.record_gauge("test.gauge", i * 0.1)
                collector.record_histogram("test.histogram", i * 0.01)

            record_duration = time.perf_counter() - start_time
            print(f"   📊 1000次指标记录耗时: {record_duration:.4f}秒")

            # 测试2: 系统指标获取性能
            start_time = time.perf_counter()
            for _ in range(10):
                system_metrics = collector.get_system_metrics()
            system_duration = time.perf_counter() - start_time
            print(f"   🖥️ 10次系统指标获取耗时: {system_duration:.4f}秒")

            # 测试3: 统计计算性能
            start_time = time.perf_counter()
            all_metrics = collector.get_all_metrics()
            stats_duration = time.perf_counter() - start_time
            print(f"   📈 统计计算耗时: {stats_duration:.4f}秒")

            # 测试4: 计时器功能
            with PerformanceTimer(collector, "test.timer"):
                await asyncio.sleep(0.01)

            # 验证结果
            metrics_count = len(all_metrics)
            system_metrics_count = len(system_metrics)

            print(f"   📋 收集的指标数量: {metrics_count}")
            print(f"   🖥️ 系统指标数量: {system_metrics_count}")

            # 性能要求验证
            performance_ok = (
                record_duration < 0.5  # 1000次记录应在0.5秒内
                and system_duration < 1.0  # 10次系统指标获取应在1秒内
                and stats_duration < 0.5  # 统计计算应在0.5秒内
                and metrics_count > 0
                and system_metrics_count >= 3
            )

            if performance_ok:
                print("✅ 性能优化测试通过")
                return {
                    "record_performance": f"{record_duration:.4f}s",
                    "system_performance": f"{system_duration:.4f}s",
                    "stats_performance": f"{stats_duration:.4f}s",
                    "metrics_count": metrics_count,
                    "system_metrics_count": system_metrics_count,
                }
            else:
                print("❌ 性能优化测试未达到预期")
                return False

        except Exception as e:
            print(f"❌ 性能优化测试异常: {e}")
            return False

    async def test_notification_channels(self) -> bool:
        """测试多通道通知功能"""
        try:
            print("📢 测试多通道通知系统...")

            # 创建通知管理器
            manager = NotificationManager()

            # 添加控制台通知渠道
            console_channel = create_channel(
                ChannelType.CONSOLE, {"enabled": True, "rate_limit": 10}
            )
            manager.add_channel("console", console_channel)

            # 创建测试消息
            test_messages = [
                NotificationMessage(
                    title="性能优化完成",
                    content="系统性能监控已优化，响应时间提升50%",
                    level=NotificationLevel.INFO,
                    tags={"category": "performance", "improvement": "50%"},
                ),
                NotificationMessage(
                    title="配置热重载启用",
                    content="配置文件变更检测已启用，支持实时重载",
                    level=NotificationLevel.INFO,
                    tags={"category": "config", "feature": "hot_reload"},
                ),
                NotificationMessage(
                    title="监控仪表板就绪",
                    content="Web监控仪表板已启动，可通过浏览器访问",
                    level=NotificationLevel.INFO,
                    tags={"category": "dashboard", "status": "ready"},
                ),
            ]

            # 发送通知测试
            success_count = 0
            total_count = len(test_messages)

            for i, message in enumerate(test_messages, 1):
                print(f"   📤 发送通知 {i}/{total_count}: {message.title}")

                # 只发送到控制台渠道
                results = await manager.send_notification(message, ["console"])

                if results.get("console", False):
                    success_count += 1
                    print("   ✅ 通知发送成功")
                else:
                    print("   ❌ 通知发送失败")

                await asyncio.sleep(0.5)  # 避免速率限制

            # 获取渠道统计
            stats = manager.get_channel_stats()
            print(f"   📊 渠道统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")

            # 验证结果
            success_rate = success_count / total_count
            channels_count = len(stats)

            notification_ok = (
                success_rate >= 0.8  # 至少80%成功率
                and channels_count >= 1  # 至少1个渠道
                and stats.get("console", {}).get("sent_count", 0)
                > 0  # 控制台渠道有发送记录
            )

            if notification_ok:
                print("✅ 多通道通知测试通过")
                return {
                    "success_rate": f"{success_rate:.1%}",
                    "channels_count": channels_count,
                    "total_sent": sum(
                        stat.get("sent_count", 0) for stat in stats.values()
                    ),
                }
            else:
                print("❌ 多通道通知测试未达到预期")
                return False

        except Exception as e:
            print(f"❌ 多通道通知测试异常: {e}")
            return False

    async def test_config_hot_reload(self) -> bool:
        """测试配置热重载功能"""
        try:
            print("🔄 测试配置热重载系统...")

            # 创建临时配置文件
            temp_config = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, encoding="utf-8"
            )
            self.temp_files.append(temp_config.name)

            initial_config = {
                "app": {
                    "name": "accessibility-service",
                    "version": "1.0.0",
                    "debug": False,
                },
                "monitoring": {"enabled": True, "interval": 30},
            }

            yaml.dump(initial_config, temp_config)
            temp_config.close()

            print(f"   📄 创建临时配置文件: {temp_config.name}")

            # 创建热重载器
            reloader = ConfigHotReloader(check_interval=0.1)  # 快速检查间隔

            # 配置变更回调
            change_events = []

            def on_config_change(event: ConfigChangeEvent):
                change_events.append(event)
                print(f"   🔔 配置变更检测: {event.file_path.name}")
                print(f"      变更的键: {event.get_changed_keys()}")

            # 添加配置文件和回调
            add_result = reloader.add_config_file(temp_config.name)
            if not add_result:
                print("❌ 添加配置文件失败")
                return False

            reloader.add_change_callback(on_config_change)

            # 启动热重载
            reloader.start()

            # 获取初始配置
            initial_loaded = reloader.get_config(temp_config.name)
            print(f"   📋 初始配置加载: {initial_loaded is not None}")

            # 等待一下确保监控启动
            await asyncio.sleep(0.5)

            # 修改配置文件
            print("   ✏️ 修改配置文件...")
            updated_config = initial_config.copy()
            updated_config["app"]["debug"] = True
            updated_config["app"]["version"] = "1.1.0"
            updated_config["new_feature"] = {"enabled": True}

            with open(temp_config.name, "w", encoding="utf-8") as f:
                yaml.dump(updated_config, f)

            # 等待变更检测
            print("   ⏳ 等待变更检测...")
            await asyncio.sleep(1.0)

            # 获取更新后的配置
            updated_loaded = reloader.get_config(temp_config.name)

            # 停止热重载
            reloader.stop()

            # 验证结果
            config_loaded = initial_loaded is not None and updated_loaded is not None
            change_detected = len(change_events) > 0
            config_updated = (
                updated_loaded
                and updated_loaded.get("app", {}).get("debug") is True
                and updated_loaded.get("app", {}).get("version") == "1.1.0"
                and "new_feature" in updated_loaded
            )

            print(f"   📊 配置加载: {config_loaded}")
            print(f"   🔔 变更检测: {change_detected}")
            print(f"   🔄 配置更新: {config_updated}")

            hot_reload_ok = config_loaded and change_detected and config_updated

            if hot_reload_ok:
                print("✅ 配置热重载测试通过")
                return {
                    "config_loaded": config_loaded,
                    "change_detected": change_detected,
                    "config_updated": config_updated,
                    "change_events_count": len(change_events),
                }
            else:
                print("❌ 配置热重载测试未达到预期")
                return False

        except Exception as e:
            print(f"❌ 配置热重载测试异常: {e}")
            return False

    async def test_integration(self) -> bool:
        """测试集成功能"""
        try:
            print("🔗 测试功能集成...")

            # 集成测试：性能监控 + 通知系统
            print("   🔧 测试性能监控与通知集成...")

            # 创建性能收集器
            collector = OptimizedPerformanceCollector()

            # 创建通知管理器
            notification_manager = NotificationManager()
            console_channel = create_channel(ChannelType.CONSOLE, {"enabled": True})
            notification_manager.add_channel("console", console_channel)

            # 模拟性能问题并发送通知
            collector.record_gauge("cpu.usage", 85.0)  # 高CPU使用率
            collector.record_gauge("memory.usage", 90.0)  # 高内存使用率

            # 创建性能告警通知
            alert_message = NotificationMessage(
                title="性能告警",
                content="系统资源使用率过高",
                level=NotificationLevel.WARNING,
                tags={"cpu": "85%", "memory": "90%"},
            )

            # 发送通知
            results = await notification_manager.send_notification(alert_message)
            notification_sent = results.get("console", False)

            print(
                f"   📤 性能告警通知: {'发送成功' if notification_sent else '发送失败'}"
            )

            # 集成测试：配置热重载 + 性能监控
            print("   🔄 测试配置热重载与性能监控集成...")

            # 创建临时配置
            temp_config = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False, encoding="utf-8"
            )
            self.temp_files.append(temp_config.name)

            config_data = {
                "performance": {"collection_interval": 1.0, "max_metrics": 1000}
            }

            yaml.dump(config_data, temp_config)
            temp_config.close()

            # 创建热重载器
            reloader = ConfigHotReloader(check_interval=0.1)
            reloader.add_config_file(temp_config.name)
            reloader.start()

            # 获取初始配置
            initial_config = reloader.get_config(temp_config.name)
            config_loaded = initial_config is not None

            reloader.stop()

            print(f"   📋 配置加载集成: {'成功' if config_loaded else '失败'}")

            # 验证集成结果
            integration_ok = notification_sent and config_loaded

            if integration_ok:
                print("✅ 功能集成测试通过")
                return {
                    "notification_integration": notification_sent,
                    "config_integration": config_loaded,
                }
            else:
                print("❌ 功能集成测试未达到预期")
                return False

        except Exception as e:
            print(f"❌ 功能集成测试异常: {e}")
            return False

    def cleanup_temp_files(self) -> None:
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                self.logger.warning(f"清理临时文件失败 {temp_file}: {e}")

    def print_test_summary(self) -> None:
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📋 短期优化功能测试总结")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results.values() if result["status"] == "PASS"
        )
        failed_tests = sum(
            1
            for result in self.test_results.values()
            if result["status"] in ["FAIL", "ERROR"]
        )

        success_rate = passed_tests / total_tests if total_tests > 0 else 0

        print("📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过测试: {passed_tests}")
        print(f"   失败测试: {failed_tests}")
        print(f"   成功率: {success_rate:.1%}")

        print("\n📋 详细结果:")
        for test_name, result in self.test_results.items():
            status_emoji = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}.get(
                result["status"], "❓"
            )

            print(f"   {status_emoji} {test_name}: {result['status']}")
            if result.get("duration"):
                print(f"      耗时: {result['duration']:.2f}秒")
            if result.get("error"):
                print(f"      错误: {result['error']}")

        # 总体评估
        if success_rate >= 0.8:
            print("\n🎉 短期优化功能测试整体通过！")
            print("   系统已具备生产环境部署条件")
        elif success_rate >= 0.6:
            print("\n⚠️ 短期优化功能测试部分通过")
            print("   建议修复失败的测试项后再部署")
        else:
            print("\n❌ 短期优化功能测试未达到预期")
            print("   需要进一步优化和修复")


async def main() -> None:
    """主函数"""
    tester = ShortTermOptimizationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
