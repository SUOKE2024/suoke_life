#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾服务HTTP API服务器
提供RESTful接口，支持设备访问和多模态交互
"""

import os
import sys
import asyncio
import logging
import signal
import argparse
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# FastAPI相关导入
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入核心组件
from internal.agent.agent_manager import AgentManager
from pkg.utils.config_manager import get_config_manager
from pkg.utils.metrics import get_metrics_collector

# 设置日志
logger = logging.getLogger(__name__)

# 全局状态管理
class AppState:
    """应用状态管理"""
    def __init__(self):
        self.agent_manager: Optional[AgentManager] = None
        self.is_shutting_down: bool = False
        self.startup_time: float = 0.0
    
    async def initialize(self):
        """初始化应用状态"""
        import time
        start_time = time.time()
        
        try:
            # 初始化智能体管理器
            self.agent_manager = AgentManager()
            await self.agent_manager.initialize()
            
            self.startup_time = time.time() - start_time
            logger.info(f"应用状态初始化完成，耗时: {self.startup_time:.2f}秒")
            
        except Exception as e:
            logger.error(f"应用状态初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理应用状态"""
        self.is_shutting_down = True
        
        if self.agent_manager:
            try:
                await self.agent_manager.close()
                logger.info("智能体管理器已关闭")
            except Exception as e:
                logger.error(f"关闭智能体管理器失败: {e}")

# 全局应用状态
app_state = AppState()

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    # 获取配置
    config = get_config_manager()
    app_config = config.get_section('http_server', {})
    
    # 创建FastAPI应用
    app = FastAPI(
        title="小艾智能体服务",
        description="提供多模态健康咨询和设备访问功能",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.get('cors_origins', ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    return app

async def get_agent_manager() -> AgentManager:
    """获取智能体管理器依赖"""
    if app_state.agent_manager is None:
        raise HTTPException(status_code=503, detail="智能体管理器未初始化")
    
    if app_state.is_shutting_down:
        raise HTTPException(status_code=503, detail="服务正在关闭")
    
    return app_state.agent_manager

def setup_routes(app: FastAPI):
    """设置路由"""
    
    # 导入API路由（延迟导入避免循环依赖）
    from internal.delivery.api.device_handler import create_device_router
    from internal.delivery.api.chat_handler import create_chat_router
    from internal.delivery.api.health_handler import create_health_router
    from internal.delivery.api.network_handler import create_network_router
    
    # 添加路由，传入依赖函数
    app.include_router(create_device_router(get_agent_manager))
    app.include_router(create_chat_router(get_agent_manager))
    app.include_router(create_health_router(get_agent_manager))
    app.include_router(create_network_router(get_agent_manager))
    
    # 添加根路由
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "service": "小艾智能体服务",
            "version": "1.0.0",
            "status": "运行中",
            "startup_time": f"{app_state.startup_time:.2f}s",
            "features": [
                "多模态健康咨询",
                "设备访问（摄像头、麦克风、屏幕）",
                "无障碍服务集成",
                "语音识别与合成",
                "图像分析",
                "屏幕阅读"
            ]
        }
    
    @app.get("/api/v1/status")
    async def get_service_status(agent_mgr: AgentManager = Depends(get_agent_manager)):
        """获取服务状态"""
        try:
            # 获取设备状态
            device_status = await agent_mgr.get_device_status()
            
            # 获取指标
            metrics = get_metrics_collector()
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "service": "xiaoai-service",
                    "status": "healthy",
                    "startup_time": f"{app_state.startup_time:.2f}s",
                    "devices": device_status,
                    "active_sessions": len(agent_mgr.active_sessions),
                    "metrics": {
                        "total_requests": metrics.get_total_requests(),
                        "active_connections": metrics.get_active_connections()
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")

def handle_shutdown_signal(signum, frame):
    """处理关闭信号"""
    if app_state.is_shutting_down:
        logger.warning("已经在关闭中，忽略重复信号")
        return
    
    signal_name = signal.Signals(signum).name
    logger.info(f"收到信号 {signal_name}，开始优雅关闭...")
    
    # 启动异步关闭
    asyncio.create_task(app_state.cleanup())

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动小艾HTTP API服务')
    parser.add_argument('--config-dir', help='配置目录路径')
    parser.add_argument('--env', help='环境 (development, staging, production)')
    parser.add_argument('--host', default='0.0.0.0', help='监听主机')
    parser.add_argument('--port', type=int, default=8000, help='监听端口')
    args = parser.parse_args()
    
    # 设置环境变量
    if args.config_dir:
        os.environ["XIAOAI_CONFIG_DIR"] = args.config_dir
    if args.env:
        os.environ["ENV"] = args.env
    
    # 获取配置
    config = get_config_manager()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # 注册信号处理程序
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    
    try:
        # 初始化应用状态
        await app_state.initialize()
        
        # 创建应用
        app = create_app()
        
        # 设置路由
        setup_routes(app)
        
        # 获取服务器配置
        http_config = config.get_section('http_server', {})
        host = args.host or http_config.get('host', '0.0.0.0')
        port = args.port or http_config.get('port', 8000)
        
        logger.info(f"启动HTTP API服务器，地址: {host}:{port}")
        
        # 启动服务器
        config_uvicorn = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )
        
        server = uvicorn.Server(config_uvicorn)
        await server.serve()
        
    except Exception as e:
        logger.error(f"HTTP服务器启动失败: {str(e)}", exc_info=True)
        sys.exit(1)
    
    finally:
        # 确保清理
        await app_state.cleanup()

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main()) 