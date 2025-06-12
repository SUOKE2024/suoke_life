"""
连接池管理器

提供数据库连接池、HTTP连接池等高性能连接管理
"""

import asyncio
import aiohttp
import asyncpg
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """数据库连接池"""
    
    def __init__(self):
        self.settings = get_settings()
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """初始化连接池"""
        try:
            self.pool = await asyncpg.create_pool(
                self.settings.database_url,
                min_size=5,
                max_size=self.settings.db_pool_size,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=30
            )
            logger.info("数据库连接池初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接"""
        if not self.pool:
            raise RuntimeError("连接池未初始化")
        
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"数据库操作失败: {e}")
                raise
    
    async def execute(self, query: str, *args) -> str:
        """执行SQL语句"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """查询多行数据"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """查询单行数据"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def close(self):
        """关闭连接池"""
        if self.pool:
            await self.pool.close()
            logger.info("数据库连接池已关闭")


class HTTPConnectionPool:
    """HTTP连接池"""
    
    def __init__(self):
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """初始化HTTP连接池"""
        try:
            timeout = aiohttp.ClientTimeout(
                total=self.settings.external_api_timeout,
                connect=5
            )
            
            connector = aiohttp.TCPConnector(
                limit=100,  # 总连接数限制
                limit_per_host=30,  # 每个主机连接数限制
                ttl_dns_cache=300,  # DNS缓存时间
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'XiaoAI-Service/1.0',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
            )
            
            logger.info("HTTP连接池初始化成功")
            
        except Exception as e:
            logger.error(f"HTTP连接池初始化失败: {e}")
            raise
    
    async def get(self, url: str,**kwargs) -> aiohttp.ClientResponse:
        """GET请求"""
        if not self.session:
            raise RuntimeError("HTTP连接池未初始化")
        
        return await self.session.get(url,**kwargs)
    
    async def post(self, url: str,**kwargs) -> aiohttp.ClientResponse:
        """POST请求"""
        if not self.session:
            raise RuntimeError("HTTP连接池未初始化")
        
        return await self.session.post(url,**kwargs)
    
    async def put(self, url: str,**kwargs) -> aiohttp.ClientResponse:
        """PUT请求"""
        if not self.session:
            raise RuntimeError("HTTP连接池未初始化")
        
        return await self.session.put(url,**kwargs)
    
    async def delete(self, url: str,**kwargs) -> aiohttp.ClientResponse:
        """DELETE请求"""
        if not self.session:
            raise RuntimeError("HTTP连接池未初始化")
        
        return await self.session.delete(url,**kwargs)
    
    async def close(self):
        """关闭连接池"""
        if self.session:
            await self.session.close()
            logger.info("HTTP连接池已关闭")


class ConnectionPoolManager:
    """连接池管理器"""
    
    def __init__(self):
        self.db_pool = DatabaseConnectionPool()
        self.http_pool = HTTPConnectionPool()
    
    async def initialize(self):
        """初始化所有连接池"""
        await self.db_pool.initialize()
        await self.http_pool.initialize()
        logger.info("所有连接池初始化完成")
    
    async def close(self):
        """关闭所有连接池"""
        await self.db_pool.close()
        await self.http_pool.close()
        logger.info("所有连接池已关闭")
    
    def get_db_pool(self) -> DatabaseConnectionPool:
        """获取数据库连接池"""
        return self.db_pool
    
    def get_http_pool(self) -> HTTPConnectionPool:
        """获取HTTP连接池"""
        return self.http_pool


# 全局连接池管理器实例
connection_pool_manager = ConnectionPoolManager()