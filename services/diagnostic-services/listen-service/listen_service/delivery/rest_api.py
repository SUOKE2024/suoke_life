"""
REST API接口实现

提供HTTP接口用于音频分析和中医诊断服务。
基于FastAPI框架，支持异步处理、文件上传、错误处理等功能。
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import structlog

from ..core.audio_analyzer import AudioAnalyzer
from ..core.tcm_analyzer import TCMFeatureExtractor
from ..models.audio_models import AudioMetadata, AudioFormat, AnalysisRequest, AnalysisResponse
from ..models.tcm_models import TCMAnalysisRequest, TCMAnalysisResponse, TCMDiagnosis
from ..config.settings import get_settings
from ..utils.cache import AudioCache
from ..utils.performance import async_timer, performance_monitor
from ..utils.logging import audit_logger, security_logger

logger = structlog.get_logger(__name__)

# 安全认证
security = HTTPBearer(auto_error=False)


class AudioAnalysisRequest(BaseModel):
    """音频分析REST请求"""
    analysis_type: str = Field(default="default", description="分析类型")
    enable_caching: bool = Field(default=True, description="是否启用缓存")
    user_id: Optional[str] = Field(default=None, description="用户ID")


class TCMAnalysisRequest(BaseModel):
    """中医分析REST请求"""
    analysis_method: str = Field(default="hybrid", description="分析方法")
    enable_constitution_analysis: bool = Field(default=True, description="启用体质分析")
    enable_emotion_analysis: bool = Field(default=True, description="启用情绪分析")
    enable_organ_analysis: bool = Field(default=True, description="启用脏腑分析")
    user_age: Optional[int] = Field(default=None, description="用户年龄")
    user_gender: Optional[str] = Field(default=None, description="用户性别")
    user_region: Optional[str] = Field(default=None, description="用户地区")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: float
    version: str
    uptime: float
    components: Dict[str, Any]


class StatsResponse(BaseModel):
    """统计信息响应"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_processing_time: float
    uptime: float
    cache_stats: Dict[str, Any]


def create_rest_app(
    audio_analyzer: Optional[AudioAnalyzer] = None,
    tcm_analyzer: Optional[TCMFeatureExtractor] = None,
    cache: Optional[AudioCache] = None,
) -> FastAPI:
    """
    创建REST API应用
    
    Args:
        audio_analyzer: 音频分析器实例
        tcm_analyzer: 中医分析器实例
        cache: 缓存实例
        
    Returns:
        配置好的FastAPI应用
    """
    settings = get_settings()
    
    # 创建FastAPI应用
    app = FastAPI(
        title="索克生活闻诊服务",
        description="基于AI的中医闻诊音频分析服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 初始化组件
    app.state.audio_analyzer = audio_analyzer or AudioAnalyzer()
    app.state.tcm_analyzer = tcm_analyzer or TCMFeatureExtractor()
    app.state.cache = cache or AudioCache()
    app.state.start_time = time.time()
    
    # 统计信息
    app.state.stats = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "total_processing_time": 0.0,
    }
    
    # 依赖注入
    async def get_audio_analyzer() -> AudioAnalyzer:
        return app.state.audio_analyzer
    
    async def get_tcm_analyzer() -> TCMFeatureExtractor:
        return app.state.tcm_analyzer
    
    async def get_cache() -> AudioCache:
        return app.state.cache
    
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
        """验证访问令牌"""
        if not credentials:
            return None
        
        # 这里应该实现真实的令牌验证逻辑
        # 暂时简单验证
        if credentials.credentials == "test-token":
            return "test-user"
        
        return None
    
    # 中间件：请求统计
    @app.middleware("http")
    async def stats_middleware(request, call_next):
        start_time = time.time()
        app.state.stats["total_requests"] += 1
        
        try:
            response = await call_next(request)
            
            if response.status_code < 400:
                app.state.stats["successful_requests"] += 1
            else:
                app.state.stats["failed_requests"] += 1
            
            processing_time = time.time() - start_time
            app.state.stats["total_processing_time"] += processing_time
            
            # 添加响应头
            response.headers["X-Processing-Time"] = str(processing_time)
            response.headers["X-Request-ID"] = str(uuid.uuid4())
            
            return response
            
        except Exception as e:
            app.state.stats["failed_requests"] += 1
            logger.error("请求处理异常", error=str(e), exc_info=True)
            raise
    
    # 健康检查端点
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """健康检查"""
        try:
            uptime = time.time() - app.state.start_time
            
            # 检查各组件状态
            components = {}
            
            # 检查音频分析器
            try:
                analyzer_stats = await app.state.audio_analyzer.get_analysis_stats()
                components["audio_analyzer"] = {"status": "healthy", "stats": analyzer_stats}
            except Exception as e:
                components["audio_analyzer"] = {"status": "unhealthy", "error": str(e)}
            
            # 检查中医分析器
            try:
                tcm_stats = await app.state.tcm_analyzer.get_analysis_stats()
                components["tcm_analyzer"] = {"status": "healthy", "stats": tcm_stats}
            except Exception as e:
                components["tcm_analyzer"] = {"status": "unhealthy", "error": str(e)}
            
            # 检查缓存
            try:
                cache_stats = await app.state.cache.get_cache_stats()
                components["cache"] = {"status": "healthy", "stats": cache_stats}
            except Exception as e:
                components["cache"] = {"status": "unhealthy", "error": str(e)}
            
            # 判断整体状态
            overall_status = "healthy"
            for component in components.values():
                if component["status"] != "healthy":
                    overall_status = "degraded"
                    break
            
            return HealthResponse(
                status=overall_status,
                timestamp=time.time(),
                version="1.0.0",
                uptime=uptime,
                components=components,
            )
            
        except Exception as e:
            logger.error("健康检查失败", error=str(e))
            raise HTTPException(status_code=500, detail="健康检查失败")
    
    # 统计信息端点
    @app.get("/stats", response_model=StatsResponse)
    async def get_stats(user_id: Optional[str] = Depends(verify_token)):
        """获取服务统计信息"""
        try:
            uptime = time.time() - app.state.start_time
            avg_processing_time = (
                app.state.stats["total_processing_time"] / app.state.stats["successful_requests"]
                if app.state.stats["successful_requests"] > 0 else 0.0
            )
            
            cache_stats = await app.state.cache.get_cache_stats()
            
            return StatsResponse(
                total_requests=app.state.stats["total_requests"],
                successful_requests=app.state.stats["successful_requests"],
                failed_requests=app.state.stats["failed_requests"],
                average_processing_time=avg_processing_time,
                uptime=uptime,
                cache_stats=cache_stats,
            )
            
        except Exception as e:
            logger.error("获取统计信息失败", error=str(e))
            raise HTTPException(status_code=500, detail="获取统计信息失败")
    
    # 音频分析端点
    @app.post("/api/v1/analyze/audio")
    @async_timer
    async def analyze_audio(
        file: UploadFile = File(...),
        request_data: AudioAnalysisRequest = Depends(),
        analyzer: AudioAnalyzer = Depends(get_audio_analyzer),
        user_id: Optional[str] = Depends(verify_token),
    ):
        """
        音频分析接口
        
        上传音频文件进行特征分析。
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # 验证文件类型
            if not file.content_type or not file.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail="请上传音频文件")
            
            # 读取音频数据
            audio_data = await file.read()
            
            if len(audio_data) == 0:
                raise HTTPException(status_code=400, detail="音频文件为空")
            
            # 创建音频元数据
            metadata = AudioMetadata(
                sample_rate=16000,  # 默认采样率
                channels=1,         # 默认单声道
                duration=len(audio_data) / (16000 * 1 * 2),  # 估算时长
                format=AudioFormat.WAV,
                file_size=len(audio_data),
                filename=file.filename,
            )
            
            # 创建分析请求
            analysis_request = AnalysisRequest(
                request_id=request_id,
                audio_data=audio_data,
                metadata=metadata,
                analysis_type=request_data.analysis_type,
                enable_caching=request_data.enable_caching,
            )
            
            # 记录审计日志
            audit_logger.log_audio_analysis(
                user_id=user_id or request_data.user_id,
                audio_hash=analyzer._hash_audio_data(audio_data),
                analysis_type=request_data.analysis_type,
                success=False,
                duration=0.0,
            )
            
            # 执行分析
            logger.info("开始音频分析", request_id=request_id, filename=file.filename)
            
            result = await analyzer.analyze_audio(analysis_request)
            
            processing_time = time.time() - start_time
            
            # 更新审计日志
            audit_logger.log_audio_analysis(
                user_id=user_id or request_data.user_id,
                audio_hash=analyzer._hash_audio_data(audio_data),
                analysis_type=request_data.analysis_type,
                success=result.success,
                duration=processing_time,
            )
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error_message)
            
            logger.info(
                "音频分析完成",
                request_id=request_id,
                processing_time=processing_time,
            )
            
            return {
                "request_id": request_id,
                "success": True,
                "voice_features": result.voice_features.model_dump() if result.voice_features else None,
                "processing_time": processing_time,
                "timestamp": time.time(),
            }
            
        except HTTPException:
            raise
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "音频分析失败",
                request_id=request_id,
                error=str(e),
                processing_time=processing_time,
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=f"音频分析失败: {str(e)}")
    
    # 中医诊断端点
    @app.post("/api/v1/analyze/tcm")
    @async_timer
    async def analyze_tcm(
        file: UploadFile = File(...),
        request_data: TCMAnalysisRequest = Depends(),
        analyzer: AudioAnalyzer = Depends(get_audio_analyzer),
        tcm_analyzer: TCMFeatureExtractor = Depends(get_tcm_analyzer),
        user_id: Optional[str] = Depends(verify_token),
    ):
        """
        中医诊断接口
        
        上传音频文件进行中医闻诊分析。
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # 验证文件类型
            if not file.content_type or not file.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail="请上传音频文件")
            
            # 读取音频数据
            audio_data = await file.read()
            
            if len(audio_data) == 0:
                raise HTTPException(status_code=400, detail="音频文件为空")
            
            # 创建音频元数据
            metadata = AudioMetadata(
                sample_rate=16000,
                channels=1,
                duration=len(audio_data) / (16000 * 1 * 2),
                format=AudioFormat.WAV,
                file_size=len(audio_data),
                filename=file.filename,
            )
            
            # 首先进行音频特征提取
            analysis_request = AnalysisRequest(
                request_id=request_id,
                audio_data=audio_data,
                metadata=metadata,
                analysis_type="tcm",
            )
            
            logger.info("开始中医诊断分析", request_id=request_id, filename=file.filename)
            
            # 提取音频特征
            audio_result = await analyzer.analyze_audio(analysis_request)
            
            if not audio_result.success or not audio_result.voice_features:
                raise HTTPException(status_code=500, detail="音频特征提取失败")
            
            # 执行中医分析
            tcm_diagnosis = await tcm_analyzer.analyze_tcm_features(
                audio_result.voice_features,
                audio_metadata=metadata.model_dump(),
            )
            
            processing_time = time.time() - start_time
            
            # 记录审计日志
            audit_logger.log_tcm_diagnosis(
                user_id=user_id,
                diagnosis_id=tcm_diagnosis.diagnosis_id,
                constitution_type=tcm_diagnosis.constitution_type,
                emotion_state=tcm_diagnosis.emotion_state,
                confidence_score=tcm_diagnosis.confidence_score,
            )
            
            logger.info(
                "中医诊断完成",
                request_id=request_id,
                processing_time=processing_time,
                constitution=tcm_diagnosis.constitution_type,
                emotion=tcm_diagnosis.emotion_state,
            )
            
            return {
                "request_id": request_id,
                "success": True,
                "diagnosis": tcm_diagnosis.model_dump(),
                "processing_time": processing_time,
                "timestamp": time.time(),
            }
            
        except HTTPException:
            raise
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "中医诊断失败",
                request_id=request_id,
                error=str(e),
                processing_time=processing_time,
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=f"中医诊断失败: {str(e)}")
    
    # 批量分析端点
    @app.post("/api/v1/analyze/batch")
    @async_timer
    async def analyze_batch(
        files: List[UploadFile] = File(...),
        analysis_type: str = "default",
        enable_tcm: bool = False,
        analyzer: AudioAnalyzer = Depends(get_audio_analyzer),
        tcm_analyzer: TCMFeatureExtractor = Depends(get_tcm_analyzer),
        user_id: Optional[str] = Depends(verify_token),
        background_tasks: BackgroundTasks = BackgroundTasks(),
    ):
        """
        批量音频分析接口
        
        支持同时上传多个音频文件进行分析。
        """
        if len(files) > 10:  # 限制批量数量
            raise HTTPException(status_code=400, detail="批量分析最多支持10个文件")
        
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            logger.info("开始批量分析", batch_id=batch_id, file_count=len(files))
            
            # 并发处理所有文件
            tasks = []
            for i, file in enumerate(files):
                task = _process_single_file(
                    file, f"{batch_id}-{i}", analysis_type, enable_tcm,
                    analyzer, tcm_analyzer, user_id
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            successful_results = []
            failed_results = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_results.append({
                        "file_index": i,
                        "filename": files[i].filename,
                        "error": str(result),
                    })
                else:
                    successful_results.append(result)
            
            processing_time = time.time() - start_time
            
            logger.info(
                "批量分析完成",
                batch_id=batch_id,
                successful_count=len(successful_results),
                failed_count=len(failed_results),
                processing_time=processing_time,
            )
            
            return {
                "batch_id": batch_id,
                "total_files": len(files),
                "successful_count": len(successful_results),
                "failed_count": len(failed_results),
                "successful_results": successful_results,
                "failed_results": failed_results,
                "processing_time": processing_time,
                "timestamp": time.time(),
            }
            
        except Exception as e:
            logger.error("批量分析失败", batch_id=batch_id, error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")
    
    # 缓存管理端点
    @app.delete("/api/v1/cache/clear")
    async def clear_cache(
        cache: AudioCache = Depends(get_cache),
        user_id: Optional[str] = Depends(verify_token),
    ):
        """清空缓存"""
        if not user_id:
            raise HTTPException(status_code=401, detail="需要认证")
        
        try:
            success = await cache.clear_all_cache()
            
            logger.info("缓存清空操作", user_id=user_id, success=success)
            
            return {
                "success": success,
                "message": "缓存已清空" if success else "缓存清空失败",
                "timestamp": time.time(),
            }
            
        except Exception as e:
            logger.error("清空缓存失败", error=str(e))
            raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")
    
    # 性能监控端点
    @app.get("/api/v1/performance/metrics")
    async def get_performance_metrics(user_id: Optional[str] = Depends(verify_token)):
        """获取性能指标"""
        if not user_id:
            raise HTTPException(status_code=401, detail="需要认证")
        
        try:
            metrics = performance_monitor.get_metrics()
            
            return {
                "metrics": metrics,
                "timestamp": time.time(),
            }
            
        except Exception as e:
            logger.error("获取性能指标失败", error=str(e))
            raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")
    
    return app


async def _process_single_file(
    file: UploadFile,
    request_id: str,
    analysis_type: str,
    enable_tcm: bool,
    analyzer: AudioAnalyzer,
    tcm_analyzer: TCMFeatureExtractor,
    user_id: Optional[str],
) -> Dict[str, Any]:
    """处理单个文件"""
    try:
        # 读取音频数据
        audio_data = await file.read()
        
        # 创建元数据
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=len(audio_data) / (16000 * 1 * 2),
            format=AudioFormat.WAV,
            file_size=len(audio_data),
            filename=file.filename,
        )
        
        # 创建分析请求
        analysis_request = AnalysisRequest(
            request_id=request_id,
            audio_data=audio_data,
            metadata=metadata,
            analysis_type=analysis_type,
        )
        
        # 执行音频分析
        audio_result = await analyzer.analyze_audio(analysis_request)
        
        result = {
            "request_id": request_id,
            "filename": file.filename,
            "audio_analysis": {
                "success": audio_result.success,
                "voice_features": audio_result.voice_features.model_dump() if audio_result.voice_features else None,
                "error_message": audio_result.error_message,
            }
        }
        
        # 如果启用中医分析
        if enable_tcm and audio_result.success and audio_result.voice_features:
            tcm_diagnosis = await tcm_analyzer.analyze_tcm_features(
                audio_result.voice_features,
                audio_metadata=metadata.model_dump(),
            )
            
            result["tcm_analysis"] = {
                "diagnosis": tcm_diagnosis.model_dump(),
            }
        
        return result
        
    except Exception as e:
        raise Exception(f"处理文件 {file.filename} 失败: {str(e)}")


# 应用工厂函数
def create_app(**kwargs) -> FastAPI:
    """创建应用实例"""
    return create_rest_app(**kwargs) 