#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SearchProvider单元测试
"""

import pytest
from unittest.mock import patch, MagicMock
import json
import requests

from src.web_search.search_provider import SearchProvider

# 测试数据
TEST_CONFIG = {
    "api_keys": {
        "google": "test_google_key",
        "brave": "test_brave_key",
        "bing": "test_bing_key"
    },
    "search": {
        "default_engine": "brave",
        "max_results": 5,
        "timeout": 10
    },
    "cache": {
        "enabled": True,
        "ttl": 3600
    }
}

class TestSearchProvider:
    """SearchProvider测试类"""
    
    @pytest.fixture
    def search_provider(self):
        """创建SearchProvider实例"""
        return SearchProvider(TEST_CONFIG)
    
    def test_init(self, search_provider):
        """测试初始化"""
        assert search_provider.default_engine == "brave"
        assert search_provider.max_results == 5
        assert search_provider.timeout == 10
        assert search_provider.cache_enabled == True
        assert search_provider.cache_ttl == 3600
        assert search_provider.api_keys["google"] == "test_google_key"
        assert search_provider.api_keys["brave"] == "test_brave_key"
        assert search_provider.api_keys["bing"] == "test_bing_key"
    
    def test_mock_search_results(self, search_provider):
        """测试模拟搜索结果"""
        results = search_provider._mock_search_results("test query", 3)
        
        assert len(results) == 3
        assert "test query" in results[0]["title"]
        assert "test query" in results[0]["snippet"]
        assert "example.com" in results[0]["link"]
    
    @patch("requests.get")
    def test_brave_search(self, mock_get, search_provider):
        """测试Brave搜索"""
        # 模拟Brave API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "测试结果1",
                        "url": "https://example.com/1",
                        "description": "这是一个测试结果",
                        "age": "2023-01-01",
                        "meta_url": {"hostname": "example.com"}
                    },
                    {
                        "title": "测试结果2",
                        "url": "https://example.com/2",
                        "description": "这是另一个测试结果",
                        "age": "2023-01-02",
                        "meta_url": {"hostname": "example.com"}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # 执行搜索
        results = search_provider.brave_search("测试查询", 2)
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["title"] == "测试结果1"
        assert results[0]["link"] == "https://example.com/1"
        assert results[0]["snippet"] == "这是一个测试结果"
        assert results[0]["date"] == "2023-01-01"
        assert results[0]["source"] == "example.com"
        
        # 验证API调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["timeout"] == 10
        assert kwargs["headers"]["X-Subscription-Token"] == "test_brave_key"
        assert kwargs["params"]["q"] == "测试查询"
    
    @patch("requests.get")
    def test_brave_search_error(self, mock_get, search_provider):
        """测试Brave搜索错误处理"""
        # 模拟请求失败
        mock_get.side_effect = requests.RequestException("连接错误")
        
        # 执行搜索
        results = search_provider.brave_search("测试查询", 2)
        
        # 验证结果为模拟数据
        assert len(results) == 2
        assert "测试查询" in results[0]["title"]
    
    def test_search_with_cache(self, search_provider):
        """测试带缓存的搜索"""
        with patch.object(search_provider, 'brave_search') as mock_brave_search:
            # 模拟brave_search返回
            mock_brave_search.return_value = [{"title": "缓存测试结果"}]
            
            # 第一次搜索，调用brave_search
            results1 = search_provider.search("缓存测试", "brave", 1)
            assert results1 == [{"title": "缓存测试结果"}]
            mock_brave_search.assert_called_once()
            
            # 重置mock，再次搜索相同查询，应使用缓存
            mock_brave_search.reset_mock()
            results2 = search_provider.search("缓存测试", "brave", 1)
            assert results2 == [{"title": "缓存测试结果"}]
            mock_brave_search.assert_not_called()  # 不应再次调用brave_search
    
    def test_search_different_engines(self, search_provider):
        """测试不同搜索引擎"""
        with patch.object(search_provider, 'brave_search') as mock_brave, \
             patch.object(search_provider, 'google_search') as mock_google, \
             patch.object(search_provider, 'bing_search') as mock_bing, \
             patch.object(search_provider, 'duckduckgo_search') as mock_duckduckgo:
            
            # 设置每个搜索引擎的返回值
            mock_brave.return_value = [{"title": "Brave结果"}]
            mock_google.return_value = [{"title": "Google结果"}]
            mock_bing.return_value = [{"title": "Bing结果"}]
            mock_duckduckgo.return_value = [{"title": "DuckDuckGo结果"}]
            
            # 测试每个引擎
            assert search_provider.search("测试", "brave", 1) == [{"title": "Brave结果"}]
            assert search_provider.search("测试", "google", 1) == [{"title": "Google结果"}]
            assert search_provider.search("测试", "bing", 1) == [{"title": "Bing结果"}]
            assert search_provider.search("测试", "duckduckgo", 1) == [{"title": "DuckDuckGo结果"}]
            
            # 测试默认引擎
            assert search_provider.search("测试") == [{"title": "Brave结果"}] 