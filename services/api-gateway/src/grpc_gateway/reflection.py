"""
gRPC反射客户端模块

提供服务发现和动态调用功能
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
import grpc
from grpc import aio
from grpc_reflection.v1alpha import reflection_pb2
from grpc_reflection.v1alpha import reflection_pb2_grpc
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.message_factory import MessageFactory
import structlog

logger = structlog.get_logger(__name__)


class GrpcReflectionClient:
    """gRPC反射客户端"""
    
    def __init__(self, channel: aio.Channel):
        self.channel = channel
        self.stub = reflection_pb2_grpc.ServerReflectionStub(channel)
        self.descriptor_pool = DescriptorPool()
        self.message_factory = MessageFactory(self.descriptor_pool)
        self._services: Dict[str, Dict[str, Any]] = {}
        self._file_descriptors: Dict[str, FileDescriptorProto] = {}
        
    async def discover_services(self) -> List[str]:
        """发现所有可用的服务"""
        try:
            request = reflection_pb2.ServerReflectionRequest()
            request.list_services = ""
            
            async with self.stub.ServerReflectionInfo([request]) as call:
                async for response in call:
                    if response.HasField('list_services_response'):
                        services = [
                            service.name 
                            for service in response.list_services_response.service
                        ]
                        
                        logger.info(
                            "发现gRPC服务",
                            services=services,
                            count=len(services)
                        )
                        
                        return services
            
            return []
            
        except Exception as e:
            logger.error(
                "服务发现失败",
                error=str(e)
            )
            raise
    
    async def get_service_descriptor(self, service_name: str) -> Optional[Dict[str, Any]]:
        """获取服务描述符"""
        if service_name in self._services:
            return self._services[service_name]
        
        try:
            # 获取文件描述符
            request = reflection_pb2.ServerReflectionRequest()
            request.file_containing_symbol = service_name
            
            async with self.stub.ServerReflectionInfo([request]) as call:
                async for response in call:
                    if response.HasField('file_descriptor_response'):
                        # 处理文件描述符
                        for proto_bytes in response.file_descriptor_response.file_descriptor_proto:
                            file_desc = FileDescriptorProto()
                            file_desc.ParseFromString(proto_bytes)
                            
                            # 添加到描述符池
                            self.descriptor_pool.Add(file_desc)
                            self._file_descriptors[file_desc.name] = file_desc
                            
                            # 查找服务
                            for service in file_desc.service:
                                if service.name == service_name.split('.')[-1]:
                                    service_info = self._parse_service_descriptor(service, file_desc)
                                    self._services[service_name] = service_info
                                    
                                    logger.info(
                                        "获取服务描述符成功",
                                        service=service_name,
                                        methods=len(service_info['methods'])
                                    )
                                    
                                    return service_info
            
            return None
            
        except Exception as e:
            logger.error(
                "获取服务描述符失败",
                service=service_name,
                error=str(e)
            )
            raise
    
    async def get_method_descriptor(
        self,
        service_name: str,
        method_name: str
    ) -> Optional[Dict[str, Any]]:
        """获取方法描述符"""
        service_desc = await self.get_service_descriptor(service_name)
        if not service_desc:
            return None
        
        return service_desc['methods'].get(method_name)
    
    async def call_method(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        metadata: Optional[List[tuple]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """动态调用gRPC方法"""
        try:
            # 获取方法描述符
            method_desc = await self.get_method_descriptor(service_name, method_name)
            if not method_desc:
                raise ValueError(f"方法不存在: {service_name}.{method_name}")
            
            # 创建请求消息
            request_class = self.message_factory.GetPrototype(
                self.descriptor_pool.FindMessageTypeByName(method_desc['input_type'])
            )
            request_message = request_class()
            
            # 填充请求数据
            self._fill_message_from_dict(request_message, request_data)
            
            # 构建方法路径
            method_path = f"/{service_name}/{method_name}"
            
            # 调用方法
            if method_desc['client_streaming'] or method_desc['server_streaming']:
                # 流式调用
                return await self._call_streaming_method(
                    method_path, request_message, method_desc, metadata, timeout
                )
            else:
                # 一元调用
                return await self._call_unary_method(
                    method_path, request_message, method_desc, metadata, timeout
                )
                
        except Exception as e:
            logger.error(
                "动态方法调用失败",
                service=service_name,
                method=method_name,
                error=str(e)
            )
            raise
    
    async def _call_unary_method(
        self,
        method_path: str,
        request_message: Any,
        method_desc: Dict[str, Any],
        metadata: Optional[List[tuple]],
        timeout: Optional[float]
    ) -> Dict[str, Any]:
        """调用一元方法"""
        # 序列化请求
        request_bytes = request_message.SerializeToString()
        
        # 创建响应消息类
        response_class = self.message_factory.GetPrototype(
            self.descriptor_pool.FindMessageTypeByName(method_desc['output_type'])
        )
        
        # 调用方法
        response_bytes = await self.channel.unary_unary(
            method_path,
            request_serializer=lambda x: x,
            response_deserializer=lambda x: x
        )(request_bytes, metadata=metadata, timeout=timeout)
        
        # 反序列化响应
        response_message = response_class()
        response_message.ParseFromString(response_bytes)
        
        return self._message_to_dict(response_message)
    
    async def _call_streaming_method(
        self,
        method_path: str,
        request_message: Any,
        method_desc: Dict[str, Any],
        metadata: Optional[List[tuple]],
        timeout: Optional[float]
    ) -> Dict[str, Any]:
        """调用流式方法"""
        # 暂时不支持流式调用的完整实现
        # 这里返回一个占位符
        logger.warning(
            "流式方法调用暂未完全实现",
            method_path=method_path
        )
        
        return {"error": "流式方法调用暂未支持"}
    
    def _parse_service_descriptor(
        self,
        service_desc: Any,
        file_desc: FileDescriptorProto
    ) -> Dict[str, Any]:
        """解析服务描述符"""
        methods = {}
        
        for method in service_desc.method:
            methods[method.name] = {
                "name": method.name,
                "input_type": method.input_type.lstrip('.'),
                "output_type": method.output_type.lstrip('.'),
                "client_streaming": method.client_streaming,
                "server_streaming": method.server_streaming,
                "options": self._parse_method_options(method)
            }
        
        return {
            "name": service_desc.name,
            "full_name": f"{file_desc.package}.{service_desc.name}",
            "methods": methods,
            "options": self._parse_service_options(service_desc)
        }
    
    def _parse_method_options(self, method_desc: Any) -> Dict[str, Any]:
        """解析方法选项"""
        options = {}
        
        if method_desc.HasField('options'):
            # 解析HTTP选项等
            pass
        
        return options
    
    def _parse_service_options(self, service_desc: Any) -> Dict[str, Any]:
        """解析服务选项"""
        options = {}
        
        if service_desc.HasField('options'):
            # 解析服务选项
            pass
        
        return options
    
    def _fill_message_from_dict(self, message: Any, data: Dict[str, Any]) -> None:
        """从字典填充消息"""
        for field_name, value in data.items():
            if hasattr(message, field_name):
                setattr(message, field_name, value)
    
    def _message_to_dict(self, message: Any) -> Dict[str, Any]:
        """将消息转换为字典"""
        result = {}
        
        for field, value in message.ListFields():
            if field.label == field.LABEL_REPEATED:
                result[field.name] = list(value)
            elif field.type == field.TYPE_MESSAGE:
                result[field.name] = self._message_to_dict(value)
            else:
                result[field.name] = value
        
        return result
    
    async def get_all_services_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有服务的详细信息"""
        services = await self.discover_services()
        services_info = {}
        
        for service_name in services:
            try:
                service_desc = await self.get_service_descriptor(service_name)
                if service_desc:
                    services_info[service_name] = service_desc
            except Exception as e:
                logger.warning(
                    "获取服务信息失败",
                    service=service_name,
                    error=str(e)
                )
        
        return services_info
    
    def get_cached_services(self) -> Dict[str, Dict[str, Any]]:
        """获取缓存的服务信息"""
        return self._services.copy()
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._services.clear()
        self._file_descriptors.clear()
        logger.info("gRPC反射缓存已清空") 