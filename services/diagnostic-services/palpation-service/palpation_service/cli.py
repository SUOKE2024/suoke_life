"""
索克生活触诊服务CLI工具
"""

import asyncio
import click
import json
import sys
import uvicorn
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .config import get_settings

console = Console()

@click.group()
@click.version_option(version="1.0.0", prog_name="palpation-service")
def cli():
    """索克生活触诊服务命令行工具"""
    pass

@cli.command()
@click.option("--host", default="0.0.0.0", help="服务主机地址")
@click.option("--port", default=8000, help="服务端口")
@click.option("--reload", is_flag=True, help="启用自动重载")
@click.option("--workers", default=1, help="工作进程数")
@click.option("--log-level", default="info", help="日志级别")
def serve(host: str, port: int, reload: bool, workers: int, log_level: str):
    """启动触诊服务"""
    console.print(f"[bold green]启动索克生活触诊服务...[/bold green]")
    console.print(f"主机: {host}")
    console.print(f"端口: {port}")
    
    try:
        uvicorn.run(
            "palpation_service.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]服务已停止[/yellow]")
    except Exception as e:
        console.print(f"[red]启动服务失败: {e}[/red]")
        sys.exit(1)

@cli.command()
def check_config():
    """检查配置文件"""
    console.print("[blue]检查配置文件...[/blue]")
    
    try:
        settings = get_settings()
        
        table = Table(title="配置信息")
        table.add_column("配置项", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("服务名称", settings.service.name)
        table.add_row("服务版本", settings.service.version)
        table.add_row("运行环境", settings.service.env)
        table.add_row("主机地址", settings.service.host)
        table.add_row("端口", str(settings.service.port))
        
        console.print(table)
        console.print("[green]✓ 配置文件检查通过[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ 配置文件检查失败: {e}[/red]")
        sys.exit(1)

@cli.command()
def dev():
    """开发模式启动服务"""
    console.print("[bold green]启动开发模式...[/bold green]")
    
    try:
        uvicorn.run(
            "palpation_service.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug",
            access_log=True
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]开发服务已停止[/yellow]")
    except Exception as e:
        console.print(f"[red]启动开发服务失败: {e}[/red]")
        sys.exit(1)

def main():
    """主函数"""
    cli()

def dev_main():
    """开发模式主函数"""
    console.print("[bold green]索克生活触诊服务 - 开发模式[/bold green]")
    dev()

if __name__ == "__main__":
    main()
