"""
集成适配层

负责与外部系统和智能体的集成：
- 智能体适配器
- 智能体协调器
- 外部API集成
"""

from .agent_adapter import AgentAdapter
from .agent_coordination import AgentCoordination

__all__ = [
    "AgentAdapter",
    "AgentCoordination"
] 