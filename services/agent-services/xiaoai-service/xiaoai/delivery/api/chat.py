#!/usr/bin/env python3
"""
小艾智能体聊天API模块
提供聊天消息处理、WebSocket连接和会话管理功能
"""

import contextlib
import json
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from xiaoai.core.agent import XiaoaiAgent

chat_router = APIRouter()


class ChatMessage(BaseModel):
    """聊天消息模型"""
    text: str
    user_id: str | None = None
    session_id: str | None = None
    context: dict[str, Any] | None = None
    message_type: str = "text"  # text, voice, image


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    agent: str = "xiaoai"
    session_id: str
    message_id: str
    timestamp: float
    type: str = "text"
    metadata: dict[str, Any] | None = None


async def get_xiaoai_agent() -> XiaoaiAgent:
    """获取小艾智能体实例的依赖注入函数"""
    # 这个函数会在main.py中被重新定义
    raise HTTPException(status_code=503, detail="智能体服务未就绪") from None


@chat_router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessage, agent: XiaoaiAgent = Depends(get_xiaoai_agent)
):
    """发送聊天消息"""
    try:
        # 处理消息
        response = await agent.process_message(
            text=message.text,
            context=message.context,
            user_id=message.user_id,
            session_id=message.session_id,
        )

        # 构建响应
        chat_response = ChatResponse(
            response=response.get("response", ""),
            session_id=response.get("session_id", str(uuid4())),
            message_id=str(uuid4()),
            timestamp=time.time(),
            type=response.get("type", "text"),
            metadata=response.get("metadata"),
        )

        return chat_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理消息失败: {e!s}") from None


@chat_router.post("/voice-message")
async def send_voice_message(
    audio_data: bytes,
    user_id: str | None = None,
    session_id: str | None = None,
    agent: XiaoaiAgent = Depends(get_xiaoai_agent),
):
    """发送语音消息"""
    try:
        # 执行语音分析
        voice_analysis = await agent.perform_voice_analysis(audio_data)

        if "error" in voice_analysis:
            raise HTTPException(status_code=400, detail=voice_analysis["error"]) from None

        return {
            "message_id": str(uuid4()),
            "timestamp": time.time(),
            "analysis": voice_analysis,
            "agent": "xiaoai",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音消息处理失败: {e!s}") from None


@chat_router.get("/session/{session_id}/history")
async def get_chat_history(
    session_id: str, limit: int = 50, agent: XiaoaiAgent = Depends(get_xiaoai_agent)
):
    """获取聊天历史"""
    try:
        if not agent.agent_manager:
            raise HTTPException(status_code=503, detail="智能体管理器未就绪") from None

        session_info = agent.agent_manager.get_session_info(session_id)

        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在") from None

        history = session_info.get("diagnosis_history", [])

        # 限制返回数量
        if limit > 0:
            history = history[-limit:]

        return {
            "session_id": session_id,
            "history": history,
            "total_count": len(session_info.get("diagnosis_history", [])),
            "returned_count": len(history),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天历史失败: {e!s}") from None


@chat_router.delete("/session/{session_id}")
async def end_chat_session(
    session_id: str, agent: XiaoaiAgent = Depends(get_xiaoai_agent)
):
    """结束聊天会话"""
    try:
        if not agent.agent_manager:
            raise HTTPException(status_code=503, detail="智能体管理器未就绪") from None

        await agent.agent_manager.end_session(session_id)

        return {
            "message": "会话已结束",
            "session_id": session_id,
            "timestamp": time.time(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结束会话失败: {e!s}") from None


@chat_router.websocket("/ws/{user_id}")
async def websocket_chat(
    websocket: WebSocket, user_id: str, agent: XiaoaiAgent = Depends(get_xiaoai_agent)
):
    """WebSocket聊天连接"""
    await websocket.accept()
    session_id = None

    try:
        # 创建会话
        if agent.agent_manager:
            session_id = await agent.agent_manager.create_session(user_id)

        await websocket.send_text(
            json.dumps(
                {
                    "type": "connection_established",
                    "session_id": session_id,
                    "message": "连接已建立,欢迎使用小艾智能体服务!",
                    "timestamp": time.time(),
                }
            )
        )

        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # 处理消息
            response = await agent.process_message(
                text=message_data.get("text", ""),
                context=message_data.get("context", {}),
                user_id=user_id,
                session_id=session_id,
            )

            # 发送响应
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "message_response",
                        "response": response.get("response", ""),
                        "session_id": session_id,
                        "message_id": str(uuid4()),
                        "timestamp": time.time(),
                        "metadata": response.get("metadata"),
                    }
                )
            )

    except WebSocketDisconnect:
        # 客户端断开连接
        if session_id and agent.agent_manager:
            await agent.agent_manager.end_session(session_id)
    except Exception as e:
        # 发送错误消息
        with contextlib.suppress(Exception):
            await websocket.send_text(
                json.dumps({"type": "error", "error": str(e), "timestamp": time.time()})
            )

        # 清理会话
        if session_id and agent.agent_manager:
            await agent.agent_manager.end_session(session_id)


@chat_router.get("/capabilities")
async def get_chat_capabilities(agent: XiaoaiAgent = Depends(get_xiaoai_agent)):
    """获取聊天能力"""
    return {
        "capabilities": agent.capabilities,
        "multimodal_config": agent.multimodal_config,
        "supported_message_types": ["text", "voice", "image"],
        "features": [
            "中医诊断咨询",
            "健康建议",
            "无障碍服务",
            "多语言支持",
            "实时语音交互",
            "图像分析",
        ],
    }
