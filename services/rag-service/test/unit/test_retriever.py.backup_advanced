from typing import Dict, List, Any, Optional, Union

"""
test_retriever - 索克生活项目模块
"""

from services.rag_service.internal.model.document import Document
from services.rag_service.internal.retriever.hybrid_retriever import HybridRetriever
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import unittest

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
混合检索器单元测试
"""



class TestHybridRetriever(unittest.TestCase):
    """混合检索器单元测试类"""

    def setUp(self) - > None:
        """设置测试环境"""
        self.mock_vector_db = AsyncMock()
        self.mock_embedding_service = AsyncMock()
        self.mock_cache_service = AsyncMock()

        # 模拟嵌入向量
        self.mock_embedding = [0.1] * 768
        self.mock_embedding_service.generate_embeddings.return_value = self.mock_embedding

        # 配置参数
        self.config = {
            "retriever": {
                "vector_search_weight": 0.7,
                "keyword_search_weight": 0.3,
                "top_k": 5,
                "min_score": 0.6,
                "hybrid_strategy": "weighted_sum"
            }
        }

        # 创建混合检索器实例
        self.retriever = HybridRetriever(
            vector_db = self.mock_vector_db,
            embedding_service = self.mock_embedding_service,
            cache_service = self.mock_cache_service,
            config = self.config
        )

        # 模拟文档数据
        self.mock_documents = [
            Document(
                id = f"doc{i}",
                content = f"这是测试文档{i}的内容",
                metadata = {"source": "测试", "category": "单元测试"},
                score = 0.9 - i * 0.1
            )
            for i in range(5)
        ]

        # 设置向量搜索的模拟返回
        self.mock_vector_db.search.return_value = self.mock_documents

    @pytest.mark.asyncio
    async def test_retrieve_with_cache_hit(self) - > None:
        """测试缓存命中情况下的检索"""
        # 设置缓存命中
        self.mock_cache_service.get.return_value = self.mock_documents

        # 执行检索
        query = "这是一个测试查询"
        result = await self.retriever.retrieve(query)

        # 验证结果
        self.assertEqual(len(result), len(self.mock_documents))
        self.assertEqual(result[0].id, "doc0")

        # 验证缓存调用
        self.mock_cache_service.get.assert_called_once()
        self.mock_vector_db.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_retrieve_with_cache_miss(self) - > None:
        """测试缓存未命中情况下的检索"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行检索
        query = "这是一个测试查询"
        result = await self.retriever.retrieve(query)

        # 验证结果
        self.assertEqual(len(result), len(self.mock_documents))

        # 验证调用
        self.mock_cache_service.get.assert_called_once()
        self.mock_embedding_service.generate_embeddings.assert_called_once()
        self.mock_vector_db.search.assert_called_once()
        self.mock_cache_service.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_with_metadata_filter(self) - > None:
        """测试带元数据过滤的检索"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行检索，带元数据过滤
        query = "这是一个测试查询"
        metadata_filter = {"category": "单元测试"}
        result = await self.retriever.retrieve(query, metadata_filter = metadata_filter)

        # 验证向量数据库调用参数
        self.mock_vector_db.search.assert_called_once()
        _, kwargs = self.mock_vector_db.search.call_args
        self.assertEqual(kwargs.get("metadata_filter"), metadata_filter)

    @pytest.mark.asyncio
    async def test_retrieve_with_custom_topk(self) - > None:
        """测试自定义top_k参数的检索"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行检索，自定义top_k
        query = "这是一个测试查询"
        custom_top_k = 3
        result = await self.retriever.retrieve(query, top_k = custom_top_k)

        # 验证向量数据库调用参数
        self.mock_vector_db.search.assert_called_once()
        _, kwargs = self.mock_vector_db.search.call_args
        self.assertEqual(kwargs.get("top_k"), custom_top_k)

    @pytest.mark.asyncio
    async def test_retrieve_with_collection_names(self) - > None:
        """测试指定集合名称的检索"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 执行检索，指定集合名称
        query = "这是一个测试查询"
        collection_names = ["中医基础理论", "方剂学"]
        result = await self.retriever.retrieve(query, collection_names = collection_names)

        # 验证向量数据库调用参数
        self.mock_vector_db.search.assert_called_once()
        _, kwargs = self.mock_vector_db.search.call_args
        self.assertEqual(kwargs.get("collection_names"), collection_names)

    @pytest.mark.asyncio
    async def test_retrieve_with_score_threshold(self) - > None:
        """测试结果分数阈值过滤"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 准备不同分数的文档
        varied_score_docs = [
            Document(
                id = f"doc{i}",
                content = f"这是测试文档{i}的内容",
                metadata = {"source": "测试"},
                score = 0.5 + i * 0.1  # 0.5, 0.6, 0.7, 0.8, 0.9
            )
            for i in range(5)
        ]
        self.mock_vector_db.search.return_value = varied_score_docs

        # 执行检索，设置分数阈值
        query = "这是一个测试查询"
        threshold = 0.7
        result = await self.retriever.retrieve(query, score_threshold = threshold)

        # 验证结果只包含满足阈值的文档
        self.assertEqual(len(result), 3)  # 只有3个文档分数> = 0.7
        self.assertTrue(all(doc.score > = threshold for doc in result))

    @pytest.mark.asyncio
    async def test_hybrid_retrieval_strategy(self) - > None:
        """测试混合检索策略"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 设置不同的混合策略
        self.retriever.config["retriever"]["hybrid_strategy"] = "reciprocal_rank_fusion"

        # 执行检索
        query = "这是一个测试查询"
        result = await self.retriever.retrieve(query)

        # 验证结果
        self.assertEqual(len(result), len(self.mock_documents))

    @pytest.mark.asyncio
    async def test_error_handling(self) - > None:
        """测试错误处理"""
        # 设置缓存未命中
        self.mock_cache_service.get.return_value = None

        # 设置向量数据库抛出异常
        self.mock_vector_db.search.side_effect = Exception("模拟数据库错误")

        # 执行检索，预期会返回空结果而不是抛出异常
        query = "这是一个测试查询"
        result = await self.retriever.retrieve(query)

        # 验证结果为空列表
        self.assertEqual(result, [])

    @pytest.mark.asyncio
    async def test_close_method(self) - > None:
        """测试关闭方法"""
        await self.retriever.close()
        # 验证依赖组件的关闭方法被调用
        self.mock_vector_db.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()