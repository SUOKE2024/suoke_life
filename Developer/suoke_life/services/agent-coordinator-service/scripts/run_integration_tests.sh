#!/bin/bash
set -e

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 打印开始信息
echo "📋 开始运行集成测试..."

# 检查测试目录是否存在
if [ ! -d "internal/tests/integration" ]; then
  echo "❌ 测试目录不存在"
  exit 1
fi

# 运行集成测试
go test -v ./internal/tests/integration/...

# 如果测试成功，打印成功信息
if [ $? -eq 0 ]; then
  echo "✅ 集成测试全部通过!"
else
  echo "❌ 集成测试失败!"
  exit 1
fi