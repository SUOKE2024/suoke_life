"""
migrate_to_postgresql - 索克生活项目模块
"""

        from ..internal.model.database import Base
    import argparse
from loguru import logger
from psycopg2.extras import RealDictCursor
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
import os
import psycopg2
import sqlite3
import sys
import yaml

#!/usr/bin/env python

"""
数据迁移脚本：从SQLite迁移到PostgreSQL
用于将健康数据服务的数据从SQLite数据库迁移到PostgreSQL数据库
"""




class DatabaseMigrator:
    """数据库迁移器"""

    def __init__(self, config_path: str = "config/default.yaml"):
        """
        初始化迁移器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = None
        self.sqlite_path = None
        self.pg_config = None

    async def load_config(self) -> None:
        """加载配置"""
        try:
            with open(self.config_path, encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            # 获取PostgreSQL配置
            db_config = self.config['database']
            self.pg_config = {
                'host': os.getenv('DB_HOST', db_config.get('host', 'localhost')),
                'port': int(os.getenv('DB_PORT', db_config.get('port', 5432))),
                'database': os.getenv('DB_NAME', db_config.get('database', 'suoke_health_data')),
                'user': os.getenv('DB_USER', db_config.get('username', 'postgres')),
                'password': os.getenv('DB_PASSWORD', db_config.get('password', 'postgres'))
            }

            # 获取SQLite路径（从环境变量或默认路径）
            self.sqlite_path = os.getenv('SQLITE_DB_PATH', 'data/health_data.db')

            logger.info(f"配置加载成功，PostgreSQL: {self.pg_config['host']}:{self.pg_config['port']}")
            logger.info(f"SQLite路径: {self.sqlite_path}")

        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            raise

    async def check_prerequisites(self) -> bool:
        """检查迁移前提条件"""
        logger.info("检查迁移前提条件...")

        # 检查SQLite文件是否存在
        if not os.path.exists(self.sqlite_path):
            logger.error(f"SQLite数据库文件不存在: {self.sqlite_path}")
            return False

        # 检查PostgreSQL连接
        try:
            conn = psycopg2.connect(**self.pg_config)
            conn.close()
            logger.info("PostgreSQL连接测试成功")
        except Exception as e:
            logger.error(f"PostgreSQL连接失败: {e}")
            return False

        return True

    async def create_postgresql_database(self) -> None:
        """创建PostgreSQL数据库（如果不存在）"""
        logger.info("检查并创建PostgreSQL数据库...")

        # 连接到默认数据库
        temp_config = self.pg_config.copy()
        temp_config['database'] = 'postgres'

        try:
            conn = psycopg2.connect(**temp_config)
            conn.autocommit = True
            cursor = conn.cursor()

            # 检查数据库是否存在
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.pg_config['database'],)
            )

            if not cursor.fetchone():
                # 创建数据库
                cursor.execute(f'CREATE DATABASE "{self.pg_config["database"]}"')
                logger.info(f"数据库 {self.pg_config['database']} 创建成功")
            else:
                logger.info(f"数据库 {self.pg_config['database']} 已存在")

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"创建PostgreSQL数据库失败: {e}")
            raise

    async def create_postgresql_tables(self) -> None:
        """在PostgreSQL中创建表结构"""
        logger.info("创建PostgreSQL表结构...")

        # 使用SQLAlchemy创建表

        pg_url = f"postgresql+asyncpg://{self.pg_config['user']}:{self.pg_config['password']}@{self.pg_config['host']}:{self.pg_config['port']}/{self.pg_config['database']}"

        engine = create_async_engine(pg_url)

        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("PostgreSQL表结构创建成功")

        except Exception as e:
            logger.error(f"创建PostgreSQL表结构失败: {e}")
            raise
        finally:
            await engine.dispose()

    async def migrate_data(self) -> None:
        """迁移数据"""
        logger.info("开始数据迁移...")

        # 连接SQLite
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row

        # 连接PostgreSQL
        pg_conn = psycopg2.connect(**self.pg_config)
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)

        try:
            # 获取要迁移的表列表
            tables_to_migrate = [
                'users',
                'health_data_records',
                'health_insight_records',
                'health_profile_records',
                'system_metrics',
                'audit_logs'
            ]

            for table_name in tables_to_migrate:
                await self._migrate_table(sqlite_conn, pg_conn, pg_cursor, table_name)

            pg_conn.commit()
            logger.info("数据迁移完成")

        except Exception as e:
            pg_conn.rollback()
            logger.error(f"数据迁移失败: {e}")
            raise
        finally:
            sqlite_conn.close()
            pg_cursor.close()
            pg_conn.close()

    async def _migrate_table(
        self,
        sqlite_conn: sqlite3.Connection,
        pg_conn: psycopg2.extensions.connection,
        pg_cursor: psycopg2.extensions.cursor,
        table_name: str
    ) -> None:
        """迁移单个表的数据"""
        logger.info(f"迁移表: {table_name}")

        # 检查SQLite表是否存在
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )

        if not sqlite_cursor.fetchone():
            logger.warning(f"SQLite中不存在表: {table_name}")
            return

        # 获取SQLite表数据
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        if not rows:
            logger.info(f"表 {table_name} 无数据，跳过")
            return

        # 获取列名
        column_names = [description[0] for description in sqlite_cursor.description]

        # 清空PostgreSQL表（如果需要）
        pg_cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")

        # 批量插入数据
        batch_size = 1000
        total_rows = len(rows)

        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]

            # 构建插入语句
            placeholders = ', '.join(['%s'] * len(column_names))
            columns = ', '.join(column_names)
            insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # 准备数据
            batch_data = []
            for row in batch:
                row_data = []
                for value in row:
                    # 处理特殊数据类型
                    if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                        # JSON字符串保持原样
                        row_data.append(value)
                    else:
                        row_data.append(value)
                batch_data.append(tuple(row_data))

            # 执行批量插入
            try:
                pg_cursor.executemany(insert_sql, batch_data)
                logger.info(f"表 {table_name}: 已迁移 {min(i + batch_size, total_rows)}/{total_rows} 行")
            except Exception as e:
                logger.error(f"插入数据失败 - 表: {table_name}, 批次: {i//batch_size + 1}, 错误: {e}")
                raise

        logger.info(f"表 {table_name} 迁移完成，共 {total_rows} 行")

    async def update_sequences(self) -> None:
        """更新PostgreSQL序列"""
        logger.info("更新PostgreSQL序列...")

        pg_conn = psycopg2.connect(**self.pg_config)
        pg_cursor = pg_conn.cursor()

        try:
            # 获取所有序列
            pg_cursor.execute("""
                SELECT schemaname, sequencename, tablename, columnname
                FROM pg_sequences
                JOIN information_schema.columns ON
                    column_default LIKE '%' || sequencename || '%'
                WHERE schemaname = 'public'
            """)

            sequences = pg_cursor.fetchall()

            for _schema, seq_name, table_name, column_name in sequences:
                # 获取表中该列的最大值
                pg_cursor.execute(f"SELECT MAX({column_name}) FROM {table_name}")
                max_value = pg_cursor.fetchone()[0]

                if max_value is not None:
                    # 设置序列的下一个值
                    pg_cursor.execute(f"SELECT setval('{seq_name}', {max_value})")
                    logger.info(f"序列 {seq_name} 更新为 {max_value}")

            pg_conn.commit()
            logger.info("序列更新完成")

        except Exception as e:
            pg_conn.rollback()
            logger.error(f"更新序列失败: {e}")
            raise
        finally:
            pg_cursor.close()
            pg_conn.close()

    async def verify_migration(self) -> bool:
        """验证迁移结果"""
        logger.info("验证迁移结果...")

        # 连接SQLite
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()

        # 连接PostgreSQL
        pg_conn = psycopg2.connect(**self.pg_config)
        pg_cursor = pg_conn.cursor()

        try:
            # 获取表列表
            sqlite_cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in sqlite_cursor.fetchall()]

            verification_passed = True

            for table_name in tables:
                # 获取SQLite表行数
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                sqlite_count = sqlite_cursor.fetchone()[0]

                # 获取PostgreSQL表行数
                try:
                    pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    pg_count = pg_cursor.fetchone()[0]
                except Exception:
                    pg_count = 0

                if sqlite_count == pg_count:
                    logger.info(f"✓ 表 {table_name}: SQLite({sqlite_count}) = PostgreSQL({pg_count})")
                else:
                    logger.error(f"✗ 表 {table_name}: SQLite({sqlite_count}) ≠ PostgreSQL({pg_count})")
                    verification_passed = False

            return verification_passed

        except Exception as e:
            logger.error(f"验证迁移结果失败: {e}")
            return False
        finally:
            sqlite_cursor.close()
            sqlite_conn.close()
            pg_cursor.close()
            pg_conn.close()

    async def run_migration(self) -> bool:
        """运行完整的迁移流程"""
        try:
            logger.info("开始数据库迁移流程...")

            # 1. 加载配置
            await self.load_config()

            # 2. 检查前提条件
            if not await self.check_prerequisites():
                return False

            # 3. 创建PostgreSQL数据库
            await self.create_postgresql_database()

            # 4. 创建表结构
            await self.create_postgresql_tables()

            # 5. 迁移数据
            await self.migrate_data()

            # 6. 更新序列
            await self.update_sequences()

            # 7. 验证迁移结果
            if await self.verify_migration():
                logger.info("🎉 数据库迁移成功完成！")
                return True
            else:
                logger.error("❌ 数据库迁移验证失败！")
                return False

        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            return False


async def main():
    """主函数"""

    parser = argparse.ArgumentParser(description="健康数据服务数据库迁移工具")
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="配置文件路径"
    )
    parser.add_argument(
        "--sqlite-path",
        help="SQLite数据库文件路径（覆盖配置文件）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅检查前提条件，不执行迁移"
    )

    args = parser.parse_args()

    # 设置日志
    logger.add(
        "logs/migration_{time}.log",
        rotation="10 MB",
        retention="30 days",
        level="INFO"
    )

    migrator = DatabaseMigrator(args.config)

    if args.sqlite_path:
        migrator.sqlite_path = args.sqlite_path

    if args.dry_run:
        await migrator.load_config()
        success = await migrator.check_prerequisites()
        if success:
            logger.info("✓ 前提条件检查通过，可以执行迁移")
        else:
            logger.error("✗ 前提条件检查失败")
        return success

    success = await migrator.run_migration()

    if success:
        logger.info("\n" + "="*50)
        logger.info("迁移完成！请按以下步骤操作：")
        logger.info("1. 更新环境变量或配置文件，指向PostgreSQL数据库")
        logger.info("2. 重启健康数据服务")
        logger.info("3. 验证服务正常运行")
        logger.info("4. 备份SQLite文件后可以删除")
        logger.info("="*50)
        sys.exit(0)
    else:
        logger.error("迁移失败，请检查日志并修复问题后重试")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
