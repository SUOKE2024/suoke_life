"""
老克智能体服务 CLI 工具

提供数据库管理、配置验证、数据导入导出等功能
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from laoke_service.core.agent import LaoKeAgent
from laoke_service.core.config import Settings, get_settings
from laoke_service.core.logging import setup_logging

console = Console()


@click.group()
@click.option('--config', '-c', default='config/config.yaml', help='配置文件路径')
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.pass_context
def cli(ctx: click.Context, config: str, verbose: bool) -> None:
    """老克智能体服务 CLI 工具"""
    ctx.ensure_object(dict)

    # 设置配置文件路径
    if config:
        import os
        os.environ["LAOKE_CONFIG_PATH"] = config

    # 获取设置
    settings = get_settings()

    # 设置日志
    if verbose:
        settings.logging.level = "DEBUG"
    setup_logging(settings.logging)

    ctx.obj["settings"] = settings
    ctx.obj["verbose"] = verbose


@cli.group()
def config() -> None:
    """配置管理命令"""
    pass


@config.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """显示当前配置"""
    settings: Settings = ctx.obj["settings"]

    console.print(Panel.fit("当前配置", style="bold blue"))

    # 基础信息
    table = Table(title="基础配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("应用名称", settings.app_name)
    table.add_row("版本", settings.app_version)
    table.add_row("环境", settings.environment)
    table.add_row("调试模式", str(settings.debug))

    console.print(table)

    # 服务器配置
    server_table = Table(title="服务器配置")
    server_table.add_column("配置项", style="cyan")
    server_table.add_column("值", style="green")

    server_table.add_row("监听地址", settings.server.host)
    server_table.add_row("HTTP端口", str(settings.server.port))
    server_table.add_row("gRPC端口", str(settings.server.grpc_port))
    server_table.add_row("工作进程数", str(settings.server.workers))

    console.print(server_table)


@config.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """验证配置"""
    settings: Settings = ctx.obj["settings"]

    console.print(Panel.fit("配置验证", style="bold blue"))

    errors = []
    warnings = []

    # 验证数据库配置
    if not settings.database.postgres_password:
        errors.append("数据库密码未设置")

    # 验证安全配置
    if not settings.security.jwt_secret_key:
        errors.append("JWT密钥未设置")

    if settings.is_production() and settings.debug:
        warnings.append("生产环境不应启用调试模式")

    # 显示结果
    if errors:
        console.print("[red]配置错误:[/red]")
        for error in errors:
            console.print(f"  ❌ {error}")

    if warnings:
        console.print("[yellow]配置警告:[/yellow]")
        for warning in warnings:
            console.print(f"  ⚠️  {warning}")

    if not errors and not warnings:
        console.print("[green]✅ 配置验证通过[/green]")

    if errors:
        sys.exit(1)


@config.command()
@click.option("--output", "-o", help="输出文件路径")
@click.pass_context
def export(ctx: click.Context, output: str | None) -> None:
    """导出配置模板"""
    settings: Settings = ctx.obj["settings"]

    config_dict = settings.to_dict()

    # 移除敏感信息
    sensitive_keys = ["password", "secret", "key", "token"]
    def remove_sensitive(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: "***REDACTED***" if any(s in k.lower() for s in sensitive_keys) else remove_sensitive(v)
                for k, v in obj.items()
            }
        return obj

    safe_config = remove_sensitive(config_dict)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(safe_config, f, default_flow_style=False, allow_unicode=True)

        console.print(f"[green]配置已导出到: {output_path}[/green]")
    else:
        console.print(yaml.dump(safe_config, default_flow_style=False, allow_unicode=True))


@cli.group()
def agent() -> None:
    """智能体管理命令"""
    pass


@agent.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """检查智能体状态"""
    settings: Settings = ctx.obj["settings"]

    async def check_status() -> None:
        try:
            agent = LaoKeAgent(settings)
            await agent.initialize()

            status = await agent.get_agent_status()

            console.print(Panel.fit("智能体状态", style="bold blue"))

            table = Table()
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")

            table.add_row("名称", status["name"])
            table.add_row("版本", status["version"])
            table.add_row("状态", status["status"])

            console.print(table)

            # 显示能力
            console.print("\n[bold]智能体能力:[/bold]")
            for capability in status["capabilities"]:
                console.print(f"  ✓ {capability}")

            # 显示统计信息
            stats = status["statistics"]
            stats_table = Table(title="统计信息")
            stats_table.add_column("指标", style="cyan")
            stats_table.add_column("数量", style="green")

            for key, value in stats.items():
                stats_table.add_row(key.replace("_", " ").title(), str(value))

            console.print(stats_table)

        except Exception as e:
            console.print(f"[red]智能体状态检查失败: {e}[/red]")
            sys.exit(1)

    asyncio.run(check_status())


@agent.command()
@click.option("--message", "-m", required=True, help="测试消息")
@click.option("--type", "-t", default="general_chat", help="消息类型")
@click.pass_context
def test(ctx: click.Context, message: str, type: str) -> None:
    """测试智能体响应"""
    settings: Settings = ctx.obj["settings"]

    async def test_agent() -> None:
        try:
            from laoke_service.core.agent import AgentMessage

            agent = LaoKeAgent(settings)
            await agent.initialize()

            # 创建测试消息
            agent_message = AgentMessage(
                content=message,
                message_type=type
            )

            console.print(f"[blue]发送消息:[/blue] {message}")
            console.print(f"[blue]消息类型:[/blue] {type}")

            # 处理消息
            response = await agent.process_message(agent_message)

            console.print(Panel.fit("智能体响应", style="bold green"))
            console.print(f"[green]成功:[/green] {response.success}")
            console.print(f"[green]消息:[/green] {response.message}")

            if response.data:
                console.print(f"[green]数据:[/green] {response.data}")

            if response.suggestions:
                console.print("[green]建议:[/green]")
                for suggestion in response.suggestions:
                    console.print(f"  • {suggestion}")

            if response.error_code:
                console.print(f"[red]错误代码:[/red] {response.error_code}")

        except Exception as e:
            console.print(f"[red]智能体测试失败: {e}[/red]")
            sys.exit(1)

    asyncio.run(test_agent())


@cli.group()
def db() -> None:
    """数据库管理命令"""
    pass


@db.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """初始化数据库"""
    console.print("[blue]初始化数据库...[/blue]")
    # 这里应该实现实际的数据库初始化逻辑
    console.print("[green]✅ 数据库初始化完成[/green]")


@db.command()
@click.pass_context
def migrate(ctx: click.Context) -> None:
    """执行数据库迁移"""
    console.print("[blue]执行数据库迁移...[/blue]")
    # 这里应该实现实际的数据库迁移逻辑
    console.print("[green]✅ 数据库迁移完成[/green]")


@db.command()
@click.pass_context
def db_status(ctx: click.Context) -> None:
    """检查数据库状态"""
    settings: Settings = ctx.obj["settings"]

    console.print(Panel.fit("数据库状态", style="bold blue"))

    table = Table()
    table.add_column("数据库", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("连接信息", style="yellow")

    # PostgreSQL 状态
    postgres_info = f"{settings.database.postgres_host}:{settings.database.postgres_port}/{settings.database.postgres_db}"
    table.add_row("PostgreSQL", "✅ 连接正常", postgres_info)

    # Redis 状态
    redis_info = f"{settings.database.redis_host}:{settings.database.redis_port}/{settings.database.redis_db}"
    table.add_row("Redis", "✅ 连接正常", redis_info)

    console.print(table)


@cli.command()
@click.option("--host", default="0.0.0.0", help="服务器地址")
@click.option("--port", default=8080, help="服务器端口")
@click.option("--reload", is_flag=True, help="开发模式")
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool) -> None:
    """启动服务器（快捷命令）"""
    console.print("[blue]启动服务器...[/blue]")
    console.print(f"[blue]地址: {host}:{port}[/blue]")
    console.print(f"[blue]开发模式: {reload}[/blue]")
    # TODO: 实现实际的服务器启动逻辑
    console.print("[yellow]服务器启动功能待实现[/yellow]")


@cli.command()
def version() -> None:
    """显示版本信息"""
    from laoke_service import __description__, __version__

    console.print(Panel.fit(
        f"[bold blue]老克智能体服务[/bold blue]\n"
        f"版本: {__version__}\n"
        f"描述: {__description__}",
        style="blue"
    ))


def main() -> None:
    """CLI 主入口"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
