# Corn Maze Service 部署指南

本文档提供 Corn Maze Service 的部署说明，包括本地开发环境、Docker 容器和 Kubernetes 集群部署方式。

## 目录

- [前置条件](#前置条件)
- [本地开发环境部署](#本地开发环境部署)
- [Docker 容器部署](#docker-容器部署)
- [Kubernetes 集群部署](#kubernetes-集群部署)
- [配置参数](#配置参数)
- [监控和日志](#监控和日志)
- [数据持久化](#数据持久化)
- [安全注意事项](#安全注意事项)
- [故障恢复](#故障恢复)

## 前置条件

### 环境要求

- Python 3.8+
- Docker 19.03+ (容器部署)
- Kubernetes 1.18+ (集群部署)
- MongoDB 4.4+ (数据存储)
- Redis 6.0+ (可选，用于缓存)

### 依赖服务

- MongoDB: 用于存储迷宫、用户进度和知识库数据
- Redis (可选): 用于缓存和速率限制
- Prometheus (可选): 用于指标监控
- Grafana (可选): 用于可视化监控数据

## 本地开发环境部署

1. 克隆代码库并进入目录

```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd corn-maze-service
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量

```bash
# Linux/macOS
export MONGODB_URI="mongodb://localhost:27017/cornmaze"
export GRPC_PORT=50057
export LOG_LEVEL=INFO

# Windows
set MONGODB_URI=mongodb://localhost:27017/cornmaze
set GRPC_PORT=50057
set LOG_LEVEL=INFO
```

4. 启动服务

```bash
python cmd/server/main.py
```

## Docker 容器部署

1. 构建 Docker 镜像

```bash
docker build -t corn-maze-service:latest .
```

2. 运行容器

```bash
docker run -d \
  --name corn-maze-service \
  -p 50057:50057 \
  -p 51057:51057 \
  -e MONGODB_URI="mongodb://mongo:27017/cornmaze" \
  -e GRPC_PORT=50057 \
  -e LOG_LEVEL=INFO \
  --network app-network \
  corn-maze-service:latest
```

### 使用 Docker Compose

可以使用 Docker Compose 配置并启动整个应用堆栈：

```bash
docker-compose -f deploy/docker-compose.yml up -d
```

## Kubernetes 集群部署

本服务提供了完整的 Kubernetes 部署配置。

1. 应用 Kubernetes 配置

```bash
kubectl apply -f deploy/kubernetes/namespace.yaml
kubectl apply -f deploy/kubernetes/configmap.yaml
kubectl apply -f deploy/kubernetes/secret.yaml
kubectl apply -f deploy/kubernetes/deployment.yaml
kubectl apply -f deploy/kubernetes/service.yaml
```

2. 检查部署状态

```bash
kubectl get pods -n suoke-life
kubectl get services -n suoke-life
```

### Helm 部署 (可选)

如果使用 Helm 进行部署，可以：

```bash
helm install corn-maze-service ./deploy/helm/corn-maze-service
```

## 配置参数

### 核心配置参数

| 参数名 | 描述 | 默认值 | 是否必需 |
|-------|------|-------|---------|
| MONGODB_URI | MongoDB 连接 URI | mongodb://localhost:27017/cornmaze | 是 |
| GRPC_PORT | gRPC 服务端口 | 50057 | 是 |
| METRICS_PORT | 指标监控端口 | 51057 | 否 |
| LOG_LEVEL | 日志级别 | INFO | 否 |
| MAX_MAZE_SIZE | 最大迷宫尺寸 | 30 | 否 |
| DEFAULT_DIFFICULTY | 默认难度级别 | 2 | 否 |
| ENABLE_CACHE | 是否开启缓存 | false | 否 |
| REDIS_URI | Redis 连接 URI | redis://localhost:6379/0 | 仅当 ENABLE_CACHE=true 时必需 |

### 配置文件

除了环境变量，还可以使用配置文件。服务按以下顺序加载配置：

1. 内置默认值
2. 配置文件 (`config/config.yaml`)
3. 环境变量 (优先级最高)

配置文件示例：

```yaml
mongodb:
  uri: mongodb://localhost:27017/cornmaze
  poolSize: 10
  connectTimeout: 5000

grpc:
  port: 50057
  maxWorkers: 10

metrics:
  enabled: true
  port: 51057

logging:
  level: INFO
  file: logs/corn-maze.log
  
maze:
  maxSize: 30
  defaultDifficulty: 2
  
cache:
  enabled: false
  redis_uri: redis://localhost:6379/0
  ttl: 3600
```

## 监控和日志

### 日志

日志默认输出到标准输出和错误输出。在生产环境中，可配置将日志写入文件。

```yaml
logging:
  level: INFO
  file: logs/corn-maze.log
  rotation: daily
  retention: 30
```

### 监控指标

服务使用 Prometheus 监控指标，默认暴露在 `/metrics` 端点。主要指标包括：

- `maze_creation_duration_seconds`: 迷宫创建耗时
- `maze_requests_total`: 按类型统计的请求总数
- `active_mazes`: 活跃迷宫数
- `user_progress_updates`: 用户进度更新次数
- `http_request_duration_seconds`: API请求持续时间
- `http_requests_total`: 总HTTP请求数量

### Grafana 仪表板

在 `deploy/grafana/dashboards` 目录中提供了预配置的 Grafana 仪表板，可用于可视化服务指标。

## 数据持久化

### MongoDB 数据备份

定期备份 MongoDB 数据是保证服务可靠性的关键。以下是备份脚本示例：

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/mongodb/$DATE"

mkdir -p $BACKUP_DIR
mongodump --uri "$MONGODB_URI" --out $BACKUP_DIR

# 保留最近30天的备份
find /backup/mongodb -type d -mtime +30 -exec rm -rf {} \;
```

## 安全注意事项

### 网络安全

- 在生产环境中，使用 TLS/SSL 加密 gRPC 连接
- 使用网络策略限制服务访问
- 确保 MongoDB 和 Redis 实例受到适当保护，不对外暴露

### 配置安全

- 不要在代码中硬编码敏感信息
- 使用 Kubernetes Secret 或环境变量管理敏感配置
- 定期轮换密钥和凭证

## 故障恢复

### 常见问题排查

1. **服务启动失败**
   - 检查日志中的错误信息
   - 验证 MongoDB 连接是否正常
   - 检查端口是否被占用

2. **性能问题**
   - 检查 MongoDB 查询性能
   - 考虑启用 Redis 缓存
   - 优化迷宫生成算法参数

3. **内存泄漏**
   - 监控容器内存使用
   - 检查长时间运行的请求
   - 考虑设置资源限制

### 灾难恢复计划

1. 保持最新的数据备份
2. 记录配置更改
3. 准备回滚计划
4. 定期测试恢复流程

## 部署检查清单

- [ ] 配置正确的 MongoDB 连接参数
- [ ] 设置适当的资源限制
- [ ] 启用监控和告警
- [ ] 配置日志记录
- [ ] 测试 gRPC 端点可访问性
- [ ] 验证指标端点正常
- [ ] 确保安全配置已应用 