"""
负载均衡器核心实现
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """负载均衡策略枚举"""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"


class LoadBalancer(ABC):
    """负载均衡器抽象基类"""

    def __init__(
        self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    ):
        self.strategy = strategy
        self.endpoints: List = []
        self._current_index = 0

    def add_endpoint(self, endpoint):
        """添加服务端点"""
        self.endpoints.append(endpoint)
        logger.info(f"添加服务端点: {endpoint}")

    def remove_endpoint(self, endpoint):
        """移除服务端点"""
        if endpoint in self.endpoints:
            self.endpoints.remove(endpoint)
            logger.info(f"移除服务端点: {endpoint}")

    @abstractmethod
    def select_endpoint(self) -> Optional[object]:
        """选择服务端点"""
        pass

    def get_healthy_endpoints(self) -> List:
        """获取健康的服务端点"""
        return self.endpoints


class RoundRobinLoadBalancer(LoadBalancer):
    """轮询负载均衡器"""

    def select_endpoint(self) -> Optional[object]:
        """轮询选择端点"""
        healthy_endpoints = self.get_healthy_endpoints()
        if not healthy_endpoints:
            return None

        endpoint = healthy_endpoints[self._current_index % len(healthy_endpoints)]
        self._current_index += 1
        return endpoint


def main() -> None:
    """主函数"""
    pass


if __name__ == "__main__":
    main()
