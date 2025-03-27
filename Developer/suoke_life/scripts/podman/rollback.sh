#!/bin/bash
set -e

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_DIR}/../.."

SERVICE_NAME="rag-service"
SERVICE_DIR="services/${SERVICE_NAME}"

echo "正在执行${SERVICE_NAME}的Podman迁移回滚..."

# 停止并移除所有Podman容器
echo "停止Podman容器..."
cd "${SERVICE_DIR}"
podman-compose down || true
podman ps -a --format "{{.ID}}" | xargs -r podman rm -f || true

# 切换回Docker
echo "切换回Docker Compose..."
cd "${SERVICE_DIR}"
docker-compose up -d

echo "等待服务启动..."
sleep 10

# 检查Docker容器状态
echo "Docker容器状态:"
docker ps

echo "${SERVICE_NAME}迁移已回滚到Docker。"
echo "现在可以访问http://localhost:8000/health检查服务状态。" 