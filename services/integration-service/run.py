#!/usr/bin/env python3
"""
Integration Service 启动脚本
"""

import uvicorn
from integration_service.main import create_app
from integration_service.config import settings

if __name__ == "__main__":
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    ) 