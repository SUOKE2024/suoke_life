"""
test_rag_service - 索克生活项目模块
"""

from internal.model.document import Document, DocumentReference, RetrieveResult, GenerateResult, QueryResult
from internal.service.rag_service import RagService
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import os
import pytest
import sys
import unittest

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG 服务单元测试
"""


# 将项目根目录添加到路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.mark.asyncio
class TestRagService:
    """测试 RAG 服务"""

    @pytest.fixture
    async def rag_service_with_mocks(self):
        """创建带有模拟依赖的 RAG 服务"""
        # 创建配置
        config = {
            'service': {
                'name': 'rag-service',
                'version': '0.1.0',
            },
            'vector_database': {
                'type': 'milvus',
                'host': 'localhost',
                'port': 19530,
                'collection_name': 'test_collection',
                'dimension': 768,
            },
            'embeddings': {
                'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',
                'device': 'cpu',
            },
            'generator': {
                'model_type': 'openai',
                'openai': {
                    'model_name': 'gpt-3.5-turbo',
                    'temperature': 0.7,
                },
            },
            'retriever': {
                'top_k': 3,
                'score_threshold': 0.7,
                'hybrid_search': {
                    'enabled': True,
                    'keyword_weight': 0.3,
                    'vector_weight': 0.7,
                },
            },
            'cache': {
                'enabled': True,
                'query': {'enabled': True, 'type': 'local'},
                'embedding': {'enabled': True, 'type': 'local'},
                'retrieval': {'enabled': True, 'type': 'local'},
                'generation': {'enabled': True, 'type': 'local'},
            }
        }
        
        # 创建 RAG 服务
        service = RagService(config)
        
        # 模拟依赖组件
        service.milvus_repository = AsyncMock()
        service.embedding_service = AsyncMock()
        service.retriever = AsyncMock()
        service.generator = AsyncMock()
        service.cache_service = AsyncMock()
        
        # 设置为初始化状态
        service.is_initialized = True
        
        # 返回配置好的服务
        return service
    
    async def test_retrieve(self, rag_service_with_mocks):
        """测试检索功能"""
        # 准备
        service = rag_service_with_mocks
        query = "痰湿体质如何调理"
        
        # 模拟缓存未命中
        service.cache_service.get.return_value = None
        
        # 模拟检索结果
        mock_documents = [
            Document(
                id="doc1",
                content="痰湿体质的人容易感到困倦，身体沉重，胃口不佳。",
                metadata={"type": "体质", "category": "痰湿体质"},
                score=0.95,
                source="中医知识库"
            ),
            Document(
                id="doc2",
                content="痰湿体质的调理方法包括饮食清淡，避免高油高糖食物，多运动出汗。",
                metadata={"type": "调理", "category": "痰湿体质"},
                score=0.85,
                source="中医知识库"
            )
        ]
        mock_result = RetrieveResult(
            documents=mock_documents,
            latency_ms=100.0
        )
        service.retriever.retrieve.return_value = mock_result
        
        # 执行
        result = await service.retrieve(
            query=query,
            top_k=3,
            collection_names=["health"],
            metadata_filter={"category": "痰湿体质"},
            score_threshold=0.7,
            rerank=True
        )
        
        # 验证
        assert result == mock_result
        service.cache_service.get.assert_called_once()
        service.retriever.retrieve.assert_called_once_with(
            query=query,
            top_k=3,
            collection_names=["health"],
            metadata_filter={"category": "痰湿体质"},
            score_threshold=0.7,
            rerank=True
        )
        service.cache_service.set.assert_called_once()
    
    async def test_generate(self, rag_service_with_mocks):
        """测试生成功能"""
        # 准备
        service = rag_service_with_mocks
        query = "痰湿体质如何调理"
        context_documents = [
            Document(
                id="doc1",
                content="痰湿体质的人容易感到困倦，身体沉重，胃口不佳。",
                metadata={"type": "体质", "category": "痰湿体质"},
                score=0.95,
                source="中医知识库"
            ),
            Document(
                id="doc2",
                content="痰湿体质的调理方法包括饮食清淡，避免高油高糖食物，多运动出汗。",
                metadata={"type": "调理", "category": "痰湿体质"},
                score=0.85,
                source="中医知识库"
            )
        ]
        
        # 模拟缓存未命中
        service.cache_service.get.return_value = None
        
        # 模拟生成结果
        mock_references = [
            DocumentReference(
                id="doc2",
                title="痰湿体质调理方法",
                source="中医知识库",
                snippet="痰湿体质的调理方法包括饮食清淡，避免高油高糖食物，多运动出汗。"
            )
        ]
        mock_result = GenerateResult(
            answer="痰湿体质的调理主要是饮食清淡，避免高油高糖食物，同时增加运动促进代谢和排汗。",
            references=mock_references,
            latency_ms=500.0
        )
        service.generator.generate.return_value = mock_result
        
        # 执行
        result = await service.generate(
            query=query,
            context_documents=context_documents,
            system_prompt="作为中医专家，你需要根据提供的知识来回答问题。",
            generation_params={"temperature": 0.5}
        )
        
        # 验证
        assert result == mock_result
        service.cache_service.get.assert_called_once()
        service.generator.generate.assert_called_once_with(
            query=query,
            context_documents=context_documents,
            system_prompt="作为中医专家，你需要根据提供的知识来回答问题。",
            generation_params={"temperature": 0.5},
            user_id=None
        )
        service.cache_service.set.assert_called_once()
    
    async     @cache(timeout=300)  # 5分钟缓存
def test_query(self, rag_service_with_mocks):
        """测试查询功能(检索+生成)"""
        # 准备
        service = rag_service_with_mocks
        query = "痰湿体质如何调理"
        
        # 模拟缓存未命中
        service.cache_service.get.return_value = None
        
        # 模拟检索结果
        mock_documents = [
            Document(
                id="doc1",
                content="痰湿体质的人容易感到困倦，身体沉重，胃口不佳。",
                metadata={"type": "体质", "category": "痰湿体质"},
                score=0.95,
                source="中医知识库"
            ),
            Document(
                id="doc2",
                content="痰湿体质的调理方法包括饮食清淡，避免高油高糖食物，多运动出汗。",
                metadata={"type": "调理", "category": "痰湿体质"},
                score=0.85,
                source="中医知识库"
            )
        ]
        mock_retrieve_result = RetrieveResult(
            documents=mock_documents,
            latency_ms=100.0
        )
        service.retrieve.return_value = mock_retrieve_result
        
        # 模拟生成结果
        mock_references = [
            DocumentReference(
                id="doc2",
                title="痰湿体质调理方法",
                source="中医知识库",
                snippet="痰湿体质的调理方法包括饮食清淡，避免高油高糖食物，多运动出汗。"
            )
        ]
        mock_generate_result = GenerateResult(
            answer="痰湿体质的调理主要是饮食清淡，避免高油高糖食物，同时增加运动促进代谢和排汗。",
            references=mock_references,
            latency_ms=500.0
        )
        service.generate.return_value = mock_generate_result
        
        # 执行
        result = await service.query(
            query=query,
            top_k=3,
            system_prompt="作为中医专家，你需要根据提供的知识来回答问题。",
            collection_names=["health"],
            generation_params={"temperature": 0.5},
            metadata_filter={"category": "痰湿体质"}
        )
        
        # 验证
        assert isinstance(result, QueryResult)
        assert result.answer == mock_generate_result.answer
        assert result.references == mock_generate_result.references
        assert result.retrieval_latency_ms > 0
        assert result.generation_latency_ms > 0
        assert result.total_latency_ms > 0
        
        service.cache_service.get.assert_called_once()
        service.retrieve.assert_called_once()
        service.generate.assert_called_once()
        service.cache_service.set.assert_called_once()
    
    async def test_add_document(self, rag_service_with_mocks):
        """测试添加文档功能"""
        # 准备
        service = rag_service_with_mocks
        document = Document(
            id="",  # 空ID，应该自动生成
            content="痰湿体质的调理方法包括饮食清淡，避免高油高糖食物，多运动出汗。",
            metadata={"type": "调理", "category": "痰湿体质"},
            source="中医知识库"
        )
        
        # 模拟嵌入向量生成
        service.embedding_service.embed_documents.return_value = [
            Document(
                id="",
                content=document.content,
                metadata=document.metadata,
                source=document.source,
                vector=[0.1] * 768  # 模拟向量
            )
        ]
        
        # 模拟文档添加成功
        service.milvus_repository.add_documents.return_value = True
        
        # 执行
        result_id = await service.add_document(
            document=document,
            collection_name="health",
            reindex=True
        )
        
        # 验证
        assert result_id  # 应返回有效的ID
        service.embedding_service.embed_documents.assert_called_once()
        service.milvus_repository.add_documents.assert_called_once()
    
    async def test_delete_document(self, rag_service_with_mocks):
        """测试删除文档功能"""
        # 准备
        service = rag_service_with_mocks
        document_id = "doc123"
        collection_name = "health"
        
        # 模拟删除成功
        service.milvus_repository.delete_documents.return_value = True
        
        # 执行
        result = await service.delete_document(
            document_id=document_id,
            collection_name=collection_name
        )
        
        # 验证
        assert result is True
        service.milvus_repository.delete_documents.assert_called_once_with([document_id])
    
    async def test_health_check(self, rag_service_with_mocks):
        """测试健康检查功能"""
        # 准备
        service = rag_service_with_mocks
        
        # 设置组件状态
        service.milvus_repository.is_connected = True
        service.embedding_service.is_initialized = True
        service.embedding_service.model_name = "test-model"
        service.retriever.is_initialized = True
        service.generator.is_initialized = True
        
        # 执行
        status, details = await service.health_check()
        
        # 验证
        assert status == "SERVING"
        assert "version" in details
        assert "name" in details
        assert details["milvus_connected"] == "true"
        assert details["embedding_model"] == "test-model"
        assert details["generator_type"] == "openai"
    
    async def test_health_check_not_initialized(self, rag_service_with_mocks):
        """测试未初始化时的健康检查"""
        # 准备
        service = rag_service_with_mocks
        service.is_initialized = False
        
        # 执行
        status, details = await service.health_check()
        
        # 验证
        assert status == "NOT_SERVING"
        assert "reason" in details
        assert details["reason"] == "Service not initialized"
    
    async def test_close(self, rag_service_with_mocks):
        """测试关闭服务功能"""
        # 准备
        service = rag_service_with_mocks
        
        # 执行
        await service.close()
        
        # 验证
        service.generator.close.assert_called_once()
        service.retriever.close.assert_called_once()
        service.embedding_service.close.assert_called_once()
        service.milvus_repository.close.assert_called_once()
        service.cache_service.close.assert_called_once()
        assert service.is_initialized is False

if __name__ == '__main__':
    asyncio.run(unittest.main()) 