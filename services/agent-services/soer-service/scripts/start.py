#!/usr/bin/env python3
"""
索儿服务启动脚本

用于启动 soer-service 微服务
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn

from soer_service.config.settings import get_settings
from soer_service.core.logging import get_logger
from soer_service.main import app

logger = get_logger(__name__)


async def main():
    """主函数"""
    try:
        settings = get_settings()

        logger.info("🚀 启动索儿服务...")
        logger.info(f"环境: {settings.environment}")
        logger.info(f"调试模式: {settings.debug}")
        logger.info(f"服务端口: {settings.port}")

        # 启动 FastAPI 应用
        config = uvicorn.Config(
            app=app,
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info" if not settings.debug else "debug",
            access_log=True
        )

        server = uvicorn.Server(config)
        await server.serve()

    except KeyboardInterrupt:
        logger.info("👋 服务已停止")
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
