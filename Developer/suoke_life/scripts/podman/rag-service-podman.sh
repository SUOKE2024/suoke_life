#!/bin/bash
set -e

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_DIR}/../.."

# 加载环境变量
if [ -f .env ]; then
  source .env
fi

SERVICE_NAME="rag-service"
SERVICE_DIR="services/${SERVICE_NAME}"

# 检查服务目录是否存在
if [ ! -d "${SERVICE_DIR}" ]; then
  echo "错误: 服务目录 ${SERVICE_DIR} 不存在"
  exit 1
fi

# 创建数据和日志目录
mkdir -p "${SERVICE_DIR}/data" "${SERVICE_DIR}/logs"

# 确保构建了简化版镜像
echo "确保已构建rag-service镜像..."
${SCRIPT_DIR}/build_podman_rag_service.sh

# 准备使用podman-compose启动服务
echo "准备使用podman-compose启动${SERVICE_NAME}服务..."
cd "${SERVICE_DIR}"

# 显示将要运行的配置
echo "配置文件内容:"
cat docker-compose.podman.yml

# 启动服务
echo "尝试使用podman-compose启动服务..."
podman-compose -f docker-compose.podman.yml up -d

echo "服务启动中，等待健康检查..."
sleep 10

# 检查容器状态
echo "容器状态:"
podman ps

# 尝试访问健康检查
echo "测试健康检查..."
curl http://localhost:8000/ || echo "无法连接到服务，可能需要更多时间启动"

echo "${SERVICE_NAME}迁移测试完成。"
echo "现在可以访问http://localhost:8000检查服务状态。"
echo ""
echo "要停止服务，请运行: cd ${SERVICE_DIR} && podman-compose -f docker-compose.podman.yml down" 