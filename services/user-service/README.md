# 索克生命平台用户服务

## 简介

用户服务是索克生命平台的核心服务之一，负责管理用户账户、身份验证、授权以及用户相关的数据操作。该服务提供了REST API和gRPC接口，为移动应用和其他微服务提供用户管理功能。

## 主要功能

- 用户账户管理（注册、更新、删除）
- 身份验证与授权（基于JWT）
- 用户配置文件管理
- 基于角色的访问控制（RBAC）
- 多因素认证支持
- 用户健康数据元数据管理
- 审计日志记录
- 设备绑定与管理

## 技术栈

- Python 3.10+
- FastAPI (REST API)
- gRPC (服务间通信)
- SQLite (数据存储)
- Prometheus (指标收集)
- JWT (身份验证)
- Kubernetes (部署环境)

## 项目结构

```
services/user-service/
├── api/                  # API定义
│   ├── grpc/             # gRPC接口定义
│   └── rest/             # REST API定义和OpenAPI文档
├── cmd/                  # 命令行入口
│   └── server/           # 服务器入口
├── config/               # 配置文件
├── deploy/               # 部署相关文件
│   ├── docker/           # Docker相关配置
│   └── kubernetes/       # Kubernetes部署配置
├── internal/             # 内部代码
│   ├── delivery/         # 传输层 (API处理程序)
│   ├── model/            # 数据模型
│   ├── observability/    # 监控和日志记录
│   ├── repository/       # 数据存储访问层
│   └── service/          # 业务逻辑层
├── migrations/           # 数据库迁移脚本
├── pkg/                  # 可重用包
│   ├── middleware/       # 中间件组件
│   └── utils/            # 实用工具
└── test/                 # 测试文件
    ├── unit/             # 单元测试
    └── integration/      # 集成测试
```

## 生产就绪特性

该用户服务实现了以下生产就绪特性：

1. **可靠性与容错性**
   - 健康检查和存活探针
   - 优雅启动和关闭
   - 异常处理和恢复机制
   - 请求重试和超时控制

2. **可伸缩性**
   - 无状态设计，支持水平扩展
   - 连接池管理
   - Kubernetes HPA自动扩缩容
   - 资源限制和请求配置

3. **可观测性**
   - 详细日志记录（结构化日志）
   - Prometheus指标导出
   - 请求跟踪（每个请求唯一ID）
   - 健康状态监控和报告

4. **安全性**
   - JWT认证和授权
   - 基于角色的访问控制
   - 密码安全存储与验证
   - 请求速率限制
   - 审计日志

5. **可维护性**
   - 清晰的代码结构和模块化设计
   - 详细的API文档
   - 全面的单元测试和集成测试
   - 版本化API设计

6. **配置管理**
   - 环境变量配置
   - 配置文件支持
   - Kubernetes ConfigMap和Secret集成

## API文档

REST API文档可以通过以下方式访问：

- 开发环境：`http://localhost:8000/docs` 或 `http://localhost:8000/redoc`
- 测试/生产环境：API文档由API网关提供

## 快速开始

### 环境需求
- Python 3.10+
- 虚拟环境工具（如venv、conda）
- Docker（用于容器化部署）

### 本地开发

1. 克隆仓库并进入用户服务目录
```bash
cd services/user-service
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

4. 运行服务
```bash
python cmd/server/main.py --config config/config.yaml
```

5. 访问API文档
```
http://localhost:8000/docs
```

### 使用Docker运行

1. 构建Docker镜像
```bash
docker build -t suoke-life/user-service:latest -f deploy/docker/Dockerfile .
```

2. 运行容器
```bash
docker run -p 8000:8000 -p 50051:50051 suoke-life/user-service:latest
```

### 部署到Kubernetes

```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
```

## 测试

### 运行单元测试
```bash
pytest test/unit
```

### 运行集成测试
```bash
pytest test/integration
```

### 运行所有测试并生成覆盖率报告
```bash
pytest --cov=internal --cov-report=html
```

## 审计日志

用户服务包含全面的审计日志系统，记录关键用户操作：

- 用户登录/注销事件
- 账户创建、修改和删除
- 密码更改和重置
- 角色和权限变更
- 敏感数据访问

审计日志存储在单独的数据库表中，并支持导出和归档功能。

## 贡献指南

1. 遵循项目的代码风格和架构模式
2. 提交代码前运行所有测试
3. 添加适当的文档和注释
4. 所有API更改必须更新相应的API文档
5. 遵循提交消息规范

## 版本历史

- v1.0.0 - 初始版本
- v1.1.0 - 添加审计日志功能
- v1.2.0 - 增强RBAC支持
- v1.3.0 - 添加速率限制和可观测性改进 