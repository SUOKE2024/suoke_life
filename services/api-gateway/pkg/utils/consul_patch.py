from typing import Dict, List, Any, Optional, Union

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
