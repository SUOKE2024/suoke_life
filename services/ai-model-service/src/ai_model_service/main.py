"""AI Model Service 主入口"""

import asyncio
import signal
import sys
from typing import Any, Optional

import structlog
import uvicorn
from fastapi import FastAPI

from .api.app import create_app
from .config.settings import get_settings
from .utils.logging import setup_logging

logger = structlog.get_logger(__name__)


class AIModelService:
    """AI模型服务主类"""

    def __init__(self) -> None:
        """初始化服务"""
        self.settings = get_settings()
        self.app: Optional[FastAPI] = None
        self.server: Optional[uvicorn.Server] = None

        # 设置日志
        setup_logging(
            level=self.settings.monitoring.log_level,
            json_logs=self.settings.monitoring.json_logs,
            service_name=self.settings.app_name,
            service_version=self.settings.app_version,
        )

    async def start(self) -> None:
        """启动服务"""
        try:
            logger.info(
                "正在启动AI模型服务",
                app_name=self.settings.app_name,
                version=self.settings.app_version,
                host=self.settings.host,
                port=self.settings.port,
            )

            # 创建FastAPI应用
            self.app = create_app()

            # 配置uvicorn服务器
            config = uvicorn.Config(
                app=self.app,
                host=self.settings.host,
                port=self.settings.port,
                workers=1,  # 异步应用使用单进程
                log_config=None,  # 使用自定义日志配置
                access_log=False,  # 禁用访问日志，使用结构化日志
            )

            self.server = uvicorn.Server(config)

            # 设置信号处理
            self._setup_signal_handlers()

            # 启动服务器
            await self.server.serve()

        except Exception as e:
            logger.error("启动AI模型服务失败", error=str(e))
            raise

    async def shutdown(self) -> None:
        """关闭服务"""
        logger.info("正在关闭AI模型服务")

        if self.server:
            self.server.should_exit = True

        logger.info("AI模型服务已关闭")

    def _setup_signal_handlers(self) -> None:
        """设置信号处理器"""

        def signal_handler(signum: int, frame: Any) -> None:
            logger.info("收到关闭信号", signal=signum)
            if self.server:
                self.server.should_exit = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main() -> None:
    """主函数"""
    service = AIModelService()

    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error("服务运行异常", error=str(e))
        sys.exit(1)
    finally:
        await service.shutdown()


def cli_main() -> None:
    """命令行入口"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
    except Exception as e:
        logger.error("服务启动失败", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
