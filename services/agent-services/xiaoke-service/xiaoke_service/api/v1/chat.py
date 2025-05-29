"""
智能对话 API 端点
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from xiaoke_service.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


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
    try:
        logger.info(f"收到对话请求: user_id={request.user_id}, session_id={request.session_id}")

        # 基础对话逻辑框架
        session_id = request.session_id or f"session_{request.user_id or 'anonymous'}"

        # 这里应该调用实际的AI对话服务
        response_text = f"小克收到您的消息: {request.message}。正在为您分析健康状况..."

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            confidence=0.85,
            suggestions=["查看中医体质分析", "获取个性化健康建议", "预约专家咨询"],
        )
    except Exception as e:
        logger.error(f"对话处理失败: {e!s}")
        raise HTTPException(status_code=500, detail="对话处理失败") from e


@router.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str) -> dict:
    """获取对话历史"""
    try:
        logger.info(f"查询对话历史: session_id={session_id}")

        # 这里应该从数据库查询实际的对话历史
        return {
            "session_id": session_id,
            "messages": [],
            "total_count": 0,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"查询对话历史失败: {e!s}")
        raise HTTPException(status_code=500, detail="查询对话历史失败") from e
