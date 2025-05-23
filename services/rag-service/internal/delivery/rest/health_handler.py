#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康检查API处理器
"""

from typing import Dict, Any
import json
import time

from aiohttp import web
from loguru import logger

from services.rag_service.internal.service.health_check import HealthCheckService, HealthStatus
from services.rag_service.internal.observability.telemetry import trace_method


class HealthHandler:
    """健康检查API处理器"""
    
    def __init__(self, health_service: HealthCheckService):
        """
        初始化健康检查API处理器
        
        Args:
            health_service: 健康检查服务
        """
        self.health_service = health_service
        self.last_check_time = 0
        self.health_cache = None
        self.cache_ttl = 30  # 缓存有效期，单位秒
    
    @trace_method("health_handler_check")
    async def handle_health_check(self, request: web.Request) -> web.Response:
        """
        处理健康检查请求
        
        Args:
            request: HTTP请求对象
        
        Returns:
            web.Response: HTTP响应对象
        """
        current_time = time.time()
        detailed = request.query.get("detailed", "false").lower() == "true"
        
        # 如果缓存有效，返回缓存结果
        if self.health_cache and current_time - self.last_check_time < self.cache_ttl and not detailed:
            status_code = 200 if self.health_cache["status"] == HealthStatus.UP.value else 503
            return web.json_response({"status": self.health_cache["status"]}, status=status_code)
        
        # 执行健康检查
        health_report = await self.health_service.check_health()
        self.health_cache = health_report
        self.last_check_time = current_time
        
        # 根据健康状态设置响应状态码
        status_code = 200
        if health_report["status"] == HealthStatus.DOWN.value:
            status_code = 503
        elif health_report["status"] == HealthStatus.DEGRADED.value:
            status_code = 207
        
        # 根据详细参数决定返回内容
        if detailed:
            return web.json_response(health_report, status=status_code)
        else:
            return web.json_response({"status": health_report["status"]}, status=status_code)
    
    @trace_method("health_handler_liveness")
    async def handle_liveness(self, request: web.Request) -> web.Response:
        """
        处理存活检测请求
        
        Args:
            request: HTTP请求对象
        
        Returns:
            web.Response: HTTP响应对象
        """
        # 存活检测只检查服务是否在运行，不检查依赖组件
        return web.json_response({"status": "up"}, status=200)
    
    @trace_method("health_handler_readiness")
    async def handle_readiness(self, request: web.Request) -> web.Response:
        """
        处理就绪检测请求
        
        Args:
            request: HTTP请求对象
        
        Returns:
            web.Response: HTTP响应对象
        """
        # 就绪检测执行完整的健康检查
        health_report = await self.health_service.check_health()
        
        status_code = 200
        if health_report["status"] == HealthStatus.DOWN.value:
            status_code = 503
        
        return web.json_response({"status": health_report["status"]}, status=status_code)
    
    def register_routes(self, app: web.Application) -> None:
        """
        注册健康检查路由
        
        Args:
            app: AIOHTTP应用实例
        """
        app.router.add_get("/health", self.handle_health_check)
        app.router.add_get("/health/liveness", self.handle_liveness)
        app.router.add_get("/health/readiness", self.handle_readiness) 