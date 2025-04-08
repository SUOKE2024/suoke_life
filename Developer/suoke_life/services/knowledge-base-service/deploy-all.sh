#!/bin/bash
# 知识库服务一键部署脚本

set -e  # 遇到错误立即退出

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示欢迎信息
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}     知识库服务一键部署脚本         ${NC}"
echo -e "${GREEN}=====================================${NC}"
echo "开始时间: $(date)"
echo ""

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}错误: kubectl命令未找到${NC}"
    exit 1
fi

# 检查命名空间是否存在
if ! kubectl get namespace suoke-prod &> /dev/null; then
    echo -e "${YELLOW}命名空间suoke-prod不存在，正在创建...${NC}"
    kubectl create namespace suoke-prod
fi

# 部署PostgreSQL数据库
echo -e "${YELLOW}1. 部署PostgreSQL数据库...${NC}"
kubectl apply -f k8s/postgres.yaml
echo -e "${GREEN}PostgreSQL配置已应用${NC}"

# 等待PostgreSQL启动
echo "等待PostgreSQL就绪..."
kubectl wait --for=condition=ready pod -l app=postgres -n suoke-prod --timeout=120s || true

# 部署Milvus向量数据库
echo -e "${YELLOW}2. 部署Milvus向量数据库...${NC}"
kubectl apply -f k8s/milvus.yaml
echo -e "${GREEN}Milvus配置已应用${NC}"

# 等待Milvus启动
echo "等待Milvus就绪..."
kubectl wait --for=condition=ready pod -l app=milvus -n suoke-prod --timeout=120s || true

# 设置监控和备份
echo -e "${YELLOW}3. 设置监控和备份...${NC}"
kubectl apply -f k8s/monitoring.yaml
kubectl apply -f k8s/backup.yaml
echo -e "${GREEN}监控和备份配置已应用${NC}"

# 部署知识库服务
echo -e "${YELLOW}4. 部署知识库服务...${NC}"
if kubectl get deployment knowledge-base-service -n suoke-prod &> /dev/null; then
    echo "知识库服务已存在，正在更新..."
    kubectl delete deployment knowledge-base-service -n suoke-prod
fi

kubectl apply -f k8s/deployment.yaml
echo -e "${GREEN}知识库服务配置已应用${NC}"

# 等待知识库服务启动
echo "等待知识库服务就绪..."
kubectl wait --for=condition=available deployment/knowledge-base-service -n suoke-prod --timeout=120s || true

# 检查部署状态
echo -e "${YELLOW}5. 检查部署状态...${NC}"
kubectl get pods -n suoke-prod -l app=knowledge-base-service
kubectl get pods -n suoke-prod -l app=postgres
kubectl get pods -n suoke-prod -l app=milvus

# 运行健康检查
echo -e "${YELLOW}6. 运行健康检查...${NC}"
./scripts/kb-health-check.sh || true

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}     知识库服务部署完成！           ${NC}"
echo -e "${GREEN}=====================================${NC}"
echo "结束时间: $(date)"
echo ""
echo "执行以下命令查看服务日志:"
echo "kubectl logs -l app=knowledge-base-service -n suoke-prod --tail=100 -f"