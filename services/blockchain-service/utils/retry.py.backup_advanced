"""
retry - 索克生活项目模块
"""

from functools import wraps
from typing import Callable, Any, Type, Tuple
import logging
import time



logger = logging.getLogger(__name__)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """重试装饰器"""
    def decorator(func: Callable) - > Callable:
        """TODO: 添加文档字符串"""
        @wraps(func)
        def wrapper( * args, * *kwargs) - > Any:
            """TODO: 添加文档字符串"""
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func( * args, * *kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        logger.error(f"函数 {func.__name__} 重试 {max_attempts} 次后仍然失败: {e}")
                        raise

                    wait_time = delay * (backoff * * attempt)
                    logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败，{wait_time}秒后重试: {e}")
                    time.sleep(wait_time)

            raise last_exception
        return wrapper
    return decorator

class CircuitBreaker:
    """熔断器"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """TODO: 添加文档字符串"""
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, * args, * *kwargs) - > Any:
        """执行函数调用"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("熔断器开启，拒绝请求")

        try:
            result = func( * args, * *kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) - > None:
        """成功回调"""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) - > None:
        """失败回调"""
        self.failure_count + = 1
        self.last_failure_time = time.time()

        if self.failure_count > = self.failure_threshold:
            self.state = "OPEN"
