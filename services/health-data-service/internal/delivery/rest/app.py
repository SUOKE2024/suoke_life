#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务REST API应用
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from loguru import logger
import uuid
import json
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from .dependencies import get_current_user, get_service, get_token_header
from .routes import health_data, wearables, tcm, insights, profiles
from internal.service.health_data_service import HealthDataService


def create_app(config: Dict[str, Any], service: Optional[HealthDataService] = None) -> FastAPI:
    """
    创建FastAPI应用
    
    Args:
        config: 配置信息
        service: 健康数据服务实例
        
    Returns:
        FastAPI应用实例
    """
    # 应用标题
    title = "索克生活 - 健康数据服务"
    description = """
    健康数据服务API提供了用户健康数据的管理、中医体质分析与评估、健康洞察和健康指标等功能。
    
    主要功能:
    * 健康数据管理: 存储、检索和管理各类健康数据
    * 可穿戴设备集成: 支持Apple Health、Fitbit、Garmin、小米等设备数据导入
    * 中医体质分析: 基于四诊数据进行中医体质辨识与分析
    * 健康趋势与洞察: 分析健康数据趋势，提供有价值的健康洞察
    * 健康数据存证: 通过区块链确保健康数据的真实性
    """
    
    # 创建FastAPI应用
    app = FastAPI(
        title=title,
        description=description,
        version="1.0.0",
        docs_url=None,  # 禁用默认的Swagger UI路径
        redoc_url=None  # 禁用默认的ReDoc路径
    )
    
    # 自定义OpenAPI和文档URL
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{title} - Swagger UI",
            oauth2_redirect_url="/docs/oauth2-redirect",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )

    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{title} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
        )

    @app.get("/openapi.json", include_in_schema=False)
    async def get_open_api_endpoint():
        return get_openapi(
            title=title,
            description=description,
            version="1.0.0",
            routes=app.routes,
        )
    
    # 添加中间件
    
    # CORS中间件
    cors_config = config.get('cors', {})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get('allow_origins', ["*"]),
        allow_credentials=cors_config.get('allow_credentials', True),
        allow_methods=cors_config.get('allow_methods', ["*"]),
        allow_headers=cors_config.get('allow_headers', ["*"]),
    )
    
    # 请求ID中间件
    @app.middleware("http")
    async def add_request_id_middleware(request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        # 将请求ID添加到请求状态中
        request.state.request_id = request_id
        
        # 处理请求
        start_time = datetime.utcnow()
        
        try:
            response = await call_next(request)
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            
            # 计算请求处理时间
            process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            
            return response
        except Exception as e:
            logger.error(f"请求处理出错 [request_id={request_id}]: {str(e)}")
            
            # 返回500错误
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "服务器内部错误",
                    "code": "internal_error",
                    "request_id": request_id
                }
            )
    
    # 异常处理
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理HTTP异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "code": getattr(exc, "code", "http_error"),
                "request_id": getattr(request.state, "request_id", str(uuid.uuid4()))
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理所有未捕获的异常"""
        logger.error(f"未捕获的异常 [request_id={getattr(request.state, 'request_id', 'unknown')}]: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "服务器内部错误",
                "code": "internal_error",
                "request_id": getattr(request.state, "request_id", str(uuid.uuid4()))
            }
        )
    
    # 添加服务依赖
    app.state.config = config
    app.state.service = service
    
    # 注册路由
    app.include_router(
        health_data.router,
        prefix="/api/v1/health-data",
        tags=["健康数据"]
    )
    
    app.include_router(
        wearables.router,
        prefix="/api/v1/wearables",
        tags=["可穿戴设备"]
    )
    
    app.include_router(
        tcm.router,
        prefix="/api/v1/tcm",
        tags=["中医体质"]
    )
    
    app.include_router(
        insights.router,
        prefix="/api/v1/insights",
        tags=["健康洞察"]
    )
    
    app.include_router(
        profiles.router,
        prefix="/api/v1/health-profile",
        tags=["健康档案"]
    )
    
    # 添加健康检查路由
    @app.get("/health", tags=["系统"])
    async def health_check():
        """健康检查"""
        if service:
            status, details = await service.health_check()
            return {"status": status, "details": details}
        return {"status": "ok", "details": {"ready": True}}
    
    # 添加元数据路由
    @app.get("/api/meta/health-data-types", tags=["元数据"])
    async def get_health_data_types():
        """获取健康数据类型"""
        return [
            {"code": "steps", "name": "步数"},
            {"code": "heart_rate", "name": "心率"},
            {"code": "sleep", "name": "睡眠"},
            {"code": "blood_pressure", "name": "血压"},
            {"code": "blood_glucose", "name": "血糖"},
            {"code": "body_temperature", "name": "体温"},
            {"code": "oxygen_saturation", "name": "血氧饱和度"},
            {"code": "respiratory_rate", "name": "呼吸率"},
            {"code": "body_mass", "name": "体重"},
            {"code": "body_fat", "name": "体脂率"},
            {"code": "activity", "name": "活动"},
            {"code": "water_intake", "name": "饮水量"},
            {"code": "nutrition", "name": "营养"},
            {"code": "medication", "name": "用药"},
            {"code": "symptom", "name": "症状"},
            {"code": "pulse", "name": "脉象"},
            {"code": "tongue", "name": "舌象"},
            {"code": "face", "name": "面色"},
            {"code": "voice", "name": "声音"},
            {"code": "custom", "name": "自定义"}
        ]
    
    @app.get("/api/meta/device-types", tags=["元数据"])
    async def get_device_types():
        """获取设备类型"""
        return [
            {"code": "apple_health", "name": "Apple健康"},
            {"code": "fitbit", "name": "Fitbit"},
            {"code": "garmin", "name": "Garmin"},
            {"code": "xiaomi", "name": "小米"},
            {"code": "tcm_device", "name": "中医设备"},
            {"code": "manual_entry", "name": "手动录入"},
            {"code": "other", "name": "其他"}
        ]
    
    @app.get("/api/meta/tcm-constitution-types", tags=["元数据"])
    async def get_tcm_constitution_types():
        """获取中医体质类型"""
        return [
            {"code": "balanced", "name": "平和质"},
            {"code": "qi_deficiency", "name": "气虚质"},
            {"code": "yang_deficiency", "name": "阳虚质"},
            {"code": "yin_deficiency", "name": "阴虚质"},
            {"code": "phlegm_dampness", "name": "痰湿质"},
            {"code": "dampness_heat", "name": "湿热质"},
            {"code": "blood_stasis", "name": "血瘀质"},
            {"code": "qi_depression", "name": "气郁质"},
            {"code": "special", "name": "特禀质"}
        ]
    
    logger.info("FastAPI应用创建成功")
    return app 