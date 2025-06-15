#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gRPC服务模块

提供认证服务的gRPC接口。
"""
import asyncio
import logging
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health_pb2, health_pb2_grpc, health


async def serve(port: int = 9090, max_workers: int = 10) -> None:
    """
    启动gRPC服务器
    
    Args:
        port: 端口号
        max_workers: 最大工作线程数
    """
    logging.info(f"启动gRPC服务器，端口: {port}")
    
    # 创建服务器
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)
        ]
    )
    
    # 注册健康检查服务
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    # 注册服务反射
    SERVICE_NAMES = (
        health_pb2.DESCRIPTOR.services_by_name['Health'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # 在真实项目中，这里应该注册实际的认证服务
    # auth_pb2_grpc.add_AuthServicer_to_server(AuthServicer(), server)
    # SERVICE_NAMES += (auth_pb2.DESCRIPTOR.services_by_name['Auth'].full_name,)
    
    # 启动服务器
    server.add_insecure_port(f'[::]:{port}')
    await server.start()
    
    # 设置所有服务为健康状态
    for service in SERVICE_NAMES:
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
    
    logging.info(f"gRPC服务器已启动于端口: {port}")
    
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        # 正常关闭
        await server.stop(grace=None)
        logging.info("gRPC服务器已关闭") 