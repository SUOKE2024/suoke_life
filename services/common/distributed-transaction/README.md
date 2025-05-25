# 分布式事务管理方案

## 概述

索克生活平台的微服务架构需要处理跨服务的数据一致性问题。本文档提供分布式事务的解决方案。

## 推荐方案

### 1. Saga 模式实现

```python
# saga_manager.py
from typing import List, Dict, Any, Callable
from enum import Enum
import asyncio
import logging

class SagaStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"

class SagaStep:
    def __init__(
        self,
        name: str,
        action: Callable,
        compensation: Callable,
        timeout: int = 30
    ):
        self.name = name
        self.action = action
        self.compensation = compensation
        self.timeout = timeout

class SagaManager:
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.steps: List[SagaStep] = []
        self.completed_steps: List[str] = []
        self.status = SagaStatus.PENDING
        self.logger = logging.getLogger(__name__)
    
    def add_step(self, step: SagaStep):
        """添加 Saga 步骤"""
        self.steps.append(step)
    
    async def execute(self) -> bool:
        """执行 Saga 事务"""
        self.status = SagaStatus.RUNNING
        
        try:
            for step in self.steps:
                self.logger.info(f"执行步骤: {step.name}")
                
                try:
                    await asyncio.wait_for(
                        step.action(),
                        timeout=step.timeout
                    )
                    self.completed_steps.append(step.name)
                except Exception as e:
                    self.logger.error(f"步骤 {step.name} 失败: {e}")
                    await self._compensate()
                    return False
            
            self.status = SagaStatus.COMPLETED
            return True
            
        except Exception as e:
            self.logger.error(f"Saga 执行失败: {e}")
            self.status = SagaStatus.FAILED
            return False
    
    async def _compensate(self):
        """执行补偿事务"""
        self.status = SagaStatus.COMPENSATING
        
        for step_name in reversed(self.completed_steps):
            step = next(s for s in self.steps if s.name == step_name)
            try:
                self.logger.info(f"补偿步骤: {step.name}")
                await step.compensation()
            except Exception as e:
                self.logger.error(f"补偿失败 {step.name}: {e}")
```

### 2. 事件驱动的最终一致性

```python
# event_sourcing.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List
import json

@dataclass
class Event:
    event_id: str
    aggregate_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    version: int

class EventStore:
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def append_event(self, event: Event):
        """追加事件到事件存储"""
        query = """
        INSERT INTO events (
            event_id, aggregate_id, event_type, 
            event_data, timestamp, version
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        await self.db.execute(
            query,
            event.event_id,
            event.aggregate_id,
            event.event_type,
            json.dumps(event.event_data),
            event.timestamp,
            event.version
        )
    
    async def get_events(
        self, 
        aggregate_id: str, 
        from_version: int = 0
    ) -> List[Event]:
        """获取聚合的事件历史"""
        query = """
        SELECT * FROM events 
        WHERE aggregate_id = %s AND version > %s
        ORDER BY version ASC
        """
        rows = await self.db.fetch(query, aggregate_id, from_version)
        return [self._row_to_event(row) for row in rows]
```

### 3. 两阶段提交优化（TCC）

```python
# tcc_coordinator.py
class TCCResource:
    """TCC 资源接口"""
    
    async def try_resource(self, request: Dict[str, Any]) -> str:
        """尝试预留资源，返回预留ID"""
        raise NotImplementedError
    
    async def confirm_resource(self, reservation_id: str) -> bool:
        """确认资源预留"""
        raise NotImplementedError
    
    async def cancel_resource(self, reservation_id: str) -> bool:
        """取消资源预留"""
        raise NotImplementedError

class TCCCoordinator:
    def __init__(self):
        self.resources: Dict[str, TCCResource] = {}
        self.reservations: Dict[str, List[str]] = {}
    
    def register_resource(self, name: str, resource: TCCResource):
        """注册 TCC 资源"""
        self.resources[name] = resource
    
    async def execute_transaction(
        self, 
        transaction_id: str,
        operations: List[Dict[str, Any]]
    ) -> bool:
        """执行 TCC 事务"""
        reservations = []
        
        # Try 阶段
        try:
            for op in operations:
                resource = self.resources[op['resource']]
                reservation_id = await resource.try_resource(op['request'])
                reservations.append({
                    'resource': op['resource'],
                    'reservation_id': reservation_id
                })
            
            # Confirm 阶段
            for res in reservations:
                resource = self.resources[res['resource']]
                await resource.confirm_resource(res['reservation_id'])
            
            return True
            
        except Exception as e:
            # Cancel 阶段
            for res in reservations:
                try:
                    resource = self.resources[res['resource']]
                    await resource.cancel_resource(res['reservation_id'])
                except Exception:
                    pass
            raise e
```

## 使用示例

### 1. 订单创建的 Saga 实现

```python
async def create_order_saga(order_data: Dict[str, Any]):
    saga = SagaManager(f"order-{order_data['order_id']}")
    
    # 步骤1：创建订单
    saga.add_step(SagaStep(
        name="create_order",
        action=lambda: order_service.create_order(order_data),
        compensation=lambda: order_service.cancel_order(order_data['order_id'])
    ))
    
    # 步骤2：扣减库存
    saga.add_step(SagaStep(
        name="reserve_inventory",
        action=lambda: inventory_service.reserve_items(order_data['items']),
        compensation=lambda: inventory_service.release_items(order_data['items'])
    ))
    
    # 步骤3：扣款
    saga.add_step(SagaStep(
        name="charge_payment",
        action=lambda: payment_service.charge(order_data['payment']),
        compensation=lambda: payment_service.refund(order_data['payment'])
    ))
    
    success = await saga.execute()
    return success
```

## 最佳实践

1. **选择合适的一致性模型**
   - 强一致性要求：使用 TCC
   - 最终一致性可接受：使用 Saga 或事件驱动

2. **幂等性设计**
   - 所有操作都应该是幂等的
   - 使用唯一标识符防止重复执行

3. **超时和重试**
   - 设置合理的超时时间
   - 实现指数退避的重试策略

4. **监控和追踪**
   - 记录所有事务步骤
   - 实现分布式追踪
   - 设置告警机制 