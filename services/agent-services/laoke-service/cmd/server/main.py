#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 主入口
提供GraphQL和REST API服务
"""

import os
import sys
import uvicorn
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import argparse

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from pkg.utils.logger import setup_logger
from pkg.utils.config import Config
from pkg.utils.middleware import request_logging_middleware
from internal.delivery.graphql.schema import schema
from internal.delivery.rest.health_controller import router as health_router
from internal.delivery.rest.metrics_controller import router as metrics_router
from internal.repository.community_repository import CommunityRepository
from internal.repository.knowledge_repository import KnowledgeRepository
from internal.repository.session_repository import SessionRepository

# 创建FastAPI应用
app = FastAPI(title="老克智能体服务")

# 加载配置
config = Config()

# 设置日志
logger = logging.getLogger("laoke-service")
setup_logger(logger, level=config.get("logging.level", "INFO"))

# GraphQL路由
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# REST API路由
app.include_router(health_router)
app.include_router(metrics_router)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("server.cors.allowed_origins", ["*"]),
    allow_credentials=config.get("server.cors.allow_credentials", True),
    allow_methods=config.get("server.cors.allowed_methods", ["*"]),
    allow_headers=config.get("server.cors.allowed_headers", ["*"]),
)

# 请求日志中间件
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    return await request_logging_middleware(request, call_next)

# 启动时初始化存储库索引
@app.on_event("startup")
async def startup_event():
    try:
        # 初始化社区存储库索引
        community_repo = CommunityRepository()
        await community_repo.init_indexes()
        
        # 初始化知识存储库索引
        knowledge_repo = KnowledgeRepository()
        await knowledge_repo.init_indexes()
        
        # 初始化会话存储库索引
        session_repo = SessionRepository()
        await session_repo.init_indexes()
        
        logger.info("存储库索引初始化完成")
    except Exception as e:
        logger.error(f"初始化存储库索引失败: {str(e)}")

def parse_args():
    parser = argparse.ArgumentParser(description="老克智能体服务")
    parser.add_argument(
        "--host", 
        type=str,
        default=config.get("server.host", "0.0.0.0"),
        help="服务主机地址"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=config.get("server.port", 8080),
        help="服务端口"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="是否启用热重载（开发模式）"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    logger.info(f"启动老克智能体服务，监听 {args.host}:{args.port}")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=config.get("logging.level", "info").lower()
    ) 