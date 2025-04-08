#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务多架构构建脚本  ${NC}"
echo -e "${BLUE}==============================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义变量
VERSION="1.0.0"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke/suoke-knowledge-graph-service"
TAG="${REGISTRY}/${REPOSITORY}:${VERSION}"
LATEST_TAG="${REGISTRY}/${REPOSITORY}:latest"
AMD64_TAG="${REGISTRY}/${REPOSITORY}:${VERSION}-amd64"
ARM64_TAG="${REGISTRY}/${REPOSITORY}:${VERSION}-arm64"
DOCKERFILE="Dockerfile.new"

# 显示构建信息
echo -e "${BLUE}构建信息:${NC}"
echo -e "${YELLOW}镜像名称: ${TAG}${NC}"
echo -e "${YELLOW}最新标签: ${LATEST_TAG}${NC}"
echo -e "${YELLOW}AMD64标签: ${AMD64_TAG}${NC}"
echo -e "${YELLOW}ARM64标签: ${ARM64_TAG}${NC}"
echo -e "${YELLOW}Dockerfile: ${DOCKERFILE}${NC}"

# 确认镜像是否已存在
echo -e "\n${BLUE}检查本地镜像...${NC}"
if docker image inspect "${TAG}" &> /dev/null; then
    echo -e "${YELLOW}镜像 ${TAG} 已存在，将被覆盖${NC}"
fi

# 检查Docker Buildx是否已安装
echo -e "\n${BLUE}检查Docker Buildx...${NC}"
if ! docker buildx version &> /dev/null; then
    echo -e "${RED}❌ Docker Buildx 未安装!${NC}"
    echo -e "${YELLOW}请尝试: docker buildx create --name multiarch-builder --use${NC}"
    exit 1
fi

# 创建并切换到buildx builder
echo -e "\n${BLUE}创建并配置buildx构建器...${NC}"
if ! docker buildx ls | grep -q multiarch-builder; then
    echo -e "${YELLOW}创建新的构建器: multiarch-builder${NC}"
    docker buildx create --name multiarch-builder --use
else
    echo -e "${YELLOW}使用现有构建器: multiarch-builder${NC}"
    docker buildx use multiarch-builder
fi

# 引导构建器
echo -e "\n${BLUE}引导构建器...${NC}"
docker buildx inspect --bootstrap

# 登录到阿里云容器镜像服务
echo -e "\n${BLUE}登录到阿里云容器镜像服务...${NC}"
docker login --username=netsong@sina.com ${REGISTRY}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 登录失败!${NC}"
    exit 1
fi

# 使用Buildx构建并推送多架构镜像
echo -e "\n${BLUE}构建并推送多架构镜像...${NC}"
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag ${TAG} \
    --tag ${LATEST_TAG} \
    --file ${DOCKERFILE} \
    --push \
    .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 多架构构建失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ 多架构镜像已成功构建并推送!${NC}"

# 构建和推送单架构镜像
echo -e "\n${BLUE}构建并推送AMD64架构镜像...${NC}"
docker buildx build \
    --platform linux/amd64 \
    --tag ${AMD64_TAG} \
    --file ${DOCKERFILE} \
    --push \
    .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ AMD64构建失败!${NC}"
else
    echo -e "${GREEN}✅ AMD64镜像已成功推送!${NC}"
fi

echo -e "\n${BLUE}构建并推送ARM64架构镜像...${NC}"
docker buildx build \
    --platform linux/arm64 \
    --tag ${ARM64_TAG} \
    --file ${DOCKERFILE} \
    --push \
    .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ARM64构建失败!${NC}"
else
    echo -e "${GREEN}✅ ARM64镜像已成功推送!${NC}"
fi

echo -e "\n${BLUE}==============================================${NC}"
echo -e "${GREEN}所有镜像已成功构建并推送到仓库:${NC}"
echo -e "${YELLOW}多架构镜像: ${TAG}${NC}"
echo -e "${YELLOW}多架构最新镜像: ${LATEST_TAG}${NC}"
echo -e "${YELLOW}AMD64镜像: ${AMD64_TAG}${NC}"
echo -e "${YELLOW}ARM64镜像: ${ARM64_TAG}${NC}"
echo -e "${BLUE}==============================================${NC}"

echo -e "\n${YELLOW}要更新Kubernetes部署，请运行:${NC}"
echo -e "./scripts/update-k8s-deployment.sh suoke-prod" 