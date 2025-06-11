# AI Model Service

索克生活AI模型云端部署和管理服务，专门负责大型AI模型的Kubernetes部署、版本管理、扩缩容和推理服务。

## 🎯 核心功能

- **🚀 模型部署**: 支持多种AI框架的模型部署到Kubernetes集群
- **📊 版本管理**: 完整的模型版本控制和A/B测试能力
- **⚡ 自动扩缩容**: 基于负载的智能扩缩容
- **🔍 监控告警**: 实时监控模型性能和资源使用
- **🛡️ 健康检查**: 自动故障检测和恢复
- **🔄 滚动更新**: 零停机时间的模型更新
- **📦 批量推理**: 支持批量推理请求处理
- **🔧 完整API**: RESTful API支持所有管理操作

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Model Service                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Model API   │  │ Deployment  │  │ Monitoring  │        │
│  │ Gateway     │  │ Manager     │  │ Service     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                 Kubernetes Cluster                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ TCM Model   │  │ Treatment   │  │ Health      │        │
│  │ Pod         │  │ Model Pod   │  │ Model Pod   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.13+
- Kubernetes 1.28+
- Docker 24.0+
- UV包管理器

### 安装

```bash
# 使用UV安装依赖
uv sync

# 或使用pip
pip install -e .
```

### 配置

1. 复制配置文件模板：
```bash
cp config/config.example.yaml config/config.yaml
```

2. 编辑配置文件，设置Kubernetes集群信息：
```yaml
kubernetes:
  namespace: "suoke-life"
  config_path: "~/.kube/config"  # 或使用集群内配置

models:
  registry: "registry.suoke.life"
  default_resources:
    cpu: "2"
    memory: "8Gi"
    gpu: "1"
```

### 启动服务

```bash
# 开发模式
./scripts/dev.sh dev

# 生产模式
uv run ai-model-service --config config/config.yaml
```

## 📖 API文档

### 模型管理API

#### 部署模型
```bash
POST /api/v1/models/deploy
Content-Type: application/json

{
  "config": {
    "model_id": "deep_tcm_diagnosis",
    "name": "深度中医诊断模型",
    "version": "v3.0.1",
    "model_type": "tcm_diagnosis",
    "framework": "tensorflow",
    "docker_image": "suoke/tcm-diagnosis:v3.0.1",
    "resource_requirements": {
      "cpu": "2",
      "memory": "8Gi",
      "nvidia.com/gpu": "1"
    },
    "scaling_config": {
      "min_replicas": 1,
      "max_replicas": 5,
      "target_cpu_utilization": 70
    }
  }
}
```

#### 单次推理
```bash
POST /api/v1/models/{model_id}/inference
Content-Type: application/json

{
  "input_data": {
    "symptoms": ["头痛", "乏力", "食欲不振"],
    "patient_info": {
      "age": 35,
      "gender": "female"
    }
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1024
  },
  "timeout": 30,
  "priority": "normal"
}
```

#### 批量推理
```bash
POST /api/v1/models/{model_id}/batch_inference
Content-Type: application/json

{
  "requests": [
    {
      "input_data": {"symptoms": ["头痛", "乏力"]},
      "parameters": {"temperature": 0.7}
    },
    {
      "input_data": {"symptoms": ["失眠", "焦虑"]},
      "parameters": {"temperature": 0.8}
    }
  ],
  "timeout": 60
}
```

#### 查看模型状态
```bash
GET /api/v1/models/{model_id}/status
```

#### 列出所有模型
```bash
GET /api/v1/models
```

#### 扩缩容模型
```bash
POST /api/v1/models/{model_id}/scale
Content-Type: application/json

{
  "replicas": 3
}
```

#### 更新模型
```bash
PUT /api/v1/models/{model_id}
Content-Type: application/json

{
  "config": {
    "model_id": "deep_tcm_diagnosis",
    "version": "v3.0.2",
    "docker_image": "suoke/tcm-diagnosis:v3.0.2"
  }
}
```

#### 删除模型
```bash
DELETE /api/v1/models/{model_id}
```

### 健康检查API

#### 基础健康检查
```bash
GET /api/v1/health/
```

#### 存活检查
```bash
GET /api/v1/health/live
```

#### 就绪检查
```bash
GET /api/v1/health/ready
```

#### 启动检查
```bash
GET /api/v1/health/startup
```

#### 详细健康检查
```bash
GET /api/v1/health/detailed
```

## 🔧 开发指南

### 项目结构

```
services/ai-model-service/
├── src/ai_model_service/
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── api/                    # API路由
│   │   ├── app.py             # FastAPI应用
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── models.py       # 模型管理API
│   │       └── health.py       # 健康检查API
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── manager.py          # 模型管理器
│   │   ├── deployer.py         # 部署器
│   │   ├── monitor.py          # 监控器
│   │   └── inference.py        # 推理引擎
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── config.py           # 配置模型
│   │   ├── deployment.py       # 部署模型
│   │   └── inference.py        # 推理模型
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── k8s.py             # Kubernetes工具
│   │   ├── logging.py         # 日志工具
│   │   └── metrics.py         # 指标工具
│   └── config/                 # 配置管理
│       ├── __init__.py
│       └── settings.py        # 设置
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── conftest.py            # 测试配置
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── fixtures/               # 测试数据
├── docs/                       # 文档
├── config/                     # 配置文件
├── scripts/                    # 脚本
│   ├── dev.sh                 # 开发工具脚本
│   └── start.sh               # 启动脚本
├── deploy/                     # 部署配置
│   └── kubernetes/
├── pyproject.toml             # 项目配置
├── README.md                  # 项目说明
└── Dockerfile                 # Docker配置
```

### 代码规范

项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **Ruff**: 代码检查和自动修复
- **MyPy**: 类型检查
- **Bandit**: 安全检查

### 开发工具脚本

使用 `./scripts/dev.sh` 脚本进行开发：

```bash
# 初始化开发环境
./scripts/dev.sh setup

# 运行测试
./scripts/dev.sh test

# 运行测试并生成覆盖率报告
./scripts/dev.sh test-cov

# 代码格式化
./scripts/dev.sh format

# 代码检查
./scripts/dev.sh lint

# 类型检查
./scripts/dev.sh type-check

# 安全检查
./scripts/dev.sh security

# 运行所有检查
./scripts/dev.sh check-all

# 开发模式启动
./scripts/dev.sh dev

# 构建Docker镜像
./scripts/dev.sh build

# 清理临时文件
./scripts/dev.sh clean

# 生成文档
./scripts/dev.sh docs
```

### 手动运行工具

```bash
# 格式化代码
uv run black src tests
uv run isort src tests
uv run ruff check --fix src tests

# 代码检查
uv run ruff check src tests
uv run black --check src tests
uv run isort --check-only src tests

# 类型检查
uv run mypy src

# 安全检查
uv run bandit -r src
```

### 测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest tests/unit

# 运行集成测试
uv run pytest tests/integration

# 生成覆盖率报告
uv run pytest --cov=ai_model_service --cov-report=html
```

## 🐳 Docker部署

### 构建镜像

```bash
# 使用开发脚本构建
./scripts/dev.sh build

# 手动构建
docker build -t suoke/ai-model-service:latest .
```

### 运行容器

```bash
docker run -d \
  --name ai-model-service \
  -p 8080:8080 \
  -v ~/.kube/config:/root/.kube/config \
  -e KUBERNETES_NAMESPACE=suoke-life \
  suoke/ai-model-service:latest
```

## ☸️ Kubernetes部署

```bash
# 应用配置
kubectl apply -f deploy/kubernetes/

# 查看状态
kubectl get pods -n suoke-life -l app=ai-model-service

# 查看日志
kubectl logs -n suoke-life -l app=ai-model-service -f
```

## 📊 监控指标

服务提供以下Prometheus指标：

- `ai_model_deployments_total`: 部署的模型总数
- `ai_model_inference_requests_total`: 推理请求总数
- `ai_model_inference_duration_seconds`: 推理耗时
- `ai_model_resource_usage`: 资源使用情况
- `ai_model_health_status`: 模型健康状态
- `ai_model_batch_inference_requests_total`: 批量推理请求总数

## 🔒 安全考虑

- **RBAC**: 使用Kubernetes RBAC控制访问权限
- **TLS**: 所有API通信使用TLS加密
- **认证**: 支持JWT和API Key认证
- **审计**: 记录所有操作日志
- **网络策略**: 限制Pod间网络访问
- **安全扫描**: 使用Bandit进行安全代码检查

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 运行代码检查 (`./scripts/dev.sh check-all`)
4. 提交更改 (`git commit -m 'Add some amazing feature'`)
5. 推送到分支 (`git push origin feature/amazing-feature`)
6. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

- 📧 邮箱: dev@suoke.life
- 📖 文档: https://docs.suoke.life/ai-model-service
- 🐛 问题反馈: https://github.com/suoke-life/suoke_life/issues

## 🗺️ 路线图

- [x] 基础模型部署和管理
- [x] 健康检查和监控
- [x] 批量推理支持
- [x] 完整的API文档
- [ ] 支持更多AI框架 (ONNX, TensorRT)
- [ ] 模型量化和优化
- [ ] 多云部署支持
- [ ] 图形化管理界面
- [ ] 模型市场集成
- [ ] 联邦学习支持