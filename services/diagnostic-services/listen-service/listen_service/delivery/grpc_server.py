"""
gRPC服务器模块

提供gRPC服务器的基本实现。
"""

import asyncio
import grpc
import structlog
import time
import uuid
from grpc import aio
from typing import Any

from ..config.settings import get_settings
from ..core.audio_analyzer import AudioAnalyzer
from ..core.tcm_analyzer import TCMFeatureExtractor
from ..utils.cache import get_cache
from ..utils.performance import async_timer

logger = structlog.get_logger(__name__)


class ListenServiceGRPCServer:
    """Listen Service gRPC服务器"""

    def __init__(self, port: int = 50051):
        self.port = port
        self.server = None
        self.settings = get_settings()

    async def start(self):
        """启动gRPC服务器"""
        try:
            self.server = aio.server()
            
            # 添加端口
            listen_port = f'[::]:{self.port}'
            self.server.add_insecure_port(listen_port)
            
            # 启动服务器
            await self.server.start()
            
            logger.info("gRPC服务器启动", port=self.port)
            
            # 等待终止
            await self.server.wait_for_termination()
            
        except Exception as e:
            logger.error("gRPC服务器启动失败", error=str(e))
            raise

    async def stop(self):
        """停止gRPC服务器"""
        if self.server:
            await self.server.stop(grace=5)
            logger.info("gRPC服务器已停止")


async def main():
    """主函数"""
    server = ListenServiceGRPCServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
