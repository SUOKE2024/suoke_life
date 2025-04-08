"""
知识检索器模块
定义了用于从知识库和知识图谱中检索信息的各种检索器
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from fastapi import HTTPException

from ..knowledge_graph.client import KnowledgeGraphClient
from ..knowledge_graph.schema import NodeType, NodeUnion, KnowledgeGraphFilter
from ..vector_db.client import VectorDBClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """知识检索基类"""
    
    def __init__(self, kg_client: KnowledgeGraphClient, vector_client: VectorDBClient):
        self.kg_client = kg_client
        self.vector_client = vector_client
    
    async def retrieve(self, query: str, **kwargs):
        """检索知识的抽象方法"""
        raise NotImplementedError("Subclasses must implement retrieve method")


class SemanticKnowledgeRetriever(KnowledgeRetriever):
    """基于语义向量的知识检索器"""
    
    async def retrieve(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """通过语义相似度检索知识"""
        try:
            filter_node_types = kwargs.get("node_types")
            limit = kwargs.get("limit", 10)
            threshold = kwargs.get("threshold", 0.7)
            
            # 获取查询的向量表示
            query_vector = await self.vector_client.encode_text(query)
            
            # 根据查询向量搜索相似节点
            similar_nodes = await self.vector_client.search_vectors(
                query_vector,
                filter_node_types,
                limit,
                threshold
            )
            
            # 对于每个找到的向量ID，获取完整节点信息
            result_nodes = []
            for item in similar_nodes:
                vector_id = item["id"]
                similarity = item["similarity"]
                
                # 从知识图谱获取节点
                node = await self.kg_client.get_node_by_vector_id(vector_id)
                if node:
                    # 添加相似度得分
                    node_dict = dict(node)
                    node_dict["similarity_score"] = similarity
                    result_nodes.append(node_dict)
            
            return result_nodes
            
        except Exception as e:
            logger.error(f"Error in semantic retrieval: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")


class GraphBasedKnowledgeRetriever(KnowledgeRetriever):
    """基于图遍历的知识检索器"""
    
    async def retrieve(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """通过图遍历检索知识"""
        try:
            filter_node_types = kwargs.get("node_types")
            categories = kwargs.get("categories")
            tags = kwargs.get("tags")
            relation_types = kwargs.get("relation_types")
            limit = kwargs.get("limit", 20)
            
            # 构建知识图谱过滤器
            kg_filter = KnowledgeGraphFilter(
                node_types=filter_node_types,
                categories=categories,
                tags=tags,
                relation_types=relation_types,
                text_query=query,
                limit=limit
            )
            
            # 从知识图谱中查询
            nodes = await self.kg_client.search_nodes(kg_filter)
            return [dict(node) for node in nodes]
            
        except Exception as e:
            logger.error(f"Error in graph-based retrieval: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")


class HybridKnowledgeRetriever(KnowledgeRetriever):
    """混合知识检索器，结合语义和图检索"""
    
    def __init__(self, kg_client: KnowledgeGraphClient, vector_client: VectorDBClient):
        super().__init__(kg_client, vector_client)
        self.semantic_retriever = SemanticKnowledgeRetriever(kg_client, vector_client)
        self.graph_retriever = GraphBasedKnowledgeRetriever(kg_client, vector_client)
    
    async def retrieve(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """结合语义和图检索方法检索知识"""
        try:
            semantic_weight = kwargs.get("semantic_weight", 0.7)
            graph_weight = 1.0 - semantic_weight
            
            # 并行执行两种检索
            semantic_results = await self.semantic_retriever.retrieve(query, **kwargs)
            graph_results = await self.graph_retriever.retrieve(query, **kwargs)
            
            # 合并结果并去重
            combined_results = self._merge_results(
                semantic_results, 
                graph_results, 
                semantic_weight, 
                graph_weight
            )
            
            # 按最终得分排序
            sorted_results = sorted(
                combined_results, 
                key=lambda x: x.get("final_score", 0), 
                reverse=True
            )
            
            # 限制结果数量
            limit = kwargs.get("limit", 10)
            return sorted_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    def _merge_results(
        self, 
        semantic_results: List[Dict[str, Any]], 
        graph_results: List[Dict[str, Any]], 
        semantic_weight: float,
        graph_weight: float
    ) -> List[Dict[str, Any]]:
        """合并两种检索结果，按ID去重，计算混合得分"""
        result_map = {}
        
        # 处理语义检索结果
        for item in semantic_results:
            node_id = item.get("id")
            if node_id:
                similarity = item.get("similarity_score", 0)
                result_map[node_id] = {
                    **item,
                    "semantic_score": similarity,
                    "graph_score": 0,
                    "final_score": similarity * semantic_weight
                }
        
        # 处理图检索结果，更新或添加到结果映射
        for item in graph_results:
            node_id = item.get("id")
            if node_id:
                # 计算图检索得分（这里简化为1.0，实际可以基于相关性或排名计算）
                graph_score = 1.0
                
                if node_id in result_map:
                    # 如果已存在该节点，更新得分
                    existing = result_map[node_id]
                    existing["graph_score"] = graph_score
                    existing["final_score"] = (
                        existing.get("semantic_score", 0) * semantic_weight +
                        graph_score * graph_weight
                    )
                else:
                    # 如果不存在，添加新节点
                    result_map[node_id] = {
                        **item,
                        "semantic_score": 0,
                        "graph_score": graph_score,
                        "final_score": graph_score * graph_weight
                    }
        
        return list(result_map.values())


class SpecializedKnowledgeRetriever(KnowledgeRetriever):
    """专业领域知识检索器，针对特定类型的知识进行优化检索"""
    
    async def retrieve(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """根据专业领域检索知识"""
        try:
            domain = kwargs.get("domain", "general")
            hybrid_retriever = HybridKnowledgeRetriever(self.kg_client, self.vector_client)
            
            # 根据领域调整检索参数
            if domain == "precision_medicine":
                kwargs["node_types"] = [NodeType.PRECISION_MEDICINE]
                kwargs["semantic_weight"] = 0.8  # 精准医学更依赖语义匹配
            
            elif domain == "traditional_medicine":
                kwargs["node_types"] = [NodeType.TCM, NodeType.HERB, NodeType.PRESCRIPTION]
                kwargs["semantic_weight"] = 0.6  # 传统医学平衡语义和图关系
            
            elif domain == "mental_health":
                kwargs["node_types"] = [NodeType.MENTAL_HEALTH]
                kwargs["semantic_weight"] = 0.75  # 心理健康倾向于语义
            
            elif domain == "environmental_health":
                kwargs["node_types"] = [NodeType.ENVIRONMENTAL_HEALTH]
                kwargs["semantic_weight"] = 0.7  # 环境健康
            
            elif domain == "multimodal_health":
                kwargs["node_types"] = [NodeType.MULTIMODAL_HEALTH]
                kwargs["semantic_weight"] = 0.7  # 多模态健康
            
            # 使用混合检索器检索
            results = await hybrid_retriever.retrieve(query, **kwargs)
            
            # 对特定领域结果进行后处理
            if domain == "precision_medicine":
                results = self._post_process_precision_medicine(results)
            elif domain == "mental_health":
                results = self._post_process_mental_health(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in specialized retrieval: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    def _post_process_precision_medicine(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """精准医学知识后处理"""
        # 例如，根据置信度级别排序或过滤
        confidence_order = {"high": 3, "moderate": 2, "low": 1, "preliminary": 0}
        for result in results:
            confidence = result.get("confidence_level", "preliminary")
            confidence_score = confidence_order.get(confidence, 0)
            result["confidence_score"] = confidence_score
            
            # 调整最终得分，考虑置信度
            final_score = result.get("final_score", 0)
            result["final_score"] = final_score * (0.7 + 0.3 * (confidence_score / 3))
        
        # 重新排序
        return sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)
    
    def _post_process_mental_health(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """心理健康知识后处理"""
        # 例如，优先考虑有完整干预方法的结果
        for result in results:
            intervention_bonus = 0
            if result.get("intervention_approaches") and len(result.get("intervention_approaches", [])) > 0:
                intervention_bonus = 0.2
            
            # 调整最终得分
            final_score = result.get("final_score", 0)
            result["final_score"] = final_score * (1 + intervention_bonus)
        
        # 重新排序
        return sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)