"""
gateway_service - 索克生活项目模块
"""

from ..core.config import Settings
from ..core.logging import get_logger
from ..services.service_registry import ServiceRegistry
from typing import AsyncIterator, Dict, List, Optional
import asyncio
import grpc

"""
gRPC 网关服务

实现网关的 gRPC 接口。
"""




logger = get_logger(__name__)

class GatewayService:
    """gRPC 网关服务实现"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.service_registry: Optional[ServiceRegistry] = None
    
    async def initialize(self, service_registry: ServiceRegistry) -> None:
        """初始化服务"""
        self.service_registry = service_registry
        logger.info("gRPC Gateway service initialized")
    
    async def ProxyRequest(self, request, context) -> None:
        """
        代理请求到后端服务
        
        这是一个示例方法，实际实现需要根据 protobuf 定义
        """
        try:
            # 获取请求信息
            service_name = request.service_name
            method = request.method
            path = request.path
            headers = dict(request.headers)
            body = request.body
            
            logger.info(
                "gRPC proxy request",
                service=service_name,
                method=method,
                path=path,
            )
            
            # 获取服务实例
            if not self.service_registry:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Service registry not initialized")
                return
            
            service_instance = self.service_registry.get_service_instance(service_name)
            if not service_instance:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Service '{service_name}' not found")
                return
            
            # 这里应该实现实际的代理逻辑
            # 由于没有具体的 protobuf 定义，这里只是示例
            
            # 返回响应（示例）
            # return ProxyResponse(
            #     status_code=200,
            #     headers=response_headers,
            #     body=response_body,
            # )
            
        except Exception as e:
            logger.error(
                "gRPC proxy request failed",
                service=service_name,
                error=str(e),
                exc_info=True,
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
    
    async def ListServices(self, request, context) -> None:
        """
        列出所有可用服务
        """
        try:
            if not self.service_registry:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Service registry not initialized")
                return
            
            services = self.service_registry.get_all_services()
            
            # 构建响应（示例）
            service_list = []
            for service_name, instances in services.items():
                healthy_instances = [inst for inst in instances if inst.healthy]
                service_info = {
                    "name": service_name,
                    "total_instances": len(instances),
                    "healthy_instances": len(healthy_instances),
                    "status": "healthy" if healthy_instances else "unhealthy",
                }
                service_list.append(service_info)
            
            # return ListServicesResponse(services=service_list)
            
        except Exception as e:
            logger.error("Failed to list services", error=str(e), exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
    
    async def GetServiceHealth(self, request, context) -> None:
        """
        获取服务健康状态
        """
        try:
            service_name = request.service_name
            
            if not self.service_registry:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Service registry not initialized")
                return
            
            health_info = self.service_registry.get_service_health(service_name)
            
            if health_info["status"] == "not_found":
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Service '{service_name}' not found")
                return
            
            # return ServiceHealthResponse(
            #     service_name=service_name,
            #     status=health_info["status"],
            #     healthy_instances=health_info["healthy_instances"],
            #     total_instances=health_info["total_instances"],
            #     health_ratio=health_info["health_ratio"],
            # )
            
        except Exception as e:
            logger.error(
                "Failed to get service health",
                service=service_name,
                error=str(e),
                exc_info=True,
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
    
    async def StreamEvents(self, request, context) -> AsyncIterator:
        """
        流式事件推送
        """
        try:
            # 这是一个示例流式方法
            event_types = request.event_types
            
            logger.info("Starting event stream", event_types=event_types)
            
            # 模拟事件流
            counter = 0
            while True:
                try:
                    # 检查客户端是否断开连接
                    if context.cancelled():
                        logger.info("Client cancelled event stream")
                        break
                    
                    # 生成示例事件
                    event = {
                        "id": counter,
                        "type": "service_health_change",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "data": {
                            "service": "example-service",
                            "status": "healthy",
                        }
                    }
                    
                    # yield StreamEvent(
                    #     id=event["id"],
                    #     type=event["type"],
                    #     timestamp=event["timestamp"],
                    #     data=json.dumps(event["data"]),
                    # )
                    
                    counter += 1
                    await asyncio.sleep(5)  # 每5秒发送一个事件
                    
                except Exception as e:
                    logger.error("Error in event stream", error=str(e))
                    break
            
            logger.info("Event stream ended")
            
        except Exception as e:
            logger.error("Failed to start event stream", error=str(e), exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")

# 注意：这个文件需要根据实际的 protobuf 定义来完善
# 以下是可能需要的 protobuf 定义示例：
#
# syntax = "proto3";
#
# package suoke.gateway.v1;
#
# service GatewayService {
#   rpc ProxyRequest(ProxyRequestMessage) returns (ProxyResponseMessage);
#   rpc ListServices(ListServicesRequest) returns (ListServicesResponse);
#   rpc GetServiceHealth(ServiceHealthRequest) returns (ServiceHealthResponse);
#   rpc StreamEvents(StreamEventsRequest) returns (stream StreamEvent);
# }
#
# message ProxyRequestMessage {
#   string service_name = 1;
#   string method = 2;
#   string path = 3;
#   map<string, string> headers = 4;
#   bytes body = 5;
# }
#
# message ProxyResponseMessage {
#   int32 status_code = 1;
#   map<string, string> headers = 2;
#   bytes body = 3;
# }
#
# message ListServicesRequest {}
#
# message ListServicesResponse {
#   repeated ServiceInfo services = 1;
# }
#
# message ServiceInfo {
#   string name = 1;
#   int32 total_instances = 2;
#   int32 healthy_instances = 3;
#   string status = 4;
# }
#
# message ServiceHealthRequest {
#   string service_name = 1;
# }
#
# message ServiceHealthResponse {
#   string service_name = 1;
#   string status = 2;
#   int32 healthy_instances = 3;
#   int32 total_instances = 4;
#   float health_ratio = 5;
# }
#
# message StreamEventsRequest {
#   repeated string event_types = 1;
# }
#
# message StreamEvent {
#   int64 id = 1;
#   string type = 2;
#   string timestamp = 3;
#   string data = 4;
# } 