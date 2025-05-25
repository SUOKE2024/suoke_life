#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康数据服务增强版API网关
提供RESTful API接口，支持健康数据的写入、查询、流处理和导出
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# 导入服务
from services.health_data_service.internal.service.enhanced_health_data_service import (
    get_health_data_service, HealthDataPoint, DataQuery, StreamConfig,
    DataType, AggregationType
)

# 导入通用组件
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="健康数据服务API",
    description="索克生活健康数据管理服务，提供时序数据存储、查询、分析和导出功能",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class HealthDataPointRequest(BaseModel):
    """健康数据点请求"""
    user_id: str = Field(..., description="用户ID")
    data_type: str = Field(..., description="数据类型")
    value: float = Field(..., description="数值")
    unit: str = Field(..., description="单位")
    timestamp: Optional[datetime] = Field(None, description="时间戳，不提供则使用当前时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    tags: Dict[str, str] = Field(default_factory=dict, description="标签")

class BatchWriteRequest(BaseModel):
    """批量写入请求"""
    data_points: List[HealthDataPointRequest] = Field(..., description="数据点列表")

class QueryRequest(BaseModel):
    """查询请求"""
    user_id: str = Field(..., description="用户ID")
    data_types: List[str] = Field(..., description="数据类型列表")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    aggregation: Optional[str] = Field(None, description="聚合类型")
    interval: Optional[str] = Field(None, description="聚合间隔")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")

class StreamRequest(BaseModel):
    """流处理请求"""
    topic: str = Field(..., description="Kafka主题")
    group_id: str = Field(..., description="消费者组ID")
    batch_size: int = Field(100, description="批处理大小")
    batch_timeout: float = Field(1.0, description="批处理超时时间")

class ExportRequest(BaseModel):
    """导出请求"""
    user_id: str = Field(..., description="用户ID")
    data_types: List[str] = Field(..., description="数据类型列表")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    format: str = Field("csv", description="导出格式：csv, json, parquet")

# 响应模型
class WriteResponse(BaseModel):
    """写入响应"""
    success: bool
    written: Optional[int] = None
    failed: Optional[int] = None
    write_time: Optional[float] = None
    errors: Optional[List[str]] = None
    error: Optional[str] = None

class QueryResponse(BaseModel):
    """查询响应"""
    user_id: str
    start_time: str
    end_time: str
    data: Dict[str, Any]
    query_time: Optional[float] = None
    error: Optional[str] = None

class HealthStatus(BaseModel):
    """健康状态"""
    service: str
    status: str
    stats: Dict[str, Any]
    connections: Dict[str, bool]
    sharding: Dict[str, Any]
    aggregation: Dict[str, Any]
    uptime: float

# 中间件
@app.middleware("http")
async def add_tracing(request, call_next):
    """添加分布式追踪"""
    tracer = get_tracer("health-data-api")
    
    with tracer.start_span(
        f"{request.method} {request.url.path}",
        kind=SpanKind.SERVER
    ) as span:
        # 添加请求信息到span
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.scheme", request.url.scheme)
        span.set_attribute("http.host", request.url.hostname)
        span.set_attribute("http.target", request.url.path)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加响应信息到span
        span.set_attribute("http.status_code", response.status_code)
        
        return response

@app.middleware("http")
async def add_monitoring(request, call_next):
    """添加监控指标"""
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    # 记录请求处理时间
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # TODO: 发送指标到Prometheus
    
    return response

# API端点
@app.post("/api/v1/health/data", response_model=WriteResponse)
async def write_health_data(request: HealthDataPointRequest):
    """
    写入单个健康数据点
    
    - **user_id**: 用户ID
    - **data_type**: 数据类型（vital_signs, activity, sleep等）
    - **value**: 数值
    - **unit**: 单位
    - **timestamp**: 时间戳（可选）
    - **metadata**: 元数据（可选）
    - **tags**: 标签（可选）
    """
    try:
        service = await get_health_data_service()
        
        # 转换数据类型
        try:
            data_type_enum = DataType(request.data_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的数据类型: {request.data_type}")
        
        # 创建数据点
        data_point = HealthDataPoint(
            user_id=request.user_id,
            data_type=data_type_enum,
            timestamp=request.timestamp or datetime.utcnow(),
            value=request.value,
            unit=request.unit,
            metadata=request.metadata,
            tags=request.tags
        )
        
        # 写入数据
        result = await service.write_data([data_point])
        
        return WriteResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"写入健康数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/health/data/batch", response_model=WriteResponse)
async def batch_write_health_data(request: BatchWriteRequest):
    """
    批量写入健康数据
    
    支持一次写入多个数据点，提高写入效率
    """
    try:
        service = await get_health_data_service()
        
        # 转换数据点
        data_points = []
        for dp_request in request.data_points:
            try:
                data_type_enum = DataType(dp_request.data_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的数据类型: {dp_request.data_type}")
            
            data_point = HealthDataPoint(
                user_id=dp_request.user_id,
                data_type=data_type_enum,
                timestamp=dp_request.timestamp or datetime.utcnow(),
                value=dp_request.value,
                unit=dp_request.unit,
                metadata=dp_request.metadata,
                tags=dp_request.tags
            )
            data_points.append(data_point)
        
        # 批量写入
        result = await service.write_data(data_points)
        
        return WriteResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量写入健康数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/health/data/query", response_model=QueryResponse)
async def query_health_data(request: QueryRequest):
    """
    查询健康数据
    
    支持原始数据查询和聚合查询，可以指定时间范围、数据类型和过滤条件
    """
    try:
        service = await get_health_data_service()
        
        # 转换数据类型
        data_types = []
        for dt in request.data_types:
            try:
                data_types.append(DataType(dt))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的数据类型: {dt}")
        
        # 转换聚合类型
        aggregation = None
        if request.aggregation:
            try:
                aggregation = AggregationType(request.aggregation)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的聚合类型: {request.aggregation}")
        
        # 创建查询对象
        query = DataQuery(
            user_id=request.user_id,
            data_types=data_types,
            start_time=request.start_time,
            end_time=request.end_time,
            aggregation=aggregation,
            interval=request.interval,
            filters=request.filters
        )
        
        # 执行查询
        result = await service.query_data(query)
        
        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询健康数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health/data/latest/{user_id}/{data_type}")
async def get_latest_data(user_id: str, data_type: str):
    """
    获取最新的健康数据
    
    快速获取指定用户和数据类型的最新数据点
    """
    try:
        service = await get_health_data_service()
        
        # 验证数据类型
        try:
            data_type_enum = DataType(data_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的数据类型: {data_type}")
        
        # 查询最近1小时的数据
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        query = DataQuery(
            user_id=user_id,
            data_types=[data_type_enum],
            start_time=start_time,
            end_time=end_time
        )
        
        result = await service.query_data(query)
        
        # 获取最新的数据点
        data_points = result.get('data', {}).get(data_type, [])
        if data_points and isinstance(data_points, list):
            return data_points[-1]  # 返回最新的
        
        raise HTTPException(status_code=404, detail="未找到数据")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/health/data/stream")
async def create_stream(request: StreamRequest):
    """
    创建数据流处理
    
    创建一个实时数据流，用于处理和分析流式健康数据
    """
    try:
        service = await get_health_data_service()
        
        # 创建流配置
        config = StreamConfig(
            topic=request.topic,
            group_id=request.group_id,
            batch_size=request.batch_size,
            batch_timeout=request.batch_timeout
        )
        
        # 创建流处理器
        async def stream_generator():
            async for item in service.create_stream_processor(config):
                yield f"data: {json.dumps(item)}\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"创建数据流失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/health/data/export")
async def export_data(request: ExportRequest, background_tasks: BackgroundTasks):
    """
    导出健康数据
    
    将指定时间范围的健康数据导出为文件（CSV、JSON或Parquet格式）
    """
    try:
        service = await get_health_data_service()
        
        # 转换数据类型
        data_types = []
        for dt in request.data_types:
            try:
                data_types.append(DataType(dt))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的数据类型: {dt}")
        
        # 执行导出
        file_path = await service.export_data(
            user_id=request.user_id,
            data_types=data_types,
            start_time=request.start_time,
            end_time=request.end_time,
            format=request.format
        )
        
        # 添加后台任务：30分钟后删除文件
        async def cleanup_file():
            await asyncio.sleep(1800)  # 30分钟
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
        
        background_tasks.add_task(cleanup_file)
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=f"health_data_{request.user_id}.{request.format}",
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health/data/aggregations/{user_id}")
async def get_aggregations(
    user_id: str,
    data_type: str = Query(..., description="数据类型"),
    aggregation: str = Query("mean", description="聚合类型"),
    interval: str = Query("1h", description="聚合间隔"),
    days: int = Query(7, description="查询天数")
):
    """
    获取预聚合数据
    
    快速获取预计算的聚合数据，支持多种聚合类型和时间间隔
    """
    try:
        service = await get_health_data_service()
        
        # 验证参数
        try:
            data_type_enum = DataType(data_type)
            aggregation_enum = AggregationType(aggregation)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # 计算时间范围
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # 创建查询
        query = DataQuery(
            user_id=user_id,
            data_types=[data_type_enum],
            start_time=start_time,
            end_time=end_time,
            aggregation=aggregation_enum,
            interval=interval
        )
        
        # 执行查询
        result = await service.query_data(query)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取聚合数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health/status", response_model=HealthStatus)
async def get_health_status():
    """
    获取服务健康状态
    
    返回服务的运行状态、统计信息和连接状态
    """
    try:
        service = await get_health_data_service()
        status = service.get_health_status()
        return HealthStatus(**status)
    except Exception as e:
        logger.error(f"获取健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health/metrics")
async def get_metrics():
    """
    获取Prometheus格式的指标
    
    用于监控系统集成
    """
    try:
        service = await get_health_data_service()
        stats = service.stats
        
        # 构建Prometheus格式的指标
        metrics = []
        
        # 计数器指标
        metrics.append(f'# HELP health_data_total_writes Total number of write operations')
        metrics.append(f'# TYPE health_data_total_writes counter')
        metrics.append(f'health_data_total_writes {stats["total_writes"]}')
        
        metrics.append(f'# HELP health_data_total_reads Total number of read operations')
        metrics.append(f'# TYPE health_data_total_reads counter')
        metrics.append(f'health_data_total_reads {stats["total_reads"]}')
        
        metrics.append(f'# HELP health_data_cache_hits Total number of cache hits')
        metrics.append(f'# TYPE health_data_cache_hits counter')
        metrics.append(f'health_data_cache_hits {stats["cache_hits"]}')
        
        metrics.append(f'# HELP health_data_cache_misses Total number of cache misses')
        metrics.append(f'# TYPE health_data_cache_misses counter')
        metrics.append(f'health_data_cache_misses {stats["cache_misses"]}')
        
        # 直方图指标
        metrics.append(f'# HELP health_data_write_duration_seconds Write operation duration')
        metrics.append(f'# TYPE health_data_write_duration_seconds histogram')
        metrics.append(f'health_data_write_duration_seconds_sum {stats["average_write_time"] * stats["total_writes"]}')
        metrics.append(f'health_data_write_duration_seconds_count {stats["total_writes"]}')
        
        metrics.append(f'# HELP health_data_read_duration_seconds Read operation duration')
        metrics.append(f'# TYPE health_data_read_duration_seconds histogram')
        metrics.append(f'health_data_read_duration_seconds_sum {stats["average_read_time"] * stats["total_reads"]}')
        metrics.append(f'health_data_read_duration_seconds_count {stats["total_reads"]}')
        
        # 仪表盘指标
        metrics.append(f'# HELP health_data_active_streams Number of active data streams')
        metrics.append(f'# TYPE health_data_active_streams gauge')
        metrics.append(f'health_data_active_streams {stats["active_streams"]}')
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查端点
@app.get("/health")
async def health_check():
    """基本健康检查"""
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    """就绪检查"""
    try:
        service = await get_health_data_service()
        status = service.get_health_status()
        
        # 检查所有连接是否正常
        connections = status.get('connections', {})
        if not all(connections.values()):
            raise HTTPException(status_code=503, detail="服务未就绪")
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        raise HTTPException(status_code=503, detail=str(e))

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("健康数据服务API启动中...")
    
    # 初始化服务
    try:
        service = await get_health_data_service()
        logger.info("健康数据服务初始化成功")
    except Exception as e:
        logger.error(f"健康数据服务初始化失败: {e}")
        raise

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("健康数据服务API关闭中...")
    
    # 清理资源
    try:
        service = await get_health_data_service()
        await service.cleanup()
        logger.info("健康数据服务清理完成")
    except Exception as e:
        logger.error(f"健康数据服务清理失败: {e}")

# 主函数
if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api_gateway:app",
        host="0.0.0.0",
        port=8082,
        reload=True,
        log_level="info"
    ) 