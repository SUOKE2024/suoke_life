"""
指标收集模块，提供Prometheus指标采集功能
"""
import time
import logging
import asyncio
import threading
from typing import Dict, Callable, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server, REGISTRY, Info

from config.settings import Settings

logger = logging.getLogger(__name__)

# 服务信息
service_info = Info('message_bus_info', 'Message Bus service information')

# 请求相关指标
request_counter = Counter(
    'message_bus_requests_total', 
    'Total number of requests received',
    ['method', 'status', 'client']
)

request_latency = Histogram(
    'message_bus_request_latency_seconds', 
    'Request latency in seconds',
    ['method'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# 消息相关指标
message_counter = Counter(
    'message_bus_messages_total', 
    'Total number of messages processed',
    ['topic', 'operation']
)

message_publish_latency = Histogram(
    'message_bus_publish_latency_seconds', 
    'Message publish latency in seconds',
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
)

message_consume_latency = Histogram(
    'message_bus_consume_latency_seconds', 
    'Message consume latency in seconds',
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

message_publish_failures = Counter(
    'message_bus_publish_failures_total', 
    'Total number of failed message publishes',
    ['error']
)

message_consume_failures = Counter(
    'message_bus_consume_failures_total', 
    'Total number of failed message consumes',
    ['error']
)

# 主题相关指标
topic_count = Gauge(
    'message_bus_topics_count', 
    'Number of active topics'
)

topic_message_count = Gauge(
    'message_bus_topic_messages_count', 
    'Number of messages in a topic',
    ['topic']
)

topic_operations = Counter(
    'message_bus_topic_operations_total', 
    'Topic operations (create, delete)',
    ['operation', 'status']
)

# 订阅相关指标
subscription_count = Gauge(
    'message_bus_subscriptions_count', 
    'Number of active subscriptions',
    ['topic']
)

subscription_operations = Counter(
    'message_bus_subscription_operations_total', 
    'Subscription operations (subscribe, unsubscribe)',
    ['operation']
)

# 系统健康指标
up = Gauge(
    'message_bus_up', 
    'Indicates if the service is up and running (1 = up, 0 = down)'
)

system_info = Gauge(
    'message_bus_system_info', 
    'System resource usage',
    ['resource']
)

kafka_connection_status = Gauge(
    'message_bus_kafka_connection_status', 
    'Kafka connection status (1 = up, 0 = down)'
)

redis_connection_status = Gauge(
    'message_bus_redis_connection_status', 
    'Redis connection status (1 = up, 0 = down)'
)

# 监控API端点使用情况
api_requests = Counter(
    'message_bus_api_requests_total', 
    'API requests count',
    ['endpoint', 'method', 'status']
)

api_request_latency = Histogram(
    'message_bus_api_request_latency_seconds', 
    'API request latency in seconds',
    ['endpoint', 'method'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
)

class MetricsService:
    """
    指标监控服务，负责收集和暴露Prometheus指标
    """
    
    def __init__(self, settings: Settings):
        """
        初始化指标服务
        
        Args:
            settings: 应用程序配置
        """
        self.settings = settings
        self.metrics_server = None
        self.server_thread = None
        self.running = False
        
        # 设置服务基本信息
        service_info.info({
            'version': '1.0.0',
            'environment': settings.environment,
            'service_name': settings.service_name
        })
        
        # 设置服务状态
        up.set(1)
        
        # 消息相关指标
        self.message_publish_counter = Counter(
            'message_publish_total',
            '发布消息数量',
            ['topic', 'status']
        )
        
        self.message_publish_latency = Histogram(
            'message_publish_latency_seconds',
            '消息发布延迟(秒)',
            ['topic'],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
        )
        
        self.messages_consumed_counter = Counter(
            'messages_consumed_total',
            '消费消息数量',
            ['topic', 'consumer_group']
        )
        
        # 主题相关指标
        self.topic_count = Gauge(
            'topics_total',
            '主题总数'
        )
        
        self.topic_operations_counter = Counter(
            'topic_operations_total',
            '主题操作次数',
            ['operation', 'status']
        )
        
        # 订阅相关指标
        self.active_subscriptions = Gauge(
            'active_subscriptions',
            '活动订阅数量',
            ['topic']
        )
        
        # 系统相关指标
        self.system_errors = Counter(
            'system_errors_total',
            '系统错误数量',
            ['component', 'error_type']
        )
        
        # API相关指标
        self.api_requests_counter = Counter(
            'api_requests_total',
            'API请求总数',
            ['method', 'status']
        )
        
        self.api_request_latency = Histogram(
            'api_request_latency_seconds',
            'API请求延迟(秒)',
            ['method'],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
        )
        
        # 开始HTTP服务器(如果启用)
        if self.settings.metrics.enabled:
            self._start_http_server()
    
    def _start_http_server(self):
        """启动Prometheus指标HTTP服务器"""
        try:
            host = self.settings.metrics.host
            port = self.settings.metrics.port
            
            start_http_server(port, host)
            logger.info(f"Prometheus指标服务器已启动，监听地址: {host}:{port}")
        except Exception as e:
            logger.error(f"启动Prometheus指标服务器失败: {str(e)}", exc_info=True)
            up.set(0)
    
    def track_message_publish(self, topic: str, success: bool = True) -> None:
        """
        记录消息发布指标
        
        Args:
            topic: 主题名称
            success: 是否发布成功
        """
        status = "success" if success else "failure"
        self.message_publish_counter.labels(topic=topic, status=status).inc()
    
    def track_message_publish_time(self, topic: str) -> Callable:
        """
        跟踪消息发布时间
        
        Args:
            topic: 主题名称
            
        Returns:
            Callable: 带有上下文管理器协议的对象
        """
        return self.message_publish_latency.labels(topic=topic).time()
    
    def track_message_consumed(self, topic: str, consumer_group: str) -> None:
        """
        记录消息消费指标
        
        Args:
            topic: 主题名称
            consumer_group: 消费者组ID
        """
        self.messages_consumed_counter.labels(topic=topic, consumer_group=consumer_group).inc()
    
    def update_topic_count(self, count: int) -> None:
        """
        更新主题数量
        
        Args:
            count: 主题总数
        """
        self.topic_count.set(count)
    
    def track_topic_operation(self, operation: str, success: bool = True) -> None:
        """
        记录主题操作指标
        
        Args:
            operation: 操作类型 (create, delete, update, get, list)
            success: 是否操作成功
        """
        status = "success" if success else "failure"
        self.topic_operations_counter.labels(operation=operation, status=status).inc()
    
    def update_active_subscriptions(self, topic: str, count: int) -> None:
        """
        更新活动订阅数量
        
        Args:
            topic: 主题名称
            count: 订阅数量
        """
        self.active_subscriptions.labels(topic=topic).set(count)
    
    def track_system_error(self, component: str, error_type: str) -> None:
        """
        记录系统错误
        
        Args:
            component: 组件名称
            error_type: 错误类型
        """
        self.system_errors.labels(component=component, error_type=error_type).inc()
    
    def track_api_request(self, method: str, status: str) -> None:
        """
        记录API请求
        
        Args:
            method: 方法名称
            status: 状态 (success, error)
        """
        self.api_requests_counter.labels(method=method, status=status).inc()
    
    def track_api_request_time(self, method: str) -> Callable:
        """
        跟踪API请求时间
        
        Args:
            method: 方法名称
            
        Returns:
            Callable: 带有上下文管理器协议的对象
        """
        return self.api_request_latency.labels(method=method).time()

    def start(self):
        """启动指标服务器"""
        if not self.settings.metrics.enabled:
            logger.info("指标服务已禁用")
            return
        
        if self.running:
            logger.warning("指标服务已经在运行")
            return
        
        try:
            host = self.settings.metrics.host
            port = self.settings.metrics.port
            
            logger.info(f"启动指标服务器: {host}:{port}")
            
            # 在单独的线程中启动HTTP服务器
            def start_server():
                try:
                    start_http_server(port=port, addr=host)
                    logger.info(f"指标服务器已启动: http://{host}:{port}/metrics")
                except Exception as e:
                    logger.error(f"启动指标服务器失败: {str(e)}", exc_info=True)
                    up.set(0)
            
            self.server_thread = threading.Thread(target=start_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            
            # 启动后台资源监控
            asyncio.create_task(self._monitor_resources())
            
        except Exception as e:
            logger.error(f"启动指标服务失败: {str(e)}", exc_info=True)
            up.set(0)
    
    def stop(self):
        """停止指标服务器"""
        if not self.running:
            return
        
        logger.info("停止指标服务器")
        self.running = False
        
        # 由于Prometheus client没有提供停止HTTP服务器的方法，
        # 我们只能关闭资源监控并标记服务为停止状态
        up.set(0)
    
    async def _monitor_resources(self):
        """定期监控系统资源使用情况"""
        if not self.running:
            return
        
        try:
            import psutil
            
            while self.running:
                try:
                    # 获取CPU使用率
                    cpu_percent = psutil.cpu_percent()
                    system_info.labels(resource='cpu_percent').set(cpu_percent)
                    
                    # 获取内存使用情况
                    memory = psutil.virtual_memory()
                    system_info.labels(resource='memory_used_percent').set(memory.percent)
                    system_info.labels(resource='memory_used_mb').set(memory.used / (1024 * 1024))
                    
                    # 获取磁盘使用情况
                    disk = psutil.disk_usage('/')
                    system_info.labels(resource='disk_used_percent').set(disk.percent)
                    
                    # 获取进程信息
                    process = psutil.Process()
                    process_memory = process.memory_info().rss / (1024 * 1024)  # MB
                    system_info.labels(resource='process_memory_mb').set(process_memory)
                    
                    process_cpu = process.cpu_percent()
                    system_info.labels(resource='process_cpu_percent').set(process_cpu)
                    
                    # 获取连接数
                    connections = len(process.connections())
                    system_info.labels(resource='connections').set(connections)
                    
                except Exception as e:
                    logger.error(f"监控资源失败: {str(e)}")
                
                # 每15秒收集一次
                await asyncio.sleep(15)
        
        except ImportError:
            logger.warning("缺少psutil模块，无法监控系统资源")
    
    def track_request(self, method, status_code, client_id, duration):
        """
        记录请求指标
        
        Args:
            method: 请求方法
            status_code: 状态码
            client_id: 客户端ID
            duration: 请求处理时间
        """
        status = 'success' if 200 <= status_code < 400 else 'error'
        request_counter.labels(method=method, status=status, client=client_id).inc()
        request_latency.labels(method=method).observe(duration)
    
    def track_message(self, topic, operation):
        """
        记录消息操作指标
        
        Args:
            topic: 主题名称
            operation: 操作类型
        """
        message_counter.labels(topic=topic, operation=operation).inc()
    
    def update_topic_message_count(self, topic, count):
        """
        更新主题消息数量
        
        Args:
            topic: 主题名称
            count: 消息数量
        """
        topic_message_count.labels(topic=topic).set(count)
    
    def update_subscription_count(self, topic, count):
        """
        更新订阅数量
        
        Args:
            topic: 主题名称
            count: 订阅数量
        """
        subscription_count.labels(topic=topic).set(count)
    
    def track_subscription_operation(self, operation):
        """
        记录订阅操作
        
        Args:
            operation: 操作类型(subscribe, unsubscribe)
        """
        subscription_operations.labels(operation=operation).inc()
    
    def update_kafka_connection(self, is_connected):
        """
        更新Kafka连接状态
        
        Args:
            is_connected: 是否连接
        """
        kafka_connection_status.set(1 if is_connected else 0)
    
    def update_redis_connection(self, is_connected):
        """
        更新Redis连接状态
        
        Args:
            is_connected: 是否连接
        """
        redis_connection_status.set(1 if is_connected else 0)
    
    def track_api_request(self, endpoint, method, status_code, duration):
        """
        记录API请求
        
        Args:
            endpoint: API端点
            method: 请求方法
            status_code: 状态码
            duration: 请求处理时间
        """
        status = 'success' if 200 <= status_code < 400 else 'error'
        api_requests.labels(endpoint=endpoint, method=method, status=status).inc()
        api_request_latency.labels(endpoint=endpoint, method=method).observe(duration)


# 装饰器
def track_time(metric_fn, *args, **kwargs):
    """
    测量函数执行时间的装饰器
    
    Args:
        metric_fn: 指标函数
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        async def wrapper(*func_args, **func_kwargs):
            with metric_fn(*args, **kwargs):
                return await func(*func_args, **func_kwargs)
        return wrapper
    return decorator 