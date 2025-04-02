#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KnowledgeIntegration单元测试
"""

import pytest
from unittest.mock import patch, MagicMock
import requests
import json

from src.web_search.knowledge_integration import KnowledgeIntegration

# 测试数据
TEST_CONFIG = {
    "services": {
        "knowledge_base": {
            "url": "http://knowledge-base-service:8080",
            "api_key": "test_kb_key",
            "timeout": 5
        },
        "knowledge_graph": {
            "url": "http://knowledge-graph-service:8090",
            "api_key": "test_kg_key",
            "timeout": 5
        }
    }
}

class TestKnowledgeIntegration:
    """KnowledgeIntegration测试类"""
    
    @pytest.fixture
    def knowledge_integration(self):
        """创建KnowledgeIntegration实例"""
        return KnowledgeIntegration(TEST_CONFIG)
    
    def test_init(self, knowledge_integration):
        """测试初始化"""
        assert knowledge_integration.knowledge_base_url == "http://knowledge-base-service:8080"
        assert knowledge_integration.knowledge_graph_url == "http://knowledge-graph-service:8090"
        assert knowledge_integration.api_key == "test_kb_key"
        assert knowledge_integration.timeout == 5
    
    @patch("requests.get")
    def test_semantic_search(self, mock_get, knowledge_integration):
        """测试语义搜索"""
        # 模拟知识库API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "太极拳养生法",
                    "content": "太极拳是中国传统的武术和养生方法",
                    "link": "kb://taiji",
                    "relevance_score": 0.92
                },
                {
                    "title": "中医养生原理",
                    "content": "中医养生基于阴阳五行理论",
                    "link": "kb://tcm-principle",
                    "relevance_score": 0.87
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # 执行语义搜索
        results = knowledge_integration.semantic_search("太极拳养生", 2)
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["title"] == "太极拳养生法"
        assert results[0]["content"] == "太极拳是中国传统的武术和养生方法"
        assert results[0]["relevance_score"] == 0.92
        
        # 验证API调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "http://knowledge-base-service:8080/api/search/semantic" in kwargs["url"]
        assert kwargs["timeout"] == 5
        assert kwargs["params"]["q"] == "太极拳养生"
        assert kwargs["params"]["limit"] == 2
        assert kwargs["headers"]["Authorization"] == "Bearer test_kb_key"
    
    @patch("requests.get")
    def test_semantic_search_error(self, mock_get, knowledge_integration):
        """测试语义搜索错误处理"""
        # 模拟请求失败
        mock_get.side_effect = requests.RequestException("连接错误")
        
        # 执行语义搜索
        results = knowledge_integration.semantic_search("太极拳养生", 2)
        
        # 验证结果为空列表
        assert results == []
        
        # 测试API返回非200状态码
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.side_effect = None
        mock_get.return_value = mock_response
        
        results = knowledge_integration.semantic_search("太极拳养生", 2)
        assert results == []
    
    @patch.object(KnowledgeIntegration, "semantic_search")
    def test_get_related_knowledge(self, mock_semantic_search, knowledge_integration):
        """测试获取相关知识"""
        # 模拟语义搜索结果
        mock_semantic_search.return_value = [
            {"title": "相关知识1", "content": "内容1"},
            {"title": "相关知识2", "content": "内容2"}
        ]
        
        # 测试数据
        query = "太极拳养生"
        web_results = [
            {"title": "太极拳简介", "link": "https://example.com/taiji"},
            {"title": "养生方法大全", "link": "https://example.com/yangsheng"}
        ]
        
        # 执行获取相关知识
        results = knowledge_integration.get_related_knowledge(query, web_results, 2)
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["title"] == "相关知识1"
        
        # 验证语义搜索调用
        mock_semantic_search.assert_called_once()
        args, kwargs = mock_semantic_search.call_args
        assert query in args[0]  # 查询应包含原始查询
        assert "太极拳简介" in args[0]  # 查询应包含web结果标题
        assert "养生方法大全" in args[0]  # 查询应包含web结果标题
        assert args[1] == 2  # limit参数
    
    @patch("requests.post")
    def test_query_knowledge_graph(self, mock_post, knowledge_integration):
        """测试查询知识图谱"""
        # 模拟知识图谱API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "nodes": [
                {"id": "太极拳", "type": "exercise", "properties": {"level": "beginner"}},
                {"id": "养生", "type": "concept", "properties": {}}
            ],
            "edges": [
                {"source": "太极拳", "target": "养生", "type": "helps_with", "properties": {"strength": "high"}}
            ]
        }
        mock_post.return_value = mock_response
        
        # 执行知识图谱查询
        result = knowledge_integration.query_knowledge_graph("太极拳", ["helps_with", "part_of"])
        
        # 验证结果
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 2
        assert len(result["edges"]) == 1
        assert result["nodes"][0]["id"] == "太极拳"
        assert result["edges"][0]["type"] == "helps_with"
        
        # 验证API调用
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "http://knowledge-graph-service:8090/api/graph/query" in kwargs["url"]
        assert kwargs["timeout"] == 5
        assert kwargs["headers"]["Authorization"] == "Bearer test_kg_key"
        assert kwargs["json"]["entity"] == "太极拳"
        assert kwargs["json"]["relation_types"] == ["helps_with", "part_of"]
    
    @patch("requests.post")
    def test_query_knowledge_graph_error(self, mock_post, knowledge_integration):
        """测试知识图谱查询错误处理"""
        # 模拟请求失败
        mock_post.side_effect = requests.RequestException("连接错误")
        
        # 执行知识图谱查询
        result = knowledge_integration.query_knowledge_graph("太极拳", ["helps_with"])
        
        # 验证结果为空对象
        assert result == {"nodes": [], "edges": []}
    
    @patch.object(KnowledgeIntegration, "get_related_knowledge")
    @patch.object(KnowledgeIntegration, "query_knowledge_graph")
    def test_enrich_search_results(self, mock_query_graph, mock_get_related, knowledge_integration):
        """测试搜索结果丰富"""
        # 模拟相关知识和知识图谱结果
        mock_get_related.return_value = [
            {"title": "相关知识1", "content": "内容1"},
            {"title": "相关知识2", "content": "内容2"}
        ]
        
        mock_query_graph.return_value = {
            "nodes": [{"id": "太极拳"}],
            "edges": [{"source": "太极拳", "target": "养生", "type": "helps_with"}]
        }
        
        # 测试数据
        query = "太极拳养生"
        web_results = [
            {"title": "太极拳简介", "link": "https://example.com/taiji"},
            {"title": "养生方法大全", "link": "https://example.com/yangsheng"}
        ]
        
        # 执行搜索结果丰富
        enriched = knowledge_integration.enrich_search_results(query, web_results)
        
        # 验证结果
        assert "web_results" in enriched
        assert "knowledge_results" in enriched
        assert "graph_data" in enriched
        assert enriched["web_results"] == web_results
        assert len(enriched["knowledge_results"]) == 2
        assert enriched["knowledge_results"][0]["title"] == "相关知识1"
        assert len(enriched["graph_data"]["nodes"]) == 1
        
        # 验证调用
        mock_get_related.assert_called_once_with(query, web_results)
        mock_query_graph.assert_called_once()
        args, kwargs = mock_query_graph.call_args
        assert args[0] == "太极拳养生"  # 使用最长的实体 