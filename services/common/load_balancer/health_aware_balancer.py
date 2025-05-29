"""
健康感知负载均衡器
根据端点健康状态和性能指标进行智能负载均衡
"""

import logging
import time
from typing import Any

from .load_balancer import LoadBalancingAlgorithm, ServiceEndpoint

logger = logging.getLogger(__name__)


class HealthAwareLoadBalancer(LoadBalancingAlgorithm):
    """健康感知负载均衡器"""

    def __init__(self):
        self.health_weights = {}
        self.performance_weights = {}
        self.config = {}

    async def initialize(self, config: dict[str, Any]):
        """初始化健康感知负载均衡器"""
        self.config = config

        # 健康权重配置
        self.health_factor = config.get("health_factor", 0.4)
        self.performance_factor = config.get("performance_factor", 0.3)
        self.connection_factor = config.get("connection_factor", 0.3)

        # 性能阈值配置
        self.max_response_time = config.get("max_response_time", 1.0)
        self.max_failure_rate = config.get("max_failure_rate", 0.1)

        logger.info("健康感知负载均衡器初始化完成")

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """基于健康状态和性能指标选择端点"""
        if not endpoints:
            return None

        # 过滤不健康的端点
        healthy_endpoints = [ep for ep in endpoints if ep.healthy and ep.is_available()]
        if not healthy_endpoints:
            logger.warning("没有健康的端点可用")
            return None

        # 计算每个端点的综合得分
        scored_endpoints = []
        for endpoint in healthy_endpoints:
            score = await self._calculate_endpoint_score(endpoint)
            scored_endpoints.append((endpoint, score))

        # 按得分排序，选择得分最高的端点
        scored_endpoints.sort(key=lambda x: x[1], reverse=True)
        selected_endpoint = scored_endpoints[0][0]

        logger.debug(
            f"选择端点 {selected_endpoint.address}，得分: {scored_endpoints[0][1]:.3f}"
        )
        return selected_endpoint

    async def _calculate_endpoint_score(self, endpoint: ServiceEndpoint) -> float:
        """计算端点综合得分"""
        # 健康得分 (0-1)
        health_score = self._calculate_health_score(endpoint)

        # 性能得分 (0-1)
        performance_score = self._calculate_performance_score(endpoint)

        # 连接负载得分 (0-1)
        connection_score = self._calculate_connection_score(endpoint)

        # 综合得分
        total_score = (
            health_score * self.health_factor
            + performance_score * self.performance_factor
            + connection_score * self.connection_factor
        )

        return total_score

    def _calculate_health_score(self, endpoint: ServiceEndpoint) -> float:
        """计算健康得分"""
        if not endpoint.healthy:
            return 0.0

        # 基于失败次数计算健康得分
        if endpoint.failure_count == 0:
            return 1.0

        # 失败次数越多，得分越低
        failure_penalty = min(endpoint.failure_count * 0.1, 0.8)
        return max(1.0 - failure_penalty, 0.2)

    def _calculate_performance_score(self, endpoint: ServiceEndpoint) -> float:
        """计算性能得分"""
        if endpoint.response_time <= 0:
            return 1.0  # 没有响应时间数据时给满分

        # 响应时间越短，得分越高
        if endpoint.response_time <= self.max_response_time * 0.5:
            return 1.0
        elif endpoint.response_time <= self.max_response_time:
            # 线性衰减
            ratio = endpoint.response_time / self.max_response_time
            return max(1.0 - ratio, 0.1)
        else:
            return 0.1  # 响应时间过长，给最低分

    def _calculate_connection_score(self, endpoint: ServiceEndpoint) -> float:
        """计算连接负载得分"""
        if endpoint.max_connections <= 0:
            return 1.0

        # 连接使用率
        connection_ratio = endpoint.current_connections / endpoint.max_connections

        if connection_ratio <= 0.5:
            return 1.0
        elif connection_ratio <= 0.8:
            # 连接使用率在50%-80%之间，线性衰减
            return 1.0 - (connection_ratio - 0.5) * 2
        else:
            # 连接使用率超过80%，快速衰减
            return max(0.2 - (connection_ratio - 0.8) * 2, 0.1)

    async def update_endpoint_metrics(
        self, endpoint: ServiceEndpoint, response_time: float, success: bool
    ):
        """更新端点性能指标"""
        if success:
            endpoint.record_success(response_time)
        else:
            endpoint.record_failure()

        # 更新健康权重缓存
        addr = endpoint.address
        self.health_weights[addr] = self._calculate_health_score(endpoint)
        self.performance_weights[addr] = self._calculate_performance_score(endpoint)

    async def get_endpoint_rankings(
        self, endpoints: list[ServiceEndpoint]
    ) -> list[dict[str, Any]]:
        """获取端点排名信息"""
        rankings = []

        for endpoint in endpoints:
            score = await self._calculate_endpoint_score(endpoint)
            health_score = self._calculate_health_score(endpoint)
            performance_score = self._calculate_performance_score(endpoint)
            connection_score = self._calculate_connection_score(endpoint)

            rankings.append(
                {
                    "address": endpoint.address,
                    "total_score": score,
                    "health_score": health_score,
                    "performance_score": performance_score,
                    "connection_score": connection_score,
                    "healthy": endpoint.healthy,
                    "current_connections": endpoint.current_connections,
                    "max_connections": endpoint.max_connections,
                    "response_time": endpoint.response_time,
                    "failure_count": endpoint.failure_count,
                    "weight": endpoint.weight,
                }
            )

        # 按总得分排序
        rankings.sort(key=lambda x: x["total_score"], reverse=True)
        return rankings


class AdaptiveLoadBalancer(LoadBalancingAlgorithm):
    """自适应负载均衡器 - 根据实时负载动态调整策略"""

    def __init__(self):
        self.strategies = {}
        self.current_strategy = None
        self.strategy_performance = {}
        self.evaluation_window = 60  # 评估窗口（秒）
        self.last_evaluation = 0

    async def initialize(self, config: dict[str, Any]):
        """初始化自适应负载均衡器"""
        from .algorithms import (
            LeastConnectionsBalancer,
            RoundRobinBalancer,
            WeightedRoundRobinBalancer,
        )

        # 初始化多种策略
        self.strategies = {
            "round_robin": RoundRobinBalancer(),
            "weighted_round_robin": WeightedRoundRobinBalancer(),
            "least_connections": LeastConnectionsBalancer(),
            "health_aware": HealthAwareLoadBalancer(),
        }

        # 初始化各策略
        for strategy in self.strategies.values():
            await strategy.initialize(config)

        # 默认策略
        self.current_strategy = "health_aware"

        # 性能统计
        for strategy_name in self.strategies:
            self.strategy_performance[strategy_name] = {
                "success_count": 0,
                "failure_count": 0,
                "total_response_time": 0.0,
                "request_count": 0,
            }

        logger.info("自适应负载均衡器初始化完成")

    async def select_endpoint(
        self,
        endpoints: list[ServiceEndpoint],
        client_info: dict[str, Any] | None = None,
    ) -> ServiceEndpoint | None:
        """使用当前最优策略选择端点"""
        # 定期评估策略性能
        current_time = time.time()
        if current_time - self.last_evaluation > self.evaluation_window:
            await self._evaluate_strategies()
            self.last_evaluation = current_time

        # 使用当前策略选择端点
        strategy = self.strategies[self.current_strategy]
        return await strategy.select_endpoint(endpoints, client_info)

    async def _evaluate_strategies(self):
        """评估各策略性能并选择最优策略"""
        best_strategy = self.current_strategy
        best_score = 0.0

        for strategy_name, performance in self.strategy_performance.items():
            if performance["request_count"] == 0:
                continue

            # 计算成功率
            success_rate = performance["success_count"] / performance["request_count"]

            # 计算平均响应时间
            avg_response_time = (
                performance["total_response_time"] / performance["request_count"]
            )

            # 综合得分（成功率权重0.7，响应时间权重0.3）
            score = success_rate * 0.7 + (1.0 / (1.0 + avg_response_time)) * 0.3

            if score > best_score:
                best_score = score
                best_strategy = strategy_name

        if best_strategy != self.current_strategy:
            logger.info(f"切换负载均衡策略: {self.current_strategy} -> {best_strategy}")
            self.current_strategy = best_strategy

    async def record_request_result(
        self, strategy_name: str, success: bool, response_time: float
    ):
        """记录请求结果"""
        if strategy_name in self.strategy_performance:
            perf = self.strategy_performance[strategy_name]
            perf["request_count"] += 1
            perf["total_response_time"] += response_time

            if success:
                perf["success_count"] += 1
            else:
                perf["failure_count"] += 1
