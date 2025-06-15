"""
数据库初始化和迁移脚本
"""

import asyncio
import logging
import os
import sys
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from internal.config.config_loader import load_config
from internal.models.session_models import create_tables, drop_tables

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """数据库迁移器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化数据库迁移器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.db_config = config.get("database", {})

        # 数据库连接配置
        self.db_url = self.db_config.get("url", "postgresql+asyncpg://user:pass@localhost/inquiry_db")
        self.engine = None

        logger.info("数据库迁移器初始化完成")

    async def initialize(self) -> None:
        """初始化数据库连接"""
        try:
            self.engine = create_async_engine(
                self.db_url,
                echo=True,  # 开启SQL日志
                pool_size=5,
                max_overflow=10
            )

            logger.info("数据库连接初始化成功")

        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise

    async def close(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
            logger.info("数据库连接已关闭")

    async def check_database_exists(self) -> bool:
        """检查数据库是否存在"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False

    async def create_database_schema(self) -> None:
        """创建数据库模式"""
        try:
            logger.info("开始创建数据库表...")

            # 创建所有表
            await create_tables(self.engine)

            logger.info("数据库表创建成功")

        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise

    async def drop_database_schema(self) -> None:
        """删除数据库模式"""
        try:
            logger.info("开始删除数据库表...")

            # 删除所有表
            await drop_tables(self.engine)

            logger.info("数据库表删除成功")

        except Exception as e:
            logger.error(f"删除数据库表失败: {e}")
            raise

    async def check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name
                        )
                    """),
                    {"table_name": table_name}
                )
                return result.scalar()
        except Exception as e:
            logger.error(f"检查表存在性失败: {e}")
            return False

    async def get_table_info(self) -> dict[str, Any]:
        """获取表信息"""
        try:
            tables_info = {}

            # 获取所有表名
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """)
                )

                table_names = [row[0] for row in result.fetchall()]

                # 获取每个表的详细信息
                for table_name in table_names:
                    # 获取列信息
                    columns_result = await conn.execute(
                        text("""
                            SELECT column_name, data_type, is_nullable, column_default
                            FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name
                            ORDER BY ordinal_position
                        """),
                        {"table_name": table_name}
                    )

                    columns = [
                        {
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == "YES",
                            "default": row[3]
                        }
                        for row in columns_result.fetchall()
                    ]

                    # 获取行数
                    count_result = await conn.execute(
                        text(f"SELECT COUNT(*) FROM {table_name}")
                    )
                    row_count = count_result.scalar()

                    tables_info[table_name] = {
                        "columns": columns,
                        "row_count": row_count
                    }

            return tables_info

        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            return {}

    async def create_indexes(self) -> None:
        """创建索引"""
        try:
            logger.info("开始创建索引...")

            indexes = [
                # 会话表索引
                "CREATE INDEX IF NOT EXISTS idx_sessions_user_created ON inquiry_sessions(user_id, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_status_updated ON inquiry_sessions(status, updated_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_agent_created ON inquiry_sessions(agent_id, created_at DESC)",

                # 消息表索引
                "CREATE INDEX IF NOT EXISTS idx_messages_session_timestamp ON session_messages(session_id, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_messages_role_timestamp ON session_messages(role, timestamp DESC)",

                # 总结表索引
                "CREATE INDEX IF NOT EXISTS idx_summaries_session_created ON session_summaries(session_id, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_summaries_type_created ON session_summaries(summary_type, created_at DESC)",

                # 症状提取表索引
                "CREATE INDEX IF NOT EXISTS idx_extractions_session_created ON symptom_extractions(session_id, created_at DESC)",

                # 中医证型映射表索引
                "CREATE INDEX IF NOT EXISTS idx_mappings_session_created ON tcm_pattern_mappings(session_id, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_mappings_pattern_created ON tcm_pattern_mappings(primary_pattern, created_at DESC)",

                # 健康风险评估表索引
                "CREATE INDEX IF NOT EXISTS idx_assessments_user_created ON health_risk_assessments(user_id, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_assessments_risk_created ON health_risk_assessments(overall_risk_level, created_at DESC)",
            ]

            async with self.engine.begin() as conn:
                for index_sql in indexes:
                    await conn.execute(text(index_sql))
                    logger.debug(f"创建索引: {index_sql}")

            logger.info("索引创建成功")

        except Exception as e:
            logger.error(f"创建索引失败: {e}")
            raise

    async def insert_sample_data(self) -> None:
        """插入示例数据"""
        try:
            logger.info("开始插入示例数据...")

            async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            async with async_session() as session:
                # 这里可以添加示例数据插入逻辑
                # 由于是生产环境，暂时不插入示例数据
                pass

            logger.info("示例数据插入成功")

        except Exception as e:
            logger.error(f"插入示例数据失败: {e}")
            raise

    async def run_migration(self, operation: str = "create") -> None:
        """运行迁移"""
        try:
            await self.initialize()

            if operation == "create":
                logger.info("执行数据库创建迁移...")
                await self.create_database_schema()
                await self.create_indexes()
                logger.info("数据库创建迁移完成")

            elif operation == "drop":
                logger.info("执行数据库删除迁移...")
                await self.drop_database_schema()
                logger.info("数据库删除迁移完成")

            elif operation == "recreate":
                logger.info("执行数据库重建迁移...")
                await self.drop_database_schema()
                await self.create_database_schema()
                await self.create_indexes()
                logger.info("数据库重建迁移完成")

            elif operation == "info":
                logger.info("获取数据库信息...")
                tables_info = await self.get_table_info()

                print("\n=== 数据库表信息 ===")
                for table_name, info in tables_info.items():
                    print(f"\n表名: {table_name}")
                    print(f"行数: {info['row_count']}")
                    print("列信息:")
                    for col in info['columns']:
                        nullable = "NULL" if col['nullable'] else "NOT NULL"
                        default = f" DEFAULT {col['default']}" if col['default'] else ""
                        print(f"  - {col['name']}: {col['type']} {nullable}{default}")

            else:
                logger.error(f"未知的迁移操作: {operation}")

        except Exception as e:
            logger.error(f"迁移执行失败: {e}")
            raise
        finally:
            await self.close()


async def main():
    """主函数"""
    import argparse

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument(
        "operation",
        choices=["create", "drop", "recreate", "info"],
        help="迁移操作类型"
    )
    parser.add_argument(
        "--config",
        default="./config/config.yaml",
        help="配置文件路径"
    )

    args = parser.parse_args()

    try:
        # 加载配置
        config = load_config(args.config)

        # 创建迁移器
        migrator = DatabaseMigrator(config)

        # 执行迁移
        await migrator.run_migration(args.operation)

        logger.info("迁移操作完成")

    except Exception as e:
        logger.error(f"迁移操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
