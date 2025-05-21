#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务入口程序
"""

import os
import sys
import argparse
import yaml
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from loguru import logger
import signal

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from internal.delivery.grpc.server import RagServicer
from internal.delivery.rest.app import create_app
from internal.service.rag_service import RagService


def load_config(config_path: str) -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        raise


def setup_logging(config: dict):
    """
    配置日志
    
    Args:
        config: 配置信息
    """
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_format = log_config.get('format', "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # 文件日志
    log_file = log_config.get('file')
    if log_file:
        logger.add(
            log_file,
            rotation=log_config.get('rotation', '500 MB'),
            retention=log_config.get('retention', '10 days'),
            compression=log_config.get('compression', 'zip'),
            level=log_level
        )
    
    # 还可以添加其他日志处理，如 Sentry, ELK 等


def setup_grpc_server(config: dict, rag_service: RagService):
    """
    启动gRPC服务器
    
    Args:
        config: 配置信息
        rag_service: RAG服务实例
    """
    import grpc
    from concurrent import futures
    from api.grpc.generated import rag_service_pb2_grpc
    
    server_config = config['server']['grpc']
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=server_config.get('max_workers', 10)),
        options=server_config.get('options', [])
    )
    
    # 创建服务实现
    servicer = RagServicer(config, rag_service)
    
    # 添加服务实现到服务器
    rag_service_pb2_grpc.add_RagServiceServicer_to_server(servicer, server)
    
    # 添加服务地址
    addr = f"{server_config['host']}:{server_config['port']}"
    server.add_insecure_port(addr)
    
    return server


async def serve_grpc(server, config: dict):
    """
    启动gRPC服务
    
    Args:
        server: gRPC服务器
        config: 配置信息
    """
    server_config = config['server']['grpc']
    addr = f"{server_config['host']}:{server_config['port']}"
    
    try:
        logger.info(f"启动gRPC服务，监听地址: {addr}")
        await server.start()
        await server.wait_for_termination()
    except Exception as e:
        logger.error(f"gRPC服务启动失败: {e}")
        raise
    finally:
        logger.info("关闭gRPC服务")
        await server.stop(0)


def serve_rest(config: dict, rag_service: RagService = None):
    """
    启动REST服务
    
    Args:
        config: 配置信息
        rag_service: 可选的RAG服务实例
    """
    server_config = config['server']['rest']
    
    # 创建FastAPI应用
    app = create_app(config)
    
    # 使用uvicorn服务器运行
    uvicorn.run(
        app,
        host=server_config['host'],
        port=server_config['port'],
        log_level=server_config.get('log_level', 'info').lower(),
        reload=server_config.get('reload', False)
    )


async def run_services(config: dict):
    """
    运行所有服务
    
    Args:
        config: 配置信息
    """
    # 创建RAG服务实例
    rag_service = RagService(config)
    await rag_service.initialize()
    
    # 决定启动哪些服务
    server_config = config['server']
    
    # 创建gRPC服务器
    grpc_server = None
    if server_config.get('grpc', {}).get('enabled', True):
        grpc_server = setup_grpc_server(config, rag_service)
    
    try:
        # 同时启动REST和gRPC服务
        if server_config.get('rest', {}).get('enabled', True) and grpc_server:
            # 创建协程任务
            grpc_task = asyncio.create_task(serve_grpc(grpc_server, config))
            
            # 启动REST服务（这会阻塞当前线程）
            rest_config = server_config['rest']
            app = create_app(config)
            config = uvicorn.Config(
                app=app,
                host=rest_config['host'],
                port=rest_config['port'],
                log_level=rest_config.get('log_level', 'info').lower(),
                reload=rest_config.get('reload', False)
            )
            server = uvicorn.Server(config)
            await server.serve()
            
            # 等待gRPC任务完成
            await grpc_task
        
        # 仅启动gRPC服务
        elif grpc_server:
            await serve_grpc(grpc_server, config)
            
        # 仅启动REST服务
        elif server_config.get('rest', {}).get('enabled', True):
            rest_config = server_config['rest']
            app = create_app(config)
            config = uvicorn.Config(
                app=app,
                host=rest_config['host'],
                port=rest_config['port'],
                log_level=rest_config.get('log_level', 'info').lower(),
                reload=rest_config.get('reload', False)
            )
            server = uvicorn.Server(config)
            await server.serve()
        
        else:
            logger.warning("未启用任何服务，程序将退出")
        
    except Exception as e:
        logger.error(f"服务运行出错: {e}")
    finally:
        # 优雅关闭
        if rag_service:
            logger.info("关闭RAG服务")
            await rag_service.close()


def handle_signal(sig, frame):
    """
    处理终止信号
    
    Args:
        sig: 信号
        frame: 栈帧
    """
    logger.info(f"接收到信号: {sig}, 准备优雅关闭")
    if 'rag_service' in globals() and rag_service:
        asyncio.run(rag_service.close())
    sys.exit(0)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='索克生活 RAG 服务')
    parser.add_argument(
        '--config', '-c',
        type=str,
        default=os.environ.get('RAG_CONFIG_PATH', 'config/default.yaml'),
        help='配置文件路径'
    )
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 设置日志
    setup_logging(config)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    logger.info("启动索克生活 RAG 服务")
    
    try:
        # 运行服务
        asyncio.run(run_services(config))
    except KeyboardInterrupt:
        logger.info("接收到中断信号，服务正在退出")
    except Exception as e:
        logger.error(f"启动服务失败: {e}")
        sys.exit(1)
    finally:
        logger.info("服务已退出")


if __name__ == '__main__':
    main()