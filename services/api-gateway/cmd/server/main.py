#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索克生活API网关服务入口文件
提供REST和gRPC双模式API网关服务
"""

# Monkey patch asyncio.coroutine以兼容Python 3.13
import asyncio
if not hasattr(asyncio, 'coroutine'):
    def coroutine(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    asyncio.coroutine = coroutine

import logging
import os
import signal
import sys
from concurrent import futures
from logging.handlers import RotatingFileHandler
from typing import Optional

import grpc
import uvicorn
import yaml
from fastapi import FastAPI
from structlog import configure, processors, stdlib

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from internal.delivery.rest.middleware import setup_middlewares
from internal.delivery.rest.routes import setup_routes
from internal.delivery.grpc.service import register_servicer
from internal.model.config import GatewayConfig
from internal.service.service_registry import ServiceRegistry
from pkg.utils.config import load_config


# 配置结构化日志
def configure_logging(log_file: Optional[str] = None) -> None:
    """配置结构化日志"""
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    
    handlers = [logging.StreamHandler()]
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5, encoding="utf-8"
        ))
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(message)s",
        handlers=handlers,
    )
    
    configure(
        processors=[
            stdlib.filter_by_level,
            stdlib.add_logger_name,
            stdlib.add_log_level,
            stdlib.PositionalArgumentsFormatter(),
            processors.TimeStamper(fmt="iso"),
            processors.StackInfoRenderer(),
            processors.format_exc_info,
            processors.UnicodeDecoder(),
            stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=stdlib.LoggerFactory(),
        wrapper_class=stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# 创建FastAPI应用
def create_app(config: GatewayConfig) -> FastAPI:
    """创建并配置FastAPI应用"""
    app = FastAPI(
        title="索克生活API网关",
        description="索克生活平台统一API入口",
        version="0.1.0",
        docs_url="/docs" if not config.server.production else None,
        redoc_url="/redoc" if not config.server.production else None,
    )
    
    # 设置中间件
    setup_middlewares(app, config)
    
    # 注册路由
    setup_routes(app, config)
    
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        return {"status": "ok"}
    
    return app


# 启动REST服务器
async def start_rest_server(config: GatewayConfig, service_registry: ServiceRegistry) -> None:
    """启动REST API服务器"""
    app = create_app(config)
    
    # 将服务注册表添加到应用状态中
    app.state.registry = service_registry
    
    config_dict = {
        "host": config.server.rest.host,
        "port": config.server.rest.port,
        "log_level": "info",
        "reload": not config.server.production,
        "access_log": not config.server.production,
    }
    
    server = uvicorn.Server(uvicorn.Config(app, **config_dict))
    await server.serve()


# 启动gRPC服务器
async def start_grpc_server(config: GatewayConfig, service_registry: ServiceRegistry) -> None:
    """启动gRPC服务器"""
    logger = logging.getLogger(__name__)
    
    # 创建gRPC服务器
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
        ]
    )
    
    # 注册gRPC服务
    servicer = register_servicer(server, service_registry, config)
    
    # 添加服务反射，便于客户端发现服务
    try:
        from grpc_reflection.v1alpha import reflection
        from api.grpc.api_gateway_pb2 import DESCRIPTOR
        
        SERVICE_NAMES = (
            DESCRIPTOR.services_by_name['ApiGateway'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
        logger.info("gRPC服务反射已启用")
    except ImportError:
        logger.warning("grpc_reflection模块未安装，服务反射未启用")
    
    # 绑定地址
    address = f"{config.server.grpc.host}:{config.server.grpc.port}"
    server.add_insecure_port(address)
    
    # 启动服务器
    await server.start()
    logger.info(f"gRPC服务已启动在 {address}")
    
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("正在关闭gRPC服务器...")
        # 关闭HTTP客户端
        await servicer.close()
        # 优雅关闭
        await server.stop(5)  # 5秒优雅关闭时间


async def main() -> None:
    """主函数，启动整个API网关服务"""
    # 加载配置
    config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")
    config = load_config(config_path)
    
    # 配置日志
    log_file = os.environ.get("LOGGING_FILE")
    configure_logging(log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"启动API网关服务，配置文件: {config_path}")
    
    # 创建服务注册表
    service_registry = ServiceRegistry(config)
    
    # 启动服务注册表
    await service_registry.start()
    
    # 启动REST和gRPC服务器
    rest_task = asyncio.create_task(start_rest_server(config, service_registry))
    grpc_task = asyncio.create_task(start_grpc_server(config, service_registry))
    
    # 设置信号处理
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, service_registry, [rest_task, grpc_task])))
    
    try:
        # 等待两个服务器任务完成
        await asyncio.gather(rest_task, grpc_task)
    finally:
        # 停止服务注册表
        await service_registry.stop()
        logger.info("API网关服务已停止")


async def shutdown(sig: signal.Signals, service_registry: ServiceRegistry, tasks: list) -> None:
    """
    优雅关闭所有服务
    
    Args:
        sig: 接收到的信号
        service_registry: 服务注册表
        tasks: 任务列表
    """
    logger = logging.getLogger(__name__)
    logger.info(f"收到信号 {sig.name}，正在关闭...")
    
    # 停止服务注册表
    await service_registry.stop()
    
    # 取消任务
    for task in tasks:
        if task.done():
            continue
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("服务已手动终止")
    except Exception as e:
        logging.exception(f"服务异常终止: {e}")
        sys.exit(1) 