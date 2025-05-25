#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laoke-service 增强版API网关
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
from services.agent_services.laoke_service.internal.service.enhanced_knowledge_service import (
    get_knowledge_service, KnowledgeRequest, LearningPathRequest, CommunityContentRequest,
    ContentType, DifficultyLevel, LearningStyle
)
from services.common.observability.tracing import get_tracer, trace_middleware

logger = logging.getLogger(__name__)

# Pydantic模型定义
class KnowledgeRequestModel(BaseModel):
    """知识搜索请求模型"""
    user_id: str = Field(..., description="用户ID")
    topic: str = Field(..., description="搜索主题")
    content_type: Optional[str] = Field(None, description="内容类型")
    difficulty_level: Optional[str] = Field(None, description="难度级别")
    learning_style: Optional[str] = Field(None, description="学习风格")
    keywords: Optional[List[str]] = Field(default_factory=list, description="关键词")
    max_results: int = Field(10, description="最大结果数")

class LearningPathRequestModel(BaseModel):
    """学习路径请求模型"""
    user_id: str = Field(..., description="用户ID")
    learning_goals: List[str] = Field(..., description="学习目标")
    current_level: str = Field("beginner", description="当前水平")
    preferred_content_types: List[str] = Field(default_factory=list, description="偏好内容类型")
    time_commitment: str = Field("weekly", description="时间投入")
    duration_weeks: int = Field(12, description="持续周数")

class CommunityContentRequestModel(BaseModel):
    """社区内容请求模型"""
    user_id: str = Field(..., description="用户ID")
    content_type: str = Field("all", description="内容类型")
    category: Optional[str] = Field(None, description="分类")
    sort_by: str = Field("latest", description="排序方式")
    limit: int = Field(20, description="限制数量")

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
    logger.info("laoke-service API网关启动中...")
    app_state['start_time'] = time.time()
    app_state['request_count'] = 0
    
    # 初始化服务
    knowledge_service = await get_knowledge_service()
    app_state['knowledge_service'] = knowledge_service
    
    logger.info("laoke-service API网关启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("laoke-service API网关关闭中...")
    if 'knowledge_service' in app_state:
        await app_state['knowledge_service'].cleanup()
    logger.info("laoke-service API网关关闭完成")

# 创建FastAPI应用
app = FastAPI(
    title="Laoke Service API",
    description="老克智能体服务 - 知识内容管理和学习路径推荐",
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
    response.headers["X-Request-ID"] = f"laoke_{int(time.time() * 1000)}"
    
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
async def get_knowledge_service_dependency():
    """获取知识服务依赖"""
    return app_state.get('knowledge_service')

# API路由
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service="laoke-service"
    )

@app.get("/metrics")
async def get_metrics():
    """获取服务指标"""
    knowledge_service = app_state.get('knowledge_service')
    service_stats = knowledge_service.get_health_status() if knowledge_service else {}
    
    return {
        "service": "laoke-service",
        "uptime": time.time() - app_state.get('start_time', time.time()),
        "total_requests": app_state.get('request_count', 0),
        "service_stats": service_stats,
        "timestamp": time.time()
    }

@app.post("/api/v1/knowledge/search")
async def search_knowledge(
    request: KnowledgeRequestModel,
    knowledge_service = Depends(get_knowledge_service_dependency)
):
    """搜索知识内容"""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="知识服务不可用")
    
    try:
        # 转换请求模型
        service_request = KnowledgeRequest(
            user_id=request.user_id,
            topic=request.topic,
            content_type=ContentType(request.content_type) if request.content_type else None,
            difficulty_level=DifficultyLevel(request.difficulty_level) if request.difficulty_level else None,
            learning_style=LearningStyle(request.learning_style) if request.learning_style else None,
            keywords=request.keywords,
            max_results=request.max_results
        )
        
        # 调用服务
        result = await knowledge_service.search_knowledge(service_request)
        
        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "matched_content": result.matched_content,
                "recommendations": result.recommendations,
                "related_topics": result.related_topics,
                "learning_suggestions": result.learning_suggestions
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"知识搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"知识搜索失败: {str(e)}")

@app.post("/api/v1/learning-path/generate")
async def generate_learning_path(
    request: LearningPathRequestModel,
    knowledge_service = Depends(get_knowledge_service_dependency)
):
    """生成学习路径"""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="知识服务不可用")
    
    try:
        # 转换请求模型
        service_request = LearningPathRequest(
            user_id=request.user_id,
            learning_goals=request.learning_goals,
            current_level=DifficultyLevel(request.current_level),
            preferred_content_types=[ContentType(ct) for ct in request.preferred_content_types],
            time_commitment=request.time_commitment,
            duration_weeks=request.duration_weeks
        )
        
        # 调用服务
        result = await knowledge_service.generate_learning_path(service_request)
        
        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "path_id": result.path_id,
                "path_name": result.path_name,
                "modules": result.modules,
                "estimated_duration": result.estimated_duration,
                "progress_tracking": result.progress_tracking,
                "milestones": result.milestones
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"学习路径生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"学习路径生成失败: {str(e)}")

@app.post("/api/v1/community/content")
async def get_community_content(
    request: CommunityContentRequestModel,
    knowledge_service = Depends(get_knowledge_service_dependency)
):
    """获取社区内容"""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="知识服务不可用")
    
    try:
        # 转换请求模型
        service_request = CommunityContentRequest(
            user_id=request.user_id,
            content_type=request.content_type,
            category=request.category,
            sort_by=request.sort_by,
            limit=request.limit
        )
        
        # 调用服务
        result = await knowledge_service.get_community_content(service_request)
        
        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "content_items": result.content_items,
                "trending_topics": result.trending_topics,
                "recommended_users": result.recommended_users,
                "engagement_stats": result.engagement_stats
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"社区内容获取失败: {e}")
        raise HTTPException(status_code=500, detail=f"社区内容获取失败: {str(e)}")

@app.get("/api/v1/content/{content_id}")
async def get_content_details(
    content_id: str,
    knowledge_service = Depends(get_knowledge_service_dependency)
):
    """获取内容详情"""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="知识服务不可用")
    
    try:
        # 模拟获取内容详情
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "content_id": content_id,
                "title": "中医基础理论详解",
                "type": "article",
                "difficulty": "intermediate",
                "duration": "45分钟",
                "author": "中医专家",
                "rating": 4.9,
                "description": "深入浅出地介绍中医基础理论，包括阴阳五行、脏腑经络等核心概念",
                "content_outline": [
                    "阴阳学说的基本概念",
                    "五行理论及其应用",
                    "脏腑经络系统",
                    "病因病机分析"
                ],
                "prerequisites": ["中医入门", "基础概念"],
                "related_content": ["中医诊断学", "方剂学基础"],
                "tags": ["中医理论", "基础知识", "阴阳五行"]
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"获取内容详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取内容详情失败: {str(e)}")

@app.get("/api/v1/learning-path/{path_id}")
async def get_learning_path_details(
    path_id: str,
    knowledge_service = Depends(get_knowledge_service_dependency)
):
    """获取学习路径详情"""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="知识服务不可用")
    
    try:
        # 模拟获取学习路径详情
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "path_id": path_id,
                "path_name": "中医基础学习路径",
                "description": "系统学习中医基础理论和实践应用",
                "total_modules": 8,
                "estimated_duration": "12周",
                "difficulty": "beginner_to_intermediate",
                "enrollment_count": 1250,
                "completion_rate": 0.78,
                "modules": [
                    {
                        "module_id": "mod_01",
                        "title": "中医概论",
                        "duration": "1周",
                        "status": "available"
                    },
                    {
                        "module_id": "mod_02", 
                        "title": "阴阳五行学说",
                        "duration": "2周",
                        "status": "locked"
                    }
                ],
                "instructor": {
                    "name": "李教授",
                    "title": "中医学博士",
                    "experience": "20年教学经验"
                }
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"获取学习路径详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取学习路径详情失败: {str(e)}")

@app.post("/api/v1/learning-path/{path_id}/enroll")
async def enroll_learning_path(
    path_id: str,
    user_data: Dict[str, Any],
    knowledge_service = Depends(get_knowledge_service_dependency)
):
    """报名学习路径"""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="知识服务不可用")
    
    try:
        # 模拟报名处理
        await asyncio.sleep(0.2)
        
        enrollment_id = f"enroll_{int(time.time() * 1000)}"
        
        return {
            "success": True,
            "data": {
                "enrollment_id": enrollment_id,
                "path_id": path_id,
                "user_id": user_data.get("user_id"),
                "status": "enrolled",
                "start_date": "2024-12-20",
                "expected_completion": "2025-03-14",
                "access_level": "full",
                "progress": {
                    "current_module": 1,
                    "completion_percentage": 0,
                    "time_spent": 0
                }
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"报名学习路径失败: {e}")
        raise HTTPException(status_code=500, detail=f"报名学习路径失败: {str(e)}")

@app.get("/api/v1/content-types")
async def get_content_types():
    """获取内容类型列表"""
    return {
        "success": True,
        "data": {
            "content_types": [
                {
                    "code": "article",
                    "name": "文章",
                    "description": "图文并茂的知识文章"
                },
                {
                    "code": "video",
                    "name": "视频",
                    "description": "视频教学内容"
                },
                {
                    "code": "audio",
                    "name": "音频",
                    "description": "音频讲解内容"
                },
                {
                    "code": "course",
                    "name": "课程",
                    "description": "系统性课程内容"
                },
                {
                    "code": "quiz",
                    "name": "测验",
                    "description": "知识测验和练习"
                }
            ]
        },
        "timestamp": time.time()
    }

@app.get("/api/v1/difficulty-levels")
async def get_difficulty_levels():
    """获取难度级别列表"""
    return {
        "success": True,
        "data": {
            "difficulty_levels": [
                {
                    "code": "beginner",
                    "name": "初级",
                    "description": "适合初学者"
                },
                {
                    "code": "intermediate",
                    "name": "中级",
                    "description": "有一定基础"
                },
                {
                    "code": "advanced",
                    "name": "高级",
                    "description": "深入学习"
                },
                {
                    "code": "expert",
                    "name": "专家级",
                    "description": "专业深度内容"
                }
            ]
        },
        "timestamp": time.time()
    }

@app.get("/api/v1/topics")
async def get_popular_topics():
    """获取热门主题"""
    return {
        "success": True,
        "data": {
            "popular_topics": [
                {
                    "topic": "中医基础",
                    "content_count": 156,
                    "popularity_score": 0.95
                },
                {
                    "topic": "养生保健",
                    "content_count": 203,
                    "popularity_score": 0.92
                },
                {
                    "topic": "针灸推拿",
                    "content_count": 89,
                    "popularity_score": 0.88
                },
                {
                    "topic": "中药方剂",
                    "content_count": 134,
                    "popularity_score": 0.85
                },
                {
                    "topic": "食疗养生",
                    "content_count": 178,
                    "popularity_score": 0.83
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
        port=8002,
        reload=True,
        log_level="info"
    ) 