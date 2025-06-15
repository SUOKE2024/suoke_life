#!/usr/bin/env python

"""
平台桥接初始化模块 - 提供平台检测和初始化功能
"""

import logging
import os
import platform

logger = logging.getLogger(__name__)

# 平台类型常量
PLATFORM_ANDROID = "android"
PLATFORM_IOS = "ios"
PLATFORM_MACOS = "macos"
PLATFORM_WINDOWS = "windows"
PLATFORM_LINUX = "linux"
PLATFORM_UNKNOWN = "unknown"

# 当前检测到的平台
_current_platform = PLATFORM_UNKNOWN


def init_platform() -> None:
    """
    初始化平台检测，设置必要的环境变量
    """
    global _current_platform

    # 检测操作系统平台
    system = platform.system().lower()

    if system == "darwin":
        # 检测是否为iOS或macOS
        if os.environ.get("FLUTTER_RUNTIME") == "true":
            # 如果在Flutter环境下运行，进一步检测是iOS还是macOS
            if os.environ.get("MOBILE_PLATFORM") == "ios":
                _current_platform = PLATFORM_IOS
            else:
                _current_platform = PLATFORM_MACOS
        else:
            _current_platform = PLATFORM_MACOS
    elif system == "linux":
        # 检测是否为Android或Linux
        if (
            os.environ.get("FLUTTER_RUNTIME") == "true"
            and os.environ.get("MOBILE_PLATFORM") == "android"
        ):
            _current_platform = PLATFORM_ANDROID
        else:
            _current_platform = PLATFORM_LINUX
    elif system == "windows":
        _current_platform = PLATFORM_WINDOWS
    else:
        _current_platform = PLATFORM_UNKNOWN

    # 记录平台信息
    logger.info(f"检测到平台: {_current_platform}")

    # 设置环境变量以便其他模块使用
    os.environ["DETECTED_PLATFORM"] = _current_platform


def get_platform() -> None:
    """
    获取当前检测到的平台

    Returns:
        平台类型字符串
    """
    global _current_platform
    return _current_platform


def is_mobile() -> None:
    """
    检查当前平台是否为移动设备

    Returns:
        是否为移动设备
    """
    return _current_platform in [PLATFORM_ANDROID, PLATFORM_IOS]


def is_desktop() -> None:
    """
    检查当前平台是否为桌面设备

    Returns:
        是否为桌面设备
    """
    return _current_platform in [PLATFORM_MACOS, PLATFORM_WINDOWS, PLATFORM_LINUX]


# 自动初始化平台检测
init_platform()
