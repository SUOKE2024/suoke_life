# 索克生活人工审核微服务

## 项目概述

人工审核微服务是"索克生活（Suoke Life）"项目的核心组件之一，负责对AI智能体生成的医疗建议进行人工审核，确保医疗建议的安全性、准确性和合规性。

### 核心功能

- **智能审核分配**: 基于审核员专业领域和工作负载的智能任务分配
- **多级风险评估**: 支持不同优先级和风险等级的审核流程
- **实时审核界面**: 提供WebSocket实时通信和状态更新
- **灵活审核工作流**: 支持自定义审核流程和规则
- **统计分析**: 提供详细的审核统计和绩效分析
- **API集成**: 完整的RESTful API支持服务间通信

### 技术架构

- **后端框架**: FastAPI + Python 3.13
- **数据库**: PostgreSQL + SQLAlchemy (异步ORM)
- **缓存**: Redis
- **消息队列**: Redis Pub/Sub
- **通知系统**: 邮件/WebSocket/Webhook多渠道通知
- **性能优化**: 查询缓存、连接池优化、性能监控
- **安全加固**: JWT认证、权限控制、数据加密、审计日志
- **监控**: Prometheus + Grafana
- **容器化**: Docker + Docker Compose + Kubernetes
- **包管理**: UV (现代Python包管理器)

## 快速开始

### 环境要求

- Python 3.13.3+
- PostgreSQL 15+
- Redis 7+
- UV包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd suoke_life/services/human-review-service
```

2. **使用启动脚本（推荐）**
```bash
# 开发模式启动
./scripts/start.sh

# 生产模式启动
./scripts/start.sh -m production -p 8080 -w 4

# 仅初始化环境
./scripts/start.sh --init-only
```

3. **手动安装**
```bash
# 安装UV包管理器
pip install uv

# 创建虚拟环境
uv venv .venv --python python3.13
source .venv/bin/activate

# 安装依赖
uv pip install -e .

# 配置环境变量
cp env.example .env
# 编辑.env文件配置数据库等信息

# 初始化数据库
python -m human_review_service.cli.main db init

# 启动服务
python -m human_review_service.cli.main server start
```

### Docker部署

1. **使用Docker Compose（推荐）**
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f human-review-service

# 停止服务
docker-compose down
```

2. **单独构建Docker镜像**
```bash
# 构建镜像
docker build -t human-review-service .

# 运行容器
docker run -d \
  --name human-review-service \
  -p 8000:8000 \
  -e DATABASE_HOST=your_db_host \
  -e REDIS_HOST=your_redis_host \
  human-review-service
```

## CLI工具使用

### 服务器管理

```bash
# 启动服务器
python -m human_review_service.cli.main server start --host 0.0.0.0 --port 8000

# 守护进程模式启动
python -m human_review_service.cli.main server start --daemon --log-file ./logs/app.log

# 查看服务状态
python -m human_review_service.cli.main server status

# 停止服务
python -m human_review_service.cli.main server stop

# 重启服务
python -m human_review_service.cli.main server restart

# 监控服务
python -m human_review_service.cli.main server monitor
```

### 数据库管理

```bash
# 初始化数据库
python -m human_review_service.cli.main db init

# 检查数据库状态
python -m human_review_service.cli.main db status

# 备份数据库
python -m human_review_service.cli.main db backup --output ./backups/

# 恢复数据库
python -m human_review_service.cli.main db restore --file ./backups/backup.sql
```

### 审核员管理

```bash
# 创建审核员
python -m human_review_service.cli.main reviewer create \
  --name "张医生" \
  --email "zhang@example.com" \
  --specialties "中医诊断,方剂学" \
  --max-tasks 5

# 查看审核员
python -m human_review_service.cli.main reviewer show <reviewer_id>

# 列出审核员
python -m human_review_service.cli.main reviewer list --status active

# 更新审核员
python -m human_review_service.cli.main reviewer update <reviewer_id> \
  --name "张主任医师" \
  --max-tasks 8

# 激活/停用审核员
python -m human_review_service.cli.main reviewer activate <reviewer_id>
python -m human_review_service.cli.main reviewer deactivate <reviewer_id>

# 查看绩效统计
python -m human_review_service.cli.main reviewer performance <reviewer_id> --days 30

# 删除审核员
python -m human_review_service.cli.main reviewer delete <reviewer_id> --force
```

## API文档

### 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **API文档**: `http://localhost:8000/docs`
- **ReDoc文档**: `http://localhost:8000/redoc`

### 主要端点

#### 审核任务管理

```http
# 创建审核任务
POST /api/v1/reviews/
Content-Type: application/json

{
  "content_type": "diagnosis",
  "content_id": "diag_123",
  "content_data": {
    "symptoms": ["头痛", "发热"],
    "diagnosis": "感冒",
    "treatment": "多休息，多喝水"
  },
  "review_type": "medical_diagnosis",
  "priority": "normal",
  "requester_id": "user_123"
}

# 获取审核任务
GET /api/v1/reviews/{task_id}

# 列出审核任务
GET /api/v1/reviews/?status=pending&priority=high&limit=20

# 分配审核任务
POST /api/v1/reviews/{task_id}/assign
Content-Type: application/json

{
  "reviewer_id": "reviewer_123"
}

# 完成审核任务
POST /api/v1/reviews/{task_id}/complete
Content-Type: application/json

{
  "approved": true,
  "feedback": "诊断准确，建议合理",
  "suggestions": ["可以增加一些预防措施"],
  "quality_score": 0.95
}
```

#### 审核员管理

```http
# 创建审核员
POST /api/v1/reviewers/
Content-Type: application/json

{
  "name": "张医生",
  "email": "zhang@example.com",
  "specialties": ["中医诊断", "方剂学"],
  "max_concurrent_tasks": 5
}

# 获取审核员信息
GET /api/v1/reviewers/{reviewer_id}

# 列出审核员
GET /api/v1/reviewers/?status=active&specialty=中医诊断

# 获取工作负载
GET /api/v1/reviewers/{reviewer_id}/workload

# 获取绩效统计
GET /api/v1/reviewers/{reviewer_id}/performance?days=30
```

#### 仪表板和统计

```http
# 获取仪表板数据
GET /api/v1/dashboard/

# 获取统计数据
GET /api/v1/dashboard/statistics

# 获取实时指标
GET /api/v1/dashboard/metrics/real-time

# 获取趋势数据
GET /api/v1/dashboard/trends/daily?days=7
```

### WebSocket连接

```javascript
// 通用审核WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/reviews');

// 审核员专用WebSocket
const reviewerWs = new WebSocket('ws://localhost:8000/api/v1/ws/reviewers/reviewer_123');

// 用户专用WebSocket
const userWs = new WebSocket('ws://localhost:8000/api/v1/ws/users/user_123');
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行API测试
pytest -m api

# 生成覆盖率报告
pytest --cov=human_review_service --cov-report=html

# 并行测试
pytest -n auto
```

### 测试配置

测试配置在 `pytest.ini` 文件中定义，支持以下测试标记：

- `unit`: 单元测试
- `integration`: 集成测试
- `e2e`: 端到端测试
- `api`: API测试
- `database`: 数据库测试
- `websocket`: WebSocket测试

## 监控和日志

### Prometheus指标

服务暴露以下Prometheus指标：

- `http_requests_total`: HTTP请求总数
- `http_request_duration_seconds`: HTTP请求持续时间
- `review_tasks_total`: 审核任务总数
- `review_tasks_by_status`: 按状态分组的审核任务数
- `reviewer_workload`: 审核员工作负载
- `database_connections`: 数据库连接数

### 日志配置

日志配置支持多种格式和输出：

```python
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 日志格式: json, text
LOG_FORMAT=json

# 日志输出
LOG_CONSOLE_ENABLED=true
LOG_FILE_ENABLED=true
LOG_FILE_PATH=./logs/app.log
```

### Grafana仪表板

项目包含预配置的Grafana仪表板，显示：

- 服务健康状态
- 请求量和响应时间
- 审核任务统计
- 审核员绩效
- 系统资源使用情况

## 配置说明

### 环境变量

主要环境变量配置（详见 `env.example`）：

```bash
# 应用配置
APP_NAME="索克生活人工审核微服务"
ENVIRONMENT=development
DEBUG=true

# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=human_review_service
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 安全配置
JWT_SECRET_KEY=your_secret_key
API_KEY=your_api_key

# 审核配置
DEFAULT_REVIEW_TIMEOUT=24
AUTO_ASSIGN_TASKS=true
REVIEW_QUALITY_THRESHOLD=0.8
```

### 数据库配置

支持多种数据库类型：

- PostgreSQL（推荐）
- MySQL
- SQLite（仅用于开发和测试）

### 缓存配置

支持多种缓存后端：

- Redis（推荐）
- 内存缓存（仅用于开发）

## 部署指南

### 生产环境部署

1. **环境准备**
```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3.13 python3.13-venv postgresql redis-server

# 创建应用用户
sudo useradd -m -s /bin/bash human-review
sudo su - human-review
```

2. **应用部署**
```bash
# 克隆代码
git clone <repository-url>
cd human-review-service

# 配置环境
cp env.example .env
# 编辑.env文件配置生产环境参数

# 安装依赖
./scripts/start.sh --init-only

# 启动服务
./scripts/start.sh -m production -p 8000 -w 4
```

3. **Nginx配置**
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

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

4. **系统服务配置**
```ini
# /etc/systemd/system/human-review-service.service
[Unit]
Description=Human Review Service
After=network.target postgresql.service redis.service

[Service]
Type=forking
User=human-review
Group=human-review
WorkingDirectory=/home/human-review/human-review-service
ExecStart=/home/human-review/human-review-service/scripts/start.sh -m production
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Kubernetes部署

项目包含Kubernetes部署配置文件：

```bash
# 部署到Kubernetes
kubectl apply -f deploy/kubernetes/

# 查看部署状态
kubectl get pods -l app=human-review-service

# 查看服务
kubectl get svc human-review-service
```

## 故障排除

### 常见问题

1. **数据库连接失败**
```bash
# 检查数据库状态
python -m human_review_service.cli.main db status

# 重新初始化数据库
python -m human_review_service.cli.main db init --force
```

2. **Redis连接失败**
```bash
# 检查Redis状态
redis-cli ping

# 检查Redis配置
grep -E "bind|port|requirepass" /etc/redis/redis.conf
```

3. **服务启动失败**
```bash
# 查看详细日志
python -m human_review_service.cli.main server start --verbose

# 检查端口占用
netstat -tlnp | grep 8000
```

4. **性能问题**
```bash
# 监控服务状态
python -m human_review_service.cli.main server monitor

# 查看Prometheus指标
curl http://localhost:8000/metrics
```

### 日志分析

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 查看访问日志
grep "GET\|POST" logs/app.log
```

## 开发指南

### 代码结构

```
human_review_service/
├── api/                    # API层
│   ├── main.py            # FastAPI应用入口
│   ├── middleware.py      # 中间件
│   └── routes/            # 路由定义
├── core/                  # 核心层
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── models.py          # 数据模型
│   └── service.py         # 业务逻辑
├── cli/                   # CLI工具
│   ├── main.py            # CLI入口
│   └── commands/          # 命令实现
└── tests/                 # 测试代码
    ├── test_api.py        # API测试
    └── test_service.py    # 服务测试
```

### 开发环境设置

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 安装pre-commit钩子
pre-commit install

# 运行代码检查
black human_review_service/
isort human_review_service/
flake8 human_review_service/
mypy human_review_service/
```

### 贡献指南

1. Fork项目
2. 创建功能分支
3. 编写测试
4. 提交代码
5. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目维护者: 索克生活开发团队
- 邮箱: dev@suokelife.com
- 文档: https://docs.suokelife.com

---

**索克生活 - 将中医智慧数字化，融入现代生活场景** 