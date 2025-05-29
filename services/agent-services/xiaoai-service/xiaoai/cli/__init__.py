#!/usr/bin/env python3
"""
小艾智能体命令行接口
XiaoAI Agent Command Line Interface

提供小艾智能体的命令行工具, 包括:
- 服务器启动和管理
- 工作进程管理
- 配置管理
- 健康检查
- 开发工具

使用示例:
    $ xiaoai --help
    $ xiaoai-server --port 8000
    $ xiaoai-worker --concurrency 4
"""

from __future__ import annotations

_all__ = [
    "main",
    "run_server",
    "run_worker",
]

# 延迟导入以提高启动速度
def main() -> None:
    """主命令行入口点"""
    from .main import main as _main
    _main()


def run_server() -> None:
    """服务器启动入口点"""
    from .server import run_server as _run_server
    _run_server()


def run_worker() -> None:
    """工作进程启动入口点"""
    from .worker import run_worker as _run_worker
    _run_worker()
