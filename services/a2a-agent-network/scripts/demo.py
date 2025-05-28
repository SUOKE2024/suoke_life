#!/usr/bin/env python3
"""
A2A 智能体网络微服务演示脚本
A2A Agent Network Microservice Demo Script
"""

import asyncio
import json
import time
from typing import Any

import aiohttp
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class A2ANetworkDemo:
    """A2A 网络演示类"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        初始化演示客户端

        Args:
            base_url: 服务基础URL
        """
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def check_health(self) -> dict[str, Any]:
        """检查服务健康状态"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_agents(self) -> dict[str, Any]:
        """获取智能体列表"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/agents") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_network_status(self) -> dict[str, Any]:
        """获取网络状态"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/network/status"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_agent_action(
        self, agent_id: str, action: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """执行智能体动作"""
        try:
            data = {
                "action": action,
                "parameters": parameters,
                "user_id": "demo_user",
                "request_id": f"demo_{int(time.time())}",
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/agents/{agent_id}/execute", json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_workflow(
        self, workflow_id: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """执行工作流"""
        try:
            data = {
                "workflow_id": workflow_id,
                "user_id": "demo_user",
                "parameters": parameters,
                "context": {"demo": True},
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/workflows/execute", json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_workflows(self) -> dict[str, Any]:
        """获取工作流列表"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/workflows"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def demo_health_check():
    """演示健康检查"""
    console.print("\n[bold blue]🏥 健康检查演示[/bold blue]")

    async with A2ANetworkDemo() as demo:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("检查服务健康状态...", total=None)

            health = await demo.check_health()
            progress.remove_task(task)

            if health.get("status") == "healthy":
                console.print("✅ 服务健康状态正常")
                console.print(f"📅 时间戳: {health.get('timestamp')}")
            else:
                console.print(f"❌ 服务健康检查失败: {health.get('error')}")


async def demo_agents():
    """演示智能体管理"""
    console.print("\n[bold green]🤖 智能体管理演示[/bold green]")

    async with A2ANetworkDemo() as demo:
        # 获取智能体列表
        agents_result = await demo.get_agents()

        if agents_result.get("success"):
            agents = agents_result.get("data", [])

            # 创建智能体状态表格
            table = Table(title="智能体状态")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="magenta")
            table.add_column("状态", style="green")
            table.add_column("URL", style="blue")

            for agent in agents:
                status_emoji = "🟢" if agent.get("status") == "online" else "🔴"
                table.add_row(
                    agent.get("id", ""),
                    agent.get("name", ""),
                    f"{status_emoji} {agent.get('status', '')}",
                    agent.get("url", ""),
                )

            console.print(table)
        else:
            console.print(f"❌ 获取智能体列表失败: {agents_result.get('error')}")


async def demo_network_status():
    """演示网络状态"""
    console.print("\n[bold yellow]🌐 网络状态演示[/bold yellow]")

    async with A2ANetworkDemo() as demo:
        status_result = await demo.get_network_status()

        if status_result.get("success"):
            status = status_result.get("data", {})

            # 创建网络状态面板
            status_text = f"""
总智能体数: {status.get('total_agents', 0)}
在线智能体: {status.get('online_agents', 0)}
离线智能体: {status.get('offline_agents', 0)}
网络健康度: {status.get('network_health', 0):.2%}
            """

            panel = Panel(status_text.strip(), title="网络状态", border_style="yellow")
            console.print(panel)

            # 显示各智能体状态
            agents_status = status.get("agents", {})
            for agent_id, agent_status in agents_status.items():
                status_emoji = "🟢" if agent_status == "online" else "🔴"
                console.print(f"  {status_emoji} {agent_id}: {agent_status}")
        else:
            console.print(f"❌ 获取网络状态失败: {status_result.get('error')}")


async def demo_agent_action():
    """演示智能体动作执行"""
    console.print("\n[bold magenta]⚡ 智能体动作演示[/bold magenta]")

    async with A2ANetworkDemo() as demo:
        # 模拟执行小艾的诊断动作
        console.print("🔍 执行小艾智能体诊断动作...")

        result = await demo.execute_agent_action(
            agent_id="xiaoai",
            action="diagnose",
            parameters={
                "symptoms": "头痛、失眠",
                "duration": "3天",
                "severity": "中等",
            },
        )

        if result.get("success"):
            console.print("✅ 智能体动作执行成功")
            console.print(f"📊 执行时间: {result.get('execution_time', 0):.2f}秒")

            data = result.get("data", {})
            if data:
                console.print("📋 执行结果:")
                console.print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            console.print(f"❌ 智能体动作执行失败: {result.get('error')}")


async def demo_workflow():
    """演示工作流执行"""
    console.print("\n[bold red]🔄 工作流演示[/bold red]")

    async with A2ANetworkDemo() as demo:
        # 获取可用工作流
        workflows_result = await demo.get_workflows()

        if workflows_result.get("success"):
            workflows = workflows_result.get("data", [])

            if workflows:
                # 显示可用工作流
                console.print("📋 可用工作流:")
                for workflow in workflows:
                    console.print(f"  • {workflow.get('name')} ({workflow.get('id')})")

                # 执行健康咨询工作流
                console.print("\n🚀 执行健康咨询工作流...")

                result = await demo.execute_workflow(
                    workflow_id="health_consultation",
                    parameters={
                        "consultation_type": "症状咨询",
                        "symptoms": "头痛、失眠、食欲不振",
                        "user_profile": {
                            "age": 30,
                            "gender": "female",
                            "constitution": "unknown",
                        },
                    },
                )

                if result.get("success"):
                    console.print("✅ 工作流启动成功")
                    data = result.get("data", {})
                    console.print(f"🆔 执行ID: {data.get('execution_id')}")
                    console.print(f"📊 状态: {data.get('status')}")
                    console.print(f"💬 消息: {data.get('message')}")
                else:
                    console.print(f"❌ 工作流执行失败: {result.get('error')}")
            else:
                console.print("⚠️ 没有可用的工作流")
        else:
            console.print(f"❌ 获取工作流列表失败: {workflows_result.get('error')}")


async def demo_real_time_monitoring():
    """演示实时监控"""
    console.print("\n[bold cyan]📊 实时监控演示[/bold cyan]")

    async with A2ANetworkDemo() as demo:
        console.print("🔄 模拟实时监控 (5秒)...")

        # 创建实时更新的表格
        def create_status_table():
            table = Table(title="实时网络状态")
            table.add_column("时间", style="cyan")
            table.add_column("在线智能体", style="green")
            table.add_column("网络健康度", style="yellow")
            return table

        with Live(create_status_table(), refresh_per_second=1, console=console) as live:
            for _i in range(5):
                # 获取当前状态
                status_result = await demo.get_network_status()

                if status_result.get("success"):
                    status = status_result.get("data", {})

                    # 更新表格
                    table = create_status_table()
                    table.add_row(
                        time.strftime("%H:%M:%S"),
                        str(status.get("online_agents", 0)),
                        f"{status.get('network_health', 0):.2%}",
                    )

                    live.update(table)

                await asyncio.sleep(1)


async def main():
    """主演示函数"""
    console.print(
        Panel.fit(
            "[bold blue]🚀 A2A 智能体网络微服务演示[/bold blue]\n"
            "展示智能体网络管理、工作流执行和实时监控功能",
            border_style="blue",
        )
    )

    try:
        # 依次执行各个演示
        await demo_health_check()
        await demo_agents()
        await demo_network_status()
        await demo_agent_action()
        await demo_workflow()
        await demo_real_time_monitoring()

        console.print("\n[bold green]🎉 演示完成！[/bold green]")
        console.print(
            "💡 提示: 确保 A2A 智能体网络微服务正在运行在 http://localhost:5000"
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ 演示被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ 演示过程中发生错误: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
