#!/usr/bin/env python3
"""
索克生活触诊服务 CLI 工具

提供开发、测试、部署等命令行功能。
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn
from rich.console import Console
from rich.table import Table

from .config import get_settings
from .main import PalpationService


console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """索克生活触诊服务 CLI 工具"""
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
    help="服务器端口",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="启用自动重载（开发模式）",
)
@click.option(
    "--workers",
    default=1,
    help="工作进程数量",
    show_default=True,
)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    help="日志级别",
    show_default=True,
)
def serve(
    host: str,
    port: int,
    reload: bool,
    workers: int,
    log_level: str,
) -> None:
    """启动触诊服务"""
    console.print("[bold green]启动索克生活触诊服务...[/bold green]")
    
    # 显示配置信息
    table = Table(title="服务配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="magenta")
    
    table.add_row("主机地址", host)
    table.add_row("端口", str(port))
    table.add_row("重载模式", "是" if reload else "否")
    table.add_row("工作进程", str(workers))
    table.add_row("日志级别", log_level)
    
    console.print(table)
    
    try:
        uvicorn.run(
            "palpation_service.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level=log_level,
            access_log=True,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]服务已停止[/yellow]")
    except Exception as e:
        console.print(f"[red]服务启动失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--config-dir",
    default="config",
    help="配置文件目录",
    show_default=True,
)
def check_config(config_dir: str) -> None:
    """检查配置文件"""
    console.print("[bold blue]检查配置文件...[/bold blue]")
    
    config_path = Path(config_dir)
    if not config_path.exists():
        console.print(f"[red]配置目录不存在: {config_path}[/red]")
        sys.exit(1)
    
    # 检查必需的配置文件
    required_files = [
        "palpation.yaml",
        "devices.yaml",
        "config.yaml",
    ]
    
    table = Table(title="配置文件检查")
    table.add_column("文件", style="cyan")
    table.add_column("状态", style="magenta")
    
    all_ok = True
    for file_name in required_files:
        file_path = config_path / file_name
        if file_path.exists():
            table.add_row(file_name, "[green]✓ 存在[/green]")
        else:
            table.add_row(file_name, "[red]✗ 缺失[/red]")
            all_ok = False
    
    console.print(table)
    
    if all_ok:
        console.print("[green]所有配置文件检查通过[/green]")
    else:
        console.print("[red]配置文件检查失败[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="输出格式",
    show_default=True,
)
def health(output_format: str) -> None:
    """检查服务健康状态"""
    console.print("[bold blue]检查服务健康状态...[/bold blue]")
    
    async def check_health():
        try:
            service = PalpationService()
            await service.initialize()
            
            # 检查各组件状态
            components = {
                "配置管理器": service.config_manager is not None,
                "缓存管理器": service.cache_manager is not None,
                "融合引擎": service.fusion_engine is not None,
                "预测分析器": service.predictive_analyzer is not None,
                "可视化器": service.visualizer is not None,
                "报告生成器": service.report_generator is not None,
                "智能协调器": service.coordinator is not None,
                "监控仪表板": service.dashboard is not None,
            }
            
            if output_format == "table":
                table = Table(title="组件健康状态")
                table.add_column("组件", style="cyan")
                table.add_column("状态", style="magenta")
                
                for component, status in components.items():
                    status_text = "[green]✓ 正常[/green]" if status else "[red]✗ 异常[/red]"
                    table.add_row(component, status_text)
                
                console.print(table)
            else:
                import json
                result = {
                    "status": "healthy" if all(components.values()) else "unhealthy",
                    "components": {k: "ok" if v else "error" for k, v in components.items()},
                }
                console.print(json.dumps(result, indent=2, ensure_ascii=False))
            
            await service.shutdown()
            
        except Exception as e:
            console.print(f"[red]健康检查失败: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(check_health())


@cli.command()
@click.option(
    "--test-type",
    default="unit",
    type=click.Choice(["unit", "integration", "e2e", "all"]),
    help="测试类型",
    show_default=True,
)
@click.option(
    "--coverage",
    is_flag=True,
    help="生成覆盖率报告",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="详细输出",
)
def test(test_type: str, coverage: bool, verbose: bool) -> None:
    """运行测试"""
    import subprocess
    
    console.print(f"[bold blue]运行 {test_type} 测试...[/bold blue]")
    
    cmd = ["python", "-m", "pytest"]
    
    if test_type != "all":
        cmd.extend(["-m", test_type])
    
    if coverage:
        cmd.extend(["--cov=palpation_service", "--cov-report=html", "--cov-report=term"])
    
    if verbose:
        cmd.append("-v")
    
    try:
        result = subprocess.run(cmd, check=True)
        console.print("[green]测试完成[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]测试失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--check-only",
    is_flag=True,
    help="仅检查，不修复",
)
def lint(check_only: bool) -> None:
    """代码检查和格式化"""
    import subprocess
    
    console.print("[bold blue]运行代码检查...[/bold blue]")
    
    commands = [
        (["ruff", "check", "."], "Ruff 检查"),
        (["ruff", "format", "." if not check_only else "--check", "."], "Ruff 格式化"),
        (["mypy", "palpation_service"], "MyPy 类型检查"),
    ]
    
    if not check_only:
        commands.insert(1, (["ruff", "check", "--fix", "."], "Ruff 自动修复"))
    
    for cmd, description in commands:
        console.print(f"[cyan]{description}...[/cyan]")
        try:
            subprocess.run(cmd, check=True)
            console.print(f"[green]✓ {description} 完成[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗ {description} 失败: {e}[/red]")


@cli.command()
def docs() -> None:
    """生成文档"""
    import subprocess
    
    console.print("[bold blue]生成文档...[/bold blue]")
    
    try:
        subprocess.run(["mkdocs", "build"], check=True)
        console.print("[green]文档生成完成[/green]")
        console.print("文档位置: site/index.html")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]文档生成失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--port",
    default=8001,
    help="文档服务器端口",
    show_default=True,
)
def docs_serve(port: int) -> None:
    """启动文档服务器"""
    import subprocess
    
    console.print(f"[bold blue]启动文档服务器 (端口: {port})...[/bold blue]")
    
    try:
        subprocess.run(["mkdocs", "serve", "--dev-addr", f"0.0.0.0:{port}"], check=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]文档服务器已停止[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]文档服务器启动失败: {e}[/red]")
        sys.exit(1)


def dev_main() -> None:
    """开发环境主入口"""
    cli()


if __name__ == "__main__":
    cli() 