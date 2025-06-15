#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API网关集成模块
支持与其他服务的通信、协调和数据交换
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import grpc
from loguru import logger

from ..observability.metrics import MetricsCollector
from ..resilience.circuit_breaker import CircuitBreakerService


class ServiceType(str, Enum):
    """服务类型"""
    AUTH_SERVICE = "auth-service"                    # 认证服务
    USER_SERVICE = "user-service"                    # 用户服务
    MEDICAL_SERVICE = "medical-service"              # 医疗服务
    HEALTH_DATA_SERVICE = "health-data-service"      # 健康数据服务
    MESSAGE_BUS = "message-bus"                      # 消息总线
    BLOCKCHAIN_SERVICE = "blockchain-service"        # 区块链服务
    ACCESSIBILITY_SERVICE = "accessibility-service"  # 无障碍服务
    AGENT_SERVICES = "agent-services"                # 智能体服务
    MED_KNOWLEDGE = "med-knowledge"                  # 医学知识库


class CommunicationProtocol(str, Enum):
    """通信协议"""
    HTTP_REST = "http_rest"      # HTTP REST API
    GRPC = "grpc"               # gRPC
    WEBSOCKET = "websocket"     # WebSocket
    MESSAGE_QUEUE = "message_queue"  # 消息队列


class RequestType(str, Enum):
    """请求类型"""
    SYNC = "sync"               # 同步请求
    ASYNC = "async"             # 异步请求
    STREAMING = "streaming"     # 流式请求
    BATCH = "batch"             # 批量请求


@dataclass
class ServiceEndpoint:
    """服务端点"""
    service_type: ServiceType
    protocol: CommunicationProtocol
    host: str
    port: int
    path: str = ""
    timeout: float = 30.0
    retry_count: int = 3
    health_check_path: str = "/health"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceRequest:
    """服务请求"""
    request_id: str
    service_type: ServiceType
    endpoint: str
    method: str = "POST"
    data: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    request_type: RequestType = RequestType.SYNC
    priority: int = 1  # 1-10, 10最高
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceResponse:
    """服务响应"""
    request_id: str
    service_type: ServiceType
    status_code: int
    data: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """服务健康状态"""
    service_type: ServiceType
    status: str  # healthy, unhealthy, degraded
    response_time: float
    last_check: float
    error_count: int = 0
    success_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceRegistry:
    """服务注册表"""
    
    def __init__(self):
        self.services = self._initialize_services()
        self.health_status = {}
        self.load_balancer = LoadBalancer()
    
    def _initialize_services(self) -> Dict[ServiceType, List[ServiceEndpoint]]:
        """初始化服务端点"""
        return {
            ServiceType.AUTH_SERVICE: [
                ServiceEndpoint(
                    service_type=ServiceType.AUTH_SERVICE,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="auth-service",
                    port=8001,
                    path="/api/v1",
                    health_check_path="/health"
                ),
                ServiceEndpoint(
                    service_type=ServiceType.AUTH_SERVICE,
                    protocol=CommunicationProtocol.GRPC,
                    host="auth-service",
                    port=9001,
                    path="/auth.AuthService"
                )
            ],
            
            ServiceType.USER_SERVICE: [
                ServiceEndpoint(
                    service_type=ServiceType.USER_SERVICE,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="user-service",
                    port=8002,
                    path="/api/v1",
                    health_check_path="/health"
                ),
                ServiceEndpoint(
                    service_type=ServiceType.USER_SERVICE,
                    protocol=CommunicationProtocol.GRPC,
                    host="user-service",
                    port=9002,
                    path="/user.UserService"
                )
            ],
            
            ServiceType.MEDICAL_SERVICE: [
                ServiceEndpoint(
                    service_type=ServiceType.MEDICAL_SERVICE,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="medical-service",
                    port=8003,
                    path="/api/v1",
                    health_check_path="/health"
                ),
                ServiceEndpoint(
                    service_type=ServiceType.MEDICAL_SERVICE,
                    protocol=CommunicationProtocol.GRPC,
                    host="medical-service",
                    port=9003,
                    path="/medical.MedicalService"
                )
            ],
            
            ServiceType.HEALTH_DATA_SERVICE: [
                ServiceEndpoint(
                    service_type=ServiceType.HEALTH_DATA_SERVICE,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="health-data-service",
                    port=8004,
                    path="/api/v1",
                    health_check_path="/health"
                ),
                ServiceEndpoint(
                    service_type=ServiceType.HEALTH_DATA_SERVICE,
                    protocol=CommunicationProtocol.GRPC,
                    host="health-data-service",
                    port=9004,
                    path="/healthdata.HealthDataService"
                )
            ],
            
            ServiceType.MESSAGE_BUS: [
                ServiceEndpoint(
                    service_type=ServiceType.MESSAGE_BUS,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="message-bus",
                    port=8005,
                    path="/api/v1",
                    health_check_path="/health"
                ),
                ServiceEndpoint(
                    service_type=ServiceType.MESSAGE_BUS,
                    protocol=CommunicationProtocol.GRPC,
                    host="message-bus",
                    port=9005,
                    path="/messagebus.MessageBusService"
                )
            ],
            
            ServiceType.BLOCKCHAIN_SERVICE: [
                ServiceEndpoint(
                    service_type=ServiceType.BLOCKCHAIN_SERVICE,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="blockchain-service",
                    port=8006,
                    path="/api/v1",
                    health_check_path="/health"
                )
            ],
            
            ServiceType.ACCESSIBILITY_SERVICE: [
                ServiceEndpoint(
                    service_type=ServiceType.ACCESSIBILITY_SERVICE,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="accessibility-service",
                    port=8007,
                    path="/api/v1",
                    health_check_path="/health"
                )
            ],
            
            ServiceType.AGENT_SERVICES: [
                ServiceEndpoint(
                    service_type=ServiceType.AGENT_SERVICES,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="xiaoai-service",
                    port=8101,
                    path="/api/v1",
                    metadata={"agent": "xiaoai"}
                ),
                ServiceEndpoint(
                    service_type=ServiceType.AGENT_SERVICES,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="xiaoke-service",
                    port=8102,
                    path="/api/v1",
                    metadata={"agent": "xiaoke"}
                ),
                ServiceEndpoint(
                    service_type=ServiceType.AGENT_SERVICES,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="laoke-service",
                    port=8103,
                    path="/api/v1",
                    metadata={"agent": "laoke"}
                ),
                ServiceEndpoint(
                    service_type=ServiceType.AGENT_SERVICES,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="soer-service",
                    port=8104,
                    path="/api/v1",
                    metadata={"agent": "soer"}
                )
            ],
            
            ServiceType.MED_KNOWLEDGE: [
                ServiceEndpoint(
                    service_type=ServiceType.MED_KNOWLEDGE,
                    protocol=CommunicationProtocol.HTTP_REST,
                    host="med-knowledge",
                    port=8008,
                    path="/api/v1",
                    health_check_path="/health"
                )
            ]
        }
    
    def get_service_endpoints(
        self,
        service_type: ServiceType,
        protocol: Optional[CommunicationProtocol] = None
    ) -> List[ServiceEndpoint]:
        """获取服务端点"""
        endpoints = self.services.get(service_type, [])
        
        if protocol:
            endpoints = [ep for ep in endpoints if ep.protocol == protocol]
        
        return endpoints
    
    def get_healthy_endpoint(
        self,
        service_type: ServiceType,
        protocol: Optional[CommunicationProtocol] = None
    ) -> Optional[ServiceEndpoint]:
        """获取健康的服务端点"""
        endpoints = self.get_service_endpoints(service_type, protocol)
        
        # 过滤健康的端点
        healthy_endpoints = []
        for endpoint in endpoints:
            health = self.health_status.get(f"{endpoint.host}:{endpoint.port}")
            if health and health.status == "healthy":
                healthy_endpoints.append(endpoint)
        
        if not healthy_endpoints:
            # 如果没有健康的端点，返回第一个可用的
            return endpoints[0] if endpoints else None
        
        # 使用负载均衡器选择端点
        return self.load_balancer.select_endpoint(healthy_endpoints)
    
    def update_health_status(self, endpoint: ServiceEndpoint, health: ServiceHealth):
        """更新健康状态"""
        key = f"{endpoint.host}:{endpoint.port}"
        self.health_status[key] = health
    
    def get_agent_endpoint(self, agent_name: str) -> Optional[ServiceEndpoint]:
        """获取特定智能体的端点"""
        agent_endpoints = self.get_service_endpoints(ServiceType.AGENT_SERVICES)
        
        for endpoint in agent_endpoints:
            if endpoint.metadata.get("agent") == agent_name:
                return endpoint
        
        return None


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.round_robin_counters = {}
    
    def select_endpoint(self, endpoints: List[ServiceEndpoint]) -> Optional[ServiceEndpoint]:
        """选择端点"""
        if not endpoints:
            return None
        
        if len(endpoints) == 1:
            return endpoints[0]
        
        if self.strategy == "round_robin":
            return self._round_robin_select(endpoints)
        elif self.strategy == "random":
            return self._random_select(endpoints)
        elif self.strategy == "least_connections":
            return self._least_connections_select(endpoints)
        else:
            return endpoints[0]
    
    def _round_robin_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """轮询选择"""
        key = str(sorted([f"{ep.host}:{ep.port}" for ep in endpoints]))
        
        if key not in self.round_robin_counters:
            self.round_robin_counters[key] = 0
        
        index = self.round_robin_counters[key] % len(endpoints)
        self.round_robin_counters[key] += 1
        
        return endpoints[index]
    
    def _random_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """随机选择"""
        import random
        return random.choice(endpoints)
    
    def _least_connections_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """最少连接选择"""
        # 简化实现，实际应该跟踪连接数
        return endpoints[0]


class HTTPClient:
    """HTTP客户端"""
    
    def __init__(self, circuit_breaker: CircuitBreakerService):
        self.circuit_breaker = circuit_breaker
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_request(
        self,
        endpoint: ServiceEndpoint,
        request: ServiceRequest
    ) -> ServiceResponse:
        """发送HTTP请求"""
        start_time = time.time()
        
        try:
            # 构建URL
            url = f"http://{endpoint.host}:{endpoint.port}{endpoint.path}{request.endpoint}"
            
            # 使用断路器
            async def make_request():
                async with self.session.request(
                    method=request.method,
                    url=url,
                    json=request.data,
                    headers=request.headers,
                    params=request.params,
                    timeout=aiohttp.ClientTimeout(total=request.timeout)
                ) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    
                    return ServiceResponse(
                        request_id=request.request_id,
                        service_type=request.service_type,
                        status_code=response.status,
                        data=response_data,
                        headers=dict(response.headers),
                        response_time=time.time() - start_time
                    )
            
            response = await self.circuit_breaker.call(
                f"{endpoint.service_type.value}_{endpoint.host}",
                make_request
            )
            
            return response
            
        except Exception as e:
            logger.error(f"HTTP请求失败: {e}")
            return ServiceResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status_code=500,
                error=str(e),
                response_time=time.time() - start_time
            )


class GRPCClient:
    """gRPC客户端"""
    
    def __init__(self, circuit_breaker: CircuitBreakerService):
        self.circuit_breaker = circuit_breaker
        self.channels = {}
    
    async def send_request(
        self,
        endpoint: ServiceEndpoint,
        request: ServiceRequest
    ) -> ServiceResponse:
        """发送gRPC请求"""
        start_time = time.time()
        
        try:
            # 获取或创建通道
            channel_key = f"{endpoint.host}:{endpoint.port}"
            if channel_key not in self.channels:
                self.channels[channel_key] = grpc.aio.insecure_channel(channel_key)
            
            channel = self.channels[channel_key]
            
            # 使用断路器
            async def make_grpc_request():
                # 这里需要根据具体的gRPC服务定义来实现
                # 简化示例
                stub = None  # 实际应该根据服务类型创建对应的stub
                
                # 模拟gRPC调用
                response_data = {"message": "gRPC response"}
                
                return ServiceResponse(
                    request_id=request.request_id,
                    service_type=request.service_type,
                    status_code=200,
                    data=response_data,
                    response_time=time.time() - start_time
                )
            
            response = await self.circuit_breaker.call(
                f"{endpoint.service_type.value}_{endpoint.host}_grpc",
                make_grpc_request
            )
            
            return response
            
        except Exception as e:
            logger.error(f"gRPC请求失败: {e}")
            return ServiceResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status_code=500,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    async def close(self):
        """关闭所有通道"""
        for channel in self.channels.values():
            await channel.close()
        self.channels.clear()


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self.check_interval = 30.0  # 30秒检查一次
        self.running = False
    
    async def start(self):
        """启动健康检查"""
        self.running = True
        asyncio.create_task(self._health_check_loop())
    
    async def stop(self):
        """停止健康检查"""
        self.running = False
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.running:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                await asyncio.sleep(5)  # 出错时短暂等待
    
    async def _check_all_services(self):
        """检查所有服务"""
        tasks = []
        
        for service_type, endpoints in self.service_registry.services.items():
            for endpoint in endpoints:
                if endpoint.protocol == CommunicationProtocol.HTTP_REST:
                    task = self._check_http_service(endpoint)
                    tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_http_service(self, endpoint: ServiceEndpoint):
        """检查HTTP服务"""
        start_time = time.time()
        
        try:
            url = f"http://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        health = ServiceHealth(
                            service_type=endpoint.service_type,
                            status="healthy",
                            response_time=response_time,
                            last_check=time.time(),
                            success_count=1
                        )
                    else:
                        health = ServiceHealth(
                            service_type=endpoint.service_type,
                            status="unhealthy",
                            response_time=response_time,
                            last_check=time.time(),
                            error_count=1
                        )
                    
                    self.service_registry.update_health_status(endpoint, health)
                    
        except Exception as e:
            response_time = time.time() - start_time
            health = ServiceHealth(
                service_type=endpoint.service_type,
                status="unhealthy",
                response_time=response_time,
                last_check=time.time(),
                error_count=1,
                metadata={"error": str(e)}
            )
            self.service_registry.update_health_status(endpoint, health)


class RequestQueue:
    """请求队列"""
    
    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.PriorityQueue(maxsize=max_size)
        self.processing = False
    
    async def enqueue(self, request: ServiceRequest, priority: int = 1):
        """入队请求"""
        # 优先级队列，数字越小优先级越高
        await self.queue.put((10 - priority, time.time(), request))
    
    async def dequeue(self) -> Optional[ServiceRequest]:
        """出队请求"""
        try:
            _, _, request = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            return request
        except asyncio.TimeoutError:
            return None
    
    def qsize(self) -> int:
        """队列大小"""
        return self.queue.qsize()
    
    def empty(self) -> bool:
        """队列是否为空"""
        return self.queue.empty()


class APIGateway:
    """API网关主类"""
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        circuit_breaker: CircuitBreakerService
    ):
        self.metrics_collector = metrics_collector
        self.circuit_breaker = circuit_breaker
        self.service_registry = ServiceRegistry()
        self.health_checker = HealthChecker(self.service_registry)
        self.request_queue = RequestQueue()
        
        self.http_client = None
        self.grpc_client = None
        
        # 请求处理器
        self.request_processors = {}
        self._initialize_request_processors()
    
    async def __aenter__(self):
        self.http_client = HTTPClient(self.circuit_breaker)
        await self.http_client.__aenter__()
        
        self.grpc_client = GRPCClient(self.circuit_breaker)
        
        await self.health_checker.start()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.health_checker.stop()
        
        if self.http_client:
            await self.http_client.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.grpc_client:
            await self.grpc_client.close()
    
    def _initialize_request_processors(self):
        """初始化请求处理器"""
        self.request_processors = {
            ServiceType.AUTH_SERVICE: self._process_auth_request,
            ServiceType.USER_SERVICE: self._process_user_request,
            ServiceType.MEDICAL_SERVICE: self._process_medical_request,
            ServiceType.HEALTH_DATA_SERVICE: self._process_health_data_request,
            ServiceType.MESSAGE_BUS: self._process_message_bus_request,
            ServiceType.BLOCKCHAIN_SERVICE: self._process_blockchain_request,
            ServiceType.AGENT_SERVICES: self._process_agent_request,
            ServiceType.MED_KNOWLEDGE: self._process_knowledge_request
        }
    
    async def send_request(
        self,
        request: ServiceRequest,
        protocol: Optional[CommunicationProtocol] = None
    ) -> ServiceResponse:
        """
        发送服务请求
        
        Args:
            request: 服务请求
            protocol: 通信协议
            
        Returns:
            服务响应
        """
        start_time = time.time()
        
        try:
            # 预处理请求
            processed_request = await self._preprocess_request(request)
            
            # 获取服务端点
            endpoint = self.service_registry.get_healthy_endpoint(
                request.service_type, protocol
            )
            
            if not endpoint:
                return ServiceResponse(
                    request_id=request.request_id,
                    service_type=request.service_type,
                    status_code=503,
                    error="服务不可用",
                    response_time=time.time() - start_time
                )
            
            # 根据协议发送请求
            if endpoint.protocol == CommunicationProtocol.HTTP_REST:
                response = await self.http_client.send_request(endpoint, processed_request)
            elif endpoint.protocol == CommunicationProtocol.GRPC:
                response = await self.grpc_client.send_request(endpoint, processed_request)
            else:
                return ServiceResponse(
                    request_id=request.request_id,
                    service_type=request.service_type,
                    status_code=501,
                    error="不支持的协议",
                    response_time=time.time() - start_time
                )
            
            # 后处理响应
            processed_response = await self._postprocess_response(response)
            
            # 记录指标
            await self._record_request_metrics(request, response, endpoint)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"发送请求失败: {e}")
            return ServiceResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                status_code=500,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    async def send_agent_request(
        self,
        agent_name: str,
        endpoint: str,
        data: Any,
        method: str = "POST"
    ) -> ServiceResponse:
        """
        发送智能体请求
        
        Args:
            agent_name: 智能体名称
            endpoint: 端点路径
            data: 请求数据
            method: HTTP方法
            
        Returns:
            服务响应
        """
        request = ServiceRequest(
            request_id=f"agent_{agent_name}_{int(time.time())}",
            service_type=ServiceType.AGENT_SERVICES,
            endpoint=endpoint,
            method=method,
            data=data,
            metadata={"agent": agent_name}
        )
        
        # 获取特定智能体的端点
        agent_endpoint = self.service_registry.get_agent_endpoint(agent_name)
        
        if not agent_endpoint:
            return ServiceResponse(
                request_id=request.request_id,
                service_type=ServiceType.AGENT_SERVICES,
                status_code=404,
                error=f"智能体 {agent_name} 不可用"
            )
        
        return await self.http_client.send_request(agent_endpoint, request)
    
    async def broadcast_to_agents(
        self,
        endpoint: str,
        data: Any,
        agents: Optional[List[str]] = None
    ) -> Dict[str, ServiceResponse]:
        """
        广播到多个智能体
        
        Args:
            endpoint: 端点路径
            data: 请求数据
            agents: 智能体列表，None表示所有智能体
            
        Returns:
            智能体响应字典
        """
        if agents is None:
            agents = ["xiaoai", "xiaoke", "laoke", "soer"]
        
        tasks = []
        for agent in agents:
            task = self.send_agent_request(agent, endpoint, data)
            tasks.append((agent, task))
        
        results = {}
        responses = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (agent, _), response in zip(tasks, responses):
            if isinstance(response, Exception):
                results[agent] = ServiceResponse(
                    request_id=f"broadcast_{agent}",
                    service_type=ServiceType.AGENT_SERVICES,
                    status_code=500,
                    error=str(response)
                )
            else:
                results[agent] = response
        
        return results
    
    async def _preprocess_request(self, request: ServiceRequest) -> ServiceRequest:
        """预处理请求"""
        # 添加通用头部
        if "Content-Type" not in request.headers:
            request.headers["Content-Type"] = "application/json"
        
        if "User-Agent" not in request.headers:
            request.headers["User-Agent"] = "RAG-Service/1.0"
        
        # 添加请求ID
        if "X-Request-ID" not in request.headers:
            request.headers["X-Request-ID"] = request.request_id
        
        # 调用特定服务的预处理器
        processor = self.request_processors.get(request.service_type)
        if processor:
            request = await processor(request)
        
        return request
    
    async def _postprocess_response(self, response: ServiceResponse) -> ServiceResponse:
        """后处理响应"""
        # 添加响应元数据
        response.metadata["processed_at"] = time.time()
        response.metadata["gateway_version"] = "1.0"
        
        return response
    
    async def _process_auth_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理认证服务请求"""
        # 添加认证相关的头部或参数
        return request
    
    async def _process_user_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理用户服务请求"""
        # 添加用户相关的头部或参数
        return request
    
    async def _process_medical_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理医疗服务请求"""
        # 添加医疗相关的头部或参数
        return request
    
    async def _process_health_data_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理健康数据服务请求"""
        # 添加健康数据相关的头部或参数
        return request
    
    async def _process_message_bus_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理消息总线请求"""
        # 添加消息总线相关的头部或参数
        return request
    
    async def _process_blockchain_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理区块链服务请求"""
        # 添加区块链相关的头部或参数
        return request
    
    async def _process_agent_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理智能体服务请求"""
        # 添加智能体相关的头部或参数
        agent_name = request.metadata.get("agent")
        if agent_name:
            request.headers["X-Agent-Name"] = agent_name
        
        return request
    
    async def _process_knowledge_request(self, request: ServiceRequest) -> ServiceRequest:
        """处理知识库请求"""
        # 添加知识库相关的头部或参数
        return request
    
    async def _record_request_metrics(
        self,
        request: ServiceRequest,
        response: ServiceResponse,
        endpoint: ServiceEndpoint
    ):
        """记录请求指标"""
        # 请求响应时间
        await self.metrics_collector.record_histogram(
            "gateway_request_duration_seconds",
            response.response_time,
            {
                "service": request.service_type.value,
                "method": request.method,
                "status_code": str(response.status_code),
                "protocol": endpoint.protocol.value
            }
        )
        
        # 请求计数
        await self.metrics_collector.increment_counter(
            "gateway_requests_total",
            {
                "service": request.service_type.value,
                "method": request.method,
                "status_code": str(response.status_code)
            }
        )
        
        # 错误计数
        if response.status_code >= 400:
            await self.metrics_collector.increment_counter(
                "gateway_request_errors_total",
                {
                    "service": request.service_type.value,
                    "status_code": str(response.status_code)
                }
            )
    
    async def get_service_health(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        health_status = {}
        
        for service_type in ServiceType:
            endpoints = self.service_registry.get_service_endpoints(service_type)
            service_health = []
            
            for endpoint in endpoints:
                key = f"{endpoint.host}:{endpoint.port}"
                health = self.service_registry.health_status.get(key)
                
                if health:
                    service_health.append({
                        "endpoint": f"{endpoint.host}:{endpoint.port}",
                        "protocol": endpoint.protocol.value,
                        "status": health.status,
                        "response_time": health.response_time,
                        "last_check": health.last_check
                    })
            
            health_status[service_type.value] = service_health
        
        return health_status
    
    async def get_gateway_statistics(self) -> Dict[str, Any]:
        """获取网关统计信息"""
        stats = {
            "services_count": len(self.service_registry.services),
            "total_endpoints": sum(
                len(endpoints) for endpoints in self.service_registry.services.values()
            ),
            "queue_size": self.request_queue.qsize(),
            "health_status": await self.get_service_health(),
            "load_balancer_strategy": self.service_registry.load_balancer.strategy
        }
        
        return stats


# 便捷函数
async def create_api_gateway(
    metrics_collector: MetricsCollector,
    circuit_breaker: CircuitBreakerService
) -> APIGateway:
    """创建API网关实例"""
    gateway = APIGateway(metrics_collector, circuit_breaker)
    await gateway.__aenter__()
    return gateway


async def send_service_request(
    gateway: APIGateway,
    service_type: ServiceType,
    endpoint: str,
    data: Any,
    method: str = "POST"
) -> ServiceResponse:
    """发送服务请求的便捷函数"""
    request = ServiceRequest(
        request_id=f"{service_type.value}_{int(time.time())}",
        service_type=service_type,
        endpoint=endpoint,
        method=method,
        data=data
    )
    
    return await gateway.send_request(request) 