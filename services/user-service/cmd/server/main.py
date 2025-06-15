"""
用户服务入口点
处理服务启动、配置加载和请求分发
"""
import argparse
import asyncio
import logging
import os
import signal
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 内部模块导入
from internal.delivery.grpc.server import start_grpc_server
from internal.delivery.rest.error_handler import add_error_handlers
from internal.delivery.rest.health_handler import create_health_api_router
from internal.delivery.rest.user_handler import create_user_api_router
from internal.observability.logging_config import configure_logging
from internal.observability.metrics import prometheus_metrics
from internal.repository.operation_log_repository import AuditLogRepository
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from pkg.middleware.rate_limit import add_rate_limit_middleware
from pkg.middleware.rbac import RBACMiddleware

# 全局变量
logger = logging.getLogger(__name__)
grpc_server = None
shutdown_event = asyncio.Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    控制启动和关闭时的行为
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时的操作
    logger.info("用户服务正在启动...")
    
    # 设置服务信息
    version = os.getenv("USER_SERVICE_VERSION", "1.0.0")
    env = os.getenv("ENVIRONMENT", "development")
    service_info = {
        "version": version,
        "environment": env,
        "name": "user-service",
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    prometheus_metrics.update_service_info(service_info)
    
    # 启动gRPC服务器
    global grpc_server
    if app.state.config.get("grpc", {}).get("enabled", False):
        grpc_port = app.state.config.get("grpc", {}).get("port", 50051)
        loop = asyncio.get_event_loop()
        grpc_server_task = loop.create_task(
            start_grpc_server(
                app.state.user_repository,
                app.state.user_service,
                grpc_port
            )
        )
        logger.info(f"gRPC服务器启动于端口 {grpc_port}")
    
    # 应用启动完成
    logger.info("用户服务启动完成")
    
    yield  # 这里暂停执行，直到应用关闭
    
    # 关闭时的操作
    logger.info("用户服务正在关闭...")
    
    # 关闭gRPC服务器
    if grpc_server:
        grpc_server.stop(None)
        logger.info("gRPC服务器已关闭")
    
    # 关闭数据库连接
    if hasattr(app.state, "user_repository"):
        await app.state.user_repository.close()
        logger.info("数据库连接已关闭")
    
    # 标记服务已关闭
    shutdown_event.set()
    logger.info("用户服务已正常关闭")

def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    import yaml
    
    # 解析命令行参数中的配置文件路径
    if not Path(config_path).exists():
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # 用环境变量覆盖配置
    if "database" in config and "path" in config["database"]:
        config["database"]["path"] = os.getenv(
            "USER_DB_PATH", 
            config["database"]["path"]
        )
    
    if "server" in config and "port" in config["server"]:
        config["server"]["port"] = int(os.getenv(
            "USER_SERVICE_PORT", 
            str(config["server"]["port"])
        ))
    
    if "grpc" in config and "port" in config["grpc"]:
        config["grpc"]["port"] = int(os.getenv(
            "USER_GRPC_PORT", 
            str(config["grpc"]["port"])
        ))
    
    if "security" in config and "jwt_secret" in config["security"]:
        config["security"]["jwt_secret"] = os.getenv(
            "JWT_SECRET_KEY", 
            config["security"]["jwt_secret"]
        )
    
    return config

def setup_signal_handlers():
    """
    设置信号处理器
    处理服务关闭信号
    """
    def handle_signal(sig, frame):
        logger.info(f"收到信号 {sig}，准备关闭服务...")
        shutdown_event.set()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_signal)  # Ctrl+C
    signal.signal(signal.SIGTERM, handle_signal)  # kill命令
    
    # 在Windows上SIGTSTP不可用
    if hasattr(signal, "SIGTSTP"):
        signal.signal(signal.SIGTSTP, handle_signal)  # Ctrl+Z

def create_app(config_path: str) -> FastAPI:
    """
    创建FastAPI应用
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        FastAPI: 应用实例
    """
    # 加载配置
    config = load_config(config_path)
    
    # 配置日志
    log_level = config.get("logging", {}).get("level", "INFO")
    configure_logging(log_level)
    
    # 创建FastAPI应用
    app = FastAPI(
        title="用户服务",
        description="索克生命平台的用户管理服务",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if config.get("server", {}).get("expose_docs", True) else None,
        redoc_url="/redoc" if config.get("server", {}).get("expose_docs", True) else None,
    )
    
    # 存储配置
    app.state.config = config
    
    # 设置CORS
    if config.get("server", {}).get("cors", {}).get("enabled", True):
        cors_origins = config.get("server", {}).get("cors", {}).get("origins", ["*"])
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # 创建数据库连接
    db_path = config.get("database", {}).get("path", "user_service.db")
    app.state.user_repository = SQLiteUserRepository(db_path)
    
    # 创建审计日志存储库
    audit_log_db_path = config.get("database", {}).get("audit_log_path", "user_audit_logs.db")
    app.state.audit_log_repository = AuditLogRepository(audit_log_db_path)
    
    # 创建用户服务
    app.state.user_service = UserService(app.state.user_repository)
    
    # 添加速率限制中间件
    if config.get("security", {}).get("rate_limit", {}).get("enabled", True):
        limiter = add_rate_limit_middleware(app)
        app.state.rate_limiter = limiter
    
    # 添加RBAC中间件
    if config.get("security", {}).get("rbac", {}).get("enabled", True):
        excluded_paths = config.get("security", {}).get("rbac", {}).get("excluded_paths", ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"])
        rbac_middleware = RBACMiddleware(exclude_paths=excluded_paths)
        app.middleware("http")(rbac_middleware)
        app.state.rbac_middleware = rbac_middleware
    
    # 添加健康检查路由
    health_router = create_health_api_router(app.state.user_repository)
    app.include_router(health_router, prefix="")
    
    # 添加用户API路由
    user_router = create_user_api_router(
        app.state.user_service,
        app.state.audit_log_repository
    )
    app.include_router(user_router, prefix="/api")
    
    # 添加请求ID中间件
    @app.middleware("http")
    async def add_request_id_middleware(request: Request, call_next):
        """为每个请求添加唯一标识符"""
        import uuid
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 添加到响应头
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    # 添加请求日志中间件
    @app.middleware("http")
    async def log_requests_middleware(request: Request, call_next):
        """记录请求和响应信息"""
        # 记录请求开始
        path = request.url.path
        method = request.method
        query_params = str(request.query_params) if request.query_params else ""
        client_host = request.client.host if request.client else "unknown"
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.info(
            f"请求开始: {method} {path} {query_params}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_ip": client_host,
                "query_params": query_params
            }
        )
        
        # 记录指标
        start_time = prometheus_metrics.record_request_start(method, path)
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应
        status_code = response.status_code
        duration = time.time() - start_time
        prometheus_metrics.record_request_end(start_time, method, path, status_code)
        
        # 记录日志
        logger.info(
            f"请求结束: {method} {path} - {status_code} ({duration:.4f}s)",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": f"{duration:.4f}",
                "client_ip": client_host
            }
        )
        
        return response
    
    # 添加错误处理
    add_error_handlers(app)
    
    # 自定义默认异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常"""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            f"未捕获的异常: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "服务器内部错误",
                "message": "请联系系统管理员",
                "request_id": request_id
            }
        )
    
    return app

async def main():
    """
    主函数
    处理命令行参数，启动服务
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="用户服务")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/config.yaml",
        help="配置文件路径"
    )
    args = parser.parse_args()
    
    # 设置信号处理器
    setup_signal_handlers()
    
    # 创建应用
    app = create_app(args.config)
    
    # 获取服务器配置
    host = app.state.config.get("server", {}).get("host", "0.0.0.0")
    port = app.state.config.get("server", {}).get("port", 8000)
    
    # 启动服务器
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        loop="asyncio",
        log_config=None,  # 使用我们自己的日志配置
    )
    
    server = uvicorn.Server(config)
    
    # 等待关闭信号
    await server.serve()
    
    # 等待正常关闭完成
    logger.info("等待服务关闭...")
    await shutdown_event.wait()
    logger.info("服务已完全关闭")

if __name__ == "__main__":
    asyncio.run(main()) 