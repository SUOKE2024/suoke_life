#!/bin/bash

# 索克生活 微服务一键部署脚本
# 按节点池资源分配原则部署所有微服务

set -e

echo "===== 索克生活APP微服务一键部署 ====="
echo "节点池资源分配原则:"
echo "| 节点池         | 分配服务组         | 特点                 |"
echo "|--------------|------------------|---------------------|"
echo "| suoke-core-np | core, feature    | 高可用性，稳定性优先   |"
echo "| suoke-ai-np   | ai, diagnosis    | 高计算能力，GPU支持    |"
echo "| suoke-db-np   | knowledge        | 高IO性能，大存储容量   |"
echo ""

# 配置变量
REGISTRY_URL="${REGISTRY_URL:-suoke-registry.cn-hangzhou.cr.aliyuncs.com}"
REGISTRY_NAMESPACE="${REGISTRY_NAMESPACE:-suoke}"
TAG="${TAG:-latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_MAPPING_FILE="${SCRIPT_DIR}/service-group-mapping.json"

# 检查依赖
command -v kubectl >/dev/null 2>&1 || { echo "错误: 需要安装kubectl"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "错误: 需要安装jq"; exit 1; }
command -v envsubst >/dev/null 2>&1 || { echo "错误: 需要安装envsubst"; exit 1; }

# 检查文件
if [ ! -f "${SERVICE_MAPPING_FILE}" ]; then
  echo "错误: 服务映射文件不存在: ${SERVICE_MAPPING_FILE}"
  exit 1
fi

# 1. 首先设置节点标签
echo "步骤1: 配置节点池标签..."
kubectl apply -f "${SCRIPT_DIR}/nodepool-setup.yaml"
echo "等待节点标签配置完成..."
sleep 10
kubectl wait --for=condition=complete --timeout=60s job/nodepool-setup -n kube-system || true

# 2. 创建命名空间
echo "步骤2: 创建命名空间..."
kubectl apply -f "${SCRIPT_DIR}/../k8s/namespace.yaml"

# 3. 创建持久卷声明
echo "步骤3: 创建持久卷声明..."
kubectl apply -f "${SCRIPT_DIR}/pvc-definitions.yaml"

# 4. 部署Consul服务发现
echo "步骤4: 部署Consul服务发现..."
kubectl apply -f "${SCRIPT_DIR}/../k8s/consul-deployment.yaml"
kubectl apply -f "${SCRIPT_DIR}/../k8s/consul-service.yaml"

# 5. 部署所有微服务
echo "步骤5: 开始部署所有微服务..."

# 5.1 部署Core服务和Feature服务
echo "步骤5.1: 部署Core服务和Feature服务..."

# Core服务
CORE_SERVICES=$(jq -r '.core[]' "${SERVICE_MAPPING_FILE}")
for SERVICE_NAME in ${CORE_SERVICES}; do
  echo "正在部署Core服务: ${SERVICE_NAME}..."
  PORT=$(jq -r ".service_ports.\"${SERVICE_NAME}\"" "${SERVICE_MAPPING_FILE}")
  export SERVICE_NAME PORT REGISTRY_URL REGISTRY_NAMESPACE TAG
  
  # 应用ConfigMap
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml"
  fi
  
  # 生成和应用Deployment
  envsubst < "${SCRIPT_DIR}/core-deployment-template.yaml" > "/tmp/${SERVICE_NAME}-deployment.yaml"
  kubectl apply -f "/tmp/${SERVICE_NAME}-deployment.yaml"
  
  # 应用Service
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml"
  fi
done

# Feature服务
FEATURE_SERVICES=$(jq -r '.feature[]' "${SERVICE_MAPPING_FILE}")
for SERVICE_NAME in ${FEATURE_SERVICES}; do
  echo "正在部署Feature服务: ${SERVICE_NAME}..."
  PORT=$(jq -r ".service_ports.\"${SERVICE_NAME}\"" "${SERVICE_MAPPING_FILE}")
  export SERVICE_NAME PORT REGISTRY_URL REGISTRY_NAMESPACE TAG
  
  # 应用ConfigMap
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml"
  fi
  
  # 生成和应用Deployment
  envsubst < "${SCRIPT_DIR}/core-deployment-template.yaml" > "/tmp/${SERVICE_NAME}-deployment.yaml"
  kubectl apply -f "/tmp/${SERVICE_NAME}-deployment.yaml"
  
  # 应用Service
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml"
  fi
done

# 5.2 部署AI服务和诊断服务
echo "步骤5.2: 部署AI服务和诊断服务..."

# 合并AI和诊断服务
AI_SERVICES=$(jq -r '.ai[]' "${SERVICE_MAPPING_FILE}")
for SERVICE_NAME in ${AI_SERVICES}; do
  echo "正在部署AI/诊断服务: ${SERVICE_NAME}..."
  PORT=$(jq -r ".service_ports.\"${SERVICE_NAME}\"" "${SERVICE_MAPPING_FILE}")
  GPU_COUNT=$(jq -r ".gpu_services.\"${SERVICE_NAME}\" // 0" "${SERVICE_MAPPING_FILE}")
  
  if [ "${GPU_COUNT}" -gt 0 ]; then
    ENABLE_GPU=true
  else
    ENABLE_GPU=false
  fi
  
  export SERVICE_NAME PORT GPU_COUNT ENABLE_GPU REGISTRY_URL REGISTRY_NAMESPACE TAG
  
  # 应用ConfigMap
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml"
  elif [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/base/configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/base/configmap.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml"
  fi
  
  # 生成和应用Deployment
  envsubst < "${SCRIPT_DIR}/ai-deployment-template.yaml" > "/tmp/${SERVICE_NAME}-deployment.yaml"
  kubectl apply -f "/tmp/${SERVICE_NAME}-deployment.yaml"
  
  # 应用Service
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml"
  elif [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/base/service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/base/service.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml"
  fi
done

# 5.3 部署知识服务
echo "步骤5.3: 部署知识服务..."

KNOWLEDGE_SERVICES=$(jq -r '.knowledge[]' "${SERVICE_MAPPING_FILE}")
for SERVICE_NAME in ${KNOWLEDGE_SERVICES}; do
  echo "正在部署知识服务: ${SERVICE_NAME}..."
  PORT=$(jq -r ".service_ports.\"${SERVICE_NAME}\"" "${SERVICE_MAPPING_FILE}")
  export SERVICE_NAME PORT REGISTRY_URL REGISTRY_NAMESPACE TAG
  
  # 应用ConfigMap
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/configmap.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-configmap.yaml"
  fi
  
  # 生成和应用Deployment
  envsubst < "${SCRIPT_DIR}/db-deployment-template.yaml" > "/tmp/${SERVICE_NAME}-deployment.yaml"
  kubectl apply -f "/tmp/${SERVICE_NAME}-deployment.yaml"
  
  # 应用Service
  if [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/service.yaml"
  elif [ -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/03-service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../${SERVICE_NAME}/k8s/03-service.yaml"
  elif [ -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml" ]; then
    kubectl apply -f "${SCRIPT_DIR}/../k8s/${SERVICE_NAME}-service.yaml"
  fi
done

# 6. 部署Ingress配置
echo "步骤6: 部署Ingress配置..."
kubectl apply -f "${SCRIPT_DIR}/../k8s/ingress.yaml"

# 7. 清理临时文件
echo "步骤7: 清理临时文件..."
rm -f /tmp/*-deployment.yaml

echo "===== 索克生活APP微服务部署完成! ====="
echo "正在检查各服务部署状态..."

# 检查所有服务的部署状态
ALL_SERVICES="${CORE_SERVICES} ${FEATURE_SERVICES} ${AI_SERVICES} ${KNOWLEDGE_SERVICES}"
for SERVICE_NAME in ${ALL_SERVICES}; do
  echo -n "检查 ${SERVICE_NAME} 状态: "
  kubectl rollout status deployment/${SERVICE_NAME} -n suoke --timeout=30s || echo "等待中..."
done

echo -e "\n所有服务部署完成! 您可以使用以下命令查看详细状态："
echo "kubectl get pods -n suoke -o wide"
echo "kubectl get svc -n suoke"
echo "kubectl get nodes --show-labels | grep suoke.life" 