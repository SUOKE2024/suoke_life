"""
__init__ - 索克生活项目模块
"""

from .event_sourcing import (
from .saga_manager import (
from .tcc_coordinator import (

#!/usr/bin/env python3
"""
分布式事务管理模块
提供Saga、TCC、事件溯源等分布式事务解决方案
"""

    AggregateRoot,
    Event,
    EventBus,
    EventProjection,
    EventSourcingRepository,
    EventStore,
    InMemoryEventStore,
    ReadModelProjection,
    get_event_bus,
    get_event_store,
)
    SagaContext,
    SagaManager,
    SagaOrchestrator,
    SagaStatus,
    SagaStep,
    get_orchestrator,
)
    TCCCoordinator,
    TCCOperation,
    TCCResource,
    TCCStatus,
    TCCTransaction,
    get_tcc_coordinator,
)

__all__ = [
    "AggregateRoot",
    # 事件溯源
    "Event",
    "EventBus",
    "EventProjection",
    "EventSourcingRepository",
    "EventStore",
    "InMemoryEventStore",
    "ReadModelProjection",
    "SagaContext",
    # Saga模式
    "SagaManager",
    "SagaOrchestrator",
    "SagaStatus",
    "SagaStep",
    # TCC模式
    "TCCCoordinator",
    "TCCOperation",
    "TCCResource",
    "TCCStatus",
    "TCCTransaction",
    "get_event_bus",
    "get_event_store",
    "get_orchestrator",
    "get_tcc_coordinator",
]
