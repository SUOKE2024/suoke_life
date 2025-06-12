
"""
main - 索克生活项目模块
"""

import uvicorn

from blockchain_service.api.main import create_app

"""
blockchain - service 主入口文件
"""


def main() -> None:
    """主函数"""
    app = create_app()
    uvicorn.run(
        app,
        host = "0.0.0.0",
        port = 8000,
        reload = True
    )

if __name__=="__main__":
    main()
