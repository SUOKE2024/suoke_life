#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
迷宫存储库 - 负责迷宫数据的存储和检索
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

import aiosqlite

from internal.model.maze import Maze
from pkg.utils.db import DBConnection
from pkg.utils.metrics import record_maze_creation

logger = logging.getLogger(__name__)

class MazeRepository:
    """迷宫存储库，负责迷宫数据的存储和检索"""
    
    def __init__(self):
        self.db_path = os.environ.get("MAZE_DB_PATH", "data/maze.db")
        logger.info(f"迷宫存储库初始化，数据库路径: {self.db_path}")
    
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
    
    async def _init_tables(self, conn):
        """初始化数据库表"""
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS mazes (
            maze_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            maze_type TEXT NOT NULL,
            size_x INTEGER NOT NULL,
            size_y INTEGER NOT NULL,
            cells TEXT NOT NULL,
            start_position TEXT NOT NULL,
            goal_position TEXT NOT NULL,
            knowledge_nodes TEXT NOT NULL,
            challenges TEXT NOT NULL,
            created_at TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            status TEXT NOT NULL,
            is_public BOOLEAN NOT NULL DEFAULT 0,
            description TEXT,
            tags TEXT
        )
        ''')
        
        # 添加索引以提高查询性能
        try:
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_mazes_user_id ON mazes(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_mazes_maze_type ON mazes(maze_type)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_mazes_status ON mazes(status)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_mazes_difficulty ON mazes(difficulty)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_mazes_is_public ON mazes(is_public)')
        except Exception as e:
            logger.warning(f"创建索引失败: {str(e)}")
    
    async def save_maze(self, maze: Maze) -> Maze:
        """
        保存迷宫
        
        Args:
            maze: 迷宫对象
            
        Returns:
            Maze: 保存后的迷宫对象
        """
        logger.info(f"保存迷宫 {maze.maze_id}")
        
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 将复杂结构转换为JSON字符串
            cells_json = json.dumps(maze.cells)
            start_pos_json = json.dumps(maze.start_position)
            goal_pos_json = json.dumps(maze.goal_position)
            knowledge_nodes_json = json.dumps(maze.knowledge_nodes)
            challenges_json = json.dumps(maze.challenges)
            tags_json = json.dumps(maze.tags)
            
            # 准备SQL语句
            query = '''
            INSERT OR REPLACE INTO mazes (
                maze_id, user_id, maze_type, size_x, size_y, cells, 
                start_position, goal_position, knowledge_nodes, challenges, 
                created_at, difficulty, status, is_public, description, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            # 执行查询
            await conn.execute(
                query,
                (
                    maze.maze_id, maze.user_id, maze.maze_type, maze.size_x, maze.size_y,
                    cells_json, start_pos_json, goal_pos_json, knowledge_nodes_json,
                    challenges_json, maze.created_at.isoformat(), maze.difficulty,
                    maze.status, maze.is_public, maze.description, tags_json
                )
            )
            
            # 记录指标
            record_maze_creation(maze.maze_type, maze.difficulty)
            
            return maze
    
    async def get_maze(self, maze_id: str) -> Optional[Maze]:
        """
        获取迷宫
        
        Args:
            maze_id: 迷宫ID
            
        Returns:
            Optional[Maze]: 迷宫对象或None（如果未找到）
        """
        logger.info(f"获取迷宫 {maze_id}")
        
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 执行查询
            async with conn.execute(
                "SELECT * FROM mazes WHERE maze_id = ?",
                (maze_id,)
            ) as cursor:
                row = await cursor.fetchone()
            
            if not row:
                logger.warning(f"未找到ID为 {maze_id} 的迷宫")
                return None
            
            # 将行数据转换为Maze对象
            return self._row_to_maze(row)
    
    async def get_mazes_by_user(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Maze]:
        """
        获取用户的迷宫列表
        
        Args:
            user_id: 用户ID
            limit: 返回结果的最大数量
            offset: 结果偏移量
            
        Returns:
            List[Maze]: 迷宫对象列表
        """
        logger.info(f"获取用户 {user_id} 的迷宫列表")
        
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 执行查询
            async with conn.execute(
                "SELECT * FROM mazes WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset)
            ) as cursor:
                rows = await cursor.fetchall()
            
            # 将行数据转换为Maze对象列表
            return [self._row_to_maze(row) for row in rows]
    
    async def delete_maze(self, maze_id: str) -> bool:
        """
        删除迷宫
        
        Args:
            maze_id: 迷宫ID
            
        Returns:
            bool: 是否成功删除
        """
        logger.info(f"删除迷宫 {maze_id}")
        
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 执行删除
            cursor = await conn.execute(
                "DELETE FROM mazes WHERE maze_id = ?",
                (maze_id,)
            )
            
            # 检查是否有行被删除
            return cursor.rowcount > 0
    
    async def count_active_mazes(self) -> int:
        """
        统计活跃迷宫数量
        
        Returns:
            int: 活跃迷宫数量
        """
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 执行查询
            async with conn.execute(
                "SELECT COUNT(*) FROM mazes WHERE status != 'COMPLETED'"
            ) as cursor:
                row = await cursor.fetchone()
            
            return row[0] if row else 0
    
    async def search_mazes(
        self,
        query: str,
        maze_type: Optional[str] = None,
        difficulty: Optional[int] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[Maze], int]:
        """
        搜索迷宫
        
        Args:
            query: 搜索关键词
            maze_type: 迷宫类型（可选）
            difficulty: 难度级别（可选）
            limit: 返回结果的最大数量
            offset: 结果偏移量
            
        Returns:
            Tuple[List[Maze], int]: 迷宫对象列表和总数
        """
        logger.info(f"搜索迷宫，关键词: {query}")
        
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 构建查询条件
            conditions = ["is_public = 1"]
            params = []
            
            if query:
                conditions.append("(description LIKE ? OR maze_type LIKE ? OR tags LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            if maze_type:
                conditions.append("maze_type = ?")
                params.append(maze_type)
            
            if difficulty:
                conditions.append("difficulty = ?")
                params.append(difficulty)
            
            # 构建完整的WHERE子句
            where_clause = " AND ".join(conditions)
            
            # 执行计数查询
            async with conn.execute(
                f"SELECT COUNT(*) FROM mazes WHERE {where_clause}",
                params
            ) as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0
            
            # 执行搜索查询
            async with conn.execute(
                f"SELECT * FROM mazes WHERE {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ) as cursor:
                rows = await cursor.fetchall()
            
            # 将行数据转换为Maze对象列表
            mazes = [self._row_to_maze(row) for row in rows]
            
            return mazes, total
    
    async def get_maze_types_count(self) -> Dict[str, int]:
        """
        获取各种迷宫类型的数量统计
        
        Returns:
            Dict[str, int]: 迷宫类型数量统计
        """
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 执行查询
            async with conn.execute(
                "SELECT maze_type, COUNT(*) as count FROM mazes GROUP BY maze_type"
            ) as cursor:
                rows = await cursor.fetchall()
            
            # 构建结果字典
            result = {}
            for row in rows:
                result[row['maze_type']] = row['count']
            
            return result
    
    async def clean_old_completed_mazes(self, days_old: int = 30) -> int:
        """
        清理旧的已完成迷宫
        
        Args:
            days_old: 清理多少天前的已完成迷宫
            
        Returns:
            int: 清理的迷宫数量
        """
        logger.info(f"清理 {days_old} 天前的已完成迷宫")
        
        async with DBConnection() as conn:
            # 初始化表结构
            await self._init_tables(conn)
            
            # 计算日期阈值
            threshold_date = (datetime.now() - datetime.timedelta(days=days_old)).isoformat()
            
            # 执行删除
            cursor = await conn.execute(
                "DELETE FROM mazes WHERE status = 'COMPLETED' AND created_at < ?",
                (threshold_date,)
            )
            
            deleted_count = cursor.rowcount
            logger.info(f"已清理 {deleted_count} 个旧的已完成迷宫")
            
            return deleted_count
    
    def _row_to_maze(self, row: aiosqlite.Row) -> Maze:
        """将数据库行转换为Maze对象"""
        return Maze(
            maze_id=row["maze_id"],
            user_id=row["user_id"],
            maze_type=row["maze_type"],
            size_x=row["size_x"],
            size_y=row["size_y"],
            cells=json.loads(row["cells"]),
            start_position=json.loads(row["start_position"]),
            goal_position=json.loads(row["goal_position"]),
            knowledge_nodes=json.loads(row["knowledge_nodes"]),
            challenges=json.loads(row["challenges"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            difficulty=row["difficulty"],
            status=row["status"],
            is_public=bool(row["is_public"]),
            description=row["description"] or "",
            tags=json.loads(row["tags"]) if row["tags"] else []
        )