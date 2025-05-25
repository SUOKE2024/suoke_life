#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式事务管理模块
提供Saga、TCC、事件溯源等分布式事务解决方案
"""

from .saga_manager import (
    SagaManager,
    SagaStep,
    SagaContext,
    SagaStatus,
    SagaOrchestrator,
    get_orchestrator
)

from .tcc_coordinator import (
    TCCCoordinator,
    TCCResource,
    TCCOperation,
    TCCTransaction,
    TCCStatus,
    get_tcc_coordinator
)

from .event_sourcing import (
    Event,
    EventStore,
    InMemoryEventStore,
    AggregateRoot,
    EventBus,
    EventSourcingRepository,
    EventProjection,
    ReadModelProjection,
    get_event_store,
    get_event_bus
)

__all__ = [
    # Saga模式
    'SagaManager',
    'SagaStep',
    'SagaContext',
    'SagaStatus',
    'SagaOrchestrator',
    'get_orchestrator',
    
    # TCC模式
    'TCCCoordinator',
    'TCCResource',
    'TCCOperation',
    'TCCTransaction',
    'TCCStatus',
    'get_tcc_coordinator',
    
    # 事件溯源
    'Event',
    'EventStore',
    'InMemoryEventStore',
    'AggregateRoot',
    'EventBus',
    'EventSourcingRepository',
    'EventProjection',
    'ReadModelProjection',
    'get_event_store',
    'get_event_bus'
] 