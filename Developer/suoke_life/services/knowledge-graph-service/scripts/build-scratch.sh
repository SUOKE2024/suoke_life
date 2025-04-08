#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${BLUE}=============================================="
echo "  索克生活知识图谱服务Scratch构建脚本  "
echo -e "===============================================${NC}"

# 设置镜像标签
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke"
IMAGE_NAME="knowledge-graph-service"
TAG="scratch"
FULL_IMAGE_NAME="${REGISTRY}/${REPOSITORY}/${IMAGE_NAME}:${TAG}"

echo "构建信息:"
echo "镜像名称: ${FULL_IMAGE_NAME}"
echo "Dockerfile: Dockerfile.scratch"

# 确保entrypoint脚本存在
if [ ! -f "entrypoint.sh" ]; then
  echo "创建entrypoint.sh..."
  ./scripts/create-entrypoint.sh
fi

# 检查Docker是否运行
echo -e "\n检查Docker状态..."
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}❌ Docker未运行，请先启动Docker${NC}"
  exit 1
fi

# 登录到阿里云容器镜像服务
echo -e "\n登录到阿里云容器镜像服务..."
docker login --username=netsong@sina.com ${REGISTRY}

# 构建scratch镜像
echo -e "\n构建scratch镜像..."
if docker build -t ${FULL_IMAGE_NAME} -f Dockerfile.scratch .; then
  echo -e "${GREEN}✅ 构建成功!${NC}"
else
  echo -e "${RED}❌ 构建失败!${NC}"
  exit 1
fi

# 推送镜像到远程仓库
echo -e "\n推送镜像到远程仓库..."
if docker push ${FULL_IMAGE_NAME}; then
  echo -e "${GREEN}✅ 推送成功!${NC}"
else
  echo -e "${RED}❌ 推送失败!${NC}"
  exit 1
fi

echo -e "\n${GREEN}✅ 镜像已成功构建并推送到远程仓库${NC}"
echo -e "镜像: ${FULL_IMAGE_NAME}"

# 更新部署配置文件
echo -e "\n更新部署配置文件中的镜像..."
sed -i '' "s|image:.*|image: ${FULL_IMAGE_NAME}|g" ./scripts/remote-deployment.yaml

echo -e "${GREEN}✅ 全部完成!${NC}"
echo -e "下一步请运行: ./scripts/deploy-prod.sh" 