#!/bin/bash
# 知识库服务健康检查脚本

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 设置服务名称
SERVICE_NAME="knowledge-base-service"
NAMESPACE="suoke-prod"

echo "===================================="
echo "开始健康检查: ${SERVICE_NAME}"
echo "命名空间: ${NAMESPACE}"
echo "时间: $(date)"
echo "===================================="

# 检查Pod是否存在
POD_COUNT=$(kubectl get pod -l app=${SERVICE_NAME} -n ${NAMESPACE} --no-headers | wc -l)

if [ "$POD_COUNT" -eq "0" ]; then
  echo -e "${RED}错误: 找不到${SERVICE_NAME}的Pod!${NC}"
  exit 1
fi

# 检查Pod是否正在运行
POD_STATUS=$(kubectl get pod -l app=${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.items[0].status.phase}')

if [ "$POD_STATUS" != "Running" ]; then
  echo -e "${RED}错误: ${SERVICE_NAME} Pod状态为 ${POD_STATUS}${NC}"
  echo "尝试重新启动部署..."
  kubectl rollout restart deployment ${SERVICE_NAME} -n ${NAMESPACE}
  exit 1
fi

# 检查容器Ready状态
CONTAINER_READY=$(kubectl get pod -l app=${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.items[0].status.containerStatuses[0].ready}')

if [ "$CONTAINER_READY" != "true" ]; then
  echo -e "${RED}错误: ${SERVICE_NAME}容器未就绪${NC}"
  echo "查看容器日志:"
  kubectl logs -l app=${SERVICE_NAME} -n ${NAMESPACE} --tail=20
  echo "尝试重新启动部署..."
  kubectl rollout restart deployment ${SERVICE_NAME} -n ${NAMESPACE}
  exit 1
fi

# 检查服务健康端点
# 使用port-forward临时暴露服务
echo "通过port-forward检查健康端点..."
kubectl port-forward service/${SERVICE_NAME} 3002:80 -n ${NAMESPACE} &
PF_PID=$!

# 等待port-forward建立
sleep 3

# 检查健康端点
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002/api/v1/health)

# 终止port-forward
kill $PF_PID

if [ "$HEALTH_STATUS" == "200" ]; then
  echo -e "${GREEN}健康检查通过: HTTP状态码 ${HEALTH_STATUS}${NC}"
  echo "===================================="
  echo -e "${GREEN}服务 ${SERVICE_NAME} 正常运行!${NC}"
  echo "===================================="
  exit 0
else
  echo -e "${RED}健康检查失败: HTTP状态码 ${HEALTH_STATUS}${NC}"
  echo "尝试重新启动部署..."
  kubectl rollout restart deployment ${SERVICE_NAME} -n ${NAMESPACE}
  exit 1
fi