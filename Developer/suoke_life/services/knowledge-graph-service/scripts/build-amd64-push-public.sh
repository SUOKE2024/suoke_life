#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务AMD64构建脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义变量
VERSION="1.0.0"
PUBLIC_REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke/suoke-knowledge-graph-service"
TAG="${PUBLIC_REGISTRY}/${REPOSITORY}:${VERSION}"
AMD64_TAG="${PUBLIC_REGISTRY}/${REPOSITORY}:${VERSION}-amd64"
LATEST_TAG="${PUBLIC_REGISTRY}/${REPOSITORY}:latest"
DOCKERFILE="Dockerfile.amd64"

# 显示构建信息
echo -e "${BLUE}构建信息:${NC}"
echo -e "${YELLOW}镜像名称: ${TAG}${NC}"
echo -e "${YELLOW}AMD64标签: ${AMD64_TAG}${NC}"
echo -e "${YELLOW}最新标签: ${LATEST_TAG}${NC}"
echo -e "${YELLOW}Dockerfile: ${DOCKERFILE}${NC}"

# 登录到阿里云容器镜像服务
echo -e "\n${BLUE}登录到阿里云容器镜像服务...${NC}"
docker login --username=netsong@sina.com ${PUBLIC_REGISTRY}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 登录失败!${NC}"
    exit 1
fi

# 确保AMD64专用Dockerfile存在
if [ ! -f "${DOCKERFILE}" ]; then
    echo -e "${RED}❌ ${DOCKERFILE}不存在!${NC}"
    exit 1
fi

# 构建AMD64架构镜像
echo -e "\n${BLUE}正在构建AMD64镜像...${NC}"
docker build --platform=linux/amd64 \
    -t ${AMD64_TAG} \
    -f ${DOCKERFILE} .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败!${NC}"
    exit 1
fi

# 标记镜像
echo -e "\n${BLUE}标记镜像...${NC}"
docker tag ${AMD64_TAG} ${TAG}
docker tag ${AMD64_TAG} ${LATEST_TAG}

# 推送镜像
echo -e "\n${BLUE}推送镜像到阿里云...${NC}"
docker push ${AMD64_TAG}
docker push ${TAG}
docker push ${LATEST_TAG}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 推送失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ AMD64镜像已成功构建并推送到公共仓库!${NC}"
echo -e "${BLUE}=========================================${NC}"

echo -e "\n${YELLOW}要更新Kubernetes部署，请运行:${NC}"
echo -e "kubectl set image deployment/knowledge-graph-service -n suoke-prod knowledge-graph-service=${TAG}" 