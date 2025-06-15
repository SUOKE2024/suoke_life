"""
优化的用户仓储层
包含查询缓存、索引优化和批量操作
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, update, delete, func, text, Index
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import json
import hashlib
from datetime import datetime, timedelta

from .base import CacheableRepository
from internal.db.models import User, Role, Permission, UserRole, AuditLog
from internal.model.user import UserCreate, UserUpdate, UserResponse


class OptimizedUserRepository(CacheableRepository[User]):
    """优化的用户仓储类"""
    
    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(session, redis, User, cache_ttl=600)  # 10分钟缓存
        
    # 查询缓存优化
    async def get_user_with_roles_cached(self, user_id: str) -> Optional[User]:
        """获取用户及其角色信息（带缓存）"""
        cache_key = f"user_roles:{user_id}"
        
        # 尝试从缓存获取
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return self._deserialize_user(json.loads(cached_data))
        
        # 从数据库查询（使用预加载优化）
        query = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.audit_logs).limit(10)  # 只加载最近10条审计日志
            )
            .where(User.id == user_id)
        )
        
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            # 缓存结果
            serialized_data = self._serialize_user(user)
            await self.redis.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(serialized_data)
            )
        
        return user
    
    async def search_users_optimized(
        self,
        query: str,
        page: int = 1,
        size: int = 20,
        include_roles: bool = False
    ) -> Tuple[List[User], int]:
        """优化的用户搜索（支持全文搜索和分页）"""
        
        # 生成缓存键
        cache_key = self._generate_search_cache_key(query, page, size, include_roles)
        
        # 尝试从缓存获取
        cached_result = await self.redis.get(cache_key)
        if cached_result:
            data = json.loads(cached_result)
            return data['users'], data['total']
        
        # 构建优化的查询
        base_query = select(User)
        count_query = select(func.count(User.id))
        
        # 使用全文搜索（PostgreSQL特性）
        search_condition = text("""
            to_tsvector('english', username || ' ' || email || ' ' || 
                       COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')) 
            @@ plainto_tsquery('english', :query)
        """)
        
        base_query = base_query.where(search_condition)
        count_query = count_query.where(search_condition)
        
        if include_roles:
            base_query = base_query.options(selectinload(User.roles))
        
        # 分页
        offset = (page - 1) * size
        base_query = base_query.offset(offset).limit(size)
        
        # 执行查询
        users_result = await self.session.execute(
            base_query.params(query=query)
        )
        count_result = await self.session.execute(
            count_query.params(query=query)
        )
        
        users = users_result.scalars().all()
        total = count_result.scalar()
        
        # 缓存结果（较短的缓存时间）
        cache_data = {
            'users': [self._serialize_user(user) for user in users],
            'total': total
        }
        await self.redis.setex(cache_key, 300, json.dumps(cache_data))  # 5分钟缓存
        
        return list(users), total
    
    async def batch_update_users(
        self, 
        updates: List[Dict[str, Any]]
    ) -> List[User]:
        """批量更新用户"""
        
        if not updates:
            return []
        
        # 构建批量更新语句
        user_ids = [update_data['id'] for update_data in updates]
        
        # 使用CASE WHEN进行批量更新
        update_cases = {}
        for field in ['status', 'last_login_at', 'failed_login_attempts']:
            cases = []
            for update_data in updates:
                if field in update_data:
                    cases.append(f"WHEN id = '{update_data['id']}' THEN '{update_data[field]}'")
            
            if cases:
                update_cases[field] = f"CASE {' '.join(cases)} ELSE {field} END"
        
        if update_cases:
            set_clause = ', '.join([f"{field} = {case}" for field, case in update_cases.items()])
            query = text(f"""
                UPDATE users 
                SET {set_clause}, updated_at = NOW()
                WHERE id = ANY(:user_ids)
            """)
            
            await self.session.execute(query.params(user_ids=user_ids))
            await self.session.commit()
        
        # 清除相关缓存
        for user_id in user_ids:
            await self._invalidate_user_cache(user_id)
        
        # 返回更新后的用户
        result = await self.session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        return list(result.scalars().all())
    
    async def get_user_statistics_cached(self) -> Dict[str, Any]:
        """获取用户统计信息（带缓存）"""
        cache_key = "user_statistics"
        
        # 尝试从缓存获取
        cached_stats = await self.redis.get(cache_key)
        if cached_stats:
            return json.loads(cached_stats)
        
        # 使用单个查询获取所有统计信息
        stats_query = text("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_users,
                COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive_users,
                COUNT(CASE WHEN status = 'locked' THEN 1 END) as locked_users,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as new_users_24h,
                COUNT(CASE WHEN last_login_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as active_users_24h,
                COUNT(CASE WHEN mfa_enabled = true THEN 1 END) as mfa_enabled_users
            FROM users
        """)
        
        result = await self.session.execute(stats_query)
        row = result.fetchone()
        
        stats = {
            'total_users': row.total_users,
            'active_users': row.active_users,
            'inactive_users': row.inactive_users,
            'locked_users': row.locked_users,
            'new_users_24h': row.new_users_24h,
            'active_users_24h': row.active_users_24h,
            'mfa_enabled_users': row.mfa_enabled_users,
            'mfa_adoption_rate': (row.mfa_enabled_users / row.total_users * 100) if row.total_users > 0 else 0
        }
        
        # 缓存统计信息（5分钟）
        await self.redis.setex(cache_key, 300, json.dumps(stats))
        
        return stats
    
    async def get_login_analytics(self, days: int = 7) -> Dict[str, Any]:
        """获取登录分析数据"""
        cache_key = f"login_analytics:{days}"
        
        # 尝试从缓存获取
        cached_analytics = await self.redis.get(cache_key)
        if cached_analytics:
            return json.loads(cached_analytics)
        
        # 查询登录分析数据
        analytics_query = text("""
            WITH daily_logins AS (
                SELECT 
                    DATE(created_at) as login_date,
                    COUNT(*) as login_count,
                    COUNT(DISTINCT user_id) as unique_users
                FROM audit_logs 
                WHERE action = 'login' 
                AND created_at >= NOW() - INTERVAL :days DAY
                GROUP BY DATE(created_at)
                ORDER BY login_date
            ),
            hourly_distribution AS (
                SELECT 
                    EXTRACT(HOUR FROM created_at) as hour,
                    COUNT(*) as login_count
                FROM audit_logs 
                WHERE action = 'login' 
                AND created_at >= NOW() - INTERVAL :days DAY
                GROUP BY EXTRACT(HOUR FROM created_at)
                ORDER BY hour
            )
            SELECT 
                (SELECT json_agg(row_to_json(daily_logins)) FROM daily_logins) as daily_data,
                (SELECT json_agg(row_to_json(hourly_distribution)) FROM hourly_distribution) as hourly_data
        """)
        
        result = await self.session.execute(analytics_query.params(days=days))
        row = result.fetchone()
        
        analytics = {
            'daily_logins': row.daily_data or [],
            'hourly_distribution': row.hourly_data or [],
            'period_days': days
        }
        
        # 缓存分析数据（30分钟）
        await self.redis.setex(cache_key, 1800, json.dumps(analytics, default=str))
        
        return analytics
    
    # 私有辅助方法
    def _generate_search_cache_key(self, query: str, page: int, size: int, include_roles: bool) -> str:
        """生成搜索缓存键"""
        key_data = f"{query}:{page}:{size}:{include_roles}"
        return f"search_users:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """序列化用户对象"""
        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'status': user.status.value if user.status else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            'mfa_enabled': user.mfa_enabled,
            'roles': [{'id': str(role.id), 'name': role.name} for role in user.roles] if hasattr(user, 'roles') else []
        }
    
    def _deserialize_user(self, data: Dict[str, Any]) -> User:
        """反序列化用户对象（简化版本，仅用于缓存）"""
        user = User()
        user.id = data['id']
        user.username = data['username']
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        return user
    
    async def _invalidate_user_cache(self, user_id: str):
        """清除用户相关缓存"""
        cache_keys = [
            f"user_roles:{user_id}",
            f"user:{user_id}",
            "user_statistics"
        ]
        
        # 清除搜索缓存（使用模式匹配）
        search_keys = await self.redis.keys("search_users:*")
        cache_keys.extend(search_keys)
        
        if cache_keys:
            await self.redis.delete(*cache_keys)


# 数据库索引优化建议
class DatabaseIndexOptimizer:
    """数据库索引优化器"""
    
    @staticmethod
    def get_recommended_indexes() -> List[str]:
        """获取推荐的数据库索引"""
        return [
            # 用户表索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_status ON users(email, status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_status ON users(username, status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_last_login ON users(last_login_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_status_created ON users(status, created_at);",
            
            # 全文搜索索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_fulltext ON users USING gin(to_tsvector('english', username || ' ' || email || ' ' || COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')));",
            
            # 审计日志索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_action_created ON audit_logs(action, created_at);",
            
            # 令牌表索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_refresh_tokens_user_active ON refresh_tokens(user_id, is_active);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);",
            
            # 角色权限索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);",
            
            # MFA相关索引
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mfa_secrets_user_type ON mfa_secrets(user_id, mfa_type);",
        ]
    
    @staticmethod
    async def apply_indexes(session: AsyncSession):
        """应用推荐的索引"""
        indexes = DatabaseIndexOptimizer.get_recommended_indexes()
        
        for index_sql in indexes:
            try:
                await session.execute(text(index_sql))
                await session.commit()
                print(f"✅ 索引创建成功: {index_sql[:50]}...")
            except Exception as e:
                await session.rollback()
                print(f"⚠️ 索引创建失败: {e}")


# 查询性能监控
class QueryPerformanceMonitor:
    """查询性能监控器"""
    
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def log_slow_query(self, query: str, execution_time: float, params: Dict = None):
        """记录慢查询"""
        if execution_time > 1.0:  # 超过1秒的查询
            slow_query_data = {
                'query': query,
                'execution_time': execution_time,
                'params': params,
                'timestamp': datetime.now().isoformat()
            }
            
            # 存储到Redis列表中
            await self.redis.lpush(
                'slow_queries', 
                json.dumps(slow_query_data)
            )
            
            # 保持最近100条慢查询记录
            await self.redis.ltrim('slow_queries', 0, 99)
    
    async def get_slow_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取慢查询记录"""
        queries = await self.redis.lrange('slow_queries', 0, limit - 1)
        return [json.loads(query) for query in queries]
    
    async def get_query_statistics(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        stats_key = "query_stats"
        cached_stats = await self.redis.get(stats_key)
        
        if cached_stats:
            return json.loads(cached_stats)
        
        # 这里可以添加更复杂的查询统计逻辑
        stats = {
            'slow_query_count': await self.redis.llen('slow_queries'),
            'last_updated': datetime.now().isoformat()
        }
        
        await self.redis.setex(stats_key, 300, json.dumps(stats))
        return stats 