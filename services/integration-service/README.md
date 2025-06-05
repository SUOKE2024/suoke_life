# Integration Service

索克生活平台第三方健康平台集成服务，提供与 Apple Health、Google Fit、Fitbit、小米健康、华为健康、微信运动、支付宝健康等平台的数据集成功能。

## 🚀 功能特性

### 核心功能
- **多平台集成**: 支持主流健康平台的数据同步
- **统一数据格式**: 将不同平台的数据转换为标准格式
- **实时同步**: 支持实时和定时数据同步
- **数据安全**: 完整的认证授权和数据加密机制
- **高可用性**: 支持集群部署和故障恢复

### 技术特性
- **RESTful API**: 完整的 REST API 接口
- **异步处理**: 基于 FastAPI 的高性能异步处理
- **数据库支持**: PostgreSQL 主数据库，Redis 缓存
- **监控告警**: Prometheus + Grafana 监控体系
- **容器化部署**: Docker 容器化部署
- **自动化测试**: 完整的单元测试和集成测试

## 📋 支持的健康平台

| 平台 | 状态 | 数据类型 | 认证方式 |
|------|------|----------|----------|
| Apple Health | ✅ 已支持 | 步数、心率、血压、体重等 | OAuth 2.0 |
| Google Fit | ✅ 已支持 | 步数、活动、心率等 | OAuth 2.0 |
| Fitbit | 🚧 开发中 | 步数、睡眠、心率等 | OAuth 2.0 |
| 小米健康 | 🚧 开发中 | 步数、心率、体重等 | API Key |
| 华为健康 | 📋 计划中 | 步数、心率、运动等 | OAuth 2.0 |
| 微信运动 | 📋 计划中 | 步数、排行榜等 | 微信授权 |
| 支付宝健康 | 📋 计划中 | 步数、健康档案等 | 支付宝授权 |

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用      │    │   移动应用      │    │   第三方系统    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      API Gateway         │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │  Integration Service     │
                    │  ┌─────────────────────┐ │
                    │  │   认证授权模块      │ │
                    │  ├─────────────────────┤ │
                    │  │   平台管理模块      │ │
                    │  ├─────────────────────┤ │
                    │  │   数据同步模块      │ │
                    │  ├─────────────────────┤ │
                    │  │   数据转换模块      │ │
                    │  └─────────────────────┘ │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
    │PostgreSQL │         │   Redis   │         │第三方平台API│
    │  主数据库 │         │   缓存    │         │           │
    └───────────┘         └───────────┘         └───────────┘
```

## 🛠️ 技术栈

- **后端框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT + OAuth 2.0
- **容器化**: Docker + Docker Compose
- **监控**: Prometheus + Grafana
- **测试**: Pytest + Coverage
- **代码质量**: Ruff + MyPy
- **包管理**: UV

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+ (可选，可使用 Docker)
- Redis 7+ (可选，可使用 Docker)

### 1. 克隆项目

```bash
git clone <repository-url>
cd suoke_life/services/integration-service
```

### 2. 环境配置

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

### 3. 使用 Docker Compose 启动

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f integration-service
```

### 4. 本地开发环境

```bash
# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn integration_service.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 验证安装

```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs
```

## 📚 API 文档

### 认证 API

#### 登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

#### 刷新令牌
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

### 平台管理 API

#### 获取平台列表
```http
GET /api/v1/platforms/
Authorization: Bearer <access_token>
```

#### 创建平台
```http
POST /api/v1/platforms/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "apple_health",
  "display_name": "Apple Health",
  "description": "Apple Health 平台",
  "api_base_url": "https://api.apple.com/health",
  "auth_type": "oauth2"
}
```

### 健康数据 API

#### 获取健康数据
```http
GET /api/v1/health-data/?skip=0&limit=100&platform_id=apple_health
Authorization: Bearer <access_token>
```

#### 创建健康数据
```http
POST /api/v1/health-data/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "platform_id": "apple_health",
  "data_type": "steps",
  "value": 10000,
  "unit": "steps",
  "metadata": {
    "source": "iPhone",
    "device_model": "iPhone 14"
  }
}
```

#### 批量创建健康数据
```http
POST /api/v1/health-data/batch
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "platform_id": "apple_health",
  "data_list": [
    {
      "data_type": "steps",
      "value": 8000,
      "unit": "steps"
    },
    {
      "data_type": "heart_rate",
      "value": 72,
      "unit": "bpm"
    }
  ]
}
```

#### 同步健康数据
```http
POST /api/v1/health-data/sync
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "platform_id": "apple_health",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "data_types": ["steps", "heart_rate"]
}
```

### 集成管理 API

#### 获取集成状态
```http
GET /api/v1/integration/status
Authorization: Bearer <access_token>
```

#### 平台授权
```http
POST /api/v1/integration/authorize
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "platform_id": "apple_health",
  "auth_code": "authorization_code",
  "redirect_uri": "https://your-app.com/callback"
}
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 生成测试覆盖率报告
make test-coverage
```

### 测试覆盖率

当前测试覆盖率：**85%+**

- 单元测试覆盖率：90%+
- 集成测试覆盖率：80%+
- API 测试覆盖率：95%+

## 📊 监控和日志

### Prometheus 指标

服务提供以下监控指标：

- `http_requests_total`: HTTP 请求总数
- `http_request_duration_seconds`: HTTP 请求响应时间
- `database_connections_active`: 活跃数据库连接数
- `sync_operations_total`: 数据同步操作总数
- `sync_operation_duration_seconds`: 数据同步操作耗时

### Grafana 仪表板

访问 http://localhost:3000 查看监控仪表板：

- 系统概览仪表板
- API 性能仪表板
- 数据库监控仪表板
- 业务指标仪表板

### 日志配置

```python
# 日志级别配置
LOGGING_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 日志文件路径
LOG_FILE = "/app/logs/integration-service.log"
```

## 🔧 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `DATABASE_URL` | 数据库连接字符串 | - | ✅ |
| `REDIS_URL` | Redis 连接字符串 | - | ✅ |
| `SECRET_KEY` | JWT 密钥 | - | ✅ |
| `DEBUG` | 调试模式 | `false` | ❌ |
| `ALLOWED_HOSTS` | 允许的主机列表 | `localhost` | ❌ |
| `LOG_LEVEL` | 日志级别 | `INFO` | ❌ |

### 数据库配置

```yaml
# config/database.yml
database:
  url: postgresql://user:password@localhost:5432/integration_db
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
```

### Redis 配置

```yaml
# config/redis.yml
redis:
  url: redis://localhost:6379/0
  max_connections: 100
  retry_on_timeout: true
  socket_timeout: 5
```

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
docker build -t integration-service:latest .

# 运行容器
docker run -d \
  --name integration-service \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@db:5432/integration_db \
  -e REDIS_URL=redis://redis:6379/0 \
  integration-service:latest
```

### Kubernetes 部署

```bash
# 应用 Kubernetes 配置
kubectl apply -f k8s/

# 查看部署状态
kubectl get pods -l app=integration-service

# 查看服务
kubectl get svc integration-service
```

### 生产环境配置

```bash
# 设置生产环境变量
export DEBUG=false
export LOG_LEVEL=WARNING
export DATABASE_URL=postgresql://prod_user:prod_password@prod_db:5432/integration_db

# 运行数据库迁移
alembic upgrade head

# 启动生产服务器
gunicorn integration_service.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## 🔒 安全

### 认证和授权

- JWT 令牌认证
- OAuth 2.0 第三方平台授权
- 基于角色的访问控制 (RBAC)
- API 密钥管理

### 数据安全

- 敏感数据加密存储
- HTTPS 强制传输
- 数据脱敏和匿名化
- 审计日志记录

### 安全最佳实践

- 定期更新依赖包
- 安全漏洞扫描
- 访问频率限制
- 输入验证和过滤

## 🤝 贡献指南

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

```bash
# 代码格式化
make format

# 代码检查
make lint

# 类型检查
make type-check

# 运行所有检查
make check
```

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- 📧 邮箱: support@suoke.life
- 📱 微信群: 扫描二维码加入技术交流群
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/suoke_life/issues)
- 📖 文档: [在线文档](https://docs.suoke.life)

## 🗺️ 路线图

### v1.1.0 (计划中)
- [ ] 支持 Fitbit 平台集成
- [ ] 添加数据可视化功能
- [ ] 实现数据导出功能
- [ ] 优化性能和稳定性

### v1.2.0 (计划中)
- [ ] 支持小米健康平台
- [ ] 添加实时数据推送
- [ ] 实现数据分析功能
- [ ] 支持多租户架构

### v2.0.0 (远期规划)
- [ ] 支持所有主流健康平台
- [ ] AI 驱动的健康数据分析
- [ ] 微服务架构重构
- [ ] 云原生部署支持

---

**Integration Service** - 让健康数据集成变得简单 🚀 