"""
SuokeBench 服务入口

同时启动FastAPI和gRPC服务
"""

import argparse
import logging
import os
from concurrent import futures
from typing import Optional

import grpc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from api.grpc import benchmark_pb2_grpc
from cmd.server.api import router as api_router
from cmd.server.grpc_service import SuokeBenchGrpcService
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

# 创建FastAPI应用
app = FastAPI(
    title="SuokeBench API",
    description="索克生活APP评测系统API",
    version="1.0.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "欢迎使用SuokeBench API。访问 /ui 查看Web界面，访问 /docs 查看API文档。"}


@app.get("/ui", tags=["UI"])
async def ui():
    """
    Web界面
    """
    return FileResponse("internal/evaluation/static/index.html")


def start_grpc_server(port: int = 50051, workers: int = 4):
    """
    启动gRPC服务器
    
    Args:
        port: gRPC服务端口
        workers: 工作线程数
    """
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


def main():
    """
    主入口函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SuokeBench服务")
    parser.add_argument("--http-port", type=int, default=8000, help="HTTP服务端口")
    parser.add_argument("--grpc-port", type=int, default=50051, help="gRPC服务端口")
    parser.add_argument("--workers", type=int, default=4, help="gRPC工作线程数")
    parser.add_argument("--no-grpc", action="store_true", help="不启动gRPC服务")
    args = parser.parse_args()
    
    # 确保目录存在
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)
    
    # 启动gRPC服务
    if not args.no_grpc:
        grpc_server = start_grpc_server(args.grpc_port, args.workers)
    
    # 启动FastAPI服务
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.http_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()