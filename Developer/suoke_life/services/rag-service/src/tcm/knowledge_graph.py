from typing import List, Dict, Any, Optional
from loguru import logger
from neo4j import GraphDatabase
from dataclasses import dataclass
from enum import Enum

class TCMEntityType(Enum):
    """中医实体类型"""
    SYNDROME = "证候"  # 证候
    SYMPTOM = "症状"   # 症状
    HERB = "中药"     # 中药
    FORMULA = "方剂"   # 方剂
    MERIDIAN = "经络"  # 经络
    DISEASE = "疾病"   # 疾病
    CONSTITUTION = "体质"  # 体质
    TREATMENT = "治法"    # 治法

@dataclass
class TCMEntity:
    """中医实体"""
    id: str
    name: str
    type: TCMEntityType
    attributes: Dict[str, Any]
    
@dataclass
class TCMRelation:
    """中医关系"""
    source_id: str
    target_id: str
    type: str
    attributes: Dict[str, Any]

class TCMKnowledgeGraph:
    def __init__(self, uri: str, user: str, password: str):
        """初始化中医知识图谱"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
        
    def create_entity(self, entity: TCMEntity) -> bool:
        """创建中医实体"""
        try:
            with self.driver.session() as session:
                query = (
                    "CREATE (n:%s {id: $id, name: $name}) "
                    "SET n += $attributes "
                    "RETURN n"
                ) % entity.type.value
                
                result = session.run(
                    query,
                    id=entity.id,
                    name=entity.name,
                    attributes=entity.attributes
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating entity: {e}")
            return False
            
    def create_relation(self, relation: TCMRelation) -> bool:
        """创建实体关系"""
        try:
            with self.driver.session() as session:
                query = (
                    "MATCH (a), (b) "
                    "WHERE a.id = $source_id AND b.id = $target_id "
                    "CREATE (a)-[r:%s]->(b) "
                    "SET r += $attributes "
                    "RETURN r"
                ) % relation.type
                
                result = session.run(
                    query,
                    source_id=relation.source_id,
                    target_id=relation.target_id,
                    attributes=relation.attributes
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating relation: {e}")
            return False
            
    def get_entity_by_id(self, entity_id: str) -> Optional[TCMEntity]:
        """根据ID获取实体"""
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (n {id: $id}) RETURN n",
                    id=entity_id
                )
                record = result.single()
                if record:
                    node = record["n"]
                    return TCMEntity(
                        id=node["id"],
                        name=node["name"],
                        type=TCMEntityType(node.labels.pop()),
                        attributes={k: v for k, v in node.items() 
                                  if k not in ["id", "name"]}
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting entity: {e}")
            return None
            
    def get_related_entities(
        self,
        entity_id: str,
        relation_type: Optional[str] = None,
        entity_type: Optional[TCMEntityType] = None
    ) -> List[Dict[str, Any]]:
        """获取相关实体"""
        try:
            with self.driver.session() as session:
                # 构建查询条件
                relation_filter = f"type(r) = '{relation_type}'" if relation_type else ""
                entity_filter = f"b:{entity_type.value}" if entity_type else ""
                filters = " AND ".join(filter(None, [relation_filter, entity_filter]))
                where_clause = f"WHERE {filters}" if filters else ""
                
                query = f"""
                MATCH (a {{id: $id}})-[r]->(b)
                {where_clause}
                RETURN b, type(r) as relation_type, r as relation_attrs
                """
                
                result = session.run(query, id=entity_id)
                return [
                    {
                        "entity": TCMEntity(
                            id=record["b"]["id"],
                            name=record["b"]["name"],
                            type=TCMEntityType(list(record["b"].labels)[0]),
                            attributes={k: v for k, v in record["b"].items() 
                                      if k not in ["id", "name"]}
                        ),
                        "relation_type": record["relation_type"],
                        "relation_attributes": dict(record["relation_attrs"])
                    }
                    for record in result
                ]
        except Exception as e:
            logger.error(f"Error getting related entities: {e}")
            return []
            
    def search_entities(
        self,
        keyword: str,
        entity_type: Optional[TCMEntityType] = None
    ) -> List[TCMEntity]:
        """搜索实体"""
        try:
            with self.driver.session() as session:
                type_filter = f":{entity_type.value}" if entity_type else ""
                query = f"""
                MATCH (n{type_filter})
                WHERE n.name CONTAINS $keyword
                RETURN n
                """
                
                result = session.run(query, keyword=keyword)
                return [
                    TCMEntity(
                        id=record["n"]["id"],
                        name=record["n"]["name"],
                        type=TCMEntityType(list(record["n"].labels)[0]),
                        attributes={k: v for k, v in record["n"].items() 
                                  if k not in ["id", "name"]}
                    )
                    for record in result
                ]
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []
            
    def get_shortest_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """获取最短路径"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH path = shortestPath((a {id: $source_id})-[*..%d]->(b {id: $target_id}))
                RETURN path
                """ % max_depth
                
                result = session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id
                )
                
                record = result.single()
                if not record:
                    return []
                    
                path = record["path"]
                return [
                    {
                        "entity": TCMEntity(
                            id=node["id"],
                            name=node["name"],
                            type=TCMEntityType(list(node.labels)[0]),
                            attributes={k: v for k, v in node.items() 
                                      if k not in ["id", "name"]}
                        ),
                        "relation": {
                            "type": rel.type,
                            "attributes": dict(rel)
                        } if i < len(path.relationships) else None
                    }
                    for i, node in enumerate(path.nodes)
                ]
        except Exception as e:
            logger.error(f"Error getting shortest path: {e}")
            return []
            
    def get_subgraph(
        self,
        entity_id: str,
        depth: int = 2,
        relation_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取子图"""
        try:
            with self.driver.session() as session:
                relation_filter = (
                    f"ALL(r IN relationships(path) WHERE type(r) IN {relation_types})"
                    if relation_types else ""
                )
                where_clause = f"WHERE {relation_filter}" if relation_filter else ""
                
                query = f"""
                MATCH path = (n {{id: $id}})-[*..{depth}]-(m)
                {where_clause}
                RETURN path
                """
                
                result = session.run(query, id=entity_id)
                
                nodes = set()
                relationships = set()
                
                for record in result:
                    path = record["path"]
                    for node in path.nodes:
                        nodes.add((
                            node["id"],
                            node["name"],
                            list(node.labels)[0],
                            frozenset(
                                (k, v) for k, v in node.items()
                                if k not in ["id", "name"]
                            )
                        ))
                        
                    for rel in path.relationships:
                        relationships.add((
                            rel.start_node["id"],
                            rel.end_node["id"],
                            rel.type,
                            frozenset(dict(rel).items())
                        ))
                        
                return {
                    "nodes": [
                        TCMEntity(
                            id=id,
                            name=name,
                            type=TCMEntityType(type),
                            attributes=dict(attrs)
                        )
                        for id, name, type, attrs in nodes
                    ],
                    "relationships": [
                        TCMRelation(
                            source_id=source,
                            target_id=target,
                            type=type,
                            attributes=dict(attrs)
                        )
                        for source, target, type, attrs in relationships
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting subgraph: {e}")
            return {"nodes": [], "relationships": []} 