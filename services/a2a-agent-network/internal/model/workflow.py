#!/usr/bin/env python3
"""
工作流数据模型
Workflow Data Models
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """工作流状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(str, Enum):
    """步骤状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    """工作流步骤模型"""

    id: str = Field(..., description="步骤ID")
    name: str = Field(..., description="步骤名称")
    agent: str = Field(..., description="执行智能体")
    action: str = Field(..., description="执行动作")
    description: str = Field("", description="步骤描述")
    timeout: int = Field(60, description="超时时间(秒)")
    retry_count: int = Field(1, description="重试次数")
    condition: str | None = Field(None, description="执行条件")
    parameters: dict[str, Any] = Field(default_factory=dict, description="步骤参数")
    dependencies: list[str] = Field(default_factory=list, description="依赖步骤")


class WorkflowDefinition(BaseModel):
    """工作流定义模型"""

    id: str = Field(..., description="工作流ID")
    name: str = Field(..., description="工作流名称")
    description: str = Field("", description="工作流描述")
    version: str = Field("1.0.0", description="版本号")
    timeout: int = Field(300, description="总超时时间(秒)")
    retry_count: int = Field(1, description="重试次数")
    steps: list[WorkflowStep] = Field(..., description="工作流步骤")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")
    tags: list[str] = Field(default_factory=list, description="标签")


class StepExecution(BaseModel):
    """步骤执行记录"""

    step_id: str = Field(..., description="步骤ID")
    status: StepStatus = Field(StepStatus.PENDING, description="执行状态")
    agent_id: str = Field(..., description="执行智能体")
    start_time: str | None = Field(None, description="开始时间")
    end_time: str | None = Field(None, description="结束时间")
    execution_time: float = Field(0.0, description="执行时间(秒)")
    result: dict[str, Any] = Field(default_factory=dict, description="执行结果")
    error: str | None = Field(None, description="错误信息")
    retry_count: int = Field(0, description="已重试次数")


class WorkflowExecution(BaseModel):
    """工作流执行记录"""

    execution_id: str = Field(..., description="执行ID")
    workflow_id: str = Field(..., description="工作流ID")
    workflow_name: str = Field(..., description="工作流名称")
    status: WorkflowStatus = Field(WorkflowStatus.PENDING, description="执行状态")
    user_id: str = Field(..., description="用户ID")
    start_time: str | None = Field(None, description="开始时间")
    end_time: str | None = Field(None, description="结束时间")
    execution_time: float = Field(0.0, description="总执行时间(秒)")
    steps: list[StepExecution] = Field(default_factory=list, description="步骤执行记录")
    context: dict[str, Any] = Field(default_factory=dict, description="执行上下文")
    result: dict[str, Any] = Field(default_factory=dict, description="最终结果")
    error: str | None = Field(None, description="错误信息")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class WorkflowRequest(BaseModel):
    """工作流执行请求"""

    workflow_id: str = Field(..., description="工作流ID")
    user_id: str = Field(..., description="用户ID")
    parameters: dict[str, Any] = Field(default_factory=dict, description="输入参数")
    context: dict[str, Any] = Field(default_factory=dict, description="执行上下文")
    priority: int = Field(0, description="优先级")
    timeout: int | None = Field(None, description="超时时间")


class WorkflowResponse(BaseModel):
    """工作流执行响应"""

    execution_id: str = Field(..., description="执行ID")
    status: WorkflowStatus = Field(..., description="执行状态")
    result: dict[str, Any] = Field(default_factory=dict, description="执行结果")
    error: str | None = Field(None, description="错误信息")
    execution_time: float = Field(0.0, description="执行时间(秒)")
    steps_completed: int = Field(0, description="已完成步骤数")
    total_steps: int = Field(0, description="总步骤数")


class WorkflowMetrics(BaseModel):
    """工作流指标模型"""

    workflow_id: str = Field(..., description="工作流ID")
    execution_count: int = Field(0, description="执行总数")
    success_count: int = Field(0, description="成功执行数")
    failure_count: int = Field(0, description="失败执行数")
    avg_execution_time: float = Field(0.0, description="平均执行时间")
    success_rate: float = Field(0.0, description="成功率")
    last_execution_time: str | None = Field(None, description="最后执行时间")


class WorkflowTemplate(BaseModel):
    """工作流模板"""

    template_id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field("", description="模板描述")
    category: str = Field("", description="模板分类")
    definition: WorkflowDefinition = Field(..., description="工作流定义")
    is_public: bool = Field(True, description="是否公开")
    created_by: str = Field(..., description="创建者")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
