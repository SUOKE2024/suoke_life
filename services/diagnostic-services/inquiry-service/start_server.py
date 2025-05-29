#!/usr/bin/env python3

"""
简化的问诊服务启动脚本
"""

import os
import sys

# 设置Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入并启动服务
from cmd.server import serve

if __name__ == "__main__":
    print("正在启动问诊服务...")
    serve()
