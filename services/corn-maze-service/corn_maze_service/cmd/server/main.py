"""
Corn Maze Service 主入口

启动 gRPC 和 HTTP 服务器。
"""

import asyncio
from collections.abc import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import signal
import sys
from typing import Any

from fastapi import FastAPI
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection
import uvicorn

from corn_maze_service.config import get_settings
from corn_maze_service.internal.delivery.http import create_app
from corn_maze_service.pkg.logging import get_logger, setup_logging

logger = get_logger(__name__)

class GracefulShutdown:
    """优雅关闭处理器"""

    def __init__(self) -> None:
        self.shutdown = False
        self.tasks: list[asyncio.Task[Any]] = []

    def signal_handler(self, signum: int, _frame: Any) -> None:
        """信号处理器"""
        logger.info("Received shutdown signal", signal=signum)
        self.shutdown = True

        # 取消所有任务
        for task in self.tasks:
            if not task.done():
                task.cancel()

    def add_task(self, task: asyncio.Task[Any]) -> None:
        """添加任务"""
        self.tasks.append(task)

async def create_grpc_server() -> grpc_aio.Server:
    """创建 gRPC 服务器"""
    settings = get_settings()

    server = grpc_aio.server(
        ThreadPoolExecutor(max_workers=settings.grpc.max_workers),
        options=[
            ("grpc.max_receive_message_length", settings.grpc.max_receive_message_length),
            ("grpc.max_send_message_length", settings.grpc.max_send_message_length),
        ]
    )

    # 注册服务
    # TODO: 当 protobuf 文件生成后，取消注释以下代码
    # corn_maze_servicer = CornMazeServicer()
    # corn_maze_pb2_grpc.add_CornMazeServiceServicer_to_server(corn_maze_servicer, server)

    # 健康检查
    if settings.grpc.enable_health_check:
        health_servicer = health_pb2_grpc.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    # gRPC 反射
    if settings.grpc.enable_reflection:
        service_names = [
            # "corn_maze.v1.CornMazeService",
            reflection.SERVICE_NAME,
        ]
        if settings.grpc.enable_health_check:
            service_names.append("grpc.health.v1.Health")

        reflection.enable_server_reflection(service_names, server)

    # 监听端口
    listen_addr = f"{settings.grpc.host}:{settings.grpc.port}"
    server.add_insecure_port(listen_addr)

    logger.info("gRPC server configured", address=listen_addr)
    return server

async def start_grpc_server(server: grpc_aio.Server) -> None:
    """启动 gRPC 服务器"""
    settings = get_settings()

    await server.start()
    logger.info("gRPC server started", port=settings.grpc.port)

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("gRPC server shutdown requested")
        await server.stop(grace=5.0)
        logger.info("gRPC server stopped")

async def start_http_server() -> None:
    """启动 HTTP 服务器"""
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        """应用生命周期管理"""
        logger.info("HTTP server starting")
        yield
        logger.info("HTTP server shutting down")

    app = create_app(lifespan=lifespan)

    config = uvicorn.Config(
        app,
        host=settings.http.host,
        port=settings.http.port,
        reload=settings.http.reload and settings.is_development(),
        workers=settings.http.workers if not settings.is_development() else 1,
        access_log=settings.http.access_log,
        log_config=None,  # 使用我们自己的日志配置
    )

    server = uvicorn.Server(config)

    try:
        await server.serve()
    except asyncio.CancelledError:
        logger.info("HTTP server shutdown requested")
        await server.shutdown()
        logger.info("HTTP server stopped")

async def start_monitoring_server() -> None:
    """启动监控服务器"""
    settings = get_settings()

    if not settings.monitoring.enable_prometheus:
        return

    from prometheus_client import start_http_server

    try:
        start_http_server(settings.monitoring.prometheus_port)
        logger.info("Prometheus metrics server started", port=settings.monitoring.prometheus_port)

        # 保持运行直到被取消
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Monitoring server stopped")

async def main() -> None:
    """主函数"""
    # 设置日志
    setup_logging()
    logger.info("Starting Corn Maze Service")

    settings = get_settings()
    logger.info("Configuration loaded", environment=settings.environment)

    # 优雅关闭处理
    shutdown_handler = GracefulShutdown()
    signal.signal(signal.SIGINT, shutdown_handler.signal_handler)
    signal.signal(signal.SIGTERM, shutdown_handler.signal_handler)

    try:
        # 创建 gRPC 服务器
        grpc_server = await create_grpc_server()

        # 启动所有服务
        tasks: list[asyncio.Task[Any]] = [
            asyncio.create_task(start_grpc_server(grpc_server)),
            asyncio.create_task(start_http_server()),
            asyncio.create_task(start_monitoring_server()),
        ]

        # 添加任务到关闭处理器
        for task in tasks:
            shutdown_handler.add_task(task)

        logger.info("All services started successfully")

        # 等待所有任务完成或被取消
        await asyncio.gather(*tasks, return_exceptions=True)

    except Exception as e:
        logger.error("Failed to start services", error=str(e), exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Corn Maze Service stopped")

def run() -> None:
    """运行服务器"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error("Service failed", error=str(e), exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run()
