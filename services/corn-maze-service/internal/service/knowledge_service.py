#!/usr/bin/env python3

"""
知识服务 - 负责管理和检索中医养生知识
"""

import logging
from typing import Any

from internal.model.knowledge import KnowledgeNode
from internal.repository.knowledge_repository import KnowledgeRepository

logger = logging.getLogger(__name__)

class KnowledgeService:
    """知识服务，负责中医养生知识的管理和检索"""

    def __init__(self):
        self.knowledge_repo = KnowledgeRepository()
        logger.info("知识服务初始化完成")

    async def get_knowledge_node(self, node_id: str) -> dict[str, Any] | None:
        """
        获取知识节点
        
        Args:
            node_id: 知识节点ID
            
        Returns:
            Optional[Dict]: 知识节点信息或None（如果未找到）
        """
        logger.info(f"获取知识节点 {node_id}")

        node = await self.knowledge_repo.get_knowledge_node(node_id)

        if not node:
            logger.warning(f"未找到ID为 {node_id} 的知识节点")
            return None

        return node.to_dict()

    async def get_knowledge_by_category(self, category: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        按类别获取知识节点
        
        Args:
            category: 知识类别（四季养生、五行平衡、经络调理等）
            limit: 返回结果的最大数量
            
        Returns:
            List[Dict]: 知识节点列表
        """
        logger.info(f"获取类别为 {category} 的知识节点")

        nodes = await self.knowledge_repo.get_knowledge_by_category(category, limit)

        return [node.to_dict() for node in nodes]

    async def get_knowledge_for_health_profile(self, health_attributes: dict[str, str], limit: int = 5) -> list[dict[str, Any]]:
        """
        根据用户健康属性获取相关知识
        
        Args:
            health_attributes: 用户健康属性（体质、季节、年龄段等）
            limit: 返回结果的最大数量
            
        Returns:
            List[Dict]: 相关知识节点列表
        """
        logger.info("根据健康属性获取知识节点")

        # 从健康属性中提取关键信息
        constitution = health_attributes.get("constitution", "")
        season = health_attributes.get("season", "")
        age_group = health_attributes.get("age_group", "")

        # 构建查询条件
        query_terms = []

        if constitution:
            query_terms.append(constitution)

        if season:
            query_terms.append(season)

        if age_group:
            query_terms.append(age_group)

        # 如果没有有效的查询条件，返回空列表
        if not query_terms:
            logger.warning("没有有效的健康属性，无法获取相关知识")
            return []

        # 查询相关知识
        nodes = await self.knowledge_repo.search_knowledge(query_terms, limit)

        return [node.to_dict() for node in nodes]

    async def create_knowledge_node(self, node_data: dict[str, Any]) -> dict[str, Any]:
        """
        创建新的知识节点
        
        Args:
            node_data: 知识节点数据
            
        Returns:
            Dict: 创建的知识节点
        """
        logger.info(f"创建新的知识节点: {node_data.get('title', '')}")

        # 创建知识节点对象
        node = KnowledgeNode(
            node_id=node_data.get("node_id", ""),
            title=node_data.get("title", ""),
            content=node_data.get("content", ""),
            category=node_data.get("category", ""),
            difficulty_level=node_data.get("difficulty_level", "1"),
            related_tags=node_data.get("related_tags", [])
        )

        # 保存知识节点
        created_node = await self.knowledge_repo.save_knowledge_node(node)

        return created_node.to_dict()
