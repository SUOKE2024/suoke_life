"""
数据库API接口
提供数据库操作的RESTful API服务
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..unified_health_data_service.health_data_service.core.database import DatabaseService

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/database", tags=["数据库"])

# 依赖注入
async def get_database_service() -> DatabaseService:
    """获取数据库服务实例"""
    service = DatabaseService()
    if not service.connected:
        await service.initialize()
    return service

# 请求模型
class DatabaseQuery(BaseModel):
    """数据库查询请求"""
    table: str = Field(..., description="表名")
    conditions: Optional[Dict[str, Any]] = Field(None, description="查询条件")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="限制数量")
    offset: Optional[int] = Field(0, ge=0, description="偏移量")

class DatabaseInsert(BaseModel):
    """数据库插入请求"""
    table: str = Field(..., description="表名")
    data: Dict[str, Any] = Field(..., description="插入数据")

class DatabaseUpdate(BaseModel):
    """数据库更新请求"""
    table: str = Field(..., description="表名")
    data: Dict[str, Any] = Field(..., description="更新数据")
    conditions: Dict[str, Any] = Field(..., description="更新条件")

class DatabaseDelete(BaseModel):
    """数据库删除请求"""
    table: str = Field(..., description="表名")
    conditions: Dict[str, Any] = Field(..., description="删除条件")

class MongoQuery(BaseModel):
    """MongoDB查询请求"""
    collection: str = Field(..., description="集合名")
    filter_dict: Optional[Dict[str, Any]] = Field(None, description="查询过滤器")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="限制数量")
    skip: Optional[int] = Field(0, ge=0, description="跳过数量")

class MongoInsert(BaseModel):
    """MongoDB插入请求"""
    collection: str = Field(..., description="集合名")
    document: Dict[str, Any] = Field(..., description="插入文档")

class CacheOperation(BaseModel):
    """缓存操作请求"""
    key: str = Field(..., description="缓存键")
    value: Optional[Any] = Field(None, description="缓存值")
    expire: Optional[int] = Field(None, description="过期时间（秒）")

# 响应模型
class APIResponse(BaseModel):
    """API响应基础模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")

# PostgreSQL 数据库接口
@router.post("/postgresql/query", response_model=APIResponse)
async def query_postgresql(
    query_request: DatabaseQuery,
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """查询PostgreSQL数据"""
    try:
        results = await service.query_data(
            table=query_request.table,
            conditions=query_request.conditions,
            limit=query_request.limit,
            offset=query_request.offset
        )
        
        return APIResponse(
            success=True,
            message="查询成功",
            data={
                "results": results,
                "count": len(results)
            }
        )
        
    except Exception as e:
        logger.error(f"PostgreSQL查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/postgresql/insert", response_model=APIResponse)
async def insert_postgresql(
    insert_request: DatabaseInsert,
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """插入PostgreSQL数据"""
    try:
        result_id = await service.store_data(
            table=insert_request.table,
            data=insert_request.data
        )
        
        return APIResponse(
            success=True,
            message="插入成功",
            data={"id": result_id}
        )
        
    except Exception as e:
        logger.error(f"PostgreSQL插入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/postgresql/update", response_model=APIResponse)
async def update_postgresql(
    update_request: DatabaseUpdate,
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """更新PostgreSQL数据"""
    try:
        affected_rows = await service.update_data(
            table=update_request.table,
            data=update_request.data,
            conditions=update_request.conditions
        )
        
        return APIResponse(
            success=True,
            message="更新成功",
            data={"affected_rows": affected_rows}
        )
        
    except Exception as e:
        logger.error(f"PostgreSQL更新失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/postgresql/delete", response_model=APIResponse)
async def delete_postgresql(
    delete_request: DatabaseDelete,
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """删除PostgreSQL数据"""
    try:
        affected_rows = await service.delete_data(
            table=delete_request.table,
            conditions=delete_request.conditions
        )
        
        return APIResponse(
            success=True,
            message="删除成功",
            data={"affected_rows": affected_rows}
        )
        
    except Exception as e:
        logger.error(f"PostgreSQL删除失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MongoDB 接口
@router.post("/mongodb/query", response_model=APIResponse)
async def query_mongodb(
    query_request: MongoQuery,
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """查询MongoDB数据"""
    try:
        results = await service.mongo_find(
            collection=query_request.collection,
            filter_dict=query_request.filter_dict,
            limit=query_request.limit,
            skip=query_request.skip
        )
        
        return APIResponse(
            success=True,
            message="查询成功",
            data={
                "results": results,
                "count": len(results)
            }
        )
        
    except Exception as e:
        logger.error(f"MongoDB查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mongodb/insert", response_model=APIResponse)
async def insert_mongodb(
    insert_request: MongoInsert,
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """插入MongoDB数据"""
    try:
        result_id = await service.mongo_insert(
            collection=insert_request.collection,
            document=insert_request.document
        )
        
        return APIResponse(
            success=True,
            message="插入成功",
            data={"id": str(result_id)}
        )
        
    except Exception as e:
        logger.error(f"MongoDB插入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mongodb/update", response_model=APIResponse)
async def update_mongodb(
    collection: str = Query(..., description="集合名"),
    filter_dict: Dict[str, Any] = Body(..., description="查询过滤器"),
    update_dict: Dict[str, Any] = Body(..., description="更新数据"),
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """更新MongoDB数据"""
    try:
        result = await service.mongo_update(
            collection=collection,
            filter_dict=filter_dict,
            update_dict=update_dict
        )
        
        return APIResponse(
            success=True,
            message="更新成功",
            data={"modified_count": result.modified_count}
        )
        
    except Exception as e:
        logger.error(f"MongoDB更新失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/mongodb/delete", response_model=APIResponse)
async def delete_mongodb(
    collection: str = Query(..., description="集合名"),
    filter_dict: Dict[str, Any] = Body(..., description="删除过滤器"),
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """删除MongoDB数据"""
    try:
        result = await service.mongo_delete(
            collection=collection,
            filter_dict=filter_dict
        )
        
        return APIResponse(
            success=True,
            message="删除成功",
            data={"deleted_count": result.deleted_count}
        )
        
    except Exception as e:
        logger.error(f"MongoDB删除失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Redis 缓存接口
@router.get("/redis/get", response_model=APIResponse)
async def get_cache(
    key: str = Query(..., description="缓存键"),
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """获取缓存数据"""
    try:
        value = await service.cache_get(key)
        
        return APIResponse(
            success=True,
            message="获取成功",
            data={"key": key, "value": value}
        )
        
    except Exception as e:
        logger.error(f"获取缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/redis/set", response_model=APIResponse)
async def set_cache(
    cache_request: CacheOperation,
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """设置缓存数据"""
    try:
        await service.cache_set(
            key=cache_request.key,
            value=cache_request.value,
            expire=cache_request.expire
        )
        
        return APIResponse(
            success=True,
            message="设置成功",
            data={"key": cache_request.key}
        )
        
    except Exception as e:
        logger.error(f"设置缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/redis/delete", response_model=APIResponse)
async def delete_cache(
    key: str = Query(..., description="缓存键"),
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """删除缓存数据"""
    try:
        await service.cache_delete(key)
        
        return APIResponse(
            success=True,
            message="删除成功",
            data={"key": key}
        )
        
    except Exception as e:
        logger.error(f"删除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 事务管理接口
@router.post("/transaction/begin", response_model=APIResponse)
async def begin_transaction(
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """开始事务"""
    try:
        transaction_id = await service.begin_transaction()
        
        return APIResponse(
            success=True,
            message="事务开始成功",
            data={"transaction_id": transaction_id}
        )
        
    except Exception as e:
        logger.error(f"开始事务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction/commit", response_model=APIResponse)
async def commit_transaction(
    transaction_id: str = Body(..., description="事务ID"),
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """提交事务"""
    try:
        await service.commit_transaction(transaction_id)
        
        return APIResponse(
            success=True,
            message="事务提交成功",
            data={"transaction_id": transaction_id}
        )
        
    except Exception as e:
        logger.error(f"提交事务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction/rollback", response_model=APIResponse)
async def rollback_transaction(
    transaction_id: str = Body(..., description="事务ID"),
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """回滚事务"""
    try:
        await service.rollback_transaction(transaction_id)
        
        return APIResponse(
            success=True,
            message="事务回滚成功",
            data={"transaction_id": transaction_id}
        )
        
    except Exception as e:
        logger.error(f"回滚事务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 数据库状态和监控接口
@router.get("/status", response_model=APIResponse)
async def get_database_status(
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """获取数据库状态"""
    try:
        status = await service.get_status()
        
        return APIResponse(
            success=True,
            message="状态获取成功",
            data=status
        )
        
    except Exception as e:
        logger.error(f"获取数据库状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=APIResponse)
async def database_health_check(
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """数据库健康检查"""
    try:
        health_status = await service.health_check()
        
        return APIResponse(
            success=True,
            message="健康检查完成",
            data=health_status
        )
        
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=APIResponse)
async def get_database_metrics(
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """获取数据库指标"""
    try:
        metrics = await service.get_metrics()
        
        return APIResponse(
            success=True,
            message="指标获取成功",
            data=metrics
        )
        
    except Exception as e:
        logger.error(f"获取数据库指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 数据迁移接口
@router.post("/migration/run", response_model=APIResponse)
async def run_migration(
    migration_name: str = Body(..., description="迁移名称"),
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """运行数据迁移"""
    try:
        result = await service.run_migration(migration_name)
        
        return APIResponse(
            success=True,
            message="迁移运行成功",
            data=result
        )
        
    except Exception as e:
        logger.error(f"运行数据迁移失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migration/status", response_model=APIResponse)
async def get_migration_status(
    service: DatabaseService = Depends(get_database_service)
) -> APIResponse:
    """获取迁移状态"""
    try:
        status = await service.get_migration_status()
        
        return APIResponse(
            success=True,
            message="迁移状态获取成功",
            data=status
        )
        
    except Exception as e:
        logger.error(f"获取迁移状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 