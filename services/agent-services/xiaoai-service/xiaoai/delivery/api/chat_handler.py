#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天API处理器
为小艾智能体提供聊天和多模态交互的HTTP接口
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...agent.agent_manager import AgentManager

logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    context_size: Optional[int] = Field(None, description="上下文大小")

class MultimodalRequest(BaseModel):
    """多模态请求模型"""
    user_id: str = Field(..., description="用户ID")
    input_data: Dict[str, Any] = Field(..., description="多模态输入数据")
    session_id: Optional[str] = Field(None, description="会话ID")

def create_chat_router(get_agent_manager_func: Callable[[], AgentManager]) -> APIRouter:
    """创建聊天路由器"""
    router = APIRouter(prefix="/api/v1/chat", tags=["聊天交互"])

    @router.post("/message")
    async def send_message(request: ChatRequest, agent_mgr: AgentManager = Depends(get_agent_manager_func)):
        """发送聊天消息"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用")
            
            # 处理聊天消息
            result = await agent_mgr.chat(
                user_id=request.user_id,
                message=request.message,
                session_id=request.session_id,
                context_size=request.context_size
            )
            
            return JSONResponse(content={
                "success": True,
                "data": result,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"聊天消息处理失败: {e}")
            raise HTTPException(status_code=500, detail=f"聊天消息处理失败: {str(e)}")

    @router.post("/multimodal")
    async def process_multimodal(request: MultimodalRequest, agent_mgr: AgentManager = Depends(get_agent_manager_func)):
        """处理多模态输入"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用")
            
            # 处理多模态输入
            result = await agent_mgr.process_multimodal_input(
                user_id=request.user_id,
                input_data=request.input_data,
                session_id=request.session_id
            )
            
            return JSONResponse(content={
                "success": True,
                "data": result,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"多模态输入处理失败: {e}")
            raise HTTPException(status_code=500, detail=f"多模态输入处理失败: {str(e)}")

    @router.get("/sessions/{user_id}")
    async def get_user_sessions(user_id: str, agent_mgr: AgentManager = Depends(get_agent_manager_func)):
        """获取用户会话列表"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用")
            
            # 获取用户的活跃会话
            user_sessions = [
                {
                    "session_id": session_id,
                    "user_id": session_data.get("user_id"),
                    "created_at": session_data.get("created_at"),
                    "last_active": session_data.get("last_active"),
                    "message_count": len(session_data.get("history", []))
                }
                for session_id, session_data in agent_mgr.active_sessions.items()
                if session_data.get("user_id") == user_id
            ]
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "user_id": user_id,
                    "sessions": user_sessions,
                    "total_count": len(user_sessions)
                },
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取用户会话失败: {str(e)}")

    @router.delete("/sessions/{session_id}")
    async def close_session(session_id: str, agent_mgr: AgentManager = Depends(get_agent_manager_func)):
        """关闭会话"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用")
            
            # 关闭会话
            success = await agent_mgr.close_session(session_id)
            
            return JSONResponse(content={
                "success": success,
                "data": {
                    "session_id": session_id,
                    "closed": success
                },
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"关闭会话失败: {e}")
            raise HTTPException(status_code=500, detail=f"关闭会话失败: {str(e)}")

    @router.post("/accessibility/content")
    async def generate_accessible_content(
        user_id: str,
        content: str,
        content_type: str = "health_advice",
        target_format: str = "audio",
        agent_mgr: AgentManager = Depends(get_agent_manager_func)
    ):
        """生成无障碍内容"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用")
            
            # 生成无障碍内容
            result = await agent_mgr.generate_accessible_content(
                content=content,
                user_id=user_id,
                content_type=content_type,
                target_format=target_format
            )
            
            return JSONResponse(content={
                "success": True,
                "data": result,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"生成无障碍内容失败: {e}")
            raise HTTPException(status_code=500, detail=f"生成无障碍内容失败: {str(e)}")

    return router 