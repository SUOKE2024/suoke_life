#!/bin/bash

# 无障碍服务测试执行脚本

set -e

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 启用测试环境（跳过mediapipe等依赖）
export TEST_ENVIRONMENT=true

# 设置测试日志级别
export LOG_LEVEL=INFO

# 判断是运行单元测试还是集成测试
if [[ "$1" == "integration" ]]; then
    echo "运行集成测试..."
    pytest test/integration/
elif [[ "$1" == "all" ]]; then
    echo "运行所有测试..."
    pytest test/ --cov=internal --cov-report=term --cov-report=html
else
    echo "运行单元测试..."
    pytest test/ --exclude=integration --cov=internal --cov-report=term
fi

# 如果生成了覆盖率报告，显示位置
if [[ -d "htmlcov" ]]; then
    echo "覆盖率报告已生成: $(pwd)/htmlcov/index.html"
fi 