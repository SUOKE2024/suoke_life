"""
enhanced_api_gateway - 索克生活项目模块
"""

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from services.agent_services.xiaoke_service.internal.service.enhanced_resource_service import (
from services.common.observability.tracing import trace_middleware
from typing import Any
import asyncio
import logging
import time
import uvicorn

#!/usr/bin/env python3
"""
xiaoke-service 增强版API网关
集成FastAPI、中间件、追踪、监控等功能
"""



# 导入服务和通用组件
    ConstitutionType,
    ProductRequest,
    ResourceRequest,
    get_resource_service,
)

logger = logging.getLogger(__name__)


# Pydantic模型定义
class ResourceRequestModel(BaseModel):
    """资源请求模型"""

    user_id: str = Field(..., description="用户ID")
    resource_type: str = Field(..., description="资源类型")
    location: str = Field(None, description="位置")
    constitution_type: str = Field("balanced", description="体质类型")
    urgency_level: str = Field("normal", description="紧急程度")
    preferences: dict[str, Any] = Field(default_factory=dict, description="偏好设置")


class ProductRequestModel(BaseModel):
    """产品请求模型"""

    user_id: str = Field(..., description="用户ID")
    product_category: str = Field(..., description="产品类别")
    constitution_type: str = Field("balanced", description="体质类型")
    dietary_restrictions: list[str] = Field(
        default_factory=list, description="饮食限制"
    )
    budget_range: str = Field("medium", description="预算范围")
    preferences: dict[str, Any] = Field(default_factory=dict, description="偏好设置")


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
    logger.info("xiaoke-service API网关启动中...")
    app_state["start_time"] = time.time()
    app_state["request_count"] = 0

    # 初始化服务
    resource_service = await get_resource_service()
    app_state["resource_service"] = resource_service

    logger.info("xiaoke-service API网关启动完成")

    yield

    # 关闭时清理
    logger.info("xiaoke-service API网关关闭中...")
    if "resource_service" in app_state:
        await app_state["resource_service"].cleanup()
    logger.info("xiaoke-service API网关关闭完成")


# 创建FastAPI应用
app = FastAPI(
    title="Xiaoke Service API",
    description="小克智能体服务 - 医疗资源调度和产品管理",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
    allowed_hosts=["*"],  # 生产环境应该限制具体主机
)

# 添加追踪中间件
app.add_middleware(trace_middleware)


# 请求计数中间件
@app.middleware("http")
async def request_counter_middleware(request: Request, call_next):
    """请求计数中间件"""
    app_state["request_count"] = app_state.get("request_count", 0) + 1

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = f"xiaoke_{int(time.time() * 1000)}"

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
            request_id=request.headers.get("X-Request-ID"),
        ).dict(),
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
            request_id=request.headers.get("X-Request-ID"),
        ).dict(),
    )


# 依赖注入
async async def get_resource_service_dependency(
    """获取资源服务依赖"""
    return app_state.get("resource_service")


# API路由
@cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy", timestamp=time.time(), servi@cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
ce="xiaoke-service"
    )


@app.get("/metrics")
async async def get_metrics(
    """获取服务指标"""
    resource_service = app_state.get("resource_service")
    service_stats = resource_service.get_health_status() if resource_service else {}

    return {
        "service": "xiaoke-service",
        "uptime": time.time() - app_state.get("start_time", time.time()),
        "total_requests": app_state.get("request_count", 0)@limiter.limit("100/minute")  # 每分钟100次请求
,
        "service_stats": service_stats,
        "timestamp": time.time(),
    }


@app.post("/api/v1/resources/search")
async def search_resources(
    request: ResourceRequestModel,
    resource_service=Depends(get_resource_service_dependency),
):
    """搜索医疗资源"""
    if not resource_service:
        raise HTTPException(status_code=503, detail="资源服务不可用")

    try:
        # 转换请求模型
        service_request = ResourceRequest(
            user_id=request.user_id,
            resource_type=request.resource_type,
            location=request.location,
            constitution_type=ConstitutionType(request.constitution_type),
            urgency_level=request.urgency_level,
            preferences=request.preferences,
        )

        # 调用服务
        result = await resource_service.search_resources(service_request)

        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "resources": result.matched_resources,
                "availability": result.availability_info,
                "cost_estimate": result.cost_estimate,
                "recommendations": result.recommendations,
                "booking_options": result.booking_options,
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp,
        }

    except@limiter.limit("100/minute")  # 每分钟100次请求
 Exception as e:
        logger.error(f"资源搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"资源搜索失败: {e!s}")


@app.post("/api/v1/products/recommend")
async def recommend_products(
    request: ProductRequestModel,
    resource_service=Depends(get_resource_service_dependency),
):
    """推荐产品"""
    if not resource_service:
        raise HTTPException(status_code=503, detail="资源服务不可用")

    try:
        # 转换请求模型
        service_request = ProductRequest(
            user_id=request.user_id,
            product_category=request.product_category,
            constitution_type=ConstitutionType(request.constitution_type),
            dietary_restrictions=request.dietary_restrictions,
            budget_range=request.budget_range,
            preferences=request.preferences,
        )

        # 调用服务
        result = await resource_service.recommend_products(service_request)

        return {
            "success": True,
            "data": {
                "request_id": result.request_id,
                "products": result.recommended_products,
                "nutrition_analysis": result.nutrition_analysis,
                "tcm_benefits": result.tcm_benefits,
                "customization_options": result.customization_options,
                "blockchain_info": result.blockchain_info,
            },
            "processing_time": result.processing_time,
            "timestamp": result.timestamp,
       @limiter.limit("100/minute")  # 每分钟100次请求
 }

    except Exception as e:
        logger.error(f"产品推荐失败: {e}")
        raise HT@cache(expire=300)  # 5分钟缓存
TPException(status_code=500, detail=f"产品推荐失败: {e!s}")


@app.get("/api/v1/resources/{resource_id}")
async def get_resource_details(
    resource_id: str, resource_service=Depends(get_resource_service_dependency)
):
    """获取资源详情"""
    if not resource_service:
        raise HTTPException(status_code=503, detail="资源服务不可用")

    try:
        # 模拟获取资源详情
        await asyncio.sleep(0.1)

        return {
            "success": True,
            "data": {
                "resource_id": resource_id,
                "name": "示例医疗资源",
                "type": "医院",
                "location": "北京市朝阳区",
                "rating": 4.8,
                "services": ["内科", "外科", "中医科"],
                "contact": {
                    "phone": "010-12345678",
                    "address": "北京市朝阳区示例路123号",
                },
                "availability": {
                    "today": True,
                    "next_available": "2024-12-20T09:00:00Z",
             @limiter.limit("100/minute")  # 每分钟100次请求
   },
            },
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"获取资源详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取资源详情失败: {e!s}")


@app.post("/api/v1/booking")
async def create_booking(
    booking_data: dict[str, Any],
    resource_service=Depends(get_resource_service_dependency),
):
    """创建预订"""
    if not resource_service:
        raise HTTPException(status_code=503, detail="资源服务不可用")

    try:
        # 模拟创建预订
        await asyncio.sleep(0.2)

        booking_id = f"booking_{int(time.time() * 1000)}"

        return {
            "success": True,
            "data": {
                "booking_id": booking_id,
                "status": "confirmed",
                "resource_id": booking_data.get("resource_id"),
                "user_id": booking_data.get("user_id"),
                "appointment_time": booking_data.get("appointment_time"),
                "confirmation_code": f"CONF{booking_id[-6:].upper()}",
                "payment_required": True,
                "@limiter.limit("100/minute")  # 每分钟100次请求
payment_amount": 200.0,
            },
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"创建@cache(expire=300)  # 5分钟缓存
预订失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建预订失败: {e!s}")


@app.get("/api/v1/constitution-types")
async async def get_constitution_types(
    """获取体质类型列表"""
    return {
        "success": True,
        "data": {
            "constitution_types": [
                {
                    "code": "balanced",
                    "name": "平和质",
                    "description": "阴阳气血调和，体质平和",
                },
                {
                    "code": "qi_xu",
                    "name": "气虚质",
                    "description": "元气不足，疲乏无力",
                },
                {
                    "code": "yang_xu",
                    "name": "阳虚质",
                    "description": "阳气不足，畏寒怕冷",
                },
                {
                    "code": "yin_xu",
                    "name": "阴虚质",
                    "description": "阴液亏少，虚热内扰",
                },
                {
                    "code": "tan_shi",
                    "name": "痰湿质",
                    "description": "痰湿凝聚，形体肥胖",
                },
                {
                    "code": "shi_re",
                    "name": "湿热质",
                    "description": "湿热内蕴，面垢油腻",
                },
                {
                    "code": "xue_yu",
                    "name": "血瘀质",
                    "description": "血行不畅，肤色晦暗",
                },
                {
                    "code": "qi_yu",
                    "name": "气郁质",
                    "descri@limiter.limit("100/minute")  # 每分钟100次请求
ption": "气机郁滞，情志不畅",
                },
                {
                    "code": "te_bing",
                    "name": "特禀质",
                    "d@cache(expire=300)  # 5分钟缓存
escription": "先天失常，过敏体质",
                },
            ]
        },
        "timestamp": time.time(),
    }


@app.get("/api/v1/product-categories")
async async def get_product_categories(
    """获取产品类别列表"""
    return {
        "success": True,
        "data": {
            "categories": [
                {
                    "code": "herbal_tea",
                    "name": "养生茶饮",
                    "description": "根据体质调配的养生茶",
                },
                {
                    "code": "health_food",
                    "name": "健康食品",
                    "description": "营养丰富的健康食品",
                },
                {
                    "code": "supplements",
                    "name": "营养补充",
                    "description": "天然营养补充剂",
                },
                {
                    "code": "organic_produce",
                    "name": "有机农产品",
                    "description": "有机种植的新鲜农产品",
                },
                {
                    "code": "tcm_products",
                    "name": "中医产品",
                    "description": "传统中医调理产品",
                },
            ]
        },
        "timestamp": time.time(),
    }


# 启动配置
if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api_gateway:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
