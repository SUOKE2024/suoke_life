#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API网关集成服务 - 与其他微服务进行通信和数据交换
"""

import asyncio
import json
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
import aiohttp
import grpc
import websockets
from prometheus_client import Counter, Histogram, Gauge
import jwt
from cryptography.fernet import Fernet

class ServiceType(Enum):
    """服务类型"""
    AUTH_SERVICE = "auth-service"                    # 认证服务
    USER_SERVICE = "user-service"                    # 用户服务
    MEDICAL_SERVICE = "medical-service"              # 医疗服务
    HEALTH_DATA_SERVICE = "health-data-service"      # 健康数据服务
    MESSAGE_BUS = "message-bus"                      # 消息总线
    BLOCKCHAIN_SERVICE = "blockchain-service"        # 区块链服务
    ACCESSIBILITY_SERVICE = "accessibility-service"  # 无障碍服务
    AGENT_SERVICES = "agent-services"                # 智能体服务
    DIAGNOSTIC_SERVICES = "diagnostic-services"      # 诊断服务
    MED_KNOWLEDGE = "med-knowledge"                  # 医学知识库

class CommunicationProtocol(Enum):
    """通信协议"""
    HTTP_REST = "http_rest"      # HTTP REST API
    GRPC = "grpc"               # gRPC
    WEBSOCKET = "websocket"     # WebSocket
    MESSAGE_QUEUE = "mq"        # 消息队列
    GRAPHQL = "graphql"         # GraphQL

class RequestMethod(Enum):
    """请求方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class AuthType(Enum):
    """认证类型"""
    NONE = "none"               # 无认证
    API_KEY = "api_key"         # API密钥
    JWT = "jwt"                 # JWT令牌
    OAUTH2 = "oauth2"           # OAuth2
    BASIC = "basic"             # 基础认证
    CUSTOM = "custom"           # 自定义认证

@dataclass
class ServiceEndpoint:
    """服务端点"""
    service_type: ServiceType
    protocol: CommunicationProtocol
    host: str
    port: int
    path: str = ""
    auth_type: AuthType = AuthType.NONE
    auth_config: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    rate_limit: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceRequest:
    """服务请求"""
    request_id: str
    service_type: ServiceType
    endpoint: str
    method: RequestMethod
    data: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None
    retry_count: Optional[int] = None
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    trace_id: Optional[str] = None

@dataclass
class ServiceResponse:
    """服务响应"""
    request_id: str
    service_type: ServiceType
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    trace_id: Optional[str] = None

@dataclass
class CircuitBreakerState:
    """断路器状态"""
    service_type: ServiceType
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_duration: timedelta = timedelta(minutes=1)

class APIGatewayService:
    """API网关集成服务"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化API网关服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 服务端点配置
        self.endpoints: Dict[ServiceType, ServiceEndpoint] = {}
        
        # HTTP客户端会话
        self.http_session: Optional[aiohttp.ClientSession] = None
        
        # gRPC通道
        self.grpc_channels: Dict[ServiceType, grpc.aio.Channel] = {}
        
        # WebSocket连接
        self.websocket_connections: Dict[ServiceType, websockets.WebSocketClientProtocol] = {}
        
        # Redis连接
        self.redis_client = None
        
        # 断路器状态
        self.circuit_breakers: Dict[ServiceType, CircuitBreakerState] = {}
        
        # 请求队列
        self.request_queue = asyncio.Queue()
        
        # 响应缓存
        self.response_cache: Dict[str, ServiceResponse] = {}
        
        # 速率限制器
        self.rate_limiters: Dict[ServiceType, Dict[str, Any]] = {}
        
        # 认证信息
        self.auth_tokens: Dict[ServiceType, Dict[str, Any]] = {}
        
        # 加密器
        self.encryptor = None
        
        # 监控指标
        self.metrics = {
            "requests_total": Counter('api_gateway_requests_total', 'Total requests', ['service', 'method', 'status']),
            "request_duration": Histogram('api_gateway_request_duration_seconds', 'Request duration', ['service', 'method']),
            "active_connections": Gauge('api_gateway_active_connections', 'Active connections', ['service', 'protocol']),
            "circuit_breaker_state": Gauge('api_gateway_circuit_breaker_state', 'Circuit breaker state', ['service']),
            "cache_hits": Counter('api_gateway_cache_hits_total', 'Cache hits', ['service']),
            "cache_misses": Counter('api_gateway_cache_misses_total', 'Cache misses', ['service'])
        }
        
        # 事件回调
        self.event_callbacks: Dict[str, List[Callable]] = {
            "request_sent": [],
            "response_received": [],
            "error_occurred": [],
            "circuit_breaker_opened": [],
            "circuit_breaker_closed": [],
            "rate_limit_exceeded": []
        }
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "requests_by_service": {},
            "errors_by_service": {},
            "cache_hit_rate": 0.0
        }
    
    async def initialize(self):
        """初始化API网关服务"""
        logger.info("Initializing API gateway service")
        
        # 初始化加密器
        encryption_key = self.config.get('encryption_key')
        if encryption_key:
            self.encryptor = Fernet(encryption_key.encode())
        
        # 初始化Redis
        await self._init_redis()
        
        # 初始化HTTP会话
        await self._init_http_session()
        
        # 加载服务端点配置
        await self._load_service_endpoints()
        
        # 初始化断路器
        await self._init_circuit_breakers()
        
        # 启动后台任务
        asyncio.create_task(self._request_processor())
        asyncio.create_task(self._health_checker())
        asyncio.create_task(self._cache_cleaner())
        asyncio.create_task(self._metrics_collector())
        
        logger.info("API gateway service initialized successfully")
    
    async def _init_redis(self):
        """初始化Redis"""
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 2),
            decode_responses=True
        )
    
    async def _init_http_session(self):
        """初始化HTTP会话"""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            keepalive_timeout=30
        )
        
        self.http_session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'SuokeLife-RAG-Service/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
    
    async def _load_service_endpoints(self):
        """加载服务端点配置"""
        endpoints_config = self.config.get('service_endpoints', {})
        
        for service_name, endpoint_config in endpoints_config.items():
            try:
                service_type = ServiceType(service_name)
                protocol = CommunicationProtocol(endpoint_config.get('protocol', 'http_rest'))
                auth_type = AuthType(endpoint_config.get('auth_type', 'none'))
                
                endpoint = ServiceEndpoint(
                    service_type=service_type,
                    protocol=protocol,
                    host=endpoint_config['host'],
                    port=endpoint_config['port'],
                    path=endpoint_config.get('path', ''),
                    auth_type=auth_type,
                    auth_config=endpoint_config.get('auth_config', {}),
                    timeout=endpoint_config.get('timeout', 30.0),
                    retry_count=endpoint_config.get('retry_count', 3),
                    circuit_breaker_enabled=endpoint_config.get('circuit_breaker_enabled', True),
                    rate_limit=endpoint_config.get('rate_limit'),
                    metadata=endpoint_config.get('metadata', {})
                )
                
                self.endpoints[service_type] = endpoint
                logger.info(f"Loaded endpoint for {service_name}: {endpoint.host}:{endpoint.port}")
                
            except Exception as e:
                logger.error(f"Error loading endpoint for {service_name}: {e}")
    
    async def _init_circuit_breakers(self):
        """初始化断路器"""
        for service_type in self.endpoints.keys():
            self.circuit_breakers[service_type] = CircuitBreakerState(
                service_type=service_type,
                failure_threshold=self.config.get('circuit_breaker', {}).get('failure_threshold', 5),
                success_threshold=self.config.get('circuit_breaker', {}).get('success_threshold', 3),
                timeout_duration=timedelta(
                    seconds=self.config.get('circuit_breaker', {}).get('timeout_seconds', 60)
                )
            )
    
    async def send_request(
        self,
        service_type: ServiceType,
        endpoint: str,
        method: RequestMethod = RequestMethod.GET,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retry_count: Optional[int] = None,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        use_cache: bool = True
    ) -> ServiceResponse:
        """
        发送请求到指定服务
        
        Args:
            service_type: 服务类型
            endpoint: 端点路径
            method: 请求方法
            data: 请求数据
            headers: 请求头
            params: 查询参数
            timeout: 超时时间
            retry_count: 重试次数
            user_id: 用户ID
            trace_id: 追踪ID
            use_cache: 是否使用缓存
            
        Returns:
            服务响应
        """
        request_id = str(uuid.uuid4())
        trace_id = trace_id or str(uuid.uuid4())
        
        # 创建请求对象
        request = ServiceRequest(
            request_id=request_id,
            service_type=service_type,
            endpoint=endpoint,
            method=method,
            data=data,
            headers=headers or {},
            params=params or {},
            timeout=timeout,
            retry_count=retry_count,
            user_id=user_id,
            trace_id=trace_id
        )
        
        # 检查缓存
        if use_cache and method == RequestMethod.GET:
            cache_key = self._generate_cache_key(request)
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                self.metrics["cache_hits"].labels(service=service_type.value).inc()
                return cached_response
            else:
                self.metrics["cache_misses"].labels(service=service_type.value).inc()
        
        # 检查断路器状态
        if not await self._check_circuit_breaker(service_type):
            return ServiceResponse(
                request_id=request_id,
                service_type=service_type,
                status_code=503,
                error="Service unavailable - circuit breaker open",
                trace_id=trace_id
            )
        
        # 检查速率限制
        if not await self._check_rate_limit(service_type, user_id):
            await self._trigger_event("rate_limit_exceeded", {"service": service_type, "user_id": user_id})
            return ServiceResponse(
                request_id=request_id,
                service_type=service_type,
                status_code=429,
                error="Rate limit exceeded",
                trace_id=trace_id
            )
        
        # 发送请求
        start_time = time.time()
        
        try:
            response = await self._execute_request(request)
            response_time = time.time() - start_time
            response.response_time = response_time
            
            # 更新断路器状态
            await self._update_circuit_breaker(service_type, success=response.status_code < 400)
            
            # 缓存响应
            if use_cache and method == RequestMethod.GET and response.status_code == 200:
                cache_key = self._generate_cache_key(request)
                await self._cache_response(cache_key, response)
            
            # 更新指标
            self.metrics["requests_total"].labels(
                service=service_type.value,
                method=method.value,
                status=str(response.status_code)
            ).inc()
            
            self.metrics["request_duration"].labels(
                service=service_type.value,
                method=method.value
            ).observe(response_time)
            
            # 触发事件
            await self._trigger_event("response_received", {"request": request, "response": response})
            
            # 更新统计信息
            self.stats["total_requests"] += 1
            if response.status_code < 400:
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            self.stats["requests_by_service"][service_type.value] = \
                self.stats["requests_by_service"].get(service_type.value, 0) + 1
            
            if response.status_code >= 400:
                self.stats["errors_by_service"][service_type.value] = \
                    self.stats["errors_by_service"].get(service_type.value, 0) + 1
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Error executing request {request_id}: {e}")
            
            # 更新断路器状态
            await self._update_circuit_breaker(service_type, success=False)
            
            # 创建错误响应
            error_response = ServiceResponse(
                request_id=request_id,
                service_type=service_type,
                status_code=500,
                error=str(e),
                response_time=response_time,
                trace_id=trace_id
            )
            
            # 触发事件
            await self._trigger_event("error_occurred", {"request": request, "error": str(e)})
            
            # 更新统计信息
            self.stats["total_requests"] += 1
            self.stats["failed_requests"] += 1
            self.stats["errors_by_service"][service_type.value] = \
                self.stats["errors_by_service"].get(service_type.value, 0) + 1
            
            return error_response
    
    async def _execute_request(self, request: ServiceRequest) -> ServiceResponse:
        """执行请求"""
        endpoint_config = self.endpoints.get(request.service_type)
        if not endpoint_config:
            raise ValueError(f"No endpoint configured for service: {request.service_type}")
        
        # 根据协议类型执行请求
        if endpoint_config.protocol == CommunicationProtocol.HTTP_REST:
            return await self._execute_http_request(request, endpoint_config)
        elif endpoint_config.protocol == CommunicationProtocol.GRPC:
            return await self._execute_grpc_request(request, endpoint_config)
        elif endpoint_config.protocol == CommunicationProtocol.WEBSOCKET:
            return await self._execute_websocket_request(request, endpoint_config)
        elif endpoint_config.protocol == CommunicationProtocol.MESSAGE_QUEUE:
            return await self._execute_mq_request(request, endpoint_config)
        else:
            raise ValueError(f"Unsupported protocol: {endpoint_config.protocol}")
    
    async def _execute_http_request(
        self,
        request: ServiceRequest,
        endpoint_config: ServiceEndpoint
    ) -> ServiceResponse:
        """执行HTTP请求"""
        # 构建URL
        url = f"http://{endpoint_config.host}:{endpoint_config.port}"
        if endpoint_config.path:
            url += f"/{endpoint_config.path.lstrip('/')}"
        if request.endpoint:
            url += f"/{request.endpoint.lstrip('/')}"
        
        # 准备请求头
        headers = request.headers.copy()
        
        # 添加认证信息
        await self._add_authentication(headers, endpoint_config, request.user_id)
        
        # 添加追踪信息
        if request.trace_id:
            headers['X-Trace-ID'] = request.trace_id
        
        # 设置超时
        timeout = request.timeout or endpoint_config.timeout
        
        # 执行请求
        async with self.http_session.request(
            method=request.method.value,
            url=url,
            json=request.data,
            headers=headers,
            params=request.params,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            
            response_data = None
            if response.content_type == 'application/json':
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
            else:
                response_data = {"text": await response.text()}
            
            return ServiceResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status_code=response.status,
                data=response_data,
                headers=dict(response.headers),
                trace_id=request.trace_id
            )
    
    async def _execute_grpc_request(
        self,
        request: ServiceRequest,
        endpoint_config: ServiceEndpoint
    ) -> ServiceResponse:
        """执行gRPC请求"""
        # 这里需要根据具体的gRPC服务定义来实现
        # 暂时返回一个模拟响应
        return ServiceResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status_code=200,
            data={"message": "gRPC request executed"},
            trace_id=request.trace_id
        )
    
    async def _execute_websocket_request(
        self,
        request: ServiceRequest,
        endpoint_config: ServiceEndpoint
    ) -> ServiceResponse:
        """执行WebSocket请求"""
        # 这里需要根据具体的WebSocket协议来实现
        # 暂时返回一个模拟响应
        return ServiceResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status_code=200,
            data={"message": "WebSocket request executed"},
            trace_id=request.trace_id
        )
    
    async def _execute_mq_request(
        self,
        request: ServiceRequest,
        endpoint_config: ServiceEndpoint
    ) -> ServiceResponse:
        """执行消息队列请求"""
        # 这里需要根据具体的消息队列实现
        # 暂时返回一个模拟响应
        return ServiceResponse(
            request_id=request.request_id,
            service_type=request.service_type,
            status_code=200,
            data={"message": "Message queue request executed"},
            trace_id=request.trace_id
        )
    
    async def _add_authentication(
        self,
        headers: Dict[str, str],
        endpoint_config: ServiceEndpoint,
        user_id: Optional[str] = None
    ):
        """添加认证信息"""
        if endpoint_config.auth_type == AuthType.NONE:
            return
        
        elif endpoint_config.auth_type == AuthType.API_KEY:
            api_key = endpoint_config.auth_config.get('api_key')
            if api_key:
                headers['X-API-Key'] = api_key
        
        elif endpoint_config.auth_type == AuthType.JWT:
            token = await self._get_jwt_token(endpoint_config.service_type, user_id)
            if token:
                headers['Authorization'] = f'Bearer {token}'
        
        elif endpoint_config.auth_type == AuthType.BASIC:
            username = endpoint_config.auth_config.get('username')
            password = endpoint_config.auth_config.get('password')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
        
        elif endpoint_config.auth_type == AuthType.OAUTH2:
            token = await self._get_oauth2_token(endpoint_config.service_type)
            if token:
                headers['Authorization'] = f'Bearer {token}'
    
    async def _get_jwt_token(self, service_type: ServiceType, user_id: Optional[str] = None) -> Optional[str]:
        """获取JWT令牌"""
        # 检查缓存的令牌
        cache_key = f"jwt_token:{service_type.value}:{user_id or 'system'}"
        cached_token = await self.redis_client.get(cache_key)
        
        if cached_token:
            # 验证令牌是否过期
            try:
                payload = jwt.decode(cached_token, options={"verify_signature": False})
                if payload.get('exp', 0) > time.time():
                    return cached_token
            except:
                pass
        
        # 生成新令牌
        endpoint_config = self.endpoints.get(service_type)
        if not endpoint_config:
            return None
        
        secret_key = endpoint_config.auth_config.get('secret_key')
        if not secret_key:
            return None
        
        payload = {
            'service': service_type.value,
            'user_id': user_id,
            'iat': time.time(),
            'exp': time.time() + 3600  # 1小时过期
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        # 缓存令牌
        await self.redis_client.setex(cache_key, 3600, token)
        
        return token
    
    async def _get_oauth2_token(self, service_type: ServiceType) -> Optional[str]:
        """获取OAuth2令牌"""
        # 这里需要实现OAuth2流程
        # 暂时返回None
        return None
    
    async def _check_circuit_breaker(self, service_type: ServiceType) -> bool:
        """检查断路器状态"""
        breaker = self.circuit_breakers.get(service_type)
        if not breaker or not self.endpoints[service_type].circuit_breaker_enabled:
            return True
        
        now = datetime.now()
        
        if breaker.state == "OPEN":
            if breaker.next_attempt_time and now >= breaker.next_attempt_time:
                # 转换到半开状态
                breaker.state = "HALF_OPEN"
                breaker.success_count = 0
                logger.info(f"Circuit breaker for {service_type.value} changed to HALF_OPEN")
                return True
            else:
                return False
        
        return True
    
    async def _update_circuit_breaker(self, service_type: ServiceType, success: bool):
        """更新断路器状态"""
        breaker = self.circuit_breakers.get(service_type)
        if not breaker or not self.endpoints[service_type].circuit_breaker_enabled:
            return
        
        now = datetime.now()
        
        if success:
            breaker.failure_count = 0
            
            if breaker.state == "HALF_OPEN":
                breaker.success_count += 1
                if breaker.success_count >= breaker.success_threshold:
                    # 转换到关闭状态
                    breaker.state = "CLOSED"
                    breaker.success_count = 0
                    logger.info(f"Circuit breaker for {service_type.value} changed to CLOSED")
                    await self._trigger_event("circuit_breaker_closed", {"service": service_type})
        else:
            breaker.failure_count += 1
            breaker.last_failure_time = now
            
            if breaker.state in ["CLOSED", "HALF_OPEN"] and breaker.failure_count >= breaker.failure_threshold:
                # 转换到开启状态
                breaker.state = "OPEN"
                breaker.next_attempt_time = now + breaker.timeout_duration
                logger.warning(f"Circuit breaker for {service_type.value} changed to OPEN")
                await self._trigger_event("circuit_breaker_opened", {"service": service_type})
        
        # 更新指标
        state_value = {"CLOSED": 0, "HALF_OPEN": 1, "OPEN": 2}.get(breaker.state, 0)
        self.metrics["circuit_breaker_state"].labels(service=service_type.value).set(state_value)
    
    async def _check_rate_limit(self, service_type: ServiceType, user_id: Optional[str] = None) -> bool:
        """检查速率限制"""
        endpoint_config = self.endpoints.get(service_type)
        if not endpoint_config or not endpoint_config.rate_limit:
            return True
        
        # 使用滑动窗口算法
        key = f"rate_limit:{service_type.value}:{user_id or 'anonymous'}"
        window_size = 60  # 1分钟窗口
        
        now = time.time()
        window_start = now - window_size
        
        # 清理过期的请求记录
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # 获取当前窗口内的请求数
        current_count = await self.redis_client.zcard(key)
        
        if current_count >= endpoint_config.rate_limit:
            return False
        
        # 记录当前请求
        await self.redis_client.zadd(key, {str(uuid.uuid4()): now})
        await self.redis_client.expire(key, window_size)
        
        return True
    
    def _generate_cache_key(self, request: ServiceRequest) -> str:
        """生成缓存键"""
        key_parts = [
            request.service_type.value,
            request.endpoint,
            request.method.value
        ]
        
        if request.params:
            params_str = "&".join(f"{k}={v}" for k, v in sorted(request.params.items()))
            key_parts.append(params_str)
        
        if request.data:
            data_str = json.dumps(request.data, sort_keys=True)
            key_parts.append(data_str)
        
        return "cache:" + ":".join(key_parts)
    
    async def _get_cached_response(self, cache_key: str) -> Optional[ServiceResponse]:
        """获取缓存的响应"""
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                response_dict = json.loads(cached_data)
                response = ServiceResponse(**response_dict)
                return response
        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: ServiceResponse):
        """缓存响应"""
        try:
            # 设置缓存过期时间
            cache_ttl = self.config.get('cache_ttl', 300)  # 默认5分钟
            
            # 序列化响应
            response_dict = {
                "request_id": response.request_id,
                "service_type": response.service_type.value,
                "status_code": response.status_code,
                "data": response.data,
                "error": response.error,
                "headers": response.headers,
                "response_time": response.response_time,
                "timestamp": response.timestamp.isoformat(),
                "trace_id": response.trace_id
            }
            
            cached_data = json.dumps(response_dict)
            await self.redis_client.setex(cache_key, cache_ttl, cached_data)
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
    
    async def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """触发事件"""
        callbacks = self.event_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                await callback(data)
            except Exception as e:
                logger.error(f"Error in event callback for {event_type}: {e}")
    
    async def _request_processor(self):
        """请求处理器"""
        while True:
            try:
                # 这里可以实现请求队列处理逻辑
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in request processor: {e}")
                await asyncio.sleep(5)
    
    async def _health_checker(self):
        """健康检查器"""
        while True:
            try:
                for service_type, endpoint_config in self.endpoints.items():
                    try:
                        # 发送健康检查请求
                        health_response = await self.send_request(
                            service_type=service_type,
                            endpoint="health",
                            method=RequestMethod.GET,
                            timeout=5.0,
                            use_cache=False
                        )
                        
                        # 更新服务状态
                        is_healthy = health_response.status_code == 200
                        await self.redis_client.setex(
                            f"service_health:{service_type.value}",
                            60,
                            "healthy" if is_healthy else "unhealthy"
                        )
                        
                    except Exception as e:
                        logger.error(f"Health check failed for {service_type.value}: {e}")
                        await self.redis_client.setex(
                            f"service_health:{service_type.value}",
                            60,
                            "unhealthy"
                        )
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"Error in health checker: {e}")
                await asyncio.sleep(30)
    
    async def _cache_cleaner(self):
        """缓存清理器"""
        while True:
            try:
                # 清理过期的缓存
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor=cursor,
                        match="cache:*",
                        count=100
                    )
                    
                    if keys:
                        # 检查键是否过期
                        for key in keys:
                            ttl = await self.redis_client.ttl(key)
                            if ttl == -1:  # 没有设置过期时间
                                await self.redis_client.expire(key, 300)  # 设置默认过期时间
                    
                    if cursor == 0:
                        break
                
                await asyncio.sleep(3600)  # 每小时清理一次
                
            except Exception as e:
                logger.error(f"Error in cache cleaner: {e}")
                await asyncio.sleep(3600)
    
    async def _metrics_collector(self):
        """指标收集器"""
        while True:
            try:
                # 更新平均响应时间
                if self.stats["total_requests"] > 0:
                    # 这里可以从历史数据计算平均响应时间
                    pass
                
                # 更新缓存命中率
                total_cache_requests = sum(
                    self.metrics["cache_hits"]._value.values()
                ) + sum(
                    self.metrics["cache_misses"]._value.values()
                )
                
                if total_cache_requests > 0:
                    cache_hits = sum(self.metrics["cache_hits"]._value.values())
                    self.stats["cache_hit_rate"] = cache_hits / total_cache_requests
                
                await asyncio.sleep(60)  # 每分钟更新一次
                
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(60)
    
    async def get_service_health(self, service_type: ServiceType) -> Dict[str, Any]:
        """获取服务健康状态"""
        health_status = await self.redis_client.get(f"service_health:{service_type.value}")
        
        breaker = self.circuit_breakers.get(service_type)
        breaker_state = breaker.state if breaker else "UNKNOWN"
        
        return {
            "service": service_type.value,
            "health_status": health_status or "unknown",
            "circuit_breaker_state": breaker_state,
            "last_check": datetime.now().isoformat()
        }
    
    async def get_all_services_health(self) -> Dict[str, Any]:
        """获取所有服务的健康状态"""
        health_status = {}
        
        for service_type in self.endpoints.keys():
            health_status[service_type.value] = await self.get_service_health(service_type)
        
        return {
            "services": health_status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": (
                self.stats["successful_requests"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0 else 0
            ),
            "average_response_time": self.stats["average_response_time"],
            "cache_hit_rate": self.stats["cache_hit_rate"],
            "requests_by_service": self.stats["requests_by_service"],
            "errors_by_service": self.stats["errors_by_service"],
            "active_endpoints": len(self.endpoints),
            "timestamp": datetime.now().isoformat()
        }
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """添加事件回调"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def remove_event_callback(self, event_type: str, callback: Callable):
        """移除事件回调"""
        if event_type in self.event_callbacks and callback in self.event_callbacks[event_type]:
            self.event_callbacks[event_type].remove(callback)
    
    async def invalidate_cache(self, pattern: str = "*"):
        """清除缓存"""
        cursor = 0
        deleted_count = 0
        
        while True:
            cursor, keys = await self.redis_client.scan(
                cursor=cursor,
                match=f"cache:{pattern}",
                count=100
            )
            
            if keys:
                deleted_count += await self.redis_client.delete(*keys)
            
            if cursor == 0:
                break
        
        logger.info(f"Invalidated {deleted_count} cache entries matching pattern: {pattern}")
        return deleted_count
    
    async def close(self):
        """关闭API网关服务"""
        logger.info("Closing API gateway service")
        
        # 关闭HTTP会话
        if self.http_session:
            await self.http_session.close()
        
        # 关闭gRPC通道
        for channel in self.grpc_channels.values():
            await channel.close()
        
        # 关闭WebSocket连接
        for ws in self.websocket_connections.values():
            await ws.close()
        
        # 关闭Redis连接
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("API gateway service closed") 