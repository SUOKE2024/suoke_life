#!/bin/bash

echo "开始部署到生产环境..."

# 1. 构建最新镜像
echo "构建Docker镜像..."
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:latest .

# 2. 推送到仓库
echo "推送到镜像仓库..."
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:latest

# 3. 应用Helm升级
echo "应用Helm升级..."
helm upgrade api-gateway ./helm/api-gateway \
  --namespace suoke \
  --set image.tag=latest \
  --set replicaCount=3

# 4. 等待部署完成
echo "等待部署完成..."
kubectl rollout status deployment/api-gateway -n suoke

# 5. 验证部署
echo "验证部署..."
./scripts/verify-deployment.sh

echo "部署完成!"