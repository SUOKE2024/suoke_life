# 小克智能体服务 (Xiaoke Service)

小克智能体服务是索克生活健康管理平台的核心AI智能体，专注于中医辨证论治和个性化健康管理。

## 🌟 特性

- **现代化架构**: 基于 FastAPI 构建的高性能异步微服务
- **中医智慧**: 集成传统中医理论与现代AI技术
- **多模态支持**: 支持文本、图像等多种输入方式
- **知识库**: 丰富的中医药知识库和健康管理知识
- **可扩展性**: 模块化设计，易于扩展和维护
- **监控完善**: 完整的日志、指标和健康检查体系

## 🚀 快速开始

### 环境要求

- Python 3.13.3+
- UV (推荐的包管理器)
- PostgreSQL 14+
- MongoDB 6.0+
- Redis 7.0+

### 安装

1. **克隆项目**
```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/agent-services/xiaoke-service
```

2. **创建虚拟环境**
```bash
uv venv --python 3.13.3
source .venv/bin/activate
```

3. **安装依赖**
```bash
# 基础依赖
uv pip install -e .

# 开发依赖
uv pip install -e ".[dev]"

# AI 依赖
uv pip install -e ".[ai]"

# 所有依赖
uv pip install -e ".[all]"
```

4. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

5. **启动服务**
```bash
# 开发模式
xiaoke-dev

# 或者直接运行
python -m xiaoke_service.main
```

## 📖 使用指南

### 命令行工具

小克服务提供了丰富的命令行工具：

```bash
# 启动开发服务器
xiaoke-dev --host 0.0.0.0 --port 8000 --reload

# 查看配置
xiaoke-service config

# 健康检查
xiaoke-service health --check-all

# 数据库管理
xiaoke-service db --create

# 代码质量检查
xiaoke-service check --all

# 与小克对话
xiaoke-service chat "你好，小克"
```

### API 文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要端点

#### 健康检查
```bash
GET /health          # 基础健康检查
GET /ready           # 就绪检查
GET /metrics         # Prometheus 指标
```

#### 智能对话
```bash
POST /api/v1/chat/                    # 发起对话
GET  /api/v1/chat/sessions/{id}/history  # 获取对话历史
```

#### 知识库
```bash
POST /api/v1/knowledge/search         # 搜索知识库
GET  /api/v1/knowledge/categories     # 获取分类
GET  /api/v1/knowledge/items/{id}     # 获取知识条目
```

## 🏗️ 项目结构

```
xiaoke-service/
├── xiaoke_service/           # 主要源代码
│   ├── api/                 # API 路由和处理器
│   │   └── v1/             # API v1 版本
│   ├── core/               # 核心模块
│   │   ├── config.py       # 配置管理
│   │   ├── logging.py      # 日志配置
│   │   └── exceptions.py   # 异常定义
│   ├── middleware/         # 中间件
│   │   ├── auth.py         # 认证中间件
│   │   ├── logging.py      # 日志中间件
│   │   └── rate_limit.py   # 限流中间件
│   ├── services/           # 业务服务
│   │   ├── database.py     # 数据库管理
│   │   └── health.py       # 健康检查
│   ├── main.py             # 应用入口
│   └── cli.py              # 命令行工具
├── tests/                  # 测试代码
├── pyproject.toml          # 项目配置
├── .pre-commit-config.yaml # 预提交钩子
├── env.example             # 环境变量示例
└── README.md               # 项目文档
```

## 🔧 开发

### 代码质量

项目使用现代化的Python开发工具链：

```bash
# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy xiaoke_service

# 运行测试
pytest

# 预提交检查
pre-commit run --all-files
```

### 配置管理

使用 Pydantic Settings 进行类型安全的配置管理：

```python
from xiaoke_service.core.config import settings

# 访问配置
print(settings.service.service_name)
print(settings.database.postgres_url)
print(settings.ai.openai_model)
```

### 日志记录

使用结构化日志记录：

```python
from xiaoke_service.core.logging import get_logger

logger = get_logger(__name__)
logger.info("处理用户请求", user_id="123", action="chat")
```

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
docker build -t xiaoke-service .

# 运行容器
docker run -p 8000:8000 xiaoke-service
```

### Kubernetes 部署

```bash
# 应用配置
kubectl apply -f deploy/kubernetes/
```

## 📊 监控

### 指标收集

服务暴露 Prometheus 指标：

```bash
curl http://localhost:8000/metrics
```

### 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/health

# 详细就绪检查
curl http://localhost:8000/ready
```

### 日志

支持结构化日志输出，可配置为 JSON 格式：

```bash
# 设置日志格式
export MONITORING__LOG_FORMAT=json
```

## 🤝 贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证和设置管理
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包
- [Loguru](https://loguru.readthedocs.io/) - 简化的日志记录

---

**索克生活团队** - 让健康管理更智能 🌱