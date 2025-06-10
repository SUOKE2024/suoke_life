from typing import Dict, List, Any, Optional, Union

"""
main - 索克生活项目模块
"""

from medical_resource_service.api.main import create_app
import uvicorn

"""
medical - resource - service 主入口文件
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

if __name__ == "__main__":
    main()
