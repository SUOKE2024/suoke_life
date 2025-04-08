#!/bin/bash
set -e

# 阿里云镜像仓库信息
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
NAMESPACE="suoke"

# 使用环境变量或提示输入凭据
USERNAME=${ALIYUN_USERNAME:-$(read -p "请输入阿里云镜像仓库用户名: " username; echo $username)}
PASSWORD=${ALIYUN_PASSWORD:-$(read -s -p "请输入阿里云镜像仓库密码: " password; echo $password; echo)}

# 创建命名空间（如果不存在）
kubectl create namespace suoke-services --dry-run=client -o yaml | kubectl apply -f -

# 创建镜像仓库凭证Secret
kubectl create secret docker-registry aliyun-registry-secret \
  --namespace=suoke-services \
  --docker-server=$REGISTRY \
  --docker-username=$USERNAME \
  --docker-password=$PASSWORD \
  --docker-email=admin@suoke.life \
  --dry-run=client -o yaml | kubectl apply -f -

echo "阿里云镜像仓库密钥创建成功!" 