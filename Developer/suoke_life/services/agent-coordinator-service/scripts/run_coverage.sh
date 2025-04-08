#!/bin/bash
set -e

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 打印开始信息
echo "📊 开始生成测试覆盖率报告..."

# 创建测试覆盖率输出目录
mkdir -p coverage

# 首先运行单元测试
echo "🔍 运行单元测试..."
go test -v ./internal/handlers/... -coverprofile=coverage/unit.out

# 然后运行集成测试
echo "🔍 运行集成测试..."
go test -v ./internal/tests/integration/... -coverprofile=coverage/integration.out

# 合并覆盖率报告
echo "📈 合并覆盖率报告..."
# 确保gocovmerge已安装
if ! command -v gocovmerge &> /dev/null; then
  echo "正在安装gocovmerge..."
  go install github.com/wadey/gocovmerge@latest
fi

# 如果安装失败，使用备选方案
if command -v gocovmerge &> /dev/null; then
  gocovmerge coverage/unit.out coverage/integration.out > coverage/coverage.out
else
  echo "警告: gocovmerge未安装，使用单元测试报告作为完整报告"
  cp coverage/unit.out coverage/coverage.out
fi

# 生成HTML报告
go tool cover -html=coverage/coverage.out -o coverage/coverage.html
echo "✅ 测试覆盖率报告生成成功!"
echo "📁 报告位置: $(pwd)/coverage/coverage.html"

# 输出覆盖率统计
go tool cover -func=coverage/coverage.out