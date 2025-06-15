"""
monitor - 索克生活项目模块
"""

from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from typing import Dict, Any, List
import argparse
import asyncio
import httpx
import json

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
API 网关监控脚本

实时监控 API 网关的运行状态，包括健康检查、性能指标、资源使用等。
"""



class GatewayMonitor:
    """API 网关监控器"""

    def __init__(
        self,
        gateway_url: str = "http: / /localhost:8000",
        refresh_interval: int = 5,
        alert_thresholds: Dict[str, float] = None,
    ):
        self.gateway_url = gateway_url.rstrip(' / ')
        self.refresh_interval = refresh_interval
        self.alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'response_time_p99': 1.0,
            'error_rate': 5.0,
        }

        self.console = Console()
        self.client = httpx.AsyncClient(timeout = 10.0)

        # 历史数据
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history = 100

        # 告警状态
        self.alerts: List[Dict[str, Any]] = []
        self.max_alerts = 50

    async def get_health_status(self) - > Dict[str, Any]:
        """获取健康状态"""
        try:
            response = await self.client.get(f"{self.gateway_url} / metrics / health - check")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_metrics(self) - > Dict[str, Any]:
        """获取指标数据"""
        try:
            response = await self.client.get(f"{self.gateway_url} / metrics / stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def get_system_info(self) - > Dict[str, Any]:
        """获取系统信息"""
        try:
            response = await self.client.get(f"{self.gateway_url} / metrics / system - info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def check_alerts(self, metrics: Dict[str, Any], system_info: Dict[str, Any]) - > List[Dict[str, Any]]:
        """检查告警条件"""
        alerts = []
        timestamp = datetime.now()

        # CPU 使用率告警
        cpu_percent = system_info.get("resources", {}).get("cpu_percent", 0)
        if cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                "type": "cpu_high",
                "level": "warning",
                "message": f"CPU usage is high: {cpu_percent:.1f}%",
                "timestamp": timestamp,
                "value": cpu_percent,
                "threshold": self.alert_thresholds['cpu_percent'],
            })

        # 内存使用率告警
        memory_percent = system_info.get("resources", {}).get("memory", {}).get("percent", 0)
        if memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                "type": "memory_high",
                "level": "warning",
                "message": f"Memory usage is high: {memory_percent:.1f}%",
                "timestamp": timestamp,
                "value": memory_percent,
                "threshold": self.alert_thresholds['memory_percent'],
            })

        # 缓存命中率告警
        cache_hit_ratio = metrics.get("cache", {}).get("hit_ratio", 1.0)
        if cache_hit_ratio < 0.5:  # 命中率低于 50%
            alerts.append({
                "type": "cache_low_hit_ratio",
                "level": "info",
                "message": f"Cache hit ratio is low: {cache_hit_ratio:.1%}",
                "timestamp": timestamp,
                "value": cache_hit_ratio,
                "threshold": 0.5,
            })

        return alerts

    def create_dashboard_layout(self) - > Layout:
        """创建仪表板布局"""
        layout = Layout()

        layout.split_column(
            Layout(name = "header", size = 3),
            Layout(name = "main"),
            Layout(name = "footer", size = 3),
        )

        layout["main"].split_row(
            Layout(name = "left"),
            Layout(name = "right"),
        )

        layout["left"].split_column(
            Layout(name = "health", size = 8),
            Layout(name = "metrics", size = 12),
        )

        layout["right"].split_column(
            Layout(name = "system", size = 10),
            Layout(name = "alerts", size = 10),
        )

        return layout

    def create_header_panel(self) - > Panel:
        """创建头部面板"""
        title = Text("索克生活 API 网关监控", style = "bold blue")
        subtitle = Text(f"监控地址: {self.gateway_url} | 刷新间隔: {self.refresh_interval}s", style = "dim")

        return Panel(
            f"{title}\n{subtitle}",
            title = "🚀 Gateway Monitor",
            border_style = "blue",
        )

    def create_health_panel(self, health_data: Dict[str, Any]) - > Panel:
        """创建健康状态面板"""
        if "error" in health_data:
            content = f"❌ 连接失败: {health_data['error']}"
            style = "red"
        else:
            status = health_data.get("status", "unknown")
            if status == "healthy":
                content = "✅ 服务健康"
                style = "green"
            else:
                content = f"⚠️  服务状态: {status}"
                style = "yellow"

            # 添加检查详情
            checks = health_data.get("checks", {})
            if checks:
                content + = "\n\n检查项目:"
                for name, check in checks.items():
                    status_icon = "✅" if check["status"] == "healthy" else "❌"
                    content + = f"\n{status_icon} {name}: {check['message']}"

        return Panel(
            content,
            title = "🏥 健康状态",
            border_style = style,
        )

    def create_metrics_panel(self, metrics: Dict[str, Any]) - > Panel:
        """创建指标面板"""
        if "error" in metrics:
            content = f"❌ 获取指标失败: {metrics['error']}"
        else:
            uptime = metrics.get("uptime_seconds", 0)
            uptime_str = str(timedelta(seconds = int(uptime)))

            cache_stats = metrics.get("cache", {})
            hit_ratio = cache_stats.get("hit_ratio", 0)

            requests = metrics.get("requests", {})
            total_requests = requests.get("total", 0)

            connections = metrics.get("connections", {})
            active_connections = connections.get("active", 0)

            content = f"""运行时间: {uptime_str}
总请求数: {total_requests:,}
活跃连接: {active_connections}
缓存命中率: {hit_ratio:.1%}
缓存命中: {cache_stats.get('hits', 0):,}
缓存未命中: {cache_stats.get('misses', 0):,}"""

        return Panel(
            content,
            title = "📊 运行指标",
            border_style = "cyan",
        )

    def create_system_panel(self, system_info: Dict[str, Any]) - > Panel:
        """创建系统信息面板"""
        if "error" in system_info:
            content = f"❌ 获取系统信息失败: {system_info['error']}"
        else:
            resources = system_info.get("resources", {})
            system_resources = system_info.get("system_resources", {})

            # 进程资源
            cpu_percent = resources.get("cpu_percent", 0)
            memory = resources.get("memory", {})
            memory_percent = memory.get("percent", 0)
            memory_rss = memory.get("rss", 0) / 1024 / 1024  # MB

            # 系统资源
            sys_cpu = system_resources.get("cpu_percent", 0)
            sys_memory = system_resources.get("memory", {})
            sys_memory_percent = sys_memory.get("percent", 0)
            sys_memory_total = sys_memory.get("total", 0) / 1024 / 1024 / 1024  # GB

            content = f"""进程资源:
CPU: {cpu_percent:.1f}%
内存: {memory_rss:.1f} MB ({memory_percent:.1f}%)
线程: {resources.get('threads', 0)}
文件: {resources.get('open_files', 0)}

系统资源:
CPU: {sys_cpu:.1f}%
内存: {sys_memory_percent:.1f}% / {sys_memory_total:.1f} GB
CPU 核心: {system_resources.get('cpu_count', 0)}"""

        return Panel(
            content,
            title = "💻 系统资源",
            border_style = "magenta",
        )

    def create_alerts_panel(self) - > Panel:
        """创建告警面板"""
        if not self.alerts:
            content = "✅ 无告警"
            style = "green"
        else:
            content = ""
            recent_alerts = self.alerts[ - 10:]  # 显示最近 10 条告警

            for alert in recent_alerts:
                level_icon = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "critical": "🚨",
                }.get(alert["level"], "❓")

                timestamp = alert["timestamp"].strftime("%H:%M:%S")
                content + = f"{level_icon} [{timestamp}] {alert['message']}\n"

            style = "red" if any(a["level"] in ["error", "critical"] for a in recent_alerts) else "yellow"

        return Panel(
            content.rstrip(),
            title = f"🚨 告警 ({len(self.alerts)})",
            border_style = style,
        )

    def create_footer_panel(self) - > Panel:
        """创建底部面板"""
        current_time = datetime.now().strftime("%Y - %m - %d %H:%M:%S")
        content = f"最后更新: {current_time} | 按 Ctrl + C 退出"

        return Panel(
            content,
            border_style = "dim",
        )

    async def collect_data(self) - > Dict[str, Any]:
        """收集监控数据"""
        health_data = await self.get_health_status()
        metrics_data = await self.get_metrics()
        system_data = await self.get_system_info()

        # 检查告警
        new_alerts = self.check_alerts(metrics_data, system_data)
        self.alerts.extend(new_alerts)

        # 限制告警历史长度
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[ - self.max_alerts:]

        # 保存历史数据
        metrics_snapshot = {
            "timestamp": datetime.now(),
            "health": health_data,
            "metrics": metrics_data,
            "system": system_data,
            "alerts_count": len(new_alerts),
        }

        self.metrics_history.append(metrics_snapshot)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[ - self.max_history:]

        return {
            "health": health_data,
            "metrics": metrics_data,
            "system": system_data,
            "new_alerts": new_alerts,
        }

    def update_dashboard(self, layout: Layout, data: Dict[str, Any]) - > None:
        """更新仪表板"""
        layout["header"].update(self.create_header_panel())
        layout["health"].update(self.create_health_panel(data["health"]))
        layout["metrics"].update(self.create_metrics_panel(data["metrics"]))
        layout["system"].update(self.create_system_panel(data["system"]))
        layout["alerts"].update(self.create_alerts_panel())
        layout["footer"].update(self.create_footer_panel())

    async def run_dashboard(self) - > None:
        """运行仪表板"""
        layout = self.create_dashboard_layout()

        with Live(layout, refresh_per_second = 1, screen = True) as live:
            try:
                while True:
                    data = await self.collect_data()
                    self.update_dashboard(layout, data)
                    await asyncio.sleep(self.refresh_interval)

            except KeyboardInterrupt:
                self.console.print("\n👋 监控已停止")
            finally:
                await self.client.aclose()

    async def run_simple(self) - > None:
        """运行简单模式（非交互式）"""
        try:
            while True:
                data = await self.collect_data()

                # 打印简单状态
                timestamp = datetime.now().strftime("%Y - %m - %d %H:%M:%S")
                health_status = data["health"].get("status", "error")

                if health_status == "healthy":
                    status_icon = "✅"
                elif health_status == "error":
                    status_icon = "❌"
                else:
                    status_icon = "⚠️"

                metrics = data["metrics"]
                uptime = metrics.get("uptime_seconds", 0)
                total_requests = metrics.get("requests", {}).get("total", 0)

                print(f"[{timestamp}] {status_icon} {health_status} | "
                    f"运行时间: {uptime:.0f}s | 总请求: {total_requests}")

                # 打印新告警
                for alert in data["new_alerts"]:
                    level_icon = {
                        "info": "ℹ️",
                        "warning": "⚠️",
                        "error": "❌",
                        "critical": "🚨",
                    }.get(alert["level"], "❓")
                    print(f"  {level_icon} {alert['message']}")

                await asyncio.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print("\n👋 监控已停止")
        finally:
            await self.client.aclose()

    def export_metrics(self, output_file: str) - > None:
        """导出指标数据"""
        output_path = Path(output_file)

        export_data = {
            "export_time": datetime.now().isoformat(),
            "gateway_url": self.gateway_url,
            "metrics_history": [
                {
                    * *item,
                    "timestamp": item["timestamp"].isoformat(),
                }
                for item in self.metrics_history
            ],
            "alerts": [
                {
                    * *alert,
                    "timestamp": alert["timestamp"].isoformat(),
                }
                for alert in self.alerts
            ],
        }

        with open(output_path, 'w', encoding = 'utf - 8') as f:
            json.dump(export_data, f, indent = 2, ensure_ascii = False)

        print(f"📊 指标数据已导出到: {output_path}")

async def main() - > None:
    """主函数"""
    parser = argparse.ArgumentParser(description = "API 网关监控工具")
    parser.add_argument(
        " - -url",
        default = "http: / /localhost:8000",
        help = "API 网关地址 (默认: http: / /localhost:8000)"
    )
    parser.add_argument(
        " - -interval",
        type = int,
        default = 5,
        help = "刷新间隔（秒）(默认: 5)"
    )
    parser.add_argument(
        " - -simple",
        action = "store_true",
        help = "使用简单模式（非交互式）"
    )
    parser.add_argument(
        " - -export",
        help = "导出指标数据到文件"
    )
    parser.add_argument(
        " - -cpu - threshold",
        type = float,
        default = 80.0,
        help = "CPU 使用率告警阈值 (默认: 80.0)"
    )
    parser.add_argument(
        " - -memory - threshold",
        type = float,
        default = 85.0,
        help = "内存使用率告警阈值 (默认: 85.0)"
    )

    args = parser.parse_args()

    # 配置告警阈值
    alert_thresholds = {
        'cpu_percent': args.cpu_threshold,
        'memory_percent': args.memory_threshold,
        'response_time_p99': 1.0,
        'error_rate': 5.0,
    }

    monitor = GatewayMonitor(
        gateway_url = args.url,
        refresh_interval = args.interval,
        alert_thresholds = alert_thresholds,
    )

    if args.export:
        # 运行一次收集数据然后导出
        await monitor.collect_data()
        monitor.export_metrics(args.export)
    elif args.simple:
        await monitor.run_simple()
    else:
        await monitor.run_dashboard()

if __name__ == "__main__":
    asyncio.run(main())