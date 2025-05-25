#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - 触诊服务主启动脚本
整合所有优化模块，提供完整的服务启动和管理功能
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入内部模块
from internal.config.config_manager import ConfigManager
from internal.service.intelligent_coordinator import IntelligentCoordinator
from internal.fusion.multimodal_fusion_engine import MultimodalFusionEngine
from internal.report.intelligent_report_generator import IntelligentReportGenerator
from internal.prediction.predictive_analyzer import PredictiveAnalyzer
from internal.visualization.advanced_visualizer import AdvancedVisualizer
from internal.cache.intelligent_cache_manager import IntelligentCacheManager
from internal.monitoring.realtime_dashboard import RealtimeDashboard

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/palpation_service.log')
    ]
)

logger = logging.getLogger(__name__)

class PalpationService:
    """触诊服务主类"""
    
    def __init__(self):
        """初始化触诊服务"""
        self.config_manager = None
        self.coordinator = None
        self.fusion_engine = None
        self.report_generator = None
        self.predictive_analyzer = None
        self.visualizer = None
        self.cache_manager = None
        self.dashboard = None
        self.app = None
        self.server = None
        
        # 服务状态
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        logger.info("触诊服务初始化开始")
    
    async def initialize(self):
        """初始化所有组件"""
        try:
            # 1. 初始化配置管理器
            logger.info("初始化配置管理器...")
            self.config_manager = ConfigManager("config")
            
            # 加载配置文件
            config_files = [
                "config/palpation.yaml",
                "config/devices.yaml",
                "config/ai.yaml"
            ]
            
            for config_file in config_files:
                if Path(config_file).exists():
                    self.config_manager.load_config_file(config_file)
            
            # 加载环境变量配置
            self.config_manager.load_environment_config()
            
            # 启用配置文件监控
            self.config_manager.enable_file_watching()
            
            # 2. 初始化缓存管理器
            logger.info("初始化缓存管理器...")
            cache_config = self.config_manager.get('cache', {})
            self.cache_manager = IntelligentCacheManager(cache_config)
            await self.cache_manager.start()
            
            # 3. 初始化多模态融合引擎
            logger.info("初始化多模态融合引擎...")
            fusion_config = self.config_manager.get('fusion', {})
            self.fusion_engine = MultimodalFusionEngine(fusion_config)
            await self.fusion_engine.start()
            
            # 4. 初始化预测分析器
            logger.info("初始化预测分析器...")
            prediction_config = self.config_manager.get('prediction', {})
            self.predictive_analyzer = PredictiveAnalyzer(prediction_config)
            await self.predictive_analyzer.start()
            
            # 5. 初始化可视化器
            logger.info("初始化可视化器...")
            viz_config = self.config_manager.get('visualization', {})
            self.visualizer = AdvancedVisualizer(viz_config)
            
            # 6. 初始化报告生成器
            logger.info("初始化报告生成器...")
            report_config = self.config_manager.get('report', {})
            self.report_generator = IntelligentReportGenerator(
                report_config, 
                self.visualizer
            )
            
            # 7. 初始化智能协调器
            logger.info("初始化智能协调器...")
            coordinator_config = self.config_manager.get('coordinator', {})
            self.coordinator = IntelligentCoordinator(
                coordinator_config,
                self.fusion_engine,
                self.predictive_analyzer,
                self.report_generator,
                self.cache_manager
            )
            await self.coordinator.start()
            
            # 8. 初始化监控仪表板
            logger.info("初始化监控仪表板...")
            dashboard_config = self.config_manager.get('monitoring', {})
            self.dashboard = RealtimeDashboard(dashboard_config)
            await self.dashboard.start()
            
            # 9. 创建FastAPI应用
            logger.info("创建FastAPI应用...")
            self.app = self._create_fastapi_app()
            
            logger.info("所有组件初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    def _create_fastapi_app(self) -> FastAPI:
        """创建FastAPI应用"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """应用生命周期管理"""
            # 启动时执行
            logger.info("FastAPI应用启动")
            yield
            # 关闭时执行
            logger.info("FastAPI应用关闭")
            await self.shutdown()
        
        app = FastAPI(
            title="索克生活 - 触诊服务",
            description="基于AI的中医触诊智能分析服务",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # 添加路由
        self._add_routes(app)
        
        # 添加中间件
        self._add_middleware(app)
        
        return app
    
    def _add_routes(self, app: FastAPI):
        """添加API路由"""
        from fastapi import HTTPException, Depends
        from pydantic import BaseModel
        from typing import List, Dict, Any
        
        # 数据模型
        class PalpationRequest(BaseModel):
            user_id: str
            session_id: str
            device_configs: Dict[str, Any] = {}
            preferences: Dict[str, Any] = {}
        
        class PalpationData(BaseModel):
            modality: str
            data: Dict[str, Any]
            timestamp: str
        
        class AnalysisRequest(BaseModel):
            session_id: str
            data_list: List[PalpationData]
        
        # API端点
        @app.get("/")
        async def root():
            """根端点"""
            return {
                "service": "palpation-service",
                "version": "1.0.0",
                "status": "running" if self.is_running else "stopped"
            }
        
        @app.get("/health")
        async def health_check():
            """健康检查"""
            try:
                # 检查各组件状态
                status = {
                    "coordinator": self.coordinator.get_status() if self.coordinator else "stopped",
                    "fusion_engine": self.fusion_engine.get_status() if self.fusion_engine else "stopped",
                    "cache_manager": self.cache_manager.get_status() if self.cache_manager else "stopped",
                    "dashboard": "running" if self.dashboard else "stopped"
                }
                
                all_healthy = all(s in ["running", "ready"] for s in status.values())
                
                return {
                    "status": "healthy" if all_healthy else "unhealthy",
                    "components": status,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                raise HTTPException(status_code=500, detail="Health check failed")
        
        @app.post("/palpation/start")
        async def start_palpation_session(request: PalpationRequest):
            """启动触诊会话"""
            try:
                if not self.coordinator:
                    raise HTTPException(status_code=503, detail="Service not ready")
                
                session_info = await self.coordinator.start_palpation_session(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    device_configs=request.device_configs,
                    preferences=request.preferences
                )
                
                return {
                    "status": "success",
                    "session_info": session_info
                }
                
            except Exception as e:
                logger.error(f"启动触诊会话失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/palpation/data")
        async def submit_palpation_data(data: PalpationData):
            """提交触诊数据"""
            try:
                if not self.coordinator:
                    raise HTTPException(status_code=503, detail="Service not ready")
                
                result = await self.coordinator.process_palpation_data(
                    modality=data.modality,
                    data=data.data,
                    timestamp=data.timestamp
                )
                
                return {
                    "status": "success",
                    "result": result
                }
                
            except Exception as e:
                logger.error(f"处理触诊数据失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/palpation/analyze")
        async def analyze_palpation(request: AnalysisRequest):
            """综合触诊分析"""
            try:
                if not self.coordinator:
                    raise HTTPException(status_code=503, detail="Service not ready")
                
                analysis_result = await self.coordinator.analyze_comprehensive_palpation(
                    session_id=request.session_id,
                    data_list=[
                        {
                            'modality': item.modality,
                            'data': item.data,
                            'timestamp': item.timestamp
                        }
                        for item in request.data_list
                    ]
                )
                
                return {
                    "status": "success",
                    "analysis": analysis_result
                }
                
            except Exception as e:
                logger.error(f"综合分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/palpation/report/{session_id}")
        async def get_palpation_report(session_id: str, format: str = "html"):
            """获取触诊报告"""
            try:
                if not self.report_generator:
                    raise HTTPException(status_code=503, detail="Report service not ready")
                
                # 从缓存或数据库获取会话数据
                session_data = await self.cache_manager.get(f"session:{session_id}")
                if not session_data:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                report = await self.report_generator.generate_report(
                    session_data=session_data,
                    format=format
                )
                
                return {
                    "status": "success",
                    "report": report
                }
                
            except Exception as e:
                logger.error(f"生成报告失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/config")
        async def get_config():
            """获取配置信息"""
            try:
                if not self.config_manager:
                    raise HTTPException(status_code=503, detail="Config service not ready")
                
                return {
                    "status": "success",
                    "config": self.config_manager.export_config()
                }
                
            except Exception as e:
                logger.error(f"获取配置失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/stats")
        async def get_service_stats():
            """获取服务统计"""
            try:
                stats = {}
                
                if self.coordinator:
                    stats['coordinator'] = self.coordinator.get_stats()
                
                if self.fusion_engine:
                    stats['fusion_engine'] = self.fusion_engine.get_stats()
                
                if self.cache_manager:
                    stats['cache_manager'] = self.cache_manager.get_stats()
                
                if self.dashboard:
                    stats['dashboard'] = self.dashboard.get_dashboard_stats()
                
                return {
                    "status": "success",
                    "stats": stats
                }
                
            except Exception as e:
                logger.error(f"获取统计信息失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _add_middleware(self, app: FastAPI):
        """添加中间件"""
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.middleware.gzip import GZipMiddleware
        import time
        
        # CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Gzip压缩中间件
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # 请求日志中间件
        @app.middleware("http")
        async def log_requests(request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
    
    async def start(self):
        """启动服务"""
        try:
            logger.info("启动触诊服务...")
            
            # 初始化组件
            await self.initialize()
            
            # 设置信号处理
            self._setup_signal_handlers()
            
            # 获取服务配置
            host = self.config_manager.get('service.host', '0.0.0.0')
            port = self.config_manager.get('service.port', 8000)
            debug = self.config_manager.get('service.debug', False)
            
            # 启动服务
            config = uvicorn.Config(
                app=self.app,
                host=host,
                port=port,
                log_level="debug" if debug else "info",
                access_log=True
            )
            
            self.server = uvicorn.Server(config)
            self.is_running = True
            
            logger.info(f"触诊服务启动成功: http://{host}:{port}")
            logger.info(f"监控仪表板: http://{host}:8080")
            logger.info("服务已就绪，等待请求...")
            
            # 运行服务
            await self.server.serve()
            
        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            await self.shutdown()
            raise
    
    async def shutdown(self):
        """关闭服务"""
        if not self.is_running:
            return
        
        logger.info("开始关闭触诊服务...")
        
        try:
            # 设置关闭标志
            self.is_running = False
            self.shutdown_event.set()
            
            # 关闭各组件
            if self.dashboard:
                await self.dashboard.stop()
            
            if self.coordinator:
                await self.coordinator.stop()
            
            if self.predictive_analyzer:
                await self.predictive_analyzer.stop()
            
            if self.fusion_engine:
                await self.fusion_engine.stop()
            
            if self.cache_manager:
                await self.cache_manager.stop()
            
            if self.config_manager:
                self.config_manager.cleanup()
            
            # 关闭服务器
            if self.server:
                self.server.should_exit = True
            
            logger.info("触诊服务关闭完成")
            
        except Exception as e:
            logger.error(f"关闭服务时出错: {e}")
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，开始关闭服务...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """主函数"""
    # 创建必要的目录
    directories = [
        "logs",
        "data",
        "config",
        "models",
        "cache",
        "reports",
        "monitoring"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # 创建并启动服务
    service = PalpationService()
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"服务运行错误: {e}")
    finally:
        await service.shutdown()

if __name__ == "__main__":
    # 设置事件循环策略（Windows兼容性）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 运行主函数
    asyncio.run(main()) 