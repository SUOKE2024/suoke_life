#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检索模块
======
提供基于知识图谱的内容检索功能
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union

from knowledge_graph.knowledge_graph import KnowledgeGraph
from retrievers.keyword_search import KeywordSearcher
from retrievers.reranker import Reranker

logger = logging.getLogger(__name__)

class Retriever:
    """内容检索器类"""
    
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        keyword_searcher: KeywordSearcher,
        reranker: Reranker,
        top_k: int = 5
    ):
        """
        初始化检索器
        
        Args:
            knowledge_graph: 知识图谱实例
            keyword_searcher: 关键词搜索器
            reranker: 重排序器
            top_k: 检索结果数量
        """
        self.knowledge_graph = knowledge_graph
        self.keyword_searcher = keyword_searcher
        self.reranker = reranker
        self.top_k = top_k
        
    async def retrieve(
        self,
        query: str,
        search_types: List[str] = None,
        filters: Dict[str, List[str]] = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        检索内容
        
        Args:
            query: 用户查询
            search_types: 搜索类型列表，可包含"keyword"、"knowledge_graph"
            filters: 过滤条件
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if top_k is None:
            top_k = self.top_k
            
        if search_types is None:
            search_types = ["keyword", "knowledge_graph"]
            
        # 执行并行检索
        search_tasks = []
        
        if "keyword" in search_types:
            search_tasks.append(self._keyword_search(query))
            
        if "knowledge_graph" in search_types:
            search_tasks.append(self._kg_search(query))
            
        # 等待所有检索任务完成
        search_results = await asyncio.gather(*search_tasks)
        
        # 合并结果
        merged_results = []
        for results in search_results:
            merged_results.extend(results)
            
        # 应用过滤条件
        if filters:
            merged_results = self._apply_filters(merged_results, filters)
            
        # 重排序结果
        if len(merged_results) > 0:
            merged_results = await self._rerank(query, merged_results)
            
        # 截取前top_k个结果
        return merged_results[:top_k]
        
    async def _keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """
        执行关键词搜索
        
        Args:
            query: 用户查询
            
        Returns:
            搜索结果列表
        """
        try:
            results = self.keyword_searcher.search(query, top_k=self.top_k * 2)
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "score": result["score"],
                    "source": "keyword_search"
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"关键词搜索失败: {e}")
            return []
            
    async def _kg_search(self, query: str) -> List[Dict[str, Any]]:
        """
        执行知识图谱搜索
        
        Args:
            query: 用户查询
            
        Returns:
            搜索结果列表
        """
        try:
            # 使用知识图谱进行节点搜索
            nodes = self.knowledge_graph.search_nodes(query, limit=self.top_k * 2)
            
            # 格式化结果
            formatted_results = []
            for node in nodes:
                # 获取邻居节点作为上下文
                neighbors = self.knowledge_graph.get_neighbors(node.id, max_depth=1)
                
                # 构建内容
                content = f"{node.name}\n\n"
                if node.properties:
                    for key, value in node.properties.items():
                        if key not in ["id", "name", "type"]:
                            content += f"{key}: {value}\n"
                            
                # 添加邻居节点信息
                if neighbors:
                    content += "\n相关信息:\n"
                    for neighbor in neighbors[:5]:  # 限制相关信息数量
                        neighbor_node = neighbor["node"]
                        path = neighbor["path"][0] if neighbor["path"] else {}
                        relation_type = path.get("type", "相关")
                        content += f"- {relation_type}: {neighbor_node.name}\n"
                        
                formatted_results.append({
                    "content": content,
                    "metadata": {
                        "id": node.id,
                        "name": node.name,
                        "type": node.type,
                        "properties": node.properties
                    },
                    "score": 1.0,  # 初始分数
                    "source": "knowledge_graph"
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"知识图谱搜索失败: {e}")
            return []
            
    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        应用过滤条件
        
        Args:
            results: 检索结果列表
            filters: 过滤条件
            
        Returns:
            过滤后的结果列表
        """
        filtered_results = []
        
        for result in results:
            metadata = result.get("metadata", {})
            match = True
            
            # 检查每个过滤条件
            for field, values in filters.items():
                if field not in metadata:
                    match = False
                    break
                    
                field_value = metadata[field]
                
                # 处理列表类型的字段
                if isinstance(field_value, list):
                    if not any(v in field_value for v in values):
                        match = False
                        break
                # 处理字符串或其他类型
                elif field_value not in values:
                    match = False
                    break
                    
            if match:
                filtered_results.append(result)
                
        return filtered_results
        
    async def _rerank(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        重排序结果
        
        Args:
            query: 用户查询
            results: 检索结果列表
            
        Returns:
            重排序后的结果列表
        """
        try:
            # 提取内容列表
            contents = [result["content"] for result in results]
            
            # 使用重排序器
            scores = await self.reranker.rerank(query, contents)
            
            # 更新分数
            for i, score in enumerate(scores):
                results[i]["score"] = float(score)
                
            # 根据分数排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"重排序失败: {e}")
            return results  # 返回原始结果
            
    def close(self):
        """关闭资源"""
        if self.knowledge_graph:
            self.knowledge_graph.close() 