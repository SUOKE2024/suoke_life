#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gRPC服务器实现模块

负责启动和配置gRPC服务器，注册服务存根。
"""
import asyncio
import logging
import grpc
from concurrent import futures
from typing import Optional

from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer

from api.grpc import auth_pb2, auth_pb2_grpc
from .service import AuthServicer


class HealthCheckServicer(HealthServicer):
    """健康检查服务实现"""
    
    async def Check(self, request, context):
        """检查服务状态"""
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )
    
    async def Watch(self, request, context):
        """监控服务状态"""
        while True:
            yield health_pb2.HealthCheckResponse(
                status=health_pb2.HealthCheckResponse.SERVING
            )
            await asyncio.sleep(1)


async def serve(port: int, max_workers: Optional[int] = None, secured: bool = False):
    """启动gRPC服务器
    
    Args:
        port: 服务端口
        max_workers: 最大工作线程数
        secured: 是否启用TLS加密
    """
    # 默认工作线程数
    if max_workers is None:
        max_workers = min(32, (asyncio.get_event_loop().get_default_executor()._max_workers * 5))
    
    # 创建服务器
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.keepalive_time_ms', 60000),  # 60s
            ('grpc.keepalive_timeout_ms', 20000),  # 20s
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.keepalive_permit_without_calls', 1),
        ]
    )
    
    # 注册健康检查服务
    health_servicer = HealthCheckServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    # 注册认证服务
    auth_servicer = AuthServicer()
    auth_pb2_grpc.add_AuthServiceStub(auth_servicer, server)
    
    # 添加服务反射
    service_names = (
        auth_pb2.DESCRIPTOR.services_by_name['AuthService'].full_name,
        health_pb2.DESCRIPTOR.services_by_name['Health'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)
    
    # 配置端口
    if secured:
        # TODO: 实现TLS加密
        # with open('server.key', 'rb') as f:
        #     private_key = f.read()
        # with open('server.crt', 'rb') as f:
        #     certificate_chain = f.read()
        # server_credentials = grpc.ssl_server_credentials(
        #     [(private_key, certificate_chain)]
        # )
        # server.add_secure_port(f'[::]:{port}', server_credentials)
        raise NotImplementedError("TLS加密尚未实现")
    else:
        server.add_insecure_port(f'[::]:{port}')
    
    # 启动服务器
    logging.info(f"gRPC服务器启动于端口 {port}")
    await server.start()
    
    try:
        # 持续运行
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("接收到终止信号，正在关闭gRPC服务器...")
        await server.stop(grace=5)  # 5秒优雅关闭
        logging.info("gRPC服务器已关闭")
    except Exception as e:
        logging.error(f"gRPC服务器运行错误: {str(e)}")
        await server.stop(grace=0)
        raise 