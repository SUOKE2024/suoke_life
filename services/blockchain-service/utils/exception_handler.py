"""
exception_handler - 索克生活项目模块
"""

import logging
import traceback
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class GlobalExceptionHandler:
    """全局异常处理器"""

    @staticmethod
    def handle_exception(
        exc: Exception, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """处理异常"""
        error_info = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
            "traceback": traceback.format_exc(),
        }

        logger.error(f"全局异常: {error_info}")

        return {
            "success": False,
            "error": error_info["error_message"],
            "error_type": error_info["error_type"],
            "timestamp": error_info["timestamp"],
        }
