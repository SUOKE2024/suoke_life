
"""
main - 索克生活项目模块
"""

from auth_service.cmd.server.main import create_app

"""认证服务主应用文件"""


# 创建应用实例供测试和其他模块使用
app = create_app()

__all__ = ["app", "create_app"]