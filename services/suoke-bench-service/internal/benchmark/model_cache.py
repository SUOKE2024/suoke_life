"""
model_cache - 索克生活项目模块
"""

from collections.abc import Callable
from dataclasses import dataclass
from internal.benchmark.model_interface import (
from threading import RLock
from typing import Any
import asyncio
import gc
import logging
import psutil
import time

"""
模型缓存管理器

提供高效的模型加载、缓存和内存管理功能
"""



    ModelInterface,
)

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""

    model: ModelInterface
    last_accessed: float
    access_count: int
    memory_usage: int  # 字节
    load_time: float


class ModelCache:
    """模型缓存管理器"""

    def __init__(
        self,
        max_memory_mb: int = 4096,
        max_models: int = 10,
        ttl_seconds: int = 3600,
        cleanup_interval: int = 300,
    ):
        """
        初始化模型缓存

        Args:
            max_memory_mb: 最大内存使用量（MB）
            max_models: 最大缓存模型数量
            ttl_seconds: 缓存生存时间（秒）
            cleanup_interval: 清理间隔（秒）
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_models = max_models
        self.ttl_seconds = ttl_seconds
        self.cleanup_interval = cleanup_interval

        self._cache: dict[str, CacheEntry] = {}
        self._lock = RLock()
        self._total_memory = 0

        # 启动后台清理任务
        self._cleanup_task = None
        self._start_cleanup_task()

        logger.info(
            f"模型缓存初始化完成，最大内存: {max_memory_mb}MB，最大模型数: {max_models}"
        )

    def _start_cleanup_task(self):
        """启动后台清理任务"""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.cleanup_interval)
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"缓存清理任务出错: {e}")

        try:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(cleanup_loop())
        except RuntimeError:
            # 如果没有运行的事件循环，稍后再启动
            pass

    def get_model(
        self,
        model_id: str,
        model_version: str,
        model_factory: Callable[[], ModelInterface],
    ) -> ModelInterface:
        """
        获取模型，如果不存在则加载

        Args:
            model_id: 模型ID
            model_version: 模型版本
            model_factory: 模型工厂函数

        Returns:
            模型实例
        """
        cache_key = f"{model_id}:{model_version}"

        with self._lock:
            # 检查缓存
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                entry.last_accessed = time.time()
                entry.access_count += 1
                logger.debug(f"从缓存获取模型: {cache_key}")
                return entry.model

            # 检查内存和数量限制
            self._ensure_capacity()

            # 加载新模型
            start_time = time.time()
            model = model_factory()
            load_time = time.time() - start_time

            # 估算内存使用
            memory_usage = self._estimate_model_memory(model)

            # 添加到缓存
            entry = CacheEntry(
                model=model,
                last_accessed=time.time(),
                access_count=1,
                memory_usage=memory_usage,
                load_time=load_time,
            )

            self._cache[cache_key] = entry
            self._total_memory += memory_usage

            logger.info(
                f"模型加载完成: {cache_key}, 耗时: {load_time:.2f}s, 内存: {memory_usage / 1024 / 1024:.1f}MB"
            )

            return model

    def _ensure_capacity(self):
        """确保缓存容量"""
        # 按访问时间排序，移除最久未使用的模型
        while (
            len(self._cache) >= self.max_models
            or self._total_memory > self.max_memory_bytes
        ):
            if not self._cache:
                break

            # 找到最久未使用的模型
            oldest_key = min(
                self._cache.keys(), key=lambda k: self._cache[k].last_accessed
            )

            self._remove_model(oldest_key)

    def _remove_model(self, cache_key: str):
        """移除模型"""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            self._total_memory -= entry.memory_usage
            del self._cache[cache_key]

            # 强制垃圾回收
            del entry.model
            gc.collect()

            logger.info(f"移除缓存模型: {cache_key}")

    def _cleanup_expired(self):
        """清理过期模型"""
        current_time = time.time()
        expired_keys = []

        with self._lock:
            for key, entry in self._cache.items():
                if current_time - entry.last_accessed > self.ttl_seconds:
                    expired_keys.append(key)

            for key in expired_keys:
                self._remove_model(key)

        if expired_keys:
            logger.info(f"清理过期模型: {len(expired_keys)} 个")

    def _estimate_model_memory(self, model: ModelInterface) -> int:
        """估算模型内存使用量"""
        try:
            # 获取当前进程内存使用
            process = psutil.Process()
            process.memory_info()

            # 简单估算：假设新加载的模型占用额外内存
            # 实际实现中可以更精确地计算
            if hasattr(model, "model") and model.model is not None:
                # 尝试获取模型参数大小
                if hasattr(model.model, "parameters"):
                    # PyTorch模型
                    try:
                        total_params = sum(p.numel() for p in model.model.parameters())
                        # 假设每个参数4字节（float32）
                        return total_params * 4
                    except Exception:
                        pass

                # 默认估算
                return 100 * 1024 * 1024  # 100MB

            return 50 * 1024 * 1024  # 50MB

        except Exception as e:
            logger.warning(f"内存估算失败: {e}")
            return 100 * 1024 * 1024  # 默认100MB

    def get_cache_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            return {
                "total_models": len(self._cache),
                "total_memory_mb": self._total_memory / 1024 / 1024,
                "max_memory_mb": self.max_memory_bytes / 1024 / 1024,
                "memory_usage_percent": (self._total_memory / self.max_memory_bytes)
                * 100,
                "models": {
                    key: {
                        "last_accessed": entry.last_accessed,
                        "access_count": entry.access_count,
                        "memory_mb": entry.memory_usage / 1024 / 1024,
                        "load_time": entry.load_time,
                    }
                    for key, entry in self._cache.items()
                },
            }

    def clear_cache(self):
        """清空缓存"""
        with self._lock:
            keys = list(self._cache.keys())
            for key in keys:
                self._remove_model(key)

            logger.info("缓存已清空")

    def preload_models(self, model_configs: dict[str, Callable[[], ModelInterface]]):
        """预加载模型"""
        logger.info(f"开始预加载 {len(model_configs)} 个模型")

        for model_key, factory in model_configs.items():
            try:
                model_id, model_version = model_key.split(":", 1)
                self.get_model(model_id, model_version, factory)
            except Exception as e:
                logger.error(f"预加载模型失败 {model_key}: {e}")

        logger.info("模型预加载完成")

    def __del__(self):
        """析构函数"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


# 全局模型缓存实例
_global_cache: ModelCache | None = None


def get_global_cache() -> ModelCache:
    """获取全局模型缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = ModelCache()
    return _global_cache


def init_global_cache(
    max_memory_mb: int = 4096,
    max_models: int = 10,
    ttl_seconds: int = 3600,
    cleanup_interval: int = 300,
):
    """初始化全局模型缓存"""
    global _global_cache
    _global_cache = ModelCache(
        max_memory_mb=max_memory_mb,
        max_models=max_models,
        ttl_seconds=ttl_seconds,
        cleanup_interval=cleanup_interval,
    )
    return _global_cache
