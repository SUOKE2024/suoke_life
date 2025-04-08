#!/bin/bash
# 标准化RAG服务目录结构的重构脚本

set -e

echo "=== 开始重构RAG服务目录结构 ==="

# 定义工作目录
BASE_DIR=$(pwd)
echo "工作目录: $BASE_DIR"

# 检查是否在正确的目录中
if [[ ! -d "$BASE_DIR/go-src" ]]; then
  echo "❌ 错误: 请在services/rag-service目录下运行此脚本"
  exit 1
fi

# 创建标准化目录结构
echo "创建标准化目录结构..."
mkdir -p cmd
mkdir -p internal/api
mkdir -p internal/config
mkdir -p internal/handlers
mkdir -p internal/middleware
mkdir -p internal/models
mkdir -p internal/rag
mkdir -p internal/storage/vector_store
mkdir -p internal/embeddings
mkdir -p internal/utils
mkdir -p pkg
mkdir -p tests
mkdir -p docs
mkdir -p deployment

# 移动main.go到cmd目录
echo "移动main.go到cmd目录..."
cp -f main.go cmd/main.go
# 修改cmd/main.go中的导入路径
sed -i '.bak' 's|github.com/suoke/suoke_life/services/rag-service/go-src|github.com/suoke/suoke_life/services/rag-service/internal|g' cmd/main.go
rm -f cmd/main.go.bak

# 安全复制函数 - 先检查目录是否存在且有内容
function safe_copy_module() {
  local src_dir="$1"
  local dst_dir="$2"
  local module_name="$3"
  
  echo "复制和更新${module_name}模块..."
  if [ ! -d "$src_dir" ]; then
    echo "注意: $src_dir 目录不存在，跳过${module_name}模块复制"
    return
  fi
  
  # 检查目录是否有文件
  if [ -z "$(ls -A $src_dir)" ]; then
    echo "注意: $src_dir 目录为空，跳过${module_name}模块复制"
    return
  fi
  
  # 复制并更新导入路径
  cp -r ${src_dir}/* ${dst_dir}/
  find ${dst_dir} -name "*.go" -exec sed -i '.bak' 's|github.com/suoke/suoke_life/services/rag-service/go-src|github.com/suoke/suoke_life/services/rag-service/internal|g' {} \;
  find ${dst_dir} -name "*.bak" -delete
  
  echo "✅ ${module_name}模块复制完成"
}

# 复制和更新各模块代码
safe_copy_module "go-src/config" "internal/config" "配置"
safe_copy_module "go-src/handlers" "internal/handlers" "处理器"
safe_copy_module "go-src/middleware" "internal/middleware" "中间件"
safe_copy_module "go-src/models" "internal/models" "模型"
safe_copy_module "go-src/rag" "internal/rag" "RAG"

# 向量存储模块需要特殊处理导入路径
echo "复制和更新向量存储模块..."
if [ -d "go-src/vector_store" ] && [ "$(ls -A go-src/vector_store)" ]; then
  cp -r go-src/vector_store/* internal/storage/vector_store/
  find internal/storage/vector_store -name "*.go" -exec sed -i '.bak' 's|github.com/suoke/suoke_life/services/rag-service/go-src/vector_store|github.com/suoke/suoke_life/services/rag-service/internal/storage/vector_store|g' {} \;
  find internal/storage/vector_store -name "*.go" -exec sed -i '.bak' 's|github.com/suoke/suoke_life/services/rag-service/go-src|github.com/suoke/suoke_life/services/rag-service/internal|g' {} \;
  find internal/storage/vector_store -name "*.bak" -delete
  echo "✅ 向量存储模块复制完成"
else
  echo "注意: go-src/vector_store 目录不存在或为空，跳过向量存储模块复制"
fi

safe_copy_module "go-src/embeddings" "internal/embeddings" "嵌入"
safe_copy_module "go-src/utils" "internal/utils" "工具"
safe_copy_module "go-src/api" "internal/api" "API"
safe_copy_module "go-src/database" "internal/database" "数据库"
safe_copy_module "go-src/core" "internal/core" "核心"
safe_copy_module "go-src/tests" "tests" "测试"

# 更新go.mod文件
echo "更新go.mod文件..."
sed -i '.bak' 's|module github.com/suoke/suoke_life/services/rag-service/go-src|module github.com/suoke/suoke_life/services/rag-service|g' go.mod
rm -f go.mod.bak

# 创建新的main.go，使用cmd/main.go的路径
echo "创建新的main.go..."
cat > main.go << EOH
package main

import (
	"github.com/suoke/suoke_life/services/rag-service/cmd"
)

func main() {
	cmd.Execute()
}
EOH

# 创建cmd/execute.go
echo "创建cmd/execute.go..."
cat > cmd/execute.go << EOH
package cmd

import (
	"os"
)

// Execute 启动主函数
func Execute() {
	// 启动主应用程序
	main()
	
	// 退出程序
	os.Exit(0)
}
EOH

# 修复所有错误的导入路径
echo "修复所有Go文件中的导入路径..."
find . -name "*.go" -type f ! -path "./go-src/*" ! -path "./archived_code/*" -exec sed -i '.bak' 's|github.com/suoke/suoke_life/services/rag-service/go-src|github.com/suoke/suoke_life/services/rag-service/internal|g' {} \;
find . -name "*.bak" -delete

# 创建README文件
echo "更新README.md..."
mkdir -p docs
cat > docs/DIRECTORY_STRUCTURE.md << EOH
# RAG服务目录结构

本文档描述了RAG服务的标准目录结构。

## 目录结构

\`\`\`
services/rag-service/
├── cmd/                    # 命令行入口
│   ├── main.go            # 主程序入口
│   └── execute.go         # 执行函数
├── internal/               # 内部包（不对外暴露）
│   ├── api/               # API定义
│   ├── config/            # 配置管理
│   ├── handlers/          # 请求处理器
│   ├── middleware/        # 中间件
│   ├── models/            # 数据模型
│   ├── rag/               # RAG核心功能
│   ├── storage/           # 存储相关
│   │   └── vector_store/  # 向量存储
│   ├── embeddings/        # 嵌入模型
│   └── utils/             # 工具函数
├── pkg/                    # 可对外暴露的包
├── tests/                  # 测试文件
├── scripts/                # 辅助脚本
├── docs/                   # 文档
└── deployment/             # 部署配置
\`\`\`

## 模块说明

- **cmd**: 包含应用程序的入口点
- **internal**: 内部实现，不对外部包可见
  - **api**: 定义API接口和路由
  - **config**: 配置加载和管理
  - **handlers**: HTTP请求处理
  - **middleware**: HTTP中间件
  - **models**: 数据模型定义
  - **rag**: RAG核心逻辑
  - **storage**: 存储相关功能
  - **embeddings**: 嵌入模型实现
  - **utils**: 工具函数
- **pkg**: 可对外暴露的包，供其他服务使用
- **tests**: 单元测试和集成测试
- **scripts**: 辅助脚本
- **docs**: 文档
- **deployment**: 部署配置
EOH

echo "=== 重构完成 ==="
echo "请运行以下命令验证重构结果:"
echo "go mod tidy"
echo "cd cmd && go run main.go" 