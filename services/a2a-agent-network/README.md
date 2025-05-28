# A2A 智能体网络微服务

[![Python 3.13.3](https://img.shields.io/badge/python-3.13.3-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/uv-latest-green.svg)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

索克生活健康管理平台的智能体协作服务，负责管理和协调四个核心智能体（小艾、小克、老克、索儿）之间的通信和工作流编排。

## 🚀 特性

- **智能体管理**: 统一管理四个核心智能体的生命周期
- **工作流编排**: 支持复杂的多智能体协作工作流
- **实时通信**: 基于 WebSocket 和 gRPC 的高性能通信
- **健康监控**: 完整的健康检查和指标监控
- **配置管理**: 灵活的配置管理和环境适配
- **现代化架构**: 使用 Python 3.13.3 和 UV 包管理器

## 🛠️ 技术栈

- **Python**: 3.13.3
- **包管理**: UV (现代化的 Python 包管理器)
- **Web框架**: Flask 3.x
- **通信**: gRPC, WebSocket, HTTP
- **数据验证**: Pydantic 2.x
- **数据库**: MongoDB (Motor), Redis
- **监控**: Prometheus, OpenTelemetry
- **容器化**: Docker, Kubernetes

## 📋 系统要求

- Python 3.13.3+
- UV 包管理器
- Docker (可选)
- Kubernetes (生产环境)

## 🔧 快速开始

### 1. 安装 UV 包管理器

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目

```bash
git clone https://github.com/suoke-life/a2a-agent-network.git
cd a2a-agent-network
```

### 3. 设置开发环境

```bash
# 使用 Makefile 快速设置
make setup-dev

# 或手动设置
uv venv .venv --python 3.13.3
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
uv pip install -e ".[dev,monitoring]"
```

### 4. 配置环境

```bash
# 复制配置模板
cp config/config.yaml.example config/config.yaml

# 编辑配置文件
vim config/config.yaml
```

### 5. 启动服务

```bash
# 开发模式
make run-dev

# 或使用启动脚本
./scripts/start.sh

# 或直接运行
python cmd/server/main.py
```

## 📚 开发指南

### 项目结构

```
a2a-agent-network/
├── api/                    # API 定义
│   ├── grpc/              # gRPC 服务定义
│   └── rest/              # REST API 定义
├── cmd/                   # 应用入口
│   ├── cli/               # CLI 工具
│   └── server/            # 服务器入口
├── config/                # 配置文件
├── deploy/                # 部署配置
│   ├── docker/            # Docker 配置
│   └── kubernetes/        # K8s 配置
├── docs/                  # 文档
├── internal/              # 内部模块
│   ├── model/             # 数据模型
│   └── service/           # 业务服务
├── pkg/                   # 公共包
├── scripts/               # 脚本工具
└── test/                  # 测试代码
```

### 常用命令

```bash
# 查看所有可用命令
make help

# 代码格式化
make format

# 代码检查
make lint

# 类型检查
make type-check

# 运行测试
make test

# 生成覆盖率报告
make test-cov

# 安全检查
make security

# 运行所有检查
make check-all
```

### 开发工作流

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **开发和测试**
   ```bash
   # 安装开发依赖
   make install-dev
   
   # 运行测试
   make test
   
   # 代码检查
   make check-all
   ```

3. **提交代码**
   ```bash
   # pre-commit 会自动运行检查
   git add .
   git commit -m "feat: add your feature"
   ```

4. **推送和创建 PR**
   ```bash
   git push origin feature/your-feature
   ```

## 🐳 Docker 部署

### 构建镜像

```bash
# 构建 Docker 镜像
make docker-build

# 或手动构建
docker build -t suoke-life/a2a-agent-network:latest .
```

### 运行容器

```bash
# 使用 Docker Compose
docker-compose up -d

# 或使用 Makefile
make docker-run
```

## ☸️ Kubernetes 部署

### 开发环境

```bash
# 部署到开发环境
make deploy-dev
```

### 生产环境

```bash
# 部署到生产环境
make deploy-prod
```

## 📊 监控和日志

### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:5000/health

# 或使用 Makefile
make health
```

### 指标监控

```bash
# 查看 Prometheus 指标
curl http://localhost:5000/metrics

# 或使用 Makefile
make metrics
```

### 日志查看

```bash
# 查看应用日志
make logs

# 查看 Docker 容器日志
make docker-logs
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

# 生成覆盖率报告
make test-cov
```

### 测试覆盖率

项目目标是保持 90% 以上的测试覆盖率。

## 📖 API 文档

- [REST API 文档](docs/API.md)
- [gRPC API 文档](api/grpc/README.md)
- [WebSocket API 文档](docs/websocket.md)

## 🔧 配置说明

详细的配置说明请参考 [配置文档](docs/configuration.md)。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

请确保：
- 遵循代码风格指南
- 添加适当的测试
- 更新相关文档
- 通过所有检查

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🆘 支持

如果您遇到问题或有疑问：

1. 查看 [文档](docs/)
2. 搜索 [Issues](https://github.com/suoke-life/a2a-agent-network/issues)
3. 创建新的 Issue
4. 联系维护团队

## 🔗 相关链接

- [索克生活主项目](https://github.com/suoke-life/suoke-life)
- [智能体服务文档](../agent-services/README.md)
- [部署指南](docs/deployment.md)
- [故障排除](docs/troubleshooting.md)

---

**索克生活团队** - 让健康管理更智能 🌟 