"""
智能体 API 端点

提供索儿智能体的交互接口
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ...models.agent import MessageType
from ...services.agent_service import AgentService

router = APIRouter(tags=["智能体"])


# 依赖注入
async def get_agent_service() -> AgentService:
    """获取智能体服务实例"""
    return AgentService()


class ChatRequest(BaseModel):
    """聊天请求模型"""

    user_id: str
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
    request: ChatRequest, agent_service: AgentService = Depends(get_agent_service)
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
            user_id=request.user_id,
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
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    获取智能体能力信息

    Returns:
        智能体能力详情
    """
    try:
        capabilities = await agent_service.get_agent_capabilities()
        return capabilities

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取能力信息失败: {str(e)}")


@router.get("/history/{user_id}")
async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    limit: int = 50,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    获取对话历史

    Args:
        user_id: 用户ID
        conversation_id: 对话ID
        limit: 消息数量限制
        agent_service: 智能体服务

    Returns:
        对话历史
    """
    try:
        history = await agent_service.get_conversation_history(
            user_id=user_id, conversation_id=conversation_id, limit=limit
        )
        return history

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")


@router.get("/config/{user_id}")
async def get_user_configuration(
    user_id: str, agent_service: AgentService = Depends(get_agent_service)
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
        config = await agent_service._get_user_configuration(user_id)
        return config

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户配置失败: {str(e)}")


@router.put("/config/{user_id}")
async def update_user_configuration(
    user_id: str,
    request: ConfigUpdateRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    更新用户配置

    Args:
        user_id: 用户ID
        request: 配置更新请求
        agent_service: 智能体服务

    Returns:
        更新后的配置
    """
    try:
        config_updates = request.dict(exclude_unset=True)
        updated_config = await agent_service.update_user_configuration(
            user_id=user_id, config_updates=config_updates
        )
        return updated_config

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户配置失败: {str(e)}")


@router.get("/sentiment/{conversation_id}")
async def analyze_conversation_sentiment(
    conversation_id: str, agent_service: AgentService = Depends(get_agent_service)
):
    """
    分析对话情感

    Args:
        conversation_id: 对话ID
        agent_service: 智能体服务

    Returns:
        情感分析结果
    """
    try:
        sentiment = await agent_service.analyze_conversation_sentiment(conversation_id)
        return sentiment

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情感分析失败: {str(e)}")


@router.websocket("/ws/{user_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: str,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    WebSocket 聊天端点

    Args:
        websocket: WebSocket 连接
        user_id: 用户ID
        agent_service: 智能体服务
    """
    await websocket.accept()

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()

            # 处理消息
            response = await agent_service.process_message(
                user_id=user_id,
                message_content=data.get("message", ""),
                conversation_id=data.get("conversation_id"),
                message_type=MessageType(data.get("message_type", "text")),
                context=data.get("context", {}),
            )

            # 发送响应
            await websocket.send_json(
                {
                    "response_id": response.response_id,
                    "conversation_id": response.conversation_id,
                    "content": response.content,
                    "suggestions": response.suggestions,
                    "quick_replies": response.quick_replies,
                    "confidence_score": response.confidence_score,
                    "tcm_insights": response.tcm_insights,
                }
            )

    except WebSocketDisconnect:
        print(f"用户 {user_id} 断开 WebSocket 连接")
    except Exception as e:
        await websocket.send_json({"error": f"处理消息失败: {str(e)}"})
        await websocket.close()


@router.get("/health")
async def agent_health_check(agent_service: AgentService = Depends(get_agent_service)):
    """
    智能体服务健康检查

    Returns:
        健康状态
    """
    try:
        health_status = await agent_service.health_check()
        return health_status

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")
