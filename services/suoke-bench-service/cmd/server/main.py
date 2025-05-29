"""
SuokeBench 服务入口

同时启动FastAPI和gRPC服务，集成缓存、监控和错误处理功能
"""

import argparse
import logging
import os
import signal
import sys
from cmd.server.api import router as api_router
from cmd.server.grpc_service import SuokeBenchGrpcService
from concurrent import futures
from datetime import datetime

import grpc
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from api.grpc import benchmark_pb2_grpc
from internal.benchmark.model_cache import init_global_cache
from internal.observability.metrics import (
    get_global_metrics,
    init_monitoring,
    start_global_monitoring,
    stop_global_monitoring,
)
from internal.resilience.retry import retry
from internal.suokebench.config import BenchConfig, load_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/server.log"),
    ],
)

logger = logging.getLogger(__name__)

# 全局变量
grpc_server: grpc.Server | None = None
config: BenchConfig | None = None


# 创建FastAPI应用
app = FastAPI(
    title="SuokeBench API",
    description="索克生活APP评测系统API - 优化版",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求监控中间件
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """监控HTTP请求"""
    start_time = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # 记录请求指标
        metrics = get_global_metrics()
        metrics.record_api_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )

        return response

    except Exception as e:
        duration = time.time() - start_time

        # 记录错误请求
        metrics = get_global_metrics()
        metrics.record_api_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=500,
            duration=duration
        )

        logger.error(f"请求处理出错: {request.method} {request.url.path} - {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误") from e


# 注册API路由
app.include_router(api_router)

# 静态文件服务
app.mount("/static", StaticFiles(directory="internal/evaluation/static"), name="static")
app.mount("/reports", StaticFiles(directory="data/reports"), name="reports")


# Web界面路由
@app.get("/", tags=["UI"])
async def root():
    """
    重定向到Web界面
    """
    return {
        "message": "欢迎使用SuokeBench API - 优化版",
        "version": "1.1.0",
        "docs": "/docs",
        "ui": "/ui",
        "metrics": "/metrics",
        "health": "/health"
    }


@app.get("/ui", tags=["UI"])
async def ui():
    """
    Web界面
    """
    return FileResponse("internal/evaluation/static/index.html")


@app.get("/health", tags=["监控"])
async def health_check():
    """
    健康检查接口
    """
    try:
        metrics = get_global_metrics()
        cache_stats = get_global_cache().get_cache_stats() if 'get_global_cache' in globals() else {}

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.1.0",
            "cache": {
                "models": cache_stats.get("total_models", 0),
                "memory_mb": cache_stats.get("total_memory_mb", 0)
            },
            "metrics": metrics.get_metrics_summary()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=503, detail="服务不健康") from e


@app.get("/metrics", tags=["监控"])
async def metrics_endpoint():
    """
    Prometheus指标接口
    """
    try:
        metrics = get_global_metrics()
        content = metrics.export_metrics()
        return Response(content=content, media_type="text/plain")
    except Exception as e:
        logger.error(f"指标导出失败: {e}")
        raise HTTPException(status_code=500, detail="指标导出失败")


@app.get("/cache/stats", tags=["缓存"])
async def cache_stats():
    """
    缓存统计接口
    """
    try:
        from internal.benchmark.model_cache import get_global_cache
        cache = get_global_cache()
        return cache.get_cache_stats()
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取缓存统计失败")


@app.post("/cache/clear", tags=["缓存"])
async def clear_cache():
    """
    清空缓存接口
    """
    try:
        from internal.benchmark.model_cache import get_global_cache
        cache = get_global_cache()
        cache.clear_cache()
        return {"message": "缓存已清空"}
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清空缓存失败")


@retry(max_attempts=3, base_delay=1.0)
def start_grpc_server(port: int = 50051, workers: int = 4) -> grpc.Server:
    """
    启动gRPC服务器（带重试机制）

    Args:
        port: gRPC服务端口
        workers: 工作线程数

    Returns:
        gRPC服务器实例
    """
    global config

    # 加载配置
    config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")
    config = load_config(config_path)

    # 创建gRPC服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))

    # 注册服务
    service = SuokeBenchGrpcService(config)
    benchmark_pb2_grpc.add_BenchmarkServiceServicer_to_server(service, server)

    # 启动服务器
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    logger.info(f"gRPC服务启动在端口 {port}")

    return server


def initialize_services():
    """初始化各种服务组件"""
    global config

    # 确保目录存在
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("cache", exist_ok=True)

    # 加载配置
    config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")
    config = load_config(config_path)

    # 初始化模型缓存
    logger.info("初始化模型缓存...")
    _cache = init_global_cache(
        max_memory_mb=4096,
        max_models=10,
        ttl_seconds=3600,
        cleanup_interval=300
    )

    # 初始化监控系统
    logger.info("初始化监控系统...")
    metrics, monitor = init_monitoring()

    # 设置服务信息
    metrics.set_service_info(
        version="1.1.0",
        build_time=datetime.now().isoformat(),
        git_commit=os.environ.get("GIT_COMMIT", "unknown")
    )

    # 启动性能监控
    start_global_monitoring(interval=30)

    logger.info("服务组件初始化完成")


def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"收到信号 {signum}，开始优雅关闭...")

    # 停止监控
    stop_global_monitoring()

    # 停止gRPC服务器
    global grpc_server
    if grpc_server:
        grpc_server.stop(grace=30)
        logger.info("gRPC服务器已停止")

    # 清理缓存
    try:
        from internal.benchmark.model_cache import get_global_cache
        cache = get_global_cache()
        cache.clear_cache()
        logger.info("缓存已清理")
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")

    logger.info("服务已优雅关闭")
    sys.exit(0)


def main():
    """
    主入口函数
    """
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SuokeBench服务 - 优化版")
    parser.add_argument("--http-port", type=int, default=8000, help="HTTP服务端口")
    parser.add_argument("--grpc-port", type=int, default=50051, help="gRPC服务端口")
    parser.add_argument("--workers", type=int, default=4, help="gRPC工作线程数")
    parser.add_argument("--no-grpc", action="store_true", help="不启动gRPC服务")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--log-level", type=str, default="INFO", help="日志级别")
    args = parser.parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    # 设置配置文件路径
    if args.config:
        os.environ["CONFIG_PATH"] = args.config

    try:
        # 初始化服务组件
        initialize_services()

        # 启动gRPC服务
        global grpc_server
        if not args.no_grpc:
            grpc_server = start_grpc_server(args.grpc_port, args.workers)

        logger.info("SuokeBench服务启动完成")
        logger.info(f"HTTP服务: http://0.0.0.0:{args.http_port}")
        if not args.no_grpc:
            logger.info(f"gRPC服务: 0.0.0.0:{args.grpc_port}")
        logger.info(f"API文档: http://0.0.0.0:{args.http_port}/docs")
        logger.info(f"健康检查: http://0.0.0.0:{args.http_port}/health")
        logger.info(f"监控指标: http://0.0.0.0:{args.http_port}/metrics")

        # 启动FastAPI服务
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=args.http_port,
            log_level=args.log_level.lower(),
            access_log=True,
        )

    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import time
    main()
