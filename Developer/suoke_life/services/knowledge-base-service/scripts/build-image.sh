#!/bin/bash
# 知识库服务镜像构建与推送脚本

# 设置变量
IMAGE_NAME="suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-base-service"
IMAGE_TAG="latest"

# 显示构建开始信息
echo "====================================="
echo "开始构建知识库服务镜像"
echo "镜像：${IMAGE_NAME}:${IMAGE_TAG}"
echo "时间：$(date)"
echo "====================================="

# 构建镜像
echo "正在构建镜像..."
docker build --network=host -t ${IMAGE_NAME}:${IMAGE_TAG} .

# 检查构建结果
if [ $? -ne 0 ]; then
  echo "错误：镜像构建失败！"
  exit 1
fi

echo "镜像构建成功！"

# 登录到镜像仓库（需要提前设置环境变量或使用参数传入）
if [ -z "$REGISTRY_USER" ] || [ -z "$REGISTRY_PASSWORD" ]; then
  echo "请提供镜像仓库凭证："
  read -p "用户名: " REGISTRY_USER
  read -s -p "密码: " REGISTRY_PASSWORD
  echo
fi

echo "正在登录镜像仓库..."
echo "$REGISTRY_PASSWORD" | docker login suoke-registry.cn-hangzhou.cr.aliyuncs.com -u "$REGISTRY_USER" --password-stdin

# 检查登录结果
if [ $? -ne 0 ]; then
  echo "错误：镜像仓库登录失败！"
  exit 1
fi

# 推送镜像
echo "正在推送镜像到仓库..."
docker push ${IMAGE_NAME}:${IMAGE_TAG}

# 检查推送结果
if [ $? -ne 0 ]; then
  echo "错误：镜像推送失败！"
  exit 1
fi

echo "====================================="
echo "镜像构建并推送完成！"
echo "${IMAGE_NAME}:${IMAGE_TAG}"
echo "====================================="