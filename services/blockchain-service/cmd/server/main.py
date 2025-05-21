#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
区块链服务主入口文件
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from internal.delivery.grpc.server import BlockchainServicer
from internal.model.config import load_config
from pkg.utils.logging_utils import setup_logging

# 从生成的protobuf导入
from api.grpc import blockchain_pb2, blockchain_pb2_grpc


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='SoKe Life 区块链服务')
    parser.add_argument('--config', type=str, default='config/config.yaml', 
                        help='配置文件路径')
    parser.add_argument('--port', type=int, default=None,
                        help='服务端口(覆盖配置文件)')
    parser.add_argument('--log-level', type=str, default=None, 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='日志级别(覆盖配置文件)')
    return parser.parse_args()


async def serve(config):
    """启动gRPC服务器"""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=config.server.max_workers),
        options=[
            ('grpc.max_send_message_length', config.server.max_message_length),
            ('grpc.max_receive_message_length', config.server.max_message_length),
        ]
    )
    
    # 注册服务实现
    servicer = BlockchainServicer(config)
    blockchain_pb2_grpc.add_BlockchainServiceServicer_to_server(servicer, server)
    
    # 添加服务反射
    service_names = (
        blockchain_pb2.DESCRIPTOR.services_by_name['BlockchainService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)
    
    # 启动服务器
    port = config.server.port
    address = f'[::]:{port}'
    server.add_insecure_port(address)
    
    logging.info(f"服务器启动于 {address}")
    await server.start()
    
    # 处理终止信号
    async def shutdown(signal_):
        logging.info(f"收到信号 {signal_.name}，正在关闭服务器...")
        await server.stop(5)  # 5秒宽限期
    
    # 注册信号处理器
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s)))
    
    # 服务器运行直到被中断
    await server.wait_for_termination()


def main():
    """主函数"""
    args = parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 命令行参数覆盖配置文件
    if args.port:
        config.server.port = args.port
    if args.log_level:
        config.logging.level = args.log_level
    
    # 设置日志
    setup_logging(config.logging)
    
    logging.info("SoKe Life 区块链服务启动中...")
    
    # 异步启动服务器
    try:
        asyncio.run(serve(config))
    except KeyboardInterrupt:
        logging.info("服务器已通过键盘中断关闭")
    except Exception as e:
        logging.error(f"服务器异常：{e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 