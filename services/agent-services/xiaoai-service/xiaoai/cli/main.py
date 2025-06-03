#!/usr/bin/env python3

"""
小艾智能体主命令行接口
XiaoAI Agent Main CLI

提供小艾智能体的主要命令行功能。
"""

import sys

import click
from loguru import logger

from xiaoai import __version__

@click.group()
@click.version_option(version=_version__, prog_name="xiaoai")
@click.option(
    "--verbose", "-v",
    count=True,
    help="增加输出详细程度 (可重复使用: -v, -vv, -vvv)"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="配置文件路径"
)
@click.pass_context
def cli(ctx: click.Context, verbose: int, config: str | None) -> None:
    """
    小艾智能体命令行工具

    小艾是索克生活平台的核心AI智能体, 专注于提供智能健康管理服务。
    """
    # 确保上下文对象存在
    ctx.ensure_object(dict)

    # 设置日志级别
    loglevels = ["ERROR", "WARNING", "INFO", "DEBUG"]
    loglevel = log_levels[min(verbose, len(loglevels) - 1)]

    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stderr,
        level=loglevel,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )

    # 存储配置到上下文
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose

    logger.info(f"小艾智能体 v{__version__} 启动")

@cli.command()
@click.option(
    "--host", "-h",
    default="0.0.0.0",
    help="服务器绑定地址 (默认: 0.0.0.0)"
)
@click.option(
    "--port", "-p",
    default=8000,
    type=int,
    help="服务器端口 (默认: 8000)"
)
@click.option(
    "--workers", "-w",
    default=1,
    type=int,
    help="工作进程数量 (默认: 1)"
)
@click.option(
    "--reload",
    is_flag=True,
    help="启用自动重载 (开发模式)"
)
@click.pass_context
def server(
    ctx: click.Context,
    host: str,
    port: int,
    workers: int,
    reload: bool
) -> None:
    """启动小艾智能体服务器"""
    from .server import run_server

    logger.info(f"启动服务器: {host}:{port}")
    logger.info(f"工作进程数: {workers}")

    run_server(
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        config=ctx.obj.get("config")
    )

@cli.command()
@click.option(
    "--concurrency", "-c",
    default=4,
    type=int,
    help="并发工作数量 (默认: 4)"
)
@click.option(
    "--queue", "-q",
    default="default",
    help="队列名称 (默认: default)"
)
@click.pass_context
def worker(
    ctx: click.Context,
    concurrency: int,
    queue: str
) -> None:
    """启动小艾智能体工作进程"""
    from .worker import run_worker

    logger.info(f"启动工作进程: 并发数={concurrency}, 队列={queue}")

    run_worker(
        concurrency=concurrency,
        queue=queue,
        config=ctx.obj.get("config")
    )

@cli.command()
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "yaml", "table"]),
    default="table",
    help="输出格式 (默认: table)"
)
def status(format: str) -> None:
    """检查小艾智能体状态"""
    from .status import check_status

    logger.info("检查服务状态...")
    check_status(format=format)

@cli.command()
@click.option(
    "--target", "-t",
    type=click.Choice(["config", "database", "cache", "all"]),
    default="all",
    help="初始化目标 (默认: all)"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="强制重新初始化"
)
def init(target: str, force: bool) -> None:
    """初始化小艾智能体"""
    from .init import initialize

    logger.info(f"初始化 {target}...")
    initialize(target=target, force=force)

@cli.command()
@click.option(
    "--check-only",
    is_flag=True,
    help="仅检查健康状态, 不输出详细信息"
)
def health(checkonly: bool) -> None:
    """健康检查"""
    from .health import health_check

    result = health_check()

    if check_only:
        sys.exit(0 if result["healthy"] else 1)

    if result["healthy"]:
        click.echo(click.style("✓ 小艾智能体运行正常", fg="green"))
    else:
        click.echo(click.style("✗ 小艾智能体存在问题", fg="red"))
        for issue in result.get("issues", []):
            click.echo(click.style(f"  - {issue}", fg="red"))
        sys.exit(1)

def main() -> None:
    """主入口点"""
    try:
        cli()
    except KeyboardInterrupt:
        logger.info("收到中断信号, 正在退出...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
