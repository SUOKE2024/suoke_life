#!/usr/bin/env python3
"""
migrate_to_postgresql - 索克生活项目模块

SQLite到PostgreSQL数据迁移脚本

该脚本用于将SQLite数据库中的数据迁移到PostgreSQL数据库。
支持表结构创建、数据迁移、序列重置等功能。
"""

import argparse
import json
import logging
import psycopg2
import sqlite3
import sys
from pathlib import Path
from psycopg2 import sql
from typing import Any, Dict, List, Tuple, Optional


class DatabaseMigrator:
    """数据库迁移器"""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        初始化迁移器

        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self.pg_conn: Optional[psycopg2.extensions.connection] = None

        # 默认配置
        self.config = {
            "sqlite": {
                "database": "health_data.db"
            },
            "postgresql": {
                "host": "localhost",
                "port": 5432,
                "database": "health_data",
                "user": "postgres",
                "password": "password"
            }
        }

        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self.config.update(user_config)
        except Exception as e:
            self.logger.warning(f"无法加载配置文件 {config_path}: {e}")

    def connect_sqlite(self) -> None:
        """连接SQLite数据库"""
        try:
            db_path = self.config["sqlite"]["database"]
            if not Path(db_path).exists():
                raise FileNotFoundError(f"SQLite数据库文件不存在: {db_path}")

            self.sqlite_conn = sqlite3.connect(db_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            self.logger.info(f"成功连接SQLite数据库: {db_path}")

        except Exception as e:
            self.logger.error(f"连接SQLite数据库失败: {e}")
            raise

    def connect_postgresql(self) -> None:
        """连接PostgreSQL数据库"""
        try:
            pg_config = self.config["postgresql"]
            self.pg_conn = psycopg2.connect(
                host=pg_config["host"],
                port=pg_config["port"],
                database=pg_config["database"],
                user=pg_config["user"],
                password=pg_config["password"]
            )
            self.pg_conn.autocommit = False
            self.logger.info("成功连接PostgreSQL数据库")

        except Exception as e:
            self.logger.error(f"连接PostgreSQL数据库失败: {e}")
            raise

    def get_sqlite_tables(self) -> List[str]:
        """获取SQLite数据库中的所有表"""
        if not self.sqlite_conn:
            raise RuntimeError("SQLite连接未建立")

        cursor = self.sqlite_conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        self.logger.info(f"发现 {len(tables)} 个表: {tables}")
        return tables

    def get_table_schema(self, table_name: str) -> List[Tuple[str, str]]:
        """获取表结构"""
        if not self.sqlite_conn:
            raise RuntimeError("SQLite连接未建立")

        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            col_name = row[1]
            col_type = row[2]
            # 转换SQLite类型到PostgreSQL类型
            pg_type = self._convert_type(col_type)
            columns.append((col_name, pg_type))

        return columns

    def _convert_type(self, sqlite_type: str) -> str:
        """转换SQLite类型到PostgreSQL类型"""
        type_mapping = {
            "INTEGER": "INTEGER",
            "TEXT": "TEXT",
            "REAL": "REAL",
            "BLOB": "BYTEA",
            "NUMERIC": "NUMERIC",
            "DATETIME": "TIMESTAMP",
            "DATE": "DATE",
            "TIME": "TIME",
            "BOOLEAN": "BOOLEAN",
            "JSON": "JSONB"
        }

        sqlite_type_upper = sqlite_type.upper()
        for sqlite_t, pg_t in type_mapping.items():
            if sqlite_t in sqlite_type_upper:
                return pg_t

        # 默认返回TEXT
        return "TEXT"

    def create_table(self, table_name: str, columns: List[Tuple[str, str]]) -> None:
        """在PostgreSQL中创建表"""
        if not self.pg_conn:
            raise RuntimeError("PostgreSQL连接未建立")

        cursor = self.pg_conn.cursor()

        # 构建CREATE TABLE语句
        column_defs = []
        for col_name, col_type in columns:
            column_defs.append(f"{col_name} {col_type}")

        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"

        try:
            cursor.execute(create_sql)
            self.pg_conn.commit()
            self.logger.info(f"成功创建表: {table_name}")

        except Exception as e:
            self.pg_conn.rollback()
            self.logger.error(f"创建表失败 {table_name}: {e}")
            raise

    def migrate_table_data(self, table_name: str) -> None:
        """迁移表数据"""
        if not self.sqlite_conn or not self.pg_conn:
            raise RuntimeError("数据库连接未建立")

        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()

        try:
            # 获取SQLite表数据
            sqlite_cursor.execute(f"SELECT * FROM {sql.Identifier(table_name).as_string(sqlite_cursor)}")
            rows = sqlite_cursor.fetchall()

            if not rows:
                self.logger.info(f"表 {table_name} 没有数据")
                return

            # 获取列名
            column_names = [description[0] for description in sqlite_cursor.description]

            # 清空PostgreSQL表
            pg_cursor.execute(sql.SQL("DELETE FROM {}").format(sql.Identifier(table_name)))

            # 插入数据
            placeholders = ', '.join(['%s'] * len(column_names))
            columns = ', '.join(column_names)
            insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, column_names)),
                sql.SQL(placeholders)
            )

            # 准备数据
            data_to_insert = []
            for row in rows:
                # 转换数据类型
                converted_row = []
                for value in row:
                    if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                        # 可能是JSON字符串
                        try:
                            json.loads(value)
                            converted_row.append(value)
                        except json.JSONDecodeError:
                            converted_row.append(value)
                    else:
                        converted_row.append(value)
                data_to_insert.append(tuple(converted_row))

            # 批量插入
            psycopg2.extras.execute_batch(pg_cursor, insert_sql, data_to_insert)
            self.pg_conn.commit()

            self.logger.info(f"成功迁移表 {table_name}: {len(rows)} 行数据")

        except Exception as e:
            self.pg_conn.rollback()
            self.logger.error(f"迁移表数据失败 {table_name}: {e}")
            raise

    def reset_sequences(self) -> None:
        """重置PostgreSQL序列"""
        if not self.pg_conn:
            raise RuntimeError("PostgreSQL连接未建立")

        pg_cursor = self.pg_conn.cursor()

        try:
            # 获取所有序列信息
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
                max_query = sql.SQL("SELECT MAX({}) FROM {}").format(
                    sql.Identifier(column_name),
                    sql.Identifier(table_name)
                )
                pg_cursor.execute(max_query)
                max_value = pg_cursor.fetchone()[0]

                if max_value is not None:
                    # 重置序列
                    reset_query = sql.SQL("SELECT setval(%s, %s)")
                    pg_cursor.execute(reset_query, (seq_name, max_value))
                    self.logger.info(f"重置序列 {seq_name} 到 {max_value}")

            self.pg_conn.commit()

        except Exception as e:
            self.pg_conn.rollback()
            self.logger.error(f"重置序列失败: {e}")
            raise

    def verify_migration(self) -> bool:
        """验证迁移结果"""
        if not self.sqlite_conn or not self.pg_conn:
            raise RuntimeError("数据库连接未建立")

        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()

        try:
            # 获取所有表
            tables = self.get_sqlite_tables()

            for table_name in tables:
                # 获取SQLite表行数
                count_query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
                sqlite_cursor.execute(count_query.as_string(sqlite_cursor))
                sqlite_count = sqlite_cursor.fetchone()[0]

                # 获取PostgreSQL表行数
                try:
                    pg_cursor.execute(count_query)
                    pg_count = pg_cursor.fetchone()[0]
                except Exception:
                    pg_count = 0

                if sqlite_count != pg_count:
                    self.logger.error(
                        f"表 {table_name} 数据不一致: SQLite={sqlite_count}, PostgreSQL={pg_count}"
                    )
                    return False

                self.logger.info(f"表 {table_name} 验证通过: {sqlite_count} 行")

            return True

        except Exception as e:
            self.logger.error(f"验证迁移失败: {e}")
            return False

    def migrate(self) -> None:
        """执行完整迁移"""
        try:
            self.logger.info("开始数据库迁移...")

            # 连接数据库
            self.connect_sqlite()
            self.connect_postgresql()

            # 获取表列表
            tables = self.get_sqlite_tables()

            # 迁移每个表
            for table_name in tables:
                self.logger.info(f"迁移表: {table_name}")

                # 获取表结构
                columns = self.get_table_schema(table_name)

                # 创建表
                self.create_table(table_name, columns)

                # 迁移数据
                self.migrate_table_data(table_name)

            # 重置序列
            self.reset_sequences()

            # 验证迁移
            if self.verify_migration():
                self.logger.info("数据库迁移完成并验证成功!")
            else:
                self.logger.error("数据库迁移验证失败!")
                return

        except Exception as e:
            self.logger.error(f"数据库迁移失败: {e}")
            raise

        finally:
            # 关闭连接
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.pg_conn:
                self.pg_conn.close()

def setup_logging(level: str = "INFO") -> None:
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('migration.log', encoding='utf-8')
        ]
    )

def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="SQLite到PostgreSQL数据迁移工具")
    parser.add_argument(
        "--config",
        type=str,
        help="配置文件路径"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别"
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.log_level)

    try:
        # 创建迁移器并执行迁移
        migrator = DatabaseMigrator(args.config)
        migrator.migrate()

    except Exception as e:
        logging.error(f"迁移失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 