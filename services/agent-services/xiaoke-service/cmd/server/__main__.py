#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小克服务(XiaoKeService)入口点
"""

import asyncio
import logging
import os
import signal
import sys
from concurrent import futures

import grpc
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保项目根目录在Python路径中，方便导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入服务实现
from internal.delivery.xiaoke_service_impl import XiaoKeServiceServicer
from internal.delivery.health_check import start_health_server
from api.grpc import xiaoke_service_pb2_grpc

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getenv('LOG_DIR', 'logs'), 'xiaoke-service.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 确保日志目录存在
os.makedirs(os.getenv('LOG_DIR', 'logs'), exist_ok=True)

# 启动服务
def serve():
    # 启动健康检查服务器
    http_server_host = os.getenv('MONITORING_HOST', '0.0.0.0')
    http_server_port = int(os.getenv('MONITORING_PORT', '51054'))
    health_server = start_health_server(http_server_host, http_server_port)
    
    # 创建gRPC服务器
    max_workers = int(os.getenv('GRPC_MAX_WORKERS', '10'))
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.keepalive_time_ms', 30000),  # 每30秒发送keepalive ping
            ('grpc.keepalive_timeout_ms', 10000),  # 10秒内无响应视为连接断开
            ('grpc.http2.max_pings_without_data', 0),  # 允许无数据的ping
            ('grpc.http2.min_time_between_pings_ms', 10000),  # ping之间的最小时间
            ('grpc.http2.min_ping_interval_without_data_ms', 5000)  # 无数据情况下ping的最小间隔
        ]
    )
    
    # 注册服务实现
    xiaoke_service_pb2_grpc.add_XiaoKeServiceServicer_to_server(
        XiaoKeServiceServicer(), server
    )
    
    # 添加端口
    server_host = os.getenv('GRPC_HOST', '0.0.0.0')
    server_port = int(os.getenv('GRPC_PORT', '50054'))
    server.add_insecure_port(f'{server_host}:{server_port}')
    
    # 启动服务器
    server.start()
    logger.info(f"小克服务(XiaoKeService)已启动，监听端口: {server_port}")
    logger.info(f"健康检查服务已启动，监听端口: {http_server_port}")
    
    # 设置优雅关闭处理
    shutdown_event = asyncio.Event()
    
    def handle_shutdown(sig, frame):
        logger.info("接收到关闭信号，准备优雅关闭...")
        shutdown_event.set()
    
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    # 保持服务运行
    try:
        # 使用asyncio事件等待关闭信号
        loop = asyncio.get_event_loop()
        loop.run_until_complete(wait_for_termination(shutdown_event))
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("正在关闭gRPC服务器...")
        server.stop(30)  # 给30秒完成进行中的请求
        logger.info("服务已关闭")

async def wait_for_termination(shutdown_event):
    """等待终止信号"""
    await shutdown_event.wait()

if __name__ == '__main__':
    logger.info("正在启动小克服务(XiaoKeService)...")
    serve()