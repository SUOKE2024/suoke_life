#!/usr/bin/env python3

"""
模板存储库 - 负责迷宫模板的存储和检索
"""

from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any
import uuid

import aiosqlite

from internal.model.template import MazeTemplate

logger = logging.getLogger(__name__)

class TemplateRepository:
    """模板存储库，负责迷宫模板的存储和检索"""

    def __init__(self):
        self.db_path = os.environ.get("MAZE_DB_PATH", "data/maze.db")
        logger.info(f"模板存储库初始化, 数据库路径: {self.db_path}")

    async def _get_db(self):
        """获取数据库连接"""
        # 确保数据库目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # 连接数据库
        db = await aiosqlite.connect(self.db_path)
        db.row_factory = aiosqlite.Row

        # 初始化表结构
        await self._init_tables(db)

        return db

    async def _init_tables(self, db):
        """初始化数据库表"""
        await db.execute('''
        CREATE TABLE IF NOT EXISTS maze_templates (
            template_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            maze_type TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            preview_image_url TEXT NOT NULL,
            size_x INTEGER NOT NULL,
            size_y INTEGER NOT NULL,
            cells TEXT NOT NULL,
            start_position TEXT NOT NULL,
            goal_position TEXT NOT NULL,
            knowledge_node_count INTEGER NOT NULL,
            challenge_count INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            tags TEXT,
            author TEXT,
            is_official BOOLEAN NOT NULL DEFAULT 0
        )
        ''')
        await db.commit()

        # 检查初始数据
        await self._check_initial_templates(db)

    async def _check_initial_templates(self, db):
        """检查并加载初始模板数据"""
        # 检查是否有模板数据
        cursor = await db.execute("SELECT COUNT(*) FROM maze_templates")
        count = (await cursor.fetchone())[0]

        # 如果没有数据, 则加载初始数据
        if count == 0:
            logger.info("模板存储库为空, 加载初始模板")
            await self._load_initial_templates(db)

    async def _load_initial_templates(self, db):
        """加载初始模板数据"""
        now = datetime.now().isoformat()

        # 创建一个简单的5x5迷宫模板
        small_template = {
            "template_id": str(uuid.uuid4()),
            "name": "四季养生小迷宫",
            "description": "一个简单的四季养生主题迷宫, 适合新手探索",
            "maze_type": "四季养生",
            "difficulty": 1,
            "preview_image_url": "/assets/images/templates/seasonal_small.png",
            "size_x": 5,
            "size_y": 5,
            "cells": self._generate_template_cells(5, 5),
            "start_position": {"x": 0, "y": 0},
            "goal_position": {"x": 4, "y": 4},
            "knowledge_node_count": 3,
            "challenge_count": 1,
            "created_at": now,
            "tags": ["初级", "四季", "养生"],
            "author": "系统",
            "is_official": True
        }

        # 创建一个中等大小的10x10迷宫模板
        medium_template = {
            "template_id": str(uuid.uuid4()),
            "name": "五行平衡迷宫",
            "description": "探索五行相生相克的中医理论, 平衡体内阴阳",
            "maze_type": "五行平衡",
            "difficulty": 3,
            "preview_image_url": "/assets/images/templates/five_elements.png",
            "size_x": 10,
            "size_y": 10,
            "cells": self._generate_template_cells(10, 10),
            "start_position": {"x": 0, "y": 0},
            "goal_position": {"x": 9, "y": 9},
            "knowledge_node_count": 5,
            "challenge_count": 3,
            "created_at": now,
            "tags": ["中级", "五行", "阴阳平衡"],
            "author": "系统",
            "is_official": True
        }

        # 插入模板数据
        templates = [small_template, medium_template]

        for template in templates:
            # 转换复杂结构为JSON字符串
            cells_json = json.dumps(template["cells"])
            start_pos_json = json.dumps(template["start_position"])
            goal_pos_json = json.dumps(template["goal_position"])
            tags_json = json.dumps(template["tags"])

            # 插入数据
            await db.execute(
                '''
                INSERT INTO maze_templates (
                    template_id, name, description, maze_type, difficulty,
                    preview_image_url, size_x, size_y, cells, start_position,
                    goal_position, knowledge_node_count, challenge_count,
                    created_at, tags, author, is_official
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    template["template_id"], template["name"], template["description"],
                    template["maze_type"], template["difficulty"], template["preview_image_url"],
                    template["size_x"], template["size_y"], cells_json, start_pos_json,
                    goal_pos_json, template["knowledge_node_count"], template["challenge_count"],
                    template["created_at"], tags_json, template["author"], template["is_official"]
                )
            )

        await db.commit()
        logger.info(f"已加载 {len(templates)} 个初始迷宫模板")

    def _generate_template_cells(self, width: int, height: int) -> list[dict[str, Any]]:
        """
        生成简单的模板单元格

        Args:
            width: 迷宫宽度
            height: 迷宫高度

        Returns:
            List[Dict]: 模板单元格列表
        """
        cells = []

        # 创建基本迷宫结构
        for y in range(height):
            for x in range(width):
                # 默认情况下，每个单元格有北墙和西墙
                north_wall = True
                east_wall = True
                south_wall = True
                west_wall = True

                # 创建简单的迷宫路径
                if (x + y) % 2 == 0:
                    # 偶数和位置，打开东墙和南墙
                    east_wall = False
                    south_wall = False
                else:
                    # 奇数和位置，打开北墙和西墙
                    north_wall = False
                    west_wall = False

                # 确保边界单元格的外墙保持完整
                if x == 0:
                    west_wall = True
                if y == 0:
                    north_wall = True
                if x == width - 1:
                    east_wall = True
                if y == height - 1:
                    south_wall = True

                # 添加一些知识节点和挑战点
                has_knowledge_node = False
                has_challenge = False

                # 在特定位置添加知识节点
                if (x + y) % 3 == 0 and x > 0 and y > 0:
                    has_knowledge_node = True

                # 在特定位置添加挑战点
                if (x * y) % 5 == 0 and x > 0 and y > 0:
                    has_challenge = True

                cell = {
                    "x": x,
                    "y": y,
                    "north_wall": north_wall,
                    "east_wall": east_wall,
                    "south_wall": south_wall,
                    "west_wall": west_wall,
                    "has_knowledge_node": has_knowledge_node,
                    "has_challenge": has_challenge,
                    "knowledge_node_id": str(uuid.uuid4()) if has_knowledge_node else None,
                    "challenge_id": str(uuid.uuid4()) if has_challenge else None
                }

                cells.append(cell)

        return cells

    async def save_template(self, template: MazeTemplate) -> MazeTemplate:
        """
        保存迷宫模板

        Args:
            template: 要保存的迷宫模板

        Returns:
            MazeTemplate: 保存后的模板（包含生成的ID）
        """
        try:
            db = await self._get_db()

            # 如果没有ID，生成一个新的
            if not template.template_id:
                template.template_id = str(uuid.uuid4())

            # 转换复杂结构为JSON字符串
            cells_json = json.dumps([cell.model_dump() for cell in template.cells])
            start_pos_json = json.dumps(template.start_position.model_dump())
            goal_pos_json = json.dumps(template.goal_position.model_dump())
            tags_json = json.dumps(template.tags)

            # 插入或更新模板
            await db.execute(
                '''
                INSERT OR REPLACE INTO maze_templates (
                    template_id, name, description, maze_type, difficulty,
                    preview_image_url, size_x, size_y, cells, start_position,
                    goal_position, knowledge_node_count, challenge_count,
                    created_at, tags, author, is_official
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    template.template_id, template.name, template.description,
                    template.maze_type, template.difficulty, template.preview_image_url,
                    template.size_x, template.size_y, cells_json, start_pos_json,
                    goal_pos_json, template.knowledge_node_count, template.challenge_count,
                    template.created_at.isoformat(), tags_json, template.author, template.is_official
                )
            )

            await db.commit()
            await db.close()

            logger.info(f"模板已保存: {template.template_id}")
            return template

        except Exception as e:
            logger.error(f"保存模板失败: {e}")
            raise

    async def get_template(self, template_id: str) -> MazeTemplate | None:
        """
        根据ID获取迷宫模板

        Args:
            template_id: 模板ID

        Returns:
            Optional[MazeTemplate]: 找到的模板，如果不存在则返回None
        """
        try:
            db = await self._get_db()

            cursor = await db.execute(
                "SELECT * FROM maze_templates WHERE template_id = ?",
                (template_id,)
            )
            row = await cursor.fetchone()

            await db.close()

            if row:
                return self._row_to_template(row)
            return None

        except Exception as e:
            logger.error(f"获取模板失败: {e}")
            raise

    async def list_templates(
        self,
        maze_type: str = "",
        difficulty: int = 0,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[MazeTemplate], int]:
        """
        获取模板列表

        Args:
            maze_type: 迷宫类型过滤
            difficulty: 难度过滤
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[MazeTemplate], int]: 模板列表和总数
        """
        try:
            db = await self._get_db()

            # 构建查询条件
            where_conditions = []
            params = []

            if maze_type:
                where_conditions.append("maze_type = ?")
                params.append(maze_type)

            if difficulty > 0:
                where_conditions.append("difficulty = ?")
                params.append(difficulty)

            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            # 获取总数
            count_query = f"SELECT COUNT(*) FROM maze_templates {where_clause}"
            cursor = await db.execute(count_query, params)
            total_count = (await cursor.fetchone())[0]

            # 获取分页数据
            offset = (page - 1) * page_size
            list_query = f"""
                SELECT * FROM maze_templates {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor = await db.execute(list_query, [*params, page_size, offset])
            rows = await cursor.fetchall()

            await db.close()

            templates = [self._row_to_template(row) for row in rows]
            return templates, total_count

        except Exception as e:
            logger.error(f"获取模板列表失败: {e}")
            raise

    async def delete_template(self, template_id: str) -> bool:
        """
        删除迷宫模板

        Args:
            template_id: 模板ID

        Returns:
            bool: 是否删除成功
        """
        try:
            db = await self._get_db()

            cursor = await db.execute(
                "DELETE FROM maze_templates WHERE template_id = ?",
                (template_id,)
            )

            await db.commit()
            await db.close()

            success = cursor.rowcount > 0
            if success:
                logger.info(f"模板已删除: {template_id}")
            else:
                logger.warning(f"模板不存在: {template_id}")

            return success

        except Exception as e:
            logger.error(f"删除模板失败: {e}")
            raise

    def _row_to_template(self, row: aiosqlite.Row) -> MazeTemplate:
        """
        将数据库行转换为MazeTemplate对象

        Args:
            row: 数据库行

        Returns:
            MazeTemplate: 转换后的模板对象
        """
        # 解析JSON字段
        cells_data = json.loads(row["cells"])
        start_position_data = json.loads(row["start_position"])
        goal_position_data = json.loads(row["goal_position"])
        tags_data = json.loads(row["tags"]) if row["tags"] else []

        # 创建模板对象
        return MazeTemplate(
            template_id=row["template_id"],
            name=row["name"],
            description=row["description"],
            maze_type=row["maze_type"],
            difficulty=row["difficulty"],
            preview_image_url=row["preview_image_url"],
            size_x=row["size_x"],
            size_y=row["size_y"],
            cells=cells_data,
            start_position=start_position_data,
            goal_position=goal_position_data,
            knowledge_node_count=row["knowledge_node_count"],
            challenge_count=row["challenge_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            tags=tags_data,
            author=row["author"],
            is_official=bool(row["is_official"])
        )
