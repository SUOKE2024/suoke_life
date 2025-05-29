"""服务器启动命令"""

import signal
import sys
from typing import Any

import click
import uvicorn
from loguru import logger

from health_data_service.core.config import settings


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """健康数据服务命令行工具"""
    pass


@cli.command()
@click.option(
    "--host",
    default=settings.api.host,
    help="服务器主机地址",
    show_default=True,
)
@click.option(
    "--port",
    default=settings.api.port,
    help="服务器端口",
    show_default=True,
)
@click.option(
    "--workers",
    default=settings.api.workers,
    help="工作进程数",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    default=settings.debug,
    help="启用自动重载",
)
@click.option(
    "--log-level",
    default=settings.logging.level.lower(),
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    help="日志级别",
    show_default=True,
)
def serve(
    host: str,
    port: int,
    workers: int,
    reload: bool,
    log_level: str,
) -> None:
    """启动HTTP服务器"""
    logger.info(f"启动健康数据服务 - {host}:{port}")
    logger.info(f"环境: {settings.environment}")
    logger.info(f"调试模式: {settings.debug}")
    logger.info(f"工作进程数: {workers}")

    # 配置uvicorn
    config = uvicorn.Config(
        app="health_data_service.api.main:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        reload=reload,
        log_level=log_level,
        access_log=True,
        use_colors=True,
    )

    server = uvicorn.Server(config)

    # 优雅关闭处理
    def signal_handler(signum: int, frame: Any) -> None:
        logger.info(f"接收到信号 {signum}，正在关闭服务器...")
        server.should_exit = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--host",
    default=settings.api.host,
    help="gRPC服务器主机地址",
    show_default=True,
)
@click.option(
    "--port",
    default=50051,
    help="gRPC服务器端口",
    show_default=True,
)
def grpc_serve(host: str, port: int) -> None:
    """启动gRPC服务器"""
    logger.info(f"启动gRPC服务器 - {host}:{port}")

    # TODO: 实现gRPC服务器
    logger.warning("gRPC服务器尚未实现")


@cli.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="配置文件路径",
)
def check_config(config_file: str | None) -> None:
    """检查配置"""
    logger.info("检查配置...")

    try:
        # 验证配置
        logger.info(f"环境: {settings.environment}")
        logger.info(f"数据库URL: {settings.database.url}")
        logger.info(f"Redis URL: {settings.redis.url}")
        logger.info(f"API配置: {settings.api.title} v{settings.api.version}")

        logger.success("配置检查通过")
    except Exception as e:
        logger.error(f"配置检查失败: {e}")
        sys.exit(1)


@cli.command()
def health() -> None:
    """健康检查"""
    logger.info("执行健康检查...")

    try:
        # TODO: 实现健康检查逻辑
        # - 数据库连接检查
        # - Redis连接检查
        # - 外部服务检查

        logger.success("健康检查通过")
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    type=click.Path(),
    default="openapi.json",
    help="输出文件路径",
    show_default=True,
)
def export_openapi(output: str) -> None:
    """导出OpenAPI规范"""
    logger.info(f"导出OpenAPI规范到 {output}")

    try:
        import json

        from health_data_service.api.main import app

        openapi_schema = app.openapi()

        with open(output, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

        logger.success(f"OpenAPI规范已导出到 {output}")
    except Exception as e:
        logger.error(f"导出失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
