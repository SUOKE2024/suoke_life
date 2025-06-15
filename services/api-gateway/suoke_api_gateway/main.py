#!/usr/bin/env python3
"""
索克生活 API 网关主程序

提供命令行接口启动和管理 API 网关服务
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

import click
import httpx
import uvicorn
from rich.console import Console
from rich.table import Table

from .core.app import create_app, create_dev_app
from .core.config import Settings, get_settings, create_settings_from_file
from .core.logging import get_logger, setup_logging

console = Console()
logger = get_logger(__name__)


@click.group()
@click.version_option()
def cli() -> None:
    """索克生活 API 网关命令行工具"""
    pass


@cli.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="监听地址",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="监听端口",
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
    type=click.Path(exists=True),
    help="配置文件路径",
)
def serve(host: str, port: int, workers: int, reload: bool, config: Optional[str]) -> None:
    """启动 API 网关服务"""
    try:
        # 加载配置
        if config:
            settings = create_settings_from_file(Path(config))
        else:
            settings = get_settings()
        
        # 设置日志
        setup_logging(settings)
        
        # 创建应用
        app = create_app(settings)
        
        # 显示启动信息
        _show_startup_info(host, port, workers, reload)
        
        # 启动服务器
        uvicorn.run(
            "suoke_api_gateway.main:app",
            host=host,
            port=port,
            workers=workers if not reload else 1,
            reload=reload,
            log_config=None,  # 使用我们自己的日志配置
            access_log=False,  # 通过中间件记录访问日志
        )
        
    except Exception as e:
        console.print(f"[red]启动失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="监听地址",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="监听端口",
    show_default=True,
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="配置文件路径",
)
def dev(host: str, port: int, config: Optional[str]) -> None:
    """启动开发模式服务器"""
    try:
        # 加载配置
        if config:
            settings = create_settings_from_file(Path(config))
        else:
            settings = get_settings()
        
        # 强制开发模式设置
        settings.environment = "development"
        settings.log_level = "DEBUG"
        
        # 设置日志
        setup_logging(settings)
        
        # 创建开发应用
        app = create_dev_app(settings)
        
        # 显示开发模式信息
        _show_dev_info(host, port)
        
        # 启动开发服务器
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=True,
            log_config=None,
            access_log=False,
        )
        
    except Exception as e:
        console.print(f"[red]开发服务器启动失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--url",
    default="http://localhost:8000",
    help="API 网关地址",
    show_default=True,
)
@click.option(
    "--timeout",
    default=10,
    type=int,
    help="请求超时时间（秒）",
    show_default=True,
)
def health(url: str, timeout: int) -> None:
    """检查 API 网关健康状态"""
    try:
        with console.status("[bold green]检查健康状态..."):
            response = httpx.get(f"{url}/health", timeout=timeout)
            
        if response.status_code == 200:
            data = response.json()
            _show_health_status(data)
        else:
            console.print(f"[red]健康检查失败: HTTP {response.status_code}[/red]")
            sys.exit(1)
            
    except httpx.TimeoutException:
        console.print(f"[red]健康检查超时: {timeout}秒[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]健康检查失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--url",
    default="http://localhost:8000",
    help="API 网关地址",
    show_default=True,
)
@click.option(
    "--timeout",
    default=10,
    type=int,
    help="请求超时时间（秒）",
    show_default=True,
)
def metrics(url: str, timeout: int) -> None:
    """获取 API 网关指标"""
    try:
        with console.status("[bold green]获取指标数据..."):
            response = httpx.get(f"{url}/metrics", timeout=timeout)
            
        if response.status_code == 200:
            data = response.json()
            _show_metrics(data)
        else:
            console.print(f"[red]指标获取失败: HTTP {response.status_code}[/red]")
            sys.exit(1)
            
    except httpx.TimeoutException:
        console.print(f"[red]指标获取超时: {timeout}秒[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]指标获取失败: {e}[/red]")
        sys.exit(1)


def _show_startup_info(host: str, port: int, workers: int, reload: bool) -> None:
    """显示启动信息"""
    table = Table(title="🚀 索克生活 API 网关启动信息")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("监听地址", f"{host}:{port}")
    table.add_row("工作进程", str(workers))
    table.add_row("自动重载", "是" if reload else "否")
    table.add_row("模式", "开发" if reload else "生产")
    
    console.print(table)
    console.print(f"\n🌐 访问地址: [link]http://{host}:{port}[/link]")
    console.print(f"📚 API 文档: [link]http://{host}:{port}/docs[/link]")
    console.print(f"❤️  健康检查: [link]http://{host}:{port}/health[/link]")
    console.print(f"📊 指标监控: [link]http://{host}:{port}/metrics[/link]")


def _show_dev_info(host: str, port: int) -> None:
    """显示开发模式信息"""
    console.print("[bold yellow]🔧 开发模式启动[/bold yellow]")
    console.print(f"🌐 访问地址: [link]http://{host}:{port}[/link]")
    console.print(f"📚 API 文档: [link]http://{host}:{port}/docs[/link]")
    console.print(f"🔄 自动重载: 已启用")
    console.print(f"📝 日志级别: DEBUG")


def _show_health_status(data: dict) -> None:
    """显示健康状态"""
    status = data.get("status", "unknown")
    timestamp = data.get("timestamp", "")
    
    if status == "healthy":
        console.print(f"[green]✅ 系统健康 ({timestamp})[/green]")
    else:
        console.print(f"[red]❌ 系统异常 ({timestamp})[/red]")
    
    # 显示服务状态
    services = data.get("services", {})
    if services:
        table = Table(title="服务状态")
        table.add_column("服务名", style="cyan")
        table.add_column("状态", style="green")
        table.add_column("健康端点", style="yellow")
        table.add_column("总端点", style="blue")
        
        for service_name, service_data in services.items():
            service_status = service_data.get("status", "unknown")
            healthy_count = service_data.get("healthy_endpoints", 0)
            total_count = service_data.get("total_endpoints", 0)
            
            status_icon = "✅" if service_status == "healthy" else "❌"
            table.add_row(
                service_name,
                f"{status_icon} {service_status}",
                str(healthy_count),
                str(total_count),
            )
        
        console.print(table)


def _show_metrics(data: dict) -> None:
    """显示指标信息"""
    table = Table(title="📊 系统指标")
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")
    
    # 基础指标
    if "total_requests" in data:
        table.add_row("总请求数", str(data["total_requests"]))
    if "success_rate" in data:
        rate = data["success_rate"] * 100
        table.add_row("成功率", f"{rate:.2f}%")
    if "average_response_time" in data:
        table.add_row("平均响应时间", f"{data['average_response_time']:.3f}s")
    if "requests_per_second" in data:
        table.add_row("每秒请求数", f"{data['requests_per_second']:.2f}")
    
    # 系统指标
    system = data.get("system", {})
    if system:
        if "cpu_percent" in system:
            table.add_row("CPU 使用率", f"{system['cpu_percent']:.1f}%")
        if "memory_percent" in system:
            table.add_row("内存使用率", f"{system['memory_percent']:.1f}%")
        if "disk_percent" in system:
            table.add_row("磁盘使用率", f"{system['disk_percent']:.1f}%")
    
    console.print(table)


def main() -> None:
    """主函数"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断操作[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]程序异常: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
