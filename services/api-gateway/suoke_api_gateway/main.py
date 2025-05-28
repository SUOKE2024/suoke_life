"""
主程序入口

提供命令行接口和服务启动功能。
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn
from rich.console import Console
from rich.table import Table

from .core.app import create_app, create_dev_app
from .core.config import Settings, get_settings, create_settings_from_file
from .core.logging import get_logger, setup_logging

console = Console()
logger = get_logger(__name__)


def handle_shutdown(signum, frame):
    """处理关闭信号"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


@click.group()
@click.version_option(version="0.1.0", prog_name="suoke-api-gateway")
def cli():
    """索克生活 API 网关服务"""
    pass


@cli.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="服务器主机地址",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="服务器端口",
    show_default=True,
)
@click.option(
    "--workers",
    default=1,
    type=int,
    help="工作进程数",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="启用自动重载（开发模式）",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="配置文件路径",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="日志级别",
    show_default=True,
)
@click.option(
    "--access-log/--no-access-log",
    default=True,
    help="是否启用访问日志",
)
def run(
    host: str,
    port: int,
    workers: int,
    reload: bool,
    config: Optional[Path],
    log_level: str,
    access_log: bool,
):
    """启动 API 网关服务"""
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        # 加载配置
        if config:
            settings = create_settings_from_file(config)
            console.print(f"[green]✓[/green] 从配置文件加载设置: {config}")
        else:
            settings = get_settings()
            console.print("[green]✓[/green] 使用默认配置")
        
        # 覆盖命令行参数
        settings.host = host
        settings.port = port
        settings.workers = workers
        settings.log_level = log_level
        
        # 设置日志
        setup_logging(settings)
        
        # 显示启动信息
        show_startup_info(settings)
        
        # 创建应用
        if reload:
            # 开发模式
            app = create_dev_app()
            console.print("[yellow]⚠[/yellow] 运行在开发模式，启用自动重载")
        else:
            app = create_app(settings)
        
        # 启动服务器
        uvicorn_config = {
            "app": app,
            "host": host,
            "port": port,
            "log_level": log_level.lower(),
            "access_log": access_log,
            "server_header": False,
            "date_header": False,
        }
        
        if reload:
            uvicorn_config.update({
                "reload": True,
                "reload_dirs": ["suoke_api_gateway"],
            })
        elif workers > 1:
            uvicorn_config["workers"] = workers
        
        logger.info("Starting Suoke API Gateway server")
        uvicorn.run(**uvicorn_config)
        
    except Exception as e:
        console.print(f"[red]✗[/red] 启动失败: {e}")
        logger.error("Failed to start server", error=str(e), exc_info=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="配置文件路径",
)
def dev(config: Optional[Path]):
    """启动开发服务器"""
    console.print("[blue]🚀[/blue] 启动开发服务器...")
    
    # 使用开发模式的默认配置
    ctx = click.get_current_context()
    ctx.invoke(
        run,
        host="127.0.0.1",
        port=8000,
        workers=1,
        reload=True,
        config=config,
        log_level="DEBUG",
        access_log=True,
    )


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="配置文件路径",
)
def check(config: Optional[Path]):
    """检查配置和依赖"""
    console.print("[blue]🔍[/blue] 检查配置和依赖...")
    
    try:
        # 加载配置
        if config:
            settings = create_settings_from_file(config)
        else:
            settings = get_settings()
        
        # 显示配置信息
        show_config_info(settings)
        
        # 检查依赖服务
        asyncio.run(check_dependencies(settings))
        
        console.print("[green]✓[/green] 所有检查通过")
        
    except Exception as e:
        console.print(f"[red]✗[/red] 检查失败: {e}")
        sys.exit(1)


def show_startup_info(settings: Settings) -> None:
    """显示启动信息"""
    table = Table(title="Suoke API Gateway 启动信息")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("应用名称", settings.app_name)
    table.add_row("版本", settings.app_version)
    table.add_row("环境", settings.environment)
    table.add_row("主机", settings.host)
    table.add_row("端口", str(settings.port))
    table.add_row("工作进程", str(settings.workers))
    table.add_row("日志级别", settings.log_level)
    table.add_row("调试模式", "是" if settings.debug else "否")
    
    if settings.grpc.enabled:
        table.add_row("gRPC 端口", str(settings.grpc.port))
    
    console.print(table)


def show_config_info(settings: Settings) -> None:
    """显示配置信息"""
    table = Table(title="配置信息")
    table.add_column("模块", style="cyan")
    table.add_column("配置", style="green")
    
    table.add_row("数据库", settings.get_database_url())
    table.add_row("Redis", settings.get_redis_url())
    table.add_row("JWT 算法", settings.jwt.algorithm)
    table.add_row("限流", "启用" if settings.rate_limit.enabled else "禁用")
    table.add_row("监控", "启用" if settings.monitoring.enabled else "禁用")
    table.add_row("gRPC", "启用" if settings.grpc.enabled else "禁用")
    
    console.print(table)


async def check_dependencies(settings: Settings) -> None:
    """检查依赖服务"""
    console.print("检查依赖服务...")
    
    # 检查 Redis 连接
    try:
        import redis.asyncio as redis
        r = redis.from_url(settings.get_redis_url())
        await r.ping()
        console.print("[green]✓[/green] Redis 连接正常")
        await r.close()
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Redis 连接失败: {e}")
    
    # 检查注册的服务
    for service_name, service_config in settings.services.items():
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                url = f"http://{service_config.host}:{service_config.port}{service_config.health_check_path}"
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    console.print(f"[green]✓[/green] 服务 {service_name} 健康")
                else:
                    console.print(f"[yellow]⚠[/yellow] 服务 {service_name} 状态异常: {response.status_code}")
        except Exception as e:
            console.print(f"[red]✗[/red] 服务 {service_name} 不可达: {e}")


def main() -> None:
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main() 