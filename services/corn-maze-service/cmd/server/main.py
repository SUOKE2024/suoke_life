#!/usr/bin/env python3

"""
迷宫服务主程序 - 负责启动gRPC服务器和相关组件
"""

import asyncio
from concurrent import futures
import logging
from pathlib import Path
import signal
import sys

import grpc

# 确保项目根目录在路径中
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from internal.delivery.grpc.server import setup_grpc_server
from internal.maze.generator import MazeGenerator
from internal.repository.maze_repository import MazeRepository
from internal.service.knowledge_service import KnowledgeService
from internal.service.maze_service import MazeService
from internal.service.progress_service import ProgressService
from pkg.utils.config import get_value, load_config
from pkg.utils.health import (
    register_health_check,
    set_status_ready,
    set_status_stopping,
    start_health_server,
)
from pkg.utils.logging import setup_logging
from pkg.utils.metrics import start_metrics_server


class MazeServiceManager:
    """迷宫服务管理器 - 管理服务器生命周期"""

    def __init__(self):
        """初始化服务管理器"""
        self.server = None
        self.should_exit = False
        self.periodic_task = None

    def handle_graceful_shutdown(self, signum, _frame):
        """处理优雅关闭信号"""
        logging.info(f"收到信号 {signum}, 准备关闭服务...")
        self.should_exit = True
        set_status_stopping()

        # 停止gRPC服务器
        if self.server:
            logging.info("正在关闭gRPC服务器...")
            self.server.stop(10)  # 给客户端10秒时间完成请求

        # 取消周期性任务
        if self.periodic_task and not self.periodic_task.done():
            self.periodic_task.cancel()

        logging.info("服务已关闭")

    async def check_db(self):
        """数据库健康检查"""
        try:
            repo = MazeRepository()
            await repo.count_active_mazes()
            return True
        except Exception as e:
            logging.error(f"数据库健康检查失败: {e!s}")
            return False

    async def init_database(self):
        """初始化数据库"""
        try:
            maze_repo = MazeRepository()
            # 确保数据库表已创建
            async with await maze_repo._get_db() as conn:
                await maze_repo._init_tables(conn)
            logging.info("数据库初始化成功")
        except Exception as e:
            logging.error(f"数据库初始化失败: {e!s}")
            raise

    async def init_services(self):
        """初始化服务组件"""
        # 初始化仓库
        maze_repository = MazeRepository()

        # 初始化服务
        maze_generator = MazeGenerator()
        knowledge_service = KnowledgeService()
        progress_service = ProgressService()

        # 创建主服务
        maze_service = MazeService(
            maze_repository=maze_repository,
            maze_generator=maze_generator,
            knowledge_service=knowledge_service,
            progress_service=progress_service
        )

        return maze_service

    async def start_periodic_tasks(self):
        """启动周期性任务, 如清理旧数据等"""
        maze_repo = MazeRepository()

        while not self.should_exit:
            try:
                # 每天清理一次30天前已完成的迷宫
                deleted_count = await maze_repo.cleanup_old_mazes(days=30)
                logging.info(f"清理了 {deleted_count} 个旧的已完成迷宫")
            except Exception as e:
                logging.error(f"执行周期性任务时出错: {e!s}")

            # 每24小时执行一次
            await asyncio.sleep(24 * 60 * 60)

    async def run(self):
        """运行主服务"""
        try:
            # 加载配置
            load_config()

            # 设置日志
            setup_logging()

            # 获取配置值
            grpc_port = get_value("grpc.port", 50057)
            max_workers = get_value("grpc.max_workers", 10)
            metrics_enabled = get_value("metrics.enabled", True)
            metrics_port = get_value("metrics.port", 51057)
            health_enabled = get_value("health.enabled", True)
            health_port = get_value("health.port", 51058)

            # 初始化数据库
            await self.init_database()

            # 初始化服务
            maze_service = await self.init_services()

            # 注册信号处理程序
            signal.signal(signal.SIGINT, self.handle_graceful_shutdown)
            signal.signal(signal.SIGTERM, self.handle_graceful_shutdown)

            # 启动健康检查服务
            if health_enabled:
                register_health_check("database", self.check_db)
                start_health_server(health_port)
                logging.info(f"健康检查服务已启动, 端口: {health_port}")

            # 启动指标服务
            if metrics_enabled:
                start_metrics_server(metrics_port)
                logging.info(f"指标服务已启动, 端口: {metrics_port}")

            # 创建gRPC服务器
            self.server = grpc.server(
                futures.ThreadPoolExecutor(max_workers=max_workers),
                maximum_concurrent_rpcs=get_value("grpc.max_concurrent_rpcs", 100),
                options=[
                    ('grpc.max_send_message_length', get_value("grpc.max_message_length", 1024 * 1024 * 10)),
                    ('grpc.max_receive_message_length', get_value("grpc.max_message_length", 1024 * 1024 * 10)),
                ]
            )

            # 设置gRPC服务
            setup_grpc_server(self.server, maze_service)

            # 启动gRPC服务器
            self.server.add_insecure_port(f'[::]:{grpc_port}')
            self.server.start()

            # 服务已准备好
            set_status_ready()
            logging.info(f"迷宫服务已启动, gRPC端口: {grpc_port}")

            # 启动周期性任务
            self.periodic_task = asyncio.create_task(self.start_periodic_tasks())

            # 保持服务器运行
            while not self.should_exit:
                await asyncio.sleep(1)

            # 取消周期性任务
            if self.periodic_task and not self.periodic_task.done():
                self.periodic_task.cancel()

        except Exception as e:
            logging.error(f"启动服务时出错: {e}", exc_info=True)
            sys.exit(1)


def main():
    """主函数"""
    service_manager = MazeServiceManager()

    try:
        # 运行主函数
        asyncio.run(service_manager.run())
    except KeyboardInterrupt:
        logging.info("用户中断, 正在关闭服务...")
    except Exception as e:
        logging.error(f"服务异常终止: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
