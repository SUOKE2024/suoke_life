"""
REST API 接口模块

提供音频分析和中医诊断的REST API接口。
"""

import asyncio
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from ..config.settings import get_settings
from ..core.audio_analyzer import AudioAnalyzer
from ..core.tcm_analyzer import TCMFeatureExtractor
from ..models.audio_models import (
    AnalysisRequest,
    AnalysisResult,
    AudioFormat,
    AudioMetadata,
    BatchAnalysisRequest,
    BatchAnalysisResult
)
from ..models.tcm_models import TCMAnalysisConfig, TCMDiagnosis
from ..utils.cache import get_cache
from ..utils.performance import async_timer, get_performance_monitor
from ..utils.validation import validate_comprehensive_request, audio_validator

logger = structlog.get_logger(__name__)

# 安全认证
security = HTTPBearer()

# 全局组件
settings = get_settings()
audio_analyzer = AudioAnalyzer()
tcm_analyzer = TCMFeatureExtractor()
cache = get_cache()
performance_monitor = get_performance_monitor()


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    timestamp: float = Field(default_factory=time.time)
    version: str = "1.0.0"
    service: str = "listen-service"


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
    timestamp: float = Field(default_factory=time.time)
    request_id: Optional[str] = None


class AnalysisStatusResponse(BaseModel):
    """分析状态响应"""
    request_id: str
    status: str
    progress: float
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


# 创建FastAPI应用
app = FastAPI(
    title="Listen Service API",
    description="音频分析和中医诊断服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# 依赖注入
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前用户"""
    # 这里应该实现真正的JWT验证
    # 暂时返回模拟用户ID
    return "user_123"


async def get_request_id() -> str:
    """生成请求ID"""
    return str(uuid.uuid4())


# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=str(exc.detail),
            request_id=getattr(request.state, 'request_id', None)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error("未处理的异常", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message="内部服务器错误",
            request_id=getattr(request.state, 'request_id', None)
        ).dict()
    )


# 中间件
@app.middleware("http")
async def request_middleware(request, call_next):
    """请求中间件"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # 记录请求
    logger.info(
        "请求开始",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host
    )
    
    try:
        response = await call_next(request)
        
        # 记录响应
        duration = time.time() - start_time
        logger.info(
            "请求完成",
            request_id=request_id,
            status_code=response.status_code,
            duration=duration
        )
        
        # 记录性能指标
        performance_monitor.record_request(
            method=request.method,
            endpoint=str(request.url.path),
            status=response.status_code,
            duration=duration
        )
        
        response.headers["X-Request-ID"] = request_id
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "请求失败",
            request_id=request_id,
            error=str(e),
            duration=duration,
            exc_info=True
        )
        raise


# API路由
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse()


@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径"""
    return {
        "service": "listen-service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.post("/api/v1/audio/upload", response_model=Dict[str, Any])
async def upload_audio(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    request_id: str = Depends(get_request_id)
):
    """上传音频文件"""
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 检查文件格式
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in audio_validator.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}"
            )
        
        # 保存文件
        upload_dir = Path(settings.get_upload_dir())
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{request_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 验证音频文件
        validation_result = audio_validator.validate_audio_file(file_path)
        
        logger.info("文件上传成功", file_path=str(file_path), user_id=user_id)
        
        return {
            "request_id": request_id,
            "file_path": str(file_path),
            "file_size": len(content),
            "validation": validation_result,
            "status": "uploaded"
        }
        
    except Exception as e:
        logger.error("文件上传失败", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/audio/analyze", response_model=AnalysisResult)
@async_timer
async def analyze_audio(
    request: AnalysisRequest,
    user_id: str = Depends(get_current_user),
    request_id: str = Depends(get_request_id)
):
    """分析音频文件"""
    try:
        # 验证请求
        validate_comprehensive_request(request.dict())
        
        # 检查缓存
        cache_key = cache.generate_key(request.file_path, request.analysis_type)
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            logger.info("使用缓存结果", cache_key=cache_key)
            return AudioAnalysisResult(**cached_result)
        
        # 执行分析
        start_time = time.time()
        
        # 基础音频分析
        audio_features = await audio_analyzer.extract_features(request.file_path)
        
        # 根据分析类型执行不同的分析
        result_data = {
            "request_id": request_id,
            "file_path": request.file_path,
            "analysis_type": request.analysis_type,
            "audio_features": audio_features,
            "timestamp": time.time(),
            "processing_time": time.time() - start_time
        }
        
        if request.analysis_type in ["tcm", "comprehensive"]:
            # 中医分析
            tcm_features = await tcm_analyzer.extract_features(request.file_path)
            result_data["tcm_features"] = tcm_features
        
        # 创建结果对象
        result = AudioAnalysisResult(**result_data)
        
        # 缓存结果
        await cache.set(cache_key, result.dict(), ttl=3600)
        
        # 记录性能指标
        performance_monitor.record_audio_analysis(
            analysis_type=request.analysis_type,
            duration=result.processing_time
        )
        
        logger.info(
            "音频分析完成",
            request_id=request_id,
            analysis_type=request.analysis_type,
            processing_time=result.processing_time
        )
        
        return result
        
    except Exception as e:
        logger.error("音频分析失败", error=str(e), request_id=request_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tcm/diagnose", response_model=TCMDiagnosis)
@async_timer
async def tcm_diagnose(
    request: TCMAnalysisConfig,
    user_id: str = Depends(get_current_user),
    request_id: str = Depends(get_request_id)
):
    """中医诊断"""
    try:
        # 验证请求
        validate_comprehensive_request(request.dict())
        
        # 检查缓存
        cache_key = cache.generate_key("tcm_diagnose", request.file_path, request.constitution_type)
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            logger.info("使用缓存的中医诊断结果", cache_key=cache_key)
            return TCMDiagnosis(**cached_result)
        
        # 执行中医诊断
        start_time = time.time()
        
        diagnosis = await tcm_analyzer.diagnose(
            file_path=request.file_path,
            constitution_type=request.constitution_type,
            symptoms=request.symptoms,
            context=request.context
        )
        
        diagnosis.request_id = request_id
        diagnosis.processing_time = time.time() - start_time
        
        # 缓存结果
        await cache.set(cache_key, diagnosis.dict(), ttl=1800)
        
        logger.info(
            "中医诊断完成",
            request_id=request_id,
            constitution_type=request.constitution_type,
            processing_time=diagnosis.processing_time
        )
        
        return diagnosis
        
    except Exception as e:
        logger.error("中医诊断失败", error=str(e), request_id=request_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/audio/batch-analyze", response_model=BatchAnalysisResult)
@async_timer
async def batch_analyze_audio(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    request_id: str = Depends(get_request_id)
):
    """批量分析音频文件"""
    try:
        # 验证批量请求
        if len(request.file_paths) > 10:
            raise HTTPException(status_code=400, detail="批量分析最多支持10个文件")
        
        # 启动后台任务
        background_tasks.add_task(
            process_batch_analysis,
            request_id,
            request.file_paths,
            request.analysis_type,
            user_id
        )
        
        return BatchAnalysisResult(
            request_id=request_id,
            status="processing",
            total_files=len(request.file_paths),
            completed_files=0,
            failed_files=0,
            results=[]
        )
        
    except Exception as e:
        logger.error("批量分析启动失败", error=str(e), request_id=request_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analysis/status/{request_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(request_id: str):
    """获取分析状态"""
    try:
        # 从缓存中获取状态
        status_key = f"analysis_status_{request_id}"
        status_data = await cache.get(status_key)
        
        if not status_data:
            raise HTTPException(status_code=404, detail="分析请求不存在")
        
        return AnalysisStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取分析状态失败", error=str(e), request_id=request_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats(user_id: str = Depends(get_current_user)):
    """获取缓存统计信息"""
    try:
        stats = cache.get_stats()
        return stats
    except Exception as e:
        logger.error("获取缓存统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/performance/stats", response_model=Dict[str, Any])
async def get_performance_stats(user_id: str = Depends(get_current_user)):
    """获取性能统计信息"""
    try:
        stats = performance_monitor.get_performance_summary()
        return stats
    except Exception as e:
        logger.error("获取性能统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/cache/clear")
async def clear_cache(user_id: str = Depends(get_current_user)):
    """清空缓存"""
    try:
        success = await cache.clear()
        if success:
            logger.info("缓存清空成功", user_id=user_id)
            return {"message": "缓存清空成功"}
        else:
            raise HTTPException(status_code=500, detail="缓存清空失败")
    except Exception as e:
        logger.error("清空缓存失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# 后台任务
async def process_batch_analysis(
    request_id: str,
    file_paths: List[str],
    analysis_type: str,
    user_id: str
):
    """处理批量分析"""
    try:
        total_files = len(file_paths)
        completed_files = 0
        failed_files = 0
        results = []
        
        # 更新状态
        async def update_status(status: str, progress: float, message: str = None):
            status_data = {
                "request_id": request_id,
                "status": status,
                "progress": progress,
                "message": message,
                "result": {
                    "total_files": total_files,
                    "completed_files": completed_files,
                    "failed_files": failed_files,
                    "results": results
                }
            }
            await cache.set(f"analysis_status_{request_id}", status_data, ttl=3600)
        
        await update_status("processing", 0.0, "开始批量分析")
        
        # 处理每个文件
        for i, file_path in enumerate(file_paths):
            try:
                # 分析单个文件
                audio_features = await audio_analyzer.extract_features(file_path)
                
                result = {
                    "file_path": file_path,
                    "status": "success",
                    "audio_features": audio_features
                }
                
                if analysis_type in ["tcm", "comprehensive"]:
                    tcm_features = await tcm_analyzer.extract_features(file_path)
                    result["tcm_features"] = tcm_features
                
                results.append(result)
                completed_files += 1
                
                logger.info(f"文件分析完成 {i+1}/{total_files}", file_path=file_path)
                
            except Exception as e:
                logger.error(f"文件分析失败 {i+1}/{total_files}", file_path=file_path, error=str(e))
                results.append({
                    "file_path": file_path,
                    "status": "failed",
                    "error": str(e)
                })
                failed_files += 1
            
            # 更新进度
            progress = (i + 1) / total_files
            await update_status("processing", progress, f"已处理 {i+1}/{total_files} 个文件")
        
        # 完成
        await update_status("completed", 1.0, "批量分析完成")
        
        logger.info(
            "批量分析完成",
            request_id=request_id,
            total_files=total_files,
            completed_files=completed_files,
            failed_files=failed_files
        )
        
    except Exception as e:
        logger.error("批量分析失败", request_id=request_id, error=str(e))
        await update_status("failed", 0.0, f"批量分析失败: {str(e)}")


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Listen Service 启动")
    
    # 初始化组件
    await audio_analyzer.initialize()
    await tcm_analyzer.initialize()
    
    # 启动性能监控
    await performance_monitor.start_monitoring_if_needed()
    
    logger.info("Listen Service 启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Listen Service 关闭")
    
    # 清理资源
    await cache.cleanup()
    await performance_monitor.cleanup()
    
    logger.info("Listen Service 关闭完成")


# 导出应用实例
def create_app() -> FastAPI:
    """创建应用实例"""
    return app


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "listen_service.delivery.rest_api:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )