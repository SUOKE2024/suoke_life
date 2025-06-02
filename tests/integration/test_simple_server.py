#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的无障碍服务测试服务器
用于验证基础功能和依赖
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_simple_app() -> FastAPI:
    """创建简化的FastAPI应用"""
    app = FastAPI(
        title="无障碍服务测试",
        description="简化的无障碍服务用于测试",
        version="0.1.0"
    )

    @app.get("/")
    async def root():
        return {
            "service": "accessibility-service-test",
            "status": "running",
            "message": "无障碍服务测试版本正在运行"
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "accessibility-service-test"
        }

    @app.get("/api/v1/accessibility/test")
    async def test_endpoint():
        return {
            "success": True,
            "message": "无障碍服务API测试成功",
            "features": [
                "导盲服务",
                "语音辅助",
                "屏幕阅读",
                "内容转换"
            ]
        }

    return app

def main():
    """主函数"""
    logger.info("启动简化的无障碍服务测试服务器...")

    try:
        app = create_simple_app()

        logger.info("服务器将在 http://localhost:50051 启动")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=50051,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()