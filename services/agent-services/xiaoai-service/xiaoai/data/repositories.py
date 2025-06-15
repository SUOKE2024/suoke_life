"""
数据仓库层

提供数据持久化和查询功能
"""

from abc import ABC, abstractmethod
import asyncio
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
import logging
from typing import Any, Dict, List, Optional, Union
import uuid

import asyncpg
import redis.asyncio as redis
from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config.settings import get_settings
from ..core.five_diagnosis_coordinator import DiagnosisResult, DiagnosisSession
from ..core.recommendation_engine import Recommendation, RecommendationPlan
from ..utils.exceptions import DatabaseError, DataNotFoundError

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """仓库基类"""
    
    def __init__(self):
        self.settings = get_settings()
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化仓库"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭仓库连接"""
        pass


class PostgreSQLRepository(BaseRepository):
    """PostgreSQL数据仓库"""
    
    def __init__(self):
        super().__init__()
        self.engine = None
        self.session_factory = None
        self.pool = None
    
    async def initialize(self) -> None:
        """初始化PostgreSQL连接"""
        try:
            # 创建异步引擎
            database_url = (
                f"postgresql+asyncpg://"
                f"{self.settings.database.user}:"
                f"{self.settings.database.password}@"
                f"{self.settings.database.host}:"
                f"{self.settings.database.port}/"
                f"{self.settings.database.name}"
            )
            
            self.engine = create_async_engine(
                database_url,
                echo=self.settings.database.echo,
                pool_size=self.settings.database.pool_size,
                max_overflow=self.settings.database.max_overflow,
                pool_timeout=self.settings.database.pool_timeout,
                pool_recycle=self.settings.database.pool_recycle
            )
            
            # 创建会话工厂
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 创建连接池
            self.pool = await asyncpg.create_pool(
                host=self.settings.database.host,
                port=self.settings.database.port,
                user=self.settings.database.user,
                password=self.settings.database.password,
                database=self.settings.database.name,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            logger.info("PostgreSQL数据仓库初始化成功")
            
        except Exception as e:
            logger.error(f"PostgreSQL数据仓库初始化失败: {e}")
            raise DatabaseError(f"无法连接到PostgreSQL数据库: {e}")
    
    async def close(self) -> None:
        """关闭PostgreSQL连接"""
        try:
            if self.pool:
                await self.pool.close()
            if self.engine:
                await self.engine.dispose()
            logger.info("PostgreSQL数据仓库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭PostgreSQL连接失败: {e}")
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        if not self.session_factory:
            raise DatabaseError("数据库未初始化")
        return self.session_factory()
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        if not self.pool:
            raise DatabaseError("数据库连接池未初始化")
        
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetch(query, *(params.values() if params else []))
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise DatabaseError(f"查询执行失败: {e}")
    
    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> str:
        """执行命令"""
        if not self.pool:
            raise DatabaseError("数据库连接池未初始化")
        
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(command, *(params.values() if params else []))
                return result
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            raise DatabaseError(f"命令执行失败: {e}")


class RedisRepository(BaseRepository):
    """Redis数据仓库"""
    
    def __init__(self):
        super().__init__()
        self.redis_client = None
    
    async def initialize(self) -> None:
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=self.settings.cache.redis.host,
                port=self.settings.cache.redis.port,
                password=self.settings.cache.redis.password,
                db=self.settings.cache.redis.db,
                decode_responses=True,
                socket_timeout=self.settings.cache.redis.socket_timeout,
                socket_connect_timeout=self.settings.cache.redis.socket_connect_timeout,
                retry_on_timeout=True,
                max_connections=self.settings.cache.redis.max_connections
            )
            
            # 测试连接
            await self.redis_client.ping()
            
            logger.info("Redis数据仓库初始化成功")
            
        except Exception as e:
            logger.error(f"Redis数据仓库初始化失败: {e}")
            raise DatabaseError(f"无法连接到Redis: {e}")
    
    async def close(self) -> None:
        """关闭Redis连接"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Redis数据仓库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭Redis连接失败: {e}")
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            return None
    
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            return await self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            return bool(await self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis存在性检查失败: {e}")
            return False


class DiagnosisRepository:
    """诊断数据仓库"""
    
    def __init__(self, pg_repo: PostgreSQLRepository, redis_repo: RedisRepository):
        self.pg_repo = pg_repo
        self.redis_repo = redis_repo
    
    async def save_diagnosis_session(self, session: DiagnosisSession) -> str:
        """保存诊断会话"""
        try:
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "metadata": json.dumps(session.metadata)
            }
            
            # 保存到PostgreSQL
            query = \"\"\"\n                INSERT INTO diagnosis_sessions \n                (session_id, user_id, status, created_at, updated_at, metadata)\n                VALUES ($1, $2, $3, $4, $5, $6)\n                ON CONFLICT (session_id) DO UPDATE SET\n                    status = EXCLUDED.status,\n                    updated_at = EXCLUDED.updated_at,\n                    metadata = EXCLUDED.metadata\n            \"\"\"\n            \n            await self.pg_repo.execute_command(query, {\n                \"session_id\": session.session_id,\n                \"user_id\": session.user_id,\n                \"status\": session.status.value,\n                \"created_at\": session.created_at,\n                \"updated_at\": session.updated_at,\n                \"metadata\": json.dumps(session.metadata)\n            })\n            \n            # 缓存到Redis\n            cache_key = f\"diagnosis_session:{session.session_id}\"\n            await self.redis_repo.set(\n                cache_key, \n                json.dumps(session_data), \n                expire=3600  # 1小时过期\n            )\n            \n            logger.info(f\"诊断会话保存成功: {session.session_id}\")\n            return session.session_id\n            \n        except Exception as e:\n            logger.error(f\"保存诊断会话失败: {e}\")\n            raise DatabaseError(f\"保存诊断会话失败: {e}\")\n    \n    async def get_diagnosis_session(self, session_id: str) -> Optional[DiagnosisSession]:\n        \"\"\"获取诊断会话\"\"\"\n        try:\n            # 先从Redis缓存获取\n            cache_key = f\"diagnosis_session:{session_id}\"\n            cached_data = await self.redis_repo.get(cache_key)\n            \n            if cached_data:\n                data = json.loads(cached_data)\n                return self._dict_to_diagnosis_session(data)\n            \n            # 从PostgreSQL获取\n            query = \"\"\"\n                SELECT session_id, user_id, status, created_at, updated_at, metadata\n                FROM diagnosis_sessions\n                WHERE session_id = $1\n            \"\"\"\n            \n            result = await self.pg_repo.execute_query(query, {\"session_id\": session_id})\n            \n            if not result:\n                return None\n            \n            session_data = result[0]\n            \n            # 更新缓存\n            await self.redis_repo.set(\n                cache_key,\n                json.dumps(session_data, default=str),\n                expire=3600\n            )\n            \n            return self._dict_to_diagnosis_session(session_data)\n            \n        except Exception as e:\n            logger.error(f\"获取诊断会话失败: {e}\")\n            raise DatabaseError(f\"获取诊断会话失败: {e}\")\n    \n    async def save_diagnosis_result(self, result: DiagnosisResult) -> str:\n        \"\"\"保存诊断结果\"\"\"\n        try:\n            result_id = str(uuid.uuid4())\n            \n            result_data = {\n                \"result_id\": result_id,\n                \"session_id\": result.session_id,\n                \"user_id\": result.user_id,\n                \"diagnosis_type\": result.diagnosis_type.value,\n                \"status\": result.status.value,\n                \"confidence\": result.confidence,\n                \"features\": json.dumps(result.features),\n                \"raw_data\": json.dumps(result.raw_data),\n                \"processing_time_ms\": result.processing_time_ms,\n                \"error_message\": result.error_message,\n                \"created_at\": result.timestamp.isoformat()\n            }\n            \n            # 保存到PostgreSQL\n            query = \"\"\"\n                INSERT INTO diagnosis_results \n                (result_id, session_id, user_id, diagnosis_type, status, confidence, \n                 features, raw_data, processing_time_ms, error_message, created_at)\n                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)\n            \"\"\"\n            \n            await self.pg_repo.execute_command(query, result_data)\n            \n            # 缓存到Redis\n            cache_key = f\"diagnosis_result:{result_id}\"\n            await self.redis_repo.set(\n                cache_key,\n                json.dumps(result_data),\n                expire=7200  # 2小时过期\n            )\n            \n            logger.info(f\"诊断结果保存成功: {result_id}\")\n            return result_id\n            \n        except Exception as e:\n            logger.error(f\"保存诊断结果失败: {e}\")\n            raise DatabaseError(f\"保存诊断结果失败: {e}\")\n    \n    async def get_diagnosis_results_by_session(self, session_id: str) -> List[DiagnosisResult]:\n        \"\"\"根据会话ID获取诊断结果\"\"\"\n        try:\n            query = \"\"\"\n                SELECT result_id, session_id, user_id, diagnosis_type, status, confidence,\n                       features, raw_data, processing_time_ms, error_message, created_at\n                FROM diagnosis_results\n                WHERE session_id = $1\n                ORDER BY created_at DESC\n            \"\"\"\n            \n            results = await self.pg_repo.execute_query(query, {\"session_id\": session_id})\n            \n            diagnosis_results = []\n            for result_data in results:\n                diagnosis_result = self._dict_to_diagnosis_result(result_data)\n                diagnosis_results.append(diagnosis_result)\n            \n            return diagnosis_results\n            \n        except Exception as e:\n            logger.error(f\"获取诊断结果失败: {e}\")\n            raise DatabaseError(f\"获取诊断结果失败: {e}\")\n    \n    async def get_user_diagnosis_history(\n        self, \n        user_id: str, \n        limit: int = 10,\n        offset: int = 0\n    ) -> List[Dict[str, Any]]:\n        \"\"\"获取用户诊断历史\"\"\"\n        try:\n            query = \"\"\"\n                SELECT ds.session_id, ds.status, ds.created_at, ds.updated_at,\n                       COUNT(dr.result_id) as result_count\n                FROM diagnosis_sessions ds\n                LEFT JOIN diagnosis_results dr ON ds.session_id = dr.session_id\n                WHERE ds.user_id = $1\n                GROUP BY ds.session_id, ds.status, ds.created_at, ds.updated_at\n                ORDER BY ds.created_at DESC\n                LIMIT $2 OFFSET $3\n            \"\"\"\n            \n            results = await self.pg_repo.execute_query(query, {\n                \"user_id\": user_id,\n                \"limit\": limit,\n                \"offset\": offset\n            })\n            \n            return results\n            \n        except Exception as e:\n            logger.error(f\"获取用户诊断历史失败: {e}\")\n            raise DatabaseError(f\"获取用户诊断历史失败: {e}\")\n    \n    def _dict_to_diagnosis_session(self, data: Dict[str, Any]) -> DiagnosisSession:\n        \"\"\"将字典转换为DiagnosisSession对象\"\"\"\n        from ..core.five_diagnosis_coordinator import SessionStatus\n        \n        return DiagnosisSession(\n            session_id=data[\"session_id\"],\n            user_id=data[\"user_id\"],\n            status=SessionStatus(data[\"status\"]),\n            created_at=datetime.fromisoformat(data[\"created_at\"]),\n            updated_at=datetime.fromisoformat(data[\"updated_at\"]),\n            metadata=json.loads(data[\"metadata\"]) if data[\"metadata\"] else {}\n        )\n    \n    def _dict_to_diagnosis_result(self, data: Dict[str, Any]) -> DiagnosisResult:\n        \"\"\"将字典转换为DiagnosisResult对象\"\"\"\n        from ..core.five_diagnosis_coordinator import DiagnosisType, DiagnosisStatus\n        \n        return DiagnosisResult(\n            session_id=data[\"session_id\"],\n            user_id=data[\"user_id\"],\n            diagnosis_type=DiagnosisType(data[\"diagnosis_type\"]),\n            status=DiagnosisStatus(data[\"status\"]),\n            confidence=data[\"confidence\"],\n            features=json.loads(data[\"features\"]) if data[\"features\"] else {},\n            raw_data=json.loads(data[\"raw_data\"]) if data[\"raw_data\"] else {},\n            processing_time_ms=data[\"processing_time_ms\"],\n            error_message=data[\"error_message\"],\n            timestamp=datetime.fromisoformat(data[\"created_at\"])\n        )\n\n\nclass RecommendationRepository:\n    \"\"\"建议数据仓库\"\"\"\n    \n    def __init__(self, pg_repo: PostgreSQLRepository, redis_repo: RedisRepository):\n        self.pg_repo = pg_repo\n        self.redis_repo = redis_repo\n    \n    async def save_recommendation_plan(self, plan: RecommendationPlan) -> str:\n        \"\"\"保存建议方案\"\"\"\n        try:\n            # 保存方案基本信息\n            plan_data = {\n                \"plan_id\": plan.plan_id,\n                \"user_id\": plan.user_id,\n                \"session_id\": plan.session_id,\n                \"overall_strategy\": plan.overall_strategy,\n                \"implementation_order\": json.dumps(plan.implementation_order),\n                \"monitoring_points\": json.dumps(plan.monitoring_points),\n                \"follow_up_schedule\": json.dumps(plan.follow_up_schedule),\n                \"created_at\": plan.created_at.isoformat(),\n                \"valid_until\": plan.valid_until.isoformat()\n            }\n            \n            # 保存方案到PostgreSQL\n            plan_query = \"\"\"\n                INSERT INTO recommendation_plans \n                (plan_id, user_id, session_id, overall_strategy, implementation_order,\n                 monitoring_points, follow_up_schedule, created_at, valid_until)\n                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)\n                ON CONFLICT (plan_id) DO UPDATE SET\n                    overall_strategy = EXCLUDED.overall_strategy,\n                    implementation_order = EXCLUDED.implementation_order,\n                    monitoring_points = EXCLUDED.monitoring_points,\n                    follow_up_schedule = EXCLUDED.follow_up_schedule\n            \"\"\"\n            \n            await self.pg_repo.execute_command(plan_query, plan_data)\n            \n            # 保存建议到PostgreSQL\n            for recommendation in plan.recommendations:\n                await self.save_recommendation(recommendation, plan.plan_id)\n            \n            # 缓存到Redis\n            cache_key = f\"recommendation_plan:{plan.plan_id}\"\n            cache_data = {\n               **plan_data,\n                \"recommendations\": [asdict(rec) for rec in plan.recommendations]\n            }\n            \n            await self.redis_repo.set(\n                cache_key,\n                json.dumps(cache_data, default=str),\n                expire=86400  # 24小时过期\n            )\n            \n            logger.info(f\"建议方案保存成功: {plan.plan_id}\")\n            return plan.plan_id\n            \n        except Exception as e:\n            logger.error(f\"保存建议方案失败: {e}\")\n            raise DatabaseError(f\"保存建议方案失败: {e}\")\n    \n    async def save_recommendation(self, recommendation: Recommendation, plan_id: str) -> str:\n        \"\"\"保存单个建议\"\"\"\n        try:\n            rec_data = {\n                \"recommendation_id\": recommendation.id,\n                \"plan_id\": plan_id,\n                \"type\": recommendation.type.value,\n                \"title\": recommendation.title,\n                \"description\": recommendation.description,\n                \"priority\": recommendation.priority.value,\n                \"confidence\": recommendation.confidence,\n                \"evidence\": json.dumps(recommendation.evidence),\n                \"contraindications\": json.dumps(recommendation.contraindications),\n                \"duration\": recommendation.duration,\n                \"frequency\": recommendation.frequency,\n                \"dosage\": recommendation.dosage,\n                \"precautions\": json.dumps(recommendation.precautions),\n                \"related_syndromes\": json.dumps(recommendation.related_syndromes),\n                \"related_constitution\": json.dumps(recommendation.related_constitution),\n                \"created_at\": recommendation.created_at.isoformat(),\n                \"expires_at\": recommendation.expires_at.isoformat() if recommendation.expires_at else None\n            }\n            \n            query = \"\"\"\n                INSERT INTO recommendations \n                (recommendation_id, plan_id, type, title, description, priority, confidence,\n                 evidence, contraindications, duration, frequency, dosage, precautions,\n                 related_syndromes, related_constitution, created_at, expires_at)\n                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)\n                ON CONFLICT (recommendation_id) DO UPDATE SET\n                    title = EXCLUDED.title,\n                    description = EXCLUDED.description,\n                    priority = EXCLUDED.priority,\n                    confidence = EXCLUDED.confidence\n            \"\"\"\n            \n            await self.pg_repo.execute_command(query, rec_data)\n            \n            return recommendation.id\n            \n        except Exception as e:\n            logger.error(f\"保存建议失败: {e}\")\n            raise DatabaseError(f\"保存建议失败: {e}\")\n    \n    async def get_recommendation_plan(self, plan_id: str) -> Optional[RecommendationPlan]:\n        \"\"\"获取建议方案\"\"\"\n        try:\n            # 先从Redis缓存获取\n            cache_key = f\"recommendation_plan:{plan_id}\"\n            cached_data = await self.redis_repo.get(cache_key)\n            \n            if cached_data:\n                data = json.loads(cached_data)\n                return self._dict_to_recommendation_plan(data)\n            \n            # 从PostgreSQL获取\n            plan_query = \"\"\"\n                SELECT plan_id, user_id, session_id, overall_strategy, implementation_order,\n                       monitoring_points, follow_up_schedule, created_at, valid_until\n                FROM recommendation_plans\n                WHERE plan_id = $1\n            \"\"\"\n            \n            plan_result = await self.pg_repo.execute_query(plan_query, {\"plan_id\": plan_id})\n            \n            if not plan_result:\n                return None\n            \n            plan_data = plan_result[0]\n            \n            # 获取建议列表\n            rec_query = \"\"\"\n                SELECT recommendation_id, type, title, description, priority, confidence,\n                       evidence, contraindications, duration, frequency, dosage, precautions,\n                       related_syndromes, related_constitution, created_at, expires_at\n                FROM recommendations\n                WHERE plan_id = $1\n                ORDER BY priority DESC, created_at ASC\n            \"\"\"\n            \n            rec_results = await self.pg_repo.execute_query(rec_query, {\"plan_id\": plan_id})\n            \n            recommendations = []\n            for rec_data in rec_results:\n                recommendation = self._dict_to_recommendation(rec_data)\n                recommendations.append(recommendation)\n            \n            plan_data[\"recommendations\"] = recommendations\n            \n            # 更新缓存\n            cache_data = {\n               **plan_data,\n                \"recommendations\": [asdict(rec) for rec in recommendations]\n            }\n            \n            await self.redis_repo.set(\n                cache_key,\n                json.dumps(cache_data, default=str),\n                expire=86400\n            )\n            \n            return self._dict_to_recommendation_plan(plan_data)\n            \n        except Exception as e:\n            logger.error(f\"获取建议方案失败: {e}\")\n            raise DatabaseError(f\"获取建议方案失败: {e}\")\n    \n    async def get_user_recommendation_history(\n        self, \n        user_id: str, \n        limit: int = 10,\n        offset: int = 0\n    ) -> List[Dict[str, Any]]:\n        \"\"\"获取用户建议历史\"\"\"\n        try:\n            query = \"\"\"\n                SELECT rp.plan_id, rp.session_id, rp.overall_strategy, rp.created_at,\n                       COUNT(r.recommendation_id) as recommendation_count\n                FROM recommendation_plans rp\n                LEFT JOIN recommendations r ON rp.plan_id = r.plan_id\n                WHERE rp.user_id = $1 AND rp.valid_until > NOW()\n                GROUP BY rp.plan_id, rp.session_id, rp.overall_strategy, rp.created_at\n                ORDER BY rp.created_at DESC\n                LIMIT $2 OFFSET $3\n            \"\"\"\n            \n            results = await self.pg_repo.execute_query(query, {\n                \"user_id\": user_id,\n                \"limit\": limit,\n                \"offset\": offset\n            })\n            \n            return results\n            \n        except Exception as e:\n            logger.error(f\"获取用户建议历史失败: {e}\")\n            raise DatabaseError(f\"获取用户建议历史失败: {e}\")\n    \n    def _dict_to_recommendation_plan(self, data: Dict[str, Any]) -> RecommendationPlan:\n        \"\"\"将字典转换为RecommendationPlan对象\"\"\"\n        recommendations = []\n        if \"recommendations\" in data:\n            for rec_data in data[\"recommendations\"]:\n                if isinstance(rec_data, dict):\n                    recommendation = self._dict_to_recommendation(rec_data)\n                    recommendations.append(recommendation)\n        \n        return RecommendationPlan(\n            plan_id=data[\"plan_id\"],\n            user_id=data[\"user_id\"],\n            session_id=data[\"session_id\"],\n            recommendations=recommendations,\n            overall_strategy=data[\"overall_strategy\"],\n            implementation_order=json.loads(data[\"implementation_order\"]) if data[\"implementation_order\"] else [],\n            monitoring_points=json.loads(data[\"monitoring_points\"]) if data[\"monitoring_points\"] else [],\n            follow_up_schedule=json.loads(data[\"follow_up_schedule\"]) if data[\"follow_up_schedule\"] else {},\n            created_at=datetime.fromisoformat(data[\"created_at\"]),\n            valid_until=datetime.fromisoformat(data[\"valid_until\"])\n        )\n    \n    def _dict_to_recommendation(self, data: Dict[str, Any]) -> Recommendation:\n        \"\"\"将字典转换为Recommendation对象\"\"\"\n        from ..core.recommendation_engine import RecommendationType, Priority\n        \n        return Recommendation(\n            id=data[\"recommendation_id\"],\n            type=RecommendationType(data[\"type\"]),\n            title=data[\"title\"],\n            description=data[\"description\"],\n            priority=Priority(data[\"priority\"]),\n            confidence=data[\"confidence\"],\n            evidence=json.loads(data[\"evidence\"]) if data[\"evidence\"] else [],\n            contraindications=json.loads(data[\"contraindications\"]) if data[\"contraindications\"] else [],\n            duration=data[\"duration\"],\n            frequency=data[\"frequency\"],\n            dosage=data[\"dosage\"],\n            precautions=json.loads(data[\"precautions\"]) if data[\"precautions\"] else [],\n            related_syndromes=json.loads(data[\"related_syndromes\"]) if data[\"related_syndromes\"] else [],\n            related_constitution=json.loads(data[\"related_constitution\"]) if data[\"related_constitution\"] else [],\n            created_at=datetime.fromisoformat(data[\"created_at\"]),\n            expires_at=datetime.fromisoformat(data[\"expires_at\"]) if data[\"expires_at\"] else None\n        )\n\n\nclass RepositoryManager:\n    \"\"\"仓库管理器\"\"\"\n    \n    def __init__(self):\n        self.pg_repo = PostgreSQLRepository()\n        self.redis_repo = RedisRepository()\n        self.diagnosis_repo = DiagnosisRepository(self.pg_repo, self.redis_repo)\n        self.recommendation_repo = RecommendationRepository(self.pg_repo, self.redis_repo)\n    \n    async def initialize(self) -> None:\n        \"\"\"初始化所有仓库\"\"\"\n        logger.info(\"初始化数据仓库管理器...\")\n        \n        try:\n            # 并行初始化\n            await asyncio.gather(\n                self.pg_repo.initialize(),\n                self.redis_repo.initialize()\n            )\n            \n            logger.info(\"数据仓库管理器初始化成功\")\n            \n        except Exception as e:\n            logger.error(f\"数据仓库管理器初始化失败: {e}\")\n            raise\n    \n    async def close(self) -> None:\n        \"\"\"关闭所有仓库连接\"\"\"\n        try:\n            await asyncio.gather(\n                self.pg_repo.close(),\n                self.redis_repo.close(),\n                return_exceptions=True\n            )\n            logger.info(\"数据仓库管理器已关闭\")\n        except Exception as e:\n            logger.warning(f\"关闭数据仓库管理器失败: {e}\")\n    \n    async def health_check(self) -> Dict[str, bool]:\n        \"\"\"健康检查\"\"\"\n        health_status = {}\n        \n        # PostgreSQL健康检查\n        try:\n            await self.pg_repo.execute_query(\"SELECT 1\")\n            health_status[\"postgresql\"] = True\n        except Exception:\n            health_status[\"postgresql\"] = False\n        \n        # Redis健康检查\n        try:\n            await self.redis_repo.redis_client.ping()\n            health_status[\"redis\"] = True\n        except Exception:\n            health_status[\"redis\"] = False\n        \n        return health_status