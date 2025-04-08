#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务部署修复脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker未运行! 请先启动Docker${NC}"
    exit 1
fi

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl未安装! 请先安装kubectl${NC}"
    exit 1
fi

# 删除现有的失败部署
echo -e "\n${BLUE}步骤1: 删除现有的失败部署...${NC}"
kubectl delete deployment knowledge-graph-service || true
echo -e "${GREEN}✅ 已删除现有部署${NC}"

# 检查本地镜像
echo -e "\n${BLUE}步骤2: 检查本地镜像...${NC}"
LOCAL_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "knowledge-graph-service" | head -1)

if [ -z "$LOCAL_IMAGE" ]; then
    echo -e "${RED}❌ 未找到本地镜像!${NC}"
    echo -e "${YELLOW}正在构建新镜像...${NC}"
    
    # 构建新镜像
    docker build -t knowledge-graph-service:local -f Dockerfile.amd64 .
    LOCAL_IMAGE="knowledge-graph-service:local"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 镜像构建失败!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 镜像构建成功: ${LOCAL_IMAGE}${NC}"
else
    echo -e "${GREEN}✅ 找到本地镜像: ${LOCAL_IMAGE}${NC}"
fi

# 创建开发部署配置
echo -e "\n${BLUE}步骤3: 创建开发部署配置...${NC}"
cat > dev-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-graph-service
  labels:
    app: knowledge-graph-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: knowledge-graph-service
  template:
    metadata:
      labels:
        app: knowledge-graph-service
    spec:
      containers:
      - name: knowledge-graph-service
        image: ${LOCAL_IMAGE}
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9464
          name: metrics
        env:
        - name: LOG_LEVEL
          value: "debug"
        - name: DEBUG
          value: "true"
        - name: ENV
          value: "development"
        - name: DB_NEO4J_URI
          value: "bolt://localhost:7687"
        - name: DB_NEO4J_USERNAME
          value: "neo4j"
        - name: DB_NEO4J_PASSWORD
          value: "password"
        - name: REDIS_HOST
          value: "localhost"
        - name: REDIS_PORT
          value: "6379"
        - name: MILVUS_URI
          value: "localhost:19530"
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: models
          mountPath: /app/models
        - name: tmp
          mountPath: /app/tmp
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
      volumes:
      - name: data
        emptyDir: {}
      - name: models
        emptyDir: {}
      - name: tmp
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: knowledge-graph-service
  labels:
    app: knowledge-graph-service
spec:
  selector:
    app: knowledge-graph-service
  ports:
  - port: 8080
    targetPort: 8080
    name: http
  - port: 9464
    targetPort: 9464
    name: metrics
  type: ClusterIP
EOF

echo -e "${GREEN}✅ 开发部署配置已创建${NC}"

# 应用部署
echo -e "\n${BLUE}步骤4: 应用部署...${NC}"
kubectl apply -f dev-deployment.yaml

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 部署已应用${NC}"
else
    echo -e "${RED}❌ 部署失败!${NC}"
    exit 1
fi

# 等待部署就绪
echo -e "\n${BLUE}步骤5: 等待部署就绪...${NC}"
echo -e "${YELLOW}这可能需要一些时间...${NC}"

kubectl rollout status deployment/knowledge-graph-service --timeout=120s

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 部署已就绪${NC}"
    
    # 显示Pod状态
    echo -e "\n${BLUE}Pod状态:${NC}"
    kubectl get pods -l app=knowledge-graph-service
    
    # 显示服务状态
    echo -e "\n${BLUE}服务状态:${NC}"
    kubectl get svc knowledge-graph-service
    
    echo -e "\n${GREEN}✅ 知识图谱服务已成功部署!${NC}"
    echo -e "${YELLOW}您可以使用以下命令查看日志:${NC}"
    echo -e "kubectl logs -f -l app=knowledge-graph-service"
else
    echo -e "${RED}❌ 部署未在指定时间内就绪!${NC}"
    echo -e "${YELLOW}请使用以下命令检查状态:${NC}"
    echo -e "kubectl get pods -l app=knowledge-graph-service"
    echo -e "kubectl describe pod -l app=knowledge-graph-service"
fi

echo -e "\n${BLUE}=========================================${NC}"
