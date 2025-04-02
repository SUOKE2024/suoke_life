#!/bin/bash
set -e

# 配置变量
SERVICE_NAME="corn-maze-service"
IMAGE_NAME="suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${SERVICE_NAME}"
TAG=${1:-"latest"}

# 打印信息
echo "===== 玉米迷宫服务部署脚本 ====="
echo "服务名称: ${SERVICE_NAME}"
echo "镜像名称: ${IMAGE_NAME}"
echo "镜像标签: ${TAG}"

# 构建Docker镜像
echo "正在构建Docker镜像..."
docker build -t ${IMAGE_NAME}:${TAG} .

# 推送到镜像仓库
echo "正在推送镜像到阿里云容器仓库..."
docker push ${IMAGE_NAME}:${TAG}

# 应用Kubernetes配置
echo "正在应用Kubernetes配置..."
kubectl apply -k k8s/

# 等待部署完成
echo "等待部署完成..."
kubectl rollout status deployment/${SERVICE_NAME} -n suoke

echo "===== 部署完成 ====="
echo "可通过以下命令查看服务状态:"
echo "kubectl get pods -n suoke -l app=${SERVICE_NAME}"
echo "kubectl logs -n suoke -l app=${SERVICE_NAME} -f" 