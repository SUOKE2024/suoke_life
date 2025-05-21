#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
REST API路由配置
负责动态注册路由并设置代理规则
"""

import logging
import time
from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from prometheus_client import Counter

from internal.model.config import GatewayConfig, RouteConfig
from internal.service.service_registry import ServiceRegistry
from pkg.utils.cache import CacheKey, CacheManager
from pkg.utils.rewrite import PathRewriter, create_path_rewriter


logger = logging.getLogger(__name__)

# 定义指标
request_counter = Counter(
    "api_gateway_requests_total", 
    "Total count of requests by service and status",
    ["service", "status"]
)

latency_by_service = Counter(
    "api_gateway_request_latency_seconds",
    "Request latency in seconds by service", 
    ["service"]
)


def setup_routes(app: FastAPI, config: GatewayConfig) -> None:
    """
    设置FastAPI路由
    
    Args:
        app: FastAPI应用实例
        config: 网关配置
    """
    # 创建API路由器
    api_router = APIRouter(prefix="/api")
    
    # 创建通用的代理路由处理函数
    async def proxy_request(request: Request, service_name: str, path: str) -> Response:
        """
        通用的代理路由处理函数
        
        Args:
            request: 请求对象
            service_name: 目标服务名称
            path: 请求路径
            
        Returns:
            Response: 响应对象
        """
        # 获取服务注册表
        service_registry: ServiceRegistry = request.app.state.registry
        
        # 尝试获取服务端点
        endpoint = service_registry.get_endpoint(service_name)
        if not endpoint:
            request_counter.labels(service=service_name, status="unavailable").inc()
            logger.warning(f"服务 {service_name} 不可用")
            raise HTTPException(status_code=503, detail=f"服务 {service_name} 暂时不可用")
            
        host, port = endpoint
        
        # 构建目标URL
        target_url = f"http://{host}:{port}/{path.lstrip('/')}"
        
        # 创建缓存键
        cache_key = None
        if config.cache.enabled and request.method.upper() == "GET":
            cache_manager = CacheManager(config.cache)
            cache_headers = config.cache.include_headers
            
            # 创建缓存键
            cache_key = cache_manager.create_cache_key_from_request(request, cache_headers)
            
            # 尝试从缓存获取响应
            cached_response = await cache_manager.get(cache_key)
            if cached_response:
                logger.debug(f"缓存命中: {request.url.path}")
                return cached_response.to_response()
        
        # 准备请求头
        headers = dict(request.headers)
        headers["X-Forwarded-For"] = request.client.host if request.client else "unknown"
        headers["X-Forwarded-Proto"] = request.url.scheme
        headers["X-Forwarded-Host"] = request.headers.get("host", "unknown")
        headers["X-Forwarded-Path"] = request.url.path
        
        # 获取请求体
        body = await request.body()
        
        start_time = time.time()
        
        try:
            # 使用异步HTTP客户端发送请求
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params,
                    timeout=config.timeout,
                    follow_redirects=True
                )
            
            # 记录请求指标
            elapsed = time.time() - start_time
            request_counter.labels(service=service_name, status=response.status_code).inc()
            latency_by_service.labels(service=service_name).inc(elapsed)
            
            # 准备响应头
            response_headers = dict(response.headers)
            
            # 添加自定义响应头
            response_headers["X-Proxy-By"] = "SuokeLife-API-Gateway"
            response_headers["X-Proxy-Service"] = service_name
            response_headers["X-Response-Time"] = str(elapsed)
            
            # 创建响应对象
            proxy_response = Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )
            
            # 如果是成功的GET请求，尝试缓存响应
            if (config.cache.enabled and
                request.method.upper() == "GET" and
                200 <= response.status_code < 300 and
                cache_key):
                
                cache_manager = CacheManager(config.cache)
                cache_item = cache_manager.create_cache_item_from_response(
                    proxy_response,
                    ttl=config.cache.ttl
                )
                await cache_manager.set(cache_key, cache_item)
            
            return proxy_response
            
        except httpx.RequestError as e:
            # 记录请求错误
            elapsed = time.time() - start_time
            request_counter.labels(service=service_name, status="error").inc()
            latency_by_service.labels(service=service_name).inc(elapsed)
            
            logger.error(f"请求服务 {service_name} 失败: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=503,
                content={"detail": f"请求服务 {service_name} 失败: {str(e)}"}
            )
    
    # 创建路径重写器
    path_rewriter = create_path_rewriter(config.routes)
    
    # 为每个路由创建代理路径
    for route in config.routes:
        # 根据路由配置创建实际的路由
        @api_router.api_route(
            path=f"{route.prefix}{{path:path}}",
            methods=route.methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            name=f"proxy_{route.name}",
            include_in_schema=True,
            description=f"代理到 {route.service} 服务"
        )
        async def route_handler(
            request: Request,
            path: str,
            service_name: str = route.service,
            prefix: str = route.prefix
        ) -> Response:
            # 获取原始路径（去掉前缀）
            original_path = path
            
            # 重写路径（如果需要）
            rewritten_path = path_rewriter.rewrite_path(service_name, original_path)
            if rewritten_path != original_path:
                logger.debug(f"路径已重写: {original_path} => {rewritten_path}")
                path = rewritten_path
                
            # 代理请求
            return await proxy_request(request, service_name, path)
    
    # 注册API路由器
    app.include_router(api_router)
    
    # 添加健康检查接口
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        return {"status": "ok", "server": "api-gateway"}
    
    # 添加服务发现接口
    @app.get("/discovery")
    async def service_discovery(request: Request):
        """服务发现接口"""
        service_registry = request.app.state.registry
        services = {
            name: {
                "endpoints": len(svc.endpoints),
                "healthy_endpoints": len(service_registry.healthy_endpoints.get(name, [])),
                "status": "up" if name in service_registry.healthy_endpoints and 
                            service_registry.healthy_endpoints[name] else "down"
            }
            for name, svc in service_registry.services.items()
        }
        return {
            "services": services,
            "routes": [
                {
                    "name": route.name,
                    "prefix": route.prefix,
                    "service": route.service,
                    "methods": route.methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                    "auth_required": route.auth_required
                }
                for route in config.routes
            ]
        }
    
    logger.info(f"已注册 {len(config.routes)} 条路由规则") 