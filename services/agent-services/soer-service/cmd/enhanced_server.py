#!/usr/bin/env python3
"""
增强的索儿服务启动器
集成依赖注入、配置管理、连接池等优化功能
"""
import argparse
import asyncio
import logging
import os
import signal
import sys
from concurrent import futures
from contextlib import asynccontextmanager

import grpc
import uvicorn
from fastapi import FastAPI

# 确保Python能够找到模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入基础设施组件
# 导入API层
from api.grpc import soer_service_pb2_grpc

# 导入业务组件
from internal.agent.enhanced_agent_manager import EnhancedAgentManager
from internal.agent.model_factory import ModelFactory
from internal.delivery.grpc.enhanced_soer_service_impl import EnhancedSoerServiceImpl
from internal.delivery.rest.enhanced_rest_app import create_enhanced_rest_app
from internal.repository.knowledge_repository import KnowledgeRepository
from internal.repository.session_repository import SessionRepository
from pkg.middleware.middleware import create_middleware_stack
from pkg.utils.connection_pool import (
    ConnectionPoolManager,
    DatabaseConnectionPool,
    RedisConnectionPool,
    setup_pool_manager,
)
from pkg.utils.dependency_injection import (
    DependencyContainer,
    setup_container,
)
from pkg.utils.enhanced_config import get_config, setup_config_manager
from pkg.utils.error_handling import ErrorHandler, setup_error_handler

logger = logging.getLogger(__name__)

class SoerServiceBootstrap:
    """索儿服务启动器"""

    def __init__(self, config_path: str, watch_config: bool = False):
        self.config_path = config_path
        self.watch_config = watch_config

        # 核心组件
        self.config_manager = None
        self.container = None
        self.pool_manager = None
        self.error_handler = None

        # 服务器实例
        self.grpc_server = None
        self.rest_server = None

        # 应用实例
        self.rest_app = None

        # 关闭标志
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        """初始化所有组件"""
        logger.info("开始初始化索儿服务...")

        try:
            # 1. 初始化配置管理器
            await self._setup_config()

            # 2. 初始化错误处理器
            await self._setup_error_handler()

            # 3. 初始化连接池管理器
            await self._setup_connection_pools()

            # 4. 初始化依赖注入容器
            await self._setup_dependency_container()

            # 5. 启动所有服务
            await self._start_services()

            logger.info("索儿服务初始化完成")

        except Exception as e:
            logger.error(f"服务初始化失败: {e}")
            await self.cleanup()
            raise

    async def _setup_config(self) -> None:
        """设置配置管理器"""
        logger.info("初始化配置管理器...")

        self.config_manager = setup_config_manager(
            self.config_path,
            watch_changes=self.watch_config
        )

        # 加载配置
        config = self.config_manager.load_config()

        # 设置日志级别
        logging.getLogger().setLevel(getattr(logging, config.logging.level))

        logger.info("配置管理器初始化完成")

    async def _setup_error_handler(self) -> None:
        """设置错误处理器"""
        logger.info("初始化错误处理器...")

        self.error_handler = ErrorHandler()
        setup_error_handler(self.error_handler)

        # 注册错误回调
        self.error_handler.register_global_callback(self._on_error)

        logger.info("错误处理器初始化完成")

    async def _setup_connection_pools(self) -> None:
        """设置连接池管理器"""
        logger.info("初始化连接池管理器...")

        config = get_config()
        self.pool_manager = ConnectionPoolManager()

        # 注册数据库连接池
        db_pool = DatabaseConnectionPool(config.database)
        self.pool_manager.register_pool('database', db_pool)

        # 注册Redis连接池
        redis_pool = RedisConnectionPool(config.cache)
        self.pool_manager.register_pool('redis', redis_pool)

        # 设置全局连接池管理器
        setup_pool_manager(self.pool_manager)

        logger.info("连接池管理器初始化完成")

    async def _setup_dependency_container(self) -> None:
        """设置依赖注入容器"""
        logger.info("初始化依赖注入容器...")

        self.container = DependencyContainer()

        # 注册核心服务
        config = get_config()

        # 注册仓储层
        session_repo = SessionRepository()
        knowledge_repo = KnowledgeRepository()
        self.container.register_singleton('session_repository', session_repo)
        self.container.register_singleton('knowledge_repository', knowledge_repo)

        # 注册模型工厂
        model_factory = ModelFactory(config.models)
        self.container.register_singleton('model_factory', model_factory)

        # 注册智能体管理器
        agent_manager = EnhancedAgentManager()
        self.container.register_singleton('agent_manager', agent_manager)

        # 设置全局容器
        setup_container(self.container)

        logger.info("依赖注入容器初始化完成")

    async def _start_services(self) -> None:
        """启动所有服务"""
        logger.info("启动所有服务...")

        # 启动连接池
        await self.pool_manager.start()

        # 启动依赖容器中的服务
        await self.container.start_all()

        logger.info("所有服务启动完成")

    async def _on_error(self, error) -> None:
        """全局错误回调"""
        logger.error(f"全局错误处理: {error}")
        # 这里可以添加错误通知、告警等逻辑

    async def start_grpc_server(self) -> None:
        """启动gRPC服务器"""
        config = get_config()
        grpc_config = config.grpc

        logger.info("启动gRPC服务器...")

        # 创建gRPC服务器
        self.grpc_server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=grpc_config.max_workers)
        )

        # 注册服务实现
        agent_manager = self.container.get('agent_manager')
        service_impl = EnhancedSoerServiceImpl(agent_manager)
        soer_service_pb2_grpc.add_SoerServiceServicer_to_server(service_impl, self.grpc_server)

        # 启用反射（开发环境）
        if grpc_config.enable_reflection:
            from grpc_reflection.v1alpha import reflection
            reflection.enable_server_reflection(
                soer_service_pb2_grpc.DESCRIPTOR.services_by_name.keys(),
                self.grpc_server
            )

        # 启动服务器
        listen_addr = f'[::]:{grpc_config.port}'
        self.grpc_server.add_insecure_port(listen_addr)
        await self.grpc_server.start()

        logger.info(f"gRPC服务器启动成功，监听地址: {listen_addr}")

    async def start_rest_server(self) -> None:
        """启动REST API服务器"""
        config = get_config()
        rest_config = config.rest

        logger.info("启动REST API服务器...")

        # 创建FastAPI应用
        self.rest_app = create_enhanced_rest_app()

        # 添加中间件
        create_middleware_stack(self.rest_app, config.dict())

        # 配置uvicorn
        uvicorn_config = uvicorn.Config(
            self.rest_app,
            host="0.0.0.0",
            port=rest_config.port,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )

        self.rest_server = uvicorn.Server(uvicorn_config)

        logger.info(f"REST API服务器启动成功，监听端口: {rest_config.port}")

    def setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        def signal_handler(sig, frame):
            logger.info(f"收到信号 {sig}，开始优雅关闭...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def run(self) -> None:
        """运行服务"""
        try:
            # 初始化所有组件
            await self.initialize()

            # 设置信号处理器
            self.setup_signal_handlers()

            # 启动gRPC服务器
            await self.start_grpc_server()

            # 启动REST服务器（在后台运行）
            await self.start_rest_server()
            rest_task = asyncio.create_task(self.rest_server.serve())

            logger.info("索儿服务启动完成，等待请求...")

            # 等待关闭信号
            await self._shutdown_event.wait()

            # 取消REST服务器任务
            rest_task.cancel()
            try:
                await rest_task
            except asyncio.CancelledError:
                pass

        except Exception as e:
            logger.error(f"服务运行失败: {e}")
            raise
        finally:
            await self.cleanup()

    async def shutdown(self) -> None:
        """优雅关闭服务"""
        logger.info("开始优雅关闭服务...")

        try:
            # 停止接受新请求
            if self.grpc_server:
                await self.grpc_server.stop(grace=5.0)
                logger.info("gRPC服务器已停止")

            if self.rest_server:
                self.rest_server.should_exit = True
                logger.info("REST服务器已停止")

            # 停止依赖容器中的服务
            if self.container:
                await self.container.stop_all()
                logger.info("依赖容器服务已停止")

            # 停止连接池
            if self.pool_manager:
                await self.pool_manager.stop()
                logger.info("连接池已停止")

            # 停止配置监控
            if self.config_manager:
                self.config_manager.stop_watching()
                logger.info("配置监控已停止")

            logger.info("服务优雅关闭完成")

        except Exception as e:
            logger.error(f"服务关闭过程中出现错误: {e}")
        finally:
            self._shutdown_event.set()

    async def cleanup(self) -> None:
        """清理资源"""
        await self.shutdown()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI生命周期管理"""
    # 启动时的初始化已在bootstrap中完成
    yield
    # 关闭时的清理也在bootstrap中处理

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="增强的索儿智能体服务")
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--dev', action='store_true', help='启用开发模式')
    parser.add_argument('--watch-config', action='store_true', help='监控配置文件变更')
    parser.add_argument('--mock', action='store_true', help='启用模拟模式')
    args = parser.parse_args()

    # 设置环境变量
    if args.dev:
        os.environ['SOER_ENV'] = 'development'
        os.environ['LOG_LEVEL'] = 'DEBUG'

    if args.mock:
        os.environ['MOCK_LLM'] = 'true'

    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    # 配置基础日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/soer-service.log')
        ]
    )

    # 创建并运行服务
    bootstrap = SoerServiceBootstrap(
        config_path=args.config,
        watch_config=args.watch_config
    )

    try:
        await bootstrap.run()
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"服务运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
