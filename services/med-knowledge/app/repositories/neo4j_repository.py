from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.core.config import DatabaseSettings
from app.core.logger import get_logger
from app.models.entities import (
    Constitution,
    ConstitutionListResponse,
    Recommendation,
    RecommendationListResponse,
    SearchResponse,
    SearchResult,
)

logger = get_logger()


class Neo4jRepository:
    """Neo4j图数据库存储库"""

    def __init__(self, driver: AsyncDriver):
        """初始化Neo4j连接"""
        self.driver = driver
        self.database = "neo4j"  # 默认数据库名



    async def close(self):
        """关闭数据库连接"""
        if self.driver is not None:
            await self.driver.close()
            logger.info("Neo4j数据库连接已关闭")

    async def _execute_query(self, query, params=None, database=None):
        """执行Cypher查询"""
        if self.driver is None:
            raise RuntimeError("数据库连接未初始化")

        db = database or self.database
        async with self.driver.session(database=db) as session:
            try:
                result = await session.run(query, params or {})
                records = await result.values()
                return records
            except Neo4jError as e:
                logger.error(f"查询执行失败: {e}")
                raise

    async def _execute_single_result_query(self, query, params=None, database=None):
        """执行返回单个结果的查询"""
        records = await self._execute_query(query, params, database)
        return records[0][0] if records and records[0] else None

    async def get_node_count(self) -> int:
        """获取知识图谱节点数量"""
        query = "MATCH (n) RETURN count(n) as count"
        return await self._execute_single_result_query(query)

    async def get_relationship_count(self) -> int:
        """获取知识图谱关系数量"""
        query = "MATCH ()-[r]->() RETURN count(r) as count"
        return await self._execute_single_result_query(query)

    async def get_node_type_statistics(self) -> dict[str, int]:
        """获取各类型节点的数量统计"""
        query = """
        MATCH (n)
        WITH labels(n)[0] AS nodeType, count(n) AS count
        RETURN nodeType, count
        ORDER BY count DESC
        """
        records = await self._execute_query(query)
        return {record[0]: record[1] for record in records}

    async def get_relationship_type_statistics(self) -> dict[str, int]:
        """获取各类型关系的数量统计"""
        query = """
        MATCH ()-[r]->()
        WITH type(r) AS relType, count(r) AS count
        RETURN relType, count
        ORDER BY count DESC
        """
        records = await self._execute_query(query)
        return {record[0]: record[1] for record in records}

    async def get_constitution_by_id(self, constitution_id: str) -> Constitution | None:
        """根据ID获取体质信息"""
        query = """
        MATCH (c:Constitution {id: $id})
        RETURN c
        """
        record = await self._execute_single_result_query(query, {"id": constitution_id})
        if not record:
            return None

        # 转换为模型对象
        props = dict(record)
        return Constitution(
            id=props["id"],
            name=props["name"],
            description=props["description"],
            characteristics=props.get("characteristics", []),
            symptoms=props.get("symptoms", []),
            preventions=props.get("preventions", []),
            food_recommendations=props.get("food_recommendations", []),
            food_avoidances=props.get("food_avoidances", []),
            prevalence=props.get("prevalence", 0.0),
            biomarker_correlations=props.get("biomarker_correlations", []),
            western_medicine_correlations=props.get("western_medicine_correlations", []),
            created_at=props.get("created_at"),
            updated_at=props.get("updated_at"),
        )

    async def get_constitutions(self, limit: int, offset: int) -> ConstitutionListResponse:
        """获取所有体质信息"""
        # 获取总数
        count_query = "MATCH (c:Constitution) RETURN count(c) as count"
        total = await self._execute_single_result_query(count_query)

        # 分页查询
        query = """
        MATCH (c:Constitution)
        RETURN c
        ORDER BY c.name
        SKIP $skip
        LIMIT $limit
        """
        records = await self._execute_query(query, {"skip": offset, "limit": limit})

        # 转换结果
        constitutions = []
        for record in records:
            props = dict(record[0])
            constitutions.append(
                Constitution(
                    id=props["id"],
                    name=props["name"],
                    description=props["description"],
                    characteristics=props.get("characteristics", []),
                    symptoms=props.get("symptoms", []),
                    preventions=props.get("preventions", []),
                    food_recommendations=props.get("food_recommendations", []),
                    food_avoidances=props.get("food_avoidances", []),
                    prevalence=props.get("prevalence", 0.0),
                    biomarker_correlations=props.get("biomarker_correlations", []),
                    western_medicine_correlations=props.get("western_medicine_correlations", []),
                    created_at=props.get("created_at"),
                    updated_at=props.get("updated_at"),
                )
            )

        return ConstitutionListResponse(data=constitutions, total=total, limit=limit, offset=offset)

    async def search_knowledge(
        self, query: str, entity_type: str | None, limit: int, offset: int
    ) -> SearchResponse:
        """搜索知识库"""
        where_clause = "WHERE (n.name CONTAINS $query OR n.description CONTAINS $query)"
        if entity_type:
            where_clause += f" AND labels(n)[0] = '{entity_type}'"

        # 获取总数
        count_query = f"""
        MATCH (n)
        {where_clause}
        RETURN count(n) as count
        """
        total = await self._execute_single_result_query(count_query, {"query": query})

        # 分页查询
        search_query = f"""
        MATCH (n)
        {where_clause}
        RETURN
            n.id as id,
            n.name as name,
            labels(n)[0] as entity_type,
            CASE
                WHEN n.description IS NOT NULL THEN substring(n.description, 0, 100)
                ELSE ''
            END as brief,
            CASE
                WHEN n.name CONTAINS $query THEN 1.0
                ELSE 0.8
            END as relevance_score
        ORDER BY relevance_score DESC, name
        SKIP $skip
        LIMIT $limit
        """
        records = await self._execute_query(
            search_query, {"query": query, "skip": offset, "limit": limit}
        )

        # 转换结果
        results = []
        for record in records:
            results.append(
                SearchResult(
                    id=record[0],
                    name=record[1],
                    entity_type=record[2],
                    brief=record[3],
                    relevance_score=record[4],
                )
            )

        return SearchResponse(data=results, total=total, limit=limit, offset=offset)

    async def get_recommendations_by_constitution(
        self, constitution_id: str, types: list[str] | None = None
    ) -> RecommendationListResponse:
        """根据体质获取推荐"""
        where_clause = ""
        if types and len(types) > 0:
            type_list = ", ".join([f"'{t}'" for t in types])
            where_clause = f"WHERE r.type IN [{type_list}]"

        query = f"""
        MATCH (c:Constitution {{id: $id}})-[:HAS_RECOMMENDATION]->(r:Recommendation)
        {where_clause}
        RETURN r
        ORDER BY r.relevance_score DESC
        """

        records = await self._execute_query(query, {"id": constitution_id})

        recommendations = []
        for record in records:
            props = dict(record[0])
            recommendations.append(
                Recommendation(
                    id=props["id"],
                    type=props["type"],
                    title=props["title"],
                    description=props["description"],
                    relevance_score=props["relevance_score"],
                    evidence=props.get("evidence", ""),
                    evidence_level=props.get("evidence_level", ""),
                    western_medicine_rationale=props.get("western_medicine_rationale", ""),
                    tcm_rationale=props.get("tcm_rationale", ""),
                    created_at=props.get("created_at"),
                    updated_at=props.get("updated_at"),
                )
            )

        return RecommendationListResponse(data=recommendations, total=len(recommendations))

    async def execute_cypher(self, cypher: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        """执行Cypher查询"""
        records = await self._execute_query(cypher, params)

        # 转换结果为字典列表
        result = []
        if records and len(records) > 0:
            keys = records[0].keys()
            for record in records:
                result_dict = {}
                for i, key in enumerate(keys):
                    result_dict[key] = record[i]
                result.append(result_dict)

        return result

    # 添加更多实现方法...
    # 例如 get_symptom_by_id, get_symptoms, get_acupoint_by_id, get_acupoints 等

    # 知识图谱方法
    async def get_visualization_data(
        self, limit: int, relationships: list[str] | None = None
    ) -> dict[str, Any]:
        """获取知识图谱可视化数据"""
        rel_clause = ""
        if relationships and len(relationships) > 0:
            rel_types = "|".join(relationships)
            rel_clause = f":[{rel_types}]"

        query = f"""
        MATCH (n)-[r{rel_clause}]->(m)
        RETURN n, r, m
        LIMIT $limit
        """

        records = await self._execute_query(query, {"limit": limit})

        # 处理结果为可视化数据格式
        nodes = {}
        edges = []

        for record in records:
            source_node = dict(record[0])
            relationship = record[1]
            target_node = dict(record[2])

            # 添加节点
            if source_node["id"] not in nodes:
                nodes[source_node["id"]] = {
                    "id": source_node["id"],
                    "label": next(iter(source_node.labels)),
                    "name": source_node.get("name", ""),
                }

            if target_node["id"] not in nodes:
                nodes[target_node["id"]] = {
                    "id": target_node["id"],
                    "label": next(iter(target_node.labels)),
                    "name": target_node.get("name", ""),
                }

            # 添加边
            edges.append(
                {
                    "source": source_node["id"],
                    "target": target_node["id"],
                    "type": type(relationship).__name__,
                }
            )

        return {"nodes": list(nodes.values()), "edges": edges}

    async def get_node_types_count(self) -> list[dict[str, Any]]:
        """获取节点类型统计（返回列表格式）"""
        stats = await self.get_node_type_statistics()
        return [{"type": k, "count": v} for k, v in stats.items()]

    async def get_relationship_types_count(self) -> list[dict[str, Any]]:
        """获取关系类型统计（返回列表格式）"""
        stats = await self.get_relationship_type_statistics()
        return [{"type": k, "count": v} for k, v in stats.items()]

    async def get_graph_visualization_data(
        self, limit: int, node_types: list[str] | None = None, relationship_types: list[str] | None = None
    ) -> dict[str, Any]:
        """获取图谱可视化数据"""
        return await self.get_visualization_data(limit, relationship_types)

    async def find_path_between_nodes(
        self, start_node_id: str, end_node_id: str, max_depth: int = 4
    ) -> dict[str, Any]:
        """查找两个节点之间的路径"""
        query = f"""
        MATCH path = shortestPath((start {{id: $start_id}})-[*1..{max_depth}]-(end {{id: $end_id}}))
        RETURN path
        LIMIT 10
        """
        
        try:
            records = await self._execute_query(query, {"start_id": start_node_id, "end_id": end_node_id})
            paths = []
            for record in records:
                path_data = []
                path = record[0]
                for i, node in enumerate(path.nodes):
                    path_data.append({
                        "id": node["id"],
                        "type": list(node.labels)[0],
                        "name": node.get("name", "")
                    })
                    if i < len(path.relationships):
                        rel = path.relationships[i]
                        path_data.append({
                            "relationship": rel.type,
                            "direction": "outgoing"
                        })
                paths.append(path_data)
            return {"paths": paths}
        except Exception as e:
            logger.error(f"查找路径失败: {e}")
            return {"paths": []}

    async def get_node_relationships(
        self, node_id: str, direction: str = "both", relationship_types: list[str] | None = None, limit: int = 20
    ) -> dict[str, Any]:
        """获取节点关系"""
        rel_clause = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_clause = f":[{rel_types}]"

        if direction == "outgoing":
            pattern = f"(n)-[r{rel_clause}]->(m)"
        elif direction == "incoming":
            pattern = f"(n)<-[r{rel_clause}]-(m)"
        else:  # both
            pattern = f"(n)-[r{rel_clause}]-(m)"

        query = f"""
        MATCH {pattern}
        WHERE n.id = $node_id
        RETURN n, r, m
        LIMIT $limit
        """

        try:
            records = await self._execute_query(query, {"node_id": node_id, "limit": limit})
            relationships = []
            central_node = None

            for record in records:
                source_node = dict(record[0])
                relationship = record[1]
                target_node = dict(record[2])

                if central_node is None:
                    central_node = {
                        "id": source_node["id"],
                        "type": list(source_node.labels)[0],
                        "name": source_node.get("name", "")
                    }

                relationships.append({
                    "source": {
                        "id": source_node["id"],
                        "type": list(source_node.labels)[0],
                        "name": source_node.get("name", "")
                    },
                    "relationship": relationship.type,
                    "target": {
                        "id": target_node["id"],
                        "type": list(target_node.labels)[0],
                        "name": target_node.get("name", "")
                    }
                })

            return {"central_node": central_node, "related_nodes": relationships}
        except Exception as e:
            logger.error(f"获取节点关系失败: {e}")
            return {"central_node": None, "related_nodes": []}

    async def execute_cypher_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """执行Cypher查询"""
        return await self.execute_cypher(query, params or {})

    async def get_knowledge_subgraph(
        self, central_entity_type: str, central_entity_id: str, depth: int = 2, max_nodes: int = 50
    ) -> dict[str, Any]:
        """获取知识子图"""
        query = f"""
        MATCH (center:{central_entity_type} {{id: $entity_id}})
        CALL apoc.path.subgraphNodes(center, {{
            maxLevel: $depth,
            limit: $max_nodes
        }}) YIELD node
        MATCH (node)-[r]-(connected)
        WHERE connected IN apoc.path.subgraphNodes(center, {{maxLevel: $depth, limit: $max_nodes}})
        RETURN node, r, connected
        """

        try:
            records = await self._execute_query(query, {
                "entity_id": central_entity_id,
                "depth": depth,
                "max_nodes": max_nodes
            })
            return self._process_graph_data(records)
        except Exception as e:
            # 如果APOC不可用，使用简单查询
            logger.warning(f"APOC查询失败，使用简单查询: {e}")
            simple_query = f"""
            MATCH (center:{central_entity_type} {{id: $entity_id}})
            MATCH (center)-[r*1..{depth}]-(node)
            RETURN center, r, node
            LIMIT $max_nodes
            """
            records = await self._execute_query(simple_query, {
                "entity_id": central_entity_id,
                "max_nodes": max_nodes
            })
            return self._process_graph_data(records)

    async def get_entity_neighbors(
        self, entity_type: str, entity_id: str, neighbor_types: list[str] | None = None
    ) -> dict[str, Any]:
        """获取实体邻居"""
        type_clause = ""
        if neighbor_types:
            type_labels = "|".join([f":{t}" for t in neighbor_types])
            type_clause = f"WHERE neighbor{type_labels}"

        query = f"""
        MATCH (entity:{entity_type} {{id: $entity_id}})-[r]-(neighbor)
        {type_clause}
        RETURN entity, r, neighbor
        """

        try:
            records = await self._execute_query(query, {"entity_id": entity_id})
            entity = None
            neighbors = []

            for record in records:
                entity_node = dict(record[0])
                relationship = record[1]
                neighbor_node = dict(record[2])

                if entity is None:
                    entity = {
                        "id": entity_node["id"],
                        "type": list(entity_node.labels)[0],
                        "name": entity_node.get("name", "")
                    }

                neighbors.append({
                    "id": neighbor_node["id"],
                    "type": list(neighbor_node.labels)[0],
                    "name": neighbor_node.get("name", ""),
                    "relationship": relationship.type
                })

            return {"entity": entity, "neighbors": neighbors}
        except Exception as e:
            logger.error(f"获取实体邻居失败: {e}")
            return {"entity": None, "neighbors": []}

    async def get_related_entities(
        self, entity_type: str, entity_id: str, target_type: str, relationship_type: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """获取相关实体"""
        rel_clause = ""
        if relationship_type:
            rel_clause = f"[r:{relationship_type}]"
        else:
            rel_clause = "[r]"

        query = f"""
        MATCH (source:{entity_type} {{id: $entity_id}})-{rel_clause}-(target:{target_type})
        RETURN target, r
        LIMIT $limit
        """

        try:
            records = await self._execute_query(query, {"entity_id": entity_id, "limit": limit})
            entities = []

            for record in records:
                target_node = dict(record[0])
                relationship = record[1] if len(record) > 1 else None

                entities.append({
                    "id": target_node["id"],
                    "type": list(target_node.labels)[0],
                    "name": target_node.get("name", ""),
                    "relationship": relationship.type if relationship else None
                })

            return entities
        except Exception as e:
            logger.error(f"获取相关实体失败: {e}")
            return []

    async def get_shortest_path(
        self, source_id: str, target_id: str, relationship_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """获取最短路径"""
        rel_clause = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_clause = f"[:{rel_types}]"

        query = f"""
        MATCH path = shortestPath((source {{id: $source_id}})-{rel_clause}*-(target {{id: $target_id}}))
        RETURN path
        """

        try:
            records = await self._execute_query(query, {"source_id": source_id, "target_id": target_id})
            if not records:
                return []

            path = records[0][0]
            path_data = []
            
            for i, node in enumerate(path.nodes):
                path_data.append({
                    "id": node["id"],
                    "type": list(node.labels)[0],
                    "name": node.get("name", "")
                })
                if i < len(path.relationships):
                    rel = path.relationships[i]
                    path_data.append({
                        "relationship": rel.type,
                        "direction": "outgoing"
                    })

            return path_data
        except Exception as e:
            logger.error(f"获取最短路径失败: {e}")
            return []

    async def get_common_neighbors(
        self, node1_id: str, node2_id: str, relationship_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """获取共同邻居"""
        rel_clause = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_clause = f"[:{rel_types}]"

        query = f"""
        MATCH (node1 {{id: $node1_id}})-{rel_clause}-(common)-{rel_clause}-(node2 {{id: $node2_id}})
        RETURN common, 
               [(node1)-[r1]-(common) | type(r1)] as relationships1,
               [(common)-[r2]-(node2) | type(r2)] as relationships2
        """

        try:
            records = await self._execute_query(query, {"node1_id": node1_id, "node2_id": node2_id})
            neighbors = []

            for record in records:
                common_node = dict(record[0])
                rel1_types = record[1]
                rel2_types = record[2]

                neighbors.append({
                    "id": common_node["id"],
                    "type": list(common_node.labels)[0],
                    "name": common_node.get("name", ""),
                    "relationships": list(set(rel1_types + rel2_types))
                })

            return neighbors
        except Exception as e:
            logger.error(f"获取共同邻居失败: {e}")
            return []

    def _process_graph_data(self, records) -> dict[str, Any]:
        """处理图数据为标准格式"""
        nodes = {}
        links = []

        for record in records:
            if len(record) >= 3:
                source_node = dict(record[0])
                relationship = record[1]
                target_node = dict(record[2])

                # 添加节点
                if source_node["id"] not in nodes:
                    nodes[source_node["id"]] = {
                        "id": source_node["id"],
                        "label": list(source_node.labels)[0],
                        "name": source_node.get("name", "")
                    }

                if target_node["id"] not in nodes:
                    nodes[target_node["id"]] = {
                        "id": target_node["id"],
                        "label": list(target_node.labels)[0],
                        "name": target_node.get("name", "")
                    }

                # 添加链接
                links.append({
                    "source": source_node["id"],
                    "target": target_node["id"],
                    "type": relationship.type if hasattr(relationship, 'type') else str(relationship)
                })

        return {"nodes": list(nodes.values()), "links": links}

    async def verify_connectivity(self):
        """验证数据库连接"""
        try:
            await self.get_node_count()
            logger.info("Neo4j数据库连接验证成功")
        except Exception as e:
            logger.error(f"Neo4j数据库连接验证失败: {e}")
            raise
