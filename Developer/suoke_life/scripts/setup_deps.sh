#!/bin/bash
set -e

# 移动到服务目录
cd "$(dirname "$0")/../services"
ROOT_DIR=$(pwd)

echo "===== 为所有微服务执行依赖管理 ====="

# 先处理shared目录
echo "处理shared共享库..."
cd "$ROOT_DIR/shared"
go mod tidy
echo "共享库依赖管理完成"

# 处理其他所有微服务
for service in $(ls -d */ | grep -v "shared\|config"); do
  service_name="${service%/}"
  echo "处理服务: $service_name"
  
  # 检查是否存在go.mod文件
  if [ -f "$service_name/go.mod" ]; then
    cd "$ROOT_DIR/$service_name"
    
    # 如果go.mod中没有replace指令，添加它
    if ! grep -q "replace github.com/suoke-life/shared" go.mod; then
      echo "添加shared库的引用..."
      echo -e "\n// 使用本地共享库\nreplace github.com/suoke-life/shared => ../shared" >> go.mod
    fi
    
    # 获取依赖
    go mod tidy
    echo "$service_name 依赖管理完成"
  else
    echo "$service_name 不是Go服务，跳过"
  fi
  
  # 返回根目录
  cd "$ROOT_DIR"
done

echo "===== 所有微服务依赖管理完成 =====" 