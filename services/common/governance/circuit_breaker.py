#!/usr/bin/env python3
"""
断路器模式实现
提供故障隔离、快速失败和自动恢复功能
"""

import asyncio
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """断路器状态"""

    CLOSED = "closed"  # 关闭状态，正常工作
    OPEN = "open"  # 开启状态，快速失败
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复


@dataclass
class CircuitBreakerConfig:
    """断路器配置"""

    failure_threshold: int = 5  # 失败阈值
    recovery_timeout: float = 60.0  # 恢复超时时间（秒）
    expected_exception: type = Exception  # 预期的异常类型
    success_threshold: int = 3  # 半开状态成功阈值
    timeout: float = 30.0  # 调用超时时间


class CircuitBreakerError(Exception):
    """断路器异常"""

    pass


class CircuitBreakerOpenError(CircuitBreakerError):
    """断路器开启状态异常"""

    pass


class CircuitBreaker:
    """断路器实现"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.next_attempt_time = 0
        self._lock = asyncio.Lock()

        # 统计信息
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_open_count": 0,
            "state_changes": [],
        }

        logger.info(f"断路器初始化完成，配置: {config}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过断路器调用函数

        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数调用结果

        Raises:
            CircuitBreakerOpenError: 断路器开启状态
            Exception: 函数调用异常
        """
        async with self._lock:
            self.stats["total_calls"] += 1

            # 检查断路器状态
            await self._check_state()

            if self.state == CircuitState.OPEN:
                self.stats["circuit_open_count"] += 1
                raise CircuitBreakerOpenError(
                    f"断路器开启状态，下次尝试时间: {self.next_attempt_time}"
                )

        # 执行函数调用
        try:
            # 添加超时控制
            result = await asyncio.wait_for(
                func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs),
                timeout=self.config.timeout,
            )

            # 调用成功
            await self._on_success()
            return result

        except self.config.expected_exception:
            # 预期异常，记录失败
            await self._on_failure()
            raise
        except TimeoutError as e:
            # 超时异常
            await self._on_failure()
            raise CircuitBreakerError(f"调用超时: {self.config.timeout}秒") from e
        except Exception as e:
            # 其他异常，不计入失败统计
            logger.warning(f"断路器调用出现非预期异常: {e}")
            raise

    @asynccontextmanager
    async def protect(self):
        """
        上下文管理器方式使用断路器

        Usage:
            async with circuit_breaker.protect():
                result = await some_function()
        """
        async with self._lock:
            self.stats["total_calls"] += 1
            await self._check_state()

            if self.state == CircuitState.OPEN:
                self.stats["circuit_open_count"] += 1
                raise CircuitBreakerOpenError("断路器开启状态")

        try:
            yield
            await self._on_success()
        except self.config.expected_exception:
            await self._on_failure()
            raise
        except Exception:
            # 非预期异常不计入失败统计
            raise

    async def _check_state(self):
        """检查并更新断路器状态"""
        current_time = time.time()

        if self.state == CircuitState.OPEN:
            # 检查是否可以尝试恢复
            if current_time >= self.next_attempt_time:
                await self._change_state(CircuitState.HALF_OPEN)
                self.success_count = 0
                logger.info("断路器进入半开状态，尝试恢复")

    async def _on_success(self):
        """处理成功调用"""
        async with self._lock:
            self.stats["successful_calls"] += 1

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    await self._change_state(CircuitState.CLOSED)
                    self.failure_count = 0
                    logger.info("断路器恢复到关闭状态")
            elif self.state == CircuitState.CLOSED:
                # 重置失败计数
                self.failure_count = 0

    async def _on_failure(self):
        """处理失败调用"""
        async with self._lock:
            self.stats["failed_calls"] += 1
            self.failure_count += 1
            self.last_failure_time = time.time()

            if (
                self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)
            ) and self.failure_count >= self.config.failure_threshold:
                await self._change_state(CircuitState.OPEN)
                self.next_attempt_time = time.time() + self.config.recovery_timeout
                logger.warning(f"断路器开启，失败次数: {self.failure_count}")

    async def _change_state(self, new_state: CircuitState):
        """改变断路器状态"""
        old_state = self.state
        self.state = new_state

        # 记录状态变化
        self.stats["state_changes"].append(
            {"from": old_state.value, "to": new_state.value, "timestamp": time.time()}
        )

        logger.info(f"断路器状态变化: {old_state.value} -> {new_state.value}")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "current_state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_rate": (
                self.stats["failed_calls"] / self.stats["total_calls"]
                if self.stats["total_calls"] > 0
                else 0
            ),
            "next_attempt_time": self.next_attempt_time
            if self.state == CircuitState.OPEN
            else None,
        }

    async def reset(self):
        """重置断路器"""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = 0
            self.next_attempt_time = 0

            # 重置统计信息
            self.stats = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "circuit_open_count": 0,
                "state_changes": [],
            }

            logger.info("断路器已重置")


class CircuitBreakerRegistry:
    """断路器注册表，管理多个断路器实例"""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get_breaker(
        self, name: str, config: CircuitBreakerConfig | None = None
    ) -> CircuitBreaker:
        """
        获取或创建断路器

        Args:
            name: 断路器名称
            config: 断路器配置，如果不提供则使用默认配置

        Returns:
            CircuitBreaker: 断路器实例
        """
        async with self._lock:
            if name not in self._breakers:
                if config is None:
                    config = CircuitBreakerConfig()
                self._breakers[name] = CircuitBreaker(config)
                logger.info(f"创建新的断路器: {name}")

            return self._breakers[name]

    async def remove_breaker(self, name: str):
        """移除断路器"""
        async with self._lock:
            if name in self._breakers:
                del self._breakers[name]
                logger.info(f"移除断路器: {name}")

    def list_breakers(self) -> dict[str, dict[str, Any]]:
        """列出所有断路器及其状态"""
        return {name: breaker.get_stats() for name, breaker in self._breakers.items()}

    async def reset_all(self):
        """重置所有断路器"""
        async with self._lock:
            for breaker in self._breakers.values():
                await breaker.reset()
            logger.info("所有断路器已重置")


# 全局断路器注册表
_global_registry = CircuitBreakerRegistry()


async def get_circuit_breaker(
    name: str, config: CircuitBreakerConfig | None = None
) -> CircuitBreaker:
    """获取全局断路器实例"""
    return await _global_registry.get_breaker(name, config)
