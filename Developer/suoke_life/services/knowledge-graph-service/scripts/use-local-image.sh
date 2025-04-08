#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务本地镜像部署脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 使用已经在本地的镜像
LOCAL_IMAGE="suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/suoke-knowledge-graph-service:1.0.0"
NAMESPACE="suoke-prod"
DEPLOYMENT_NAME="knowledge-graph-service"

echo -e "${BLUE}部署信息:${NC}"
echo -e "${YELLOW}命名空间: ${NAMESPACE}${NC}"
echo -e "${YELLOW}部署名称: ${DEPLOYMENT_NAME}${NC}"
echo -e "${YELLOW}使用本地镜像: ${LOCAL_IMAGE}${NC}"

# 删除现有部署
echo -e "\n${BLUE}删除现有部署...${NC}"
kubectl delete deployment -n ${NAMESPACE} ${DEPLOYMENT_NAME}

# 等待几秒确保删除完成
echo -e "\n${BLUE}等待删除完成...${NC}"
sleep 5

# 创建新的部署
echo -e "\n${BLUE}创建新的部署...${NC}"
cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${DEPLOYMENT_NAME}
  namespace: ${NAMESPACE}
  labels:
    app.kubernetes.io/instance: knowledge-graph
    app.kubernetes.io/name: ${DEPLOYMENT_NAME}
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/instance: knowledge-graph
      app.kubernetes.io/name: ${DEPLOYMENT_NAME}
  template:
    metadata:
      labels:
        app.kubernetes.io/instance: knowledge-graph
        app.kubernetes.io/name: ${DEPLOYMENT_NAME}
    spec:
      serviceAccountName: ${DEPLOYMENT_NAME}
      securityContext:
        {}
      containers:
        - name: ${DEPLOYMENT_NAME}
          securityContext:
            {}
          image: ${LOCAL_IMAGE}
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9464
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          resources:
            limits:
              cpu: 1000m
              memory: 1Gi
            requests:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: data
              mountPath: /data
          env:
            - name: APP_ENV
              value: production
            - name: POSTGRESQL_DATABASE
              value: knowledge_graph
            - name: POSTGRESQL_HOST
              value: postgres-postgresql.suoke-prod.svc.cluster.local
            - name: POSTGRESQL_PORT
              value: "5432"
            - name: POSTGRESQL_USERNAME
              valueFrom:
                secretKeyRef:
                  name: postgres-postgresql
                  key: postgres-username
            - name: POSTGRESQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-postgresql
                  key: postgres-password
            - name: DEBUG
              value: "false"
            - name: LOG_LEVEL
              value: info
            - name: PORT
              value: "8080"
            - name: METRICS_PORT
              value: "9464"
            - name: PGVECTOR_ENABLED
              value: "true"
      volumes:
        - name: data
          emptyDir: {}
      nodeSelector:
        role: suoke-core-np
      tolerations:
        - key: dedicated
          operator: Equal
          value: suoke-core
          effect: NoSchedule
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 部署创建失败!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ 新部署已创建!${NC}"
echo -e "${BLUE}正在等待Pod启动...${NC}"
sleep 10

# 显示Pod状态
echo -e "\n${BLUE}当前Pod状态:${NC}"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=${DEPLOYMENT_NAME}

echo -e "\n${BLUE}查看部署详情:${NC}"
kubectl describe deployment -n ${NAMESPACE} ${DEPLOYMENT_NAME}

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}如果Pod仍处于ImagePullBackOff状态，可考虑以下操作:${NC}"
echo -e "${YELLOW}1. 确认集群节点是否可以访问镜像仓库${NC}"
echo -e "${YELLOW}2. 创建镜像拉取密钥: kubectl create secret docker-registry...${NC}"
echo -e "${YELLOW}3. 将镜像导出并手动导入到集群节点${NC}"
echo -e "${BLUE}=========================================${NC}" 