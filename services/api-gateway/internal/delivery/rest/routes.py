"""
routes - 索克生活项目模块
"""

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from internal.model.config import GatewayConfig, RouteConfig
from internal.service.service_registry import ServiceRegistry
from pkg.utils.cache import CacheKey, CacheManager
from pkg.utils.rewrite import PathRewriter, create_path_rewriter
from prometheus_client import Counter
import httpx
import logging
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
REST API路由模块
设置API网关的路由
"""




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

# 通用的代理路由处理函数
async def proxy_request(request: Request, service_name: str, path: str) -> Response:
    """
    通用的代理路由处理函数
    
    Args:
        request: 请求对象
        service_name: 目标服务名称
        path: 请求路径（已处理过的部分路径）
        
    Returns:
        Response: 响应对象
    """
    logger.debug(f"处理代理请求: 服务={service_name}, 路径={path}")
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
    
    # 获取配置
    config = getattr(request.app.state, "config", None)
    
    # 创建缓存键
    cache_key = None
    if config and config.cache.enabled and request.method.upper() == "GET":
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
    # FastAPI和HTTP标准中，请求头名称都是小写的，但我们需要遵循原始请求头的格式
    # 先创建一个临时字典来存储原始头信息和小写键的映射
    headers_mapping = {k.lower(): (k, v) for k, v in request.headers.items()}
    
    # 创建最终的请求头字典
    headers = {k: v for _, (k, v) in headers_mapping.items()}
    
    # 添加自定义头部
    headers["X-Forwarded-For"] = request.client.host if request.client else "unknown"
    headers["X-Forwarded-Proto"] = request.url.scheme
    headers["X-Forwarded-Host"] = headers_mapping.get("host", (None, "unknown"))[1]
    headers["X-Forwarded-Path"] = request.url.path
    
    # 获取请求体
    body = await request.body()
    
    start_time = time.time()
    timeout = config.timeout if config else 30.0
    
    try:
        # 使用异步HTTP客户端发送请求
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params,
                    timeout=timeout,
                    follow_redirects=True
                )
            except Exception as e:
                # 处理请求异常
                logger.error(f"请求服务 {service_name} 失败: {str(e)}", exc_info=True)
                return JSONResponse(
                    status_code=503,
                    content={"detail": f"请求服务 {service_name} 失败: {str(e)}"}
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
        if (config and config.cache.enabled and
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

def setup_routes(app: FastAPI, config: GatewayConfig):
    """设置路由"""
    # 添加基础路由
    @app.get("/")
    async def index():
        """网关根路径"""
        return {
            "name": "索克生活API网关",
            "version": "0.1.0",
            "description": "索克生活平台统一API入口"
        }
    
    @app.get("/routes")
    async def get_routes():
        """获取所有路由信息"""
        routes = []
        for route in config.routes:
            routes.append({
                "name": route.name,
                "prefix": route.prefix,
                "service": route.service,
                "auth_required": route.auth_required
            })
        return {"routes": routes}
    
    # 添加健康检查路由
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "ok"}
    
    # 添加版本路由
    @app.get("/version")
    async def version():
        """版本信息"""
        return {"version": "0.1.0"}
    
    # 添加调试路由
    if config.server.debug:
        @app.get("/debug/config")
        async def debug_config():
            """配置信息（仅调试模式可用）"""
            # 简化配置，移除敏感信息
            debug_config = {
                "server": {
                    "rest": {
                        "host": config.server.rest.host,
                        "port": config.server.rest.port
                    },
                    "grpc": {
                        "host": config.server.grpc.host,
                        "port": config.server.grpc.port
                    },
                    "production": config.server.production,
                    "debug": config.server.debug
                },
                "routes_count": len(config.routes) if hasattr(config, 'routes') else 0,
                "middleware": {
                    "cors": {"enabled": config.middleware.cors.enabled},
                    "rate_limit": {"enabled": config.middleware.rate_limit.enabled}
                }
            }
            return debug_config
        
        @app.get("/debug/routes")
        async def debug_routes():
            """路由详情（仅调试模式可用）"""
            return {"routes": [vars(route) for route in config.routes]}
    
    logger.info("基础路由设置完成")

    # 保存配置到应用状态
    app.state.config = config
    
    # 创建API路由器 - 不添加前缀，因为路由配置已经包含了/api前缀
    api_router = APIRouter()
    
    # 创建路径重写器
    path_rewriter = create_path_rewriter(config.routes)
    
    # 为每个路由创建代理路径
    for route in config.routes:
        # 使用函数工厂模式，为每个路由创建独立的处理函数
        def create_route_handler(route_config):
            """创建特定路由的处理函数"""
            async def route_handler(
                request: Request,
                path: str
            ) -> Response:
                service_name = route_config.service
                
                # 获取完整路径
                full_path = f"{route_config.prefix.rstrip('/')}/{path}"
                
                # 记录原始路径信息
                logger.info(f"处理请求: 前缀={route_config.prefix}, 路径={path}, 完整路径={full_path}")
                
                # 重写路径处理
                if route_config.rewrite_path:
                    # 有重写规则，尝试重写
                    rewritten_path = path_rewriter.rewrite_path(service_name, full_path)
                    if rewritten_path != full_path:
                        logger.info(f"路径已重写: {full_path} => {rewritten_path}")
                        path = rewritten_path.lstrip('/')
                    else:
                        # 即使有规则但未匹配时，保持原始路径
                        logger.debug(f"路径未匹配重写规则: {full_path}")
                else:
                    # 无重写规则时，检查strip_prefix属性决定是否保留完整路径
                    if not route_config.strip_prefix:
                        path = full_path.lstrip('/')
                        logger.debug(f"保留完整路径: {path}")
                    # 否则使用原始path，即去掉了前缀的部分
                
                # 代理请求
                return await proxy_request(request, service_name, path)
            
            return route_handler
        
        # 为当前路由创建处理函数
        handler = create_route_handler(route)
        
        # 注册路由
        # 确保路由前缀以斜杠开头，不以斜杠结尾
        prefix = route.prefix.rstrip("/")
        route_path = f"{prefix}/{{path:path}}"
        logger.info(f"注册路由: {route_path} -> {route.service}")
        api_router.add_api_route(
            path=route_path,
            endpoint=handler,
            methods=route.methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            name=f"proxy_{route.name}",
            include_in_schema=True,
            description=f"代理到 {route.service} 服务"
        )
    
    # 注册API路由器
    app.include_router(api_router)
    
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