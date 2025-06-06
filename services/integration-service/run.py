"""
run - 索克生活项目模块
"""

from integration_service.config import settings
from integration_service.main import create_app
import uvicorn

#!/usr/bin/env python3
"""
Integration Service 启动脚本
"""


if __name__ == "__main__":
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    ) 