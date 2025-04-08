#!/bin/bash

# 索克生活知识图谱服务 - Node.js清理脚本
# 该脚本用于备份旧的Node.js代码，并移除不需要的Node.js项目文件

set -e

# 定义服务根目录，使用相对路径以便在任何位置都可以运行
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVICE_ROOT="$SCRIPT_DIR/.."
NODE_BACKUP_DIR="$SERVICE_ROOT/node-backup"

echo "===== 索克生活知识图谱服务 - Node.js清理脚本 ====="
echo "服务根目录: $SERVICE_ROOT"

# 创建备份目录
mkdir -p "$NODE_BACKUP_DIR"
echo "创建备份目录: $NODE_BACKUP_DIR"

# 备份package.json和相关配置文件
echo "备份Node.js配置文件..."
cp -v "$SERVICE_ROOT/package.json" "$NODE_BACKUP_DIR/package.json" 2>/dev/null || echo "package.json不存在"
cp -v "$SERVICE_ROOT/package-lock.json" "$NODE_BACKUP_DIR/package-lock.json" 2>/dev/null || echo "package-lock.json不存在"
cp -v "$SERVICE_ROOT/tsconfig.json" "$NODE_BACKUP_DIR/tsconfig.json" 2>/dev/null || echo "tsconfig.json不存在"
cp -v "$SERVICE_ROOT/.eslintrc" "$NODE_BACKUP_DIR/.eslintrc" 2>/dev/null || echo ".eslintrc不存在"
cp -v "$SERVICE_ROOT/.eslintrc.js" "$NODE_BACKUP_DIR/.eslintrc.js" 2>/dev/null || echo ".eslintrc.js不存在"
cp -v "$SERVICE_ROOT/.prettierrc" "$NODE_BACKUP_DIR/.prettierrc" 2>/dev/null || echo ".prettierrc不存在"

# 备份src目录(如果尚未备份)
if [ -d "$SERVICE_ROOT/src" ] && [ ! -d "$NODE_BACKUP_DIR/src" ]; then
  echo "备份Node.js源码..."
  cp -rv "$SERVICE_ROOT/src" "$NODE_BACKUP_DIR/src"
fi

# 备份dist目录(如果存在)
if [ -d "$SERVICE_ROOT/dist" ] && [ ! -d "$NODE_BACKUP_DIR/dist" ]; then
  echo "备份Node.js编译文件..."
  cp -rv "$SERVICE_ROOT/dist" "$NODE_BACKUP_DIR/dist"
fi

# 备份node_modules目录的package列表(不备份整个目录)
if [ -d "$SERVICE_ROOT/node_modules" ]; then
  echo "生成Node.js依赖列表..."
  find "$SERVICE_ROOT/node_modules" -maxdepth 1 -type d | grep -v "^$SERVICE_ROOT/node_modules$" | sort > "$NODE_BACKUP_DIR/node_modules_list.txt"
fi

echo "备份完成。"

# 清理Node.js文件
read -p "是否移除旧的Node.js文件? (y/N): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
  echo "移除Node.js文件..."
  
  # 移除Node.js特定文件
  rm -fv "$SERVICE_ROOT/package.json" "$SERVICE_ROOT/package-lock.json" "$SERVICE_ROOT/tsconfig.json" 2>/dev/null
  rm -fv "$SERVICE_ROOT/.eslintrc" "$SERVICE_ROOT/.eslintrc.js" "$SERVICE_ROOT/.prettierrc" 2>/dev/null
  
  # 移除src和dist目录
  if [ -d "$SERVICE_ROOT/src" ]; then
    echo "移除src目录..."
    rm -rfv "$SERVICE_ROOT/src"
  fi
  
  if [ -d "$SERVICE_ROOT/dist" ]; then
    echo "移除dist目录..."
    rm -rfv "$SERVICE_ROOT/dist"
  fi
  
  # 移除node_modules目录(可选)
  if [ -d "$SERVICE_ROOT/node_modules" ]; then
    read -p "是否移除node_modules目录? (警告: 该目录可能很大) (y/N): " remove_modules
    if [[ $remove_modules == [yY] || $remove_modules == [yY][eE][sS] ]]; then
      echo "移除node_modules目录..."
      rm -rfv "$SERVICE_ROOT/node_modules"
    fi
  fi
  
  echo "Node.js文件移除完成。"
else
  echo "跳过移除操作。"
fi

echo "===== 脚本执行完成 =====" 