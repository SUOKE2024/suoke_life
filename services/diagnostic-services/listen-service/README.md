# 索克生活闻诊服务

基于AI的中医闻诊音频分析服务，采用Python 3.13.3和现代化技术栈构建。

## 功能特性

- 🎵 **音频特征提取** - 支持多种音频格式的特征分析
- 🏥 **中医诊断** - 基于传统中医理论的智能诊断
- 🔄 **缓存系统** - 支持内存和Redis缓存
- 📊 **性能监控** - 实时性能指标和健康检查
- 🌐 **双协议支持** - 同时支持REST API和gRPC
- 🔒 **安全认证** - 支持Token认证和访问控制
- 📝 **结构化日志** - 基于structlog的现代化日志系统

## 技术栈

- **Python 3.13.3** - 最新Python版本
- **UV** - 现代化包管理器
- **FastAPI** - 高性能Web框架
- **gRPC** - 高效RPC通信
- **Pydantic v2** - 数据验证和序列化
- **AsyncIO** - 异步处理
- **Structlog** - 结构化日志
- **Pytest** - 测试框架
- **Ruff** - 代码质量工具
- **MyPy** - 类型检查

## 快速开始

### 环境要求

- Python 3.13.3+
- UV包管理器

### 安装UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安装依赖

```bash
# 开发环境
make dev

# 生产环境
make install
```

### 启动服务

```bash
# 启动REST API服务器
make run-rest

# 启动gRPC服务器
make run-grpc

# 启动混合服务器（同时支持REST和gRPC）
make run-hybrid
```

### 开发模式

```bash
# 开发模式（自动重载）
make dev-rest
```

## API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 主要接口

### 音频分析

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/audio" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_audio.wav" \
  -F "analysis_type=basic"
```

### 中医诊断

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/tcm" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_audio.wav" \
  -F "enable_constitution_analysis=true"
```

### 健康检查

```bash
curl http://localhost:8000/health
```

### 统计信息

```bash
curl http://localhost:8000/stats
```

## 开发工具

### 代码质量

```bash
# 代码检查
make lint

# 代码格式化
make format

# 运行测试
make test

# 测试覆盖率
make test-cov
```

### 测试

```bash
# 单元测试
make test

# 集成测试
make integration-test

# 性能测试
make perf-test

# 完整测试
make test-all
```

### 清理

```bash
# 清理临时文件
make clean

# 清理缓存
make clear-cache
```

## 项目结构

```
listen_service/
├── __init__.py
├── core/                   # 核心业务逻辑
│   ├── audio_analyzer.py   # 音频分析器
│   └── tcm_analyzer.py     # 中医分析器
├── models/                 # 数据模型
│   ├── audio_models.py     # 音频相关模型
│   └── tcm_models.py       # 中医相关模型
├── config/                 # 配置管理
│   └── settings.py         # 设置配置
├── utils/                  # 工具模块
│   ├── cache.py           # 缓存工具
│   ├── logging.py         # 日志工具
│   └── performance.py     # 性能监控
├── delivery/              # 接口层
│   ├── grpc_server.py     # gRPC服务器
│   └── rest_api.py        # REST API
└── cmd/                   # 命令行工具
    └── server.py          # 服务器启动器
```

## 配置

### 环境变量

```bash
# 服务配置
LISTEN_SERVICE_HOST=0.0.0.0
LISTEN_SERVICE_PORT=8000
LISTEN_SERVICE_GRPC_PORT=50051

# 缓存配置
CACHE_BACKEND=memory  # memory 或 redis
REDIS_URL=redis://localhost:6379

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json  # json, console, plain

# 认证配置
AUTH_ENABLED=false
AUTH_SECRET_KEY=your-secret-key
```

### 配置文件

创建 `.env` 文件：

```bash
cp .env.example .env
```

## Docker部署

### 构建镜像

```bash
make docker-build
```

### 运行容器

```bash
make docker-run
```

### Docker Compose

```yaml
version: '3.8'
services:
  listen-service:
    build: .
    ports:
      - "8000:8000"
      - "50051:50051"
    environment:
      - CACHE_BACKEND=redis
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## 监控和日志

### 健康检查

```bash
make health-check
```

### 性能指标

```bash
make metrics
```

### 查看日志

```bash
make logs
```

## 中医诊断功能

### 支持的体质类型

- 平和质 - 身体健康平衡
- 气虚质 - 气力不足
- 阳虚质 - 阳气不足
- 阴虚质 - 阴液不足
- 痰湿质 - 痰湿内盛
- 湿热质 - 湿热内蕴
- 血瘀质 - 血液瘀滞
- 气郁质 - 气机郁滞
- 特禀质 - 特殊体质

### 情绪状态分析

基于中医五志理论：
- 喜 - 心志过度
- 怒 - 肝气郁结
- 忧 - 肺气不宣
- 思 - 脾气虚弱
- 恐 - 肾气不足

### 脏腑功能评估

- 心 - 主血脉，藏神
- 肝 - 主疏泄，藏血
- 脾 - 主运化，统血
- 肺 - 主气，司呼吸
- 肾 - 主水，藏精

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

### 开发流程

```bash
# 设置开发环境
make setup-dev

# 开发工作流
make dev-workflow

# 发布准备
make release-prep
```

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/suoke-life/listen-service
- 问题反馈: https://github.com/suoke-life/listen-service/issues
- 邮箱: support@suoke.life

## 更新日志

### v1.0.0 (2024-01-XX)

- ✨ 初始版本发布
- 🎵 音频特征提取功能
- 🏥 中医诊断分析
- 🌐 REST API和gRPC支持
- 📊 性能监控和健康检查
- 🔄 缓存系统
- 📝 结构化日志 