"""
__init__ - 索克生活项目模块
"""

import sys
from typing import Optional, list

#!/usr/bin/env python3
"""
CLI模块 - 提供命令行接口
"""

def main(args: list[str] | None = None) -> int:
    """主命令行入口点"""
    if args is None:
        args = sys.argv[1:]

    print("小艾服务 CLI")
    print("可用命令:")
    print("  server - 启动服务器")
    print("  worker - 启动工作进程")
    print("  status - 查看状态")

    return 0

def run_server() -> int:
    """服务器启动入口点"""
    print("启动小艾服务器...")
    # 这里应该启动实际的服务器
    return 0

def run_worker() -> int:
    """工作进程启动入口点"""
    print("启动小艾工作进程...")
    # 这里应该启动实际的工作进程
    return 0

# 向后兼容的别名
_main = main
_run_server = run_server
_run_worker = run_worker

__all__ = [
    "main",
    "run_server",
    "run_worker",
]
