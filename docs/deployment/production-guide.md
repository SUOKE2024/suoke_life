# 索克生活生产环境部署指南

## 📋 部署概览

本指南详细说明如何在生产环境中部署索克生活平台，包括所有微服务、数据库、监控系统等组件。

## 🏗️ 系统架构

```
生产环境架构:
├── 负载均衡器 (Nginx/HAProxy)
├── API网关集群 (3个实例)
├── 智能体服务集群 (4个服务 × 3个实例)
├── 诊断服务集群 (5个服务 × 2个实例)
├── 业务服务集群 (8个服务 × 2个实例)
├── 数据库集群 (PostgreSQL主从 + Redis集群)
├── 消息队列 (RabbitMQ集群)
├── 监控系统 (Prometheus + Grafana)
└── 日志系统 (ELK Stack)
```

## 🔧 环境要求

### 硬件要求

#### 最小配置
- **CPU**: 16核心
- **内存**: 64GB RAM
- **存储**: 1TB SSD
- **网络**: 1Gbps带宽

#### 推荐配置
- **CPU**: 32核心
- **内存**: 128GB RAM
- **存储**: 2TB NVMe SSD
- **网络**: 10Gbps带宽

### 软件要求

```bash
# 操作系统
Ubuntu 22.04 LTS / CentOS 8 / RHEL 8

# 容器运行时
Docker 24.0+
Docker Compose 2.20+

# 容器编排
Kubernetes 1.28+
Helm 3.12+

# 数据库
PostgreSQL 15+
Redis 7.0+
MongoDB 6.0+

# 监控
Prometheus 2.45+
Grafana 10.0+
```

## 🚀 部署步骤

### 1. 环境准备

#### 1.1 服务器初始化

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl wget git vim htop

# 配置防火墙
sudo ufw enable
sudo ufw allow 22,80,443,8080,9090,3000/tcp

# 设置时区
sudo timedatectl set-timezone Asia/Shanghai

# 配置系统限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf
```

#### 1.2 Docker安装

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动Docker服务
sudo systemctl enable docker
sudo systemctl start docker

# 添加用户到docker组
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 1.3 Kubernetes安装 (可选)

```bash
# 安装kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 安装Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 2. 数据库部署

#### 2.1 PostgreSQL集群部署

```yaml
# docker-compose.postgres.yml
version: '3.8'
services:
  postgres-master:
    image: postgres:15
    environment:
      POSTGRES_DB: suoke_life
      POSTGRES_USER: suoke_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${REPLICATION_PASSWORD}
    volumes:
      - postgres_master_data:/var/lib/postgresql/data
      - ./postgres/master.conf:/etc/postgresql/postgresql.conf
      - ./postgres/pg_hba.conf:/etc/postgresql/pg_hba.conf
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    
  postgres-slave:
    image: postgres:15
    environment:
      POSTGRES_USER: suoke_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGUSER: postgres
    volumes:
      - postgres_slave_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    depends_on:
      - postgres-master

volumes:
  postgres_master_data:
  postgres_slave_data:
```

#### 2.2 Redis集群部署

```yaml
# docker-compose.redis.yml
version: '3.8'
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_master_data:/data
    ports:
      - "6379:6379"
      
  redis-slave-1:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD} --slaveof redis-master 6379
    volumes:
      - redis_slave1_data:/data
    ports:
      - "6380:6379"
    depends_on:
      - redis-master
      
  redis-slave-2:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD} --slaveof redis-master 6379
    volumes:
      - redis_slave2_data:/data
    ports:
      - "6381:6379"
    depends_on:
      - redis-master

volumes:
  redis_master_data:
  redis_slave1_data:
  redis_slave2_data:
```

### 3. 微服务部署

#### 3.1 创建生产环境配置

```bash
# 创建环境变量文件
cat > .env.production << EOF
# 数据库配置
POSTGRES_HOST=postgres-master
POSTGRES_PORT=5432
POSTGRES_DB=suoke_life
POSTGRES_USER=suoke_admin
POSTGRES_PASSWORD=your_secure_password

# Redis配置
REDIS_HOST=redis-master
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT配置
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRE_HOURS=24

# API网关配置
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8080

# 智能体服务配置
XIAOAI_SERVICE_HOST=xiaoai-service
XIAOAI_SERVICE_PORT=50053
XIAOKE_SERVICE_HOST=xiaoke-service
XIAOKE_SERVICE_PORT=50054
LAOKE_SERVICE_HOST=laoke-service
LAOKE_SERVICE_PORT=50055
SOER_SERVICE_HOST=soer-service
SOER_SERVICE_PORT=50056

# 监控配置
PROMETHEUS_HOST=prometheus
PROMETHEUS_PORT=9090
GRAFANA_HOST=grafana
GRAFANA_PORT=3000

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# 安全配置
ENABLE_HTTPS=true
SSL_CERT_PATH=/etc/ssl/certs/suoke.crt
SSL_KEY_PATH=/etc/ssl/private/suoke.key
EOF
```

#### 3.2 主服务部署配置

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  # API网关
  api-gateway:
    image: suoke/api-gateway:latest
    ports:
      - "8080:8080"
      - "443:443"
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./ssl:/etc/ssl
      - ./logs:/app/logs
    depends_on:
      - postgres-master
      - redis-master
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped
    
  # 智能体服务
  xiaoai-service:
    image: suoke/xiaoai-service:latest
    ports:
      - "50053:50053"
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    restart: unless-stopped
    
  xiaoke-service:
    image: suoke/xiaoke-service:latest
    ports:
      - "50054:50054"
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped
    
  laoke-service:
    image: suoke/laoke-service:latest
    ports:
      - "50055:50055"
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped
    
  soer-service:
    image: suoke/soer-service:latest
    ports:
      - "50056:50056"
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped

  # 诊断服务
  look-service:
    image: suoke/look-service:latest
    ports:
      - "8010:8010"
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '3'
          memory: 6G
        reservations:
          cpus: '2'
          memory: 4G
    restart: unless-stopped
    
  listen-service:
    image: suoke/listen-service:latest
    ports:
      - "8011:8011"
    environment:
      - ENV=production
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '3'
          memory: 6G
        reservations:
          cpus: '2'
          memory: 4G
    restart: unless-stopped

  # 监控服务
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 4. 负载均衡配置

#### 4.1 Nginx配置

```nginx
# /etc/nginx/sites-available/suoke-life
upstream api_gateway {
    least_conn;
    server 172.20.0.10:8080 max_fails=3 fail_timeout=30s;
    server 172.20.0.11:8080 max_fails=3 fail_timeout=30s;
    server 172.20.0.12:8080 max_fails=3 fail_timeout=30s;
}

upstream xiaoai_service {
    least_conn;
    server 172.20.0.20:50053 max_fails=3 fail_timeout=30s;
    server 172.20.0.21:50053 max_fails=3 fail_timeout=30s;
    server 172.20.0.22:50053 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    listen [::]:80;
    server_name api.suoke.life;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.suoke.life;

    # SSL配置
    ssl_certificate /etc/ssl/certs/suoke.crt;
    ssl_certificate_key /etc/ssl/private/suoke.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # API网关代理
    location /api/ {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 健康检查
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    }

    # gRPC代理
    location /grpc/ {
        grpc_pass grpc://xiaoai_service;
        grpc_set_header Host $host;
        grpc_set_header X-Real-IP $remote_addr;
        grpc_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        grpc_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static/ {
        alias /var/www/suoke-life/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 5. 监控配置

#### 5.1 Prometheus配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # API网关监控
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8080']
    metrics_path: /metrics
    scrape_interval: 10s

  # 智能体服务监控
  - job_name: 'xiaoai-service'
    static_configs:
      - targets: ['xiaoai-service:50053']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'xiaoke-service'
    static_configs:
      - targets: ['xiaoke-service:50054']
    metrics_path: /metrics
    scrape_interval: 10s

  # 数据库监控
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # 系统监控
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 6. 部署执行

#### 6.1 构建镜像

```bash
# 构建所有服务镜像
./scripts/build-images.sh production

# 推送到镜像仓库
./scripts/push-images.sh
```

#### 6.2 部署服务

```bash
# 创建部署目录
mkdir -p /opt/suoke-life
cd /opt/suoke-life

# 复制配置文件
cp docker-compose.production.yml .
cp .env.production .

# 启动数据库
docker-compose -f docker-compose.postgres.yml up -d
docker-compose -f docker-compose.redis.yml up -d

# 等待数据库启动
sleep 30

# 初始化数据库
docker-compose exec postgres-master psql -U suoke_admin -d suoke_life -f /docker-entrypoint-initdb.d/init.sql

# 启动所有服务
docker-compose -f docker-compose.production.yml up -d

# 检查服务状态
docker-compose ps
```

### 7. 健康检查和验证

#### 7.1 服务健康检查

```bash
# 检查API网关
curl -f http://localhost:8080/health

# 检查智能体服务
curl -f http://localhost:50053/health
curl -f http://localhost:50054/health
curl -f http://localhost:50055/health
curl -f http://localhost:50056/health

# 检查数据库连接
docker-compose exec postgres-master pg_isready -U suoke_admin

# 检查Redis连接
docker-compose exec redis-master redis-cli ping
```

#### 7.2 功能验证

```bash
# 测试用户注册
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# 测试智能体服务
curl -X POST http://localhost:8080/api/v1/xiaoai/health/consult \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"user_id":"test","symptoms":["头痛"],"duration":"1天","severity":"轻微"}'
```

## 🔒 安全配置

### SSL证书配置

```bash
# 使用Let's Encrypt获取免费SSL证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.suoke.life

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 防火墙配置

```bash
# 配置iptables规则
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j DROP
sudo iptables -A INPUT -j DROP

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
```

## 📊 性能优化

### 数据库优化

```sql
-- PostgreSQL性能优化
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- 重启PostgreSQL使配置生效
SELECT pg_reload_conf();
```

### 应用优化

```bash
# 调整系统参数
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_fin_timeout = 30' >> /etc/sysctl.conf

# 应用配置
sysctl -p
```

## 🔄 备份和恢复

### 数据库备份

```bash
# 创建备份脚本
cat > /opt/suoke-life/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/suoke-life"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# PostgreSQL备份
docker-compose exec -T postgres-master pg_dump -U suoke_admin suoke_life | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Redis备份
docker-compose exec -T redis-master redis-cli --rdb /data/dump.rdb
docker cp $(docker-compose ps -q redis-master):/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# 清理7天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/suoke-life/backup.sh

# 设置定时备份
echo "0 2 * * * /opt/suoke-life/backup.sh" | crontab -
```

## 📈 监控和告警

### Grafana仪表板

```json
{
  "dashboard": {
    "title": "索克生活系统监控",
    "panels": [
      {
        "title": "API响应时间",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "服务可用性",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\".*-service\"}",
            "legendFormat": "{{job}}"
          }
        ]
      }
    ]
  }
}
```

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 查看日志
   docker-compose logs -f service-name
   
   # 检查资源使用
   docker stats
   ```

2. **数据库连接问题**
   ```bash
   # 检查数据库状态
   docker-compose exec postgres-master pg_isready
   
   # 查看连接数
   docker-compose exec postgres-master psql -U suoke_admin -c "SELECT count(*) FROM pg_stat_activity;"
   ```

3. **性能问题**
   ```bash
   # 查看系统资源
   htop
   iotop
   
   # 查看网络连接
   netstat -tulpn
   ```

## 📞 技术支持

- **技术文档**: https://docs.suoke.life
- **问题反馈**: https://github.com/SUOKE2024/suoke_life/issues
- **技术支持**: support@suoke.life
- **紧急联系**: +86-400-SUOKE-LIFE

---

**部署完成后，请确保所有服务正常运行，监控系统正常工作，并进行全面的功能测试。**
