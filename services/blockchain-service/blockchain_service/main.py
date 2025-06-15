"""
主入口模块

区块链服务的主入口点。
"""

import uvicorn

from .api.main import create_app
from .config.settings import get_settings
from .utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    """主函数"""
    settings = get_settings()

    logger.info("启动区块链服务", extra={
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    })

    # 创建应用
    app = create_app()

    # 启动服务
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.monitoring.log_level.lower()
    )


if __name__ == "__main__":
    main()
