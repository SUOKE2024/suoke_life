#!/usr/bin/env python3
"""
智能体数据模型
Agent Data Models
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """智能体状态枚举"""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class AgentCapability(BaseModel):
    """智能体能力模型"""

    name: str = Field(..., description="能力名称")
    description: str = Field(..., description="能力描述")
    enabled: bool = Field(True, description="是否启用")
    parameters: dict[str, Any] = Field(default_factory=dict, description="能力参数")


class AgentConfig(BaseModel):
    """智能体配置模型"""

    name: str = Field(..., description="智能体名称")
    url: str = Field(..., description="智能体服务地址")
    timeout: int = Field(30, description="超时时间(秒)")
    retry_count: int = Field(3, description="重试次数")
    health_check_interval: int = Field(60, description="健康检查间隔(秒)")
    capabilities: list[str] = Field(default_factory=list, description="能力列表")


class AgentInfo(BaseModel):
    """智能体信息模型"""

    id: str = Field(..., description="智能体ID")
    name: str = Field(..., description="智能体名称")
    description: str = Field("", description="智能体描述")
    version: str = Field("1.0.0", description="版本号")
    status: AgentStatus = Field(AgentStatus.OFFLINE, description="状态")
    url: str = Field(..., description="服务地址")
    capabilities: list[AgentCapability] = Field(
        default_factory=list, description="能力列表"
    )
    last_heartbeat: str | None = Field(None, description="最后心跳时间")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class AgentRequest(BaseModel):
    """智能体请求模型"""

    agent_id: str = Field(..., description="目标智能体ID")
    action: str = Field(..., description="动作名称")
    parameters: dict[str, Any] = Field(default_factory=dict, description="请求参数")
    user_id: str = Field(..., description="用户ID")
    request_id: str = Field(..., description="请求ID")
    timeout: int | None = Field(None, description="超时时间")


class AgentResponse(BaseModel):
    """智能体响应模型"""

    success: bool = Field(..., description="是否成功")
    data: dict[str, Any] = Field(default_factory=dict, description="响应数据")
    error: str | None = Field(None, description="错误信息")
    agent_id: str = Field(..., description="响应智能体ID")
    request_id: str = Field(..., description="请求ID")
    timestamp: str = Field(..., description="响应时间戳")
    execution_time: float = Field(0.0, description="执行时间(秒)")


class AgentMetrics(BaseModel):
    """智能体指标模型"""

    agent_id: str = Field(..., description="智能体ID")
    request_count: int = Field(0, description="请求总数")
    success_count: int = Field(0, description="成功请求数")
    error_count: int = Field(0, description="错误请求数")
    avg_response_time: float = Field(0.0, description="平均响应时间")
    last_request_time: str | None = Field(None, description="最后请求时间")
    uptime: float = Field(0.0, description="运行时间(秒)")


class AgentHealthCheck(BaseModel):
    """智能体健康检查模型"""

    agent_id: str = Field(..., description="智能体ID")
    status: AgentStatus = Field(..., description="健康状态")
    response_time: float = Field(0.0, description="响应时间(毫秒)")
    error_message: str | None = Field(None, description="错误信息")
    timestamp: str = Field(..., description="检查时间戳")
    details: dict[str, Any] = Field(default_factory=dict, description="详细信息")
