#!/usr/bin/env python3

"""
智能批量处理器

该模块提供智能的批量操作处理功能，包括动态批量大小调整、
智能重试机制、Gas优化策略等，提高区块链操作的效率和可靠性。
"""

import asyncio
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import logging
import statistics
import time
from typing import Any

from internal.model.config import AppConfig


class BatchStrategy(Enum):
    """批量策略枚举"""
    FIXED_SIZE = "fixed_size"
    DYNAMIC_SIZE = "dynamic_size"
    ADAPTIVE = "adaptive"
    GAS_OPTIMIZED = "gas_optimized"


class RetryStrategy(Enum):
    """重试策略枚举"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    ADAPTIVE = "adaptive"


@dataclass
class BatchItem:
    """批量处理项"""
    id: str
    data: dict[str, Any]
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    last_attempt: datetime | None = None
    error_message: str | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class BatchResult:
    """批量处理结果"""
    batch_id: str
    total_items: int
    successful_items: int
    failed_items: int
    processing_time: float
    gas_used: int | None = None
    gas_price: int | None = None
    transaction_hash: str | None = None
    error_details: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.error_details is None:
            self.error_details = []

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_items == 0:
            return 0.0
        return self.successful_items / self.total_items


@dataclass
class BatchMetrics:
    """批量处理指标"""
    average_batch_size: float = 0.0
    average_processing_time: float = 0.0
    average_gas_per_item: float = 0.0
    success_rate: float = 0.0
    throughput_per_second: float = 0.0
    total_batches: int = 0
    total_items: int = 0
    total_gas_used: int = 0


class SmartBatchProcessor:
    """智能批量处理器"""

    def __init__(self, config: AppConfig):
        """
        初始化智能批量处理器
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 批量处理配置
        self.min_batch_size = 1
        self.max_batch_size = 100
        self.default_batch_size = 10
        self.current_batch_size = self.default_batch_size

        # 策略配置
        self.batch_strategy = BatchStrategy.ADAPTIVE
        self.retry_strategy = RetryStrategy.ADAPTIVE

        # Gas优化配置
        self.target_gas_limit = 8000000  # 目标Gas限制
        self.gas_buffer_ratio = 0.1  # Gas缓冲比例
        self.gas_price_multiplier = 1.2  # Gas价格倍数

        # 性能指标
        self.metrics = BatchMetrics()
        self.recent_results: list[BatchResult] = []
        self.max_recent_results = 100

        # 处理队列
        self.pending_items: list[BatchItem] = []
        self.processing_batches: dict[str, list[BatchItem]] = {}

        # 处理器映射
        self.processors: dict[str, Callable] = {}

        # 自适应参数
        self.performance_window = 10  # 性能评估窗口
        self.adjustment_threshold = 0.1  # 调整阈值

        self.logger.info("智能批量处理器初始化完成")

    def register_processor(self, operation_type: str, processor: Callable):
        """
        注册批量处理器
        
        Args:
            operation_type: 操作类型
            processor: 处理函数
        """
        self.processors[operation_type] = processor
        self.logger.info(f"注册批量处理器: {operation_type}")

    async def submit_item(
        self,
        operation_type: str,
        data: dict[str, Any],
        priority: int = 1,
        max_retries: int = 3
    ) -> str:
        """
        提交批量处理项
        
        Args:
            operation_type: 操作类型
            data: 数据
            priority: 优先级
            max_retries: 最大重试次数
            
        Returns:
            项目ID
        """
        item_id = f"{operation_type}_{int(time.time() * 1000000)}"

        batch_item = BatchItem(
            id=item_id,
            data={
                "operation_type": operation_type,
                **data
            },
            priority=priority,
            max_retries=max_retries
        )

        self.pending_items.append(batch_item)

        # 按优先级排序
        self.pending_items.sort(key=lambda x: x.priority, reverse=True)

        self.logger.debug(f"提交批量处理项: {item_id}")
        return item_id

    async def process_pending_items(self) -> list[BatchResult]:
        """
        处理待处理项目
        
        Returns:
            批量处理结果列表
        """
        if not self.pending_items:
            return []

        results = []

        # 根据策略确定批量大小
        batch_size = self._determine_batch_size()

        # 分批处理
        while self.pending_items:
            # 取出一批项目
            batch_items = self.pending_items[:batch_size]
            self.pending_items = self.pending_items[batch_size:]

            if not batch_items:
                break

            # 处理批次
            result = await self._process_batch(batch_items)
            results.append(result)

            # 更新指标
            self._update_metrics(result)

            # 自适应调整
            if self.batch_strategy == BatchStrategy.ADAPTIVE:
                self._adaptive_adjustment()

        return results

    async def _process_batch(self, batch_items: list[BatchItem]) -> BatchResult:
        """
        处理单个批次
        
        Args:
            batch_items: 批次项目列表
            
        Returns:
            批量处理结果
        """
        batch_id = f"batch_{int(time.time() * 1000000)}"
        start_time = time.time()

        # 按操作类型分组
        grouped_items = {}
        for item in batch_items:
            operation_type = item.data.get("operation_type")
            if operation_type not in grouped_items:
                grouped_items[operation_type] = []
            grouped_items[operation_type].append(item)

        total_successful = 0
        total_failed = 0
        error_details = []
        total_gas_used = 0

        # 处理每个操作类型的项目
        for operation_type, items in grouped_items.items():
            try:
                processor = self.processors.get(operation_type)
                if not processor:
                    raise ValueError(f"未找到处理器: {operation_type}")

                # 执行批量处理
                batch_data = [item.data for item in items]
                result = await self._execute_with_retry(processor, batch_data)

                # 处理结果
                if isinstance(result, dict):
                    successful = result.get("successful_items", len(items))
                    failed = result.get("failed_items", 0)
                    gas_used = result.get("gas_used", 0)

                    total_successful += successful
                    total_failed += failed
                    total_gas_used += gas_used

                    # 记录错误详情
                    if "errors" in result:
                        error_details.extend(result["errors"])
                else:
                    # 简单成功结果
                    total_successful += len(items)

            except Exception as e:
                # 批次处理失败
                total_failed += len(items)
                error_details.append({
                    "operation_type": operation_type,
                    "error": str(e),
                    "items_count": len(items)
                })

                self.logger.error(f"批次处理失败 {operation_type}: {e!s}")

        processing_time = time.time() - start_time

        # 创建结果
        batch_result = BatchResult(
            batch_id=batch_id,
            total_items=len(batch_items),
            successful_items=total_successful,
            failed_items=total_failed,
            processing_time=processing_time,
            gas_used=total_gas_used,
            error_details=error_details
        )

        # 保存最近结果
        self.recent_results.append(batch_result)
        if len(self.recent_results) > self.max_recent_results:
            self.recent_results = self.recent_results[-self.max_recent_results:]

        self.logger.info(
            f"批次处理完成: {batch_id}, "
            f"成功: {total_successful}, 失败: {total_failed}, "
            f"耗时: {processing_time:.2f}s"
        )

        return batch_result

    async def _execute_with_retry(
        self,
        processor: Callable,
        batch_data: list[dict[str, Any]],
        max_retries: int = 3
    ) -> Any:
        """
        执行处理器并支持重试
        
        Args:
            processor: 处理器函数
            batch_data: 批量数据
            max_retries: 最大重试次数
            
        Returns:
            处理结果
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                # 执行处理器
                if asyncio.iscoroutinefunction(processor):
                    result = await processor(batch_data)
                else:
                    result = processor(batch_data)

                return result

            except Exception as e:
                last_exception = e

                if attempt < max_retries:
                    # 计算重试延迟
                    delay = self._calculate_retry_delay(attempt)

                    self.logger.warning(
                        f"批量处理失败，将在 {delay} 秒后重试 "
                        f"({attempt + 1}/{max_retries}): {e!s}"
                    )

                    await asyncio.sleep(delay)

        # 所有重试都失败
        raise last_exception

    def _determine_batch_size(self) -> int:
        """
        确定批量大小
        
        Returns:
            批量大小
        """
        if self.batch_strategy == BatchStrategy.FIXED_SIZE:
            return self.default_batch_size
        elif self.batch_strategy == BatchStrategy.DYNAMIC_SIZE:
            return self._dynamic_batch_size()
        elif self.batch_strategy == BatchStrategy.GAS_OPTIMIZED:
            return self._gas_optimized_batch_size()
        else:  # ADAPTIVE
            return self._adaptive_batch_size()

    def _dynamic_batch_size(self) -> int:
        """动态批量大小"""
        # 根据待处理项目数量调整
        pending_count = len(self.pending_items)

        if pending_count < 5:
            return min(pending_count, self.min_batch_size)
        elif pending_count < 20:
            return min(pending_count // 2, self.max_batch_size)
        else:
            return self.max_batch_size

    def _gas_optimized_batch_size(self) -> int:
        """Gas优化的批量大小"""
        if not self.recent_results:
            return self.default_batch_size

        # 计算平均每项Gas消耗
        recent_results = self.recent_results[-10:]  # 最近10次
        total_gas = sum(r.gas_used or 0 for r in recent_results)
        total_items = sum(r.total_items for r in recent_results)

        if total_items == 0:
            return self.default_batch_size

        avg_gas_per_item = total_gas / total_items

        if avg_gas_per_item == 0:
            return self.default_batch_size

        # 计算最优批量大小
        optimal_size = int(self.target_gas_limit * (1 - self.gas_buffer_ratio) / avg_gas_per_item)

        return max(self.min_batch_size, min(optimal_size, self.max_batch_size))

    def _adaptive_batch_size(self) -> int:
        """自适应批量大小"""
        if len(self.recent_results) < 3:
            return self.current_batch_size

        # 分析最近的性能
        recent_results = self.recent_results[-self.performance_window:]

        # 计算平均成功率和处理时间
        avg_success_rate = statistics.mean(r.success_rate for r in recent_results)
        avg_processing_time = statistics.mean(r.processing_time for r in recent_results)

        # 根据性能调整批量大小
        if avg_success_rate > 0.95 and avg_processing_time < 5.0:
            # 性能良好，可以增加批量大小
            new_size = min(int(self.current_batch_size * 1.2), self.max_batch_size)
        elif avg_success_rate < 0.8 or avg_processing_time > 10.0:
            # 性能不佳，减少批量大小
            new_size = max(int(self.current_batch_size * 0.8), self.min_batch_size)
        else:
            # 性能稳定，保持当前大小
            new_size = self.current_batch_size

        return new_size

    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        计算重试延迟
        
        Args:
            attempt: 重试次数
            
        Returns:
            延迟时间（秒）
        """
        if self.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return min(2 ** attempt, 60)  # 最大60秒
        elif self.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            return min(attempt * 2, 30)  # 最大30秒
        elif self.retry_strategy == RetryStrategy.FIXED_INTERVAL:
            return 5  # 固定5秒
        # 根据最近的成功率调整延迟
        elif self.recent_results:
            recent_success_rate = statistics.mean(
                r.success_rate for r in self.recent_results[-5:]
            )
            if recent_success_rate > 0.8:
                return min(2 ** attempt, 30)
            else:
                return min(2 ** attempt * 2, 60)
        else:
            return min(2 ** attempt, 60)

    def _update_metrics(self, result: BatchResult):
        """
        更新性能指标
        
        Args:
            result: 批量处理结果
        """
        self.metrics.total_batches += 1
        self.metrics.total_items += result.total_items
        self.metrics.total_gas_used += result.gas_used or 0

        # 更新移动平均
        alpha = 0.1  # 平滑因子

        if self.metrics.total_batches == 1:
            self.metrics.average_batch_size = result.total_items
            self.metrics.average_processing_time = result.processing_time
            self.metrics.success_rate = result.success_rate
            if result.gas_used and result.total_items > 0:
                self.metrics.average_gas_per_item = result.gas_used / result.total_items
        else:
            self.metrics.average_batch_size = (
                alpha * result.total_items +
                (1 - alpha) * self.metrics.average_batch_size
            )
            self.metrics.average_processing_time = (
                alpha * result.processing_time +
                (1 - alpha) * self.metrics.average_processing_time
            )
            self.metrics.success_rate = (
                alpha * result.success_rate +
                (1 - alpha) * self.metrics.success_rate
            )
            if result.gas_used and result.total_items > 0:
                gas_per_item = result.gas_used / result.total_items
                self.metrics.average_gas_per_item = (
                    alpha * gas_per_item +
                    (1 - alpha) * self.metrics.average_gas_per_item
                )

        # 计算吞吐量
        if result.processing_time > 0:
            throughput = result.total_items / result.processing_time
            self.metrics.throughput_per_second = (
                alpha * throughput +
                (1 - alpha) * self.metrics.throughput_per_second
            )

    def _adaptive_adjustment(self):
        """自适应调整"""
        if len(self.recent_results) < self.performance_window:
            return

        # 分析最近的性能趋势
        recent_results = self.recent_results[-self.performance_window:]

        # 计算性能指标的变化趋势
        success_rates = [r.success_rate for r in recent_results]
        processing_times = [r.processing_time for r in recent_results]

        # 检查是否需要调整批量大小
        if len(success_rates) >= 2:
            success_trend = success_rates[-1] - success_rates[0]
            time_trend = processing_times[-1] - processing_times[0]

            if success_trend < -self.adjustment_threshold or time_trend > self.adjustment_threshold:
                # 性能下降，减少批量大小
                self.current_batch_size = max(
                    int(self.current_batch_size * 0.9),
                    self.min_batch_size
                )
                self.logger.info(f"性能下降，调整批量大小为: {self.current_batch_size}")
            elif success_trend > self.adjustment_threshold and time_trend < -self.adjustment_threshold:
                # 性能提升，可以增加批量大小
                self.current_batch_size = min(
                    int(self.current_batch_size * 1.1),
                    self.max_batch_size
                )
                self.logger.info(f"性能提升，调整批量大小为: {self.current_batch_size}")

    def get_metrics(self) -> dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            性能指标信息
        """
        return {
            "metrics": asdict(self.metrics),
            "current_batch_size": self.current_batch_size,
            "pending_items": len(self.pending_items),
            "processing_batches": len(self.processing_batches),
            "recent_results_count": len(self.recent_results),
            "strategies": {
                "batch_strategy": self.batch_strategy.value,
                "retry_strategy": self.retry_strategy.value
            },
            "config": {
                "min_batch_size": self.min_batch_size,
                "max_batch_size": self.max_batch_size,
                "target_gas_limit": self.target_gas_limit,
                "gas_buffer_ratio": self.gas_buffer_ratio
            }
        }

    def get_recent_results(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        获取最近的处理结果
        
        Args:
            limit: 返回结果数量限制
            
        Returns:
            最近的处理结果列表
        """
        recent = self.recent_results[-limit:] if limit > 0 else self.recent_results
        return [asdict(result) for result in recent]

    def optimize_settings(self):
        """优化设置"""
        if len(self.recent_results) < 10:
            return

        # 分析最近的结果
        recent_results = self.recent_results[-20:]

        # 优化批量大小范围
        successful_results = [r for r in recent_results if r.success_rate > 0.9]
        if successful_results:
            optimal_sizes = [r.total_items for r in successful_results]
            avg_optimal_size = statistics.mean(optimal_sizes)

            # 调整批量大小范围
            self.min_batch_size = max(1, int(avg_optimal_size * 0.5))
            self.max_batch_size = min(200, int(avg_optimal_size * 2))

            self.logger.info(
                f"优化批量大小范围: {self.min_batch_size} - {self.max_batch_size}"
            )

        # 优化Gas设置
        gas_results = [r for r in recent_results if r.gas_used and r.gas_used > 0]
        if gas_results:
            avg_gas_usage = statistics.mean(r.gas_used for r in gas_results)

            # 调整目标Gas限制
            if avg_gas_usage < self.target_gas_limit * 0.5:
                self.target_gas_limit = int(avg_gas_usage * 2)
            elif avg_gas_usage > self.target_gas_limit * 0.9:
                self.target_gas_limit = int(avg_gas_usage * 1.2)

            self.logger.info(f"优化目标Gas限制: {self.target_gas_limit}")

    def set_strategy(self, batch_strategy: BatchStrategy, retry_strategy: RetryStrategy):
        """
        设置处理策略
        
        Args:
            batch_strategy: 批量策略
            retry_strategy: 重试策略
        """
        self.batch_strategy = batch_strategy
        self.retry_strategy = retry_strategy

        self.logger.info(
            f"更新处理策略: 批量={batch_strategy.value}, 重试={retry_strategy.value}"
        )
