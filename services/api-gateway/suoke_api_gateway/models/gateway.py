"""
gateway - 索克生活项目模块
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

"""
网关请求响应模型

定义网关处理的请求和响应数据结构。
"""



class GatewayRequest(BaseModel):
    """网关请求模型"""
    
    method: str = Field(..., description="HTTP 方法")
    path: str = Field(..., description="请求路径")
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    query_params: Dict[str, Union[str, List[str]]] = Field(
        default_factory=dict, 
        description="查询参数"
    )
    body: Optional[bytes] = Field(default=None, description="请求体")
    client_ip: Optional[str] = Field(default=None, description="客户端IP")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="请求时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            bytes: lambda v: v.decode('utf-8', errors='ignore'),
        }

class GatewayResponse(BaseModel):
    """网关响应模型"""
    
    status_code: int = Field(..., description="HTTP 状态码")
    headers: Dict[str, str] = Field(default_factory=dict, description="响应头")
    body: Optional[bytes] = Field(default=None, description="响应体")
    content_type: Optional[str] = Field(default=None, description="内容类型")
    content_length: Optional[int] = Field(default=None, description="内容长度")
    processing_time: Optional[float] = Field(default=None, description="处理时间(秒)")
    service_name: Optional[str] = Field(default=None, description="处理服务名称")
    cache_hit: bool = Field(default=False, description="是否命中缓存")
    
    class Config:
        json_encoders = {
            bytes: lambda v: v.decode('utf-8', errors='ignore'),
        }

class RouteInfo(BaseModel):
    """路由信息模型"""
    
    path_pattern: str = Field(..., description="路径模式")
    methods: List[str] = Field(..., description="支持的HTTP方法")
    service_name: str = Field(..., description="目标服务名称")
    target_path: Optional[str] = Field(default=None, description="目标路径")
    auth_required: bool = Field(default=True, description="是否需要认证")
    rate_limit: Optional[str] = Field(default=None, description="限流规则")
    timeout: int = Field(default=30, description="超时时间(秒)")
    retry_count: int = Field(default=3, description="重试次数")
    cache_ttl: Optional[int] = Field(default=None, description="缓存TTL(秒)")

class LoadBalancerInfo(BaseModel):
    """负载均衡信息模型"""
    
    strategy: str = Field(default="round_robin", description="负载均衡策略")
    health_check_interval: int = Field(default=30, description="健康检查间隔(秒)")
    failure_threshold: int = Field(default=3, description="失败阈值")
    recovery_threshold: int = Field(default=2, description="恢复阈值")

class CircuitBreakerInfo(BaseModel):
    """熔断器信息模型"""
    
    failure_threshold: int = Field(default=5, description="失败阈值")
    recovery_timeout: int = Field(default=60, description="恢复超时(秒)")
    expected_exception: Optional[str] = Field(default=None, description="预期异常类型")

class MetricsInfo(BaseModel):
    """指标信息模型"""
    
    request_count: int = Field(default=0, description="请求总数")
    error_count: int = Field(default=0, description="错误总数")
    avg_response_time: float = Field(default=0.0, description="平均响应时间")
    p95_response_time: float = Field(default=0.0, description="95分位响应时间")
    p99_response_time: float = Field(default=0.0, description="99分位响应时间")
    cache_hit_rate: float = Field(default=0.0, description="缓存命中率")

class HealthCheckResult(BaseModel):
    """健康检查结果模型"""
    
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="健康状态")
    response_time: float = Field(..., description="响应时间(毫秒)")
    last_check: datetime = Field(..., description="最后检查时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        } 