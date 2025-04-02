# RAG服务部署指南

## 1. 系统要求

### 1.1 硬件要求
- CPU: 8核或以上
- 内存: 16GB或以上
- 磁盘: 100GB或以上SSD

### 1.2 软件要求
- Python 3.9+
- Docker 20.10+
- Docker Compose 2.0+
- Neo4j 4.4+
- Redis 6.0+

## 2. 环境准备

### 2.1 Python环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2.2 环境变量配置
创建`.env`文件：
```env
# 服务配置
SERVICE_NAME=rag-service
VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
WORKERS=4
THREADS=2
DEBUG=false

# 日志配置
LOG_LEVEL=INFO
LOG_PATH=/var/log/rag-service

# 监控配置
METRICS_PORT=9090
ERROR_RATE_THRESHOLD=0.1
LATENCY_THRESHOLD=5.0
CACHE_HIT_RATE_THRESHOLD=0.7
ALERT_CHECK_INTERVAL=300

# Neo4j配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## 3. 部署步骤

### 3.1 使用Docker Compose部署
1. 创建`docker-compose.yml`：
```yaml
version: '3.8'

services:
  rag:
    build: .
    ports:
      - "8000:8000"
      - "9090:9090"
    volumes:
      - ./logs:/var/log/rag-service
    env_file:
      - .env
    depends_on:
      - neo4j
      - redis
      - prometheus
      - grafana

  neo4j:
    image: neo4j:4.4
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    environment:
      NEO4J_AUTH: neo4j/your-password

  redis:
    image: redis:6.0
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  neo4j_data:
  neo4j_logs:
  redis_data:
  prometheus_data:
  grafana_data:
```

2. 创建`prometheus.yml`：
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rag'
    static_configs:
      - targets: ['rag:9090']
```

3. 启动服务：
```bash
docker-compose up -d
```

### 3.2 直接部署
1. 安装系统依赖：
```bash
# Ubuntu/Debian
apt-get update
apt-get install -y python3-dev build-essential

# CentOS/RHEL
yum groupinstall -y "Development Tools"
yum install -y python3-devel
```

2. 配置系统服务：
创建`/etc/systemd/system/rag.service`：
```ini
[Unit]
Description=RAG Service
After=network.target

[Service]
User=rag
Group=rag
WorkingDirectory=/opt/rag-service
Environment=PATH=/opt/rag-service/venv/bin
EnvironmentFile=/opt/rag-service/.env
ExecStart=/opt/rag-service/venv/bin/python src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 启动服务：
```bash
systemctl daemon-reload
systemctl enable rag
systemctl start rag
```

## 4. 监控配置

### 4.1 Prometheus配置
访问`http://localhost:9090`配置监控指标：
- `rag_request_total`: 请求总数
- `rag_request_latency_seconds`: 请求延迟
- `rag_error_total`: 错误总数
- `rag_cache_hits_total`: 缓存命中数
- `rag_vector_store_health`: 向量存储健康状态

### 4.2 Grafana配置
1. 访问`http://localhost:3000`（默认用户名/密码：admin/admin）
2. 添加Prometheus数据源
3. 导入监控面板模板（提供的JSON文件）

### 4.3 告警配置
1. 在Prometheus中配置告警规则：
```yaml
groups:
  - name: rag-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(rag_error_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          
      - alert: HighLatency
        expr: rate(rag_request_latency_seconds_sum[5m]) / rate(rag_request_latency_seconds_count[5m]) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
```

2. 配置告警通知（可选）：
- 配置邮件通知
- 配置Slack通知
- 配置企业微信通知

## 5. 日志管理

### 5.1 日志路径
- 应用日志：`/var/log/rag-service/app.log`
- 错误日志：`/var/log/rag-service/error.log`
- 访问日志：`/var/log/rag-service/access.log`

### 5.2 日志轮转
使用logrotate配置日志轮转：
```conf
/var/log/rag-service/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 rag rag
}
```

## 6. 维护操作

### 6.1 备份
1. 知识库备份：
```bash
# Neo4j备份
neo4j-admin backup --backup-dir=/backup/neo4j

# Redis备份
redis-cli save
cp /var/lib/redis/dump.rdb /backup/redis/
```

2. 配置备份：
```bash
cp .env /backup/config/
cp prometheus.yml /backup/config/
```

### 6.2 更新
1. 更新代码：
```bash
git pull origin main
```

2. 更新依赖：
```bash
pip install -r requirements.txt --upgrade
```

3. 重启服务：
```bash
systemctl restart rag
```

### 6.3 故障排查
1. 检查服务状态：
```bash
systemctl status rag
```

2. 检查日志：
```bash
tail -f /var/log/rag-service/error.log
```

3. 检查监控指标：
访问`http://localhost:9090/metrics`

4. 健康检查：
```bash
curl http://localhost:8000/health
```

## 7. 安全配置

### 7.1 防火墙配置
```bash
# 开放必要端口
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --permanent --add-port=9090/tcp
firewall-cmd --reload
```

### 7.2 SSL配置
1. 获取SSL证书
2. 配置Nginx反向代理：
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
    }
}
```

## 8. 性能优化

### 8.1 系统优化
1. 调整系统限制：
```bash
# /etc/security/limits.conf
rag soft nofile 65535
rag hard nofile 65535
```

2. 调整内核参数：
```bash
# /etc/sysctl.conf
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
```

### 8.2 应用优化
1. 调整工作进程数：
```env
WORKERS=8  # 设置为CPU核心数的2倍
```

2. 调整缓存配置：
```env
CACHE_SIZE=1000
CACHE_TTL=3600
```

## 9. 常见问题

### 9.1 服务无法启动
1. 检查配置文件
2. 检查依赖安装
3. 检查日志错误信息

### 9.2 性能问题
1. 检查系统资源使用情况
2. 检查慢查询日志
3. 优化缓存配置

### 9.3 监控告警
1. 检查Prometheus配置
2. 检查告警规则
3. 验证告警通知渠道