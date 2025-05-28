#!/usr/bin/env python3

"""
区块链连接池管理器

该模块提供优化的区块链连接池管理功能，支持多个节点、负载均衡、
故障转移和连接健康检查，提高系统的可靠性和性能。
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import random
import statistics
import time
from typing import Any

from web3 import Web3
from web3.middleware import geth_poa_middleware

from internal.model.config import AppConfig


class NodeStatus(Enum):
    """节点状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class LoadBalanceStrategy(Enum):
    """负载均衡策略枚举"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    WEIGHTED = "weighted"


@dataclass
class NodeMetrics:
    """节点指标数据类"""
    response_times: list[float]
    success_count: int = 0
    error_count: int = 0
    last_check_time: datetime = None
    last_error_time: datetime | None = None
    consecutive_errors: int = 0

    def __post_init__(self):
        if self.last_check_time is None:
            self.last_check_time = datetime.now()

    @property
    def average_response_time(self) -> float:
        """平均响应时间"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times[-100:])  # 最近100次的平均值

    @property
    def success_rate(self) -> float:
        """成功率"""
        total = self.success_count + self.error_count
        if total == 0:
            return 1.0
        return self.success_count / total

    def add_response_time(self, response_time: float):
        """添加响应时间"""
        self.response_times.append(response_time)
        # 保持最近1000次记录
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def record_success(self, response_time: float):
        """记录成功"""
        self.success_count += 1
        self.consecutive_errors = 0
        self.add_response_time(response_time)
        self.last_check_time = datetime.now()

    def record_error(self):
        """记录错误"""
        self.error_count += 1
        self.consecutive_errors += 1
        self.last_error_time = datetime.now()
        self.last_check_time = datetime.now()


@dataclass
class BlockchainNode:
    """区块链节点数据类"""
    endpoint: str
    weight: float = 1.0
    is_poa: bool = False
    timeout: int = 30
    max_connections: int = 10
    status: NodeStatus = NodeStatus.HEALTHY
    web3_instance: Web3 | None = None
    metrics: NodeMetrics = None
    active_connections: int = 0

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = NodeMetrics(response_times=[])


class ConnectionPool:
    """区块链连接池管理器"""

    def __init__(self, config: AppConfig):
        """
        初始化连接池
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 节点列表
        self.nodes: list[BlockchainNode] = []

        # 负载均衡策略
        self.load_balance_strategy = LoadBalanceStrategy.RESPONSE_TIME

        # 当前节点索引（用于轮询）
        self.current_node_index = 0

        # 健康检查配置
        self.health_check_interval = 30  # 秒
        self.health_check_timeout = 10   # 秒
        self.max_consecutive_errors = 3

        # 连接池状态
        self.is_running = False
        self.health_check_task: asyncio.Task | None = None

        # 初始化节点
        self._init_nodes()

        self.logger.info(f"连接池初始化完成，共 {len(self.nodes)} 个节点")

    def _init_nodes(self):
        """初始化区块链节点"""
        # 从配置加载主节点
        main_node = BlockchainNode(
            endpoint=self.config.blockchain.node.endpoint,
            is_poa=getattr(self.config.blockchain.node, "is_poa", False),
            weight=1.0
        )
        self.nodes.append(main_node)

        # 从配置加载备用节点（如果有）
        if hasattr(self.config.blockchain, "backup_nodes"):
            for node_config in self.config.blockchain.backup_nodes:
                backup_node = BlockchainNode(
                    endpoint=node_config.endpoint,
                    is_poa=getattr(node_config, "is_poa", False),
                    weight=getattr(node_config, "weight", 0.5)
                )
                self.nodes.append(backup_node)

        # 初始化Web3实例
        for node in self.nodes:
            self._init_node_connection(node)

    def _init_node_connection(self, node: BlockchainNode):
        """
        初始化节点连接
        
        Args:
            node: 区块链节点
        """
        try:
            # 创建Web3实例
            if node.endpoint.startswith("http"):
                provider = Web3.HTTPProvider(
                    node.endpoint,
                    request_kwargs={"timeout": node.timeout}
                )
            elif node.endpoint.startswith("ws"):
                provider = Web3.WebsocketProvider(node.endpoint)
            else:
                raise ValueError(f"不支持的节点端点: {node.endpoint}")

            node.web3_instance = Web3(provider)

            # 添加POA中间件（如果需要）
            if node.is_poa:
                node.web3_instance.middleware_onion.inject(geth_poa_middleware, layer=0)

            # 测试连接
            if node.web3_instance.is_connected():
                node.status = NodeStatus.HEALTHY
                self.logger.info(f"节点连接成功: {node.endpoint}")
            else:
                node.status = NodeStatus.OFFLINE
                self.logger.warning(f"节点连接失败: {node.endpoint}")

        except Exception as e:
            node.status = NodeStatus.OFFLINE
            self.logger.error(f"初始化节点连接失败 {node.endpoint}: {e!s}")

    async def get_connection(self) -> tuple[Web3, BlockchainNode]:
        """
        获取可用的区块链连接
        
        Returns:
            (Web3实例, 节点信息)
        """
        # 获取健康的节点
        healthy_nodes = [
            node for node in self.nodes
            if node.status in [NodeStatus.HEALTHY, NodeStatus.DEGRADED]
        ]

        if not healthy_nodes:
            raise ConnectionError("没有可用的区块链节点")

        # 根据负载均衡策略选择节点
        selected_node = self._select_node(healthy_nodes)

        # 增加活跃连接数
        selected_node.active_connections += 1

        return selected_node.web3_instance, selected_node

    def release_connection(self, node: BlockchainNode):
        """
        释放连接
        
        Args:
            node: 要释放的节点
        """
        if node.active_connections > 0:
            node.active_connections -= 1

    def _select_node(self, available_nodes: list[BlockchainNode]) -> BlockchainNode:
        """
        根据负载均衡策略选择节点
        
        Args:
            available_nodes: 可用节点列表
            
        Returns:
            选中的节点
        """
        if self.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._select_round_robin(available_nodes)
        elif self.load_balance_strategy == LoadBalanceStrategy.RANDOM:
            return self._select_random(available_nodes)
        elif self.load_balance_strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._select_least_connections(available_nodes)
        elif self.load_balance_strategy == LoadBalanceStrategy.RESPONSE_TIME:
            return self._select_by_response_time(available_nodes)
        elif self.load_balance_strategy == LoadBalanceStrategy.WEIGHTED:
            return self._select_weighted(available_nodes)
        else:
            return available_nodes[0]

    def _select_round_robin(self, nodes: list[BlockchainNode]) -> BlockchainNode:
        """轮询选择"""
        node = nodes[self.current_node_index % len(nodes)]
        self.current_node_index += 1
        return node

    def _select_random(self, nodes: list[BlockchainNode]) -> BlockchainNode:
        """随机选择"""
        return random.choice(nodes)

    def _select_least_connections(self, nodes: list[BlockchainNode]) -> BlockchainNode:
        """最少连接选择"""
        return min(nodes, key=lambda n: n.active_connections)

    def _select_by_response_time(self, nodes: list[BlockchainNode]) -> BlockchainNode:
        """按响应时间选择"""
        # 优先选择响应时间最短的节点
        return min(nodes, key=lambda n: n.metrics.average_response_time)

    def _select_weighted(self, nodes: list[BlockchainNode]) -> BlockchainNode:
        """加权选择"""
        # 根据权重和成功率计算有效权重
        weights = []
        for node in nodes:
            effective_weight = node.weight * node.metrics.success_rate
            weights.append(effective_weight)

        # 加权随机选择
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(nodes)

        rand_val = random.uniform(0, total_weight)
        cumulative_weight = 0

        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if rand_val <= cumulative_weight:
                return nodes[i]

        return nodes[-1]

    async def execute_with_retry(
        self,
        operation: callable,
        max_retries: int = 3,
        *args,
        **kwargs
    ) -> Any:
        """
        执行操作并支持重试和故障转移
        
        Args:
            operation: 要执行的操作
            max_retries: 最大重试次数
            *args: 操作参数
            **kwargs: 操作关键字参数
            
        Returns:
            操作结果
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                # 获取连接
                web3, node = await self.get_connection()

                start_time = time.time()

                try:
                    # 执行操作
                    result = await operation(web3, *args, **kwargs)

                    # 记录成功
                    response_time = time.time() - start_time
                    node.metrics.record_success(response_time)

                    return result

                finally:
                    # 释放连接
                    self.release_connection(node)

            except Exception as e:
                last_exception = e

                # 记录错误
                if "node" in locals():
                    node.metrics.record_error()

                    # 检查是否需要标记节点为不健康
                    if node.metrics.consecutive_errors >= self.max_consecutive_errors:
                        node.status = NodeStatus.UNHEALTHY
                        self.logger.warning(f"节点标记为不健康: {node.endpoint}")

                self.logger.warning(f"操作失败 (尝试 {attempt + 1}/{max_retries + 1}): {e!s}")

                if attempt < max_retries:
                    # 等待后重试
                    await asyncio.sleep(2 ** attempt)  # 指数退避

        # 所有重试都失败
        raise last_exception

    async def start_health_check(self):
        """启动健康检查"""
        if self.is_running:
            return

        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.logger.info("健康检查已启动")

    async def stop_health_check(self):
        """停止健康检查"""
        if not self.is_running:
            return

        self.is_running = False

        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        self.logger.info("健康检查已停止")

    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_running:
            try:
                await self._check_all_nodes()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"健康检查错误: {e!s}")
                await asyncio.sleep(5)

    async def _check_all_nodes(self):
        """检查所有节点的健康状态"""
        for node in self.nodes:
            await self._check_node_health(node)

    async def _check_node_health(self, node: BlockchainNode):
        """
        检查单个节点的健康状态
        
        Args:
            node: 要检查的节点
        """
        try:
            if not node.web3_instance:
                self._init_node_connection(node)
                return

            start_time = time.time()

            # 执行健康检查操作
            is_connected = node.web3_instance.is_connected()

            if is_connected:
                # 尝试获取最新区块号
                block_number = node.web3_instance.eth.block_number

                response_time = time.time() - start_time
                node.metrics.record_success(response_time)

                # 更新节点状态
                if node.status == NodeStatus.UNHEALTHY:
                    node.status = NodeStatus.HEALTHY
                    self.logger.info(f"节点恢复健康: {node.endpoint}")
                elif response_time > 5.0:  # 响应时间超过5秒
                    node.status = NodeStatus.DEGRADED
                else:
                    node.status = NodeStatus.HEALTHY
            else:
                raise ConnectionError("节点连接失败")

        except Exception as e:
            node.metrics.record_error()

            # 根据连续错误次数更新状态
            if node.metrics.consecutive_errors >= self.max_consecutive_errors:
                if node.status != NodeStatus.OFFLINE:
                    node.status = NodeStatus.OFFLINE
                    self.logger.error(f"节点离线: {node.endpoint}")
            else:
                node.status = NodeStatus.UNHEALTHY

            self.logger.debug(f"节点健康检查失败 {node.endpoint}: {e!s}")

    def get_pool_stats(self) -> dict[str, Any]:
        """
        获取连接池统计信息
        
        Returns:
            连接池统计信息
        """
        stats = {
            "total_nodes": len(self.nodes),
            "healthy_nodes": len([n for n in self.nodes if n.status == NodeStatus.HEALTHY]),
            "degraded_nodes": len([n for n in self.nodes if n.status == NodeStatus.DEGRADED]),
            "unhealthy_nodes": len([n for n in self.nodes if n.status == NodeStatus.UNHEALTHY]),
            "offline_nodes": len([n for n in self.nodes if n.status == NodeStatus.OFFLINE]),
            "total_active_connections": sum(n.active_connections for n in self.nodes),
            "load_balance_strategy": self.load_balance_strategy.value,
            "is_health_check_running": self.is_running,
            "nodes": []
        }

        # 添加每个节点的详细信息
        for node in self.nodes:
            node_stats = {
                "endpoint": node.endpoint,
                "status": node.status.value,
                "weight": node.weight,
                "active_connections": node.active_connections,
                "success_rate": round(node.metrics.success_rate, 3),
                "average_response_time": round(node.metrics.average_response_time, 3),
                "success_count": node.metrics.success_count,
                "error_count": node.metrics.error_count,
                "consecutive_errors": node.metrics.consecutive_errors,
                "last_check_time": node.metrics.last_check_time.isoformat() if node.metrics.last_check_time else None,
                "last_error_time": node.metrics.last_error_time.isoformat() if node.metrics.last_error_time else None
            }
            stats["nodes"].append(node_stats)

        return stats

    def set_load_balance_strategy(self, strategy: LoadBalanceStrategy):
        """
        设置负载均衡策略
        
        Args:
            strategy: 负载均衡策略
        """
        self.load_balance_strategy = strategy
        self.logger.info(f"负载均衡策略已更新为: {strategy.value}")

    def add_node(self, endpoint: str, weight: float = 1.0, is_poa: bool = False):
        """
        添加新节点
        
        Args:
            endpoint: 节点端点
            weight: 节点权重
            is_poa: 是否为POA网络
        """
        new_node = BlockchainNode(
            endpoint=endpoint,
            weight=weight,
            is_poa=is_poa
        )

        self._init_node_connection(new_node)
        self.nodes.append(new_node)

        self.logger.info(f"添加新节点: {endpoint}")

    def remove_node(self, endpoint: str) -> bool:
        """
        移除节点
        
        Args:
            endpoint: 要移除的节点端点
            
        Returns:
            是否移除成功
        """
        for i, node in enumerate(self.nodes):
            if node.endpoint == endpoint:
                del self.nodes[i]
                self.logger.info(f"移除节点: {endpoint}")
                return True

        return False
