"""
智能体协同API接口
提供智能体协同管理的REST API
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from ..communication_service.event_bus.orchestration.agent_orchestrator import (
    AgentCollaborationManager
)
from ..communication_service.event_bus.core.event_bus import SuokeEventBus
from ..communication_service.event_bus.core.agent_event_types import COLLABORATION_SCENARIOS


# Pydantic模型定义
class CollaborationRequest(BaseModel):
    """协同请求模型"""
    scenario: str = Field(..., description="协同场景")
    user_id: str = Field(..., description="用户ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class CollaborationResponse(BaseModel):
    """协同响应模型"""
    session_id: str = Field(..., description="协同会话ID")
    scenario: str = Field(..., description="协同场景")
    status: str = Field(..., description="协同状态")
    message: str = Field(..., description="响应消息")


class SessionStatusResponse(BaseModel):
    """会话状态响应模型"""
    session_id: str
    scenario: str
    state: str
    participating_agents: List[str]
    progress: Dict[str, int]
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


class AgentHandoffRequest(BaseModel):
    """智能体交接请求模型"""
    from_agent: str = Field(..., description="源智能体")
    to_agent: str = Field(..., description="目标智能体")
    context: Dict[str, Any] = Field(..., description="交接上下文")


class HealthDiagnosisRequest(BaseModel):
    """健康诊断请求模型"""
    user_id: str = Field(..., description="用户ID")
    symptoms: List[str] = Field(default_factory=list, description="症状列表")
    user_info: Dict[str, Any] = Field(default_factory=dict, description="用户信息")
    urgency: str = Field("normal", description="紧急程度")


class WellnessPlanRequest(BaseModel):
    """养生计划请求模型"""
    user_id: str = Field(..., description="用户ID")
    health_goals: List[str] = Field(..., description="健康目标")
    lifestyle_data: Dict[str, Any] = Field(default_factory=dict, description="生活数据")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="偏好设置")


# 创建路由器
router = APIRouter(prefix="/api/v1/collaboration", tags=["智能体协同"])

# 全局变量（实际应用中应该通过依赖注入）
collaboration_manager: Optional[AgentCollaborationManager] = None


def get_collaboration_manager() -> AgentCollaborationManager:
    """获取协同管理器依赖"""
    global collaboration_manager
    if collaboration_manager is None:
        raise HTTPException(status_code=500, detail="协同管理器未初始化")
    return collaboration_manager


async def initialize_collaboration_api(event_bus: SuokeEventBus):
    """初始化协同API"""
    global collaboration_manager
    collaboration_manager = AgentCollaborationManager(event_bus)
    await collaboration_manager.initialize()


@router.post("/start", response_model=CollaborationResponse)
async def start_collaboration(
    request: CollaborationRequest,
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """启动智能体协同"""
    try:
        # 验证协同场景
        if request.scenario not in COLLABORATION_SCENARIOS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的协同场景: {request.scenario}"
            )
        
        # 启动协同
        session_id = await manager.start_collaboration(
            scenario=request.scenario,
            user_id=request.user_id,
            context=request.context
        )
        
        return CollaborationResponse(
            session_id=session_id,
            scenario=request.scenario,
            status="started",
            message="智能体协同已启动"
        )
    
    except Exception as e:
        logging.error(f"启动协同失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动协同失败: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """获取协同会话状态"""
    try:
        status = await manager.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="协同会话不存在")
        
        return SessionStatusResponse(**status)
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"获取会话状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会话状态失败: {str(e)}")


@router.delete("/sessions/{session_id}")
async def cancel_collaboration(
    session_id: str,
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """取消协同会话"""
    try:
        success = await manager.cancel_collaboration(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="协同会话不存在")
        
        return {"message": "协同会话已取消", "session_id": session_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"取消协同失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消协同失败: {str(e)}")


@router.get("/sessions", response_model=List[SessionStatusResponse])
async def list_active_sessions(
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """列出活跃的协同会话"""
    try:
        sessions = await manager.list_active_sessions()
        return [SessionStatusResponse(**session) for session in sessions]
    
    except Exception as e:
        logging.error(f"获取活跃会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取活跃会话失败: {str(e)}")


@router.get("/scenarios")
async def get_collaboration_scenarios():
    """获取支持的协同场景"""
    return {
        "scenarios": list(COLLABORATION_SCENARIOS.keys()),
        "details": COLLABORATION_SCENARIOS
    }


@router.post("/health-diagnosis", response_model=CollaborationResponse)
async def start_health_diagnosis(
    request: HealthDiagnosisRequest,
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """启动健康诊断协同"""
    try:
        # 根据紧急程度选择协同场景
        scenario = "emergency_health_support" if request.urgency == "high" else "comprehensive_health_diagnosis"
        
        context = {
            "symptoms": request.symptoms,
            "user_info": request.user_info,
            "urgency": request.urgency,
            "diagnosis_type": "health_diagnosis"
        }
        
        session_id = await manager.start_collaboration(
            scenario=scenario,
            user_id=request.user_id,
            context=context
        )
        
        return CollaborationResponse(
            session_id=session_id,
            scenario=scenario,
            status="started",
            message="健康诊断协同已启动"
        )
    
    except Exception as e:
        logging.error(f"启动健康诊断失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动健康诊断失败: {str(e)}")


@router.post("/wellness-plan", response_model=CollaborationResponse)
async def start_wellness_planning(
    request: WellnessPlanRequest,
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """启动养生计划协同"""
    try:
        context = {
            "health_goals": request.health_goals,
            "lifestyle_data": request.lifestyle_data,
            "preferences": request.preferences,
            "plan_type": "wellness_plan"
        }
        
        session_id = await manager.start_collaboration(
            scenario="personalized_wellness_plan",
            user_id=request.user_id,
            context=context
        )
        
        return CollaborationResponse(
            session_id=session_id,
            scenario="personalized_wellness_plan",
            status="started",
            message="养生计划协同已启动"
        )
    
    except Exception as e:
        logging.error(f"启动养生计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动养生计划失败: {str(e)}")


@router.post("/agent-handoff")
async def initiate_agent_handoff(
    request: AgentHandoffRequest,
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """发起智能体交接"""
    try:
        # 发布智能体交接事件
        from ..communication_service.event_bus.core.agent_event_types import AgentCollaborationEvents
        
        await manager.orchestrator.event_bus.publish(
            AgentCollaborationEvents.AGENT_HANDOFF_INITIATED,
            {
                "from_agent": request.from_agent,
                "to_agent": request.to_agent,
                "context": request.context,
                "handoff_time": datetime.now().isoformat()
            }
        )
        
        return {
            "message": "智能体交接已发起",
            "from_agent": request.from_agent,
            "to_agent": request.to_agent
        }
    
    except Exception as e:
        logging.error(f"发起智能体交接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发起智能体交接失败: {str(e)}")


@router.get("/agents/status")
async def get_agents_status(
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """获取所有智能体状态"""
    try:
        agents = ["xiaoai", "xiaoke", "laoke", "soer"]
        status_data = {}
        
        for agent_id in agents:
            status = await manager.orchestrator.get_agent_status(agent_id)
            status_data[agent_id] = status or {"status": "unknown", "last_seen": None}
        
        return {
            "agents": status_data,
            "total_agents": len(agents),
            "active_agents": len([s for s in status_data.values() if s.get("status") == "active"])
        }
    
    except Exception as e:
        logging.error(f"获取智能体状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取智能体状态失败: {str(e)}")


@router.post("/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status_data: Dict[str, Any],
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """更新智能体状态"""
    try:
        await manager.orchestrator.update_agent_status(agent_id, status_data)
        return {"message": f"智能体 {agent_id} 状态已更新"}
    
    except Exception as e:
        logging.error(f"更新智能体状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新智能体状态失败: {str(e)}")


@router.get("/metrics")
async def get_collaboration_metrics(
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """获取协同指标"""
    try:
        active_sessions = await manager.list_active_sessions()
        
        # 统计各种状态的会话数量
        state_counts = {}
        scenario_counts = {}
        
        for session in active_sessions:
            state = session.get("state", "unknown")
            scenario = session.get("scenario", "unknown")
            
            state_counts[state] = state_counts.get(state, 0) + 1
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
        
        return {
            "total_active_sessions": len(active_sessions),
            "state_distribution": state_counts,
            "scenario_distribution": scenario_counts,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logging.error(f"获取协同指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取协同指标失败: {str(e)}")


@router.post("/test/mock-collaboration")
async def test_mock_collaboration(
    scenario: str = "comprehensive_health_diagnosis",
    user_id: str = "test_user_001",
    manager: AgentCollaborationManager = Depends(get_collaboration_manager)
):
    """测试模拟协同（仅用于开发测试）"""
    try:
        context = {
            "test_mode": True,
            "symptoms": ["疲劳", "食欲不振", "睡眠质量差"],
            "user_info": {
                "age": 30,
                "gender": "female",
                "occupation": "office_worker"
            }
        }
        
        session_id = await manager.start_collaboration(
            scenario=scenario,
            user_id=user_id,
            context=context
        )
        
        return {
            "message": "测试协同已启动",
            "session_id": session_id,
            "scenario": scenario,
            "test_mode": True
        }
    
    except Exception as e:
        logging.error(f"测试协同失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试协同失败: {str(e)}")


# 错误处理器
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logging.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "timestamp": datetime.now().isoformat()
        }
    ) 