#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务构建与部署脚本  ${NC}"
echo -e "${BLUE}==============================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义变量
VERSION="1.0.0"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke/suoke-knowledge-graph-service"
TAG="${REGISTRY}/${REPOSITORY}:${VERSION}"
NAMESPACE="suoke-prod"
RELEASE_NAME="knowledge-graph"

# 显示信息
echo -e "${BLUE}构建与部署信息:${NC}"
echo -e "${YELLOW}镜像: ${TAG}${NC}"
echo -e "${YELLOW}命名空间: ${NAMESPACE}${NC}"
echo -e "${YELLOW}Helm发布名称: ${RELEASE_NAME}${NC}"

# 1. 首先执行构建步骤
echo -e "\n${BLUE}开始构建镜像...${NC}"
./scripts/build-amd64.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败，终止部署!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ 构建完成，开始部署...${NC}"

# 2. 执行部署步骤
echo -e "\n${BLUE}开始部署...${NC}"
./scripts/deploy-helm-fix.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 部署失败!${NC}"
    echo -e "${YELLOW}查看Pod状态:${NC}"
    kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
    echo -e "${YELLOW}查看Pod描述:${NC}"
    kubectl describe pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
    exit 1
fi

echo -e "\n${GREEN}✅ 部署成功!${NC}"
echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}构建和部署完成!${NC}"
echo -e "${BLUE}==============================================${NC}" 