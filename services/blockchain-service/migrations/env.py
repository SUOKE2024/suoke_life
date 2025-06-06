"""
env - 索克生活项目模块
"""

    from sqlalchemy.engine import Connection
from __future__ import annotations
from alembic import context
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from suoke_blockchain_service.config import settings
from suoke_blockchain_service.database import Base
from typing import TYPE_CHECKING
import asyncio

"""
Alembic 环境配置

配置数据库迁移环境。
"""




if TYPE_CHECKING:


# Alembic Config 对象
config = context.config

# 解释配置文件的日志记录
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的 MetaData 对象以支持自动生成
target_metadata = Base.metadata

# 其他从 mypy 环境中需要的值


def get_url() -> str:
    """获取数据库连接 URL"""
    return settings.database.url


def run_migrations_offline() -> None:
    """在 'offline' 模式下运行迁移。

    这将配置上下文仅使用 URL
    而不是 Engine, 尽管这里也需要 Engine。
    通过跳过 Engine 创建, 我们甚至不需要
    DBAPI 可用。

    调用 context.execute() 来发出字符串到脚本输出。
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """运行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在 'online' 模式下运行迁移。

    在这种情况下, 我们需要创建一个 Engine
    并将连接与上下文关联。
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在 'online' 模式下运行迁移。

    在这种情况下, 我们需要创建一个 Engine
    并将连接与上下文关联。
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
