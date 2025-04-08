#!/bin/bash
# 从标准化目录结构重构恢复到原始状态的脚本

set -e

echo "=== 开始恢复到重构前状态 ==="

# 定义工作目录
BASE_DIR=$(pwd)
echo "工作目录: $BASE_DIR"

# 检查是否在正确的目录中
if [[ ! -d "$BASE_DIR/internal" || ! -d "$BASE_DIR/cmd" ]]; then
  echo "❌ 错误: 请在services/rag-service目录下运行此脚本，且确保已执行过重构"
  exit 1
fi

# 检查go-src目录是否存在
if [[ ! -d "$BASE_DIR/go-src" ]]; then
  echo "⚠️ 警告: go-src目录不存在，无法恢复原始导入路径"
  echo "请确保备份了原始状态，或者重新克隆仓库"
  exit 1
fi

# 恢复go.mod文件
echo "恢复go.mod文件..."
sed -i '.bak' 's|module github.com/suoke/suoke_life/services/rag-service|module github.com/suoke/suoke_life/services/rag-service/go-src|g' go.mod
rm -f go.mod.bak

# 恢复main.go文件
echo "恢复main.go文件..."
if [[ -f "$BASE_DIR/cmd/main.go.original" ]]; then
  cp -f cmd/main.go.original main.go
else
  cp -f cmd/main.go main.go
  sed -i '.bak' 's|github.com/suoke/suoke_life/services/rag-service/internal|github.com/suoke/suoke_life/services/rag-service/go-src|g' main.go
  rm -f main.go.bak
fi

echo "注意: 该脚本只恢复了go.mod和main.go文件到原始状态"
echo "如果要完全恢复，建议清理重构后的目录结构:"
echo "rm -rf internal pkg cmd"

echo "=== 恢复完成 ==="
echo "现在可以继续使用原始的目录结构和导入路径" 