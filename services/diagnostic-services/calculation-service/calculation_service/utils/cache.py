"""
缓存管理器
索克生活 - 算诊服务缓存管理
"""

import asyncio
import hashlib
import json
import logging
import time
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化缓存管理器

        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认缓存生存时间（秒）
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._access_times: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def initialize(self):
        """初始化缓存管理器"""
        logger.info("缓存管理器初始化完成")

    async def cleanup(self):
        """清理缓存管理器"""
        await self.clear_all()
        logger.info("缓存管理器已清理")

    def _generate_key(self, prefix: str, data: str | dict | Any) -> str:
        """生成缓存键"""
        if isinstance(data, dict):
            # 对字典进行排序后序列化，确保一致性
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        else:
            data_str = str(data)

        # 使用MD5生成短键
        hash_obj = hashlib.md5(data_str.encode("utf-8"))
        return f"{prefix}:{hash_obj.hexdigest()}"

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        async with self._lock:
            if key not in self._cache:
                return None

            cache_item = self._cache[key]

            # 检查是否过期
            if cache_item["expires_at"] < time.time():
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                return None

            # 更新访问时间
            self._access_times[key] = time.time()

            logger.debug(f"缓存命中: {key}")
            return cache_item["value"]

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """设置缓存值"""
        async with self._lock:
            if ttl is None:
                ttl = self._default_ttl

            expires_at = time.time() + ttl

            # 如果缓存已满，删除最久未访问的项
            if len(self._cache) >= self._max_size and key not in self._cache:
                await self._evict_lru()

            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
            }
            self._access_times[key] = time.time()

            logger.debug(f"缓存设置: {key}, TTL: {ttl}秒")

    async def delete(self, key: str) -> bool:
        """删除缓存项"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                logger.debug(f"缓存删除: {key}")
                return True
            return False

    async def clear_all(self) -> None:
        """清理所有缓存"""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()
            logger.info("所有缓存已清理")

    async def cleanup_expired(self) -> int:
        """清理过期缓存"""
        async with self._lock:
            current_time = time.time()
            expired_keys = []

            for key, cache_item in self._cache.items():
                if cache_item["expires_at"] < current_time:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]

            if expired_keys:
                logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")

            return len(expired_keys)

    async def _evict_lru(self) -> None:
        """删除最久未访问的缓存项"""
        if not self._access_times:
            return

        # 找到最久未访问的键
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])

        del self._cache[lru_key]
        del self._access_times[lru_key]

        logger.debug(f"LRU淘汰: {lru_key}")

    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        async with self._lock:
            current_time = time.time()
            expired_count = 0

            for cache_item in self._cache.values():
                if cache_item["expires_at"] < current_time:
                    expired_count += 1

            return {
                "total_items": len(self._cache),
                "expired_items": expired_count,
                "max_size": self._max_size,
                "usage_ratio": len(self._cache) / self._max_size
                if self._max_size > 0
                else 0,
                "default_ttl": self._default_ttl,
            }

    # 算诊特定的缓存方法
    async def cache_calculation_result(
        self, calc_type: str, input_data: dict, result: Any, ttl: int | None = None
    ) -> None:
        """缓存算诊结果"""
        key = self._generate_key(f"calc:{calc_type}", input_data)
        await self.set(key, result, ttl)

    async def get_calculation_result(
        self, calc_type: str, input_data: dict
    ) -> Any | None:
        """获取缓存的算诊结果"""
        key = self._generate_key(f"calc:{calc_type}", input_data)
        return await self.get(key)

    async def cache_ziwu_analysis(self, time_data: dict, result: Any) -> None:
        """缓存子午流注分析结果"""
        # 子午流注结果按小时缓存
        await self.cache_calculation_result("ziwu", time_data, result, ttl=3600)

    async def get_ziwu_analysis(self, time_data: dict) -> Any | None:
        """获取缓存的子午流注分析结果"""
        return await self.get_calculation_result("ziwu", time_data)

    async def cache_constitution_analysis(self, birth_data: dict, result: Any) -> None:
        """缓存体质分析结果"""
        # 体质分析结果长期缓存
        await self.cache_calculation_result(
            "constitution", birth_data, result, ttl=86400
        )

    async def get_constitution_analysis(self, birth_data: dict) -> Any | None:
        """获取缓存的体质分析结果"""
        return await self.get_calculation_result("constitution", birth_data)

    async def cache_bagua_analysis(self, birth_data: dict, result: Any) -> None:
        """缓存八卦分析结果"""
        # 八卦分析结果长期缓存
        await self.cache_calculation_result("bagua", birth_data, result, ttl=86400)

    async def get_bagua_analysis(self, birth_data: dict) -> Any | None:
        """获取缓存的八卦分析结果"""
        return await self.get_calculation_result("bagua", birth_data)

    async def cache_wuyun_liuqi_analysis(self, date_data: dict, result: Any) -> None:
        """缓存五运六气分析结果"""
        # 五运六气结果按日缓存
        await self.cache_calculation_result("wuyun_liuqi", date_data, result, ttl=86400)

    async def get_wuyun_liuqi_analysis(self, date_data: dict) -> Any | None:
        """获取缓存的五运六气分析结果"""
        return await self.get_calculation_result("wuyun_liuqi", date_data)


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached_calculation(cache_key_func=None):
    """
    算诊计算缓存装饰器

    Args:
        cache_key_func: 自定义缓存键生成函数
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_data = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": kwargs,
                }
                cache_key = cache_manager._generate_key(
                    f"calc:{func.__name__}", key_data
                )

            # 尝试从缓存获取结果
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 执行计算
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )

            # 缓存结果
            await cache_manager.set(cache_key, result)

            return result

        return wrapper

    return decorator


def generate_birth_info_cache_key(
    birth_info: dict[str, Any], analysis_date: str = None
) -> str:
    """
    生成出生信息缓存键

    Args:
        birth_info: 出生信息
        analysis_date: 分析日期

    Returns:
        缓存键
    """
    key_data = {"birth_info": birth_info, "analysis_date": analysis_date}
    return cache_manager._generate_key("calc:constitution", key_data)


def generate_time_analysis_cache_key(analysis_time: str) -> str:
    """
    生成时间分析缓存键

    Args:
        analysis_time: 分析时间

    Returns:
        缓存键
    """
    # 只缓存到小时级别，避免缓存过于细粒度
    time_parts = analysis_time.split(":")
    if len(time_parts) >= 2:
        hour_time = f"{time_parts[0]}:{time_parts[1]}"
    else:
        hour_time = analysis_time

    key_data = {"analysis_time": hour_time}
    return cache_manager._generate_key("calc:ziwu", key_data)
