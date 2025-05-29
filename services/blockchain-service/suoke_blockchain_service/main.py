"""
主应用入口

区块链服务的主要入口点, 负责应用的创建和启动。
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
import typer
import uvicorn

from .config import settings
from .database import close_database, init_database
from .grpc_server import GRPCServer
from .logging import configure_logging, get_logger
from .monitoring import setup_monitoring

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = get_logger(__name__)

# 创建 Typer 应用
cli = typer.Typer(
    name="blockchain-service",
    help="索克生活区块链服务",
    add_completion=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("启动区块链服务")

    # 初始化数据库
    await init_database()

    # 设置监控
    setup_monitoring(app)

    logger.info("区块链服务启动完成")

    yield

    # 关闭时清理
    logger.info("关闭区块链服务")
    await close_database()
    logger.info("区块链服务已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.app_name,
        description="索克生活区块链服务 - 健康数据的区块链存储、验证和访问控制",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """健康检查端点"""
        return {"status": "healthy", "service": "blockchain-service"}

    @app.get("/")
    async def root() -> dict[str, str]:
        """根端点"""
        return {
            "service": "SuoKe Blockchain Service",
            "version": "0.1.0",
            "status": "running"
        }

    return app


@cli.command()
def serve(
    host: str = typer.Option(
        settings.grpc.host,
        "--host",
        help="gRPC 服务器主机地址",
    ),
    port: int = typer.Option(
        settings.grpc.port,
        "--port",
        help="gRPC 服务器端口",
    ),
    http_port: int = typer.Option(
        8080,
        "--http-port",
        help="HTTP 服务器端口",
    ),
    workers: int = typer.Option(
        1,
        "--workers",
        help="工作进程数量",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="启用自动重载(开发模式)",
    ),
) -> None:
    """启动区块链服务"""
    # 配置日志
    configure_logging()

    logger.info(
        "启动区块链服务",
        host=host,
        grpc_port=port,
        http_port=http_port,
        workers=workers,
        reload=reload,
    )

    # 创建 FastAPI 应用(用于健康检查等)
    app = create_app()

    # 启动 HTTP 服务器(用于健康检查)
    uvicorn.run(
        app,
        host=host,
        port=http_port,
        workers=workers,
        reload=reload,
        log_config=None,  # 使用我们自己的日志配置
    )


@cli.command()
def grpc_serve(
    host: str = typer.Option(
        settings.grpc.host,
        "--host",
        help="gRPC 服务器主机地址",
    ),
    port: int = typer.Option(
        settings.grpc.port,
        "--port",
        help="gRPC 服务器端口",
    ),
) -> None:
    """启动 gRPC 服务器"""
    # 配置日志
    configure_logging()

    logger.info("启动 gRPC 服务器", host=host, port=port)

    async def run_grpc_server() -> None:
        """运行 gRPC 服务器"""
        # 初始化数据库
        await init_database()

        # 创建并启动 gRPC 服务器
        server = GRPCServer()
        await server.start(host, port)

        try:
            # 保持服务器运行
            await server.wait_for_termination()
        finally:
            # 清理资源
            await server.stop()
            await close_database()

    # 运行异步服务器
    asyncio.run(run_grpc_server())


def main() -> None:
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main()
