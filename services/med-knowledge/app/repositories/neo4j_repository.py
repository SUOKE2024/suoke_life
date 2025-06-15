from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import asyncio
import logging

import neo4j
from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.core.config import DatabaseSettings
from app.core.logger import get_logger
from app.models.entities import (Acupoint, AcupointListResponse, Constitution,
                              ConstitutionListResponse, Herb, HerbListResponse,
                              PaginatedResponse, Recommendation,
                              RecommendationListResponse, SearchResponse,
                              SearchResult, Syndrome, SyndromeListResponse,
                              SyndromePathwaysResponse, Symptom,
                              SymptomListResponse, DiagnosisPathway,
                              Biomarker, BiomarkerListResponse, WesternDisease,
                              WesternDiseaseListResponse, PreventionEvidence,
                              PreventionEvidenceListResponse, IntegratedTreatment,
                              IntegratedTreatmentListResponse, LifestyleIntervention,
                              LifestyleInterventionListResponse)

logger = get_logger()


class Neo4jRepository:
    """Neo4j图数据库存储库"""

    def __init__(self, db_settings: DatabaseSettings):
        """初始化Neo4j连接"""
        self.uri = db_settings.uri
        self.user = db_settings.user
        self.password = db_settings.password
        self.database = db_settings.name
        self.driver: Optional[AsyncDriver] = None
        self._connect()

    def _connect(self):
        """连接到Neo4j数据库"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            logger.info(f"成功连接到Neo4j数据库: {self.uri}")
        except ServiceUnavailable as e:
            logger.error(f"无法连接到Neo4j数据库: {e}")
            raise

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

    async def get_node_type_statistics(self) -> Dict[str, int]:
        """获取各类型节点的数量统计"""
        query = """
        MATCH (n)
        WITH labels(n)[0] AS nodeType, count(n) AS count
        RETURN nodeType, count
        ORDER BY count DESC
        """
        records = await self._execute_query(query)
        return {record[0]: record[1] for record in records}

    async def get_relationship_type_statistics(self) -> Dict[str, int]:
        """获取各类型关系的数量统计"""
        query = """
        MATCH ()-[r]->()
        WITH type(r) AS relType, count(r) AS count
        RETURN relType, count
        ORDER BY count DESC
        """
        records = await self._execute_query(query)
        return {record[0]: record[1] for record in records}

    async def get_constitution_by_id(self, constitution_id: str) -> Optional[Constitution]:
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
            updated_at=props.get("updated_at")
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
            constitutions.append(Constitution(
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
                updated_at=props.get("updated_at")
            ))
        
        return ConstitutionListResponse(
            data=constitutions,
            total=total,
            limit=limit,
            offset=offset
        )

    async def search_knowledge(
        self, query: str, entity_type: Optional[str], limit: int, offset: int
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
            results.append(SearchResult(
                id=record[0],
                name=record[1],
                entity_type=record[2],
                brief=record[3],
                relevance_score=record[4]
            ))
        
        return SearchResponse(
            data=results,
            total=total,
            limit=limit,
            offset=offset
        )

    async def get_recommendations_by_constitution(
        self, constitution_id: str, types: Optional[List[str]] = None
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
            recommendations.append(Recommendation(
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
                updated_at=props.get("updated_at")
            ))
        
        return RecommendationListResponse(
            data=recommendations,
            total=len(recommendations)
        )

    async def execute_cypher(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
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
        self, limit: int, relationships: Optional[List[str]] = None
    ) -> Dict[str, Any]:
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
                    "label": list(source_node.labels)[0],
                    "name": source_node.get("name", "")
                }
            
            if target_node["id"] not in nodes:
                nodes[target_node["id"]] = {
                    "id": target_node["id"],
                    "label": list(target_node.labels)[0],
                    "name": target_node.get("name", "")
                }
            
            # 添加边
            edges.append({
                "source": source_node["id"],
                "target": target_node["id"],
                "type": type(relationship).__name__
            })
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }
    
    # 更多方法实现...