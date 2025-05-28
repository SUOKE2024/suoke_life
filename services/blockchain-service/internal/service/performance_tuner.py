#!/usr/bin/env python3

"""
性能调优器

该模块提供自动性能调优、资源使用优化、预测性维护等功能，
通过机器学习和统计分析自动优化系统性能参数。
"""

import asyncio
from collections import deque
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import logging
import statistics
import time
from typing import Any

from internal.model.config import AppConfig


class OptimizationTarget(Enum):
    """优化目标枚举"""
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESOURCE_USAGE = "resource_usage"
    ERROR_RATE = "error_rate"
    COST = "cost"
    BALANCED = "balanced"


class TuningStrategy(Enum):
    """调优策略枚举"""
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    PREDICTIVE = "predictive"


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    timestamp: datetime
    target_value: float | None = None
    weight: float = 1.0

    @property
    def deviation(self) -> float:
        """偏差值"""
        if self.target_value is None:
            return 0.0
        return abs(self.value - self.target_value) / max(self.target_value, 0.001)


@dataclass
class OptimizationAction:
    """优化动作"""
    parameter: str
    old_value: Any
    new_value: Any
    expected_impact: float
    confidence: float
    timestamp: datetime
    applied: bool = False
    actual_impact: float | None = None


@dataclass
class TuningResult:
    """调优结果"""
    optimization_id: str
    actions: list[OptimizationAction]
    before_metrics: dict[str, float]
    after_metrics: dict[str, float]
    improvement: float
    duration: float
    success: bool
    error_message: str | None = None


class PerformanceTuner:
    """性能调优器"""

    def __init__(self, config: AppConfig):
        """
        初始化性能调优器
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 调优配置
        self.optimization_target = OptimizationTarget.BALANCED
        self.tuning_strategy = TuningStrategy.ADAPTIVE
        self.tuning_interval = 300  # 5分钟
        self.min_data_points = 10  # 最少数据点数

        # 性能指标历史
        self.metrics_history: dict[str, deque] = {}
        self.max_history_size = 1000

        # 优化历史
        self.optimization_history: list[TuningResult] = []
        self.max_optimization_history = 100

        # 参数配置
        self.tunable_parameters = {
            "batch_size": {
                "min": 1,
                "max": 200,
                "step": 1,
                "current": 10,
                "impact_weight": 0.8
            },
            "cache_size": {
                "min": 100,
                "max": 5000,
                "step": 100,
                "current": 1000,
                "impact_weight": 0.6
            },
            "connection_pool_size": {
                "min": 5,
                "max": 50,
                "step": 5,
                "current": 20,
                "impact_weight": 0.7
            },
            "worker_threads": {
                "min": 2,
                "max": 20,
                "step": 2,
                "current": 8,
                "impact_weight": 0.5
            },
            "gas_limit": {
                "min": 1000000,
                "max": 15000000,
                "step": 500000,
                "current": 8000000,
                "impact_weight": 0.9
            }
        }

        # 目标指标
        self.target_metrics = {
            "throughput": 100.0,  # 每秒处理数
            "latency": 2.0,       # 平均延迟（秒）
            "cpu_usage": 70.0,    # CPU使用率（%）
            "memory_usage": 80.0, # 内存使用率（%）
            "error_rate": 0.01,   # 错误率
            "cache_hit_rate": 0.9 # 缓存命中率
        }

        # 调优状态
        self.is_tuning = False
        self.tuning_task: asyncio.Task | None = None
        self.last_optimization: datetime | None = None

        # 回调函数
        self.parameter_update_callbacks: dict[str, Callable] = {}

        self.logger.info("性能调优器初始化完成")

    async def start_tuning(self):
        """启动性能调优"""
        if self.is_tuning:
            return

        self.is_tuning = True
        self.tuning_task = asyncio.create_task(self._tuning_loop())

        self.logger.info("性能调优已启动")

    async def stop_tuning(self):
        """停止性能调优"""
        if not self.is_tuning:
            return

        self.is_tuning = False

        if self.tuning_task:
            self.tuning_task.cancel()
            try:
                await self.tuning_task
            except asyncio.CancelledError:
                pass

        self.logger.info("性能调优已停止")

    def register_parameter_callback(self, parameter: str, callback: Callable):
        """
        注册参数更新回调
        
        Args:
            parameter: 参数名
            callback: 回调函数
        """
        self.parameter_update_callbacks[parameter] = callback
        self.logger.info(f"注册参数更新回调: {parameter}")

    def record_metric(self, name: str, value: float, target_value: float | None = None):
        """
        记录性能指标
        
        Args:
            name: 指标名称
            value: 指标值
            target_value: 目标值
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            target_value=target_value or self.target_metrics.get(name)
        )

        if name not in self.metrics_history:
            self.metrics_history[name] = deque(maxlen=self.max_history_size)

        self.metrics_history[name].append(metric)

    async def _tuning_loop(self):
        """调优循环"""
        while self.is_tuning:
            try:
                await asyncio.sleep(self.tuning_interval)

                # 检查是否有足够的数据进行优化
                if self._has_sufficient_data():
                    await self._perform_optimization()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"调优循环错误: {e!s}")
                await asyncio.sleep(60)  # 错误后等待1分钟

    def _has_sufficient_data(self) -> bool:
        """检查是否有足够的数据进行优化"""
        for name, history in self.metrics_history.items():
            if len(history) < self.min_data_points:
                return False

        return len(self.metrics_history) > 0

    async def _perform_optimization(self):
        """执行优化"""
        optimization_id = f"opt_{int(time.time())}"
        start_time = time.time()

        try:
            self.logger.info(f"开始性能优化: {optimization_id}")

            # 分析当前性能
            current_metrics = self._analyze_current_performance()

            # 生成优化建议
            optimization_actions = self._generate_optimization_actions(current_metrics)

            if not optimization_actions:
                self.logger.info("未发现需要优化的参数")
                return

            # 应用优化动作
            before_metrics = {name: metrics[-1].value for name, metrics in self.metrics_history.items()}

            for action in optimization_actions:
                await self._apply_optimization_action(action)

            # 等待一段时间观察效果
            await asyncio.sleep(60)  # 等待1分钟

            # 评估优化效果
            after_metrics = {name: metrics[-1].value for name, metrics in self.metrics_history.items()}
            improvement = self._calculate_improvement(before_metrics, after_metrics)

            # 记录优化结果
            result = TuningResult(
                optimization_id=optimization_id,
                actions=optimization_actions,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement=improvement,
                duration=time.time() - start_time,
                success=improvement > 0
            )

            self.optimization_history.append(result)
            if len(self.optimization_history) > self.max_optimization_history:
                self.optimization_history = self.optimization_history[-self.max_optimization_history:]

            self.last_optimization = datetime.now()

            self.logger.info(
                f"优化完成: {optimization_id}, 改进: {improvement:.2%}, "
                f"耗时: {result.duration:.2f}s"
            )

        except Exception as e:
            self.logger.error(f"优化执行失败: {e!s}")

    def _analyze_current_performance(self) -> dict[str, PerformanceMetric]:
        """分析当前性能"""
        current_metrics = {}

        for name, history in self.metrics_history.items():
            if history:
                # 使用最近的指标值
                recent_values = [m.value for m in list(history)[-10:]]
                avg_value = statistics.mean(recent_values)

                current_metrics[name] = PerformanceMetric(
                    name=name,
                    value=avg_value,
                    timestamp=datetime.now(),
                    target_value=self.target_metrics.get(name)
                )

        return current_metrics

    def _generate_optimization_actions(
        self,
        current_metrics: dict[str, PerformanceMetric]
    ) -> list[OptimizationAction]:
        """
        生成优化动作
        
        Args:
            current_metrics: 当前性能指标
            
        Returns:
            优化动作列表
        """
        actions = []

        # 根据优化目标和策略生成动作
        if self.optimization_target == OptimizationTarget.THROUGHPUT:
            actions.extend(self._optimize_for_throughput(current_metrics))
        elif self.optimization_target == OptimizationTarget.LATENCY:
            actions.extend(self._optimize_for_latency(current_metrics))
        elif self.optimization_target == OptimizationTarget.RESOURCE_USAGE:
            actions.extend(self._optimize_for_resource_usage(current_metrics))
        elif self.optimization_target == OptimizationTarget.ERROR_RATE:
            actions.extend(self._optimize_for_error_rate(current_metrics))
        else:  # BALANCED
            actions.extend(self._optimize_balanced(current_metrics))

        # 根据调优策略过滤动作
        actions = self._filter_actions_by_strategy(actions)

        return actions

    def _optimize_for_throughput(
        self,
        current_metrics: dict[str, PerformanceMetric]
    ) -> list[OptimizationAction]:
        """优化吞吐量"""
        actions = []

        throughput_metric = current_metrics.get("throughput")
        if throughput_metric and throughput_metric.target_value:
            if throughput_metric.value < throughput_metric.target_value:
                # 吞吐量不足，尝试增加批量大小和连接池大小
                actions.append(self._create_parameter_adjustment("batch_size", 1.2))
                actions.append(self._create_parameter_adjustment("connection_pool_size", 1.1))
                actions.append(self._create_parameter_adjustment("worker_threads", 1.1))

        return actions

    def _optimize_for_latency(
        self,
        current_metrics: dict[str, PerformanceMetric]
    ) -> list[OptimizationAction]:
        """优化延迟"""
        actions = []

        latency_metric = current_metrics.get("latency")
        if latency_metric and latency_metric.target_value:
            if latency_metric.value > latency_metric.target_value:
                # 延迟过高，尝试增加缓存大小和连接池大小
                actions.append(self._create_parameter_adjustment("cache_size", 1.2))
                actions.append(self._create_parameter_adjustment("connection_pool_size", 1.1))
                # 可能需要减少批量大小以降低延迟
                actions.append(self._create_parameter_adjustment("batch_size", 0.9))

        return actions

    def _optimize_for_resource_usage(
        self,
        current_metrics: dict[str, PerformanceMetric]
    ) -> list[OptimizationAction]:
        """优化资源使用"""
        actions = []

        cpu_metric = current_metrics.get("cpu_usage")
        memory_metric = current_metrics.get("memory_usage")

        if cpu_metric and cpu_metric.target_value and cpu_metric.value > cpu_metric.target_value:
            # CPU使用率过高
            actions.append(self._create_parameter_adjustment("worker_threads", 0.9))
            actions.append(self._create_parameter_adjustment("batch_size", 0.9))

        if memory_metric and memory_metric.target_value and memory_metric.value > memory_metric.target_value:
            # 内存使用率过高
            actions.append(self._create_parameter_adjustment("cache_size", 0.9))

        return actions

    def _optimize_for_error_rate(
        self,
        current_metrics: dict[str, PerformanceMetric]
    ) -> list[OptimizationAction]:
        """优化错误率"""
        actions = []

        error_rate_metric = current_metrics.get("error_rate")
        if error_rate_metric and error_rate_metric.target_value:
            if error_rate_metric.value > error_rate_metric.target_value:
                # 错误率过高，采用保守策略
                actions.append(self._create_parameter_adjustment("batch_size", 0.8))
                actions.append(self._create_parameter_adjustment("gas_limit", 1.1))
                actions.append(self._create_parameter_adjustment("connection_pool_size", 1.1))

        return actions

    def _optimize_balanced(
        self,
        current_metrics: dict[str, PerformanceMetric]
    ) -> list[OptimizationAction]:
        """平衡优化"""
        actions = []

        # 计算综合性能分数
        performance_score = self._calculate_performance_score(current_metrics)

        if performance_score < 0.8:  # 性能分数低于80%
            # 需要优化，根据最差的指标进行调整
            worst_metric = min(
                current_metrics.values(),
                key=lambda m: 1 - m.deviation if m.target_value else 0
            )

            if worst_metric.name == "throughput":
                actions.extend(self._optimize_for_throughput(current_metrics))
            elif worst_metric.name == "latency":
                actions.extend(self._optimize_for_latency(current_metrics))
            elif worst_metric.name in ["cpu_usage", "memory_usage"]:
                actions.extend(self._optimize_for_resource_usage(current_metrics))
            elif worst_metric.name == "error_rate":
                actions.extend(self._optimize_for_error_rate(current_metrics))

        return actions

    def _create_parameter_adjustment(
        self,
        parameter: str,
        multiplier: float
    ) -> OptimizationAction:
        """
        创建参数调整动作
        
        Args:
            parameter: 参数名
            multiplier: 调整倍数
            
        Returns:
            优化动作
        """
        param_config = self.tunable_parameters.get(parameter)
        if not param_config:
            raise ValueError(f"未知参数: {parameter}")

        old_value = param_config["current"]
        new_value = old_value * multiplier

        # 确保新值在有效范围内
        new_value = max(param_config["min"], min(new_value, param_config["max"]))

        # 按步长调整
        step = param_config["step"]
        new_value = round(new_value / step) * step

        # 计算预期影响
        expected_impact = abs(new_value - old_value) / old_value * param_config["impact_weight"]

        return OptimizationAction(
            parameter=parameter,
            old_value=old_value,
            new_value=new_value,
            expected_impact=expected_impact,
            confidence=0.7,  # 默认置信度
            timestamp=datetime.now()
        )

    def _filter_actions_by_strategy(
        self,
        actions: list[OptimizationAction]
    ) -> list[OptimizationAction]:
        """根据调优策略过滤动作"""
        if self.tuning_strategy == TuningStrategy.CONSERVATIVE:
            # 保守策略：只选择影响较小的动作
            return [a for a in actions if a.expected_impact < 0.2]
        elif self.tuning_strategy == TuningStrategy.AGGRESSIVE:
            # 激进策略：选择影响较大的动作
            return [a for a in actions if a.expected_impact > 0.1]
        elif self.tuning_strategy == TuningStrategy.PREDICTIVE:
            # 预测策略：基于历史数据选择最有可能成功的动作
            return self._select_predictive_actions(actions)
        else:  # ADAPTIVE
            # 自适应策略：根据最近的优化结果调整
            return self._select_adaptive_actions(actions)

    def _select_predictive_actions(
        self,
        actions: list[OptimizationAction]
    ) -> list[OptimizationAction]:
        """选择预测性动作"""
        # 基于历史优化结果预测成功概率
        if not self.optimization_history:
            return actions[:2]  # 如果没有历史数据，选择前两个动作

        # 分析历史成功的动作模式
        successful_actions = []
        for result in self.optimization_history:
            if result.success:
                successful_actions.extend(result.actions)

        # 根据历史成功率调整置信度
        for action in actions:
            similar_actions = [
                a for a in successful_actions
                if a.parameter == action.parameter
            ]
            if similar_actions:
                success_rate = len(similar_actions) / len(successful_actions)
                action.confidence = success_rate

        # 选择置信度最高的动作
        actions.sort(key=lambda a: a.confidence, reverse=True)
        return actions[:3]

    def _select_adaptive_actions(
        self,
        actions: list[OptimizationAction]
    ) -> list[OptimizationAction]:
        """选择自适应动作"""
        if not self.optimization_history:
            return actions[:2]

        # 分析最近的优化效果
        recent_results = self.optimization_history[-5:]
        avg_improvement = statistics.mean(r.improvement for r in recent_results)

        if avg_improvement > 0.1:
            # 最近优化效果好，可以尝试更多动作
            return actions[:4]
        elif avg_improvement < 0:
            # 最近优化效果不好，采用保守策略
            return [a for a in actions if a.expected_impact < 0.1][:1]
        else:
            # 效果一般，选择中等数量的动作
            return actions[:2]

    async def _apply_optimization_action(self, action: OptimizationAction):
        """
        应用优化动作
        
        Args:
            action: 优化动作
        """
        try:
            # 更新参数配置
            self.tunable_parameters[action.parameter]["current"] = action.new_value

            # 调用回调函数
            callback = self.parameter_update_callbacks.get(action.parameter)
            if callback:
                if asyncio.iscoroutinefunction(callback):
                    await callback(action.new_value)
                else:
                    callback(action.new_value)

            action.applied = True

            self.logger.info(
                f"应用优化动作: {action.parameter} "
                f"{action.old_value} -> {action.new_value}"
            )

        except Exception as e:
            self.logger.error(f"应用优化动作失败: {e!s}")
            action.applied = False

    def _calculate_improvement(
        self,
        before_metrics: dict[str, float],
        after_metrics: dict[str, float]
    ) -> float:
        """
        计算改进程度
        
        Args:
            before_metrics: 优化前指标
            after_metrics: 优化后指标
            
        Returns:
            改进程度（-1到1之间）
        """
        improvements = []

        for name, target_value in self.target_metrics.items():
            if name in before_metrics and name in after_metrics:
                before_value = before_metrics[name]
                after_value = after_metrics[name]

                if target_value:
                    # 计算相对于目标值的改进
                    before_deviation = abs(before_value - target_value) / target_value
                    after_deviation = abs(after_value - target_value) / target_value

                    improvement = (before_deviation - after_deviation) / before_deviation
                    improvements.append(improvement)

        return statistics.mean(improvements) if improvements else 0.0

    def _calculate_performance_score(
        self,
        current_metrics: dict[str, PerformanceMetric]
    ) -> float:
        """
        计算性能分数
        
        Args:
            current_metrics: 当前性能指标
            
        Returns:
            性能分数（0到1之间）
        """
        scores = []

        for metric in current_metrics.values():
            if metric.target_value:
                # 计算相对于目标值的分数
                deviation = metric.deviation
                score = max(0, 1 - deviation)
                scores.append(score)

        return statistics.mean(scores) if scores else 0.5

    def get_tuning_status(self) -> dict[str, Any]:
        """
        获取调优状态
        
        Returns:
            调优状态信息
        """
        current_metrics = self._analyze_current_performance()
        performance_score = self._calculate_performance_score(current_metrics)

        return {
            "is_tuning": self.is_tuning,
            "optimization_target": self.optimization_target.value,
            "tuning_strategy": self.tuning_strategy.value,
            "performance_score": performance_score,
            "last_optimization": self.last_optimization.isoformat() if self.last_optimization else None,
            "total_optimizations": len(self.optimization_history),
            "current_parameters": {
                name: config["current"]
                for name, config in self.tunable_parameters.items()
            },
            "metrics_data_points": {
                name: len(history)
                for name, history in self.metrics_history.items()
            }
        }

    def get_optimization_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        获取优化历史
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            优化历史列表
        """
        recent_history = self.optimization_history[-limit:] if limit > 0 else self.optimization_history
        return [asdict(result) for result in recent_history]

    def set_target_metric(self, name: str, target_value: float):
        """
        设置目标指标
        
        Args:
            name: 指标名称
            target_value: 目标值
        """
        self.target_metrics[name] = target_value
        self.logger.info(f"设置目标指标: {name} = {target_value}")

    def set_optimization_target(self, target: OptimizationTarget):
        """
        设置优化目标
        
        Args:
            target: 优化目标
        """
        self.optimization_target = target
        self.logger.info(f"设置优化目标: {target.value}")

    def set_tuning_strategy(self, strategy: TuningStrategy):
        """
        设置调优策略
        
        Args:
            strategy: 调优策略
        """
        self.tuning_strategy = strategy
        self.logger.info(f"设置调优策略: {strategy.value}")

    async def manual_optimization(self) -> TuningResult:
        """
        手动执行优化
        
        Returns:
            优化结果
        """
        if not self._has_sufficient_data():
            raise ValueError("数据不足，无法执行优化")

        await self._perform_optimization()

        if self.optimization_history:
            return self.optimization_history[-1]
        else:
            raise RuntimeError("优化执行失败")
