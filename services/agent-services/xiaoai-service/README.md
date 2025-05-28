# 小艾智能体服务 (XiaoAI Agent Service)

[![Python Version](https://img.shields.io/badge/python-3.13.3-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

小艾是索克生活平台的核心AI智能体，专注于提供智能健康管理服务。本服务基于中医"辨证论治未病"的理念，结合现代预防医学技术，为用户提供个性化的全生命周期健康管理。

## 🌟 核心特性

### 🧠 智能诊断
- **四诊协调**: 集成望、闻、问、切四种诊断方式
- **辨证论治**: 基于中医理论的智能症候分析
- **多模态数据**: 支持文本、图像、音频等多种数据输入
- **个性化建议**: 根据用户体质提供定制化健康建议

### 🔬 技术架构
- **微服务架构**: 基于 FastAPI 的高性能异步服务
- **AI 模型集成**: 支持本地和云端 AI 模型
- **分布式任务**: 基于 Celery 的异步任务处理
- **实时监控**: 完整的健康检查和监控体系

### 🛡️ 安全与隐私
- **数据加密**: 端到端健康数据加密
- **访问控制**: 基于 JWT 的身份认证
- **隐私保护**: 符合医疗数据隐私标准
- **审计日志**: 完整的操作审计追踪

## 📋 系统要求

- **Python**: 3.13.3+
- **数据库**: PostgreSQL 14+
- **缓存**: Redis 6+
- **消息队列**: Redis (Celery broker)
- **操作系统**: Linux, macOS, Windows

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/suokelife/suoke_life.git
cd suoke_life/services/agent-services/xiaoai-service

# 确保 Python 3.13.3 已安装
python --version

# 安装 UV 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装依赖

```bash
# 安装核心依赖
make install

# 或安装所有依赖（包括开发和AI依赖）
make install-all
```

### 3. 配置环境

```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件
vim .env
```

### 4. 初始化服务

```bash
# 初始化项目（配置、数据库、缓存等）
make init

# 或分步初始化
make init-config
make init-db
```

### 5. 启动服务

```bash
# 启动开发服务器
make run-dev

# 或启动生产服务器
make run

# 启动工作进程（另一个终端）
make run-worker
```

### 6. 验证安装

```bash
# 检查服务状态
make status

# 健康检查
make health

# 访问 API 文档
open http://localhost:8000/docs
```

## 🛠️ 开发指南

### 项目结构

```
xiaoai-service/
├── xiaoai/                     # 主要源码目录
│   ├── __init__.py            # 包初始化和延迟导入
│   ├── agent/                 # 智能体核心模块
│   ├── cli/                   # 命令行接口
│   ├── config/                # 配置管理
│   ├── delivery/              # API 交付层
│   ├── four_diagnosis/        # 四诊协调模块
│   ├── service/               # 业务服务层
│   └── utils/                 # 工具函数
├── tests/                     # 测试代码
├── config/                    # 配置文件
├── docs/                      # 文档
├── scripts/                   # 脚本工具
├── pyproject.toml            # 项目配置
├── Makefile                  # 开发工具
└── README.md                 # 项目说明
```

### 开发环境设置

```bash
# 完整开发环境设置
make dev-setup

# 安装开发依赖
make install-dev

# 安装 AI/ML 依赖
make install-ai
```

### 代码质量

```bash
# 代码格式化
make format

# 代码检查
make lint

# 类型检查
make type-check

# 安全检查
make security-check

# 运行所有质量检查
make quality
```

### 测试

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 生成覆盖率报告
make test-coverage

# 监视模式（自动运行测试）
make test-watch
```

## 📚 API 文档

### 核心端点

- **健康检查**: `GET /health`
- **服务状态**: `GET /status`
- **四诊分析**: `POST /api/v1/diagnosis/analyze`
- **健康建议**: `POST /api/v1/advice/generate`
- **用户画像**: `GET /api/v1/profile/{user_id}`

### 认证

所有 API 请求需要在 Header 中包含 JWT token：

```bash
Authorization: Bearer <your-jwt-token>
```

### 示例请求

```bash
# 健康检查
curl -X GET "http://localhost:8000/health"

# 四诊分析
curl -X POST "http://localhost:8000/api/v1/diagnosis/analyze" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "12345",
    "symptoms": ["头痛", "失眠"],
    "images": ["base64-encoded-image"],
    "audio": "base64-encoded-audio"
  }'
```

## 🔧 配置说明

### 环境变量

主要配置项说明：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | `development` |
| `SERVER_PORT` | 服务端口 | `8000` |
| `DATABASE_URL` | 数据库连接 | `postgresql://...` |
| `REDIS_URL` | Redis 连接 | `redis://localhost:6379/0` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### 配置文件

支持多环境配置文件：

- `config/default.yaml` - 默认配置
- `config/development.yaml` - 开发环境
- `config/production.yaml` - 生产环境

## 🐳 Docker 部署

### 构建镜像

```bash
# 构建 Docker 镜像
make docker-build

# 运行容器
make docker-run
```

### Docker Compose

```yaml
version: '3.8'
services:
  xiaoai-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/xiaoai
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: xiaoai
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  
  redis:
    image: redis:6-alpine
```

## 📊 监控和日志

### 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/health

# 详细状态检查
xiaoai status --format json
```

### 日志管理

```bash
# 查看实时日志
tail -f logs/xiaoai.log

# 日志级别配置
export LOG_LEVEL=DEBUG
```

### 性能监控

```bash
# 性能分析
make profile

# 系统资源监控
xiaoai health
```

## 🧪 测试策略

### 测试分类

- **单元测试**: 测试单个函数和类
- **集成测试**: 测试服务间交互
- **端到端测试**: 测试完整用户流程
- **性能测试**: 测试系统性能指标

### 测试覆盖率

目标覆盖率: **80%+**

```bash
# 生成覆盖率报告
make test-coverage

# 查看 HTML 报告
open htmlcov/index.html
```

## 🚀 部署指南

### 生产环境部署

1. **环境准备**
   ```bash
   # 设置生产环境变量
   export ENVIRONMENT=production
   export DATABASE_URL=postgresql://...
   export REDIS_URL=redis://...
   ```

2. **数据库迁移**
   ```bash
   make db-migrate
   ```

3. **启动服务**
   ```bash
   # 启动服务器（多进程）
   xiaoai-server --workers 4 --host 0.0.0.0 --port 8000
   
   # 启动工作进程
   xiaoai-worker --concurrency 8
   ```

### Kubernetes 部署

参考 `deploy/kubernetes/` 目录下的配置文件。

## 🤝 贡献指南

### 开发流程

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写完整的文档字符串
- 保持测试覆盖率 80% 以上

### 提交前检查

```bash
# 运行提交前检查
make pre-commit
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持与帮助

### 常见问题

**Q: 如何重置数据库？**
```bash
make db-downgrade
make db-migrate
```

**Q: 如何更新依赖？**
```bash
uv sync --upgrade
```

**Q: 如何调试性能问题？**
```bash
make profile
```

### 获取帮助

- 📧 邮箱: dev@suokelife.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/suokelife/suoke_life/issues)
- 📖 文档: [在线文档](https://docs.suokelife.com/xiaoai)

### 社区

- 💬 讨论: [GitHub Discussions](https://github.com/suokelife/suoke_life/discussions)
- 📢 公告: [项目博客](https://blog.suokelife.com)

---

**小艾智能体** - 让健康管理更智能，让生活更美好 ✨ 