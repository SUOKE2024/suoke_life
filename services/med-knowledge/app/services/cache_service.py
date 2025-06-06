"""
cache_service - 索克生活项目模块
"""

from app.core.logger import get_logger
from pydantic import BaseModel
from typing import Any
import json
import pickle
import redis

"""
缓存服务
提供Redis缓存功能,支持数据缓存和性能优化
"""




class CacheService:
    """缓存服务"""

    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.logger = get_logger()

    async def get(self, key: str, model_class: type | None = None) -> Any | None:
        """获取缓存数据"""
        try:
            data = await self.redis.get(key)
            if data is None:
                return None

            # 尝试JSON反序列化
            try:
                parsed_data = json.loads(data)
                if model_class and issubclass(model_class, BaseModel):
                    return model_class(**parsed_data)
                return parsed_data
            except (json.JSONDecodeError, TypeError):
                # 如果JSON反序列化失败,尝试pickle
                try:
                    return pickle.loads(data.encode("latin1"))
                except (pickle.PickleError, UnicodeDecodeError):
                    return data

        except Exception as e:
            self.logger.error(f"缓存获取失败 key={key}: {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl: int | None = None, serialize_method: str = "json"
    ) -> bool:
        """设置缓存数据"""
        try:
            ttl = ttl or self.default_ttl

            # 序列化数据
            if serialize_method == "json":
                if isinstance(value, BaseModel):
                    serialized_data = value.model_dump_json()
                else:
                    serialized_data = json.dumps(value, ensure_ascii=False)
            elif serialize_method == "pickle":
                serialized_data = pickle.dumps(value).decode("latin1")
            else:
                serialized_data = str(value)

            await self.redis.setex(key, ttl, serialized_data)
            return True

        except Exception as e:
            self.logger.error(f"缓存设置失败 key={key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"缓存删除失败 key={key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            self.logger.error(f"缓存检查失败 key={key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            self.logger.error(f"缓存过期设置失败 key={key}: {e}")
            return False

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """批量获取缓存数据"""
        try:
            values = await self.redis.mget(keys)
            result = {}

            for key, value in zip(keys, values, strict=False):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[key] = value

            return result

        except Exception as e:
            self.logger.error(f"批量缓存获取失败: {e}")
            return {}

    async def set_many(self, data: dict[str, Any], ttl: int | None = None) -> bool:
        """批量设置缓存数据"""
        try:
            ttl = ttl or self.default_ttl
            pipe = self.redis.pipeline()

            for key, value in data.items():
                if isinstance(value, BaseModel):
                    serialized_value = value.model_dump_json()
                else:
                    serialized_value = json.dumps(value, ensure_ascii=False)
                pipe.setex(key, ttl, serialized_value)

            await pipe.execute()
            return True

        except Exception as e:
            self.logger.error(f"批量缓存设置失败: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """根据模式删除缓存"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            self.logger.error(f"模式缓存删除失败 pattern={pattern}: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> int | None:
        """递增计数器"""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            self.logger.error(f"计数器递增失败 key={key}: {e}")
            return None

    async def decrement(self, key: str, amount: int = 1) -> int | None:
        """递减计数器"""
        try:
            return await self.redis.decrby(key, amount)
        except Exception as e:
            self.logger.error(f"计数器递减失败 key={key}: {e}")
            return None

    async def get_ttl(self, key: str) -> int | None:
        """获取缓存剩余过期时间"""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            self.logger.error(f"获取TTL失败 key={key}: {e}")
            return None

    async def clear_all(self) -> bool:
        """清空所有缓存"""
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            self.logger.error(f"清空缓存失败: {e}")
            return False

    async def get_info(self) -> dict[str, Any]:
        """获取Redis信息"""
        try:
            info = await self.redis.info()
            return {
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            self.logger.error(f"获取Redis信息失败: {e}")
            return {}

    async def close(self):
        """关闭Redis连接"""
        try:
            await self.redis.close()
            self.logger.info("Redis连接已关闭")
        except Exception as e:
            self.logger.error(f"关闭Redis连接失败: {e}")

class CacheKeys:
    """缓存键名常量"""

    # 体质相关
    CONSTITUTION_LIST = "constitutions:list"
    CONSTITUTION_DETAIL = "constitution:{constitution_id}"
    CONSTITUTION_RECOMMENDATIONS = "constitution:{constitution_id}:recommendations"

    # 症状相关
    SYMPTOM_LIST = "symptoms:list"
    SYMPTOM_DETAIL = "symptom:{symptom_id}"

    # 穴位相关
    ACUPOINT_LIST = "acupoints:list"
    ACUPOINT_DETAIL = "acupoint:{acupoint_id}"

    # 中药相关
    HERB_LIST = "herbs:list"
    HERB_DETAIL = "herb:{herb_id}"

    # 证型相关
    SYNDROME_LIST = "syndromes:list"
    SYNDROME_DETAIL = "syndrome:{syndrome_id}"
    SYNDROME_PATHWAYS = "syndrome:{syndrome_id}:pathways"

    # 搜索相关
    SEARCH_RESULT = "search:{query_hash}"

    # 知识图谱相关
    GRAPH_STATISTICS = "graph:statistics"
    GRAPH_VISUALIZATION = "graph:visualization"
    GRAPH_PATHS = "graph:paths:{from_id}:{to_id}"
    GRAPH_RELATIONSHIPS = "graph:node:{node_id}:relationships"
    GRAPH_SUBGRAPH = "graph:subgraph:{entity_type}:{entity_id}"

    # 中西医结合相关
    BIOMARKER_LIST = "biomarkers:list"
    BIOMARKER_DETAIL = "biomarker:{biomarker_id}"
    BIOMARKER_BY_CONSTITUTION = "biomarkers:constitution:{constitution_id}"

    WESTERN_DISEASE_LIST = "western_diseases:list"
    WESTERN_DISEASE_DETAIL = "western_disease:{disease_id}"
    WESTERN_DISEASE_BY_SYNDROME = "western_diseases:syndrome"

    # 预防医学证据相关
    PREVENTION_EVIDENCE_LIST = "prevention_evidence:list"
    PREVENTION_EVIDENCE_DETAIL = "prevention_evidence:{evidence_id}"

    # 中西医结合治疗相关
    INTEGRATED_TREATMENT_LIST = "integrated_treatments:list"
    INTEGRATED_TREATMENT_DETAIL = "integrated_treatment:{treatment_id}"

    # 生活方式干预相关
    LIFESTYLE_INTERVENTION_LIST = "lifestyle_interventions:list"
    LIFESTYLE_INTERVENTION_DETAIL = "lifestyle_intervention:{intervention_id}"
    LIFESTYLE_INTERVENTION_BY_CONSTITUTION = "lifestyle_interventions:constitution"

    # 统计信息
    API_STATS = "api:stats:{endpoint}"
    USER_ACTIVITY = "user:activity:{user_id}"

    @classmethod
    def format_key(cls, template: str, **kwargs) -> str:
        """格式化缓存键"""
        return template.format(**kwargs)
