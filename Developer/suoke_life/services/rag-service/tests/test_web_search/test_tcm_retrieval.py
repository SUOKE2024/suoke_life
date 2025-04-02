#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医养生特色检索功能测试
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.api.routes.specialized_retrievers import retrieve_tcm
from src.api.models.retrieval import TCMQuery

class TestTCMRetrieval:
    """测试中医养生特色检索功能"""
    
    @pytest.fixture
    def mock_kg_client(self):
        """模拟知识图谱客户端"""
        mock_client = MagicMock()
        
        # 模拟查询方法
        mock_client.query.return_value = [
            {
                "id": "tcm-001",
                "title": "春季养生指南",
                "content": "春季养肝为主，饮食宜温，忌食生冷。",
                "constitution_type": "平和质",
                "season": "春季",
                "source_type": "养生指南",
                "dietary_recommendations": ["春笋", "菠菜", "枸杞"]
            },
            {
                "id": "tcm-002",
                "title": "阴虚体质调理",
                "content": "阴虚体质宜食用滋阴润燥食物，如百合、银耳等。",
                "constitution_type": "阴虚质",
                "source_type": "体质养生",
                "dietary_recommendations": ["百合", "银耳", "梨"]
            }
        ]
        
        return mock_client
    
    @pytest.fixture
    def mock_vector_client(self):
        """模拟向量数据库客户端"""
        mock_client = MagicMock()
        
        # 模拟相似性搜索方法
        mock_client.similarity_search.return_value = [
            {
                "id": "tcm-003",
                "title": "黄帝内经中的养生智慧",
                "content": "《黄帝内经》认为养生应顺应四时变化，调和阴阳...",
                "source_type": "经典文献",
                "classic_reference": "黄帝内经",
                "similarity_score": 0.92
            },
            {
                "id": "tcm-004",
                "title": "冬季温补养生",
                "content": "冬季宜温补阳气，食物宜温热，避免生冷...",
                "season": "冬季",
                "source_type": "养生指南",
                "similarity_score": 0.85
            }
        ]
        
        return mock_client
    
    async def test_retrieve_tcm_basic(self, mock_kg_client, mock_vector_client):
        """测试基本的中医养生检索功能"""
        # 创建测试请求
        query = TCMQuery(
            query="春季养生",
            limit=10
        )
        
        # 调用检索函数
        response = await retrieve_tcm(query, mock_kg_client, mock_vector_client)
        
        # 验证响应
        assert response["domain"] == "tcm"
        assert response["query"] == "春季养生"
        assert len(response["results"]) > 0
        
        # 验证调用
        mock_vector_client.similarity_search.assert_called_once()
    
    async def test_retrieve_tcm_with_filters(self, mock_kg_client, mock_vector_client):
        """测试带过滤条件的中医养生检索功能"""
        # 创建测试请求
        query = TCMQuery(
            query="养生方法",
            limit=10,
            constitution_type="阴虚质",
            season="冬季",
            source_type="经典文献"
        )
        
        # 调用检索函数
        response = await retrieve_tcm(query, mock_kg_client, mock_vector_client)
        
        # 验证响应
        assert response["domain"] == "tcm"
        assert response["query"] == "养生方法"
        
        # 验证知识图谱查询和向量数据库都被调用
        mock_kg_client.query.assert_called_once()
        mock_vector_client.similarity_search.assert_called_once()
        
        # 验证过滤条件正确传递
        call_args = mock_vector_client.similarity_search.call_args[1]
        assert "constitution_type" in call_args
        assert call_args["constitution_type"] == "阴虚质"
        assert "season" in call_args
        assert call_args["season"] == "冬季" 