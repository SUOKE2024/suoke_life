#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检索器单元测试
"""

import sys
import os
import pytest
import asyncio
from typing import List, Dict, Any

# 将项目根目录添加到路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.model.document import Document
from internal.retriever.base import BaseRetriever


class MockRetriever(BaseRetriever):
    """测试用检索器模拟实现"""
    
    async def initialize(self):
        """初始化检索器"""
        pass
    
    async def _do_retrieve(
        self,
        query: str,
        top_k: int = 5,
        collection_names = None,
        metadata_filter = None,
        score_threshold: float = 0.0,
        rerank: bool = False
    ) -> List[Document]:
        """
        模拟检索
        """
        documents = [
            Document(
                id="doc1",
                content="痰湿体质的人容易感到困倦，身体沉重，胃口不佳。",
                metadata={"type": "体质", "category": "痰湿体质"},
                score=0.95
            ),
            Document(
                id="doc2",
                content="痰湿体质的调理方法包括饮食清淡，避免高油高糖食物，多运动出汗。",
                metadata={"type": "调理", "category": "痰湿体质"},
                score=0.85
            ),
            Document(
                id="doc3",
                content="痰湿体质可通过服用二陈汤、藿香正气丸等进行调理。",
                metadata={"type": "药物", "category": "痰湿体质"},
                score=0.78
            )
        ]
        
        # 根据top_k控制返回数量
        result = documents[:min(top_k, len(documents))]
        
        # 应用分数阈值过滤
        result = [doc for doc in result if doc.score >= score_threshold]
        
        return result
    
    async def rerank(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """
        模拟重排序
        """
        # 简单地返回输入文档
        return documents[:min(top_k, len(documents))]
    
    async def close(self):
        """关闭检索器及相关连接"""
        pass


@pytest.mark.asyncio
async def test_retrieve():
    """测试检索功能"""
    # 创建检索器
    retriever = MockRetriever()
    await retriever.initialize()
    
    # 测试检索
    result = await retriever.retrieve(
        query="痰湿体质的调理方法",
        top_k=2,
        score_threshold=0.8
    )
    
    # 验证结果
    assert len(result.documents) == 2
    assert result.documents[0].id == "doc1"
    assert result.documents[1].id == "doc2"
    assert result.latency_ms > 0
    
    # 测试分数阈值过滤
    result = await retriever.retrieve(
        query="痰湿体质的调理方法",
        top_k=3,
        score_threshold=0.9
    )
    
    # 应该只返回一个文档(doc1)，因为只有它的分数高于0.9
    assert len(result.documents) == 1
    assert result.documents[0].id == "doc1"
    
    await retriever.close()


if __name__ == "__main__":
    asyncio.run(test_retrieve())