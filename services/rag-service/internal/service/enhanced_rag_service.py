#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版RAG服务

该模块是RAG服务的增强版本，集成了所有优化组件，包括向量索引优化、
知识库分片存储、多级缓存、模型推理加速等，提供最高性能的检索增强生成服务。
"""

import asyncio
import time
import uuid
import hashlib
import json
from typing import Dict, List, Any, Optional, AsyncGenerator, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from loguru import logger

# 导入基础服务
from .rag_service import RagService
from ..model.document import Document, DocumentReference, RetrieveResult, GenerateResult, QueryResult
from ..repository.milvus_repository import MilvusRepository

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter, rate_limit
)
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

# 导入平台组件
from ..platform.model_manager import get_model_manager, ModelType

class IndexType(Enum):
    """索引类型"""
    FLAT = "FLAT"
    IVF_FLAT = "IVF_FLAT"
    IVF_SQ8 = "IVF_SQ8"
    IVF_PQ = "IVF_PQ"
    HNSW = "HNSW"
    ANNOY = "ANNOY"
    DISKANN = "DISKANN"

class ShardingStrategy(Enum):
    """分片策略"""
    HASH = "hash"
    RANGE = "range"
    CONSISTENT_HASH = "consistent_hash"
    DYNAMIC = "dynamic"

class CacheLevel(Enum):
    """缓存级别"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISK = "l3_disk"

@dataclass
class ShardInfo:
    """分片信息"""
    shard_id: str
    collection_name: str
    document_count: int
    size_mb: float
    last_updated: datetime
    status: str = "active"

@dataclass
class QueryPlan:
    """查询计划"""
    query_id: str
    shards: List[str]
    index_type: IndexType
    parallel: bool = True
    cache_strategy: str = "multi_level"
    estimated_time_ms: float = 0.0

@dataclass
class BatchInferenceRequest:
    """批量推理请求"""
    batch_id: str
    queries: List[str]
    contexts: List[List[Document]]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

class EnhancedRagService(RagService):
    """增强版RAG服务，集成了所有优化组件"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化增强版RAG服务
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        
        # 增强配置
        self.enhanced_config = {
            'sharding': {
                'enabled': True,
                'strategy': ShardingStrategy.CONSISTENT_HASH,
                'shard_count': 8,
                'replication_factor': 2
            },
            'indexing': {
                'default_type': IndexType.HNSW,
                'index_params': {
                    'HNSW': {'M': 16, 'ef_construction': 200},
                    'IVF_FLAT': {'nlist': 1024},
                    'IVF_PQ': {'nlist': 1024, 'm': 8, 'nbits': 8}
                }
            },
            'caching': {
                'multi_level': True,
                'l1_size_mb': 1024,
                'l2_size_mb': 4096,
                'l3_size_gb': 10,
                'ttl_seconds': {
                    'query': 300,
                    'embedding': 3600,
                    'document': 86400
                }
            },
            'inference': {
                'batch_size': 32,
                'max_batch_wait_ms': 50,
                'parallel_inference': True,
                'num_workers': 4
            }
        }
        
        # 分片管理
        self.shards: Dict[str, ShardInfo] = {}
        self.shard_connections: Dict[str, MilvusRepository] = {}
        
        # 批处理队列
        self.inference_queue: asyncio.Queue = asyncio.Queue()
        self.embedding_queue: asyncio.Queue = asyncio.Queue()
        
        # 多级缓存
        self.cache_levels: Dict[CacheLevel, Any] = {}
        
        # 性能统计
        self.stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_latency_ms': 0.0,
            'shard_queries': defaultdict(int),
            'index_usage': defaultdict(int),
            'batch_processed': 0
        }
        
        # 断路器配置
        self.circuit_breaker_configs = {
            'milvus': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=30.0
            ),
            'embedding': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=10.0
            ),
            'generator': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=45.0,
                timeout=60.0
            )
        }
        
        # 限流配置
        self.rate_limit_configs = {
            'query': RateLimitConfig(rate=100.0, burst=200),
            'embedding': RateLimitConfig(rate=50.0, burst=100),
            'generation': RateLimitConfig(rate=30.0, burst=60)
        }
        
        # 后台任务
        self.background_tasks: List[asyncio.Task] = []
        
        # 通过模型管理器加载生成模型和嵌入模型
        self.model_manager = get_model_manager()
        
        logger.info("增强版RAG服务初始化完成")
    
    async def initialize(self) -> None:
        """初始化所有组件"""
        await super().initialize()
        
        # 初始化分片
        await self._initialize_shards()
        
        # 初始化多级缓存
        await self._initialize_multi_level_cache()
        
        # 通过模型管理器加载生成模型和嵌入模型
        if self.model_manager:
            gen_model = await self.model_manager.get_model(
                self.config['generator']['model_name'],
                self.config['generator'].get('model_version')
            )
            if gen_model:
                self.generator = gen_model
            embed_model = await self.model_manager.get_model(
                self.config['embedding']['model_name'],
                self.config['embedding'].get('model_version')
            )
            if embed_model:
                self.embedding_service.set_model(embed_model)
        
        # 启动后台任务
        self._start_background_tasks()
        
        logger.info("增强版RAG服务组件初始化完成")
    
    async def _initialize_shards(self):
        """初始化分片"""
        if not self.enhanced_config['sharding']['enabled']:
            return
        
        shard_count = self.enhanced_config['sharding']['shard_count']
        
        for i in range(shard_count):
            shard_id = f"shard_{i}"
            collection_name = f"{self.config['vector_database']['collection_name']}_{shard_id}"
            
            # 创建分片信息
            self.shards[shard_id] = ShardInfo(
                shard_id=shard_id,
                collection_name=collection_name,
                document_count=0,
                size_mb=0.0,
                last_updated=datetime.now()
            )
            
            # 创建分片连接
            shard_config = self.config['vector_database'].copy()
            shard_config['collection_name'] = collection_name
            
            shard_repo = MilvusRepository(shard_config)
            await shard_repo.initialize()
            self.shard_connections[shard_id] = shard_repo
        
        logger.info(f"初始化了{shard_count}个分片")
    
    async def _initialize_multi_level_cache(self):
        """初始化多级缓存"""
        if not self.enhanced_config['caching']['multi_level']:
            return
        
        # L1: 内存缓存
        self.cache_levels[CacheLevel.L1_MEMORY] = {}
        
        # L2: Redis缓存（使用现有的缓存服务）
        self.cache_levels[CacheLevel.L2_REDIS] = self.cache_service
        
        # L3: 磁盘缓存（简化实现）
        self.cache_levels[CacheLevel.L3_DISK] = {}
        
        logger.info("多级缓存初始化完成")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 批量推理处理器
        self.background_tasks.append(
            asyncio.create_task(self._batch_inference_processor())
        )
        
        # 批量嵌入处理器
        self.background_tasks.append(
            asyncio.create_task(self._batch_embedding_processor())
        )
        
        # 缓存清理器
        self.background_tasks.append(
            asyncio.create_task(self._cache_cleaner())
        )
        
        # 分片平衡器
        self.background_tasks.append(
            asyncio.create_task(self._shard_balancer())
        )
        
        logger.info("后台任务启动完成")
    
    @trace(service_name="rag-service", kind=SpanKind.SERVER)
    @rate_limit(name="query", tokens=1)
    async def query(
        self,
        query: str,
        top_k: int = 5,
        system_prompt: Optional[str] = None,
        collection_names: Optional[List[str]] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> QueryResult:
        """
        执行增强版检索增强生成查询
        
        Args:
            query: 查询
            top_k: 检索文档数量
            system_prompt: 系统提示词
            collection_names: 集合名称列表
            generation_params: 生成参数
            metadata_filter: 元数据过滤条件
            user_id: 用户ID
            
        Returns:
            查询结果
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        # 生成查询计划
        query_plan = await self._generate_query_plan(
            query, collection_names, metadata_filter
        )
        
        # 检查多级缓存
        cache_key = self._generate_cache_key(
            "query", query, top_k, system_prompt, 
            collection_names, generation_params, metadata_filter
        )
        
        cached_result = await self._get_from_multi_level_cache(cache_key)
        if cached_result:
            self.stats['cache_hits'] += 1
            logger.info(f"多级缓存命中: {query}")
            return cached_result
        
        self.stats['cache_misses'] += 1
        
        # 执行分片并行检索
        retrieve_result = await self._parallel_shard_retrieve(
            query, top_k, query_plan, metadata_filter
        )
        
        # 批量推理优化
        if self._should_use_batch_inference():
            generate_result = await self._batch_generate(
                query, retrieve_result.documents, 
                system_prompt, generation_params, user_id
            )
        else:
            generate_result = await self.generate(
                query, retrieve_result.documents,
                system_prompt, generation_params, user_id
            )
        
        # 构建结果
        total_latency_ms = (time.time() - start_time) * 1000
        
        result = QueryResult(
            answer=generate_result.answer,
            references=generate_result.references,
            retrieval_latency_ms=retrieve_result.latency_ms,
            generation_latency_ms=generate_result.latency_ms,
            total_latency_ms=total_latency_ms
        )
        
        # 存储到多级缓存
        await self._set_to_multi_level_cache(cache_key, result)
        
        # 更新统计
        self._update_stats(total_latency_ms)
        
        return result
    
    async def _generate_query_plan(
        self,
        query: str,
        collection_names: Optional[List[str]],
        metadata_filter: Optional[Dict[str, Any]]
    ) -> QueryPlan:
        """生成查询计划"""
        query_id = str(uuid.uuid4())
        
        # 确定要查询的分片
        if self.enhanced_config['sharding']['enabled']:
            # 使用一致性哈希确定分片
            query_hash = hashlib.md5(query.encode()).hexdigest()
            primary_shard = f"shard_{int(query_hash[:8], 16) % len(self.shards)}"
            
            # 如果有元数据过滤，可能需要查询多个分片
            if metadata_filter:
                shards = list(self.shards.keys())  # 查询所有分片
            else:
                # 查询主分片和副本
                shards = [primary_shard]
                if self.enhanced_config['sharding']['replication_factor'] > 1:
                    replica_shard = f"shard_{(int(query_hash[:8], 16) + 1) % len(self.shards)}"
                    shards.append(replica_shard)
        else:
            shards = ["default"]
        
        # 选择索引类型
        index_type = self._select_index_type(query, len(shards))
        
        # 估算查询时间
        estimated_time = self._estimate_query_time(query, len(shards), index_type)
        
        return QueryPlan(
            query_id=query_id,
            shards=shards,
            index_type=index_type,
            parallel=len(shards) > 1,
            estimated_time_ms=estimated_time
        )
    
    def _select_index_type(self, query: str, shard_count: int) -> IndexType:
        """选择最优索引类型"""
        # 简单的启发式规则
        query_length = len(query.split())
        
        if query_length < 5 and shard_count == 1:
            # 短查询，单分片，使用精确索引
            return IndexType.FLAT
        elif shard_count > 4:
            # 多分片查询，使用压缩索引
            return IndexType.IVF_PQ
        else:
            # 默认使用HNSW
            return IndexType.HNSW
    
    def _estimate_query_time(
        self, 
        query: str, 
        shard_count: int, 
        index_type: IndexType
    ) -> float:
        """估算查询时间（毫秒）"""
        base_time = {
            IndexType.FLAT: 10.0,
            IndexType.IVF_FLAT: 5.0,
            IndexType.IVF_SQ8: 4.0,
            IndexType.IVF_PQ: 3.0,
            IndexType.HNSW: 2.0,
            IndexType.ANNOY: 2.5,
            IndexType.DISKANN: 3.5
        }
        
        # 基础时间 + 分片开销
        estimated_time = base_time.get(index_type, 5.0)
        if shard_count > 1:
            # 并行查询，取最大时间
            estimated_time *= 1.2
        else:
            estimated_time *= shard_count
        
        # 查询复杂度因子
        query_complexity = len(query.split()) * 0.5
        estimated_time += query_complexity
        
        return estimated_time
    
    async def _parallel_shard_retrieve(
        self,
        query: str,
        top_k: int,
        query_plan: QueryPlan,
        metadata_filter: Optional[Dict[str, Any]]
    ) -> RetrieveResult:
        """并行分片检索"""
        if not query_plan.parallel or len(query_plan.shards) == 1:
            # 单分片查询
            return await self._single_shard_retrieve(
                query, top_k, query_plan.shards[0], metadata_filter
            )
        
        # 并行查询多个分片
        tasks = []
        for shard_id in query_plan.shards:
            task = self._single_shard_retrieve(
                query, top_k * 2,  # 每个分片多检索一些
                shard_id, metadata_filter
            )
            tasks.append(task)
        
        # 等待所有分片结果
        shard_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        all_documents = []
        total_latency = 0.0
        
        for result in shard_results:
            if isinstance(result, Exception):
                logger.error(f"分片查询失败: {result}")
                continue
            
            all_documents.extend(result.documents)
            total_latency = max(total_latency, result.latency_ms)
        
        # 重新排序和截断
        all_documents.sort(key=lambda d: d.score if hasattr(d, 'score') else 0, reverse=True)
        top_documents = all_documents[:top_k]
        
        return RetrieveResult(
            documents=top_documents,
            latency_ms=total_latency
        )
    
    async def _single_shard_retrieve(
        self,
        query: str,
        top_k: int,
        shard_id: str,
        metadata_filter: Optional[Dict[str, Any]]
    ) -> RetrieveResult:
        """单分片检索"""
        start_time = time.time()
        
        # 获取分片连接
        if shard_id in self.shard_connections:
            repo = self.shard_connections[shard_id]
        else:
            repo = self.milvus_repository
        
        # 使用断路器保护
        breaker = await get_circuit_breaker(
            f"milvus_{shard_id}",
            self.circuit_breaker_configs['milvus']
        )
        
        async with breaker.protect():
            # 执行检索
            result = await self.retriever.retrieve(
                query=query,
                top_k=top_k,
                metadata_filter=metadata_filter
            )
        
        # 更新分片统计
        self.stats['shard_queries'][shard_id] += 1
        
        latency_ms = (time.time() - start_time) * 1000
        result.latency_ms = latency_ms
        
        return result
    
    def _should_use_batch_inference(self) -> bool:
        """判断是否应该使用批量推理"""
        # 基于队列长度和配置决定
        queue_size = self.inference_queue.qsize()
        return (
            self.enhanced_config['inference']['parallel_inference'] and
            queue_size < self.enhanced_config['inference']['batch_size'] * 2
        )
    
    async def _batch_generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str],
        generation_params: Optional[Dict[str, Any]],
        user_id: Optional[str]
    ) -> GenerateResult:
        """批量生成（将请求加入批处理队列）"""
        # 创建批量请求
        request = BatchInferenceRequest(
            batch_id=str(uuid.uuid4()),
            queries=[query],
            contexts=[context_documents],
            priority=1
        )
        
        # 创建结果Future
        result_future = asyncio.Future()
        
        # 加入队列
        await self.inference_queue.put((request, result_future))
        
        # 等待结果
        result = await result_future
        
        return result
    
    async def _batch_inference_processor(self):
        """批量推理处理器"""
        while True:
            try:
                batch = []
                batch_futures = []
                deadline = time.time() + self.enhanced_config['inference']['max_batch_wait_ms'] / 1000
                
                # 收集批次
                while len(batch) < self.enhanced_config['inference']['batch_size']:
                    try:
                        remaining_time = deadline - time.time()
                        if remaining_time <= 0:
                            break
                        
                        request, future = await asyncio.wait_for(
                            self.inference_queue.get(),
                            timeout=remaining_time
                        )
                        batch.append(request)
                        batch_futures.append(future)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    # 执行批量推理
                    results = await self._process_batch_inference(batch)
                    
                    # 返回结果
                    for i, future in enumerate(batch_futures):
                        if i < len(results):
                            future.set_result(results[i])
                        else:
                            future.set_exception(Exception("批量推理失败"))
                    
                    self.stats['batch_processed'] += 1
                
                await asyncio.sleep(0.01)  # 短暂休眠
                
            except Exception as e:
                logger.error(f"批量推理处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _process_batch_inference(
        self,
        batch: List[BatchInferenceRequest]
    ) -> List[GenerateResult]:
        """处理批量推理"""
        # 合并所有查询和上下文
        all_queries = []
        all_contexts = []
        
        for request in batch:
            all_queries.extend(request.queries)
            all_contexts.extend(request.contexts)
        
        # 并行处理
        if self.enhanced_config['inference']['parallel_inference']:
            # 分组并行处理
            num_workers = self.enhanced_config['inference']['num_workers']
            chunk_size = len(all_queries) // num_workers + 1
            
            tasks = []
            for i in range(0, len(all_queries), chunk_size):
                chunk_queries = all_queries[i:i+chunk_size]
                chunk_contexts = all_contexts[i:i+chunk_size]
                
                task = self._process_inference_chunk(chunk_queries, chunk_contexts)
                tasks.append(task)
            
            chunk_results = await asyncio.gather(*tasks)
            
            # 合并结果
            results = []
            for chunk in chunk_results:
                results.extend(chunk)
        else:
            # 串行处理
            results = await self._process_inference_chunk(all_queries, all_contexts)
        
        return results
    
    async def _process_inference_chunk(
        self,
        queries: List[str],
        contexts: List[List[Document]]
    ) -> List[GenerateResult]:
        """处理推理块"""
        results = []
        
        for query, context in zip(queries, contexts):
            try:
                result = await self.generator.generate(
                    query=query,
                    context_documents=context
                )
                results.append(result)
            except Exception as e:
                logger.error(f"推理失败: {e}")
                # 返回错误结果
                results.append(GenerateResult(
                    answer=f"生成失败: {str(e)}",
                    references=[],
                    latency_ms=0
                ))
        
        return results
    
    async def _batch_embedding_processor(self):
        """批量嵌入处理器"""
        while True:
            try:
                # 收集待嵌入的文档
                documents = []
                deadline = time.time() + 0.1  # 100ms收集窗口
                
                while time.time() < deadline and len(documents) < 100:
                    try:
                        doc = await asyncio.wait_for(
                            self.embedding_queue.get(),
                            timeout=deadline - time.time()
                        )
                        documents.append(doc)
                    except asyncio.TimeoutError:
                        break
                
                if documents:
                    # 批量生成嵌入
                    await self.embedding_service.embed_documents(documents)
                    logger.info(f"批量处理了{len(documents)}个文档的嵌入")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"批量嵌入处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _get_from_multi_level_cache(self, key: str) -> Optional[Any]:
        """从多级缓存获取数据"""
        # L1: 内存缓存
        if key in self.cache_levels[CacheLevel.L1_MEMORY]:
            logger.debug(f"L1缓存命中: {key}")
            return self.cache_levels[CacheLevel.L1_MEMORY][key]
        
        # L2: Redis缓存
        if self.cache_levels[CacheLevel.L2_REDIS]:
            value = await self.cache_levels[CacheLevel.L2_REDIS].get("query", key)
            if value:
                logger.debug(f"L2缓存命中: {key}")
                # 提升到L1
                self.cache_levels[CacheLevel.L1_MEMORY][key] = value
                return value
        
        # L3: 磁盘缓存（简化实现）
        if key in self.cache_levels[CacheLevel.L3_DISK]:
            logger.debug(f"L3缓存命中: {key}")
            value = self.cache_levels[CacheLevel.L3_DISK][key]
            # 提升到L1和L2
            self.cache_levels[CacheLevel.L1_MEMORY][key] = value
            if self.cache_levels[CacheLevel.L2_REDIS]:
                await self.cache_levels[CacheLevel.L2_REDIS].set("query", key, value)
            return value
        
        return None
    
    async def _set_to_multi_level_cache(self, key: str, value: Any):
        """设置多级缓存"""
        # 存储到所有级别
        self.cache_levels[CacheLevel.L1_MEMORY][key] = value
        
        if self.cache_levels[CacheLevel.L2_REDIS]:
            await self.cache_levels[CacheLevel.L2_REDIS].set(
                "query", key, value,
                ttl=self.enhanced_config['caching']['ttl_seconds']['query']
            )
        
        self.cache_levels[CacheLevel.L3_DISK][key] = value
    
    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_stats(self, latency_ms: float):
        """更新统计信息"""
        # 更新平均延迟（指数移动平均）
        alpha = 0.1
        if self.stats['average_latency_ms'] == 0:
            self.stats['average_latency_ms'] = latency_ms
        else:
            self.stats['average_latency_ms'] = (
                alpha * latency_ms + 
                (1 - alpha) * self.stats['average_latency_ms']
            )
    
    async def _cache_cleaner(self):
        """缓存清理器"""
        while True:
            try:
                # 清理L1内存缓存
                if len(self.cache_levels[CacheLevel.L1_MEMORY]) > 10000:
                    # 简单的LRU实现：删除一半
                    keys = list(self.cache_levels[CacheLevel.L1_MEMORY].keys())
                    for key in keys[:len(keys)//2]:
                        del self.cache_levels[CacheLevel.L1_MEMORY][key]
                    logger.info(f"清理了{len(keys)//2}个L1缓存项")
                
                # 清理L3磁盘缓存
                if len(self.cache_levels[CacheLevel.L3_DISK]) > 100000:
                    keys = list(self.cache_levels[CacheLevel.L3_DISK].keys())
                    for key in keys[:len(keys)//2]:
                        del self.cache_levels[CacheLevel.L3_DISK][key]
                    logger.info(f"清理了{len(keys)//2}个L3缓存项")
                
                await asyncio.sleep(300)  # 5分钟清理一次
                
            except Exception as e:
                logger.error(f"缓存清理器错误: {e}")
                await asyncio.sleep(60)
    
    async def _shard_balancer(self):
        """分片平衡器"""
        while True:
            try:
                if not self.enhanced_config['sharding']['enabled']:
                    await asyncio.sleep(3600)
                    continue
                
                # 检查分片负载
                total_queries = sum(self.stats['shard_queries'].values())
                if total_queries > 1000:
                    # 计算负载分布
                    avg_queries = total_queries / len(self.shards)
                    
                    for shard_id, query_count in self.stats['shard_queries'].items():
                        if query_count > avg_queries * 1.5:
                            logger.warning(f"分片{shard_id}负载过高: {query_count}次查询")
                            # 这里可以实现分片重平衡逻辑
                
                # 重置统计
                self.stats['shard_queries'].clear()
                
                await asyncio.sleep(3600)  # 每小时检查一次
                
            except Exception as e:
                logger.error(f"分片平衡器错误: {e}")
                await asyncio.sleep(300)
    
    async def add_documents_batch(
        self,
        documents: List[Document],
        collection_name: str = "default",
        use_sharding: bool = True
    ) -> List[str]:
        """批量添加文档（优化版）"""
        if not documents:
            return []
        
        # 生成ID
        for doc in documents:
            if not doc.id:
                doc.id = str(uuid.uuid4())
        
        # 批量生成嵌入（如果需要）
        docs_without_vectors = [d for d in documents if not d.vector]
        if docs_without_vectors:
            # 加入批处理队列
            for doc in docs_without_vectors:
                await self.embedding_queue.put(doc)
        
        # 分片存储
        if use_sharding and self.enhanced_config['sharding']['enabled']:
            # 按分片分组文档
            shard_docs = defaultdict(list)
            for doc in documents:
                shard_id = self._get_document_shard(doc)
                shard_docs[shard_id].append(doc)
            
            # 并行写入各分片
            tasks = []
            for shard_id, docs in shard_docs.items():
                if shard_id in self.shard_connections:
                    task = self.shard_connections[shard_id].add_documents(docs)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 更新分片信息
            for shard_id, docs in shard_docs.items():
                if shard_id in self.shards:
                    self.shards[shard_id].document_count += len(docs)
                    self.shards[shard_id].last_updated = datetime.now()
        else:
            # 直接存储
            await self.milvus_repository.add_documents(documents)
        
        return [doc.id for doc in documents]
    
    def _get_document_shard(self, document: Document) -> str:
        """获取文档所属分片"""
        if self.enhanced_config['sharding']['strategy'] == ShardingStrategy.CONSISTENT_HASH:
            # 使用文档ID的哈希值确定分片
            doc_hash = hashlib.md5(document.id.encode()).hexdigest()
            shard_index = int(doc_hash[:8], 16) % len(self.shards)
            return f"shard_{shard_index}"
        elif self.enhanced_config['sharding']['strategy'] == ShardingStrategy.RANGE:
            # 基于时间范围分片
            # 简化实现：使用ID的第一个字符
            shard_index = ord(document.id[0]) % len(self.shards)
            return f"shard_{shard_index}"
        else:
            # 默认使用第一个分片
            return "shard_0"
    
    async def optimize_indices(self):
        """优化向量索引"""
        logger.info("开始优化向量索引")
        
        # 分析查询模式
        most_used_index = max(
            self.stats['index_usage'].items(),
            key=lambda x: x[1],
            default=(IndexType.HNSW, 0)
        )[0]
        
        logger.info(f"最常用的索引类型: {most_used_index}")
        
        # 优化各分片的索引
        if self.enhanced_config['sharding']['enabled']:
            for shard_id, shard_repo in self.shard_connections.items():
                # 这里可以根据查询模式调整索引参数
                logger.info(f"优化分片{shard_id}的索引")
                # 实际的索引优化逻辑需要根据Milvus API实现
        
        logger.info("索引优化完成")
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        cache_hit_rate = (
            self.stats['cache_hits'] / 
            max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
        )
        
        return {
            'total_queries': self.stats['total_queries'],
            'cache_hit_rate': cache_hit_rate,
            'average_latency_ms': self.stats['average_latency_ms'],
            'batch_processed': self.stats['batch_processed'],
            'sharding': {
                'enabled': self.enhanced_config['sharding']['enabled'],
                'shard_count': len(self.shards),
                'shards': {
                    shard_id: {
                        'document_count': info.document_count,
                        'queries': self.stats['shard_queries'].get(shard_id, 0),
                        'status': info.status
                    }
                    for shard_id, info in self.shards.items()
                }
            },
            'cache_sizes': {
                'l1_memory': len(self.cache_levels.get(CacheLevel.L1_MEMORY, {})),
                'l3_disk': len(self.cache_levels.get(CacheLevel.L3_DISK, {}))
            },
            'queue_sizes': {
                'inference': self.inference_queue.qsize(),
                'embedding': self.embedding_queue.qsize()
            }
        }
    
    async def close(self):
        """关闭服务"""
        # 停止后台任务
        for task in self.background_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # 关闭分片连接
        for shard_repo in self.shard_connections.values():
            await shard_repo.close()
        
        # 调用父类关闭方法
        await super().close()
        
        logger.info("增强版RAG服务已关闭")
    
    async def reload_model(self, model_name: str, version: str = None):
        """支持热更新指定模型"""
        if self.model_manager:
            await self.model_manager.load_model(model_name, version)
        logger.info(f"模型{model_name}已热更新") 