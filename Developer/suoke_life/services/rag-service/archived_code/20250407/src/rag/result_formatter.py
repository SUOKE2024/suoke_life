#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
结果格式化器
=========
用于格式化RAG查询和检索结果
"""

import json
from typing import List, Dict, Any, Optional, Union


class ResultFormatter:
    """结果格式化器，用于格式化RAG查询和检索结果"""
    
    @staticmethod
    def format_query_result(
        query: str,
        answer: Optional[str] = None,
        contexts: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        format_type: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """
        格式化查询结果
        
        Args:
            query: 原始查询
            answer: 生成的回答
            contexts: 检索上下文列表
            metadata: 结果元数据
            format_type: 格式类型，'json' 或 'text'
            
        Returns:
            Union[str, Dict[str, Any]]: 格式化的结果
        """
        metadata = metadata or {}
        contexts = contexts or []
        
        # 为每个上下文添加序号
        for i, context in enumerate(contexts):
            context["index"] = i + 1
            
        result = {
            "query": query,
            "answer": answer or "",
            "contexts": contexts,
            "metadata": metadata
        }
        
        if format_type.lower() == "json":
            return result
        else:
            return ResultFormatter.json_to_text(result)
    
    @staticmethod
    def format_search_result(
        query: str,
        contexts: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        format_type: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """
        格式化搜索结果
        
        Args:
            query: 原始查询
            contexts: 检索上下文列表
            metadata: 结果元数据
            format_type: 格式类型，'json' 或 'text'
            
        Returns:
            Union[str, Dict[str, Any]]: 格式化的结果
        """
        metadata = metadata or {}
        
        # 为每个上下文添加序号
        for i, context in enumerate(contexts):
            context["index"] = i + 1
            
        result = {
            "query": query,
            "contexts": contexts,
            "metadata": metadata
        }
        
        if format_type.lower() == "json":
            return result
        else:
            return ResultFormatter.search_json_to_text(result)
    
    @staticmethod
    def json_to_text(result: Dict[str, Any]) -> str:
        """
        将JSON结果格式化为文本
        
        Args:
            result: JSON格式的结果
            
        Returns:
            str: 文本格式的结果
        """
        query = result.get("query", "")
        answer = result.get("answer", "")
        contexts = result.get("contexts", [])
        
        text_parts = []
        text_parts.append(f"问题: {query}")
        text_parts.append("\n答案: " + answer if answer else "\n未找到答案")
        
        if contexts:
            text_parts.append("\n\n参考资料:")
            for i, context in enumerate(contexts):
                text = context.get("text", "")
                source = context.get("metadata", {}).get("source", "未知来源")
                text_parts.append(f"\n[{i+1}] {text} (来源: {source})")
        
        return "\n".join(text_parts)
    
    @staticmethod
    def search_json_to_text(result: Dict[str, Any]) -> str:
        """
        将搜索JSON结果格式化为文本
        
        Args:
            result: JSON格式的结果
            
        Returns:
            str: 文本格式的结果
        """
        query = result.get("query", "")
        contexts = result.get("contexts", [])
        
        text_parts = []
        text_parts.append(f"搜索查询: {query}")
        
        if contexts:
            text_parts.append("\n搜索结果:")
            for i, context in enumerate(contexts):
                text = context.get("text", "")
                score = context.get("score", 0)
                score_str = f"{score:.2f}" if isinstance(score, float) else str(score)
                source = context.get("metadata", {}).get("source", "未知来源")
                text_parts.append(f"\n[{i+1}] 相关度: {score_str}\n{text}\n(来源: {source})")
        else:
            text_parts.append("\n未找到相关结果")
        
        return "\n".join(text_parts)
    
    @staticmethod
    def format_error(error_message: str, format_type: str = "json") -> Union[str, Dict[str, Any]]:
        """
        格式化错误信息
        
        Args:
            error_message: 错误消息
            format_type: 格式类型，'json' 或 'text'
            
        Returns:
            Union[str, Dict[str, Any]]: 格式化的错误信息
        """
        result = {
            "error": True,
            "message": error_message
        }
        
        if format_type.lower() == "json":
            return result
        else:
            return f"错误: {error_message}" 