#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${BLUE}=============================================="
echo "  索克生活知识图谱服务部署更新脚本  "
echo -e "===============================================${NC}"

# 设置镜像标签
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke"
IMAGE_NAME="knowledge-graph-service"
TAG="local"
FULL_IMAGE_NAME="${REGISTRY}/${REPOSITORY}/${IMAGE_NAME}:${TAG}"

echo "部署信息:"
echo "使用镜像: ${FULL_IMAGE_NAME}"
echo "部署文件: ./scripts/remote-deployment.yaml"

# 更新部署配置文件
echo -e "\n更新部署配置文件中的镜像..."
sed -i '' "s|image:.*|image: ${FULL_IMAGE_NAME}|g" ./scripts/remote-deployment.yaml

echo -e "${GREEN}✅ 部署文件已更新!${NC}"

# 应用部署
echo -e "\n应用部署到Kubernetes集群..."
kubectl apply -f ./scripts/remote-deployment.yaml

echo -e "\n等待Pod就绪..."
kubectl -n suoke-prod rollout status deployment/knowledge-graph-service --timeout=120s

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ 部署成功!${NC}"
  
  # 显示服务信息
  echo -e "\n服务状态:"
  kubectl get svc,pod -n suoke-prod -l app=knowledge-graph-service
else
  echo -e "${RED}❌ 部署未能在指定时间内完成!${NC}"
  
  # 显示Pod状态
  echo -e "\n查看Pod状态:"
  kubectl get pods -n suoke-prod -l app=knowledge-graph-service
  
  # 显示Pod详情
  POD_NAME=$(kubectl get pods -n suoke-prod -l app=knowledge-graph-service -o jsonpath='{.items[0].metadata.name}')
  if [ ! -z "$POD_NAME" ]; then
    echo -e "\n查看Pod描述:"
    kubectl describe pod $POD_NAME -n suoke-prod
    
    echo -e "\n查看Pod日志:"
    kubectl logs $POD_NAME -n suoke-prod
  fi
fi