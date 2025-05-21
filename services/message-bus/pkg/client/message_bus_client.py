"""
消息总线客户端SDK
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable, Union

import grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

# 导入生成的gRPC代码
try:
    from api.grpc import message_bus_pb2 as pb
    from api.grpc import message_bus_pb2_grpc as pb_grpc
except ImportError:
    # 假设客户端在外部项目中使用
    try:
        import message_bus_pb2 as pb
        import message_bus_pb2_grpc as pb_grpc
    except ImportError:
        raise ImportError("无法导入message_bus gRPC生成的代码，请确保已安装并可访问")

logger = logging.getLogger(__name__)

class Subscription:
    """订阅对象"""
    
    def __init__(self, client, topic: str, subscription_id: str):
        """
        初始化订阅对象
        
        Args:
            client: 消息总线客户端
            topic: 主题名称
            subscription_id: 订阅ID
        """
        self.client = client
        self.topic = topic
        self.subscription_id = subscription_id
        self.is_active = True
    
    def unsubscribe(self) -> bool:
        """
        取消订阅
        
        Returns:
            bool: 是否成功取消
        """
        if not self.is_active:
            return False
            
        success = self.client.unsubscribe(self.topic, self.subscription_id)
        if success:
            self.is_active = False
            
        return success
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.unsubscribe()

class MessageBusClient:
    """
    消息总线客户端
    
    提供发布和订阅消息的接口，以及主题管理功能
    """
    
    def __init__(
        self, 
        endpoint: str,
        auth_token: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
        secure: bool = False
    ):
        """
        初始化客户端
        
        Args:
            endpoint: 服务端点地址，如"localhost:50051"
            auth_token: 认证令牌，如果需要认证
            timeout: 请求超时时间(秒)
            max_retries: 最大重试次数
            secure: 是否使用TLS加密连接
        """
        self.endpoint = endpoint
        self.auth_token = auth_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.secure = secure
        
        self._channel = None
        self._stub = None
        self._health_stub = None
        self._subscriptions = {}
        self._subscription_tasks = {}
        
        # 初始化连接
        self._initialize()
    
    def _initialize(self):
        """初始化gRPC连接"""
        # 创建认证元数据
        self.metadata = []
        if self.auth_token:
            self.metadata.append(("authorization", f"Bearer {self.auth_token}"))
        
        # 创建gRPC通道
        if self.secure:
            # 使用TLS加密连接
            self._channel = grpc.secure_channel(
                self.endpoint,
                grpc.ssl_channel_credentials()
            )
        else:
            # 使用非加密连接
            self._channel = grpc.insecure_channel(self.endpoint)
        
        # 创建gRPC存根
        self._stub = pb_grpc.MessageBusServiceStub(self._channel)
        self._health_stub = health_pb2_grpc.HealthStub(self._channel)
    
    def close(self):
        """关闭客户端连接"""
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None
            self._health_stub = None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def _call_with_retry(self, method, request, timeout=None):
        """
        带重试的RPC调用
        
        Args:
            method: RPC方法
            request: 请求对象
            timeout: 超时时间，默认使用客户端超时
            
        Returns:
            响应对象
            
        Raises:
            grpc.RpcError: 如果重试后仍然失败
        """
        timeout = timeout or self.timeout
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                return method(request, timeout=timeout, metadata=self.metadata)
            except grpc.RpcError as e:
                retry_count += 1
                last_error = e
                
                # 检查错误是否可重试
                if e.code() in [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED]:
                    if retry_count <= self.max_retries:
                        # 指数退避重试
                        backoff = 0.1 * (2 ** (retry_count - 1))
                        logger.warning(f"RPC调用失败，将在{backoff:.2f}秒后重试(第{retry_count}次): {e}")
                        time.sleep(backoff)
                        continue
                
                # 不可重试的错误或超过重试次数
                raise e
        
        # 超过重试次数
        raise last_error
    
    def publish(
        self, 
        topic: str, 
        payload: Union[bytes, str, Dict[str, Any]], 
        attributes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发布消息到指定主题
        
        Args:
            topic: 主题名称
            payload: 消息内容，可以是字节、字符串或字典
            attributes: 消息属性
            
        Returns:
            Dict[str, Any]: 包含message_id和publish_time的字典
            
        Raises:
            ValueError: 如果主题不存在
            grpc.RpcError: 如果RPC调用失败
        """
        # 处理payload
        if isinstance(payload, dict) or isinstance(payload, list):
            payload = json.dumps(payload).encode('utf-8')
        elif isinstance(payload, str):
            payload = payload.encode('utf-8')
        elif not isinstance(payload, bytes):
            raise TypeError(f"不支持的payload类型: {type(payload)}")
        
        # 创建请求
        request = pb.PublishRequest(
            topic=topic,
            payload=payload,
            attributes=attributes or {}
        )
        
        # 发送请求
        response = self._call_with_retry(self._stub.PublishMessage, request)
        
        # 检查响应
        if not response.success:
            raise ValueError(f"发布消息失败: {response.error_message}")
        
        return {
            "message_id": response.message_id,
            "publish_time": response.publish_time
        }
    
    def create_topic(
        self,
        name: str,
        description: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        partition_count: int = 3,
        retention_hours: int = 24
    ) -> Dict[str, Any]:
        """
        创建新主题
        
        Args:
            name: 主题名称
            description: 主题描述
            properties: 主题属性
            partition_count: 分区数量
            retention_hours: 消息保留时间(小时)
            
        Returns:
            Dict[str, Any]: 主题信息字典
            
        Raises:
            ValueError: 如果主题已存在或名称无效
            grpc.RpcError: 如果RPC调用失败
        """
        # 创建请求
        request = pb.CreateTopicRequest(
            name=name,
            description=description or "",
            properties=properties or {},
            partition_count=partition_count,
            retention_hours=retention_hours
        )
        
        # 发送请求
        response = self._call_with_retry(self._stub.CreateTopic, request)
        
        # 检查响应
        if not response.success:
            raise ValueError(f"创建主题失败: {response.error_message}")
        
        # 转换主题为字典
        topic = response.topic
        return {
            "name": topic.name,
            "description": topic.description,
            "properties": dict(topic.properties),
            "creation_time": topic.creation_time,
            "partition_count": topic.partition_count,
            "retention_hours": topic.retention_hours
        }
    
    def get_topic(self, name: str) -> Dict[str, Any]:
        """
        获取主题信息
        
        Args:
            name: 主题名称
            
        Returns:
            Dict[str, Any]: 主题信息字典
            
        Raises:
            ValueError: 如果主题不存在
            grpc.RpcError: 如果RPC调用失败
        """
        # 创建请求
        request = pb.GetTopicRequest(name=name)
        
        # 发送请求
        response = self._call_with_retry(self._stub.GetTopic, request)
        
        # 检查响应
        if not response.success:
            raise ValueError(f"获取主题失败: {response.error_message}")
        
        # 转换主题为字典
        topic = response.topic
        return {
            "name": topic.name,
            "description": topic.description,
            "properties": dict(topic.properties),
            "creation_time": topic.creation_time,
            "partition_count": topic.partition_count,
            "retention_hours": topic.retention_hours
        }
    
    def list_topics(self, page_size: int = 100, page_token: Optional[str] = None) -> tuple:
        """
        获取主题列表
        
        Args:
            page_size: 每页大小
            page_token: 分页标记
            
        Returns:
            Tuple[List[Dict[str, Any]], Optional[str], int]: 主题列表, 下一页标记, 总主题数
            
        Raises:
            grpc.RpcError: 如果RPC调用失败
        """
        # 创建请求
        request = pb.ListTopicsRequest(
            page_size=page_size,
            page_token=page_token or ""
        )
        
        # 发送请求
        response = self._call_with_retry(self._stub.ListTopics, request)
        
        # 转换主题列表
        topics = []
        for topic in response.topics:
            topics.append({
                "name": topic.name,
                "description": topic.description,
                "properties": dict(topic.properties),
                "creation_time": topic.creation_time,
                "partition_count": topic.partition_count,
                "retention_hours": topic.retention_hours
            })
        
        next_page_token = response.next_page_token if response.next_page_token else None
        
        return topics, next_page_token, response.total_count
    
    def delete_topic(self, name: str) -> bool:
        """
        删除主题
        
        Args:
            name: 主题名称
            
        Returns:
            bool: 是否成功删除
            
        Raises:
            ValueError: 如果删除失败
            grpc.RpcError: 如果RPC调用失败
        """
        # 创建请求
        request = pb.DeleteTopicRequest(name=name)
        
        # 发送请求
        response = self._call_with_retry(self._stub.DeleteTopic, request)
        
        # 检查响应
        if not response.success:
            raise ValueError(f"删除主题失败: {response.error_message}")
        
        return True
    
    def subscribe(
        self,
        topic: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
        filter_attributes: Optional[Dict[str, str]] = None,
        subscription_name: Optional[str] = None,
        max_messages: int = 100,
        timeout_seconds: int = 30
    ) -> Subscription:
        """
        订阅主题以接收消息
        
        Args:
            topic: 主题名称
            callback: 消息处理回调函数
            filter_attributes: 消息过滤属性
            subscription_name: 订阅名称
            max_messages: 最大批量消息数
            timeout_seconds: 超时时间(秒)
            
        Returns:
            Subscription: 订阅对象
            
        Raises:
            ValueError: 如果主题不存在
            grpc.RpcError: 如果RPC调用失败
        """
        # 生成订阅ID
        subscription_id = str(uuid.uuid4())
        
        # 生成订阅名称
        if not subscription_name:
            subscription_name = f"sub-{topic}-{subscription_id[:8]}"
        
        # 创建请求
        request = pb.SubscribeRequest(
            topic=topic,
            subscription_name=subscription_name,
            filter=filter_attributes or {},
            acknowledge=True,
            max_messages=max_messages,
            timeout_seconds=timeout_seconds
        )
        
        # 存储订阅信息
        self._subscriptions[subscription_id] = {
            "topic": topic,
            "subscription_name": subscription_name,
            "filter_attributes": filter_attributes or {}
        }
        
        # 启动订阅任务
        task = asyncio.create_task(self._subscribe_task(request, callback, subscription_id))
        self._subscription_tasks[subscription_id] = task
        
        # 创建订阅对象
        return Subscription(self, topic, subscription_id)
    
    async def _subscribe_task(
        self,
        request: pb.SubscribeRequest,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
        subscription_id: str
    ):
        """
        订阅任务
        
        Args:
            request: 订阅请求
            callback: 消息处理回调函数
            subscription_id: 订阅ID
        """
        retry_count = 0
        max_retries = self.max_retries
        
        while subscription_id in self._subscriptions:
            try:
                # 创建订阅流
                response_stream = self._stub.Subscribe(request, metadata=self.metadata)
                
                # 重置重试计数
                retry_count = 0
                
                # 处理消息
                async for response in response_stream:
                    for message_pb in response.messages:
                        # 如果订阅已取消，退出循环
                        if subscription_id not in self._subscriptions:
                            break
                        
                        # 转换为Python字典
                        message = {
                            "id": message_pb.id,
                            "topic": message_pb.topic,
                            "payload": message_pb.payload,
                            "attributes": dict(message_pb.attributes),
                            "publish_time": message_pb.publish_time,
                            "publisher_id": message_pb.publisher_id
                        }
                        
                        # 调用回调函数
                        try:
                            await callback(message)
                        except Exception as e:
                            logger.error(f"消息处理回调异常: {str(e)}", exc_info=True)
            
            except grpc.RpcError as e:
                # 如果订阅已取消，退出循环
                if subscription_id not in self._subscriptions:
                    break
                
                # 增加重试计数
                retry_count += 1
                
                # 检查是否达到最大重试次数
                if retry_count > max_retries:
                    logger.error(f"订阅重试次数超过最大值，停止重试: {str(e)}")
                    break
                
                # 指数退避重试
                backoff = 0.1 * (2 ** (retry_count - 1))
                logger.warning(f"订阅流中断，将在{backoff:.2f}秒后重试(第{retry_count}次): {e}")
                await asyncio.sleep(backoff)
            
            except Exception as e:
                logger.error(f"订阅任务异常: {str(e)}", exc_info=True)
                break
        
        # 清理任务
        if subscription_id in self._subscription_tasks:
            del self._subscription_tasks[subscription_id]
    
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        """
        取消订阅
        
        Args:
            topic: 主题名称
            subscription_id: 订阅ID
            
        Returns:
            bool: 是否成功取消
        """
        if subscription_id not in self._subscriptions:
            return False
            
        # 移除订阅信息
        del self._subscriptions[subscription_id]
        
        # 取消订阅任务
        if subscription_id in self._subscription_tasks:
            task = self._subscription_tasks[subscription_id]
            task.cancel()
            del self._subscription_tasks[subscription_id]
        
        return True
    
    def health_check(self) -> str:
        """
        检查服务健康状态
        
        Returns:
            str: 服务状态 ("UNKNOWN", "SERVING", "NOT_SERVING", "SERVICE_UNKNOWN")
            
        Raises:
            grpc.RpcError: 如果RPC调用失败
        """
        # 创建请求
        request = health_pb2.HealthCheckRequest(service="messagebus.MessageBusService")
        
        try:
            # 发送请求
            response = self._call_with_retry(self._health_stub.Check, request)
            
            # 返回状态
            status_mapping = {
                health_pb2.HealthCheckResponse.UNKNOWN: "UNKNOWN",
                health_pb2.HealthCheckResponse.SERVING: "SERVING",
                health_pb2.HealthCheckResponse.NOT_SERVING: "NOT_SERVING",
                health_pb2.HealthCheckResponse.SERVICE_UNKNOWN: "SERVICE_UNKNOWN"
            }
            
            return status_mapping.get(response.status, "UNKNOWN")
        except grpc.RpcError as e:
            logger.error(f"健康检查失败: {str(e)}")
            return "NOT_SERVING" 