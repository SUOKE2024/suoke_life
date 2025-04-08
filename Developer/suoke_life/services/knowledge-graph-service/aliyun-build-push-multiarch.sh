#!/bin/bash
set -e

echo "===== 索克生活知识图谱服务多架构镜像构建工具 ====="
echo "===== 从阿里云官方基础镜像构建，支持多架构 ====="

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd $SCRIPT_DIR

# 确保脚本有执行权限
chmod +x setup-env.sh
chmod +x build-multiarch.sh

# 步骤1: 自动配置环境
echo "步骤1: 配置环境..."
./setup-env.sh

# 步骤2: 构建多架构镜像
echo "步骤2: 构建多架构镜像..."
./build-multiarch.sh

# 步骤3: 验证镜像
echo "步骤3: 验证镜像..."

# 从.env文件获取镜像名称
REGISTRY_URL=$(grep "REGISTRY_URL" .env | cut -d '=' -f2)
IMAGE_NAME="knowledge-graph-service"
LATEST_IMAGE_NAME="${REGISTRY_URL}${IMAGE_NAME}:latest"

# 验证镜像是否成功推送
echo "验证镜像: $LATEST_IMAGE_NAME"
if docker buildx imagetools inspect $LATEST_IMAGE_NAME &>/dev/null; then
  echo "镜像验证成功: $LATEST_IMAGE_NAME"
  echo "支持的架构:"
  docker buildx imagetools inspect $LATEST_IMAGE_NAME | grep -A 5 "Manifests"
else
  echo "警告: 镜像验证失败，请检查构建和推送过程"
fi

# 步骤4: 输出部署信息
cat << EOF

===== 镜像构建完成 =====

镜像信息:
- 镜像名称: ${REGISTRY_URL}${IMAGE_NAME}:latest
- 镜像仓库: ${REGISTRY_URL}
- 支持架构: linux/amd64, linux/arm64

部署示例:
  
kubectl create namespace suoke-system (如果命名空间不存在)

# 部署服务
kubectl apply -f aliyun-deployment.yaml -n suoke-system

# 检查部署状态
kubectl get deployments -n suoke-system
kubectl get pods -n suoke-system

# 查看服务日志
kubectl logs -f deployment/knowledge-graph-service -n suoke-system

感谢使用索克生活知识图谱服务部署工具!
EOF 