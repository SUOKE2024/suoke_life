# 消息总线服务部署指南

本文档提供了在不同环境中部署消息总线服务的详细说明。

## 目录

- [部署前提](#部署前提)
- [环境配置](#环境配置)
- [本地开发部署](#本地开发部署)
- [Docker部署](#docker部署)
- [Kubernetes部署](#kubernetes部署)
- [配置项说明](#配置项说明)
- [安全配置](#安全配置)
- [监控配置](#监控配置)
- [常见问题](#常见问题)

## 部署前提

### 基础要求

- Python 3.9 或更高版本
- 访问Kafka集群
- 访问Redis服务器(生产环境)
- 足够的磁盘空间用于日志和数据存储

### 依赖服务

- **Kafka**: 用于消息存储和传输
- **Redis**: 用于主题管理(生产环境)
- **认证服务**: 如果启用了安全认证特性

## 环境配置

消息总线服务支持以下环境:

- `development`: 开发环境，使用文件系统作为主题存储
- `testing`: 测试环境，使用文件系统作为主题存储，增强日志输出
- `staging`: 预发布环境，使用Redis作为主题存储
- `production`: 生产环境，使用Redis作为主题存储，启用安全功能

通过环境变量`ENVIRONMENT`设置当前环境，例如:

```bash
export ENVIRONMENT=production
```

## 本地开发部署

### 步骤1: 准备环境

```bash
# 克隆代码库
git clone <repository-url>
cd services/message-bus

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 步骤2: 生成gRPC代码

```bash
python scripts/generate_grpc.py
```

### 步骤3: 配置环境变量

创建`.env.development`配置文件:

```ini
# 服务器配置
SERVER__HOST=0.0.0.0
SERVER__PORT=50051

# Kafka配置
KAFKA__BOOTSTRAP_SERVERS=localhost:9092

# 日志配置
LOGGING__LEVEL=DEBUG
LOGGING__FORMAT=json
```

### 步骤4: 启动服务

```bash
python -m cmd.server.main
```

服务将在`localhost:50051`启动。

## Docker部署

### 步骤1: 构建Docker镜像

```bash
docker build -t suoke-life/message-bus:latest -f deploy/docker/Dockerfile .
```

### 步骤2: 运行容器

```bash
docker run -d --name message-bus \
  -p 50051:50051 \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e KAFKA__BOOTSTRAP_SERVERS=kafka:9092 \
  -e REDIS__HOST=redis \
  -e REDIS__PASSWORD=your-redis-password \
  -e ENABLE_AUTH=false \
  suoke-life/message-bus:latest
```

### Docker Compose示例

创建`docker-compose.yml`文件:

```yaml
version: '3'

services:
  message-bus:
    image: suoke-life/message-bus:latest
    ports:
      - "50051:50051"
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - KAFKA__BOOTSTRAP_SERVERS=kafka:9092
      - REDIS__HOST=redis
      - REDIS__PASSWORD=your-redis-password
      - ENABLE_AUTH=false
    depends_on:
      - kafka
      - redis
    restart: always
    volumes:
      - ./logs:/app/logs

  kafka:
    image: confluentinc/cp-kafka:7.3.2
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
      - KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
      # 更多Kafka配置...

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    command: redis-server --requirepass your-redis-password
```

启动:

```bash
docker-compose up -d
```

## Kubernetes部署

### 步骤1: 准备部署文件

已在项目中提供了`deploy/kubernetes/deployment.yaml`文件。

### 步骤2: 创建ConfigMap和Secret

```bash
# 创建ConfigMap
kubectl create configmap message-bus-config \
  --from-literal=environment=production \
  --from-literal=kafka_bootstrap_servers=kafka-0.kafka-headless.kafka.svc.cluster.local:9092 \
  --from-literal=redis_host=redis-master.redis.svc.cluster.local \
  --from-literal=redis_port=6379

# 创建Secret
kubectl create secret generic message-bus-secrets \
  --from-literal=redis_password=$(echo -n "your-redis-password" | base64)
```

### 步骤3: 部署服务

```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
```

### 步骤4: 验证部署

```bash
kubectl get pods -l app=message-bus
```

## 配置项说明

消息总线服务支持以下配置项:

### 服务器配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|----------|-------|------|
| 主机地址 | SERVER__HOST | 0.0.0.0 | 服务绑定的IP地址 |
| 端口号 | SERVER__PORT | 50051 | 服务监听的端口号 |
| 工作线程数 | SERVER__MAX_WORKERS | 10 | gRPC服务器工作线程数 |
| 超时时间 | SERVER__TIMEOUT_SECONDS | 60 | 请求超时时间(秒) |

### Kafka配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|----------|-------|------|
| 服务器地址 | KAFKA__BOOTSTRAP_SERVERS | localhost:9092 | Kafka服务器地址，多个地址用逗号分隔 |
| 主题前缀 | KAFKA__TOPIC_PREFIX | suoke- | Kafka主题前缀 |
| 自动创建主题 | KAFKA__AUTO_CREATE_TOPICS | true | 是否自动创建不存在的主题 |
| 分区数量 | KAFKA__NUM_PARTITIONS | 3 | 创建主题的默认分区数 |

### Redis配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|----------|-------|------|
| 主机地址 | REDIS__HOST | localhost | Redis服务器地址 |
| 端口号 | REDIS__PORT | 6379 | Redis服务器端口 |
| 数据库索引 | REDIS__DB | 0 | Redis数据库索引 |
| 密码 | REDIS__PASSWORD | 无 | Redis密码 |
| 使用SSL | REDIS__USE_SSL | false | 是否使用SSL连接Redis |

### 日志配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|----------|-------|------|
| 日志级别 | LOGGING__LEVEL | INFO | 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| 日志格式 | LOGGING__FORMAT | json | 日志格式: json 或 text |
| 日志文件 | LOGGING__LOG_FILE | 无 | 日志文件路径，不设置则只输出到控制台 |

### 指标配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|----------|-------|------|
| 启用指标 | METRICS__ENABLED | true | 是否启用Prometheus指标 |
| 指标主机地址 | METRICS__HOST | 0.0.0.0 | 指标服务绑定的IP地址 |
| 指标端口号 | METRICS__PORT | 8000 | 指标服务监听的端口号 |

### 安全配置

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|----------|-------|------|
| 启用认证 | ENABLE_AUTH | false | 是否启用认证 |
| 认证服务URL | AUTH_SERVICE_URL | 无 | 认证服务的URL |
| 认证公钥 | AUTH_PUBLIC_KEY | 无 | JWT验证公钥(可选) |

## 安全配置

### 步骤1: 启用认证

在部署时设置环境变量:

```bash
export ENABLE_AUTH=true
export AUTH_SERVICE_URL=https://auth.suoke-life.com
```

### 步骤2: 配置TLS (生产环境)

在生产环境中，强烈建议启用TLS加密。

在Kubernetes中使用cert-manager创建证书:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: message-bus-tls
  namespace: suoke-life
spec:
  secretName: message-bus-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - message-bus.suoke-life.com
```

然后在服务中使用:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: message-bus
  namespace: suoke-life
spec:
  ports:
  - name: grpc
    port: 50051
    targetPort: 50051
  selector:
    app: message-bus
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: message-bus-ingress
  namespace: suoke-life
  annotations:
    nginx.ingress.kubernetes.io/backend-protocol: "GRPC"
spec:
  tls:
  - hosts:
    - message-bus.suoke-life.com
    secretName: message-bus-tls
  rules:
  - host: message-bus.suoke-life.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: message-bus
            port:
              number: 50051
```

## 监控配置

### Prometheus集成

服务自动在`http://<host>:8000/metrics`端点提供Prometheus指标。

在Prometheus配置中添加:

```yaml
scrape_configs:
  - job_name: 'message-bus'
    scrape_interval: 15s
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: message-bus
      - source_labels: [__address__]
        action: replace
        regex: ([^:]+)(?::\d+)?
        replacement: ${1}:8000
        target_label: __address__
```

### Grafana仪表板

在`deploy/grafana/dashboards`目录中提供了Grafana仪表板JSON文件，可以导入到Grafana中。

## 常见问题

### Q: 服务启动失败，无法连接到Kafka
**A**: 检查Kafka连接配置是否正确，确保服务器可以访问Kafka集群。可以使用以下命令测试连接:
```bash
nc -zv <kafka-host> <kafka-port>
```

### Q: Redis连接错误
**A**: 检查Redis连接配置，特别是密码和TLS设置。确保Redis服务器允许远程连接。

### Q: 认证失败
**A**: 首先检查`AUTH_SERVICE_URL`是否正确。然后确认JWT令牌是否有效，以及验证密钥是否正确配置。

### Q: 性能问题
**A**: 检查以下几点:
1. Kafka分区数量是否足够
2. gRPC服务器的工作线程数是否足够
3. 监控系统资源使用情况，确保CPU和内存充足

### Q: 日志文件未生成
**A**: 确保`LOGGING__LOG_FILE`配置了有效路径，并且服务有权限写入该路径。