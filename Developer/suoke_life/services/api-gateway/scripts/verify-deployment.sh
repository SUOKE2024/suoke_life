#!/bin/bash

# 验证API网关是否部署成功
echo "验证API网关部署..."

# 获取API网关pod
PODS=$(kubectl get pods -n suoke -l app=api-gateway -o jsonpath="{.items[*].metadata.name}")

if [ -z "$PODS" ]; then
  echo "错误: 未找到API网关pods"
  exit 1
fi

# 检查pod状态
for POD in $PODS; do
  STATUS=$(kubectl get pod $POD -n suoke -o jsonpath="{.status.phase}")
  if [ "$STATUS" != "Running" ]; then
    echo "错误: Pod $POD 状态为 $STATUS，预期为 Running"
    exit 1
  fi
  
  # 检查健康状态
  READY=$(kubectl get pod $POD -n suoke -o jsonpath="{.status.containerStatuses[0].ready}")
  if [ "$READY" != "true" ]; then
    echo "错误: Pod $POD 尚未就绪"
    exit 1
  fi
done

echo "API网关Pod运行正常"

# 验证代理协调器服务集成
echo "验证代理协调器服务集成..."

# 从API网关访问代理协调器健康端点
kubectl exec $POD -n suoke -- curl -s http://localhost:3000/api/v1/agents/coordinator/health | grep "ok"

if [ $? -ne 0 ]; then
  echo "错误: 无法通过API网关访问代理协调器健康端点"
  exit 1
fi

echo "代理协调器集成验证通过"
echo "部署验证成功!"