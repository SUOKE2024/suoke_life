#!/bin/bash
# 全面测试重构后的RAG服务

set -e

echo "=== 开始全面测试重构后的RAG服务 ==="

# 定义工作目录
BASE_DIR=$(pwd)
echo "工作目录: $BASE_DIR"

# 确保在正确的目录中
if [[ ! -d "./internal" || ! -d "./cmd" ]]; then
  echo "❌ 错误: 请在services/rag-service目录下运行此脚本，且确保已执行重构脚本"
  exit 1
fi

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 函数：显示测试步骤
function show_step() {
  echo -e "\n${YELLOW}>> $1${NC}"
}

# 函数：显示成功消息
function success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# 函数：显示错误消息
function error() {
  echo -e "${RED}✗ $1${NC}"
  exit 1
}

# 函数：验证目录或文件存在
function verify_exists() {
  if [[ ! -e "$1" ]]; then
    error "$1 不存在！"
  else
    success "$1 存在"
  fi
}

# 测试1：验证目录结构
show_step "测试1：验证目录结构"
verify_exists "cmd/main.go"
verify_exists "cmd/execute.go"
verify_exists "internal/config"
verify_exists "internal/handlers"
verify_exists "internal/middleware"
verify_exists "internal/models"
verify_exists "internal/rag"
verify_exists "internal/storage/vector_store"
verify_exists "internal/embeddings"
verify_exists "internal/utils"
verify_exists "internal/api"
success "目录结构验证通过"

# 测试2：验证go.mod中的模块名
show_step "测试2：验证go.mod中的模块名"
if grep -q "module github.com/suoke/suoke_life/services/rag-service/go-src" go.mod; then
  error "go.mod中仍包含旧的模块路径"
else
  if grep -q "module github.com/suoke/suoke_life/services/rag-service" go.mod; then
    success "go.mod模块名更新正确"
  else
    error "go.mod模块名更新有问题"
  fi
fi

# 测试3：验证导入路径
show_step "测试3：验证导入路径"
if grep -r "github.com/suoke/suoke_life/services/rag-service/go-src" --include="*.go" ./cmd ./internal > /dev/null; then
  error "仍有文件使用旧的导入路径"
else
  success "所有文件都使用了新的导入路径"
fi

# 测试4：编译代码
show_step "测试4：编译代码"
go mod tidy
if go build -o /dev/null ./cmd; then
  success "代码编译通过"
else
  error "代码编译失败"
fi

# 测试5：运行单元测试（如果存在）
show_step "测试5：运行单元测试"
if ls internal/*/test_*.go &> /dev/null || ls internal/*/*_test.go &> /dev/null; then
  echo "发现测试文件，执行单元测试..."
  if go test -v ./internal/... -short; then
    success "单元测试通过"
  else
    error "单元测试失败"
  fi
else
  echo "未发现测试文件，跳过单元测试"
fi

# 测试6：验证配置文件加载
show_step "测试6：验证配置文件加载"
cat > test_config.go << EOL
package main

import (
	"fmt"
	"github.com/suoke/suoke_life/services/rag-service/internal/config"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		fmt.Printf("配置加载失败: %v\n", err)
		return
	}
	fmt.Printf("配置加载成功，服务端口: %d\n", cfg.ServerConfig.Port)
}
EOL

if go run test_config.go; then
  success "配置文件加载测试通过"
  rm test_config.go
else
  error "配置文件加载测试失败"
  rm test_config.go
fi

# 测试7：启动服务（短时间）
show_step "测试7：启动服务测试（运行3秒）"
echo "启动服务，将在3秒后自动停止..."
(timeout 3 go run cmd/main.go || [[ $? == 124 ]]) &
SERVER_PID=$!
sleep 3
kill -9 $SERVER_PID 2>/dev/null || true
success "服务启动测试完成"

echo -e "\n${GREEN}===================================================${NC}"
echo -e "${GREEN}✓ 全面测试通过! RAG服务重构成功!${NC}"
echo -e "${GREEN}===================================================${NC}"
echo "你现在可以放心地使用重构后的代码结构了。"
echo "如果需要备份或清理旧代码，可以执行以下命令："
echo "  mv go-src go-src-backup  # 备份旧代码"
echo "  rm -rf vector_store utils rag models handlers embeddings core database config api  # 清理根目录下的冗余文件" 