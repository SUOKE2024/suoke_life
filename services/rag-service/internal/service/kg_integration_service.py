"""
kg_integration_service - 索克生活项目模块
"""

from ..model.document import Document, Metadata
from datetime import datetime
from loguru import logger
from typing import Dict, List, Any, Optional
import aiohttp
import asyncio

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱集成服务，用于同步Neo4j知识图谱数据到RAG系统
"""




class KnowledgeGraphIntegrationService:
    """
    知识图谱集成服务，负责从Med Knowledge服务同步数据到RAG系统
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化知识图谱集成服务
        
        Args:
            config: 配置信息，包含med-knowledge服务地址等
        """
        self.config = config
        self.med_knowledge_base_url = config.get('med_knowledge_service', {}).get(
            'base_url', 'http://med-knowledge-service:8000'
        )
        self.api_version = '/api/v1'
        self.session = None
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """初始化服务"""
        if self.is_initialized:
            return
        
        logger.info("Initializing Knowledge Graph Integration Service")
        self.session = aiohttp.ClientSession()
        self.is_initialized = True
        logger.info("Knowledge Graph Integration Service initialized")
    
    async def close(self) -> None:
        """关闭服务"""
        if self.session:
            await self.session.close()
        self.is_initialized = False
    
    async def _fetch_from_med_knowledge(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        从Med Knowledge服务获取数据
        
        Args:
            endpoint: API端点
            params: 查询参数
            
        Returns:
            响应数据
        """
        url = f"{self.med_knowledge_base_url}{self.api_version}{endpoint}"
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch from {url}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching from Med Knowledge service: {str(e)}")
            return None
    
    async def sync_constitutions(self) -> List[Document]:
        """
        同步体质数据到向量数据库
        
        Returns:
            转换后的文档列表
        """
        logger.info("Syncing constitutions from knowledge graph")
        constitutions = await self._fetch_from_med_knowledge('/constitutions')
        
        if not constitutions:
            return []
        
        documents = []
        for constitution in constitutions:
            # 构建文档内容
            content = self._build_constitution_content(constitution)
            
            # 创建文档对象
            doc = Document(
                id=f"constitution_{constitution['id']}",
                content=content,
                metadata=Metadata(
                    source="med_knowledge_graph",
                    entity_type="constitution",
                    entity_id=constitution['id'],
                    name=constitution['name'],
                    category="中医体质",
                    created_at=datetime.now(),
                    tags=["中医", "体质", constitution['name']]
                )
            )
            documents.append(doc)
        
        logger.info(f"Prepared {len(documents)} constitution documents for syncing")
        return documents
    
    async def sync_syndromes(self) -> List[Document]:
        """
        同步证型数据到向量数据库
        
        Returns:
            转换后的文档列表
        """
        logger.info("Syncing syndromes from knowledge graph")
        syndromes = await self._fetch_from_med_knowledge('/syndromes')
        
        if not syndromes:
            return []
        
        documents = []
        for syndrome in syndromes:
            # 获取相关的诊断路径
            pathways = await self._fetch_from_med_knowledge(f'/syndromes/{syndrome["id"]}/pathways')
            
            # 构建文档内容
            content = self._build_syndrome_content(syndrome, pathways)
            
            # 创建文档对象
            doc = Document(
                id=f"syndrome_{syndrome['id']}",
                content=content,
                metadata=Metadata(
                    source="med_knowledge_graph",
                    entity_type="syndrome",
                    entity_id=syndrome['id'],
                    name=syndrome['name'],
                    category="中医证型",
                    created_at=datetime.now(),
                    tags=["中医", "证型", syndrome['name']]
                )
            )
            documents.append(doc)
        
        logger.info(f"Prepared {len(documents)} syndrome documents for syncing")
        return documents
    
    async def sync_herbs(self) -> List[Document]:
        """
        同步中药数据到向量数据库
        
        Returns:
            转换后的文档列表
        """
        logger.info("Syncing herbs from knowledge graph")
        herbs = await self._fetch_from_med_knowledge('/herbs')
        
        if not herbs:
            return []
        
        documents = []
        for herb in herbs:
            # 构建文档内容
            content = self._build_herb_content(herb)
            
            # 创建文档对象
            doc = Document(
                id=f"herb_{herb['id']}",
                content=content,
                metadata=Metadata(
                    source="med_knowledge_graph",
                    entity_type="herb",
                    entity_id=herb['id'],
                    name=herb['name'],
                    category="中药材",
                    created_at=datetime.now(),
                    tags=["中医", "中药", herb['name']]
                )
            )
            documents.append(doc)
        
        logger.info(f"Prepared {len(documents)} herb documents for syncing")
        return documents
    
    async def sync_acupoints(self) -> List[Document]:
        """
        同步穴位数据到向量数据库
        
        Returns:
            转换后的文档列表
        """
        logger.info("Syncing acupoints from knowledge graph")
        acupoints = await self._fetch_from_med_knowledge('/acupoints')
        
        if not acupoints:
            return []
        
        documents = []
        for acupoint in acupoints:
            # 构建文档内容
            content = self._build_acupoint_content(acupoint)
            
            # 创建文档对象
            doc = Document(
                id=f"acupoint_{acupoint['id']}",
                content=content,
                metadata=Metadata(
                    source="med_knowledge_graph",
                    entity_type="acupoint",
                    entity_id=acupoint['id'],
                    name=acupoint['name'],
                    category="经络穴位",
                    created_at=datetime.now(),
                    tags=["中医", "穴位", acupoint['name']]
                )
            )
            documents.append(doc)
        
        logger.info(f"Prepared {len(documents)} acupoint documents for syncing")
        return documents
    
    async def sync_all_knowledge(self) -> Dict[str, int]:
        """
        同步所有知识图谱数据
        
        Returns:
            各类型同步的文档数量
        """
        logger.info("Starting full knowledge graph sync")
        
        results = {
            "constitutions": 0,
            "syndromes": 0,
            "herbs": 0,
            "acupoints": 0,
            "total": 0
        }
        
        # 并发同步各类数据
        tasks = [
            self.sync_constitutions(),
            self.sync_syndromes(),
            self.sync_herbs(),
            self.sync_acupoints()
        ]
        
        sync_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, result in enumerate(sync_results):
            if isinstance(result, Exception):
                logger.error(f"Error syncing data: {str(result)}")
            else:
                if i == 0:
                    results["constitutions"] = len(result)
                elif i == 1:
                    results["syndromes"] = len(result)
                elif i == 2:
                    results["herbs"] = len(result)
                elif i == 3:
                    results["acupoints"] = len(result)
        
        results["total"] = sum(results.values()) - results["total"]
        logger.info(f"Knowledge graph sync completed: {results}")
        
        return results
    
    def _build_constitution_content(self, constitution: Dict[str, Any]) -> str:
        """构建体质文档内容"""
        content_parts = [
            f"中医体质类型：{constitution['name']}",
            f"描述：{constitution.get('description', '')}",
            f"特征：{constitution.get('characteristics', '')}",
            f"形成原因：{constitution.get('causes', '')}",
            f"易患疾病：{constitution.get('prone_diseases', '')}",
            f"调理方法：{constitution.get('treatment_methods', '')}",
            f"饮食建议：{constitution.get('diet_suggestions', '')}",
            f"生活建议：{constitution.get('lifestyle_suggestions', '')}"
        ]
        
        return "\n".join(filter(lambda x: x.split('：')[1], content_parts))
    
    def _build_syndrome_content(self, syndrome: Dict[str, Any], pathways: List[Dict]) -> str:
        """构建证型文档内容"""
        content_parts = [
            f"中医证型：{syndrome['name']}",
            f"描述：{syndrome.get('description', '')}",
            f"主要症状：{syndrome.get('main_symptoms', '')}",
            f"次要症状：{syndrome.get('secondary_symptoms', '')}",
            f"舌象：{syndrome.get('tongue_appearance', '')}",
            f"脉象：{syndrome.get('pulse_condition', '')}",
            f"病机：{syndrome.get('pathogenesis', '')}",
            f"治法：{syndrome.get('treatment_principle', '')}"
        ]
        
        if pathways:
            content_parts.append("诊断路径：")
            for pathway in pathways:
                content_parts.append(f"  - {pathway.get('description', '')}")
        
        return "\n".join(filter(lambda x: x if '：' not in x else x.split('：')[1], content_parts))
    
    def _build_herb_content(self, herb: Dict[str, Any]) -> str:
        """构建中药文档内容"""
        content_parts = [
            f"中药名称：{herb['name']}",
            f"别名：{herb.get('aliases', '')}",
            f"性味：{herb.get('properties', '')}",
            f"归经：{herb.get('meridians', '')}",
            f"功效：{herb.get('effects', '')}",
            f"主治：{herb.get('indications', '')}",
            f"用法用量：{herb.get('usage', '')}",
            f"注意事项：{herb.get('precautions', '')}"
        ]
        
        return "\n".join(filter(lambda x: x.split('：')[1], content_parts))
    
    def _build_acupoint_content(self, acupoint: Dict[str, Any]) -> str:
        """构建穴位文档内容"""
        content_parts = [
            f"穴位名称：{acupoint['name']}",
            f"经络：{acupoint.get('meridian', '')}",
            f"定位：{acupoint.get('location', '')}",
            f"取穴方法：{acupoint.get('locating_method', '')}",
            f"主治：{acupoint.get('indications', '')}",
            f"操作方法：{acupoint.get('operation_method', '')}",
            f"配伍：{acupoint.get('combinations', '')}",
            f"注意事项：{acupoint.get('precautions', '')}"
        ]
        
        return "\n".join(filter(lambda x: x.split('：')[1], content_parts))
    
    async def get_entity_relationships(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """
        获取实体的关系信息
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            
        Returns:
            关系信息
        """
        endpoint = f'/graph/entities/{entity_type}/{entity_id}/neighbors'
        relationships = await self._fetch_from_med_knowledge(endpoint)
        return relationships or {}
    
    async def get_knowledge_subgraph(self, entity_type: str, entity_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        获取以特定实体为中心的知识子图
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            depth: 子图深度
            
        Returns:
            子图数据
        """
        endpoint = f'/graph/subgraph/{entity_type}/{entity_id}'
        params = {'depth': depth}
        subgraph = await self._fetch_from_med_knowledge(endpoint, params)
        return subgraph or {} 