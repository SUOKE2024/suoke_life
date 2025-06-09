# 部署指南

## 生产环境部署

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.20+ (可选)
- 4GB+ RAM
- 2+ CPU cores

### 快速部署
```bash
# 1. 克隆项目
git clone https://github.com/suoke/suoke_life.git
cd suoke_life

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 启动服务
docker-compose -f deploy/production/docker-compose.production.yml up -d

# 4. 验证部署
curl http://localhost/health
```

### Kubernetes部署
```bash
kubectl apply -f deploy/production/kubernetes.yml
```

### 监控部署
```bash
# 启动监控服务
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# 访问Grafana
open http://localhost:3000
```

## 配置说明

### 环境变量
- `DATABASE_URL`: 数据库连接字符串
- `REDIS_URL`: Redis连接字符串
- `LOG_LEVEL`: 日志级别 (DEBUG/INFO/WARN/ERROR)
- `ENVIRONMENT`: 环境标识 (development/staging/production)

### 健康检查
所有服务都提供健康检查端点：
- `/health`: 基础健康检查
- `/ready`: 就绪状态检查
- `/metrics`: Prometheus指标
