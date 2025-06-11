"""
索克生活事件总线模块
提供统一的事件驱动架构支持
"""

from .core.event_bus import SuokeEventBus
from .core.event_store import EventStore
from .core.event_types import (
    AgentCollaborationEvents,
    HealthDataEvents,
    UserInteractionEvents,
)
from .handlers.agent_handlers import AgentEventHandlers
from .handlers.health_handlers import HealthEventHandlers
from .utils.event_router import SmartDataAccessRouter

__all__ = [
    'SuokeEventBus',
    'EventStore', 
    'AgentCollaborationEvents',
    'HealthDataEvents',
    'UserInteractionEvents',
    'AgentEventHandlers',
    'HealthEventHandlers',
    'SmartDataAccessRouter'
]

__version__ = "1.0.0" 