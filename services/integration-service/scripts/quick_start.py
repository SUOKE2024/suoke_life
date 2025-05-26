#!/usr/bin/env python3
"""
Integration Service Quick Start Script
快速启动脚本 - 用于开发和测试
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault("APP_DEBUG", "true")
os.environ.setdefault("APP_LOG_LEVEL", "INFO")
os.environ.setdefault("APP_HOST", "localhost")
os.environ.setdefault("APP_PORT", "8003")

# 数据库配置（使用SQLite进行快速测试）
os.environ.setdefault("DATABASE_URL", "sqlite:///./integration_service.db")
os.environ.setdefault("DATABASE_ECHO", "false")

# Redis配置
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "0")

# 平台配置（启用所有平台用于测试）
platforms = ["apple_health", "google_fit", "fitbit", "xiaomi", "huawei", "wechat", "alipay"]
for platform in platforms:
    os.environ.setdefault(f"PLATFORM_{platform.upper()}_ENABLED", "true")
    os.environ.setdefault(f"PLATFORM_{platform.upper()}_CLIENT_ID", f"test_{platform}_client_id")
    os.environ.setdefault(f"PLATFORM_{platform.upper()}_CLIENT_SECRET", f"test_{platform}_client_secret")


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


async def check_dependencies():
    """检查依赖"""
    logger = logging.getLogger(__name__)
    
    # 检查Redis连接（可选）
    try:
        import aioredis
        redis = aioredis.from_url("redis://localhost:6379/0")
        await redis.ping()
        await redis.close()
        logger.info("✓ Redis连接正常")
    except Exception as e:
        logger.warning(f"⚠ Redis连接失败: {str(e)} (将使用内存缓存)")
        # 设置为使用内存缓存
        os.environ["REDIS_HOST"] = "memory"
    
    logger.info("依赖检查完成")


def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Integration Service 快速启动")
    logger.info("=" * 60)
    
    # 检查依赖
    try:
        asyncio.run(check_dependencies())
    except Exception as e:
        logger.error(f"依赖检查失败: {str(e)}")
    
    # 导入并启动应用
    try:
        from cmd.server.main import main as start_server
        logger.info("正在启动服务...")
        start_server()
    except ImportError as e:
        logger.error(f"导入模块失败: {str(e)}")
        logger.info("请确保在正确的目录中运行此脚本")
        sys.exit(1)
    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 