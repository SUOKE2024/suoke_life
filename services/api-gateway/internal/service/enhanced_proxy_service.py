"""
enhanced_proxy_service - 索克生活项目模块
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from internal.model.config import GatewayConfig, RetryConfig, ServiceConfig
from internal.service.service_registry import ServiceRegistry
from pkg.utils.circuit_breaker import CircuitBreaker, CircuitBreakerRegistry
from pkg.utils.connection_pool import (
from pkg.utils.enhanced_cache import SmartCacheManager, CacheConfig
from pkg.utils.metrics_collector import MetricsCollector, RequestMetrics
from pkg.utils.smart_load_balancer import (
from typing import Any, Dict, List, Optional, Tuple, Union
import asyncio
import logging
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的代理服务
集成智能连接池、多级缓存、负载均衡和监控指标
"""



    SmartConnectionPool, ConnectionPoolConfig, connection_pool_manager
)
    SmartLoadBalancer, LoadBalancerConfig, LoadBalancerAlgorithm,
    EndpointConfig, LoadBalancerFactory
)

logger = logging.getLogger(__name__)

class EnhancedProxyService:
    """
    增强的代理服务
    集成智能连接池、多级缓存、负载均衡和监控指标
    """
    
    def __init__(
        self, 
        config: GatewayConfig,
        service_registry: ServiceRegistry,
        circuit_breaker_registry: CircuitBreakerRegistry,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        初始化增强代理服务
        
        Args:
            config: 网关配置
            service_registry: 服务注册表
            circuit_breaker_registry: 熔断器注册表
            metrics_collector: 指标收集器
        """
        self.config = config
        self.service_registry = service_registry
        self.circuit_breaker_registry = circuit_breaker_registry
        self.metrics_collector = metrics_collector
        
        # 初始化组件
        self._init_connection_pools()
        self._init_cache_manager()
        self._init_load_balancers()
        
        # 运行时状态
        self._running = False
        self._background_tasks: List[asyncio.Task] = []
    
    def _init_connection_pools(self):
        """初始化连接池"""
        self.connection_pools: Dict[str, SmartConnectionPool] = {}
        
        # 为每个服务创建连接池
        for service_name, service_config in self.config.service_discovery.services.items():
            pool_config = ConnectionPoolConfig(
                max_connections=100,
                max_connections_per_host=30,
                connection_timeout=10.0,
                read_timeout=service_config.timeout,
                keepalive_timeout=30.0,
                enable_cleanup=True,
                cleanup_interval=60.0,
                max_idle_time=300.0
            )
            
            pool = connection_pool_manager.create_pool(service_name, pool_config)
            self.connection_pools[service_name] = pool
            
            logger.info(f"为服务 {service_name} 创建连接池")
    
    def _init_cache_manager(self):
        """初始化缓存管理器"""
        cache_config = CacheConfig(
            enabled=self.config.cache.enabled,
            default_ttl=self.config.cache.default_ttl,
            max_memory_size=100 * 1024 * 1024,  # 100MB
            max_memory_items=10000,
            redis_url=getattr(self.config.cache, 'redis_url', None),
            redis_db=getattr(self.config.cache, 'redis_db', 0),
            compression_enabled=True,
            compression_threshold=1024,
            cache_warming_enabled=True,
            cache_warming_interval=300
        )
        
        self.cache_manager = SmartCacheManager(cache_config)
        
        # 添加缓存规则
        self._setup_cache_rules()
        
        logger.info("缓存管理器已初始化")
    
    def _setup_cache_rules(self):
        """设置缓存规则"""
        # 用户信息缓存5分钟
        self.cache_manager.add_cache_rule(
            pattern=r"/api/users/\d+",
            ttl=300,
            conditions={"headers": {"cache-control": "public"}}
        )
        
        # 健康检查缓存30秒
        self.cache_manager.add_cache_rule(
            pattern=r"/health",
            ttl=30
        )
        
        # 静态资源缓存1小时
        self.cache_manager.add_cache_rule(
            pattern=r"/static/.*",
            ttl=3600
        )
    
    def _init_load_balancers(self):
        """初始化负载均衡器"""
        self.load_balancers: Dict[str, SmartLoadBalancer] = {}
        
        for service_name, service_config in self.config.service_discovery.services.items():
            # 创建负载均衡器配置
            lb_config = LoadBalancerConfig(
                algorithm=LoadBalancerAlgorithm(service_config.load_balancer),
                health_check_enabled=True,
                health_check_interval=30,
                adaptive_weights=True,
                weight_adjustment_interval=60,
                max_weight_factor=2.0,
                min_weight_factor=0.1
            )
            
            # 创建负载均衡器
            load_balancer = SmartLoadBalancer(lb_config)
            
            # 添加端点
            for endpoint in service_config.endpoints:
                endpoint_config = EndpointConfig(
                    host=endpoint.host,
                    port=endpoint.port,
                    weight=getattr(endpoint, 'weight', 1),
                    max_connections=getattr(endpoint, 'max_connections', 100),
                    use_tls=endpoint.use_tls,
                    health_check_path=endpoint.health_check.path if endpoint.health_check.enabled else "/health",
                    health_check_interval=endpoint.health_check.interval if endpoint.health_check.enabled else 30,
                    health_check_timeout=endpoint.health_check.timeout if endpoint.health_check.enabled else 5,
                    health_check_retries=endpoint.health_check.retries if endpoint.health_check.enabled else 3
                )
                load_balancer.add_endpoint(endpoint_config)
            
            self.load_balancers[service_name] = load_balancer
            logger.info(f"为服务 {service_name} 创建负载均衡器")
    
    async def start(self):
        """启动增强代理服务"""
        if self._running:
            return
        
        # 启动连接池
        await connection_pool_manager.start_all()
        
        # 启动缓存管理器
        await self.cache_manager.start()
        
        # 启动负载均衡器
        for load_balancer in self.load_balancers.values():
            await load_balancer.start()
        
        # 启动后台任务
        self._background_tasks.append(
            asyncio.create_task(self._metrics_collection_loop())
        )
        
        self._running = True
        logger.info("增强代理服务已启动")
    
    async def stop(self):
        """停止增强代理服务"""
        if not self._running:
            return
        
        # 停止后台任务
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
        
        # 停止负载均衡器
        for load_balancer in self.load_balancers.values():
            await load_balancer.stop()
        
        # 停止缓存管理器
        await self.cache_manager.stop()
        
        # 停止连接池
        await connection_pool_manager.stop_all()
        
        self._running = False
        logger.info("增强代理服务已停止")
    
    async def forward_request(
        self, 
        request: Request,
        service_name: str,
        path: str
    ) -> Response:
        """
        转发请求到后端服务
        
        Args:
            request: 原始请求
            service_name: 目标服务名称
            path: 目标路径
            
        Returns:
            Response: 后端服务的响应
        """
        start_time = time.time()
        
        # 检查缓存
        if self.cache_manager.config.enabled:
            cached_response = await self.cache_manager.get_cached_response(request)
            if cached_response:
                if self.metrics_collector:
                    self.metrics_collector.record_cache_hit("l1_memory")
                logger.debug(f"返回缓存响应: {service_name}{path}")
                return cached_response
            else:
                if self.metrics_collector:
                    self.metrics_collector.record_cache_miss("l1_memory")
        
        # 获取负载均衡器
        load_balancer = self.load_balancers.get(service_name)
        if not load_balancer:
            error_msg = f"服务 {service_name} 的负载均衡器不存在"
            logger.error(error_msg)
            if self.metrics_collector:
                self.metrics_collector.record_error("load_balancer_not_found", service_name)
            return JSONResponse(
                status_code=503,
                content={"detail": error_msg}
            )
        
        # 选择端点
        client_ip = request.client.host if request.client else None
        endpoint = load_balancer.select_endpoint(client_ip)
        if not endpoint:
            error_msg = f"服务 {service_name} 没有可用的端点"
            logger.error(error_msg)
            if self.metrics_collector:
                self.metrics_collector.record_error("no_available_endpoint", service_name)
            return JSONResponse(
                status_code=503,
                content={"detail": error_msg}
            )
        
        # 获取熔断器
        circuit_breaker = self.circuit_breaker_registry.get_or_create(service_name)
        
        # 检查熔断器状态
        if not circuit_breaker.allow_request():
            error_msg = f"服务 {service_name} 熔断器已打开"
            logger.warning(error_msg)
            if self.metrics_collector:
                self.metrics_collector.record_error("circuit_breaker_open", service_name)
            return JSONResponse(
                status_code=503,
                content={"detail": error_msg}
            )
        
        # 记录请求开始
        load_balancer.record_request_start(endpoint)
        
        try:
            # 执行请求
            response = await self._execute_request(
                request, endpoint, path, service_name, circuit_breaker
            )
            
            # 记录成功
            response_time = time.time() - start_time
            load_balancer.record_request_end(endpoint, True, response_time)
            circuit_breaker.record_result(True)
            
            # 记录指标
            if self.metrics_collector:
                backend_key = f"{endpoint.host}:{endpoint.port}"
                self.metrics_collector.record_backend_request(backend_key, "success", response_time)
            
            # 缓存响应
            if self.cache_manager.config.enabled and response and 200 <= response.status_code < 300:
                await self.cache_manager.cache_response(request, response)
            
            return response
            
        except Exception as e:
            # 记录失败
            response_time = time.time() - start_time
            load_balancer.record_request_end(endpoint, False, response_time)
            circuit_breaker.record_result(False)
            
            # 记录指标
            if self.metrics_collector:
                backend_key = f"{endpoint.host}:{endpoint.port}"
                self.metrics_collector.record_backend_request(backend_key, "error", response_time)
                self.metrics_collector.record_error("request_execution_error", service_name)
            
            logger.error(f"请求执行失败: {service_name}{path}, 错误: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"内部服务器错误: {str(e)}"}
            )
    
    async def _execute_request(
        self,
        request: Request,
        endpoint: EndpointConfig,
        path: str,
        service_name: str,
        circuit_breaker: CircuitBreaker
    ) -> Response:
        """
        执行HTTP请求
        
        Args:
            request: 原始请求
            endpoint: 目标端点
            path: 目标路径
            service_name: 服务名称
            circuit_breaker: 熔断器
            
        Returns:
            Response: HTTP响应
        """
        # 获取连接池
        connection_pool = self.connection_pools.get(service_name)
        if not connection_pool:
            raise RuntimeError(f"服务 {service_name} 的连接池不存在")
        
        # 构建目标URL
        protocol = "https" if endpoint.use_tls else "http"
        base_url = f"{protocol}://{endpoint.host}:{endpoint.port}"
        target_url = f"{base_url}{path}"
        
        # 获取会话
        session = await connection_pool.get_session(service_name, base_url)
        
        # 准备请求参数
        method = request.method
        headers = dict(request.headers)
        
        # 移除不应转发的头部
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # 读取请求体
        body = await request.body()
        
        # 获取重试配置
        retry_config = self.config.retry
        max_retries = retry_config.max_retries if retry_config.enabled else 0
        
        # 执行请求（支持重试）
        for attempt in range(max_retries + 1):
            try:
                async with session.request(
                    method=method,
                    url=target_url,
                    headers=headers,
                    data=body,
                    allow_redirects=False
                ) as resp:
                    # 读取响应内容
                    content = await resp.read()
                    
                    # 创建响应对象
                    response_headers = dict(resp.headers)
                    
                    # 移除不应返回的头部
                    response_headers.pop("transfer-encoding", None)
                    response_headers.pop("connection", None)
                    
                    response = Response(
                        content=content,
                        status_code=resp.status,
                        headers=response_headers,
                        media_type=response_headers.get("content-type")
                    )
                    
                    # 检查是否需要重试
                    if (
                        retry_config.enabled and 
                        attempt < max_retries and 
                        resp.status in retry_config.retry_status_codes
                    ):
                        retry_delay = retry_config.retry_delay * (2 ** attempt)  # 指数退避
                        logger.warning(
                            f"请求失败，准备第 {attempt + 1} 次重试: {method} {target_url}, "
                            f"状态码: {resp.status}, 延迟: {retry_delay}s"
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    
                    return response
                    
            except Exception as e:
                if attempt < max_retries:
                    retry_delay = retry_config.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"请求异常，准备第 {attempt + 1} 次重试: {method} {target_url}, "
                        f"错误: {e}, 延迟: {retry_delay}s"
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    raise
        
        # 如果所有重试都失败，抛出异常
        raise RuntimeError(f"请求失败，已达到最大重试次数: {max_retries}")
    
    async def _metrics_collection_loop(self):
        """指标收集循环"""
        while self._running:
            try:
                await asyncio.sleep(30)  # 每30秒收集一次指标
                await self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"指标收集出错: {e}")
    
    async def _collect_metrics(self):
        """收集指标"""
        if not self.metrics_collector:
            return
        
        # 收集连接池指标
        for service_name, pool in self.connection_pools.items():
            stats = pool.get_total_stats()
            self.metrics_collector.update_active_connections(service_name, stats.active_connections)
            self.metrics_collector.update_connection_pool_size(service_name, stats.total_connections)
        
        # 收集负载均衡器指标
        for service_name, load_balancer in self.load_balancers.items():
            stats = load_balancer.get_stats()
            for endpoint_key, endpoint_stats in stats["endpoint_stats"].items():
                self.metrics_collector.update_backend_health(
                    endpoint_key, 
                    endpoint_stats["is_healthy"]
                )
        
        # 收集缓存指标
        cache_stats = self.cache_manager.get_stats()
        for level, stats in cache_stats["cache_stats"].items():
            self.metrics_collector.update_cache_size(level, stats.memory_usage)
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        stats = {
            "running": self._running,
            "connection_pools": {},
            "load_balancers": {},
            "cache_stats": self.cache_manager.get_stats() if self.cache_manager else {},
            "background_tasks": len(self._background_tasks)
        }
        
        # 连接池统计
        for service_name, pool in self.connection_pools.items():
            stats["connection_pools"][service_name] = pool.get_stats()
        
        # 负载均衡器统计
        for service_name, load_balancer in self.load_balancers.items():
            stats["load_balancers"][service_name] = load_balancer.get_stats()
        
        return stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        healthy_services = 0
        total_services = len(self.load_balancers)
        
        for load_balancer in self.load_balancers.values():
            stats = load_balancer.get_stats()
            if stats["healthy_endpoints"] > 0:
                healthy_services += 1
        
        return {
            "status": "healthy" if self._running and healthy_services > 0 else "unhealthy",
            "running": self._running,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "components": {
                "connection_pools": len(self.connection_pools),
                "load_balancers": len(self.load_balancers),
                "cache_manager": self.cache_manager is not None,
                "metrics_collector": self.metrics_collector is not None
            }
        } 