#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱接口
==========
提供对Neo4j知识图谱的操作接口
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from neo4j import GraphDatabase
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Node(BaseModel):
    """节点类，表示知识图谱中的节点"""
    id: str
    name: str
    type: str
    properties: Dict[str, Any] = {}
    
    class Config:
        """Pydantic配置"""
        arbitrary_types_allowed = True
        extra = "allow"

class Relation(BaseModel):
    """关系类，表示知识图谱中的关系"""
    start_node: str  # 起始节点ID
    end_node: str    # 终止节点ID
    type: str        # 关系类型
    properties: Dict[str, Any] = {}
    
    class Config:
        """Pydantic配置"""
        arbitrary_types_allowed = True
        extra = "allow"

class KnowledgeGraph:
    """中医知识图谱接口"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        初始化知识图谱接口
        
        Args:
            uri: Neo4j数据库URI
            user: 用户名
            password: 密码
        """
        self.uri = uri
        self.user = user
        self.password = password
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info(f"已连接到Neo4j: {uri}")
        except Exception as e:
            logger.error(f"Neo4j连接失败: {e}")
            self.driver = None
            raise
    
    def add_node(self, node: Node) -> bool:
        """
        添加节点
        
        Args:
            node: 节点对象
            
        Returns:
            bool: 操作是否成功
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return False
            
        try:
            with self.driver.session() as session:
                # 构建属性字典，包含所有基本属性和额外属性
                props = {
                    "id": node.id,
                    "name": node.name,
                    "type": node.type,
                    **node.properties
                }
                
                # 创建节点的Cypher查询
                query = """
                MERGE (n:{label} {id: $id})
                SET n += $props
                RETURN n
                """.format(label=node.type)
                
                result = session.run(query, id=node.id, props=props)
                return result.single() is not None
        except Exception as e:
            logger.error(f"添加节点失败: {e}")
            return False
    
    def add_relation(self, relation: Relation) -> bool:
        """
        添加关系
        
        Args:
            relation: 关系对象
            
        Returns:
            bool: 操作是否成功
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return False
            
        try:
            with self.driver.session() as session:
                # 构建属性字典
                props = relation.properties
                
                # 创建关系的Cypher查询
                query = """
                MATCH (start {id: $start_id})
                MATCH (end {id: $end_id})
                MERGE (start)-[r:{rel_type}]->(end)
                SET r += $props
                RETURN r
                """.format(rel_type=relation.type)
                
                result = session.run(
                    query, 
                    start_id=relation.start_node, 
                    end_id=relation.end_node,
                    props=props
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"添加关系失败: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        获取节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            Optional[Node]: 节点对象，如不存在则返回None
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return None
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (n {id: $id})
                RETURN n
                """
                
                result = session.run(query, id=node_id)
                record = result.single()
                
                if not record:
                    return None
                    
                node_data = record["n"]
                
                # 提取节点属性
                props = dict(node_data)
                node_id = props.pop("id")
                node_name = props.pop("name", "")
                node_type = props.pop("type", list(node_data.labels)[0])
                
                return Node(
                    id=node_id,
                    name=node_name,
                    type=node_type,
                    properties=props
                )
        except Exception as e:
            logger.error(f"获取节点失败: {e}")
            return None
    
    def get_neighbors(self, node_id: str, relation_types: List[str] = None, 
                     max_depth: int = 1) -> List[Dict[str, Any]]:
        """
        获取节点的邻居节点
        
        Args:
            node_id: 中心节点ID
            relation_types: 关系类型列表，None表示所有类型
            max_depth: 最大深度
            
        Returns:
            List[Dict[str, Any]]: 邻居节点和关系列表
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return []
            
        try:
            with self.driver.session() as session:
                # 构建关系类型过滤条件
                rel_filter = ""
                if relation_types:
                    rel_types = "|".join([f":{t}" for t in relation_types])
                    rel_filter = f"[{rel_types}]"
                
                # 构建变长路径查询
                path_pattern = f"-[r{rel_filter}*1..{max_depth}]->"
                
                query = f"""
                MATCH (start {{id: $id}}){path_pattern}(end)
                RETURN r, end
                """
                
                result = session.run(query, id=node_id)
                
                neighbors = []
                for record in result:
                    # 处理关系路径
                    relationships = record["r"]
                    end_node = record["end"]
                    
                    # 提取终点节点属性
                    end_props = dict(end_node)
                    end_id = end_props.pop("id", "")
                    end_name = end_props.pop("name", "")
                    end_type = end_props.pop("type", list(end_node.labels)[0])
                    
                    # 提取关系属性
                    path_info = []
                    for rel in relationships:
                        rel_props = dict(rel)
                        rel_type = type(rel).__name__
                        
                        path_info.append({
                            "type": rel_type,
                            "properties": rel_props
                        })
                    
                    neighbors.append({
                        "node": Node(
                            id=end_id,
                            name=end_name,
                            type=end_type,
                            properties=end_props
                        ),
                        "path": path_info,
                        "depth": len(path_info)
                    })
                
                return neighbors
        except Exception as e:
            logger.error(f"获取邻居节点失败: {e}")
            return []
    
    def search_nodes(self, text: str, node_types: List[str] = None, 
                    limit: int = 10) -> List[Node]:
        """
        搜索节点
        
        Args:
            text: 搜索文本
            node_types: 节点类型列表，None表示所有类型
            limit: 结果数量限制
            
        Returns:
            List[Node]: 节点列表
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return []
            
        try:
            with self.driver.session() as session:
                # 构建节点类型过滤条件
                type_filter = ""
                if node_types:
                    labels = [f":{t}" for t in node_types]
                    type_filter = " OR ".join([f"n{label}" for label in labels])
                    type_filter = f"WHERE {type_filter}"
                
                query = f"""
                MATCH (n)
                {type_filter}
                WHERE n.name CONTAINS $text OR n.id CONTAINS $text
                RETURN n
                LIMIT $limit
                """
                
                result = session.run(query, text=text, limit=limit)
                
                nodes = []
                for record in result:
                    node_data = record["n"]
                    
                    # 提取节点属性
                    props = dict(node_data)
                    node_id = props.pop("id", "")
                    node_name = props.pop("name", "")
                    node_type = props.pop("type", list(node_data.labels)[0])
                    
                    nodes.append(Node(
                        id=node_id,
                        name=node_name,
                        type=node_type,
                        properties=props
                    ))
                
                return nodes
        except Exception as e:
            logger.error(f"搜索节点失败: {e}")
            return []
    
    def update_node(self, node: Node) -> bool:
        """
        更新节点
        
        Args:
            node: 节点对象
            
        Returns:
            bool: 操作是否成功
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return False
            
        try:
            with self.driver.session() as session:
                # 构建属性字典
                props = {
                    "name": node.name,
                    "type": node.type,
                    **node.properties
                }
                
                query = """
                MATCH (n {id: $id})
                SET n += $props
                RETURN n
                """
                
                result = session.run(query, id=node.id, props=props)
                return result.single() is not None
        except Exception as e:
            logger.error(f"更新节点失败: {e}")
            return False
    
    def delete_node(self, node_id: str) -> bool:
        """
        删除节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            bool: 操作是否成功
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return False
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (n {id: $id})
                DETACH DELETE n
                """
                
                result = session.run(query, id=node_id)
                return result.consume().counters.nodes_deleted > 0
        except Exception as e:
            logger.error(f"删除节点失败: {e}")
            return False
    
    def delete_relation(self, relation: Relation) -> bool:
        """
        删除关系
        
        Args:
            relation: 关系对象
            
        Returns:
            bool: 操作是否成功
        """
        if not self.driver:
            logger.error("Neo4j连接未建立")
            return False
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (start {id: $start_id})-[r:{rel_type}]->(end {id: $end_id})
                DELETE r
                """.format(rel_type=relation.type)
                
                result = session.run(
                    query, 
                    start_id=relation.start_node, 
                    end_id=relation.end_node
                )
                return result.consume().counters.relationships_deleted > 0
        except Exception as e:
            logger.error(f"删除关系失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j连接已关闭") 