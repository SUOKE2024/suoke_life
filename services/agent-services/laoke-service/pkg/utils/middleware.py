#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 中间件工具
提供请求处理的中间件功能
"""

import time
import logging
import json
import uuid
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import Config

logger = logging.getLogger(__name__)
config = Config()

# 简单的内存缓存，用于速率限制
rate_limit_cache: Dict[str, Dict[str, Any]] = {}

async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    请求日志中间件，记录请求的处理时间和结果
    
    Args:
        request: 请求对象
        call_next: 下一个处理函数
        
    Returns:
        Response: 响应对象
    """
    # 生成请求ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # 记录请求开始
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    # 记录请求信息
    logger.info(
        f"请求开始 - ID: {request_id} - {method} {path}",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("User-Agent", "unknown")
        }
    )
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        response.headers["X-Request-ID"] = request_id
        
        # 记录响应信息
        logger.info(
            f"请求完成 - ID: {request_id} - {method} {path} - 状态: {response.status_code} - 耗时: {process_time:.2f}ms",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "process_time_ms": process_time
            }
        )
        
        return response
    except Exception as e:
        # 计算处理时间
        process_time = (time.time() - start_time) * 1000
        
        # 记录错误信息
        logger.error(
            f"请求异常 - ID: {request_id} - {method} {path} - 错误: {str(e)} - 耗时: {process_time:.2f}ms",
            exc_info=True,
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "error": str(e),
                "process_time_ms": process_time
            }
        )
        
        raise

async def rate_limiter_middleware(request: Request, call_next: Callable) -> Response:
    """
    速率限制中间件，限制请求频率
    
    Args:
        request: 请求对象
        call_next: 下一个处理函数
        
    Returns:
        Response: 响应对象
    """
    # 检查是否启用速率限制
    rate_limit_enabled = config.get("security.rate_limit.enabled", True)
    if not rate_limit_enabled:
        return await call_next(request)
    
    # 获取客户端IP
    client_ip = request.client.host if request.client else "unknown"
    
    # 获取速率限制配置
    requests_per_minute = config.get("security.rate_limit.requests_per_minute", 60)
    burst = config.get("security.rate_limit.burst", 20)
    
    # 当前时间
    current_time = time.time()
    minute_ago = current_time - 60
    
    # 初始化或更新客户端记录
    if client_ip not in rate_limit_cache:
        rate_limit_cache[client_ip] = {
            "requests": [],
            "blocked_until": 0
        }
    
    client_cache = rate_limit_cache[client_ip]
    
    # 检查是否被阻止
    if client_cache["blocked_until"] > current_time:
        # 被阻止，返回429响应
        blocked_seconds = int(client_cache["blocked_until"] - current_time)
        logger.warning(
            f"请求被限制 - IP: {client_ip} - 还需等待: {blocked_seconds}秒",
            extra={
                "client_ip": client_ip,
                "blocked_seconds": blocked_seconds
            }
        )
        
        return Response(
            content=json.dumps({
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"请求过于频繁，请在{blocked_seconds}秒后重试",
                "details": {"retry_after": blocked_seconds}
            }),
            status_code=429,
            media_type="application/json"
        )
    
    # 清理过期请求记录
    client_cache["requests"] = [t for t in client_cache["requests"] if t > minute_ago]
    
    # 检查请求频率
    request_count = len(client_cache["requests"])
    if request_count >= requests_per_minute:
        # 超过限制，阻止5分钟
        client_cache["blocked_until"] = current_time + 300  # 5分钟
        
        logger.warning(
            f"请求频率超限 - IP: {client_ip} - 每分钟请求数: {request_count}",
            extra={
                "client_ip": client_ip,
                "request_count": request_count,
                "limit": requests_per_minute
            }
        )
        
        return Response(
            content=json.dumps({
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "请求过于频繁，请在5分钟后重试",
                "details": {"retry_after": 300}
            }),
            status_code=429,
            media_type="application/json"
        )
    
    # 如果请求数接近限制，但未超过突发限制，允许请求
    if request_count >= requests_per_minute - burst:
        logger.info(
            f"请求接近限制 - IP: {client_ip} - 每分钟请求数: {request_count}",
            extra={
                "client_ip": client_ip,
                "request_count": request_count,
                "limit": requests_per_minute
            }
        )
    
    # 添加当前请求时间戳
    client_cache["requests"].append(current_time)
    
    # 继续处理请求
    return await call_next(request)

class CORSMiddleware(BaseHTTPMiddleware):
    """CORS中间件，处理跨域请求"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取CORS配置
        cors_enabled = config.get("security.cors.enabled", True)
        if not cors_enabled:
            return await call_next(request)
        
        # 获取允许的来源
        allowed_origins = config.get("security.cors.allowed_origins", ["*"])
        origin = request.headers.get("Origin", "")
        
        # 处理OPTIONS请求（预检请求）
        if request.method == "OPTIONS":
            response = Response(
                content="",
                status_code=200
            )
        else:
            # 处理实际请求
            response = await call_next(request)
        
        # 添加CORS头
        if origin in allowed_origins or "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Token"
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response 