#!/usr/bin/env python3
"""
算诊微服务启动脚本

用于快速启动和测试算诊微服务
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    from calculation_service.cmd.server import main
    main() 