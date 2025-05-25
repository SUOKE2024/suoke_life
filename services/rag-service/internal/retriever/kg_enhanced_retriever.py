#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱增强的检索器，结合Neo4j知识图谱查询和向量检索
"""

from typing import Dict, List, Any, Optional, Tuple
from loguru import logger

from ..model.document import Document, RetrieveResult
from ..repository.milvus_repository import MilvusRepository
from ..service.kg_integration_service import KnowledgeGraphIntegrationService
from .hybrid_retriever import HybridRetriever


class KGEnhancedRetriever(HybridRetriever):
    """
    知识图谱增强的检索器，在混合检索基础上增加知识图谱查询能力
    """
    
    def __init__(self, config: Dict[str, Any], milvus_repository: MilvusRepository):
        """
        初始化知识图谱增强检索器
        
        Args:
            config: 配置信息
            milvus_repository: Milvus向量数据库仓库
        """
        super().__init__(config, milvus_repository)
        self.kg_service = KnowledgeGraphIntegrationService(config)
        self.kg_weight = config.get('kg_weight', 0.3)  # 知识图谱权重
        self.enable_kg_expansion = config.get('enable_kg_expansion', True)  # 是否启用知识图谱扩展
    
    async def initialize(self) -> None:
        """初始化检索器"""
        await super().initialize()
        await self.kg_service.initialize()
        logger.info("Knowledge Graph Enhanced Retriever initialized")
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        collection_names: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0,
        rerank: bool = False
    ) -> RetrieveResult:
        """
        执行知识图谱增强的检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            collection_names: 向量集合名称列表
            metadata_filter: 元数据过滤条件
            score_threshold: 分数阈值
            rerank: 是否重排序
            
        Returns:
            检索结果
        """
        # 1. 执行基础混合检索
        base_result = await super().retrieve(
            query=query,
            top_k=top_k * 2,  # 获取更多结果用于后续融合
            collection_names=collection_names,
            metadata_filter=metadata_filter,
            score_threshold=score_threshold,
            rerank=False  # 暂不重排序
        )
        
        # 2. 识别查询中的医学实体
        entities = await self._extract_medical_entities(query)
        
        # 3. 如果识别到医学实体，进行知识图谱扩展
        kg_documents = []
        if entities and self.enable_kg_expansion:
            kg_documents = await self._expand_with_knowledge_graph(entities)
        
        # 4. 融合检索结果
        final_documents = await self._merge_results(
            base_documents=base_result.documents,
            kg_documents=kg_documents,
            query=query,
            top_k=top_k
        )
        
        # 5. 如果需要重排序，对最终结果进行重排序
        if rerank:
            final_documents = await self._rerank_documents(query, final_documents)
        
        # 6. 构建最终结果
        total_latency_ms = base_result.total_latency_ms  # 使用基础检索的延迟
        
        return RetrieveResult(
            documents=final_documents[:top_k],
            total_latency_ms=total_latency_ms
        )
    
    async def _extract_medical_entities(self, query: str) -> List[Tuple[str, str]]:
        """
        从查询中提取医学实体
        
        Args:
            query: 查询文本
            
        Returns:
            实体列表 [(实体类型, 实体名称), ...]
        """
        entities = []
        
        # 简单的基于规则的实体识别
        # TODO: 未来可以集成更复杂的NER模型
        
        # 体质关键词
        constitution_keywords = ["平和质", "气虚质", "阳虚质", "阴虚质", "痰湿质", 
                               "湿热质", "血瘀质", "气郁质", "特禀质"]
        for keyword in constitution_keywords:
            if keyword in query:
                entities.append(("constitution", keyword))
        
        # 症状关键词
        symptom_keywords = ["头痛", "失眠", "疲劳", "咳嗽", "发热", "腹痛", 
                           "胸闷", "心悸", "眩晕", "便秘"]
        for keyword in symptom_keywords:
            if keyword in query:
                entities.append(("symptom", keyword))
        
        # 中药关键词
        herb_keywords = ["人参", "黄芪", "当归", "甘草", "枸杞", "山药",
                        "茯苓", "白术", "陈皮", "半夏"]
        for keyword in herb_keywords:
            if keyword in query:
                entities.append(("herb", keyword))
        
        # 穴位关键词
        acupoint_keywords = ["足三里", "合谷", "太冲", "三阴交", "百会", 
                            "神门", "内关", "气海", "关元", "中脘"]
        for keyword in acupoint_keywords:
            if keyword in query:
                entities.append(("acupoint", keyword))
        
        logger.info(f"Extracted entities from query: {entities}")
        return entities
    
    async def _expand_with_knowledge_graph(self, entities: List[Tuple[str, str]]) -> List[Document]:
        """
        使用知识图谱扩展查询
        
        Args:
            entities: 实体列表
            
        Returns:
            扩展的文档列表
        """
        expanded_documents = []
        
        for entity_type, entity_name in entities:
            try:
                # 获取实体的相关信息
                # 这里需要先通过名称查找实体ID
                # TODO: 实现实体名称到ID的映射查询
                
                # 获取实体的关系
                relationships = await self.kg_service.get_entity_relationships(
                    entity_type=entity_type,
                    entity_id=entity_name  # 暂时使用名称作为ID
                )
                
                # 将关系信息转换为文档
                if relationships:
                    doc = self._relationship_to_document(
                        entity_type=entity_type,
                        entity_name=entity_name,
                        relationships=relationships
                    )
                    expanded_documents.append(doc)
                
                # 获取实体的子图
                subgraph = await self.kg_service.get_knowledge_subgraph(
                    entity_type=entity_type,
                    entity_id=entity_name,
                    depth=1
                )
                
                # 将子图信息转换为文档
                if subgraph:
                    docs = self._subgraph_to_documents(subgraph)
                    expanded_documents.extend(docs)
                    
            except Exception as e:
                logger.error(f"Error expanding entity {entity_name}: {str(e)}")
        
        logger.info(f"Expanded {len(expanded_documents)} documents from knowledge graph")
        return expanded_documents
    
    def _relationship_to_document(
        self, 
        entity_type: str, 
        entity_name: str, 
        relationships: Dict[str, Any]
    ) -> Document:
        """
        将关系信息转换为文档
        
        Args:
            entity_type: 实体类型
            entity_name: 实体名称
            relationships: 关系信息
            
        Returns:
            文档对象
        """
        content_parts = [f"{entity_type}：{entity_name}的相关信息"]
        
        # 处理各种关系
        for rel_type, related_entities in relationships.items():
            if related_entities:
                content_parts.append(f"\n{rel_type}：")
                for entity in related_entities[:5]:  # 限制数量
                    content_parts.append(f"  - {entity.get('name', entity.get('id'))}")
        
        content = "\n".join(content_parts)
        
        return Document(
            id=f"kg_rel_{entity_type}_{entity_name}",
            content=content,
            metadata={
                "source": "knowledge_graph",
                "entity_type": entity_type,
                "entity_name": entity_name,
                "relationship_type": "expanded"
            },
            score=self.kg_weight  # 使用配置的知识图谱权重作为初始分数
        )
    
    def _subgraph_to_documents(self, subgraph: Dict[str, Any]) -> List[Document]:
        """
        将子图信息转换为文档列表
        
        Args:
            subgraph: 子图数据
            
        Returns:
            文档列表
        """
        documents = []
        
        # 处理节点
        nodes = subgraph.get('nodes', [])
        for node in nodes[:10]:  # 限制数量
            content = self._node_to_content(node)
            if content:
                doc = Document(
                    id=f"kg_node_{node.get('type')}_{node.get('id')}",
                    content=content,
                    metadata={
                        "source": "knowledge_graph",
                        "entity_type": node.get('type'),
                        "entity_id": node.get('id'),
                        "subgraph_type": "node"
                    },
                    score=self.kg_weight * 0.8  # 子图节点权重稍低
                )
                documents.append(doc)
        
        return documents
    
    def _node_to_content(self, node: Dict[str, Any]) -> str:
        """
        将节点信息转换为内容文本
        
        Args:
            node: 节点数据
            
        Returns:
            内容文本
        """
        node_type = node.get('type', '')
        properties = node.get('properties', {})
        
        if not properties:
            return ""
        
        content_parts = [f"{node_type}：{properties.get('name', node.get('id'))}"]
        
        # 根据节点类型处理属性
        if node_type == 'constitution':
            for key in ['description', 'characteristics', 'treatment_methods']:
                if key in properties:
                    content_parts.append(f"{key}：{properties[key]}")
        elif node_type == 'syndrome':
            for key in ['description', 'main_symptoms', 'treatment_principle']:
                if key in properties:
                    content_parts.append(f"{key}：{properties[key]}")
        elif node_type == 'herb':
            for key in ['properties', 'effects', 'indications']:
                if key in properties:
                    content_parts.append(f"{key}：{properties[key]}")
        elif node_type == 'acupoint':
            for key in ['location', 'indications', 'operation_method']:
                if key in properties:
                    content_parts.append(f"{key}：{properties[key]}")
        
        return "\n".join(content_parts)
    
    async def _merge_results(
        self,
        base_documents: List[Document],
        kg_documents: List[Document],
        query: str,
        top_k: int
    ) -> List[Document]:
        """
        融合基础检索和知识图谱扩展的结果
        
        Args:
            base_documents: 基础检索结果
            kg_documents: 知识图谱扩展结果
            query: 原始查询
            top_k: 最终返回数量
            
        Returns:
            融合后的文档列表
        """
        # 创建文档ID到文档的映射，避免重复
        doc_map = {}
        
        # 添加基础检索结果
        for doc in base_documents:
            doc_map[doc.id] = doc
        
        # 添加知识图谱扩展结果
        for doc in kg_documents:
            if doc.id not in doc_map:
                doc_map[doc.id] = doc
            else:
                # 如果文档已存在，提升其分数
                existing_doc = doc_map[doc.id]
                existing_doc.score = min(1.0, existing_doc.score + self.kg_weight * 0.5)
        
        # 按分数排序
        sorted_documents = sorted(
            doc_map.values(),
            key=lambda d: d.score,
            reverse=True
        )
        
        return sorted_documents[:top_k]
    
    async def close(self) -> None:
        """关闭检索器"""
        await super().close()
        await self.kg_service.close()
        logger.info("Knowledge Graph Enhanced Retriever closed") 