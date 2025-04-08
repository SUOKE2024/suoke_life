#!/bin/bash
# 索克生活 - 阿里云容器镜像仓库设置脚本

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    索克生活 - 阿里云容器镜像仓库设置    ${NC}"
echo -e "${BLUE}============================================${NC}"

# 加载环境变量
echo -e "${YELLOW}[步骤 1/4] 加载环境变量${NC}"

# 直接设置变量，绕过环境变量文件加载问题
REGISTRY_USERNAME="netsong@sina.com"
REGISTRY_PASSWORD="Netsong2025"
REGISTRY_URL="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REGISTRY_NAMESPACE="suoke"
IMAGE_NAME="user-service"

echo -e "用户名: $REGISTRY_USERNAME"
echo -e "仓库地址: $REGISTRY_URL"
echo -e "命名空间: $REGISTRY_NAMESPACE"
echo -e "镜像名称: $IMAGE_NAME"

# 检查 Docker 是否已安装
echo -e "${YELLOW}[步骤 2/4] 检查 Docker${NC}"
if ! command -v docker &> /dev/null; then
  echo -e "${RED}错误: Docker 未安装${NC}"
  echo -e "请按照以下指南安装 Docker: https://docs.docker.com/get-docker/"
  exit 1
fi
echo -e "${GREEN}✓ Docker 已安装${NC}"

# 设置 Docker 镜像加速
echo -e "${YELLOW}[步骤 3/4] 配置 Docker 镜像加速${NC}"
DOCKER_CONFIG_DIR="$HOME/.docker"
DOCKER_CONFIG_FILE="$DOCKER_CONFIG_DIR/config.json"

mkdir -p "$DOCKER_CONFIG_DIR"

if [ ! -f "$DOCKER_CONFIG_FILE" ]; then
  echo "{}" > "$DOCKER_CONFIG_FILE"
fi

# 检查是否已配置镜像加速
if ! grep -q "registry-mirrors" "$DOCKER_CONFIG_FILE"; then
  # 添加镜像加速配置
  echo -e "添加阿里云镜像加速器..."
  cat <<EOF > "$DOCKER_CONFIG_FILE"
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.m.daocloud.io",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
  echo -e "${GREEN}✓ Docker 镜像加速已配置${NC}"
else
  echo -e "${GREEN}✓ Docker 镜像加速已存在${NC}"
fi

# 登录到阿里云容器镜像仓库
echo -e "${YELLOW}[步骤 4/4] 登录阿里云容器镜像仓库${NC}"
echo -e "正在登录到 $REGISTRY_URL..."

# 选择交互模式或自动模式
if [ "$1" = "--interactive" ] || [ "$1" = "-i" ]; then
  # 交互模式
  echo "请输入阿里云容器镜像仓库用户名:"
  read -r username
  echo "请输入阿里云容器镜像仓库密码:"
  read -rs password
  
  docker login --username "$username" --password "$password" "$REGISTRY_URL"
else
  # 自动模式，使用环境变量中的凭据
  echo "$REGISTRY_PASSWORD" | docker login --username "$REGISTRY_USERNAME" --password-stdin "$REGISTRY_URL"
fi

LOGIN_RESULT=$?
if [ $LOGIN_RESULT -ne 0 ]; then
  echo -e "${RED}✗ 登录失败${NC}"
  exit 1
fi

echo -e "${GREEN}✓ 登录成功${NC}"

# 验证镜像仓库访问
echo -e "\n正在验证镜像仓库访问..."
docker search "$REGISTRY_URL/$REGISTRY_NAMESPACE/$IMAGE_NAME" > /dev/null 2>&1

SEARCH_RESULT=$?
if [ $SEARCH_RESULT -ne 0 ]; then
  echo -e "${YELLOW}⚠ 无法验证镜像仓库访问，这可能是正常的，特别是对于私有仓库${NC}"
else
  echo -e "${GREEN}✓ 成功验证镜像仓库访问${NC}"
fi

# 显示可用操作
echo -e "\n${BLUE}可用镜像操作:${NC}"
echo -e "1. 构建并推送镜像:"
echo -e "   docker build -t $REGISTRY_URL/$REGISTRY_NAMESPACE/$IMAGE_NAME:latest ."
echo -e "   docker push $REGISTRY_URL/$REGISTRY_NAMESPACE/$IMAGE_NAME:latest"
echo -e ""
echo -e "2. 拉取镜像:"
echo -e "   docker pull $REGISTRY_URL/$REGISTRY_NAMESPACE/$IMAGE_NAME:latest"
echo -e ""
echo -e "3. 查看可用标签:"
echo -e "   通过阿里云控制台查看: https://cr.console.aliyun.com/"

# 完成
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}    阿里云容器镜像仓库设置完成    ${NC}"
echo -e "${GREEN}============================================${NC}" 