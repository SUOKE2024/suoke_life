#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版健康数据服务
集成时序数据库优化、数据预聚合、流式处理、智能分片等功能
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
import redis.asyncio as redis
import aiokafka
from motor.motor_asyncio import AsyncIOMotorClient

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter, rate_limit
)
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

logger = logging.getLogger(__name__)

class DataType(Enum):
    """健康数据类型"""
    VITAL_SIGNS = "vital_signs"          # 生命体征
    ACTIVITY = "activity"                # 活动数据
    SLEEP = "sleep"                      # 睡眠数据
    NUTRITION = "nutrition"              # 营养数据
    MENTAL_HEALTH = "mental_health"      # 心理健康
    MEDICAL_RECORDS = "medical_records"  # 医疗记录
    LAB_RESULTS = "lab_results"          # 实验室结果
    MEDICATIONS = "medications"          # 用药记录

class AggregationType(Enum):
    """聚合类型"""
    MEAN = "mean"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    STDDEV = "stddev"
    PERCENTILE = "percentile"

@dataclass
class HealthDataPoint:
    """健康数据点"""
    user_id: str
    data_type: DataType
    timestamp: datetime
    value: float
    unit: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class DataQuery:
    """数据查询请求"""
    user_id: str
    data_types: List[DataType]
    start_time: datetime
    end_time: datetime
    aggregation: Optional[AggregationType] = None
    interval: Optional[str] = None  # 1m, 5m, 1h, 1d等
    filters: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class StreamConfig:
    """流处理配置"""
    topic: str
    group_id: str
    batch_size: int = 100
    batch_timeout: float = 1.0
    
class EnhancedHealthDataService:
    """增强版健康数据服务"""
    
    def __init__(self):
        self.service_name = "health-data-service"
        self.tracer = get_tracer(self.service_name)
        
        # 时序数据库客户端（InfluxDB）
        self.influx_client = None
        self.write_api = None
        
        # MongoDB客户端（用于元数据和复杂查询）
        self.mongo_client = None
        self.mongo_db = None
        
        # Redis客户端（用于缓存和实时数据）
        self.redis_pool = None
        
        # Kafka客户端（用于流处理）
        self.kafka_producer = None
        self.kafka_consumers = {}
        
        # 初始化断路器配置
        self._init_circuit_breakers()
        
        # 初始化限流器配置
        self._init_rate_limiters()
        
        # 数据分片配置
        self.shard_config = {
            'shard_count': 10,
            'replication_factor': 3,
            'retention_policy': {
                DataType.VITAL_SIGNS: '30d',
                DataType.ACTIVITY: '90d',
                DataType.SLEEP: '180d',
                DataType.MEDICAL_RECORDS: '10y',
                DataType.LAB_RESULTS: '5y'
            }
        }
        
        # 预聚合配置
        self.aggregation_config = {
            'intervals': ['1m', '5m', '1h', '1d'],
            'metrics': ['mean', 'min', 'max', 'count', 'stddev'],
            'enabled_types': [
                DataType.VITAL_SIGNS,
                DataType.ACTIVITY,
                DataType.SLEEP
            ]
        }
        
        # 缓存配置
        self.cache_config = {
            'query_cache_ttl': 300,      # 5分钟
            'aggregation_cache_ttl': 3600,  # 1小时
            'user_profile_cache_ttl': 1800,  # 30分钟
            'max_cache_size': 10000
        }
        
        # 统计信息
        self.stats = {
            'total_writes': 0,
            'total_reads': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'stream_processed': 0,
            'aggregations_computed': 0,
            'average_write_time': 0.0,
            'average_read_time': 0.0,
            'active_streams': 0
        }
        
        logger.info("增强版健康数据服务初始化完成")
    
    def _init_circuit_breakers(self):
        """初始化断路器配置"""
        self.circuit_breaker_configs = {
            'influxdb': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=10.0
            ),
            'mongodb': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=5.0
            ),
            'redis': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=3.0
            ),
            'kafka': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=45.0,
                timeout=5.0
            )
        }
    
    def _init_rate_limiters(self):
        """初始化限流器配置"""
        self.rate_limit_configs = {
            'write': RateLimitConfig(rate=1000.0, burst=2000),    # 每秒1000次写入
            'read': RateLimitConfig(rate=2000.0, burst=4000),     # 每秒2000次读取
            'stream': RateLimitConfig(rate=500.0, burst=1000),    # 每秒500次流处理
            'export': RateLimitConfig(rate=10.0, burst=20),       # 每秒10次导出
        }
    
    async def initialize(self):
        """初始化服务连接"""
        # 初始化InfluxDB
        self.influx_client = InfluxDBClient(
            url="http://localhost:8086",
            token="your-token",
            org="suoke-life"
        )
        self.write_api = self.influx_client.write_api(write_options=ASYNCHRONOUS)
        
        # 初始化MongoDB
        self.mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.mongo_db = self.mongo_client.health_data
        
        # 初始化Redis
        self.redis_pool = redis.ConnectionPool(
            host='localhost',
            port=6379,
            db=2,
            max_connections=50,
            decode_responses=True
        )
        
        # 初始化Kafka
        self.kafka_producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.kafka_producer.start()
        
        # 创建预聚合任务
        asyncio.create_task(self._aggregation_worker())
        
        logger.info("健康数据服务连接初始化完成")
    
    @trace(service_name="health-data-service", kind=SpanKind.SERVER)
    @rate_limit(name="write", tokens=1)
    async def write_data(self, data_points: List[HealthDataPoint]) -> Dict[str, Any]:
        """
        写入健康数据
        
        Args:
            data_points: 健康数据点列表
            
        Returns:
            Dict: 写入结果
        """
        start_time = time.time()
        self.stats['total_writes'] += len(data_points)
        
        try:
            # 批量写入优化
            influx_points = []
            mongo_docs = []
            cache_updates = []
            
            for dp in data_points:
                # 确定数据分片
                shard_id = self._get_shard_id(dp.user_id, dp.data_type)
                
                # 准备InfluxDB数据点
                point = Point(dp.data_type.value) \
                    .tag("user_id", dp.user_id) \
                    .tag("shard_id", str(shard_id)) \
                    .field("value", dp.value) \
                    .field("unit", dp.unit) \
                    .time(dp.timestamp)
                
                # 添加标签
                for tag_key, tag_value in dp.tags.items():
                    point.tag(tag_key, tag_value)
                
                # 添加元数据字段
                for meta_key, meta_value in dp.metadata.items():
                    point.field(meta_key, meta_value)
                
                influx_points.append(point)
                
                # 准备MongoDB文档（用于复杂查询）
                if dp.data_type in [DataType.MEDICAL_RECORDS, DataType.LAB_RESULTS]:
                    mongo_docs.append({
                        'user_id': dp.user_id,
                        'data_type': dp.data_type.value,
                        'timestamp': dp.timestamp,
                        'value': dp.value,
                        'unit': dp.unit,
                        'metadata': dp.metadata,
                        'tags': dp.tags,
                        'shard_id': shard_id,
                        'created_at': datetime.utcnow()
                    })
                
                # 准备缓存更新（最新数据）
                cache_updates.append((dp.user_id, dp.data_type, dp))
            
            # 并行写入不同存储
            write_tasks = []
            
            # 写入InfluxDB
            if influx_points:
                write_tasks.append(self._write_to_influx(influx_points))
            
            # 写入MongoDB
            if mongo_docs:
                write_tasks.append(self._write_to_mongo(mongo_docs))
            
            # 更新缓存
            if cache_updates:
                write_tasks.append(self._update_cache(cache_updates))
            
            # 发送到流处理
            write_tasks.append(self._send_to_stream(data_points))
            
            # 等待所有写入完成
            results = await asyncio.gather(*write_tasks, return_exceptions=True)
            
            # 检查错误
            errors = [r for r in results if isinstance(r, Exception)]
            if errors:
                logger.error(f"部分写入失败: {errors}")
            
            # 更新统计
            write_time = time.time() - start_time
            self._update_average_write_time(write_time)
            
            return {
                'success': len(errors) == 0,
                'written': len(data_points) - len(errors),
                'failed': len(errors),
                'write_time': write_time,
                'errors': [str(e) for e in errors]
            }
            
        except Exception as e:
            logger.error(f"写入健康数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @trace(operation_name="write_to_influx")
    async def _write_to_influx(self, points: List[Point]):
        """写入InfluxDB"""
        breaker = await get_circuit_breaker(
            f"{self.service_name}_influxdb",
            self.circuit_breaker_configs['influxdb']
        )
        
        async with breaker.protect():
            # InfluxDB异步写入
            self.write_api.write(bucket="health_data", points=points)
            await asyncio.sleep(0.01)  # 模拟写入延迟
    
    @trace(operation_name="write_to_mongo")
    async def _write_to_mongo(self, docs: List[Dict[str, Any]]):
        """写入MongoDB"""
        breaker = await get_circuit_breaker(
            f"{self.service_name}_mongodb",
            self.circuit_breaker_configs['mongodb']
        )
        
        async with breaker.protect():
            collection = self.mongo_db.health_records
            await collection.insert_many(docs)
    
    async def _update_cache(self, updates: List[Tuple[str, DataType, HealthDataPoint]]):
        """更新缓存"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            pipe = redis_conn.pipeline()
            
            for user_id, data_type, data_point in updates:
                # 缓存最新数据
                cache_key = f"health:latest:{user_id}:{data_type.value}"
                cache_value = json.dumps({
                    'value': data_point.value,
                    'unit': data_point.unit,
                    'timestamp': data_point.timestamp.isoformat(),
                    'metadata': data_point.metadata
                })
                pipe.set(cache_key, cache_value, ex=3600)  # 1小时过期
                
                # 更新用户活跃时间
                active_key = f"health:active:{user_id}"
                pipe.zadd(active_key, {data_type.value: time.time()})
                pipe.expire(active_key, 86400)  # 24小时过期
            
            await pipe.execute()
    
    async def _send_to_stream(self, data_points: List[HealthDataPoint]):
        """发送到流处理"""
        breaker = await get_circuit_breaker(
            f"{self.service_name}_kafka",
            self.circuit_breaker_configs['kafka']
        )
        
        async with breaker.protect():
            # 按数据类型分组发送到不同主题
            grouped = {}
            for dp in data_points:
                topic = f"health_data_{dp.data_type.value}"
                if topic not in grouped:
                    grouped[topic] = []
                
                grouped[topic].append({
                    'user_id': dp.user_id,
                    'timestamp': dp.timestamp.isoformat(),
                    'value': dp.value,
                    'unit': dp.unit,
                    'metadata': dp.metadata,
                    'tags': dp.tags
                })
            
            # 批量发送
            send_tasks = []
            for topic, messages in grouped.items():
                for msg in messages:
                    task = self.kafka_producer.send(topic, msg)
                    send_tasks.append(task)
            
            await asyncio.gather(*send_tasks)
            self.stats['stream_processed'] += len(data_points)
    
    @trace(service_name="health-data-service", kind=SpanKind.SERVER)
    @rate_limit(name="read", tokens=1)
    async def query_data(self, query: DataQuery) -> Dict[str, Any]:
        """
        查询健康数据
        
        Args:
            query: 数据查询请求
            
        Returns:
            Dict: 查询结果
        """
        start_time = time.time()
        self.stats['total_reads'] += 1
        
        try:
            # 检查缓存
            cache_key = self._generate_query_cache_key(query)
            cached_result = await self._get_from_cache(cache_key)
            
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result
            
            self.stats['cache_misses'] += 1
            
            # 并行查询不同数据类型
            query_tasks = []
            for data_type in query.data_types:
                if query.aggregation:
                    # 查询预聚合数据
                    task = self._query_aggregated_data(
                        query.user_id,
                        data_type,
                        query.start_time,
                        query.end_time,
                        query.aggregation,
                        query.interval
                    )
                else:
                    # 查询原始数据
                    task = self._query_raw_data(
                        query.user_id,
                        data_type,
                        query.start_time,
                        query.end_time,
                        query.filters
                    )
                query_tasks.append(task)
            
            # 等待所有查询完成
            results = await asyncio.gather(*query_tasks, return_exceptions=True)
            
            # 合并结果
            merged_result = {
                'user_id': query.user_id,
                'start_time': query.start_time.isoformat(),
                'end_time': query.end_time.isoformat(),
                'data': {}
            }
            
            for i, data_type in enumerate(query.data_types):
                if isinstance(results[i], Exception):
                    logger.error(f"查询{data_type.value}失败: {results[i]}")
                    merged_result['data'][data_type.value] = {'error': str(results[i])}
                else:
                    merged_result['data'][data_type.value] = results[i]
            
            # 缓存结果
            await self._cache_result(cache_key, merged_result, self.cache_config['query_cache_ttl'])
            
            # 更新统计
            read_time = time.time() - start_time
            self._update_average_read_time(read_time)
            merged_result['query_time'] = read_time
            
            return merged_result
            
        except Exception as e:
            logger.error(f"查询健康数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _query_raw_data(self, user_id: str, data_type: DataType, 
                             start_time: datetime, end_time: datetime,
                             filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查询原始数据"""
        # 使用InfluxDB查询时序数据
        query_api = self.influx_client.query_api()
        
        # 构建Flux查询
        flux_query = f'''
        from(bucket: "health_data")
            |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
            |> filter(fn: (r) => r["_measurement"] == "{data_type.value}")
            |> filter(fn: (r) => r["user_id"] == "{user_id}")
        '''
        
        # 添加额外过滤条件
        for key, value in filters.items():
            flux_query += f'|> filter(fn: (r) => r["{key}"] == "{value}")'
        
        flux_query += '|> sort(columns: ["_time"])'
        
        # 执行查询
        result = await asyncio.to_thread(query_api.query, flux_query)
        
        # 转换结果
        data_points = []
        for table in result:
            for record in table.records:
                data_points.append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value(),
                    'unit': record.values.get('unit', ''),
                    'metadata': {k: v for k, v in record.values.items() 
                               if k not in ['_time', '_value', 'user_id', 'unit']}
                })
        
        return data_points
    
    async def _query_aggregated_data(self, user_id: str, data_type: DataType,
                                   start_time: datetime, end_time: datetime,
                                   aggregation: AggregationType, interval: str) -> List[Dict[str, Any]]:
        """查询聚合数据"""
        # 先检查预聚合表
        cache_key = f"health:agg:{user_id}:{data_type.value}:{aggregation.value}:{interval}"
        cached = await self._get_from_cache(cache_key)
        
        if cached:
            # 过滤时间范围
            return [d for d in cached if start_time <= datetime.fromisoformat(d['timestamp']) <= end_time]
        
        # 构建聚合查询
        flux_query = f'''
        from(bucket: "health_data")
            |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
            |> filter(fn: (r) => r["_measurement"] == "{data_type.value}")
            |> filter(fn: (r) => r["user_id"] == "{user_id}")
            |> aggregateWindow(every: {interval}, fn: {aggregation.value})
            |> sort(columns: ["_time"])
        '''
        
        # 执行查询
        query_api = self.influx_client.query_api()
        result = await asyncio.to_thread(query_api.query, flux_query)
        
        # 转换结果
        aggregated_data = []
        for table in result:
            for record in table.records:
                aggregated_data.append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value(),
                    'aggregation': aggregation.value,
                    'interval': interval
                })
        
        # 缓存聚合结果
        await self._cache_result(cache_key, aggregated_data, self.cache_config['aggregation_cache_ttl'])
        self.stats['aggregations_computed'] += 1
        
        return aggregated_data
    
    async def create_stream_processor(self, config: StreamConfig) -> AsyncIterator[Dict[str, Any]]:
        """
        创建流处理器
        
        Args:
            config: 流处理配置
            
        Yields:
            Dict: 处理后的数据
        """
        consumer = aiokafka.AIOKafkaConsumer(
            config.topic,
            bootstrap_servers='localhost:9092',
            group_id=config.group_id,
            value_deserializer=lambda v: json.loads(v.decode())
        )
        
        await consumer.start()
        self.kafka_consumers[config.topic] = consumer
        self.stats['active_streams'] += 1
        
        try:
            batch = []
            last_batch_time = time.time()
            
            async for message in consumer:
                batch.append(message.value)
                
                # 批处理逻辑
                if len(batch) >= config.batch_size or \
                   time.time() - last_batch_time >= config.batch_timeout:
                    
                    # 处理批次数据
                    processed_batch = await self._process_stream_batch(batch)
                    
                    for item in processed_batch:
                        yield item
                    
                    batch = []
                    last_batch_time = time.time()
                    
        finally:
            await consumer.stop()
            del self.kafka_consumers[config.topic]
            self.stats['active_streams'] -= 1
    
    async def _process_stream_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理流数据批次"""
        # 实时异常检测
        processed = []
        
        for item in batch:
            # 简单的异常检测示例
            if item.get('data_type') == 'vital_signs':
                value = item.get('value', 0)
                
                # 心率异常检测
                if 'heart_rate' in item.get('metadata', {}):
                    if value < 40 or value > 120:
                        item['alert'] = {
                            'type': 'abnormal_heart_rate',
                            'severity': 'high' if value < 30 or value > 150 else 'medium',
                            'message': f"异常心率: {value} bpm"
                        }
                
                # 血压异常检测
                elif 'blood_pressure' in item.get('metadata', {}):
                    systolic = item.get('metadata', {}).get('systolic', 0)
                    diastolic = item.get('metadata', {}).get('diastolic', 0)
                    
                    if systolic > 140 or diastolic > 90:
                        item['alert'] = {
                            'type': 'high_blood_pressure',
                            'severity': 'high' if systolic > 180 or diastolic > 120 else 'medium',
                            'message': f"高血压: {systolic}/{diastolic} mmHg"
                        }
            
            processed.append(item)
        
        return processed
    
    async def export_data(self, user_id: str, data_types: List[DataType],
                         start_time: datetime, end_time: datetime,
                         format: str = 'csv') -> str:
        """
        导出健康数据
        
        Args:
            user_id: 用户ID
            data_types: 数据类型列表
            start_time: 开始时间
            end_time: 结束时间
            format: 导出格式（csv, json, parquet）
            
        Returns:
            str: 导出文件路径
        """
        # 限流检查
        limiter = await get_rate_limiter(
            f"{self.service_name}_export_{user_id}",
            config=self.rate_limit_configs['export']
        )
        
        if not await limiter.try_acquire():
            raise Exception("导出请求过于频繁，请稍后再试")
        
        # 查询数据
        query = DataQuery(
            user_id=user_id,
            data_types=data_types,
            start_time=start_time,
            end_time=end_time
        )
        
        result = await self.query_data(query)
        
        # 转换为DataFrame
        all_data = []
        for data_type, data_points in result['data'].items():
            if isinstance(data_points, list):
                for point in data_points:
                    all_data.append({
                        'data_type': data_type,
                        'timestamp': point['timestamp'],
                        'value': point['value'],
                        'unit': point.get('unit', ''),
                        **point.get('metadata', {})
                    })
        
        df = pd.DataFrame(all_data)
        
        # 导出文件
        export_path = f"/tmp/health_data_{user_id}_{int(time.time())}.{format}"
        
        if format == 'csv':
            df.to_csv(export_path, index=False)
        elif format == 'json':
            df.to_json(export_path, orient='records', date_format='iso')
        elif format == 'parquet':
            df.to_parquet(export_path, index=False)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
        
        return export_path
    
    async def _aggregation_worker(self):
        """预聚合工作线程"""
        while True:
            try:
                # 每5分钟执行一次预聚合
                await asyncio.sleep(300)
                
                # 获取需要聚合的用户列表
                redis_conn = await self._get_redis_connection()
                active_users = await redis_conn.keys("health:active:*")
                
                for user_key in active_users:
                    user_id = user_key.split(":")[-1]
                    
                    # 对每个活跃用户的数据进行预聚合
                    for data_type in self.aggregation_config['enabled_types']:
                        await self._compute_aggregations(user_id, data_type)
                
            except Exception as e:
                logger.error(f"预聚合失败: {e}")
                await asyncio.sleep(60)  # 错误后等待1分钟
    
    async def _compute_aggregations(self, user_id: str, data_type: DataType):
        """计算预聚合数据"""
        now = datetime.utcnow()
        
        for interval in self.aggregation_config['intervals']:
            # 确定聚合时间范围
            if interval == '1m':
                start_time = now - timedelta(minutes=60)
            elif interval == '5m':
                start_time = now - timedelta(hours=6)
            elif interval == '1h':
                start_time = now - timedelta(days=7)
            elif interval == '1d':
                start_time = now - timedelta(days=90)
            else:
                continue
            
            # 计算各种聚合指标
            for metric in self.aggregation_config['metrics']:
                try:
                    aggregation_type = AggregationType(metric)
                    result = await self._query_aggregated_data(
                        user_id, data_type, start_time, now,
                        aggregation_type, interval
                    )
                    
                    # 结果已经被缓存
                    logger.debug(f"预聚合完成: {user_id}/{data_type.value}/{metric}/{interval}")
                    
                except Exception as e:
                    logger.error(f"预聚合失败: {e}")
    
    def _get_shard_id(self, user_id: str, data_type: DataType) -> int:
        """获取数据分片ID"""
        # 基于用户ID和数据类型的哈希分片
        shard_key = f"{user_id}:{data_type.value}"
        hash_value = int(hashlib.md5(shard_key.encode()).hexdigest(), 16)
        return hash_value % self.shard_config['shard_count']
    
    def _generate_query_cache_key(self, query: DataQuery) -> str:
        """生成查询缓存键"""
        key_parts = [
            query.user_id,
            ','.join([dt.value for dt in query.data_types]),
            query.start_time.isoformat(),
            query.end_time.isoformat(),
            query.aggregation.value if query.aggregation else 'raw',
            query.interval or 'none',
            json.dumps(query.filters, sort_keys=True)
        ]
        key_string = '|'.join(key_parts)
        return f"health:query:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def _get_redis_connection(self) -> redis.Redis:
        """获取Redis连接"""
        return redis.Redis(connection_pool=self.redis_pool)
    
    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            cached = await redis_conn.get(key)
            if cached:
                return json.loads(cached)
        return None
    
    async def _cache_result(self, key: str, data: Any, ttl: int):
        """缓存结果"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            await redis_conn.set(key, json.dumps(data), ex=ttl)
    
    def _update_average_write_time(self, write_time: float):
        """更新平均写入时间"""
        total_writes = self.stats['total_writes']
        if total_writes <= len(self.stats):  # 避免除零
            self.stats['average_write_time'] = write_time
        else:
            current_avg = self.stats['average_write_time']
            self.stats['average_write_time'] = (
                (current_avg * (total_writes - 1) + write_time) / total_writes
            )
    
    def _update_average_read_time(self, read_time: float):
        """更新平均读取时间"""
        total_reads = self.stats['total_reads']
        if total_reads == 1:
            self.stats['average_read_time'] = read_time
        else:
            current_avg = self.stats['average_read_time']
            self.stats['average_read_time'] = (
                (current_avg * (total_reads - 1) + read_time) / total_reads
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'stats': self.stats,
            'connections': {
                'influxdb': self.influx_client is not None,
                'mongodb': self.mongo_client is not None,
                'redis': self.redis_pool is not None,
                'kafka': self.kafka_producer is not None
            },
            'sharding': self.shard_config,
            'aggregation': {
                'enabled': True,
                'intervals': self.aggregation_config['intervals'],
                'types': [dt.value for dt in self.aggregation_config['enabled_types']]
            },
            'uptime': time.time()
        }
    
    async def cleanup(self):
        """清理资源"""
        # 关闭InfluxDB连接
        if self.influx_client:
            self.influx_client.close()
        
        # 关闭MongoDB连接
        if self.mongo_client:
            self.mongo_client.close()
        
        # 关闭Redis连接池
        if self.redis_pool:
            await self.redis_pool.disconnect()
        
        # 关闭Kafka生产者
        if self.kafka_producer:
            await self.kafka_producer.stop()
        
        # 关闭所有Kafka消费者
        for consumer in self.kafka_consumers.values():
            await consumer.stop()
        
        logger.info("健康数据服务清理完成")

# 全局服务实例
_health_data_service = None

async def get_health_data_service() -> EnhancedHealthDataService:
    """获取健康数据服务实例"""
    global _health_data_service
    if _health_data_service is None:
        _health_data_service = EnhancedHealthDataService()
        await _health_data_service.initialize()
    return _health_data_service 