#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务 Helm 部署脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义变量
NAMESPACE="suoke-prod"
RELEASE_NAME="knowledge-graph"
VERSION="1.0.0"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REPOSITORY="suoke/suoke-knowledge-graph-service"
TAG="${REGISTRY}/${REPOSITORY}:${VERSION}"
CHART_PATH="./helm"
VALUES_FILE="./helm/override-configs/values-storage-fix.yaml"

# 显示部署信息
echo -e "${BLUE}部署信息:${NC}"
echo -e "${YELLOW}命名空间: ${NAMESPACE}${NC}"
echo -e "${YELLOW}发布名称: ${RELEASE_NAME}${NC}"
echo -e "${YELLOW}镜像: ${TAG}${NC}"
echo -e "${YELLOW}Chart路径: ${CHART_PATH}${NC}"
echo -e "${YELLOW}Values文件: ${VALUES_FILE}${NC}"

# 检查values文件是否存在
if [ ! -f "$VALUES_FILE" ]; then
    echo -e "${RED}❌ Values文件不存在: ${VALUES_FILE}${NC}"
    exit 1
fi

# 确保命名空间存在
echo -e "\n${BLUE}确保命名空间存在...${NC}"
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# 将镜像标签添加到values覆盖文件
echo -e "\n${BLUE}更新values文件中的镜像标签...${NC}"
cat > ./helm/override-configs/image-values.yaml << EOF
image:
  repository: ${REGISTRY}/${REPOSITORY}
  tag: ${VERSION}
  pullPolicy: Always
EOF

# 使用Helm部署或升级
echo -e "\n${BLUE}使用Helm部署/升级服务...${NC}"
helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
  --namespace ${NAMESPACE} \
  -f ${VALUES_FILE} \
  -f ./helm/override-configs/image-values.yaml \
  --set deployment.annotations.timestamp="$(date +%s)" \
  --create-namespace \
  --atomic \
  --timeout 5m

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Helm部署失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Helm部署成功!${NC}"

# 等待Pod就绪
echo -e "\n${BLUE}等待Pod就绪...${NC}"
kubectl rollout status deployment/${RELEASE_NAME} -n ${NAMESPACE} --timeout=120s

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Pod未能在指定时间内就绪!${NC}"
    echo -e "\n${BLUE}查看Pod状态:${NC}"
    kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
    echo -e "\n${BLUE}查看Pod描述:${NC}"
    kubectl describe pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
    exit 1
fi

# 显示服务信息
echo -e "\n${BLUE}服务信息:${NC}"
kubectl get svc -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}

echo -e "\n${BLUE}Pod信息:${NC}"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}

echo -e "\n${GREEN}✅ 部署完成!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "${YELLOW}访问服务: http://知识图谱服务地址:8080${NC}"
echo -e "${BLUE}=========================================${NC}" 