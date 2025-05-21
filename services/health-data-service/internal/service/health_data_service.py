#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务，提供健康数据的管理、分析和洞察功能
"""

import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from loguru import logger
import asyncio
import aiohttp
import json

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..model.health_data import (
    HealthData, HealthDataType, TCMConstitutionData, HealthInsight,
    HealthProfile, DeviceType, MeasurementUnit
)
from ..model.database import Base
from ..repository.health_data_repository import HealthDataRepository


class HealthDataService:
    """健康数据服务类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化健康数据服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.engine = None
        self.session_factory = None
        self.is_initialized = False
        
        # 组件初始化
        self.wearable_parsers = {}
        self.analytics_services = {}
        self.blockchain_client = None
    
    async def initialize(self) -> None:
        """初始化所有组件"""
        if self.is_initialized:
            return
            
        logger.info("正在初始化健康数据服务")
        
        # 初始化数据库连接
        await self._init_database()
        
        # 初始化可穿戴设备数据解析器
        await self._init_wearable_parsers()
        
        # 初始化分析服务
        await self._init_analytics_services()
        
        # 初始化区块链客户端
        if self.config['blockchain']['enabled']:
            await self._init_blockchain_client()
        
        self.is_initialized = True
        logger.info("健康数据服务初始化成功")
    
    async def _init_database(self) -> None:
        """初始化数据库连接"""
        db_config = self.config['database']
        
        # 构建数据库URL
        if db_config['dialect'] == 'postgresql':
            url = f"{db_config['dialect']}+{db_config['driver']}://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_config['dialect']}")
        
        # 创建引擎和会话工厂
        self.engine = create_async_engine(
            url,
            echo=False,
            pool_size=db_config.get('pool_size', 5),
            max_overflow=db_config.get('max_overflow', 10),
            pool_timeout=db_config.get('pool_timeout', 30),
            pool_recycle=db_config.get('pool_recycle', 1800),
            connect_args=db_config.get('connect_args', {})
        )
        
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # 创建数据库表
        async with self.engine.begin() as conn:
            # 仅在开发环境下自动创建表
            if self.config.get('env', 'development') == 'development':
                await conn.run_sync(Base.metadata.create_all)
                logger.info("数据库表创建完成")
    
    async def _init_wearable_parsers(self) -> None:
        """初始化可穿戴设备数据解析器"""
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
    
    async def _init_analytics_services(self) -> None:
        """初始化分析服务"""
        from .analytics.time_series_analyzer import TimeSeriesAnalyzer
        from .analytics.correlation_analyzer import CorrelationAnalyzer
        from .analytics.health_index_calculator import HealthIndexCalculator
        from .analytics.tcm_constitution_analyzer import TCMConstitutionAnalyzer
        
        # 注册分析服务
        self.analytics_services = {
            "time_series": TimeSeriesAnalyzer(self.config['analytics']['time_series']),
            "correlation": CorrelationAnalyzer(self.config['analytics']['correlation']),
            "health_index": HealthIndexCalculator(self.config['analytics']['health_index']),
            "tcm_constitution": TCMConstitutionAnalyzer(self.config)
        }
        
        logger.info(f"已注册{len(self.analytics_services)}个分析服务")
    
    async def _init_blockchain_client(self) -> None:
        """初始化区块链客户端"""
        from .blockchain.blockchain_client import BlockchainClient
        
        self.blockchain_client = BlockchainClient(
            service_url=self.config['blockchain']['service_url'],
            timeout=self.config['blockchain']['timeout']
        )
        
        await self.blockchain_client.initialize()
        logger.info("区块链客户端初始化成功")
    
    async def get_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: Optional[HealthDataType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
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
            
        Returns:
            健康数据列表
        """
        if not self.is_initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            repository = HealthDataRepository(session)
            records = await repository.get_health_data(
                user_id=user_id,
                data_type=data_type,
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
                    value=record.value.get("value", record.value),
                    unit=MeasurementUnit(record.unit),
                    source=record.source,
                    metadata=record.metadata
                )
                results.append(health_data)
            
            return results
    
    async def save_health_data(self, data: HealthData) -> str:
        """
        保存健康数据
        
        Args:
            data: 健康数据对象
            
        Returns:
            数据ID
        """
        if not self.is_initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            async with session.begin():
                repository = HealthDataRepository(session)
                
                # 检查用户是否存在，不存在则创建
                if isinstance(data.user_id, str):
                    data.user_id = uuid.UUID(data.user_id)
                
                # 保存数据
                record = await repository.save_health_data(data)
                
                # 触发分析任务
                await self._trigger_analysis_task(data)
                
                # 如果启用了区块链，保存哈希到区块链
                if self.blockchain_client and self.config['blockchain']['enabled']:
                    data_dict = data.dict()
                    await self._save_to_blockchain("health_data_hash", data_dict, data.user_id)
                
                return str(record.id)
    
    async def save_health_data_batch(self, data_list: List[HealthData]) -> List[str]:
        """
        批量保存健康数据
        
        Args:
            data_list: 健康数据对象列表
            
        Returns:
            数据ID列表
        """
        if not self.is_initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            async with session.begin():
                repository = HealthDataRepository(session)
                
                # 转换用户ID为UUID
                for data in data_list:
                    if isinstance(data.user_id, str):
                        data.user_id = uuid.UUID(data.user_id)
                
                # 批量保存数据
                records = await repository.save_health_data_batch(data_list)
                
                # 触发分析任务
                for data in data_list:
                    await self._trigger_analysis_task(data)
                
                # 如果启用了区块链，批量保存哈希到区块链
                if self.blockchain_client and self.config['blockchain']['enabled']:
                    # 仅将一个批次的哈希保存到区块链，而不是每个数据项
                    batch_data = [data.dict() for data in data_list]
                    await self._save_to_blockchain(
                        "health_data_batch_hash",
                        {"batch_size": len(batch_data), "timestamp": datetime.utcnow().isoformat()},
                        data_list[0].user_id
                    )
                
                return [str(record.id) for record in records]
    
    async def process_wearable_data(
        self,
        user_id: Union[uuid.UUID, str],
        device_type: DeviceType,
        data: Union[str, Dict, bytes],
        source: str = "api_import"
    ) -> Dict[str, Any]:
        """
        处理可穿戴设备数据
        
        Args:
            user_id: 用户ID
            device_type: 设备类型
            data: 设备数据
            source: 数据来源
            
        Returns:
            处理结果摘要
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 查找设备解析器
        device_config = None
        parser_name = None
        
        for device in self.config['wearable_data']['supported_devices']:
            if device['name'] == device_type.value:
                device_config = device
                parser_name = device['parser']
                break
        
        if not parser_name or parser_name not in self.wearable_parsers:
            raise ValueError(f"不支持的设备类型: {device_type}")
        
        # 解析设备数据
        parser = self.wearable_parsers[parser_name]
        parsed_data = await parser.parse(data, device_config)
        
        # 转换成健康数据对象并保存
        health_data_list = []
        for item in parsed_data:
            health_data = HealthData(
                user_id=user_id,
                data_type=item['data_type'],
                timestamp=item['timestamp'],
                device_type=device_type,
                device_id=item.get('device_id'),
                value=item['value'],
                unit=item['unit'],
                source=source,
                metadata=item.get('metadata', {})
            )
            health_data_list.append(health_data)
        
        # 批量保存数据
        if health_data_list:
            await self.save_health_data_batch(health_data_list)
        
        # 返回处理结果摘要
        data_type_counts = {}
        for item in health_data_list:
            data_type = item.data_type.value
            if data_type in data_type_counts:
                data_type_counts[data_type] += 1
            else:
                data_type_counts[data_type] = 1
        
        return {
            "device_type": device_type.value,
            "processed_items": len(health_data_list),
            "data_types": data_type_counts,
            "time_range": {
                "start": min([item.timestamp for item in health_data_list]).isoformat() if health_data_list else None,
                "end": max([item.timestamp for item in health_data_list]).isoformat() if health_data_list else None
            }
        }
    
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
        if not self.is_initialized:
            await self.initialize()
        
        # 计算时间范围
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        async with self.session_factory() as session:
            repository = HealthDataRepository(session)
            
            stats = await repository.get_health_data_statistics(
                user_id=user_id,
                data_type=data_type,
                start_time=start_time,
                end_time=end_time
            )
            
            return stats
    
    async def get_health_insights(
        self,
        user_id: Union[uuid.UUID, str],
        insight_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 20
    ) -> List[HealthInsight]:
        """
        获取健康洞察
        
        Args:
            user_id: 用户ID
            insight_type: 洞察类型
            severity: 严重程度
            limit: 结果限制
            
        Returns:
            健康洞察列表
        """
        if not self.is_initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            repository = HealthDataRepository(session)
            
            insights = await repository.get_health_insights(
                user_id=user_id,
                insight_type=insight_type,
                severity=severity,
                limit=limit
            )
            
            # 转换为模型对象
            results = []
            for insight in insights:
                insight_model = HealthInsight(
                    id=insight.id,
                    user_id=insight.user_id,
                    timestamp=insight.timestamp,
                    insight_type=insight.insight_type,
                    data_type=HealthDataType(insight.data_type),
                    time_range=insight.time_range,
                    description=insight.description,
                    details=insight.details,
                    severity=insight.severity,
                    relevance_score=insight.relevance_score,
                    created_at=insight.created_at
                )
                results.append(insight_model)
            
            return results
    
    async def get_latest_tcm_constitution(
        self,
        user_id: Union[uuid.UUID, str]
    ) -> Optional[TCMConstitutionData]:
        """
        获取用户最新的中医体质数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            中医体质数据
        """
        if not self.is_initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            repository = HealthDataRepository(session)
            
            constitution = await repository.get_latest_tcm_constitution(user_id)
            
            if not constitution:
                return None
            
            # 转换为模型对象
            from ..model.health_data import TCMConstitutionType
            
            result = TCMConstitutionData(
                id=constitution.id,
                user_id=constitution.user_id,
                timestamp=constitution.timestamp,
                primary_type=TCMConstitutionType(constitution.primary_type),
                secondary_types=[TCMConstitutionType(t) for t in constitution.secondary_types],
                scores=constitution.scores,
                analysis_basis=constitution.analysis_basis,
                recommendations=constitution.recommendations,
                created_by=constitution.created_by,
                created_at=constitution.created_at,
                updated_at=constitution.updated_at
            )
            
            return result
    
    async def _trigger_analysis_task(self, data: HealthData) -> None:
        """
        触发健康数据分析任务
        
        Args:
            data: 健康数据
        """
        # 发送到消息队列进行异步处理
        message = {
            "task_type": "analyze_health_data",
            "data": {
                "user_id": str(data.user_id),
                "data_type": data.data_type.value,
                "timestamp": data.timestamp.isoformat(),
                "data_id": str(data.id)
            }
        }
        
        # 使用消息队列客户端发送消息
        if 'message_queue' in self.config and self.config['message_queue']['provider'] == 'kafka':
            try:
                from .queue.kafka_client import KafkaClient
                kafka_client = KafkaClient(self.config['message_queue'])
                await kafka_client.send_message(
                    topic=self.config['message_queue']['topics']['analytics'],
                    message=json.dumps(message)
                )
                logger.info(f"已触发数据分析任务: {message['task_type']}")
            except Exception as e:
                logger.error(f"发送消息到Kafka失败: {str(e)}")
    
    async def _save_to_blockchain(
        self,
        record_type: str,
        data: Dict[str, Any],
        user_id: Union[uuid.UUID, str]
    ) -> Optional[str]:
        """
        保存数据到区块链
        
        Args:
            record_type: 记录类型
            data: 数据字典
            user_id: 用户ID
            
        Returns:
            区块链交易ID
        """
        if not self.blockchain_client:
            logger.warning("区块链客户端未初始化")
            return None
        
        try:
            # 计算数据哈希
            import hashlib
            data_str = json.dumps(data, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()
            
            # 发送到区块链服务
            blockchain_id = await self.blockchain_client.store_hash(data_hash, record_type)
            
            # 保存记录到数据库
            async with self.session_factory() as session:
                async with session.begin():
                    from ..model.database import BlockchainRecord
                    
                    record = BlockchainRecord(
                        user_id=user_id,
                        record_type=record_type,
                        data_hash=data_hash,
                        blockchain_id=blockchain_id,
                        blockchain_status="confirmed" if blockchain_id else "pending",
                        details={"data_type": data.get("data_type"), "timestamp": datetime.utcnow().isoformat()}
                    )
                    
                    session.add(record)
            
            return blockchain_id
        except Exception as e:
            logger.error(f"保存到区块链失败: {str(e)}")
            return None
    
    async def health_check(self) -> Tuple[str, Dict[str, Any]]:
        """
        检查服务健康状态
        
        Returns:
            状态和详细信息
        """
        status = "SERVING"
        details = {
            "version": self.config['service'].get('version', "0.1.0"),
            "name": self.config['service'].get('name', "health-data-service")
        }
        
        try:
            if not self.is_initialized:
                status = "NOT_SERVING"
                details["reason"] = "服务未初始化"
                return status, details
            
            # 检查数据库连接
            async with self.engine.connect() as conn:
                result = await conn.execute("SELECT 1")
                row = result.fetchone()
                if row and row[0] == 1:
                    details["database_connected"] = True
                else:
                    status = "NOT_SERVING"
                    details["reason"] = "数据库连接失败"
                    return status, details
            
            # 检查区块链服务
            if self.blockchain_client and self.config['blockchain']['enabled']:
                blockchain_status = await self.blockchain_client.health_check()
                details["blockchain_status"] = blockchain_status
                if not blockchain_status.get("healthy", False):
                    details["warnings"] = ["区块链服务不可用"]
            
            return status, details
            
        except Exception as e:
            status = "NOT_SERVING"
            details["error"] = str(e)
            logger.error(f"健康检查失败: {str(e)}")
            return status, details
    
    async def close(self) -> None:
        """关闭服务和所有组件"""
        logger.info("正在关闭健康数据服务")
        
        # 关闭区块链客户端
        if self.blockchain_client:
            await self.blockchain_client.close()
        
        # 关闭分析服务
        for service_name, service in self.analytics_services.items():
            if hasattr(service, 'close') and callable(service.close):
                await service.close()
        
        # 关闭数据库引擎
        if self.engine:
            await self.engine.dispose()
        
        self.is_initialized = False
        logger.info("健康数据服务已关闭") 