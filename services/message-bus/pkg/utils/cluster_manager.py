#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
集群管理器
支持多节点协同、服务发现、负载均衡和故障转移
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Union
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class NodeState(Enum):
    """节点状态"""
    UNKNOWN = "unknown"
    JOINING = "joining"
    ACTIVE = "active"
    LEAVING = "leaving"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class ClusterState(Enum):
    """集群状态"""
    FORMING = "forming"
    STABLE = "stable"
    REBALANCING = "rebalancing"
    DEGRADED = "degraded"
    FAILED = "failed"


class ServiceType(Enum):
    """服务类型"""
    MESSAGE_BUS = "message_bus"
    STORAGE = "storage"
    ROUTER = "router"
    METRICS = "metrics"
    SECURITY = "security"


@dataclass
class NodeInfo:
    """节点信息"""
    node_id: str
    host: str
    port: int
    state: NodeState = NodeState.UNKNOWN
    services: List[ServiceType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: float = field(default_factory=time.time)
    join_time: float = field(default_factory=time.time)
    load: float = 0.0
    capacity: float = 100.0
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'state': self.state.value,
            'services': [s.value for s in self.services],
            'metadata': self.metadata,
            'last_heartbeat': self.last_heartbeat,
            'join_time': self.join_time,
            'load': self.load,
            'capacity': self.capacity,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeInfo':
        """从字典创建"""
        return cls(
            node_id=data['node_id'],
            host=data['host'],
            port=data['port'],
            state=NodeState(data.get('state', 'unknown')),
            services=[ServiceType(s) for s in data.get('services', [])],
            metadata=data.get('metadata', {}),
            last_heartbeat=data.get('last_heartbeat', time.time()),
            join_time=data.get('join_time', time.time()),
            load=data.get('load', 0.0),
            capacity=data.get('capacity', 100.0),
            version=data.get('version', '1.0.0')
        )


@dataclass
class ClusterConfig:
    """集群配置"""
    cluster_name: str = "suoke-message-bus"
    node_id: Optional[str] = None
    discovery_service: str = "consul"  # consul, etcd, zookeeper, redis
    discovery_endpoints: List[str] = field(default_factory=lambda: ["localhost:8500"])
    
    # 心跳配置
    heartbeat_interval: float = 10.0  # 秒
    heartbeat_timeout: float = 30.0   # 秒
    max_missed_heartbeats: int = 3
    
    # 集群配置
    min_cluster_size: int = 1
    max_cluster_size: int = 100
    replication_factor: int = 3
    
    # 负载均衡配置
    load_balance_strategy: str = "least_connections"  # round_robin, least_connections, weighted
    health_check_interval: float = 30.0
    
    # 故障转移配置
    enable_auto_failover: bool = True
    failover_timeout: float = 60.0
    split_brain_protection: bool = True
    
    # 安全配置
    enable_encryption: bool = True
    cluster_key: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.node_id is None:
            self.node_id = str(uuid.uuid4())
        
        if self.cluster_key is None:
            self.cluster_key = hashlib.sha256(self.cluster_name.encode()).hexdigest()[:32]


class ServiceDiscovery:
    """服务发现接口"""
    
    async def register_node(self, node: NodeInfo) -> bool:
        """注册节点"""
        raise NotImplementedError
    
    async def unregister_node(self, node_id: str) -> bool:
        """注销节点"""
        raise NotImplementedError
    
    async def discover_nodes(self) -> List[NodeInfo]:
        """发现节点"""
        raise NotImplementedError
    
    async def update_node_status(self, node_id: str, status: Dict[str, Any]) -> bool:
        """更新节点状态"""
        raise NotImplementedError
    
    async def watch_cluster_changes(self, callback: Callable[[List[NodeInfo]], None]):
        """监听集群变化"""
        raise NotImplementedError


class ConsulServiceDiscovery(ServiceDiscovery):
    """Consul服务发现"""
    
    def __init__(self, endpoints: List[str], cluster_name: str):
        self.endpoints = endpoints
        self.cluster_name = cluster_name
        self.consul_client = None
        self._init_consul_client()
    
    def _init_consul_client(self):
        """初始化Consul客户端"""
        try:
            import consul
            host, port = self.endpoints[0].split(':')
            self.consul_client = consul.Consul(host=host, port=int(port))
        except ImportError:
            logger.error("Consul客户端未安装，请安装python-consul")
            raise
    
    async def register_node(self, node: NodeInfo) -> bool:
        """注册节点到Consul"""
        try:
            service_id = f"{self.cluster_name}-{node.node_id}"
            
            # 注册服务
            self.consul_client.agent.service.register(
                name=self.cluster_name,
                service_id=service_id,
                address=node.host,
                port=node.port,
                tags=[s.value for s in node.services],
                meta=node.metadata,
                check=consul.Check.http(
                    f"http://{node.host}:{node.port}/health",
                    interval="10s",
                    timeout="5s"
                )
            )
            
            # 存储节点详细信息
            key = f"{self.cluster_name}/nodes/{node.node_id}"
            self.consul_client.kv.put(key, json.dumps(node.to_dict()))
            
            logger.info(f"节点注册成功: {node.node_id}")
            return True
            
        except Exception as e:
            logger.error(f"节点注册失败: {e}")
            return False
    
    async def unregister_node(self, node_id: str) -> bool:
        """从Consul注销节点"""
        try:
            service_id = f"{self.cluster_name}-{node_id}"
            
            # 注销服务
            self.consul_client.agent.service.deregister(service_id)
            
            # 删除节点信息
            key = f"{self.cluster_name}/nodes/{node_id}"
            self.consul_client.kv.delete(key)
            
            logger.info(f"节点注销成功: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"节点注销失败: {e}")
            return False
    
    async def discover_nodes(self) -> List[NodeInfo]:
        """从Consul发现节点"""
        try:
            nodes = []
            
            # 获取所有节点信息
            _, data = self.consul_client.kv.get(f"{self.cluster_name}/nodes/", recurse=True)
            
            if data:
                for item in data:
                    try:
                        node_data = json.loads(item['Value'].decode())
                        node = NodeInfo.from_dict(node_data)
                        nodes.append(node)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"解析节点数据失败: {e}")
            
            return nodes
            
        except Exception as e:
            logger.error(f"节点发现失败: {e}")
            return []
    
    async def update_node_status(self, node_id: str, status: Dict[str, Any]) -> bool:
        """更新节点状态"""
        try:
            key = f"{self.cluster_name}/nodes/{node_id}/status"
            self.consul_client.kv.put(key, json.dumps(status))
            return True
        except Exception as e:
            logger.error(f"更新节点状态失败: {e}")
            return False
    
    async def watch_cluster_changes(self, callback: Callable[[List[NodeInfo]], None]):
        """监听集群变化"""
        # 这里可以实现Consul的watch功能
        pass


class RedisServiceDiscovery(ServiceDiscovery):
    """Redis服务发现"""
    
    def __init__(self, endpoints: List[str], cluster_name: str):
        self.endpoints = endpoints
        self.cluster_name = cluster_name
        self.redis_client = None
        self._init_redis_client()
    
    def _init_redis_client(self):
        """初始化Redis客户端"""
        try:
            import redis
            host, port = self.endpoints[0].split(':')
            self.redis_client = redis.Redis(host=host, port=int(port), decode_responses=True)
        except ImportError:
            logger.error("Redis客户端未安装，请安装redis-py")
            raise
    
    async def register_node(self, node: NodeInfo) -> bool:
        """注册节点到Redis"""
        try:
            key = f"{self.cluster_name}:nodes:{node.node_id}"
            value = json.dumps(node.to_dict())
            
            # 设置节点信息，带过期时间
            self.redis_client.setex(key, 60, value)  # 60秒过期
            
            # 添加到节点集合
            self.redis_client.sadd(f"{self.cluster_name}:node_list", node.node_id)
            
            logger.info(f"节点注册成功: {node.node_id}")
            return True
            
        except Exception as e:
            logger.error(f"节点注册失败: {e}")
            return False
    
    async def unregister_node(self, node_id: str) -> bool:
        """从Redis注销节点"""
        try:
            key = f"{self.cluster_name}:nodes:{node_id}"
            
            # 删除节点信息
            self.redis_client.delete(key)
            
            # 从节点集合中移除
            self.redis_client.srem(f"{self.cluster_name}:node_list", node_id)
            
            logger.info(f"节点注销成功: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"节点注销失败: {e}")
            return False
    
    async def discover_nodes(self) -> List[NodeInfo]:
        """从Redis发现节点"""
        try:
            nodes = []
            
            # 获取所有节点ID
            node_ids = self.redis_client.smembers(f"{self.cluster_name}:node_list")
            
            for node_id in node_ids:
                key = f"{self.cluster_name}:nodes:{node_id}"
                data = self.redis_client.get(key)
                
                if data:
                    try:
                        node_data = json.loads(data)
                        node = NodeInfo.from_dict(node_data)
                        nodes.append(node)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"解析节点数据失败: {e}")
            
            return nodes
            
        except Exception as e:
            logger.error(f"节点发现失败: {e}")
            return []
    
    async def update_node_status(self, node_id: str, status: Dict[str, Any]) -> bool:
        """更新节点状态"""
        try:
            key = f"{self.cluster_name}:nodes:{node_id}:status"
            self.redis_client.setex(key, 60, json.dumps(status))
            return True
        except Exception as e:
            logger.error(f"更新节点状态失败: {e}")
            return False


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.current_index = 0
        self.node_weights = {}
        self.node_connections = defaultdict(int)
    
    def select_node(self, nodes: List[NodeInfo], exclude: Set[str] = None) -> Optional[NodeInfo]:
        """选择节点"""
        if not nodes:
            return None
        
        # 过滤排除的节点和不健康的节点
        available_nodes = [
            node for node in nodes 
            if node.node_id not in (exclude or set()) 
            and node.state == NodeState.ACTIVE
            and node.load < node.capacity * 0.9  # 负载不超过90%
        ]
        
        if not available_nodes:
            return None
        
        if self.strategy == "round_robin":
            return self._round_robin_select(available_nodes)
        elif self.strategy == "least_connections":
            return self._least_connections_select(available_nodes)
        elif self.strategy == "weighted":
            return self._weighted_select(available_nodes)
        elif self.strategy == "least_load":
            return self._least_load_select(available_nodes)
        else:
            return available_nodes[0]
    
    def _round_robin_select(self, nodes: List[NodeInfo]) -> NodeInfo:
        """轮询选择"""
        node = nodes[self.current_index % len(nodes)]
        self.current_index += 1
        return node
    
    def _least_connections_select(self, nodes: List[NodeInfo]) -> NodeInfo:
        """最少连接选择"""
        return min(nodes, key=lambda n: self.node_connections[n.node_id])
    
    def _weighted_select(self, nodes: List[NodeInfo]) -> NodeInfo:
        """加权选择"""
        # 根据节点容量计算权重
        total_weight = sum(node.capacity for node in nodes)
        if total_weight == 0:
            return nodes[0]
        
        import random
        weight = random.uniform(0, total_weight)
        current_weight = 0
        
        for node in nodes:
            current_weight += node.capacity
            if weight <= current_weight:
                return node
        
        return nodes[-1]
    
    def _least_load_select(self, nodes: List[NodeInfo]) -> NodeInfo:
        """最少负载选择"""
        return min(nodes, key=lambda n: n.load / n.capacity if n.capacity > 0 else float('inf'))
    
    def update_node_connections(self, node_id: str, delta: int):
        """更新节点连接数"""
        self.node_connections[node_id] += delta
        if self.node_connections[node_id] < 0:
            self.node_connections[node_id] = 0


class FailoverManager:
    """故障转移管理器"""
    
    def __init__(self, config: ClusterConfig):
        self.config = config
        self.failed_nodes: Set[str] = set()
        self.failover_history: List[Dict[str, Any]] = []
    
    async def detect_failures(self, nodes: List[NodeInfo]) -> List[str]:
        """检测故障节点"""
        current_time = time.time()
        failed_nodes = []
        
        for node in nodes:
            # 检查心跳超时
            if current_time - node.last_heartbeat > self.config.heartbeat_timeout:
                if node.node_id not in self.failed_nodes:
                    failed_nodes.append(node.node_id)
                    self.failed_nodes.add(node.node_id)
                    
                    # 记录故障历史
                    self.failover_history.append({
                        'node_id': node.node_id,
                        'failure_time': current_time,
                        'reason': 'heartbeat_timeout'
                    })
                    
                    logger.warning(f"检测到节点故障: {node.node_id}")
        
        return failed_nodes
    
    async def handle_node_failure(self, failed_node_id: str, cluster_nodes: List[NodeInfo]) -> bool:
        """处理节点故障"""
        if not self.config.enable_auto_failover:
            return False
        
        try:
            # 找到故障节点
            failed_node = None
            for node in cluster_nodes:
                if node.node_id == failed_node_id:
                    failed_node = node
                    break
            
            if not failed_node:
                return False
            
            # 选择替代节点
            available_nodes = [
                node for node in cluster_nodes 
                if node.node_id != failed_node_id 
                and node.state == NodeState.ACTIVE
            ]
            
            if not available_nodes:
                logger.error("没有可用的替代节点")
                return False
            
            # 执行故障转移逻辑
            # 这里可以实现具体的故障转移策略
            logger.info(f"执行故障转移: {failed_node_id} -> {available_nodes[0].node_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"故障转移失败: {e}")
            return False
    
    def is_node_failed(self, node_id: str) -> bool:
        """检查节点是否已故障"""
        return node_id in self.failed_nodes
    
    def recover_node(self, node_id: str):
        """恢复节点"""
        if node_id in self.failed_nodes:
            self.failed_nodes.remove(node_id)
            logger.info(f"节点已恢复: {node_id}")


class ClusterManager:
    """
    集群管理器
    负责节点管理、服务发现、负载均衡和故障转移
    """
    
    def __init__(self, config: ClusterConfig):
        self.config = config
        self.local_node: Optional[NodeInfo] = None
        self.cluster_nodes: Dict[str, NodeInfo] = {}
        self.cluster_state = ClusterState.FORMING
        
        # 组件
        self.service_discovery: Optional[ServiceDiscovery] = None
        self.load_balancer = LoadBalancer(config.load_balance_strategy)
        self.failover_manager = FailoverManager(config)
        
        # 状态
        self.is_leader = False
        self.leader_node_id: Optional[str] = None
        self.last_heartbeat_time = 0
        
        # 后台任务
        self._background_tasks: List[asyncio.Task] = []
        self._running = False
        
        # 初始化服务发现
        self._init_service_discovery()
    
    def _init_service_discovery(self):
        """初始化服务发现"""
        try:
            if self.config.discovery_service == "consul":
                self.service_discovery = ConsulServiceDiscovery(
                    self.config.discovery_endpoints,
                    self.config.cluster_name
                )
            elif self.config.discovery_service == "redis":
                self.service_discovery = RedisServiceDiscovery(
                    self.config.discovery_endpoints,
                    self.config.cluster_name
                )
            else:
                logger.warning(f"不支持的服务发现类型: {self.config.discovery_service}")
                
        except Exception as e:
            logger.error(f"服务发现初始化失败: {e}")
    
    async def start(self, host: str, port: int, services: List[ServiceType] = None):
        """启动集群管理器"""
        if self._running:
            logger.warning("集群管理器已在运行")
            return
        
        try:
            # 创建本地节点信息
            self.local_node = NodeInfo(
                node_id=self.config.node_id,
                host=host,
                port=port,
                state=NodeState.JOINING,
                services=services or [ServiceType.MESSAGE_BUS],
                metadata={
                    'cluster_name': self.config.cluster_name,
                    'start_time': time.time()
                }
            )
            
            # 注册到服务发现
            if self.service_discovery:
                success = await self.service_discovery.register_node(self.local_node)
                if not success:
                    raise RuntimeError("节点注册失败")
            
            # 发现现有节点
            await self._discover_cluster_nodes()
            
            # 启动后台任务
            await self._start_background_tasks()
            
            # 更新节点状态为活跃
            self.local_node.state = NodeState.ACTIVE
            if self.service_discovery:
                await self.service_discovery.update_node_status(
                    self.local_node.node_id,
                    {'state': NodeState.ACTIVE.value}
                )
            
            self._running = True
            self.cluster_state = ClusterState.STABLE
            
            logger.info(f"集群管理器启动成功: {self.local_node.node_id}")
            
        except Exception as e:
            logger.error(f"集群管理器启动失败: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """停止集群管理器"""
        if not self._running:
            return
        
        try:
            self._running = False
            
            # 更新节点状态为离开
            if self.local_node:
                self.local_node.state = NodeState.LEAVING
                if self.service_discovery:
                    await self.service_discovery.update_node_status(
                        self.local_node.node_id,
                        {'state': NodeState.LEAVING.value}
                    )
            
            # 停止后台任务
            await self._stop_background_tasks()
            
            # 注销节点
            if self.service_discovery and self.local_node:
                await self.service_discovery.unregister_node(self.local_node.node_id)
            
            logger.info("集群管理器已停止")
            
        except Exception as e:
            logger.error(f"集群管理器停止失败: {e}")
    
    async def _discover_cluster_nodes(self):
        """发现集群节点"""
        if not self.service_discovery:
            return
        
        try:
            nodes = await self.service_discovery.discover_nodes()
            
            for node in nodes:
                if node.node_id != self.local_node.node_id:
                    self.cluster_nodes[node.node_id] = node
            
            logger.info(f"发现集群节点: {len(self.cluster_nodes)}")
            
        except Exception as e:
            logger.error(f"节点发现失败: {e}")
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        # 心跳任务
        task = asyncio.create_task(self._heartbeat_loop())
        self._background_tasks.append(task)
        
        # 健康检查任务
        task = asyncio.create_task(self._health_check_loop())
        self._background_tasks.append(task)
        
        # 故障检测任务
        task = asyncio.create_task(self._failure_detection_loop())
        self._background_tasks.append(task)
        
        # 集群同步任务
        task = asyncio.create_task(self._cluster_sync_loop())
        self._background_tasks.append(task)
    
    async def _stop_background_tasks(self):
        """停止后台任务"""
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                if self.local_node and self.service_discovery:
                    # 更新心跳时间
                    self.local_node.last_heartbeat = time.time()
                    self.last_heartbeat_time = self.local_node.last_heartbeat
                    
                    # 更新节点状态
                    status = {
                        'last_heartbeat': self.local_node.last_heartbeat,
                        'load': self.local_node.load,
                        'state': self.local_node.state.value
                    }
                    
                    await self.service_discovery.update_node_status(
                        self.local_node.node_id, status
                    )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳发送失败: {e}")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._check_cluster_health()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
    
    async def _failure_detection_loop(self):
        """故障检测循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                # 检测故障节点
                all_nodes = list(self.cluster_nodes.values())
                if self.local_node:
                    all_nodes.append(self.local_node)
                
                failed_nodes = await self.failover_manager.detect_failures(all_nodes)
                
                # 处理故障节点
                for node_id in failed_nodes:
                    await self.failover_manager.handle_node_failure(node_id, all_nodes)
                    
                    # 从集群中移除故障节点
                    if node_id in self.cluster_nodes:
                        del self.cluster_nodes[node_id]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"故障检测失败: {e}")
    
    async def _cluster_sync_loop(self):
        """集群同步循环"""
        while self._running:
            try:
                await asyncio.sleep(30)  # 每30秒同步一次
                await self._discover_cluster_nodes()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"集群同步失败: {e}")
    
    async def _check_cluster_health(self):
        """检查集群健康状态"""
        try:
            total_nodes = len(self.cluster_nodes) + (1 if self.local_node else 0)
            active_nodes = sum(
                1 for node in self.cluster_nodes.values() 
                if node.state == NodeState.ACTIVE
            )
            
            if self.local_node and self.local_node.state == NodeState.ACTIVE:
                active_nodes += 1
            
            # 更新集群状态
            if total_nodes < self.config.min_cluster_size:
                self.cluster_state = ClusterState.DEGRADED
            elif active_nodes < total_nodes * 0.5:
                self.cluster_state = ClusterState.DEGRADED
            else:
                self.cluster_state = ClusterState.STABLE
            
        except Exception as e:
            logger.error(f"集群健康检查失败: {e}")
            self.cluster_state = ClusterState.FAILED
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """获取集群信息"""
        all_nodes = list(self.cluster_nodes.values())
        if self.local_node:
            all_nodes.append(self.local_node)
        
        return {
            'cluster_name': self.config.cluster_name,
            'cluster_state': self.cluster_state.value,
            'total_nodes': len(all_nodes),
            'active_nodes': sum(1 for node in all_nodes if node.state == NodeState.ACTIVE),
            'local_node_id': self.local_node.node_id if self.local_node else None,
            'is_leader': self.is_leader,
            'leader_node_id': self.leader_node_id,
            'nodes': [node.to_dict() for node in all_nodes]
        }
    
    def get_available_nodes(self, service_type: ServiceType = None) -> List[NodeInfo]:
        """获取可用节点"""
        nodes = [
            node for node in self.cluster_nodes.values()
            if node.state == NodeState.ACTIVE
        ]
        
        if self.local_node and self.local_node.state == NodeState.ACTIVE:
            nodes.append(self.local_node)
        
        if service_type:
            nodes = [node for node in nodes if service_type in node.services]
        
        return nodes
    
    def select_node(self, service_type: ServiceType = None, exclude: Set[str] = None) -> Optional[NodeInfo]:
        """选择节点"""
        available_nodes = self.get_available_nodes(service_type)
        return self.load_balancer.select_node(available_nodes, exclude)
    
    def update_local_node_load(self, load: float):
        """更新本地节点负载"""
        if self.local_node:
            self.local_node.load = load
    
    def update_node_connections(self, node_id: str, delta: int):
        """更新节点连接数"""
        self.load_balancer.update_node_connections(node_id, delta)
    
    def is_cluster_healthy(self) -> bool:
        """检查集群是否健康"""
        return self.cluster_state in [ClusterState.STABLE, ClusterState.REBALANCING]
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """获取集群统计"""
        all_nodes = list(self.cluster_nodes.values())
        if self.local_node:
            all_nodes.append(self.local_node)
        
        total_load = sum(node.load for node in all_nodes)
        total_capacity = sum(node.capacity for node in all_nodes)
        
        return {
            'total_nodes': len(all_nodes),
            'active_nodes': sum(1 for node in all_nodes if node.state == NodeState.ACTIVE),
            'failed_nodes': len(self.failover_manager.failed_nodes),
            'total_load': total_load,
            'total_capacity': total_capacity,
            'average_load': total_load / len(all_nodes) if all_nodes else 0,
            'cluster_utilization': total_load / total_capacity if total_capacity > 0 else 0,
            'cluster_state': self.cluster_state.value
        }


class ClusterManagerFactory:
    """集群管理器工厂"""
    
    @staticmethod
    def create_cluster_manager(config: Optional[ClusterConfig] = None) -> ClusterManager:
        """创建集群管理器"""
        if config is None:
            config = ClusterConfig()
        
        return ClusterManager(config)
    
    @staticmethod
    def create_from_dict(config_dict: Dict[str, Any]) -> ClusterManager:
        """从字典创建集群管理器"""
        # 这里可以实现从字典配置创建的逻辑
        config = ClusterConfig()
        return ClusterManager(config) 