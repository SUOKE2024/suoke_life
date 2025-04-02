#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web搜索API路由测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, Response

from src.api.routes.web_search import web_search_bp
from src.web_search import SearchProvider, ContentProcessor, KnowledgeIntegration

# 创建测试Flask应用
@pytest.fixture
def app():
    """创建测试Flask应用"""
    app = Flask(__name__)
    app.register_blueprint(web_search_bp)
    
    # 配置测试配置
    app.config['WEB_SEARCH_CONFIG'] = {
        "api_keys": {
            "brave": "test_key"
        },
        "search": {
            "default_engine": "brave",
            "max_results": 5
        }
    }
    
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

class TestWebSearchAPI:
    """Web搜索API测试类"""
    
    @patch("src.web_search.SearchProvider.search")
    def test_search_endpoint(self, mock_search, client):
        """测试搜索端点"""
        # 模拟搜索结果
        mock_search.return_value = [
            {"title": "测试结果1", "link": "https://example.com/1", "snippet": "摘要1"},
            {"title": "测试结果2", "link": "https://example.com/2", "snippet": "摘要2"}
        ]
        
        # 发送POST请求
        response = client.post(
            '/api/web-search/search',
            json={"query": "测试查询", "engine": "brave", "max_results": 2}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["query"] == "测试查询"
        assert data["engine"] == "brave"
        assert len(data["web_results"]) == 2
        assert data["web_results"][0]["title"] == "测试结果1"
        
        # 验证函数调用
        mock_search.assert_called_once_with("测试查询", "brave", 2)
    
    def test_search_empty_query(self, client):
        """测试空查询"""
        response = client.post(
            '/api/web-search/search',
            json={"query": "", "engine": "brave"}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    
    @patch("src.web_search.ContentProcessor.filter_results")
    @patch("src.web_search.SearchProvider.search")
    def test_search_with_filtering(self, mock_search, mock_filter, client):
        """测试带过滤的搜索"""
        # 模拟搜索和过滤结果
        mock_search.return_value = [{"title": "原始结果1"}, {"title": "原始结果2"}]
        mock_filter.return_value = [{"title": "过滤后结果"}]
        
        # 发送请求
        response = client.post(
            '/api/web-search/search',
            json={"query": "测试查询", "include_knowledge": False}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["web_results"]) == 1
        assert data["web_results"][0]["title"] == "过滤后结果"
        
        # 验证调用顺序
        mock_search.assert_called_once()
        mock_filter.assert_called_once_with([{"title": "原始结果1"}, {"title": "原始结果2"}])
    
    @patch("src.web_search.KnowledgeIntegration.semantic_search")
    def test_knowledge_endpoint(self, mock_semantic_search, client):
        """测试知识库查询端点"""
        # 模拟语义搜索结果
        mock_semantic_search.return_value = [
            {"title": "知识结果1", "content": "内容1"},
            {"title": "知识结果2", "content": "内容2"}
        ]
        
        # 发送POST请求
        response = client.post(
            '/api/web-search/knowledge',
            json={"query": "中医养生", "limit": 2}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["query"] == "中医养生"
        assert len(data["results"]) == 2
        assert data["results"][0]["title"] == "知识结果1"
        
        # 验证函数调用
        mock_semantic_search.assert_called_once_with("中医养生", 2)
    
    @patch("src.web_search.KnowledgeIntegration.query_knowledge_graph")
    def test_graph_endpoint(self, mock_query_graph, client):
        """测试知识图谱查询端点"""
        # 模拟知识图谱结果
        mock_query_graph.return_value = {
            "nodes": [{"id": "太极拳"}],
            "edges": [{"source": "太极拳", "target": "养生", "type": "helps_with"}]
        }
        
        # 发送POST请求
        response = client.post(
            '/api/web-search/graph',
            json={"entity": "太极拳", "relation_types": ["helps_with"]}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["entity"] == "太极拳"
        assert "graph" in data
        assert len(data["graph"]["nodes"]) == 1
        assert len(data["graph"]["edges"]) == 1
        
        # 验证函数调用
        mock_query_graph.assert_called_once_with("太极拳", ["helps_with"])
    
    @patch("src.web_search.ContentProcessor.generate_insights")
    @patch("src.web_search.ContentProcessor.combine_results")
    @patch("src.web_search.KnowledgeIntegration.enrich_search_results")
    @patch("src.web_search.ContentProcessor.filter_results")
    @patch("src.web_search.SearchProvider.search")
    def test_integrated_search_endpoint(self, mock_search, mock_filter, mock_enrich, 
                                     mock_combine, mock_insights, client):
        """测试集成搜索端点"""
        # 模拟各函数返回值
        mock_search.return_value = [{"title": "Web结果"}]
        mock_filter.return_value = [{"title": "过滤后Web结果"}]
        mock_enrich.return_value = {
            "web_results": [{"title": "过滤后Web结果"}],
            "knowledge_results": [{"title": "知识库结果"}],
            "graph_data": {"nodes": [], "edges": []}
        }
        mock_combine.return_value = [{"title": "知识库结果"}, {"title": "过滤后Web结果"}]
        mock_insights.return_value = {"top_topics": ["中医", "养生"]}
        
        # 发送POST请求
        response = client.post(
            '/api/web-search/integrated-search',
            json={"query": "中医养生", "include_insights": True}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["query"] == "中医养生"
        assert "combined_results" in data
        assert "web_results" in data
        assert "knowledge_results" in data
        assert "graph_data" in data
        assert "insights" in data
        assert data["insights"]["top_topics"] == ["中医", "养生"]
        
        # 验证调用顺序
        mock_search.assert_called_once()
        mock_filter.assert_called_once()
        mock_enrich.assert_called_once()
        mock_combine.assert_called_once()
        mock_insights.assert_called_once() 