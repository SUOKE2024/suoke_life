# 快速启动指南

## 环境要求

- Python 3.13+
- PostgreSQL 12+
- Redis 6+

## 快速启动

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装项目依赖
pip install -e .
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件（可选）
vim .env
```

### 3. 设置数据库

```bash
# 创建PostgreSQL数据库
createdb human_review

# 初始化数据库表
python -m human_review_service.cli.main db init

# 填充测试数据（可选）
python -m human_review_service.cli.main db seed
```

### 4. 启动服务

```bash
# 开发模式启动（支持热重载）
python -m human_review_service.cli.main serve --reload

# 或者生产模式启动
python -m human_review_service.cli.main serve --workers 4
```

### 5. 验证服务

访问以下URL验证服务是否正常运行：

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **指标监控**: http://localhost:8000/metrics

## Docker 快速启动

```bash
# 使用Docker Compose启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f human-review-service
```

## CLI 工具使用

```bash
# 查看帮助
python -m human_review_service.cli.main --help

# 查看服务信息
python -m human_review_service.cli.main info

# 数据库管理
python -m human_review_service.cli.main db status
python -m human_review_service.cli.main db init

# 审核员管理
python -m human_review_service.cli.main reviewer list
python -m human_review_service.cli.main reviewer create --name "张医生" --email "zhang@example.com"

# 服务器管理
python -m human_review_service.cli.main server status
python -m human_review_service.cli.main server monitor
```

## API 使用示例

### 创建审核任务

```bash
curl -X POST "http://localhost:8000/api/v1/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "建议患者多喝水，注意休息",
    "content_type": "medical_advice",
    "priority": "normal",
    "metadata": {
      "patient_id": "12345",
      "ai_model": "gpt-4"
    }
  }'
```

### 查询审核任务

```bash
curl "http://localhost:8000/api/v1/reviews?status=pending&limit=10"
```

### 创建审核员

```bash
curl -X POST "http://localhost:8000/api/v1/reviewers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "李医生",
    "email": "li@example.com",
    "specialties": ["内科", "全科"],
    "max_concurrent_tasks": 5
  }'
```

## 监控和日志

### 查看实时日志

```bash
# 查看服务日志
tail -f logs/human_review_service.log

# 查看错误日志
tail -f logs/error.log
```

### Prometheus 指标

访问 http://localhost:8000/metrics 查看Prometheus格式的指标数据。

主要指标包括：
- `review_tasks_total` - 审核任务总数
- `review_tasks_duration_seconds` - 审核任务处理时间
- `active_reviewers_total` - 活跃审核员数量
- `http_requests_total` - HTTP请求总数

### 健康检查

```bash
# 基本健康检查
curl http://localhost:8000/health

# 详细健康检查
python -m human_review_service.cli.main health --check-db --check-redis
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查PostgreSQL是否运行
   pg_ctl status
   
   # 检查数据库是否存在
   psql -l | grep human_review
   ```

2. **Redis连接失败**
   ```bash
   # 检查Redis是否运行
   redis-cli ping
   ```

3. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :8000
   
   # 使用其他端口启动
   python -m human_review_service.cli.main serve --port 8001
   ```

### 日志级别调整

```bash
# 设置调试模式
export DEBUG=true
python -m human_review_service.cli.main serve --reload

# 或者修改 .env 文件
echo "DEBUG=true" >> .env
echo "MONITORING_LOG_LEVEL=DEBUG" >> .env
```

## 开发模式

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 生成覆盖率报告
pytest --cov=human_review_service --cov-report=html
```

### 代码格式化

```bash
# 安装开发工具
pip install black isort flake8

# 格式化代码
black human_review_service/
isort human_review_service/

# 检查代码质量
flake8 human_review_service/
```

## 生产部署

### 环境变量配置

```bash
# 生产环境配置
export ENVIRONMENT=production
export DEBUG=false
export DATABASE_URL="postgresql://user:password@db-host:5432/human_review"
export REDIS_URL="redis://redis-host:6379/0"
export SECURITY_SECRET_KEY="your-super-secret-key-32-chars-min"
```

### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn human_review_service.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 反向代理配置 (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 支持

如有问题，请查看：
- [项目文档](README.md)
- [项目状态](PROJECT_STATUS.md)
- [API文档](http://localhost:8000/docs)

或联系开发团队获取支持。 