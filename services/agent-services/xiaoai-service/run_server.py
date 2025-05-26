#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体服务启动脚本
XiaoAI Agent Service Startup Script
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import asyncio
    from xiaoai.cli.main import main
    asyncio.run(main()) 