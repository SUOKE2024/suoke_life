import asyncio
import os
import signal
import sys
from concurrent import futures
import grpc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

from app.api.rest.router import router as api_router
from app.api.grpc.knowledge_service import MedKnowledgeServicer
from app.api.grpc.generated import knowledge_pb2_grpc
from app.core.config import get_settings
from app.core.logger import get_logger
from app.repositories.neo4j_repository import Neo4jRepository
from app.services.knowledge_service import KnowledgeService

# 获取配置和日志
settings = get_settings()
logger = get_logger()

# 创建FastAPI应用
app = FastAPI(
    title="索克生活-医学知识服务",
    description="提供中医知识图谱数据服务",
    version="1.0.0",
    docs_url=None,
    redoc_url="/api/docs",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
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

# gRPC服务器
grpc_server = None

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化数据库连接
    global repository, knowledge_service, grpc_server
    
    try:
        # 创建仓库和服务实例
        repository = Neo4jRepository(settings.database)
        knowledge_service = KnowledgeService(repository)
        
        # 启动gRPC服务器
        start_grpc_server(knowledge_service)
        
        logger.info("医学知识服务启动成功")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    # 关闭数据库连接
    if 'repository' in globals():
        repository.close()
    
    # 停止gRPC服务器
    if grpc_server:
        grpc_server.stop(0)
        logger.info("gRPC服务器已停止")
    
    logger.info("医学知识服务已关闭")

def start_grpc_server(knowledge_service):
    """启动gRPC服务器"""
    global grpc_server
    
    # 创建gRPC服务器
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 注册服务实现
    knowledge_pb2_grpc.add_MedKnowledgeServiceServicer_to_server(
        MedKnowledgeServicer(knowledge_service), grpc_server
    )
    
    # 确定gRPC服务器端口
    grpc_port = int(os.environ.get("GRPC_PORT", "50051"))
    grpc_server.add_insecure_port(f"[::]:{grpc_port}")
    
    # 启动服务器
    grpc_server.start()
    logger.info(f"gRPC服务器已启动于端口 {grpc_port}")

def handle_sigterm(*args):
    """处理SIGTERM信号"""
    # 在Kubernetes环境中优雅关闭
    logger.info("收到SIGTERM信号，准备关闭服务")
    asyncio.create_task(app.shutdown())
    if grpc_server:
        grpc_server.stop(5)  # 5秒内优雅关闭
    sys.exit(0)

# 注册信号处理
signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == "__main__":
    import uvicorn
    
    host = settings.server.host
    port = int(os.environ.get("PORT", settings.server.port))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.server.debug,
        log_level=settings.logging.level.lower(),
    ) 