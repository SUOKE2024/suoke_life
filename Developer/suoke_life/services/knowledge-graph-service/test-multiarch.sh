#!/bin/bash
set -e

echo "===== 多架构镜像测试工具 ====="

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd $SCRIPT_DIR

# 从.env文件获取镜像信息
if [ -f ".env" ]; then
  REGISTRY_URL=$(grep "REGISTRY_URL" .env | cut -d '=' -f2)
else
  REGISTRY_URL="suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/"
fi

IMAGE_NAME="knowledge-graph-service"
LATEST_IMAGE_NAME="${REGISTRY_URL}${IMAGE_NAME}:latest"

echo "正在测试镜像: $LATEST_IMAGE_NAME"

# 检查镜像是否存在
echo "检查镜像是否存在..."
if ! docker buildx imagetools inspect $LATEST_IMAGE_NAME &>/dev/null; then
  echo "错误: 镜像 $LATEST_IMAGE_NAME 不存在"
  exit 1
fi

# 获取并显示镜像支持的架构
echo "检查镜像支持的架构..."
docker buildx imagetools inspect $LATEST_IMAGE_NAME

# 针对不同架构验证镜像
echo "测试在x86_64平台上运行..."
docker run --rm --platform=linux/amd64 $LATEST_IMAGE_NAME uname -a || echo "x86_64测试失败"

echo "测试在arm64平台上运行..."
docker run --rm --platform=linux/arm64 $LATEST_IMAGE_NAME uname -a || echo "arm64测试失败"

echo "测试镜像中的服务健康检查..."
echo "注意: 服务需要一段时间启动，将在30秒后超时"
docker run --rm -d --name kg-test-service $LATEST_IMAGE_NAME
sleep 5
docker exec kg-test-service wget -q -O- http://localhost:3000/health || echo "健康检查失败"
docker stop kg-test-service

# 输出测试结果摘要
echo "===== 测试完成 ====="
echo "镜像支持以下架构:"
docker buildx imagetools inspect $LATEST_IMAGE_NAME | grep -A 5 "Platform" 