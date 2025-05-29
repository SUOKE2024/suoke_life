# 医疗资源微服务 (Medical Resource Service)

## 概述

医疗资源微服务是"索克生活（Suoke Life）"平台的核心组件之一，负责医疗资源的智能管理和调度。该服务集成了传统中医理论与现代医疗技术，通过小克智能体提供个性化的医疗资源推荐和管理服务。

## 技术栈

- **Python**: 3.13.3
- **依赖管理**: UV (Python 包管理器)
- **Web框架**: FastAPI
- **数据库**: PostgreSQL, Redis, MongoDB
- **容器化**: Docker
- **代码质量**: Black, isort, pytest

## 快速开始

### 环境要求

- Python 3.13.3+
- UV (Python 包管理器)
- Docker (可选)

### 安装依赖

```bash
# 使用 UV 安装依赖（国内镜像）
uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

# 安装开发依赖
uv sync --extra dev --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 运行服务

```bash
# 直接运行
uv run python -m cmd.server.main

# 或使用 Docker
docker build -t medical-resource-service .
docker run -p 9084:9084 medical-resource-service
```

### 代码质量检查

```bash
# 代码格式化
uv run black .

# 导入排序
uv run isort .

# 运行测试
uv run pytest
```

## 项目结构

```
medical-resource-service/
├── api/                    # API 接口定义
│   ├── grpc/              # gRPC 接口
│   └── rest/              # REST API
├── cmd/                   # 命令行入口
│   └── server/            # 服务器启动
├── config/                # 配置文件
├── internal/              # 内部实现
│   ├── agent/             # 智能体模块
│   ├── domain/            # 领域模型
│   ├── infrastructure/    # 基础设施
│   ├── modules/           # 功能模块
│   └── service/           # 业务服务
├── pyproject.toml         # 项目配置和依赖
├── uv.lock               # 依赖锁定文件
└── Dockerfile            # 容器构建文件
```

## 核心功能

### 1. 智能体集成
- **小克智能体**: 专门的医疗资源管理智能体
- **决策引擎**: 基于机器学习的智能决策
- **学习模块**: 持续学习和模型优化

### 2. 医疗资源管理
- **资源调度**: 智能资源分配和调度
- **质量控制**: 多维度资源质量评估
- **个性化服务**: 基于体质的个性化推荐

### 3. 中医知识服务
- **方剂管理**: 传统方剂的数字化管理
- **中药知识**: 中药材信息和配伍
- **穴位信息**: 针灸穴位和治疗方案
- **证候辨识**: 中医证候的智能识别

### 4. 食农结合
- **食疗方案**: 基于体质的食疗推荐
- **农产品管理**: 有机农产品的质量管理
- **营养分析**: 食物营养成分分析

### 5. 山水养生
- **养生旅游**: 个性化养生旅游方案
- **环境评估**: 养生环境的质量评估
- **活动推荐**: 适合的养生活动推荐

## 配置说明

### 环境变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/medical_resource
REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017/medical_resource

# 服务配置
SERVICE_HOST=0.0.0.0
SERVICE_PORT=9084
LOG_LEVEL=INFO

# 智能体配置
XIAOKE_AGENT_ENABLED=true
LEARNING_MODULE_ENABLED=true
```

### 配置文件

- `config/config.yaml`: 主配置文件
- `config/infrastructure.yaml`: 基础设施配置

## API 文档

服务启动后，可以通过以下地址访问 API 文档：

- Swagger UI: http://localhost:9084/docs
- ReDoc: http://localhost:9084/redoc

## 开发指南

### 代码规范

- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 遵循 PEP 8 编码规范
- 使用类型注解

### 测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/unit/

# 生成覆盖率报告
uv run pytest --cov=internal --cov-report=html
```

### 部署

#### Docker 部署

```bash
# 构建镜像
docker build -t medical-resource-service .

# 运行容器
docker run -d \
  --name medical-resource-service \
  -p 9084:9084 \
  -e DATABASE_URL=postgresql://... \
  medical-resource-service
```

#### Kubernetes 部署

```bash
# 应用配置
kubectl apply -f deploy/kubernetes/
```

## 监控和日志

### 健康检查

- 健康检查端点: `GET /health`
- 就绪检查端点: `GET /ready`

### 指标监控

- Prometheus 指标: `GET /metrics`
- 性能监控: 内置性能监控器

### 日志

- 结构化日志输出
- 支持多种日志级别
- 日志轮转和归档

## 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 清理缓存重新安装
   uv cache clean
   uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接字符串配置
   - 检查网络连接

3. **服务启动失败**
   - 检查端口是否被占用
   - 验证配置文件格式
   - 查看详细错误日志

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目仓库: [GitHub](https://github.com/your-org/suoke-life)
- 邮箱: support@suoke-life.com

---

**索克生活 - 让中医智慧融入现代生活** 