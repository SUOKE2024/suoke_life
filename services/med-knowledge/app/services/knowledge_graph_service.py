"""
knowledge_graph_service - 索克生活项目模块
"""

from app.core.logger import get_logger
from app.repositories.neo4j_repository import Neo4jRepository
from typing import Any



logger = get_logger()


class KnowledgeGraphService:
    """知识图谱服务"""

    def __init__(self, repository: Neo4jRepository):
        self.repository = repository

    async def get_graph_statistics(self) -> dict[str, Any]:
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
                "relationship_types": relationship_types,
            }
        except Exception as e:
            logger.error(f"获取知识图谱统计信息失败: {e}")
            return {
                "node_count": 0,
                "relationship_count": 0,
                "node_types": [],
                "relationship_types": [],
            }

    async def get_graph_visualization_data(
        self,
        limit: int = 100,
        node_types: list[str] | None = None,
        relationship_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """获取知识图谱可视化数据"""
        try:
            return await self.repository.get_graph_visualization_data(
                limit, node_types, relationship_types
            )
        except Exception as e:
            logger.error(f"获取知识图谱可视化数据失败: {e}")
            return {"nodes": [], "links": []}

    async def find_path_between_nodes(
        self, start_node_id: str, end_node_id: str, max_depth: int = 4
    ) -> dict[str, Any]:
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
        relationship_types: list[str] | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """获取节点的关系"""
        try:
            return await self.repository.get_node_relationships(
                node_id, direction, relationship_types, limit
            )
        except Exception as e:
            logger.error(f"获取节点关系失败: {e}")
            return {"central_node": None, "related_nodes": []}

    async def execute_cypher_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """执行Cypher查询(高级用户)"""
        try:
            if params is None:
                params = {}
            return await self.repository.execute_cypher_query(query, params)
        except Exception as e:
            logger.error(f"执行Cypher查询失败: {e}")
            return []

    async def get_knowledge_subgraph(
        self, central_entity_type: str, central_entity_id: str, depth: int = 2, max_nodes: int = 50
    ) -> dict[str, Any]:
        """获取以特定实体为中心的知识子图"""
        try:
            return await self.repository.get_knowledge_subgraph(
                central_entity_type, central_entity_id, depth, max_nodes
            )
        except Exception as e:
            logger.error(f"获取知识子图失败: {e}")
            return {"nodes": [], "links": []}

    async def get_entity_neighbors(
        self, entity_type: str, entity_id: str, neighbor_types: list[str] | None = None
    ) -> dict[str, Any]:
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
        relationship_type: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """获取相关实体"""
        try:
            return await self.repository.get_related_entities(
                entity_type, entity_id, target_type, relationship_type, limit
            )
        except Exception as e:
            logger.error(f"获取相关实体失败: {e}")
            return []

    # 为测试兼容性添加的方法别名和新方法
    async def get_visualization_data(
        self,
        limit: int = 100,
        relationship_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """获取可视化数据 (测试兼容性别名)"""
        return await self.get_graph_visualization_data(limit, None, relationship_types)

    async def find_paths(
        self, source_id: str, target_id: str, max_depth: int = 4
    ) -> list[list[dict[str, Any]]]:
        """查找路径 (测试兼容性别名)"""
        result = await self.find_path_between_nodes(source_id, target_id, max_depth)
        return result.get("paths", [])

    async def execute_cypher(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """执行Cypher查询 (测试兼容性别名)"""
        return await self.execute_cypher_query(query, params)

    async def get_entity_subgraph(
        self, entity_type: str, entity_id: str, depth: int = 2, relationship_types: list[str] | None = None
    ) -> dict[str, Any]:
        """获取实体子图 (测试兼容性别名)"""
        return await self.get_knowledge_subgraph(entity_type, entity_id, depth, 50)

    async def get_shortest_path(
        self, source_id: str, target_id: str, relationship_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """获取最短路径"""
        try:
            result = await self.repository.get_shortest_path(source_id, target_id, relationship_types)
            return result
        except Exception as e:
            logger.error(f"获取最短路径失败: {e}")
            return []

    async def get_common_neighbors(
        self, node1_id: str, node2_id: str, relationship_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """获取共同邻居"""
        try:
            return await self.repository.get_common_neighbors(node1_id, node2_id, relationship_types)
        except Exception as e:
            logger.error(f"获取共同邻居失败: {e}")
            return []
