#!/usr/bin/env python3
"""
问诊服务增强版API网关
提供RESTful API接口，支持智能问诊、会话管理、批量分析和实时交互
"""

import logging
from typing import Any, Optional

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 导入通用组件
from services.common.observability.tracing import SpanKind, get_tracer

# 导入服务
from services.diagnostic_services.inquiry_service.internal.enhanced_inquiry_service import (
    EnhancedInquiryService,
)
import uvicorn

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="问诊服务API",
    description="索克生活问诊服务，提供智能化的中医问诊数据采集和分析功能",
    version="2.0.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
inquiry_service: EnhancedInquiryService | None = None


# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict[str, Any]):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


# 请求模型
class StartSessionRequest(BaseModel):
    """开始会话请求"""

    patient_id: str = Field(..., description="患者ID")
    chief_complaint: str = Field(..., description="主诉")
    metadata: dict[str, Any] | None = Field(None, description="元数据")


class SubmitAnswerRequest(BaseModel):
    """提交答案请求"""

    session_id: str = Field(..., description="会话ID")
    question_id: str = Field(..., description="问题ID")
    answer: Any = Field(..., description="答案")
    confidence: float = Field(1.0, description="置信度", ge=0.0, le=1.0)


class BatchAnalyzeRequest(BaseModel):
    """批量分析请求"""

    session_ids: list[str] = Field(..., description="会话ID列表")


# 响应模型
class SessionResponse(BaseModel):
    """会话响应"""

    session_id: str
    patient_id: str
    questions: list[dict[str, Any]]
    status: str
    start_time: str


class QuestionResponse(BaseModel):
    """问题响应"""

    question_id: str
    category: str
    question_type: str
    question: str
    options: list[str] | None
    required: bool


class AnalysisResponse(BaseModel):
    """分析响应"""

    session_id: str
    patient_id: str
    chief_complaint: str
    present_illness: str
    symptoms: list[dict[str, Any]]
    syndrome_analysis: dict[str, Any]
    recommendations: list[str]
    confidence_score: float
    processing_time_ms: float


class ServiceStats(BaseModel):
    """服务统计"""

    total_sessions: int
    completed_sessions: int
    active_sessions: int
    cache_hit_rate: float
    average_questions_per_session: float
    average_processing_time_ms: float
    batch_processed: int


# 中间件
@app.middleware("http")
async def add_tracing(request, call_next):
    """添加分布式追踪"""
    tracer = get_tracer("inquiry-api")

    with tracer.start_span(
        f"{request.method} {request.url.path}", kind=SpanKind.SERVER
    ) as span:
        # 添加请求信息到span
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.scheme", request.url.scheme)
        span.set_attribute("http.host", request.url.hostname)
        span.set_attribute("http.target", request.url.path)

        # 处理请求
        response = await call_next(request)

        # 添加响应信息到span
        span.set_attribute("http.status_code", response.status_code)

        return response


# 依赖项
async def get_inquiry_service() -> EnhancedInquiryService:
    """获取问诊服务实例"""
    global inquiry_service
    if not inquiry_service:
        raise HTTPException(status_code=503, detail="问诊服务未初始化")
    return inquiry_service


# API端点
@app.post("/api/v1/inquiry/sessions", response_model=SessionResponse)
async def start_session(
    request: StartSessionRequest,
    service: EnhancedInquiryService = Depends(get_inquiry_service),
):
    """
    开始新的问诊会话

    创建一个新的问诊会话，并返回初始问题集
    """
    try:
        session = await service.start_inquiry_session(
            patient_id=request.patient_id,
            chief_complaint=request.chief_complaint,
            metadata=request.metadata,
        )

        # 转换问题格式
        questions = []
        for q in session.questions[:10]:  # 返回前10个问题
            questions.append(
                {
                    "question_id": q.id,
                    "category": q.category.value,
                    "question_type": q.question_type.value,
                    "question": q.question,
                    "options": q.options,
                    "required": q.required,
                }
            )

        return SessionResponse(
            session_id=session.session_id,
            patient_id=session.patient_id,
            questions=questions,
            status=session.status,
            start_time=session.start_time.isoformat(),
        )

    except Exception as e:
        logger.error(f"开始会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inquiry/answers", response_model=Optional[QuestionResponse])
async def submit_answer(
    request: SubmitAnswerRequest,
    service: EnhancedInquiryService = Depends(get_inquiry_service),
):
    """
    提交问题答案

    提交答案并获取下一个问题（如果有）
    """
    try:
        next_question = await service.submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer,
            confidence=request.confidence,
        )

        if next_question:
            return QuestionResponse(
                question_id=next_question.id,
                category=next_question.category.value,
                question_type=next_question.question_type.value,
                question=next_question.question,
                options=next_question.options,
                required=next_question.required,
            )

        return None

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"提交答案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/inquiry/sessions/{session_id}")
async def get_session(
    session_id: str, service: EnhancedInquiryService = Depends(get_inquiry_service)
):
    """
    获取会话详情

    返回会话的当前状态和已回答的问题
    """
    try:
        session = service.active_sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 构建响应
        answered_questions = []
        for answer in session.answers:
            question = next(
                (q for q in session.questions if q.id == answer.question_id), None
            )
            if question:
                answered_questions.append(
                    {
                        "question": question.question,
                        "answer": answer.answer,
                        "confidence": answer.confidence,
                        "timestamp": answer.timestamp.isoformat(),
                    }
                )

        return {
            "session_id": session.session_id,
            "patient_id": session.patient_id,
            "status": session.status,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "total_questions": len(session.questions),
            "answered_questions": len(session.answers),
            "answers": answered_questions,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inquiry/analyze/{session_id}", response_model=AnalysisResponse)
async def analyze_session(
    session_id: str, service: EnhancedInquiryService = Depends(get_inquiry_service)
):
    """
    分析问诊结果

    对完成的问诊会话进行综合分析，生成诊断建议
    """
    try:
        result = await service.analyze_inquiry(session_id)

        return AnalysisResponse(
            session_id=result.session_id,
            patient_id=result.patient_id,
            chief_complaint=result.chief_complaint,
            present_illness=result.present_illness,
            symptoms=result.symptoms,
            syndrome_analysis=result.syndrome_analysis,
            recommendations=result.recommendations,
            confidence_score=result.confidence_score,
            processing_time_ms=result.processing_time_ms,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"分析会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inquiry/batch/analyze")
async def batch_analyze(
    request: BatchAnalyzeRequest,
    service: EnhancedInquiryService = Depends(get_inquiry_service),
):
    """
    批量分析问诊结果

    同时分析多个问诊会话，提高处理效率
    """
    try:
        results = await service.batch_analyze(request.session_ids)

        return {
            "status": "success",
            "analyzed_count": len(results),
            "results": [
                {
                    "session_id": r.session_id,
                    "patient_id": r.patient_id,
                    "syndrome": r.syndrome_analysis.get("primary", "未明确"),
                    "confidence": r.confidence_score,
                }
                for r in results
            ],
        }

    except Exception as e:
        logger.error(f"批量分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/inquiry/{session_id}")
async def websocket_inquiry(
    websocket: WebSocket,
    session_id: str,
    service: EnhancedInquiryService = Depends(get_inquiry_service),
):
    """
    WebSocket实时问诊接口

    支持实时交互式问诊，提供更好的用户体验
    """
    await manager.connect(session_id, websocket)

    try:
        # 发送初始问题
        session = service.active_sessions.get(session_id)
        if session:
            initial_question = session.questions[0] if session.questions else None
            if initial_question:
                await manager.send_message(
                    session_id,
                    {
                        "type": "question",
                        "data": {
                            "question_id": initial_question.id,
                            "question": initial_question.question,
                            "options": initial_question.options,
                            "question_type": initial_question.question_type.value,
                        },
                    },
                )

        # 处理消息
        while True:
            data = await websocket.receive_json()

            if data["type"] == "answer":
                # 提交答案
                next_question = await service.submit_answer(
                    session_id=session_id,
                    question_id=data["question_id"],
                    answer=data["answer"],
                    confidence=data.get("confidence", 1.0),
                )

                if next_question:
                    # 发送下一个问题
                    await manager.send_message(
                        session_id,
                        {
                            "type": "question",
                            "data": {
                                "question_id": next_question.id,
                                "question": next_question.question,
                                "options": next_question.options,
                                "question_type": next_question.question_type.value,
                            },
                        },
                    )
                else:
                    # 问诊结束，开始分析
                    await manager.send_message(
                        session_id,
                        {"type": "analyzing", "message": "问诊结束，正在分析..."},
                    )

                    # 分析结果
                    result = await service.analyze_inquiry(session_id)

                    # 发送结果
                    await manager.send_message(
                        session_id,
                        {
                            "type": "result",
                            "data": {
                                "syndrome": result.syndrome_analysis.get(
                                    "primary", "未明确"
                                ),
                                "confidence": result.confidence_score,
                                "recommendations": result.recommendations,
                            },
                        },
                    )

                    break

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket断开连接: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(session_id)


@app.get("/api/v1/inquiry/stats", response_model=ServiceStats)
async def get_stats(service: EnhancedInquiryService = Depends(get_inquiry_service)):
    """
    获取服务统计信息

    包括会话统计、缓存命中率、性能指标等
    """
    try:
        stats = await service.get_service_stats()

        return ServiceStats(
            total_sessions=stats["total_sessions"],
            completed_sessions=stats["completed_sessions"],
            active_sessions=stats["active_sessions"],
            cache_hit_rate=stats["cache_hit_rate"],
            average_questions_per_session=stats["average_questions_per_session"],
            average_processing_time_ms=stats["average_processing_time_ms"],
            batch_processed=stats["batch_processed"],
        )

    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/inquiry/metrics")
async def get_metrics(service: EnhancedInquiryService = Depends(get_inquiry_service)):
    """
    获取Prometheus格式的指标
    """
    try:
        stats = await service.get_service_stats()

        # 构建Prometheus格式的指标
        metrics = []

        # 会话指标
        metrics.append("# HELP inquiry_total_sessions Total number of inquiry sessions")
        metrics.append("# TYPE inquiry_total_sessions counter")
        metrics.append(f"inquiry_total_sessions {stats['total_sessions']}")

        metrics.append("# HELP inquiry_completed_sessions Number of completed sessions")
        metrics.append("# TYPE inquiry_completed_sessions counter")
        metrics.append(f"inquiry_completed_sessions {stats['completed_sessions']}")

        metrics.append("# HELP inquiry_active_sessions Number of active sessions")
        metrics.append("# TYPE inquiry_active_sessions gauge")
        metrics.append(f"inquiry_active_sessions {stats['active_sessions']}")

        # 缓存指标
        metrics.append("# HELP inquiry_cache_hit_rate Cache hit rate")
        metrics.append("# TYPE inquiry_cache_hit_rate gauge")
        metrics.append(f"inquiry_cache_hit_rate {stats['cache_hit_rate']}")

        # 性能指标
        metrics.append(
            "# HELP inquiry_average_processing_time_ms Average processing time"
        )
        metrics.append("# TYPE inquiry_average_processing_time_ms gauge")
        metrics.append(
            f"inquiry_average_processing_time_ms {stats['average_processing_time_ms']}"
        )

        metrics.append(
            "# HELP inquiry_average_questions_per_session Average questions per session"
        )
        metrics.append("# TYPE inquiry_average_questions_per_session gauge")
        metrics.append(
            f"inquiry_average_questions_per_session {stats['average_questions_per_session']}"
        )

        return "\n".join(metrics)

    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 健康检查端点
@app.get("/health")
async def health_check():
    """基本健康检查"""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check(
    service: EnhancedInquiryService = Depends(get_inquiry_service),
):
    """就绪检查"""
    try:
        # 检查服务状态
        stats = await service.get_service_stats()

        if stats["question_bank_size"] == 0:
            raise HTTPException(status_code=503, detail="问题库未初始化")

        return {
            "status": "ready",
            "question_bank_size": stats["question_bank_size"],
            "active_sessions": stats["active_sessions"],
        }

    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global inquiry_service

    logger.info("问诊服务API启动中...")

    # 初始化服务
    try:
        # 加载配置
        config = {"service": {"name": "inquiry-service", "version": "2.0.0"}}

        inquiry_service = EnhancedInquiryService(config)
        await inquiry_service.initialize()

        logger.info("问诊服务初始化成功")

    except Exception as e:
        logger.error(f"问诊服务初始化失败: {e}")
        raise


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global inquiry_service

    logger.info("问诊服务API关闭中...")

    # 清理资源
    try:
        if inquiry_service:
            await inquiry_service.close()
            logger.info("问诊服务清理完成")
    except Exception as e:
        logger.error(f"问诊服务清理失败: {e}")


# 主函数
if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api_gateway:app",
        host="0.0.0.0",
        port=8091,
        reload=True,
        log_level="info",
    )
