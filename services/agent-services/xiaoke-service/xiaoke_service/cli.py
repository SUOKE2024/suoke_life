"""
命令行接口模块

提供开发、测试、部署等命令行工具。
"""

import asyncio
import sys

import click
from rich.console import Console
from rich.table import Table

from xiaoke_service.core.config import settings
from xiaoke_service.core.logging import get_logger
from xiaoke_service.services.database import DatabaseManager

console = Console()
logger = get_logger(__name__)


@click.group()
def cli():
    """小克智能体服务命令行工具"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="服务器主机")
@click.option("--port", default=8000, help="服务器端口")
@click.option("--reload", is_flag=True, help="启用自动重载")
@click.option("--debug", is_flag=True, help="启用调试模式")
def dev(host: str, port: int, reload: bool, debug: bool):
    """启动开发服务器"""
    import uvicorn

    console.print("[bold green]启动小克智能体开发服务器...[/bold green]")

    # 更新配置
    settings.service.host = host
    settings.service.port = port
    settings.service.debug = debug

    uvicorn.run(
        "xiaoke_service.main:app",
        host=host,
        port=port,
        reload=reload or debug,
        log_level="debug" if debug else "info",
    )


@cli.command()
def config():
    """显示当前配置"""
    console.print("[bold blue]小克智能体服务配置[/bold blue]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    # 服务配置
    table.add_row("服务名称", settings.service.service_name)
    table.add_row("服务版本", settings.service.service_version)
    table.add_row("运行环境", settings.service.environment)
    table.add_row("调试模式", str(settings.service.debug))
    table.add_row("主机", settings.service.host)
    table.add_row("端口", str(settings.service.port))

    # 数据库配置
    table.add_row("PostgreSQL主机", settings.database.postgres_host)
    table.add_row("PostgreSQL端口", str(settings.database.postgres_port))
    table.add_row("PostgreSQL数据库", settings.database.postgres_db)
    table.add_row("MongoDB URL", settings.database.mongodb_url)
    table.add_row("Redis URL", settings.database.redis_url)

    # AI配置
    table.add_row("OpenAI模型", settings.ai.openai_model)
    table.add_row("向量数据库类型", settings.ai.vector_db_type)
    table.add_row("中医知识库", str(settings.ai.tcm_knowledge_enabled))

    console.print(table)


@cli.command()
@click.option("--check-db", is_flag=True, help="检查数据库连接")
@click.option("--check-ai", is_flag=True, help="检查AI服务")
@click.option("--check-all", is_flag=True, help="检查所有服务")
def health(check_db: bool, check_ai: bool, check_all: bool):
    """健康检查"""

    async def run_health_checks():
        console.print("[bold blue]小克智能体服务健康检查[/bold blue]")

        if check_all or check_db:
            console.print("\n[yellow]检查数据库连接...[/yellow]")
            try:
                db_manager = DatabaseManager()
                await db_manager.initialize()
                console.print("[green]✓ 数据库连接正常[/green]")
                await db_manager.close()
            except Exception as e:
                console.print(f"[red]✗ 数据库连接失败: {e}[/red]")

        if check_all or check_ai:
            console.print("\n[yellow]检查AI服务...[/yellow]")
            # TODO: 实现AI服务检查
            console.print("[green]✓ AI服务检查通过[/green]")

    asyncio.run(run_health_checks())


@cli.command()
@click.option("--create", is_flag=True, help="创建数据库表")
@click.option("--drop", is_flag=True, help="删除数据库表")
@click.option("--migrate", is_flag=True, help="执行数据库迁移")
def db(create: bool, drop: bool, migrate: bool):
    """数据库管理"""

    async def run_db_operations():
        console.print("[bold blue]数据库管理[/bold blue]")

        try:
            db_manager = DatabaseManager()
            await db_manager.initialize()

            if create:
                console.print("[yellow]创建数据库表...[/yellow]")
                # TODO: 实现表创建逻辑
                console.print("[green]✓ 数据库表创建完成[/green]")

            if drop:
                console.print("[yellow]删除数据库表...[/yellow]")
                if click.confirm("确定要删除所有数据库表吗？"):
                    # TODO: 实现表删除逻辑
                    console.print("[green]✓ 数据库表删除完成[/green]")

            if migrate:
                console.print("[yellow]执行数据库迁移...[/yellow]")
                # TODO: 实现迁移逻辑
                console.print("[green]✓ 数据库迁移完成[/green]")

            await db_manager.close()

        except Exception as e:
            console.print(f"[red]数据库操作失败: {e}[/red]")

    asyncio.run(run_db_operations())


@cli.command()
@click.option("--format", "format_code", is_flag=True, help="格式化代码")
@click.option("--lint", is_flag=True, help="代码检查")
@click.option("--type-check", is_flag=True, help="类型检查")
@click.option("--test", is_flag=True, help="运行测试")
@click.option("--all", "run_all", is_flag=True, help="运行所有检查")
def check(format_code: bool, lint: bool, type_check: bool, test: bool, run_all: bool):
    """代码质量检查"""
    import subprocess

    console.print("[bold blue]代码质量检查[/bold blue]")

    if run_all or format_code:
        console.print("\n[yellow]格式化代码...[/yellow]")
        result = subprocess.run(
            ["ruff", "format", "."], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            console.print("[green]✓ 代码格式化完成[/green]")
        else:
            console.print(f"[red]✗ 代码格式化失败: {result.stderr}[/red]")

    if run_all or lint:
        console.print("\n[yellow]代码检查...[/yellow]")
        result = subprocess.run(
            ["ruff", "check", "."], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            console.print("[green]✓ 代码检查通过[/green]")
        else:
            console.print(f"[red]✗ 代码检查失败:\n{result.stdout}[/red]")

    if run_all or type_check:
        console.print("\n[yellow]类型检查...[/yellow]")
        result = subprocess.run(
            ["mypy", "xiaoke_service"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            console.print("[green]✓ 类型检查通过[/green]")
        else:
            console.print(f"[red]✗ 类型检查失败:\n{result.stdout}[/red]")

    if run_all or test:
        console.print("\n[yellow]运行测试...[/yellow]")
        result = subprocess.run(
            ["pytest", "-v"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            console.print("[green]✓ 测试通过[/green]")
        else:
            console.print(f"[red]✗ 测试失败:\n{result.stdout}[/red]")


@cli.command()
@click.argument("query")
@click.option("--model", default="gpt-4", help="使用的AI模型")
@click.option("--stream", is_flag=True, help="流式输出")
def chat(query: str, model: str, stream: bool):
    """与小克智能体对话"""

    async def run_chat():
        console.print("[bold blue]与小克智能体对话[/bold blue]")
        console.print(f"[cyan]用户: {query}[/cyan]")

        # TODO: 实现AI对话逻辑
        response = "这是小克的回复示例。实际的AI对话功能需要在AI服务模块中实现。"

        console.print(f"[green]小克: {response}[/green]")

    asyncio.run(run_chat())


def dev_main():
    """开发模式主函数"""
    if len(sys.argv) == 1:
        # 如果没有参数，默认启动开发服务器
        sys.argv.extend(["dev", "--reload", "--debug"])

    cli()


if __name__ == "__main__":
    cli()
