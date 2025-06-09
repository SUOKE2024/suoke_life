"""
统一知识服务主管理器
整合医学知识管理和基准测试功能
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .med_knowledge import MedKnowledgeManager
from .benchmark import BenchmarkManager
from .common import ConfigManager, DatabaseManager, CacheManager
from .api import create_api_router


class UnifiedKnowledgeService:
    """统一知识服务管理器"""
    
    def __init__(self, config_path: str = "config/service.yml"):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化组件
        self.db_manager = DatabaseManager(self.config.get("database", {}))
        self.cache_manager = CacheManager(self.config.get("cache", {}))
        
        # 初始化业务模块
        self.med_knowledge = MedKnowledgeManager(
            db_manager=self.db_manager,
            cache_manager=self.cache_manager,
            config=self.config.get("med_knowledge", {})
        )
        
        self.benchmark = BenchmarkManager(
            db_manager=self.db_manager,
            cache_manager=self.cache_manager,
            config=self.config.get("benchmark", {})
        )
        
        # FastAPI应用
        self.app = None
        self.logger = logging.getLogger(__name__)
        
        # 服务状态
        self.is_running = False
        self.health_status = {"status": "initializing"}
    
    async def initialize(self):
        """初始化服务"""
        try:
            self.logger.info("初始化统一知识服务...")
            
            # 初始化数据库连接
            await self.db_manager.initialize()
            
            # 初始化缓存
            await self.cache_manager.initialize()
            
            # 初始化业务模块
            await self.med_knowledge.initialize()
            await self.benchmark.initialize()
            
            # 创建FastAPI应用
            self.app = await self.create_app()
            
            self.health_status = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            self.logger.info("统一知识服务初始化完成")
            
        except Exception as e:
            self.logger.error(f"服务初始化失败: {e}")
            self.health_status = {"status": "unhealthy", "error": str(e)}
            raise
    
    async def create_app(self) -> FastAPI:
        """创建FastAPI应用"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # 启动时执行
            await self.startup()
            yield
            # 关闭时执行
            await self.shutdown()
        
        app = FastAPI(
            title="统一知识服务",
            description="整合医学知识管理和基准测试的统一服务",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get("cors", {}).get("origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 注册路由
        api_router = create_api_router(
            med_knowledge=self.med_knowledge,
            benchmark=self.benchmark
        )
        app.include_router(api_router, prefix="/api/v1")
        
        # 健康检查端点
        @app.get("/health")
        async def health_check():
            return self.health_status
        
        # 服务信息端点
        @app.get("/info")
        async def service_info():
            return {
                "service": "unified-knowledge-service",
                "version": "1.0.0",
                "modules": ["med-knowledge", "benchmark"],
                "status": self.health_status["status"]
            }
        
        return app
    
    async def startup(self):
        """服务启动"""
        self.logger.info("启动统一知识服务...")
        self.is_running = True
        
        # 启动业务模块
        await self.med_knowledge.start()
        await self.benchmark.start()
        
        self.logger.info("统一知识服务启动完成")
    
    async def shutdown(self):
        """服务关闭"""
        self.logger.info("关闭统一知识服务...")
        self.is_running = False
        
        # 关闭业务模块
        await self.med_knowledge.stop()
        await self.benchmark.stop()
        
        # 关闭基础组件
        await self.cache_manager.close()
        await self.db_manager.close()
        
        self.logger.info("统一知识服务关闭完成")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service": "unified-knowledge-service",
            "running": self.is_running,
            "health": self.health_status,
            "modules": {
                "med_knowledge": await self.med_knowledge.get_status(),
                "benchmark": await self.benchmark.get_status()
            },
            "components": {
                "database": await self.db_manager.get_status(),
                "cache": await self.cache_manager.get_status()
            }
        }


# 全局服务实例
service_instance: Optional[UnifiedKnowledgeService] = None


async def get_service() -> UnifiedKnowledgeService:
    """获取服务实例"""
    global service_instance
    if service_instance is None:
        service_instance = UnifiedKnowledgeService()
        await service_instance.initialize()
    return service_instance


async def create_application() -> FastAPI:
    """创建应用实例"""
    service = await get_service()
    return service.app


if __name__ == "__main__":
    import uvicorn
    
    async def main():
        service = UnifiedKnowledgeService()
        await service.initialize()
        
        config = uvicorn.Config(
            app=service.app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    asyncio.run(main())
