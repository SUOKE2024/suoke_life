#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级缓存策略管理器
支持多层缓存、智能失效、预热机制和中医特色缓存
"""

import asyncio
import hashlib
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import pickle
from abc import ABC, abstractmethod
from loguru import logger

from ..observability.metrics import MetricsCollector

class CacheLevel(str, Enum):
    """缓存层级"""
    L1_MEMORY = "l1_memory"          # L1内存缓存
    L2_REDIS = "l2_redis"            # L2 Redis缓存
    L3_DISK = "l3_disk"              # L3磁盘缓存
    L4_DISTRIBUTED = "l4_distributed"  # L4分布式缓存

class CacheStrategy(str, Enum):
    """缓存策略"""
    LRU = "lru"                      # 最近最少使用
    LFU = "lfu"                      # 最少使用频率
    TTL = "ttl"                      # 时间过期
    ADAPTIVE = "adaptive"            # 自适应策略
    TCM_SEMANTIC = "tcm_semantic"    # 中医语义缓存

class InvalidationStrategy(str, Enum):
    """失效策略"""
    TIME_BASED = "time_based"        # 基于时间
    VERSION_BASED = "version_based"  # 基于版本
    DEPENDENCY_BASED = "dependency_based"  # 基于依赖
    SEMANTIC_BASED = "semantic_based"  # 基于语义

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    version: str = "1.0"
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def update_access(self):
        """更新访问信息"""
        self.last_accessed = time.time()
        self.access_count += 1

@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

class CacheBackend(ABC):
    """缓存后端抽象基类"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存条目"""
        pass
    
    @abstractmethod
    async def set(self, entry: CacheEntry) -> bool:
        """设置缓存条目"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存条目"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """获取统计信息"""
        pass

class MemoryCache(CacheBackend):
    """内存缓存后端"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = CacheStats()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存条目"""
        if key in self.cache:
            entry = self.cache[key]
            if entry.is_expired():
                await self.delete(key)
                self.stats.misses += 1
                return None
            
            entry.update_access()
            self.stats.hits += 1
            return entry
        
        self.stats.misses += 1
        return None
    
    async def set(self, entry: CacheEntry) -> bool:
        """设置缓存条目"""
        # 检查是否需要清理空间
        await self._ensure_space(entry.size_bytes)
        
        # 如果key已存在，更新统计
        if entry.key in self.cache:
            old_entry = self.cache[entry.key]
            self.stats.size_bytes -= old_entry.size_bytes
        else:
            self.stats.entry_count += 1
        
        self.cache[entry.key] = entry
        self.stats.size_bytes += entry.size_bytes
        
        return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存条目"""
        if key in self.cache:
            entry = self.cache.pop(key)
            self.stats.size_bytes -= entry.size_bytes
            self.stats.entry_count -= 1
            return True
        return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        self.cache.clear()
        self.stats = CacheStats()
        return True
    
    async def get_stats(self) -> CacheStats:
        """获取统计信息"""
        return self.stats
    
    async def _ensure_space(self, needed_bytes: int):
        """确保有足够空间"""
        # 检查条目数量限制
        while len(self.cache) >= self.max_size:
            await self._evict_lru()
        
        # 检查内存限制
        while self.stats.size_bytes + needed_bytes > self.max_memory_bytes:
            await self._evict_lru()
    
    async def _evict_lru(self):
        """驱逐最近最少使用的条目"""
        if not self.cache:
            return
        
        # 找到最近最少使用的条目
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        await self.delete(lru_key)
        self.stats.evictions += 1

class RedisCache(CacheBackend):
    """Redis缓存后端"""
    
    def __init__(self, redis_client, prefix: str = "rag_cache:"):
        self.redis = redis_client
        self.prefix = prefix
        self.stats = CacheStats()
    
    def _make_key(self, key: str) -> str:
        """生成Redis键"""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存条目"""
        redis_key = self._make_key(key)
        
        try:
            data = await self.redis.get(redis_key)
            if data is None:
                self.stats.misses += 1
                return None
            
            entry = pickle.loads(data)
            if entry.is_expired():
                await self.delete(key)
                self.stats.misses += 1
                return None
            
            entry.update_access()
            self.stats.hits += 1
            
            # 更新Redis中的访问信息
            await self.redis.set(redis_key, pickle.dumps(entry))
            
            return entry
            
        except Exception as e:
            logger.error(f"Redis缓存获取失败: {e}")
            self.stats.misses += 1
            return None
    
    async def set(self, entry: CacheEntry) -> bool:
        """设置缓存条目"""
        redis_key = self._make_key(entry.key)
        
        try:
            data = pickle.dumps(entry)
            
            if entry.ttl:
                await self.redis.setex(redis_key, int(entry.ttl), data)
            else:
                await self.redis.set(redis_key, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis缓存设置失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存条目"""
        redis_key = self._make_key(key)
        
        try:
            result = await self.redis.delete(redis_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis缓存删除失败: {e}")
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        try:
            pattern = f"{self.prefix}*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
            
        except Exception as e:
            logger.error(f"Redis缓存清空失败: {e}")
            return False
    
    async def get_stats(self) -> CacheStats:
        """获取统计信息"""
        return self.stats

class SemanticCacheManager:
    """语义缓存管理器"""
    
    def __init__(self, embedding_service, similarity_threshold: float = 0.85):
        self.embedding_service = embedding_service
        self.similarity_threshold = similarity_threshold
        self.semantic_index: Dict[str, Tuple[List[float], str]] = {}  # query_hash -> (embedding, cache_key)
    
    async def find_similar_query(self, query: str) -> Optional[str]:
        """查找语义相似的查询"""
        if not self.semantic_index:
            return None
        
        try:
            # 获取查询的嵌入向量
            query_embedding = await self.embedding_service.embed_text(query)
            
            # 计算与所有已缓存查询的相似度
            best_similarity = 0.0
            best_cache_key = None
            
            for query_hash, (cached_embedding, cache_key) in self.semantic_index.items():
                similarity = self._cosine_similarity(query_embedding, cached_embedding)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_cache_key = cache_key
            
            return best_cache_key
            
        except Exception as e:
            logger.error(f"语义相似查询查找失败: {e}")
            return None
    
    async def add_query_embedding(self, query: str, cache_key: str):
        """添加查询嵌入向量"""
        try:
            query_embedding = await self.embedding_service.embed_text(query)
            query_hash = hashlib.md5(query.encode()).hexdigest()
            self.semantic_index[query_hash] = (query_embedding, cache_key)
            
        except Exception as e:
            logger.error(f"添加查询嵌入向量失败: {e}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

class CachePrewarmer:
    """缓存预热器"""
    
    def __init__(self, cache_manager, metrics_collector: MetricsCollector):
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.prewarming_tasks: Dict[str, asyncio.Task] = {}
    
    async def prewarm_common_queries(self, queries: List[str]):
        """预热常见查询"""
        logger.info(f"开始预热 {len(queries)} 个常见查询")
        
        start_time = time.time()
        success_count = 0
        
        for query in queries:
            try:
                # 这里应该调用实际的查询处理逻辑
                # 暂时模拟预热过程
                await asyncio.sleep(0.1)  # 模拟处理时间
                success_count += 1
                
            except Exception as e:
                logger.error(f"预热查询失败 '{query}': {e}")
        
        duration = time.time() - start_time
        
        await self.metrics_collector.record_histogram(
            "cache_prewarm_duration_seconds",
            duration,
            {"type": "common_queries"}
        )
        
        await self.metrics_collector.record_histogram(
            "cache_prewarm_success_rate",
            success_count / len(queries) if queries else 0,
            {"type": "common_queries"}
        )
        
        logger.info(f"预热完成，成功率: {success_count}/{len(queries)}")
    
    async def prewarm_tcm_knowledge(self):
        """预热中医知识"""
        logger.info("开始预热中医知识缓存")
        
        # 常见中医查询
        tcm_queries = [
            "气虚体质的调理方法",
            "四君子汤的功效与作用",
            "肾阴虚的症状表现",
            "六味地黄丸的适应症",
            "脾胃虚弱的食疗方案",
            "血瘀证的辨证要点",
            "逍遥散的组成和功效",
            "阳虚体质的养生建议",
            "痰湿体质的特征",
            "补中益气汤的临床应用"
        ]
        
        await self.prewarm_common_queries(tcm_queries)
    
    async def start_background_prewarming(self):
        """启动后台预热任务"""
        if "tcm_knowledge" not in self.prewarming_tasks:
            task = asyncio.create_task(self._periodic_prewarm())
            self.prewarming_tasks["tcm_knowledge"] = task
    
    async def _periodic_prewarm(self):
        """定期预热任务"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时预热一次
                await self.prewarm_tcm_knowledge()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"定期预热任务失败: {e}")
                await asyncio.sleep(300)  # 出错后等待5分钟再试

class AdvancedCacheManager:
    """高级缓存管理器"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        metrics_collector: MetricsCollector,
        embedding_service=None,
        redis_client=None
    ):
        self.config = config
        self.metrics_collector = metrics_collector
        self.embedding_service = embedding_service
        
        # 初始化多层缓存后端
        self.backends: Dict[CacheLevel, CacheBackend] = {}
        self._init_backends(redis_client)
        
        # 语义缓存管理器
        if embedding_service:
            self.semantic_cache = SemanticCacheManager(
                embedding_service,
                config.get("semantic_similarity_threshold", 0.85)
            )
        else:
            self.semantic_cache = None
        
        # 缓存预热器
        self.prewarmer = CachePrewarmer(self, metrics_collector)
        
        # 失效策略
        self.invalidation_strategies = {
            InvalidationStrategy.TIME_BASED: self._time_based_invalidation,
            InvalidationStrategy.VERSION_BASED: self._version_based_invalidation,
            InvalidationStrategy.DEPENDENCY_BASED: self._dependency_based_invalidation,
            InvalidationStrategy.SEMANTIC_BASED: self._semantic_based_invalidation
        }
    
    def _init_backends(self, redis_client):
        """初始化缓存后端"""
        # L1内存缓存
        self.backends[CacheLevel.L1_MEMORY] = MemoryCache(
            max_size=self.config.get("l1_max_size", 1000),
            max_memory_mb=self.config.get("l1_max_memory_mb", 100)
        )
        
        # L2 Redis缓存
        if redis_client:
            self.backends[CacheLevel.L2_REDIS] = RedisCache(
                redis_client,
                self.config.get("redis_prefix", "rag_cache:")
            )
    
    async def get(
        self,
        key: str,
        use_semantic: bool = True,
        levels: Optional[List[CacheLevel]] = None
    ) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            use_semantic: 是否使用语义缓存
            levels: 指定查询的缓存层级
            
        Returns:
            缓存值或None
        """
        start_time = time.time()
        
        try:
            # 如果启用语义缓存，先尝试语义匹配
            if use_semantic and self.semantic_cache:
                semantic_key = await self.semantic_cache.find_similar_query(key)
                if semantic_key:
                    result = await self._get_from_levels(semantic_key, levels)
                    if result is not None:
                        await self._record_cache_metrics("semantic_hit", time.time() - start_time)
                        return result
            
            # 常规缓存查询
            result = await self._get_from_levels(key, levels)
            
            if result is not None:
                await self._record_cache_metrics("hit", time.time() - start_time)
            else:
                await self._record_cache_metrics("miss", time.time() - start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            await self._record_cache_metrics("error", time.time() - start_time)
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        levels: Optional[List[CacheLevel]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        add_semantic: bool = True
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            levels: 指定设置的缓存层级
            metadata: 元数据
            add_semantic: 是否添加到语义缓存
            
        Returns:
            是否成功
        """
        start_time = time.time()
        
        try:
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl,
                metadata=metadata or {},
                size_bytes=self._estimate_size(value)
            )
            
            # 设置到指定层级
            success = await self._set_to_levels(entry, levels)
            
            # 添加到语义缓存
            if add_semantic and self.semantic_cache and success:
                await self.semantic_cache.add_query_embedding(key, key)
            
            if success:
                await self._record_cache_metrics("set_success", time.time() - start_time)
            else:
                await self._record_cache_metrics("set_failure", time.time() - start_time)
            
            return success
            
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            await self._record_cache_metrics("set_error", time.time() - start_time)
            return False
    
    async def delete(
        self,
        key: str,
        levels: Optional[List[CacheLevel]] = None
    ) -> bool:
        """删除缓存"""
        try:
            success = True
            target_levels = levels or list(self.backends.keys())
            
            for level in target_levels:
                if level in self.backends:
                    result = await self.backends[level].delete(key)
                    success = success and result
            
            return success
            
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            return False
    
    async def invalidate(
        self,
        pattern: str,
        strategy: InvalidationStrategy = InvalidationStrategy.TIME_BASED,
        **kwargs
    ) -> int:
        """
        失效缓存
        
        Args:
            pattern: 失效模式
            strategy: 失效策略
            **kwargs: 策略参数
            
        Returns:
            失效的条目数量
        """
        try:
            invalidation_func = self.invalidation_strategies.get(strategy)
            if not invalidation_func:
                logger.error(f"未知的失效策略: {strategy}")
                return 0
            
            return await invalidation_func(pattern, **kwargs)
            
        except Exception as e:
            logger.error(f"缓存失效失败: {e}")
            return 0
    
    async def get_stats(self) -> Dict[CacheLevel, CacheStats]:
        """获取所有层级的统计信息"""
        stats = {}
        
        for level, backend in self.backends.items():
            try:
                stats[level] = await backend.get_stats()
            except Exception as e:
                logger.error(f"获取缓存统计失败 {level}: {e}")
                stats[level] = CacheStats()
        
        return stats
    
    async def start_prewarming(self):
        """启动缓存预热"""
        await self.prewarmer.start_background_prewarming()
    
    async def _get_from_levels(
        self,
        key: str,
        levels: Optional[List[CacheLevel]] = None
    ) -> Optional[Any]:
        """从指定层级获取缓存"""
        target_levels = levels or [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        for level in target_levels:
            if level in self.backends:
                entry = await self.backends[level].get(key)
                if entry is not None:
                    # 如果从L2获取到数据，回填到L1
                    if level != CacheLevel.L1_MEMORY and CacheLevel.L1_MEMORY in self.backends:
                        await self.backends[CacheLevel.L1_MEMORY].set(entry)
                    
                    return entry.value
        
        return None
    
    async def _set_to_levels(
        self,
        entry: CacheEntry,
        levels: Optional[List[CacheLevel]] = None
    ) -> bool:
        """设置到指定层级"""
        target_levels = levels or [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        success = True
        
        for level in target_levels:
            if level in self.backends:
                result = await self.backends[level].set(entry)
                success = success and result
        
        return success
    
    def _estimate_size(self, value: Any) -> int:
        """估算值的大小"""
        try:
            return len(pickle.dumps(value))
        except:
            return len(str(value).encode('utf-8'))
    
    async def _time_based_invalidation(self, pattern: str, max_age: float = 3600) -> int:
        """基于时间的失效策略"""
        # 这里应该实现基于时间的失效逻辑
        # 暂时返回0
        return 0
    
    async def _version_based_invalidation(self, pattern: str, version: str) -> int:
        """基于版本的失效策略"""
        # 这里应该实现基于版本的失效逻辑
        # 暂时返回0
        return 0
    
    async def _dependency_based_invalidation(self, pattern: str, dependencies: List[str]) -> int:
        """基于依赖的失效策略"""
        # 这里应该实现基于依赖的失效逻辑
        # 暂时返回0
        return 0
    
    async def _semantic_based_invalidation(self, pattern: str, similarity_threshold: float = 0.9) -> int:
        """基于语义的失效策略"""
        # 这里应该实现基于语义的失效逻辑
        # 暂时返回0
        return 0
    
    async def _record_cache_metrics(self, operation: str, duration: float):
        """记录缓存指标"""
        await self.metrics_collector.increment_counter(
            f"cache_operations_total",
            {"operation": operation}
        )
        
        await self.metrics_collector.record_histogram(
            "cache_operation_duration_seconds",
            duration,
            {"operation": operation}
        ) 