# 索儿服务 (Soer Service)

索儿智能体微服务，是"索克生活"健康管理平台的核心组件之一。专注于提供营养分析、健康咨询、生活方式建议和中医养生指导。

## 🌟 特性

### 核心功能
- **营养分析**: 食物营养成分分析、膳食计划制定
- **健康管理**: 健康数据分析、健康趋势监测、个性化建议
- **生活方式**: 运动计划、睡眠分析、压力管理
- **智能对话**: 自然语言交互、个性化响应、情感支持
- **中医养生**: 体质分析、经络指导、季节性养生建议

### 技术特点
- **现代化架构**: 基于 FastAPI 的异步微服务
- **类型安全**: 完整的 Pydantic 模型和类型注解
- **多数据库支持**: MongoDB、Redis、PostgreSQL
- **监控集成**: Prometheus 指标、健康检查
- **代码质量**: 完整的代码质量工具链

## 🚀 快速开始

### 环境要求
- Python 3.13.3+
- UV 包管理器
- MongoDB (可选)
- Redis (可选)
- PostgreSQL (可选)

### 安装依赖

```bash
# 使用 UV 安装依赖
uv sync

# 或使用 pip
pip install -e .
```

### 环境配置

创建 `.env` 文件：

```bash
# 基础配置
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 数据库配置
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://user:password@localhost:5432/soer_db

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# AI 服务配置
OPENAI_API_KEY=your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 启动服务

```bash
# 使用简化启动脚本
python run_service.py

# 使用启动脚本
python scripts/start.py

# 或直接使用 uvicorn
uvicorn soer_service.main:create_app --factory --reload --host 0.0.0.0 --port 8003
```

### Docker 部署

```bash
# 构建镜像
docker build -t soer-service .

# 运行容器
docker run -p 8003:8003 soer-service

# 使用 docker-compose
docker-compose up -d
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_basic.py

# 生成覆盖率报告
pytest --cov=soer_service --cov-report=html
```

## 📚 API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
- **OpenAPI JSON**: http://localhost:8003/openapi.json
- **健康检查**: http://localhost:8003/health
- **监控指标**: http://localhost:8003/metrics

### 主要端点

#### 健康检查
```http
GET /health
```

#### 智能体交互
```http
POST /api/v1/agent/chat
GET /api/v1/agent/capabilities
GET /api/v1/agent/history/{user_id}
```

#### 营养分析
```http
POST /api/v1/nutrition/analyze
POST /api/v1/nutrition/diet-plan
GET /api/v1/nutrition/search
GET /api/v1/nutrition/recommendations/{user_id}
```

#### 健康管理
```http
POST /api/v1/health/data
GET /api/v1/health/analysis/{user_id}
GET /api/v1/health/dashboard/{user_id}
GET /api/v1/health/trends/{user_id}
```

#### 生活方式
```http
POST /api/v1/lifestyle/exercise-plan
POST /api/v1/lifestyle/sleep-analysis
POST /api/v1/lifestyle/stress-assessment
GET /api/v1/lifestyle/recommendations/{user_id}
```

## 🏗️ 项目结构

```
soer-service/
├── soer_service/           # 主要源代码
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   │   ├── __init__.py
│   │   ├── routes.py      # 主路由器
│   │   └── endpoints/     # 具体端点
│   ├── config/            # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py    # 应用设置
│   ├── core/              # 核心功能
│   │   ├── __init__.py
│   │   ├── database.py    # 数据库连接
│   │   ├── logging.py     # 日志配置
│   │   └── monitoring.py  # 监控指标
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── agent.py       # 智能体模型
│   │   ├── health.py      # 健康模型
│   │   ├── lifestyle.py   # 生活方式模型
│   │   └── nutrition.py   # 营养模型
│   └── services/          # 业务逻辑
│       ├── __init__.py
│       ├── base_service.py
│       ├── agent_service.py
│       ├── health_service.py
│       ├── lifestyle_service.py
│       └── nutrition_service.py
├── scripts/               # 脚本文件
│   └── start.py          # 启动脚本
├── tests/                 # 测试文件
│   └── test_basic.py     # 基础测试
├── .python-version       # Python 版本
├── pyproject.toml        # 项目配置
├── README.md             # 项目说明
└── requirements.txt      # 依赖列表
```

## 🔧 开发指南

### 代码质量

项目集成了完整的代码质量工具链：

```bash
# 代码格式化
black soer_service/
isort soer_service/

# 代码检查
ruff check soer_service/
mypy soer_service/
pylint soer_service/

# 运行所有质量检查
pre-commit run --all-files
```

### 添加新功能

1. **创建数据模型**: 在 `models/` 目录下定义 Pydantic 模型
2. **实现业务逻辑**: 在 `services/` 目录下创建服务类
3. **添加 API 端点**: 在 `api/endpoints/` 目录下创建路由
4. **编写测试**: 在 `tests/` 目录下添加测试用例
5. **更新文档**: 更新 README 和 API 文档

### 数据库迁移

```bash
# 创建迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t soer-service:latest .
```

### 运行容器

```bash
docker run -d \
  --name soer-service \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e MONGODB_URL=mongodb://mongo:27017 \
  soer-service:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  soer-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis
  
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## 📊 监控和日志

### Prometheus 指标

服务暴露以下 Prometheus 指标：

- `http_requests_total`: HTTP 请求总数
- `http_request_duration_seconds`: HTTP 请求持续时间
- `active_connections`: 活跃连接数
- `database_operations_total`: 数据库操作总数

访问 `/metrics` 端点获取指标数据。

### 日志配置

支持多种日志格式和输出：

- **控制台输出**: 开发环境彩色日志
- **JSON 格式**: 生产环境结构化日志
- **文件轮转**: 自动日志文件管理
- **远程日志**: 支持发送到日志聚合服务

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建过程或辅助工具的变动
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证和设置管理
- [UV](https://github.com/astral-sh/uv) - 快速的 Python 包管理器
- [MongoDB](https://www.mongodb.com/) - 文档数据库
- [Redis](https://redis.io/) - 内存数据结构存储

## 📞 联系方式

- 项目主页: [索克生活](https://github.com/your-org/suoke-life)
- 问题反馈: [Issues](https://github.com/your-org/suoke-life/issues)
- 邮箱: support@suoke-life.com

---

**索儿智能体** - 您的个人健康管理助手 🌱