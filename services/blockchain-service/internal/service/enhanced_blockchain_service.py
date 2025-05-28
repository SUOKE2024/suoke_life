#!/usr/bin/env python3

"""
增强版区块链服务

该模块是区块链服务的增强版本，集成了所有优化组件，包括高级缓存、
智能批量处理、性能调优、增强监控等，提供最高性能和可靠性的区块链服务。
"""

import asyncio
from datetime import datetime, timedelta
import hashlib
import json
import logging
import time
from typing import Any

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreakerConfig,
    get_circuit_breaker,
)
from services.common.governance.rate_limiter import (
    RateLimitConfig,
    get_rate_limiter,
    rate_limit,
)
from services.common.observability.tracing import SpanKind, trace

from internal.blockchain.connection_pool import ConnectionPoolManager
from internal.model.config import AppConfig
from internal.model.entities import (
    DataType,
    HealthDataRecord,
)
from internal.service.advanced_cache_manager import AdvancedCacheManager, CacheLevel
from internal.service.blockchain_service import BlockchainService
from internal.service.cache_service import CacheKeyTypes, CacheService, cached
from internal.service.enhanced_monitoring import (
    AlertSeverity,
    EnhancedMonitoringService,
)

# 导入所有优化组件
from internal.service.integrated_optimization_service import (
    IntegratedOptimizationService,
    OptimizationLevel,
    ServiceStatus,
)
from internal.service.monitoring_service import MonitoringService
from internal.service.performance_tuner import (
    PerformanceTuner,
)
from internal.service.smart_batch_processor import (
    BatchStrategy,
    RetryStrategy,
    SmartBatchProcessor,
)
from internal.service.task_processor import (
    TaskPriority,
    TaskProcessor,
    TaskTypes,
    async_task,
)

logger = logging.getLogger(__name__)

class ChainType(Enum):
    """区块链类型"""
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    PRIVATE = "private"

class TransactionPriority(Enum):
    """交易优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class BatchTransaction:
    """批量交易"""
    transactions: list[dict[str, Any]]
    priority: TransactionPriority = TransactionPriority.NORMAL
    max_gas_price: int | None = None
    deadline: datetime | None = None

@dataclass
class IndexedData:
    """索引数据"""
    user_id: str
    data_type: str
    data_hash: str
    transaction_hash: str
    block_number: int
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

@dataclass
class ContractCache:
    """合约缓存"""
    address: str
    abi: list[dict[str, Any]]
    bytecode: str | None = None
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0

class EnhancedBlockchainService(BlockchainService):
    """增强版区块链服务，集成了所有优化组件"""

    def __init__(self, config: AppConfig):
        """
        初始化增强版区块链服务
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 先初始化基础服务
        super().__init__(config)

        # 初始化基础服务组件
        self.cache_service = CacheService(config)
        self.task_processor = TaskProcessor(config)
        self.monitoring_service = MonitoringService(config)
        self.connection_pool = ConnectionPoolManager(config)

        # 初始化集成优化服务
        self.optimization_service = IntegratedOptimizationService(
            config,
            self.cache_service,
            self.monitoring_service,
            self.task_processor,
            self.connection_pool
        )

        # 优化组件的直接引用（用于高级操作）
        self.advanced_cache: AdvancedCacheManager | None = None
        self.batch_processor: SmartBatchProcessor | None = None
        self.performance_tuner: PerformanceTuner | None = None
        self.enhanced_monitoring: EnhancedMonitoringService | None = None

        # 注册任务处理器
        self._register_task_handlers()

        # 注册健康检查器
        self._register_health_checkers()

        # 注册优化回调
        self._register_optimization_callbacks()

        # 性能统计
        self.performance_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "error_count": 0,
            "batch_operations": 0,
            "optimization_count": 0
        }

        # 服务状态
        self.is_running = False
        self.optimization_enabled = False
        self.current_optimization_level = OptimizationLevel.BASIC

        # Web3实例（多链支持）
        self.web3_instances: dict[ChainType, Web3] = {}
        self.accounts: dict[ChainType, Account] = {}
        self.current_chain = ChainType.PRIVATE

        # Redis客户端（用于缓存和索引）
        self.redis_pool = None

        # 初始化断路器配置
        self._init_circuit_breakers()

        # 初始化限流器配置
        self._init_rate_limiters()

        # 交易批处理配置
        self.batch_config = {
            "batch_size": 100,
            "batch_timeout": 5.0,  # 秒
            "max_gas_per_batch": 8000000,
            "parallel_batches": 3
        }

        # 合约缓存配置
        self.cache_config = {
            "contract_cache_ttl": 3600,      # 1小时
            "method_cache_ttl": 300,         # 5分钟
            "event_cache_ttl": 600,          # 10分钟
            "max_cache_size": 1000
        }

        # 链下索引配置
        self.index_config = {
            "index_batch_size": 1000,
            "index_interval": 10,  # 秒
            "retention_days": 365,
            "shard_count": 10
        }

        # 多链配置
        self.chain_configs = {
            ChainType.ETHEREUM: {
                "rpc_url": "https://mainnet.infura.io/v3/YOUR_KEY",
                "chain_id": 1,
                "block_time": 12,
                "confirmations": 12
            },
            ChainType.BSC: {
                "rpc_url": "https://bsc-dataseed.binance.org/",
                "chain_id": 56,
                "block_time": 3,
                "confirmations": 15
            },
            ChainType.POLYGON: {
                "rpc_url": "https://polygon-rpc.com/",
                "chain_id": 137,
                "block_time": 2,
                "confirmations": 128
            },
            ChainType.PRIVATE: {
                "rpc_url": "http://localhost:8545",
                "chain_id": 1337,
                "block_time": 1,
                "confirmations": 1
            }
        }

        # 交易队列
        self.transaction_queues: dict[TransactionPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in TransactionPriority
        }

        # 合约缓存
        self.contract_cache: dict[str, ContractCache] = {}

        self.logger.info("增强版区块链服务初始化完成")

    def _init_circuit_breakers(self):
        """初始化断路器配置"""
        self.circuit_breaker_configs = {
            "blockchain": CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=30.0
            ),
            "redis": CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=5.0
            ),
            "indexer": CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=45.0,
                timeout=10.0
            )
        }

    def _init_rate_limiters(self):
        """初始化限流器配置"""
        self.rate_limit_configs = {
            "transaction": RateLimitConfig(rate=100.0, burst=200),    # 每秒100笔交易
            "query": RateLimitConfig(rate=1000.0, burst=2000),       # 每秒1000次查询
            "batch": RateLimitConfig(rate=10.0, burst=20),           # 每秒10个批次
            "deploy": RateLimitConfig(rate=1.0, burst=2),            # 每秒1次部署
        }

    async def initialize(self):
        """初始化服务连接"""
        # 初始化Web3连接
        for chain_type, config in self.chain_configs.items():
            try:
                if chain_type == ChainType.ETHEREUM and "YOUR_KEY" in config["rpc_url"]:
                    continue  # 跳过未配置的链

                web3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
                if web3.is_connected():
                    self.web3_instances[chain_type] = web3
                    self.stats["active_chains"].append(chain_type.value)
                    logger.info(f"连接到{chain_type.value}成功")
            except Exception as e:
                logger.error(f"连接到{chain_type.value}失败: {e}")

        # 初始化Redis
        self.redis_pool = await aioredis.create_redis_pool(
            "redis://localhost:6379/3",
            minsize=5,
            maxsize=20
        )

        # 启动后台任务
        asyncio.create_task(self._batch_processor())
        asyncio.create_task(self._index_processor())
        asyncio.create_task(self._cache_cleaner())

        logger.info("区块链服务连接初始化完成")

    async def start_service(
        self,
        optimization_profile: str = "standard",
        enable_auto_optimization: bool = True
    ):
        """
        启动服务
        
        Args:
            optimization_profile: 优化配置文件名称
            enable_auto_optimization: 是否启用自动优化
        """
        if self.is_running:
            self.logger.warning("服务已在运行")
            return

        try:
            self.logger.info(f"启动增强版区块链服务，优化配置: {optimization_profile}")

            # 启动基础服务
            await self.task_processor.start()
            await self.monitoring_service.start_monitoring()
            await self.connection_pool.start()

            # 启动优化服务
            await self.optimization_service.start_optimization(optimization_profile)
            self.optimization_enabled = True

            # 获取优化组件的引用
            await self._get_optimization_components()

            # 设置自动优化
            if enable_auto_optimization:
                await self._setup_auto_optimization()

            self.is_running = True

            # 记录启动指标
            self.monitoring_service.increment_counter(
                "service_starts_total",
                labels={"service": "enhanced_blockchain", "profile": optimization_profile}
            )

            self.logger.info("增强版区块链服务启动完成")

        except Exception as e:
            self.logger.error(f"服务启动失败: {e!s}")
            await self.stop_service()
            raise

    async def stop_service(self):
        """停止服务"""
        if not self.is_running:
            return

        try:
            self.logger.info("停止增强版区块链服务")

            # 停止优化服务
            if self.optimization_enabled:
                await self.optimization_service.stop_optimization()
                self.optimization_enabled = False

            # 停止基础服务
            await self.task_processor.stop()
            await self.monitoring_service.stop_monitoring()
            await self.connection_pool.stop()

            # 清理组件引用
            self.advanced_cache = None
            self.batch_processor = None
            self.performance_tuner = None
            self.enhanced_monitoring = None

            self.is_running = False

            # 记录停止指标
            self.monitoring_service.increment_counter(
                "service_stops_total",
                labels={"service": "enhanced_blockchain"}
            )

            self.logger.info("增强版区块链服务已停止")

        except Exception as e:
            self.logger.error(f"服务停止失败: {e!s}")

    async def _get_optimization_components(self):
        """获取优化组件的引用"""
        optimization_status = await self.optimization_service.get_optimization_status()
        components = optimization_status.get("components", {})

        # 这里需要根据实际的集成优化服务实现来获取组件引用
        # 暂时使用占位符逻辑
        if "advanced_cache" in components:
            # self.advanced_cache = self.optimization_service.advanced_cache
            pass

        if "batch_processor" in components:
            # self.batch_processor = self.optimization_service.batch_processor
            pass

        if "performance_tuner" in components:
            # self.performance_tuner = self.optimization_service.performance_tuner
            pass

        if "enhanced_monitoring" in components:
            # self.enhanced_monitoring = self.optimization_service.enhanced_monitoring
            pass

    async def _setup_auto_optimization(self):
        """设置自动优化"""
        if self.performance_tuner:
            # 注册性能指标记录回调
            self.performance_tuner.register_parameter_callback(
                "batch_size",
                self._on_batch_size_changed
            )

            # 启动自动调优
            await self.performance_tuner.start_tuning()

        if self.enhanced_monitoring:
            # 注册告警处理回调
            self.enhanced_monitoring.add_alert_callback(self._handle_performance_alert)
            self.enhanced_monitoring.add_insight_callback(self._handle_performance_insight)

    async def _on_batch_size_changed(self, new_size: int):
        """批量大小变化回调"""
        if self.batch_processor:
            self.batch_processor.current_batch_size = new_size
            self.logger.info(f"自动调整批量大小: {new_size}")

    async def _handle_performance_alert(self, alert):
        """处理性能告警"""
        self.logger.warning(f"性能告警: {alert.message}")

        # 根据告警类型自动调整
        if alert.metric_name == "response_time" and alert.severity == AlertSeverity.HIGH:
            # 响应时间过长，启用更激进的缓存策略
            if self.advanced_cache:
                await self.advanced_cache.set_cache_strategy("aggressive")

        elif alert.metric_name == "error_rate" and alert.severity == AlertSeverity.CRITICAL:
            # 错误率过高，切换到保守模式
            await self.switch_optimization_profile("basic")

    async def _handle_performance_insight(self, insight):
        """处理性能洞察"""
        self.logger.info(f"性能洞察: {insight.title}")

        # 根据洞察类型自动优化
        if insight.insight_type == "capacity_planning":
            # 容量规划洞察，预先扩容
            if "memory" in insight.metrics_involved:
                await self._preemptive_cache_optimization()

        elif insight.insight_type == "performance_degradation":
            # 性能退化，执行全面优化
            await self.comprehensive_optimization()

    async def _preemptive_cache_optimization(self):
        """预防性缓存优化"""
        if self.advanced_cache:
            # 清理过期缓存
            await self.advanced_cache.cleanup_expired()

            # 优化缓存分布
            await self.advanced_cache.optimize_distribution()

            self.logger.info("执行预防性缓存优化")

    # 增强的核心方法
    async def store_health_data_enhanced(
        self,
        user_id: str,
        data_type: DataType,
        data_hash: bytes,
        metadata: dict[str, str] = None,
        encrypted_data: bytes = None,
        use_batch: bool = False,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> tuple[bool, str, HealthDataRecord | None]:
        """
        增强版存储健康数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            data_hash: 数据哈希
            metadata: 元数据
            encrypted_data: 加密数据
            use_batch: 是否使用批量处理
            priority: 任务优先级
            
        Returns:
            (是否成功, 消息, 健康数据记录)
        """
        start_time = time.time()

        try:
            # 记录性能指标
            if self.performance_tuner:
                self.performance_tuner.record_metric("request_start", time.time())

            # 检查缓存
            cache_key = f"health_data:{user_id}:{data_type.value}:{data_hash.hex()}"

            if self.advanced_cache:
                cached_result = await self.advanced_cache.get(cache_key)
                if cached_result:
                    self.performance_stats["cache_hits"] += 1
                    return cached_result

            self.performance_stats["cache_misses"] += 1

            # 选择处理方式
            if use_batch and self.batch_processor:
                # 使用批量处理
                result = await self._store_with_batch_processing(
                    user_id, data_type, data_hash, metadata, encrypted_data, priority
                )
            else:
                # 使用直接处理
                result = await self._store_with_direct_processing(
                    user_id, data_type, data_hash, metadata, encrypted_data
                )

            # 缓存结果
            if self.advanced_cache and result[0]:
                await self.advanced_cache.set(
                    cache_key,
                    result,
                    ttl=300,
                    cache_levels=[CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
                )

            # 记录性能指标
            response_time = time.time() - start_time
            self._update_performance_stats(response_time, success=result[0])

            if self.performance_tuner:
                self.performance_tuner.record_metric("response_time", response_time)
                self.performance_tuner.record_metric("throughput", 1.0 / response_time)

            return result

        except Exception as e:
            response_time = time.time() - start_time
            self._update_performance_stats(response_time, success=False)

            if self.performance_tuner:
                self.performance_tuner.record_metric("error_rate", 1.0)

            self.logger.error(f"增强版存储健康数据失败: {e!s}")
            raise

    async def _store_with_batch_processing(
        self,
        user_id: str,
        data_type: DataType,
        data_hash: bytes,
        metadata: dict[str, str],
        encrypted_data: bytes,
        priority: TaskPriority
    ):
        """使用批量处理存储数据"""
        if not self.batch_processor:
            raise RuntimeError("批量处理器未初始化")

        # 提交到批量处理器
        item_id = await self.batch_processor.submit_item(
            "store_health_data",
            {
                "user_id": user_id,
                "data_type": data_type.value,
                "data_hash": data_hash.hex(),
                "metadata": metadata or {},
                "encrypted_data": encrypted_data.hex() if encrypted_data else None
            },
            priority=priority.value
        )

        # 等待处理完成（这里可以优化为异步回调）
        max_wait_time = 30  # 最大等待30秒
        wait_interval = 0.5
        waited_time = 0

        while waited_time < max_wait_time:
            # 检查处理状态（这里需要实现状态查询机制）
            await asyncio.sleep(wait_interval)
            waited_time += wait_interval

            # 暂时返回成功结果（实际实现中需要真正的状态查询）
            break

        # 调用原始方法作为后备
        return await super().store_health_data(
            user_id, data_type, data_hash, metadata, encrypted_data
        )

    async def _store_with_direct_processing(
        self,
        user_id: str,
        data_type: DataType,
        data_hash: bytes,
        metadata: dict[str, str],
        encrypted_data: bytes
    ):
        """使用直接处理存储数据"""
        return await super().store_health_data(
            user_id, data_type, data_hash, metadata, encrypted_data
        )

    async def batch_store_health_data_smart(
        self,
        batch_data: list[dict[str, Any]],
        strategy: BatchStrategy = BatchStrategy.ADAPTIVE,
        retry_strategy: RetryStrategy = RetryStrategy.ADAPTIVE
    ) -> dict[str, Any]:
        """
        智能批量存储健康数据
        
        Args:
            batch_data: 批量数据列表
            strategy: 批量策略
            retry_strategy: 重试策略
            
        Returns:
            批量操作结果
        """
        if not self.batch_processor:
            # 如果没有批量处理器，使用基础批量处理
            return await self.batch_store_health_data(batch_data)

        start_time = time.time()

        try:
            # 设置批量策略
            self.batch_processor.set_strategy(strategy, retry_strategy)

            # 提交所有项目
            item_ids = []
            for item in batch_data:
                item_id = await self.batch_processor.submit_item(
                    "store_health_data",
                    item,
                    priority=item.get("priority", 1)
                )
                item_ids.append(item_id)

            # 处理待处理项目
            results = await self.batch_processor.process_pending_items()

            # 统计结果
            total_successful = sum(r.successful_items for r in results)
            total_failed = sum(r.failed_items for r in results)
            total_gas_used = sum(r.gas_used or 0 for r in results)

            processing_time = time.time() - start_time

            # 更新统计
            self.performance_stats["batch_operations"] += 1

            return {
                "success": True,
                "total_items": len(batch_data),
                "successful_items": total_successful,
                "failed_items": total_failed,
                "processing_time": processing_time,
                "gas_used": total_gas_used,
                "batch_results": [
                    {
                        "batch_id": r.batch_id,
                        "success_rate": r.success_rate,
                        "processing_time": r.processing_time
                    }
                    for r in results
                ]
            }

        except Exception as e:
            self.logger.error(f"智能批量存储失败: {e!s}")
            # 降级到基础批量处理
            return await self.batch_store_health_data(batch_data)

    async def comprehensive_optimization(self) -> dict[str, Any]:
        """
        全面性能优化
        
        Returns:
            优化结果
        """
        optimization_results = {}

        try:
            self.logger.info("开始全面性能优化")

            # 1. 缓存优化
            if self.advanced_cache:
                cache_result = await self.advanced_cache.comprehensive_optimization()
                optimization_results["cache_optimization"] = cache_result

            # 2. 批量处理优化
            if self.batch_processor:
                self.batch_processor.optimize_settings()
                optimization_results["batch_optimization"] = {
                    "status": "completed",
                    "metrics": self.batch_processor.get_metrics()
                }

            # 3. 连接池优化
            pool_optimization = await self.connection_pool.optimize_connections()
            optimization_results["connection_pool_optimization"] = pool_optimization

            # 4. 性能调优
            if self.performance_tuner:
                tuning_result = await self.performance_tuner.manual_optimization()
                optimization_results["performance_tuning"] = tuning_result

            # 5. 监控优化
            if self.enhanced_monitoring:
                monitoring_optimization = await self.enhanced_monitoring.optimize_monitoring()
                optimization_results["monitoring_optimization"] = monitoring_optimization

            # 更新统计
            self.performance_stats["optimization_count"] += 1

            self.logger.info("全面性能优化完成")

            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "optimizations": optimization_results
            }

        except Exception as e:
            self.logger.error(f"全面性能优化失败: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_comprehensive_status(self) -> dict[str, Any]:
        """
        获取全面状态信息
        
        Returns:
            全面状态信息
        """
        status = {
            "service": {
                "is_running": self.is_running,
                "optimization_enabled": self.optimization_enabled,
                "optimization_level": self.current_optimization_level.value,
                "uptime": self._get_uptime() if self.is_running else None
            },
            "performance": self.performance_stats.copy(),
            "optimization_service": None,
            "system_health": None,
            "components": {}
        }

        # 获取优化服务状态
        if self.optimization_enabled:
            status["optimization_service"] = await self.optimization_service.get_optimization_status()

        # 获取系统健康状态
        if self.enhanced_monitoring:
            system_health = self.enhanced_monitoring.get_system_health()
            status["system_health"] = {
                "overall_score": system_health.overall_score,
                "component_scores": system_health.component_scores,
                "active_alerts": system_health.active_alerts,
                "critical_alerts": system_health.critical_alerts
            }

        # 获取各组件状态
        if self.advanced_cache:
            status["components"]["advanced_cache"] = await self.advanced_cache.get_status()

        if self.batch_processor:
            status["components"]["batch_processor"] = self.batch_processor.get_metrics()

        if self.performance_tuner:
            status["components"]["performance_tuner"] = self.performance_tuner.get_tuning_status()

        # 获取基础服务状态
        status["components"]["cache_service"] = self.cache_service.get_stats()
        status["components"]["task_processor"] = self.task_processor.get_stats()
        status["components"]["monitoring_service"] = self.monitoring_service.get_health_status()
        status["components"]["connection_pool"] = self.connection_pool.get_pool_stats()

        return status

    def _get_uptime(self) -> str:
        """获取服务运行时间"""
        # 这里需要记录服务启动时间
        # 暂时返回占位符
        return "unknown"

    def _register_optimization_callbacks(self):
        """注册优化回调"""
        # 注册优化服务状态变化回调
        self.optimization_service.add_status_callback(self._on_optimization_status_changed)

        # 注册优化完成回调
        self.optimization_service.add_optimization_callback(self._on_optimization_completed)

    async def _on_optimization_status_changed(self, status: ServiceStatus):
        """优化服务状态变化回调"""
        self.logger.info(f"优化服务状态变化: {status.value}")

        if status == ServiceStatus.RUNNING:
            # 优化服务启动完成，更新组件引用
            await self._get_optimization_components()
        elif status == ServiceStatus.ERROR:
            # 优化服务出错，记录告警
            self.monitoring_service.increment_counter(
                "optimization_service_errors_total",
                labels={"error_type": "service_error"}
            )

    async def _on_optimization_completed(self, optimization_result: dict[str, Any]):
        """优化完成回调"""
        self.logger.info(f"优化完成: {optimization_result}")

        # 记录优化指标
        self.monitoring_service.increment_counter(
            "optimizations_completed_total",
            labels={"type": "automatic"}
        )

        # 更新性能统计
        self.performance_stats["optimization_count"] += 1

    # 继承的方法增强
    @cached(CacheKeyTypes.HEALTH_DATA_RECORD, ttl=300)
    async def store_health_data(
        self,
        user_id: str,
        data_type: DataType,
        data_hash: bytes,
        metadata: dict[str, str] = None,
        encrypted_data: bytes = None
    ) -> tuple[bool, str, HealthDataRecord | None]:
        """
        存储健康数据到区块链（带缓存和监控）
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            data_hash: 数据哈希
            metadata: 元数据
            encrypted_data: 加密数据
            
        Returns:
            (是否成功, 消息, 健康数据记录)
        """
        start_time = time.time()

        try:
            # 记录请求指标
            self.monitoring_service.increment_counter(
                "blockchain_requests_total",
                labels={"operation": "store_health_data", "data_type": data_type.value}
            )

            # 使用连接池执行操作
            result = await self.connection_pool.execute_with_retry(
                self._store_health_data_with_connection,
                max_retries=3,
                user_id=user_id,
                data_type=data_type,
                data_hash=data_hash,
                metadata=metadata,
                encrypted_data=encrypted_data
            )

            # 记录成功指标
            response_time = time.time() - start_time
            self.monitoring_service.record_histogram(
                "blockchain_operation_duration_seconds",
                response_time,
                labels={"operation": "store_health_data", "status": "success"}
            )

            # 更新性能统计
            self._update_performance_stats(response_time, success=True)

            # 记录性能指标到调优器
            if self.performance_tuner:
                self.performance_tuner.record_metric("response_time", response_time)
                self.performance_tuner.record_metric("throughput", 1.0 / response_time)

            return result

        except Exception as e:
            # 记录错误指标
            response_time = time.time() - start_time
            self.monitoring_service.increment_counter(
                "blockchain_errors_total",
                labels={"operation": "store_health_data", "error_type": type(e).__name__}
            )

            self.monitoring_service.record_histogram(
                "blockchain_operation_duration_seconds",
                response_time,
                labels={"operation": "store_health_data", "status": "error"}
            )

            # 更新性能统计
            self._update_performance_stats(response_time, success=False)

            # 记录错误指标到调优器
            if self.performance_tuner:
                self.performance_tuner.record_metric("error_rate", 1.0)

            self.logger.error(f"存储健康数据失败: {e!s}")
            raise

    async def _store_health_data_with_connection(
        self,
        web3,
        user_id: str,
        data_type: DataType,
        data_hash: bytes,
        metadata: dict[str, str] = None,
        encrypted_data: bytes = None
    ):
        """使用指定连接存储健康数据"""
        # 调用父类方法
        return await super().store_health_data(
            user_id, data_type, data_hash, metadata, encrypted_data
        )

    @cached(CacheKeyTypes.VERIFICATION_RESULT, ttl=600)
    async def verify_health_data(
        self,
        transaction_id: str,
        data_hash: bytes
    ) -> tuple[bool, str, datetime | None]:
        """
        验证健康数据（带缓存和监控）
        
        Args:
            transaction_id: 交易ID
            data_hash: 数据哈希
            
        Returns:
            (是否验证通过, 消息, 时间戳)
        """
        start_time = time.time()

        try:
            # 记录请求指标
            self.monitoring_service.increment_counter(
                "blockchain_requests_total",
                labels={"operation": "verify_health_data"}
            )

            # 使用连接池执行操作
            result = await self.connection_pool.execute_with_retry(
                self._verify_health_data_with_connection,
                max_retries=3,
                transaction_id=transaction_id,
                data_hash=data_hash
            )

            # 记录成功指标
            response_time = time.time() - start_time
            self.monitoring_service.record_histogram(
                "blockchain_operation_duration_seconds",
                response_time,
                labels={"operation": "verify_health_data", "status": "success"}
            )

            # 更新性能统计
            self._update_performance_stats(response_time, success=True)

            return result

        except Exception as e:
            # 记录错误指标
            response_time = time.time() - start_time
            self.monitoring_service.increment_counter(
                "blockchain_errors_total",
                labels={"operation": "verify_health_data", "error_type": type(e).__name__}
            )

            # 更新性能统计
            self._update_performance_stats(response_time, success=False)

            self.logger.error(f"验证健康数据失败: {e!s}")
            raise

    async def _verify_health_data_with_connection(
        self,
        web3,
        transaction_id: str,
        data_hash: bytes
    ):
        """使用指定连接验证健康数据"""
        return await super().verify_health_data(transaction_id, data_hash)

    @async_task(TaskTypes.BATCH_DATA_STORAGE, TaskPriority.HIGH)
    async def batch_store_health_data(
        self,
        batch_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        批量存储健康数据（异步任务）
        
        Args:
            batch_data: 批量数据列表
            
        Returns:
            批量操作结果
        """
        start_time = time.time()
        results = []

        try:
            # 记录批量操作指标
            self.monitoring_service.increment_counter(
                "blockchain_batch_operations_total",
                labels={"operation": "batch_store", "batch_size": str(len(batch_data))}
            )

            # 分批处理以避免超时
            batch_size = 10
            for i in range(0, len(batch_data), batch_size):
                batch_chunk = batch_data[i:i + batch_size]

                # 处理当前批次
                chunk_results = await self._process_batch_chunk(batch_chunk)
                results.extend(chunk_results)

                # 短暂延迟以避免过载
                await asyncio.sleep(0.1)

            # 记录成功指标
            response_time = time.time() - start_time
            self.monitoring_service.record_histogram(
                "blockchain_batch_operation_duration_seconds",
                response_time,
                labels={"operation": "batch_store", "status": "success"}
            )

            return {
                "success": True,
                "total_items": len(batch_data),
                "processed_items": len(results),
                "results": results,
                "processing_time": response_time
            }

        except Exception as e:
            # 记录错误指标
            response_time = time.time() - start_time
            self.monitoring_service.increment_counter(
                "blockchain_batch_errors_total",
                labels={"operation": "batch_store", "error_type": type(e).__name__}
            )

            self.logger.error(f"批量存储健康数据失败: {e!s}")
            raise

    async def _process_batch_chunk(self, batch_chunk: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """处理批量数据块"""
        results = []

        for item in batch_chunk:
            try:
                result = await self.store_health_data(
                    user_id=item["user_id"],
                    data_type=DataType(item["data_type"]),
                    data_hash=bytes.fromhex(item["data_hash"]),
                    metadata=item.get("metadata", {}),
                    encrypted_data=bytes.fromhex(item["encrypted_data"]) if item.get("encrypted_data") else None
                )

                results.append({
                    "user_id": item["user_id"],
                    "success": result[0],
                    "message": result[1],
                    "transaction_id": result[2].transaction_id if result[2] else None
                })

            except Exception as e:
                results.append({
                    "user_id": item["user_id"],
                    "success": False,
                    "message": str(e),
                    "transaction_id": None
                })

        return results

    @cached(CacheKeyTypes.USER_TRANSACTIONS, ttl=300)
    async def get_user_health_records(
        self,
        user_id: str,
        data_type: DataType = None,
        start_time: datetime = None,
        end_time: datetime = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[HealthDataRecord], int]:
        """
        获取用户健康记录（带缓存）
        
        Args:
            user_id: 用户ID
            data_type: 数据类型过滤
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            page_size: 页面大小
            
        Returns:
            (健康记录列表, 总数)
        """
        start_time_metric = time.time()

        try:
            # 记录请求指标
            self.monitoring_service.increment_counter(
                "blockchain_requests_total",
                labels={"operation": "get_user_health_records"}
            )

            # 调用父类方法
            result = await super().get_health_data_records(
                user_id, data_type, start_time, end_time, page, page_size
            )

            # 记录成功指标
            response_time = time.time() - start_time_metric
            self.monitoring_service.record_histogram(
                "blockchain_operation_duration_seconds",
                response_time,
                labels={"operation": "get_user_health_records", "status": "success"}
            )

            return result

        except Exception as e:
            # 记录错误指标
            response_time = time.time() - start_time_metric
            self.monitoring_service.increment_counter(
                "blockchain_errors_total",
                labels={"operation": "get_user_health_records", "error_type": type(e).__name__}
            )

            self.logger.error(f"获取用户健康记录失败: {e!s}")
            raise

    # 服务管理方法
    async def get_service_status(self) -> dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        status = {
            "is_running": self.is_running,
            "optimization_enabled": self.optimization_enabled,
            "optimization_level": self.current_optimization_level.value,
            "blockchain_service": await super().get_blockchain_status(include_node_info=True) if self.is_running else None,
            "optimization_service": await self.optimization_service.get_optimization_status() if self.optimization_enabled else None
        }

        return status

    async def get_performance_summary(self) -> dict[str, Any]:
        """
        获取性能摘要
        
        Returns:
            性能摘要信息
        """
        if not self.optimization_enabled:
            return {"error": "优化服务未启用"}

        return await self.optimization_service.get_performance_summary()

    async def switch_optimization_profile(self, profile_name: str):
        """
        切换优化配置文件
        
        Args:
            profile_name: 配置文件名称
        """
        if not self.optimization_enabled:
            raise RuntimeError("优化服务未启用")

        self.logger.info(f"切换优化配置文件: {profile_name}")
        await self.optimization_service.switch_profile(profile_name)

        # 更新当前优化级别
        profiles = self.optimization_service.get_optimization_profiles()
        if profile_name in profiles:
            self.current_optimization_level = OptimizationLevel(profiles[profile_name]["level"])

    async def manual_optimization(self) -> dict[str, Any]:
        """
        手动执行优化
        
        Returns:
            优化结果
        """
        if not self.optimization_enabled:
            raise RuntimeError("优化服务未启用")

        self.logger.info("执行手动优化")
        result = await self.optimization_service.manual_optimization()

        # 记录手动优化指标
        self.monitoring_service.increment_counter(
            "optimizations_completed_total",
            labels={"type": "manual"}
        )

        return result

    # 工具方法
    def _update_performance_stats(self, response_time: float, success: bool):
        """
        更新性能统计
        
        Args:
            response_time: 响应时间
            success: 是否成功
        """
        self.performance_stats["total_requests"] += 1

        if not success:
            self.performance_stats["error_count"] += 1

        # 更新平均响应时间
        current_avg = self.performance_stats["average_response_time"]
        total_requests = self.performance_stats["total_requests"]

        if total_requests == 1:
            self.performance_stats["average_response_time"] = response_time
        else:
            # 使用指数移动平均
            alpha = 0.1
            self.performance_stats["average_response_time"] = (
                alpha * response_time + (1 - alpha) * current_avg
            )

    def _register_task_handlers(self):
        """注册任务处理器"""

        async def handle_batch_storage(payload: dict[str, Any]):
            """处理批量存储任务"""
            batch_data = payload.get("batch_data", [])
            return await self._process_batch_chunk(batch_data)

        async def handle_cache_refresh(payload: dict[str, Any]):
            """处理缓存刷新任务"""
            pattern = payload.get("pattern", "*")
            deleted_count = self.cache_service.delete_pattern(pattern)
            return {"deleted_count": deleted_count}

        async def handle_health_check(payload: dict[str, Any]):
            """处理健康检查任务"""
            return self.monitoring_service.get_health_status()

        async def handle_optimization(payload: dict[str, Any]):
            """处理优化任务"""
            optimization_type = payload.get("type", "comprehensive")

            if optimization_type == "comprehensive":
                return await self.comprehensive_optimization()
            elif optimization_type == "cache":
                return await self._preemptive_cache_optimization()
            else:
                return {"error": f"未知优化类型: {optimization_type}"}

        # 注册处理器
        self.task_processor.register_handler(TaskTypes.BATCH_DATA_STORAGE, handle_batch_storage)
        self.task_processor.register_handler(TaskTypes.CACHE_REFRESH, handle_cache_refresh)
        self.task_processor.register_handler(TaskTypes.HEALTH_CHECK, handle_health_check)
        self.task_processor.register_handler("optimization", handle_optimization)

    def _register_health_checkers(self):
        """注册健康检查器"""

        async def check_blockchain_connection():
            """检查区块链连接"""
            try:
                web3, node = await self.connection_pool.get_connection()

                # 测试基本操作
                block_number = web3.eth.block_number

                self.connection_pool.release_connection(node)

                return {
                    "status": "healthy",
                    "message": f"Blockchain connected, latest block: {block_number}",
                    "details": {"block_number": block_number}
                }
            except Exception as e:
                return {
                    "status": "critical",
                    "message": f"Blockchain connection failed: {e!s}"
                }

        def check_cache_service():
            """检查缓存服务"""
            return self.cache_service.health_check()

        def check_task_processor():
            """检查任务处理器"""
            stats = self.task_processor.get_stats()

            if not stats["is_running"]:
                return {
                    "status": "critical",
                    "message": "Task processor not running"
                }

            # 检查失败率
            total_tasks = stats["total_tasks"]
            failed_tasks = stats["failed_tasks"]

            if total_tasks > 0:
                failure_rate = failed_tasks / total_tasks
                if failure_rate > 0.1:  # 失败率超过10%
                    return {
                        "status": "warning",
                        "message": f"High task failure rate: {failure_rate:.2%}",
                        "details": stats
                    }

            return {
                "status": "healthy",
                "message": "Task processor running normally",
                "details": stats
            }

        def check_optimization_service():
            """检查优化服务"""
            if not self.optimization_enabled:
                return {
                    "status": "warning",
                    "message": "Optimization service not enabled"
                }

            # 这里可以添加更详细的优化服务健康检查
            return {
                "status": "healthy",
                "message": "Optimization service running normally"
            }

        # 注册健康检查器
        self.monitoring_service.register_health_checker("blockchain_connection", check_blockchain_connection)
        self.monitoring_service.register_health_checker("cache_service", check_cache_service)
        self.monitoring_service.register_health_checker("task_processor", check_task_processor)
        self.monitoring_service.register_health_checker("optimization_service", check_optimization_service)

    # 缓存管理方法
    async def clear_cache(self, pattern: str = None) -> dict[str, Any]:
        """
        清理缓存
        
        Args:
            pattern: 缓存键模式，如果为None则清理所有缓存
            
        Returns:
            清理结果
        """
        try:
            if pattern:
                deleted_count = self.cache_service.delete_pattern(pattern)
            else:
                success = self.cache_service.clear_all()
                deleted_count = "all" if success else 0

            # 如果有高级缓存，也清理高级缓存
            if self.advanced_cache:
                if pattern:
                    await self.advanced_cache.clear_pattern(pattern)
                else:
                    await self.advanced_cache.clear_all()

            self.logger.info(f"缓存清理完成: 删除了 {deleted_count} 个键")

            return {
                "success": True,
                "deleted_count": deleted_count,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"缓存清理失败: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def optimize_performance(self) -> dict[str, Any]:
        """
        性能优化操作
        
        Returns:
            优化结果
        """
        optimization_results = []

        try:
            # 1. 清理过期缓存
            cache_result = await self.clear_cache("*:expired:*")
            optimization_results.append({
                "operation": "cache_cleanup",
                "result": cache_result
            })

            # 2. 优化连接池
            pool_stats = self.connection_pool.get_pool_stats()
            if pool_stats["offline_nodes"] > 0:
                # 尝试重新连接离线节点
                reconnect_result = await self.connection_pool.reconnect_offline_nodes()
                optimization_results.append({
                    "operation": "connection_pool_optimization",
                    "result": reconnect_result
                })

            # 3. 任务队列优化
            task_stats = self.task_processor.get_stats()
            if sum(task_stats["queue_lengths"].values()) > 100:
                # 队列积压过多，可以考虑增加工作线程或优化任务处理
                optimization_results.append({
                    "operation": "task_queue_optimization",
                    "result": {"warning": "High queue backlog detected"}
                })

            # 4. 如果启用了优化服务，执行全面优化
            if self.optimization_enabled:
                comprehensive_result = await self.comprehensive_optimization()
                optimization_results.append({
                    "operation": "comprehensive_optimization",
                    "result": comprehensive_result
                })

            return {
                "success": True,
                "optimizations": optimization_results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"性能优化失败: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _batch_processor(self):
        """批处理器"""
        while True:
            try:
                # 收集批次
                for priority in [TransactionPriority.NORMAL, TransactionPriority.LOW]:
                    batch = []
                    deadline = datetime.now() + timedelta(seconds=self.batch_config["batch_timeout"])

                    while len(batch) < self.batch_config["batch_size"]:
                        try:
                            remaining_time = (deadline - datetime.now()).total_seconds()
                            if remaining_time <= 0:
                                break

                            transaction = await asyncio.wait_for(
                                self.transaction_queues[priority].get(),
                                timeout=remaining_time
                            )
                            batch.append(transaction)
                        except TimeoutError:
                            break

                    if batch:
                        # 处理批次
                        await self._process_batch(batch)

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"批处理器错误: {e}")
                await asyncio.sleep(5)

    async def _process_batch(self, batch: list[dict[str, Any]]):
        """处理交易批次"""
        # 按链分组
        chain_groups = defaultdict(list)
        for tx in batch:
            chain_groups[tx["chain"]].append(tx)

        # 并行处理不同链的交易
        tasks = []
        for chain, transactions in chain_groups.items():
            task = self._process_chain_batch(chain, transactions)
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_chain_batch(self, chain: ChainType, transactions: list[dict[str, Any]]):
        """处理单链交易批次"""
        web3 = self._get_web3(chain)
        account = self._get_account(chain)

        # 使用多调用合约批量执行
        # 这里简化实现，实际应使用Multicall合约
        results = []
        for tx in transactions:
            try:
                result = await self._send_single_transaction(tx, web3)
                results.append(result)
            except Exception as e:
                logger.error(f"批次交易失败: {e}")
                results.append({"status": "failed", "error": str(e)})

        return results

    @trace(service_name="blockchain-service", kind=SpanKind.SERVER)
    async def get_contract(self, address: str, abi: list[dict[str, Any]],
                          chain: ChainType = None) -> Any:
        """
        获取合约实例（带缓存）
        
        Args:
            address: 合约地址
            abi: 合约ABI
            chain: 目标链
            
        Returns:
            合约实例
        """
        chain = chain or self.current_chain
        cache_key = f"{chain.value}:{address}"

        # 检查缓存
        if cache_key in self.contract_cache:
            cache = self.contract_cache[cache_key]
            cache.access_count += 1
            cache.last_accessed = datetime.now()
            self.stats["cache_hits"] += 1

            web3 = self._get_web3(chain)
            return web3.eth.contract(address=address, abi=cache.abi)

        self.stats["cache_misses"] += 1

        # 创建合约实例
        web3 = self._get_web3(chain)
        contract = web3.eth.contract(
            address=Web3.toChecksumAddress(address),
            abi=abi
        )

        # 缓存合约信息
        self.contract_cache[cache_key] = ContractCache(
            address=address,
            abi=abi
        )

        return contract

    @trace(service_name="blockchain-service", kind=SpanKind.SERVER)
    async def call_contract_method(
        self,
        contract_address: str,
        method_name: str,
        args: list[Any],
        abi: list[dict[str, Any]],
        chain: ChainType = None,
        use_cache: bool = True
    ) -> Any:
        """
        调用合约方法（带缓存）
        
        Args:
            contract_address: 合约地址
            method_name: 方法名
            args: 方法参数
            abi: 合约ABI
            chain: 目标链
            use_cache: 是否使用缓存
            
        Returns:
            方法返回值
        """
        chain = chain or self.current_chain

        # 生成缓存键
        cache_key = self._generate_method_cache_key(
            chain, contract_address, method_name, args
        )

        # 检查缓存
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached is not None:
                self.stats["cache_hits"] += 1
                return cached

        # 获取合约实例
        contract = await self.get_contract(contract_address, abi, chain)

        # 调用方法
        breaker = await get_circuit_breaker(
            f"{self.service_name}_blockchain",
            self.circuit_breaker_configs["blockchain"]
        )

        async with breaker.protect():
            method = getattr(contract.functions, method_name)
            result = await asyncio.to_thread(method(*args).call)

            # 缓存结果
            if use_cache:
                await self._cache_result(cache_key, result, self.cache_config["method_cache_ttl"])

            return result

    @trace(service_name="blockchain-service", kind=SpanKind.SERVER)
    async def index_transaction_data(
        self,
        tx_hash: str,
        user_id: str,
        data_type: str,
        data_hash: str,
        metadata: dict[str, Any] = None,
        tags: list[str] = None
    ) -> bool:
        """
        索引交易数据
        
        Args:
            tx_hash: 交易哈希
            user_id: 用户ID
            data_type: 数据类型
            data_hash: 数据哈希
            metadata: 元数据
            tags: 标签
            
        Returns:
            bool: 是否成功
        """
        try:
            # 获取交易详情
            web3 = self._get_web3(self.current_chain)
            tx_receipt = web3.eth.get_transaction_receipt(tx_hash)

            # 创建索引数据
            indexed_data = IndexedData(
                user_id=user_id,
                data_type=data_type,
                data_hash=data_hash,
                transaction_hash=tx_hash,
                block_number=tx_receipt["blockNumber"],
                timestamp=datetime.now(),
                metadata=metadata or {},
                tags=tags or []
            )

            # 存储到Redis（分片存储）
            shard_id = self._get_shard_id(user_id)
            index_key = f"blockchain:index:{shard_id}:{user_id}:{data_type}:{tx_hash}"

            await self.redis_pool.setex(
                index_key,
                self.index_config["retention_days"] * 86400,
                json.dumps({
                    "user_id": indexed_data.user_id,
                    "data_type": indexed_data.data_type,
                    "data_hash": indexed_data.data_hash,
                    "transaction_hash": indexed_data.transaction_hash,
                    "block_number": indexed_data.block_number,
                    "timestamp": indexed_data.timestamp.isoformat(),
                    "metadata": indexed_data.metadata,
                    "tags": indexed_data.tags
                })
            )

            # 更新索引集合
            await self.redis_pool.sadd(
                f"blockchain:index:users:{user_id}",
                index_key
            )

            # 更新标签索引
            for tag in indexed_data.tags:
                await self.redis_pool.sadd(
                    f"blockchain:index:tags:{tag}",
                    index_key
                )

            self.stats["indexed_records"] += 1
            return True

        except Exception as e:
            logger.error(f"索引交易数据失败: {e}")
            return False

    @trace(service_name="blockchain-service", kind=SpanKind.SERVER)
    @rate_limit(name="query", tokens=1)
    async def query_indexed_data(
        self,
        user_id: str | None = None,
        data_type: str | None = None,
        tags: list[str] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100
    ) -> list[IndexedData]:
        """
        查询索引数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            tags: 标签过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制
            
        Returns:
            List[IndexedData]: 索引数据列表
        """
        try:
            # 构建查询键集合
            keys = set()

            if user_id:
                user_keys = await self.redis_pool.smembers(f"blockchain:index:users:{user_id}")
                keys.update(user_keys)

            if tags:
                for tag in tags:
                    tag_keys = await self.redis_pool.smembers(f"blockchain:index:tags:{tag}")
                    if keys:
                        keys = keys.intersection(tag_keys)
                    else:
                        keys = tag_keys

            # 获取数据
            results = []
            for key in list(keys)[:limit]:
                data = await self.redis_pool.get(key)
                if data:
                    indexed_data = json.loads(data)

                    # 时间过滤
                    timestamp = datetime.fromisoformat(indexed_data["timestamp"])
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue

                    # 数据类型过滤
                    if data_type and indexed_data["data_type"] != data_type:
                        continue

                    results.append(IndexedData(
                        user_id=indexed_data["user_id"],
                        data_type=indexed_data["data_type"],
                        data_hash=indexed_data["data_hash"],
                        transaction_hash=indexed_data["transaction_hash"],
                        block_number=indexed_data["block_number"],
                        timestamp=timestamp,
                        metadata=indexed_data["metadata"],
                        tags=indexed_data["tags"]
                    ))

            return results

        except Exception as e:
            logger.error(f"查询索引数据失败: {e}")
            return []

    async def switch_chain(self, chain: ChainType) -> bool:
        """
        切换当前链
        
        Args:
            chain: 目标链
            
        Returns:
            bool: 是否成功
        """
        if chain not in self.web3_instances:
            logger.error(f"链{chain.value}未初始化")
            return False

        self.current_chain = chain
        logger.info(f"切换到链: {chain.value}")
        return True

    async def deploy_contract(
        self,
        bytecode: str,
        abi: list[dict[str, Any]],
        constructor_args: list[Any] = None,
        chain: ChainType = None
    ) -> dict[str, Any]:
        """
        部署智能合约
        
        Args:
            bytecode: 合约字节码
            abi: 合约ABI
            constructor_args: 构造函数参数
            chain: 目标链
            
        Returns:
            Dict: 部署结果
        """
        chain = chain or self.current_chain

        # 限流检查
        limiter = await get_rate_limiter(
            f"{self.service_name}_deploy",
            config=self.rate_limit_configs["deploy"]
        )

        if not await limiter.try_acquire():
            raise Exception("部署请求过于频繁")

        try:
            web3 = self._get_web3(chain)
            account = self._get_account(chain)

            # 创建合约对象
            contract = web3.eth.contract(abi=abi, bytecode=bytecode)

            # 构建部署交易
            if constructor_args:
                deploy_tx = contract.constructor(*constructor_args)
            else:
                deploy_tx = contract.constructor()

            # 估算gas
            gas_estimate = deploy_tx.estimate_gas({"from": account.address})

            # 构建交易
            tx = deploy_tx.build_transaction({
                "from": account.address,
                "gas": int(gas_estimate * 1.2),  # 20%缓冲
                "gasPrice": await self._get_optimal_gas_price(web3, TransactionPriority.HIGH),
                "nonce": web3.eth.get_transaction_count(account.address),
                "chainId": self.chain_configs[chain]["chain_id"]
            })

            # 签名并发送
            signed_tx = account.sign_transaction(tx)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # 等待确认
            receipt = await self._wait_for_confirmation(
                web3,
                tx_hash,
                self.chain_configs[chain]["confirmations"]
            )

            contract_address = receipt["contractAddress"]

            # 缓存合约
            self.contract_cache[f"{chain.value}:{contract_address}"] = ContractCache(
                address=contract_address,
                abi=abi,
                bytecode=bytecode
            )

            return {
                "status": "success",
                "contract_address": contract_address,
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt["blockNumber"],
                "gas_used": receipt["gasUsed"]
            }

        except Exception as e:
            logger.error(f"部署合约失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _index_processor(self):
        """索引处理器"""
        while True:
            try:
                # 定期清理过期索引
                await self._cleanup_expired_indexes()

                # 等待下一个处理周期
                await asyncio.sleep(self.index_config["index_interval"])

            except Exception as e:
                logger.error(f"索引处理器错误: {e}")
                await asyncio.sleep(60)

    async def _cache_cleaner(self):
        """缓存清理器"""
        while True:
            try:
                # 清理过期的合约缓存
                now = datetime.now()
                expired_keys = []

                for key, cache in self.contract_cache.items():
                    if (now - cache.last_accessed).total_seconds() > self.cache_config["contract_cache_ttl"]:
                        expired_keys.append(key)

                for key in expired_keys:
                    del self.contract_cache[key]

                if expired_keys:
                    logger.info(f"清理了{len(expired_keys)}个过期的合约缓存")

                # 控制缓存大小
                if len(self.contract_cache) > self.cache_config["max_cache_size"]:
                    # 删除最少访问的缓存
                    sorted_caches = sorted(
                        self.contract_cache.items(),
                        key=lambda x: (x[1].access_count, x[1].last_accessed)
                    )

                    to_remove = len(self.contract_cache) - self.cache_config["max_cache_size"]
                    for key, _ in sorted_caches[:to_remove]:
                        del self.contract_cache[key]

                await asyncio.sleep(300)  # 5分钟清理一次

            except Exception as e:
                logger.error(f"缓存清理器错误: {e}")
                await asyncio.sleep(60)

    async def _cleanup_expired_indexes(self):
        """清理过期索引"""
        # 实现索引过期清理逻辑
        pass

    async def _get_optimal_gas_price(self, web3: Web3, priority: TransactionPriority) -> int:
        """获取最优gas价格"""
        base_price = web3.eth.gas_price

        multipliers = {
            TransactionPriority.LOW: 0.8,
            TransactionPriority.NORMAL: 1.0,
            TransactionPriority.HIGH: 1.5,
            TransactionPriority.URGENT: 2.0
        }

        return int(base_price * multipliers[priority])

    async def _wait_for_confirmation(self, web3: Web3, tx_hash: HexBytes, confirmations: int) -> dict[str, Any]:
        """等待交易确认"""
        start_time = time.time()

        while True:
            try:
                receipt = web3.eth.get_transaction_receipt(tx_hash)
                if receipt and receipt["blockNumber"]:
                    current_block = web3.eth.block_number
                    if current_block - receipt["blockNumber"] >= confirmations:
                        confirmation_time = time.time() - start_time
                        self._update_confirmation_stats(confirmation_time)
                        return receipt
            except Exception:
                pass

            await asyncio.sleep(1)

    def _get_web3(self, chain: ChainType) -> Web3:
        """获取Web3实例"""
        if chain not in self.web3_instances:
            raise ValueError(f"链{chain.value}未初始化")
        return self.web3_instances[chain]

    def _get_account(self, chain: ChainType) -> Account:
        """获取账户"""
        # 简化实现，实际应该为每个链管理不同的账户
        if chain not in self.accounts:
            # 从环境变量或配置文件加载私钥
            private_key = "0x" + "1" * 64  # 示例私钥
            self.accounts[chain] = Account.from_key(private_key)
        return self.accounts[chain]

    def _get_shard_id(self, user_id: str) -> int:
        """获取分片ID"""
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        return hash_value % self.index_config["shard_count"]

    def _generate_method_cache_key(self, chain: ChainType, address: str,
                                  method: str, args: list[Any]) -> str:
        """生成方法缓存键"""
        args_str = json.dumps(args, sort_keys=True)
        key_string = f"{chain.value}:{address}:{method}:{args_str}"
        return f"blockchain:method:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def _get_from_cache(self, key: str) -> Any | None:
        """从缓存获取数据"""
        try:
            data = await self.redis_pool.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"缓存读取失败: {e}")
        return None

    async def _cache_result(self, key: str, data: Any, ttl: int):
        """缓存结果"""
        try:
            await self.redis_pool.setex(key, ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"缓存写入失败: {e}")

    def _update_gas_stats(self, gas_price: int):
        """更新gas统计"""
        total_tx = self.stats["total_transactions"]
        if total_tx == 1:
            self.stats["average_gas_price"] = gas_price
        else:
            current_avg = self.stats["average_gas_price"]
            self.stats["average_gas_price"] = int(
                (current_avg * (total_tx - 1) + gas_price) / total_tx
            )

    def _update_confirmation_stats(self, confirmation_time: float):
        """更新确认时间统计"""
        total_tx = self.stats["total_transactions"]
        if total_tx == 1:
            self.stats["average_confirmation_time"] = confirmation_time
        else:
            current_avg = self.stats["average_confirmation_time"]
            self.stats["average_confirmation_time"] = (
                (current_avg * (total_tx - 1) + confirmation_time) / total_tx
            )

    def get_health_status(self) -> dict[str, Any]:
        """获取服务健康状态"""
        return {
            "service": self.service_name,
            "status": "healthy",
            "stats": self.stats,
            "chains": {
                chain.value: {
                    "connected": chain in self.web3_instances,
                    "config": self.chain_configs[chain]
                }
                for chain in ChainType
            },
            "cache": {
                "contracts_cached": len(self.contract_cache),
                "hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
            },
            "batch_processing": {
                "enabled": True,
                "config": self.batch_config,
                "queued_transactions": sum(q.qsize() for q in self.transaction_queues.values())
            },
            "uptime": time.time()
        }

    async def cleanup(self):
        """清理资源"""
        # 关闭Redis连接
        if self.redis_pool:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()

        logger.info("区块链服务清理完成")

# 全局服务实例
_blockchain_service = None

async def get_blockchain_service() -> EnhancedBlockchainService:
    """获取区块链服务实例"""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = EnhancedBlockchainService()
        await _blockchain_service.initialize()
    return _blockchain_service
