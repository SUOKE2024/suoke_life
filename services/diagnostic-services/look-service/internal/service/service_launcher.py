#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务启动器

提供统一的服务生命周期管理、优雅启动和关闭、健康检查等功能。
"""

import asyncio
import signal
import sys
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager

import grpc
from concurrent import futures
from structlog import get_logger

from api.grpc import look_service_pb2_grpc
from internal.container.container import get_container, container_context
from internal.delivery.enhanced_look_service_impl import EnhancedLookServiceServicer
from internal.service.task_processor import AsyncTaskProcessor
from internal.service.validation_service import validation_service, serialization_service
from internal.service.resilience_service import PresetConfigs
from config.config import get_config

logger = get_logger()


class ServiceState(Enum):
    """服务状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    version: str
    description: str
    start_time: Optional[float] = None
    state: ServiceState = ServiceState.STOPPED
    health_status: str = "unknown"
    last_health_check: Optional[float] = None


class ServiceLauncher:
    """服务启动器"""
    
    def __init__(self):
        self.config = get_config()
        self.container = get_container()
        self.grpc_server = None
        self.service_info = ServiceInfo(
            name="look-service",
            version="1.0.0",
            description="索克生活望诊服务"
        )
        self.shutdown_event = asyncio.Event()
        self.health_check_task = None
        self.background_tasks = []
        
    async def initialize(self):
        """初始化服务"""
        try:
            logger.info("开始初始化服务", service=self.service_info.name)
            self.service_info.state = ServiceState.STARTING
            
            # 初始化依赖注入容器
            await self.container.initialize()
            
            # 初始化任务处理器
            await self._init_task_processor()
            
            # 初始化弹性服务
            await self._init_resilience_services()
            
            # 初始化gRPC服务器
            await self._init_grpc_server()
            
            # 启动后台任务
            await self._start_background_tasks()
            
            # 设置信号处理
            self._setup_signal_handlers()
            
            self.service_info.start_time = time.time()
            self.service_info.state = ServiceState.RUNNING
            
            logger.info("服务初始化完成", service=self.service_info.name)
            
        except Exception as e:
            self.service_info.state = ServiceState.ERROR
            logger.error("服务初始化失败", service=self.service_info.name, error=str(e))
            raise
    
    async def _init_task_processor(self):
        """初始化任务处理器"""
        task_config = self.config.get_all().get("task_processor", {
            "max_workers": 10,
            "queue_size": 1000,
            "cleanup_interval": 300,
            "max_result_age": 3600
        })
        
        task_processor = AsyncTaskProcessor(task_config)
        await task_processor.initialize()
        
        self.container.register("task_processor", task_processor)
        logger.info("任务处理器初始化完成")
    
    async def _init_resilience_services(self):
        """初始化弹性服务"""
        # 为不同类型的操作注册弹性服务
        analysis_resilience = PresetConfigs.analysis_resilience()
        external_resilience = PresetConfigs.external_service_resilience()
        
        self.container.register("analysis_resilience", analysis_resilience)
        self.container.register("external_resilience", external_resilience)
        
        logger.info("弹性服务初始化完成")
    
    async def _init_grpc_server(self):
        """初始化gRPC服务器"""
        server_config = self.config.get_all().get("server", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 50053)
        max_workers = server_config.get("max_workers", 10)
        
        # 创建gRPC服务器
        self.grpc_server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=max_workers)
        )
        
        # 创建服务实现
        service_impl = EnhancedLookServiceServicer()
        await service_impl.initialize()
        
        # 注册服务
        look_service_pb2_grpc.add_LookServiceServicer_to_server(
            service_impl, 
            self.grpc_server
        )
        
        # 添加监听端口
        listen_addr = f"{host}:{port}"
        self.grpc_server.add_insecure_port(listen_addr)
        
        logger.info("gRPC服务器初始化完成", address=listen_addr)
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        # 启动健康检查任务
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.background_tasks.append(self.health_check_task)
        
        # 启动指标收集任务
        metrics_service = self.container.get("metrics_service")
        if metrics_service:
            metrics_task = asyncio.create_task(metrics_service.start_background_collection())
            self.background_tasks.append(metrics_task)
        
        logger.info("后台任务已启动", task_count=len(self.background_tasks))
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info("接收到停止信号", signal=signum)
            asyncio.create_task(self.shutdown())
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if sys.platform != "win32":
            signal.signal(signal.SIGHUP, signal_handler)
    
    async def start(self):
        """启动服务"""
        try:
            await self.initialize()
            
            # 启动gRPC服务器
            await self.grpc_server.start()
            
            server_config = self.config.get_all().get("server", {})
            host = server_config.get("host", "0.0.0.0")
            port = server_config.get("port", 50053)
            
            logger.info(
                "服务启动成功",
                service=self.service_info.name,
                version=self.service_info.version,
                address=f"{host}:{port}",
                state=self.service_info.state.value
            )
            
            # 等待关闭信号
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error("服务启动失败", error=str(e))
            self.service_info.state = ServiceState.ERROR
            raise
    
    async def shutdown(self):
        """关闭服务"""
        if self.service_info.state == ServiceState.STOPPING:
            return
        
        logger.info("开始关闭服务", service=self.service_info.name)
        self.service_info.state = ServiceState.STOPPING
        
        try:
            # 停止接受新请求
            if self.grpc_server:
                await self.grpc_server.stop(grace=30)
                logger.info("gRPC服务器已停止")
            
            # 取消后台任务
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
                logger.info("后台任务已停止")
            
            # 关闭容器
            await self.container.shutdown()
            logger.info("依赖注入容器已关闭")
            
            self.service_info.state = ServiceState.STOPPED
            logger.info("服务关闭完成")
            
        except Exception as e:
            logger.error("服务关闭过程中发生错误", error=str(e))
            self.service_info.state = ServiceState.ERROR
        finally:
            self.shutdown_event.set()
    
    async def _health_check_loop(self):
        """健康检查循环"""
        check_interval = self.config.get_all().get("health_check", {}).get("interval", 30)
        
        while not self.shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("健康检查失败", error=str(e))
                await asyncio.sleep(check_interval)
    
    async def _perform_health_check(self):
        """执行健康检查"""
        try:
            # 检查容器健康状态
            health_results = await self.container.health_check()
            
            # 判断整体健康状态
            all_healthy = all(
                health.status == "healthy" 
                for health in health_results.values()
            )
            
            self.service_info.health_status = "healthy" if all_healthy else "unhealthy"
            self.service_info.last_health_check = time.time()
            
            # 记录健康状态
            if not all_healthy:
                unhealthy_components = [
                    name for name, health in health_results.items()
                    if health.status != "healthy"
                ]
                logger.warning(
                    "部分组件不健康",
                    unhealthy_components=unhealthy_components
                )
            
        except Exception as e:
            self.service_info.health_status = "unhealthy"
            logger.error("健康检查执行失败", error=str(e))
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        uptime = None
        if self.service_info.start_time:
            uptime = time.time() - self.service_info.start_time
        
        return {
            "name": self.service_info.name,
            "version": self.service_info.version,
            "description": self.service_info.description,
            "state": self.service_info.state.value,
            "health_status": self.service_info.health_status,
            "start_time": self.service_info.start_time,
            "uptime_seconds": uptime,
            "last_health_check": self.service_info.last_health_check
        }
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """获取详细状态信息"""
        status = {
            "service": self.get_service_info(),
            "components": {}
        }
        
        try:
            # 获取容器健康状态
            health_results = await self.container.health_check()
            status["components"]["health"] = {
                name: {
                    "status": health.status,
                    "last_check": health.last_check,
                    "details": health.details
                }
                for name, health in health_results.items()
            }
            
            # 获取任务处理器状态
            task_processor = self.container.get("task_processor")
            if task_processor:
                status["components"]["task_processor"] = await task_processor.get_stats()
            
            # 获取缓存状态
            cache_service = self.container.get("cache_service")
            if cache_service:
                status["components"]["cache"] = await cache_service.get_stats()
            
            # 获取弹性服务状态
            analysis_resilience = self.container.get("analysis_resilience")
            if analysis_resilience:
                status["components"]["analysis_resilience"] = analysis_resilience.get_status()
            
        except Exception as e:
            logger.error("获取详细状态失败", error=str(e))
            status["error"] = str(e)
        
        return status


# 全局启动器实例
_launcher: Optional[ServiceLauncher] = None


def get_launcher() -> ServiceLauncher:
    """获取全局启动器实例"""
    global _launcher
    if _launcher is None:
        _launcher = ServiceLauncher()
    return _launcher


@asynccontextmanager
async def service_context():
    """服务上下文管理器"""
    launcher = get_launcher()
    try:
        await launcher.initialize()
        yield launcher
    finally:
        await launcher.shutdown()


async def main():
    """主函数"""
    launcher = get_launcher()
    
    try:
        await launcher.start()
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号")
    except Exception as e:
        logger.error("服务运行异常", error=str(e))
        sys.exit(1)
    finally:
        await launcher.shutdown()


if __name__ == "__main__":
    # 配置日志
    import structlog
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
    
    # 运行服务
    asyncio.run(main()) 