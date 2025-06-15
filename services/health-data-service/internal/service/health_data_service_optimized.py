#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务 - 优化版
提供高性能的健康数据管理、分析和洞察功能
"""

import uuid
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from ..model.health_data import (
    HealthData, HealthDataType, TCMConstitutionData, HealthInsight,
    HealthProfile, DeviceType, MeasurementUnit
)
from ..model.database import Base, HealthDataRecord, User
from ..repository.health_data_repository import HealthDataRepository
from ...pkg.utils.cache_service import CacheService, cache_result
from ...pkg.utils.error_handler import (
    HealthDataError, DatabaseError, ValidationError, 
    with_retry, with_timeout, safe_execute, CircuitBreaker
)


@dataclass
class DataQualityMetrics:
    """数据质量指标"""
    completeness: float  # 完整性 0-1
    accuracy: float      # 准确性 0-1
    consistency: float   # 一致性 0-1
    timeliness: float    # 及时性 0-1
    overall_score: float # 总体评分 0-1


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation: str
    duration: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class HealthDataServiceOptimized:
    """优化版健康数据服务"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化健康数据服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.engine = None
        self.session_factory = None
        self.cache_service: Optional[CacheService] = None
        self.is_initialized = False
        
        # 性能监控
        self.performance_metrics: List[PerformanceMetrics] = []
        self.circuit_breakers = {}
        
        # 组件初始化
        self.wearable_parsers = {}
        self.analytics_services = {}
        self.blockchain_client = None
        
        # 数据质量评估器
        self.quality_assessor = None
    
    async def initialize(self) -> None:
        """初始化所有组件"""
        if self.is_initialized:
            return
            
        logger.info("正在初始化优化版健康数据服务")
        
        try:
            # 初始化缓存服务
            await self._init_cache_service()
            
            # 初始化数据库连接
            await self._init_database()
            
            # 初始化熔断器
            self._init_circuit_breakers()
            
            # 初始化数据质量评估器
            await self._init_quality_assessor()
            
            # 初始化可穿戴设备数据解析器
            await self._init_wearable_parsers()
            
            # 初始化分析服务
            await self._init_analytics_services()
            
            # 初始化区块链客户端
            if self.config.get('blockchain', {}).get('enabled', False):
                await self._init_blockchain_client()
            
            self.is_initialized = True
            logger.info("优化版健康数据服务初始化成功")
            
        except Exception as e:
            logger.error(f"健康数据服务初始化失败: {e}")
            raise HealthDataError(f"服务初始化失败: {str(e)}")
    
    async def _init_cache_service(self) -> None:
        """初始化缓存服务"""
        cache_config = self.config.get('cache', {})
        if cache_config.get('enabled', False):
            from ...pkg.utils.cache_service import init_cache_service
            self.cache_service = await init_cache_service(cache_config)
            logger.info("缓存服务初始化成功")
    
    async def _init_database(self) -> None:
        """初始化数据库连接"""
        db_config = self.config['database']
        
        # 构建数据库URL - 支持PostgreSQL
        if db_config['dialect'] == 'postgresql':
            url = f"{db_config['dialect']}+{db_config['driver']}://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_config['dialect']}")
        
        # 创建引擎
        engine_kwargs = {
            'echo': db_config.get('echo', False),
            'pool_size': db_config.get('pool_size', 20),
            'max_overflow': db_config.get('max_overflow', 10),
            'pool_timeout': db_config.get('pool_timeout', 30),
            'pool_recycle': db_config.get('pool_recycle', 3600),
            'pool_pre_ping': db_config.get('pool_pre_ping', True),
        }
        
        # PostgreSQL特定配置
        connect_args = db_config.get('connect_args', {})
        if connect_args:
            engine_kwargs['connect_args'] = connect_args
        
        # 引擎选项
        engine_options = db_config.get('engine_options', {})
        if engine_options:
            engine_kwargs.update(engine_options)
        
        self.engine = create_async_engine(url, **engine_kwargs)
        
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # 创建数据库表
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # PostgreSQL优化设置
            if db_config['dialect'] == 'postgresql':
                # 设置一些PostgreSQL特定的优化参数
                optimization_queries = [
                    "SET shared_preload_libraries = 'pg_stat_statements'",
                    "SET log_statement = 'none'",
                    "SET log_min_duration_statement = 1000",  # 记录超过1秒的查询
                ]
                
                for query in optimization_queries:
                    try:
                        await conn.execute(text(query))
                    except Exception as e:
                        logger.warning(f"PostgreSQL优化设置失败: {query}, 错误: {e}")
                    
        logger.info("PostgreSQL数据库连接初始化成功")
    
    def _init_circuit_breakers(self) -> None:
        """初始化熔断器"""
        cb_config = self.config.get('circuit_breaker', {})
        if cb_config.get('enabled', False):
            self.circuit_breakers = {
                'database': CircuitBreaker(
                    failure_threshold=cb_config.get('failure_threshold', 5),
                    recovery_timeout=cb_config.get('recovery_timeout', 30),
                    expected_exception=DatabaseError
                ),
                'external_api': CircuitBreaker(
                    failure_threshold=cb_config.get('failure_threshold', 5),
                    recovery_timeout=cb_config.get('recovery_timeout', 30)
                )
            }
            logger.info("熔断器初始化成功")
    
    async def _init_quality_assessor(self) -> None:
        """初始化数据质量评估器"""
        from .quality.data_quality_assessor import DataQualityAssessor
        self.quality_assessor = DataQualityAssessor(self.config)
        await self.quality_assessor.initialize()
        logger.info("数据质量评估器初始化成功")
    
    async def _init_wearable_parsers(self) -> None:
        """初始化可穿戴设备数据解析器"""
        try:
            from .parsers.apple_health_parser import AppleHealthParser
            from .parsers.fitbit_parser import FitbitParser
            from .parsers.garmin_parser import GarminParser
            from .parsers.xiaomi_parser import XiaomiParser
            
            # 注册解析器
            self.wearable_parsers = {
                "apple_health_xml_parser": AppleHealthParser(),
                "fitbit_json_parser": FitbitParser(),
                "garmin_fit_parser": GarminParser(),
                "xiaomi_json_parser": XiaomiParser()
            }
            
            logger.info(f"已注册{len(self.wearable_parsers)}个设备数据解析器")
        except ImportError as e:
            logger.warning(f"部分解析器加载失败: {e}")
    
    async def _init_analytics_services(self) -> None:
        """初始化分析服务"""
        try:
            from .analytics.time_series_analyzer import TimeSeriesAnalyzer
            from .analytics.correlation_analyzer import CorrelationAnalyzer
            from .analytics.health_index_calculator import HealthIndexCalculator
            from .analytics.tcm_constitution_analyzer import TCMConstitutionAnalyzer
            
            # 注册分析服务
            self.analytics_services = {
                "time_series": TimeSeriesAnalyzer(self.config.get('analytics', {}).get('time_series', {})),
                "correlation": CorrelationAnalyzer(self.config.get('analytics', {}).get('correlation', {})),
                "health_index": HealthIndexCalculator(self.config.get('analytics', {}).get('health_index', {})),
                "tcm_constitution": TCMConstitutionAnalyzer(self.config)
            }
            
            logger.info(f"已注册{len(self.analytics_services)}个分析服务")
        except ImportError as e:
            logger.warning(f"部分分析服务加载失败: {e}")
    
    async def _init_blockchain_client(self) -> None:
        """初始化区块链客户端"""
        try:
            from .blockchain.blockchain_client import BlockchainClient
            
            self.blockchain_client = BlockchainClient(
                service_url=self.config['blockchain']['service_url'],
                timeout=self.config['blockchain']['timeout']
            )
            
            await self.blockchain_client.initialize()
            logger.info("区块链客户端初始化成功")
        except Exception as e:
            logger.warning(f"区块链客户端初始化失败: {e}")
    
    def _record_performance(self, operation: str, duration: float, success: bool, error_message: str = None):
        """记录性能指标"""
        metric = PerformanceMetrics(
            operation=operation,
            duration=duration,
            success=success,
            error_message=error_message
        )
        self.performance_metrics.append(metric)
        
        # 保持最近1000条记录
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def get_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: Optional[HealthDataType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        use_cache: bool = True
    ) -> List[HealthData]:
        """
        获取用户健康数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间
            end_time: 结束时间
            limit: 结果限制
            offset: 结果偏移
            use_cache: 是否使用缓存
            
        Returns:
            健康数据列表
        """
        start_time_op = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 生成缓存键
            cache_key = f"health_data:{user_id}:{data_type}:{start_time}:{end_time}:{limit}:{offset}"
            
            # 尝试从缓存获取
            if use_cache and self.cache_service:
                cached_result = await self.cache_service.get(cache_key, "health_data")
                if cached_result is not None:
                    duration = time.time() - start_time_op
                    self._record_performance("get_health_data_cached", duration, True)
                    return [HealthData(**item) for item in cached_result]
            
            # 从数据库获取
            async with self.session_factory() as session:
                repository = HealthDataRepository(session)
                records = await repository.get_health_data(
                    user_id=user_id,
                    data_type=data_type.value if data_type else None,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit,
                    offset=offset
                )
                
                # 转换为模型对象
                results = []
                for record in records:
                    health_data = HealthData(
                        id=record.id,
                        user_id=record.user_id,
                        data_type=HealthDataType(record.data_type),
                        timestamp=record.timestamp,
                        device_type=DeviceType(record.device_type),
                        device_id=record.device_id,
                        value=record.value.get("value", record.value) if isinstance(record.value, dict) else record.value,
                        unit=MeasurementUnit(record.unit),
                        source=record.source,
                        metadata=record.metadata or {}
                    )
                    results.append(health_data)
                
                # 缓存结果
                if use_cache and self.cache_service and results:
                    cache_data = [data.__dict__ for data in results]
                    ttl = self.cache_service.strategies.get('health_data', 1800)
                    await self.cache_service.set(cache_key, cache_data, ttl, "health_data")
                
                duration = time.time() - start_time_op
                self._record_performance("get_health_data", duration, True)
                return results
                
        except Exception as e:
            duration = time.time() - start_time_op
            self._record_performance("get_health_data", duration, False, str(e))
            logger.error(f"获取健康数据失败: {e}")
            raise DatabaseError(f"获取健康数据失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def save_health_data(self, data: HealthData, validate_quality: bool = True) -> str:
        """
        保存健康数据
        
        Args:
            data: 健康数据
            validate_quality: 是否进行数据质量验证
            
        Returns:
            数据记录ID
        """
        start_time_op = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 数据验证
            if not data.user_id:
                raise ValidationError("用户ID不能为空")
            
            # 数据质量评估
            quality_score = 1.0
            if validate_quality and self.quality_assessor:
                quality_metrics = await self.quality_assessor.assess_data_quality(data)
                quality_score = quality_metrics.overall_score
                
                # 如果质量分数过低，记录警告
                if quality_score < 0.5:
                    logger.warning(f"数据质量较低: {quality_score}, 数据: {data}")
            
            # 保存到数据库
            async with self.session_factory() as session:
                repository = HealthDataRepository(session)
                
                # 创建数据库记录
                record = HealthDataRecord(
                    id=data.id or uuid.uuid4(),
                    user_id=data.user_id,
                    data_type=data.data_type.value,
                    timestamp=data.timestamp,
                    device_type=data.device_type.value,
                    device_id=data.device_id,
                    value={"value": data.value} if not isinstance(data.value, dict) else data.value,
                    unit=data.unit.value,
                    source=data.source,
                    metadata=data.metadata or {},
                    quality_score=quality_score,
                    is_validated=validate_quality
                )
                
                record_id = await repository.save_health_data_record(record)
                
                # 清除相关缓存
                if self.cache_service:
                    await self.cache_service.clear_pattern(f"health_data:{data.user_id}:*")
                
                # 触发异步分析任务
                asyncio.create_task(self._trigger_analysis_task(data))
                
                # 保存到区块链（如果启用）
                if self.blockchain_client:
                    asyncio.create_task(self._save_to_blockchain("health_data", data.__dict__, data.user_id))
                
                duration = time.time() - start_time_op
                self._record_performance("save_health_data", duration, True)
                return str(record_id)
                
        except Exception as e:
            duration = time.time() - start_time_op
            self._record_performance("save_health_data", duration, False, str(e))
            logger.error(f"保存健康数据失败: {e}")
            raise DatabaseError(f"保存健康数据失败: {str(e)}")
    
    async def save_health_data_batch(
        self, 
        data_list: List[HealthData], 
        batch_size: int = 100,
        validate_quality: bool = True
    ) -> List[str]:
        """
        批量保存健康数据
        
        Args:
            data_list: 健康数据列表
            batch_size: 批处理大小
            validate_quality: 是否进行数据质量验证
            
        Returns:
            数据记录ID列表
        """
        start_time_op = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not data_list:
                return []
            
            record_ids = []
            
            # 分批处理
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                
                async with self.session_factory() as session:
                    repository = HealthDataRepository(session)
                    
                    # 准备批量数据
                    records = []
                    for data in batch:
                        # 数据质量评估
                        quality_score = 1.0
                        if validate_quality and self.quality_assessor:
                            quality_metrics = await self.quality_assessor.assess_data_quality(data)
                            quality_score = quality_metrics.overall_score
                        
                        record = HealthDataRecord(
                            id=data.id or uuid.uuid4(),
                            user_id=data.user_id,
                            data_type=data.data_type.value,
                            timestamp=data.timestamp,
                            device_type=data.device_type.value,
                            device_id=data.device_id,
                            value={"value": data.value} if not isinstance(data.value, dict) else data.value,
                            unit=data.unit.value,
                            source=data.source,
                            metadata=data.metadata or {},
                            quality_score=quality_score,
                            is_validated=validate_quality
                        )
                        records.append(record)
                    
                    # 批量保存
                    batch_ids = await repository.save_health_data_batch(records)
                    record_ids.extend(batch_ids)
            
            # 清除相关缓存
            if self.cache_service:
                user_ids = {str(data.user_id) for data in data_list}
                for user_id in user_ids:
                    await self.cache_service.clear_pattern(f"health_data:{user_id}:*")
            
            duration = time.time() - start_time_op
            self._record_performance("save_health_data_batch", duration, True)
            logger.info(f"批量保存{len(data_list)}条健康数据成功")
            return [str(rid) for rid in record_ids]
            
        except Exception as e:
            duration = time.time() - start_time_op
            self._record_performance("save_health_data_batch", duration, False, str(e))
            logger.error(f"批量保存健康数据失败: {e}")
            raise DatabaseError(f"批量保存健康数据失败: {str(e)}")
    
    @cache_result(ttl=1800, prefix="health_stats")
    async def get_health_statistics(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: HealthDataType,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取健康数据统计信息
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            days: 统计天数
            
        Returns:
            统计信息
        """
        start_time_op = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # 获取数据
            data_list = await self.get_health_data(
                user_id=user_id,
                data_type=data_type,
                start_time=start_time,
                end_time=end_time,
                limit=10000,
                use_cache=True
            )
            
            if not data_list:
                return {
                    "count": 0,
                    "average": None,
                    "min": None,
                    "max": None,
                    "trend": None
                }
            
            # 计算统计信息
            values = [float(data.value) for data in data_list if isinstance(data.value, (int, float))]
            
            if not values:
                return {
                    "count": len(data_list),
                    "average": None,
                    "min": None,
                    "max": None,
                    "trend": None
                }
            
            # 使用时间序列分析器计算趋势
            trend = None
            if "time_series" in self.analytics_services:
                try:
                    trend_result = await self.analytics_services["time_series"].analyze_trend(data_list)
                    trend = trend_result.get("trend_direction")
                except Exception as e:
                    logger.warning(f"趋势分析失败: {e}")
            
            stats = {
                "count": len(data_list),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "trend": trend,
                "data_quality_avg": sum(data.metadata.get("quality_score", 1.0) for data in data_list) / len(data_list)
            }
            
            duration = time.time() - start_time_op
            self._record_performance("get_health_statistics", duration, True)
            return stats
            
        except Exception as e:
            duration = time.time() - start_time_op
            self._record_performance("get_health_statistics", duration, False, str(e))
            logger.error(f"获取健康统计信息失败: {e}")
            raise DatabaseError(f"获取健康统计信息失败: {str(e)}")
    
    async def _trigger_analysis_task(self, data: HealthData) -> None:
        """触发异步分析任务"""
        try:
            # 健康指数计算
            if "health_index" in self.analytics_services:
                asyncio.create_task(
                    self.analytics_services["health_index"].update_health_index(data.user_id)
                )
            
            # 异常检测
            if "time_series" in self.analytics_services:
                asyncio.create_task(
                    self.analytics_services["time_series"].detect_anomalies(data)
                )
            
            # 中医体质分析（定期触发）
            if "tcm_constitution" in self.analytics_services and data.data_type in [
                HealthDataType.HEART_RATE, HealthDataType.SLEEP, HealthDataType.STEPS
            ]:
                asyncio.create_task(
                    self.analytics_services["tcm_constitution"].analyze_constitution(data.user_id)
                )
                
        except Exception as e:
            logger.warning(f"触发分析任务失败: {e}")
    
    @safe_execute(default_return=None, log_errors=True, raise_on_error=False)
    async def _save_to_blockchain(
        self,
        record_type: str,
        data: Dict[str, Any],
        user_id: Union[uuid.UUID, str]
    ) -> Optional[str]:
        """保存数据到区块链"""
        if not self.blockchain_client:
            return None
        
        try:
            return await self.blockchain_client.save_record(
                record_type=record_type,
                data=data,
                user_id=str(user_id)
            )
        except Exception as e:
            logger.warning(f"保存到区块链失败: {e}")
            return None
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        if not self.performance_metrics:
            return {"message": "暂无性能数据"}
        
        # 计算统计信息
        total_operations = len(self.performance_metrics)
        successful_operations = sum(1 for m in self.performance_metrics if m.success)
        failed_operations = total_operations - successful_operations
        
        durations = [m.duration for m in self.performance_metrics if m.success]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # 按操作类型分组
        operations_by_type = {}
        for metric in self.performance_metrics:
            op_type = metric.operation
            if op_type not in operations_by_type:
                operations_by_type[op_type] = {"count": 0, "success": 0, "total_duration": 0}
            
            operations_by_type[op_type]["count"] += 1
            if metric.success:
                operations_by_type[op_type]["success"] += 1
                operations_by_type[op_type]["total_duration"] += metric.duration
        
        # 计算每种操作的平均时间
        for op_type, stats in operations_by_type.items():
            if stats["success"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["success"]
            else:
                stats["avg_duration"] = 0
            stats["success_rate"] = stats["success"] / stats["count"]
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations,
            "average_duration": avg_duration,
            "operations_by_type": operations_by_type,
            "cache_stats": await self.cache_service.get_stats() if self.cache_service else None
        }
    
    async def health_check(self) -> Tuple[str, Dict[str, Any]]:
        """健康检查"""
        status = "healthy"
        details = {
            "service": "health-data-service-optimized",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # 检查数据库连接
        try:
            async with self.session_factory() as session:
                await session.execute(text("SELECT 1"))
            details["components"]["database"] = "healthy"
        except Exception as e:
            details["components"]["database"] = f"unhealthy: {str(e)}"
            status = "unhealthy"
        
        # 检查缓存服务
        if self.cache_service:
            try:
                await self.cache_service.set("health_check", "ok", 10)
                cached_value = await self.cache_service.get("health_check")
                if cached_value == "ok":
                    details["components"]["cache"] = "healthy"
                else:
                    details["components"]["cache"] = "unhealthy: cache test failed"
                    status = "degraded"
            except Exception as e:
                details["components"]["cache"] = f"unhealthy: {str(e)}"
                status = "degraded"
        else:
            details["components"]["cache"] = "disabled"
        
        # 检查区块链客户端
        if self.blockchain_client:
            try:
                blockchain_status = await self.blockchain_client.health_check()
                details["components"]["blockchain"] = blockchain_status
            except Exception as e:
                details["components"]["blockchain"] = f"unhealthy: {str(e)}"
                status = "degraded"
        else:
            details["components"]["blockchain"] = "disabled"
        
        # 添加性能指标
        details["performance"] = await self.get_performance_metrics()
        
        return status, details
    
    async def close(self) -> None:
        """关闭服务"""
        logger.info("正在关闭健康数据服务")
        
        if self.cache_service:
            await self.cache_service.close()
        
        if self.blockchain_client:
            await self.blockchain_client.close()
        
        if self.engine:
            await self.engine.dispose()
        
        logger.info("健康数据服务已关闭") 