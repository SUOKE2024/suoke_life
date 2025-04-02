#!/bin/bash
# 索克生活Docker镜像安全扫描脚本

set -e

# 确保提供了服务名称
if [ -z "$1" ]; then
  echo "错误: 请提供服务名称"
  echo "用法: $0 <服务名称> [严重程度级别]"
  echo "示例: $0 xiaoai-service CRITICAL,HIGH"
  exit 1
fi

SERVICE_NAME=$1
SEVERITY=${2:-"CRITICAL,HIGH,MEDIUM"}
OUTPUT_FORMAT=${3:-"table"}
OUTPUT_DIR="./services/${SERVICE_NAME}/security-reports"

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 生成时间戳用于报告文件名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${OUTPUT_DIR}/trivy_image_${TIMESTAMP}.${OUTPUT_FORMAT}"

echo "🔍 开始扫描 ${SERVICE_NAME} 镜像..."

# 检查本地是否有镜像
IMAGE_ID=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "suokelife/${SERVICE_NAME}" | head -1)

if [ -z "$IMAGE_ID" ]; then
  echo "⚠️ 未找到本地镜像，尝试构建..."
  docker build -t "suokelife/${SERVICE_NAME}:latest" "./services/${SERVICE_NAME}"
  IMAGE_ID="suokelife/${SERVICE_NAME}:latest"
fi

echo "🔎 使用Trivy扫描镜像: ${IMAGE_ID}"

if [ "$OUTPUT_FORMAT" == "json" ] || [ "$OUTPUT_FORMAT" == "sarif" ]; then
  # JSON或SARIF格式输出到文件
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PWD:/workspace" aquasec/trivy:latest image \
    --severity "$SEVERITY" \
    --format "$OUTPUT_FORMAT" \
    --output "/workspace/$OUTPUT_FILE" \
    "$IMAGE_ID"
else
  # 表格格式直接显示在终端并保存到文件
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy:latest image \
    --severity "$SEVERITY" \
    --format "$OUTPUT_FORMAT" \
    "$IMAGE_ID" | tee "$OUTPUT_FILE"
fi

echo "✅ 扫描完成！结果已保存至: $OUTPUT_FILE"

# 检查是否有严重漏洞
if [ "$OUTPUT_FORMAT" == "json" ]; then
  VULN_COUNT=$(cat "$OUTPUT_FILE" | grep -c "\"Severity\":\"CRITICAL\"" || true)
  if [ "$VULN_COUNT" -gt 0 ]; then
    echo "⚠️ 发现 ${VULN_COUNT} 个严重漏洞，请尽快修复！"
    exit 1
  fi
fi

exit 0