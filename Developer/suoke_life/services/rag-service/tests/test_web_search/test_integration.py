#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web搜索模块集成测试
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
import requests
from flask import Flask

from src.web_search import SearchProvider, ContentProcessor, KnowledgeIntegration
from src.api.routes.web_search import web_search_bp

# 配置测试数据
TEST_CONFIG = {
    "api_keys": {
        "brave": "test_brave_key",
        "google": "test_google_key"
    },
    "search": {
        "default_engine": "brave",
        "max_results": 5,
        "timeout": 10
    },
    "content": {
        "summarization_enabled": True,
        "max_summary_length": 200,
        "translation_enabled": False,
        "filtering_enabled": True,
        "blocked_domains": ["spam.com"]
    },
    "knowledge": {
        "knowledge_base_url": "http://localhost:8001/api",
        "knowledge_graph_url": "http://localhost:8002/api",
        "api_key": "test_kb_key",
        "timeout": 5
    }
}

@pytest.fixture
def app():
    """创建测试Flask应用"""
    app = Flask(__name__)
    app.register_blueprint(web_search_bp)
    app.config['WEB_SEARCH_CONFIG'] = TEST_CONFIG
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def search_provider():
    """创建SearchProvider实例"""
    return SearchProvider(
        default_engine=TEST_CONFIG["search"]["default_engine"],
        max_results=TEST_CONFIG["search"]["max_results"],
        timeout=TEST_CONFIG["search"]["timeout"],
        api_keys=TEST_CONFIG["api_keys"]
    )

@pytest.fixture
def content_processor():
    """创建ContentProcessor实例"""
    config = TEST_CONFIG["content"]
    return ContentProcessor(
        summarization_enabled=config["summarization_enabled"],
        max_summary_length=config["max_summary_length"],
        translation_enabled=config["translation_enabled"],
        target_language="zh",
        filtering_enabled=config["filtering_enabled"],
        blocked_domains=config["blocked_domains"]
    )

@pytest.fixture
def knowledge_integration():
    """创建KnowledgeIntegration实例"""
    config = TEST_CONFIG["knowledge"]
    return KnowledgeIntegration(
        knowledge_base_url=config["knowledge_base_url"],
        knowledge_graph_url=config["knowledge_graph_url"],
        api_key=config["api_key"],
        timeout=config["timeout"]
    )

class TestWebSearchIntegration:
    """Web搜索集成测试类"""
    
    @patch("requests.get")
    def test_web_search_to_content_processing(self, mock_requests, search_provider, content_processor):
        """测试网络搜索到内容处理的集成流程"""
        # 模拟web请求响应
        mock_html_content = """
        <html>
            <head><title>测试页面</title></head>
            <body>
                <div>
                    <h1>中医养生知识</h1>
                    <p>太极拳是一种常见的养生方式，对健康大有裨益。</p>
                </div>
                <script>console.log('this should be ignored');</script>
            </body>
        </html>
        """
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html_content
        mock_response.content = mock_html_content.encode()
        mock_requests.return_value = mock_response
        
        # 模拟搜索结果
        with patch.object(search_provider, 'brave_search') as mock_search:
            mock_search.return_value = [
                {
                    "title": "中医养生方法", 
                    "link": "https://example.com/tcm", 
                    "snippet": "中医养生包括太极拳等多种方式"
                },
                {
                    "title": "屏蔽网站测试", 
                    "link": "https://spam.com/test", 
                    "snippet": "这应该被过滤"
                }
            ]
            
            # 执行搜索
            results = search_provider.search("中医养生", "brave", 5)
            assert len(results) == 2
            
            # 过滤结果
            filtered_results = content_processor.filter_results(results)
            assert len(filtered_results) == 1
            assert "spam.com" not in filtered_results[0]["link"]
            
            # 提取内容
            for result in filtered_results:
                with patch.object(content_processor, '_fetch_page_content') as mock_fetch:
                    mock_fetch.return_value = mock_html_content
                    content = content_processor.extract_content(result["link"])
                    assert "中医养生知识" in content
                    assert "太极拳是一种常见的养生方式" in content
                    assert "this should be ignored" not in content
            
            # 生成摘要
            with patch("src.web_search.ContentProcessor._generate_summary") as mock_summary:
                mock_summary.return_value = "太极拳是中医养生的重要方法"
                summary = content_processor.summarize_text("太极拳是一种常见的养生方式，对健康大有裨益。" * 20)
                assert summary == "太极拳是中医养生的重要方法"
    
    @patch("requests.post")
    def test_knowledge_integration_with_web_search(self, mock_requests, search_provider, knowledge_integration):
        """测试知识库集成与网络搜索的集成流程"""
        # 模拟知识库搜索响应
        mock_kb_response = MagicMock()
        mock_kb_response.status_code = 200
        mock_kb_response.json.return_value = {
            "results": [
                {"title": "太极拳养生", "content": "太极拳可以锻炼身体平衡能力", "relevance": 0.92},
                {"title": "中医经络理论", "content": "经络是中医理论的重要组成部分", "relevance": 0.87}
            ]
        }
        
        # 模拟知识图谱响应
        mock_kg_response = MagicMock()
        mock_kg_response.status_code = 200
        mock_kg_response.json.return_value = {
            "nodes": [{"id": "太极拳", "type": "exercise"}, {"id": "养生", "type": "concept"}],
            "edges": [{"source": "太极拳", "target": "养生", "type": "contributes_to"}]
        }
        
        # 配置mock响应
        mock_requests.side_effect = lambda url, **kwargs: mock_kb_response if "knowledge_base" in url else mock_kg_response
        
        # 模拟网络搜索结果
        with patch.object(search_provider, "search") as mock_search:
            mock_search.return_value = [
                {"title": "太极拳入门", "link": "https://example.com/taichi", "snippet": "太极拳基础动作讲解"}
            ]
            
            # 执行搜索
            web_results = search_provider.search("太极拳养生", "brave", 3)
            
            # 执行知识库搜索
            kb_results = knowledge_integration.semantic_search("太极拳养生", 3)
            assert len(kb_results) == 2
            assert kb_results[0]["title"] == "太极拳养生"
            
            # 查询知识图谱
            graph_data = knowledge_integration.query_knowledge_graph("太极拳")
            assert len(graph_data["nodes"]) == 2
            assert len(graph_data["edges"]) == 1
            
            # 整合结果
            enriched_results = knowledge_integration.enrich_search_results(web_results, "太极拳养生")
            assert "web_results" in enriched_results
            assert "knowledge_results" in enriched_results
            assert "graph_data" in enriched_results
    
    @patch("requests.post")
    @patch("requests.get")
    def test_full_api_integration(self, mock_get, mock_post, client):
        """测试完整API集成流程"""
        # 模拟brave搜索API响应
        brave_response = {
            "web": {
                "results": [
                    {
                        "title": "中医养生知识大全", 
                        "url": "https://example.com/tcm",
                        "description": "包含太极拳、气功等多种养生方法介绍"
                    }
                ]
            }
        }
        
        # 模拟知识库API响应
        kb_response = {
            "results": [
                {"title": "太极拳养生", "content": "太极拳可以锻炼身体平衡能力", "relevance": 0.92}
            ]
        }
        
        # 模拟知识图谱API响应
        kg_response = {
            "nodes": [{"id": "太极拳", "type": "exercise"}],
            "edges": []
        }
        
        # 配置mock响应
        def mock_request_side_effect(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            
            if "brave" in url:
                mock_resp.json.return_value = brave_response
            elif "knowledge_base" in url:
                mock_resp.json.return_value = kb_response
            elif "knowledge_graph" in url:
                mock_resp.json.return_value = kg_response
            else:
                # 模拟HTML内容获取
                mock_resp.text = "<html><body><h1>中医养生</h1><p>内容...</p></body></html>"
                mock_resp.content = mock_resp.text.encode()
            
            return mock_resp
        
        mock_get.side_effect = mock_request_side_effect
        mock_post.side_effect = mock_request_side_effect
        
        # 发送集成搜索请求
        response = client.post(
            '/api/web-search/integrated-search',
            json={"query": "中医养生太极拳", "include_insights": True}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["query"] == "中医养生太极拳"
        assert "web_results" in data
        assert "knowledge_results" in data
        assert "graph_data" in data
        assert "combined_results" in data 