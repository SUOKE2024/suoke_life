#!/usr/bin/env python3
"""
修复特定文件的语法错误
"""

import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_consul_patch():
    """修复consul_patch.py文件"""
    file_path = "services/api-gateway/pkg/utils/consul_patch.py"

    # 重写整个文件内容
    content = '''from typing import Dict, List, Any, Optional, Union

"""
consul_patch - 索克生活项目模块
"""

import asyncio
import functools
import sys

#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
修补python-consul库的兼容性问题
在Python 3.13中，asyncio.coroutine装饰器已被移除
"""


# 检查Python版本，仅当Python 3.10+并且缺少coroutine装饰器时执行修补
if sys.version_info >= (3, 10) and not hasattr(asyncio, 'coroutine'):
    # 创建一个兼容性修补，模拟旧的coroutine装饰器的行为
    def async_coroutine_patch(func):
        """
        模拟原始asyncio.coroutine装饰器
        将普通函数标记为协程函数
        """
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper

    # 将修补版本添加到asyncio模块
    asyncio.coroutine = async_coroutine_patch
'''

    try:
        # 验证语法
        ast.parse(content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"成功修复 {file_path}")
        return True
    except Exception as e:
        logger.error(f"修复失败: {e}")
        return False


def fix_exception_handler():
    """修复exception_handler.py文件"""
    file_path = "services/api-gateway/utils/exception_handler.py"

    content = '''"""
exception_handler - 索克生活项目模块
"""

from datetime import datetime
import logging
import traceback
from typing import Any

logger = logging.getLogger(__name__)

class GlobalExceptionHandler:
    """全局异常处理器"""

    @staticmethod
    def handle_exception(exc: Exception, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """处理异常"""
        error_info = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
            "traceback": traceback.format_exc()
        }

        logger.error(f"全局异常: {error_info}")

        return {
            "success": False,
            "error": error_info["error_message"],
            "error_type": error_info["error_type"],
            "timestamp": error_info["timestamp"]
        }
'''

    try:
        # 验证语法
        ast.parse(content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"成功修复 {file_path}")
        return True
    except Exception as e:
        logger.error(f"修复失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("开始修复特定文件的语法错误...")

    success_count = 0

    if fix_consul_patch():
        success_count += 1

    if fix_exception_handler():
        success_count += 1

    logger.info(f"修复完成，成功修复 {success_count} 个文件")


if __name__ == "__main__":
    main()
