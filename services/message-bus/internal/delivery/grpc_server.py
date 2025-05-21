import asyncio
import logging
import time
import signal
import grpc
from concurrent import futures
from typing import Optional, Dict, Any, List
import json

from internal.service.message_service import MessageService
from internal.security.auth import AuthInterceptor
from internal.observability.metrics import (
    message_counter, message_publish_latency, api_requests, api_request_latency
)
from internal.delivery.health_check import HealthCheck, HealthServicer
from api.grpc.message_bus_pb2 import (
    PublishRequest, PublishResponse,
    CreateTopicRequest, CreateTopicResponse,
    ListTopicsRequest, ListTopicsResponse,
    GetTopicRequest, GetTopicResponse,
    DeleteTopicRequest, DeleteTopicResponse,
    SubscribeRequest, SubscribeResponse,
    HealthCheckRequest, HealthCheckResponse,
    Topic, Message
)
from api.grpc.message_bus_pb2_grpc import (
    MessageBusServiceServicer, 
    add_MessageBusServiceServicer_to_server
)
from grpc_health.v1 import health_pb2_grpc

logger = logging.getLogger(__name__)

class MessageBusServicer(MessageBusServiceServicer):
    """
    gRPC服务实现，处理消息总线API请求
    """
    
    def __init__(self, message_service: MessageService):
        """
        初始化服务实现
        
        Args:
            message_service: 消息服务
        """
        self.message_service = message_service
        self.subscriptions = {}  # 存储活动订阅
        
    async def PublishMessage(self, request: PublishRequest, context: grpc.ServicerContext) -> PublishResponse:
        """
        发布消息到指定主题
        
        Args:
            request: PublishRequest
            context: gRPC上下文
            
        Returns:
            PublishResponse
        """
        method = "PublishMessage"
        client_id = self._get_client_id(context)
        start_time = time.time()
        
        try:
            # 从请求中提取参数
            topic = request.topic
            payload = request.payload
            attributes = dict(request.attributes)
            
            # 获取用户ID (如果认证启用)
            publisher_id = context.get_value('user_id', 'anonymous')
            
            # 记录请求
            logger.info(f"发布消息请求: 主题={topic}, 发布者={publisher_id}, 客户端={client_id}")
            
            # 发布消息
            message = await self.message_service.publish_message(
                topic=topic,
                payload=payload,
                attributes=attributes,
                publisher_id=publisher_id
            )
            
            # 记录成功指标
            duration = time.time() - start_time
            self._record_success_metrics(method, client_id, duration)
            message_counter.labels(topic=topic, operation="publish").inc()
            message_publish_latency.observe(duration)
            
            # 构建响应
            response = PublishResponse(
                message_id=message.message_id,
                publish_time=message.publish_time,
                success=True
            )
            
            return response
        except ValueError as e:
            # 业务逻辑错误
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            self._record_error_metrics(method, client_id, grpc.StatusCode.INVALID_ARGUMENT, start_time)
            return PublishResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            # 服务内部错误
            logger.error(f"发布消息时发生错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务内部错误")
            self._record_error_metrics(method, client_id, grpc.StatusCode.INTERNAL, start_time)
            return PublishResponse(
                success=False,
                error_message="服务内部错误"
            )
    
    async def CreateTopic(self, request: CreateTopicRequest, context: grpc.ServicerContext) -> CreateTopicResponse:
        """
        创建新主题
        
        Args:
            request: CreateTopicRequest
            context: gRPC上下文
            
        Returns:
            CreateTopicResponse
        """
        method = "CreateTopic"
        client_id = self._get_client_id(context)
        start_time = time.time()
        
        try:
            # 从请求中提取参数
            name = request.name
            description = request.description
            properties = dict(request.properties)
            partition_count = request.partition_count
            retention_hours = request.retention_hours
            
            # 创建主题
            topic = await self.message_service.create_topic(
                name=name,
                description=description,
                properties=properties,
                partition_count=partition_count,
                retention_hours=retention_hours
            )
            
            # 记录成功指标
            duration = time.time() - start_time
            self._record_success_metrics(method, client_id, duration)
            
            # 转换为gRPC主题对象
            topic_pb = self._convert_topic_to_pb(topic)
            
            # 构建响应
            response = CreateTopicResponse(
                success=True,
                topic=topic_pb
            )
            
            return response
        except ValueError as e:
            # 业务逻辑错误
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            self._record_error_metrics(method, client_id, grpc.StatusCode.INVALID_ARGUMENT, start_time)
            return CreateTopicResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            # 服务内部错误
            logger.error(f"创建主题时发生错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务内部错误")
            self._record_error_metrics(method, client_id, grpc.StatusCode.INTERNAL, start_time)
            return CreateTopicResponse(
                success=False,
                error_message="服务内部错误"
            )
    
    async def ListTopics(self, request: ListTopicsRequest, context: grpc.ServicerContext) -> ListTopicsResponse:
        """
        获取主题列表
        
        Args:
            request: ListTopicsRequest
            context: gRPC上下文
            
        Returns:
            ListTopicsResponse
        """
        method = "ListTopics"
        client_id = self._get_client_id(context)
        start_time = time.time()
        
        try:
            # 从请求中提取参数
            page_size = request.page_size
            page_token = request.page_token if request.page_token else None
            
            # 获取主题列表
            topics, next_page_token, total_count = await self.message_service.list_topics(
                page_size=page_size,
                page_token=page_token
            )
            
            # 记录成功指标
            duration = time.time() - start_time
            self._record_success_metrics(method, client_id, duration)
            
            # 转换为gRPC主题对象列表
            topics_pb = [self._convert_topic_to_pb(topic) for topic in topics]
            
            # 构建响应
            response = ListTopicsResponse(
                topics=topics_pb,
                next_page_token=next_page_token if next_page_token else "",
                total_count=total_count
            )
            
            return response
        except Exception as e:
            # 服务内部错误
            logger.error(f"获取主题列表时发生错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务内部错误")
            self._record_error_metrics(method, client_id, grpc.StatusCode.INTERNAL, start_time)
            return ListTopicsResponse()
    
    async def GetTopic(self, request: GetTopicRequest, context: grpc.ServicerContext) -> GetTopicResponse:
        """
        获取主题详情
        
        Args:
            request: GetTopicRequest
            context: gRPC上下文
            
        Returns:
            GetTopicResponse
        """
        method = "GetTopic"
        client_id = self._get_client_id(context)
        start_time = time.time()
        
        try:
            # 从请求中提取参数
            name = request.name
            
            # 获取主题
            topic = await self.message_service.get_topic(name)
            
            # 记录成功指标
            duration = time.time() - start_time
            self._record_success_metrics(method, client_id, duration)
            
            # 转换为gRPC主题对象
            topic_pb = self._convert_topic_to_pb(topic)
            
            # 构建响应
            response = GetTopicResponse(
                topic=topic_pb,
                success=True
            )
            
            return response
        except ValueError as e:
            # 业务逻辑错误
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            self._record_error_metrics(method, client_id, grpc.StatusCode.NOT_FOUND, start_time)
            return GetTopicResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            # 服务内部错误
            logger.error(f"获取主题时发生错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务内部错误")
            self._record_error_metrics(method, client_id, grpc.StatusCode.INTERNAL, start_time)
            return GetTopicResponse(
                success=False,
                error_message="服务内部错误"
            )
    
    async def DeleteTopic(self, request: DeleteTopicRequest, context: grpc.ServicerContext) -> DeleteTopicResponse:
        """
        删除主题
        
        Args:
            request: DeleteTopicRequest
            context: gRPC上下文
            
        Returns:
            DeleteTopicResponse
        """
        method = "DeleteTopic"
        client_id = self._get_client_id(context)
        start_time = time.time()
        
        try:
            # 从请求中提取参数
            name = request.name
            
            # 删除主题
            success = await self.message_service.delete_topic(name)
            
            # 记录成功指标
            duration = time.time() - start_time
            self._record_success_metrics(method, client_id, duration)
            
            # 构建响应
            response = DeleteTopicResponse(
                success=success,
                error_message="" if success else "删除主题失败"
            )
            
            return response
        except ValueError as e:
            # 业务逻辑错误
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            self._record_error_metrics(method, client_id, grpc.StatusCode.NOT_FOUND, start_time)
            return DeleteTopicResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            # 服务内部错误
            logger.error(f"删除主题时发生错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务内部错误")
            self._record_error_metrics(method, client_id, grpc.StatusCode.INTERNAL, start_time)
            return DeleteTopicResponse(
                success=False,
                error_message="服务内部错误"
            )
    
    async def Subscribe(self, request: SubscribeRequest, context: grpc.ServicerContext) -> SubscribeResponse:
        """
        订阅主题消息
        
        Args:
            request: SubscribeRequest
            context: gRPC上下文
            
        Returns:
            Stream of SubscribeResponse
        """
        method = "Subscribe"
        client_id = self._get_client_id(context)
        start_time = time.time()
        
        # 从请求中提取参数
        topic = request.topic
        subscription_name = request.subscription_name
        filter_attributes = dict(request.filter)
        max_messages = request.max_messages or 10
        timeout_seconds = request.timeout_seconds or 30
        
        # 生成订阅ID
        subscription_id = f"{client_id}-{int(time.time())}"
        
        # 记录订阅开始
        logger.info(f"开始订阅: 主题={topic}, 客户端={client_id}, 订阅ID={subscription_id}")
        
        try:
            # 创建消息队列和事件
            queue = asyncio.Queue()
            
            # 定义回调函数
            async def message_callback(message):
                # 将消息放入队列
                await queue.put(message)
            
            # 订阅主题
            subscription_id = await self.message_service.subscribe(
                topic=topic,
                callback=message_callback,
                filter_attributes=filter_attributes,
                subscription_name=subscription_name
            )
            
            # 记录订阅指标
            self._record_success_metrics(method, client_id, time.time() - start_time)
            
            # 超时设置
            end_time = time.time() + timeout_seconds
            
            # 处理订阅
            try:
                while not context.is_active() or time.time() < end_time:
                    messages = []
                    
                    # 收集消息或等待超时
                    remaining_time = max(0, end_time - time.time())
                    
                    # 尝试获取一条消息
                    try:
                        message = await asyncio.wait_for(
                            queue.get(),
                            timeout=remaining_time
                        )
                        messages.append(message)
                        
                        # 尝试快速获取更多消息，直到达到最大数量
                        while len(messages) < max_messages:
                            try:
                                # 非阻塞获取
                                message = queue.get_nowait()
                                messages.append(message)
                            except asyncio.QueueEmpty:
                                break
                    except asyncio.TimeoutError:
                        # 超时，发送当前收集的消息
                        pass
                    
                    # 如果有消息，发送响应
                    if messages:
                        yield SubscribeResponse(messages=messages)
                    
                    # 检查是否达到超时
                    if time.time() >= end_time:
                        break
                
            finally:
                # 确保清理订阅
                self.message_service.unsubscribe(topic, subscription_id)
                logger.info(f"结束订阅: 主题={topic}, 客户端={client_id}, 订阅ID={subscription_id}")
            
        except ValueError as e:
            # 业务逻辑错误
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            self._record_error_metrics(method, client_id, grpc.StatusCode.INVALID_ARGUMENT, start_time)
            # 在流式响应中，我们需要通过设置状态码表示错误
            # 无法返回错误响应
            
        except Exception as e:
            # 服务内部错误
            logger.error(f"订阅时发生错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务内部错误")
            self._record_error_metrics(method, client_id, grpc.StatusCode.INTERNAL, start_time)
    
    def _cleanup_subscription(self, subscription_id: str, topic: str) -> None:
        """
        清理订阅
        
        Args:
            subscription_id: 订阅ID
            topic: 主题名称
        """
        try:
            # 取消订阅
            if subscription_id and topic:
                self.message_service.unsubscribe(topic, subscription_id)
                
            # 移除订阅信息
            if subscription_id in self.subscriptions:
                del self.subscriptions[subscription_id]
                
            logger.info(f"清理订阅: {subscription_id}")
        except Exception as e:
            logger.error(f"清理订阅时发生异常: {str(e)}", exc_info=True)
    
    async def HealthCheck(self, request: HealthCheckRequest, context: grpc.ServicerContext) -> HealthCheckResponse:
        """
        健康检查
        
        Args:
            request: HealthCheckRequest
            context: gRPC上下文
            
        Returns:
            HealthCheckResponse
        """
        method = "HealthCheck"
        client_id = self._get_client_id(context)
        start_time = time.time()
        
        try:
            # 执行简单的健康检查
            service_status = HealthCheckResponse.ServingStatus.SERVING
            
            # 记录成功指标
            self._record_success_metrics(method, client_id, time.time() - start_time)
            return HealthCheckResponse(status=service_status)
        except Exception as e:
            # 服务内部错误
            logger.error(f"健康检查发生错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务内部错误")
            self._record_error_metrics(method, client_id, grpc.StatusCode.INTERNAL, start_time)
            return HealthCheckResponse(status=HealthCheckResponse.ServingStatus.NOT_SERVING)
    
    def _convert_topic_to_pb(self, topic) -> Topic:
        """
        将主题对象转换为gRPC主题对象
        
        Args:
            topic: 主题对象
            
        Returns:
            Topic: gRPC主题对象
        """
        topic_pb = Topic(
            name=topic.name,
            description=topic.description,
            creation_time=topic.creation_time,
            partition_count=topic.partition_count,
            retention_hours=topic.retention_hours
        )
        
        for key, value in topic.properties.items():
            topic_pb.properties[key] = value
            
        return topic_pb
    
    def _convert_message_to_pb(self, message) -> Message:
        """
        将消息对象转换为gRPC消息对象
        
        Args:
            message: 消息对象
            
        Returns:
            Message: gRPC消息对象
        """
        message_pb = Message(
            id=message.message_id,
            topic=message.topic,
            payload=message.payload,
            publish_time=message.publish_time,
            publisher_id=message.publisher_id or ""
        )
        
        for key, value in message.attributes.items():
            message_pb.attributes[key] = value
            
        return message_pb
    
    def _get_client_id(self, context: grpc.ServicerContext) -> str:
        """
        从上下文中获取客户端ID
        
        Args:
            context: gRPC上下文
            
        Returns:
            str: 客户端ID
        """
        # 尝试从认证上下文获取
        client_id = context.get_value('client_id')
        if client_id:
            return client_id
        
        # 尝试从元数据获取
        try:
            metadata = dict(context.invocation_metadata())
            if 'client-id' in metadata:
                return metadata['client-id']
        except:
            pass
        
        # 使用对等信息作为后备
        try:
            peer = context.peer()
            return peer
        except:
            pass
        
        return "unknown"
    
    def _record_success_metrics(self, method: str, client_id: str, duration: float):
        """
        记录成功请求指标
        
        Args:
            method: 方法名称
            client_id: 客户端ID
            duration: 请求处理时间(秒)
        """
        api_requests.labels(endpoint=method, method='unary', status='success').inc()
        api_request_latency.labels(endpoint=method, method='unary').observe(duration)
    
    def _record_error_metrics(self, method: str, client_id: str, status_code: grpc.StatusCode, start_time: float):
        """
        记录错误请求指标
        
        Args:
            method: 方法名称
            client_id: 客户端ID
            status_code: 错误状态码
            start_time: 请求开始时间
        """
        duration = time.time() - start_time
        status = str(status_code).split('.')[-1].lower()
        api_requests.labels(endpoint=method, method='unary', status=status).inc()
        api_request_latency.labels(endpoint=method, method='unary').observe(duration)

class GrpcServer:
    """gRPC服务器"""
    
    def __init__(self, settings, message_service: MessageService):
        """
        初始化gRPC服务器
        
        Args:
            settings: 应用配置
            message_service: 消息服务
        """
        self.settings = settings
        self.server_settings = settings.server
        self.message_service = message_service
        self.server = None
        self.server_interceptors = []  # 服务器拦截器列表
        
        # 健康检查服务
        self.health_check = HealthCheck(settings, message_service)
        self.health_servicer = HealthServicer(self.health_check)
    
    async def start(self):
        """启动gRPC服务器"""
        if self.server:
            logger.warning("gRPC服务器已经在运行")
            return
        
        # 创建服务器，应用拦截器
        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=self.server_settings.max_workers),
            interceptors=self.server_interceptors
        )
        
        # 注册服务
        add_MessageBusServiceServicer_to_server(
            MessageBusServicer(self.message_service),
            self.server
        )
        
        # 添加健康检查服务
        health_pb2_grpc.add_HealthServicer_to_server(self.health_servicer, self.server)
        
        # 绑定端口
        host = self.server_settings.host
        port = self.server_settings.port
        address = f"{host}:{port}"
        self.server.add_insecure_port(address)
        
        # 启动健康检查服务
        await self.health_check.start()
        
        # 启动服务器
        await self.server.start()
        
        logger.info(f"gRPC服务器已启动，监听地址: {address}")
    
    async def stop(self):
        """停止gRPC服务器"""
        if self.server:
            # 优雅关闭服务器
            logger.info("正在优雅关闭gRPC服务器...")
            await self.server.stop(grace=5)  # 5秒优雅关闭期
            logger.info("gRPC服务器已关闭")
            self.server = None
        
        # 停止健康检查服务
        await self.health_check.stop()
    
    async def _monitor_server(self):
        """监控服务器状态"""
        while self.server:
            try:
                # 每30秒检查一次服务器状态
                await asyncio.sleep(30)
                
                # 这里可以添加服务器状态检查逻辑
                if self.server:
                    # 例如检查连接数、负载等
                    pass
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"服务器监控异常: {str(e)}", exc_info=True)
                await asyncio.sleep(5)  # 出错后暂停一下再继续 