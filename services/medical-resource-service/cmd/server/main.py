#!/usr/bin/env python3
"""
医疗资源微服务主启动文件
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import yaml

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.rest.handlers import router
from internal.infrastructure.container import init_container, get_container
from internal.infrastructure.database import init_database

# 配置日志
def setup_logging(config: Dict[str, Any]):
    """设置日志配置"""
    log_config = config.get("logging", {})
    
    # 创建日志目录
    log_file = log_config.get("file_path", "logs/medical-resource-service.log")
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if log_config.get("format") == "json":
        log_format = '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    
    logging.basicConfig(
        level=getattr(logging, log_config.get("level", "INFO")),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

logger = logging.getLogger(__name__)

class MedicalResourceService:
    """医疗资源微服务主类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.app: FastAPI = None
        self.container = None
        
        # 服务状态
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    
    def load_config(self):
        """加载配置文件"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                self.config = self._get_default_config()
                return
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            logger.info(f"成功加载配置文件: {self.config_path}")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "service": {
                "name": "medical-resource-service",
                "version": "1.0.0",
                "host": "0.0.0.0",
                "port": 9084,
                "debug": False
            },
            "database": {
                "postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "medical_resources",
                    "username": "postgres",
                    "password": "password",
                    "pool_size": 20,
                    "max_overflow": 30,
                    "pool_timeout": 30
                },
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "database": 0,
                    "max_connections": 20
                },
                "mongodb": {
                    "host": "localhost",
                    "port": 27017,
                    "database": "medical_analytics"
                }
            },
            "xiaoke_agent": {
                "agent_id": "xiaoke_001",
                "name": "小克",
                "version": "1.0.0",
                "capabilities": [
                    "medical_resource_management",
                    "tcm_knowledge",
                    "food_agriculture",
                    "wellness_tourism"
                ],
                "learning_rate": 0.01,
                "memory_size": 10000
            },
            "tcm_knowledge": {
                "knowledge_base_path": "/data/tcm_knowledge",
                "enable_learning": True,
                "update_interval": 3600
            },
            "food_agriculture": {
                "food_database_path": "/data/food_agriculture",
                "enable_seasonal_updates": True,
                "nutrition_api_enabled": True
            },
            "wellness_tourism": {
                "wellness_database_path": "/data/wellness_tourism",
                "enable_weather_integration": True,
                "booking_api_enabled": False
            },
            "resource_scheduler": {
                "scheduler_algorithm": "constitution_based",
                "max_queue_size": 1000,
                "scheduling_interval": 60,
                "enable_load_balancing": True
            },
            "logging": {
                "level": "INFO",
                "file_path": "logs/medical-resource-service.log",
                "format": "text",
                "max_size": "100MB",
                "backup_count": 5
            },
            "cors": {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"]
            },
            "monitoring": {
                "metrics": {
                    "enabled": True,
                    "port": 9090,
                    "path": "/metrics"
                },
                "health_check": {
                    "enabled": True,
                    "path": "/health"
                }
            }
        }
    
    async def initialize_container(self):
        """初始化依赖注入容器"""
        try:
            logger.info("初始化依赖注入容器...")
            self.container = init_container(self.config)
            await self.container.initialize_all()
            logger.info("依赖注入容器初始化完成")
            
        except Exception as e:
            logger.error(f"初始化依赖注入容器失败: {e}")
            raise
    
    def create_app(self) -> FastAPI:
        """创建FastAPI应用"""
        app = FastAPI(
            title="医疗资源微服务",
            description="索克生活平台医疗资源管理服务",
            version=self.config.get("service", {}).get("version", "1.0.0"),
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 添加CORS中间件
        cors_config = self.config.get("cors", {})
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.get("allow_origins", ["*"]),
            allow_credentials=cors_config.get("allow_credentials", True),
            allow_methods=cors_config.get("allow_methods", ["*"]),
            allow_headers=cors_config.get("allow_headers", ["*"])
        )
        
        # 添加Gzip压缩中间件
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # 请求日志中间件
        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = asyncio.get_event_loop().time()
            response = await call_next(request)
            process_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            return response
        
        # 全局异常处理器
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.error(f"未处理的异常: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": 500,
                        "message": "内部服务器错误",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                }
            )
        
        # 包含路由
        app.include_router(router, prefix="/api/v1")
        
        # 根路径
        @app.get("/")
        async def root():
            return {
                "service": "medical-resource-service",
                "version": self.config.get("service", {}).get("version", "1.0.0"),
                "status": "running",
                "description": "索克生活平台医疗资源管理服务"
            }
        
        # 健康检查端点
        @app.get("/health")
        async def health_check():
            try:
                if self.container:
                    health_status = await self.container.health_check()
                    overall_health = all(health_status.values())
                    
                    return {
                        "status": "healthy" if overall_health else "unhealthy",
                        "service": "medical-resource-service",
                        "version": self.config.get("service", {}).get("version", "1.0.0"),
                        "components": health_status
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "service": "medical-resource-service",
                        "error": "容器未初始化"
                    }
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                return {
                    "status": "unhealthy",
                    "service": "medical-resource-service",
                    "error": str(e)
                }
        
        # 服务信息端点
        @app.get("/info")
        async def service_info():
            try:
                if self.container:
                    service_info = self.container.get_service_info()
                    return {
                        "service": "medical-resource-service",
                        "version": self.config.get("service", {}).get("version", "1.0.0"),
                        "components": service_info
                    }
                else:
                    return {
                        "service": "medical-resource-service",
                        "error": "容器未初始化"
                    }
            except Exception as e:
                logger.error(f"获取服务信息失败: {e}")
                return {
                    "service": "medical-resource-service",
                    "error": str(e)
                }
        
        return app
    
    async def start(self):
        """启动服务"""
        try:
            logger.info("开始启动医疗资源微服务...")
            
            # 加载配置
            self.load_config()
            
            # 设置日志
            setup_logging(self.config)
            
            # 初始化依赖注入容器
            await self.initialize_container()
            
            # 创建FastAPI应用
            self.app = self.create_app()
            
            # 设置信号处理器
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.is_running = True
            
            # 启动服务器
            server_config = self.config.get("server", {})
            host = server_config.get("host", "0.0.0.0")
            port = server_config.get("port", 9084)
            workers = server_config.get("workers", 1)
            
            logger.info(f"医疗资源微服务启动成功，监听 {host}:{port}")
            
            # 使用uvicorn启动服务
            config = uvicorn.Config(
                app=self.app,
                host=host,
                port=port,
                workers=workers,
                log_level="info",
                access_log=True
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            await self.shutdown()
            raise
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，开始关闭服务...")
        self.shutdown_event.set()
    
    async def shutdown(self):
        """关闭服务"""
        try:
            logger.info("开始关闭医疗资源微服务...")
            
            self.is_running = False
            
            # 关闭依赖注入容器
            if self.container:
                await self.container.shutdown()
            
            logger.info("医疗资源微服务关闭完成")
            
        except Exception as e:
            logger.error(f"关闭服务失败: {e}")

async def main():
    """主函数"""
    try:
        # 创建服务实例
        service = MedicalResourceService()
        
        # 启动服务
        await service.start()
        
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"服务运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 