"""
circuit_breaker - 索克生活项目模块
"""

from enum import Enum
from internal.model.config import CircuitBreakerConfig
from typing import Dict, Optional
import logging
import time

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
熔断器模块，实现断路器模式
断路器模式用于防止系统持续尝试执行可能会失败的操作，
从而使系统继续运行并避免级联故障
"""



logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"  # 闭合状态，允许请求通过
    OPEN = "open"  # 打开状态，拒绝所有请求
    HALF_OPEN = "half_open"  # 半开状态，允许有限请求通过


class CircuitBreaker:
    """
    熔断器实现
    """

    def __init__(self, config: CircuitBreakerConfig, service_name: str):
"""
初始化熔断器

Args:
            config: 熔断器配置
            service_name: 服务名称
"""
self.config = config
self.service_name = service_name
self.state = CircuitState.CLOSED
self.failure_count = 0
self.success_count = 0
self.last_failure_time = 0
self.last_state_change_time = time.time()

    def allow_request(self) -> bool:
"""
检查是否允许请求通过

Returns:
            是否允许请求
"""
# 如果未启用熔断器，始终允许请求
if not self.config.enabled:
            return True

current_time = time.time()

if self.state==CircuitState.OPEN:
            # 检查是否达到重试超时时间
            if current_time - self.last_failure_time > self.config.recovery_timeout:
                logger.info(f"熔断器 {self.service_name} 从OPEN切换到HALF_OPEN状态")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.last_state_change_time = current_time
            else:
                return False

return True

    def record_result(self, success: bool) -> None:
"""
记录请求结果

Args:
            success: 请求是否成功
"""
# 如果未启用熔断器，不记录结果
if not self.config.enabled:
            return

current_time = time.time()

if self.state==CircuitState.CLOSED:
            if success:
                # 成功请求，重置失败计数
                self.failure_count = 0
            else:
                # 失败请求，增加失败计数
                self.failure_count+=1
                self.last_failure_time = current_time

                # 检查是否达到失败阈值
                if self.failure_count >=self.config.failure_threshold:
                    logger.warning(f"熔断器 {self.service_name} 从CLOSED切换到OPEN状态, 失败次数: {self.failure_count}")
                    self.state = CircuitState.OPEN
                    self.last_state_change_time = current_time

elif self.state==CircuitState.HALF_OPEN:
            if success:
                # 成功请求，增加成功计数
                self.success_count+=1

                # 检查是否达到成功阈值
                if self.success_count >=self.config.half_open_success:
                    logger.info(f"熔断器 {self.service_name} 从HALF_OPEN切换到CLOSED状态, 成功次数: {self.success_count}")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.last_state_change_time = current_time
            else:
                # 失败请求，回到OPEN状态
                logger.warning(f"熔断器 {self.service_name} 从HALF_OPEN切换回OPEN状态, 请求失败")
                self.state = CircuitState.OPEN
                self.last_failure_time = current_time
                self.last_state_change_time = current_time

    def reset(self) -> None:
"""
重置熔断器状态
"""
self.state = CircuitState.CLOSED
self.failure_count = 0
self.success_count = 0
self.last_state_change_time = time.time()
logger.info(f"熔断器 {self.service_name} 已重置")

    def get_state(self) -> CircuitState:
"""
获取当前状态

Returns:
            熔断器状态
"""
return self.state

    def get_metrics(self) -> Dict:
"""
获取熔断器指标

Returns:
            熔断器指标
"""
return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "last_state_change_time": self.last_state_change_time,
            "uptime": time.time() - self.last_state_change_time
}


class CircuitBreakerRegistry:
    """
    熔断器注册表，管理所有服务的熔断器
    """

    def __init__(self, config: CircuitBreakerConfig):
"""
初始化熔断器注册表

Args:
            config: 熔断器配置
"""
self.config = config
self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def get_or_create(self, service_name: str) -> CircuitBreaker:
"""
获取或创建服务的熔断器

Args:
            service_name: 服务名称

Returns:
            服务的熔断器
"""
if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(self.config, service_name)

return self.circuit_breakers[service_name]

    def reset(self, service_name: Optional[str] = None) -> None:
"""
重置熔断器

Args:
            service_name: 服务名称，为None时重置所有熔断器
"""
if service_name:
            if service_name in self.circuit_breakers:
                self.circuit_breakers[service_name].reset()
else:
            for circuit_breaker in self.circuit_breakers.values():
                circuit_breaker.reset()

    def get_all_metrics(self) -> Dict:
"""
获取所有熔断器指标

Returns:
            所有熔断器指标
"""
return {
            name: breaker.get_metrics()
            for name, breaker in self.circuit_breakers.items()
}
