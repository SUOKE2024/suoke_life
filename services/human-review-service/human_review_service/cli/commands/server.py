"""
server - 索克生活项目模块
"""

from ...core.config import settings
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from typing import Optional
import click
import os
import psutil
import structlog
import sys
import time
import uvicorn

"""
服务器管理命令
Server Management Commands

提供服务器的启动、停止、重启等管理功能
"""




logger = structlog.get_logger(__name__)
console = Console()

# PID文件路径
PID_FILE = Path("/tmp/human_review_service.pid")

@click.group()
def server():
    """服务器管理命令"""
    pass

@server.command()
@click.option("--host", default="0.0.0.0", help="服务器主机地址")
@click.option("--port", default=8000, type=int, help="服务器端口")
@click.option("--workers", default=1, type=int, help="工作进程数量")
@click.option("--daemon", "-d", is_flag=True, help="以守护进程模式运行")
@click.option("--log-file", type=click.Path(), help="日志文件路径（守护进程模式）")
def start(host: str, port: int, workers: int, daemon: bool, log_file: str):
    """启动服务器"""
    if daemon:
        start_daemon(host, port, workers, log_file)
    else:
        start_foreground(host, port, workers)

def start_foreground(host: str, port: int, workers: int):
    """前台启动服务器"""
    console.print(f"[bold blue]启动人工审核微服务...[/bold blue]")
    console.print(f"主机: {host}")
    console.print(f"端口: {port}")
    console.print(f"工作进程: {workers}")

    try:
        uvicorn.run(
            "human_review_service.api.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level="info" if not settings.debug else "debug",
            access_log=True,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]服务已停止[/yellow]")
    except Exception as e:
        console.print(f"[red]启动失败: {e}[/red]")
        sys.exit(1)

def start_daemon(host: str, port: int, workers: int, log_file: Optional[str]):
    """守护进程模式启动服务器"""
    if is_running():
        console.print("[yellow]服务已在运行中[/yellow]")
        return

    console.print(f"[bold blue]以守护进程模式启动服务器...[/bold blue]")

    # 创建子进程
    pid = os.fork()
    if pid > 0:
        # 父进程：保存PID并退出
        save_pid(pid)
        console.print(f"[green]✅ 服务已启动，PID: {pid}[/green]")
        return

    # 子进程：启动服务器
    try:
        # 重定向标准输出和错误输出
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, "a") as f:
                os.dup2(f.fileno(), sys.stdout.fileno())
                os.dup2(f.fileno(), sys.stderr.fileno())

        # 启动服务器
        uvicorn.run(
            "human_review_service.api.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level="info",
            access_log=True,
        )
    except Exception as e:
        logger.error("Daemon startup failed", error=str(e))
        sys.exit(1)

@server.command()
@click.option("--force", "-f", is_flag=True, help="强制停止")
def stop(force: bool):
    """停止服务器"""
    console.print("[bold blue]停止服务器...[/bold blue]")

    if not is_running():
        console.print("[yellow]服务未运行[/yellow]")
        return

    pid = get_pid()
    if not pid:
        console.print("[red]无法获取服务PID[/red]")
        return

    try:
        process = psutil.Process(pid)

        if force:
            # 强制终止
            process.kill()
            console.print(f"[green]✅ 服务已强制停止（PID: {pid}）[/green]")
        else:
            # 优雅停止
            process.terminate()

            # 等待进程结束
            try:
                process.wait(timeout=30)
                console.print(f"[green]✅ 服务已停止（PID: {pid}）[/green]")
            except psutil.TimeoutExpired:
                console.print("[yellow]优雅停止超时，强制终止...[/yellow]")
                process.kill()
                console.print(f"[green]✅ 服务已强制停止（PID: {pid}）[/green]")

        # 清理PID文件
        remove_pid()

    except psutil.NoSuchProcess:
        console.print("[yellow]进程不存在，清理PID文件[/yellow]")
        remove_pid()
    except Exception as e:
        console.print(f"[red]停止服务失败: {e}[/red]")
        sys.exit(1)

@server.command()
def restart():
    """重启服务器"""
    console.print("[bold blue]重启服务器...[/bold blue]")

    # 先停止服务
    if is_running():
        stop.callback(force=False)
        time.sleep(2)

    # 重新启动
    start.callback(host="0.0.0.0", port=8000, workers=1, daemon=True, log_file=None)

@server.command()
def status():
    """查看服务器状态"""
    console.print("[bold blue]服务器状态[/bold blue]")

    if not is_running():
        console.print("[red]❌ 服务未运行[/red]")
        return

    pid = get_pid()
    if not pid:
        console.print("[red]❌ 无法获取服务PID[/red]")
        return

    try:
        process = psutil.Process(pid)

        # 创建状态表格
        table = Table(title="服务状态")
        table.add_column("属性", style="cyan")
        table.add_column("值", style="green")

        table.add_row("状态", "✅ 运行中")
        table.add_row("PID", str(pid))
        table.add_row(
            "启动时间",
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(process.create_time())),
        )
        table.add_row("运行时长", format_duration(time.time() - process.create_time()))
        table.add_row("CPU使用率", f"{process.cpu_percent():.1f}%")
        table.add_row("内存使用", f"{process.memory_info().rss / 1024 / 1024:.1f} MB")
        table.add_row("线程数", str(process.num_threads()))

        console.print(table)

    except psutil.NoSuchProcess:
        console.print("[red]❌ 进程不存在[/red]")
        remove_pid()
    except Exception as e:
        console.print(f"[red]获取状态失败: {e}[/red]")

@server.command()
@click.option("--interval", default=5, type=int, help="刷新间隔（秒）")
def monitor(interval: int):
    """监控服务器状态"""
    console.print(f"[bold blue]监控服务器状态（每{interval}秒刷新）[/bold blue]")
    console.print("按 Ctrl+C 退出监控")

    def generate_table():
        if not is_running():
            table = Table(title="服务状态")
            table.add_column("状态", style="red")
            table.add_row("❌ 服务未运行")
            return table

        pid = get_pid()
        if not pid:
            table = Table(title="服务状态")
            table.add_column("状态", style="red")
            table.add_row("❌ 无法获取PID")
            return table

        try:
            process = psutil.Process(pid)

            table = Table(title=f"服务监控 - {time.strftime('%H:%M:%S')}")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")

            table.add_row("状态", "✅ 运行中")
            table.add_row("PID", str(pid))
            table.add_row(
                "运行时长", format_duration(time.time() - process.create_time())
            )
            table.add_row("CPU使用率", f"{process.cpu_percent():.1f}%")
            table.add_row(
                "内存使用", f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
            )
            table.add_row("线程数", str(process.num_threads()))

            # 网络连接
            connections = len(process.connections())
            table.add_row("网络连接", str(connections))

            return table

        except psutil.NoSuchProcess:
            table = Table(title="服务状态")
            table.add_column("状态", style="red")
            table.add_row("❌ 进程不存在")
            return table

    try:
        with Live(generate_table(), refresh_per_second=1 / interval) as live:
            while True:
                time.sleep(interval)
                live.update(generate_table())
    except KeyboardInterrupt:
        console.print("\n[yellow]监控已停止[/yellow]")

@server.command()
def logs():
    """查看服务日志"""
    console.print("[bold blue]服务日志[/bold blue]")

    # 这里应该实现日志查看功能
    # 可以集成tail -f 或者读取日志文件
    console.print("[yellow]⚠️ 日志查看功能需要根据具体日志配置实现[/yellow]")

# 辅助函数

def is_running() -> bool:
    """检查服务是否运行"""
    if not PID_FILE.exists():
        return False

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        return psutil.pid_exists(pid)
    except (ValueError, FileNotFoundError):
        return False

def get_pid() -> Optional[int]:
    """获取服务PID"""
    if not PID_FILE.exists():
        return None

    try:
        with open(PID_FILE, "r") as f:
            return int(f.read().strip())
    except (ValueError, FileNotFoundError):
        return None

def save_pid(pid: int):
    """保存PID到文件"""
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(pid))
    except Exception as e:
        logger.error("Failed to save PID", error=str(e))

def remove_pid():
    """删除PID文件"""
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception as e:
        logger.error("Failed to remove PID file", error=str(e))

def format_duration(seconds: float) -> str:
    """格式化时间间隔"""
    seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if days > 0:
        return f"{days}天 {hours}小时 {minutes}分钟"
    elif hours > 0:
        return f"{hours}小时 {minutes}分钟"
    else:
        return f"{minutes}分钟 {seconds}秒"
