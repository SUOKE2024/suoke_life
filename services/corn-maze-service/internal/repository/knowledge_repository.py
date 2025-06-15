#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识存储库 - 负责中医养生知识的存储和检索
"""

import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Any, Tuple

import aiosqlite

from internal.model.knowledge import KnowledgeNode

logger = logging.getLogger(__name__)

class KnowledgeRepository:
    """知识存储库，负责中医养生知识的存储和检索"""
    
    def __init__(self):
        self.db_path = os.environ.get("MAZE_DB_PATH", "data/maze.db")
        logger.info(f"知识存储库初始化，数据库路径: {self.db_path}")
    
    async def _get_db(self):
        """获取数据库连接"""
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 连接数据库
        db = await aiosqlite.connect(self.db_path)
        db.row_factory = aiosqlite.Row
        
        # 初始化表结构
        await self._init_tables(db)
        
        return db
    
    async def _init_tables(self, db):
        """初始化数据库表"""
        await db.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_nodes (
            node_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty_level TEXT NOT NULL,
            related_tags TEXT NOT NULL,
            references TEXT,
            media_links TEXT
        )
        ''')
        await db.commit()
        
        # 检查初始数据
        await self._check_initial_data(db)
    
    async def _check_initial_data(self, db):
        """检查并加载初始数据"""
        # 检查是否有知识节点数据
        cursor = await db.execute("SELECT COUNT(*) FROM knowledge_nodes")
        count = (await cursor.fetchone())[0]
        
        # 如果没有数据，则加载初始数据
        if count == 0:
            logger.info("知识存储库为空，加载初始数据")
            await self._load_initial_data(db)
    
    async def _load_initial_data(self, db):
        """加载初始知识数据"""
        # 初始知识节点数据
        initial_nodes = [
            {
                "node_id": str(uuid.uuid4()),
                "title": "春季养肝护肝",
                "content": "春季养肝护肝的关键在于顺应阳气生发的特点，饮食上宜选择辛甘微温之品，如韭菜、香椿、荠菜等春季时蔬。避免过食酸味和油腻食物，保持情绪舒畅，避免暴怒伤肝。",
                "category": "四季养生",
                "difficulty_level": "1",
                "related_tags": ["春季", "肝脏", "饮食"]
            },
            {
                "node_id": str(uuid.uuid4()),
                "title": "夏季养心祛暑",
                "content": "夏季养心祛暑应以清淡饮食为主，多食用具有清热解暑作用的食物，如绿豆、莲子、西瓜等。注意避免过度贪凉，保持充足睡眠，避免暴躁情绪。",
                "category": "四季养生",
                "difficulty_level": "1",
                "related_tags": ["夏季", "心脏", "祛暑"]
            },
            {
                "node_id": str(uuid.uuid4()),
                "title": "金木相生相克",
                "content": "五行中，木生火，火生土，土生金，金生水，水生木，这是相生关系。木克土，土克水，水克火，火克金，金克木，这是相克关系。在中医理论中，五行对应五脏：肝属木，心属火，脾属土，肺属金，肾属水。",
                "category": "五行平衡",
                "difficulty_level": "2",
                "related_tags": ["五行", "相生相克", "中医理论"]
            },
            {
                "node_id": str(uuid.uuid4()),
                "title": "任脉调理",
                "content": "任脉为人体奇经八脉之一，是阴脉之海，主要功能是调节阴经气血。任脉起于胞中，下出会阴，沿腹部正中线上行至咽喉。调理任脉可通过按摩关元、中极等穴位，有助于调节生殖系统、增强免疫力。",
                "category": "经络调理",
                "difficulty_level": "3",
                "related_tags": ["任脉", "奇经八脉", "穴位按摩"]
            },
            {
                "node_id": str(uuid.uuid4()),
                "title": "艾灸调和阴阳",
                "content": "艾灸是传统中医外治法，通过燃烧艾条产生的热力和药力，作用于穴位，达到调和阴阳、扶正祛邪的作用。常用于命门、关元等穴位，可温补肾阳、增强免疫力，适合体质虚寒者使用。",
                "category": "五行平衡",
                "difficulty_level": "2",
                "related_tags": ["艾灸", "阴阳", "外治法"]
            }
        ]
        
        # 插入初始数据
        for node_data in initial_nodes:
            # 转换复杂结构为JSON
            related_tags_json = json.dumps(node_data["related_tags"])
            references_json = json.dumps(node_data.get("references", []))
            media_links_json = json.dumps(node_data.get("media_links", []))
            
            # 插入数据
            await db.execute(
                '''
                INSERT INTO knowledge_nodes (
                    node_id, title, content, category, difficulty_level, 
                    related_tags, references, media_links
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    node_data["node_id"], node_data["title"], node_data["content"],
                    node_data["category"], node_data["difficulty_level"],
                    related_tags_json, references_json, media_links_json
                )
            )
        
        await db.commit()
        logger.info(f"已加载 {len(initial_nodes)} 个初始知识节点")
    
    async def save_knowledge_node(self, node: KnowledgeNode) -> KnowledgeNode:
        """
        保存知识节点
        
        Args:
            node: 知识节点对象
            
        Returns:
            KnowledgeNode: 保存后的知识节点对象
        """
        logger.info(f"保存知识节点 {node.node_id}")
        
        # 如果节点ID为空，生成新ID
        if not node.node_id:
            node.node_id = str(uuid.uuid4())
        
        db = await self._get_db()
        try:
            # 将复杂结构转换为JSON字符串
            related_tags_json = json.dumps(node.related_tags)
            references_json = json.dumps(node.references)
            media_links_json = json.dumps(node.media_links)
            
            # 准备SQL语句
            query = '''
            INSERT OR REPLACE INTO knowledge_nodes (
                node_id, title, content, category, difficulty_level, 
                related_tags, references, media_links
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            # 执行查询
            await db.execute(
                query,
                (
                    node.node_id, node.title, node.content, node.category,
                    node.difficulty_level, related_tags_json, references_json,
                    media_links_json
                )
            )
            await db.commit()
            
            return node
        
        finally:
            await db.close()
    
    async def get_knowledge_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """
        获取知识节点
        
        Args:
            node_id: 知识节点ID
            
        Returns:
            Optional[KnowledgeNode]: 知识节点对象或None（如果未找到）
        """
        logger.info(f"获取知识节点 {node_id}")
        
        db = await self._get_db()
        try:
            # 执行查询
            cursor = await db.execute(
                "SELECT * FROM knowledge_nodes WHERE node_id = ?",
                (node_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                logger.warning(f"未找到ID为 {node_id} 的知识节点")
                return None
            
            # 将行数据转换为KnowledgeNode对象
            return self._row_to_knowledge_node(row)
        
        finally:
            await db.close()
    
    async def get_knowledge_by_category(self, category: str, limit: int = 10) -> List[KnowledgeNode]:
        """
        按类别获取知识节点
        
        Args:
            category: 知识类别（四季养生、五行平衡、经络调理等）
            limit: 返回结果的最大数量
            
        Returns:
            List[KnowledgeNode]: 知识节点对象列表
        """
        logger.info(f"获取类别为 {category} 的知识节点")
        
        db = await self._get_db()
        try:
            # 执行查询
            cursor = await db.execute(
                "SELECT * FROM knowledge_nodes WHERE category = ? LIMIT ?",
                (category, limit)
            )
            rows = await cursor.fetchall()
            
            # 将行数据转换为KnowledgeNode对象列表
            return [self._row_to_knowledge_node(row) for row in rows]
        
        finally:
            await db.close()
    
    async def search_knowledge(self, query_terms: List[str], limit: int = 10) -> List[KnowledgeNode]:
        """
        搜索知识节点
        
        Args:
            query_terms: 搜索关键词列表
            limit: 返回结果的最大数量
            
        Returns:
            List[KnowledgeNode]: 知识节点对象列表
        """
        if not query_terms:
            return []
        
        logger.info(f"搜索知识节点，关键词: {', '.join(query_terms)}")
        
        db = await self._get_db()
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            for term in query_terms:
                term_pattern = f"%{term}%"
                conditions.append("(title LIKE ? OR content LIKE ? OR related_tags LIKE ?)")
                params.extend([term_pattern, term_pattern, term_pattern])
            
            # 构建完整的WHERE子句
            where_clause = " OR ".join(conditions)
            
            # 执行查询
            cursor = await db.execute(
                f"SELECT * FROM knowledge_nodes WHERE {where_clause} LIMIT ?",
                params + [limit]
            )
            rows = await cursor.fetchall()
            
            # 将行数据转换为KnowledgeNode对象列表
            return [self._row_to_knowledge_node(row) for row in rows]
        
        finally:
            await db.close()
    
    async def delete_knowledge_node(self, node_id: str) -> bool:
        """
        删除知识节点
        
        Args:
            node_id: 知识节点ID
            
        Returns:
            bool: 是否成功删除
        """
        logger.info(f"删除知识节点 {node_id}")
        
        db = await self._get_db()
        try:
            # 执行删除
            cursor = await db.execute(
                "DELETE FROM knowledge_nodes WHERE node_id = ?",
                (node_id,)
            )
            await db.commit()
            
            # 检查是否有行被删除
            return cursor.rowcount > 0
        
        finally:
            await db.close()
    
    def _row_to_knowledge_node(self, row: aiosqlite.Row) -> KnowledgeNode:
        """将数据库行转换为KnowledgeNode对象"""
        return KnowledgeNode(
            node_id=row["node_id"],
            title=row["title"],
            content=row["content"],
            category=row["category"],
            difficulty_level=row["difficulty_level"],
            related_tags=json.loads(row["related_tags"]),
            references=json.loads(row["references"]) if row["references"] else [],
            media_links=json.loads(row["media_links"]) if row["media_links"] else []
        )