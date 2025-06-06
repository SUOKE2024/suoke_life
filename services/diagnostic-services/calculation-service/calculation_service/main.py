"""
main - 索克生活项目模块
"""

from .api.routes import router
from .config.settings import get_settings
from .middleware import LoggingMiddleware, ErrorHandlerMiddleware, RateLimiterMiddleware
from .utils.cache import cache_manager
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import uvicorn

"""
算诊服务主应用

提供中医五诊中"算诊"功能的微服务
"""



# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("算诊服务启动中...")
    logger.info("初始化算诊算法模块...")
    
    # 初始化缓存管理器
    if settings.ENABLE_CACHE:
        logger.info(f"启用缓存，TTL: {settings.CACHE_TTL}秒")
        cache_manager.ttl = settings.CACHE_TTL
    
    # 这里可以添加启动时的初始化逻辑
    # 例如：预加载模型、连接数据库等
    
    logger.info("算诊服务启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("算诊服务关闭中...")
    
    # 清理缓存
    if settings.ENABLE_CACHE:
        cache_stats = cache_manager.get_stats()
        logger.info(f"缓存统计: {cache_stats}")
        cache_manager.clear()
        logger.info("缓存已清理")
    
    logger.info("算诊服务已关闭")

# 创建FastAPI应用
app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
    title="索克生活 - 算诊服务",
    description="""
    中医五诊中的"算诊"功能微服务
    
    ## 功能特性
    
    * **子午流注分析** - 十二经络时间医学分析
    * **八字体质分析** - 基于出生时间的体质分析
    * **八卦配属分析** - 易学与健康的关系分析
    * **五运六气分析** - 运气学说的健康预测
    * **综合算诊** - 整合多种算诊方法的综合分析
    
    ## 技术特点
    
    * 传统中医理论与现代算法结合
    * 个性化健康分析和调养建议
    * 时间医学指导和预防保健
    * 科学化的中医智慧数字化实现
    * 智能缓存和限流保护
    * 完善的错误处理和日志记录
    
    ## 创新价值
    
    * **传统与现代结合** - 将古代算诊智慧与现代AI技术完美融合
    * **差异化竞争优势** - 市面上几乎没有类似的算诊功能产品
    * **完善诊断体系** - 与现有望、闻、问、切四诊形成完整的"五诊合参"
    * **科学化实现** - 用现代算法实现传统医学理论
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中间件（注意顺序很重要）
# 1. 错误处理中间件（最外层）
app.add_middleware(ErrorHandlerMiddleware)

# 2. 限流中间件
max_requests = getattr(settings, 'RATE_LIMIT_MAX_REQUESTS', 100)
window_seconds = getattr(settings, 'RATE_LIMIT_WINDOW_SECONDS', 60)
app.add_middleware(RateLimiterMiddleware, max_requests=max_requests, window_seconds=window_seconds)

# 3. 日志中间件
app.add_middleware(LoggingMiddleware)

# 4. CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)

@cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/", summary="服务根路径")
async def root():
    """服务根路径"""
    return {
        "service": "calculation-service",
        "name": "索克生活 - 算诊服务",
        "version": "1.0.0",
        "description": "中医五诊中的算诊功能微服务",
        "status": "running",
        "features": [
            "子午流注分析",
            "八字体质分析", 
            "八卦配属分析",
            "五运六气分析",
            "综合算诊"
        ],
        "innovation": [
            "传统中医智慧数字化",
            "个性化健康分析",
            "时间医学指导",
            "预防保健建议"
        ],
        "docs": "/docs",
        "health": "/api/v1/calculation/health",
        "cache_enabled": s@cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
ettings.ENABLE_CACHE
    }

@app.get("/ping", summary="服务状态检查")
async def ping():
    """简单的服务状态检查"""
    return {"status": "ok", "message": "pong", "timestamp": "2024-01-15T10:00:00Z"}

@app.get("/cache/stats", summary="缓存统计信息")
async def cache_stats():
    """获取缓存统计信息"""
    if not settings.ENABLE_CACHE:
        return {"message": "缓存未启用"}
    
    stats = cache_manager.get_stats()
    return {
   @limiter.limit("100/minute")  # 每分钟100次请求
     "success": True,
        "data": stats,
        "message": "缓存统计信息获取成功"
    }

@app.post("/cache/clear", summary="清理缓存")
async def clear_cache():
    """清理所有缓存"""
    if not settings.ENABLE_CACHE:
        retur@limiter.limit("100/minute")  # 每分钟100次请求
n {"message": "缓存未启用"}
    
    cache_manager.clear()
    return {
        "success": True,
        "message": "缓存已清理"
    }

@app.post("/cache/cleanup", summary="清理过期缓存")
async def cleanup_expired_cache():
    """清理过期缓存"""
    if not settings.ENABLE_CACHE:
        return {"message": "缓存未启用"}
    
    cleaned_count = cache_manager.cleanup_expired()
    return {
        "success": True,
        "data": {"cleaned_items": cleaned_count},
        "message": f"已清理 {cleaned_count} 个过期缓存项"
    }

if __name__ == "__main__":
    uvicorn.run(
        "calculation_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 