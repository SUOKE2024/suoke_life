#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务生产环境部署脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 删除现有部署
echo -e "\n${BLUE}删除现有部署...${NC}"
kubectl delete -f ./scripts/remote-deployment.yaml --ignore-not-found=true

# 等待删除完成
echo -e "\n${BLUE}等待删除完成...${NC}"
sleep 5

# 创建新部署
echo -e "\n${BLUE}创建新部署...${NC}"
kubectl apply -f ./scripts/remote-deployment.yaml

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 部署失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ 部署命令执行成功!${NC}"

# 等待Pod就绪
echo -e "\n${BLUE}等待Pod就绪...${NC}"
kubectl rollout status deployment/knowledge-graph-service -n suoke-prod --timeout=120s

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Pod未能在指定时间内就绪!${NC}"
    echo -e "\n${BLUE}查看Pod状态:${NC}"
    kubectl get pods -n suoke-prod -l app=knowledge-graph-service
    echo -e "\n${BLUE}查看Pod描述:${NC}"
    kubectl describe pods -n suoke-prod -l app=knowledge-graph-service
    exit 1
fi

# 显示服务信息
echo -e "\n${BLUE}服务信息:${NC}"
kubectl get svc -n suoke-prod -l app=knowledge-graph-service

echo -e "\n${BLUE}Pod信息:${NC}"
kubectl get pods -n suoke-prod -l app=knowledge-graph-service

echo -e "\n${GREEN}✅ 部署完成!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "${YELLOW}访问服务: http://knowledge-graph.suoke.life/health${NC}"
echo -e "${BLUE}=========================================${NC}" 