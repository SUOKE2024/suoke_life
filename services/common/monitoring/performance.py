"""
performance - 索克生活项目模块
"""

from datetime import datetime
from functools import wraps
from typing import Dict, Any
import logging
import psutil
import time



logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""

    @staticmethod
    def monitor_execution_time(func):
        """监控函数执行时间"""
        @wraps(func)
        def wrapper( *args, **kwargs):
            """TODO: 添加文档字符串"""
            start_time = time.time()
            try:
                result = func( *args, **kwargs)
                execution_time = time.time() - start_time

                # 记录执行时间
                logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.4f}秒")

                # 如果执行时间过长，发出警告
                if execution_time > 5.0:
                    logger.warning(f"函数 {func.__name__} 执行时间过长: {execution_time:.4f}秒")

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.4f}秒，错误: {e}")
                raise
        return wrapper

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """获取系统指标"""
        return {
            "cpu_percent": psutil.cpu_percent(interval = 1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage(' / ').percent,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def monitor_memory_usage(func):
        """监控内存使用"""
        @wraps(func)
        def wrapper( *args, **kwargs):
            """TODO: 添加文档字符串"""
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            result = func( *args, **kwargs)

            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = memory_after - memory_before

            logger.info(f"函数 {func.__name__} 内存使用变化: {memory_diff:.2f}MB")

            return result
        return wrapper
