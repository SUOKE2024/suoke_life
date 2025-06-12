"""
健康数据仓储模式实现
提供数据访问层的抽象和具体实现
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from ..core.database import DatabaseService

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
"""基础仓储抽象类"""

    def __init__(self, database_service: DatabaseService):
    """初始化仓储"""
self.database_service = database_service

    @abstractmethod
async def create(self, data: dict[str, Any]) -> str:
    """创建数据"""
pass

    @abstractmethod
async def get_by_id(self, id: str) -> Optional[dict[str, Any]]:
    """根据ID获取数据"""
pass

    @abstractmethod
async def update(self, id: str, data: dict[str, Any]) -> bool:
    """更新数据"""
pass

    @abstractmethod
async def delete(self, id: str) -> bool:
    """删除数据"""
pass

    @abstractmethod
async def find(self, conditions: dict[str, Any], limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """查找数据"""
pass


class HealthDataRepository(BaseRepository):
"""健康数据仓储实现"""

    async def create(self, data: dict[str, Any]) -> str:
    """创建健康数据"""
try:
    # 添加时间戳
data['created_at'] = datetime.utcnow()
data['updated_at'] = datetime.utcnow()

# 存储到数据库
data_id = await self.database_service.store_data('health_data', data)

# 缓存最新数据
if data.get('user_id'):
    cache_key = f"health_data:latest:{data['user_id']}:{data.get('data_type', 'general')}"
await self.database_service.cache_set(cache_key, data, expire=3600)

logger.info(f"健康数据创建成功: {data_id}")
return data_id

except Exception as e:
    logger.error(f"创建健康数据失败: {e}")
raise

    async def get_by_id(self, id: str) -> Optional[dict[str, Any]]:
    """根据ID获取健康数据"""
try:
    # 先尝试从缓存获取
cache_key = f"health_data:id:{id}"
cached_data = await self.database_service.cache_get(cache_key)

if cached_data:
    return cached_data

# 从数据库查询
results = await self.database_service.query_data(
'health_data',
conditions={'id': id},
limit=1
)

if results:
    data = results[0]
# 更新缓存
await self.database_service.cache_set(cache_key, data, expire=1800)
return data

return None

except Exception as e:
    logger.error(f"根据ID获取健康数据失败: {e}")
return None

    async def update(self, id: str, data: dict[str, Any]) -> bool:
    """更新健康数据"""
try:
    # 添加更新时间戳
data['updated_at'] = datetime.utcnow()

# 更新数据库
affected_rows = await self.database_service.update_data(
'health_data',
data,
{'id': id}
)

if affected_rows > 0:
    # 清除相关缓存
await self._clear_related_cache(id)
logger.info(f"健康数据更新成功: {id}")
return True

return False

except Exception as e:
    logger.error(f"更新健康数据失败: {e}")
return False

    async def delete(self, id: str) -> bool:
    """删除健康数据"""
try:
    # 删除数据库记录
affected_rows = await self.database_service.delete_data(
'health_data',
{'id': id}
)

if affected_rows > 0:
    # 清除相关缓存
await self._clear_related_cache(id)
logger.info(f"健康数据删除成功: {id}")
return True

return False

except Exception as e:
    logger.error(f"删除健康数据失败: {e}")
return False

    async def find(self, conditions: dict[str, Any], limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """查找健康数据"""
try:
    # 构建缓存键
cache_key = f"health_data:query:{hash(str(sorted(conditions.items())))}:{limit}:{offset}"

# 尝试从缓存获取
cached_results = await self.database_service.cache_get(cache_key)
if cached_results:
    return cached_results

# 从数据库查询
results = await self.database_service.query_data(
'health_data',
conditions=conditions,
limit=limit,
offset=offset
)

# 缓存结果（较短时间）
if results:
    await self.database_service.cache_set(cache_key, results, expire=300)

return results

except Exception as e:
    logger.error(f"查找健康数据失败: {e}")
return []

    async def find_by_user_and_type(self, user_id: str, data_type: str, 
start_date: Optional[datetime] = None,
end_date: Optional[datetime] = None,
limit: int = 100) -> list[dict[str, Any]]:
    """根据用户ID和数据类型查找数据"""
try:
    conditions = {
'user_id': user_id,
'data_type': data_type
}

# 添加时间范围条件（这里需要更复杂的SQL查询实现）
# 暂时简化处理

return await self.find(conditions, limit=limit)

except Exception as e:
    logger.error(f"根据用户和类型查找数据失败: {e}")
return []

    async def get_latest_by_user_and_type(self, user_id: str, data_type: str) -> Optional[dict[str, Any]]:
    """获取用户最新的特定类型数据"""
try:
    # 先尝试从缓存获取
cache_key = f"health_data:latest:{user_id}:{data_type}"
cached_data = await self.database_service.cache_get(cache_key)

if cached_data:
    return cached_data

# 从数据库查询最新记录
results = await self.find(
{'user_id': user_id, 'data_type': data_type},
limit=1
)

if results:
    latest_data = results[0]
# 缓存最新数据
await self.database_service.cache_set(cache_key, latest_data, expire=3600)
return latest_data

return None

except Exception as e:
    logger.error(f"获取最新数据失败: {e}")
return None

    async def count_by_conditions(self, conditions: dict[str, Any]) -> int:
    """根据条件统计数据数量"""
try:
    # 这里需要实现count查询
# 暂时通过查询所有数据来统计
results = await self.find(conditions, limit=10000)
return len(results)

except Exception as e:
    logger.error(f"统计数据数量失败: {e}")
return 0

    async def _clear_related_cache(self, id: str):
    """清除相关缓存"""
try:
    # 获取数据信息以清除相关缓存
data = await self.get_by_id(id)
if data:
    user_id = data.get('user_id')
data_type = data.get('data_type')

# 清除相关缓存键
cache_keys = [
f"health_data:id:{id}",
f"health_data:latest:{user_id}:{data_type}",
f"health_data:latest:{user_id}:general"
]

for key in cache_keys:
    await self.database_service.cache_delete(key)

except Exception as e:
    logger.error(f"清除缓存失败: {e}")


class VitalSignsRepository(BaseRepository):
"""生命体征仓储实现"""

    async def create(self, data: dict[str, Any]) -> str:
    """创建生命体征数据"""
try:
    # 添加时间戳
data['created_at'] = datetime.utcnow()
data['updated_at'] = datetime.utcnow()

if 'recorded_at' not in data:
    data['recorded_at'] = datetime.utcnow()

# 存储到数据库
data_id = await self.database_service.store_data('vital_signs', data)

# 缓存最新生命体征
if data.get('user_id'):
    cache_key = f"vital_signs:latest:{data['user_id']}"
await self.database_service.cache_set(cache_key, data, expire=3600)

logger.info(f"生命体征数据创建成功: {data_id}")
return data_id

except Exception as e:
    logger.error(f"创建生命体征数据失败: {e}")
raise

    async def get_by_id(self, id: str) -> Optional[dict[str, Any]]:
    """根据ID获取生命体征数据"""
try:
    results = await self.database_service.query_data(
'vital_signs',
conditions={'id': id},
limit=1
)

return results[0] if results else None

except Exception as e:
    logger.error(f"根据ID获取生命体征数据失败: {e}")
return None

    async def update(self, id: str, data: dict[str, Any]) -> bool:
    """更新生命体征数据"""
try:
    data['updated_at'] = datetime.utcnow()

affected_rows = await self.database_service.update_data(
'vital_signs',
data,
{'id': id}
)

if affected_rows > 0:
    # 清除相关缓存
await self._clear_vital_signs_cache(id)
return True

return False

except Exception as e:
    logger.error(f"更新生命体征数据失败: {e}")
return False

    async def delete(self, id: str) -> bool:
    """删除生命体征数据"""
try:
    affected_rows = await self.database_service.delete_data(
'vital_signs',
{'id': id}
)

if affected_rows > 0:
    await self._clear_vital_signs_cache(id)
return True

return False

except Exception as e:
    logger.error(f"删除生命体征数据失败: {e}")
return False

    async def find(self, conditions: dict[str, Any], limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """查找生命体征数据"""
try:
    return await self.database_service.query_data(
'vital_signs',
conditions=conditions,
limit=limit,
offset=offset
)

except Exception as e:
    logger.error(f"查找生命体征数据失败: {e}")
return []

    async def get_latest_by_user(self, user_id: str) -> Optional[dict[str, Any]]:
    """获取用户最新生命体征"""
try:
    # 先尝试从缓存获取
cache_key = f"vital_signs:latest:{user_id}"
cached_data = await self.database_service.cache_get(cache_key)

if cached_data:
    return cached_data

# 从数据库查询
results = await self.find({'user_id': user_id}, limit=1)

if results:
    latest_data = results[0]
# 更新缓存
await self.database_service.cache_set(cache_key, latest_data, expire=3600)
return latest_data

return None

except Exception as e:
    logger.error(f"获取最新生命体征失败: {e}")
return None

    async def get_trends(self, user_id: str, days: int = 30) -> list[dict[str, Any]]:
    """获取生命体征趋势数据"""
try:
    # 计算时间范围
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=days)

# 查询时间范围内的数据
# 这里需要更复杂的时间范围查询实现
results = await self.find({'user_id': user_id}, limit=1000)

# 简单过滤（实际应该在SQL层面处理）
filtered_results = []
for result in results:
    recorded_at = result.get('recorded_at')
if recorded_at and isinstance(recorded_at, datetime):
    if start_date<=recorded_at<=end_date:
    filtered_results.append(result)

return filtered_results

except Exception as e:
    logger.error(f"获取生命体征趋势失败: {e}")
return []

    async def _clear_vital_signs_cache(self, id: str):
    """清除生命体征相关缓存"""
try:
    data = await self.get_by_id(id)
if data and data.get('user_id'):
    cache_key = f"vital_signs:latest:{data['user_id']}"
await self.database_service.cache_delete(cache_key)

except Exception as e:
    logger.error(f"清除生命体征缓存失败: {e}")


class DiagnosticDataRepository(BaseRepository):
"""诊断数据仓储实现"""

    async def create(self, data: dict[str, Any]) -> str:
    """创建诊断数据"""
try:
    # 添加时间戳
data['created_at'] = datetime.utcnow()
data['updated_at'] = datetime.utcnow()

# 存储到PostgreSQL
pg_id = await self.database_service.store_data('diagnostic_data', data)

# 同时存储到MongoDB（用于复杂查询）
mongo_data = data.copy()
mongo_data['pg_id'] = pg_id
mongo_id = await self.database_service.mongo_insert('diagnostic_data', mongo_data)

logger.info(f"诊断数据创建成功: PG={pg_id}, Mongo={mongo_id}")
return pg_id

except Exception as e:
    logger.error(f"创建诊断数据失败: {e}")
raise

    async def get_by_id(self, id: str) -> Optional[dict[str, Any]]:
    """根据ID获取诊断数据"""
try:
    results = await self.database_service.query_data(
'diagnostic_data',
conditions={'id': id},
limit=1
)

return results[0] if results else None

except Exception as e:
    logger.error(f"根据ID获取诊断数据失败: {e}")
return None

    async def update(self, id: str, data: dict[str, Any]) -> bool:
    """更新诊断数据"""
try:
    data['updated_at'] = datetime.utcnow()

# 更新PostgreSQL
affected_rows = await self.database_service.update_data(
'diagnostic_data',
data,
{'id': id}
)

# 同时更新MongoDB
if affected_rows > 0:
    await self.database_service.mongo_update(
'diagnostic_data',
{'pg_id': id},
{'$set': data}
)
return True

return False

except Exception as e:
    logger.error(f"更新诊断数据失败: {e}")
return False

    async def delete(self, id: str) -> bool:
    """删除诊断数据"""
try:
    # 删除PostgreSQL记录
affected_rows = await self.database_service.delete_data(
'diagnostic_data',
{'id': id}
)

# 删除MongoDB记录
if affected_rows > 0:
    await self.database_service.mongo_delete(
'diagnostic_data',
{'pg_id': id}
)
return True

return False

except Exception as e:
    logger.error(f"删除诊断数据失败: {e}")
return False

    async def find(self, conditions: dict[str, Any], limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """查找诊断数据"""
try:
    return await self.database_service.query_data(
'diagnostic_data',
conditions=conditions,
limit=limit,
offset=offset
)

except Exception as e:
    logger.error(f"查找诊断数据失败: {e}")
return []

    async def find_by_user(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """根据用户ID查找诊断数据"""
return await self.find({'user_id': user_id}, limit=limit)

    async def find_by_type(self, diagnosis_type: str, limit: int = 100) -> list[dict[str, Any]]:
    """根据诊断类型查找数据"""
return await self.find({'diagnosis_type': diagnosis_type}, limit=limit)


class RepositoryFactory:
"""仓储工厂类"""

    def __init__(self, database_service: DatabaseService):
    """初始化工厂"""
self.database_service = database_service
self._repositories = {}

    def get_health_data_repository(self) -> HealthDataRepository:
    """获取健康数据仓储"""
if 'health_data' not in self._repositories:
    self._repositories['health_data'] = HealthDataRepository(self.database_service)
return self._repositories['health_data']

    def get_vital_signs_repository(self) -> VitalSignsRepository:
    """获取生命体征仓储"""
if 'vital_signs' not in self._repositories:
    self._repositories['vital_signs'] = VitalSignsRepository(self.database_service)
return self._repositories['vital_signs']

    def get_diagnostic_data_repository(self) -> DiagnosticDataRepository:
    """获取诊断数据仓储"""
if 'diagnostic_data' not in self._repositories:
    self._repositories['diagnostic_data'] = DiagnosticDataRepository(self.database_service)
return self._repositories['diagnostic_data'] 
