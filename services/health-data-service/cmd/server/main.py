#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务主入口
"""

import os
import sys
import argparse
import asyncio
import signal
import logging
from typing import Optional, Dict, Any
import json
import yaml
from pathlib import Path

import uvicorn
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from internal.delivery.rest.app import create_app
from internal.delivery.grpc.server import serve as serve_grpc
from internal.service.health_data_service import HealthDataService
from pkg.utils.config import load_config


def configure_logging(log_level: str) -> None:
    """配置日志"""
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # 添加文件处理器
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    logger.add(
        logs_dir / "health_data_service_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天轮换
        retention="30 days",  # 保留30天
        level=log_level,
        compression="zip",  # 压缩旧日志
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # 配置uvicorn日志
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    
    logger.info(f"日志配置完成，级别：{log_level}")


async def start_rest_server(config: Dict[str, Any], service: HealthDataService) -> None:
    """启动REST服务器"""
    host = config.get("rest", {}).get("host", "0.0.0.0")
    port = config.get("rest", {}).get("port", 8080)
    
    app = create_app(config, service)
    
    # 使用uvicorn服务器
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        loop="auto",
        reload=False,
        workers=1
    )
    server = uvicorn.Server(config)
    logger.info(f"REST API服务启动于 http://{host}:{port}")
    await server.serve()


async def start_grpc_server(config: Dict[str, Any], service: HealthDataService) -> None:
    """启动gRPC服务器"""
    host = config.get("grpc", {}).get("host", "0.0.0.0")
    port = config.get("grpc", {}).get("port", 50051)
    
    logger.info(f"gRPC服务启动于 {host}:{port}")
    await serve_grpc(host, port, service)


async def start_server(
    config_path: str,
    mode: str = "all",
    log_level: str = "INFO"
) -> None:
    """
    启动服务器
    
    Args:
        config_path: 配置文件路径
        mode: 启动模式，可选值为: all, rest, grpc
        log_level: 日志级别
    """
    # 配置日志
    configure_logging(log_level)
    
    logger.info(f"健康数据服务启动中，模式：{mode}")
    
    # 加载配置
    config = load_config(config_path)
    if not config:
        logger.error(f"无法加载配置文件：{config_path}")
        sys.exit(1)
    
    logger.info(f"配置加载成功: {config_path}")
    
    # 创建服务实例
    service = HealthDataService(config)
    await service.initialize()
    
    # 处理终止信号
    loop = asyncio.get_event_loop()
    
    def handle_signal(signum, frame):
        logger.info(f"收到信号 {signum}，准备关闭服务...")
        loop.stop()
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        tasks = []
        
        # 根据模式启动服务
        if mode in ["all", "rest"]:
            tasks.append(start_rest_server(config, service))
        
        if mode in ["all", "grpc"]:
            tasks.append(start_grpc_server(config, service))
        
        # 启动所有服务
        await asyncio.gather(*tasks)
        
    except Exception as e:
        logger.error(f"服务启动出错: {e}")
        sys.exit(1)
    finally:
        # 关闭服务
        await service.shutdown()
        logger.info("健康数据服务已关闭")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="健康数据服务")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/default.yaml",
        help="配置文件路径"
    )
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["all", "rest", "grpc"], 
        default="all",
        help="启动模式：all - 所有服务, rest - 只启动REST API, grpc - 只启动gRPC服务"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
        default="INFO",
        help="日志级别"
    )
    
    args = parser.parse_args()
    
    # 解析配置文件路径
    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            config_path
        )
    
    # 启动服务
    asyncio.run(start_server(config_path, args.mode, args.log_level))


if __name__ == "__main__":
    main() 