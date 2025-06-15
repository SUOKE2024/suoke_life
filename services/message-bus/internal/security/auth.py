"""
安全机制模块，提供认证和授权功能
"""
import os
import json
import time
import logging
import grpc
import jwt
import requests
from typing import Dict, Any, Optional, Callable, Awaitable, List
from jwt.exceptions import PyJWTError
import asyncio

from config.settings import Settings
from internal.observability.metrics import request_counter

logger = logging.getLogger(__name__)

class AuthError(Exception):
    """认证或授权错误"""
    pass

class AuthInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC服务器认证与授权拦截器
    
    处理请求认证和基于角色的访问控制
    """
    
    def __init__(self, settings):
        """
        初始化认证拦截器
        
        Args:
            settings: 应用程序配置
        """
        self.settings = settings
        self.enable_auth = settings.enable_auth
        
        # 设置方法权限映射(方法名 -> 所需角色列表)
        self.method_permissions = {
            # PublishMessage需要publisher或admin角色
            "/messagebus.MessageBusService/PublishMessage": ["publisher", "admin"],
            
            # 主题管理方法需要admin角色
            "/messagebus.MessageBusService/CreateTopic": ["admin"],
            "/messagebus.MessageBusService/DeleteTopic": ["admin"],
            
            # 读取方法需要基本角色
            "/messagebus.MessageBusService/ListTopics": ["subscriber", "publisher", "admin"],
            "/messagebus.MessageBusService/GetTopic": ["subscriber", "publisher", "admin"],
            "/messagebus.MessageBusService/Subscribe": ["subscriber", "admin"],
            
            # 健康检查不需要认证
            "/messagebus.MessageBusService/HealthCheck": [],
        }
        
        # 将私钥从配置中解析出来 (在实际生产环境中应从安全存储获取)
        # 这里简单使用默认密钥，实际应用中应使用环境变量或Vault等机制
        self.jwt_secret = getattr(settings, 'jwt_secret', 'message-bus-secret-key')
        self.jwt_algorithm = getattr(settings, 'jwt_algorithm', 'HS256')
        self.token_expiry_seconds = getattr(settings, 'token_expiry_seconds', 3600)  # 默认1小时
        
        # 服务间身份验证的服务账户列表
        self.service_accounts = getattr(settings, 'service_accounts', {
            'api-gateway': ["publisher", "subscriber", "admin"],
            'auth-service': ["admin"],
            'health-data-service': ["publisher", "subscriber"]
        })
    
    async def intercept_service(
        self, 
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails
    ) -> Any:
        """
        拦截服务请求进行认证和授权
        
        Args:
            continuation: gRPC继续处理函数
            handler_call_details: 请求详情
            
        Returns:
            处理函数或错误
        """
        # 检查是否启用认证
        if not self.enable_auth:
            # 认证已禁用，直接继续处理
            return await continuation(handler_call_details)
        
        # 获取请求方法
        method_name = handler_call_details.method
        
        # 检查方法是否需要认证 (健康检查等方法可能不需要)
        if method_name in self.method_permissions and not self.method_permissions[method_name]:
            # 此方法不需要认证
            return await continuation(handler_call_details)
        
        # 从元数据中获取授权令牌
        metadata = handler_call_details.invocation_metadata
        auth_token = None
        client_id = "unknown"
        
        try:
            for meta in metadata:
                if meta.key == 'authorization':
                    # 获取授权标头
                    auth_header = meta.value
                    if auth_header.startswith('Bearer '):
                        auth_token = auth_header[7:]  # 移除"Bearer "前缀
                elif meta.key == 'client-id':
                    client_id = meta.value
        except Exception as e:
            logger.error(f"解析元数据时出错: {str(e)}")
        
        try:
            # 检查令牌是否提供
            if not auth_token:
                logger.warning(f"请求未提供认证令牌: {method_name}")
                request_counter.labels(
                    method=method_name.split('/')[-1], 
                    status="unauthorized", 
                    client=client_id
                ).inc()
                return self._unauthenticated_error(f"认证失败: 未提供令牌")
            
            # 验证令牌
            try:
                # 验证JWT令牌
                payload = await self._validate_token(auth_token)
                user_id = payload.get('sub', 'unknown')
                roles = payload.get('roles', [])
                
                # 检查服务间通信
                service_name = payload.get('service_name')
                if service_name and service_name in self.service_accounts:
                    # 这是服务间通信，使用预定义角色
                    roles = self.service_accounts[service_name]
                    logger.debug(f"服务间通信: {service_name}, 角色: {roles}")
                
                # 检查用户是否有权限执行此方法
                if method_name in self.method_permissions:
                    required_roles = self.method_permissions[method_name]
                    if required_roles and not any(role in roles for role in required_roles):
                        # 用户没有所需角色
                        logger.warning(
                            f"用户({user_id})缺少权限执行{method_name}, "
                            f"需要角色: {required_roles}, 拥有角色: {roles}"
                        )
                        request_counter.labels(
                            method=method_name.split('/')[-1], 
                            status="forbidden", 
                            client=client_id
                        ).inc()
                        return self._permission_denied_error(
                            f"权限不足: 需要角色 {required_roles}"
                        )
                
                # 记录认证成功
                logger.debug(f"用户({user_id})已认证访问{method_name}, 角色: {roles}")
                
                # 添加认证信息到上下文
                context = {
                    'user_id': user_id,
                    'roles': roles,
                    'client_id': client_id
                }
                
                # 继续处理请求，使用上下文
                return await self._authenticated_continuation(continuation, handler_call_details, context)
                
            except PyJWTError as e:
                # JWT验证错误
                logger.warning(f"令牌验证失败: {str(e)}")
                request_counter.labels(
                    method=method_name.split('/')[-1], 
                    status="invalid_token", 
                    client=client_id
                ).inc()
                return self._unauthenticated_error(f"认证失败: 无效令牌: {str(e)}")
            
        except Exception as e:
            # 其他错误
            logger.error(f"认证过程中出错: {str(e)}", exc_info=True)
            request_counter.labels(
                method=method_name.split('/')[-1], 
                status="error", 
                client=client_id
            ).inc()
            return self._internal_error(f"认证服务错误: {str(e)}")
    
    async def _validate_token(self, token: str) -> Dict[str, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Dict[str, Any]: 令牌载荷
            
        Raises:
            PyJWTError: 如果令牌无效
        """
        # 令牌验证的核心逻辑
        try:
            # 验证令牌签名和过期时间
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm],
                options={"verify_signature": True, "verify_exp": True}
            )
            return payload
        except PyJWTError as e:
            # 尝试连接到认证服务验证令牌（如果配置了）
            if self.settings.auth_service_url:
                try:
                    # 调用外部认证服务验证令牌
                    return await self._validate_token_with_auth_service(token)
                except Exception as auth_service_error:
                    logger.error(f"调用认证服务失败: {str(auth_service_error)}")
                    # 如果认证服务调用失败，抛出原始错误
                    raise e
            else:
                # 没有配置认证服务，直接抛出错误
                raise
    
    async def _validate_token_with_auth_service(self, token: str) -> Dict[str, Any]:
        """
        通过认证服务验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Dict[str, Any]: 令牌载荷
            
        Raises:
            AuthError: 如果验证失败
        """
        import aiohttp
        
        # 认证服务的URL
        auth_url = f"{self.settings.auth_service_url}/api/auth/validate"
        
        try:
            # 发送请求到认证服务
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    auth_url,
                    json={"token": token},
                    timeout=5,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        # 成功验证
                        result = await response.json()
                        return result["payload"]
                    else:
                        # 验证失败
                        error_data = await response.text()
                        raise AuthError(f"Token validation failed: {error_data}")
        except aiohttp.ClientError as e:
            # 网络错误或超时
            raise AuthError(f"认证服务连接错误: {str(e)}")
    
    @staticmethod
    def _unauthenticated_error(details: str) -> grpc.RpcMethodHandler:
        """
        创建未认证错误响应
        
        Args:
            details: 错误详情
            
        Returns:
            grpc.RpcMethodHandler: 错误处理函数
        """
        async def abort(request, context):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, details)
        
        return grpc.unary_unary_rpc_method_handler(abort)
    
    @staticmethod
    def _permission_denied_error(details: str) -> grpc.RpcMethodHandler:
        """
        创建权限拒绝错误响应
        
        Args:
            details: 错误详情
            
        Returns:
            grpc.RpcMethodHandler: 错误处理函数
        """
        async def abort(request, context):
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, details)
        
        return grpc.unary_unary_rpc_method_handler(abort)
    
    @staticmethod
    def _internal_error(details: str) -> grpc.RpcMethodHandler:
        """
        创建内部错误响应
        
        Args:
            details: 错误详情
            
        Returns:
            grpc.RpcMethodHandler: 错误处理函数
        """
        async def abort(request, context):
            await context.abort(grpc.StatusCode.INTERNAL, details)
        
        return grpc.unary_unary_rpc_method_handler(abort)
    
    @staticmethod
    async def _authenticated_continuation(
        continuation: Callable, 
        handler_call_details: grpc.HandlerCallDetails,
        context: Dict[str, Any]
    ) -> Any:
        """
        认证成功后继续处理请求
        
        Args:
            continuation: gRPC继续处理函数
            handler_call_details: 请求详情
            context: 认证上下文
            
        Returns:
            处理函数
        """
        handler = await continuation(handler_call_details)
        
        # 拦截响应以添加认证上下文
        original_handler = handler
        
        # 定义包装函数
        async def wrapped_handler(request, call):
            # 将认证上下文添加到调用
            for key, value in context.items():
                call.set_value(key, value)
            
            # 调用原始处理函数
            return await original_handler(request, call)
        
        # 替换原始处理函数
        if hasattr(handler, 'unary_unary'):
            handler = grpc.unary_unary_rpc_method_handler(
                wrapped_handler,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )
        elif hasattr(handler, 'unary_stream'):
            handler = grpc.unary_stream_rpc_method_handler(
                wrapped_handler,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )
        # ... 类似地处理其他RPC类型
        
        return handler
    
    @staticmethod
    def generate_token(
        user_id: str, 
        roles: List[str], 
        secret_key: str, 
        algorithm: str = 'HS256',
        expiry_seconds: int = 3600
    ) -> str:
        """
        生成JWT令牌
        
        Args:
            user_id: 用户ID
            roles: 角色列表
            secret_key: 密钥
            algorithm: 算法
            expiry_seconds: 过期时间(秒)
            
        Returns:
            str: JWT令牌
        """
        payload = {
            'sub': user_id,
            'roles': roles,
            'iat': int(time.time()),
            'exp': int(time.time()) + expiry_seconds
        }
        
        return jwt.encode(payload, secret_key, algorithm=algorithm)
    
    @staticmethod
    def generate_service_token(
        service_name: str,
        secret_key: str,
        algorithm: str = 'HS256',
        expiry_seconds: int = 3600
    ) -> str:
        """
        生成服务间认证令牌
        
        Args:
            service_name: 服务名称
            secret_key: 密钥
            algorithm: 算法
            expiry_seconds: 过期时间(秒)
            
        Returns:
            str: JWT令牌
        """
        payload = {
            'sub': f"service:{service_name}",
            'service_name': service_name,
            'iat': int(time.time()),
            'exp': int(time.time()) + expiry_seconds
        }
        
        return jwt.encode(payload, secret_key, algorithm=algorithm) 