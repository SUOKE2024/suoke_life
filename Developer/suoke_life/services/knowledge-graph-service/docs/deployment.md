# 索克生活知识图谱服务部署指南

本文档提供索克生活知识图谱服务的部署说明，包括本地开发环境、Docker容器和Kubernetes集群部署方法。

## 环境要求

- Go 1.20+
- Neo4j 4.4+
- Redis 6.0+
- Milvus 2.1+（可选，用于向量搜索）

## 本地开发环境部署

### 1. 克隆代码仓库

```bash
git clone https://github.com/suoke-life/knowledge-graph-service.git
cd knowledge-graph-service
```

### 2. 配置环境变量

```bash
cp configs/config.example.yaml configs/config.local.yaml
# 编辑config.local.yaml文件设置本地配置
```

主要配置项：

```yaml
environment: development  # 环境：development, testing, production
server:
  port: 8080
  timeout: 30s
database:
  neo4j:
    uri: bolt://localhost:7687
    username: neo4j
    password: password
    database: neo4j
  redis:
    host: localhost
    port: 6379
    password: ""
    db: 0
vector_db:
  enabled: false
  uri: localhost:19530
  username: root
  password: milvus
logging:
  level: debug
  format: console
```

### 3. 启动依赖服务

可以使用Docker Compose启动依赖服务：

```bash
docker-compose -f docker-compose.dev.yaml up -d
```

### 4. 构建和运行服务

```bash
# 构建服务
go build -o bin/kg-service ./cmd/server

# 运行服务
./bin/kg-service
```

服务将默认在 http://localhost:8080 上运行。

## Docker容器部署

### 1. 构建Docker镜像

```bash
docker build -f Dockerfile.go -t knowledge-graph-service:latest .
```

### 2. 运行Docker容器

```bash
docker run -d --name knowledge-graph-service \
  -p 8080:8080 \
  -e DB_NEO4J_URI=bolt://neo4j:7687 \
  -e DB_NEO4J_USERNAME=neo4j \
  -e DB_NEO4J_PASSWORD=password \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  -e LOG_LEVEL=info \
  -v $(pwd)/data:/app/data \
  --network suoke-network \
  knowledge-graph-service:latest
```

## Kubernetes集群部署

知识图谱服务支持在Kubernetes集群中部署，并提供通过Helm Chart和kustomize两种部署方式。

### 使用Helm部署

```bash
# 添加Helm仓库
helm repo add suoke https://suoke-life.github.io/helm-charts/
helm repo update

# 创建配置值文件（替换为实际配置）
cat > values.yaml << EOF
image:
  repository: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service-go
  tag: latest
  pullPolicy: Always

config:
  logLevel: info
  logFormat: json

neo4j:
  uri: bolt://neo4j-service:7687
  username: neo4j
  # 密码通过Secret注入

redis:
  host: redis-master
  port: 6379
  # 密码通过Secret注入

resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 2Gi

persistence:
  data:
    enabled: true
    size: 10Gi
  models:
    enabled: true
    size: 5Gi
EOF

# 部署服务
helm install knowledge-graph-service suoke/knowledge-graph-service -f values.yaml -n suoke
```

### 使用kustomize部署

项目仓库中包含了完整的kustomize配置：

```bash
# 直接应用base配置
kubectl apply -k k8s/base

# 或者使用特定环境的overlay
kubectl apply -k k8s/overlays/production
```

## 配置项说明

| 环境变量 | 描述 | 默认值 |
|---------|------|-------|
| `ENV` | 运行环境 | `development` |
| `LOG_LEVEL` | 日志级别 | `info` |
| `LOG_FORMAT` | 日志格式 (console, json) | `console` |
| `SERVER_PORT` | 服务端口 | `8080` |
| `DB_NEO4J_URI` | Neo4j连接URI | `bolt://localhost:7687` |
| `DB_NEO4J_USERNAME` | Neo4j用户名 | `neo4j` |
| `DB_NEO4J_PASSWORD` | Neo4j密码 | - |
| `DB_NEO4J_DATABASE` | Neo4j数据库名 | `neo4j` |
| `REDIS_HOST` | Redis主机地址 | `localhost` |
| `REDIS_PORT` | Redis端口 | `6379` |
| `REDIS_PASSWORD` | Redis密码 | - |
| `MILVUS_URI` | Milvus URI | `localhost:19530` |
| `MILVUS_USERNAME` | Milvus用户名 | `root` |
| `MILVUS_PASSWORD` | Milvus密码 | - |
| `API_KEY` | API访问密钥 | - |

## 健康检查

服务提供了健康检查端点：

```
GET /health
```

响应示例：

```json
{
  "status": "ok",
  "version": "1.0.0",
  "dependencies": {
    "neo4j": "connected",
    "redis": "connected",
    "milvus": "connected"
  },
  "uptime": 86400
}
```

## 资源要求

推荐的资源配置：

- 最小配置：1 CPU核心，512MB内存
- 推荐配置：2 CPU核心，2GB内存
- 生产环境：4 CPU核心，4GB内存

## 部署后验证

部署完成后，可以通过以下方式验证服务是否正常运行：

```bash
# 检查服务健康状态
curl http://localhost:8080/health

# 尝试API调用（需要提供API密钥）
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8080/api/v1/nodes?limit=10
```

## 日志和监控

服务支持以下监控接口：

- 健康检查：`/health`
- Prometheus指标：`/metrics`
- 可观测性：支持OpenTelemetry导出到Jaeger/Tempo

## 备份和恢复

### 数据备份

```bash
# 使用提供的备份脚本
./scripts/backup.sh

# 或使用Neo4j自带的备份工具
neo4j-admin backup --backup-dir=/backups --database=neo4j
```

### 数据恢复

```bash
# 使用提供的恢复脚本
./scripts/restore.sh <backup-file>

# 或使用Neo4j自带的恢复工具
neo4j-admin restore --from=/backups/latest --database=neo4j
```

## 故障排除

常见问题：

1. **无法连接到Neo4j**：检查Neo4j连接URI、用户名和密码是否正确，Neo4j服务是否在运行。

2. **API返回401错误**：检查API密钥是否正确配置和传递。

3. **内存使用过高**：调整JVM内存设置，检查是否有内存泄漏问题。

4. **服务启动失败**：检查日志，确保所有依赖服务都已启动且配置正确。

5. **导入数据失败**：检查导入数据格式，确保符合要求，查看详细错误日志。

## 扩展配置

### 启用TLS

编辑配置文件，启用TLS：

```yaml
server:
  tls:
    enabled: true
    cert_file: /path/to/cert.pem
    key_file: /path/to/key.pem
```

### 配置认证

编辑配置文件，设置认证：

```yaml
auth:
  enabled: true
  api_key: YOUR_API_KEY
  jwt:
    enabled: false
    secret: YOUR_JWT_SECRET
```

### 集成Milvus向量数据库

编辑配置文件，启用Milvus：

```yaml
vector_db:
  enabled: true
  uri: localhost:19530
  username: root
  password: milvus
  collection_prefix: kg_
``` 