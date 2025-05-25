#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的连接池管理器
提供智能连接管理、自动扩缩容和健康监控功能
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple, Any
from contextlib import asynccontextmanager

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.client_exceptions import ClientError, ClientTimeout as ClientTimeoutError

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolMetrics:
    """连接池指标"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_errors: int = 0
    avg_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = float('inf')
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0


@dataclass
class EnhancedConnectionConfig:
    """增强连接池配置"""
    # 基础配置
    max_connections: int = 100
    max_connections_per_host: int = 30
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    total_timeout: float = 60.0
    
    # 连接保持
    keepalive_timeout: float = 30.0
    enable_cleanup: bool = True
    cleanup_interval: float = 60.0
    max_idle_time: float = 300.0
    
    # 智能扩缩容
    auto_scaling: bool = True
    min_connections: int = 5
    scale_up_threshold: float = 0.8  # 80%使用率时扩容
    scale_down_threshold: float = 0.3  # 30%使用率时缩容
    scale_factor: float = 1.5
    
    # 健康检查
    health_check_enabled: bool = True
    health_check_interval: float = 30.0
    health_check_timeout: float = 5.0
    max_consecutive_failures: int = 3
    
    # 重试配置
    retry_enabled: bool = True
    max_retries: int = 3
    retry_backoff_factor: float = 1.5
    retry_jitter: bool = True


class EnhancedConnectionPool:
    """增强的连接池"""
    
    def __init__(self, service_name: str, config: EnhancedConnectionConfig):
        self.service_name = service_name
        self.config = config
        self.metrics = ConnectionPoolMetrics()
        
        # 连接管理
        self._session: Optional[ClientSession] = None
        self._connector: Optional[TCPConnector] = None
        self._active_requests: Set[asyncio.Task] = set()
        
        # 健康状态
        self._healthy = True
        self._consecutive_failures = 0
        self._last_health_check = 0.0
        
        # 监控数据
        self._response_times: list = []
        self._last_cleanup = time.time()
        
        # 控制标志
        self._running = False
        self._background_tasks: list = []
    
    async def start(self):
        """启动连接池"""
        if self._running:
            return
        
        # 创建连接器
        self._connector = TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections_per_host,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=self.config.enable_cleanup,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        # 创建会话
        timeout = ClientTimeout(
            total=self.config.total_timeout,
            connect=self.config.connection_timeout,
            sock_read=self.config.read_timeout
        )
        
        self._session = ClientSession(
            connector=self._connector,
            timeout=timeout,
            headers={
                'User-Agent': f'SuokeLife-Gateway/{self.service_name}',
                'Connection': 'keep-alive'
            }
        )
        
        # 启动后台任务
        if self.config.health_check_enabled:
            self._background_tasks.append(
                asyncio.create_task(self._health_check_loop())
            )
        
        if self.config.enable_cleanup:
            self._background_tasks.append(
                asyncio.create_task(self._cleanup_loop())
            )
        
        self._running = True
        logger.info(f"连接池 {self.service_name} 已启动")
    
    async def stop(self):
        """停止连接池"""
        if not self._running:
            return
        
        self._running = False
        
        # 取消后台任务
        for task in self._background_tasks:
            task.cancel()
        
        # 等待活跃请求完成
        if self._active_requests:
            await asyncio.gather(*self._active_requests, return_exceptions=True)
        
        # 关闭会话
        if self._session:
            await self._session.close()
        
        logger.info(f"连接池 {self.service_name} 已停止")
    
    @asynccontextmanager
    async def request(self, method: str, url: str, **kwargs):
        """执行HTTP请求"""
        if not self._running or not self._session:
            raise RuntimeError(f"连接池 {self.service_name} 未启动")
        
        start_time = time.time()
        task = None
        
        try:
            # 创建请求任务
            task = asyncio.create_task(
                self._execute_request(method, url, **kwargs)
            )
            self._active_requests.add(task)
            
            # 执行请求
            response = await task
            
            # 更新指标
            response_time = time.time() - start_time
            self._update_metrics(response_time, True)
            
            yield response
            
        except Exception as e:
            # 更新错误指标
            response_time = time.time() - start_time
            self._update_metrics(response_time, False)
            
            logger.error(f"请求失败 {method} {url}: {e}")
            raise
        
        finally:
            if task and task in self._active_requests:
                self._active_requests.remove(task)
    
    async def _execute_request(self, method: str, url: str, **kwargs):
        """执行HTTP请求"""
        retries = 0
        last_exception = None
        
        while retries <= self.config.max_retries:
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    # 检查响应状态
                    if response.status >= 500:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
                    
                    return response
            
            except (ClientError, ClientTimeoutError, asyncio.TimeoutError) as e:
                last_exception = e
                retries += 1
                
                if retries <= self.config.max_retries:
                    # 计算退避时间
                    backoff = self.config.retry_backoff_factor ** (retries - 1)
                    if self.config.retry_jitter:
                        import random
                        backoff *= (0.5 + random.random() * 0.5)
                    
                    await asyncio.sleep(backoff)
                    logger.warning(f"请求重试 {retries}/{self.config.max_retries}: {e}")
        
        # 所有重试都失败
        raise last_exception
    
    def _update_metrics(self, response_time: float, success: bool):
        """更新指标"""
        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_requests += 1
            self._consecutive_failures = 0
        else:
            self.metrics.failed_requests += 1
            self.metrics.connection_errors += 1
            self._consecutive_failures += 1
        
        # 更新响应时间统计
        self._response_times.append(response_time)
        if len(self._response_times) > 1000:  # 保持最近1000个样本
            self._response_times.pop(0)
        
        if self._response_times:
            self.metrics.avg_response_time = sum(self._response_times) / len(self._response_times)
            self.metrics.max_response_time = max(self._response_times)
            self.metrics.min_response_time = min(self._response_times)
        
        # 更新连接统计
        if self._connector:
            self.metrics.total_connections = len(self._connector._conns)
            self.metrics.active_connections = len(self._active_requests)
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self._running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _perform_health_check(self):
        """执行健康检查"""
        # 检查连续失败次数
        if self._consecutive_failures >= self.config.max_consecutive_failures:
            self._healthy = False
            logger.warning(f"连接池 {self.service_name} 标记为不健康")
        else:
            self._healthy = True
        
        self._last_health_check = time.time()
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(self.config.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务失败: {e}")
                await asyncio.sleep(self.config.cleanup_interval)
    
    async def _perform_cleanup(self):
        """执行清理"""
        current_time = time.time()
        
        # 清理过期的响应时间数据
        if current_time - self._last_cleanup > 300:  # 5分钟清理一次
            if len(self._response_times) > 100:
                self._response_times = self._response_times[-100:]  # 保留最近100个
            self._last_cleanup = current_time
    
    @property
    def is_healthy(self) -> bool:
        """检查连接池是否健康"""
        return self._healthy and self._running
    
    @property
    def connection_utilization(self) -> float:
        """获取连接使用率"""
        if self.config.max_connections == 0:
            return 0.0
        return self.metrics.active_connections / self.config.max_connections
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return {
            'service_name': self.service_name,
            'healthy': self.is_healthy,
            'utilization': self.connection_utilization,
            'metrics': {
                'total_connections': self.metrics.total_connections,
                'active_connections': self.metrics.active_connections,
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'avg_response_time': self.metrics.avg_response_time,
                'max_response_time': self.metrics.max_response_time,
                'min_response_time': self.metrics.min_response_time,
                'connection_errors': self.metrics.connection_errors
            },
            'config': {
                'max_connections': self.config.max_connections,
                'max_connections_per_host': self.config.max_connections_per_host,
                'connection_timeout': self.config.connection_timeout,
                'read_timeout': self.config.read_timeout
            }
        }


class EnhancedConnectionPoolManager:
    """增强连接池管理器"""
    
    def __init__(self):
        self._pools: Dict[str, EnhancedConnectionPool] = {}
        self._running = False
    
    def create_pool(self, service_name: str, config: EnhancedConnectionConfig) -> EnhancedConnectionPool:
        """创建连接池"""
        if service_name in self._pools:
            raise ValueError(f"连接池 {service_name} 已存在")
        
        pool = EnhancedConnectionPool(service_name, config)
        self._pools[service_name] = pool
        
        return pool
    
    def get_pool(self, service_name: str) -> Optional[EnhancedConnectionPool]:
        """获取连接池"""
        return self._pools.get(service_name)
    
    async def start_all(self):
        """启动所有连接池"""
        if self._running:
            return
        
        for pool in self._pools.values():
            await pool.start()
        
        self._running = True
        logger.info("所有连接池已启动")
    
    async def stop_all(self):
        """停止所有连接池"""
        if not self._running:
            return
        
        for pool in self._pools.values():
            await pool.stop()
        
        self._running = False
        logger.info("所有连接池已停止")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有连接池统计信息"""
        return {
            service_name: pool.get_stats()
            for service_name, pool in self._pools.items()
        }


# 全局连接池管理器实例
enhanced_connection_pool_manager = EnhancedConnectionPoolManager() 