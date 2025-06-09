"""
main - 索克生活项目模块
"""

from prometheus_client import start_http_server
from typing import Any
import asyncio
import signal
import structlog
import sys

"""
消息总线服务主入口
"""



# 配置结构化日志
structlog.configure(
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt = "iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class = dict,
    logger_factory = structlog.stdlib.LoggerFactory(),
    wrapper_class = structlog.stdlib.BoundLogger,
    cache_logger_on_first_use = True,
)

logger = structlog.get_logger(__name__)


class MessageBusService:
    """消息总线服务主类"""

    def __init__(self) - > None:
        """TODO: 添加文档字符串"""
        self.running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) - > None:
        """启动服务"""
        logger.info("启动消息总线服务...")
        self.running = True

        # 启动 Prometheus 监控服务器
        start_http_server(8000)
        logger.info("Prometheus 监控服务器已启动", port = 8000)

        # 等待关闭信号
        await self._shutdown_event.wait()

    async def stop(self) - > None:
        """停止服务"""
        logger.info("正在停止消息总线服务...")
        self.running = False
        self._shutdown_event.set()

    def handle_shutdown(self, signum: int, frame: Any) - > None:
        """处理关闭信号"""
        logger.info("收到关闭信号", signal = signum)
        asyncio.create_task(self.stop())


async def main() - > None:
    """主函数"""
    service = MessageBusService()

    # 注册信号处理器
    signal.signal(signal.SIGINT, service.handle_shutdown)
    signal.signal(signal.SIGTERM, service.handle_shutdown)

    try:
        await service.start()
    except Exception as e:
        logger.error("服务启动失败", error = str(e))
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
