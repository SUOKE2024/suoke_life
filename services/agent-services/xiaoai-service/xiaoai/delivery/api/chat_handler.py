#!/usr/bin/env python3
"""
聊天API处理器
为小艾智能体提供聊天和多模态交互的HTTP接口
"""

import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...agent.agent_manager import AgentManager

logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    """聊天请求模型"""
    userid: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息")
    sessionid: str | None = Field(None, description="会话ID")
    contextsize: int | None = Field(None, description="上下文大小")

class MultimodalRequest(BaseModel):
    """多模态请求模型"""
    userid: str = Field(..., description="用户ID")
    inputdata: dict[str, Any] = Field(..., description="多模态输入数据")
    sessionid: str | None = Field(None, description="会话ID")

def create_chat_router(getagent_manager_func: Callable[[], AgentManager]) -> APIRouter:
    """创建聊天路由器"""
    router = APIRouter(prefix="/api/v1/chat", tags=["聊天交互"])

    @router.post("/message")
    async def send_message(request: ChatRequest, agent_mgr: AgentManager = Depends(getagent_manager_func)):
        """发送聊天消息"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用") from e

            # 处理聊天消息
            result = await agent_mgr.chat(
                user_id=request.userid,
                message=request.message,
                session_id=request.sessionid,
                context_size=request.context_size
            )

            return JSONResponse(content={
                "success": True,
                "data": result,
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"聊天消息处理失败: {e}")
            raise HTTPException(status_code=500, detail=f"聊天消息处理失败: {e!s}") from e

    @router.post("/multimodal")
    async def process_multimodal(request: MultimodalRequest, agent_mgr: AgentManager = Depends(getagent_manager_func)):
        """处理多模态输入"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用") from e

            # 处理多模态输入
            result = await agent_mgr.process_multimodal_input(
                user_id=request.userid,
                input_data=request.inputdata,
                session_id=request.session_id
            )

            return JSONResponse(content={
                "success": True,
                "data": result,
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"多模态输入处理失败: {e}")
            raise HTTPException(status_code=500, detail=f"多模态输入处理失败: {e!s}") from e

    @router.get("/sessions/{user_id}")
    async def get_user_sessions(userid: str, agent_mgr: AgentManager = Depends(getagent_manager_func)):
        """获取用户会话列表"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用") from e

            # 获取用户的活跃会话
            usersessions = [
                {
                    "session_id": sessionid,
                    "user_id": session_data.get("user_id"),
                    "created_at": session_data.get("created_at"),
                    "last_active": session_data.get("last_active"),
                    "message_count": len(session_data.get("history", []))
                }
                for sessionid, session_data in agent_mgr.active_sessions.items()
                if session_data.get("user_id") == user_id
            ]

            return JSONResponse(content={
                "success": True,
                "data": {
                    "user_id": userid,
                    "sessions": usersessions,
                    "total_count": len(usersessions)
                },
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取用户会话失败: {e!s}") from e

    @router.delete("/sessions/{session_id}")
    async def close_session(sessionid: str, agent_mgr: AgentManager = Depends(getagent_manager_func)):
        """关闭会话"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用") from e

            # 关闭会话
            success = await agent_mgr.close_session(sessionid)

            return JSONResponse(content={
                "success": success,
                "data": {
                    "session_id": sessionid,
                    "closed": success
                },
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"关闭会话失败: {e}")
            raise HTTPException(status_code=500, detail=f"关闭会话失败: {e!s}") from e

    @router.post("/accessibility/content")
    async def generate_accessible_content(
        userid: str,
        content: str,
        contenttype: str = "health_advice",
        targetformat: str = "audio",
        agentmgr: AgentManager = Depends(getagent_manager_func)
    ):
        """生成无障碍内容"""
        try:
            if not agent_mgr:
                raise HTTPException(status_code=503, detail="智能体管理器不可用") from e

            # 生成无障碍内容
            result = await agent_mgr.generate_accessible_content(
                content=content,
                user_id=userid,
                content_type=contenttype,
                target_format=target_format
            )

            return JSONResponse(content={
                "success": True,
                "data": result,
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"生成无障碍内容失败: {e}")
            raise HTTPException(status_code=500, detail=f"生成无障碍内容失败: {e!s}") from e

    return router
