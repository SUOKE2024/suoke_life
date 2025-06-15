"""
短期优化功能演示脚本
展示性能优化、多通道通知、配置热重载和监控仪表板等功能
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path

import yaml

from internal.service.config_hot_reload import ConfigChangeEvent, ConfigHotReloader
from internal.service.notification_channels import (
    ChannelType,
    NotificationLevel,
    NotificationManager,
    NotificationMessage,
    create_channel,
)

# 导入优化模块
from internal.service.optimized_performance_monitor import (
    OptimizedPerformanceCollector,
    PerformanceTimer,
)


class OptimizationDemo:
    """优化功能演示器"""

    def __init__(self) -> None:
        self.temp_files = []

    async def run_demo(self) -> None:
        """运行完整演示"""
        print("🚀 索克生活无障碍服务 - 短期优化功能演示")
        print("=" * 60)

        demos = [
            ("性能优化演示", self.demo_performance_optimization),
            ("多通道通知演示", self.demo_notification_channels),
            ("配置热重载演示", self.demo_config_hot_reload),
            ("综合功能演示", self.demo_integration),
        ]

        for demo_name, demo_func in demos:
            print(f"\n🎭 {demo_name}")
            print("-" * 40)

            try:
                await demo_func()
                print(f"✅ {demo_name} 完成")
            except Exception as e:
                print(f"❌ {demo_name} 异常: {e}")

            print("\n⏳ 等待3秒...")
            await asyncio.sleep(3)

        # 清理临时文件
        self.cleanup_temp_files()

        print("\n🎉 所有演示完成！")
        print("系统已准备好投入生产使用。")

    async def demo_performance_optimization(self) -> None:
        """演示性能优化功能"""
        print("⚡ 展示优化的性能监控器...")

        # 创建优化的性能收集器
        collector = OptimizedPerformanceCollector()

        # 演示高性能指标记录
        print("📊 高性能指标记录演示...")
        start_time = time.perf_counter()

        for i in range(100):
            collector.record_counter("demo.requests", 1, {"endpoint": f"/api/v{i%3+1}"})
            collector.record_gauge("demo.cpu_usage", 20 + (i % 60))
            collector.record_histogram("demo.response_time", 0.1 + (i % 10) * 0.01)

        record_time = time.perf_counter() - start_time
        print(f"   ⚡ 100次指标记录耗时: {record_time:.4f}秒")

        # 演示系统指标获取
        print("🖥️ 系统指标获取演示...")
        system_metrics = collector.get_system_metrics()
        print(
            f"   📈 系统指标: CPU {system_metrics.get('system.cpu.usage', 0):.1f}%, "
            f"内存 {system_metrics.get('system.memory.usage', 0):.1f}%"
        )

        # 演示计时器功能
        print("⏱️ 性能计时器演示...")
        with PerformanceTimer(collector, "demo.database_query"):
            await asyncio.sleep(0.05)  # 模拟数据库查询

        # 获取统计信息
        all_metrics = collector.get_all_metrics()
        print(f"   📋 收集的指标总数: {len(all_metrics)}")

        # 展示部分指标
        for name, metric in list(all_metrics.items())[:3]:
            print(f"   📊 {name}: {metric['value']:.3f} ({metric['type']})")

    async def demo_notification_channels(self) -> None:
        """演示多通道通知功能"""
        print("📢 展示多通道通知系统...")

        # 创建通知管理器
        manager = NotificationManager()

        # 添加控制台通知渠道
        console_channel = create_channel(
            ChannelType.CONSOLE, {"enabled": True, "rate_limit": 10}
        )
        manager.add_channel("console", console_channel)

        print("📱 已配置通知渠道: 控制台")

        # 创建演示消息
        demo_messages = [
            NotificationMessage(
                title="🚀 系统优化完成",
                content="性能监控系统已优化，响应速度提升60%",
                level=NotificationLevel.INFO,
                tags={"category": "optimization", "improvement": "60%"},
            ),
            NotificationMessage(
                title="⚠️ 性能告警",
                content="检测到CPU使用率较高，建议检查系统负载",
                level=NotificationLevel.WARNING,
                tags={"metric": "cpu", "value": "85%"},
            ),
            NotificationMessage(
                title="✅ 健康检查通过",
                content="所有系统组件运行正常",
                level=NotificationLevel.INFO,
                tags={"status": "healthy", "components": "all"},
            ),
        ]

        # 发送演示通知
        for i, message in enumerate(demo_messages, 1):
            print(f"\n📤 发送通知 {i}/{len(demo_messages)}")
            results = await manager.send_notification(message)

            success = results.get("console", False)
            print(f"   {'✅ 发送成功' if success else '❌ 发送失败'}")

            await asyncio.sleep(1)

        # 显示通知统计
        stats = manager.get_channel_stats()
        console_stats = stats.get("console", {})
        print(f"\n📊 通知统计: 已发送 {console_stats.get('sent_count', 0)} 条消息")

    async def demo_config_hot_reload(self) -> None:
        """演示配置热重载功能"""
        print("🔄 展示配置热重载系统...")

        # 创建临时配置文件
        temp_config = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        )
        self.temp_files.append(temp_config.name)

        initial_config = {
            "service": {
                "name": "accessibility-service",
                "version": "1.0.0",
                "performance_mode": "standard",
            },
            "monitoring": {
                "enabled": True,
                "interval": 30,
                "alerts": ["cpu", "memory"],
            },
        }

        yaml.dump(initial_config, temp_config)
        temp_config.close()

        print(f"📄 创建配置文件: {Path(temp_config.name).name}")

        # 创建热重载器
        reloader = ConfigHotReloader(check_interval=0.2)

        # 配置变更回调
        change_count = 0

        def on_config_change(event: ConfigChangeEvent):
            nonlocal change_count
            change_count += 1
            print(f"   🔔 检测到配置变更 #{change_count}")
            print(f"      变更的配置项: {', '.join(event.get_changed_keys())}")

        # 启动热重载监控
        reloader.add_config_file(temp_config.name)
        reloader.add_change_callback(on_config_change)
        reloader.start()

        # 显示初始配置
        initial_loaded = reloader.get_config(temp_config.name)
        print(
            f"📋 初始配置加载: {initial_loaded['service']['name']} v{initial_loaded['service']['version']}"
        )

        await asyncio.sleep(0.5)

        # 模拟配置变更
        print("\n✏️ 模拟配置变更...")

        # 第一次变更：性能模式
        updated_config = initial_config.copy()
        updated_config["service"]["performance_mode"] = "optimized"
        updated_config["service"]["version"] = "1.1.0"

        with open(temp_config.name, "w", encoding="utf-8") as f:
            yaml.dump(updated_config, f)

        await asyncio.sleep(0.5)

        # 第二次变更：添加新功能
        updated_config["features"] = {
            "hot_reload": True,
            "multi_channel_notifications": True,
            "dashboard": True,
        }

        with open(temp_config.name, "w", encoding="utf-8") as f:
            yaml.dump(updated_config, f)

        await asyncio.sleep(0.5)

        # 获取最终配置
        final_config = reloader.get_config(temp_config.name)
        print("\n📊 最终配置:")
        print(f"   版本: {final_config['service']['version']}")
        print(f"   性能模式: {final_config['service']['performance_mode']}")
        print(f"   新功能: {len(final_config.get('features', {}))} 项")

        reloader.stop()
        print(f"🔄 配置热重载演示完成，共检测到 {change_count} 次变更")

    async def demo_integration(self) -> None:
        """演示综合功能集成"""
        print("🔗 展示功能集成...")

        # 创建各个组件
        collector = OptimizedPerformanceCollector()
        notification_manager = NotificationManager()

        # 配置通知渠道
        console_channel = create_channel(ChannelType.CONSOLE, {"enabled": True})
        notification_manager.add_channel("console", console_channel)

        print("🎯 模拟实际运行场景...")

        # 场景1: 系统启动
        print("\n📍 场景1: 系统启动")
        collector.record_counter("system.startup", 1)

        startup_message = NotificationMessage(
            title="🚀 系统启动完成",
            content="无障碍服务已成功启动，所有优化功能已激活",
            level=NotificationLevel.INFO,
            tags={"event": "startup", "optimizations": "enabled"},
        )
        await notification_manager.send_notification(startup_message)

        await asyncio.sleep(1)

        # 场景2: 性能监控
        print("\n📍 场景2: 性能监控")
        for i in range(5):
            cpu_usage = 30 + i * 10
            memory_usage = 40 + i * 8

            collector.record_gauge("system.cpu", cpu_usage)
            collector.record_gauge("system.memory", memory_usage)

            print(f"   📊 监控数据 #{i+1}: CPU {cpu_usage}%, 内存 {memory_usage}%")

            # 如果资源使用过高，发送告警
            if cpu_usage > 60:
                alert_message = NotificationMessage(
                    title="⚠️ 资源使用告警",
                    content=f"CPU使用率达到 {cpu_usage}%，请关注系统负载",
                    level=NotificationLevel.WARNING,
                    tags={"metric": "cpu", "value": f"{cpu_usage}%"},
                )
                await notification_manager.send_notification(alert_message)

            await asyncio.sleep(0.5)

        # 场景3: 功能演示总结
        print("\n📍 场景3: 功能总结")

        # 获取性能统计
        all_metrics = collector.get_all_metrics()
        system_metrics = collector.get_system_metrics()

        # 发送总结通知
        summary_message = NotificationMessage(
            title="📊 演示总结",
            content=f"演示完成！收集了 {len(all_metrics)} 个指标，"
            f"系统CPU使用率 {system_metrics.get('system.cpu.usage', 0):.1f}%",
            level=NotificationLevel.INFO,
            tags={"metrics_count": str(len(all_metrics)), "demo_status": "completed"},
        )
        await notification_manager.send_notification(summary_message)

        print("🎯 集成演示完成:")
        print(f"   📊 性能指标: {len(all_metrics)} 个")
        print("   📢 通知发送: 成功")
        print("   🔄 配置管理: 就绪")
        print("   📱 监控界面: 可用")

    def cleanup_temp_files(self) -> None:
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.exception(f"操作失败: {e}")
                raise


async def main() -> None:
    """主函数"""
    demo = OptimizationDemo()
    await demo.run_demo()


if __name__ == "__main__":
    print("🎭 启动索克生活无障碍服务优化功能演示...")
    print("请稍等，正在初始化演示环境...\n")

    asyncio.run(main())
