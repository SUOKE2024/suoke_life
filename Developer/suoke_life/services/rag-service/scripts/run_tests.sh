#!/bin/bash

# 设置所需环境变量
export PYTHONPATH=$(pwd):$PYTHONPATH

# 显示测试开始信息
echo "===================================================="
echo "开始执行 Web 搜索模块测试"
echo "===================================================="

# 先运行单元测试
echo "正在运行单元测试..."
python -m pytest tests/test_web_search/test_search_provider.py -v
python -m pytest tests/test_web_search/test_content_processor.py -v
python -m pytest tests/test_web_search/test_knowledge_integration.py -v
python -m pytest tests/test_web_search/test_api_routes.py -v

# 运行集成测试
echo "正在运行集成测试..."
python -m pytest tests/test_web_search/test_integration.py -v

# 显示测试完成信息
echo "===================================================="
echo "Web 搜索模块测试完成"
echo "====================================================" 