"""
progress_repository - 索克生活项目模块
"""

from datetime import datetime
from internal.model.progress import UserProgress
from pathlib import Path
import aiosqlite
import json
import logging
import os

#!/usr/bin/env python3

"""
进度存储库 - 负责用户迷宫进度的存储和检索
"""




logger = logging.getLogger(__name__)

class ProgressRepository:
    """进度存储库，负责用户迷宫进度的存储和检索"""

    def __init__(self):
        self.db_path = os.environ.get("MAZE_DB_PATH", "data/maze.db")
        logger.info(f"进度存储库初始化, 数据库路径: {self.db_path}")

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
        CREATE TABLE IF NOT EXISTS progress (
            user_id TEXT NOT NULL,
            maze_id TEXT NOT NULL,
            current_position TEXT NOT NULL,
            visited_cells TEXT NOT NULL,
            completed_challenges TEXT NOT NULL,
            acquired_knowledge TEXT NOT NULL,
            completion_percentage INTEGER NOT NULL,
            status TEXT NOT NULL,
            steps_taken INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            last_active_time TEXT NOT NULL,
            notes TEXT,
            PRIMARY KEY (user_id, maze_id)
        )
        ''')
        await db.commit()

    async def save_progress(self, progress: UserProgress) -> UserProgress:
        """
        保存用户进度

        Args:
            progress: 用户进度对象

        Returns:
            UserProgress: 保存后的用户进度对象
        """
        logger.info(f"保存用户 {progress.user_id} 在迷宫 {progress.maze_id} 中的进度")

        db = await self._get_db()
        try:
            # 将复杂结构转换为JSON字符串
            current_pos_json = json.dumps(progress.current_position)
            visited_cells_json = json.dumps(progress.visited_cells)
            completed_challenges_json = json.dumps(progress.completed_challenges)
            acquired_knowledge_json = json.dumps(progress.acquired_knowledge)
            notes_json = json.dumps(progress.notes)

            # 准备SQL语句
            query = '''
            INSERT OR REPLACE INTO progress (
                user_id, maze_id, current_position, visited_cells,
                completed_challenges, acquired_knowledge, completion_percentage,
                status, steps_taken, start_time, last_active_time, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            # 执行查询
            await db.execute(
                query,
                (
                    progress.user_id, progress.maze_id, current_pos_json,
                    visited_cells_json, completed_challenges_json, acquired_knowledge_json,
                    progress.completion_percentage, progress.status, progress.steps_taken,
                    progress.start_time.isoformat(), progress.last_active_time.isoformat(),
                    notes_json
                )
            )
            await db.commit()

            return progress

        finally:
            await db.close()

    async def get_progress(self, user_id: str, maze_id: str) -> UserProgress | None:
        """
        获取用户进度

        Args:
            user_id: 用户ID
            maze_id: 迷宫ID

        Returns:
            Optional[UserProgress]: 用户进度对象或None（如果未找到）
        """
        logger.info(f"获取用户 {user_id} 在迷宫 {maze_id} 中的进度")

        db = await self._get_db()
        try:
            # 执行查询
            cursor = await db.execute(
                "SELECT * FROM progress WHERE user_id = ? AND maze_id = ?",
                (user_id, maze_id)
            )
            row = await cursor.fetchone()

            if not row:
                logger.warning(f"未找到用户 {user_id} 在迷宫 {maze_id} 中的进度")
                return None

            # 将行数据转换为UserProgress对象
            return self._row_to_progress(row)

        finally:
            await db.close()

    async def get_user_progress_list(self, user_id: str, limit: int = 10, offset: int = 0) -> list[UserProgress]:
        """
        获取用户的所有进度列表

        Args:
            user_id: 用户ID
            limit: 返回结果的最大数量
            offset: 结果偏移量

        Returns:
            List[UserProgress]: 用户进度对象列表
        """
        logger.info(f"获取用户 {user_id} 的进度列表")

        db = await self._get_db()
        try:
            # 执行查询
            cursor = await db.execute(
                "SELECT * FROM progress WHERE user_id = ? ORDER BY last_active_time DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset)
            )
            rows = await cursor.fetchall()

            # 将行数据转换为UserProgress对象列表
            return [self._row_to_progress(row) for row in rows]

        finally:
            await db.close()

    async def delete_progress(self, user_id: str, maze_id: str) -> bool:
        """
        删除用户进度

        Args:
            user_id: 用户ID
            maze_id: 迷宫ID

        Returns:
            bool: 是否成功删除
        """
        logger.info(f"删除用户 {user_id} 在迷宫 {maze_id} 中的进度")

        db = await self._get_db()
        try:
            # 执行删除
            cursor = await db.execute(
                "DELETE FROM progress WHERE user_id = ? AND maze_id = ?",
                (user_id, maze_id)
            )
            await db.commit()

            # 检查是否有行被删除
            return cursor.rowcount > 0

        finally:
            await db.close()

    async def get_completed_mazes(self, user_id: str) -> list[str]:
        """
        获取用户已完成的迷宫ID列表

        Args:
            user_id: 用户ID

        Returns:
            List[str]: 已完成迷宫的ID列表
        """
        logger.info(f"获取用户 {user_id} 已完成的迷宫列表")

        db = await self._get_db()
        try:
            # 执行查询
            cursor = await db.execute(
                "SELECT maze_id FROM progress WHERE user_id = ? AND status = 'COMPLETED'",
                (user_id,)
            )
            rows = await cursor.fetchall()

            # 提取迷宫ID
            return [row["maze_id"] for row in rows]

        finally:
            await db.close()

    def _row_to_progress(self, row: aiosqlite.Row) -> UserProgress:
        """将数据库行转换为UserProgress对象"""
        return UserProgress(
            user_id=row["user_id"],
            maze_id=row["maze_id"],
            current_position=json.loads(row["current_position"]),
            visited_cells=json.loads(row["visited_cells"]),
            completed_challenges=json.loads(row["completed_challenges"]),
            acquired_knowledge=json.loads(row["acquired_knowledge"]),
            completion_percentage=row["completion_percentage"],
            status=row["status"],
            steps_taken=row["steps_taken"],
            start_time=datetime.fromisoformat(row["start_time"]),
            last_active_time=datetime.fromisoformat(row["last_active_time"]),
            notes=json.loads(row["notes"]) if row["notes"] else {}
        )
