#!/usr/bin/env python

"""
知识服务单元测试
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# 添加项目根路径到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from internal.knowledge.knowledge_graph import KnowledgeGraph
from internal.knowledge.knowledge_service import KnowledgeService


class TestKnowledgeService(unittest.TestCase):
    """知识服务单元测试类"""

    def setUp(self):
        """测试前初始化"""
        # 模拟知识图谱依赖
        self.mock_knowledge_graph = MagicMock(spec=KnowledgeGraph)

        # 模拟配置
        self.mock_config = {
            'knowledge': {
                'max_search_results': 10,
                'search_similarity_threshold': 0.7,
                'embedding_model': 'text-embedding-3-large'
            }
        }

        # 模拟存储库
        self.mock_repository = MagicMock()
        self.mock_repository.get_article_by_id = AsyncMock()
        self.mock_repository.get_articles = AsyncMock()
        self.mock_repository.create_article = AsyncMock()
        self.mock_repository.update_article = AsyncMock()

        # 初始化知识服务
        with patch('internal.knowledge.knowledge_service.Config', return_value=self.mock_config):
            self.knowledge_service = KnowledgeService()
            self.knowledge_service.knowledge_graph = self.mock_knowledge_graph
            self.knowledge_service.repository = self.mock_repository

    @pytest.mark.asyncio
    async def test_get_article_by_id(self):
        """测试通过ID获取文章"""
        # 设置模拟返回值
        mock_article = {
            'id': '123',
            'title': '中医基础理论',
            'content': '中医学是中国传统医学...',
            'category': '中医基础',
            'tags': ['基础理论', '中医']
        }
        self.mock_repository.get_article_by_id.return_value = mock_article

        # 调用被测试的方法
        result = await self.knowledge_service.get_article_by_id('123')

        # 断言
        assert result == mock_article
        self.mock_repository.get_article_by_id.assert_called_once_with('123')

    @pytest.mark.asyncio
    async def test_search_knowledge(self):
        """测试知识检索功能"""
        # 设置模拟返回值
        mock_embeddings = [0.1, 0.2, 0.3]
        mock_results = [
            {
                'id': '123',
                'title': '中医基础理论',
                'content': '中医学是中国传统医学...',
                'category': '中医基础',
                'similarity': 0.85
            },
            {
                'id': '456',
                'title': '阴阳五行学说',
                'content': '阴阳五行是中医基础理论...',
                'category': '中医基础',
                'similarity': 0.75
            }
        ]

        # 模拟嵌入和搜索
        self.mock_knowledge_graph.generate_embeddings.return_value = mock_embeddings
        self.mock_knowledge_graph.search_similar_content.return_value = mock_results

        # 调用被测试的方法
        results = await self.knowledge_service.search_knowledge('中医基础理论', limit=5)

        # 断言
        assert len(results) == 2
        assert results[0]['id'] == '123'
        assert results[0]['similarity'] == 0.85
        self.mock_knowledge_graph.generate_embeddings.assert_called_once_with('中医基础理论')
        self.mock_knowledge_graph.search_similar_content.assert_called_once_with(
            mock_embeddings,
            limit=5,
            threshold=0.7
        )

    @pytest.mark.asyncio
    async def test_create_article(self):
        """测试创建知识文章"""
        # 设置模拟数据
        article_data = {
            'title': '中药学概论',
            'content': '中药学是研究中药的基本理论...',
            'category': '中药学',
            'tags': ['中药', '概论', '基础知识']
        }

        # 设置模拟返回值
        mock_created_article = {
            'id': '789',
            **article_data,
            'created_at': '2023-11-12T10:00:00Z',
            'updated_at': None,
            'rating': 0,
            'rating_count': 0,
            'view_count': 0
        }
        self.mock_repository.create_article.return_value = mock_created_article

        # 模拟嵌入生成
        self.mock_knowledge_graph.generate_embeddings.return_value = [0.1, 0.2, 0.3]
        self.mock_knowledge_graph.store_embeddings.return_value = True

        # 调用被测试的方法
        result = await self.knowledge_service.create_article(article_data)

        # 断言
        assert result['id'] == '789'
        assert result['title'] == '中药学概论'
        self.mock_repository.create_article.assert_called_once()
        self.mock_knowledge_graph.generate_embeddings.assert_called_once()
        self.mock_knowledge_graph.store_embeddings.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_related_topics(self):
        """测试获取相关主题"""
        # 设置模拟返回值
        self.mock_knowledge_graph.get_related_topics.return_value = [
            '中医基础理论',
            '阴阳五行',
            '经络学说'
        ]

        # 调用被测试的方法
        topics = await self.knowledge_service.get_related_topics('中医基础')

        # 断言
        assert len(topics) == 3
        assert '阴阳五行' in topics
        self.mock_knowledge_graph.get_related_topics.assert_called_once_with('中医基础')

    @pytest.mark.asyncio
    async def test_rate_article(self):
        """测试文章评分功能"""
        # 设置模拟数据
        article_id = '123'
        rating = 4

        # 设置模拟返回值
        mock_article = {
            'id': '123',
            'title': '中医基础理论',
            'content': '中医学是中国传统医学...',
            'category': '中医基础',
            'tags': ['基础理论', '中医'],
            'rating': 3.5,
            'rating_count': 2
        }

        mock_updated_article = {
            **mock_article,
            'rating': 3.67,  # (3.5*2 + 4)/3 = 3.67
            'rating_count': 3
        }

        self.mock_repository.get_article_by_id.return_value = mock_article
        self.mock_repository.update_article.return_value = mock_updated_article

        # 调用被测试的方法
        result = await self.knowledge_service.rate_article(article_id, rating)

        # 断言
        assert result['rating'] == 3.67
        assert result['rating_count'] == 3
        self.mock_repository.get_article_by_id.assert_called_once_with(article_id)
        self.mock_repository.update_article.assert_called_once()


if __name__ == '__main__':
    unittest.main()
