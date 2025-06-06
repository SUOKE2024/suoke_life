"""
maze_repository - 索克生活项目模块
"""

    import aiosqlite
from datetime import datetime, timedelta
from internal.model.maze import Maze
from pathlib import Path
from pkg.utils.metrics import record_db_operation
import logging
import os

#!/usr/bin/env python3

"""
迷宫存储库 - 数据库优化版本
"""


try:
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False


logger = logging.getLogger(__name__)

class MazeRepository:
    """迷宫数据存储库 - 优化版本"""

    def __init__(self):
        self.db_path = os.environ.get("MAZE_DB_PATH", "data/maze.db")
        logger.info(f"迷宫存储库初始化, 数据库路径: {self.db_path}")
        self._connection_pool = None
        self._initialized = False

    async def _ensure_initialized(self):
        """确保数据库已初始化"""
        if not self._initialized:
            await self._init_database()
            self._initialized = True

    async def _init_database(self):
        """初始化数据库和索引"""
        if not SQLITE_AVAILABLE:
            logger.warning("SQLite不可用, 使用内存存储")
            self._mazes = {}
            return

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 创建迷宫表
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS mazes (
                        maze_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        maze_type TEXT NOT NULL,
                        size_x INTEGER NOT NULL,
                        size_y INTEGER NOT NULL,
                        difficulty INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'ACTIVE',
                        is_public BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP NULL,
                        maze_data TEXT NOT NULL,
                        description TEXT,
                        tags TEXT
                    )
                """)

                # 创建性能优化索引
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_mazes_user_id ON mazes(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_type ON mazes(maze_type)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_status ON mazes(status)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_difficulty ON mazes(difficulty)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_created_at ON mazes(created_at)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_user_type ON mazes(user_id, maze_type)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_user_status ON mazes(user_id, status)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_type_difficulty ON mazes(maze_type, difficulty)",
                    "CREATE INDEX IF NOT EXISTS idx_mazes_public_type ON mazes(is_public, maze_type) WHERE is_public = TRUE"
                ]

                for index_sql in indexes:
                    await db.execute(index_sql)

                # 创建全文搜索表
                await db.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS mazes_fts USING fts5(
                        maze_id,
                        description,
                        tags,
                        content='mazes',
                        content_rowid='rowid'
                    )
                """)

                # 创建触发器保持FTS同步
                await db.execute("""
                    CREATE TRIGGER IF NOT EXISTS mazes_fts_insert AFTER INSERT ON mazes BEGIN
                        INSERT INTO mazes_fts(maze_id, description, tags)
                        VALUES (new.maze_id, new.description, new.tags);
                    END
                """)

                await db.execute("""
                    CREATE TRIGGER IF NOT EXISTS mazes_fts_update AFTER UPDATE ON mazes BEGIN
                        UPDATE mazes_fts SET description = new.description, tags = new.tags
                        WHERE maze_id = new.maze_id;
                    END
                """)

                await db.execute("""
                    CREATE TRIGGER IF NOT EXISTS mazes_fts_delete AFTER DELETE ON mazes BEGIN
                        DELETE FROM mazes_fts WHERE maze_id = old.maze_id;
                    END
                """)

                await db.commit()
                logger.info("数据库初始化完成, 索引已创建")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e!s}")
            # 回退到内存存储
            self._mazes = {}

    async     @cache(timeout=300)  # 5分钟缓存
def _get_db(self):
        """获取数据库连接"""
        # 确保数据库目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def save_maze(self, maze: Maze) -> Maze:
        """保存迷宫"""
        await self._ensure_initialized()

        try:
            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    maze_data = maze.to_json()
                    tags_str = ','.join(maze.tags) if maze.tags else ''

                    await db.execute("""
                        INSERT OR REPLACE INTO mazes
                        (maze_id, user_id, maze_type, size_x, size_y, difficulty,
                         status, is_public, created_at, updated_at, completed_at,
                         maze_data, description, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        maze.maze_id, maze.user_id, maze.maze_type,
                        maze.size_x, maze.size_y, maze.difficulty,
                        maze.status, maze.is_public, maze.created_at,
                        datetime.now(), maze.completed_at,
                        maze_data, maze.description, tags_str
                    ))
                    await db.commit()

                record_db_operation("save", "mazes", "success")
            else:
                # 内存存储备用
                self._mazes[maze.maze_id] = maze

            return maze

        except Exception as e:
            logger.error(f"保存迷宫失败: {e!s}")
            record_db_operation("save", "mazes", "error")
            raise

    async def get_maze(self, maze_id: str) -> Maze | None:
        """获取迷宫"""
        await self._ensure_initialized()

        try:
            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute(
                        "SELECT maze_data FROM mazes WHERE maze_id = ?",
                        (maze_id,)
                    )
                    row = await cursor.fetchone()

                    if row:
                        maze = Maze.from_json(row[0])
                        record_db_operation("get", "mazes", "success")
                        return maze
            else:
                # 内存存储备用
                maze = self._mazes.get(maze_id)
                if maze:
                    record_db_operation("get", "mazes", "success")
                    return maze

            record_db_operation("get", "mazes", "not_found")
            return None

        except Exception as e:
            logger.error(f"获取迷宫失败: {e!s}")
            record_db_operation("get", "mazes", "error")
            raise

    async def get_mazes_by_user(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        maze_type: str | None = None,
        status: str | None = None
    ) -> list[Maze]:
        """获取用户的迷宫列表 - 优化版本"""
        await self._ensure_initialized()

        try:
            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    # 构建动态查询
                    where_conditions = ["user_id = ?"]
                    params = [user_id]

                    if maze_type:
                        where_conditions.append("maze_type = ?")
                        params.append(maze_type)

                    if status:
                        where_conditions.append("status = ?")
                        params.append(status)

                    where_clause = " AND ".join(where_conditions)

                    query = f"""
                        SELECT maze_data FROM mazes
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    """
                    params.extend([limit, offset])

                    cursor = await db.execute(query, params)
                    rows = await cursor.fetchall()

                    mazes = [Maze.from_json(row[0]) for row in rows]
                    record_db_operation("list", "mazes", "success")
                    return mazes
            else:
                # 内存存储备用
                user_mazes = [
                    maze for maze in self._mazes.values()
                    if maze.user_id == user_id
                ]

                # 应用筛选
                if maze_type:
                    user_mazes = [m for m in user_mazes if m.maze_type == maze_type]
                if status:
                    user_mazes = [m for m in user_mazes if m.status == status]

                # 排序和分页
                user_mazes.sort(key=lambda x: x.created_at, reverse=True)
                return user_mazes[offset:offset + limit]

        except Exception as e:
            logger.error(f"获取用户迷宫列表失败: {e!s}")
            record_db_operation("list", "mazes", "error")
            raise

    async def search_mazes(
        self,
        query: str,
        maze_type: str | None = None,
        difficulty: int | None = None,
        limit: int = 10,
        offset: int = 0
    ) -> tuple[list[Maze], int]:
        """搜索迷宫 - 使用全文搜索优化"""
        await self._ensure_initialized()

        try:
            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    # 使用FTS进行全文搜索
                    where_conditions = []
                    params = []

                    # 全文搜索条件
                    fts_query = f"description:{query}* OR tags:{query}*"

                    # 构建JOIN查询
                    join_conditions = ["m.maze_id = fts.maze_id"]

                    if maze_type:
                        where_conditions.append("m.maze_type = ?")
                        params.append(maze_type)

                    if difficulty:
                        where_conditions.append("m.difficulty = ?")
                        params.append(difficulty)

                    # 只搜索公开的迷宫
                    where_conditions.append("m.is_public = TRUE")

                    where_clause = ""
                    if where_conditions:
                        where_clause = "WHERE " + " AND ".join(where_conditions)

                    # 搜索查询
                    search_query = f"""
                        SELECT m.maze_data FROM mazes m
                        JOIN mazes_fts fts ON {' AND '.join(join_conditions)}
                        WHERE fts MATCH ?
                        {where_clause}
                        ORDER BY fts.rank
                        LIMIT ? OFFSET ?
                    """

                    search_params = [fts_query, *params, limit, offset]
                    cursor = await db.execute(search_query, search_params)
                    rows = await cursor.fetchall()

                    mazes = [Maze.from_json(row[0]) for row in rows]

                    # 获取总数
                    count_query = f"""
                        SELECT COUNT(*) FROM mazes m
                        JOIN mazes_fts fts ON {' AND '.join(join_conditions)}
                        WHERE fts MATCH ?
                        {where_clause}
                    """
                    count_params = [fts_query, *params]
                    cursor = await db.execute(count_query, count_params)
                    total = (await cursor.fetchone())[0]

                    record_db_operation("search", "mazes", "success")
                    return mazes, total
            else:
                # 内存存储备用 - 简单文本匹配
                all_mazes = [
                    maze for maze in self._mazes.values()
                    if maze.is_public and (
                        query.lower() in (maze.description or '').lower() or
                        any(query.lower() in tag.lower() for tag in (maze.tags or []))
                    )
                ]

                # 应用筛选
                if maze_type:
                    all_mazes = [m for m in all_mazes if m.maze_type == maze_type]
                if difficulty:
                    all_mazes = [m for m in all_mazes if m.difficulty == difficulty]

                total = len(all_mazes)
                mazes = all_mazes[offset:offset + limit]

                return mazes, total

        except Exception as e:
            logger.error(f"搜索迷宫失败: {e!s}")
            record_db_operation("search", "mazes", "error")
            raise

    async def delete_maze(self, maze_id: str) -> bool:
        """删除迷宫"""
        await self._ensure_initialized()

        try:
            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute(
                        "DELETE FROM mazes WHERE maze_id = ?",
                        (maze_id,)
                    )
                    await db.commit()

                    success = cursor.rowcount > 0
                    record_db_operation("delete", "mazes", "success" if success else "not_found")
                    return success
            # 内存存储备用
            elif maze_id in self._mazes:
                del self._mazes[maze_id]
                record_db_operation("delete", "mazes", "success")
                return True
            else:
                record_db_operation("delete", "mazes", "not_found")
                return False

        except Exception as e:
            logger.error(f"删除迷宫失败: {e!s}")
            record_db_operation("delete", "mazes", "error")
            raise

    async def count_active_mazes(self) -> int:
        """统计活跃迷宫数量"""
        await self._ensure_initialized()

        try:
            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute(
                        "SELECT COUNT(*) FROM mazes WHERE status = 'ACTIVE'"
                    )
                    count = (await cursor.fetchone())[0]
                    return count
            else:
                # 内存存储备用
                return len([m for m in self._mazes.values() if m.status == "ACTIVE"])

        except Exception as e:
            logger.error(f"统计活跃迷宫失败: {e!s}")
            return 0

    async def get_maze_types_count(self) -> dict[str, int]:
        """获取各类型迷宫数量统计"""
        await self._ensure_initialized()

        try:
            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute("""
                        SELECT maze_type, COUNT(*)
                        FROM mazes
                        WHERE status = 'ACTIVE'
                        GROUP BY maze_type
                    """)
                    rows = await cursor.fetchall()
                    return dict(rows)
            else:
                # 内存存储备用
                type_counts = {}
                for maze in self._mazes.values():
                    if maze.status == "ACTIVE":
                        type_counts[maze.maze_type] = type_counts.get(maze.maze_type, 0) + 1
                return type_counts

        except Exception as e:
            logger.error(f"获取类型统计失败: {e!s}")
            return {}

    async def cleanup_old_mazes(self, days: int = 30) -> int:
        """清理旧的已完成迷宫"""
        await self._ensure_initialized()

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            if SQLITE_AVAILABLE and hasattr(self, 'db_path'):
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute("""
                        DELETE FROM mazes
                        WHERE status = 'COMPLETED'
                        AND completed_at < ?
                    """, (cutoff_date,))
                    await db.commit()

                    deleted_count = cursor.rowcount
                    logger.info(f"清理了 {deleted_count} 个旧迷宫")
                    return deleted_count
            else:
                # 内存存储备用
                to_delete = [
                    maze_id for maze_id, maze in self._mazes.items()
                    if maze.status == "COMPLETED" and
                       maze.completed_at and maze.completed_at < cutoff_date
                ]

                for maze_id in to_delete:
                    del self._mazes[maze_id]

                return len(to_delete)

        except Exception as e:
            logger.error(f"清理旧迷宫失败: {e!s}")
            return 0
