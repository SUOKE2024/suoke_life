#!/usr/bin/env python3
"""
简单的服务器启动脚本

用于快速启动闻诊服务的REST API服务器。
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from listen_service.delivery.rest_api import create_rest_app
from listen_service.utils.logging import setup_logging


def main():
    """主函数"""
    # 设置日志
    setup_logging(
        level="INFO",
        format_type="console",
        service_name="listen-service",
    )
    
    # 创建应用
    app = create_rest_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
    )


if __name__ == "__main__":
    main() 