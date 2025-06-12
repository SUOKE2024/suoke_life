"""
algorithms - 索克生活项目模块
"""

import asyncio
import hashlib
import random
import time
from typing import Any

from .load_balancer import LoadBalancingAlgorithm, ServiceEndpoint

"""
负载均衡算法实现
提供多种负载均衡策略的具体算法
"""


class RoundRobinBalancer(LoadBalancingAlgorithm):
    """轮询负载均衡算法"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.current_index = 0
        self.lock = asyncio.Lock()

    async def initialize(self, config: dict[str, Any]):
        """初始化算法"""
        pass

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """轮询选择端点"""
        if not endpoints:
            return None

        async with self.lock:
            endpoint = endpoints[self.current_index % len(endpoints)]
            self.current_index += 1
            return endpoint


class WeightedRoundRobinBalancer(LoadBalancingAlgorithm):
    """加权轮询负载均衡算法"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.current_weights = {}
        self.lock = asyncio.Lock()

    async def initialize(self, config: dict[str, Any]):
        """初始化算法"""
        pass

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """加权轮询选择端点"""
        if not endpoints:
            return None

        async with self.lock:
            # 计算总权重
            total_weight = sum(ep.weight for ep in endpoints)

            # 更新当前权重
            for endpoint in endpoints:
                addr = endpoint.address
                if addr not in self.current_weights:
                    self.current_weights[addr] = 0
                self.current_weights[addr] += endpoint.weight

            # 选择权重最高的端点
            selected_endpoint = max(
                endpoints, key=lambda ep: self.current_weights[ep.address]
            )

            # 减少选中端点的权重
            self.current_weights[selected_endpoint.address] -= total_weight

            return selected_endpoint


class LeastConnectionsBalancer(LoadBalancingAlgorithm):
    """最少连接负载均衡算法"""

    async def initialize(self, config: dict[str, Any]):
        """初始化算法"""
        pass

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """选择连接数最少的端点"""
        if not endpoints:
            return None

        # 选择当前连接数最少的端点
        return min(endpoints, key=lambda ep: ep.current_connections)


class IPHashBalancer(LoadBalancingAlgorithm):
    """IP哈希负载均衡算法"""

    async def initialize(self, config: dict[str, Any]):
        """初始化算法"""
        pass

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """基于客户端IP哈希选择端点"""
        if not endpoints:
            return None

        # 获取客户端IP
        client_ip = "127.0.0.1"  # 默认值
        if client_info and "client_ip" in client_info:
            client_ip = client_info["client_ip"]

        # 计算哈希值
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(endpoints)

        return endpoints[index]


class RandomBalancer(LoadBalancingAlgorithm):
    """随机负载均衡算法"""

    async def initialize(self, config: dict[str, Any]):
        """初始化算法"""
        random.seed(time.time())

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """随机选择端点"""
        if not endpoints:
            return None

        return random.choice(endpoints)


class ConsistentHashBalancer(LoadBalancingAlgorithm):
    """一致性哈希负载均衡算法"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.hash_ring = {}
        self.virtual_nodes = 150  # 虚拟节点数量

    async def initialize(self, config: dict[str, Any]):
        """初始化算法"""
        self.virtual_nodes = config.get("virtual_nodes", 150)

    def _hash(self, key: str) -> int:
        """计算哈希值"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _build_hash_ring(self, endpoints: list[ServiceEndpoint]):
        """构建哈希环"""
        self.hash_ring.clear()

        for endpoint in endpoints:
            for i in range(self.virtual_nodes):
                virtual_key = f"{endpoint.address}:{i}"
                hash_value = self._hash(virtual_key)
                self.hash_ring[hash_value] = endpoint

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """一致性哈希选择端点"""
        if not endpoints:
            return None

        # 重建哈希环（在实际应用中可以优化为只在端点变化时重建）
        self._build_hash_ring(endpoints)

        # 获取客户端标识
        client_key = "default"
        if client_info:
            if "client_ip" in client_info:
                client_key = client_info["client_ip"]
            elif "user_id" in client_info:
                client_key = client_info["user_id"]

        # 计算客户端哈希值
        client_hash = self._hash(client_key)

        # 在哈希环上查找最近的节点
        if not self.hash_ring:
            return endpoints[0]

        # 找到第一个大于等于客户端哈希值的节点
        sorted_hashes = sorted(self.hash_ring.keys())
        for hash_value in sorted_hashes:
            if hash_value >= client_hash:
                return self.hash_ring[hash_value]

        # 如果没找到，返回第一个节点（环形结构）
        return self.hash_ring[sorted_hashes[0]]
