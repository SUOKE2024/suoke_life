#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
内容处理模块
提供搜索内容处理、整合和分析功能
"""

import re
from typing import Dict, List, Optional, Union, Any
from loguru import logger
import requests
from bs4 import BeautifulSoup
import html2text
import json
import pandas as pd
from urllib.parse import urlparse

class ContentProcessor:
    """内容处理类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化内容处理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.summarization_enabled = config.get('content_processing', {}).get('summarization', {}).get('enabled', True)
        self.max_summary_length = config.get('content_processing', {}).get('summarization', {}).get('max_length', 200)
        self.translation_enabled = config.get('content_processing', {}).get('translation', {}).get('enabled', True)
        self.target_language = config.get('content_processing', {}).get('translation', {}).get('target_language', 'zh-CN')
        self.filtering_enabled = config.get('content_processing', {}).get('filtering', {}).get('enabled', True)
        self.blocked_domains = config.get('content_processing', {}).get('filtering', {}).get('blocked_domains', [])
        
        # 创建HTML到文本转换器
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.ignore_tables = False
    
    def filter_results(self, results: List[Dict]) -> List[Dict]:
        """
        过滤搜索结果
        
        Args:
            results: 搜索结果列表
            
        Returns:
            过滤后的搜索结果
        """
        if not self.filtering_enabled:
            return results
            
        filtered_results = []
        for result in results:
            # 检查URL是否在阻止列表中
            if 'link' in result:
                domain = urlparse(result['link']).netloc
                if domain in self.blocked_domains:
                    continue
            
            filtered_results.append(result)
        
        return filtered_results
    
    def extract_content(self, url: str) -> Optional[str]:
        """
        从URL提取内容
        
        Args:
            url: 网页URL
            
        Returns:
            提取的文本内容
        """
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return None
                
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 移除脚本、样式和导航元素
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # 转换为文本
            text = self.html_converter.handle(str(soup))
            
            # 清理文本
            text = re.sub(r'\n{3,}', '\n\n', text)  # 移除多余空行
            text = re.sub(r'\s{2,}', ' ', text)     # 移除多余空格
            
            return text
            
        except Exception as e:
            logger.error(f"提取内容异常: {e}")
            return None
    
    def summarize_text(self, text: str) -> str:
        """
        摘要生成
        
        Args:
            text: 要摘要的文本
            
        Returns:
            生成的摘要
        """
        if not self.summarization_enabled or not text:
            return text
            
        # 简单摘要方法 - 提取前几句话
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        
        summary = ' '.join(sentences[:3])
        
        # 限制长度
        if len(summary) > self.max_summary_length:
            summary = summary[:self.max_summary_length] + "..."
            
        return summary
    
    def combine_results(self, web_results: List[Dict], knowledge_results: List[Dict]) -> List[Dict]:
        """
        整合网络搜索结果和知识库结果
        
        Args:
            web_results: 网络搜索结果
            knowledge_results: 知识库搜索结果
            
        Returns:
            整合后的结果
        """
        combined_results = []
        
        # 添加知识库结果（优先显示）
        for i, result in enumerate(knowledge_results):
            combined_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("content", "")[:200] + "..." if result.get("content") else "",
                "source": "索克知识库",
                "source_type": "knowledge_base",
                "relevance_score": result.get("relevance_score", 0.9),
                "position": i
            })
        
        # 添加网络搜索结果
        for i, result in enumerate(web_results):
            combined_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": result.get("source", "网络搜索"),
                "source_type": "web_search",
                "relevance_score": 0.7 - (i * 0.05),  # 简单递减权重
                "position": i + len(knowledge_results)
            })
        
        # 按相关性排序
        combined_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return combined_results
    
    def extract_entities(self, results: List[Dict]) -> List[str]:
        """
        从搜索结果中提取实体
        
        Args:
            results: 搜索结果列表
            
        Returns:
            提取的实体列表
        """
        entities = []
        
        # 简单实体提取 - 使用标题和摘要
        for result in results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            # 提取可能的实体（简单实现）
            title_entities = [word for word in title.split() if len(word) > 1 and not re.match(r'[\W\d]+', word)]
            
            entities.extend(title_entities)
        
        # 去重
        entities = list(set(entities))
        
        return entities[:5]  # 返回前5个实体
    
    def generate_insights(self, query: str, combined_results: List[Dict]) -> Dict:
        """
        从搜索结果生成洞察
        
        Args:
            query: 搜索查询
            combined_results: 整合的搜索结果
            
        Returns:
            生成的洞察
        """
        # 主题分析
        topics = self.extract_entities(combined_results[:5])
        
        # 信息来源分析
        sources = {}
        for result in combined_results:
            source_type = result.get("source_type", "")
            if source_type in sources:
                sources[source_type] += 1
            else:
                sources[source_type] = 1
                
        # 相关性分布
        relevance_scores = [result.get("relevance_score", 0) for result in combined_results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        return {
            "query": query,
            "result_count": len(combined_results),
            "top_topics": topics,
            "source_distribution": sources,
            "average_relevance": avg_relevance
        }
