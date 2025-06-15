#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务启动脚本

简单的服务启动入口，用于开发和测试。
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.server.main import main

if __name__ == "__main__":
    main() 