"""
saga_coordinator - 索克生活项目模块
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Optional, Callable, Any
import aioredis
import asyncio
import json
import logging
import time
import uuid

"""
基于Saga模式的分布式事务管理器
支持事务编排、补偿操作和状态管理
"""



logger = logging.getLogger(__name__)

Base = declarative_base()


class TransactionStatus(Enum):
    """事务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    """Saga步骤定义"""
    step_id: str
    service_name: str
    action: str
    compensation_action: str
    payload: Dict[str, Any]
    timeout: int = 30
    retry_count: int = 3
    depends_on: List[str] = field(default_factory=list)


@dataclass
class StepExecution:
    """步骤执行记录"""
    step_id: str
    status: StepStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0


class SagaTransaction(Base):
    """Saga事务数据模型"""
    __tablename__ = 'saga_transactions'
    
    transaction_id = Column(String(36), primary_key=True)
    status = Column(String(20), nullable=False)
    definition = Column(Text, nullable=False)  # JSON格式的步骤定义
    execution_log = Column(Text)  # JSON格式的执行日志
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    timeout_at = Column(DateTime)
    retry_count = Column(Integer, default=0)


class SagaCoordinator:
    """Saga协调器"""
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 db_url: str = "sqlite:///saga_transactions.db"):
        self.redis_url = redis_url
        self.db_url = db_url
        self.redis_client = None
        self.db_engine = None
        self.db_session = None
        self.service_clients = {}
        self.running_transactions = {}
        self._running = False
        
    async def start(self):
        """启动协调器"""
        # 初始化Redis连接
        self.redis_client = await aioredis.from_url(self.redis_url)
        
        # 初始化数据库连接
        self.db_engine = create_engine(self.db_url)
        Base.metadata.create_all(self.db_engine)
        Session = sessionmaker(bind=self.db_engine)
        self.db_session = Session()
        
        self._running = True
        
        # 启动后台任务
        asyncio.create_task(self._recovery_loop())
        asyncio.create_task(self._timeout_check_loop())
        
        logger.info("Saga coordinator started")
        
    async def stop(self):
        """停止协调器"""
        self._running = False
        
        if self.redis_client:
            await self.redis_client.close()
            
        if self.db_session:
            self.db_session.close()
            
        logger.info("Saga coordinator stopped")
    
    def register_service_client(self, service_name: str, client: Any):
        """注册服务客户端"""
        self.service_clients[service_name] = client
        logger.info(f"Registered service client for {service_name}")
    
    async def start_saga(self, 
                        saga_id: str,
                        steps: List[SagaStep],
                        timeout: int = 300) -> str:
        """启动Saga事务"""
        
        transaction_id = saga_id or str(uuid.uuid4())
        
        # 验证步骤定义
        self._validate_saga_steps(steps)
        
        # 创建事务记录
        transaction = SagaTransaction(
            transaction_id=transaction_id,
            status=TransactionStatus.PENDING.value,
            definition=json.dumps([
                {
                    "step_id": step.step_id,
                    "service_name": step.service_name,
                    "action": step.action,
                    "compensation_action": step.compensation_action,
                    "payload": step.payload,
                    "timeout": step.timeout,
                    "retry_count": step.retry_count,
                    "depends_on": step.depends_on
                }
                for step in steps
            ]),
            timeout_at=datetime.utcnow() + timedelta(seconds=timeout)
        )
        
        self.db_session.add(transaction)
        self.db_session.commit()
        
        # 初始化执行状态
        execution_state = {
            "transaction_id": transaction_id,
            "status": TransactionStatus.PENDING,
            "steps": {
                step.step_id: StepExecution(
                    step_id=step.step_id,
                    status=StepStatus.PENDING
                )
                for step in steps
            },
            "completed_steps": [],
            "failed_steps": []
        }
        
        self.running_transactions[transaction_id] = execution_state
        
        # 开始执行
        asyncio.create_task(self._execute_saga(transaction_id, steps))
        
        logger.info(f"Started saga transaction: {transaction_id}")
        return transaction_id
    
    def _validate_saga_steps(self, steps: List[SagaStep]):
        """验证Saga步骤定义"""
        step_ids = {step.step_id for step in steps}
        
        for step in steps:
            # 检查依赖关系
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(f"Step {step.step_id} depends on non-existent step {dep}")
            
            # 检查服务客户端
            if step.service_name not in self.service_clients:
                raise ValueError(f"No client registered for service {step.service_name}")
    
    async def _execute_saga(self, transaction_id: str, steps: List[SagaStep]):
        """执行Saga事务"""
        try:
            execution_state = self.running_transactions[transaction_id]
            execution_state["status"] = TransactionStatus.RUNNING
            
            # 更新数据库状态
            await self._update_transaction_status(transaction_id, TransactionStatus.RUNNING)
            
            # 构建依赖图
            dependency_graph = self._build_dependency_graph(steps)
            
            # 执行步骤
            await self._execute_steps(transaction_id, steps, dependency_graph)
            
            # 检查最终状态
            if all(step_exec.status == StepStatus.COMPLETED 
                   for step_exec in execution_state["steps"].values()):
                execution_state["status"] = TransactionStatus.COMPLETED
                await self._update_transaction_status(transaction_id, TransactionStatus.COMPLETED)
                logger.info(f"Saga transaction {transaction_id} completed successfully")
            else:
                # 有步骤失败，开始补偿
                await self._start_compensation(transaction_id, steps)
                
        except Exception as e:
            logger.error(f"Error executing saga {transaction_id}: {e}")
            await self._start_compensation(transaction_id, steps)
        finally:
            # 清理运行时状态
            if transaction_id in self.running_transactions:
                del self.running_transactions[transaction_id]
    
    def _build_dependency_graph(self, steps: List[SagaStep]) -> Dict[str, List[str]]:
        """构建依赖图"""
        graph = {}
        for step in steps:
            graph[step.step_id] = step.depends_on.copy()
        return graph
    
    async def _execute_steps(self, 
                           transaction_id: str, 
                           steps: List[SagaStep], 
                           dependency_graph: Dict[str, List[str]]):
        """执行步骤（支持并行执行）"""
        execution_state = self.running_transactions[transaction_id]
        step_map = {step.step_id: step for step in steps}
        
        while True:
            # 找到可以执行的步骤（依赖已完成且未执行）
            ready_steps = []
            for step_id, dependencies in dependency_graph.items():
                step_exec = execution_state["steps"][step_id]
                if (step_exec.status == StepStatus.PENDING and
                    all(execution_state["steps"][dep].status == StepStatus.COMPLETED 
                        for dep in dependencies)):
                    ready_steps.append(step_id)
            
            if not ready_steps:
                # 检查是否还有未完成的步骤
                pending_steps = [step_id for step_id, step_exec in execution_state["steps"].items()
                               if step_exec.status in [StepStatus.PENDING, StepStatus.RUNNING]]
                if not pending_steps:
                    break  # 所有步骤都已完成
                
                # 等待运行中的步骤完成
                await asyncio.sleep(0.1)
                continue
            
            # 并行执行准备好的步骤
            tasks = []
            for step_id in ready_steps:
                step = step_map[step_id]
                task = asyncio.create_task(
                    self._execute_single_step(transaction_id, step)
                )
                tasks.append(task)
            
            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # 检查是否有步骤失败
            if any(execution_state["steps"][step_id].status == StepStatus.FAILED 
                   for step_id in ready_steps):
                break  # 有步骤失败，停止执行
    
    async def _execute_single_step(self, transaction_id: str, step: SagaStep):
        """执行单个步骤"""
        execution_state = self.running_transactions[transaction_id]
        step_exec = execution_state["steps"][step.step_id]
        
        step_exec.status = StepStatus.RUNNING
        step_exec.start_time = datetime.utcnow()
        
        logger.info(f"Executing step {step.step_id} in transaction {transaction_id}")
        
        for attempt in range(step.retry_count + 1):
            try:
                # 获取服务客户端
                client = self.service_clients[step.service_name]
                
                # 执行步骤
                result = await asyncio.wait_for(
                    self._call_service_action(client, step.action, step.payload),
                    timeout=step.timeout
                )
                
                # 记录成功结果
                step_exec.status = StepStatus.COMPLETED
                step_exec.end_time = datetime.utcnow()
                step_exec.result = result
                execution_state["completed_steps"].append(step.step_id)
                
                logger.info(f"Step {step.step_id} completed successfully")
                break
                
            except Exception as e:
                step_exec.retry_count = attempt + 1
                step_exec.error = str(e)
                
                if attempt < step.retry_count:
                    logger.warning(f"Step {step.step_id} failed (attempt {attempt + 1}), retrying: {e}")
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    step_exec.status = StepStatus.FAILED
                    step_exec.end_time = datetime.utcnow()
                    execution_state["failed_steps"].append(step.step_id)
                    logger.error(f"Step {step.step_id} failed after {step.retry_count + 1} attempts: {e}")
                    break
        
        # 更新执行日志
        await self._update_execution_log(transaction_id, execution_state)
    
    async def _call_service_action(self, client: Any, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """调用服务操作"""
        # 这里需要根据实际的服务客户端接口来实现
        # 假设客户端有一个通用的call方法
        if hasattr(client, 'call'):
            return await client.call(action, payload)
        elif hasattr(client, action):
            method = getattr(client, action)
            return await method(**payload)
        else:
            raise ValueError(f"Service client does not support action: {action}")
    
    async def _start_compensation(self, transaction_id: str, steps: List[SagaStep]):
        """开始补偿操作"""
        execution_state = self.running_transactions[transaction_id]
        execution_state["status"] = TransactionStatus.COMPENSATING
        
        await self._update_transaction_status(transaction_id, TransactionStatus.COMPENSATING)
        
        logger.info(f"Starting compensation for transaction {transaction_id}")
        
        # 按完成顺序的逆序进行补偿
        completed_steps = execution_state["completed_steps"]
        step_map = {step.step_id: step for step in steps}
        
        for step_id in reversed(completed_steps):
            step = step_map[step_id]
            await self._compensate_step(transaction_id, step)
        
        execution_state["status"] = TransactionStatus.COMPENSATED
        await self._update_transaction_status(transaction_id, TransactionStatus.COMPENSATED)
        
        logger.info(f"Compensation completed for transaction {transaction_id}")
    
    async def _compensate_step(self, transaction_id: str, step: SagaStep):
        """补偿单个步骤"""
        execution_state = self.running_transactions[transaction_id]
        step_exec = execution_state["steps"][step.step_id]
        
        if step_exec.status != StepStatus.COMPLETED:
            return  # 只补偿已完成的步骤
        
        step_exec.status = StepStatus.COMPENSATING
        
        logger.info(f"Compensating step {step.step_id} in transaction {transaction_id}")
        
        try:
            client = self.service_clients[step.service_name]
            
            # 构建补偿载荷（包含原始结果）
            compensation_payload = {
                **step.payload,
                "original_result": step_exec.result
            }
            
            await asyncio.wait_for(
                self._call_service_action(client, step.compensation_action, compensation_payload),
                timeout=step.timeout
            )
            
            step_exec.status = StepStatus.COMPENSATED
            logger.info(f"Step {step.step_id} compensated successfully")
            
        except Exception as e:
            logger.error(f"Failed to compensate step {step.step_id}: {e}")
            # 补偿失败，但继续补偿其他步骤
        
        await self._update_execution_log(transaction_id, execution_state)
    
    async def _update_transaction_status(self, transaction_id: str, status: TransactionStatus):
        """更新事务状态"""
        transaction = self.db_session.query(SagaTransaction).filter_by(
            transaction_id=transaction_id
        ).first()
        
        if transaction:
            transaction.status = status.value
            transaction.updated_at = datetime.utcnow()
            self.db_session.commit()
    
    async def _update_execution_log(self, transaction_id: str, execution_state: Dict):
        """更新执行日志"""
        transaction = self.db_session.query(SagaTransaction).filter_by(
            transaction_id=transaction_id
        ).first()
        
        if transaction:
            # 序列化执行状态（处理不可序列化的对象）
            serializable_state = {
                "transaction_id": execution_state["transaction_id"],
                "status": execution_state["status"].value if isinstance(execution_state["status"], TransactionStatus) else execution_state["status"],
                "steps": {
                    step_id: {
                        "step_id": step_exec.step_id,
                        "status": step_exec.status.value if isinstance(step_exec.status, StepStatus) else step_exec.status,
                        "start_time": step_exec.start_time.isoformat() if step_exec.start_time else None,
                        "end_time": step_exec.end_time.isoformat() if step_exec.end_time else None,
                        "result": step_exec.result,
                        "error": step_exec.error,
                        "retry_count": step_exec.retry_count
                    }
                    for step_id, step_exec in execution_state["steps"].items()
                },
                "completed_steps": execution_state["completed_steps"],
                "failed_steps": execution_state["failed_steps"]
            }
            
            transaction.execution_log = json.dumps(serializable_state)
            transaction.updated_at = datetime.utcnow()
            self.db_session.commit()
    
    async def _recovery_loop(self):
        """恢复循环，处理中断的事务"""
        while self._running:
            try:
                # 查找需要恢复的事务
                transactions = self.db_session.query(SagaTransaction).filter(
                    SagaTransaction.status.in_([
                        TransactionStatus.RUNNING.value,
                        TransactionStatus.COMPENSATING.value
                    ])
                ).all()[:1000]  # 限制查询结果数量
                
                for transaction in transactions:
                    if transaction.transaction_id not in self.running_transactions:
                        logger.info(f"Recovering transaction {transaction.transaction_id}")
                        await self._recover_transaction(transaction)
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"Error in recovery loop: {e}")
                await asyncio.sleep(5)
    
    async def _recover_transaction(self, transaction: SagaTransaction):
        """恢复单个事务"""
        try:
            # 解析步骤定义
            steps_data = json.loads(transaction.definition)
            steps = [
                SagaStep(
                    step_id=step_data["step_id"],
                    service_name=step_data["service_name"],
                    action=step_data["action"],
                    compensation_action=step_data["compensation_action"],
                    payload=step_data["payload"],
                    timeout=step_data["timeout"],
                    retry_count=step_data["retry_count"],
                    depends_on=step_data["depends_on"]
                )
                for step_data in steps_data
            ]
            
            # 解析执行日志
            if transaction.execution_log:
                execution_data = json.loads(transaction.execution_log)
                # 重建执行状态
                execution_state = {
                    "transaction_id": transaction.transaction_id,
                    "status": TransactionStatus(execution_data["status"]),
                    "steps": {},
                    "completed_steps": execution_data["completed_steps"],
                    "failed_steps": execution_data["failed_steps"]
                }
                
                for step_id, step_data in execution_data["steps"].items():
                    step_exec = StepExecution(
                        step_id=step_data["step_id"],
                        status=StepStatus(step_data["status"])
                    )
                    if step_data["start_time"]:
                        step_exec.start_time = datetime.fromisoformat(step_data["start_time"])
                    if step_data["end_time"]:
                        step_exec.end_time = datetime.fromisoformat(step_data["end_time"])
                    step_exec.result = step_data["result"]
                    step_exec.error = step_data["error"]
                    step_exec.retry_count = step_data["retry_count"]
                    
                    execution_state["steps"][step_id] = step_exec
                
                self.running_transactions[transaction.transaction_id] = execution_state
                
                # 根据状态继续执行
                if execution_state["status"] == TransactionStatus.RUNNING:
                    asyncio.create_task(self._execute_saga(transaction.transaction_id, steps))
                elif execution_state["status"] == TransactionStatus.COMPENSATING:
                    asyncio.create_task(self._start_compensation(transaction.transaction_id, steps))
            
        except Exception as e:
            logger.error(f"Failed to recover transaction {transaction.transaction_id}: {e}")
    
    async def _timeout_check_loop(self):
        """超时检查循环"""
        while self._running:
            try:
                now = datetime.utcnow()
                
                # 查找超时的事务
                timeout_transactions = self.db_session.query(SagaTransaction).filter(
                    SagaTransaction.timeout_at < now,
                    SagaTransaction.status.in_([
                        TransactionStatus.PENDING.value,
                        TransactionStatus.RUNNING.value
                    ])
                ).all()[:1000]  # 限制查询结果数量
                
                for transaction in timeout_transactions:
                    logger.warning(f"Transaction {transaction.transaction_id} timed out")
                    
                    # 标记为失败并开始补偿
                    if transaction.transaction_id in self.running_transactions:
                        execution_state = self.running_transactions[transaction.transaction_id]
                        execution_state["status"] = TransactionStatus.FAILED
                        
                        # 解析步骤定义并开始补偿
                        steps_data = json.loads(transaction.definition)
                        steps = [
                            SagaStep(
                                step_id=step_data["step_id"],
                                service_name=step_data["service_name"],
                                action=step_data["action"],
                                compensation_action=step_data["compensation_action"],
                                payload=step_data["payload"],
                                timeout=step_data["timeout"],
                                retry_count=step_data["retry_count"],
                                depends_on=step_data["depends_on"]
                            )
                            for step_data in steps_data
                        ]
                        
                        await self._start_compensation(transaction.transaction_id, steps)
                    else:
                        # 直接标记为失败
                        await self._update_transaction_status(transaction.transaction_id, TransactionStatus.FAILED)
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"Error in timeout check loop: {e}")
                await asyncio.sleep(5)
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict]:
        """获取事务状态"""
        transaction = self.db_session.query(SagaTransaction).filter_by(
            transaction_id=transaction_id
        ).first()
        
        if not transaction:
            return None
        
        result = {
            "transaction_id": transaction.transaction_id,
            "status": transaction.status,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat(),
            "timeout_at": transaction.timeout_at.isoformat() if transaction.timeout_at else None,
            "retry_count": transaction.retry_count
        }
        
        if transaction.execution_log:
            result["execution_log"] = json.loads(transaction.execution_log)
        
        return result
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """取消事务"""
        if transaction_id in self.running_transactions:
            execution_state = self.running_transactions[transaction_id]
            
            # 如果事务正在运行，开始补偿
            if execution_state["status"] == TransactionStatus.RUNNING:
                transaction = self.db_session.query(SagaTransaction).filter_by(
                    transaction_id=transaction_id
                ).first()
                
                if transaction:
                    steps_data = json.loads(transaction.definition)
                    steps = [
                        SagaStep(
                            step_id=step_data["step_id"],
                            service_name=step_data["service_name"],
                            action=step_data["action"],
                            compensation_action=step_data["compensation_action"],
                            payload=step_data["payload"],
                            timeout=step_data["timeout"],
                            retry_count=step_data["retry_count"],
                            depends_on=step_data["depends_on"]
                        )
                        for step_data in steps_data
                    ]
                    
                    await self._start_compensation(transaction_id, steps)
                    return True
        
        return False


# 全局协调器实例
_saga_coordinator = None


def get_saga_coordinator(redis_url: str = "redis://localhost:6379",
                        db_url: str = "sqlite:///saga_transactions.db") -> SagaCoordinator:
    """获取Saga协调器单例"""
    global _saga_coordinator
    if _saga_coordinator is None:
        _saga_coordinator = SagaCoordinator(redis_url, db_url)
    return _saga_coordinator


# 使用示例
async def main():
    """示例用法"""
    
    # 模拟服务客户端
    class MockServiceClient:
        def __init__(self, service_name: str):
            self.service_name = service_name
        
        async def call(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
            print(f"[{self.service_name}] Executing {action} with payload: {payload}")
            await asyncio.sleep(1)  # 模拟网络延迟
            return {"success": True, "result": f"{action}_result"}
    
    # 创建协调器
    coordinator = SagaCoordinator()
    await coordinator.start()
    
    # 注册服务客户端
    coordinator.register_service_client("user-service", MockServiceClient("user-service"))
    coordinator.register_service_client("payment-service", MockServiceClient("payment-service"))
    coordinator.register_service_client("inventory-service", MockServiceClient("inventory-service"))
    
    try:
        # 定义Saga步骤
        steps = [
            SagaStep(
                step_id="create_order",
                service_name="user-service",
                action="create_order",
                compensation_action="cancel_order",
                payload={"user_id": "user123", "items": ["item1", "item2"]}
            ),
            SagaStep(
                step_id="reserve_inventory",
                service_name="inventory-service",
                action="reserve_items",
                compensation_action="release_items",
                payload={"items": ["item1", "item2"]},
                depends_on=["create_order"]
            ),
            SagaStep(
                step_id="process_payment",
                service_name="payment-service",
                action="charge_payment",
                compensation_action="refund_payment",
                payload={"amount": 100.0, "currency": "USD"},
                depends_on=["reserve_inventory"]
            )
        ]
        
        # 启动Saga事务
        transaction_id = await coordinator.start_saga("order_saga_001", steps)
        print(f"Started saga transaction: {transaction_id}")
        
        # 等待事务完成
        while True:
            status = await coordinator.get_transaction_status(transaction_id)
            print(f"Transaction status: {status['status']}")
            
            if status["status"] in ["completed", "compensated", "failed"]:
                break
                
            await asyncio.sleep(2)
        
        print("Final transaction status:", status)
        
    finally:
        await coordinator.stop()


if __name__ == "__main__":
    asyncio.run(main()) 