#!/usr/bin/env python3
"""
通信服务主入口文件
整合消息总线和RAG服务的统一启动入口
"""

import asyncio
import logging
import signal
import sys
from typing import Any

from communication_service import CommunicationService

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class CommunicationServiceManager:
    """通信服务管理器"""

    def __init__(self):
        """初始化服务管理器"""
        self.service = CommunicationService()
        self._shutdown_event = asyncio.Event()

    def handle_shutdown(self, signum: int, frame: Any) -> None:
        """处理关闭信号"""
        logger.info(f"收到关闭信号: {signum}")
        asyncio.create_task(self.shutdown())

    async def shutdown(self) -> None:
        """关闭服务"""
        logger.info("正在关闭通信服务...")
        await self.service.stop()
        self._shutdown_event.set()

    async def run(self) -> None:
        """运行服务"""
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

        try:
            # 启动服务
            await self.service.start()

            # 等待关闭信号
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"服务运行失败: {e}")
            sys.exit(1)
        finally:
            await self.service.stop()


async def main() -> None:
    """主函数"""
    logger.info("启动索克生活通信服务...")

    manager = CommunicationServiceManager()
    await manager.run()

    logger.info("通信服务已停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在退出...")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)
