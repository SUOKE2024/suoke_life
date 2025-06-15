#!/usr/bin/env python3
"""
简化版脉诊服务器
用于测试基本功能
"""

import asyncio
import json
import sys
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from palpation_service.config import get_settings
from palpation_service.internal.enhanced_palpation_service import (
    EnhancedPalpationService,
    PulseDataPoint,
    PulseAnalysisRequest
)

# 全局服务实例
palpation_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global palpation_service
    
    # 启动
    try:
        config = {"test": True}
        palpation_service = EnhancedPalpationService(config)
        await palpation_service.initialize()
        print("✅ 脉诊服务初始化成功")
    except Exception as e:
        print(f"❌ 脉诊服务初始化失败: {e}")
        raise
    
    yield
    
    # 关闭
    if palpation_service:
        await palpation_service.close()
        print("✅ 脉诊服务已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="脉诊服务",
    description="索克生活脉诊分析服务",
    version="1.0.0",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 请求模型
class PulseDataRequest(BaseModel):
    patient_id: str
    pulse_data: list[dict]
    duration: float
    sample_rate: int
    metadata: dict = {}

class SessionCreateRequest(BaseModel):
    patient_id: str
    metadata: dict = {}

# 响应模型
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str

class SessionResponse(BaseModel):
    session_id: str
    patient_id: str
    created_at: str
    status: str



@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="palpation-service",
        version="1.0.0"
    )

@app.get("/ready")
async def readiness_check():
    """就绪检查"""
    if palpation_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """创建分析会话"""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.patient_id}"
    
    return SessionResponse(
        session_id=session_id,
        patient_id=request.patient_id,
        created_at=datetime.now().isoformat(),
        status="active"
    )

@app.post("/api/v1/analyze")
async def analyze_pulse(request: PulseDataRequest):
    """分析脉象数据"""
    if palpation_service is None:
        raise HTTPException(status_code=503, detail="Service not available")
    
    try:
        # 转换脉象数据
        pulse_data = []
        for point_data in request.pulse_data:
            point = PulseDataPoint(
                timestamp=point_data.get("timestamp", 0),
                amplitude=point_data.get("amplitude", 0),
                pressure=point_data.get("pressure", 0),
                channel=point_data.get("channel", 0)
            )
            pulse_data.append(point)
        
        # 分析脉象
        result = await palpation_service.analyze_pulse(
            patient_id=request.patient_id,
            pulse_data=pulse_data,
            duration=request.duration,
            sample_rate=request.sample_rate,
            metadata=request.metadata
        )
        
        return {
            "request_id": result.request_id,
            "patient_id": result.patient_id,
            "analysis_time": datetime.now().isoformat(),
            "quality_score": result.quality_score,
            "processing_time_ms": result.processing_time_ms,
            "pulse_characteristics": result.pulse_characteristics,
            "syndrome_indicators": result.syndrome_indicators,
            "recommendations": result.recommendations,
            "confidence_score": 0.85  # 默认置信度
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/stats")
async def get_stats():
    """获取服务统计"""
    if palpation_service is None:
        raise HTTPException(status_code=503, detail="Service not available")
    
    try:
        stats = await palpation_service.get_service_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "palpation-service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "create_session": "/api/v1/sessions",
            "analyze": "/api/v1/analyze",
            "stats": "/api/v1/stats"
        }
    }

def main():
    """主函数"""
    try:
        settings = get_settings()
        print(f"🚀 启动脉诊服务...")
        print(f"   服务地址: http://{settings.service.host}:{settings.service.port}")
        print(f"   调试模式: {settings.service.debug}")
        
        uvicorn.run(
            "simple_server:app",
            host=settings.service.host,
            port=settings.service.port,
            log_level="info" if settings.service.debug else "warning",
            reload=False  # 禁用reload以避免问题
        )
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 