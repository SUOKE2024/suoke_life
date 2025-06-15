# 小艾智能体生产环境部署指南

## 📋 目录
- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [部署步骤](#部署步骤)
- [配置说明](#配置说明)
- [监控设置](#监控设置)
- [故障排除](#故障排除)
- [维护指南](#维护指南)

## 🖥️ 系统要求

### 最低配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **网络**: 100Mbps带宽
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Docker

### 推荐配置
- **CPU**: 8核心
- **内存**: 16GB RAM
- **存储**: 100GB SSD
- **网络**: 1Gbps带宽
- **操作系统**: Ubuntu 22.04 LTS

### 依赖服务
- **PostgreSQL**: 13+
- **Redis**: 6+
- **Nginx**: 1.18+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

## 🔧 环境准备

### 1. 安装Docker和Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 创建部署目录

```bash
sudo mkdir -p /opt/xiaoai-service
sudo chown $USER:$USER /opt/xiaoai-service
cd /opt/xiaoai-service
```

### 3. 下载项目文件

```bash
# 克隆项目或复制文件
git clone <repository-url> .
# 或者
scp -r xiaoai-service/* /opt/xiaoai-service/
```

## 🚀 部署步骤

### 1. 配置环境变量

```bash
# 复制环境配置文件
cp .env.production .env

# 编辑配置文件
nano .env
```

**重要**: 修改以下关键配置：
- `SECRET_KEY`: 生成强密钥
- `JWT_SECRET`: 生成JWT密钥
- `DB_PASSWORD`: 设置数据库密码
- `REDIS_PASSWORD`: 设置Redis密码
- `ENCRYPTION_KEY`: 设置加密密钥

### 2. 生成SSL证书

```bash
# 创建SSL目录
mkdir -p ssl

# 使用Let's Encrypt (推荐)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*

# 或者生成自签名证书 (仅用于测试)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem
```

### 3. 创建数据目录

```bash
mkdir -p {logs,models,data}
chmod 755 logs models data
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f xiaoai-service
```

### 5. 数据库初始化

```bash
# 等待数据库启动
sleep 30

# 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec xiaoai-service \
    python -m alembic upgrade head

# 创建初始数据
docker-compose -f docker-compose.prod.yml exec xiaoai-service \
    python -m xiaoai.scripts.init_data
```

### 6. 验证部署

```bash
# 健康检查
curl -f http://localhost/health

# API测试
curl -X POST http://localhost/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}'
```

## ⚙️ 配置说明

### 环境变量详解

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `ENVIRONMENT` | 运行环境 | production | ✅ |
| `SECRET_KEY` | 应用密钥 | - | ✅ |
| `DATABASE_URL` | 数据库连接 | - | ✅ |
| `REDIS_URL` | Redis连接 | - | ✅ |
| `LOG_LEVEL` | 日志级别 | INFO | ❌ |
| `WORKER_PROCESSES` | 工作进程数 | 4 | ❌ |

### Nginx配置

编辑 `nginx.conf` 文件以自定义：
- 域名设置
- SSL配置
- 限流规则
- 缓存策略

### 数据库配置

PostgreSQL优化建议：
```sql
-- 在postgresql.conf中设置
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
max_connections = 100
```

## 📊 监控设置

### 1. 启用指标收集

```bash
# 访问指标端点
curl http://localhost:9090/metrics
```

### 2. 配置Prometheus (可选)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'xiaoai-service'
    static_configs:
      - targets: ['localhost:9090']
```

### 3. 日志监控

```bash
# 查看实时日志
tail -f logs/xiaoai.log

# 查看错误日志
grep ERROR logs/xiaoai.log
```

## 🔧 故障排除

### 常见问题

#### 1. 服务无法启动
```bash
# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查Docker日志
docker-compose logs xiaoai-service

# 检查配置文件
docker-compose config
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready

# 测试连接
docker-compose exec postgres psql -U xiaoai -d xiaoai_db -c "SELECT 1;"
```

#### 3. Redis连接失败
```bash
# 检查Redis状态
docker-compose exec redis redis-cli ping

# 查看Redis日志
docker-compose logs redis
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h
docker stats

# 调整Docker内存限制
# 编辑docker-compose.prod.yml中的resources配置
```

### 性能调优

#### 1. 数据库优化
```bash
# 分析慢查询
docker-compose exec postgres psql -U xiaoai -d xiaoai_db \
    -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

#### 2. 缓存优化
```bash
# 查看缓存命中率
curl http://localhost:8000/api/metrics | grep cache_hit_rate
```

## 🛠️ 维护指南

### 日常维护

#### 1. 日志轮转
```bash
# 设置logrotate
sudo tee /etc/logrotate.d/xiaoai-service << EOF
/opt/xiaoai-service/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 xiaoai xiaoai
}
EOF
```

#### 2. 数据库备份
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U xiaoai xiaoai_db > backup_${DATE}.sql
gzip backup_${DATE}.sql
find . -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# 设置定时任务
echo "0 2 * * * /opt/xiaoai-service/backup.sh" | crontab -
```

#### 3. 更新部署
```bash
# 拉取新镜像
docker-compose -f docker-compose.prod.yml pull

# 重启服务
docker-compose -f docker-compose.prod.yml up -d

# 清理旧镜像
docker image prune -f
```

### 安全维护

#### 1. 证书更新
```bash
# 自动更新Let's Encrypt证书
sudo certbot renew --quiet
sudo systemctl reload nginx
```

#### 2. 安全扫描
```bash
# 扫描容器漏洞
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image xiaoai-service:latest
```

### 监控告警

#### 1. 健康检查脚本
```bash
#!/bin/bash
# health_check.sh
HEALTH_URL="http://localhost/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
    echo "服务健康检查失败: HTTP $RESPONSE"
    # 发送告警通知
    # curl -X POST "https://api.telegram.org/bot<token>/sendMessage" \
    #     -d "chat_id=<chat_id>&text=小艾服务异常: HTTP $RESPONSE"
fi
```

#### 2. 资源监控
```bash
#!/bin/bash
# resource_monitor.sh
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')

if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "CPU使用率过高: $CPU_USAGE%"
fi

if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "内存使用率过高: $MEM_USAGE%"
fi
```

## 📞 支持联系

如遇到部署问题，请联系：
- 技术支持邮箱: support@xiaoai.com
- 文档地址: https://docs.xiaoai.com
- 问题反馈: https://github.com/xiaoai/issues

---

*最后更新: 2024年12月6日*