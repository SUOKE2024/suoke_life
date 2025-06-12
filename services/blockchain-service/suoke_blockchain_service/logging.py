"""
日志模块
"""

import logging
import sys


def configure_logging() -> None:
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)

class LoggerMixin:
    """日志混入类"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        return get_logger(self.__class__.__name__)

if __name__=="__main__":
    configure_logging()
    print("日志模块已配置")
