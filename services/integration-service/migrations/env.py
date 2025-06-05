"""
Alembic 环境配置

该模块为Alembic数据库迁移工具提供环境配置。
"""

import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from integration_service.models.base import Base
from integration_service.config import settings

# Alembic Config对象
config = context.config

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.database_url)

# 解释配置文件的Python日志记录
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的MetaData对象以支持'autogenerate'
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。

    这将配置上下文，只使用URL而不是Engine，
    尽管这里也需要一个Engine，但我们不创建连接；
    迁移脚本输出到stdout。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """运行迁移的核心函数"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """在异步模式下运行迁移"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = AsyncEngine(
        engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移。

    在这种情况下，我们需要创建一个Engine并将连接与上下文关联。
    """
    # 检查是否使用异步引擎
    if settings.database_url.startswith("postgresql+asyncpg"):
        asyncio.run(run_async_migrations())
    else:
        # 同步模式
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 