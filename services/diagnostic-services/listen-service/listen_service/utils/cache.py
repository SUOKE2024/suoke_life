"""
音频分析缓存工具

提供音频特征和分析结果的缓存功能，支持内存缓存和Redis缓存。
"""

import hashlib
import json
import pickle
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import structlog

from ..models.audio_models import AudioMetadata, VoiceFeatures
from ..models.tcm_models import TCMDiagnosis

logger = structlog.get_logger(__name__)

@dataclass
class CacheEntry:
    """缓存条目"""

    key: str
    value: Any
    created_at: float
    expires_at: float | None = None
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def access(self) -> None:
        """记录访问"""
        self.access_count += 1
        self.last_accessed = time.time()

class CacheBackend(ABC):
    """缓存后端抽象基类"""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """清空缓存"""
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        pass

class MemoryCache(CacheBackend):
    """内存缓存后端"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: dict[str, CacheEntry] = {}
        self.lock = threading.RLock()

        # 统计信息
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
        }

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                self.stats["misses"] += 1
                return None

            if entry.is_expired():
                del self.cache[key]
                self.stats["misses"] += 1
                return None

            entry.access()
            self.stats["hits"] += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        with self.lock:
            # 检查是否需要清理空间
            if len(self.cache) >= self.max_size:
                await self._evict_lru()

            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl if ttl > 0 else None

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                expires_at=expires_at,
            )

            self.cache[key] = entry
            self.stats["sets"] += 1
            return True

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats["deletes"] += 1
                return True
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return False

            if entry.is_expired():
                del self.cache[key]
                return False

            return True

    async def clear(self) -> bool:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            return True

    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                self.stats["hits"] / total_requests if total_requests > 0 else 0.0
            )

            return {
                **self.stats,
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate,
                "memory_usage": self._estimate_memory_usage(),
            }

    async def _evict_lru(self) -> None:
        """LRU淘汰策略"""
        if not self.cache:
            return

        # 找到最少使用的条目
        lru_key = min(
            self.cache.keys(),
            key=lambda k: (self.cache[k].last_accessed, self.cache[k].access_count),
        )

        del self.cache[lru_key]
        self.stats["evictions"] += 1

    def _estimate_memory_usage(self) -> int:
        """估算内存使用量"""
        try:
            import sys

            total_size = 0
            for entry in self.cache.values():
                total_size += sys.getsizeof(entry.key)
                total_size += sys.getsizeof(entry.value)
            return total_size
        except Exception:
            return 0

class RedisCache(CacheBackend):
    """Redis缓存后端"""

    def __init__(
        self, redis_url: str = "redis://localhost:6379", prefix: str = "listen_service"
    ):
        self.redis_url = redis_url
        self.prefix = prefix
        self.redis = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }

    async def _get_redis(self):
        """获取Redis连接"""
        if self.redis is None:
            try:

                self.redis = redis.from_url(self.redis_url, decode_responses=False)
                await self.redis.ping()
                logger.info("Redis连接已建立", url=self.redis_url)
            except ImportError:
                logger.error("redis包未安装，无法使用Redis缓存")
                raise
            except Exception as e:
                logger.error("Redis连接失败", error=str(e))
                raise
        return self.redis

    def _make_key(self, key: str) -> str:
        """生成带前缀的键"""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        try:
            redis = await self._get_redis()
            redis_key = self._make_key(key)

            data = await redis.get(redis_key)
            if data is None:
                self.stats["misses"] += 1
                return None

            value = pickle.loads(data)
            self.stats["hits"] += 1
            return value

        except Exception as e:
            logger.error("Redis获取失败", key=key, error=str(e))
            self.stats["errors"] += 1
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        try:
            redis = await self._get_redis()
            redis_key = self._make_key(key)

            data = pickle.dumps(value)

            if ttl:
                await redis.setex(redis_key, ttl, data)
            else:
                await redis.set(redis_key, data)

            self.stats["sets"] += 1
            return True

        except Exception as e:
            logger.error("Redis设置失败", key=key, error=str(e))
            self.stats["errors"] += 1
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            redis = await self._get_redis()
            redis_key = self._make_key(key)

            result = await redis.delete(redis_key)
            self.stats["deletes"] += 1
            return result > 0

        except Exception as e:
            logger.error("Redis删除失败", key=key, error=str(e))
            self.stats["errors"] += 1
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            redis = await self._get_redis()
            redis_key = self._make_key(key)

            result = await redis.exists(redis_key)
            return result > 0

        except Exception as e:
            logger.error("Redis检查存在失败", key=key, error=str(e))
            self.stats["errors"] += 1
            return False

    async def clear(self) -> bool:
        """清空缓存"""
        try:
            redis = await self._get_redis()
            pattern = f"{self.prefix}:*"

            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)

            return True

        except Exception as e:
            logger.error("Redis清空失败", error=str(e))
            self.stats["errors"] += 1
            return False

    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        try:
            redis = await self._get_redis()
            info = await redis.info()

            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                self.stats["hits"] / total_requests if total_requests > 0 else 0.0
            )

            return {
                **self.stats,
                "hit_rate": hit_rate,
                "redis_info": {
                    "used_memory": info.get("used_memory", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                },
            }

        except Exception as e:
            logger.error("获取Redis统计失败", error=str(e))
            return self.stats

class AudioCache:
    """音频分析缓存管理器"""

    def __init__(
        self,
        backend: CacheBackend | None = None,
        enable_compression: bool = True,
        cache_features: bool = True,
        cache_diagnosis: bool = True,
    ):
        self.backend = backend or MemoryCache()
        self.enable_compression = enable_compression
        self.cache_features = cache_features
        self.cache_diagnosis = cache_diagnosis

        # 缓存键前缀
        self.FEATURES_PREFIX = "features"
        self.DIAGNOSIS_PREFIX = "diagnosis"
        self.METADATA_PREFIX = "metadata"

        logger.info(
            "音频缓存初始化完成",
            backend=type(self.backend).__name__,
            compression=enable_compression,
            cache_features=cache_features,
            cache_diagnosis=cache_diagnosis,
        )

    def _generate_cache_key(self, prefix: str, audio_hash: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [prefix, audio_hash]

        # 添加额外的键参数
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")

        return ":".join(key_parts)

    def _hash_audio_data(self, audio_data: bytes) -> str:
        """计算音频数据哈希"""
        return hashlib.sha256(audio_data).hexdigest()[:16]

    def _hash_audio_metadata(self, metadata: AudioMetadata) -> str:
        """计算音频元数据哈希"""
        # 使用关键元数据生成哈希
        key_data = {
            "sample_rate": metadata.sample_rate,
            "channels": metadata.channels,
            "duration": round(metadata.duration, 2),  # 精确到0.01秒
            "format": metadata.format.value,
        }

        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()[:12]

    async def get_voice_features(
        self,
        audio_hash: str,
        analysis_type: str = "default",
    ) -> VoiceFeatures | None:
        """获取缓存的语音特征"""
        if not self.cache_features:
            return None

        cache_key = self._generate_cache_key(
            self.FEATURES_PREFIX,
            audio_hash,
            analysis_type=analysis_type,
        )

        try:
            cached_data = await self.backend.get(cache_key)
            if cached_data is not None:
                logger.debug("语音特征缓存命中", key=cache_key)
                return VoiceFeatures.model_validate(cached_data)
        except Exception as e:
            logger.warning("获取语音特征缓存失败", key=cache_key, error=str(e))

        return None

    async def set_voice_features(
        self,
        audio_hash: str,
        features: VoiceFeatures,
        analysis_type: str = "default",
        ttl: int = 3600,
    ) -> bool:
        """缓存语音特征"""
        if not self.cache_features:
            return False

        cache_key = self._generate_cache_key(
            self.FEATURES_PREFIX,
            audio_hash,
            analysis_type=analysis_type,
        )

        try:
            # 转换为可序列化的格式
            features_data = features.model_dump()

            success = await self.backend.set(cache_key, features_data, ttl)
            if success:
                logger.debug("语音特征已缓存", key=cache_key)
            return success

        except Exception as e:
            logger.warning("缓存语音特征失败", key=cache_key, error=str(e))
            return False

    async def get_tcm_diagnosis(
        self,
        audio_hash: str,
        analysis_method: str = "hybrid",
        user_profile: dict[str, Any] | None = None,
    ) -> TCMDiagnosis | None:
        """获取缓存的中医诊断"""
        if not self.cache_diagnosis:
            return None

        # 生成用户配置哈希
        profile_hash = ""
        if user_profile:
            profile_str = json.dumps(user_profile, sort_keys=True)
            profile_hash = hashlib.md5(profile_str.encode()).hexdigest()[:8]

        cache_key = self._generate_cache_key(
            self.DIAGNOSIS_PREFIX,
            audio_hash,
            method=analysis_method,
            profile=profile_hash,
        )

        try:
            cached_data = await self.backend.get(cache_key)
            if cached_data is not None:
                logger.debug("中医诊断缓存命中", key=cache_key)
                return TCMDiagnosis.model_validate(cached_data)
        except Exception as e:
            logger.warning("获取中医诊断缓存失败", key=cache_key, error=str(e))

        return None

    async def set_tcm_diagnosis(
        self,
        audio_hash: str,
        diagnosis: TCMDiagnosis,
        analysis_method: str = "hybrid",
        user_profile: dict[str, Any] | None = None,
        ttl: int = 1800,  # 30分钟
    ) -> bool:
        """缓存中医诊断"""
        if not self.cache_diagnosis:
            return False

        # 生成用户配置哈希
        profile_hash = ""
        if user_profile:
            profile_str = json.dumps(user_profile, sort_keys=True)
            profile_hash = hashlib.md5(profile_str.encode()).hexdigest()[:8]

        cache_key = self._generate_cache_key(
            self.DIAGNOSIS_PREFIX,
            audio_hash,
            method=analysis_method,
            profile=profile_hash,
        )

        try:
            # 转换为可序列化的格式
            diagnosis_data = diagnosis.model_dump()

            success = await self.backend.set(cache_key, diagnosis_data, ttl)
            if success:
                logger.debug("中医诊断已缓存", key=cache_key)
            return success

        except Exception as e:
            logger.warning("缓存中医诊断失败", key=cache_key, error=str(e))
            return False

    async def invalidate_audio_cache(self, audio_hash: str) -> bool:
        """清除特定音频的所有缓存"""
        try:
            # 这里简化处理，实际应该删除所有相关的键
            # 在生产环境中，可能需要维护键的索引

            # 删除特征缓存
            features_key = self._generate_cache_key(self.FEATURES_PREFIX, audio_hash)
            await self.backend.delete(features_key)

            # 删除诊断缓存
            diagnosis_key = self._generate_cache_key(self.DIAGNOSIS_PREFIX, audio_hash)
            await self.backend.delete(diagnosis_key)

            logger.info("音频缓存已清除", audio_hash=audio_hash)
            return True

        except Exception as e:
            logger.error("清除音频缓存失败", audio_hash=audio_hash, error=str(e))
            return False

    async def get_cache_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        try:
            backend_stats = await self.backend.get_stats()

            return {
                "backend": type(self.backend).__name__,
                "backend_stats": backend_stats,
                "config": {
                    "enable_compression": self.enable_compression,
                    "cache_features": self.cache_features,
                    "cache_diagnosis": self.cache_diagnosis,
                },
            }
        except Exception as e:
            logger.error("获取缓存统计失败", error=str(e))
            return {"error": str(e)}

    async def clear_all_cache(self) -> bool:
        """清空所有缓存"""
        try:
            success = await self.backend.clear()
            if success:
                logger.info("所有缓存已清空")
            return success
        except Exception as e:
            logger.error("清空缓存失败", error=str(e))
            return False

    async def get(self, key: str) -> Any | None:
        """通用获取方法，兼容AudioAnalyzer"""
        return await self.backend.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """通用设置方法，兼容AudioAnalyzer"""
        return await self.backend.set(key, value, ttl)

# 缓存装饰器
def cache_result(
    cache_instance: AudioCache,
    key_generator: Callable[..., str],
    ttl: int = 3600,
    cache_condition: Callable[..., bool] | None = None,
):
    """
    缓存结果装饰器

    Args:
        cache_instance: 缓存实例
        key_generator: 键生成函数
        ttl: 过期时间
        cache_condition: 缓存条件函数
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 检查缓存条件
            if cache_condition and not cache_condition(*args, **kwargs):
                return await func(*args, **kwargs)

            # 生成缓存键
            cache_key = key_generator(*args, **kwargs)

            # 尝试从缓存获取
            cached_result = await cache_instance.backend.get(cache_key)
            if cached_result is not None:
                logger.debug("缓存命中", function=func.__name__, key=cache_key)
                return cached_result

            # 执行函数
            result = await func(*args, **kwargs)

            # 缓存结果
            if result is not None:
                await cache_instance.backend.set(cache_key, result, ttl)
                logger.debug("结果已缓存", function=func.__name__, key=cache_key)

            return result

        return wrapper

    return decorator
