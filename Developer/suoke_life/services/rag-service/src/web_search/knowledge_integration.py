#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库和知识图谱集成模块
为网络搜索服务提供知识库和知识图谱集成能力
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any
import requests
from loguru import logger

class KnowledgeIntegration:
    """知识库和知识图谱集成类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化知识库集成
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.knowledge_base_url = config.get('services', {}).get('knowledge_base', {}).get('url', 'http://knowledge-base-service:8080')
        self.knowledge_graph_url = config.get('services', {}).get('knowledge_graph', {}).get('url', 'http://knowledge-graph-service:8090')
        self.api_key = config.get('services', {}).get('knowledge_base', {}).get('api_key', '')
        self.timeout = config.get('services', {}).get('knowledge_base', {}).get('timeout', 30)

    def semantic_search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        语义搜索知识库
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            url = f"{self.knowledge_base_url}/api/search/semantic"
            params = {
                "q": query,
                "limit": limit
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                logger.error(f"语义搜索请求失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"语义搜索异常: {e}")
            return []
    
    def get_related_knowledge(self, query: str, web_results: List[Dict], limit: int = 3) -> List[Dict]:
        """
        根据网络搜索结果获取相关知识
        
        Args:
            query: 原始查询
            web_results: 网络搜索结果
            limit: 结果数量限制
            
        Returns:
            相关知识列表
        """
        try:
            # 从网络搜索结果中提取关键信息用于查询知识库
            topics = []
            for result in web_results[:3]:  # 只取前三个结果
                topics.append(result.get('title', ''))
                
            # 组合原始查询和提取的主题
            enhanced_query = f"{query} {' '.join(topics)}"
            
            # 调用语义搜索
            return self.semantic_search(enhanced_query, limit)
                
        except Exception as e:
            logger.error(f"获取相关知识异常: {e}")
            return []
    
    def query_knowledge_graph(self, entity: str, relation_types: Optional[List[str]] = None) -> Dict:
        """
        查询知识图谱
        
        Args:
            entity: 实体名称
            relation_types: 关系类型列表
            
        Returns:
            知识图谱查询结果
        """
        try:
            url = f"{self.knowledge_graph_url}/api/graph/query"
            payload = {
                "entity": entity,
                "relation_types": relation_types or []
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"知识图谱查询失败: {response.status_code} - {response.text}")
                return {"nodes": [], "edges": []}
                
        except Exception as e:
            logger.error(f"知识图谱查询异常: {e}")
            return {"nodes": [], "edges": []}
    
    def enrich_search_results(self, query: str, web_results: List[Dict]) -> Dict:
        """
        使用知识库和知识图谱信息丰富搜索结果
        
        Args:
            query: 搜索查询
            web_results: 网络搜索结果
            
        Returns:
            丰富后的搜索结果
        """
        # 获取相关知识
        related_knowledge = self.get_related_knowledge(query, web_results)
        
        # 查询知识图谱
        graph_data = {}
        # 从查询或搜索结果中提取可能的实体
        potential_entities = [query]
        for result in web_results[:2]:
            if 'title' in result:
                potential_entities.append(result['title'])
        
        # 选择最可能是实体的词语
        main_entity = max(potential_entities, key=len)
        graph_data = self.query_knowledge_graph(main_entity)
        
        return {
            "web_results": web_results,
            "knowledge_results": related_knowledge,
            "graph_data": graph_data
        }
