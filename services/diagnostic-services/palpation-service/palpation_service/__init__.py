"""
__init__ - 索克生活项目模块
"""

    from .main import app
    from .main import main

"""
索克生活触诊服务包

基于AI的中医触诊智能分析微服务，提供多模态数据融合、
智能分析和预测功能。
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"


# 延迟导入以避免循环依赖
def get_app():
    """获取FastAPI应用实例"""

    return app


def get_main():
    """获取主函数"""

    return main


__all__ = ["__version__", "get_app", "get_main"]
