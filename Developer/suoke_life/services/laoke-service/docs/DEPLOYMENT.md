# 老克服务部署指南

## 1. 环境要求

- Node.js 18+
- MongoDB 5.0+
- Redis 6.0+
- 容器环境: Docker 20.10+ 或 Kubernetes 1.24+

## 2. 本地开发环境

### 2.1 环境准备

1. 克隆代码库
```bash
git clone https://github.com/your-org/suoke_life.git
cd suoke_life/services/laoke-service
```

2. 安装依赖
```bash
npm install
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

4. 启动开发服务器
```bash
npm run dev
```

### 2.2 本地测试

```bash
# 运行单元测试
npm test

# 运行特定测试
npm test -- -t "数据库连接模块"

# 生成测试覆盖率报告
npm test -- --coverage
```

## 3. Docker部署

### 3.1 构建Docker镜像

```bash
docker build -t laoke-service:1.0.0 .
```

### 3.2 运行Docker容器

```bash
docker run -d --name laoke-service \
  -p 3012:3012 \
  -p 9465:9465 \
  --env-file .env \
  laoke-service:1.0.0
```

### 3.3 查看日志

```bash
docker logs -f laoke-service
```

## 4. Kubernetes部署

### 4.1 配置文件

在项目根目录下创建Kubernetes配置文件目录:

```bash
mkdir -p k8s/base k8s/overlays/dev k8s/overlays/prod
```

### 4.2 创建基础配置

**k8s/base/deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: laoke-service
  labels:
    app: laoke-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: laoke-service
  template:
    metadata:
      labels:
        app: laoke-service
    spec:
      containers:
      - name: laoke-service
        image: ${IMAGE_NAME}:${IMAGE_TAG}
        ports:
        - containerPort: 3012
          name: http
        - containerPort: 9465
          name: metrics
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
        env:
        - name: NODE_ENV
          value: production
        - name: PORT
          value: "3012"
        envFrom:
        - configMapRef:
            name: laoke-service-configmap
        - secretRef:
            name: laoke-service-secrets
        readinessProbe:
          httpGet:
            path: /health/ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health/live
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
```

**k8s/base/service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: laoke-service
  labels:
    app: laoke-service
spec:
  ports:
  - port: 80
    targetPort: 3012
    name: http
  - port: 9465
    targetPort: 9465
    name: metrics
  selector:
    app: laoke-service
```

**k8s/base/configmap.yaml**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: laoke-service-configmap
data:
  API_VERSION: v1
  SERVICE_NAME: laoke-service
  LOG_LEVEL: info
  METRICS_PORT: "9465"
  METRICS_PATH: /metrics
  HEALTH_CHECK_PATH: /health
```

**k8s/base/kustomization.yaml**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
- configmap.yaml
```

### 4.3 创建环境特定配置

**k8s/overlays/dev/kustomization.yaml**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
patchesStrategicMerge:
- deployment-patch.yaml
configMapGenerator:
- name: laoke-service-configmap
  behavior: merge
  literals:
  - NODE_ENV=development
  - LOG_LEVEL=debug
images:
- name: ${IMAGE_NAME}
  newName: suoke/laoke-service
  newTag: latest
```

**k8s/overlays/prod/kustomization.yaml**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
patchesStrategicMerge:
- deployment-patch.yaml
- hpa.yaml
configMapGenerator:
- name: laoke-service-configmap
  behavior: merge
  literals:
  - NODE_ENV=production
  - LOG_LEVEL=info
images:
- name: ${IMAGE_NAME}
  newName: suoke/laoke-service
  newTag: 1.0.0
```

**k8s/overlays/prod/hpa.yaml**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: laoke-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: laoke-service
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 4.4 部署到Kubernetes

```bash
# 开发环境部署
kubectl apply -k k8s/overlays/dev

# 生产环境部署
kubectl apply -k k8s/overlays/prod
```

## 5. 环境变量配置说明

| 变量名 | 描述 | 默认值 | 是否必需 |
|--------|------|--------|----------|
| NODE_ENV | 运行环境 | development | 是 |
| PORT | HTTP服务端口 | 3012 | 是 |
| METRICS_PORT | 指标监控端口 | 9465 | 是 |
| MONGO_URI | MongoDB连接字符串 | mongodb://localhost:27017/laoke_service | 是 |
| REDIS_URI | Redis连接字符串 | redis://localhost:6379 | 是 |
| LOG_LEVEL | 日志级别 | info | 否 |
| JWT_SECRET | JWT密钥 | - | 是 |
| AI_MODEL_ENDPOINT | AI模型服务端点 | - | 是 |
| AI_MODEL_API_KEY | AI模型API密钥 | - | 是 |

## 6. 监控与日志

### 6.1 Prometheus集成

服务在`/metrics`端点暴露Prometheus指标，可以配置Prometheus服务抓取这些指标。

**prometheus.yaml配置示例**:
```yaml
scrape_configs:
  - job_name: 'laoke-service'
    scrape_interval: 15s
    static_configs:
      - targets: ['laoke-service:9465']
```

### 6.2 日志收集

服务日志输出到标准输出，可以使用Kubernetes日志收集解决方案进行收集。

**EFK配置示例**:
```yaml
apiVersion: logging.banzaicloud.io/v1beta1
kind: Flow
metadata:
  name: laoke-service-logs
spec:
  filters:
    - parser:
        reserve_data: true
        parse:
          type: json
  match:
    - select:
        labels:
          app: laoke-service
  localOutputRefs:
    - elasticsearch-output
```

## 7. 故障排除

### 7.1 常见问题

1. **服务无法启动**: 检查MongoDB和Redis连接是否正常
   ```bash
   kubectl logs -l app=laoke-service
   ```

2. **API请求失败**: 检查服务网络配置
   ```bash
   kubectl exec -it <任意pod> -- curl laoke-service/health/live
   ```

3. **性能问题**: 检查资源使用情况
   ```bash
   kubectl top pods -l app=laoke-service
   ```

### 7.2 联系支持

如遇到无法解决的问题，请联系技术支持团队:
- Email: support@suoke.life
- 内部工单: https://jira.suoke.life 