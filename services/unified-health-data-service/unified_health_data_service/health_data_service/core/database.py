"""
数据库服务核心模块
提供统一的数据库访问接口和事务管理
"""

import json
import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from pymongo import AsyncMongoClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseService:
"""
    统一数据库服务
    支持PostgreSQL、Redis、MongoDB多种数据库
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
    """初始化数据库服务"""
self.config = config or self._get_default_config()
self.pg_engine = None
self.pg_session_factory = None
self.redis_client = None
self.mongo_client = None
self.connected = False

    def _get_default_config(self) -> dict[str, Any]:
    """获取默认配置"""
return {
"postgresql": {
"url": "postgresql+asyncpg://postgres:password@localhost:5432/suoke_health",
"pool_size": 20,
"max_overflow": 30,
"pool_timeout": 30,
"pool_recycle": 3600
},
"redis": {
"url": "redis://localhost:6379/0",
"max_connections": 20,
"retry_on_timeout": True
},
"mongodb": {
"url": "mongodb://localhost:27017",
"database": "suoke_health"
}
}

    async def initialize(self) -> None:
    """初始化所有数据库连接"""
try:
    await self._init_postgresql()
await self._init_redis()
await self._init_mongodb()
self.connected = True
logger.info("数据库服务初始化完成")
except Exception as e:
    logger.error(f"数据库服务初始化失败: {e}")
raise

    async def _init_postgresql(self) -> None:
    """初始化PostgreSQL连接"""
pg_config = self.config["postgresql"]
self.pg_engine = create_async_engine(
pg_config["url"],
pool_size=pg_config["pool_size"],
max_overflow=pg_config["max_overflow"],
pool_timeout=pg_config["pool_timeout"],
pool_recycle=pg_config["pool_recycle"],
echo=False
)

self.pg_session_factory = async_sessionmaker(
self.pg_engine,
class_=AsyncSession,
expire_on_commit=False
)

# 测试连接
async with self.pg_engine.begin() as conn:
    await conn.execute(text("SELECT 1"))

logger.info("PostgreSQL连接初始化成功")

    async def _init_redis(self) -> None:
    """初始化Redis连接"""
redis_config = self.config["redis"]
self.redis_client = redis.from_url(
redis_config["url"],
max_connections=redis_config["max_connections"],
retry_on_timeout=redis_config["retry_on_timeout"]
)

# 测试连接
await self.redis_client.ping()
logger.info("Redis连接初始化成功")

    async def _init_mongodb(self) -> None:
    """初始化MongoDB连接"""
mongo_config = self.config["mongodb"]
self.mongo_client = AsyncMongoClient(mongo_config["url"])

# 测试连接
await self.mongo_client.admin.command('ping')
logger.info("MongoDB连接初始化成功")

    @asynccontextmanager
async def get_pg_session(self):
    """获取PostgreSQL会话"""
if not self.pg_session_factory:
    raise RuntimeError("PostgreSQL未初始化")

async with self.pg_session_factory() as session:
    try:
    yield session
except Exception:
    await session.rollback()
raise
finally:
    await session.close()

    async def execute_query(self, query: str, params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    """执行SQL查询"""
async with self.get_pg_session() as session:
    result = await session.execute(text(query), params or {})
return [dict(row._mapping) for row in result.fetchall()]

    async def execute_command(self, command: str, params: Optional[dict[str, Any]] = None) -> int:
    """执行SQL命令（INSERT、UPDATE、DELETE）"""
async with self.get_pg_session() as session:
    result = await session.execute(text(command), params or {})
await session.commit()
return result.rowcount

    async def store_data(self, table: str, data: dict[str, Any]) -> str:
    """存储数据到PostgreSQL"""
columns = list(data.keys())
values = list(data.values())
placeholders = [f":{col}" for col in columns]

query = f"""
INSERT INTO {table} ({', '.join(columns)})
VALUES ({', '.join(placeholders)})
RETURNING id
"""

async with self.get_pg_session() as session:
    result = await session.execute(text(query), data)
await session.commit()
return str(result.scalar())

    async def query_data(self, table: str, conditions: Optional[dict[str, Any]] = None, 
limit: Optional[int] = None, offset: Optional[int] = None) -> list[dict[str, Any]]:
    """查询数据"""
query = f"SELECT * FROM {table}"
params = {}

if conditions:
    where_clauses = []
for key, value in conditions.items():
    where_clauses.append(f"{key} = :{key}")
params[key] = value
query+=f" WHERE {' AND '.join(where_clauses)}"

if limit:
    query+=f" LIMIT {limit}"

if offset:
    query+=f" OFFSET {offset}"

return await self.execute_query(query, params)

    async def update_data(self, table: str, data: dict[str, Any], conditions: dict[str, Any]) -> int:
    """更新数据"""
set_clauses = [f"{key} = :{key}" for key in data.keys()]
where_clauses = [f"{key} = :where_{key}" for key in conditions.keys()]

query = f"""
UPDATE {table}
SET {', '.join(set_clauses)}
WHERE {' AND '.join(where_clauses)}
"""

params = {**data,**{f"where_{k}": v for k, v in conditions.items()}}
return await self.execute_command(query, params)

    async def delete_data(self, table: str, conditions: dict[str, Any]) -> int:
    """删除数据"""
where_clauses = [f"{key} = :{key}" for key in conditions.keys()]
query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
return await self.execute_command(query, conditions)

    # Redis操作
    async def cache_set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
    """设置缓存"""
if not self.redis_client:
    raise RuntimeError("Redis未初始化")

serialized_value = json.dumps(value) if not isinstance(value, str) else value
return await self.redis_client.set(key, serialized_value, ex=expire)

    async def cache_get(self, key: str) -> Optional[Any]:
    """获取缓存"""
if not self.redis_client:
    raise RuntimeError("Redis未初始化")

value = await self.redis_client.get(key)
if value is None:
    return None

try:
    return json.loads(value)
except json.JSONDecodeError:
    return value.decode('utf-8')

    async def cache_delete(self, key: str) -> bool:
    """删除缓存"""
if not self.redis_client:
    raise RuntimeError("Redis未初始化")

return bool(await self.redis_client.delete(key))

    async def cache_exists(self, key: str) -> bool:
    """检查缓存是否存在"""
if not self.redis_client:
    raise RuntimeError("Redis未初始化")

return bool(await self.redis_client.exists(key))

    # MongoDB操作
    async def mongo_insert(self, collection: str, document: dict[str, Any]) -> str:
    """插入MongoDB文档"""
if not self.mongo_client:
    raise RuntimeError("MongoDB未初始化")

db = self.mongo_client[self.config["mongodb"]["database"]]
result = await db[collection].insert_one(document)
return str(result.inserted_id)

    async def mongo_find(self, collection: str, filter_dict: Optional[dict[str, Any]] = None,
limit: Optional[int] = None) -> list[dict[str, Any]]:
    """查询MongoDB文档"""
if not self.mongo_client:
    raise RuntimeError("MongoDB未初始化")

db = self.mongo_client[self.config["mongodb"]["database"]]
cursor = db[collection].find(filter_dict or {})

if limit:
    cursor = cursor.limit(limit)

documents = []
async for doc in cursor:
    doc['_id'] = str(doc['_id'])  # 转换ObjectId为字符串
documents.append(doc)

return documents

    async def mongo_update(self, collection: str, filter_dict: dict[str, Any], 
update_dict: dict[str, Any]) -> int:
    """更新MongoDB文档"""
if not self.mongo_client:
    raise RuntimeError("MongoDB未初始化")

db = self.mongo_client[self.config["mongodb"]["database"]]
result = await db[collection].update_many(filter_dict, {"$set": update_dict})
return result.modified_count

    async def mongo_delete(self, collection: str, filter_dict: dict[str, Any]) -> int:
    """删除MongoDB文档"""
if not self.mongo_client:
    raise RuntimeError("MongoDB未初始化")

db = self.mongo_client[self.config["mongodb"]["database"]]
result = await db[collection].delete_many(filter_dict)
return result.deleted_count

    # 事务管理
    @asynccontextmanager
async def transaction(self):
    """数据库事务上下文管理器"""
async with self.get_pg_session() as session:
    async with session.begin():
    try:
    yield session
except Exception:
    await session.rollback()
raise

    async def close(self) -> None:
    """关闭所有数据库连接"""
if self.pg_engine:
    await self.pg_engine.dispose()

if self.redis_client:
    await self.redis_client.close()

if self.mongo_client:
    self.mongo_client.close()

self.connected = False
logger.info("数据库服务连接已关闭")

    def get_health_status(self) -> dict[str, Any]:
    """获取数据库服务健康状态"""
return {
"connected": self.connected,
"postgresql": bool(self.pg_engine),
"redis": bool(self.redis_client),
"mongodb": bool(self.mongo_client)
}
    """主函数 - 自动生成的最小可用版本"""
    pass

if __name__=="__main__":
    main()
