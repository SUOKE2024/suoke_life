#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web搜索API路由
"""

from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify, current_app
from loguru import logger
from prometheus_client import Counter, Histogram

from ...web_search import ContentProcessor, KnowledgeIntegration, SearchProvider

# 创建Blueprint
web_search_bp = Blueprint('web_search', __name__, url_prefix='/api/web-search')

# 指标
SEARCH_COUNTER = Counter('web_search_api_total', 'Total number of web search API requests', ['endpoint'])
SEARCH_LATENCY = Histogram('web_search_api_latency_seconds', 'Web search API latency', ['endpoint'])

@web_search_bp.route('/search', methods=['POST'])
def search():
    """通用搜索接口"""
    data = request.json
    query = data.get('query', '')
    engine = data.get('engine', '')
    max_results = data.get('max_results', 10)
    include_knowledge = data.get('include_knowledge', True)
    include_insights = data.get('include_insights', False)
    
    if not query:
        return jsonify({"error": "查询内容不能为空"}), 400
    
    with SEARCH_LATENCY.labels(endpoint='search').time():
        SEARCH_COUNTER.labels(endpoint='search').inc()
        
        config = current_app.config.get('WEB_SEARCH_CONFIG', {})
        search_provider = SearchProvider(config)
        content_processor = ContentProcessor(config)
        knowledge_integration = KnowledgeIntegration(config)
        
        try:
            # 进行搜索
            web_results = search_provider.search(query, engine, max_results)
            
            # 过滤搜索结果
            filtered_results = content_processor.filter_results(web_results)
            
            response_data = {
                "query": query,
                "engine": engine or search_provider.default_engine,
                "web_results": filtered_results
            }
            
            # 整合知识库内容（如果启用）
            if include_knowledge:
                enriched_data = knowledge_integration.enrich_search_results(query, filtered_results)
                
                # 整合结果
                combined_results = content_processor.combine_results(
                    filtered_results, 
                    enriched_data.get('knowledge_results', [])
                )
                
                response_data.update({
                    "combined_results": combined_results,
                    "knowledge_results": enriched_data.get('knowledge_results', []),
                    "graph_data": enriched_data.get('graph_data', {})
                })
            
            # 生成洞察（如果启用）
            if include_insights:
                insights = content_processor.generate_insights(
                    query, 
                    response_data.get('combined_results', filtered_results)
                )
                response_data["insights"] = insights
                
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return jsonify({"error": str(e)}), 500

@web_search_bp.route('/knowledge', methods=['POST'])
def query_knowledge():
    """知识库查询接口"""
    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 5)
    
    if not query:
        return jsonify({"error": "查询内容不能为空"}), 400
    
    with SEARCH_LATENCY.labels(endpoint='knowledge').time():
        SEARCH_COUNTER.labels(endpoint='knowledge').inc()
        
        config = current_app.config.get('WEB_SEARCH_CONFIG', {})
        knowledge_integration = KnowledgeIntegration(config)
        
        try:
            # 调用知识库的语义搜索
            results = knowledge_integration.semantic_search(query, limit)
            
            return jsonify({
                "query": query,
                "results": results
            })
        except Exception as e:
            logger.error(f"知识库查询失败: {e}")
            return jsonify({"error": str(e)}), 500

@web_search_bp.route('/graph', methods=['POST'])
def query_graph():
    """知识图谱查询接口"""
    data = request.json
    entity = data.get('entity', '')
    relation_types = data.get('relation_types', [])
    
    if not entity:
        return jsonify({"error": "实体名称不能为空"}), 400
    
    with SEARCH_LATENCY.labels(endpoint='graph').time():
        SEARCH_COUNTER.labels(endpoint='graph').inc()
        
        config = current_app.config.get('WEB_SEARCH_CONFIG', {})
        knowledge_integration = KnowledgeIntegration(config)
        
        try:
            # 调用知识图谱查询
            results = knowledge_integration.query_knowledge_graph(entity, relation_types)
            
            return jsonify({
                "entity": entity,
                "graph": results
            })
        except Exception as e:
            logger.error(f"知识图谱查询失败: {e}")
            return jsonify({"error": str(e)}), 500

@web_search_bp.route('/integrated-search', methods=['POST'])
def integrated_search():
    """集成搜索接口，整合网络搜索和知识库搜索"""
    data = request.json
    query = data.get('query', '')
    engine = data.get('engine', '')
    max_results = data.get('max_results', 10)
    include_insights = data.get('include_insights', True)
    
    if not query:
        return jsonify({"error": "查询内容不能为空"}), 400
    
    with SEARCH_LATENCY.labels(endpoint='integrated_search').time():
        SEARCH_COUNTER.labels(endpoint='integrated_search').inc()
        
        config = current_app.config.get('WEB_SEARCH_CONFIG', {})
        search_provider = SearchProvider(config)
        content_processor = ContentProcessor(config)
        knowledge_integration = KnowledgeIntegration(config)
        
        try:
            # 进行网络搜索
            web_results = search_provider.search(query, engine, max_results)
            
            # 过滤和丰富搜索结果
            filtered_results = content_processor.filter_results(web_results)
            enriched_data = knowledge_integration.enrich_search_results(query, filtered_results)
            
            # 整合结果
            combined_results = content_processor.combine_results(
                filtered_results, 
                enriched_data.get('knowledge_results', [])
            )
            
            # 构建响应
            response_data = {
                "query": query,
                "engine": engine or search_provider.default_engine,
                "combined_results": combined_results,
                "web_results": filtered_results,
                "knowledge_results": enriched_data.get('knowledge_results', []),
                "graph_data": enriched_data.get('graph_data', {})
            }
            
            # 生成洞察（如果启用）
            if include_insights:
                insights = content_processor.generate_insights(query, combined_results)
                response_data["insights"] = insights
                
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"集成搜索失败: {e}")
            return jsonify({"error": str(e)}), 500 