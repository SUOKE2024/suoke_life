"""
简化版触诊服务主程序
只包含基本功能，用于测试和演示
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .config import get_settings
from .models import (
    SuccessResponse,
    ErrorResponse,
    SessionCreateRequest,
    SessionResponse,
    SensorDataInput,
    AnalysisRequest,
    SessionStatus,
    SessionType,
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus 指标
REQUEST_COUNT = Counter("palpation_requests_total", "Total requests", ["method", "endpoint"])
REQUEST_DURATION = Histogram("palpation_request_duration_seconds", "Request duration")

# 全局配置
settings = get_settings()

# 模拟数据存储
sessions_db: Dict[str, Dict[str, Any]] = {}
sensor_data_db: Dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("触诊服务启动中...")
    yield
    logger.info("触诊服务关闭中...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="索克生活 - 触诊服务",
        description="基于AI的中医触诊分析服务",
        version=settings.service.version,
        lifespan=lifespan,
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins_list,
        allow_credentials=True,
        allow_methods=settings.security.cors_methods_list,
        allow_headers=settings.security.cors_headers_list,
    )

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
        return SuccessResponse(
            message="服务运行正常",
            data={
                "service": settings.service.name,
                "version": settings.service.version,
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
            },
        )

    # Prometheus指标端点
    @app.get("/metrics")
    async def metrics():
        """Prometheus指标"""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # 创建触诊会话
    @app.post("/palpation/sessions", response_model=SessionResponse)
    async def create_session(request: SessionCreateRequest):
        """创建新的触诊会话"""
        REQUEST_COUNT.labels(method="POST", endpoint="/palpation/sessions").inc()
        
        try:
            session_id = str(uuid4())
            session_data = {
                "id": session_id,
                "user_id": request.user_id,
                "session_type": request.session_type,
                "status": SessionStatus.ACTIVE,
                "start_time": datetime.now(),
                "end_time": None,
                "metadata": request.metadata,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            
            sessions_db[session_id] = session_data
            sensor_data_db[session_id] = []
            
            logger.info(f"创建触诊会话: {session_id} for user: {request.user_id}")
            
            return SessionResponse(**session_data)
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # 获取会话信息
    @app.get("/palpation/sessions/{session_id}", response_model=SessionResponse)
    async def get_session(session_id: str):
        """获取会话信息"""
        REQUEST_COUNT.labels(method="GET", endpoint="/palpation/sessions/{session_id}").inc()
        
        if session_id not in sessions_db:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return SessionResponse(**sessions_db[session_id])

    # 上传传感器数据
    @app.post("/palpation/sessions/{session_id}/data")
    async def upload_sensor_data(session_id: str, data: SensorDataInput):
        """上传传感器数据"""
        REQUEST_COUNT.labels(method="POST", endpoint="/palpation/sessions/{session_id}/data").inc()
        
        if session_id not in sessions_db:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        try:
            # 存储传感器数据
            sensor_data_db[session_id].append({
                "sensor_type": data.sensor_type,
                "data_points": [dp.dict() for dp in data.data_points],
                "quality_indicators": data.quality_indicators,
                "timestamp": datetime.now().isoformat(),
            })
            
            logger.info(f"接收传感器数据: {session_id}, 类型: {data.sensor_type}, 数据点: {len(data.data_points)}")
            
            return SuccessResponse(
                message="数据上传成功",
                data={
                    "session_id": session_id,
                    "sensor_type": data.sensor_type,
                    "data_points_count": len(data.data_points),
                }
            )
            
        except Exception as e:
            logger.error(f"上传数据失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # 分析数据
    @app.post("/palpation/sessions/{session_id}/analyze")
    async def analyze_session(session_id: str, request: AnalysisRequest):
        """分析会话数据"""
        REQUEST_COUNT.labels(method="POST", endpoint="/palpation/sessions/{session_id}/analyze").inc()
        
        if session_id not in sessions_db:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        try:
            # 模拟分析过程
            sensor_data = sensor_data_db.get(session_id, [])
            
            # 简单的模拟分析结果
            analysis_result = {
                "session_id": session_id,
                "analysis_types": request.analysis_types,
                "results": {
                    "overall_health_score": 75.5,
                    "confidence": 0.85,
                    "sensor_data_count": len(sensor_data),
                    "analysis_summary": "基于传感器数据的初步分析显示健康状况良好",
                },
                "recommendations": [
                    "继续保持良好的生活习惯",
                    "建议定期进行健康检查",
                    "注意饮食均衡和适量运动",
                ],
                "timestamp": datetime.now().isoformat(),
            }
            
            logger.info(f"完成会话分析: {session_id}")
            
            return SuccessResponse(
                message="分析完成",
                data=analysis_result
            )
            
        except Exception as e:
            logger.error(f"分析失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # 获取配置信息
    @app.get("/config")
    async def get_config():
        """获取服务配置"""
        REQUEST_COUNT.labels(method="GET", endpoint="/config").inc()
        
        return SuccessResponse(
            message="配置信息",
            data={
                "service": {
                    "name": settings.service.name,
                    "version": settings.service.version,
                    "environment": settings.service.env,
                },
                "fusion": {
                    "enabled_modalities": settings.fusion.enabled_modalities,
                    "algorithm": settings.fusion.algorithm,
                    "weights": settings.fusion.fusion_weights,
                },
            }
        )

    # 获取统计信息
    @app.get("/stats")
    async def get_stats():
        """获取服务统计"""
        REQUEST_COUNT.labels(method="GET", endpoint="/stats").inc()
        
        return SuccessResponse(
            message="统计信息",
            data={
                "total_sessions": len(sessions_db),
                "active_sessions": len([s for s in sessions_db.values() if s["status"] == SessionStatus.ACTIVE]),
                "total_sensor_data": sum(len(data) for data in sensor_data_db.values()),
                "uptime": "运行中",
            }
        )

    return app


def main():
    """主函数"""
    import uvicorn
    
    app = create_app()
    
    logger.info(f"启动触诊服务: {settings.service.host}:{settings.service.port}")
    logger.info(f"环境: {settings.service.env}")
    logger.info(f"调试模式: {settings.service.debug}")
    
    uvicorn.run(
        app,
        host=settings.service.host,
        port=settings.service.port,
        log_level="info" if not settings.service.debug else "debug",
        reload=settings.service.debug,
    )


if __name__ == "__main__":
    main() 