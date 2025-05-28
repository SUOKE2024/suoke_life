#!/usr/bin/env python3
"""
索儿智能体服务启动脚本

简化的服务启动入口
"""

import os
import sys
import uvicorn

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from soer_service.main import create_app

def main():
    """主函数"""
    # 设置默认环境变量
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8003")
    
    # 创建应用
    app = create_app()
    
    # 启动服务
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8003)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )

if __name__ == "__main__":
    main() 