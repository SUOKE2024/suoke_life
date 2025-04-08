#!/bin/bash

# 索克生活知识图谱服务 - Kubernetes配置更新脚本
# 该脚本用于更新Kubernetes配置文件，适配Go实现版本

set -e

# 定义服务根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVICE_ROOT="$SCRIPT_DIR/.."
K8S_DIR="$SERVICE_ROOT/k8s"

echo "===== 索克生活知识图谱服务 - Kubernetes配置更新脚本 ====="
echo "服务根目录: $SERVICE_ROOT"
echo "K8s配置目录: $K8S_DIR"

# 检查K8s目录是否存在
if [ ! -d "$K8S_DIR" ]; then
  echo "错误: K8s配置目录不存在"
  exit 1
fi

# 备份现有配置
BACKUP_DIR="$K8S_DIR/backup-$(date +"%Y%m%d%H%M%S")"
mkdir -p "$BACKUP_DIR"
echo "备份现有配置到: $BACKUP_DIR"
cp -rv "$K8S_DIR"/*.yaml "$BACKUP_DIR/"

# 更新deployment.yaml
echo "更新deployment.yaml..."
if [ -f "$K8S_DIR/deployment.yaml" ]; then
  # 使用sed更新镜像相关配置
  sed -i.bak \
    -e 's/node:18-alpine/golang:1.21-alpine/g' \
    -e 's/npm start/\/app\/server/g' \
    -e 's/\/app\/node_modules\/.bin\/ts-node/\/app\/server/g' \
    -e 's/\/app\/src\/index.ts/\/app\/server/g' \
    -e 's/\/app\/dist\/index.js/\/app\/server/g' \
    "$K8S_DIR/deployment.yaml"
  
  # 更新资源限制
  sed -i.bak \
    -e 's/memory: "512Mi"/memory: "256Mi"/g' \
    -e 's/cpu: "500m"/cpu: "200m"/g' \
    -e 's/memory: "1Gi"/memory: "512Mi"/g' \
    -e 's/cpu: "1"/cpu: "500m"/g' \
    "$K8S_DIR/deployment.yaml"
  
  # 更新健康检查
  sed -i.bak \
    -e 's/path: \/health\/live/path: \/health/g' \
    -e 's/path: \/health\/ready/path: \/health/g' \
    "$K8S_DIR/deployment.yaml"
  
  echo "deployment.yaml更新完成"
else
  echo "警告: deployment.yaml不存在"
fi

# 更新configmap.yaml (如果存在)
echo "更新configmap.yaml..."
if [ -f "$K8S_DIR/configmap.yaml" ]; then
  # 将NODE_ENV更改为适用于Go的环境变量
  sed -i.bak \
    -e 's/NODE_ENV: "production"/GO_ENV: "production"/g' \
    -e 's/LOG_LEVEL: "info"/LOG_LEVEL: "info"/g' \
    "$K8S_DIR/configmap.yaml"
  
  echo "configmap.yaml更新完成"
else
  echo "警告: configmap.yaml不存在"
fi

# 更新service.yaml (通常不需要修改)
echo "检查service.yaml..."
if [ -f "$K8S_DIR/service.yaml" ]; then
  echo "service.yaml无需更改"
else
  echo "警告: service.yaml不存在"
fi

# 更新其他配置文件
for config_file in "$K8S_DIR"/*.yaml; do
  basename=$(basename "$config_file")
  if [[ "$basename" != "deployment.yaml" && "$basename" != "configmap.yaml" && "$basename" != "service.yaml" ]]; then
    echo "检查其他配置文件: $basename"
    if grep -q "Node.js" "$config_file"; then
      echo "- 更新$basename中的Node.js引用"
      sed -i.bak 's/Node\.js/Go/g' "$config_file"
    fi
  fi
done

# 清理备份文件
echo "清理临时备份文件..."
find "$K8S_DIR" -name "*.bak" -delete

echo "===== 配置更新完成 ====="
echo "请检查更新后的配置文件，确保所有内容正确无误。"
echo "原始配置已备份至: $BACKUP_DIR"