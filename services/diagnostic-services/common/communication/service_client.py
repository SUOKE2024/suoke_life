"""
service_client - 索克生活项目模块
"""

        import random
from ..config.settings import get_settings
from ..database.manager import get_cache_manager
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from grpc import aio as grpc_aio
from typing import Dict, Any, List, Optional, Union, Callable
import asyncio
import backoff
import consul
import etcd3
import grpc
import httpx
import json
import logging
import time

"""
服务间通信客户端

支持HTTP和gRPC协议，提供服务发现、负载均衡、重试机制、
熔断器、监控等功能，实现五诊服务间的可靠通信。
"""



logger = logging.getLogger(__name__)

class Protocol(Enum):
    """通信协议"""
    HTTP = "http"
    GRPC = "grpc"

class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"

@dataclass
class ServiceInstance:
    """服务实例"""
    id: str
    name: str
    host: str
    port: int
    protocol: Protocol
    weight: int = 1
    health_check_url: str = "/health"
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_healthy: bool = True
    connections: int = 0
    last_used: Optional[datetime] = None
    response_time: float = 0.0

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3

class ServiceDiscovery:
    """服务发现"""
    
    def __init__(self, discovery_type: str = "consul"):
        self.discovery_type = discovery_type
        self.consul_client = None
        self.etcd_client = None
        self.local_registry: Dict[str, List[ServiceInstance]] = {}
        
    async def initialize(self):
        """初始化服务发现"""
        if self.discovery_type == "consul":
            self.consul_client = consul.Consul()
        elif self.discovery_type == "etcd":
            self.etcd_client = etcd3.client()
        
        logger.info(f"服务发现初始化完成: {self.discovery_type}")
    
    async def register_service(self, instance: ServiceInstance):
        """注册服务"""
        if self.discovery_type == "consul":
            await self._register_to_consul(instance)
        elif self.discovery_type == "etcd":
            await self._register_to_etcd(instance)
        else:
            # 本地注册
            if instance.name not in self.local_registry:
                self.local_registry[instance.name] = []
            self.local_registry[instance.name].append(instance)
        
        logger.info(f"服务注册成功: {instance.name}:{instance.id}")
    
    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """发现服务"""
        if self.discovery_type == "consul":
            return await self._discover_from_consul(service_name)
        elif self.discovery_type == "etcd":
            return await self._discover_from_etcd(service_name)
        else:
            return self.local_registry.get(service_name, [])
    
    async def _register_to_consul(self, instance: ServiceInstance):
        """注册到Consul"""
        try:
            self.consul_client.agent.service.register(
                name=instance.name,
                service_id=instance.id,
                address=instance.host,
                port=instance.port,
                check=consul.Check.http(
                    f"http://{instance.host}:{instance.port}{instance.health_check_url}",
                    interval="10s"
                ),
                meta=instance.metadata
            )
        except Exception as e:
            logger.error(f"Consul注册失败: {e}")
    
    async def _discover_from_consul(self, service_name: str) -> List[ServiceInstance]:
        """从Consul发现服务"""
        try:
            _, services = self.consul_client.health.service(service_name, passing=True)
            instances = []
            
            for service in services:
                service_info = service['Service']
                instance = ServiceInstance(
                    id=service_info['ID'],
                    name=service_info['Service'],
                    host=service_info['Address'],
                    port=service_info['Port'],
                    protocol=Protocol.HTTP,  # 默认HTTP
                    metadata=service_info.get('Meta', {})
                )
                instances.append(instance)
            
            return instances
            
        except Exception as e:
            logger.error(f"Consul服务发现失败: {e}")
            return []
    
    async def _register_to_etcd(self, instance: ServiceInstance):
        """注册到etcd"""
        try:
            key = f"/services/{instance.name}/{instance.id}"
            value = json.dumps({
                "host": instance.host,
                "port": instance.port,
                "protocol": instance.protocol.value,
                "metadata": instance.metadata
            })
            
            self.etcd_client.put(key, value, lease=self.etcd_client.lease(ttl=30))
            
        except Exception as e:
            logger.error(f"etcd注册失败: {e}")
    
    async def _discover_from_etcd(self, service_name: str) -> List[ServiceInstance]:
        """从etcd发现服务"""
        try:
            prefix = f"/services/{service_name}/"
            instances = []
            
            for value, metadata in self.etcd_client.get_prefix(prefix):
                service_data = json.loads(value.decode())
                instance_id = metadata.key.decode().split('/')[-1]
                
                instance = ServiceInstance(
                    id=instance_id,
                    name=service_name,
                    host=service_data['host'],
                    port=service_data['port'],
                    protocol=Protocol(service_data['protocol']),
                    metadata=service_data.get('metadata', {})
                )
                instances.append(instance)
            
            return instances
            
        except Exception as e:
            logger.error(f"etcd服务发现失败: {e}")
            return []

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.round_robin_index: Dict[str, int] = {}
    
    def select_instance(self, service_name: str, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """选择服务实例"""
        healthy_instances = [inst for inst in instances if inst.is_healthy]
        if not healthy_instances:
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(service_name, healthy_instances)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_instances)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_instances)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random_select(healthy_instances)
        
        return healthy_instances[0]
    
    def _round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """轮询选择"""
        if service_name not in self.round_robin_index:
            self.round_robin_index[service_name] = 0
        
        index = self.round_robin_index[service_name] % len(instances)
        self.round_robin_index[service_name] = (index + 1) % len(instances)
        
        return instances[index]
    
    def _weighted_round_robin_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """加权轮询选择"""
        total_weight = sum(inst.weight for inst in instances)
        if total_weight == 0:
            return instances[0]
        
        random_weight = random.randint(1, total_weight)
        weight_sum = 0
        
        for instance in instances:
            weight_sum += instance.weight
            if random_weight <= weight_sum:
                return instance
        
        return instances[0]
    
    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """最少连接选择"""
        return min(instances, key=lambda inst: inst.connections)
    
    def _random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """随机选择"""
        return random.choice(instances)

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
                return True
            return False
        elif self.state == "HALF_OPEN":
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def record_success(self):
        """记录成功"""
        if self.state == "HALF_OPEN":
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.half_open_max_calls:
                self.state = "CLOSED"
                self.failure_count = 0
        elif self.state == "CLOSED":
            self.failure_count = 0
    
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
        elif self.failure_count >= self.config.failure_threshold:
            self.state = "OPEN"
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.utcnow() - self.last_failure_time).seconds >= self.config.recovery_timeout

class HTTPClient:
    """HTTP客户端"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
    
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """发送HTTP请求"""
        kwargs = {
            "method": method,
            "url": url,
            "headers": headers or {},
            "params": params or {}
        }
        
        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["content"] = data
        
        if timeout:
            kwargs["timeout"] = timeout
        
        return await self.client.request(**kwargs)
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

class GRPCClient:
    """gRPC客户端"""
    
    def __init__(self):
        self.channels: Dict[str, grpc_aio.Channel] = {}
    
    async def get_channel(self, host: str, port: int) -> grpc_aio.Channel:
        """获取gRPC通道"""
        address = f"{host}:{port}"
        
        if address not in self.channels:
            self.channels[address] = grpc_aio.insecure_channel(address)
        
        return self.channels[address]
    
    async def call_unary(
        self,
        host: str,
        port: int,
        service_method: str,
        request_data: Any,
        timeout: Optional[float] = None
    ) -> Any:
        """调用一元RPC"""
        channel = await self.get_channel(host, port)
        
        # 这里需要根据具体的proto文件生成的代码来实现
        # 示例代码，实际需要根据服务定义调整
        # stub = YourServiceStub(channel)
        # response = await stub.YourMethod(request_data, timeout=timeout)
        # return response
        
        raise NotImplementedError("需要根据具体的gRPC服务实现")
    
    async def close(self):
        """关闭所有通道"""
        for channel in self.channels.values():
            await channel.close()

class ServiceClient:
    """服务客户端"""
    
    def __init__(
        self,
        service_discovery: ServiceDiscovery,
        load_balancer: LoadBalancer,
        retry_config: RetryConfig = None,
        circuit_breaker_config: CircuitBreakerConfig = None
    ):
        self.service_discovery = service_discovery
        self.load_balancer = load_balancer
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        
        # 客户端
        self.http_client = HTTPClient()
        self.grpc_client = GRPCClient()
        
        # 熔断器
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # 缓存
        self.cache_manager = None
    
    async def initialize(self):
        """初始化客户端"""
        await self.service_discovery.initialize()
        self.cache_manager = await get_cache_manager()
        logger.info("服务客户端初始化完成")
    
    async def call_service(
        self,
        service_name: str,
        method: str,
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        use_cache: bool = False,
        cache_ttl: int = 300
    ) -> Any:
        """调用服务"""
        # 检查缓存
        if use_cache and method.upper() == "GET":
            cache_key = f"service_call:{service_name}:{path}:{hash(str(data))}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
        
        # 获取熔断器
        circuit_breaker = self._get_circuit_breaker(service_name)
        if not circuit_breaker.can_execute():
            raise Exception(f"服务 {service_name} 熔断器开启")
        
        # 服务发现
        instances = await self.service_discovery.discover_services(service_name)
        if not instances:
            raise Exception(f"未找到服务: {service_name}")
        
        # 负载均衡
        instance = self.load_balancer.select_instance(service_name, instances)
        if not instance:
            raise Exception(f"没有健康的服务实例: {service_name}")
        
        # 执行调用
        try:
            result = await self._execute_call(instance, method, path, data, headers, timeout)
            
            # 记录成功
            circuit_breaker.record_success()
            
            # 缓存结果
            if use_cache and method.upper() == "GET":
                cache_key = f"service_call:{service_name}:{path}:{hash(str(data))}"
                await self.cache_manager.set(cache_key, result, cache_ttl)
            
            return result
            
        except Exception as e:
            # 记录失败
            circuit_breaker.record_failure()
            logger.error(f"服务调用失败: {service_name}, 错误: {e}")
            raise
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=60
    )
    async def _execute_call(
        self,
        instance: ServiceInstance,
        method: str,
        path: str,
        data: Optional[Any],
        headers: Optional[Dict[str, str]],
        timeout: Optional[float]
    ) -> Any:
        """执行实际调用"""
        start_time = time.time()
        
        try:
            if instance.protocol == Protocol.HTTP:
                result = await self._http_call(instance, method, path, data, headers, timeout)
            elif instance.protocol == Protocol.GRPC:
                result = await self._grpc_call(instance, method, path, data, timeout)
            else:
                raise ValueError(f"不支持的协议: {instance.protocol}")
            
            # 更新实例统计
            instance.last_used = datetime.utcnow()
            instance.response_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"调用失败: {instance.name}:{instance.id}, 错误: {e}")
            raise
    
    async def _http_call(
        self,
        instance: ServiceInstance,
        method: str,
        path: str,
        data: Optional[Any],
        headers: Optional[Dict[str, str]],
        timeout: Optional[float]
    ) -> Any:
        """HTTP调用"""
        url = f"http://{instance.host}:{instance.port}/{path.lstrip('/')}"
        
        response = await self.http_client.request(
            method=method,
            url=url,
            headers=headers,
            json_data=data if isinstance(data, dict) else None,
            data=data if not isinstance(data, dict) else None,
            timeout=timeout
        )
        
        response.raise_for_status()
        
        try:
            return response.json()
        except:
            return response.text
    
    async def _grpc_call(
        self,
        instance: ServiceInstance,
        method: str,
        path: str,
        data: Optional[Any],
        timeout: Optional[float]
    ) -> Any:
        """gRPC调用"""
        return await self.grpc_client.call_unary(
            instance.host,
            instance.port,
            method,
            data,
            timeout
        )
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """获取熔断器"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(self.circuit_breaker_config)
        return self.circuit_breakers[service_name]
    
    async def close(self):
        """关闭客户端"""
        await self.http_client.close()
        await self.grpc_client.close()

# 五诊服务客户端
class DiagnosisServiceClient:
    """五诊服务客户端"""
    
    def __init__(self, service_client: ServiceClient):
        self.client = service_client
    
    async def analyze_look(self, image_data: bytes, analysis_type: str = "face") -> Dict[str, Any]:
        """望诊分析"""
        return await self.client.call_service(
            service_name="look",
            method="POST",
            path=f"analyze/{analysis_type}",
            data={"image": image_data},
            timeout=30
        )
    
    async def analyze_listen(self, audio_data: bytes, analysis_type: str = "voice") -> Dict[str, Any]:
        """闻诊分析"""
        return await self.client.call_service(
            service_name="listen",
            method="POST",
            path=f"analyze/{analysis_type}",
            data={"audio": audio_data},
            timeout=30
        )
    
    async def analyze_inquiry(self, dialogue_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """问诊分析"""
        return await self.client.call_service(
            service_name="inquiry",
            method="POST",
            path="analyze",
            data={"dialogue": dialogue_data},
            timeout=60
        )
    
    async def analyze_palpation(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """切诊分析"""
        return await self.client.call_service(
            service_name="palpation",
            method="POST",
            path="analyze",
            data=sensor_data,
            timeout=30
        )
    
    async def analyze_calculation(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """算诊分析"""
        return await self.client.call_service(
            service_name="calculation",
            method="POST",
            path="analyze",
            data=birth_info,
            timeout=15,
            use_cache=True,
            cache_ttl=3600
        )

# 全局客户端实例
_service_client = None
_diagnosis_client = None

async def get_service_client() -> ServiceClient:
    """获取服务客户端实例"""
    global _service_client
    if _service_client is None:
        service_discovery = ServiceDiscovery("local")  # 可配置
        load_balancer = LoadBalancer(LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN)
        
        _service_client = ServiceClient(service_discovery, load_balancer)
        await _service_client.initialize()
    
    return _service_client

async def get_diagnosis_client() -> DiagnosisServiceClient:
    """获取五诊服务客户端实例"""
    global _diagnosis_client
    if _diagnosis_client is None:
        service_client = await get_service_client()
        _diagnosis_client = DiagnosisServiceClient(service_client)
    
    return _diagnosis_client 