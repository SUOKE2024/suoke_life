#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务镜像加速构建脚本  ${NC}"
echo -e "${BLUE}==============================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义变量
VERSION="1.0.0"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke/suoke-knowledge-graph-service"
TAG="${REGISTRY}/${REPOSITORY}:${VERSION}"
LATEST_TAG="${REGISTRY}/${REPOSITORY}:latest"
MIRROR="registry.cn-hangzhou.aliyuncs.com/library"

# 显示构建信息
echo -e "${BLUE}构建信息:${NC}"
echo -e "${YELLOW}镜像名称: ${TAG}${NC}"
echo -e "${YELLOW}最新标签: ${LATEST_TAG}${NC}"
echo -e "${YELLOW}使用镜像加速: ${MIRROR}${NC}"

# 登录到阿里云容器镜像服务
echo -e "\n${BLUE}登录到阿里云容器镜像服务...${NC}"
docker login --username=netsong@sina.com ${REGISTRY}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 登录失败!${NC}"
    exit 1
fi

# 直接使用docker build命令构建镜像，明确指定构建参数
echo -e "\n${BLUE}开始构建镜像...${NC}"
docker build \
  --build-arg DOCKER_REGISTRY_MIRROR=${MIRROR} \
  --build-arg GOPROXY=https://goproxy.cn,direct \
  -t ${TAG} \
  -f Dockerfile.amd64 .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败!${NC}"
    exit 1
fi

# 标记最新版本
echo -e "\n${BLUE}标记最新版本...${NC}"
docker tag ${TAG} ${LATEST_TAG}

# 推送镜像
echo -e "\n${BLUE}推送镜像...${NC}"
docker push ${TAG}
docker push ${LATEST_TAG}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 推送失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ 镜像已成功构建并推送!${NC}"
echo -e "${BLUE}==============================================${NC}"
echo -e "${YELLOW}镜像: ${TAG}${NC}"
echo -e "${YELLOW}最新镜像: ${LATEST_TAG}${NC}"
echo -e "${BLUE}==============================================${NC}"

echo -e "\n${YELLOW}要更新Kubernetes部署，请运行:${NC}"
echo -e "./scripts/deploy-helm-fix.sh"