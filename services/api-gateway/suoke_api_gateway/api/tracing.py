#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分布式追踪 API 端点

提供追踪查询和管理功能。
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..services.tracing import get_tracing_service, TracingService, SpanData
from ..core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tracing", tags=["tracing"])


class TraceSearchRequest(BaseModel):
    """追踪搜索请求"""
    service_name: Optional[str] = Field(None, description="服务名称")
    operation_name: Optional[str] = Field(None, description="操作名称")
    tags: Optional[Dict[str, Any]] = Field(None, description="标签过滤")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    limit: int = Field(100, ge=1, le=1000, description="结果数量限制")


class SpanResponse(BaseModel):
    """Span 响应"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    status: str
    kind: str


class TraceResponse(BaseModel):
    """Trace 响应"""
    trace_id: str
    spans: List[SpanResponse]
    total_spans: int
    duration: Optional[float]
    root_span: Optional[SpanResponse]


@router.get("/health")
async def tracing_health(
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    获取追踪服务健康状态
    
    Returns:
        健康状态信息
    """
    try:
        stats = tracing_service.get_stats()
        
        return {
            "status": "healthy" if tracing_service.enabled else "disabled",
            "enabled": tracing_service.enabled,
            "service_name": tracing_service.service_name,
            "jaeger_endpoint": tracing_service.jaeger_endpoint,
            "stats": stats,
        }
    
    except Exception as e:
        logger.error("Failed to get tracing health", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def tracing_stats(
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    获取追踪统计信息
    
    Returns:
        统计信息
    """
    try:
        stats = tracing_service.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
        }
    
    except Exception as e:
        logger.error("Failed to get tracing stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces")
async def search_traces(
    service_name: Optional[str] = Query(None, description="服务名称"),
    operation_name: Optional[str] = Query(None, description="操作名称"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000, description="结果数量限制"),
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    搜索追踪记录
    
    Args:
        service_name: 服务名称过滤
        operation_name: 操作名称过滤
        start_time: 开始时间过滤
        end_time: 结束时间过滤
        limit: 结果数量限制
    
    Returns:
        搜索结果
    """
    try:
        # 转换时间戳
        start_timestamp = start_time.timestamp() if start_time else None
        end_timestamp = end_time.timestamp() if end_time else None
        
        # 搜索 spans
        spans = tracing_service.search_traces(
            service_name=service_name,
            operation_name=operation_name,
            start_time=start_timestamp,
            end_time=end_timestamp,
            limit=limit,
        )
        
        # 转换为响应格式
        span_responses = []
        for span in spans:
            span_responses.append(SpanResponse(
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                operation_name=span.operation_name,
                start_time=span.start_time,
                end_time=span.end_time,
                duration=span.duration,
                tags=span.tags,
                logs=span.logs,
                status=span.status,
                kind=span.kind,
            ))
        
        return {
            "status": "success",
            "spans": [span.dict() for span in span_responses],
            "total": len(span_responses),
            "limit": limit,
        }
    
    except Exception as e:
        logger.error("Failed to search traces", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/{trace_id}")
async def get_trace(
    trace_id: str,
    tracing_service: TracingService = Depends(get_tracing_service),
) -> TraceResponse:
    """
    获取完整的追踪记录
    
    Args:
        trace_id: 追踪ID
    
    Returns:
        完整的追踪记录
    """
    try:
        spans = tracing_service.get_trace(trace_id)
        if not spans:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        # 转换为响应格式
        span_responses = []
        root_span = None
        total_duration = 0
        
        for span in spans:
            span_response = SpanResponse(
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                operation_name=span.operation_name,
                start_time=span.start_time,
                end_time=span.end_time,
                duration=span.duration,
                tags=span.tags,
                logs=span.logs,
                status=span.status,
                kind=span.kind,
            )
            span_responses.append(span_response)
            
            # 找到根 span
            if not span.parent_span_id:
                root_span = span_response
            
            # 计算总持续时间
            if span.duration:
                total_duration = max(total_duration, span.duration)
        
        return TraceResponse(
            trace_id=trace_id,
            spans=span_responses,
            total_spans=len(span_responses),
            duration=total_duration if total_duration > 0 else None,
            root_span=root_span,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get trace", trace_id=trace_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spans/{span_id}")
async def get_span(
    span_id: str,
    tracing_service: TracingService = Depends(get_tracing_service),
) -> SpanResponse:
    """
    获取单个 Span 详情
    
    Args:
        span_id: Span ID
    
    Returns:
        Span 详情
    """
    try:
        span = tracing_service.get_span(span_id)
        if not span:
            raise HTTPException(status_code=404, detail="Span not found")
        
        return SpanResponse(
            trace_id=span.trace_id,
            span_id=span.span_id,
            parent_span_id=span.parent_span_id,
            operation_name=span.operation_name,
            start_time=span.start_time,
            end_time=span.end_time,
            duration=span.duration,
            tags=span.tags,
            logs=span.logs,
            status=span.status,
            kind=span.kind,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get span", span_id=span_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations")
async def list_operations(
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    列出所有操作名称
    
    Returns:
        操作名称列表
    """
    try:
        stats = tracing_service.get_stats()
        operations = stats.get("operations", {})
        
        # 按调用次数排序
        sorted_operations = sorted(
            operations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "status": "success",
            "operations": [
                {
                    "name": name,
                    "count": count,
                }
                for name, count in sorted_operations
            ],
            "total": len(operations),
        }
    
    except Exception as e:
        logger.error("Failed to list operations", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services")
async def list_services(
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    列出所有服务
    
    Returns:
        服务列表
    """
    try:
        # 目前只有当前服务
        services = [
            {
                "name": tracing_service.service_name,
                "spans": len(tracing_service.spans),
                "traces": len(tracing_service.traces),
            }
        ]
        
        return {
            "status": "success",
            "services": services,
            "total": len(services),
        }
    
    except Exception as e:
        logger.error("Failed to list services", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_spans(
    max_age_hours: int = Query(1, ge=1, le=24, description="最大保留时间（小时）"),
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    清理旧的 Span 数据
    
    Args:
        max_age_hours: 最大保留时间（小时）
    
    Returns:
        清理结果
    """
    try:
        max_age_seconds = max_age_hours * 3600
        
        # 记录清理前的统计
        before_stats = tracing_service.get_stats()
        
        # 执行清理
        tracing_service.cleanup_old_spans(max_age_seconds)
        
        # 记录清理后的统计
        after_stats = tracing_service.get_stats()
        
        cleaned_spans = before_stats["total_spans"] - after_stats["total_spans"]
        cleaned_traces = before_stats["total_traces"] - after_stats["total_traces"]
        
        return {
            "status": "success",
            "message": "Old spans cleaned up successfully",
            "cleaned_spans": cleaned_spans,
            "cleaned_traces": cleaned_traces,
            "remaining_spans": after_stats["total_spans"],
            "remaining_traces": after_stats["total_traces"],
        }
    
    except Exception as e:
        logger.error("Failed to cleanup old spans", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_trace_timeline(
    trace_id: str,
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    获取追踪时间线
    
    Args:
        trace_id: 追踪ID
    
    Returns:
        时间线数据
    """
    try:
        spans = tracing_service.get_trace(trace_id)
        if not spans:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        # 构建时间线
        timeline = []
        min_start_time = min(span.start_time for span in spans)
        
        for span in spans:
            relative_start = span.start_time - min_start_time
            relative_end = (span.end_time - min_start_time) if span.end_time else None
            
            timeline.append({
                "span_id": span.span_id,
                "operation_name": span.operation_name,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "relative_start": relative_start,
                "relative_end": relative_end,
                "duration": span.duration,
                "status": span.status,
                "kind": span.kind,
                "parent_span_id": span.parent_span_id,
                "tags": span.tags,
            })
        
        # 按开始时间排序
        timeline.sort(key=lambda x: x["relative_start"])
        
        total_duration = max(
            (span.end_time - min_start_time) for span in spans if span.end_time
        ) if any(span.end_time for span in spans) else 0
        
        return {
            "status": "success",
            "trace_id": trace_id,
            "timeline": timeline,
            "total_duration": total_duration,
            "span_count": len(spans),
            "start_time": min_start_time,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get trace timeline", trace_id=trace_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dependencies")
async def get_service_dependencies(
    tracing_service: TracingService = Depends(get_tracing_service),
) -> Dict[str, Any]:
    """
    获取服务依赖关系
    
    Returns:
        服务依赖关系图
    """
    try:
        # 分析 spans 中的服务调用关系
        dependencies = {}
        
        for span in tracing_service.spans.values():
            service_name = tracing_service.service_name
            
            # 检查是否有外部服务调用
            if "http.url" in span.tags:
                url = span.tags["http.url"]
                # 简单解析目标服务
                if "://" in url:
                    target_service = url.split("://")[1].split("/")[0]
                    if service_name not in dependencies:
                        dependencies[service_name] = set()
                    dependencies[service_name].add(target_service)
        
        # 转换为列表格式
        dependency_list = []
        for source, targets in dependencies.items():
            for target in targets:
                dependency_list.append({
                    "source": source,
                    "target": target,
                    "type": "http",
                })
        
        return {
            "status": "success",
            "dependencies": dependency_list,
            "services": list(set(
                [dep["source"] for dep in dependency_list] +
                [dep["target"] for dep in dependency_list]
            )),
        }
    
    except Exception as e:
        logger.error("Failed to get service dependencies", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))