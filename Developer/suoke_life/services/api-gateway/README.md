# 索克生活平台 API 网关服务

![版本](https://img.shields.io/badge/版本-1.0.0-brightgreen.svg)
![许可证](https://img.shields.io/badge/许可证-Apache%202.0-blue.svg)

## 项目概述

索克生活平台 API 网关服务是整个微服务架构的核心入口点，负责管理和路由所有对内部微服务的访问请求。它提供了一个统一的API接口，处理认证、授权、流量控制、监控、日志记录和请求/响应转换等横切关注点。

### 主要功能

- **API路由和聚合**: 将请求路由到相应的后端服务，并聚合多个微服务的响应
- **身份验证和授权**: 集成JWT、OAuth2.0等认证机制
- **流量管理**: 实现请求限流、熔断、重试等机制
- **安全防护**: TLS终止、防SQL注入、XSS攻击等安全措施
- **监控和追踪**: Prometheus指标集成、OpenTelemetry分布式追踪
- **请求/响应转换**: 支持数据格式转换和协议转换
- **缓存**: API响应缓存，减少后端服务负载
- **灰度发布**: 支持流量分割和A/B测试

## 技术栈

- **运行时环境**: Node.js 18
- **框架**: Express
- **容器化**: Docker
- **编排**: Kubernetes
- **配置管理**: Helm Chart
- **密钥管理**: HashiCorp Vault
- **监控**: Prometheus + Grafana
- **日志**: ELK (Elasticsearch, Logstash, Kibana)
- **CI/CD**: GitHub Actions / Jenkins

## 本地开发

### 前提条件

- Node.js 18+
- Docker 20.10+
- Kubernetes 1.25+ (可选，用于本地测试)
- Helm 3.9+ (可选，用于部署)

### 安装依赖

```bash
npm install
```

### 启动开发环境

```bash
# 启动开发服务器
npm run dev

# 使用模拟数据启动
npm run dev:mock
```

### 运行测试

```bash
# 运行单元测试
npm test

# 运行集成测试
npm run test:integration

# 运行端到端测试
npm run test:e2e
```

### 构建项目

```bash
# 构建生产版本
npm run build

# 生成Docker镜像
docker build -t suoke/api-gateway:latest .
```

## 部署指南

### 使用Helm部署

API网关提供了完整的Helm Chart，支持在Kubernetes集群中部署：

```bash
# 添加索克生活Helm仓库
helm repo add suoke https://charts.suoke.life
helm repo update

# 安装API网关
helm install api-gateway suoke/api-gateway \
  --namespace suoke-system \
  --create-namespace \
  --values values-prod.yaml
```

### 配置选项

通过修改Helm Chart的values.yaml文件，可以配置以下主要选项：

- **复制数量**: 设置部署的Pod数量
- **资源限制**: 配置CPU和内存限制
- **持久化存储**: 配置日志和数据持久化
- **自动伸缩**: 配置HPA自动伸缩参数
- **网络策略**: 配置入站/出站网络规则
- **服务发现**: 配置服务发现集成
- **外部服务**: 配置外部服务访问
- **Vault集成**: 配置密钥管理

详细配置选项请参考 [values.yaml文档](./helm/api-gateway/README.md)。

### 环境变量

主要环境变量说明：

| 变量名 | 描述 | 默认值 | 必填 |
|--------|------|--------|------|
| NODE_ENV | 运行环境 | production | 是 |
| PORT | HTTP服务端口 | 3000 | 是 |
| HOST | 监听地址 | 0.0.0.0 | 是 |
| LOG_LEVEL | 日志级别 | info | 否 |
| METRICS_PORT | 指标监控端口 | 9090 | 否 |

完整环境变量列表请参考 [环境变量文档](./docs/ENV_VARS.md)。

## 项目结构

```
api-gateway/
├── src/                  # 源代码
│   ├── config/           # 配置文件
│   ├── controllers/      # 控制器
│   ├── middleware/       # 中间件
│   ├── routes/           # 路由定义
│   ├── services/         # 服务
│   ├── utils/            # 工具函数
│   └── index.js          # 入口文件
├── test/                 # 测试
│   ├── unit/             # 单元测试
│   └── integration/      # 集成测试
├── helm/                 # Helm Chart
│   └── api-gateway/      # API网关Helm包
├── k8s/                  # Kubernetes资源清单
├── docs/                 # 文档
├── Dockerfile            # Docker构建文件
├── package.json          # 项目依赖
└── README.md             # 项目说明
```

## API文档

API网关提供了自动生成的API文档，可通过以下方式访问：

- **开发环境**: http://localhost:3000/docs
- **生产环境**: https://api.suoke.life/docs

也可以通过Swagger规范文件查看完整API定义：

- **SwaggerUI**: https://api.suoke.life/swagger
- **OpenAPI文件**: https://api.suoke.life/openapi.json

## 监控和可观测性

API网关集成了完整的监控和可观测性功能：

- **健康检查**: /health/live和/health/ready端点
- **Prometheus指标**: /metrics端点（9090端口）
- **OpenTelemetry追踪**: 配置文件位于config/otel.js
- **结构化日志**: JSON格式，集成ELK栈

## 贡献指南

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加了一些惊人的功能'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

贡献前请阅读[贡献指南](./CONTRIBUTING.md)和[代码规范](./CODE_OF_CONDUCT.md)。

## 许可证

本项目采用Apache 2.0许可证 - 详情请参见[LICENSE](./LICENSE)文件。

## 联系我们

- 项目维护团队: 索克生活技术团队
- 电子邮件: devops@suoke.life
- 问题反馈: [GitHub Issues](https://github.com/suoke/api-gateway/issues) 