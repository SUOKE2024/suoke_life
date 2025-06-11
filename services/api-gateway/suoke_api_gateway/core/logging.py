"""日志配置模块"""
import logging


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)

def setup_logging() -> None:
    """设置日志配置"""
    logging.basicConfig(level=logging.INFO)
