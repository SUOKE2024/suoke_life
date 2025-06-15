"""
Alembic环境配置

用于数据库迁移的环境设置。
"""
import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入模型
from internal.db import Base
from internal.db.models import (
    UserModel, RoleModel, PermissionModel, UserRoleModel, RolePermissionModel,
    RefreshTokenModel, OAuthConnectionModel, MFASecretModel, 
    BiometricCredentialModel, AuditLogModel
)
from internal.config.settings import get_settings

# Alembic配置对象
config = context.config

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据
target_metadata = Base.metadata

# 获取设置
settings = get_settings()

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。

    这将配置上下文，只使用URL而不是Engine，
    尽管这里也需要一个Engine，但我们不创建连接。
    通过跳过Engine创建，我们甚至不需要DBAPI可用。

    调用context.execute()将发出给定的字符串到脚本输出。
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


def do_run_migrations(connection: Connection) -> None:
    """运行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在异步模式下运行迁移"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 