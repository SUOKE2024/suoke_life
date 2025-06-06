"""
main - 索克生活项目模块
"""

from config.settings import load_settings
from internal.delivery.grpc_server import GrpcServer
from internal.delivery.health_check import HealthCheck 
from internal.observability.metrics import MetricsService, service_info
from internal.repository.message_repository import KafkaMessageRepository
from internal.security.auth import AuthInterceptor
from internal.service.message_service import MessageService
from pathlib import Path
import asyncio
import logging
import os
import signal
import sys

#!/usr/bin/env python3
"""
Message Bus服务主入口
提供可靠的消息发布/订阅功能
"""


# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', 'message_bus.log'))
    ]
)
logger = logging.getLogger(__name__)

class MessageBusServer:
    """
    消息总线服务主类
    
    负责协调各组件的初始化、启动和关闭
    """
    
    def __init__(self):
        """初始化服务器"""
        self.settings = load_settings()
        self.shutdown_event = asyncio.Event()
        self.services = []
        
        # 版本和构建信息
        self.version = os.environ.get("APP_VERSION", "0.1.0")
        self.build_id = os.environ.get("BUILD_ID", "development")
        
        # 设置服务信息指标
        service_info.info({
            'version': self.version,
            'build_id': self.build_id,
            'name': 'message-bus',
            'environment': os.environ.get("APP_ENV", "development")
        })
    
    async def setup(self):
        """设置和初始化服务组件"""
        try:
            logger.info("正在初始化消息总线服务...")
            
            # 创建存储库
            repository = KafkaMessageRepository(self.settings)
            await repository.setup()
            
            # 创建服务层
            message_service = MessageService(repository, self.settings)
            
            # 创建指标服务
            metrics_service = MetricsService(self.settings.metrics.port)
            self.services.append(metrics_service)
            
            # 创建健康检查
            health_check = HealthCheck(self.settings, message_service)
            self.services.append(health_check)
            
            # 创建认证拦截器
            auth_interceptor = None
            if self.settings.enable_auth:
                auth_interceptor = AuthInterceptor(self.settings)
            
            # 创建gRPC服务器
            grpc_server = GrpcServer(self.settings, message_service)
            if auth_interceptor:
                grpc_server.server_interceptors.append(auth_interceptor)
            self.services.append(grpc_server)
            
            # 启动所有服务
            logger.info("正在启动所有服务...")
            for service in self.services:
                await service.start()
            
            logger.info(f"消息总线服务已成功启动，版本 {self.version}, 构建 {self.build_id}")
            return True
            
        except Exception as e:
            logger.error(f"初始化服务时出错: {str(e)}", exc_info=True)
            await self.cleanup()
            return False
    
    async def cleanup(self):
        """清理资源和关闭服务"""
        logger.info("正在关闭消息总线服务...")
        
        # 按相反顺序关闭服务
        for service in reversed(self.services):
            try:
                await service.stop()
            except Exception as e:
                logger.error(f"关闭服务 {service.__class__.__name__} 时出错: {str(e)}", exc_info=True)
        
        logger.info("消息总线服务已关闭")
    
    def handle_signals(self):
        """设置信号处理函数"""
        loop = asyncio.get_event_loop()
        
        # 定义信号处理函数
        def signal_handler():
            if not self.shutdown_event.is_set():
                logger.info("收到终止信号，开始优雅关闭...")
                self.shutdown_event.set()
        
        # 注册SIGINT和SIGTERM信号处理
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
    
    async def run(self):
        """运行服务器"""
        # 设置信号处理
        self.handle_signals()
        
        # 初始化服务
        success = await self.setup()
        if not success:
            return 1
        
        try:
            # 等待关闭信号
            await self.shutdown_event.wait()
        finally:
            # 清理资源
            await self.cleanup()
        
        return 0

async def main():
    """主函数"""
    server = MessageBusServer()
    return await server.run()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 