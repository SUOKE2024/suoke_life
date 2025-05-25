#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
soer-service 增强版API网关
集成FastAPI、中间件、追踪、监控等功能
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# 导入服务和通用组件
from services.agent_services.soer_service.internal.service.enhanced_health_service import (
    get_health_service, HealthDataRequest, LifestyleRequest, EmotionAnalysisRequest,
    SensorDataRequest, DataType, HealthGoal, EmotionType
)
from services.common.observability.tracing import get_tracer, trace_middleware

logger = logging.getLogger(__name__)

# Pydantic模型定义
class HealthDataRequestModel(BaseModel):
    """健康数据分析请求模型"""
    user_id: str = Field(..., description="用户ID")
    data_types: List[str] = Field(..., description="数据类型列表")
    time_range_days: int = Field(7, description="时间范围（天）")
    include_trends: bool = Field(True, description="是否包含趋势分析")
    include_predictions: bool = Field(False, description="是否包含预测")

class LifestyleRequestModel(BaseModel):
    """生活方式建议请求模型"""
    user_id: str = Field(..., description="用户ID")
    current_habits: Dict[str, Any] = Field(..., description="当前习惯")
    health_goals: List[str] = Field(..., description="健康目标")
    constitution_type: Optional[str] = Field(None, description="体质类型")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="偏好设置")

class EmotionAnalysisRequestModel(BaseModel):
    """情绪分析请求模型"""
    user_id: str = Field(..., description="用户ID")
    input_type: str = Field(..., description="输入类型")
    input_data: Any = Field(..., description="输入数据")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="上下文")

class SensorDataRequestModel(BaseModel):
    """传感器数据处理请求模型"""
    user_id: str = Field(..., description="用户ID")
    device_id: str = Field(..., description="设备ID")
    sensor_type: str = Field(..., description="传感器类型")
    data_points: List[Dict[str, Any]] = Field(..., description="数据点")
    timestamp_range: Dict[str, str] = Field(..., description="时间戳范围")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: float
    service: str
    version: str = "1.0.0"

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
    timestamp: float
    request_id: str = None

# 全局变量
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("soer-service API网关启动中...")
    app_state['start_time'] = time.time()
    app_state['request_count'] = 0
    
    # 初始化服务
    health_service = await get_health_service()
    app_state['health_service'] = health_service
    
    logger.info("soer-service API网关启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("soer-service API网关关闭中...")
    if 'health_service' in app_state:
        await app_state['health_service'].cleanup()
    logger.info("soer-service API网关关闭完成")

# 创建FastAPI应用
app = FastAPI(
    title="Soer Service API",
    description="索儿智能体服务 - 健康数据分析和生活习惯培养",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 生产环境应该限制具体主机
)

# 添加追踪中间件
app.add_middleware(trace_middleware)

# 请求计数中间件
@app.middleware("http")
async def request_counter_middleware(request: Request, call_next):
    """请求计数中间件"""
    app_state['request_count'] = app_state.get('request_count', 0) + 1
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = f"soer_{int(time.time() * 1000)}"
    
    return response

# 异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP_{exc.status_code}",
            message=exc.detail,
            timestamp=time.time(),
            request_id=request.headers.get("X-Request-ID")
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="服务内部错误，请稍后重试",
            timestamp=time.time(),
            request_id=request.headers.get("X-Request-ID")
        ).dict()
    )

# 依赖注入
async def get_health_service_dependency():
    """获取健康服务依赖"""
    return app_state.get('health_service')

# API路由
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service="soer-service"
    )

@app.get("/metrics")
async def get_metrics():
    """获取服务指标"""
    health_service = app_state.get('health_service')
    service_stats = health_service.get_health_status() if health_service else {}
    
    return {
        "service": "soer-service",
        "uptime": time.time() - app_state.get('start_time', time.time()),
        "total_requests": app_state.get('request_count', 0),
        "service_stats": service_stats,
        "timestamp": time.time()
    }

@app.post("/api/v1/health/analyze")
async def analyze_health_data(
    request: HealthDataRequestModel,
    health_service = Depends(get_health_service_dependency)
):
    """分析健康数据"""
    if not health_service:
        raise HTTPException(status_code=503, detail="健康服务不可用")
    
    try:
        # 转换请求模型
        service_request = HealthDataRequest(
            user_id=request.user_id,
            data_types=[DataType(dt) for dt in request.data_types],
            time_range_days=request.time_range_days,
            include_trends=request.include_trends,
            include_predictions=request.include_predictions
        )
        
        # 调用服务
        result = await health_service.analyze_health_data(service_request)
        
        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "analysis_summary": result.analysis_summary,
                "health_trends": result.health_trends,
                "risk_indicators": result.risk_indicators,
                "recommendations": result.recommendations,
                "next_check_date": result.next_check_date
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"健康数据分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康数据分析失败: {str(e)}")

@app.post("/api/v1/lifestyle/advice")
async def generate_lifestyle_advice(
    request: LifestyleRequestModel,
    health_service = Depends(get_health_service_dependency)
):
    """生成生活方式建议"""
    if not health_service:
        raise HTTPException(status_code=503, detail="健康服务不可用")
    
    try:
        # 转换请求模型
        service_request = LifestyleRequest(
            user_id=request.user_id,
            current_habits=request.current_habits,
            health_goals=[HealthGoal(hg) for hg in request.health_goals],
            constitution_type=request.constitution_type,
            preferences=request.preferences
        )
        
        # 调用服务
        result = await health_service.generate_lifestyle_advice(service_request)
        
        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "habit_analysis": result.habit_analysis,
                "improvement_plan": result.improvement_plan,
                "daily_schedule": result.daily_schedule,
                "nutrition_plan": result.nutrition_plan,
                "exercise_plan": result.exercise_plan
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"生活方式建议生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"生活方式建议生成失败: {str(e)}")

@app.post("/api/v1/emotion/analyze")
async def analyze_emotion(
    request: EmotionAnalysisRequestModel,
    health_service = Depends(get_health_service_dependency)
):
    """分析情绪状态"""
    if not health_service:
        raise HTTPException(status_code=503, detail="健康服务不可用")
    
    try:
        # 转换请求模型
        service_request = EmotionAnalysisRequest(
            user_id=request.user_id,
            input_type=request.input_type,
            input_data=request.input_data,
            context=request.context
        )
        
        # 调用服务
        result = await health_service.analyze_emotion(service_request)
        
        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "detected_emotions": result.detected_emotions,
                "emotion_score": result.emotion_score,
                "tcm_emotion_mapping": result.tcm_emotion_mapping,
                "intervention_suggestions": result.intervention_suggestions
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"情绪分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"情绪分析失败: {str(e)}")

@app.post("/api/v1/sensor/process")
async def process_sensor_data(
    request: SensorDataRequestModel,
    health_service = Depends(get_health_service_dependency)
):
    """处理传感器数据"""
    if not health_service:
        raise HTTPException(status_code=503, detail="健康服务不可用")
    
    try:
        # 转换请求模型
        service_request = SensorDataRequest(
            user_id=request.user_id,
            device_id=request.device_id,
            sensor_type=request.sensor_type,
            data_points=request.data_points,
            timestamp_range=request.timestamp_range
        )
        
        # 调用服务
        result = await health_service.process_sensor_data(service_request)
        
        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "processed_data": result.processed_data,
                "anomalies": result.anomalies,
                "insights": result.insights,
                "data_quality_score": result.data_quality_score
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"传感器数据处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"传感器数据处理失败: {str(e)}")

@app.get("/api/v1/health/dashboard/{user_id}")
async def get_health_dashboard(
    user_id: str,
    health_service = Depends(get_health_service_dependency)
):
    """获取健康仪表板"""
    if not health_service:
        raise HTTPException(status_code=503, detail="健康服务不可用")
    
    try:
        # 模拟获取健康仪表板数据
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "overall_score": 85,
                "health_status": "良好",
                "recent_trends": [
                    {
                        "metric": "心率",
                        "value": 72,
                        "trend": "stable",
                        "change": "+2%"
                    },
                    {
                        "metric": "睡眠质量",
                        "value": 8.2,
                        "trend": "improving",
                        "change": "+5%"
                    },
                    {
                        "metric": "运动量",
                        "value": 8500,
                        "trend": "stable",
                        "change": "+1%"
                    }
                ],
                "alerts": [
                    {
                        "type": "reminder",
                        "message": "今日水分摄入不足，建议多喝水",
                        "priority": "medium"
                    }
                ],
                "recommendations": [
                    "建议保持规律的睡眠时间",
                    "增加有氧运动频率",
                    "注意饮食营养均衡"
                ]
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"获取健康仪表板失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取健康仪表板失败: {str(e)}")

@app.get("/api/v1/health/report/{user_id}")
async def generate_health_report(
    user_id: str,
    period: str = "weekly",
    health_service = Depends(get_health_service_dependency)
):
    """生成健康报告"""
    if not health_service:
        raise HTTPException(status_code=503, detail="健康服务不可用")
    
    try:
        # 模拟生成健康报告
        await asyncio.sleep(0.3)
        
        return {
            "success": True,
            "data": {
                "report_id": f"report_{int(time.time() * 1000)}",
                "user_id": user_id,
                "period": period,
                "generated_at": time.time(),
                "summary": {
                    "overall_score": 82,
                    "improvement_areas": ["睡眠质量", "运动强度"],
                    "strengths": ["心率稳定", "饮食规律"]
                },
                "detailed_analysis": {
                    "cardiovascular": {
                        "score": 85,
                        "status": "良好",
                        "recommendations": ["保持规律运动"]
                    },
                    "sleep": {
                        "score": 78,
                        "status": "一般",
                        "recommendations": ["改善睡眠环境", "规律作息"]
                    },
                    "nutrition": {
                        "score": 88,
                        "status": "优秀",
                        "recommendations": ["继续保持"]
                    }
                },
                "action_plan": [
                    {
                        "goal": "改善睡眠质量",
                        "actions": ["22:30前上床", "睡前1小时不使用电子设备"],
                        "timeline": "2周"
                    }
                ]
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"生成健康报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成健康报告失败: {str(e)}")

@app.get("/api/v1/data-types")
async def get_data_types():
    """获取数据类型列表"""
    return {
        "success": True,
        "data": {
            "data_types": [
                {
                    "code": "heart_rate",
                    "name": "心率",
                    "description": "心跳频率数据"
                },
                {
                    "code": "blood_pressure",
                    "name": "血压",
                    "description": "血压测量数据"
                },
                {
                    "code": "sleep",
                    "name": "睡眠",
                    "description": "睡眠质量和时长数据"
                },
                {
                    "code": "steps",
                    "name": "步数",
                    "description": "日常步行数据"
                },
                {
                    "code": "weight",
                    "name": "体重",
                    "description": "体重变化数据"
                },
                {
                    "code": "mood",
                    "name": "情绪",
                    "description": "情绪状态数据"
                },
                {
                    "code": "stress",
                    "name": "压力",
                    "description": "压力水平数据"
                }
            ]
        },
        "timestamp": time.time()
    }

@app.get("/api/v1/health-goals")
async def get_health_goals():
    """获取健康目标列表"""
    return {
        "success": True,
        "data": {
            "health_goals": [
                {
                    "code": "weight_loss",
                    "name": "减重",
                    "description": "健康减重目标"
                },
                {
                    "code": "fitness",
                    "name": "健身",
                    "description": "提升身体素质"
                },
                {
                    "code": "sleep_improvement",
                    "name": "改善睡眠",
                    "description": "提高睡眠质量"
                },
                {
                    "code": "stress_reduction",
                    "name": "减压",
                    "description": "降低压力水平"
                },
                {
                    "code": "nutrition",
                    "name": "营养",
                    "description": "改善营养状况"
                }
            ]
        },
        "timestamp": time.time()
    }

@app.get("/api/v1/emotion-types")
async def get_emotion_types():
    """获取情绪类型列表"""
    return {
        "success": True,
        "data": {
            "emotion_types": [
                {
                    "code": "happy",
                    "name": "快乐",
                    "description": "积极愉悦的情绪"
                },
                {
                    "code": "sad",
                    "name": "悲伤",
                    "description": "低落的情绪状态"
                },
                {
                    "code": "angry",
                    "name": "愤怒",
                    "description": "生气的情绪状态"
                },
                {
                    "code": "anxious",
                    "name": "焦虑",
                    "description": "担忧不安的情绪"
                },
                {
                    "code": "calm",
                    "name": "平静",
                    "description": "宁静平和的状态"
                },
                {
                    "code": "excited",
                    "name": "兴奋",
                    "description": "激动兴奋的状态"
                },
                {
                    "code": "stressed",
                    "name": "压力",
                    "description": "感受到压力的状态"
                }
            ]
        },
        "timestamp": time.time()
    }

# 启动配置
if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api_gateway:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    ) 