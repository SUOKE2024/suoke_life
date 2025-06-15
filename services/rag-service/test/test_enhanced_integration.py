#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG服务集成测试
测试增强版RAG服务的所有功能
"""

import asyncio
import pytest
import time
from datetime import datetime
from typing import List, Dict, Any
import json
import numpy as np

from services.rag_service.internal.service.enhanced_rag_service import (
    EnhancedRagService, IndexType, ShardingStrategy, CacheLevel
)
from services.rag_service.internal.model.document import Document

@pytest.fixture
async def rag_service():
    """创建RAG服务实例"""
    config = {
        "service": {
            "name": "rag-service-test",
            "version": "2.0.0"
        },
        "vector_database": {
            "host": "localhost",
            "port": 19530,
            "collection_name": "test_documents"
        },
        "generator": {
            "model_type": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "cache": {
            "redis_url": "redis://localhost:6379/15"
        }
    }
    
    service = EnhancedRagService(config)
    await service.initialize()
    yield service
    await service.close()

class TestEnhancedRagService:
    """增强版RAG服务测试类"""
    
    @pytest.mark.asyncio
    async def test_multi_level_cache(self, rag_service):
        """测试多级缓存功能"""
        # 第一次查询
        query = "什么是中医的辨证论治？"
        start_time = time.time()
        result1 = await rag_service.query(query, top_k=5)
        first_query_time = time.time() - start_time
        
        assert result1.answer
        assert result1.total_latency_ms > 0
        
        # 第二次查询（应该从缓存获取）
        start_time = time.time()
        result2 = await rag_service.query(query, top_k=5)
        cached_query_time = time.time() - start_time
        
        # 验证缓存命中
        assert result2.answer == result1.answer
        assert cached_query_time < first_query_time * 0.1  # 缓存查询应该快10倍以上
        
        # 检查统计信息
        stats = await rag_service.get_service_stats()
        assert stats['cache_hit_rate'] > 0
        print(f"缓存命中率: {stats['cache_hit_rate']:.2%}")
    
    @pytest.mark.asyncio
    async def test_document_sharding(self, rag_service):
        """测试文档分片存储"""
        # 创建测试文档
        documents = []
        for i in range(100):
            doc = Document(
                content=f"测试文档{i}：这是关于中医养生的内容，包括饮食调理、运动养生等方面。",
                metadata={
                    "category": f"category_{i % 5}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            documents.append(doc)
        
        # 批量添加文档（使用分片）
        doc_ids = await rag_service.add_documents_batch(
            documents=documents,
            use_sharding=True
        )
        
        assert len(doc_ids) == 100
        
        # 检查分片分布
        stats = await rag_service.get_service_stats()
        shard_info = stats['sharding']['shards']
        
        # 验证文档分布到多个分片
        shards_with_docs = sum(1 for s in shard_info.values() if s['document_count'] > 0)
        assert shards_with_docs > 1
        
        print(f"文档分布到{shards_with_docs}个分片")
        for shard_id, info in shard_info.items():
            print(f"  {shard_id}: {info['document_count']}个文档")
    
    @pytest.mark.asyncio
    async def test_parallel_shard_retrieval(self, rag_service):
        """测试并行分片检索"""
        # 先添加一些测试数据
        test_categories = ["中药", "针灸", "推拿", "食疗", "气功"]
        documents = []
        
        for category in test_categories:
            for i in range(20):
                doc = Document(
                    content=f"{category}相关内容{i}：详细介绍{category}的原理、方法和注意事项。",
                    metadata={"category": category}
                )
                documents.append(doc)
        
        await rag_service.add_documents_batch(documents)
        
        # 执行检索
        query = "中医治疗方法有哪些？"
        result = await rag_service.retrieve(
            query=query,
            top_k=10,
            metadata_filter={"category": {"$in": ["中药", "针灸", "推拿"]}}
        )
        
        assert len(result.documents) > 0
        assert result.latency_ms > 0
        
        # 验证检索结果来自多个分片
        categories = set(doc.metadata.get("category") for doc in result.documents)
        assert len(categories) >= 2
        
        print(f"检索到{len(result.documents)}个文档，来自{len(categories)}个类别")
    
    @pytest.mark.asyncio
    async def test_batch_inference(self, rag_service):
        """测试批量推理功能"""
        # 准备多个查询
        queries = [
            "什么是阴阳平衡？",
            "如何进行经络调理？",
            "中医食疗的原则是什么？",
            "什么是五行学说？",
            "如何进行体质辨识？"
        ]
        
        # 并发执行查询
        start_time = time.time()
        tasks = [rag_service.query(q) for q in queries]
        results = await asyncio.gather(*tasks)
        batch_time = time.time() - start_time
        
        # 验证结果
        assert len(results) == len(queries)
        for result in results:
            assert result.answer
            assert result.total_latency_ms > 0
        
        # 检查批处理统计
        stats = await rag_service.get_service_stats()
        assert stats['batch_processed'] > 0
        
        print(f"批量处理{len(queries)}个查询，总耗时: {batch_time:.2f}秒")
        print(f"平均每个查询: {batch_time/len(queries):.2f}秒")
    
    @pytest.mark.asyncio
    async def test_index_optimization(self, rag_service):
        """测试索引优化功能"""
        # 执行一些查询以收集使用模式
        test_queries = [
            "短查询",
            "这是一个中等长度的查询，包含更多的上下文信息",
            "这是一个非常长的查询，包含了大量的详细信息和背景说明，用于测试不同查询长度对索引选择的影响"
        ]
        
        for query in test_queries * 10:
            await rag_service.retrieve(query, top_k=5)
        
        # 执行索引优化
        await rag_service.optimize_indices()
        
        # 检查索引使用统计
        stats = await rag_service.get_service_stats()
        print("索引使用统计:")
        # 注意：实际统计可能需要从内部stats获取
    
    @pytest.mark.asyncio
    async def test_streaming_query(self, rag_service):
        """测试流式查询功能"""
        query = "请详细介绍中医的整体观念"
        
        fragments = []
        references = None
        
        async for fragment, is_final, refs in rag_service.stream_query(query):
            fragments.append(fragment)
            if is_final:
                references = refs
        
        # 验证流式输出
        assert len(fragments) > 1  # 应该有多个片段
        assert references is not None
        
        # 完整答案
        full_answer = "".join(fragments)
        assert len(full_answer) > 0
        
        print(f"流式输出{len(fragments)}个片段")
        print(f"完整答案长度: {len(full_answer)}字符")
    
    @pytest.mark.asyncio
    async def test_cache_levels(self, rag_service):
        """测试不同缓存级别"""
        query = "测试缓存级别查询"
        cache_key = rag_service._generate_cache_key("query", query, 5, None, None, None, None)
        
        # 测试数据
        test_data = {"answer": "测试答案", "references": []}
        
        # 设置到不同级别的缓存
        await rag_service._set_to_multi_level_cache(cache_key, test_data)
        
        # 清除L1缓存，测试L2
        rag_service.cache_levels[CacheLevel.L1_MEMORY].clear()
        result = await rag_service._get_from_multi_level_cache(cache_key)
        assert result == test_data
        
        # 清除L1和L2，测试L3
        rag_service.cache_levels[CacheLevel.L1_MEMORY].clear()
        if rag_service.cache_levels[CacheLevel.L2_REDIS]:
            await rag_service.cache_levels[CacheLevel.L2_REDIS].delete("query", cache_key)
        
        result = await rag_service._get_from_multi_level_cache(cache_key)
        assert result == test_data
        
        print("多级缓存测试通过")
    
    @pytest.mark.asyncio
    async def test_query_plan_generation(self, rag_service):
        """测试查询计划生成"""
        # 简单查询
        simple_query = "中医"
        plan1 = await rag_service._generate_query_plan(simple_query, None, None)
        
        assert plan1.query_id
        assert plan1.index_type == IndexType.FLAT  # 短查询应该使用FLAT索引
        assert len(plan1.shards) >= 1
        
        # 复杂查询with元数据过滤
        complex_query = "详细介绍中医辨证论治的理论基础和实践方法"
        metadata_filter = {"category": "理论"}
        plan2 = await rag_service._generate_query_plan(complex_query, None, metadata_filter)
        
        assert plan2.index_type in [IndexType.HNSW, IndexType.IVF_PQ]
        assert len(plan2.shards) > 1  # 有元数据过滤时应该查询多个分片
        
        print(f"简单查询计划: 索引={plan1.index_type.value}, 分片数={len(plan1.shards)}")
        print(f"复杂查询计划: 索引={plan2.index_type.value}, 分片数={len(plan2.shards)}")

# 性能测试
class TestPerformance:
    """性能测试类"""
    
    @pytest.mark.asyncio
    async def test_throughput(self, rag_service):
        """测试吞吐量"""
        num_queries = 50
        queries = [f"测试查询{i}：中医养生的第{i}个问题" for i in range(num_queries)]
        
        start_time = time.time()
        
        # 并发执行所有查询
        tasks = [rag_service.query(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # 统计成功和失败
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = num_queries - successful
        
        throughput = successful / total_time
        
        print(f"吞吐量测试:")
        print(f"  总查询数: {num_queries}")
        print(f"  成功: {successful}, 失败: {failed}")
        print(f"  总耗时: {total_time:.2f}秒")
        print(f"  吞吐量: {throughput:.2f} queries/秒")
        
        assert throughput > 5  # 至少5 queries/秒
    
    @pytest.mark.asyncio
    async def test_latency_percentiles(self, rag_service):
        """测试延迟百分位数"""
        num_queries = 100
        latencies = []
        
        for i in range(num_queries):
            query = f"延迟测试查询{i}"
            start = time.time()
            
            try:
                result = await rag_service.query(query)
                latency = (time.time() - start) * 1000  # 转换为毫秒
                latencies.append(latency)
            except Exception as e:
                print(f"查询失败: {e}")
        
        if latencies:
            latencies.sort()
            p50 = latencies[int(len(latencies) * 0.5)]
            p90 = latencies[int(len(latencies) * 0.9)]
            p95 = latencies[int(len(latencies) * 0.95)]
            p99 = latencies[int(len(latencies) * 0.99)]
            
            print(f"延迟统计 (毫秒):")
            print(f"  P50: {p50:.2f}")
            print(f"  P90: {p90:.2f}")
            print(f"  P95: {p95:.2f}")
            print(f"  P99: {p99:.2f}")
            print(f"  平均: {np.mean(latencies):.2f}")
            
            # 性能目标
            assert p95 < 1000  # P95应该小于1秒
    
    @pytest.mark.asyncio
    async def test_cache_effectiveness(self, rag_service):
        """测试缓存效果"""
        # 准备测试查询
        queries = [
            "缓存测试查询A",
            "缓存测试查询B",
            "缓存测试查询C"
        ]
        
        # 第一轮：填充缓存
        for query in queries * 3:
            await rag_service.query(query)
        
        # 重置统计
        initial_stats = await rag_service.get_service_stats()
        initial_hits = rag_service.stats['cache_hits']
        initial_misses = rag_service.stats['cache_misses']
        
        # 第二轮：测试缓存命中
        for query in queries * 10:
            await rag_service.query(query)
        
        # 计算缓存命中率
        final_hits = rag_service.stats['cache_hits'] - initial_hits
        final_misses = rag_service.stats['cache_misses'] - initial_misses
        
        hit_rate = final_hits / (final_hits + final_misses) if (final_hits + final_misses) > 0 else 0
        
        print(f"缓存效果测试:")
        print(f"  命中: {final_hits}")
        print(f"  未命中: {final_misses}")
        print(f"  命中率: {hit_rate:.2%}")
        
        assert hit_rate > 0.8  # 缓存命中率应该大于80%

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"]) 