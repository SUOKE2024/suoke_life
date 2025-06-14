"""
knowledge_graph - 索克生活项目模块
"""

import logging
from typing import Any

import networkx as nx
from neo4j import GraphDatabase
from py2neo import Graph

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """中医知识图谱服务"""

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """初始化知识图谱服务

        Args:
            neo4j_uri: Neo4j数据库URI
            neo4j_user: Neo4j用户名
            neo4j_password: Neo4j密码
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password

        # Neo4j客户端
        self._driver = None
        self._py2neo_graph = None

        # 内存图 - 用于快速查询
        self.graph = nx.MultiDiGraph()

        # 实体和关系类型
        self.entity_types = [
            "症候",
            "疾病",
            "方剂",
            "药物",
            "穴位",
            "食材",
            "经络",
            "体质",
            "养生方法",
            "医家",
            "医籍",
            "中医理论",
            "证型",
            "中药方属性",
            "五行",
            "五味",
            "四性",
            "归经",
        ]

        self.relation_types = [
            "治疗",
            "组成",
            "主治",
            "配伍",
            "归经",
            "含有",
            "相关",
            "著作",
            "适宜",
            "禁忌",
            "出处",
            "属于",
            "分类",
            "表现为",
            "具有",
            "来源",
            "可替代",
            "调理",
            "作用于",
            "辩证",
            "所属",
        ]

    def connect(self) -> bool:
        """连接到Neo4j知识图谱数据库

        Returns:
            bool: 连接是否成功
        """
        try:
            # 优化连接配置
            self._driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password),
                max_connection_lifetime=3600,  # 连接最大生存时间1小时
                max_connection_pool_size=50,  # 最大连接池大小
                connection_acquisition_timeout=60,  # 获取连接超时60秒
                connection_timeout=30,  # 连接超时30秒
                max_retry_time=30,  # 最大重试时间30秒
                resolver=None,
                encrypted=False,  # 根据实际环境调整
            )

            # 测试连接
            with self._driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) AS count")
                count = result.single()["count"]
                logger.info(f"已连接到Neo4j知识图谱，包含 {count} 个节点")

            # 构建Py2neo连接（用于复杂查询）
            self._py2neo_graph = Graph(
                self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
            )

            # 加载基本知识图谱到内存
            self._load_base_graph()

            return True
        except Exception as e:
            logger.error(f"连接Neo4j失败: {str(e)}")
            return False

    def close(self) -> None:
        """关闭数据库连接"""
        if self._driver:
            self._driver.close()

    def _load_base_graph(self) -> None:
        """加载基本知识图谱到内存中，用于快速查询"""
        if not self._driver:
            logger.error("未连接到Neo4j，无法加载知识图谱")
            return

        try:
            # 清空现有图
            self.graph.clear()

            # 加载节点
            with self._driver.session() as session:
                # 加载节点
                result = session.run(
                    """
                    MATCH (n)
                    RETURN id(n) AS id, labels(n) AS types, properties(n) AS props
                    LIMIT 10000
                """
                )

                for record in result:
                    node_id = record["id"]
                    node_types = record["types"]
                    node_props = record["props"]

                    # 添加到NetworkX图
                    self.graph.add_node(node_id, types=node_types, **node_props)

                # 加载关系
                result = session.run(
                    """
                    MATCH ()-[r]->()
                    RETURN id(startNode(r)) AS source, id(endNode(r)) AS target,
                        type(r) AS type, properties(r) AS props
                    LIMIT 20000
                """
                )

                for record in result:
                    source = record["source"]
                    target = record["target"]
                    rel_type = record["type"]
                    rel_props = record["props"]

                    # 添加到NetworkX图
                    self.graph.add_edge(source, target, type=rel_type, **rel_props)

            logger.info(
                f"已加载基本知识图谱到内存: {self.graph.number_of_nodes()} 个节点, "
                f"{self.graph.number_of_edges()} 个关系"
            )
        except Exception as e:
            logger.error(f"加载知识图谱失败: {str(e)}")

    def get_entity_by_name(
        self, name: str, entity_type: str | None = None
    ) -> dict | None:
        """根据名称获取实体

        Args:
            name: 实体名称
            entity_type: 实体类型（可选）

        Returns:
            Optional[Dict]: 实体信息
        """
        query_params = {"name": name}

        cypher = """
            MATCH (n {name: $name})
        """

        if entity_type:
            cypher += f" WHERE '{entity_type}' IN labels(n)"

        cypher += """
            RETURN id(n) AS id, labels(n) AS types, properties(n) AS props
            LIMIT 1
        """

        try:
            with self._driver.session() as session:
                result = session.run(cypher, query_params)
                record = result.single()

                if not record:
                    return None

                return {
                    "id": record["id"],
                    "types": record["types"],
                    "properties": record["props"],
                }
        except Exception as e:
            logger.error(f"获取实体失败: {str(e)}")
            return None

    def search_entities(
        self, keyword: str, entity_types: list[str] = None
    ) -> list[dict]:
        """搜索实体

        Args:
            keyword: 搜索关键词
            entity_types: 实体类型列表（可选）

        Returns:
            List[Dict]: 匹配的实体列表
        """
        query_params = {"keyword": f".*{keyword}.*"}

        cypher = """
            MATCH (n)
            WHERE n.name =~ $keyword
        """

        if entity_types and len(entity_types) > 0:
            type_conditions = " OR ".join([f"'{t}' IN labels(n)" for t in entity_types])
            cypher += f" AND ({type_conditions})"

        cypher += """
            RETURN id(n) AS id, labels(n) AS types, properties(n) AS props
            LIMIT 50
        """

        try:
            with self._driver.session() as session:
                result = session.run(cypher, query_params)
                entities = []

                for record in result:
                    entities.append(
                        {
                            "id": record["id"],
                            "types": record["types"],
                            "properties": record["props"],
                        }
                    )

                return entities
        except Exception as e:
            logger.error(f"搜索实体失败: {str(e)}")
            return []

    def get_entity_relations(self, entity_id: int) -> dict[str, list[dict]]:
        """获取实体的关系

        Args:
            entity_id: 实体ID

        Returns:
            Dict[str, List[Dict]]: 按关系类型分组的关系列表
        """
        query_params = {"entity_id": entity_id}

        # 获取出向关系
        outgoing_cypher = """
            MATCH (n)-[r]->(m)
            WHERE id(n) = $entity_id
            RETURN id(n) AS source_id, type(r) AS relation_type,
                properties(r) AS relation_props,
                id(m) AS target_id, labels(m) AS target_types,
                properties(m) AS target_props
            LIMIT 100
        """

        # 获取入向关系
        incoming_cypher = """
            MATCH (n)<-[r]-(m)
            WHERE id(n) = $entity_id
            RETURN id(m) AS source_id, type(r) AS relation_type,
                properties(r) AS relation_props,
                id(n) AS target_id, labels(n) AS target_types,
                properties(n) AS target_props
            LIMIT 100
        """

        try:
            relations = {"outgoing": {}, "incoming": {}}

            with self._driver.session() as session:
                # 处理出向关系
                out_result = session.run(outgoing_cypher, query_params)

                for record in out_result:
                    rel_type = record["relation_type"]

                    if rel_type not in relations["outgoing"]:
                        relations["outgoing"][rel_type] = []

                    relations["outgoing"][rel_type].append(
                        {
                            "source": {
                                "id": record["source_id"],
                                "properties": record.get("source_props", {}),
                            },
                            "target": {
                                "id": record["target_id"],
                                "types": record["target_types"],
                                "properties": record["target_props"],
                            },
                            "properties": record["relation_props"],
                        }
                    )

                # 处理入向关系
                in_result = session.run(incoming_cypher, query_params)

                for record in in_result:
                    rel_type = record["relation_type"]

                    if rel_type not in relations["incoming"]:
                        relations["incoming"][rel_type] = []

                    relations["incoming"][rel_type].append(
                        {
                            "source": {
                                "id": record["source_id"],
                                "types": record[
                                    "target_types"
                                ],  # 这里是入向关系，所以对调了
                                "properties": record.get("source_props", {}),
                            },
                            "target": {
                                "id": record["target_id"],
                                "properties": record["target_props"],
                            },
                            "properties": record["relation_props"],
                        }
                    )

            return relations
        except Exception as e:
            logger.error(f"获取实体关系失败: {str(e)}")
            return {"outgoing": {}, "incoming": {}}

    def get_path_between_entities(
        self, source_id: int, target_id: int, max_depth: int = 3
    ) -> list[dict]:
        """查找两个实体之间的路径

        Args:
            source_id: 起始实体ID
            target_id: 目标实体ID
            max_depth: 最大深度

        Returns:
            List[Dict]: 路径列表
        """

        cypher = f"""
            MATCH p = shortestPath((source)-[*..{max_depth}]-(target))
            WHERE id(source) = $source_id AND id(target) = $target_id
            RETURN p
            LIMIT 5
        """

        try:
            paths = []

            # 这里使用py2neo执行，因为它更容易处理路径
            result = self._py2neo_graph.run(
                cypher, source_id=source_id, target_id=target_id
            )

            for record in result:
                path = record[0]  # 获取路径
                path_data = self._format_path(path)
                paths.append(path_data)

            return paths
        except Exception as e:
            logger.error(f"获取实体间路径失败: {str(e)}")
            return []

    def _format_path(self, path) -> dict:
        """格式化Neo4j路径为字典格式

        Args:
            path: Neo4j路径对象

        Returns:
            Dict: 格式化后的路径
        """
        formatted_path = {"nodes": [], "relationships": []}

        # 处理节点
        for node in path.nodes:
            formatted_node = {
                "id": node.identity,
                "labels": list(node.labels),
                "properties": dict(node),
            }
            formatted_path["nodes"].append(formatted_node)

        # 处理关系
        for rel in path.relationships:
            formatted_rel = {
                "id": rel.identity,
                "type": rel.type,
                "properties": dict(rel),
                "start_node": rel.start_node.identity,
                "end_node": rel.end_node.identity,
            }
            formatted_path["relationships"].append(formatted_rel)

        return formatted_path

    def find_related_knowledge(
        self,
        entity_name: str,
        relation_types: list[str] = None,
        entity_types: list[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """查找与实体相关的知识

        Args:
            entity_name: 实体名称
            relation_types: 关系类型列表（可选）
            entity_types: 实体类型列表（可选）
            limit: 返回数量限制

        Returns:
            List[Dict]: 相关知识列表
        """
        query_params = {"entity_name": entity_name}

        cypher = """
            MATCH (n {name: $entity_name})
        """

        # 构建关系和目标节点类型的约束
        relation_constraint = ""
        if relation_types and len(relation_types) > 0:
            relation_constraint = (
                "WHERE type(r) IN ["
                + ", ".join([f"'{t}'" for t in relation_types])
                + "]"
            )

        entity_constraint = ""
        if entity_types and len(entity_types) > 0:
            type_conditions = " OR ".join([f"'{t}' IN labels(m)" for t in entity_types])
            entity_constraint = f"AND ({type_conditions})"

        cypher += f"""
            MATCH (n)-[r]->(m) {relation_constraint} {entity_constraint}
            RETURN id(n) AS source_id, properties(n) AS source_props, labels(n) AS source_types,
                type(r) AS relation_type, properties(r) AS relation_props,
                id(m) AS target_id, properties(m) AS target_props, labels(m) AS target_types
            LIMIT {limit}
        """

        try:
            with self._driver.session() as session:
                result = session.run(cypher, query_params)
                knowledge_items = []

                for record in result:
                    knowledge_items.append(
                        {
                            "source": {
                                "id": record["source_id"],
                                "types": record["source_types"],
                                "properties": record["source_props"],
                            },
                            "relation": {
                                "type": record["relation_type"],
                                "properties": record["relation_props"],
                            },
                            "target": {
                                "id": record["target_id"],
                                "types": record["target_types"],
                                "properties": record["target_props"],
                            },
                        }
                    )

                return knowledge_items
        except Exception as e:
            logger.error(f"查找相关知识失败: {str(e)}")
            return []

    def create_entity(
        self, name: str, entity_type: str, properties: dict[str, Any] = None
    ) -> int | None:
        """创建实体

        Args:
            name: 实体名称
            entity_type: 实体类型
            properties: 实体属性

        Returns:
            Optional[int]: 创建的实体ID，失败返回None
        """
        if entity_type not in self.entity_types:
            logger.warning(f"未知的实体类型: {entity_type}")

        props = properties or {}
        props["name"] = name

        query_params = {"props": props}

        cypher = f"""
            CREATE (n:{entity_type} $props)
            RETURN id(n) AS id
        """

        try:
            with self._driver.session() as session:
                result = session.run(cypher, query_params)
                record = result.single()
                return record["id"]
        except Exception as e:
            logger.error(f"创建实体失败: {str(e)}")
            return None

    def create_relation(
        self,
        source_id: int,
        target_id: int,
        relation_type: str,
        properties: dict[str, Any] = None,
    ) -> bool:
        """创建关系

        Args:
            source_id: 源实体ID
            target_id: 目标实体ID
            relation_type: 关系类型
            properties: 关系属性

        Returns:
            bool: 是否创建成功
        """
        if relation_type not in self.relation_types:
            logger.warning(f"未知的关系类型: {relation_type}")

        props = properties or {}

        query_params = {"source_id": source_id, "target_id": target_id, "props": props}

        cypher = f"""
            MATCH (source), (target)
            WHERE id(source) = $source_id AND id(target) = $target_id
            CREATE (source)-[r:{relation_type} $props]->(target)
            RETURN id(r) AS id
        """

        try:
            with self._driver.session() as session:
                result = session.run(cypher, query_params)
                return result.single() is not None
        except Exception as e:
            logger.error(f"创建关系失败: {str(e)}")
            return False

    def get_subgraph_by_entity(
        self, entity_name: str, depth: int = 2, max_nodes: int = 100
    ) -> dict:
        """获取以实体为中心的子图

        Args:
            entity_name: 实体名称
            depth: 探索深度
            max_nodes: 最大节点数量

        Returns:
            Dict: 子图数据
        """

        cypher = f"""
            MATCH (center {{name: $entity_name}})
            CALL apoc.path.subgraphNodes(center, {{
                maxLevel: {depth},
                limit: $max_nodes
            }})
            YIELD node
            WITH collect(node) as nodes
            CALL apoc.path.subgraphAll(nodes, {{}})
            YIELD nodes, relationships
            RETURN nodes, relationships
        """

        try:
            subgraph = {"nodes": [], "links": []}

            # 这里使用py2neo执行
            result = self._py2neo_graph.run(
                cypher, entity_name=entity_name, max_nodes=max_nodes
            )

            record = result.data()[0]

            # 处理节点
            for node in record["nodes"]:
                subgraph["nodes"].append(
                    {
                        "id": node.identity,
                        "labels": list(node.labels),
                        "properties": dict(node),
                    }
                )

            # 处理关系
            for rel in record["relationships"]:
                subgraph["links"].append(
                    {
                        "id": rel.identity,
                        "source": rel.start_node.identity,
                        "target": rel.end_node.identity,
                        "type": rel.type,
                        "properties": dict(rel),
                    }
                )

            return subgraph
        except Exception as e:
            logger.error(f"获取子图失败: {str(e)}")
            return {"nodes": [], "links": []}

    def suggest_related_content(
        self, user_interests: list[str], limit: int = 10
    ) -> list[dict]:
        """基于用户兴趣推荐相关内容

        Args:
            user_interests: 用户兴趣列表（实体名称）
            limit: 返回数量限制

        Returns:
            List[Dict]: 推荐内容列表
        """
        if not user_interests:
            return []

        try:
            # 构建查询参数
            interest_params = {
                f"interest_{i}": interest for i, interest in enumerate(user_interests)
            }
            interest_strings = [f"$interest_{i}" for i in range(len(user_interests))]

            # Cypher查询
            cypher = f"""
                MATCH (interest {{name: interest_name}})
                WHERE interest_name IN [{', '.join(interest_strings)}]
                MATCH (interest)-[*1..2]-(related)
                WHERE NOT related.name IN [{', '.join(interest_strings)}]
                WITH related, count(*) AS relevance
                ORDER BY relevance DESC
                LIMIT {limit}
                RETURN id(related) AS id, labels(related) AS types,
                    properties(related) AS props,
                    relevance
            """

            with self._driver.session() as session:
                params = {"interest_name": interest_params}
                result = session.run(cypher, params)

                recommendations = []
                for record in result:
                    recommendations.append(
                        {
                            "id": record["id"],
                            "types": record["types"],
                            "properties": record["props"],
                            "relevance_score": record["relevance"],
                        }
                    )

                return recommendations
        except Exception as e:
            logger.error(f"推荐相关内容失败: {str(e)}")
            return []

    def get_virtual_real_integrated_knowledge(self, concept: str) -> dict[str, Any]:
        """获取虚实融合知识

        为特定概念提供虚拟和现实知识的融合视图

        Args:
            concept: 概念名称

        Returns:
            Dict: 融合知识视图
        """
        try:
            concept_entity = self.get_entity_by_name(concept)
            if not concept_entity:
                return {"concept": concept, "found": False, "message": "未找到相关概念"}

            concept_id = concept_entity["id"]
            entity_type = (
                concept_entity["types"][0] if concept_entity["types"] else "未知"
            )

            # 获取虚拟知识 - 理论关联
            virtual_knowledge = []
            virtual_relations = ["属于", "分类", "相关", "理论基础"]
            virtual_data = self.find_related_knowledge(
                concept, relation_types=virtual_relations, limit=10
            )

            for item in virtual_data:
                virtual_knowledge.append(
                    {
                        "entity": item["target"]["properties"].get("name", "未知"),
                        "relation": item["relation"]["type"],
                        "description": item["relation"]["properties"].get(
                            "description", ""
                        ),
                    }
                )

            # 获取实体知识 - 实践应用
            real_knowledge = []
            real_relations = ["治疗", "组成", "主治", "应用", "调理"]
            real_data = self.find_related_knowledge(
                concept, relation_types=real_relations, limit=10
            )

            for item in real_data:
                real_knowledge.append(
                    {
                        "entity": item["target"]["properties"].get("name", "未知"),
                        "relation": item["relation"]["type"],
                        "description": item["relation"]["properties"].get(
                            "description", ""
                        ),
                    }
                )

            # 获取关联媒体资源
            media_resources = self.get_related_media_resources(concept_id)

            # 返回融合视图
            return {
                "concept": concept,
                "found": True,
                "entity_type": entity_type,
                "properties": concept_entity["properties"],
                "virtual_knowledge": virtual_knowledge,
                "real_knowledge": real_knowledge,
                "media_resources": media_resources,
            }
        except Exception as e:
            logger.error(f"获取虚实融合知识失败: {str(e)}")
            return {
                "concept": concept,
                "found": False,
                "message": f"获取知识时出错: {str(e)}",
            }

    def get_related_media_resources(self, entity_id: int) -> list[dict]:
        """获取实体相关的媒体资源

        Args:
            entity_id: 实体ID

        Returns:
            List[Dict]: 媒体资源列表
        """
        query_params = {"entity_id": entity_id}

        cypher = """
            MATCH (n)-[:HAS_MEDIA]->(m:MediaResource)
            WHERE id(n) = $entity_id
            RETURN id(m) AS id, m.type AS type, m.url AS url,
                m.title AS title, m.description AS description
            LIMIT 20
        """

        try:
            with self._driver.session() as session:
                result = session.run(cypher, query_params)

                media_resources = []
                for record in result:
                    media_resources.append(
                        {
                            "id": record["id"],
                            "type": record["type"],
                            "url": record["url"],
                            "title": record["title"],
                            "description": record["description"],
                        }
                    )

                return media_resources
        except Exception as e:
            logger.error(f"获取媒体资源失败: {str(e)}")
            return []

    def get_knowledge_hierarchy(self, root_concept: str, max_depth: int = 3) -> dict:
        """获取知识层次结构

        Args:
            root_concept: 根概念名称
            max_depth: 最大深度

        Returns:
            Dict: 层次结构树
        """
        query_params = {"root_name": root_concept}

        # 基于层次关系构建树
        cypher = f"""
            MATCH path = (root {{name: $root_name}})-[:包含|属于|分类*1..{max_depth}]->(child)
            WITH root, collect(path) AS paths
            CALL apoc.convert.toTree(paths) AS tree
            RETURN tree
        """

        try:
            with self._driver.session() as session:
                result = session.run(cypher, query_params)

                record = result.single()
                if not record:
                    return {"name": root_concept, "children": []}

                tree = record["tree"]
                return self._format_tree(tree)
        except Exception as e:
            logger.error(f"获取知识层次结构失败: {str(e)}")
            return {"name": root_concept, "children": []}

    def _format_tree(self, tree_data) -> dict:
        """格式化树结构数据

        Args:
            tree_data: Neo4j树结构数据

        Returns:
            Dict: 格式化后的树
        """

        # 递归格式化树
        def format_node(node):
            """格式化单个节点"""
            formatted = {
                "name": node.get("name", "未命名"),
                "id": node.get("_id", -1),
                "type": node.get("type", "未知"),
            }

            children = []
            for rel_type, child_nodes in node.items():
                if rel_type.startswith("_") or rel_type in ["name", "id", "type"]:
                    continue

                if isinstance(child_nodes, list):
                    for child in child_nodes:
                        children.append(format_node(child))

            if children:
                formatted["children"] = children

            return formatted

        return format_node(tree_data)
