# 索克生活 API 网关

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

索克生活项目的现代化 API 网关服务，基于 FastAPI 构建，提供高性能、可扩展的微服务网关解决方案。

## 🚀 特性

### 核心功能
- **服务发现与注册**: 自动服务注册和健康检查
- **负载均衡**: 支持轮询、加权轮询、最少连接、随机等策略
- **请求代理**: 高性能的 HTTP/gRPC 请求代理
- **熔断器**: 防止级联故障的熔断器模式
- **限流**: 基于 Redis 的分布式限流
- **缓存**: 智能缓存管理和策略

### 安全特性
- **JWT 认证**: 完整的 JWT 令牌验证
- **CORS 支持**: 跨域资源共享配置
- **安全头部**: 自动添加安全相关的 HTTP 头部
- **输入验证**: 基于 Pydantic 的数据验证

### 可观测性
- **结构化日志**: 基于 structlog 的结构化日志记录
- **指标监控**: Prometheus 指标导出
- **链路追踪**: 分布式链路追踪支持
- **健康检查**: 多维度健康状态监控

### 开发体验
- **现代化工具链**: 使用 UV 包管理器和 Python 3.13
- **类型安全**: 完整的类型注解和 MyPy 检查
- **代码质量**: 集成 Ruff、Bandit 等代码质量工具
- **自动化测试**: 完整的单元测试和集成测试

## 📋 系统要求

- Python 3.13+
- Redis 6.0+
- UV 包管理器

## 🛠️ 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd suoke_life/services/api-gateway
```

### 2. 一键启动开发环境（推荐）

使用开发启动脚本，自动检查环境、安装依赖、配置服务并启动：

```bash
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
```

### 3. 自动化设置

或者运行设置脚本，手动安装依赖和配置环境：

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 4. 配置环境

复制环境变量模板并根据需要修改：

```bash
cp .env.example .env
```

主要配置项：

```env
# 应用配置
ENVIRONMENT=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT 配置
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# 限流配置
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT_RATE=100/minute
```

### 5. 启动服务

#### 开发模式

```bash
# 使用 UV 运行
uv run python -m suoke_api_gateway dev

# 或者激活虚拟环境后运行
source .venv/bin/activate
python -m suoke_api_gateway dev
```

#### 生产模式

```bash
uv run python -m suoke_api_gateway serve --workers 4
```

### 6. 验证安装

访问以下端点验证服务正常运行：

- **管理仪表板**: http://localhost:8000/admin/
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **指标监控**: http://localhost:8000/metrics/prometheus
- **系统信息**: http://localhost:8000/metrics/system-info
- **配置信息**: http://localhost:8000/metrics/config

### 7. 功能演示

#### WebSocket 实时通信

```bash
# 运行 WebSocket 客户端示例
python examples/websocket_client.py
```

支持的功能：
- 实时消息传递
- 房间管理
- 连接状态监控
- 多客户端演示

#### OAuth2 认证

```bash
# 运行 OAuth2 客户端示例
python examples/oauth2_client.py
```

支持的流程：
- 客户端凭证流程
- 授权码流程
- OpenID Connect
- 令牌管理

## 🛠️ 运维工具

### 监控工具

项目提供了实时监控工具，可以监控 API 网关的运行状态：

```bash
# 启动实时监控仪表板
python scripts/monitor.py

# 简单模式监控（非交互式）
python scripts/monitor.py --simple

# 自定义监控参数
python scripts/monitor.py --url http://localhost:8000 --interval 10

# 导出监控数据
python scripts/monitor.py --export metrics_data.json
```

监控功能包括：
- 🏥 健康状态检查
- 📊 实时性能指标
- 💻 系统资源监控
- 🚨 智能告警系统
- 📈 历史数据记录

### 性能测试工具

内置性能测试工具，支持多种测试场景：

```bash
# 基本性能测试
python scripts/benchmark.py --url http://localhost:8000/health

# 高并发测试
python scripts/benchmark.py --concurrent 100 --requests 5000

# 持续负载测试
python scripts/benchmark.py --duration 300 --concurrent 50

# 运行完整测试套件
python scripts/benchmark.py --suite

# 导出测试结果
python scripts/benchmark.py --export test_results.json
```

测试功能包括：
- 🚀 并发性能测试
- ⏱️ 响应时间分析
- 📈 吞吐量测试
- 🔄 持续负载测试
- 📊 详细统计报告

## 🏗️ 项目结构

```
suoke_api_gateway/
├── core/                   # 核心模块
│   ├── app.py             # FastAPI 应用工厂
│   ├── config.py          # 配置管理
│   └── logging.py         # 日志配置
├── models/                # 数据模型
│   ├── gateway.py         # 网关相关模型
│   └── common.py          # 通用模型
├── middleware/            # 中间件
│   ├── auth.py           # 认证中间件
│   ├── logging.py        # 日志中间件
│   ├── rate_limit.py     # 限流中间件
│   ├── security.py       # 安全中间件
│   └── tracing.py        # 链路追踪中间件
├── services/              # 业务服务
│   ├── load_balancer.py  # 负载均衡器
│   ├── proxy.py          # 代理服务
│   └── service_registry.py # 服务注册中心
├── api/                   # API 路由
│   ├── gateway.py        # 网关 API
│   ├── health.py         # 健康检查 API
│   ├── metrics.py        # 指标 API
│   ├── websocket.py      # WebSocket API
│   ├── oauth2.py         # OAuth2 认证 API
│   ├── tracing.py        # 分布式追踪 API
│   └── admin.py          # 管理界面 API
├── utils/                 # 工具模块
│   ├── cache.py          # 缓存管理
│   ├── circuit_breaker.py # 熔断器
│   ├── retry.py          # 重试机制
│   └── health_check.py   # 健康检查
├── grpc_services/         # gRPC 服务
│   ├── gateway_service.py # gRPC 网关服务
│   └── server.py         # gRPC 服务器
└── main.py               # 主程序入口
```

## 🔧 配置说明

### 环境变量配置

项目支持通过环境变量进行配置，主要配置项包括：

#### 应用配置
- `ENVIRONMENT`: 运行环境 (development/staging/production)
- `LOG_LEVEL`: 日志级别 (DEBUG/INFO/WARNING/ERROR)
- `HOST`: 监听地址
- `PORT`: 监听端口

#### 数据库配置
- `REDIS_HOST`: Redis 主机地址
- `REDIS_PORT`: Redis 端口
- `REDIS_DB`: Redis 数据库编号
- `REDIS_PASSWORD`: Redis 密码

#### 安全配置
- `JWT_SECRET_KEY`: JWT 签名密钥
- `JWT_ALGORITHM`: JWT 算法
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: 访问令牌过期时间

#### 功能开关
- `RATE_LIMIT_ENABLED`: 是否启用限流
- `TRACING_ENABLED`: 是否启用链路追踪
- `METRICS_ENABLED`: 是否启用指标监控

### 配置文件

除了环境变量，还支持 YAML 配置文件：

```yaml
# config/config.yaml
app:
  name: "suoke-api-gateway"
  version: "1.0.0"

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

logging:
  level: "INFO"
  format: "json"

redis:
  host: "localhost"
  port: 6379
  db: 0

rate_limit:
  enabled: true
  default_rate: "100/minute"
  burst_size: 10
```

## 📚 API 文档

### 核心端点

#### 健康检查
```http
GET /health
```

返回服务健康状态：

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": [
    {
      "name": "redis",
      "status": "healthy",
      "message": "Redis connection successful",
      "duration": 0.001
    }
  ]
}
```

#### 服务代理
```http
POST /proxy/{service_name}
```

代理请求到后端服务：

```json
{
  "method": "GET",
  "path": "/api/users",
  "headers": {
    "Authorization": "Bearer token"
  },
  "body": ""
}
```

#### 服务注册
```http
POST /services/register
```

注册新的服务实例：

```json
{
  "id": "user-service-1",
  "name": "user-service",
  "host": "localhost",
  "port": 8080,
  "weight": 1,
  "metadata": {
    "version": "1.0.0"
  }
}
```

### gRPC 接口

项目同时提供 gRPC 接口，支持：

- 服务代理
- 服务发现
- 健康检查
- 事件流

详细的 gRPC 接口定义请参考 `api/grpc/` 目录。

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest test/test_middleware.py

# 运行测试并生成覆盖率报告
uv run pytest --cov=suoke_api_gateway --cov-report=html
```

### 测试覆盖率

项目目标是保持 90% 以上的测试覆盖率。当前测试包括：

- 单元测试：核心功能和工具模块
- 集成测试：API 端点和中间件
- 性能测试：负载均衡和代理性能

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
docker build -t suoke/api-gateway .

# 运行容器
docker run -d \
  --name api-gateway \
  -p 8000:8000 \
  -e REDIS_HOST=redis \
  suoke/api-gateway
```

### Kubernetes 部署

```bash
# 应用 Kubernetes 配置
kubectl apply -f deploy/kubernetes/

# 检查部署状态
kubectl get pods -l app=suoke-api-gateway
```

### 使用部署脚本

```bash
# 构建和部署到开发环境
./scripts/deploy.sh -e development deploy

# 部署到生产环境
./scripts/deploy.sh -e production -t v1.0.0 deploy

# 查看部署状态
./scripts/deploy.sh status
```

## 📊 监控和运维

### 指标监控

服务导出 Prometheus 格式的指标：

- 请求计数和延迟
- 错误率统计
- 服务健康状态
- 资源使用情况

访问 `/metrics` 端点获取指标数据。

### 日志管理

结构化日志输出，支持：

- JSON 格式日志
- 请求链路追踪
- 错误堆栈记录
- 性能指标记录

### 健康检查

多维度健康检查：

- Redis 连接状态
- 磁盘空间使用
- 内存使用情况
- 外部服务依赖

## 🔧 开发指南

### 开发环境设置

1. 安装开发依赖：
```bash
uv sync --group dev
```

2. 安装 pre-commit 钩子：
```bash
uv run pre-commit install
```

3. 运行代码质量检查：
```bash
uv run ruff check .
uv run mypy .
uv run bandit -r suoke_api_gateway/
```

### 代码规范

项目遵循以下代码规范：

- **PEP 8**: Python 代码风格指南
- **类型注解**: 所有公共接口必须有类型注解
- **文档字符串**: 使用 Google 风格的文档字符串
- **测试覆盖**: 新功能必须包含相应测试

### 提交规范

使用 Conventional Commits 规范：

```
feat: 添加新的负载均衡策略
fix: 修复 Redis 连接池泄漏问题
docs: 更新 API 文档
test: 添加中间件测试用例
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🆘 支持

如果您遇到问题或有疑问，请：

1. 查看 [文档](docs/)
2. 搜索 [Issues](../../issues)
3. 创建新的 [Issue](../../issues/new)

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库
- [structlog](https://www.structlog.org/) - 结构化日志库
- [Redis](https://redis.io/) - 内存数据库
```yaml
server:
  rest:
    host: 0.0.0.0
    port: 8080
  grpc:
    host: 0.0.0.0
    port: 50050
  production: false

middleware:
  cors:
    enabled: true
    # CORS配置...

  rate_limit:
    enabled: true
    # 限流配置...

  auth:
    enabled: true
    # 认证配置...

cache:
  enabled: true
  type: memory  # memory或redis
  # 缓存配置...

routes:
  - name: auth
    prefix: /api/auth/
    service: auth-service
    # 路由配置...
```

## 贡献指南

欢迎贡献代码和提交问题，请遵循以下步骤：

1. Fork仓库并创建特性分支
2. 运行测试确保代码质量
3. 提交PR并描述变更内容

## 许可证

索克生活平台专有软件，未经授权不得使用、复制或分发。

## 联系我们

如有任何疑问或需要进一步支持，请联系API网关团队：api-gateway-team@suoke.life 