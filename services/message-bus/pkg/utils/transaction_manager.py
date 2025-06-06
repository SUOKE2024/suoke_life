"""
transaction_manager - 索克生活项目模块
"""

                import redis
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Union
import asyncio
import json
import logging
import time
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
事务管理器
支持消息事务、两阶段提交、分布式事务和可靠性保证
"""


logger = logging.getLogger(__name__)

class TransactionState(Enum):
    """事务状态"""
    UNKNOWN = "unknown"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    TIMEOUT = "timeout"

class TransactionType(Enum):
    """事务类型"""
    LOCAL = "local"           # 本地事务
    DISTRIBUTED = "distributed"  # 分布式事务
    SAGA = "saga"            # Saga事务
    TCC = "tcc"              # Try-Confirm-Cancel

class IsolationLevel(Enum):
    """隔离级别"""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"

@dataclass
class TransactionMessage:
    """事务消息"""
    message_id: str
    topic: str
    payload: bytes
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'message_id': self.message_id,
            'topic': self.topic,
            'payload': self.payload.hex(),
            'headers': self.headers,
            'timestamp': self.timestamp,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionMessage':
        """从字典创建"""
        return cls(
            message_id=data['message_id'],
            topic=data['topic'],
            payload=bytes.fromhex(data['payload']),
            headers=data.get('headers', {}),
            timestamp=data.get('timestamp', time.time()),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3)
        )

@dataclass
class TransactionParticipant:
    """事务参与者"""
    participant_id: str
    endpoint: str
    role: str = "participant"  # coordinator, participant
    state: TransactionState = TransactionState.UNKNOWN
    last_heartbeat: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'participant_id': self.participant_id,
            'endpoint': self.endpoint,
            'role': self.role,
            'state': self.state.value,
            'last_heartbeat': self.last_heartbeat,
            'metadata': self.metadata
        }

@dataclass
class Transaction:
    """事务"""
    transaction_id: str
    transaction_type: TransactionType = TransactionType.LOCAL
    state: TransactionState = TransactionState.PREPARING
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    
    # 时间信息
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    timeout: float = 300.0  # 5分钟超时
    
    # 参与者和消息
    coordinator_id: Optional[str] = None
    participants: Dict[str, TransactionParticipant] = field(default_factory=dict)
    messages: List[TransactionMessage] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def add_participant(self, participant: TransactionParticipant):
        """添加参与者"""
        self.participants[participant.participant_id] = participant
    
    def add_message(self, message: TransactionMessage):
        """添加消息"""
        self.messages.append(message)
    
    def is_expired(self) -> bool:
        """检查是否超时"""
        return time.time() - self.created_at > self.timeout
    
    def get_duration(self) -> float:
        """获取事务持续时间"""
        if self.completed_at:
            return self.completed_at - (self.started_at or self.created_at)
        return time.time() - (self.started_at or self.created_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type.value,
            'state': self.state.value,
            'isolation_level': self.isolation_level.value,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'timeout': self.timeout,
            'coordinator_id': self.coordinator_id,
            'participants': {k: v.to_dict() for k, v in self.participants.items()},
            'messages': [msg.to_dict() for msg in self.messages],
            'metadata': self.metadata,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }

@dataclass
class TransactionConfig:
    """事务配置"""
    # 基础配置
    enable_transactions: bool = True
    default_timeout: float = 300.0  # 5分钟
    max_concurrent_transactions: int = 1000
    
    # 两阶段提交配置
    enable_2pc: bool = True
    prepare_timeout: float = 30.0
    commit_timeout: float = 60.0
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    
    # 持久化配置
    enable_persistence: bool = True
    persistence_backend: str = "redis"  # redis, database, file
    
    # 监控配置
    enable_metrics: bool = True
    log_level: str = "INFO"
    
    # 清理配置
    cleanup_interval: float = 300.0  # 5分钟
    max_completed_transactions: int = 10000

class TransactionStorage:
    """事务存储接口"""
    
    async def save_transaction(self, transaction: Transaction) -> bool:
        """保存事务"""
        raise NotImplementedError
    
    async def load_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """加载事务"""
        raise NotImplementedError
    
    async def update_transaction_state(self, transaction_id: str, state: TransactionState) -> bool:
        """更新事务状态"""
        raise NotImplementedError
    
    async def delete_transaction(self, transaction_id: str) -> bool:
        """删除事务"""
        raise NotImplementedError
    
    async def list_transactions(self, state: Optional[TransactionState] = None) -> List[Transaction]:
        """列出事务"""
        raise NotImplementedError

class RedisTransactionStorage(TransactionStorage):
    """Redis事务存储"""
    
    def __init__(self, redis_client, key_prefix: str = "tx"):
        self.redis_client = redis_client
        self.key_prefix = key_prefix
    
    def _get_key(self, transaction_id: str) -> str:
        """获取Redis键"""
        return f"{self.key_prefix}:transaction:{transaction_id}"
    
    async def save_transaction(self, transaction: Transaction) -> bool:
        """保存事务到Redis"""
        try:
            key = self._get_key(transaction.transaction_id)
            data = json.dumps(transaction.to_dict())
            
            # 设置过期时间为事务超时时间的2倍
            expire_time = int(transaction.timeout * 2)
            self.redis_client.setex(key, expire_time, data)
            
            # 添加到状态索引
            state_key = f"{self.key_prefix}:state:{transaction.state.value}"
            self.redis_client.sadd(state_key, transaction.transaction_id)
            
            return True
            
        except Exception as e:
            logger.error(f"保存事务失败: {e}")
            return False
    
    async def load_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """从Redis加载事务"""
        try:
            key = self._get_key(transaction_id)
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            tx_data = json.loads(data)
            
            # 重建事务对象
            transaction = Transaction(
                transaction_id=tx_data['transaction_id'],
                transaction_type=TransactionType(tx_data['transaction_type']),
                state=TransactionState(tx_data['state']),
                isolation_level=IsolationLevel(tx_data['isolation_level']),
                created_at=tx_data['created_at'],
                started_at=tx_data.get('started_at'),
                completed_at=tx_data.get('completed_at'),
                timeout=tx_data['timeout'],
                coordinator_id=tx_data.get('coordinator_id'),
                metadata=tx_data.get('metadata', {}),
                error_message=tx_data.get('error_message'),
                retry_count=tx_data.get('retry_count', 0),
                max_retries=tx_data.get('max_retries', 3)
            )
            
            # 重建参与者
            for p_data in tx_data.get('participants', {}).values():
                participant = TransactionParticipant(
                    participant_id=p_data['participant_id'],
                    endpoint=p_data['endpoint'],
                    role=p_data['role'],
                    state=TransactionState(p_data['state']),
                    last_heartbeat=p_data['last_heartbeat'],
                    metadata=p_data.get('metadata', {})
                )
                transaction.add_participant(participant)
            
            # 重建消息
            for m_data in tx_data.get('messages', []):
                message = TransactionMessage.from_dict(m_data)
                transaction.add_message(message)
            
            return transaction
            
        except Exception as e:
            logger.error(f"加载事务失败: {e}")
            return None
    
    async def update_transaction_state(self, transaction_id: str, state: TransactionState) -> bool:
        """更新事务状态"""
        try:
            transaction = await self.load_transaction(transaction_id)
            if not transaction:
                return False
            
            old_state = transaction.state
            transaction.state = state
            
            # 更新完成时间
            if state in [TransactionState.COMMITTED, TransactionState.ABORTED]:
                transaction.completed_at = time.time()
            
            # 保存更新后的事务
            success = await self.save_transaction(transaction)
            
            if success:
                # 更新状态索引
                old_state_key = f"{self.key_prefix}:state:{old_state.value}"
                new_state_key = f"{self.key_prefix}:state:{state.value}"
                
                self.redis_client.srem(old_state_key, transaction_id)
                self.redis_client.sadd(new_state_key, transaction_id)
            
            return success
            
        except Exception as e:
            logger.error(f"更新事务状态失败: {e}")
            return False
    
    async def delete_transaction(self, transaction_id: str) -> bool:
        """删除事务"""
        try:
            transaction = await self.load_transaction(transaction_id)
            if not transaction:
                return True
            
            key = self._get_key(transaction_id)
            self.redis_client.delete(key)
            
            # 从状态索引中移除
            state_key = f"{self.key_prefix}:state:{transaction.state.value}"
            self.redis_client.srem(state_key, transaction_id)
            
            return True
            
        except Exception as e:
            logger.error(f"删除事务失败: {e}")
            return False
    
    async def list_transactions(self, state: Optional[TransactionState] = None) -> List[Transaction]:
        """列出事务"""
        try:
            transactions = []
            
            if state:
                # 按状态查询
                state_key = f"{self.key_prefix}:state:{state.value}"
                transaction_ids = self.redis_client.smembers(state_key)
            else:
                # 查询所有事务
                pattern = f"{self.key_prefix}:transaction:*"
                keys = self.redis_client.keys(pattern)
                transaction_ids = [key.split(':')[-1] for key in keys]
            
            for transaction_id in transaction_ids:
                transaction = await self.load_transaction(transaction_id)
                if transaction:
                    transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"列出事务失败: {e}")
            return []

class TwoPhaseCommitCoordinator:
    """两阶段提交协调器"""
    
    def __init__(self, config: TransactionConfig, storage: TransactionStorage):
        self.config = config
        self.storage = storage
        self.coordinator_id = str(uuid.uuid4())
    
    async def begin_transaction(self, transaction_id: str, participants: List[str],
                              transaction_type: TransactionType = TransactionType.DISTRIBUTED) -> Transaction:
        """开始事务"""
        try:
            transaction = Transaction(
                transaction_id=transaction_id,
                transaction_type=transaction_type,
                state=TransactionState.PREPARING,
                coordinator_id=self.coordinator_id,
                timeout=self.config.default_timeout
            )
            
            # 添加参与者
            for participant_id in participants:
                participant = TransactionParticipant(
                    participant_id=participant_id,
                    endpoint=f"http://{participant_id}:8080",  # 假设的端点
                    role="participant"
                )
                transaction.add_participant(participant)
            
            # 保存事务
            await self.storage.save_transaction(transaction)
            
            logger.info(f"开始事务: {transaction_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"开始事务失败: {e}")
            raise
    
    async def prepare_phase(self, transaction: Transaction) -> bool:
        """准备阶段"""
        try:
            logger.info(f"执行准备阶段: {transaction.transaction_id}")
            
            # 向所有参与者发送准备请求
            prepare_results = []
            for participant in transaction.participants.values():
                try:
                    # 这里应该发送实际的网络请求
                    # 为了演示，我们模拟准备成功
                    result = await self._send_prepare_request(participant, transaction)
                    prepare_results.append(result)
                    
                    # 更新参与者状态
                    participant.state = TransactionState.PREPARED if result else TransactionState.ABORTED
                    
                except Exception as e:
                    logger.error(f"参与者准备失败 {participant.participant_id}: {e}")
                    participant.state = TransactionState.ABORTED
                    prepare_results.append(False)
            
            # 检查所有参与者是否都准备成功
            all_prepared = all(prepare_results)
            
            if all_prepared:
                transaction.state = TransactionState.PREPARED
                logger.info(f"所有参与者准备成功: {transaction.transaction_id}")
            else:
                transaction.state = TransactionState.ABORTING
                logger.warning(f"部分参与者准备失败: {transaction.transaction_id}")
            
            # 更新事务状态
            await self.storage.save_transaction(transaction)
            
            return all_prepared
            
        except Exception as e:
            logger.error(f"准备阶段失败: {e}")
            transaction.state = TransactionState.ABORTING
            await self.storage.save_transaction(transaction)
            return False
    
    async def commit_phase(self, transaction: Transaction) -> bool:
        """提交阶段"""
        try:
            logger.info(f"执行提交阶段: {transaction.transaction_id}")
            
            transaction.state = TransactionState.COMMITTING
            await self.storage.save_transaction(transaction)
            
            # 向所有参与者发送提交请求
            commit_results = []
            for participant in transaction.participants.values():
                try:
                    result = await self._send_commit_request(participant, transaction)
                    commit_results.append(result)
                    
                    # 更新参与者状态
                    participant.state = TransactionState.COMMITTED if result else TransactionState.ABORTED
                    
                except Exception as e:
                    logger.error(f"参与者提交失败 {participant.participant_id}: {e}")
                    participant.state = TransactionState.ABORTED
                    commit_results.append(False)
            
            # 检查提交结果
            all_committed = all(commit_results)
            
            if all_committed:
                transaction.state = TransactionState.COMMITTED
                logger.info(f"事务提交成功: {transaction.transaction_id}")
            else:
                transaction.state = TransactionState.ABORTED
                logger.error(f"事务提交失败: {transaction.transaction_id}")
            
            transaction.completed_at = time.time()
            await self.storage.save_transaction(transaction)
            
            return all_committed
            
        except Exception as e:
            logger.error(f"提交阶段失败: {e}")
            transaction.state = TransactionState.ABORTED
            transaction.completed_at = time.time()
            await self.storage.save_transaction(transaction)
            return False
    
    async def abort_phase(self, transaction: Transaction) -> bool:
        """中止阶段"""
        try:
            logger.info(f"执行中止阶段: {transaction.transaction_id}")
            
            transaction.state = TransactionState.ABORTING
            await self.storage.save_transaction(transaction)
            
            # 向所有参与者发送中止请求
            for participant in transaction.participants.values():
                try:
                    await self._send_abort_request(participant, transaction)
                    participant.state = TransactionState.ABORTED
                except Exception as e:
                    logger.error(f"参与者中止失败 {participant.participant_id}: {e}")
            
            transaction.state = TransactionState.ABORTED
            transaction.completed_at = time.time()
            await self.storage.save_transaction(transaction)
            
            logger.info(f"事务中止完成: {transaction.transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"中止阶段失败: {e}")
            return False
    
    async def _send_prepare_request(self, participant: TransactionParticipant, 
                                  transaction: Transaction) -> bool:
        """发送准备请求"""
        # 这里应该实现实际的网络请求
        # 为了演示，我们模拟成功
        await asyncio.sleep(0.1)  # 模拟网络延迟
        return True
    
    async def _send_commit_request(self, participant: TransactionParticipant, 
                                 transaction: Transaction) -> bool:
        """发送提交请求"""
        # 这里应该实现实际的网络请求
        await asyncio.sleep(0.1)
        return True
    
    async def _send_abort_request(self, participant: TransactionParticipant, 
                                transaction: Transaction) -> bool:
        """发送中止请求"""
        # 这里应该实现实际的网络请求
        await asyncio.sleep(0.1)
        return True

class TransactionManager:
    """
    事务管理器
    支持本地事务、分布式事务、两阶段提交和Saga模式
    """
    
    def __init__(self, config: TransactionConfig, storage: TransactionStorage):
        self.config = config
        self.storage = storage
        
        # 组件
        self.coordinator = TwoPhaseCommitCoordinator(config, storage)
        
        # 状态
        self.active_transactions: Dict[str, Transaction] = {}
        self.transaction_stats = {
            'total_transactions': 0,
            'committed_transactions': 0,
            'aborted_transactions': 0,
            'timeout_transactions': 0,
            'active_transactions': 0
        }
        
        # 后台任务
        self._background_tasks: List[asyncio.Task] = []
        self._running = False
    
    async def start(self):
        """启动事务管理器"""
        if self._running:
            logger.warning("事务管理器已在运行")
            return
        
        try:
            # 恢复未完成的事务
            await self._recover_transactions()
            
            # 启动后台任务
            await self._start_background_tasks()
            
            self._running = True
            logger.info("事务管理器启动成功")
            
        except Exception as e:
            logger.error(f"事务管理器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止事务管理器"""
        if not self._running:
            return
        
        try:
            self._running = False
            
            # 停止后台任务
            await self._stop_background_tasks()
            
            # 中止所有活跃事务
            for transaction in list(self.active_transactions.values()):
                if transaction.state not in [TransactionState.COMMITTED, TransactionState.ABORTED]:
                    await self.abort_transaction(transaction.transaction_id)
            
            logger.info("事务管理器已停止")
            
        except Exception as e:
            logger.error(f"事务管理器停止失败: {e}")
    
    async def begin_transaction(self, transaction_id: Optional[str] = None,
                              transaction_type: TransactionType = TransactionType.LOCAL,
                              participants: List[str] = None,
                              timeout: Optional[float] = None) -> str:
        """开始事务"""
        if transaction_id is None:
            transaction_id = str(uuid.uuid4())
        
        if transaction_id in self.active_transactions:
            raise ValueError(f"事务已存在: {transaction_id}")
        
        try:
            if transaction_type == TransactionType.DISTRIBUTED:
                if not participants:
                    raise ValueError("分布式事务需要指定参与者")
                
                transaction = await self.coordinator.begin_transaction(
                    transaction_id, participants, transaction_type
                )
            else:
                transaction = Transaction(
                    transaction_id=transaction_id,
                    transaction_type=transaction_type,
                    timeout=timeout or self.config.default_timeout
                )
                await self.storage.save_transaction(transaction)
            
            transaction.started_at = time.time()
            self.active_transactions[transaction_id] = transaction
            
            # 更新统计
            self.transaction_stats['total_transactions'] += 1
            self.transaction_stats['active_transactions'] += 1
            
            logger.info(f"开始事务: {transaction_id} ({transaction_type.value})")
            return transaction_id
            
        except Exception as e:
            logger.error(f"开始事务失败: {e}")
            raise
    
    async def add_message_to_transaction(self, transaction_id: str, 
                                       topic: str, payload: bytes,
                                       headers: Dict[str, str] = None) -> bool:
        """向事务添加消息"""
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            raise ValueError(f"事务不存在: {transaction_id}")
        
        if transaction.state != TransactionState.PREPARING:
            raise ValueError(f"事务状态不允许添加消息: {transaction.state}")
        
        try:
            message = TransactionMessage(
                message_id=str(uuid.uuid4()),
                topic=topic,
                payload=payload,
                headers=headers or {}
            )
            
            transaction.add_message(message)
            await self.storage.save_transaction(transaction)
            
            logger.debug(f"向事务添加消息: {transaction_id} -> {topic}")
            return True
            
        except Exception as e:
            logger.error(f"添加消息到事务失败: {e}")
            return False
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """提交事务"""
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            raise ValueError(f"事务不存在: {transaction_id}")
        
        try:
            if transaction.transaction_type == TransactionType.DISTRIBUTED:
                # 分布式事务使用两阶段提交
                prepare_success = await self.coordinator.prepare_phase(transaction)
                if prepare_success:
                    commit_success = await self.coordinator.commit_phase(transaction)
                else:
                    commit_success = await self.coordinator.abort_phase(transaction)
            else:
                # 本地事务直接提交
                commit_success = await self._commit_local_transaction(transaction)
            
            # 更新统计
            if commit_success:
                self.transaction_stats['committed_transactions'] += 1
            else:
                self.transaction_stats['aborted_transactions'] += 1
            
            self.transaction_stats['active_transactions'] -= 1
            
            # 从活跃事务中移除
            self.active_transactions.pop(transaction_id, None)
            
            logger.info(f"事务提交{'成功' if commit_success else '失败'}: {transaction_id}")
            return commit_success
            
        except Exception as e:
            logger.error(f"提交事务失败: {e}")
            await self.abort_transaction(transaction_id)
            return False
    
    async def abort_transaction(self, transaction_id: str) -> bool:
        """中止事务"""
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            # 尝试从存储加载
            transaction = await self.storage.load_transaction(transaction_id)
            if not transaction:
                logger.warning(f"事务不存在: {transaction_id}")
                return True
        
        try:
            if transaction.transaction_type == TransactionType.DISTRIBUTED:
                success = await self.coordinator.abort_phase(transaction)
            else:
                success = await self._abort_local_transaction(transaction)
            
            # 更新统计
            self.transaction_stats['aborted_transactions'] += 1
            if transaction_id in self.active_transactions:
                self.transaction_stats['active_transactions'] -= 1
            
            # 从活跃事务中移除
            self.active_transactions.pop(transaction_id, None)
            
            logger.info(f"事务中止: {transaction_id}")
            return success
            
        except Exception as e:
            logger.error(f"中止事务失败: {e}")
            return False
    
    async def _commit_local_transaction(self, transaction: Transaction) -> bool:
        """提交本地事务"""
        try:
            transaction.state = TransactionState.COMMITTING
            await self.storage.save_transaction(transaction)
            
            # 这里应该实现实际的消息发送逻辑
            # 为了演示，我们模拟成功
            for message in transaction.messages:
                logger.debug(f"发送消息: {message.topic} -> {message.message_id}")
            
            transaction.state = TransactionState.COMMITTED
            transaction.completed_at = time.time()
            await self.storage.save_transaction(transaction)
            
            return True
            
        except Exception as e:
            logger.error(f"本地事务提交失败: {e}")
            transaction.state = TransactionState.ABORTED
            transaction.completed_at = time.time()
            await self.storage.save_transaction(transaction)
            return False
    
    async def _abort_local_transaction(self, transaction: Transaction) -> bool:
        """中止本地事务"""
        try:
            transaction.state = TransactionState.ABORTED
            transaction.completed_at = time.time()
            await self.storage.save_transaction(transaction)
            
            logger.debug(f"本地事务中止: {transaction.transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"本地事务中止失败: {e}")
            return False
    
    async def _recover_transactions(self):
        """恢复未完成的事务"""
        try:
            # 加载所有未完成的事务
            incomplete_states = [
                TransactionState.PREPARING,
                TransactionState.PREPARED,
                TransactionState.COMMITTING,
                TransactionState.ABORTING
            ]
            
            for state in incomplete_states:
                transactions = await self.storage.list_transactions(state)
                
                for transaction in transactions:
                    # 检查是否超时
                    if transaction.is_expired():
                        logger.warning(f"事务超时，自动中止: {transaction.transaction_id}")
                        await self.abort_transaction(transaction.transaction_id)
                        self.transaction_stats['timeout_transactions'] += 1
                    else:
                        # 恢复到活跃事务
                        self.active_transactions[transaction.transaction_id] = transaction
                        self.transaction_stats['active_transactions'] += 1
            
            logger.info(f"恢复事务完成，活跃事务数: {len(self.active_transactions)}")
            
        except Exception as e:
            logger.error(f"恢复事务失败: {e}")
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        # 超时检查任务
        task = asyncio.create_task(self._timeout_check_loop())
        self._background_tasks.append(task)
        
        # 清理任务
        task = asyncio.create_task(self._cleanup_loop())
        self._background_tasks.append(task)
    
    async def _stop_background_tasks(self):
        """停止后台任务"""
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
    
    async def _timeout_check_loop(self):
        """超时检查循环"""
        while self._running:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次
                
                current_time = time.time()
                timeout_transactions = []
                
                for transaction in list(self.active_transactions.values()):
                    if transaction.is_expired():
                        timeout_transactions.append(transaction.transaction_id)
                
                # 中止超时事务
                for transaction_id in timeout_transactions:
                    logger.warning(f"事务超时，自动中止: {transaction_id}")
                    await self.abort_transaction(transaction_id)
                    self.transaction_stats['timeout_transactions'] += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"超时检查失败: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                
                # 清理已完成的事务
                completed_transactions = await self.storage.list_transactions(TransactionState.COMMITTED)
                completed_transactions.extend(await self.storage.list_transactions(TransactionState.ABORTED))
                
                if len(completed_transactions) > self.config.max_completed_transactions:
                    # 按时间排序，删除最旧的事务
                    completed_transactions.sort(key=lambda t: t.completed_at or 0)
                    to_delete = completed_transactions[:-self.config.max_completed_transactions]
                    
                    for transaction in to_delete:
                        await self.storage.delete_transaction(transaction.transaction_id)
                    
                    logger.info(f"清理已完成事务: {len(to_delete)}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务失败: {e}")
    
    def get_transaction_info(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """获取事务信息"""
        transaction = self.active_transactions.get(transaction_id)
        if transaction:
            return transaction.to_dict()
        return None
    
    def get_transaction_stats(self) -> Dict[str, Any]:
        """获取事务统计"""
        return {
            **self.transaction_stats,
            'active_transaction_ids': list(self.active_transactions.keys())
        }
    
    def list_active_transactions(self) -> List[Dict[str, Any]]:
        """列出活跃事务"""
        return [tx.to_dict() for tx in self.active_transactions.values()]

class TransactionManagerFactory:
    """事务管理器工厂"""
    
    @staticmethod
    def create_transaction_manager(config: Optional[TransactionConfig] = None,
                                 storage: Optional[TransactionStorage] = None) -> TransactionManager:
        """创建事务管理器"""
        if config is None:
            config = TransactionConfig()
        
        if storage is None:
            # 创建默认的Redis存储
            try:
                redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                storage = RedisTransactionStorage(redis_client)
            except ImportError:
                logger.error("Redis客户端未安装，无法创建默认存储")
                raise
        
        return TransactionManager(config, storage)
    
    @staticmethod
    def create_from_dict(config_dict: Dict[str, Any]) -> TransactionManager:
        """从字典创建事务管理器"""
        # 这里可以实现从字典配置创建的逻辑
        config = TransactionConfig()
        return TransactionManagerFactory.create_transaction_manager(config) 