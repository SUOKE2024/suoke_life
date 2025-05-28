"""
主应用入口

区块链服务的主要入口点，负责应用的创建和启动。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import typer
import uvicorn

from .config import settings
from .database import close_database, init_database
from .grpc_server import GRPCServer
from .logging import configure_logging, logger
from .monitoring import setup_monitoring


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理"""
    logger.info("启动区块链服务", version=settings.app_version)

    # 初始化数据库
    await init_database()

    # 设置监控
    setup_monitoring(app)

    # 启动 gRPC 服务器
    grpc_server = GRPCServer()
    await grpc_server.start()

    logger.info("区块链服务启动完成")

    yield

    # 清理资源
    logger.info("正在关闭区块链服务")
    await grpc_server.stop()
    await close_database()
    logger.info("区块链服务已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    # 配置日志
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="索克生活区块链服务 - 健康数据的区块链存储、验证和访问控制",
        lifespan=lifespan,
        debug=settings.debug,
    )

    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

    # 就绪检查端点
    @app.get("/ready")
    async def readiness_check():
        """就绪检查端点"""
        # TODO: 检查数据库连接、区块链连接等
        return {
            "status": "ready",
            "service": settings.app_name,
            "version": settings.app_version,
        }

    return app


# CLI 应用
cli_app = typer.Typer(
    name="blockchain-service",
    help="索克生活区块链服务命令行工具",
)


@cli_app.command()
def serve(
    host: str = typer.Option(
        settings.grpc.host,
        "--host",
        "-h",
        help="服务主机地址",
    ),
    port: int = typer.Option(
        settings.grpc.port,
        "--port",
        "-p",
        help="服务端口",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="启用自动重载（开发模式）",
    ),
) -> None:
    """启动区块链服务"""

    configure_logging()
    logger.info(
        "启动区块链服务",
        host=host,
        port=port,
        environment=settings.environment,
    )

    # 创建 FastAPI 应用（用于健康检查等）
    app = create_app()

    # 启动 HTTP 服务器（用于健康检查）
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=reload and settings.is_development,
        log_config=None,  # 使用我们自己的日志配置
    )


@cli_app.command()
def deploy_contracts() -> None:
    """部署智能合约"""
    from .blockchain.deployer import ContractDeployer

    configure_logging()
    logger.info("开始部署智能合约")

    deployer = ContractDeployer()
    asyncio.run(deployer.deploy_all())

    logger.info("智能合约部署完成")


@cli_app.command()
def migrate_db() -> None:
    """运行数据库迁移"""
    from alembic import command
    from alembic.config import Config

    configure_logging()
    logger.info("开始数据库迁移")

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    logger.info("数据库迁移完成")


def main() -> None:
    """主入口点"""
    cli_app()


if __name__ == "__main__":
    main()
