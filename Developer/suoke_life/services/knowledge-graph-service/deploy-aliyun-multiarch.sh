#!/bin/bash
#
# 知识图谱服务阿里云多架构部署脚本
#

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 加载环境变量
if [ -f .env ]; then
  echo "从.env文件加载环境变量"
  export $(grep -v '^#' .env | xargs)
else
  echo "警告：.env文件不存在，使用默认值"
fi

# 镜像配置
IMAGE_NAME="${REGISTRY_URL:-suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/}knowledge-graph-service"
VERSION=$(cat VERSION || echo "0.1.0")
REGISTRY_USERNAME="${REGISTRY_USERNAME:-netsong@sina.com}"
REGISTRY_PASSWORD="${REGISTRY_PASSWORD:-Netsong2025}"
DEPLOYMENT_FILE="aliyun-multiarch-deployment.yaml"

echo "开始部署知识图谱服务(多架构版本)到阿里云Kubernetes..."

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
  echo "错误: kubectl命令不可用，请安装kubectl并配置好集群访问"
  exit 1
fi

# 检查部署文件是否存在
if [ ! -f "$DEPLOYMENT_FILE" ]; then
  echo "错误: 部署文件 $DEPLOYMENT_FILE 不存在"
  exit 1
fi

# 创建或更新镜像仓库密钥(如果需要)
echo "创建或更新镜像仓库密钥..."
kubectl create secret docker-registry suoke-registry-secret \
  --docker-server=${IMAGE_NAME%/*} \
  --docker-username="$REGISTRY_USERNAME" \
  --docker-password="$REGISTRY_PASSWORD" \
  --docker-email="dev@suoke.life" \
  -o yaml --dry-run=client | kubectl apply -f -

# 替换部署文件中的占位符变量
echo "更新部署配置..."
TEMP_DEPLOYMENT_FILE=$(mktemp)
cat "$DEPLOYMENT_FILE" | \
  sed "s|{{IMAGE_URL}}|$IMAGE_NAME:$VERSION|g" | \
  sed "s|{{APP_ENV}}|production|g" | \
  sed "s|{{LOG_LEVEL}}|info|g" > "$TEMP_DEPLOYMENT_FILE"

# 应用部署
echo "应用Kubernetes部署..."
kubectl apply -f "$TEMP_DEPLOYMENT_FILE"

# 删除临时文件
rm "$TEMP_DEPLOYMENT_FILE"

# 等待部署完成
echo "等待部署完成..."
kubectl rollout status deployment/knowledge-graph-service

echo "部署完成！知识图谱服务(多架构版本)已成功部署"
echo "访问服务: http://<cluster-ip>:3000"