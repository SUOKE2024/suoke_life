#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API网关的gRPC服务实现
提供健康检查、代理请求、获取路由等功能
"""

import logging
from typing import Dict, List, Optional

import grpc
import httpx
from google.protobuf.json_format import MessageToDict

# 在导入自动生成的proto模块前，需要确保已经生成了这些模块
# 通常在项目初始化阶段使用grpc_tools.protoc生成这些模块
# 这里假设模块已生成并位于正确的包导入路径上
from api.grpc.api_gateway_pb2 import (
    HealthCheckResponse, 
    ProxyResponse, 
    GetRoutesResponse, 
    GetServiceStatusResponse
)
from api.grpc.api_gateway_pb2_grpc import ApiGatewayServicer, add_ApiGatewayServicer_to_server

from internal.model.config import GatewayConfig, RouteConfig
from internal.service.service_registry import ServiceRegistry


logger = logging.getLogger(__name__)


class ApiGatewayService(ApiGatewayServicer):
    """API网关gRPC服务实现"""
    
    def __init__(self, service_registry: ServiceRegistry, config: GatewayConfig):
        """
        初始化API网关gRPC服务
        
        Args:
            service_registry: 服务注册表实例
            config: 网关配置
        """
        self.service_registry = service_registry
        self.config = config
        self.http_client = httpx.AsyncClient()
    
    async def HealthCheck(self, request, context):
        """
        健康检查处理函数
        
        Args:
            request: 健康检查请求
            context: gRPC上下文
            
        Returns:
            HealthCheckResponse: 健康检查响应
        """
        logger.debug(f"收到健康检查请求: {request}")
        response = HealthCheckResponse()
        
        # 检查特定服务健康状态
        if request.service_name:
            if self.service_registry.get_service(request.service_name):
                endpoint = self.service_registry.get_endpoint(request.service_name)
                if endpoint:
                    response.status = HealthCheckResponse.ServingStatus.SERVING
                    response.message = f"服务 {request.service_name} 可用"
                else:
                    response.status = HealthCheckResponse.ServingStatus.NOT_SERVING
                    response.message = f"服务 {request.service_name} 端点不可用"
            else:
                response.status = HealthCheckResponse.ServingStatus.UNKNOWN
                response.message = f"服务 {request.service_name} 不存在"
        else:
            # 检查网关自身状态
            response.status = HealthCheckResponse.ServingStatus.SERVING
            response.message = "API网关服务正常"
        
        return response
    
    async def ProxyRequest(self, request, context):
        """
        代理请求处理函数
        
        Args:
            request: 代理请求
            context: gRPC上下文
            
        Returns:
            ProxyResponse: 代理响应
        """
        logger.debug(f"收到代理请求: 服务={request.service}, 路径={request.path}")
        response = ProxyResponse()
        
        # 获取服务端点
        endpoint = self.service_registry.get_endpoint(request.service)
        if not endpoint:
            logger.error(f"服务不可用: {request.service}")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(f"服务不可用: {request.service}")
            response.error = f"服务不可用: {request.service}"
            return response
        
        host, port = endpoint
        target_url = f"http://{host}:{port}/{request.path.lstrip('/')}"
        
        # 准备请求头
        headers = dict(request.headers)
        
        # 准备查询参数
        params = dict(request.query_params)
        
        try:
            # 发送HTTP请求
            http_response = await self.http_client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=request.body,
                params=params,
            )
            
            # 填充响应
            response.status_code = http_response.status_code
            for key, value in http_response.headers.items():
                response.headers[key] = value
            response.body = http_response.content
            
            return response
        except Exception as e:
            logger.error(f"代理请求异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"代理请求异常: {str(e)}")
            response.error = f"代理请求异常: {str(e)}"
            return response
    
    async def GetRoutes(self, request, context):
        """
        获取路由信息处理函数
        
        Args:
            request: 获取路由信息请求
            context: gRPC上下文
            
        Returns:
            GetRoutesResponse: 路由信息响应
        """
        logger.debug(f"收到获取路由信息请求: {request}")
        response = GetRoutesResponse()
        
        # 筛选路由
        routes = self.config.routes
        if request.service_name:
            routes = [r for r in routes if r.service == request.service_name]
        
        # 填充路由信息
        for route in routes:
            route_info = response.routes.add()
            route_info.name = route.name
            route_info.prefix = route.prefix
            route_info.service = route.service
            route_info.auth_required = route.auth_required
        
        return response
    
    async def GetServiceStatus(self, request, context):
        """
        获取服务状态处理函数
        
        Args:
            request: 获取服务状态请求
            context: gRPC上下文
            
        Returns:
            GetServiceStatusResponse: 服务状态响应
        """
        logger.debug(f"收到获取服务状态请求: {request}")
        response = GetServiceStatusResponse()
        
        service_names = list(request.service_names) if request.service_names else list(self.service_registry.services.keys())
        
        for service_name in service_names:
            service = self.service_registry.get_service(service_name)
            if not service:
                continue
            
            status = response.statuses.add()
            status.name = service_name
            
            healthy_endpoints = self.service_registry.healthy_endpoints.get(service_name, [])
            status.available = len(healthy_endpoints) > 0
            status.endpoint_count = len(service.endpoints)
            status.healthy_endpoint_count = len(healthy_endpoints)
        
        return response
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()


def register_servicer(server, service_registry, config):
    """
    注册gRPC服务到服务器
    
    Args:
        server: gRPC服务器
        service_registry: 服务注册表
        config: 网关配置
    """
    servicer = ApiGatewayService(service_registry, config)
    add_ApiGatewayServicer_to_server(servicer, server)
    return servicer 