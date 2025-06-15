"""
故障转移管理器

提供高可用性支持，包括故障检测、自动故障转移和恢复机制。
"""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from internal.config.settings import get_settings
from internal.cache.redis_cache import get_redis_cache
from internal.database.connection_manager import get_connection_manager
from internal.discovery.service_registry import get_service_registry, ServiceInstance, ServiceStatus

logger = logging.getLogger(__name__)
settings = get_settings()


class FailoverState(Enum):
    """故障转移状态"""
    ACTIVE = "active"           # 主节点活跃
    STANDBY = "standby"         # 备用节点待机
    FAILOVER = "failover"       # 故障转移中
    RECOVERING = "recovering"   # 恢复中
    FAILED = "failed"          # 故障状态


class NodeRole(Enum):
    """节点角色"""
    PRIMARY = "primary"         # 主节点
    SECONDARY = "secondary"     # 备用节点
    WITNESS = "witness"         # 见证节点


@dataclass
class FailoverNode:
    """故障转移节点"""
    id: str
    role: NodeRole
    host: str
    port: int
    state: FailoverState = FailoverState.STANDBY
    priority: int = 1  # 优先级，数字越大优先级越高
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    health_score: float = 100.0  # 健康评分 0-100
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 故障统计
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    recovery_count: int = 0
    last_recovery: Optional[datetime] = None
    
    @property
    def address(self) -> str:
        """获取节点地址"""
        return f"{self.host}:{self.port}"
    
    @property
    def is_healthy(self) -> bool:
        """检查节点是否健康"""
        # 检查心跳时间
        heartbeat_timeout = datetime.utcnow() - timedelta(seconds=30)
        if self.last_heartbeat < heartbeat_timeout:
            return False
        
        # 检查健康评分
        return self.health_score >= 50.0
    
    @property
    def is_primary(self) -> bool:
        """检查是否为主节点"""
        return self.role == NodeRole.PRIMARY and self.state == FailoverState.ACTIVE


@dataclass
class FailoverEvent:
    """故障转移事件"""
    id: str
    event_type: str  # failover, recovery, election
    from_node: Optional[str]
    to_node: Optional[str]
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FailoverManager:
    """故障转移管理器"""
    
    def __init__(self):
        self.cache = get_redis_cache()
        self.db_manager = get_connection_manager()
        self.service_registry = get_service_registry()
        
        self.node_id = str(uuid.uuid4())
        self.current_node: Optional[FailoverNode] = None
        self.cluster_nodes: Dict[str, FailoverNode] = {}
        self.failover_events: List[FailoverEvent] = []
        
        self.is_running = False
        self.election_in_progress = False
        self.failover_callbacks: List[Callable] = []
        
        # Redis键前缀
        self.CLUSTER_PREFIX = "ha_cluster:"
        self.NODE_PREFIX = "ha_node:"
        self.ELECTION_PREFIX = "ha_election:"
        self.EVENT_PREFIX = "ha_event:"
        
        # 配置参数
        self.heartbeat_interval = 10  # 心跳间隔（秒）
        self.election_timeout = 30    # 选举超时（秒）
        self.failover_timeout = 60    # 故障转移超时（秒）
        self.max_failure_count = 3    # 最大失败次数
    
    async def start(self, role: NodeRole = NodeRole.SECONDARY, priority: int = 1):
        """启动故障转移管理器"""
        if self.is_running:
            return
        
        try:
            # 创建当前节点
            self.current_node = FailoverNode(
                id=self.node_id,
                role=role,
                host=self._get_local_ip(),
                port=settings.server_port,
                priority=priority,
                metadata={
                    "service_name": "auth-service",
                    "version": "1.0.0",
                    "started_at": datetime.utcnow().isoformat()
                }
            )
            
            # 注册到集群
            await self._register_node()
            
            # 启动心跳任务
            asyncio.create_task(self._heartbeat_loop())
            
            # 启动监控任务
            asyncio.create_task(self._monitor_loop())
            
            # 启动选举检查
            asyncio.create_task(self._election_check_loop())
            
            self.is_running = True
            
            # 如果是主节点角色，尝试成为主节点
            if role == NodeRole.PRIMARY:
                await self._try_become_primary()
            
            logger.info(f"故障转移管理器已启动: {self.node_id} ({role.value})")
            
        except Exception as e:
            logger.error(f"故障转移管理器启动失败: {str(e)}")
            raise
    
    async def stop(self):
        """停止故障转移管理器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        try:
            # 注销节点
            await self._deregister_node()
            
            logger.info(f"故障转移管理器已停止: {self.node_id}")
            
        except Exception as e:
            logger.error(f"故障转移管理器停止失败: {str(e)}")
    
    async def register_failover_callback(self, callback: Callable):
        """注册故障转移回调"""
        self.failover_callbacks.append(callback)
    
    async def trigger_failover(self, reason: str = "manual") -> bool:
        """触发故障转移"""
        try:
            if not self.current_node or self.current_node.role != NodeRole.PRIMARY:
                logger.warning("只有主节点可以触发故障转移")
                return False
            
            # 查找最佳备用节点
            best_secondary = await self._find_best_secondary()
            if not best_secondary:
                logger.error("没有可用的备用节点进行故障转移")
                return False
            
            # 执行故障转移
            await self._execute_failover(best_secondary, reason)
            
            return True
            
        except Exception as e:
            logger.error(f"故障转移失败: {str(e)}")
            return False
    
    async def _register_node(self):
        """注册节点到集群"""
        node_key = f"{self.NODE_PREFIX}{self.node_id}"
        node_data = {
            "id": self.current_node.id,
            "role": self.current_node.role.value,
            "host": self.current_node.host,
            "port": self.current_node.port,
            "state": self.current_node.state.value,
            "priority": self.current_node.priority,
            "last_heartbeat": self.current_node.last_heartbeat.isoformat(),
            "health_score": self.current_node.health_score,
            "metadata": self.current_node.metadata
        }
        
        await self.cache.set(node_key, node_data, ttl=60)
        
        # 添加到集群节点列表
        cluster_key = f"{self.CLUSTER_PREFIX}nodes"
        cluster_nodes = await self.cache.get(cluster_key, default=[])
        if self.node_id not in cluster_nodes:
            cluster_nodes.append(self.node_id)
            await self.cache.set(cluster_key, cluster_nodes, ttl=300)
        
        logger.info(f"节点已注册到集群: {self.node_id}")
    
    async def _deregister_node(self):
        """从集群注销节点"""
        # 如果是主节点，触发故障转移
        if self.current_node and self.current_node.is_primary:
            await self.trigger_failover("shutdown")
        
        # 从Redis删除节点信息
        node_key = f"{self.NODE_PREFIX}{self.node_id}"
        await self.cache.delete(node_key)
        
        # 从集群节点列表移除
        cluster_key = f"{self.CLUSTER_PREFIX}nodes"
        cluster_nodes = await self.cache.get(cluster_key, default=[])
        if self.node_id in cluster_nodes:
            cluster_nodes.remove(self.node_id)
            await self.cache.set(cluster_key, cluster_nodes, ttl=300)
        
        logger.info(f"节点已从集群注销: {self.node_id}")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if self.current_node:
                    # 更新心跳时间
                    self.current_node.last_heartbeat = datetime.utcnow()
                    
                    # 计算健康评分
                    health_score = await self._calculate_health_score()
                    self.current_node.health_score = health_score
                    
                    # 更新节点信息
                    await self._register_node()
                
            except Exception as e:
                logger.error(f"心跳更新失败: {str(e)}")
    
    async def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                await asyncio.sleep(15)  # 每15秒检查一次
                
                # 更新集群节点信息
                await self._update_cluster_nodes()
                
                # 检查主节点状态
                await self._check_primary_health()
                
                # 清理过期事件
                await self._cleanup_old_events()
                
            except Exception as e:
                logger.error(f"监控循环失败: {str(e)}")
    
    async def _election_check_loop(self):
        """选举检查循环"""
        while self.is_running:
            try:
                await asyncio.sleep(20)  # 每20秒检查一次
                
                # 检查是否需要选举
                if await self._should_start_election():
                    await self._start_election()
                
            except Exception as e:
                logger.error(f"选举检查失败: {str(e)}")
    
    async def _update_cluster_nodes(self):
        """更新集群节点信息"""
        try:
            cluster_key = f"{self.CLUSTER_PREFIX}nodes"
            node_ids = await self.cache.get(cluster_key, default=[])
            
            current_nodes = {}
            for node_id in node_ids:
                node_key = f"{self.NODE_PREFIX}{node_id}"
                node_data = await self.cache.get(node_key)
                
                if node_data:
                    node = FailoverNode(
                        id=node_data["id"],
                        role=NodeRole(node_data["role"]),
                        host=node_data["host"],
                        port=node_data["port"],
                        state=FailoverState(node_data["state"]),
                        priority=node_data["priority"],
                        last_heartbeat=datetime.fromisoformat(node_data["last_heartbeat"]),
                        health_score=node_data["health_score"],
                        metadata=node_data["metadata"]
                    )
                    current_nodes[node_id] = node
            
            self.cluster_nodes = current_nodes
            
        except Exception as e:
            logger.error(f"更新集群节点失败: {str(e)}")
    
    async def _check_primary_health(self):
        """检查主节点健康状态"""
        try:
            primary_node = self._get_primary_node()
            
            if not primary_node:
                # 没有主节点，可能需要选举
                logger.warning("集群中没有主节点")
                return
            
            if not primary_node.is_healthy:
                logger.warning(f"主节点不健康: {primary_node.id}")
                
                # 如果当前节点是备用节点，考虑发起选举
                if (self.current_node and 
                    self.current_node.role == NodeRole.SECONDARY and
                    not self.election_in_progress):
                    
                    await self._start_election()
            
        except Exception as e:
            logger.error(f"检查主节点健康失败: {str(e)}")
    
    async def _should_start_election(self) -> bool:
        """检查是否应该开始选举"""
        # 如果已经在选举中，不重复选举
        if self.election_in_progress:
            return False
        
        # 检查是否有活跃的主节点
        primary_node = self._get_primary_node()
        if primary_node and primary_node.is_healthy:
            return False
        
        # 检查当前节点是否有资格参与选举
        if not self.current_node or self.current_node.role == NodeRole.WITNESS:
            return False
        
        return True
    
    async def _start_election(self):
        """开始选举"""
        if self.election_in_progress:
            return
        
        try:
            self.election_in_progress = True
            election_id = str(uuid.uuid4())
            
            logger.info(f"开始选举: {election_id}")
            
            # 设置选举锁
            election_key = f"{self.ELECTION_PREFIX}{election_id}"
            election_data = {
                "id": election_id,
                "initiator": self.node_id,
                "started_at": datetime.utcnow().isoformat(),
                "candidates": []
            }
            
            # 尝试获取选举锁
            if await self.cache.set(election_key, election_data, ttl=self.election_timeout):
                # 执行选举
                winner = await self._conduct_election(election_id)
                
                if winner:
                    await self._promote_to_primary(winner)
                
                # 清理选举锁
                await self.cache.delete(election_key)
            
        except Exception as e:
            logger.error(f"选举失败: {str(e)}")
        finally:
            self.election_in_progress = False
    
    async def _conduct_election(self, election_id: str) -> Optional[FailoverNode]:
        """执行选举"""
        try:
            # 收集候选节点
            candidates = []
            for node in self.cluster_nodes.values():
                if (node.role in [NodeRole.PRIMARY, NodeRole.SECONDARY] and 
                    node.is_healthy):
                    candidates.append(node)
            
            if not candidates:
                logger.warning("没有可用的候选节点")
                return None
            
            # 按优先级和健康评分排序
            candidates.sort(
                key=lambda n: (n.priority, n.health_score, -n.failure_count),
                reverse=True
            )
            
            winner = candidates[0]
            
            # 记录选举事件
            event = FailoverEvent(
                id=str(uuid.uuid4()),
                event_type="election",
                from_node=None,
                to_node=winner.id,
                reason=f"Election {election_id}",
                metadata={
                    "candidates": [c.id for c in candidates],
                    "winner_priority": winner.priority,
                    "winner_health": winner.health_score
                }
            )
            await self._record_event(event)
            
            logger.info(f"选举获胜者: {winner.id} (优先级: {winner.priority}, 健康: {winner.health_score})")
            return winner
            
        except Exception as e:
            logger.error(f"执行选举失败: {str(e)}")
            return None
    
    async def _promote_to_primary(self, node: FailoverNode):
        """提升节点为主节点"""
        try:
            # 更新节点角色和状态
            node.role = NodeRole.PRIMARY
            node.state = FailoverState.ACTIVE
            
            # 如果是当前节点，更新本地状态
            if node.id == self.node_id:
                self.current_node.role = NodeRole.PRIMARY
                self.current_node.state = FailoverState.ACTIVE
                
                # 执行故障转移回调
                for callback in self.failover_callbacks:
                    try:
                        await callback("promoted_to_primary")
                    except Exception as e:
                        logger.error(f"故障转移回调失败: {str(e)}")
            
            # 更新Redis中的节点信息
            node_key = f"{self.NODE_PREFIX}{node.id}"
            node_data = await self.cache.get(node_key)
            if node_data:
                node_data["role"] = NodeRole.PRIMARY.value
                node_data["state"] = FailoverState.ACTIVE.value
                await self.cache.set(node_key, node_data, ttl=60)
            
            logger.info(f"节点已提升为主节点: {node.id}")
            
        except Exception as e:
            logger.error(f"提升主节点失败: {str(e)}")
    
    async def _try_become_primary(self):
        """尝试成为主节点"""
        try:
            # 检查是否已有主节点
            primary_node = self._get_primary_node()
            if primary_node and primary_node.is_healthy:
                logger.info("集群中已有健康的主节点")
                return
            
            # 尝试获取主节点锁
            primary_lock_key = f"{self.CLUSTER_PREFIX}primary_lock"
            lock_data = {
                "node_id": self.node_id,
                "acquired_at": datetime.utcnow().isoformat()
            }
            
            # 使用Redis的SET NX命令实现分布式锁
            if await self.cache.set(primary_lock_key, lock_data, ttl=30):
                # 成功获取锁，成为主节点
                await self._promote_to_primary(self.current_node)
            
        except Exception as e:
            logger.error(f"尝试成为主节点失败: {str(e)}")
    
    async def _find_best_secondary(self) -> Optional[FailoverNode]:
        """查找最佳备用节点"""
        secondary_nodes = [
            node for node in self.cluster_nodes.values()
            if node.role == NodeRole.SECONDARY and node.is_healthy
        ]
        
        if not secondary_nodes:
            return None
        
        # 按优先级和健康评分排序
        secondary_nodes.sort(
            key=lambda n: (n.priority, n.health_score, -n.failure_count),
            reverse=True
        )
        
        return secondary_nodes[0]
    
    async def _execute_failover(self, target_node: FailoverNode, reason: str):
        """执行故障转移"""
        try:
            logger.info(f"执行故障转移: {self.current_node.id} -> {target_node.id}")
            
            # 记录故障转移事件
            event = FailoverEvent(
                id=str(uuid.uuid4()),
                event_type="failover",
                from_node=self.current_node.id,
                to_node=target_node.id,
                reason=reason
            )
            await self._record_event(event)
            
            # 将当前节点设为备用
            self.current_node.role = NodeRole.SECONDARY
            self.current_node.state = FailoverState.STANDBY
            
            # 提升目标节点为主节点
            await self._promote_to_primary(target_node)
            
            # 执行故障转移回调
            for callback in self.failover_callbacks:
                try:
                    await callback("failover_completed")
                except Exception as e:
                    logger.error(f"故障转移回调失败: {str(e)}")
            
            logger.info("故障转移完成")
            
        except Exception as e:
            logger.error(f"执行故障转移失败: {str(e)}")
    
    async def _calculate_health_score(self) -> float:
        """计算健康评分"""
        try:
            score = 100.0
            
            # 检查数据库连接
            try:
                db_health = await self.db_manager.health_check()
                if db_health.get("status") != "healthy":
                    score -= 30.0
                else:
                    # 根据响应时间调整评分
                    response_time = db_health.get("response_time_ms", 0)
                    if response_time > 1000:
                        score -= 10.0
                    elif response_time > 500:
                        score -= 5.0
            except Exception:
                score -= 40.0
            
            # 检查缓存连接
            try:
                cache_health = await self.cache.health_check()
                if cache_health.get("status") != "healthy":
                    score -= 20.0
            except Exception:
                score -= 20.0
            
            # 检查系统负载（简化版）
            # 这里可以添加更多系统指标检查
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"计算健康评分失败: {str(e)}")
            return 0.0
    
    def _get_primary_node(self) -> Optional[FailoverNode]:
        """获取主节点"""
        for node in self.cluster_nodes.values():
            if node.role == NodeRole.PRIMARY:
                return node
        return None
    
    async def _record_event(self, event: FailoverEvent):
        """记录故障转移事件"""
        try:
            event_key = f"{self.EVENT_PREFIX}{event.id}"
            event_data = {
                "id": event.id,
                "event_type": event.event_type,
                "from_node": event.from_node,
                "to_node": event.to_node,
                "reason": event.reason,
                "timestamp": event.timestamp.isoformat(),
                "metadata": event.metadata
            }
            
            await self.cache.set(event_key, event_data, ttl=86400)  # 保存24小时
            
            # 添加到事件列表
            self.failover_events.append(event)
            
            # 保持最近100个事件
            if len(self.failover_events) > 100:
                self.failover_events = self.failover_events[-100:]
            
        except Exception as e:
            logger.error(f"记录事件失败: {str(e)}")
    
    async def _cleanup_old_events(self):
        """清理旧事件"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.failover_events = [
                event for event in self.failover_events
                if event.timestamp > cutoff_time
            ]
        except Exception as e:
            logger.error(f"清理旧事件失败: {str(e)}")
    
    def _get_local_ip(self) -> str:
        """获取本地IP地址"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群状态"""
        primary_node = self._get_primary_node()
        secondary_nodes = [
            node for node in self.cluster_nodes.values()
            if node.role == NodeRole.SECONDARY
        ]
        
        return {
            "cluster_id": f"auth-service-cluster",
            "total_nodes": len(self.cluster_nodes),
            "current_node": {
                "id": self.current_node.id if self.current_node else None,
                "role": self.current_node.role.value if self.current_node else None,
                "state": self.current_node.state.value if self.current_node else None,
                "health_score": self.current_node.health_score if self.current_node else 0
            },
            "primary_node": {
                "id": primary_node.id if primary_node else None,
                "address": primary_node.address if primary_node else None,
                "health_score": primary_node.health_score if primary_node else 0,
                "is_healthy": primary_node.is_healthy if primary_node else False
            } if primary_node else None,
            "secondary_nodes": [
                {
                    "id": node.id,
                    "address": node.address,
                    "priority": node.priority,
                    "health_score": node.health_score,
                    "is_healthy": node.is_healthy
                }
                for node in secondary_nodes
            ],
            "recent_events": [
                {
                    "type": event.event_type,
                    "from_node": event.from_node,
                    "to_node": event.to_node,
                    "reason": event.reason,
                    "timestamp": event.timestamp.isoformat()
                }
                for event in self.failover_events[-10:]  # 最近10个事件
            ],
            "election_in_progress": self.election_in_progress,
            "is_running": self.is_running
        }


# 全局故障转移管理器实例
_failover_manager: Optional[FailoverManager] = None


def get_failover_manager() -> FailoverManager:
    """获取故障转移管理器实例"""
    global _failover_manager
    if _failover_manager is None:
        _failover_manager = FailoverManager()
    return _failover_manager


async def init_failover_manager(role: NodeRole = NodeRole.SECONDARY, priority: int = 1) -> None:
    """初始化故障转移管理器"""
    manager = get_failover_manager()
    await manager.start(role, priority)


async def shutdown_failover_manager() -> None:
    """关闭故障转移管理器"""
    global _failover_manager
    if _failover_manager:
        await _failover_manager.stop()
        _failover_manager = None 