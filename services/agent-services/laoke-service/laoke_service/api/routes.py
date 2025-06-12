"""老克智能体服务API路由模块"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..core.agent import get_agent, shutdown_agent
from ..core.config import get_config
from ..core.exceptions import (
    AIModelException,
    LaokeServiceException,
    SessionException,
    ValidationException,
    handle_exception,
)
from ..core.logging import (
    get_logger,
    log_error,
    log_request,
    log_response,
    log_security_event,
    setup_logging,
)


# 请求/响应模型
class ChatRequest(BaseModel):
    """对话请求模型"""

    message: str = Field(..., description="用户消息", min_length=1, max_length=4096)
    stream: bool = Field(False, description="是否使用流式响应")
    metadata: Optional[Dict[str, Any]] = Field(None, description="附加元数据")


class ChatResponse(BaseModel):
    """对话响应模型"""

    response: str = Field(..., description="智能体响应")
    session_id: str = Field(..., description="会话 ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="响应元数据")


class SessionCreateRequest(BaseModel):
    """创建会话请求模型"""

    user_id: str = Field(..., description="用户 ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="会话元数据")


class SessionResponse(BaseModel):
    """会话响应模型"""

    session_id: str = Field(..., description="会话 ID")
    user_id: str = Field(..., description="用户 ID")
    status: str = Field(..., description="会话状态")
    created_at: str = Field(..., description="创建时间")
    last_activity: str = Field(..., description="最后活动时间")
    message_count: int = Field(..., description="消息数量")
    metadata: Optional[Dict[str, Any]] = Field(None, description="会话元数据")


class MessageResponse(BaseModel):
    """消息响应模型"""

    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    timestamp: str = Field(..., description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")


class HistoryResponse(BaseModel):
    """历史记录响应模型"""

    session_id: str = Field(..., description="会话 ID")
    messages: List[MessageResponse] = Field(..., description="消息列表")


class StatsResponse(BaseModel):
    """统计信息响应模型"""

    total_sessions: int = Field(..., description="总会话数")
    active_sessions: int = Field(..., description="活跃会话数")
    max_concurrent_sessions: int = Field(..., description="最大并发会话数")
    session_timeout: int = Field(..., description="会话超时时间")
    cleanup_interval: int = Field(..., description="清理间隔")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error_code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: str = Field(..., description="错误时间")


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: str = Field(..., description="检查时间")
    checks: Dict[str, Any] = Field(..., description="各组件检查结果")


# 全局变量
logger = get_logger("api_routes")


# 依赖注入
def get_user_id(request: Request) -> str:
    """获取用户ID（从请求头或查询参数）"""
    # 从请求头获取
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id

    # 从查询参数获取
    user_id = request.query_params.get("user_id")
    if user_id:
        return user_id

    # 默认用户
    return "anonymous"


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    # 检查代理头
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # 直接连接
    if request.client:
        return request.client.host

    return "unknown"


# 中间件
async def request_logging_middleware(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()

    # 记录请求
    user_id = get_user_id(request)
    client_ip = get_client_ip(request)

    log_request(
        method=request.method,
        path=request.url.path,
        user_id=user_id,
        client_ip=client_ip,
        user_agent=request.headers.get("User-Agent", ""),
    )

    try:
        response = await call_next(request)

        # 记录响应
        duration_ms = (time.time() - start_time) * 1000

        log_response(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            client_ip=client_ip,
        )

        return response

    except Exception as e:
        # 记录错误
        duration_ms = (time.time() - start_time) * 1000

        log_error(
            e,
            {
                "method": request.method,
                "path": request.url.path,
                "user_id": user_id,
                "client_ip": client_ip,
                "duration_ms": duration_ms,
            },
        )

        raise


# 异常处理器
async def exception_handler(request: Request, exc: Exception) -> Response:
    """全局异常处理器"""
    from datetime import datetime

    from fastapi.responses import JSONResponse

    # 转换为服务异常
    if not isinstance(exc, LaokeServiceException):
        exc = handle_exception(exc)

    # 记录安全事件（如果是权限相关错误）
    if "permission" in str(exc).lower() or "access" in str(exc).lower():
        log_security_event(
            "access_denied",
            user_id=get_user_id(request),
            ip_address=get_client_ip(request),
            path=request.url.path,
        )

    # 根据错误类型返回相应的HTTP状态码
    status_code = 500
    if isinstance(exc, ValidationException):
        status_code = 400
    elif isinstance(exc, SessionException):
        if "not_found" in exc.details.get("error_type", ""):
            status_code = 404
        elif "expired" in exc.details.get("error_type", ""):
            status_code = 410
        else:
            status_code = 400
    elif isinstance(exc, AIModelException):
        if "timeout" in exc.details.get("error_type", ""):
            status_code = 504
        elif "quota" in exc.details.get("error_type", ""):
            status_code = 429
        else:
            status_code = 502

    error_response = ErrorResponse(
        error_code=exc.error_code.value,
        message=exc.message,
        details=exc.details,
        timestamp=datetime.now().isoformat(),
    )

    return JSONResponse(status_code=status_code, content=error_response.dict())


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("老克智能体服务启动中...")

    # 初始化日志系统
    setup_logging()

    # 初始化智能体
    agent = get_agent()
    logger.info("老克智能体初始化完成")

    yield

    # 关闭
    logger.info("老克智能体服务关闭中...")
    await shutdown_agent()
    logger.info("老克智能体服务已关闭")


# 创建FastAPI应用
def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    config = get_config()

    app = FastAPI(
        title="老克智能体服务",
        description="中医知识传播和教育的智能体服务",
        version=config.service.version,
        debug=config.service.debug,
        lifespan=lifespan,
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.server.cors_allowed_origins,
        allow_credentials=config.server.cors_allow_credentials,
        allow_methods=config.server.cors_allowed_methods,
        allow_headers=config.server.cors_allowed_headers,
    )

    # 添加请求日志中间件
    app.middleware("http")(request_logging_middleware)

    # 添加异常处理器
    app.add_exception_handler(Exception, exception_handler)

    return app


# 创建app实例
app = create_app()


# API路由
@app.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check():
    """健康检查接口"""
    from datetime import datetime

    config = get_config()
    agent = get_agent()

    # 检查各组件状态
    checks = {"agent": "healthy", "config": "healthy", "logging": "healthy"}

    # 检查智能体状态
    try:
        stats = agent.get_stats()
        checks["agent_stats"] = stats
    except Exception as e:
        checks["agent"] = f"unhealthy: {e}"

    overall_status = (
        "healthy"
        if all(
            status == "healthy" or isinstance(status, dict)
            for status in checks.values()
        )
        else "unhealthy"
    )

    return HealthResponse(
        status=overall_status,
        version=config.service.version,
        timestamp=datetime.now().isoformat(),
        checks=checks,
    )


@app.get("/stats", response_model=StatsResponse, summary="获取统计信息")
async def get_stats():
    """获取服务统计信息"""
    agent = get_agent()
    stats = agent.get_stats()

    return StatsResponse(**stats)


@app.post("/sessions", response_model=SessionResponse, summary="创建会话")
async def create_session(
    request: SessionCreateRequest, user_id: str = Depends(get_user_id)
):
    """创建新的对话会话"""
    agent = get_agent()

    # 使用请求中的user_id，如果没有则使用依赖注入的
    actual_user_id = request.user_id or user_id

    session_id = await agent.create_session(
        user_id=actual_user_id, metadata=request.metadata
    )

    session_info = await agent.get_session_info(session_id)

    return SessionResponse(**session_info)


@app.get(
    "/sessions/{session_id}", response_model=SessionResponse, summary="获取会话信息"
)
async def get_session_info(session_id: str):
    """获取指定会话的信息"""
    agent = get_agent()
    session_info = await agent.get_session_info(session_id)

    return SessionResponse(**session_info)


@app.delete("/sessions/{session_id}", summary="终止会话")
async def terminate_session(session_id: str):
    """终止指定的对话会话"""
    agent = get_agent()
    await agent.terminate_session(session_id)

    return {"message": "会话已终止", "session_id": session_id}


@app.post(
    "/sessions/{session_id}/chat", response_model=ChatResponse, summary="对话接口"
)
async def chat(session_id: str, request: ChatRequest):
    """与老克智能体进行对话"""
    agent = get_agent()

    if request.stream:
        # 流式响应
        async def generate_stream():
            async for chunk in agent.chat(
                session_id=session_id, message=request.message, stream=True
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-ID": session_id,
            },
        )
    else:
        # 普通响应
        response = await agent.chat(
            session_id=session_id, message=request.message, stream=False
        )

        return ChatResponse(
            response=response, session_id=session_id, metadata=request.metadata
        )


@app.get(
    "/sessions/{session_id}/history",
    response_model=HistoryResponse,
    summary="获取对话历史",
)
async def get_conversation_history(session_id: str, limit: Optional[int] = None):
    """获取指定会话的对话历史"""
    agent = get_agent()

    messages = await agent.get_conversation_history(session_id, limit)

    return HistoryResponse(
        session_id=session_id, messages=[MessageResponse(**msg) for msg in messages]
    )


# 根路径
@app.get("/", summary="服务信息")
async def root():
    """服务根路径，返回基本信息"""
    config = get_config()

    return {
        "service": "老克智能体服务",
        "version": config.service.version,
        "description": "中医知识传播和教育的智能体服务",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "sessions": "/sessions",
            "chat": "/sessions/{session_id}/chat",
            "history": "/sessions/{session_id}/history",
        },
    }


@app.get("/info", summary="服务信息")
async def service_info():
    """获取服务详细信息"""
    config = get_config()

    return {
        "service_name": config.service.name,
        "version": config.service.version,
        "environment": config.service.environment,
        "description": "中医知识传播和教育的智能体服务",
        "status": "running",
        "features": {
            "chat": True,
            "streaming": True,
            "session_management": True,
            "accessibility": True,
        },
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "sessions": "/sessions",
            "chat": "/sessions/{session_id}/chat",
            "history": "/sessions/{session_id}/history",
        },
    }


if __name__ == "__main__":
    import uvicorn

    config = get_config()

    uvicorn.run(
        "laoke_service.api.routes:app",
        host=config.server.rest_host,
        port=config.server.rest_port,
        workers=config.server.rest_workers,
        reload=config.service.debug,
        log_level="info",
    )
