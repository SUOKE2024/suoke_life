#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务K8s部署更新脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 参数检查
if [ $# -lt 1 ]; then
    echo -e "${RED}使用方法: $0 <namespace> [version]${NC}"
    echo -e "${YELLOW}示例: $0 suoke-prod 1.0.0${NC}"
    exit 1
fi

NAMESPACE=$1
VERSION=${2:-"1.0.0"}
PUBLIC_REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke/suoke-knowledge-graph-service"
IMAGE="${PUBLIC_REGISTRY}/${REPOSITORY}:${VERSION}"
DEPLOYMENT_NAME="knowledge-graph-service"

echo -e "${BLUE}更新信息:${NC}"
echo -e "${YELLOW}命名空间: ${NAMESPACE}${NC}"
echo -e "${YELLOW}部署名称: ${DEPLOYMENT_NAME}${NC}"
echo -e "${YELLOW}镜像: ${IMAGE}${NC}"

# 更新镜像
echo -e "\n${BLUE}正在更新部署使用新镜像...${NC}"
kubectl set image deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} ${DEPLOYMENT_NAME}=${IMAGE}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 更新失败!${NC}"
    exit 1
fi

# 检查部署状态
echo -e "\n${BLUE}正在检查部署状态...${NC}"
kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} --timeout=60s

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 部署未在60秒内完成!${NC}"
    echo -e "${YELLOW}请手动检查部署状态:${NC}"
    echo -e "kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=${DEPLOYMENT_NAME}"
    exit 1
fi

echo -e "\n${GREEN}✅ 部署已成功更新!${NC}"
echo -e "${BLUE}=========================================${NC}"

# 显示Pod状态
echo -e "\n${BLUE}当前Pod状态:${NC}"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=${DEPLOYMENT_NAME} 