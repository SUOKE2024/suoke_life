#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务生产环境部署脚本  ${NC}"
echo -e "${BLUE}==============================================${NC}"

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
VALUES_FILE="./helm/override-configs/values-production.yaml"

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

# 确保存在镜像拉取密钥
echo -e "\n${BLUE}检查镜像拉取密钥...${NC}"
if ! kubectl get secret aliyun-registry-secret -n ${NAMESPACE} &> /dev/null; then
    echo -e "${YELLOW}未找到镜像拉取密钥，请创建密钥:${NC}"
    echo -e "kubectl create secret docker-registry aliyun-registry-secret \\"
    echo -e "  --namespace=${NAMESPACE} \\"
    echo -e "  --docker-server=registry.cn-hangzhou.aliyuncs.com \\"
    echo -e "  --docker-username=<用户名> \\"
    echo -e "  --docker-password=<密码> \\"
    echo -e "  --docker-email=<邮箱>"
    
    # 可以选择在此脚本中执行密钥创建，但需要用户输入凭据
    read -p "是否现在创建密钥? (y/n): " CREATE_SECRET
    if [[ "$CREATE_SECRET" == "y" ]]; then
        read -p "阿里云容器镜像服务用户名: " DOCKER_USERNAME
        read -sp "阿里云容器镜像服务密码: " DOCKER_PASSWORD
        echo
        read -p "邮箱: " DOCKER_EMAIL
        
        kubectl create secret docker-registry aliyun-registry-secret \
          --namespace=${NAMESPACE} \
          --docker-server=registry.cn-hangzhou.aliyuncs.com \
          --docker-username=${DOCKER_USERNAME} \
          --docker-password=${DOCKER_PASSWORD} \
          --docker-email=${DOCKER_EMAIL}
          
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ 创建密钥失败!${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ 密钥创建成功!${NC}"
        fi
    else
        echo -e "${YELLOW}请手动创建密钥后再运行此脚本${NC}"
        exit 1
    fi
fi

# 配置服务账户使用镜像拉取密钥
echo -e "\n${BLUE}配置服务账户使用镜像拉取密钥...${NC}"
kubectl get serviceaccount knowledge-graph-service -n ${NAMESPACE} &> /dev/null
if [ $? -eq 0 ]; then
    kubectl patch serviceaccount knowledge-graph-service \
      -n ${NAMESPACE} \
      -p '{"imagePullSecrets": [{"name": "aliyun-registry-secret"}]}'
else
    echo -e "${YELLOW}服务账户不存在，将在Helm部署时创建${NC}"
fi

# 使用Helm部署或升级
echo -e "\n${BLUE}使用Helm部署/升级服务...${NC}"
helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
  --namespace ${NAMESPACE} \
  -f ${VALUES_FILE} \
  --set image.repository=${REGISTRY}/${REPOSITORY} \
  --set image.tag=${VERSION} \
  --set deployment.annotations.timestamp="$(date +%s)" \
  --create-namespace \
  --atomic \
  --timeout 10m

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Helm部署失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Helm部署成功!${NC}"

# 等待Pod就绪
echo -e "\n${BLUE}等待Pod就绪...${NC}"
kubectl rollout status deployment/${RELEASE_NAME} -n ${NAMESPACE} --timeout=300s

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Pod未能在指定时间内就绪!${NC}"
    echo -e "\n${BLUE}查看Pod状态:${NC}"
    kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
    echo -e "\n${BLUE}查看Pod描述:${NC}"
    kubectl describe pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
    
    # 查看Pod日志
    echo -e "\n${BLUE}查看Pod日志:${NC}"
    POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME} -o jsonpath='{.items[0].metadata.name}')
    kubectl logs ${POD_NAME} -n ${NAMESPACE}
    exit 1
fi

# 显示服务信息
echo -e "\n${BLUE}服务信息:${NC}"
kubectl get svc -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}

echo -e "\n${BLUE}Pod信息:${NC}"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}

echo -e "\n${GREEN}✅ 部署完成!${NC}"
echo -e "${BLUE}==============================================${NC}"
echo -e "${YELLOW}访问服务: http://知识图谱服务地址:8080${NC}"
echo -e "${BLUE}==============================================${NC}"