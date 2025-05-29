#!/usr/bin/env python3
"""
健康数据仓库
"""
import json
import logging
from typing import Any

from internal.repository.database import get_database

logger = logging.getLogger(__name__)

class HealthRepository:
    """健康数据仓库，负责存储和检索用户健康信息"""

    def __init__(self):
        """初始化健康数据仓库"""
        self.db = get_database()

    async def initialize(self):
        """初始化数据库表"""
        await self.db.initialize()

        # 创建用户健康档案表
        if self.db.db_type == 'postgresql':
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    constitution_type TEXT,
                    health_data JSONB,
                    habits JSONB,
                    work_schedule TEXT,
                    pain_points JSONB,
                    goals JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        elif self.db.db_type == 'sqlite':
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    constitution_type TEXT,
                    health_data TEXT,
                    habits TEXT,
                    work_schedule TEXT,
                    pain_points TEXT,
                    goals TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # 创建传感器数据表
        if self.db.db_type == 'postgresql':
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    sensor_type TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    timestamp BIGINT NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            await self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_data_user_timestamp
                ON sensor_data(user_id, timestamp)
            """)
        elif self.db.db_type == 'sqlite':
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    sensor_type TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            await self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_data_user_timestamp
                ON sensor_data(user_id, timestamp)
            """)

        # 创建健康计划表
        if self.db.db_type == 'postgresql':
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS health_plans (
                    plan_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    diet_recommendations JSONB,
                    exercise_recommendations JSONB,
                    lifestyle_recommendations JSONB,
                    supplement_recommendations JSONB,
                    schedule JSONB,
                    confidence_score FLOAT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        elif self.db.db_type == 'sqlite':
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS health_plans (
                    plan_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    diet_recommendations TEXT,
                    exercise_recommendations TEXT,
                    lifestyle_recommendations TEXT,
                    supplement_recommendations TEXT,
                    schedule TEXT,
                    confidence_score REAL,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        logger.info("健康数据表创建完成")

    async def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        """
        获取用户健康档案

        Args:
            user_id: 用户ID

        Returns:
            Optional[Dict[str, Any]]: 用户健康档案或None
        """
        if self.db.db_type == 'postgresql':
            query = "SELECT * FROM user_profiles WHERE user_id = $1"
            result = await self.db.fetchone(query, user_id)
        elif self.db.db_type == 'sqlite':
            query = "SELECT * FROM user_profiles WHERE user_id = ?"
            result = await self.db.fetchone(query, (user_id,))

        if not result:
            return None

        # 转换JSON字段
        if self.db.db_type == 'postgresql':
            return result
        elif self.db.db_type == 'sqlite':
            result['health_data'] = json.loads(result['health_data']) if result['health_data'] else {}
            result['habits'] = json.loads(result['habits']) if result['habits'] else {}
            result['pain_points'] = json.loads(result['pain_points']) if result['pain_points'] else []
            result['goals'] = json.loads(result['goals']) if result['goals'] else []

        return result

    async def create_or_update_profile(self, user_id: str, profile_data: dict[str, Any]) -> bool:
        """
        创建或更新用户健康档案

        Args:
            user_id: 用户ID
            profile_data: 档案数据

        Returns:
            bool: 是否成功
        """
        try:
            health_data = profile_data.get('health_data', {})
            habits = profile_data.get('habits', {})
            work_schedule = profile_data.get('work_schedule', '')
            pain_points = profile_data.get('pain_points', [])
            goals = profile_data.get('goals', [])
            constitution_type = profile_data.get('constitution_type', '')

            # 检查用户是否存在
            existing_profile = await self.get_user_profile(user_id)

            if self.db.db_type == 'postgresql':
                if existing_profile:
                    query = """
                        UPDATE user_profiles
                        SET constitution_type = $2,
                            health_data = $3,
                            habits = $4,
                            work_schedule = $5,
                            pain_points = $6,
                            goals = $7,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = $1
                    """
                    await self.db.execute(
                        query,
                        user_id,
                        constitution_type,
                        json.dumps(health_data),
                        json.dumps(habits),
                        work_schedule,
                        json.dumps(pain_points),
                        json.dumps(goals)
                    )
                else:
                    query = """
                        INSERT INTO user_profiles
                        (user_id, constitution_type, health_data, habits, work_schedule, pain_points, goals)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """
                    await self.db.execute(
                        query,
                        user_id,
                        constitution_type,
                        json.dumps(health_data),
                        json.dumps(habits),
                        work_schedule,
                        json.dumps(pain_points),
                        json.dumps(goals)
                    )
            elif self.db.db_type == 'sqlite':
                if existing_profile:
                    query = """
                        UPDATE user_profiles
                        SET constitution_type = ?,
                            health_data = ?,
                            habits = ?,
                            work_schedule = ?,
                            pain_points = ?,
                            goals = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """
                    await self.db.execute(
                        query,
                        (constitution_type,
                        json.dumps(health_data),
                        json.dumps(habits),
                        work_schedule,
                        json.dumps(pain_points),
                        json.dumps(goals),
                        user_id)
                    )
                else:
                    query = """
                        INSERT INTO user_profiles
                        (user_id, constitution_type, health_data, habits, work_schedule, pain_points, goals)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    await self.db.execute(
                        query,
                        (user_id,
                        constitution_type,
                        json.dumps(health_data),
                        json.dumps(habits),
                        work_schedule,
                        json.dumps(pain_points),
                        json.dumps(goals))
                    )

            return True
        except Exception as e:
            logger.error(f"创建或更新用户档案失败: {str(e)}")
            return False

    async def store_sensor_data(self, user_id: str, sensor_type: str, device_id: str,
                                timestamp: int, data: dict[str, Any]) -> bool:
        """
        存储传感器数据

        Args:
            user_id: 用户ID
            sensor_type: 传感器类型
            device_id: 设备ID
            timestamp: 时间戳
            data: 传感器数据

        Returns:
            bool: 是否成功
        """
        try:
            if self.db.db_type == 'postgresql':
                query = """
                    INSERT INTO sensor_data
                    (user_id, sensor_type, device_id, timestamp, data)
                    VALUES ($1, $2, $3, $4, $5)
                """
                await self.db.execute(query, user_id, sensor_type, device_id, timestamp, json.dumps(data))
            elif self.db.db_type == 'sqlite':
                query = """
                    INSERT INTO sensor_data
                    (user_id, sensor_type, device_id, timestamp, data)
                    VALUES (?, ?, ?, ?, ?)
                """
                await self.db.execute(query, (user_id, sensor_type, device_id, timestamp, json.dumps(data)))

            return True
        except Exception as e:
            logger.error(f"存储传感器数据失败: {str(e)}")
            return False

    async def get_sensor_data(self, user_id: str, sensor_type: str | None = None,
                             start_time: int | None = None, end_time: int | None = None,
                             limit: int = 1000) -> list[dict[str, Any]]:
        """
        获取传感器数据

        Args:
            user_id: 用户ID
            sensor_type: 传感器类型
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 结果限制

        Returns:
            List[Dict[str, Any]]: 传感器数据列表
        """
        conditions = ["user_id = $1" if self.db.db_type == 'postgresql' else "user_id = ?"]
        params = [user_id]
        param_idx = 2

        if sensor_type:
            conditions.append(f"sensor_type = ${param_idx}" if self.db.db_type == 'postgresql' else "sensor_type = ?")
            params.append(sensor_type)
            param_idx += 1

        if start_time is not None:
            conditions.append(f"timestamp >= ${param_idx}" if self.db.db_type == 'postgresql' else "timestamp >= ?")
            params.append(start_time)
            param_idx += 1

        if end_time is not None:
            conditions.append(f"timestamp <= ${param_idx}" if self.db.db_type == 'postgresql' else "timestamp <= ?")
            params.append(end_time)
            param_idx += 1

        where_clause = " AND ".join(conditions)

        if self.db.db_type == 'sqlite':
            params = tuple(params)

        query = f"""
            SELECT * FROM sensor_data
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT {limit}
        """

        results = await self.db.fetch(query, *params)

        # 转换JSON数据
        if self.db.db_type == 'sqlite':
            for result in results:
                result['data'] = json.loads(result['data'])

        return results

    async def save_health_plan(self, plan_id: str, user_id: str, plan_data: dict[str, Any]) -> bool:
        """
        保存健康计划

        Args:
            plan_id: 计划ID
            user_id: 用户ID
            plan_data: 计划数据

        Returns:
            bool: 是否成功
        """
        try:
            diet_recommendations = plan_data.get('diet_recommendations', [])
            exercise_recommendations = plan_data.get('exercise_recommendations', [])
            lifestyle_recommendations = plan_data.get('lifestyle_recommendations', [])
            supplement_recommendations = plan_data.get('supplement_recommendations', [])
            schedule = plan_data.get('schedule', {})
            confidence_score = plan_data.get('confidence_score', 0.0)
            start_date = plan_data.get('start_date')
            end_date = plan_data.get('end_date')

            if self.db.db_type == 'postgresql':
                query = """
                    INSERT INTO health_plans
                    (plan_id, user_id, diet_recommendations, exercise_recommendations,
                     lifestyle_recommendations, supplement_recommendations, schedule,
                     confidence_score, start_date, end_date)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (plan_id) DO UPDATE
                    SET diet_recommendations = $3,
                        exercise_recommendations = $4,
                        lifestyle_recommendations = $5,
                        supplement_recommendations = $6,
                        schedule = $7,
                        confidence_score = $8,
                        start_date = $9,
                        end_date = $10,
                        updated_at = CURRENT_TIMESTAMP
                """
                await self.db.execute(
                    query,
                    plan_id,
                    user_id,
                    json.dumps(diet_recommendations),
                    json.dumps(exercise_recommendations),
                    json.dumps(lifestyle_recommendations),
                    json.dumps(supplement_recommendations),
                    json.dumps(schedule),
                    confidence_score,
                    start_date,
                    end_date
                )
            elif self.db.db_type == 'sqlite':
                # 检查记录是否存在
                existing = await self.db.fetchone(
                    "SELECT 1 FROM health_plans WHERE plan_id = ?",
                    (plan_id,)
                )

                if existing:
                    query = """
                        UPDATE health_plans
                        SET diet_recommendations = ?,
                            exercise_recommendations = ?,
                            lifestyle_recommendations = ?,
                            supplement_recommendations = ?,
                            schedule = ?,
                            confidence_score = ?,
                            start_date = ?,
                            end_date = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE plan_id = ?
                    """
                    await self.db.execute(
                        query,
                        (json.dumps(diet_recommendations),
                        json.dumps(exercise_recommendations),
                        json.dumps(lifestyle_recommendations),
                        json.dumps(supplement_recommendations),
                        json.dumps(schedule),
                        confidence_score,
                        start_date,
                        end_date,
                        plan_id)
                    )
                else:
                    query = """
                        INSERT INTO health_plans
                        (plan_id, user_id, diet_recommendations, exercise_recommendations,
                         lifestyle_recommendations, supplement_recommendations, schedule,
                         confidence_score, start_date, end_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    await self.db.execute(
                        query,
                        (plan_id,
                        user_id,
                        json.dumps(diet_recommendations),
                        json.dumps(exercise_recommendations),
                        json.dumps(lifestyle_recommendations),
                        json.dumps(supplement_recommendations),
                        json.dumps(schedule),
                        confidence_score,
                        start_date,
                        end_date)
                    )

            return True
        except Exception as e:
            logger.error(f"保存健康计划失败: {str(e)}")
            return False

    async def get_health_plan(self, plan_id: str) -> dict[str, Any] | None:
        """
        获取健康计划

        Args:
            plan_id: 计划ID

        Returns:
            Optional[Dict[str, Any]]: 健康计划或None
        """
        if self.db.db_type == 'postgresql':
            query = "SELECT * FROM health_plans WHERE plan_id = $1"
            result = await self.db.fetchone(query, plan_id)
        elif self.db.db_type == 'sqlite':
            query = "SELECT * FROM health_plans WHERE plan_id = ?"
            result = await self.db.fetchone(query, (plan_id,))

        if not result:
            return None

        # 转换JSON字段
        if self.db.db_type == 'sqlite':
            result['diet_recommendations'] = json.loads(result['diet_recommendations']) if result['diet_recommendations'] else []
            result['exercise_recommendations'] = json.loads(result['exercise_recommendations']) if result['exercise_recommendations'] else []
            result['lifestyle_recommendations'] = json.loads(result['lifestyle_recommendations']) if result['lifestyle_recommendations'] else []
            result['supplement_recommendations'] = json.loads(result['supplement_recommendations']) if result['supplement_recommendations'] else []
            result['schedule'] = json.loads(result['schedule']) if result['schedule'] else {}

        return result

    async def get_user_health_plans(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        获取用户所有健康计划

        Args:
            user_id: 用户ID
            limit: 结果限制

        Returns:
            List[Dict[str, Any]]: 健康计划列表
        """
        if self.db.db_type == 'postgresql':
            query = """
                SELECT * FROM health_plans
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """
            results = await self.db.fetch(query, user_id, limit)
        elif self.db.db_type == 'sqlite':
            query = """
                SELECT * FROM health_plans
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            results = await self.db.fetch(query, (user_id, limit))

        # 转换JSON字段
        if self.db.db_type == 'sqlite':
            for result in results:
                result['diet_recommendations'] = json.loads(result['diet_recommendations']) if result['diet_recommendations'] else []
                result['exercise_recommendations'] = json.loads(result['exercise_recommendations']) if result['exercise_recommendations'] else []
                result['lifestyle_recommendations'] = json.loads(result['lifestyle_recommendations']) if result['lifestyle_recommendations'] else []
                result['supplement_recommendations'] = json.loads(result['supplement_recommendations']) if result['supplement_recommendations'] else []
                result['schedule'] = json.loads(result['schedule']) if result['schedule'] else {}

        return results
