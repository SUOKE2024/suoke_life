"""
proxy_service - 索克生活项目模块
"""

        from fastapi.responses import Response as RawResponse
        import random
from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from internal.model.config import GatewayConfig, RetryConfig, ServiceConfig
from internal.service.service_registry import ServiceRegistry
from pkg.utils.cache import Cache, CacheManager
from pkg.utils.circuit_breaker import CircuitBreaker, CircuitBreakerRegistry
from typing import Any, Dict, List, Optional, Tuple, Union
import aiohttp
import asyncio
import json
import logging

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代理服务，负责转发请求到后端微服务
"""




logger = logging.getLogger(__name__)

class ProxyService:
    """
    代理服务，负责将请求转发到后端微服务
    """
    
    def __init__(
        self, 
        config: GatewayConfig,
        service_registry: ServiceRegistry,
        circuit_breaker_registry: CircuitBreakerRegistry,
        cache_manager: Optional[CacheManager] = None
    ):
        """
        初始化代理服务
        
        Args:
            config: 网关配置
            service_registry: 服务注册表
            circuit_breaker_registry: 熔断器注册表
            cache_manager: 缓存管理器
        """
        self.config = config
        self.service_registry = service_registry
        self.circuit_breaker_registry = circuit_breaker_registry
        self.cache_manager = cache_manager
        self.session = None
    
    async def start(self):
        """
        启动代理服务
        """
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("代理服务已启动")
    
    async def stop(self):
        """
        停止代理服务
        """
        if self.session is not None:
            await self.session.close()
            self.session = None
            logger.info("代理服务已停止")
    
    async def forward_request(
        self, 
        request: Request,
        service_name: str,
        path: str
    ) -> Response:
        """
        转发请求到后端服务
        
        Args:
            request: 原始请求
            service_name: 目标服务名称
            path: 目标路径
            
        Returns:
            Response: 后端服务的响应
        """
        if self.session is None:
            await self.start()
        
        # 检查缓存（如果启用）
        if self.cache_manager and self.config.cache.enabled and request.method.upper() == "GET":
            cache_key = self.cache_manager.create_key_from_request(request)
            cached_response = await self.cache_manager.get(cache_key)
            if cached_response:
                logger.debug(f"返回缓存响应: {service_name}{path}")
                return cached_response
        
        # 获取服务端点
        endpoint = await self._get_service_endpoint(service_name)
        if not endpoint:
            return JSONResponse(
                status_code=503,
                content={"detail": f"服务 {service_name} 不可用"}
            )
        
        # 构建目标URL
        target_url = f"http://{endpoint.host}:{endpoint.port}{path}"
        
        # 获取熔断器
        circuit_breaker = self.circuit_breaker_registry.get_or_create(service_name)
        
        # 如果熔断器已打开，直接返回错误
        if not circuit_breaker.allow_request():
            logger.warning(f"熔断器已打开，拒绝请求: {service_name}{path}")
            return JSONResponse(
                status_code=503,
                content={"detail": f"服务 {service_name} 暂时不可用 (熔断器已打开)"}
            )
        
        # 获取重试配置
        retry_config = self.config.retry
        
        # 执行请求（可能有重试）
        response = await self._execute_request_with_retry(
            request, target_url, service_name, circuit_breaker, retry_config
        )
        
        # 更新缓存（如果启用且是GET请求）
        if (
            self.cache_manager and 
            self.config.cache.enabled and 
            request.method.upper() == "GET" and
            response and
            200 <= response.status < 300
        ):
            await self.cache_manager.set(cache_key, response)
        
        return response
    
    async def _execute_request_with_retry(
        self,
        request: Request,
        target_url: str,
        service_name: str,
        circuit_breaker: CircuitBreaker,
        retry_config: RetryConfig
    ) -> Optional[Response]:
        """
        执行请求，支持重试逻辑
        
        Args:
            request: 原始请求
            target_url: 目标URL
            service_name: 服务名称
            circuit_breaker: 服务对应的熔断器
            retry_config: 重试配置
            
        Returns:
            Response: 响应对象，失败时返回None
        """
        method = request.method
        headers = dict(request.headers)
        
        # 移除不应转发的头
        headers.pop("host", None)
        
        # 读取请求体
        body = await request.body()
        
        # 初始化重试计数器
        retry_count = 0
        max_retries = retry_config.max_retries if retry_config.enabled else 0
        
        while True:
            try:
                # 发送请求
                async with self.session.request(
                    method=method,
                    url=target_url,
                    headers=headers,
                    data=body,
                    allow_redirects=False
                ) as resp:
                    # 记录响应状态
                    is_success = 200 <= resp.status < 500
                    circuit_breaker.record_result(is_success)
                    
                    # 如果不成功，检查是否需要重试
                    if not is_success and retry_config.enabled:
                        if retry_count < max_retries and resp.status in retry_config.retry_status_codes:
                            retry_count += 1
                            retry_delay = retry_config.retry_delay * (2 ** (retry_count - 1))  # 指数退避
                            logger.warning(
                                f"请求失败，准备第 {retry_count} 次重试: {method} {target_url}, "
                                f"状态码: {resp.status}, 延迟: {retry_delay}s"
                            )
                            await asyncio.sleep(retry_delay)
                            continue
                    
                    # 处理响应
                    content = await resp.read()
                    return await self._create_response(resp.status, resp.headers, content)
                    
            except Exception as e:
                # 记录失败
                circuit_breaker.record_result(False)
                
                # 检查是否需要重试
                if retry_config.enabled and retry_count < max_retries:
                    retry_count += 1
                    retry_delay = retry_config.retry_delay * (2 ** (retry_count - 1))  # 指数退避
                    logger.warning(
                        f"请求异常，准备第 {retry_count} 次重试: {method} {target_url}, "
                        f"异常: {str(e)}, 延迟: {retry_delay}s"
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                
                # 超过重试次数或不允许重试，返回错误
                logger.error(
                    f"请求失败: {method} {target_url}, "
                    f"异常: {str(e)}, 重试次数: {retry_count}"
                )
                return JSONResponse(
                    status_code=503,
                    content={"detail": f"服务 {service_name} 请求失败: {str(e)}"}
                )
                
            # 如果到达这里，表示已尝试所有重试
            break
        
        # 如果所有重试都失败
        return JSONResponse(
            status_code=503,
            content={"detail": f"服务 {service_name} 在 {max_retries} 次重试后仍不可用"}
        )
    
    async def _get_service_endpoint(self, service_name: str) -> Optional[ServiceEndpointConfig]:
        """
        从服务注册表获取服务端点
        
        Args:
            service_name: 服务名称
            
        Returns:
            ServiceEndpointConfig: 服务端点配置，不可用时返回None
        """
        # 从服务注册表获取健康的端点
        endpoints = self.service_registry.get_healthy_endpoints(service_name)
        if not endpoints:
            logger.warning(f"找不到服务的健康端点: {service_name}")
            return None
        
        # 根据负载均衡策略选择端点
        # 这里简单实现随机选择，实际应根据配置的负载均衡策略
        return random.choice(endpoints)
    
    async def _create_response(
        self, 
        status_code: int, 
        headers: Dict[str, str], 
        content: bytes
    ) -> Response:
        """
        创建响应对象
        
        Args:
            status_code: 状态码
            headers: 响应头
            content: 响应内容
            
        Returns:
            Response: FastAPI响应对象
        """
        # 复制响应头，移除不需要的
        response_headers = dict(headers)
        response_headers.pop("transfer-encoding", None)
        response_headers.pop("content-encoding", None)
        
        # 根据内容类型创建响应
        content_type = response_headers.get("content-type", "")
        
        if "application/json" in content_type:
            try:
                # 尝试解析JSON
                json_content = json.loads(content)
                return JSONResponse(
                    status_code=status_code,
                    content=json_content,
                    headers=response_headers
                )
            except:
                # 解析失败，返回原始内容
                pass
        
        # 对于非JSON或解析失败的情况，返回原始响应
        return RawResponse(
            content=content,
            status_code=status_code,
            headers=response_headers
        ) 