"""
智能体 API 端点

提供索儿智能体的交互接口
"""

import json
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Any, Dict

from ...models.agent import MessageType
from ...models.user import UserContext
from ...services.agent_service import AgentService
from ...core.dependencies import get_current_user, get_websocket_user

router = APIRouter(tags=["智能体"])


# 依赖注入
async def get_agent_service() -> AgentService:
    """获取智能体服务实例"""
    return AgentService()


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    conversation_id: str | None = None
    message_type: MessageType = MessageType.TEXT
    context: dict[str, Any] = {}


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response_id: str
    conversation_id: str
    content: str
    suggestions: list[str]
    quick_replies: list[str]
    confidence_score: float
    tcm_insights: dict[str, Any] | None = None


class ConfigUpdateRequest(BaseModel):
    """配置更新请求模型"""
    personality: str | None = None
    expertise_level: str | None = None
    language: str | None = None
    response_length: str | None = None
    use_emojis: bool | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    与智能体对话

    Args:
        request: 聊天请求
        agent_service: 智能体服务

    Returns:
        智能体响应
    """
    try:
        response = await agent_service.process_message(
            user_id=current_user["user_id"],
            message_content=request.message,
            conversation_id=request.conversation_id,
            message_type=request.message_type,
            context=request.context,
        )

        return ChatResponse(
            response_id=response.response_id,
            conversation_id=response.conversation_id,
            content=response.content,
            suggestions=response.suggestions,
            quick_replies=response.quick_replies,
            confidence_score=response.confidence_score,
            tcm_insights=response.tcm_insights,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")


@router.get("/capabilities")
async def get_agent_capabilities(
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    获取智能体能力

    Args:
        agent_service: 智能体服务

    Returns:
        智能体能力信息
    """
    try:
        capabilities = await agent_service.get_capabilities()
        return capabilities

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取能力失败: {str(e)}")


@router.get("/history")
async def get_conversation_history(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    获取对话历史

    Args:
        user_id: 用户ID
        limit: 限制数量
        agent_service: 智能体服务

    Returns:
        对话历史
    """
    try:
        user_id = current_user["user_id"]
        history = await agent_service.get_conversation_history(user_id, limit)
        if history:
            return history.dict()
        else:
            return {"user_id": user_id, "messages": [], "responses": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.get("/config")
async def get_user_config(
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    获取用户配置

    Args:
        user_id: 用户ID
        agent_service: 智能体服务

    Returns:
        用户配置
    """
    try:
        user_id = current_user["user_id"]
        config = await agent_service.get_user_config(user_id)
        return config

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.put("/config")
async def update_user_config(
    request: ConfigUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    更新用户配置

    Args:
        user_id: 用户ID
        request: 配置更新请求
        agent_service: 智能体服务

    Returns:
        更新结果
    """
    try:
        # 构建配置字典
        config_updates = {}
        if request.personality is not None:
            config_updates["personality"] = request.personality
        if request.expertise_level is not None:
            config_updates["expertise_level"] = request.expertise_level
        if request.language is not None:
            config_updates["language"] = request.language
        if request.response_length is not None:
            config_updates["response_length"] = request.response_length
        if request.use_emojis is not None:
            config_updates["use_emojis"] = request.use_emojis

        user_id = current_user["user_id"]
        success = await agent_service.update_user_config(user_id, config_updates)

        if success:
            return {"message": "配置更新成功"}
        else:
            raise HTTPException(status_code=400, detail="配置更新失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置更新失败: {str(e)}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 连接端点

    Args:
        websocket: WebSocket 连接
    """
    try:
        # 先进行认证
        user_data = await get_websocket_user(websocket)
        user_id = user_data["user_id"]
        
        await websocket.accept()
        agent_service = AgentService()

        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # 处理消息
            response = await agent_service.process_message(
                user_id=user_id,
                message_content=message_data.get("message", ""),
                conversation_id=message_data.get("conversation_id"),
                message_type=MessageType(message_data.get("message_type", "text")),
                context=message_data.get("context", {}),
            )

            # 发送响应
            await websocket.send_text(
                json.dumps(
                    {
                        "response_id": response.response_id,
                        "conversation_id": response.conversation_id,
                        "content": response.content,
                        "suggestions": response.suggestions,
                        "quick_replies": response.quick_replies,
                        "confidence_score": response.confidence_score,
                        "tcm_insights": response.tcm_insights,
                        "timestamp": response.timestamp.isoformat(),
                    },
                    ensure_ascii=False,
                )
            )

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        try:
            await websocket.send_text(
                json.dumps({"error": f"处理失败: {str(e)}"}, ensure_ascii=False)
            )
        except:
            print(f"WebSocket error for user {user_id}: {str(e)}")