"""
用户服务主入口文件
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """主入口函数"""
    try:
        # 导入并运行现有的 main.py
        from cmd.server.main import main as server_main

        server_main()
    except ImportError:
        # 如果没有找到现有的 main.py，提供一个简单的启动函数
        print("用户服务启动中...")
        print("请确保已正确配置服务依赖项")


if __name__ == "__main__":
    main()
