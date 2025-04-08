#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务一键部署脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义命令行参数
ENV=${1:-"dev"}
NAMESPACE=${2:-"default"}
BUILD_IMAGE=${3:-"true"}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}用法:${NC}"
    echo -e "  $0 [environment] [namespace] [build_image]"
    echo -e ""
    echo -e "${BLUE}参数:${NC}"
    echo -e "  environment  部署环境 (dev|test|staging|prod), 默认: dev"
    echo -e "  namespace    Kubernetes命名空间, 默认: default"
    echo -e "  build_image  是否构建镜像 (true|false), 默认: true"
    echo -e ""
    echo -e "${BLUE}示例:${NC}"
    echo -e "  $0                     # 部署到开发环境，默认命名空间"
    echo -e "  $0 test suoke-test     # 部署到测试环境，suoke-test命名空间"
    echo -e "  $0 prod suoke-prod     # 部署到生产环境，suoke-prod命名空间"
    echo -e "  $0 dev default false   # 部署到开发环境，不构建镜像"
    echo -e ""
}

# 检查参数
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_help
    exit 0
fi

# 检查环境
if [[ ! "$ENV" =~ ^(dev|test|staging|prod)$ ]]; then
    echo -e "${RED}❌ 无效的环境: $ENV${NC}"
    show_help
    exit 1
fi

# 检查必要工具
check_tools() {
    echo -e "\n${BLUE}检查必要工具...${NC}"
    
    MISSING_TOOLS=0
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker未安装!${NC}"
        MISSING_TOOLS=1
    else
        echo -e "${GREEN}✅ Docker已安装${NC}"
        
        # 检查Docker是否运行
        if ! docker info &> /dev/null; then
            echo -e "${RED}❌ Docker未运行!${NC}"
            MISSING_TOOLS=1
        else
            echo -e "${GREEN}✅ Docker正在运行${NC}"
        fi
    fi
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl未安装!${NC}"
        MISSING_TOOLS=1
    else
        echo -e "${GREEN}✅ kubectl已安装${NC}"
        
        # 检查kubectl连接
        if ! kubectl get nodes &> /dev/null; then
            echo -e "${RED}❌ kubectl无法连接到Kubernetes集群!${NC}"
            MISSING_TOOLS=1
        else
            echo -e "${GREEN}✅ kubectl可以连接到Kubernetes集群${NC}"
        fi
    fi
    
    # 检查Go
    if ! command -v go &> /dev/null; then
        echo -e "${YELLOW}⚠️ Go未安装，将使用Docker构建${NC}"
    else
        echo -e "${GREEN}✅ Go已安装${NC}"
    fi
    
    if [ $MISSING_TOOLS -eq 1 ]; then
        echo -e "${RED}❌ 缺少必要工具，无法继续!${NC}"
        exit 1
    fi
}

# 构建镜像
build_image() {
    if [ "$BUILD_IMAGE" != "true" ]; then
        echo -e "\n${BLUE}跳过镜像构建...${NC}"
        return 0
    fi
    
    echo -e "\n${BLUE}构建Docker镜像...${NC}"
    
    # 根据环境选择Dockerfile
    if [ "$ENV" == "prod" ]; then
        DOCKERFILE="Dockerfile.amd64"
        TAG="knowledge-graph-service:prod"
    else
        DOCKERFILE="Dockerfile.amd64"
        TAG="knowledge-graph-service:$ENV"
    fi
    
    echo -e "${YELLOW}使用Dockerfile: $DOCKERFILE${NC}"
    echo -e "${YELLOW}构建标签: $TAG${NC}"
    
    # 构建镜像
    if docker build -t $TAG -f $DOCKERFILE .; then
        echo -e "${GREEN}✅ 镜像构建成功: $TAG${NC}"
    else
        echo -e "${RED}❌ 镜像构建失败!${NC}"
        exit 1
    fi
    
    # 为本地开发标记latest标签
    if [ "$ENV" == "dev" ]; then
        docker tag $TAG knowledge-graph-service:latest
        echo -e "${GREEN}✅ 已标记latest标签${NC}"
    fi
}

# 创建配置
create_configs() {
    echo -e "\n${BLUE}创建配置...${NC}"
    
    # 检查命名空间是否存在
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}命名空间 $NAMESPACE 不存在，正在创建...${NC}"
        kubectl create namespace $NAMESPACE
    fi
    
    # 使用配置管理脚本
    if [ -f "./scripts/manage-configs.sh" ]; then
        chmod +x ./scripts/manage-configs.sh
        ./scripts/manage-configs.sh create $ENV $NAMESPACE
    else
        echo -e "${RED}❌ 配置管理脚本不存在!${NC}"
        exit 1
    fi
}

# 部署应用
deploy_app() {
    echo -e "\n${BLUE}部署应用...${NC}"
    
    # 根据环境选择部署方法
    if [ "$ENV" == "prod" ]; then
        # 生产环境使用Helm
        echo -e "${YELLOW}使用Helm部署到生产环境...${NC}"
        
        # 检查Helm是否安装
        if ! command -v helm &> /dev/null; then
            echo -e "${RED}❌ Helm未安装!${NC}"
            exit 1
        fi
        
        # 更新Helm依赖
        helm dependency update ./helm
        
        # 部署或升级
        if helm upgrade --install knowledge-graph ./helm \
            --namespace $NAMESPACE \
            -f ./helm/override-configs/values-prod.yaml \
            --set namespace=$NAMESPACE \
            --set image.tag=$ENV; then
            echo -e "${GREEN}✅ Helm部署成功${NC}"
        else
            echo -e "${RED}❌ Helm部署失败!${NC}"
            exit 1
        fi
    else
        # 非生产环境使用kubectl
        echo -e "${YELLOW}使用kubectl部署到$ENV环境...${NC}"
        
        # 创建部署配置
        cat > deploy-$ENV.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-graph-service
  namespace: $NAMESPACE
  labels:
    app: knowledge-graph-service
    environment: $ENV
spec:
  replicas: 1
  selector:
    matchLabels:
      app: knowledge-graph-service
  template:
    metadata:
      labels:
        app: knowledge-graph-service
        environment: $ENV
    spec:
      containers:
      - name: knowledge-graph-service
        image: knowledge-graph-service:$ENV
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
          value: "$ENV"
        envFrom:
        - configMapRef:
            name: knowledge-graph-config
        - secretRef:
            name: knowledge-graph-secrets
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
  namespace: $NAMESPACE
  labels:
    app: knowledge-graph-service
    environment: $ENV
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
        
        # 应用部署
        if kubectl apply -f deploy-$ENV.yaml; then
            echo -e "${GREEN}✅ 部署成功${NC}"
            rm deploy-$ENV.yaml
        else
            echo -e "${RED}❌ 部署失败!${NC}"
            exit 1
        fi
    fi
}

# 设置监控
setup_monitoring() {
    echo -e "\n${BLUE}设置监控...${NC}"
    
    # 使用监控设置脚本
    if [ -f "./scripts/setup-monitoring.sh" ]; then
        chmod +x ./scripts/setup-monitoring.sh
        ./scripts/setup-monitoring.sh setup $NAMESPACE
    else
        echo -e "${YELLOW}⚠️ 监控设置脚本不存在，跳过监控设置${NC}"
    fi
}

# 验证部署
verify_deployment() {
    echo -e "\n${BLUE}验证部署...${NC}"
    
    # 等待部署就绪
    echo -e "${YELLOW}等待部署就绪...${NC}"
    if kubectl rollout status deployment/knowledge-graph-service -n $NAMESPACE --timeout=120s; then
        echo -e "${GREEN}✅ 部署已就绪${NC}"
    else
        echo -e "${RED}❌ 部署未在指定时间内就绪!${NC}"
        echo -e "${YELLOW}请检查Pod状态:${NC}"
        kubectl get pods -n $NAMESPACE -l app=knowledge-graph-service
        exit 1
    fi
    
    # 显示Pod状态
    echo -e "\n${BLUE}Pod状态:${NC}"
    kubectl get pods -n $NAMESPACE -l app=knowledge-graph-service
    
    # 显示服务状态
    echo -e "\n${BLUE}服务状态:${NC}"
    kubectl get svc -n $NAMESPACE knowledge-graph-service
    
    # 设置端口转发并检查健康状态
    echo -e "\n${BLUE}检查健康状态...${NC}"
    kubectl port-forward -n $NAMESPACE svc/knowledge-graph-service 8080:8080 &
    PF_PID=$!
    
    # 等待端口转发建立
    sleep 3
    
    # 检查健康状态
    if curl -s http://localhost:8080/health | grep -q "ok"; then
        echo -e "${GREEN}✅ 服务健康状态正常${NC}"
    else
        echo -e "${RED}❌ 服务健康状态异常!${NC}"
    fi
    
    # 清理端口转发
    kill $PF_PID 2>/dev/null
}

# 显示部署信息
show_deployment_info() {
    echo -e "\n${BLUE}部署信息:${NC}"
    echo -e "${YELLOW}环境: $ENV${NC}"
    echo -e "${YELLOW}命名空间: $NAMESPACE${NC}"
    echo -e "${YELLOW}服务URL: http://knowledge-graph-service.$NAMESPACE.svc.cluster.local:8080${NC}"
    
    # 显示访问方法
    echo -e "\n${BLUE}访问服务:${NC}"
    echo -e "${YELLOW}1. 使用端口转发:${NC}"
    echo -e "   kubectl port-forward -n $NAMESPACE svc/knowledge-graph-service 8080:8080"
    echo -e "   然后访问: http://localhost:8080"
    
    echo -e "\n${YELLOW}2. 使用集群内部URL:${NC}"
    echo -e "   http://knowledge-graph-service.$NAMESPACE.svc.cluster.local:8080"
    
    if [ "$ENV" == "prod" ]; then
        echo -e "\n${YELLOW}3. 使用Ingress (如果已配置):${NC}"
        echo -e "   https://kg.suoke.life"
    fi
    
    # 显示常用命令
    echo -e "\n${BLUE}常用命令:${NC}"
    echo -e "${YELLOW}查看日志:${NC}"
    echo -e "   kubectl logs -f -n $NAMESPACE -l app=knowledge-graph-service"
    
    echo -e "\n${YELLOW}查看Pod状态:${NC}"
    echo -e "   kubectl get pods -n $NAMESPACE -l app=knowledge-graph-service"
    
    echo -e "\n${YELLOW}查看服务指标:${NC}"
    echo -e "   ./scripts/setup-monitoring.sh metrics $NAMESPACE"
    
    echo -e "\n${YELLOW}更新配置:${NC}"
    echo -e "   ./scripts/manage-configs.sh update $ENV $NAMESPACE"
    echo -e "   ./scripts/manage-configs.sh apply $ENV $NAMESPACE"
}

# 主流程
main() {
    echo -e "${BLUE}开始部署索克生活知识图谱服务...${NC}"
    echo -e "${YELLOW}环境: $ENV${NC}"
    echo -e "${YELLOW}命名空间: $NAMESPACE${NC}"
    
    # 检查工具
    check_tools
    
    # 构建镜像
    build_image
    
    # 创建配置
    create_configs
    
    # 部署应用
    deploy_app
    
    # 设置监控
    setup_monitoring
    
    # 验证部署
    verify_deployment
    
    # 显示部署信息
    show_deployment_info
    
    echo -e "\n${GREEN}✅ 部署完成!${NC}"
    echo -e "${BLUE}=========================================${NC}"
}

# 执行主流程
main
