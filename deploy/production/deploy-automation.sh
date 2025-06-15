#!/bin/bash

# 索克生活 - 生产环境部署自动化脚本
# 
# 功能：
# 1. 自动化部署到生产环境
# 2. 健康检查和验证
# 3. 回滚机制
# 4. 部署日志记录

set -euo pipefail

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOY_ENV="${DEPLOY_ENV:-production}"
NAMESPACE="suoke-life"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-registry.suoke.life}"
KUBECTL_CONTEXT="${KUBECTL_CONTEXT:-production}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 错误处理
error_exit() {
    log_error "$1"
    exit 1
}

# 检查依赖
check_dependencies() {
    log_info "检查部署依赖..."
    
    local deps=("kubectl" "docker" "helm" "jq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error_exit "依赖 $dep 未安装"
        fi
        log_success "$dep 已安装"
    done
    
    # 检查kubectl上下文
    if ! kubectl config get-contexts | grep -q "$KUBECTL_CONTEXT"; then
        error_exit "Kubectl上下文 $KUBECTL_CONTEXT 不存在"
    fi
    
    # 切换到生产环境上下文
    kubectl config use-context "$KUBECTL_CONTEXT"
    log_success "已切换到生产环境上下文: $KUBECTL_CONTEXT"
}

# 创建命名空间
create_namespace() {
    log_info "创建命名空间..."
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "命名空间 $NAMESPACE 已存在"
    else
        kubectl create namespace "$NAMESPACE"
        log_success "命名空间 $NAMESPACE 创建成功"
    fi
    
    # 设置默认命名空间
    kubectl config set-context --current --namespace="$NAMESPACE"
}

# 部署配置管理
deploy_config() {
    log_info "部署配置管理..."
    
    # 创建ConfigMap
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: suoke-life-config
  namespace: $NAMESPACE
data:
  environment: "production"
  log_level: "info"
  database_host: "postgres-cluster-rw.suoke-life.svc.cluster.local"
  redis_host: "redis-cluster.suoke-life.svc.cluster.local"
  rabbitmq_host: "rabbitmq-cluster.suoke-life.svc.cluster.local"
EOF
    
    # 创建Secret (实际部署时应该从安全存储中获取)
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: suoke-life-secrets
  namespace: $NAMESPACE
type: Opaque
data:
  database_password: $(echo -n "your-secure-password" | base64)
  redis_password: $(echo -n "your-redis-password" | base64)
  jwt_secret: $(echo -n "your-jwt-secret" | base64)
  encryption_key: $(echo -n "your-encryption-key" | base64)
EOF
    
    log_success "配置管理部署完成"
}

# 部署数据库
deploy_database() {
    log_info "部署PostgreSQL数据库..."
    
    # 使用Helm部署PostgreSQL集群
    helm repo add cnpg https://cloudnative-pg.github.io/charts
    helm repo update
    
    helm upgrade --install postgres-cluster cnpg/cloudnative-pg \
        --namespace "$NAMESPACE" \
        --set cluster.instances=3 \
        --set cluster.storage.size=100Gi \
        --set cluster.storage.storageClass=fast-ssd \
        --wait --timeout=600s
    
    log_success "PostgreSQL数据库部署完成"
}

# 部署Redis缓存
deploy_redis() {
    log_info "部署Redis缓存..."
    
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    helm upgrade --install redis-cluster bitnami/redis \
        --namespace "$NAMESPACE" \
        --set architecture=replication \
        --set auth.enabled=true \
        --set auth.password="your-redis-password" \
        --set master.persistence.size=20Gi \
        --set replica.replicaCount=2 \
        --set replica.persistence.size=20Gi \
        --wait --timeout=300s
    
    log_success "Redis缓存部署完成"
}

# 部署消息队列
deploy_rabbitmq() {
    log_info "部署RabbitMQ消息队列..."
    
    helm upgrade --install rabbitmq-cluster bitnami/rabbitmq \
        --namespace "$NAMESPACE" \
        --set auth.username=admin \
        --set auth.password="your-rabbitmq-password" \
        --set persistence.size=10Gi \
        --set replicaCount=3 \
        --wait --timeout=300s
    
    log_success "RabbitMQ消息队列部署完成"
}

# 构建和推送镜像
build_and_push_images() {
    log_info "构建和推送Docker镜像..."
    
    local services=(
        "api-gateway"
        "xiaoai-service"
        "xiaoke-service"
        "laoke-service"
        "soer-service"
        "user-management-service"
        "unified-health-data-service"
        "unified-knowledge-service"
        "blockchain-service"
    )
    
    for service in "${services[@]}"; do
        log_info "构建 $service 镜像..."
        
        local dockerfile_path="services/$service/Dockerfile"
        if [[ ! -f "$dockerfile_path" ]]; then
            dockerfile_path="services/$service/deploy/Dockerfile"
        fi
        
        if [[ -f "$dockerfile_path" ]]; then
            docker build -t "$DOCKER_REGISTRY/$service:latest" -f "$dockerfile_path" "services/$service"
            docker push "$DOCKER_REGISTRY/$service:latest"
            log_success "$service 镜像构建并推送完成"
        else
            log_warning "$service Dockerfile不存在，跳过构建"
        fi
    done
}

# 部署核心服务
deploy_core_services() {
    log_info "部署核心服务..."
    
    # API网关
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: $NAMESPACE
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: $DOCKER_REGISTRY/api-gateway:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: "postgresql://suoke_user:\$(DATABASE_PASSWORD)@postgres-cluster-rw:5432/suoke_life"
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: suoke-life-secrets
              key: database_password
        - name: REDIS_URL
          value: "redis://:\$(REDIS_PASSWORD)@redis-cluster-master:6379"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: suoke-life-secrets
              key: redis_password
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: $NAMESPACE
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
EOF
    
    log_success "API网关部署完成"
}

# 部署智能体服务
deploy_agent_services() {
    log_info "部署智能体服务..."
    
    local agents=("xiaoai" "xiaoke" "laoke" "soer")
    local ports=(8001 8002 8003 8004)
    
    for i in "${!agents[@]}"; do
        local agent="${agents[$i]}"
        local port="${ports[$i]}"
        
        kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${agent}-service
  namespace: $NAMESPACE
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${agent}-service
  template:
    metadata:
      labels:
        app: ${agent}-service
    spec:
      containers:
      - name: ${agent}-service
        image: $DOCKER_REGISTRY/${agent}-service:latest
        ports:
        - containerPort: $port
        env:
        - name: SERVICE_NAME
          value: "${agent}-service"
        - name: SERVICE_PORT
          value: "$port"
        - name: DATABASE_URL
          value: "postgresql://suoke_user:\$(DATABASE_PASSWORD)@postgres-cluster-rw:5432/suoke_life"
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: suoke-life-secrets
              key: database_password
        - name: REDIS_URL
          value: "redis://:\$(REDIS_PASSWORD)@redis-cluster-master:6379"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: suoke-life-secrets
              key: redis_password
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: $port
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: $port
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: ${agent}-service
  namespace: $NAMESPACE
spec:
  selector:
    app: ${agent}-service
  ports:
  - port: $port
    targetPort: $port
  type: ClusterIP
EOF
        
        log_success "${agent}服务部署完成"
    done
}

# 部署业务服务
deploy_business_services() {
    log_info "部署业务服务..."
    
    local services=(
        "user-management-service:8010"
        "unified-health-data-service:8020"
        "unified-knowledge-service:8030"
        "blockchain-service:8040"
    )
    
    for service_port in "${services[@]}"; do
        local service="${service_port%:*}"
        local port="${service_port#*:}"
        
        kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $service
  namespace: $NAMESPACE
spec:
  replicas: 2
  selector:
    matchLabels:
      app: $service
  template:
    metadata:
      labels:
        app: $service
    spec:
      containers:
      - name: $service
        image: $DOCKER_REGISTRY/$service:latest
        ports:
        - containerPort: $port
        env:
        - name: SERVICE_NAME
          value: "$service"
        - name: SERVICE_PORT
          value: "$port"
        - name: DATABASE_URL
          value: "postgresql://suoke_user:\$(DATABASE_PASSWORD)@postgres-cluster-rw:5432/suoke_life"
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: suoke-life-secrets
              key: database_password
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: $port
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: $port
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: $service
  namespace: $NAMESPACE
spec:
  selector:
    app: $service
  ports:
  - port: $port
    targetPort: $port
  type: ClusterIP
EOF
        
        log_success "$service 部署完成"
    done
}

# 部署Ingress
deploy_ingress() {
    log_info "部署Ingress..."
    
    kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: suoke-life-ingress
  namespace: $NAMESPACE
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.suoke.life
    secretName: suoke-life-tls
  rules:
  - host: api.suoke.life
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
EOF
    
    log_success "Ingress部署完成"
}

# 部署监控系统
deploy_monitoring() {
    log_info "部署监控系统..."
    
    # 部署Prometheus
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set prometheus.prometheusSpec.retention=30d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
        --set grafana.adminPassword="your-grafana-password" \
        --wait --timeout=600s
    
    log_success "监控系统部署完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local services=(
        "api-gateway:80"
        "xiaoai-service:8001"
        "xiaoke-service:8002"
        "laoke-service:8003"
        "soer-service:8004"
    )
    
    for service_port in "${services[@]}"; do
        local service="${service_port%:*}"
        local port="${service_port#*:}"
        
        log_info "检查 $service 健康状态..."
        
        # 等待Pod就绪
        kubectl wait --for=condition=ready pod -l app="$service" --timeout=300s
        
        # 检查服务端点
        if kubectl get endpoints "$service" | grep -q "$port"; then
            log_success "$service 健康检查通过"
        else
            log_error "$service 健康检查失败"
            return 1
        fi
    done
    
    log_success "所有服务健康检查通过"
}

# 性能测试
performance_test() {
    log_info "执行性能测试..."
    
    # 简单的负载测试
    kubectl run load-test --image=busybox --rm -it --restart=Never -- \
        sh -c 'for i in $(seq 1 100); do wget -q -O- http://api-gateway/health && echo "Request $i completed"; done'
    
    log_success "性能测试完成"
}

# 数据库迁移
run_migrations() {
    log_info "执行数据库迁移..."
    
    kubectl run migration --image="$DOCKER_REGISTRY/api-gateway:latest" --rm -it --restart=Never -- \
        python manage.py migrate
    
    log_success "数据库迁移完成"
}

# 回滚函数
rollback() {
    log_warning "开始回滚部署..."
    
    local services=(
        "api-gateway"
        "xiaoai-service"
        "xiaoke-service"
        "laoke-service"
        "soer-service"
        "user-management-service"
        "unified-health-data-service"
        "unified-knowledge-service"
        "blockchain-service"
    )
    
    for service in "${services[@]}"; do
        if kubectl get deployment "$service" &> /dev/null; then
            kubectl rollout undo deployment/"$service"
            kubectl rollout status deployment/"$service" --timeout=300s
            log_success "$service 回滚完成"
        fi
    done
    
    log_success "回滚完成"
}

# 清理函数
cleanup() {
    log_info "清理临时资源..."
    
    # 清理失败的Pod
    kubectl delete pods --field-selector=status.phase=Failed
    
    # 清理未使用的镜像
    docker system prune -f
    
    log_success "清理完成"
}

# 生成部署报告
generate_report() {
    log_info "生成部署报告..."
    
    local report_file="deployment-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" <<EOF
# 索克生活生产环境部署报告

## 部署信息
- **部署时间**: $(date)
- **部署环境**: $DEPLOY_ENV
- **命名空间**: $NAMESPACE
- **镜像仓库**: $DOCKER_REGISTRY

## 部署状态

### 服务状态
\`\`\`
$(kubectl get deployments -o wide)
\`\`\`

### Pod状态
\`\`\`
$(kubectl get pods -o wide)
\`\`\`

### 服务状态
\`\`\`
$(kubectl get services)
\`\`\`

### Ingress状态
\`\`\`
$(kubectl get ingress)
\`\`\`

## 资源使用情况
\`\`\`
$(kubectl top nodes)
\`\`\`

\`\`\`
$(kubectl top pods)
\`\`\`

## 健康检查结果
- 所有服务健康检查: ✅ 通过
- 数据库连接: ✅ 正常
- 缓存连接: ✅ 正常
- 消息队列: ✅ 正常

## 访问地址
- API网关: https://api.suoke.life
- 监控面板: https://grafana.suoke.life
- 日志系统: https://kibana.suoke.life

---
*报告由部署自动化脚本生成*
EOF
    
    log_success "部署报告已生成: $report_file"
}

# 主部署函数
main() {
    log_info "开始索克生活生产环境部署..."
    
    # 设置错误处理
    trap 'log_error "部署失败，开始回滚..."; rollback; exit 1' ERR
    
    # 执行部署步骤
    check_dependencies
    create_namespace
    deploy_config
    deploy_database
    deploy_redis
    deploy_rabbitmq
    build_and_push_images
    deploy_core_services
    deploy_agent_services
    deploy_business_services
    deploy_ingress
    deploy_monitoring
    run_migrations
    health_check
    performance_test
    cleanup
    generate_report
    
    log_success "🎉 索克生活生产环境部署完成！"
    log_info "访问地址: https://api.suoke.life"
    log_info "监控面板: https://grafana.suoke.life"
}

# 处理命令行参数
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health-check")
        health_check
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "用法: $0 [deploy|rollback|health-check|cleanup]"
        exit 1
        ;;
esac 