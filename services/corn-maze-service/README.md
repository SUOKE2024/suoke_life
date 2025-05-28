# Corn Maze Service

> 索克生活迷宫探索微服务 - 提供游戏化健康知识学习体验

[![Python](https://img.shields.io/badge/Python-3.13.3-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com)
[![gRPC](https://img.shields.io/badge/gRPC-1.68.0-orange.svg)](https://grpc.io)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## 📖 项目简介

Corn Maze Service 是"索克生活（Suoke Life）"项目的核心微服务之一，专注于提供游戏化的健康知识学习体验。通过迷宫探索的方式，将中医养生知识和现代预防医学技术相结合，为用户创造有趣且富有教育意义的健康管理体验。

### 🎯 核心特性

- **🎮 游戏化学习**: 通过迷宫探索的方式学习健康知识
- **🏥 中医结合**: 融合传统中医智慧与现代医学技术
- **🤖 AI 驱动**: 由四个智能体（小艾、小克、老克、索儿）提供个性化指导
- **📊 进度追踪**: 完整的学习进度和成就系统
- **🔄 实时同步**: 支持多设备同步学习进度
- **📈 数据分析**: 提供详细的学习分析和健康建议

### 🏗️ 技术架构

- **语言**: Python 3.13.3
- **框架**: FastAPI + gRPC
- **包管理**: UV (现代化 Python 包管理器)
- **数据库**: SQLite/PostgreSQL + Redis
- **监控**: Prometheus + OpenTelemetry
- **日志**: Structlog (结构化日志)
- **测试**: Pytest + Coverage
- **代码质量**: Ruff + MyPy

## 🚀 快速开始

### 环境要求

- Python 3.13.3+
- UV 包管理器
- Redis (可选，用于缓存)
- Docker (可选，用于容器化部署)

### 安装 UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 快速启动

```bash
# 克隆项目
git clone https://github.com/suokelife/suoke_life.git
cd suoke_life/services/corn-maze-service

# 快速开始（自动设置环境并启动服务）
make quick-start
```

### 手动设置

```bash
# 1. 安装依赖
make install

# 2. 设置开发环境
make setup-dev

# 3. 编辑环境配置
cp env.example .env
# 编辑 .env 文件配置必要的环境变量

# 4. 启动服务
make dev
```

## 📚 API 文档

服务启动后，可以通过以下地址访问 API 文档：

- **Swagger UI**: http://localhost:51057/docs
- **ReDoc**: http://localhost:51057/redoc
- **OpenAPI JSON**: http://localhost:51057/openapi.json

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/mazes` | GET | 获取迷宫列表 |
| `/api/v1/mazes` | POST | 创建新迷宫 |
| `/api/v1/mazes/{id}` | GET | 获取迷宫详情 |
| `/api/v1/mazes/{id}` | DELETE | 删除迷宫 |

### gRPC 服务

- **端口**: 50057
- **反射**: 启用（开发环境）
- **健康检查**: 启用

## 🛠️ 开发指南

### 项目结构

```
corn-maze-service/
├── corn_maze_service/          # 主要源代码
│   ├── __init__.py            # 包初始化
│   ├── config/                # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py        # 应用设置
│   ├── pkg/                   # 共享包
│   │   ├── __init__.py
│   │   └── logging.py         # 日志配置
│   ├── cmd/                   # 命令行入口
│   │   └── server/            # 服务器启动
│   │       ├── __init__.py
│   │       └── main.py        # 主入口
│   └── internal/              # 内部模块
│       ├── __init__.py
│       ├── delivery/          # 交付层
│       │   ├── __init__.py
│       │   ├── http.py        # HTTP API
│       │   └── grpc.py        # gRPC 服务
│       └── model/             # 数据模型
│           ├── __init__.py
│           └── maze.py        # 迷宫模型
├── tests/                     # 测试代码
├── scripts/                   # 开发脚本
├── pyproject.toml            # 项目配置
├── Makefile                  # 开发工具
└── README.md                 # 项目文档
```

### 开发命令

```bash
# 安装依赖
make install

# 启动开发服务器
make dev

# 启动开发服务器（自动重载）
make dev-reload

# 运行测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 代码检查
make lint

# 格式化代码
make format

# 类型检查
make type-check

# 运行所有检查
make check-all

# 清理临时文件
make clean

# 查看所有可用命令
make help
```

### 代码规范

项目使用以下工具确保代码质量：

- **Ruff**: 代码检查和格式化
- **MyPy**: 静态类型检查
- **Pytest**: 单元测试和集成测试
- **Coverage**: 测试覆盖率

### 提交规范

请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 添加新的迷宫生成算法
fix: 修复迷宫节点连接问题
docs: 更新 API 文档
test: 添加迷宫模型测试
refactor: 重构配置管理模块
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

# 运行端到端测试
make test-e2e

# 生成覆盖率报告
make test-cov
```

### 测试结构

```
tests/
├── conftest.py              # 测试配置和夹具
├── test_config.py           # 配置测试
├── test_http_api.py         # HTTP API 测试
├── test_models.py           # 模型测试
└── integration/             # 集成测试
    └── test_maze_service.py
```

## 🐳 Docker 部署

### 构建镜像

```bash
make docker-build
```

### 运行容器

```bash
make docker-run
```

### 推送镜像

```bash
make docker-push
```

## 📊 监控和日志

### Prometheus 指标

服务提供 Prometheus 指标端点：

- **端口**: 51058
- **路径**: `/metrics`

### 日志配置

- **开发环境**: 彩色控制台输出
- **生产环境**: JSON 格式结构化日志
- **日志级别**: 可通过环境变量配置

### 健康检查

- **HTTP**: `GET /health`
- **gRPC**: 标准 gRPC 健康检查协议

## 🔧 配置

### 环境变量

主要配置项：

```bash
# 应用配置
APP_NAME="Corn Maze Service"
ENVIRONMENT=development
DEBUG=false

# 服务端口
GRPC__PORT=50057
HTTP__PORT=51057
MONITORING__PROMETHEUS_PORT=51058

# 数据库
DATABASE__URL=sqlite:///./data/corn_maze.db

# Redis
REDIS__URL=redis://localhost:6379/0

# AI 配置
AI__OPENAI_API_KEY=your-api-key
AI__MODEL_NAME=gpt-3.5-turbo
```

完整配置请参考 `env.example` 文件。

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发流程

1. 确保所有测试通过：`make ci-test`
2. 确保代码质量检查通过：`make check-all`
3. 更新相关文档
4. 提交 PR 并等待审核

## 📄 许可证

本项目为专有软件，版权归索克生活团队所有。

## 🆘 支持

如果您遇到问题或有疑问，请：

1. 查看 [文档](https://docs.suokelife.com/services/corn-maze)
2. 搜索 [Issues](https://github.com/suokelife/suoke_life/issues)
3. 创建新的 Issue
4. 联系开发团队：dev@suokelife.com

## 🎉 致谢

感谢所有为"索克生活"项目做出贡献的开发者和用户！

---

**索克生活团队** ❤️ 用技术守护健康