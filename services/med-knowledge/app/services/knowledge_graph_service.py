from typing import Dict, List, Optional, Any

from app.core.logger import get_logger
from app.repositories.neo4j_repository import Neo4jRepository

logger = get_logger()


class KnowledgeGraphService:
    """知识图谱服务"""
    
    def __init__(self, repository: Neo4jRepository):
        self.repository = repository

    async def get_graph_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        try:
            node_count = await self.repository.get_node_count()
            relationship_count = await self.repository.get_relationship_count()
            
            # 获取各节点类型统计
            node_types = await self.repository.get_node_types_count()
            
            # 获取各关系类型统计
            relationship_types = await self.repository.get_relationship_types_count()
            
            return {
                "node_count": node_count,
                "relationship_count": relationship_count,
                "node_types": node_types,
                "relationship_types": relationship_types
            }
        except Exception as e:
            logger.error(f"获取知识图谱统计信息失败: {e}")
            return {
                "node_count": 0,
                "relationship_count": 0,
                "node_types": [],
                "relationship_types": []
            }

    async def get_graph_visualization_data(
        self, 
        limit: int = 100, 
        node_types: Optional[List[str]] = None,
        relationship_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取知识图谱可视化数据"""
        try:
            return await self.repository.get_graph_visualization_data(
                limit, node_types, relationship_types
            )
        except Exception as e:
            logger.error(f"获取知识图谱可视化数据失败: {e}")
            return {"nodes": [], "links": []}

    async def find_path_between_nodes(
        self, 
        start_node_id: str, 
        end_node_id: str,
        max_depth: int = 4
    ) -> Dict[str, Any]:
        """查找两个节点之间的路径"""
        try:
            return await self.repository.find_path_between_nodes(
                start_node_id, end_node_id, max_depth
            )
        except Exception as e:
            logger.error(f"查找节点间路径失败: {e}")
            return {"paths": []}

    async def get_node_relationships(
        self, 
        node_id: str, 
        direction: str = "both",
        relationship_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """获取节点的关系"""
        try:
            return await self.repository.get_node_relationships(
                node_id, direction, relationship_types, limit
            )
        except Exception as e:
            logger.error(f"获取节点关系失败: {e}")
            return {"central_node": None, "related_nodes": []}

    async def execute_cypher_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行Cypher查询（高级用户）"""
        try:
            if params is None:
                params = {}
            return await self.repository.execute_cypher_query(query, params)
        except Exception as e:
            logger.error(f"执行Cypher查询失败: {e}")
            return []

    async def get_knowledge_subgraph(
        self,
        central_entity_type: str,
        central_entity_id: str,
        depth: int = 2,
        max_nodes: int = 50
    ) -> Dict[str, Any]:
        """获取以特定实体为中心的知识子图"""
        try:
            return await self.repository.get_knowledge_subgraph(
                central_entity_type, central_entity_id, depth, max_nodes
            )
        except Exception as e:
            logger.error(f"获取知识子图失败: {e}")
            return {"nodes": [], "links": []}

    async def get_entity_neighbors(
        self,
        entity_type: str,
        entity_id: str,
        neighbor_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取实体相邻节点"""
        try:
            return await self.repository.get_entity_neighbors(
                entity_type, entity_id, neighbor_types
            )
        except Exception as e:
            logger.error(f"获取实体相邻节点失败: {e}")
            return {"entity": None, "neighbors": []}
            
    async def get_related_entities(
        self,
        entity_type: str,
        entity_id: str,
        target_type: str,
        relationship_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取相关实体"""
        try:
            return await self.repository.get_related_entities(
                entity_type, entity_id, target_type, relationship_type, limit
            )
        except Exception as e:
            logger.error(f"获取相关实体失败: {e}")
            return [] 