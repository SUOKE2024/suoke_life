#!/usr/bin/env python3
"""

from __future__ import annotations
    from .main import main as _main
    from .server import run_server as _run_server
    from .worker import run_worker as _run_worker


小艾智能体命令行接口
XiaoAI Agent Command Line Interface

提供小艾智能体的命令行工具, 包括:
    pass
- 服务器启动和管理
- 工作进程管理
- 配置管理
- 健康检查
- 开发工具

使用示例:
    pass
    $ xiaoai --help
    $ xiaoai-server --port 8000
    $ xiaoai-worker --concurrency 4
"""


_all__ = [
    "main",
    "run_server",
    "run_worker"]


# 延迟导入以提高启动速度
def main() -> None:
    pass
    """主命令行入口点"""

    _main()


def run_server() -> None:
    pass
    """服务器启动入口点"""

    _run_server()


def run_worker() -> None:
    pass
    """工作进程启动入口点"""

    _run_worker()
