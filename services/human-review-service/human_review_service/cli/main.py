"""
CLI 主入口
CLI Main Entry

提供命令行工具的主要功能
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
import structlog
import uvicorn
from rich.console import Console
from rich.table import Table

from ..core.config import settings
from ..core.database import close_database, init_database
from .commands import database, reviewer, server

logger = structlog.get_logger(__name__)
console = Console()


@click.group()
@click.option("--config", "-c", type=click.Path(exists=True), help="配置文件路径")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool):
    """
    索克生活人工审核微服务 CLI 工具

    提供服务管理、数据库操作、审核员管理等功能
    """
    # 确保上下文对象存在
    ctx.ensure_object(dict)

    # 保存配置
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose

    # 配置日志级别
    if verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO
        )

    # 显示欢迎信息
    if ctx.invoked_subcommand is None:
        console.print(f"[bold green]索克生活人工审核微服务 CLI[/bold green]")
        console.print(f"版本: {settings.app_version}")
        console.print(f"环境: {settings.environment}")
        console.print("\n使用 --help 查看可用命令")


@cli.command()
@click.option("--host", default="0.0.0.0", help="服务器主机地址")
@click.option("--port", default=8000, type=int, help="服务器端口")
@click.option("--reload", is_flag=True, help="启用自动重载（开发模式）")
@click.option("--workers", default=1, type=int, help="工作进程数量")
def serve(host: str, port: int, reload: bool, workers: int):
    """启动HTTP服务器"""
    console.print(f"[bold blue]启动人工审核微服务...[/bold blue]")
    console.print(f"主机: {host}")
    console.print(f"端口: {port}")
    console.print(f"工作进程: {workers}")
    console.print(f"自动重载: {'是' if reload else '否'}")

    try:
        uvicorn.run(
            "human_review_service.api.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level="info" if not settings.debug else "debug",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]服务已停止[/yellow]")
    except Exception as e:
        console.print(f"[red]启动失败: {e}[/red]")
        sys.exit(1)


@cli.command()
def info():
    """显示服务信息"""
    table = Table(title="服务信息")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("服务名称", settings.app_name)
    table.add_row("版本", settings.app_version)
    table.add_row("环境", settings.environment)
    table.add_row("调试模式", "是" if settings.debug else "否")
    # 隐藏数据库URL中的密码
    db_url = settings.database.url
    if "@" in db_url and "://" in db_url:
        # 格式: postgresql://user:password@host:port/db
        parts = db_url.split("://")
        if len(parts) == 2:
            scheme = parts[0]
            rest = parts[1]
            if "@" in rest:
                auth_part, host_part = rest.split("@", 1)
                if ":" in auth_part:
                    user, _ = auth_part.split(":", 1)
                    db_url = f"{scheme}://{user}:***@{host_part}"
    table.add_row("数据库URL", db_url)
    table.add_row("Redis URL", settings.redis.url if settings.redis.url else "未配置")
    table.add_row("日志级别", settings.monitoring.log_level)

    console.print(table)


@cli.command()
@click.option("--check-db", is_flag=True, help="检查数据库连接")
@click.option("--check-redis", is_flag=True, help="检查Redis连接")
def health(check_db: bool, check_redis: bool):
    """健康检查"""
    console.print("[bold blue]执行健康检查...[/bold blue]")

    async def run_checks():
        checks = []

        if check_db:
            try:
                await init_database()
                checks.append(("数据库", "✅ 正常"))
                await close_database()
            except Exception as e:
                checks.append(("数据库", f"❌ 错误: {e}"))

        if check_redis:
            # TODO: 实现Redis连接检查
            checks.append(("Redis", "⚠️ 未实现"))

        # 显示检查结果
        table = Table(title="健康检查结果")
        table.add_column("组件", style="cyan")
        table.add_column("状态", style="white")

        for component, status in checks:
            table.add_row(component, status)

        console.print(table)

    try:
        asyncio.run(run_checks())
    except Exception as e:
        console.print(f"[red]健康检查失败: {e}[/red]")
        sys.exit(1)


@cli.command()
def version():
    """显示版本信息"""
    console.print(
        f"[bold green]{settings.app_name}[/bold green] v{settings.app_version}"
    )


# 注册子命令组
cli.add_command(database.db)
cli.add_command(reviewer.reviewer)
cli.add_command(server.server)


if __name__ == "__main__":
    cli()
