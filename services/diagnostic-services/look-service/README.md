# Look Service - 索克生活望诊微服务

基于计算机视觉的中医望诊智能分析系统，使用 Python 3.13.3 和现代化开发工具构建。

## 🚀 特性

- **现代化架构**: 基于 FastAPI 的异步 Web 框架
- **类型安全**: 完整的 Python 类型注解和 MyPy 严格检查
- **高性能**: 使用 UV 包管理器和优化的依赖管理
- **可观测性**: 集成 Prometheus 指标、结构化日志和健康检查
- **安全性**: 内置安全中间件、限流和异常处理
- **测试覆盖**: 完整的单元测试和集成测试套件

## 📋 技术栈

- **Python**: 3.13.3
- **包管理**: UV (现代化 Python 包管理器)
- **Web框架**: FastAPI + Uvicorn
- **图像处理**: OpenCV, Pillow, NumPy
- **机器学习**: ONNX Runtime, scikit-learn
- **数据库**: PostgreSQL (AsyncPG), Redis, MongoDB
- **监控**: Prometheus, Structlog, Loguru
- **测试**: Pytest, pytest-asyncio, pytest-cov
- **代码质量**: Ruff, MyPy

## 🏗️ 项目结构

```
look-service/
├── look_service/                 # 主包目录
│   ├── __init__.py              # 包初始化
│   ├── api/                     # API 层
│   │   ├── app.py              # FastAPI 应用工厂
│   │   └── routes/             # API 路由
│   │       ├── analysis.py     # 分析相关路由
│   │       └── health.py       # 健康检查路由
│   ├── core/                   # 核心配置
│   │   ├── config.py          # 配置管理
│   │   └── logging.py         # 日志配置
│   ├── exceptions/             # 异常处理
│   │   ├── base.py            # 基础异常类
│   │   └── handlers.py        # 异常处理器
│   ├── middleware/             # 中间件
│   │   ├── logging.py         # 日志中间件
│   │   ├── metrics.py         # 指标中间件
│   │   ├── rate_limit.py      # 限流中间件
│   │   └── security.py        # 安全中间件
│   ├── utils/                  # 工具函数
│   │   ├── image_utils.py     # 图像处理工具
│   │   └── time_utils.py      # 时间工具
│   └── cmd/                    # 命令行工具
│       └── server.py          # 服务器启动脚本
├── tests/                      # 测试目录
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── conftest.py           # 测试配置
├── pyproject.toml             # 项目配置
├── Makefile                   # 开发任务
├── env.example               # 环境变量示例
└── README.md                 # 项目文档
```

## 🛠️ 开发环境设置

### 前置要求

- Python 3.13.3+
- UV 包管理器

### 安装 UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 项目设置

```bash
# 克隆项目
git clone <repository-url>
cd look-service

# 安装依赖
uv sync

# 复制环境变量文件
cp env.example .env

# 运行测试
uv run pytest

# 启动开发服务器
uv run uvicorn look_service.api.app:create_app --factory --reload
```

## 📝 使用 Makefile

项目提供了便捷的 Makefile 命令：

```bash
# 查看所有可用命令
make help

# 安装依赖
make install-dev

# 运行测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 代码格式化
make format

# 代码检查
make lint

# 启动开发服务器
make run-dev

# 清理生成文件
make clean
```

## 🔧 配置

### 环境变量

主要配置项（详见 `env.example`）：

```bash
# 服务配置
SERVICE_NAME=look-service
SERVICE_VERSION=1.0.0
HOST=0.0.0.0
PORT=8080

# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=look_service

REDIS_HOST=localhost
REDIS_PORT=6379

# 机器学习配置
ML_MODEL_PATH=/path/to/models
ML_BATCH_SIZE=32
ML_CONFIDENCE_THRESHOLD=0.8
```

### 配置层次

配置系统支持多层次配置：

1. 默认配置（代码中定义）
2. 环境变量
3. `.env` 文件
4. 命令行参数

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
make docker-build

# 运行容器
make docker-run
```

### 生产环境

```bash
# 安装生产依赖
uv sync --no-dev

# 启动服务器
uv run python -m look_service.cmd.server
```

## 📊 API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

### 主要 API 端点

- `GET /health` - 基础健康检查
- `GET /health/detailed` - 详细健康检查
- `POST /api/v1/analysis/face` - 面部分析
- `POST /api/v1/analysis/tongue` - 舌诊分析
- `POST /api/v1/analysis/eye` - 眼部分析
- `POST /api/v1/analysis/batch` - 批量分析
- `GET /api/v1/analysis/{analysis_id}` - 获取分析结果

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest tests/unit/

# 运行集成测试
uv run pytest tests/integration/

# 生成覆盖率报告
uv run pytest --cov=look_service --cov-report=html
```

### 测试覆盖率

当前测试覆盖率：**57%**

主要覆盖的模块：
- 配置管理: 99%
- 图像工具: 88%
- 健康检查: 72%

## 📈 监控和指标

### Prometheus 指标

服务暴露以下指标：

- `http_requests_total` - HTTP 请求总数
- `http_request_duration_seconds` - 请求响应时间
- `http_request_size_bytes` - 请求大小
- `http_response_size_bytes` - 响应大小
- `image_processing_duration_seconds` - 图像处理时间
- `ml_model_inference_duration_seconds` - 模型推理时间

访问 `http://localhost:9090/metrics` 查看指标。

### 日志

使用结构化日志，支持：

- JSON 格式输出
- 上下文信息追踪
- 多级别日志
- 文件轮转

## 🔒 安全性

### 安全特性

- HTTP 安全头设置
- 请求限流
- 输入验证
- 异常处理
- 敏感信息脱敏

### 限流配置

默认限流设置：
- 每分钟 100 请求
- 突发限制 10 请求/秒

## 🤝 开发指南

### 代码风格

项目使用以下工具确保代码质量：

- **Ruff**: 代码格式化和 linting
- **MyPy**: 静态类型检查
- **Pytest**: 测试框架

### 提交前检查

```bash
# 运行所有检查
make check-all

# 或者分别运行
make lint
make test
make security-check
```

### 添加新功能

1. 在 `look_service/` 下添加新模块
2. 编写对应的测试
3. 更新 API 文档
4. 运行测试和代码检查

## 📚 依赖管理

### 添加新依赖

```bash
# 添加生产依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 添加可选依赖
uv add --optional gpu package-name
```

### 依赖组

- `dev`: 开发工具（测试、linting 等）
- `gpu`: GPU 加速支持
- `cloud`: 云服务集成

## 🐛 故障排除

### 常见问题

1. **导入错误**: 确保使用 `uv run` 运行命令
2. **端口占用**: 修改 `.env` 中的 `PORT` 配置
3. **依赖冲突**: 运行 `uv sync` 重新同步依赖

### 日志查看

```bash
# 查看服务日志
make logs

# 查看指标
make metrics

# 健康检查
make health
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**索克生活团队** - 让中医智慧数字化，融入现代生活 