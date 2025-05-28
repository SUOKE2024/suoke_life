"""
A2A 智能体网络微服务
A2A Agent Network Microservice

索克生活健康管理平台的智能体协作服务
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suoke-life.com"
__description__ = "A2A 智能体网络微服务 - 索克生活健康管理平台的智能体协作服务"

# 导出主要组件
from .model.agent import AgentInfo, AgentRequest, AgentResponse
from .model.workflow import WorkflowDefinition, WorkflowExecution
from .service.agent_manager import AgentManager
from .service.workflow_engine import WorkflowEngine

__all__ = [
    "AgentManager",
    "WorkflowEngine",
    "AgentInfo",
    "AgentRequest",
    "AgentResponse",
    "WorkflowDefinition",
    "WorkflowExecution",
]
