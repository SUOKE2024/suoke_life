"""
main - 索克生活项目模块
"""

from api_gateway.api.main import create_app
import uvicorn

"""
api-gateway 主入口文件
"""


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
