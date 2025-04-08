#!/bin/bash
set -e

echo "===== 开始部署Knowledge Graph Service ====="

# 检查kubectl是否安装
if ! command -v kubectl &> /dev/null; then
    echo "错误: 未找到kubectl命令，请先安装kubectl"
    exit 1
fi

# 检查当前kubectl上下文
CURRENT_CONTEXT=$(kubectl config current-context)
echo "当前Kubernetes上下文: $CURRENT_CONTEXT"
read -p "是否继续使用此上下文进行部署? [y/N]: " CONTINUE
if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
    echo "已取消部署"
    exit 0
fi

# 应用部署配置
echo "应用Knowledge Graph Service部署配置..."
kubectl apply -f aliyun-deployment.yaml

# 等待部署完成
echo "等待部署完成..."
kubectl -n suoke-services rollout status deployment/knowledge-graph-service

# 获取服务状态
echo "服务状态:"
kubectl -n suoke-services get pods -l app=knowledge-graph-service
kubectl -n suoke-services get svc knowledge-graph-service
kubectl -n suoke-services get ingress knowledge-graph-service-ingress

echo "===== Knowledge Graph Service部署完成 ====="
echo "服务内部访问地址: http://knowledge-graph-service.suoke-services"
echo "服务外部访问地址: http://kg.suoke.life"
echo ""
echo "API文档地址: http://kg.suoke.life/api/v1/docs"
echo "健康检查: http://kg.suoke.life/health" 