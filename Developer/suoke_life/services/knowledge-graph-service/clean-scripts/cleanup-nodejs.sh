#!/bin/bash

# 知识图谱服务 Node.js 代码清理脚本
# 该脚本用于在完成 Go 重构后，清理不再需要的 Node.js 代码

echo "开始清理知识图谱服务的 Node.js 代码..."

# 项目根目录
PROJECT_ROOT="$(pwd)"
SERVICE_DIR="${PROJECT_ROOT}/services/knowledge-graph-service"

# 确保在正确的目录中执行
if [[ ! -d "${SERVICE_DIR}" ]]; then
  echo "错误: 找不到服务目录 ${SERVICE_DIR}"
  echo "请在项目根目录下运行此脚本"
  exit 1
fi

# 创建备份目录
BACKUP_DIR="${SERVICE_DIR}/node-backup-$(date +%Y%m%d%H%M%S)"
mkdir -p "${BACKUP_DIR}"
echo "创建备份目录: ${BACKUP_DIR}"

# 备份 Node.js 文件
echo "备份 Node.js 相关文件..."
cp "${SERVICE_DIR}/package.json" "${BACKUP_DIR}/"
cp "${SERVICE_DIR}/package-lock.json" "${BACKUP_DIR}/" 2>/dev/null || echo "package-lock.json 不存在，跳过"
cp "${SERVICE_DIR}/tsconfig.json" "${BACKUP_DIR}/" 2>/dev/null || echo "tsconfig.json 不存在，跳过"
cp "${SERVICE_DIR}/nodemon.json" "${BACKUP_DIR}/" 2>/dev/null || echo "nodemon.json 不存在，跳过"
cp "${SERVICE_DIR}/jest.config.js" "${BACKUP_DIR}/" 2>/dev/null || echo "jest.config.js 不存在，跳过"
cp "${SERVICE_DIR}/.eslintrc.js" "${BACKUP_DIR}/" 2>/dev/null || echo ".eslintrc.js 不存在，跳过"

# 备份 Node.js 源代码目录
if [[ -d "${SERVICE_DIR}/src" ]]; then
  echo "备份 src 目录..."
  cp -r "${SERVICE_DIR}/src" "${BACKUP_DIR}/"
fi

if [[ -d "${SERVICE_DIR}/node_modules" ]]; then
  echo "备份 node_modules 目录信息..."
  ls -la "${SERVICE_DIR}/node_modules" > "${BACKUP_DIR}/node_modules-list.txt"
fi

# 替换 Dockerfile
if [[ -f "${SERVICE_DIR}/Dockerfile" ]]; then
  echo "备份并替换 Dockerfile..."
  cp "${SERVICE_DIR}/Dockerfile" "${BACKUP_DIR}/Dockerfile.node"
  
  if [[ -f "${SERVICE_DIR}/Dockerfile.go" ]]; then
    cp "${SERVICE_DIR}/Dockerfile.go" "${SERVICE_DIR}/Dockerfile"
    rm "${SERVICE_DIR}/Dockerfile.go"
    echo "已替换 Dockerfile 为 Go 版本"
  else
    echo "警告: 找不到 Dockerfile.go，Dockerfile 未替换"
  fi
fi

# 删除 Node.js 文件
echo "删除 Node.js 相关文件..."
rm -f "${SERVICE_DIR}/package.json"
rm -f "${SERVICE_DIR}/package-lock.json"
rm -f "${SERVICE_DIR}/tsconfig.json"
rm -f "${SERVICE_DIR}/nodemon.json"
rm -f "${SERVICE_DIR}/jest.config.js"
rm -f "${SERVICE_DIR}/.eslintrc.js"

# 删除 Node.js 目录
echo "删除 Node.js 相关目录..."
if [[ -d "${SERVICE_DIR}/src" ]]; then
  rm -rf "${SERVICE_DIR}/src"
  echo "已删除 src 目录"
fi

if [[ -d "${SERVICE_DIR}/node_modules" ]]; then
  rm -rf "${SERVICE_DIR}/node_modules"
  echo "已删除 node_modules 目录"
fi

if [[ -d "${SERVICE_DIR}/dist" ]]; then
  rm -rf "${SERVICE_DIR}/dist"
  echo "已删除 dist 目录"
fi

if [[ -d "${SERVICE_DIR}/coverage" ]]; then
  rm -rf "${SERVICE_DIR}/coverage"
  echo "已删除 coverage 目录"
fi

echo "清理完成！所有 Node.js 代码已备份到: ${BACKUP_DIR}"
echo ""
echo "如需恢复，请运行: cp -r ${BACKUP_DIR}/* ${SERVICE_DIR}/"
echo ""
echo "重要: 请验证 Go 服务正常运行后，再删除备份目录" 