# 索克生活认证服务部署指南

## 概述

本指南将帮助您部署索克生活认证服务到生产环境。该服务是一个高可用、安全的企业级认证解决方案。

## 系统要求

### 最低配置
- CPU: 2核心
- 内存: 4GB RAM
- 存储: 20GB SSD
- 网络: 100Mbps

### 推荐配置
- CPU: 4核心
- 内存: 8GB RAM
- 存储: 50GB SSD
- 网络: 1Gbps

### 软件依赖
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker 20.10+
- Kubernetes 1.20+ (可选)

## 环境配置

### 1. 创建环境配置文件

创建 `.env` 文件并配置以下必需变量：

```bash
# 数据库配置 (必需)
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=suoke_auth_db
DB_USER=auth_user
DB_PASSWORD=your_secure_password

# Redis配置 (必需)
REDIS_HOST=your_redis_host
REDIS_PORT=6379

# JWT配置 (必需)
JWT_SECRET_KEY=your_very_long_and_secure_secret_key_at_least_32_characters_long
JWT_ALGORITHM=RS256

# 服务配置 (必需)
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
DEBUG=false
```

### 2. 可选功能配置

#### 短信服务 (Twilio)
```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

#### 邮件服务 (SMTP)
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
```

#### OAuth社交登录
```bash
# GitHub
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Google
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# 微信
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
```

## 部署方式

### 方式1: Docker部署 (推荐)

#### 1. 构建镜像
```bash
docker build -t suoke-auth-service:latest .
```

#### 2. 使用Docker Compose
```bash
docker-compose up -d
```

#### 3. 验证部署
```bash
docker-compose ps
docker-compose logs auth-service
```

### 方式2: Kubernetes部署

#### 1. 应用配置
```bash
kubectl apply -f k8s/
```

#### 2. 检查状态
```bash
kubectl get pods -l app=auth-service
kubectl get services auth-service
```

#### 3. 查看日志
```bash
kubectl logs -l app=auth-service -f
```

### 方式3: 直接部署

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 数据库迁移
```bash
python -m alembic upgrade head
```

#### 3. 启动服务
```bash
python main.py
```

## 数据库设置

### PostgreSQL配置

#### 1. 创建数据库和用户
```sql
CREATE DATABASE suoke_auth_db;
CREATE USER auth_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE suoke_auth_db TO auth_user;
```

#### 2. 运行迁移
```bash
python -m alembic upgrade head
```

### Redis配置

#### 1. 基本配置
```bash
# redis.conf
bind 0.0.0.0
port 6379
requirepass your_redis_password
maxmemory 2gb
maxmemory-policy allkeys-lru
```

## 安全配置

### 1. JWT密钥生成

#### 生成RSA密钥对
```bash
# 生成私钥
openssl genrsa -out jwt_private.pem 2048

# 生成公钥
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
```

### 2. 防火墙配置
```bash
# 只允许必要端口
ufw allow 8000/tcp  # 服务端口
ufw allow 22/tcp    # SSH
ufw enable
```

### 3. SSL/TLS配置

使用反向代理 (如Nginx) 配置HTTPS：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 监控和日志

### 1. 健康检查端点
- `GET /health` - 基本健康检查
- `GET /health/detailed` - 详细健康状态

### 2. 指标监控
- Prometheus指标: `http://localhost:9090/metrics`
- Grafana仪表板配置

### 3. 日志配置
```python
# 日志级别
LOG_LEVEL=INFO

# 日志格式
LOG_FORMAT=json

# 日志文件
LOG_FILE=/var/log/auth-service/app.log
```

## 性能优化

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
```

### 2. Redis缓存策略
```python
# 缓存配置
CACHE_TTL_SHORT=300      # 5分钟
CACHE_TTL_MEDIUM=3600    # 1小时
CACHE_TTL_LONG=86400     # 24小时
```

### 3. 连接池配置
```python
# 数据库连接池
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis连接池
REDIS_POOL_SIZE=10
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库状态
systemctl status postgresql
netstat -tlnp | grep 5432

# 检查连接配置
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

#### 2. Redis连接失败
```bash
# 检查Redis状态
systemctl status redis
redis-cli ping

# 检查配置
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping
```

#### 3. JWT验证失败
```bash
# 检查密钥配置
echo $JWT_SECRET_KEY | wc -c  # 应该 >= 32

# 验证RSA密钥
openssl rsa -in jwt_private.pem -check
```

### 日志分析

#### 查看错误日志
```bash
# Docker部署
docker-compose logs auth-service | grep ERROR

# 直接部署
tail -f /var/log/auth-service/app.log | grep ERROR
```

#### 性能分析
```bash
# 查看响应时间
grep "response_time" /var/log/auth-service/app.log

# 查看错误率
grep "status_code" /var/log/auth-service/app.log | grep -E "4[0-9]{2}|5[0-9]{2}"
```

## 备份和恢复

### 数据库备份
```bash
# 创建备份
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
psql -h $DB_HOST -U $DB_USER $DB_NAME < backup_file.sql
```

### Redis备份
```bash
# 创建快照
redis-cli BGSAVE

# 复制RDB文件
cp /var/lib/redis/dump.rdb /backup/redis_$(date +%Y%m%d_%H%M%S).rdb
```

## 扩展和升级

### 水平扩展
1. 使用负载均衡器 (如HAProxy、Nginx)
2. 部署多个服务实例
3. 配置会话共享 (Redis)

### 垂直扩展
1. 增加CPU和内存资源
2. 优化数据库性能
3. 调整连接池大小

### 升级流程
1. 备份数据库和配置
2. 测试新版本
3. 滚动更新部署
4. 验证功能正常

## 支持和维护

### 定期维护任务
- [ ] 数据库备份 (每日)
- [ ] 日志轮转 (每周)
- [ ] 安全更新 (每月)
- [ ] 性能监控 (持续)

### 联系支持
- 技术文档: [项目README](./README.md)
- 问题报告: GitHub Issues
- 紧急支持: 联系开发团队

---

**注意**: 请确保在生产环境中使用强密码和安全配置。定期更新依赖包和监控安全漏洞。 