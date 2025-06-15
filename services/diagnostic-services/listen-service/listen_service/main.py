"""
Listen Service 主启动模块

提供服务的主要入口点和启动逻辑。
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

import structlog
import uvicorn
from fastapi import FastAPI

from .config.settings import get_settings
from .delivery.rest_api import create_app
from .delivery.grpc_api import create_grpc_server
from .utils.cache import cleanup_cache
from .utils.performance import cleanup_performance_monitor, start_metrics_server

logger = structlog.get_logger(__name__)


class ListenService:
    """Listen Service 主服务类"""

    def __init__(self):
        self.settings = get_settings()
        self.rest_app: Optional[FastAPI] = None
        self.grpc_server = None
        self.running = False

    async def initialize(self):
        """初始化服务"""
        try:
            logger.info("初始化 Listen Service")
            
            # 创建必要的目录
            self._create_directories()
            
            # 初始化REST API
            self.rest_app = create_app()
            
            # 初始化gRPC服务器
            if self.settings.get_grpc_config().get("enabled", False):
                grpc_port = self.settings.get_grpc_config().get("port", 50051)
                self.grpc_server = await create_grpc_server(grpc_port)
            
            # 启动Prometheus指标服务器
            metrics_config = self.settings.get_metrics_config()
            if metrics_config.get("enabled", False):
                start_metrics_server(metrics_config.get("port", 9090))
            
            logger.info("Listen Service 初始化完成")
            
        except Exception as e:
            logger.error("Listen Service 初始化失败", error=str(e))
            raise

    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.settings.get_upload_dir(),
            self.settings.get_log_dir(),
            self.settings.get_cache_dir(),
            self.settings.get_temp_dir()
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.debug("创建目录", directory=directory)

    async def start_rest_api(self):
        """启动REST API服务器"""
        try:
            rest_config = self.settings.get_rest_config()
            
            config = uvicorn.Config(
                app=self.rest_app,
                host=rest_config.get("host", "0.0.0.0"),
                port=rest_config.get("port", 8004),
                log_level=rest_config.get("log_level", "info"),
                reload=rest_config.get("reload", False),
                workers=rest_config.get("workers", 1)
            )
            
            server = uvicorn.Server(config)
            
            logger.info(
                "启动REST API服务器",
                host=config.host,
                port=config.port,
                workers=config.workers
            )
            
            await server.serve()
            
        except Exception as e:
            logger.error("REST API服务器启动失败", error=str(e))
            raise

    async def start_grpc_server(self):
        """启动gRPC服务器"""
        try:
            if self.grpc_server:
                logger.info("启动gRPC服务器")
                await self.grpc_server.start()
            else:
                logger.info("gRPC服务器未启用")
                
        except Exception as e:
            logger.error("gRPC服务器启动失败", error=str(e))
            raise

    async def start(self):
        """启动服务"""
        try:
            await self.initialize()
            self.running = True
            
            # 设置信号处理
            self._setup_signal_handlers()
            
            # 创建任务
            tasks = []
            
            # REST API任务
            rest_task = asyncio.create_task(self.start_rest_api())
            tasks.append(rest_task)
            
            # gRPC任务
            if self.grpc_server:
                grpc_task = asyncio.create_task(self.start_grpc_server())
                tasks.append(grpc_task)
            
            logger.info("Listen Service 启动完成")
            
            # 等待任务完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error("Listen Service 启动失败", error=str(e))
            raise
        finally:
            await self.cleanup()

    async def stop(self):
        """停止服务"""
        try:
            logger.info("正在停止 Listen Service")
            self.running = False
            
            # 停止gRPC服务器
            if self.grpc_server:
                await self.grpc_server.stop()
            
            logger.info("Listen Service 已停止")
            
        except Exception as e:
            logger.error("停止服务时出错", error=str(e))

    async def cleanup(self):
        """清理资源"""
        try:
            logger.info("清理 Listen Service 资源")
            
            # 清理缓存
            await cleanup_cache()
            
            # 清理性能监控器
            await cleanup_performance_monitor()
            
            logger.info("Listen Service 资源清理完成")
            
        except Exception as e:
            logger.error("资源清理失败", error=str(e))

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，正在关闭服务...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def health_check(self) -> dict:
        """健康检查"""
        try:
            return {
                "status": "healthy" if self.running else "stopped",
                "service": "listen-service",
                "version": "1.0.0",
                "components": {
                    "rest_api": self.rest_app is not None,
                    "grpc_server": self.grpc_server is not None,
                    "cache": True,  # 假设缓存总是可用的
                    "performance_monitor": True
                }
            }
        except Exception as e:
            logger.error("健康检查失败", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# 全局服务实例
_service_instance: Optional[ListenService] = None


def get_service() -> ListenService:
    """获取服务实例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ListenService()
    return _service_instance


async def main():
    """主函数"""
    try:
        # 配置日志
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        logger.info("启动 Listen Service")
        
        # 创建并启动服务
        service = get_service()
        await service.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error("服务运行失败", error=str(e), exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Listen Service 退出")


# 命令行接口
def cli():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Listen Service")
    parser.add_argument(
        "--config",
        type=str,
        help="配置文件路径"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="REST API主机地址"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8004,
        help="REST API端口"
    )
    parser.add_argument(
        "--grpc-port",
        type=int,
        default=50051,
        help="gRPC端口"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用自动重载"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="日志级别"
    )
    
    args = parser.parse_args()
    
    # 更新配置
    settings = get_settings()
    if args.config:
        settings.load_from_file(args.config)
    
    # 运行服务
    asyncio.run(main())


# 开发模式启动
def dev():
    """开发模式启动"""
    import uvicorn
    
    uvicorn.run(
        "listen_service.delivery.rest_api:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="debug"
    )


# 生产模式启动
def prod():
    """生产模式启动"""
    asyncio.run(main())


if __name__ == "__main__":
    cli()