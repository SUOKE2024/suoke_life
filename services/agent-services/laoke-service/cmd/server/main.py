#!/usr/bin/env python3

"""
老克智能体服务器启动脚本
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 项目导入
from internal.delivery.grpc_server import GRPCServer  # noqa: E402
from internal.delivery.rest_server import RESTServer  # noqa: E402
from pkg.container.container import ServiceContainer  # noqa: E402
from pkg.utils.config import Config  # noqa: E402
from pkg.utils.logger import setup_logger  # noqa: E402

logger = logging.getLogger(__name__)

class LaokeSevice:
    """老克智能体服务"""

    def __init__(self):
        self.container: ServiceContainer | None = None
        self.grpc_server: GRPCServer | None = None
        self.rest_server: RESTServer | None = None
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        """初始化服务"""
        try:
            # 设置日志
            setup_logger()
            logger.info("开始初始化老克智能体服务...")

            # 加载配置
            config = Config()

            # 创建依赖注入容器
            self.container = ServiceContainer(config)
            await self.container.initialize()

            # 创建服务器
            self.grpc_server = GRPCServer(self.container)
            self.rest_server = RESTServer(self.container)

            logger.info("老克智能体服务初始化完成")

        except Exception as e:
            logger.error(f"服务初始化失败: {str(e)}")
            raise

    async def start(self) -> None:
        """启动服务"""
        try:
            logger.info("启动老克智能体服务...")

            # 启动服务器
            await asyncio.gather(
                self.grpc_server.start(),
                self.rest_server.start()
            )

            logger.info("老克智能体服务启动成功")

            # 等待关闭信号
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"服务启动失败: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """关闭服务"""
        try:
            logger.info("开始关闭老克智能体服务...")

            # 关闭服务器
            if self.grpc_server:
                await self.grpc_server.stop()

            if self.rest_server:
                await self.rest_server.stop()

            # 关闭容器
            if self.container:
                await self.container.close()

            logger.info("老克智能体服务已关闭")

        except Exception as e:
            logger.error(f"服务关闭失败: {str(e)}")

    def _setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，开始优雅关闭...")
            self._shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """主函数"""
    service = LaokeSevice()

    try:
        # 初始化服务
        await service.initialize()

        # 设置信号处理器
        service._setup_signal_handlers()

        # 启动服务
        await service.start()

    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"服务运行异常: {str(e)}")
        return 1
    finally:
        # 关闭服务
        await service.shutdown()

    return 0

if __name__ == "__main__":
    # 设置环境变量
    os.environ.setdefault("PYTHONPATH", str(project_root))

    # 运行服务
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
