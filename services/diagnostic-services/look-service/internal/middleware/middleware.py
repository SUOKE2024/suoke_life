#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
中间件系统

提供认证、限流、日志、错误处理等中间件功能。
"""

import time
import asyncio
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from collections import defaultdict, deque

import grpc
from structlog import get_logger

logger = get_logger()


class Middleware(ABC):
    """中间件抽象基类"""
    
    @abstractmethod
    async def process_request(self, request, context, handler):
        """处理请求"""
        pass


@dataclass
class RateLimitConfig:
    """限流配置"""
    max_requests: int = 100  # 最大请求数
    window_seconds: int = 60  # 时间窗口（秒）
    burst_size: int = 10  # 突发大小
    enabled: bool = True


class RateLimitMiddleware(Middleware):
    """限流中间件"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
        
    async def process_request(self, request, context, handler):
        """处理请求限流"""
        if not self.config.enabled:
            return await handler(request, context)
        
        # 获取客户端标识（这里简化为IP地址）
        client_id = self._get_client_id(context)
        
        async with self.lock:
            current_time = time.time()
            window_start = current_time - self.config.window_seconds
            
            # 清理过期的请求记录
            client_requests = self.request_counts[client_id]
            while client_requests and client_requests[0] < window_start:
                client_requests.popleft()
            
            # 检查是否超过限制
            if len(client_requests) >= self.config.max_requests:
                logger.warning(
                    "请求被限流",
                    client_id=client_id,
                    request_count=len(client_requests),
                    max_requests=self.config.max_requests
                )
                context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                context.set_details("请求频率过高，请稍后重试")
                return None
            
            # 记录当前请求
            client_requests.append(current_time)
        
        return await handler(request, context)
    
    def _get_client_id(self, context) -> str:
        """获取客户端标识"""
        # 从gRPC上下文获取客户端信息
        peer = context.peer()
        if peer:
            return peer
        return "unknown"


class AuthenticationMiddleware(Middleware):
    """认证中间件"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.jwt_secret = config.get("jwt_secret", "")
        self.excluded_methods = set(config.get("excluded_methods", ["HealthCheck"]))
        
    async def process_request(self, request, context, handler):
        """处理认证"""
        if not self.enabled:
            return await handler(request, context)
        
        # 获取方法名
        method_name = context._rpc_event.call_details.method.split('/')[-1]
        
        # 检查是否需要认证
        if method_name in self.excluded_methods:
            return await handler(request, context)
        
        # 获取认证令牌
        token = self._get_auth_token(context)
        if not token:
            logger.warning("缺少认证令牌", method=method_name)
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("缺少认证令牌")
            return None
        
        # 验证令牌
        user_info = await self._validate_token(token)
        if not user_info:
            logger.warning("认证令牌无效", method=method_name, token=token[:10] + "...")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("认证令牌无效")
            return None
        
        # 将用户信息添加到上下文
        context.user_info = user_info
        logger.debug("用户认证成功", user_id=user_info.get("user_id"), method=method_name)
        
        return await handler(request, context)
    
    def _get_auth_token(self, context) -> Optional[str]:
        """从上下文获取认证令牌"""
        metadata = dict(context.invocation_metadata())
        
        # 从Authorization头获取
        auth_header = metadata.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        # 从自定义头获取
        return metadata.get("x-auth-token", "")
    
    async def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            # 这里应该实现真实的JWT验证逻辑
            # 为了演示，我们返回一个模拟的用户信息
            if token == "valid_token":
                return {
                    "user_id": "test_user",
                    "username": "test",
                    "roles": ["user"]
                }
            return None
        except Exception as e:
            logger.error("令牌验证失败", error=str(e))
            return None


class LoggingMiddleware(Middleware):
    """日志中间件"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.log_request_body = config.get("log_request_body", False)
        self.log_response_body = config.get("log_response_body", False)
        self.excluded_methods = set(config.get("excluded_methods", []))
        
    async def process_request(self, request, context, handler):
        """处理日志记录"""
        if not self.enabled:
            return await handler(request, context)
        
        # 获取方法名
        method_name = context._rpc_event.call_details.method.split('/')[-1]
        
        # 检查是否需要记录日志
        if method_name in self.excluded_methods:
            return await handler(request, context)
        
        # 记录请求开始
        start_time = time.time()
        request_id = self._generate_request_id()
        
        # 获取客户端信息
        client_info = self._get_client_info(context)
        
        # 记录请求日志
        log_data = {
            "request_id": request_id,
            "method": method_name,
            "client_ip": client_info.get("ip"),
            "user_agent": client_info.get("user_agent"),
            "start_time": start_time
        }
        
        if self.log_request_body and hasattr(request, 'user_id'):
            log_data["user_id"] = getattr(request, 'user_id', None)
        
        logger.info("请求开始", **log_data)
        
        try:
            # 处理请求
            response = await handler(request, context)
            
            # 记录成功响应
            duration = time.time() - start_time
            logger.info(
                "请求完成",
                request_id=request_id,
                method=method_name,
                duration_ms=int(duration * 1000),
                status="success"
            )
            
            return response
            
        except Exception as e:
            # 记录错误响应
            duration = time.time() - start_time
            logger.error(
                "请求失败",
                request_id=request_id,
                method=method_name,
                duration_ms=int(duration * 1000),
                status="error",
                error=str(e),
                traceback=traceback.format_exc()
            )
            raise
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_client_info(self, context) -> Dict[str, str]:
        """获取客户端信息"""
        metadata = dict(context.invocation_metadata())
        peer = context.peer()
        
        return {
            "ip": peer.split(":")[-2] if peer else "unknown",
            "user_agent": metadata.get("user-agent", "unknown")
        }


class ErrorHandlingMiddleware(Middleware):
    """错误处理中间件"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.include_traceback = config.get("include_traceback", False)
        
    async def process_request(self, request, context, handler):
        """处理错误"""
        if not self.enabled:
            return await handler(request, context)
        
        try:
            return await handler(request, context)
            
        except grpc.RpcError:
            # gRPC错误直接重新抛出
            raise
            
        except ValueError as e:
            # 参数错误
            logger.warning("参数错误", error=str(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"参数错误: {str(e)}")
            return None
            
        except PermissionError as e:
            # 权限错误
            logger.warning("权限错误", error=str(e))
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("权限不足")
            return None
            
        except FileNotFoundError as e:
            # 资源不存在
            logger.warning("资源不存在", error=str(e))
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("请求的资源不存在")
            return None
            
        except TimeoutError as e:
            # 超时错误
            logger.warning("请求超时", error=str(e))
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("请求处理超时")
            return None
            
        except Exception as e:
            # 其他未知错误
            logger.error("未知错误", error=str(e), traceback=traceback.format_exc())
            context.set_code(grpc.StatusCode.INTERNAL)
            
            if self.include_traceback:
                context.set_details(f"内部错误: {str(e)}\n{traceback.format_exc()}")
            else:
                context.set_details("内部服务错误，请稍后重试")
            
            return None


class MetricsMiddleware(Middleware):
    """指标中间件"""
    
    def __init__(self, metrics_service):
        self.metrics = metrics_service
        
    async def process_request(self, request, context, handler):
        """处理指标收集"""
        method_name = context._rpc_event.call_details.method.split('/')[-1]
        
        # 增加活跃请求数
        self.metrics.inc_gauge("active_requests", labels={"method": method_name})
        
        start_time = time.time()
        
        try:
            # 处理请求
            response = await handler(request, context)
            
            # 记录成功指标
            duration = time.time() - start_time
            self.metrics.inc_counter(
                "requests_total",
                labels={"method": method_name, "status": "success"}
            )
            self.metrics.observe_histogram(
                "request_duration",
                duration,
                labels={"method": method_name}
            )
            
            return response
            
        except Exception as e:
            # 记录错误指标
            duration = time.time() - start_time
            self.metrics.inc_counter(
                "requests_total",
                labels={"method": method_name, "status": "error"}
            )
            self.metrics.observe_histogram(
                "request_duration",
                duration,
                labels={"method": method_name}
            )
            self.metrics.inc_counter(
                "errors_total",
                labels={"error_type": type(e).__name__, "component": "grpc"}
            )
            raise
            
        finally:
            # 减少活跃请求数
            self.metrics.dec_gauge("active_requests", labels={"method": method_name})


class MiddlewareChain:
    """中间件链"""
    
    def __init__(self):
        self.middlewares: List[Middleware] = []
        
    def add_middleware(self, middleware: Middleware):
        """添加中间件"""
        self.middlewares.append(middleware)
        logger.info("中间件已添加", middleware=type(middleware).__name__)
    
    async def process_request(self, request, context, handler):
        """处理请求链"""
        if not self.middlewares:
            return await handler(request, context)
        
        # 创建中间件处理链
        async def create_handler(index: int):
            if index >= len(self.middlewares):
                return handler
            
            middleware = self.middlewares[index]
            next_handler = await create_handler(index + 1)
            
            async def middleware_handler(req, ctx):
                return await middleware.process_request(req, ctx, next_handler)
            
            return middleware_handler
        
        # 执行中间件链
        chain_handler = await create_handler(0)
        return await chain_handler(request, context)


def create_middleware_chain(config: Dict, metrics_service=None) -> MiddlewareChain:
    """创建中间件链"""
    chain = MiddlewareChain()
    
    # 添加日志中间件（最外层）
    logging_config = config.get("logging", {})
    if logging_config.get("enabled", True):
        chain.add_middleware(LoggingMiddleware(logging_config))
    
    # 添加指标中间件
    if metrics_service:
        chain.add_middleware(MetricsMiddleware(metrics_service))
    
    # 添加限流中间件
    rate_limit_config = config.get("rate_limit", {})
    if rate_limit_config.get("enabled", False):
        rate_limit = RateLimitConfig(**rate_limit_config)
        chain.add_middleware(RateLimitMiddleware(rate_limit))
    
    # 添加认证中间件
    auth_config = config.get("authentication", {})
    if auth_config.get("enabled", False):
        chain.add_middleware(AuthenticationMiddleware(auth_config))
    
    # 添加错误处理中间件（最内层）
    error_config = config.get("error_handling", {})
    if error_config.get("enabled", True):
        chain.add_middleware(ErrorHandlingMiddleware(error_config))
    
    logger.info("中间件链创建完成", middleware_count=len(chain.middlewares))
    return chain 