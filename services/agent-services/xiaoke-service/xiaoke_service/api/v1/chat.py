"""
智能对话 API 端点
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    """对话请求模型"""

    message: str
    session_id: str | None = None
    user_id: str | None = None
    context: dict | None = None


class ChatResponse(BaseModel):
    """对话响应模型"""

    response: str
    session_id: str
    confidence: float
    suggestions: list[str] = []


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """智能对话接口"""
    # TODO: 实现实际的AI对话逻辑
    return ChatResponse(
        response=f"小克收到您的消息：{request.message}。这是一个示例回复。",
        session_id=request.session_id or "default-session",
        confidence=0.95,
        suggestions=["了解更多中医知识", "查看健康建议", "预约专家咨询"],
    )


@router.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str) -> dict:
    """获取对话历史"""
    # TODO: 实现对话历史查询
    return {"session_id": session_id, "messages": [], "total_count": 0}
