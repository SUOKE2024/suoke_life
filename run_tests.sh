#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 设置 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 创建测试目录
mkdir -p tests/logs

# 运行测试
pytest tests/ -v --asyncio-mode=strict "$@" 