"""
索克生活-医学知识服务主应用
提供中医知识图谱数据服务，支持中西医结合的健康管理
"""
import asyncio
import os
import signal
import sys
from concurrent import futures
from contextlib import asynccontextmanager

import grpc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.rest.router import router as api_router
from app.api.rest.health import router as health_router
from app.api.grpc.knowledge_service import MedKnowledgeServicer
from app.api.grpc.generated import knowledge_pb2_grpc
from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.container import get_container, lifespan_context
from app.core.middleware import (
    MetricsMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware,
    AuthenticationMiddleware,
    limiter,
    create_rate_limit_handler
)

# 获取配置和日志
settings = get_settings()
logger = get_logger()

# gRPC服务器
grpc_server = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("索克生活-医学知识服务启动中...")
    
    try:
        # 初始化依赖注入容器
        async with lifespan_context() as container:
            app.state.container = container
            
            # 启动gRPC服务器
            await start_grpc_server(container.knowledge_service)
            
            logger.info("索克生活-医学知识服务启动成功")
            
            yield
            
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)
    finally:
        # 停止gRPC服务器
        await stop_grpc_server()
        logger.info("索克生活-医学知识服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="索克生活-医学知识服务",
    description="""
    ## 索克生活医学知识服务
    
    提供中医知识图谱数据服务，融合传统中医"辨证治未病"理念与现代预防医学技术。
    
    ### 核心功能
    - **中医基础知识**：体质、症状、穴位、中药、证型等
    - **知识图谱**：可视化、路径分析、关系探索
    - **中西医结合**：生物标志物、疾病解析、预防医学证据
    - **智能推荐**：个性化健康建议和生活方式干预
    
    ### 技术特色
    - 高性能异步架构
    - Redis缓存优化
    - Prometheus监控
    - 分布式追踪
    - 安全认证授权
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url="/api/docs",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加中间件（顺序很重要）
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# 配置限流器
app.state.limiter = limiter
app.add_exception_handler(429, create_rate_limit_handler())

# 配置Prometheus监控
if settings.metrics and settings.metrics.enabled:
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/health/live", "/health/ready"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app)

# 注册路由
app.include_router(health_router)
app.include_router(api_router)

# 自定义Swagger UI路由
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="索克生活-医学知识服务 API文档",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )


@app.get("/", include_in_schema=False)
async def root():
    """根路径"""
    return {
        "service": "索克生活-医学知识服务",
        "version": "1.0.0",
        "description": "提供中医知识图谱数据服务，融合中西医结合的健康管理",
        "docs": "/api/docs",
        "health": "/api/v1/health",
        "metrics": "/metrics"
    }


async def start_grpc_server(knowledge_service):
    """启动gRPC服务器"""
    global grpc_server
    
    try:
        # 创建gRPC服务器
        grpc_server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # 注册服务实现
        knowledge_pb2_grpc.add_MedKnowledgeServiceServicer_to_server(
            MedKnowledgeServicer(knowledge_service), grpc_server
        )
        
        # 确定gRPC服务器端口
        grpc_port = int(os.environ.get("GRPC_PORT", "50051"))
        listen_addr = f"[::]:{grpc_port}"
        grpc_server.add_insecure_port(listen_addr)
        
        # 启动服务器
        await grpc_server.start()
        logger.info(f"gRPC服务器已启动于端口 {grpc_port}")
        
    except Exception as e:
        logger.error(f"gRPC服务器启动失败: {e}")
        raise


async def stop_grpc_server():
    """停止gRPC服务器"""
    global grpc_server
    
    if grpc_server:
        try:
            await grpc_server.stop(5)  # 5秒内优雅关闭
            logger.info("gRPC服务器已停止")
        except Exception as e:
            logger.error(f"停止gRPC服务器失败: {e}")


def handle_sigterm(*args):
    """处理SIGTERM信号"""
    logger.info("收到SIGTERM信号，准备关闭服务")
    # 在Kubernetes环境中优雅关闭
    asyncio.create_task(stop_grpc_server())
    sys.exit(0)


# 注册信号处理
signal.signal(signal.SIGTERM, handle_sigterm)


if __name__ == "__main__":
    import uvicorn
    
    host = settings.server.host
    port = int(os.environ.get("PORT", settings.server.port))
    
    # 配置日志
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "access": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.server.debug,
        log_level=settings.logging.level.lower(),
        log_config=log_config,
        access_log=True,
        server_header=False,
        date_header=False,
    ) 