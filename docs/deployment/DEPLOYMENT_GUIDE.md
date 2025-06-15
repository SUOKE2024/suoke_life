# 索克生活平台部署指南

## 概述

本指南详细介绍了如何在不同环境中部署索克生活平台，包括开发环境、测试环境和生产环境的完整部署流程。

## 系统要求

### 硬件要求

#### 开发环境
- **CPU**: 4核心以上
- **内存**: 16GB以上
- **存储**: 100GB可用空间
- **网络**: 稳定的互联网连接

#### 测试环境
- **CPU**: 8核心以上
- **内存**: 32GB以上
- **存储**: 500GB可用空间
- **网络**: 高速网络连接

#### 生产环境
- **CPU**: 16核心以上（推荐32核心）
- **内存**: 64GB以上（推荐128GB）
- **存储**: 2TB以上SSD存储
- **网络**: 企业级网络连接
- **负载均衡**: 支持高可用性

### 软件要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Kubernetes**: 1.24+ (生产环境)
- **Node.js**: 18.0+
- **Python**: 3.11+
- **PostgreSQL**: 15+
- **Redis**: 7.0+

## 部署架构

### 微服务架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        负载均衡器                              │
│                    (Nginx/HAProxy)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    API网关                                   │
│                 (Kong/Zuul)                                │
└─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┘
      │     │     │     │     │     │     │     │     │
      ▼     ▼     ▼     ▼     ▼     ▼     ▼     ▼     ▼
   ┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐
   │用户││健康││区块││通信││工具││小艾││小克││老克││索儿│
   │管理││数据││链  ││服务││服务││智能││智能││智能││智能│
   │服务││服务││服务││    ││    ││体  ││体  ││体  ││体  │
   └────┘└────┘└────┘└────┘└────┘└────┘└────┘└────┘└────┘
      │     │     │     │     │     │     │     │     │
      └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┐
                                                            │
┌─────────────────────────────────────────────────────────┴─┐
│                      数据层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PostgreSQL│  │   Redis  │  │Blockchain│  │   MinIO  │  │
│  │   主库   │  │   缓存   │  │   网络   │  │  对象存储 │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└───────────────────────────────────────────────────────────┘
```

## 环境准备

### 1. 安装Docker和Docker Compose

#### Ubuntu/Debian
```bash
# 更新包索引
sudo apt update

# 安装必要的包
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将用户添加到docker组
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS
```bash
# 使用Homebrew安装
brew install docker docker-compose

# 或者下载Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### 2. 克隆项目代码

```bash
git clone https://github.com/suoke-life/suoke-life.git
cd suoke-life
```

### 3. 环境配置

```bash
# 复制环境配置文件
cp env.example .env

# 编辑环境配置
nano .env
```

#### 环境变量配置示例

```bash
# 基础配置
NODE_ENV=production
API_VERSION=v1
PORT=8000

# 数据库配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=suoke_life
POSTGRES_USER=suoke_user
POSTGRES_PASSWORD=your_secure_password

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT配置
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=24h

# 区块链配置
BLOCKCHAIN_NETWORK=ethereum
BLOCKCHAIN_RPC_URL=https://mainnet.infura.io/v3/your_project_id
PRIVATE_KEY=your_private_key

# 对象存储配置
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

# 监控配置
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# 日志配置
LOG_LEVEL=info
LOG_FORMAT=json

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# 微信小程序配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# AI模型配置
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

## 部署方式

### 方式一：Docker Compose部署（推荐用于开发和测试）

#### 1. 快速启动

```bash
# 启动所有服务
docker-compose -f docker-compose.microservices.yml up -d

# 查看服务状态
docker-compose -f docker-compose.microservices.yml ps

# 查看日志
docker-compose -f docker-compose.microservices.yml logs -f
```

#### 2. 分步启动

```bash
# 1. 启动基础设施服务
docker-compose -f docker-compose.microservices.yml up -d postgres redis minio

# 等待数据库启动
sleep 30

# 2. 启动核心服务
docker-compose -f docker-compose.microservices.yml up -d api-gateway user-management-service unified-health-data-service

# 3. 启动智能体服务
docker-compose -f docker-compose.microservices.yml up -d xiaoai-service xiaoke-service laoke-service soer-service

# 4. 启动其他服务
docker-compose -f docker-compose.microservices.yml up -d blockchain-service communication-service utility-services

# 5. 启动监控服务
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

#### 3. 健康检查

```bash
# 运行健康检查脚本
./scripts/check-monitoring.sh

# 手动检查服务状态
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### 方式二：Kubernetes部署（推荐用于生产）

#### 1. 准备Kubernetes集群

```bash
# 安装kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 验证集群连接
kubectl cluster-info
kubectl get nodes
```

#### 2. 创建命名空间

```bash
# 创建生产环境命名空间
kubectl create namespace suoke-production

# 创建测试环境命名空间
kubectl create namespace suoke-staging
```

#### 3. 配置密钥

```bash
# 创建数据库密钥
kubectl create secret generic postgres-secret \
  --from-literal=username=suoke_user \
  --from-literal=password=your_secure_password \
  -n suoke-production

# 创建JWT密钥
kubectl create secret generic jwt-secret \
  --from-literal=secret=your_jwt_secret_key \
  -n suoke-production

# 创建区块链密钥
kubectl create secret generic blockchain-secret \
  --from-literal=private-key=your_private_key \
  --from-literal=rpc-url=https://mainnet.infura.io/v3/your_project_id \
  -n suoke-production
```

#### 4. 部署基础设施

```bash
# 部署PostgreSQL
kubectl apply -f k8s/production/postgres/ -n suoke-production

# 部署Redis
kubectl apply -f k8s/production/redis/ -n suoke-production

# 部署MinIO
kubectl apply -f k8s/production/minio/ -n suoke-production

# 等待基础设施就绪
kubectl wait --for=condition=ready pod -l app=postgres -n suoke-production --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n suoke-production --timeout=300s
```

#### 5. 部署应用服务

```bash
# 部署API网关
kubectl apply -f k8s/production/api-gateway/ -n suoke-production

# 部署核心服务
kubectl apply -f k8s/production/user-management-service/ -n suoke-production
kubectl apply -f k8s/production/unified-health-data-service/ -n suoke-production
kubectl apply -f k8s/production/blockchain-service/ -n suoke-production

# 部署智能体服务
kubectl apply -f k8s/production/agent-services/ -n suoke-production

# 部署其他服务
kubectl apply -f k8s/production/communication-service/ -n suoke-production
kubectl apply -f k8s/production/utility-services/ -n suoke-production
```

#### 6. 配置Ingress

```bash
# 安装Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 部署Ingress规则
kubectl apply -f k8s/production/ingress/ -n suoke-production
```

#### 7. 部署监控

```bash
# 部署Prometheus
kubectl apply -f k8s/production/monitoring/prometheus/ -n suoke-production

# 部署Grafana
kubectl apply -f k8s/production/monitoring/grafana/ -n suoke-production

# 部署ELK Stack
kubectl apply -f k8s/production/monitoring/elasticsearch/ -n suoke-production
kubectl apply -f k8s/production/monitoring/logstash/ -n suoke-production
kubectl apply -f k8s/production/monitoring/kibana/ -n suoke-production
```

## 数据库初始化

### 1. 运行数据库迁移

```bash
# Docker Compose环境
docker-compose -f docker-compose.microservices.yml exec user-management-service python manage.py migrate

# Kubernetes环境
kubectl exec -it deployment/user-management-service -n suoke-production -- python manage.py migrate
```

### 2. 创建超级用户

```bash
# Docker Compose环境
docker-compose -f docker-compose.microservices.yml exec user-management-service python manage.py createsuperuser

# Kubernetes环境
kubectl exec -it deployment/user-management-service -n suoke-production -- python manage.py createsuperuser
```

### 3. 加载初始数据

```bash
# 加载中医知识库
docker-compose -f docker-compose.microservices.yml exec laoke-service python manage.py loaddata tcm_knowledge.json

# 加载诊断规则
docker-compose -f docker-compose.microservices.yml exec xiaoke-service python manage.py loaddata diagnosis_rules.json
```

## SSL/TLS配置

### 1. 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d api.suoke.life -d app.suoke.life

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. 配置Nginx

```nginx
# /etc/nginx/sites-available/suoke-life
server {
    listen 80;
    server_name api.suoke.life app.suoke.life;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.suoke.life;

    ssl_certificate /etc/letsencrypt/live/api.suoke.life/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.suoke.life/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 性能优化

### 1. 数据库优化

```sql
-- PostgreSQL配置优化
-- /etc/postgresql/15/main/postgresql.conf

# 内存配置
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# 连接配置
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# 日志配置
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000

# 检查点配置
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

### 2. Redis优化

```conf
# /etc/redis/redis.conf

# 内存配置
maxmemory 512mb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1
save 300 10
save 60 10000

# 网络配置
tcp-keepalive 300
timeout 0
```

### 3. 应用优化

```yaml
# docker-compose.microservices.yml
services:
  api-gateway:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    environment:
      - NODE_OPTIONS=--max-old-space-size=1536
```

## 监控和日志

### 1. 访问监控面板

- **Grafana**: https://monitoring.suoke.life:3000
  - 用户名: admin
  - 密码: 在环境变量中配置

- **Prometheus**: https://monitoring.suoke.life:9090

- **Kibana**: https://monitoring.suoke.life:5601

### 2. 关键监控指标

#### 系统指标
- CPU使用率
- 内存使用率
- 磁盘使用率
- 网络流量

#### 应用指标
- 请求响应时间
- 错误率
- 吞吐量
- 数据库连接数

#### 业务指标
- 用户注册数
- 健康数据提交量
- 智能体交互次数
- 区块链交易数

### 3. 告警配置

```yaml
# prometheus/alert-rules.yml
groups:
  - name: suoke-life-alerts
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          
      - alert: HighMemoryUsage
        expr: memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
```

## 备份和恢复

### 1. 数据库备份

```bash
#!/bin/bash
# scripts/backup-database.sh

BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="suoke_life_backup_${DATE}.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker-compose -f docker-compose.microservices.yml exec -T postgres pg_dump -U suoke_user suoke_life > $BACKUP_DIR/$BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_DIR/$BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Database backup completed: $BACKUP_FILE.gz"
```

### 2. 应用数据备份

```bash
#!/bin/bash
# scripts/backup-application.sh

BACKUP_DIR="/backup/application"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份配置文件
tar -czf $BACKUP_DIR/config_backup_${DATE}.tar.gz .env docker-compose.*.yml k8s/

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_backup_${DATE}.tar.gz uploads/

# 备份日志文件
tar -czf $BACKUP_DIR/logs_backup_${DATE}.tar.gz logs/

echo "Application backup completed"
```

### 3. 自动备份配置

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点执行数据库备份
0 2 * * * /path/to/suoke-life/scripts/backup-database.sh

# 每周日凌晨3点执行应用备份
0 3 * * 0 /path/to/suoke-life/scripts/backup-application.sh
```

## 故障排除

### 1. 常见问题

#### 服务启动失败
```bash
# 查看服务日志
docker-compose -f docker-compose.microservices.yml logs service-name

# 检查端口占用
netstat -tulpn | grep :8000

# 检查磁盘空间
df -h
```

#### 数据库连接失败
```bash
# 检查数据库状态
docker-compose -f docker-compose.microservices.yml exec postgres pg_isready

# 检查数据库日志
docker-compose -f docker-compose.microservices.yml logs postgres

# 测试数据库连接
docker-compose -f docker-compose.microservices.yml exec postgres psql -U suoke_user -d suoke_life -c "SELECT 1;"
```

#### 内存不足
```bash
# 查看内存使用情况
free -h
docker stats

# 清理Docker缓存
docker system prune -a
```

### 2. 性能问题诊断

```bash
# 查看系统负载
top
htop

# 查看网络连接
ss -tulpn

# 查看磁盘I/O
iotop

# 查看应用性能
docker-compose -f docker-compose.microservices.yml exec api-gateway npm run profile
```

## 安全配置

### 1. 防火墙配置

```bash
# Ubuntu UFW
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp  # 禁止外部访问数据库
sudo ufw deny 6379/tcp  # 禁止外部访问Redis
```

### 2. 容器安全

```yaml
# docker-compose.microservices.yml
services:
  api-gateway:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"
```

### 3. 网络安全

```yaml
# docker-compose.microservices.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 内部网络，不允许外部访问
```

## 更新和维护

### 1. 滚动更新

```bash
# Docker Compose环境
docker-compose -f docker-compose.microservices.yml pull
docker-compose -f docker-compose.microservices.yml up -d --no-deps service-name

# Kubernetes环境
kubectl set image deployment/api-gateway api-gateway=suoke-life/api-gateway:v1.1.0 -n suoke-production
kubectl rollout status deployment/api-gateway -n suoke-production
```

### 2. 回滚操作

```bash
# Kubernetes回滚
kubectl rollout undo deployment/api-gateway -n suoke-production
kubectl rollout status deployment/api-gateway -n suoke-production
```

### 3. 维护模式

```bash
# 启用维护模式
kubectl scale deployment --replicas=0 --all -n suoke-production

# 显示维护页面
kubectl apply -f k8s/production/maintenance-page.yml -n suoke-production

# 恢复服务
kubectl delete -f k8s/production/maintenance-page.yml -n suoke-production
kubectl scale deployment --replicas=3 --all -n suoke-production
```

## 联系支持

如果在部署过程中遇到问题，请联系：

- **技术支持邮箱**: devops@suoke.life
- **紧急联系电话**: +86-400-xxx-xxxx
- **在线文档**: https://docs.suoke.life
- **GitHub Issues**: https://github.com/suoke-life/suoke-life/issues

---

*最后更新: 2024年1月15日*
*文档版本: v1.0.0* 