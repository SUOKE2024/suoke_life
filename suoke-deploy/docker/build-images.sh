#!/bin/bash
# 索克生活APP镜像构建与推送脚本
# 必须使用 sudo chmod +x build-images.sh 赋予执行权限

# 设置变量
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
NAMESPACE="suoke"
VERSION="1.0.0"
PLATFORMS="linux/amd64,linux/arm64"

# 确保已登录阿里云容器镜像服务
echo "请确保已登录阿里云容器镜像服务"
echo "如未登录，请运行: docker login --username=netsong@sina.com ${REGISTRY}"
echo

# 创建buildx构建器
if ! docker buildx inspect suoke-builder &>/dev/null; then
  echo "创建多架构构建器..."
  docker buildx create --name suoke-builder --use
fi

docker buildx inspect suoke-builder --bootstrap

# 构建并推送API网关镜像
build_and_push() {
  SERVICE=$1
  DOCKERFILE_DIR=$2
  TAG="${REGISTRY}/${NAMESPACE}/${SERVICE}:${VERSION}"
  LATEST_TAG="${REGISTRY}/${NAMESPACE}/${SERVICE}:latest"
  
  echo "构建并推送 ${SERVICE} 镜像..."
  echo "Dockerfile: ${DOCKERFILE_DIR}/Dockerfile"
  echo "目标标签: ${TAG} 和 ${LATEST_TAG}"
  
  cd ${DOCKERFILE_DIR} || { echo "目录 ${DOCKERFILE_DIR} 不存在!"; return 1; }
  
  docker buildx build --platform ${PLATFORMS} \
    -t ${TAG} \
    -t ${LATEST_TAG} \
    --push \
    .
  
  if [ $? -eq 0 ]; then
    echo "✅ ${SERVICE} 镜像构建并推送成功!"
  else
    echo "❌ ${SERVICE} 镜像构建失败!"
    return 1
  fi
  
  cd - > /dev/null
  echo
}

# 主函数
main() {
  echo "=== 开始构建索克生活APP镜像 ==="
  echo "镜像仓库: ${REGISTRY}/${NAMESPACE}"
  echo "镜像版本: ${VERSION}"
  echo "构建平台: ${PLATFORMS}"
  echo
  
  # 构建服务镜像
  build_and_push "api-gateway" "$(pwd)/api-gateway"
  build_and_push "agent-coordinator" "$(pwd)/agent-coordinator"
  build_and_push "rag-service" "$(pwd)/rag-service"
  
  echo "=== 所有镜像构建完成 ==="
}

# 执行主函数
main "$@"