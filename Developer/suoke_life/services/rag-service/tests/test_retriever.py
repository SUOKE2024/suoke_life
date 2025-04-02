import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.retrievers.keyword_search import KeywordSearcher
from src.retrievers.reranker import Reranker
from src.knowledge_graph.knowledge_graph import KnowledgeGraph
from src.retrievers.retriever import Retriever

# 模拟依赖
@pytest.fixture
def mock_dependencies():
    """模拟依赖"""
    return {
        'retrievers.keyword_search': MagicMock(),
        'retrievers.reranker': MagicMock(),
        'knowledge_graph.knowledge_graph': MagicMock(),
    }

@pytest.fixture
def retriever():
    """创建检索器实例"""
    # 创建模拟对象
    kg = MagicMock(spec=KnowledgeGraph)
    keyword_searcher = MagicMock(spec=KeywordSearcher)
    reranker = MagicMock(spec=Reranker)
    
    # 配置模拟行为
    kg.search_nodes.return_value = [
        MagicMock(id="1", name="气虚", type="Constitution", properties={})
    ]
    kg.get_neighbors.return_value = []
    
    keyword_searcher.search.return_value = [
        {"content": "气虚体质的特征", "metadata": {}, "score": 0.8}
    ]
    
    reranker.rerank = AsyncMock(return_value=[0.9, 0.8, 0.7])
    
    return Retriever(
        knowledge_graph=kg,
        keyword_searcher=keyword_searcher,
        reranker=reranker,
        top_k=5
    )

def test_init(retriever):
    """测试初始化"""
    assert retriever is not None
    assert retriever.knowledge_graph is not None
    assert retriever.keyword_searcher is not None
    assert retriever.reranker is not None
    assert retriever.top_k == 5

@pytest.mark.asyncio
async def test_keyword_search(retriever):
    """测试关键词搜索"""
    results = await retriever._keyword_search("气虚体质")
    assert len(results) > 0
    assert "content" in results[0]
    
@pytest.mark.asyncio
async def test_kg_search(retriever):
    """测试知识图谱搜索"""
    results = await retriever._kg_search("气虚质")
    assert len(results) > 0
    assert "content" in results[0]
    
@pytest.mark.asyncio
async def test_rerank(retriever):
    """测试重排序"""
    results = [
        {"content": "文档1", "score": 0.5},
        {"content": "文档2", "score": 0.6},
        {"content": "文档3", "score": 0.7}
    ]
    reranked = await retriever._rerank("气虚体质有什么表现", results)
    assert len(reranked) == 3
    # 验证分数已更新
    assert reranked[0]["score"] > reranked[1]["score"]
    
@pytest.mark.asyncio
async def test_retrieve(retriever):
    """测试检索"""
    results = await retriever.retrieve("气虚体质的表现和调理方法")
    assert len(results) > 0
    assert "content" in results[0]
    assert "score" in results[0]
    
def test_close(retriever):
    """测试关闭资源"""
    retriever.close()
    retriever.knowledge_graph.close.assert_called_once() 