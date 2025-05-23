"""
数据库迁移环境配置

该模块为Alembic数据库迁移工具提供环境配置。
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# 导入模型，确保Base.metadata正确配置
from internal.repository.models import metadata

# Alembic Config对象
config = context.config

# 解释配置文件中的section
fileConfig(config.config_file_name)

target_metadata = metadata

def run_migrations_offline():
    """
    离线模式运行迁移
    
    离线模式不需要实际连接数据库。通过在配置中指定的URL，
    生成SQL语句而不执行它们，适合在不同环境间传递迁移。
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
    """
    在给定连接上运行迁移
    
    Args:
        connection: 数据库连接
    """
    context.configure(
        connection=connection, 
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """
    在线模式运行迁移
    
    连接到实际数据库并执行迁移。适合开发和直接部署场景。
    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())