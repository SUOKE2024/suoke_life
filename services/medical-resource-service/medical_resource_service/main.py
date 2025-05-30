"""
medical-resource-service 主入口文件
"""

import uvicorn
from fastapi import FastAPI
from medical_resource_service.api.main import create_app

def main():
    """主函数"""
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
