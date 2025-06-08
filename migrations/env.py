#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - Alembic迁移环境配置
Database Migration Environment Configuration
"""

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from logging.config import fileConfig
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.database import get_database_config

# Alembic配置对象
config = context.config

# 解释配置文件中的日志设置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 获取数据库配置
db_config = get_database_config()

# 设置数据库URL
config.set_main_option("sqlalchemy.url", db_config.primary_url)

# 导入所有模型以确保metadata正确配置
from services.user_service.user_service.models import Base as UserBase
from services.health_data_service.health_data_service.models import Base as HealthBase
from services.blockchain_service.suoke_blockchain_service.models import Base as BlockchainBase

# 合并所有metadata
target_metadata = UserBase.metadata

def run_migrations_offline():
    """
    在离线模式下运行迁移

    这种模式不需要实际连接数据库，而是通过配置中的URL
    生成SQL语句而不执行它们。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """执行迁移"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """在异步模式下运行迁移"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = db_config.primary_url

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

def run_migrations_online():
    """在在线模式下运行迁移"""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 