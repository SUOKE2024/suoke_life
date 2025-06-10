"""
健康数据服务核心实现
提供健康数据的收集、处理、存储和查询功能
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthDataService:
"""
    健康数据服务
    负责健康数据的全生命周期管理
    """

    def __init__(self, database_service=None):
    """初始化健康数据服务"""
self.database_service = database_service
self.running = False

    async def start(self) -> None:
    """启动健康数据服务"""
try:
    # 初始化数据库连接
if self.database_service and not self.database_service.connected:
    await self.database_service.initialize()

self.running = True
logger.info("健康数据服务启动成功")

except Exception as e:
    logger.error(f"健康数据服务启动失败: {e}")
raise

    async def stop(self) -> None:
    """停止健康数据服务"""
self.running = False
logger.info("健康数据服务已停止")

    async def process_data(self, data: dict[str, Any]) -> dict[str, Any]:
    """处理健康数据"""
try:
    # 验证数据
validated_data = self._validate_data(data)

# 处理数据
processed_data = self._process_data(validated_data)

# 存储数据
data_id = await self.store_health_data(processed_data)

return {
"status": "success",
"data_id": data_id,
"processed_data": processed_data
}

except Exception as e:
    logger.error(f"健康数据处理失败: {e}")
return {
"status": "error",
"error": str(e)
}

    def _validate_data(self, data: dict[str, Any]) -> dict[str, Any]:
    """验证数据"""
# 基本验证
if not data.get('user_id'):
    raise ValueError("缺少用户ID")

if not data.get('data_type'):
    raise ValueError("缺少数据类型")

return data

    def _process_data(self, data: dict[str, Any]) -> dict[str, Any]:
    """处理数据"""
# 添加时间戳
data['processed_at'] = datetime.utcnow()

# 数据标准化
if data.get('data_type') == 'vital_signs':
    data = self._normalize_vital_signs(data)

return data

    def _normalize_vital_signs(self, data: dict[str, Any]) -> dict[str, Any]:
    """标准化生命体征数据"""
# 心率范围检查
if 'heart_rate' in data:
    hr = data['heart_rate']
if hr < 30 or hr > 200:
    data['heart_rate_warning'] = True

# 血压范围检查
if 'blood_pressure_systolic' in data and 'blood_pressure_diastolic' in data:
    sys_bp = data['blood_pressure_systolic']
dia_bp = data['blood_pressure_diastolic']
if sys_bp > 140 or dia_bp > 90:
    data['blood_pressure_warning'] = True

return data

    async def store_health_data(self, data: dict[str, Any]) -> str:
    """存储健康数据"""
if not self.database_service:
    # 模拟存储
return f"mock_id_{datetime.utcnow().timestamp()}"

try:
    # 根据数据类型选择存储策略
data_type = data.get('data_type', 'general')

if data_type == 'vital_signs':
    return await self._store_vital_signs(data)
elif data_type == 'diagnostic':
    return await self._store_diagnostic_data(data)
elif data_type == 'tcm':
    return await self._store_tcm_data(data)
else:
    return await self._store_general_health_data(data)

except Exception as e:
    logger.error(f"健康数据存储失败: {e}")
raise

    async def _store_vital_signs(self, data: dict[str, Any]) -> str:
    """存储生命体征数据"""
# 存储到PostgreSQL
pg_id = await self.database_service.store_data('vital_signs', {
'user_id': data['user_id'],
'heart_rate': data.get('heart_rate'),
'blood_pressure_systolic': data.get('blood_pressure_systolic'),
'blood_pressure_diastolic': data.get('blood_pressure_diastolic'),
'temperature': data.get('temperature'),
'oxygen_saturation': data.get('oxygen_saturation'),
'recorded_at': data.get('recorded_at', datetime.utcnow()),
'created_at': datetime.utcnow()
})

# 缓存最新数据
cache_key = f"vital_signs:latest:{data['user_id']}"
await self.database_service.cache_set(cache_key, data, expire=3600)

return pg_id

    async def _store_diagnostic_data(self, data: dict[str, Any]) -> str:
    """存储诊断数据"""
# 存储到PostgreSQL
pg_id = await self.database_service.store_data('diagnostic_data', {
'user_id': data['user_id'],
'diagnosis_type': data['diagnosis_type'],
'diagnosis_result': data['diagnosis_result'],
'confidence_score': data.get('confidence_score'),
'created_at': datetime.utcnow()
})

return pg_id

    async def _store_tcm_data(self, data: dict[str, Any]) -> str:
    """存储中医数据"""
# 存储到MongoDB（适合中医复杂数据结构）
mongo_id = await self.database_service.mongo_insert('tcm_data', {
'user_id': data['user_id'],
'diagnosis_method': data['diagnosis_method'],  # 望、闻、问、切
'symptoms': data.get('symptoms', []),
'constitution': data.get('constitution'),
'syndrome_differentiation': data.get('syndrome_differentiation'),
'treatment_plan': data.get('treatment_plan'),
'created_at': datetime.utcnow()
})

return mongo_id

    async def _store_general_health_data(self, data: dict[str, Any]) -> str:
    """存储一般健康数据"""
return await self.database_service.store_data('health_data', {
'user_id': data['user_id'],
'data_type': data['data_type'],
'data_value': data.get('data_value'),
'unit': data.get('unit'),
'source': data.get('source'),
'metadata': data.get('metadata'),
'created_at': datetime.utcnow()
})

    def get_service_status(self) -> dict[str, Any]:
    """获取服务状态"""
return {
"service_name": "health_data_service",
"running": self.running,
"database_connected": self.database_service.connected if self.database_service else False
}
