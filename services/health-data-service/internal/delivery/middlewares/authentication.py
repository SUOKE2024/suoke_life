#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证中间件
"""

from typing import Optional
import re
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            响应对象
        """
        # 不需要认证的路径正则表达式
        exempt_paths = [
            r"/health",
            r"/docs",
            r"/redoc",
            r"/openapi.json",
            r"/api/v1/auth/.*"
        ]
        
        # 检查是否为免认证路径
        path = request.url.path
        for exempt_path in exempt_paths:
            if re.match(exempt_path, path):
                return await call_next(request)
        
        # 检查认证头
        auth_header = request.headers.get("Authorization")
        
        # 开发环境直接放行
        env = request.app.state.config.get("env", "development")
        if env == "development" and not auth_header:
            # 在开发环境中，如果没有认证头，使用开发令牌
            request.headers.__dict__["_list"].append(
                (b"authorization", b"Bearer dev-token")
            )
            return await call_next(request)
            
        # 验证认证头格式
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "未提供有效的认证凭证"}
            )
        
        # 继续处理请求
        return await call_next(request) 