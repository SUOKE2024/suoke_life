"""
service - 索克生活项目模块
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
服务相关数据模型

定义服务实例、服务状态等相关的数据结构。
"""




class ServiceStatus(str, Enum):
    """服务状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class ServiceInfo(BaseModel):
    """服务信息模型"""
    id: str = Field(..., description = "服务实例ID")
    name: str = Field(..., description = "服务名称")
    host: str = Field(..., description = "服务主机地址")
    port: int = Field(..., description = "服务端口", ge = 1, le = 65535)
    status: ServiceStatus = Field(default = ServiceStatus.UNKNOWN, description = "服务状态")
    weight: int = Field(default = 1, description = "负载均衡权重", ge = 0)
    version: Optional[str] = Field(None, description = "服务版本")
    metadata: Dict[str, Any] = Field(default_factory = dict, description = "服务元数据")
    tags: List[str] = Field(default_factory = list, description = "服务标签")
    health_check_url: Optional[str] = Field(None, description = "健康检查URL")
    created_at: datetime = Field(default_factory = datetime.utcnow, description = "创建时间")
    updated_at: datetime = Field(default_factory = datetime.utcnow, description = "更新时间")
    last_seen: datetime = Field(default_factory = datetime.utcnow, description = "最后活跃时间")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @property
    def url(self)-> str:
        """获取服务URL"""
        return f"http: / /{self.host}:{self.port}"

    @property
    def is_healthy(self)-> bool:
        """检查服务是否健康"""
        return self.status == ServiceStatus.HEALTHY

    def update_status(self, status: ServiceStatus)-> None:
        """更新服务状态"""
        self.status = status
        self.updated_at = datetime.utcnow()
        self.last_seen = datetime.utcnow()


class ServiceRegistration(BaseModel):
    """服务注册请求模型"""
    name: str = Field(..., description = "服务名称")
    host: str = Field(..., description = "服务主机地址")
    port: int = Field(..., description = "服务端口", ge = 1, le = 65535)
    weight: int = Field(default = 1, description = "负载均衡权重", ge = 0)
    version: Optional[str] = Field(None, description = "服务版本")
    metadata: Dict[str, Any] = Field(default_factory = dict, description = "服务元数据")
    tags: List[str] = Field(default_factory = list, description = "服务标签")
    health_check_url: Optional[str] = Field(None, description = "健康检查URL")


class ServiceDeregistration(BaseModel):
    """服务注销请求模型"""
    service_id: str = Field(..., description = "服务实例ID")


class ServiceDiscoveryRequest(BaseModel):
    """服务发现请求模型"""
    service_name: str = Field(..., description = "服务名称")
    tags: Optional[List[str]] = Field(None, description = "服务标签过滤")
    healthy_only: bool = Field(default = True, description = "只返回健康的服务实例")


class ServiceDiscoveryResponse(BaseModel):
    """服务发现响应模型"""
    services: List[ServiceInfo] = Field(..., description = "服务实例列表")
    total: int = Field(..., description = "总数量")


class ServiceHealthCheck(BaseModel):
    """服务健康检查模型"""
    service_id: str = Field(..., description = "服务实例ID")
    status: ServiceStatus = Field(..., description = "健康状态")
    message: Optional[str] = Field(None, description = "健康检查消息")
    timestamp: datetime = Field(default_factory = datetime.utcnow, description = "检查时间")
    response_time: Optional[float] = Field(None, description = "响应时间（秒）")


class LoadBalancerStats(BaseModel):
    """负载均衡器统计信息"""
    service_name: str = Field(..., description = "服务名称")
    total_requests: int = Field(default = 0, description = "总请求数")
    successful_requests: int = Field(default = 0, description = "成功请求数")
    failed_requests: int = Field(default = 0, description = "失败请求数")
    average_response_time: float = Field(default = 0.0, description = "平均响应时间")
    active_connections: int = Field(default = 0, description = "活跃连接数")
    last_updated: datetime = Field(default_factory = datetime.utcnow, description = "最后更新时间")

    @property
    def success_rate(self)-> float:
        """计算成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def error_rate(self)-> float:
        """计算错误率"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests