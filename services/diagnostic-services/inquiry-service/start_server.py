from typing import Any, Dict, List, Optional, Union

"""
start_server - 索克生活项目模块
"""

import os
import sys
from cmd.server import serve

#! / usr / bin / env python3

"""
简化的问诊服务启动脚本
"""


# 设置Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入并启动服务

if __name__ == "__main__":
    print("正在启动问诊服务...")
    serve()
