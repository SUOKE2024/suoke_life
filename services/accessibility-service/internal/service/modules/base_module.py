#!/usr/bin/env python

"""
无障碍服务基础模块

定义所有服务模块的通用接口和基础功能。
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ModuleConfig:
    """模块配置"""

    enabled: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5分钟
    max_retries: int = 3
    timeout: int = 30
    model_path: str | None = None
    device: str = "cpu"  # cpu, cuda, mps


@dataclass
class ProcessingResult:
    """处理结果"""

    success: bool
    data: Any = None
    error: str | None = None
    processing_time: float = 0.0
    confidence: float = 0.0
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class BaseModule(ABC):
    """无障碍服务基础模块"""

    def __init__(self, config: ModuleConfig, module_name: str):
        """
        初始化基础模块

        Args:
            config: 模块配置
            module_name: 模块名称
        """
        self.config = config
        self.module_name = module_name
        self.logger = logging.getLogger(f"{__name__}.{module_name}")
        self._model = None
        self._cache = {}
        self._stats = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "avg_processing_time": 0.0,
        }

        if self.config.enabled:
            self._initialize()

    def _initialize(self) -> None:
        """初始化模块"""
        try:
            self.logger.info(f"初始化{self.module_name}模块")
            self._load_model()
            self.logger.info(f"{self.module_name}模块初始化完成")
        except Exception as e:
            self.logger.error(f"{self.module_name}模块初始化失败: {e!s}")
            raise

    @abstractmethod
    def _load_model(self) -> None:
        """加载模型（子类实现）"""
        pass

    @abstractmethod
    def _process_request(self, request_data: dict[str, Any]) -> ProcessingResult:
        """处理请求（子类实现）"""
        pass

    def process(self, request_data: dict[str, Any]) -> ProcessingResult:
        """
        处理请求的通用入口

        Args:
            request_data: 请求数据

        Returns:
            处理结果
        """
        if not self.config.enabled:
            return ProcessingResult(
                success=False, error=f"{self.module_name}模块已禁用"
            )

        start_time = time.time()
        self._stats["requests_total"] += 1

        try:
            # 检查缓存
            cache_key = self._generate_cache_key(request_data)
            if self.config.cache_enabled and cache_key in self._cache:
                cached_result = self._cache[cache_key]
                if time.time() - cached_result["timestamp"] < self.config.cache_ttl:
                    self.logger.debug(f"使用缓存结果: {cache_key}")
                    return cached_result["result"]

            # 处理请求
            result = self._process_request(request_data)
            result.processing_time = time.time() - start_time

            # 更新统计信息
            if result.success:
                self._stats["requests_success"] += 1
            else:
                self._stats["requests_failed"] += 1

            self._update_avg_processing_time(result.processing_time)

            # 缓存结果
            if self.config.cache_enabled and result.success:
                self._cache[cache_key] = {"result": result, "timestamp": time.time()}
                self._cleanup_cache()

            return result

        except Exception as e:
            self._stats["requests_failed"] += 1
            self.logger.error(f"{self.module_name}处理请求失败: {e!s}")
            return ProcessingResult(
                success=False, error=str(e), processing_time=time.time() - start_time
            )

    def _generate_cache_key(self, request_data: dict[str, Any]) -> str:
        """生成缓存键"""
        # 简单的哈希实现，实际应用中可能需要更复杂的逻辑
        import hashlib

        key_str = str(sorted(request_data.items()))
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _cleanup_cache(self) -> None:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key
            for key, value in self._cache.items()
            if current_time - value["timestamp"] > self.config.cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]

    def _update_avg_processing_time(self, processing_time: float):
        """更新平均处理时间"""
        total_requests = self._stats["requests_total"]
        current_avg = self._stats["avg_processing_time"]
        self._stats["avg_processing_time"] = (
            current_avg * (total_requests - 1) + processing_time
        ) / total_requests

    def get_stats(self) -> dict[str, Any]:
        """获取模块统计信息"""
        return {
            "module_name": self.module_name,
            "enabled": self.config.enabled,
            "stats": self._stats.copy(),
            "cache_size": len(self._cache) if self.config.cache_enabled else 0,
        }

    def health_check(self) -> dict[str, Any]:
        """健康检查"""
        try:
            # 基础健康检查
            health_status = {
                "module": self.module_name,
                "status": "healthy" if self.config.enabled else "disabled",
                "model_loaded": self._model is not None,
                "cache_enabled": self.config.cache_enabled,
                "stats": self._stats,
            }

            # 子类可以重写此方法添加特定的健康检查
            additional_checks = self._additional_health_checks()
            health_status.update(additional_checks)

            return health_status

        except Exception as e:
            return {"module": self.module_name, "status": "unhealthy", "error": str(e)}

    def _additional_health_checks(self) -> dict[str, Any]:
        """额外的健康检查（子类可重写）"""
        return {}

    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self.logger.info(f"{self.module_name}模块缓存已清空")

    def reload_model(self) -> None:
        """重新加载模型"""
        try:
            self.logger.info(f"重新加载{self.module_name}模块模型")
            self._load_model()
            self.clear_cache()
            self.logger.info(f"{self.module_name}模块模型重新加载完成")
        except Exception as e:
            self.logger.error(f"{self.module_name}模块模型重新加载失败: {e!s}")
            raise
