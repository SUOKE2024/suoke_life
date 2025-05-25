#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索儿智能体服务 - 知识存储库
提供健康知识、生活方式和个性化建议的存储和检索
"""

import uuid
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set

import motor.motor_asyncio
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector
from pkg.utils.dependency_injection import ServiceLifecycle
from pkg.utils.connection_pool import get_pool_manager, DatabaseConnectionPool, RedisConnectionPool
from pkg.utils.error_handling import DatabaseException, retry_async, RetryConfig

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class KnowledgeRepository(ServiceLifecycle):
    """知识仓储"""
    
    def __init__(self):
        self.db_pool: Optional[DatabaseConnectionPool] = None
        self.cache_pool: Optional[RedisConnectionPool] = None
        self.metrics = get_metrics_collector()
    
    async def start(self) -> None:
        """启动仓储"""
        try:
            pool_manager = get_pool_manager()
            self.db_pool = pool_manager.get_pool('database')
            self.cache_pool = pool_manager.get_pool('redis')
            
            # 确保数据库表存在
            await self._ensure_tables()
            
            logger.info("知识仓储启动成功")
            
        except Exception as e:
            logger.error(f"知识仓储启动失败: {e}")
            raise DatabaseException(f"知识仓储启动失败: {e}")
    
    async def stop(self) -> None:
        """停止仓储"""
        logger.info("知识仓储已停止")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.db_pool or not self.cache_pool:
                return False
            
            # 测试数据库连接
            async with self.db_pool.get_session() as session:
                await session.execute("SELECT 1")
            
            # 测试缓存连接
            await self.cache_pool.ping()
            
            return True
            
        except Exception as e:
            logger.error(f"知识仓储健康检查失败: {e}")
            return False
    
    async def _ensure_tables(self) -> None:
        """确保数据库表存在"""
        # 知识条目表
        create_knowledge_entries_table = """
        CREATE TABLE IF NOT EXISTS knowledge_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(500) NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(100) NOT NULL,
            subcategory VARCHAR(100),
            tags TEXT[],
            source VARCHAR(200),
            author VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            version INTEGER DEFAULT 1,
            status VARCHAR(50) DEFAULT 'active',
            metadata JSONB DEFAULT '{}',
            INDEX idx_knowledge_category (category),
            INDEX idx_knowledge_tags (tags),
            INDEX idx_knowledge_status (status),
            INDEX idx_knowledge_created_at (created_at)
        );
        """
        
        # 中医体质表
        create_tcm_constitutions_table = """
        CREATE TABLE IF NOT EXISTS tcm_constitutions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT NOT NULL,
            characteristics JSONB NOT NULL,
            dietary_recommendations JSONB,
            lifestyle_recommendations JSONB,
            exercise_recommendations JSONB,
            seasonal_adjustments JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            INDEX idx_tcm_constitutions_name (name)
        );
        """
        
        # 症状知识表
        create_symptoms_table = """
        CREATE TABLE IF NOT EXISTS symptoms (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            severity_levels JSONB,
            related_conditions TEXT[],
            tcm_patterns JSONB,
            recommendations JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            INDEX idx_symptoms_name (name),
            INDEX idx_symptoms_category (category)
        );
        """
        
        # 食物营养表
        create_foods_table = """
        CREATE TABLE IF NOT EXISTS foods (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(200) NOT NULL,
            category VARCHAR(100),
            nutrition_facts JSONB,
            tcm_properties JSONB,
            health_benefits TEXT[],
            contraindications TEXT[],
            seasonal_suitability JSONB,
            preparation_methods TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            INDEX idx_foods_name (name),
            INDEX idx_foods_category (category)
        );
        """
        
        # 运动方案表
        create_exercises_table = """
        CREATE TABLE IF NOT EXISTS exercises (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(200) NOT NULL,
            type VARCHAR(100),
            description TEXT,
            instructions JSONB,
            duration_minutes INTEGER,
            intensity_level VARCHAR(50),
            target_groups TEXT[],
            benefits TEXT[],
            precautions TEXT[],
            equipment_needed TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            INDEX idx_exercises_name (name),
            INDEX idx_exercises_type (type),
            INDEX idx_exercises_intensity (intensity_level)
        );
        """
        
        try:
            async with self.db_pool.get_session() as session:
                await session.execute(create_knowledge_entries_table)
                await session.execute(create_tcm_constitutions_table)
                await session.execute(create_symptoms_table)
                await session.execute(create_foods_table)
                await session.execute(create_exercises_table)
                await session.commit()
                
            logger.info("知识库数据库表检查完成")
            
        except Exception as e:
            logger.error(f"创建知识库数据库表失败: {e}")
            raise DatabaseException(f"创建知识库数据库表失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def search_knowledge(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索知识条目"""
        try:
            # 先尝试从缓存获取
            cache_key = self._generate_search_cache_key(query, category, limit)
            cached_result = await self._get_cached_search_result(cache_key)
            if cached_result:
                return cached_result
            
            self.metrics.increment_counter("soer_db_queries", {"operation": "search", "table": "knowledge_entries"})
            
            # 构建搜索查询
            where_conditions = ["status = 'active'"]
            params = {"query": f"%{query}%", "limit": limit}
            
            if category:
                where_conditions.append("category = :category")
                params["category"] = category
            
            where_clause = " AND ".join(where_conditions)
            
            search_query = f"""
            SELECT id, title, content, category, subcategory, tags, source, author, 
                   created_at, updated_at, metadata,
                   ts_rank(to_tsvector('chinese', title || ' ' || content), plainto_tsquery('chinese', :query)) as rank
            FROM knowledge_entries 
            WHERE {where_clause}
            AND (
                title ILIKE :query 
                OR content ILIKE :query 
                OR to_tsvector('chinese', title || ' ' || content) @@ plainto_tsquery('chinese', :query)
            )
            ORDER BY rank DESC, created_at DESC
            LIMIT :limit
            """
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "search", "table": "knowledge_entries"}):
                async with self.db_pool.get_session() as db_session:
                    result = await db_session.execute(search_query, params)
                    rows = result.fetchall()
            
            knowledge_entries = []
            for row in rows:
                knowledge_entries.append({
                    "id": str(row.id),
                    "title": row.title,
                    "content": row.content,
                    "category": row.category,
                    "subcategory": row.subcategory,
                    "tags": row.tags or [],
                    "source": row.source,
                    "author": row.author,
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat(),
                    "metadata": json.loads(row.metadata) if row.metadata else {},
                    "relevance_score": float(row.rank) if row.rank else 0.0
                })
            
            # 缓存搜索结果
            await self._cache_search_result(cache_key, knowledge_entries)
            
            return knowledge_entries
            
        except Exception as e:
            logger.error(f"搜索知识条目失败: {e}")
            raise DatabaseException(f"搜索知识条目失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_tcm_constitution(self, constitution_name: str) -> Optional[Dict[str, Any]]:
        """获取中医体质信息"""
        try:
            # 先从缓存获取
            cache_key = f"tcm_constitution:{constitution_name}"
            cached_result = await self._get_cached_data(cache_key)
            if cached_result:
                return cached_result
            
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "tcm_constitutions"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "tcm_constitutions"}):
                async with self.db_pool.get_session() as db_session:
                    query = """
                    SELECT id, name, description, characteristics, dietary_recommendations,
                           lifestyle_recommendations, exercise_recommendations, seasonal_adjustments,
                           created_at, updated_at
                    FROM tcm_constitutions 
                    WHERE name = :constitution_name
                    """
                    
                    result = await db_session.execute(query, {"constitution_name": constitution_name})
                    row = result.fetchone()
            
            if not row:
                return None
            
            constitution_data = {
                "id": str(row.id),
                "name": row.name,
                "description": row.description,
                "characteristics": json.loads(row.characteristics) if row.characteristics else {},
                "dietary_recommendations": json.loads(row.dietary_recommendations) if row.dietary_recommendations else {},
                "lifestyle_recommendations": json.loads(row.lifestyle_recommendations) if row.lifestyle_recommendations else {},
                "exercise_recommendations": json.loads(row.exercise_recommendations) if row.exercise_recommendations else {},
                "seasonal_adjustments": json.loads(row.seasonal_adjustments) if row.seasonal_adjustments else {},
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat()
            }
            
            # 缓存结果
            await self._cache_data(cache_key, constitution_data, ttl=7200)  # 缓存2小时
            
            return constitution_data
            
        except Exception as e:
            logger.error(f"获取中医体质信息失败: {e}")
            raise DatabaseException(f"获取中医体质信息失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_symptom_info(self, symptom_name: str) -> Optional[Dict[str, Any]]:
        """获取症状信息"""
        try:
            # 先从缓存获取
            cache_key = f"symptom:{symptom_name}"
            cached_result = await self._get_cached_data(cache_key)
            if cached_result:
                return cached_result
            
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "symptoms"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "symptoms"}):
                async with self.db_pool.get_session() as db_session:
                    query = """
                    SELECT id, name, description, category, severity_levels, related_conditions,
                           tcm_patterns, recommendations, created_at, updated_at
                    FROM symptoms 
                    WHERE name ILIKE :symptom_name
                    """
                    
                    result = await db_session.execute(query, {"symptom_name": f"%{symptom_name}%"})
                    row = result.fetchone()
            
            if not row:
                return None
            
            symptom_data = {
                "id": str(row.id),
                "name": row.name,
                "description": row.description,
                "category": row.category,
                "severity_levels": json.loads(row.severity_levels) if row.severity_levels else {},
                "related_conditions": row.related_conditions or [],
                "tcm_patterns": json.loads(row.tcm_patterns) if row.tcm_patterns else {},
                "recommendations": json.loads(row.recommendations) if row.recommendations else {},
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat()
            }
            
            # 缓存结果
            await self._cache_data(cache_key, symptom_data, ttl=3600)  # 缓存1小时
            
            return symptom_data
            
        except Exception as e:
            logger.error(f"获取症状信息失败: {e}")
            raise DatabaseException(f"获取症状信息失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_food_recommendations(
        self, 
        constitution_type: Optional[str] = None,
        season: Optional[str] = None,
        health_goals: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取食物推荐"""
        try:
            # 生成缓存键
            cache_key = self._generate_food_cache_key(constitution_type, season, health_goals, limit)
            cached_result = await self._get_cached_data(cache_key)
            if cached_result:
                return cached_result
            
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "foods"})
            
            # 构建查询条件
            where_conditions = []
            params = {"limit": limit}
            
            if constitution_type:
                where_conditions.append("tcm_properties->>'suitable_constitutions' LIKE :constitution")
                params["constitution"] = f"%{constitution_type}%"
            
            if season:
                where_conditions.append("seasonal_suitability->:season IS NOT NULL")
                params["season"] = season
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
            SELECT id, name, category, nutrition_facts, tcm_properties, health_benefits,
                   contraindications, seasonal_suitability, preparation_methods,
                   created_at, updated_at
            FROM foods 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
            """
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "foods"}):
                async with self.db_pool.get_session() as db_session:
                    result = await db_session.execute(query, params)
                    rows = result.fetchall()
            
            foods = []
            for row in rows:
                food_data = {
                    "id": str(row.id),
                    "name": row.name,
                    "category": row.category,
                    "nutrition_facts": json.loads(row.nutrition_facts) if row.nutrition_facts else {},
                    "tcm_properties": json.loads(row.tcm_properties) if row.tcm_properties else {},
                    "health_benefits": row.health_benefits or [],
                    "contraindications": row.contraindications or [],
                    "seasonal_suitability": json.loads(row.seasonal_suitability) if row.seasonal_suitability else {},
                    "preparation_methods": row.preparation_methods or [],
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat()
                }
                
                # 根据健康目标过滤
                if health_goals:
                    benefits = food_data.get("health_benefits", [])
                    if any(goal in " ".join(benefits) for goal in health_goals):
                        foods.append(food_data)
                else:
                    foods.append(food_data)
            
            # 缓存结果
            await self._cache_data(cache_key, foods, ttl=1800)  # 缓存30分钟
            
            return foods
            
        except Exception as e:
            logger.error(f"获取食物推荐失败: {e}")
            raise DatabaseException(f"获取食物推荐失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_exercise_recommendations(
        self, 
        constitution_type: Optional[str] = None,
        fitness_level: Optional[str] = None,
        health_goals: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取运动推荐"""
        try:
            # 生成缓存键
            cache_key = self._generate_exercise_cache_key(constitution_type, fitness_level, health_goals, limit)
            cached_result = await self._get_cached_data(cache_key)
            if cached_result:
                return cached_result
            
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "exercises"})
            
            # 构建查询条件
            where_conditions = []
            params = {"limit": limit}
            
            if constitution_type:
                where_conditions.append(f"'{constitution_type}' = ANY(target_groups)")
            
            if fitness_level:
                where_conditions.append("intensity_level = :intensity")
                params["intensity"] = fitness_level
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
            SELECT id, name, type, description, instructions, duration_minutes,
                   intensity_level, target_groups, benefits, precautions, equipment_needed,
                   created_at, updated_at
            FROM exercises 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
            """
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "exercises"}):
                async with self.db_pool.get_session() as db_session:
                    result = await db_session.execute(query, params)
                    rows = result.fetchall()
            
            exercises = []
            for row in rows:
                exercise_data = {
                    "id": str(row.id),
                    "name": row.name,
                    "type": row.type,
                    "description": row.description,
                    "instructions": json.loads(row.instructions) if row.instructions else {},
                    "duration_minutes": row.duration_minutes,
                    "intensity_level": row.intensity_level,
                    "target_groups": row.target_groups or [],
                    "benefits": row.benefits or [],
                    "precautions": row.precautions or [],
                    "equipment_needed": row.equipment_needed or [],
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat()
                }
                
                # 根据健康目标过滤
                if health_goals:
                    benefits = exercise_data.get("benefits", [])
                    if any(goal in " ".join(benefits) for goal in health_goals):
                        exercises.append(exercise_data)
                else:
                    exercises.append(exercise_data)
            
            # 缓存结果
            await self._cache_data(cache_key, exercises, ttl=1800)  # 缓存30分钟
            
            return exercises
            
        except Exception as e:
            logger.error(f"获取运动推荐失败: {e}")
            raise DatabaseException(f"获取运动推荐失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_knowledge_by_category(
        self, 
        category: str, 
        subcategory: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """根据分类获取知识条目"""
        try:
            # 生成缓存键
            cache_key = f"knowledge_category:{category}:{subcategory or 'all'}:{limit}"
            cached_result = await self._get_cached_data(cache_key)
            if cached_result:
                return cached_result
            
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "knowledge_entries"})
            
            # 构建查询条件
            where_conditions = ["status = 'active'", "category = :category"]
            params = {"category": category, "limit": limit}
            
            if subcategory:
                where_conditions.append("subcategory = :subcategory")
                params["subcategory"] = subcategory
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
            SELECT id, title, content, category, subcategory, tags, source, author,
                   created_at, updated_at, metadata
            FROM knowledge_entries 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
            """
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "knowledge_entries"}):
                async with self.db_pool.get_session() as db_session:
                    result = await db_session.execute(query, params)
                    rows = result.fetchall()
            
            knowledge_entries = []
            for row in rows:
                knowledge_entries.append({
                    "id": str(row.id),
                    "title": row.title,
                    "content": row.content,
                    "category": row.category,
                    "subcategory": row.subcategory,
                    "tags": row.tags or [],
                    "source": row.source,
                    "author": row.author,
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat(),
                    "metadata": json.loads(row.metadata) if row.metadata else {}
                })
            
            # 缓存结果
            await self._cache_data(cache_key, knowledge_entries, ttl=3600)  # 缓存1小时
            
            return knowledge_entries
            
        except Exception as e:
            logger.error(f"根据分类获取知识条目失败: {e}")
            raise DatabaseException(f"根据分类获取知识条目失败: {e}")
    
    # 缓存相关方法
    def _generate_search_cache_key(self, query: str, category: Optional[str], limit: int) -> str:
        """生成搜索缓存键"""
        key_data = f"search:{query}:{category or 'all'}:{limit}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _generate_food_cache_key(
        self, 
        constitution_type: Optional[str], 
        season: Optional[str], 
        health_goals: Optional[List[str]], 
        limit: int
    ) -> str:
        """生成食物推荐缓存键"""
        goals_str = ",".join(sorted(health_goals)) if health_goals else "none"
        key_data = f"food_rec:{constitution_type or 'all'}:{season or 'all'}:{goals_str}:{limit}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _generate_exercise_cache_key(
        self, 
        constitution_type: Optional[str], 
        fitness_level: Optional[str], 
        health_goals: Optional[List[str]], 
        limit: int
    ) -> str:
        """生成运动推荐缓存键"""
        goals_str = ",".join(sorted(health_goals)) if health_goals else "none"
        key_data = f"exercise_rec:{constitution_type or 'all'}:{fitness_level or 'all'}:{goals_str}:{limit}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _cache_data(self, cache_key: str, data: Any, ttl: int = 3600) -> None:
        """缓存数据"""
        try:
            cache_data = json.dumps(data, ensure_ascii=False)
            await self.cache_pool.set(f"knowledge:{cache_key}", cache_data, ttl=ttl)
        except Exception as e:
            logger.warning(f"缓存数据失败: {e}")
    
    async def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            cached_data = await self.cache_pool.get(f"knowledge:{cache_key}")
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.warning(f"获取缓存数据失败: {e}")
            return None
    
    async def _cache_search_result(self, cache_key: str, results: List[Dict[str, Any]]) -> None:
        """缓存搜索结果"""
        await self._cache_data(f"search:{cache_key}", results, ttl=1800)  # 缓存30分钟
    
    async def _get_cached_search_result(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """获取缓存的搜索结果"""
        return await self._get_cached_data(f"search:{cache_key}") 