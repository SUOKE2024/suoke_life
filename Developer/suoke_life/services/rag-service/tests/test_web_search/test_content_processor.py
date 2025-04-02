#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ContentProcessor单元测试
"""

import pytest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup
import re

from src.web_search.content_processor import ContentProcessor

# 测试数据
TEST_CONFIG = {
    "content_processing": {
        "summarization": {
            "enabled": True,
            "max_length": 100
        },
        "translation": {
            "enabled": True,
            "target_language": "zh-CN"
        },
        "filtering": {
            "enabled": True,
            "blocked_domains": [
                "blocked-site.com",
                "malicious-domain.com"
            ]
        }
    }
}

class TestContentProcessor:
    """ContentProcessor测试类"""
    
    @pytest.fixture
    def content_processor(self):
        """创建ContentProcessor实例"""
        return ContentProcessor(TEST_CONFIG)
    
    def test_init(self, content_processor):
        """测试初始化"""
        assert content_processor.summarization_enabled == True
        assert content_processor.max_summary_length == 100
        assert content_processor.translation_enabled == True
        assert content_processor.target_language == "zh-CN"
        assert content_processor.filtering_enabled == True
        assert "blocked-site.com" in content_processor.blocked_domains
    
    def test_filter_results(self, content_processor):
        """测试过滤搜索结果"""
        test_results = [
            {"title": "正常结果", "link": "https://example.com/page1"},
            {"title": "应被过滤", "link": "https://blocked-site.com/page"},
            {"title": "另一个正常结果", "link": "https://good-site.com/page"},
            {"title": "应被过滤", "link": "https://malicious-domain.com/page"}
        ]
        
        filtered = content_processor.filter_results(test_results)
        
        assert len(filtered) == 2
        assert filtered[0]["title"] == "正常结果"
        assert filtered[1]["title"] == "另一个正常结果"
        
        # 测试禁用过滤
        content_processor.filtering_enabled = False
        unfiltered = content_processor.filter_results(test_results)
        assert len(unfiltered) == 4
    
    @patch("requests.get")
    def test_extract_content(self, mock_get, content_processor):
        """测试内容提取"""
        # 模拟HTML响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>测试页面</title></head>
            <body>
                <script>alert('script');</script>
                <header>页面头部</header>
                <div>
                    <h1>主要内容标题</h1>
                    <p>这是一段<b>主要内容</b>。</p>
                </div>
                <footer>页面底部</footer>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # 执行内容提取
        content = content_processor.extract_content("https://example.com/page")
        
        # 验证结果
        assert "主要内容标题" in content
        assert "主要内容" in content
        assert "script" not in content
        assert "页面头部" not in content
        assert "页面底部" not in content
        
        # 测试请求失败
        mock_get.side_effect = requests.RequestException("连接失败")
        assert content_processor.extract_content("https://example.com/error") is None
    
    def test_summarize_text(self, content_processor):
        """测试文本摘要"""
        long_text = "这是第一个句子。这是第二个句子。这是第三个句子。这是第四个句子，但它不应该出现在摘要中。"
        
        # 摘要应只包含前三个句子
        summary = content_processor.summarize_text(long_text)
        
        assert "这是第一个句子" in summary
        assert "这是第二个句子" in summary
        assert "这是第三个句子" in summary
        assert "这是第四个句子" not in summary
        
        # 测试超长文本截断
        content_processor.max_summary_length = 10
        short_summary = content_processor.summarize_text(long_text)
        assert len(short_summary) <= 13  # 10 + "..."
        
        # 测试禁用摘要
        content_processor.summarization_enabled = False
        disabled_summary = content_processor.summarize_text(long_text)
        assert disabled_summary == long_text
    
    def test_combine_results(self, content_processor):
        """测试结果整合"""
        web_results = [
            {"title": "Web结果1", "link": "https://example.com/1", "snippet": "Web摘要1", "source": "网站1"},
            {"title": "Web结果2", "link": "https://example.com/2", "snippet": "Web摘要2", "source": "网站2"}
        ]
        
        kb_results = [
            {"title": "知识库结果1", "link": "kb://1", "content": "知识库内容1", "relevance_score": 0.95},
            {"title": "知识库结果2", "link": "kb://2", "content": "知识库内容2", "relevance_score": 0.85}
        ]
        
        combined = content_processor.combine_results(web_results, kb_results)
        
        assert len(combined) == 4
        # 验证按相关性排序
        assert combined[0]["title"] == "知识库结果1"
        assert combined[1]["title"] == "知识库结果2"
        
        # 验证字段转换
        assert combined[0]["source"] == "索克知识库"
        assert combined[0]["source_type"] == "knowledge_base"
        assert combined[0]["snippet"].startswith("知识库内容1")
        
        # 验证web结果的字段
        web_in_combined = [r for r in combined if r["source_type"] == "web_search"]
        assert len(web_in_combined) == 2
        assert "relevance_score" in web_in_combined[0]
    
    def test_extract_entities(self, content_processor):
        """测试实体提取"""
        results = [
            {"title": "太极拳和健康", "snippet": "太极拳对健康的好处"},
            {"title": "中医养生方法", "snippet": "传统中医养生方法包括太极拳和气功"},
            {"title": "气功基础教程", "snippet": "气功是中医养生的重要组成部分"}
        ]
        
        entities = content_processor.extract_entities(results)
        
        assert len(entities) <= 5  # 最多返回5个实体
        assert "太极拳" in entities
        assert "中医养生" in entities or "中医" in entities or "养生" in entities
        assert "气功" in entities
    
    def test_generate_insights(self, content_processor):
        """测试洞察生成"""
        query = "中医养生方法"
        results = [
            {"title": "太极拳养生", "source_type": "knowledge_base", "relevance_score": 0.9},
            {"title": "气功基础", "source_type": "knowledge_base", "relevance_score": 0.85},
            {"title": "中医理论", "source_type": "web_search", "relevance_score": 0.7},
            {"title": "现代养生", "source_type": "web_search", "relevance_score": 0.6}
        ]
        
        insights = content_processor.generate_insights(query, results)
        
        assert insights["query"] == query
        assert insights["result_count"] == 4
        assert isinstance(insights["top_topics"], list)
        assert "source_distribution" in insights
        assert insights["source_distribution"]["knowledge_base"] == 2
        assert insights["source_distribution"]["web_search"] == 2
        assert isinstance(insights["average_relevance"], float)
        assert 0 <= insights["average_relevance"] <= 1 