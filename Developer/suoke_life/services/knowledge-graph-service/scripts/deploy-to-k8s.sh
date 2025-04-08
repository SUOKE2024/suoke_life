#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务Kubernetes部署脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义变量
NAMESPACE=${1:-suoke-prod}
RELEASE_NAME="knowledge-graph"
CHART_PATH="./helm"
VALUES_FILE="./helm/override-configs/values-${NAMESPACE#suoke-}.yaml"

# 显示部署信息
echo -e "${BLUE}部署信息:${NC}"
echo -e "${YELLOW}命名空间: ${NAMESPACE}${NC}"
echo -e "${YELLOW}发布名称: ${RELEASE_NAME}${NC}"
echo -e "${YELLOW}Chart路径: ${CHART_PATH}${NC}"
echo -e "${YELLOW}配置文件: ${VALUES_FILE}${NC}"

# 检查命名空间是否存在
echo -e "\n${BLUE}检查命名空间 ${NAMESPACE} 是否存在...${NC}"
if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
    echo -e "${YELLOW}命名空间 ${NAMESPACE} 不存在，正在创建...${NC}"
    kubectl create namespace ${NAMESPACE}
    
    # 为命名空间启用Istio注入
    kubectl label namespace ${NAMESPACE} istio-injection=enabled --overwrite
    
    echo -e "${GREEN}命名空间 ${NAMESPACE} 已创建并启用Istio注入${NC}"
else
    echo -e "${GREEN}命名空间 ${NAMESPACE} 已存在${NC}"
fi

# 检查镜像拉取密钥是否存在
echo -e "\n${BLUE}检查镜像拉取密钥是否存在...${NC}"
if ! kubectl get secret suoke-registry-secret -n ${NAMESPACE} &> /dev/null; then
    echo -e "${YELLOW}镜像拉取密钥不存在，正在创建...${NC}"
    
    # 提示用户输入镜像仓库凭据
    echo -e "${YELLOW}请输入阿里云容器镜像仓库用户名:${NC}"
    read -r REGISTRY_USERNAME
    
    echo -e "${YELLOW}请输入阿里云容器镜像仓库密码:${NC}"
    read -rs REGISTRY_PASSWORD
    
    # 创建镜像拉取密钥
    kubectl create secret docker-registry suoke-registry-secret \
        --docker-server=suoke-registry.cn-hangzhou.cr.aliyuncs.com \
        --docker-username=${REGISTRY_USERNAME} \
        --docker-password=${REGISTRY_PASSWORD} \
        -n ${NAMESPACE}
    
    echo -e "${GREEN}镜像拉取密钥已创建${NC}"
else
    echo -e "${GREEN}镜像拉取密钥已存在${NC}"
fi

# 检查Helm是否已安装
echo -e "\n${BLUE}检查Helm是否已安装...${NC}"
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm未安装，请先安装Helm${NC}"
    exit 1
else
    echo -e "${GREEN}Helm已安装${NC}"
fi

# 更新Helm仓库
echo -e "\n${BLUE}更新Helm仓库...${NC}"
helm repo update

# 部署或升级应用
echo -e "\n${BLUE}正在部署或升级知识图谱服务...${NC}"
helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
    --namespace ${NAMESPACE} \
    -f ${VALUES_FILE} \
    --set namespace=${NAMESPACE} \
    --debug

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ 知识图谱服务已成功部署/升级到命名空间 ${NAMESPACE}!${NC}"
    
    # 显示部署状态
    echo -e "\n${BLUE}部署状态:${NC}"
    kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
else
    echo -e "\n${RED}❌ 部署失败!${NC}"
    exit 1
fi

echo -e "\n${BLUE}=========================================${NC}" 