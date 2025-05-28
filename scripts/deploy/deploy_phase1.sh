#!/bin/bash

# 索克生活项目第一阶段部署脚本
# 部署LiteLLM网关、监控体系和配置管理

set -e

echo "🚀 开始部署索克生活项目第一阶段基础设施..."
echo "================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl未找到，请先安装kubectl${NC}"
    exit 1
fi

# 检查集群连接
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ 无法连接到Kubernetes集群${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Kubernetes集群连接正常${NC}"

# 步骤1: 创建命名空间和基础配置
echo -e "\n${BLUE}📦 步骤1: 创建命名空间和基础配置${NC}"
kubectl apply -f deploy/config-management/namespace.yaml
echo -e "${GREEN}✅ 命名空间和基础配置创建完成${NC}"

# 步骤2: 部署Redis缓存
echo -e "\n${BLUE}📦 步骤2: 部署Redis缓存服务${NC}"
kubectl apply -f deploy/litellm/secrets.yaml
echo -e "${GREEN}✅ Redis缓存服务部署完成${NC}"

# 步骤3: 部署LiteLLM网关
echo -e "\n${BLUE}📦 步骤3: 部署LiteLLM网关${NC}"
kubectl apply -f deploy/litellm/deployment.yaml

# 等待LiteLLM网关启动
echo -e "${YELLOW}⏳ 等待LiteLLM网关启动...${NC}"
kubectl wait --for=condition=ready pod -l app=litellm-gateway -n suoke-life --timeout=300s
echo -e "${GREEN}✅ LiteLLM网关部署完成${NC}"

# 步骤4: 部署Prometheus监控
echo -e "\n${BLUE}📦 步骤4: 部署Prometheus监控${NC}"
kubectl apply -f deploy/monitoring/prometheus-config.yaml
kubectl apply -f deploy/monitoring/prometheus-deployment.yaml

# 等待Prometheus启动
echo -e "${YELLOW}⏳ 等待Prometheus启动...${NC}"
kubectl wait --for=condition=ready pod -l app=prometheus -n suoke-life --timeout=300s
echo -e "${GREEN}✅ Prometheus监控部署完成${NC}"

# 步骤5: 部署Grafana
echo -e "\n${BLUE}📦 步骤5: 部署Grafana仪表板${NC}"
kubectl apply -f deploy/monitoring/grafana-deployment.yaml

# 等待Grafana启动
echo -e "${YELLOW}⏳ 等待Grafana启动...${NC}"
kubectl wait --for=condition=ready pod -l app=grafana -n suoke-life --timeout=300s
echo -e "${GREEN}✅ Grafana仪表板部署完成${NC}"

# 步骤6: 验证部署状态
echo -e "\n${BLUE}🔍 步骤6: 验证部署状态${NC}"
echo -e "\n${YELLOW}📊 服务状态检查:${NC}"
kubectl get pods -n suoke-life
kubectl get services -n suoke-life

# 检查服务健康状态
echo -e "\n${YELLOW}🏥 健康检查:${NC}"

# 检查LiteLLM网关
LITELLM_POD=$(kubectl get pods -n suoke-life -l app=litellm-gateway -o jsonpath='{.items[0].metadata.name}')
if [ ! -z "$LITELLM_POD" ]; then
    echo -e "${GREEN}✅ LiteLLM网关: $LITELLM_POD${NC}"
    # 端口转发测试（后台运行）
    kubectl port-forward -n suoke-life $LITELLM_POD 4000:4000 &
    PORT_FORWARD_PID=$!
    sleep 3
    
    # 测试健康检查
    if curl -s http://localhost:4000/health > /dev/null; then
        echo -e "${GREEN}✅ LiteLLM网关健康检查通过${NC}"
    else
        echo -e "${YELLOW}⚠️ LiteLLM网关健康检查失败，可能仍在启动中${NC}"
    fi
    
    # 停止端口转发
    kill $PORT_FORWARD_PID 2>/dev/null || true
else
    echo -e "${RED}❌ LiteLLM网关Pod未找到${NC}"
fi

# 检查Prometheus
PROMETHEUS_POD=$(kubectl get pods -n suoke-life -l app=prometheus -o jsonpath='{.items[0].metadata.name}')
if [ ! -z "$PROMETHEUS_POD" ]; then
    echo -e "${GREEN}✅ Prometheus: $PROMETHEUS_POD${NC}"
else
    echo -e "${RED}❌ Prometheus Pod未找到${NC}"
fi

# 检查Grafana
GRAFANA_POD=$(kubectl get pods -n suoke-life -l app=grafana -o jsonpath='{.items[0].metadata.name}')
if [ ! -z "$GRAFANA_POD" ]; then
    echo -e "${GREEN}✅ Grafana: $GRAFANA_POD${NC}"
else
    echo -e "${RED}❌ Grafana Pod未找到${NC}"
fi

# 检查Redis
REDIS_POD=$(kubectl get pods -n suoke-life -l app=redis -o jsonpath='{.items[0].metadata.name}')
if [ ! -z "$REDIS_POD" ]; then
    echo -e "${GREEN}✅ Redis: $REDIS_POD${NC}"
else
    echo -e "${RED}❌ Redis Pod未找到${NC}"
fi

# 步骤7: 提供访问信息
echo -e "\n${BLUE}🌐 步骤7: 服务访问信息${NC}"
echo -e "${YELLOW}要访问服务，请使用以下端口转发命令:${NC}"
echo ""
echo -e "${GREEN}LiteLLM网关:${NC}"
echo "  kubectl port-forward -n suoke-life svc/litellm-gateway-service 4000:4000"
echo "  访问地址: http://localhost:4000"
echo "  管理界面: http://localhost:8080"
echo ""
echo -e "${GREEN}Prometheus:${NC}"
echo "  kubectl port-forward -n suoke-life svc/prometheus-service 9090:9090"
echo "  访问地址: http://localhost:9090"
echo ""
echo -e "${GREEN}Grafana:${NC}"
echo "  kubectl port-forward -n suoke-life svc/grafana-service 3000:3000"
echo "  访问地址: http://localhost:3000"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""

# 步骤8: 下一步建议
echo -e "\n${BLUE}📋 下一步建议${NC}"
echo -e "${YELLOW}1. 配置LLM API密钥:${NC}"
echo "   kubectl create secret generic llm-secrets -n suoke-life \\"
echo "     --from-literal=openai-key=your-openai-key \\"
echo "     --from-literal=anthropic-key=your-anthropic-key \\"
echo "     --from-literal=google-key=your-google-key"
echo ""
echo -e "${YELLOW}2. 重启LiteLLM网关以加载新密钥:${NC}"
echo "   kubectl rollout restart deployment/litellm-gateway -n suoke-life"
echo ""
echo -e "${YELLOW}3. 验证LiteLLM网关功能:${NC}"
echo "   curl -X POST http://localhost:4000/chat/completions \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"model\": \"gpt-4\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}]}'"
echo ""

echo -e "\n${GREEN}🎉 第一阶段部署完成！${NC}"
echo -e "${GREEN}基础设施已就绪，可以开始第二阶段的智能体协作框架部署。${NC}" 