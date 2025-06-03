import asyncio
import logging
import time
from typing import Dict, Any, Optional
from enum import Enum
from aiohttp import web
from grpc_health.v1 import health_pb2, health_pb2_grpc

from internal.service.message_service import MessageService
from internal.observability.metrics import up

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """健康状态枚举"""
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    DEGRADED = "DEGRADED"

class ComponentHealth:
    """组件健康状态"""
    
    def __init__(self, name: str):
        """初始化组件健康状态"""
        self.name = name
        self.status = HealthStatus.UNKNOWN
        self.details = ""
        self.last_check_time = 0
        self.response_time = 0
    
    def update(self, status: HealthStatus, details: str = "", response_time: float = 0):
        """更新组件状态"""
        self.status = status
        self.details = details
        self.last_check_time = time.time()
        self.response_time = response_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "status": self.status.value,
            "details": self.details,
            "last_check_time": self.last_check_time,
            "response_time_ms": round(self.response_time * 1000, 2)
        }

class HealthCheck:
    """健康检查服务"""
    
    def __init__(self, settings, message_service: MessageService):
        """
        初始化健康检查服务
        
        Args:
            settings: 应用程序配置
            message_service: 消息服务实例
        """
        self.settings = settings
        self.message_service = message_service
        self.components: Dict[str, ComponentHealth] = {
            "message_service": ComponentHealth("message_service"),
            "kafka": ComponentHealth("kafka"),
            "redis": ComponentHealth("redis"),
            "topic_repository": ComponentHealth("topic_repository")
        }
        self.overall_status = HealthStatus.UNKNOWN
        self.last_check_time = 0
        
        # 健康检查间隔(秒)
        self.check_interval = 60
        self.is_running = False
        self.check_task = None
    
    async def start(self):
        """启动健康检查服务"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动定期健康检查
        self.check_task = asyncio.create_task(self._health_check_loop())
        logger.info("健康检查服务已启动")
    
    async def stop(self):
        """停止健康检查服务"""
        self.is_running = False
        
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
            self.check_task = None
        
        logger.info("健康检查服务已停止")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_running:
            try:
                await self.check_health()
            except Exception as e:
                logger.error(f"健康检查异常: {str(e)}", exc_info=True)
            
            # 等待下一次检查
            await asyncio.sleep(self.check_interval)
    
    async def check_health(self) -> HealthStatus:
        """
        执行健康检查
        
        Returns:
            HealthStatus: 总体健康状态
        """
        logger.debug("执行健康检查")
        start_time = time.time()
        
        # 检查消息服务
        await self._check_message_service()
        
        # 检查Kafka连接
        await self._check_kafka()
        
        # 检查Redis连接(如果使用)
        await self._check_redis()
        
        # 检查主题存储
        await self._check_topic_repository()
        
        # 更新总体状态
        self._update_overall_status()
        
        self.last_check_time = time.time()
        check_duration = self.last_check_time - start_time
        
        logger.debug(f"健康检查完成，耗时: {check_duration:.2f}秒，状态: {self.overall_status.value}")
        
        # 更新Prometheus指标
        up.set(1 if self.overall_status == HealthStatus.HEALTHY else 0)
        
        return self.overall_status
    
    async def _check_message_service(self):
        """检查消息服务健康状态"""
        component = self.components["message_service"]
        start_time = time.time()
        
        try:
            # 创建测试主题，确认服务工作正常
            test_topic_name = f"health-check-{int(time.time())}"
            
            # 尝试创建主题
            await self.message_service.create_topic(
                name=test_topic_name,
                description="Health check test topic",
                retention_hours=1
            )
            
            # 尝试列出主题
            topics, _, _ = await self.message_service.list_topics(page_size=10)
            
            # 删除测试主题
            await self.message_service.delete_topic(test_topic_name)
            
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.HEALTHY,
                details=f"服务正常，主题数量: {len(topics)}",
                response_time=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.UNHEALTHY,
                details=f"服务异常: {str(e)}",
                response_time=duration
            )
    
    async def _check_kafka(self):
        """检查Kafka连接健康状态"""
        component = self.components["kafka"]
        start_time = time.time()
        
        try:
            # 检查与Kafka的连接
            kafka_servers = self.settings.kafka.bootstrap_servers
            
            # 使用Message Repository的功能检查Kafka连接
            # 这里假设在MessageService中可以访问到消息存储库实例
            message_repo = self.message_service.message_repository
            
            # 创建一个临时消费者检测Kafka连通性
            from aiokafka.admin import AIOKafkaAdminClient
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=kafka_servers,
                client_id=f"health-check-{int(time.time())}"
            )
            
            await admin_client.start()
            cluster_info = await admin_client.describe_cluster()
            
            broker_count = len(cluster_info["brokers"])
            controller_id = cluster_info["controller"].id
            
            await admin_client.close()
            
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.HEALTHY,
                details=f"Kafka集群正常，Broker数量: {broker_count}, 控制器ID: {controller_id}",
                response_time=duration
            )
        
        except Exception as e:
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.UNHEALTHY,
                details=f"Kafka连接异常: {str(e)}",
                response_time=duration
            )
    
    async def _check_redis(self):
        """检查Redis连接健康状态"""
        component = self.components["redis"]
        start_time = time.time()
        
        # 检查当前是否使用Redis作为主题存储
        if self.settings.environment in ["development", "testing"]:
            # 开发环境使用文件存储，跳过Redis检查
            component.update(
                status=HealthStatus.UNKNOWN,
                details="在当前环境中不使用Redis",
                response_time=0
            )
            return
        
        try:
            # 获取Redis配置
            redis_config = self.settings.redis
            
            # 尝试连接Redis并执行PING命令
            import aioredis
            redis = await aioredis.create_redis_pool(
                f"redis://{redis_config.host}:{redis_config.port}",
                db=redis_config.db,
                password=redis_config.password,
                ssl=redis_config.use_ssl
            )
            
            # 执行PING命令
            ping_result = await redis.ping()
            
            # 获取Redis信息
            info = await redis.info()
            redis_version = info.get("server", {}).get("redis_version", "unknown")
            connected_clients = info.get("clients", {}).get("connected_clients", 0)
            
            # 关闭连接
            redis.close()
            await redis.wait_closed()
            
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.HEALTHY,
                details=f"Redis连接正常，版本: {redis_version}, 连接数: {connected_clients}",
                response_time=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.UNHEALTHY,
                details=f"Redis连接异常: {str(e)}",
                response_time=duration
            )
    
    async def _check_topic_repository(self):
        """检查主题存储库健康状态"""
        component = self.components["topic_repository"]
        start_time = time.time()
        
        try:
            # 检查主题存储库
            topic_repo = self.message_service.topic_repository
            
            # 尝试列出主题
            topics, _, total = await topic_repo.list_topics(page_size=10)
            
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.HEALTHY,
                details=f"主题存储库正常，主题数量: {total}",
                response_time=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            component.update(
                status=HealthStatus.UNHEALTHY,
                details=f"主题存储库异常: {str(e)}",
                response_time=duration
            )
    
    def _update_overall_status(self):
        """更新总体健康状态"""
        # 检查所有组件状态
        has_unhealthy = False
        has_degraded = False
        all_unknown = True
        
        for component in self.components.values():
            if component.status == HealthStatus.UNHEALTHY:
                has_unhealthy = True
            elif component.status == HealthStatus.DEGRADED:
                has_degraded = True
            
            if component.status != HealthStatus.UNKNOWN:
                all_unknown = False
        
        # 确定总体状态
        if all_unknown:
            self.overall_status = HealthStatus.UNKNOWN
        elif has_unhealthy:
            self.overall_status = HealthStatus.UNHEALTHY
        elif has_degraded:
            self.overall_status = HealthStatus.DEGRADED
        else:
            self.overall_status = HealthStatus.HEALTHY
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        获取健康报告
        
        Returns:
            Dict[str, Any]: 健康报告字典
        """
        return {
            "status": self.overall_status.value,
            "timestamp": self.last_check_time,
            "components": {name: component.to_dict() for name, component in self.components.items()},
            "service": {
                "name": self.settings.service_name,
                "environment": self.settings.environment,
                "version": "1.0.0"  # 应从配置或构建信息中获取
            }
        }

class HealthCheckHTTPHandler:
    """HTTP健康检查处理器"""
    
    def __init__(self, health_check: HealthCheck):
        """
        初始化HTTP健康检查处理器
        
        Args:
            health_check: 健康检查服务实例
        """
        self.health_check = health_check
    
    async def handle_health_check(self, request: web.Request) -> web.Response:
        """
        处理健康检查请求
        
        Args:
            request: HTTP请求
        
        Returns:
            web.Response: HTTP响应
        """
        # 检查是否要求进行完整检查
        perform_check = request.query.get('check', '').lower() in ['true', '1', 'yes']
        
        if perform_check:
            await self.health_check.check_health()
        
        # 获取健康报告
        report = self.health_check.get_health_report()
        
        # 设置状态码
        status_code = 200
        if report["status"] == HealthStatus.UNHEALTHY.value:
            status_code = 503  # Service Unavailable
        elif report["status"] == HealthStatus.DEGRADED.value:
            status_code = 429  # Too Many Requests (often used for degraded)
        elif report["status"] == HealthStatus.UNKNOWN.value:
            status_code = 500  # Internal Server Error
        
        return web.json_response(report, status=status_code)
    
    async def handle_liveness(self, request: web.Request) -> web.Response:
        """
        处理存活检查请求 (Kubernetes Liveness Probe)
        
        返回简单的状态，只检查服务是否运行
        
        Args:
            request: HTTP请求
        
        Returns:
            web.Response: HTTP响应
        """
        # 简单的存活检查，只要服务在运行就返回成功
        return web.json_response({"status": "UP"})
    
    async def handle_readiness(self, request: web.Request) -> web.Response:
        """
        处理就绪检查请求 (Kubernetes Readiness Probe)
        
        检查服务是否能够处理请求
        
        Args:
            request: HTTP请求
        
        Returns:
            web.Response: HTTP响应
        """
        # 获取当前健康状态，但不执行完整检查
        report = self.health_check.get_health_report()
        
        # 检查服务是否就绪
        is_ready = report["status"] in [HealthStatus.HEALTHY.value, HealthStatus.DEGRADED.value]
        
        if is_ready:
            return web.json_response({"status": "READY"})
        else:
            return web.json_response({"status": "NOT_READY"}, status=503)
    
    def setup_routes(self, app: web.Application):
        """
        设置路由
        
        Args:
            app: AIOHTTP应用实例
        """
        app.router.add_get('/health', self.handle_health_check)
        app.router.add_get('/health/live', self.handle_liveness)
        app.router.add_get('/health/ready', self.handle_readiness)

class HealthServicer(health_pb2_grpc.HealthServicer):
    """gRPC健康检查服务实现"""
    
    def __init__(self, health_check: HealthCheck):
        """
        初始化gRPC健康检查服务
        
        Args:
            health_check: 健康检查服务实例
        """
        self.health_check = health_check
    
    async def Check(self, request, context):
        """
        执行健康检查
        
        Args:
            request: gRPC请求
            context: gRPC上下文
        
        Returns:
            HealthCheckResponse: 健康检查响应
        """
        # 获取当前健康状态
        current_status = self.health_check.overall_status
        
        # 将HealthStatus映射到gRPC HealthCheckResponse.ServingStatus
        status_map = {
            HealthStatus.UNKNOWN: health_pb2.HealthCheckResponse.UNKNOWN,
            HealthStatus.HEALTHY: health_pb2.HealthCheckResponse.SERVING,
            HealthStatus.UNHEALTHY: health_pb2.HealthCheckResponse.NOT_SERVING,
            HealthStatus.DEGRADED: health_pb2.HealthCheckResponse.SERVING  # 降级状态仍然为服务中
        }
        
        return health_pb2.HealthCheckResponse(
            status=status_map.get(current_status, health_pb2.HealthCheckResponse.UNKNOWN)
        )
    
    async def Watch(self, request, context):
        """
        监视健康状态变化
        
        Args:
            request: gRPC请求
            context: gRPC上下文
            
        Yields:
            HealthCheckResponse: 健康检查响应
        """
        # 每5秒发送一次健康状态更新
        last_status = None
        
        while True:
            # 获取当前健康状态
            current_status = self.health_check.overall_status
            
            # 如果状态变化或是第一次报告，则发送更新
            if current_status != last_status or last_status is None:
                status_map = {
                    HealthStatus.UNKNOWN: health_pb2.HealthCheckResponse.UNKNOWN,
                    HealthStatus.HEALTHY: health_pb2.HealthCheckResponse.SERVING,
                    HealthStatus.UNHEALTHY: health_pb2.HealthCheckResponse.NOT_SERVING,
                    HealthStatus.DEGRADED: health_pb2.HealthCheckResponse.SERVING
                }
                
                yield health_pb2.HealthCheckResponse(
                    status=status_map.get(current_status, health_pb2.HealthCheckResponse.UNKNOWN)
                )
                
                last_status = current_status
            
            await asyncio.sleep(5) 