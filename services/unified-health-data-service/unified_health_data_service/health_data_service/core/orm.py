"""
ORM设置和配置
配置SQLAlchemy ORM和数据库连接
"""

import asyncio
import logging

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from ..models.health_data import Base

logger = logging.getLogger(__name__)

class ORMManager:
"""ORM管理器"""

    def __init__(self, config: dict[str, Any]):
    """初始化ORM管理器"""
self.config = config
self.async_engine = None
self.sync_engine = None
self.async_session_factory = None
self.sync_session_factory = None
self.metadata = Base.metadata

    async def initialize(self):
    """初始化ORM"""
try:
    # 创建异步引擎
await self._create_async_engine()

# 创建同步引擎（用于迁移等）
self._create_sync_engine()

# 创建会话工厂
self._create_session_factories()

# 设置事件监听器
self._setup_event_listeners()

logger.info("ORM初始化成功")

except Exception as e:
    logger.error(f"ORM初始化失败: {e}")
raise

    async def _create_async_engine(self):
    """创建异步数据库引擎"""
try:
    # 构建异步连接URL
db_config = self.config.get('database', {})
async_url = (
f"postgresql+asyncpg://"
f"{db_config.get('user', 'suoke_user')}:"
f"{db_config.get('password', 'suoke_password')}@"
f"{db_config.get('host', 'localhost')}:"
f"{db_config.get('port', 5432)}/"
f"{db_config.get('database', 'suoke_health_data')}"
)

# 引擎配置
engine_config = {
'echo': self.config.get('debug', False),
'pool_size': self.config.get('pool_size', 20),
'max_overflow': self.config.get('max_overflow', 30),
'pool_timeout': self.config.get('pool_timeout', 30),
'pool_recycle': self.config.get('pool_recycle', 3600),
'pool_pre_ping': True,
'poolclass': QueuePool
}

# SSL配置
ssl_config = self.config.get('ssl', {})
if ssl_config.get('enabled', False):
    engine_config['connect_args'] = {
'ssl': ssl_config.get('mode', 'prefer'),
'sslcert': ssl_config.get('cert'),
'sslkey': ssl_config.get('key'),
'sslrootcert': ssl_config.get('ca')
}

self.async_engine = create_async_engine(async_url,**engine_config)

# 测试连接
async with self.async_engine.begin() as conn:
    await conn.execute("SELECT 1")

logger.info("异步数据库引擎创建成功")

except Exception as e:
    logger.error(f"创建异步数据库引擎失败: {e}")
raise

    def _create_sync_engine(self):
    """创建同步数据库引擎"""
try:
    # 构建同步连接URL
db_config = self.config.get('database', {})
sync_url = (
f"postgresql://"
f"{db_config.get('user', 'suoke_user')}:"
f"{db_config.get('password', 'suoke_password')}@"
f"{db_config.get('host', 'localhost')}:"
f"{db_config.get('port', 5432)}/"
f"{db_config.get('database', 'suoke_health_data')}"
)

# 引擎配置
engine_config = {
'echo': self.config.get('debug', False),
'pool_size': 5,  # 同步引擎使用较小的连接池
'max_overflow': 10,
'pool_timeout': 30,
'pool_recycle': 3600,
'pool_pre_ping': True
}

self.sync_engine = create_engine(sync_url,**engine_config)

# 测试连接
with self.sync_engine.begin() as conn:
    conn.execute("SELECT 1")

logger.info("同步数据库引擎创建成功")

except Exception as e:
    logger.error(f"创建同步数据库引擎失败: {e}")
raise

    def _create_session_factories(self):
    """创建会话工厂"""
try:
    # 异步会话工厂
self.async_session_factory = async_sessionmaker(
bind=self.async_engine,
class_=AsyncSession,
expire_on_commit=False,
autoflush=True,
autocommit=False
)

# 同步会话工厂
self.sync_session_factory = sessionmaker(
bind=self.sync_engine,
class_=Session,
expire_on_commit=False,
autoflush=True,
autocommit=False
)

logger.info("会话工厂创建成功")

except Exception as e:
    logger.error(f"创建会话工厂失败: {e}")
raise

    def _setup_event_listeners(self):
    """设置事件监听器"""
try:
    # 连接事件监听器
@event.listens_for(self.async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """设置数据库连接参数"""
if hasattr(dbapi_connection, 'set_type_codec'):
    # PostgreSQL特定设置
pass

# 查询事件监听器（用于性能监控）
if self.config.get('monitoring', {}).get('enable_query_log', False):
    @event.listens_for(self.async_engine.sync_engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """查询执行前事件"""
context._query_start_time = asyncio.get_event_loop().time()

@event.listens_for(self.async_engine.sync_engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """查询执行后事件"""
total = asyncio.get_event_loop().time() - context._query_start_time

# 记录慢查询
slow_query_threshold = self.config.get('monitoring', {}).get('slow_query_threshold', 1.0)
if total > slow_query_threshold:
    logger.warning(f"慢查询检测: {total:.3f}s - {statement[:200]}...")

logger.info("事件监听器设置成功")

except Exception as e:
    logger.error(f"设置事件监听器失败: {e}")

    async def get_async_session(self) -> AsyncSession:
    """获取异步会话"""
if not self.async_session_factory:
    raise RuntimeError("ORM未初始化")
return self.async_session_factory()

    def get_sync_session(self) -> Session:
    """获取同步会话"""
if not self.sync_session_factory:
    raise RuntimeError("ORM未初始化")
return self.sync_session_factory()

    async def create_tables(self):
    """创建数据库表"""
try:
    async with self.async_engine.begin() as conn:
    await conn.run_sync(self.metadata.create_all)
logger.info("数据库表创建成功")

except Exception as e:
    logger.error(f"创建数据库表失败: {e}")
raise

    async def drop_tables(self):
    """删除数据库表"""
try:
    async with self.async_engine.begin() as conn:
    await conn.run_sync(self.metadata.drop_all)
logger.info("数据库表删除成功")

except Exception as e:
    logger.error(f"删除数据库表失败: {e}")
raise

    async def get_engine_status(self) -> dict[str, Any]:
    """获取引擎状态"""
try:
    status = {
'async_engine': {
'url': str(self.async_engine.url) if self.async_engine else None,
'pool_size': self.async_engine.pool.size() if self.async_engine else 0,
'checked_in': self.async_engine.pool.checkedin() if self.async_engine else 0,
'checked_out': self.async_engine.pool.checkedout() if self.async_engine else 0,
'overflow': self.async_engine.pool.overflow() if self.async_engine else 0
},
'sync_engine': {
'url': str(self.sync_engine.url) if self.sync_engine else None,
'pool_size': self.sync_engine.pool.size() if self.sync_engine else 0,
'checked_in': self.sync_engine.pool.checkedin() if self.sync_engine else 0,
'checked_out': self.sync_engine.pool.checkedout() if self.sync_engine else 0,
'overflow': self.sync_engine.pool.overflow() if self.sync_engine else 0
}
}

return status

except Exception as e:
    logger.error(f"获取引擎状态失败: {e}")
return {}

    async def health_check(self) -> bool:
    """健康检查"""
try:
    # 检查异步引擎
async with self.async_engine.begin() as conn:
    result = await conn.execute("SELECT 1")
await result.fetchone()

# 检查同步引擎
with self.sync_engine.begin() as conn:
    result = conn.execute("SELECT 1")
result.fetchone()

return True

except Exception as e:
    logger.error(f"ORM健康检查失败: {e}")
return False

    async def close(self):
    """关闭ORM连接"""
try:
    if self.async_engine:
    await self.async_engine.dispose()
logger.info("异步引擎已关闭")

if self.sync_engine:
    self.sync_engine.dispose()
logger.info("同步引擎已关闭")

except Exception as e:
    logger.error(f"关闭ORM连接失败: {e}")


class SessionManager:
"""会话管理器"""

    def __init__(self, orm_manager: ORMManager):
    """初始化会话管理器"""
self.orm_manager = orm_manager

    async def __aenter__(self) -> AsyncSession:
    """异步上下文管理器入口"""
self.session = await self.orm_manager.get_async_session()
return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
    """异步上下文管理器出口"""
try:
    if exc_type is None:
    await self.session.commit()
else:
    await self.session.rollback()
finally:
    await self.session.close()

    def __enter__(self) -> Session:
    """同步上下文管理器入口"""
self.session = self.orm_manager.get_sync_session()
return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
    """同步上下文管理器出口"""
try:
    if exc_type is None:
    self.session.commit()
else:
    self.session.rollback()
finally:
    self.session.close()


# 全局ORM管理器实例
_orm_manager: Optional[ORMManager] = None

async def initialize_orm(config: dict[str, Any]) -> ORMManager:
    """初始化全局ORM管理器"""
    global _orm_manager

    if _orm_manager is None:
    _orm_manager = ORMManager(config)
await _orm_manager.initialize()

    return _orm_manager

def get_orm_manager() -> ORMManager:
"""获取全局ORM管理器"""
    if _orm_manager is None:
    raise RuntimeError("ORM管理器未初始化")
    return _orm_manager

async def get_async_session() -> AsyncSession:
    """获取异步数据库会话"""
    orm_manager = get_orm_manager()
    return await orm_manager.get_async_session()

def get_sync_session() -> Session:
"""获取同步数据库会话"""
    orm_manager = get_orm_manager()
    return orm_manager.get_sync_session()

async def close_orm():
    """关闭ORM连接"""
    global _orm_manager

    if _orm_manager:
    await _orm_manager.close()
_orm_manager = None 
