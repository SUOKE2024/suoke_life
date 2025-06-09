"""
索克生活事件驱动架构API接口
为其他服务提供事件发布、订阅和数据访问接口
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..communication_service.event_bus.core.event_bus import get_event_bus
from ..communication_service.event_bus.core.event_store import get_event_store
from ..communication_service.event_bus.core.event_types import (
    AgentCollaborationEvents, HealthDataEvents, UserInteractionEvents
)

logger = structlog.get_logger(__name__)

# 创建API路由器
router = APIRouter(prefix="/api/v1/events", tags=["事件驱动架构"])


# Pydantic模型定义
class EventPublishRequest(BaseModel):
    """事件发布请求"""
    event_type: str = Field(..., description="事件类型")
    data: Dict[str, Any] = Field(..., description="事件数据")
    correlation_id: Optional[str] = Field(None, description="关联ID")


class EventPublishResponse(BaseModel):
    """事件发布响应"""
    success: bool = Field(..., description="是否成功")
    event_id: Optional[str] = Field(None, description="事件ID")
    message: str = Field(..., description="响应消息")


class DiagnosisStartRequest(BaseModel):
    """诊断启动请求"""
    user_id: str = Field(..., description="用户ID")
    user_data: Dict[str, Any] = Field(..., description="用户数据")
    priority: str = Field("normal", description="优先级")


class DiagnosisStartResponse(BaseModel):
    """诊断启动响应"""
    success: bool = Field(..., description="是否成功")
    session_id: Optional[str] = Field(None, description="诊断会话ID")
    message: str = Field(..., description="响应消息")


class HealthDataUpdateRequest(BaseModel):
    """健康数据更新请求"""
    user_id: str = Field(..., description="用户ID")
    data_type: str = Field(..., description="数据类型")
    data_value: Any = Field(..., description="数据值")
    source: str = Field("api", description="数据来源")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class HealthDataUpdateResponse(BaseModel):
    """健康数据更新响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")


class HealthDataQueryRequest(BaseModel):
    """健康数据查询请求"""
    user_id: str = Field(..., description="用户ID")
    data_type: Optional[str] = Field(None, description="数据类型")
    access_mode: str = Field("real_time", description="访问模式")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    limit: int = Field(100, description="限制数量")


class EventQueryRequest(BaseModel):
    """事件查询请求"""
    event_type: Optional[str] = Field(None, description="事件类型")
    source: Optional[str] = Field(None, description="事件来源")
    correlation_id: Optional[str] = Field(None, description="关联ID")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    limit: int = Field(100, description="限制数量")
    offset: int = Field(0, description="偏移量")


# API端点实现
@router.post("/publish", response_model=EventPublishResponse)
async def publish_event(request: EventPublishRequest) -> EventPublishResponse:
    """发布事件"""
    try:
        event_bus = get_event_bus()
        
        event_id = await event_bus.publish(
            event_type=request.event_type,
            data=request.data,
            correlation_id=request.correlation_id
        )
        
        return EventPublishResponse(
            success=True,
            event_id=event_id,
            message="事件发布成功"
        )
        
    except Exception as e:
        logger.error("事件发布失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"事件发布失败: {str(e)}")


@router.post("/diagnosis/start", response_model=DiagnosisStartResponse)
async def start_diagnosis(request: DiagnosisStartRequest) -> DiagnosisStartResponse:
    """启动智能体协同诊断"""
    try:
        event_bus = get_event_bus()
        
        # 生成会话ID
        session_id = f"diagnosis_{request.user_id}_{int(datetime.utcnow().timestamp())}"
        
        # 发布诊断启动事件
        await event_bus.publish(
            AgentCollaborationEvents.DIAGNOSIS_STARTED,
            {
                'user_id': request.user_id,
                'session_id': session_id,
                'user_data': request.user_data,
                'priority': request.priority,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return DiagnosisStartResponse(
            success=True,
            session_id=session_id,
            message="诊断流程启动成功"
        )
        
    except Exception as e:
        logger.error("诊断启动失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"诊断启动失败: {str(e)}")


@router.post("/health-data/update", response_model=HealthDataUpdateResponse)
async def update_health_data(request: HealthDataUpdateRequest) -> HealthDataUpdateResponse:
    """更新健康数据"""
    try:
        event_bus = get_event_bus()
        
        # 发布健康数据接收事件
        await event_bus.publish(
            HealthDataEvents.HEALTH_DATA_RECEIVED,
            {
                'user_id': request.user_id,
                'data_type': request.data_type,
                'data_value': request.data_value,
                'source': request.source,
                'metadata': request.metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return HealthDataUpdateResponse(
            success=True,
            message="健康数据更新成功"
        )
        
    except Exception as e:
        logger.error("健康数据更新失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"健康数据更新失败: {str(e)}")


@router.post("/health-data/query")
async def query_health_data(request: HealthDataQueryRequest) -> Dict[str, Any]:
    """查询健康数据"""
    try:
        # 这里应该调用SmartDataAccessRouter
        # 暂时返回模拟数据
        return {
            'user_id': request.user_id,
            'data_type': request.data_type,
            'access_mode': request.access_mode,
            'data': [
                {
                    'id': f"{request.user_id}_{request.data_type}_1",
                    'value': 75.5,
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'cache'
                }
            ],
            'total_count': 1,
            'query_time': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("健康数据查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"健康数据查询失败: {str(e)}")


@router.post("/events/query")
async def query_events(request: EventQueryRequest) -> Dict[str, Any]:
    """查询事件"""
    try:
        event_store = get_event_store()
        
        events = await event_store.get_events(
            event_type=request.event_type,
            source=request.source,
            correlation_id=request.correlation_id,
            start_time=request.start_time,
            end_time=request.end_time,
            limit=request.limit,
            offset=request.offset
        )
        
        return {
            'events': [
                {
                    'id': event.id,
                    'type': event.type,
                    'data': event.data,
                    'timestamp': event.timestamp,
                    'source': event.source,
                    'correlation_id': event.correlation_id
                }
                for event in events
            ],
            'total_count': len(events),
            'query_time': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("事件查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"事件查询失败: {str(e)}")


@router.get("/diagnosis/{session_id}/status")
async def get_diagnosis_status(session_id: str) -> Dict[str, Any]:
    """获取诊断状态"""
    try:
        # 这里应该调用AgentEventHandlers获取会话状态
        # 暂时返回模拟数据
        return {
            'session_id': session_id,
            'status': 'in_progress',
            'current_step': 'look',
            'progress': {
                'look': 'completed',
                'listen': 'in_progress',
                'inquiry': 'pending',
                'palpation': 'pending'
            },
            'started_at': datetime.utcnow().isoformat(),
            'estimated_completion': (datetime.utcnow()).isoformat()
        }
        
    except Exception as e:
        logger.error("诊断状态查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"诊断状态查询失败: {str(e)}")


@router.get("/agents/status")
async def get_agents_status() -> Dict[str, Any]:
    """获取智能体状态"""
    try:
        # 这里应该调用AgentEventHandlers获取智能体状态
        # 暂时返回模拟数据
        return {
            'agents': {
                'xiaoai': {
                    'available': True,
                    'current_task': None,
                    'last_activity': datetime.utcnow().isoformat()
                },
                'xiaoke': {
                    'available': True,
                    'current_task': 'diagnosis_123',
                    'last_activity': datetime.utcnow().isoformat()
                },
                'laoke': {
                    'available': True,
                    'current_task': None,
                    'last_activity': datetime.utcnow().isoformat()
                },
                'soer': {
                    'available': True,
                    'current_task': None,
                    'last_activity': datetime.utcnow().isoformat()
                }
            },
            'active_sessions': 1,
            'total_sessions': 5,
            'query_time': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("智能体状态查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"智能体状态查询失败: {str(e)}")


@router.get("/health/trends/{user_id}")
async def get_health_trends(
    user_id: str,
    data_type: str,
    period: str = "week"
) -> Dict[str, Any]:
    """获取健康趋势"""
    try:
        # 这里应该调用SmartDataAccessRouter获取趋势数据
        # 暂时返回模拟数据
        return {
            'user_id': user_id,
            'data_type': data_type,
            'period': period,
            'trend': 'stable',
            'change_rate': 2.5,
            'data_points': 24,
            'avg_value': 76.2,
            'min_value': 72.1,
            'max_value': 80.3,
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("健康趋势查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"健康趋势查询失败: {str(e)}")


@router.get("/alerts/{user_id}")
async def get_user_alerts(user_id: str) -> Dict[str, Any]:
    """获取用户警报"""
    try:
        # 这里应该调用SmartDataAccessRouter获取实时警报
        # 暂时返回模拟数据
        return {
            'user_id': user_id,
            'alerts': [
                {
                    'id': 'alert_001',
                    'type': 'vital_signs_abnormal',
                    'severity': 'warning',
                    'message': '血压偏高，建议关注',
                    'data_type': 'blood_pressure',
                    'value': {'systolic': 145, 'diastolic': 95},
                    'timestamp': datetime.utcnow().isoformat(),
                    'acknowledged': False
                }
            ],
            'total_alerts': 1,
            'unacknowledged_count': 1,
            'query_time': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("用户警报查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"用户警报查询失败: {str(e)}")


@router.get("/statistics")
async def get_event_statistics() -> Dict[str, Any]:
    """获取事件统计"""
    try:
        event_store = get_event_store()
        event_bus = get_event_bus()
        
        # 获取事件存储统计
        store_stats = await event_store.get_event_statistics()
        
        # 获取事件总线统计
        bus_stats = event_bus.get_stats()
        
        return {
            'event_store': store_stats,
            'event_bus': bus_stats,
            'query_time': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("事件统计查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"事件统计查询失败: {str(e)}")


# 用户交互事件API
@router.post("/user/question")
async def submit_user_question(
    user_id: str,
    question: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """提交用户问题"""
    try:
        event_bus = get_event_bus()
        
        # 发布用户问题事件
        await event_bus.publish(
            UserInteractionEvents.USER_QUESTION_RECEIVED,
            {
                'user_id': user_id,
                'question': question,
                'context': context or {},
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'success': True,
            'message': '问题已提交，正在处理中',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("用户问题提交失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"用户问题提交失败: {str(e)}")


@router.post("/user/feedback")
async def submit_user_feedback(
    user_id: str,
    feedback_type: str,
    content: str,
    rating: Optional[int] = None
) -> Dict[str, Any]:
    """提交用户反馈"""
    try:
        event_bus = get_event_bus()
        
        # 发布用户反馈事件
        await event_bus.publish(
            UserInteractionEvents.USER_FEEDBACK_RECEIVED,
            {
                'user_id': user_id,
                'feedback_type': feedback_type,
                'content': content,
                'rating': rating,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'success': True,
            'message': '反馈已提交，感谢您的意见',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("用户反馈提交失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"用户反馈提交失败: {str(e)}") 