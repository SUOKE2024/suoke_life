from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .agent_adapter import AgentAdapter
from .agent_coordination import AgentCoordination

"""
集成适配层

负责与外部系统和智能体的集成：
- 智能体适配器
- 智能体协调器
- 外部API集成
"""


__all__ = [
    "AgentAdapter",
    "AgentCoordination"
]
