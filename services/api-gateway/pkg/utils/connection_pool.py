#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能连接池管理器
提供高效的HTTP连接池管理，支持连接复用、健康检查和自动清理
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Set
from dataclasses import dataclass
from urllib.parse import urlparse

from aiohttp import ClientSession, ClientTimeout, TCPConnector

logger = logging.getLogger(__name__)

@dataclass
class ConnectionPoolConfig:
    """连接池配置"""
    max_connections: int = 100
    max_connections_per_host: int = 30
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    keepalive_timeout: float = 30.0
    enable_cleanup: bool = True
    cleanup_interval: float = 60.0
    max_idle_time: float = 300.0

@dataclass
class PoolStats:
    """连接池统计信息"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    created_connections: int = 0
    closed_connections: int = 0
    failed_connections: int = 0

class SmartConnectionPool:
    """
    智能连接池管理器
    提供高效的HTTP连接管理和自动优化
    """
    
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self._sessions: Dict[str, ClientSession] = {}
        self._session_stats: Dict[str, PoolStats] = {}
        self._session_last_used: Dict[str, float] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
    async def start(self):
        """启动连接池"""
        if self.config.enable_cleanup:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("智能连接池已启动")
    
    async def stop(self):
        """停止连接池"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 关闭所有会话
        for session in self._sessions.values():
            await session.close()
        
        self._sessions.clear()
        self._session_stats.clear()
        self._session_last_used.clear()
        logger.info("智能连接池已停止")
    
    async def get_session(self, service_name: str, base_url: str) -> ClientSession:
        """
        获取或创建会话
        
        Args:
            service_name: 服务名称
            base_url: 基础URL
            
        Returns:
            ClientSession: HTTP会话对象
        """
        session_key = f"{service_name}:{base_url}"
        
        async with self._lock:
            if session_key not in self._sessions:
                session = await self._create_session(service_name, base_url)
                self._sessions[session_key] = session
                self._session_stats[session_key] = PoolStats()
                logger.debug(f"为 {service_name} 创建新会话: {base_url}")
            
            self._session_last_used[session_key] = time.time()
            return self._sessions[session_key]
    
    async def _create_session(self, service_name: str, base_url: str) -> ClientSession:
        """
        创建新的HTTP会话
        
        Args:
            service_name: 服务名称
            base_url: 基础URL
            
        Returns:
            ClientSession: 新的HTTP会话
        """
        # 解析URL获取主机信息
        parsed_url = urlparse(base_url)
        host = parsed_url.hostname
        
        # 创建连接器
        connector = TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections_per_host,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=True,
            use_dns_cache=True,
            ttl_dns_cache=300,  # DNS缓存5分钟
        )
        
        # 创建超时配置
        timeout = ClientTimeout(
            total=self.config.read_timeout,
            connect=self.config.connection_timeout,
        )
        
        # 创建会话
        session = ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': f'SuokeLife-Gateway/1.0 ({service_name})',
                'Connection': 'keep-alive',
            },
            raise_for_status=False,
        )
        
        return session
    
    async def _cleanup_loop(self):
        """清理循环，定期清理空闲连接"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_idle_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"连接池清理出错: {e}")
    
    async def _cleanup_idle_sessions(self):
        """清理空闲会话"""
        current_time = time.time()
        sessions_to_remove = []
        
        async with self._lock:
            for session_key, last_used in self._session_last_used.items():
                if current_time - last_used > self.config.max_idle_time:
                    sessions_to_remove.append(session_key)
            
            for session_key in sessions_to_remove:
                session = self._sessions.pop(session_key, None)
                if session:
                    await session.close()
                    self._session_stats.pop(session_key, None)
                    self._session_last_used.pop(session_key, None)
                    logger.debug(f"清理空闲会话: {session_key}")
    
    def get_stats(self) -> Dict[str, PoolStats]:
        """获取连接池统计信息"""
        return self._session_stats.copy()
    
    def get_total_stats(self) -> PoolStats:
        """获取总体统计信息"""
        total_stats = PoolStats()
        for stats in self._session_stats.values():
            total_stats.total_connections += stats.total_connections
            total_stats.active_connections += stats.active_connections
            total_stats.idle_connections += stats.idle_connections
            total_stats.created_connections += stats.created_connections
            total_stats.closed_connections += stats.closed_connections
            total_stats.failed_connections += stats.failed_connections
        
        return total_stats

class ConnectionPoolManager:
    """
    连接池管理器
    管理多个连接池实例
    """
    
    def __init__(self):
        self._pools: Dict[str, SmartConnectionPool] = {}
        self._default_config = ConnectionPoolConfig()
    
    def create_pool(self, name: str, config: Optional[ConnectionPoolConfig] = None) -> SmartConnectionPool:
        """
        创建连接池
        
        Args:
            name: 连接池名称
            config: 连接池配置
            
        Returns:
            SmartConnectionPool: 连接池实例
        """
        if name in self._pools:
            return self._pools[name]
        
        pool_config = config or self._default_config
        pool = SmartConnectionPool(pool_config)
        self._pools[name] = pool
        return pool
    
    def get_pool(self, name: str) -> Optional[SmartConnectionPool]:
        """获取连接池"""
        return self._pools.get(name)
    
    async def start_all(self):
        """启动所有连接池"""
        for pool in self._pools.values():
            await pool.start()
    
    async def stop_all(self):
        """停止所有连接池"""
        for pool in self._pools.values():
            await pool.stop()
        self._pools.clear()
    
    def get_all_stats(self) -> Dict[str, Dict[str, PoolStats]]:
        """获取所有连接池统计信息"""
        return {name: pool.get_stats() for name, pool in self._pools.items()}

# 全局连接池管理器实例
connection_pool_manager = ConnectionPoolManager() 