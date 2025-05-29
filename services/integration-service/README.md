# Integration Service

索克生活第三方健康平台集成服务

## 概述

Integration Service 是索克生活平台的核心组件之一，负责与各种第三方健康平台进行数据集成，为用户提供统一的健康数据管理体验。

## 支持的平台

- **Apple Health** - iOS 健康应用数据集成
- **Google Fit** - Android 健康数据集成
- **Fitbit** - 智能手环和健康设备数据
- **小米健康** - 小米生态健康设备数据
- **华为健康** - 华为生态健康设备数据
- **微信运动** - 微信运动步数等数据
- **支付宝健康** - 支付宝健康相关数据

## 技术栈

- **Python 3.13.3** - 主要编程语言
- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM 框架
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和会话存储
- **UV** - 包管理工具
- **Ruff** - 代码格式化和检查
- **Pytest** - 测试框架

## 项目结构

```
integration-service/
├── integration_service/          # 主应用包
│   ├── models/                   # 数据模型
│   ├── services/                 # 业务逻辑层
│   ├── api/                      # API 路由
│   ├── config.py                 # 配置管理
│   └── main.py                   # 应用入口
├── test/                         # 测试文件
├── config/                       # 配置文件
├── pyproject.toml               # 项目配置
├── run.py                       # 启动脚本
└── README.md                    # 项目说明
```

## 快速开始

### 环境要求

- Python 3.13.3+
- PostgreSQL 12+
- Redis 6+

### 安装依赖

```bash
# 使用 UV 安装依赖
uv sync

# 或者安装开发依赖
uv sync --extra dev
```

### 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

### 运行服务

```bash
# 开发模式
python run.py

# 或使用 UV
uv run python run.py
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=integration_service
```

## API 文档

服务启动后，可以通过以下地址访问 API 文档：

- Swagger UI: http://localhost:8090/docs
- ReDoc: http://localhost:8090/redoc

## 开发指南

### 代码规范

项目使用 Ruff 进行代码格式化和检查：

```bash
# 检查代码
uv run ruff check integration_service/

# 自动修复
uv run ruff check integration_service/ --fix

# 格式化代码
uv run ruff format integration_service/
```

### 类型检查

使用 MyPy 进行类型检查：

```bash
uv run mypy integration_service/
```

### 数据库迁移

使用 Alembic 管理数据库迁移：

```bash
# 生成迁移文件
uv run alembic revision --autogenerate -m "描述"

# 执行迁移
uv run alembic upgrade head
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t integration-service .

# 运行容器
docker run -p 8090:8090 integration-service
```

### Kubernetes 部署

参考 `deploy/kubernetes/` 目录下的配置文件。

## 监控和日志

- **健康检查**: `/health`
- **指标监控**: `/metrics` (Prometheus 格式)
- **日志**: 使用 structlog 结构化日志

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

- 项目主页: https://github.com/suokelife/integration-service
- 问题反馈: https://github.com/suokelife/integration-service/issues
- 邮箱: dev@suokelife.com 