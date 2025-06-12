"""老克智能体服务主入口文件"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from laoke_service.api.routes import app
from laoke_service.core.agent import get_agent, shutdown_agent
from laoke_service.core.config import get_config, validate_config
from laoke_service.core.logging import get_logger, setup_logging


class ServiceManager:
    """服务管理器"""

    def __init__(self):
        self.logger: Optional[any] = None
        self.config = None
        self.shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        """初始化服务"""
        try:
            # 加载配置
            self.config = get_config()

            # 初始化日志系统
            setup_logging()
            self.logger = get_logger("service_manager")

            self.logger.info("老克智能体服务初始化开始")

            # 验证配置
            if not validate_config():
                raise RuntimeError("配置验证失败")

            # 初始化智能体
            agent = get_agent()
            self.logger.info("老克智能体初始化完成")

            # 设置信号处理
            self._setup_signal_handlers()

            self.logger.info(
                f"老克智能体服务初始化完成 - "
                f"环境: {self.config.service.environment}, "
                f"版本: {self.config.service.version}"
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"服务初始化失败: {e}")
            else:
                print(f"服务初始化失败: {e}")
            raise

    def _setup_signal_handlers(self) -> None:
        """设置信号处理器"""

        def signal_handler(signum, frame):
            self.logger.info(f"收到信号 {signum}，开始关闭服务...")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def run_rest_server(self) -> None:
        """运行REST服务器"""
        import uvicorn

        config = uvicorn.Config(
            app=app,
            host=self.config.server.rest_host,
            port=self.config.server.rest_port,
            workers=1,  # 单进程模式
            log_level="info" if not self.config.service.debug else "debug",
            access_log=True,
            reload=False,  # 生产环境不使用自动重载
        )

        server = uvicorn.Server(config)

        self.logger.info(
            f"REST服务器启动中 - "
            f"{self.config.server.rest_host}:{self.config.server.rest_port}"
        )

        # 在后台运行服务器
        server_task = asyncio.create_task(server.serve())

        try:
            # 等待关闭信号
            await self.shutdown_event.wait()

            self.logger.info("正在关闭REST服务器...")

            # 关闭服务器
            server.should_exit = True
            await server_task

        except Exception as e:
            self.logger.error(f"REST服务器运行错误: {e}")
            raise

    async def run_grpc_server(self) -> None:
        """运行gRPC服务器"""
        try:
            from concurrent import futures

            import grpc

            # 创建gRPC服务器
            server = grpc.aio.server(
                futures.ThreadPoolExecutor(
                    max_workers=self.config.server.grpc_max_workers
                )
            )

            # 添加服务实现（待实现）
            # add_LaokeServiceServicer_to_server(LaokeServiceImpl(), server)

            listen_addr = (
                f"{self.config.server.grpc_host}:{self.config.server.grpc_port}"
            )
            server.add_insecure_port(listen_addr)

            self.logger.info(f"gRPC服务器启动中 - {listen_addr}")

            await server.start()

            # 等待关闭信号
            await self.shutdown_event.wait()

            self.logger.info("正在关闭gRPC服务器...")
            await server.stop(grace=5.0)

        except ImportError:
            self.logger.warning("grpcio未安装，跳过gRPC服务器")
        except Exception as e:
            self.logger.error(f"gRPC服务器运行错误: {e}")
            raise

    async def shutdown(self) -> None:
        """关闭服务"""
        try:
            self.logger.info("开始关闭老克智能体服务...")

            # 关闭智能体
            await shutdown_agent()

            self.logger.info("老克智能体服务已关闭")

        except Exception as e:
            self.logger.error(f"服务关闭错误: {e}")

    async def run(self) -> None:
        """运行服务"""
        try:
            await self.initialize()

            # 创建任务列表
            tasks = []

            # REST服务器任务
            tasks.append(asyncio.create_task(self.run_rest_server()))

            # gRPC服务器任务（可选）
            if self.config.server.grpc_port:
                tasks.append(asyncio.create_task(self.run_grpc_server()))

            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            if self.logger:
                self.logger.error(f"服务运行错误: {e}")
            raise
        finally:
            await self.shutdown()


async def main() -> None:
    """主函数"""
    service_manager = ServiceManager()

    try:
        await service_manager.run()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在关闭服务...")
    except Exception as e:
        print(f"服务运行失败: {e}")
        sys.exit(1)


def cli_main() -> None:
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="老克智能体服务")
    parser.add_argument(
        "--config", type=str, help="配置文件路径", default="config/config.yaml"
    )
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--host", type=str, help="服务器主机地址", default=None)
    parser.add_argument("--port", type=int, help="服务器端口", default=None)

    args = parser.parse_args()

    # 设置环境变量
    if args.debug:
        import os

        # os.environ["SERVICE__DEBUG"] = "true"  # 生产环境禁用调试模式

    if args.host:
        import os

        os.environ["SERVER__REST_HOST"] = args.host

    if args.port:
        import os

        os.environ["SERVER__REST_PORT"] = str(args.port)

    # 运行服务
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
