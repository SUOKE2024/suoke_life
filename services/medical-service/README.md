# 医疗服务 (Medical Service)

## 概述

医疗服务是索克生活应用的核心微服务之一，负责管理用户医疗记录、提供医学咨询、生成个性化健康建议，以及对接传统中医和现代医疗知识库。该服务结合中西医理念，为用户提供全面的健康管理功能。

## 功能特性

- **医疗记录管理**：存储和管理用户的医疗记录，包括症状、诊断、治疗方案等
- **医疗咨询**：使用RAG（检索增强生成）技术处理用户的医疗问题咨询
- **诊断服务**：基于用户健康数据和症状描述提供初步诊断建议
- **健康风险评估**：分析用户健康数据，生成健康风险评估报告
- **治疗方案推荐**：根据诊断结果提供个性化治疗和保健建议
- **中西医结合**：整合传统中医和现代医学知识，提供全面的健康解决方案

## 系统架构

Medical Service采用清晰的分层架构设计，遵循领域驱动设计(DDD)原则：

```
medical-service/
├── api/                  # API定义
│   ├── grpc/             # gRPC服务定义
│   └── rest/             # REST API定义和Swagger文档
├── cmd/                  # 应用入口
│   └── server/           # 服务器启动程序
├── config/               # 配置文件
├── internal/             # 内部实现
│   ├── delivery/         # 传输层(API处理)
│   │   ├── grpc/         # gRPC服务实现
│   │   └── rest/         # REST服务实现
│   ├── model/            # 领域模型
│   ├── repository/       # 数据访问层
│   └── service/          # 业务逻辑层
├── pkg/                  # 公共包
│   └── utils/            # 工具函数
└── test/                 # 测试
    ├── integration/      # 集成测试
    └── unit/             # 单元测试
```

## 技术栈

- **语言**：Python 3.9+
- **Web框架**：Flask + Connexion (REST API)
- **RPC框架**：gRPC
- **数据库**：PostgreSQL
- **消息队列**：Kafka
- **文档**：OpenAPI (Swagger)
- **监控**：Prometheus + Grafana
- **链路追踪**：Jaeger
- **容器化**：Docker + Kubernetes

## API接口

医疗服务提供双重API接口：

### gRPC接口

用于服务间高效通信，包括：

- `MedicalRecordService`：医疗记录管理
- `DiagnosisService`：健康诊断服务
- `TreatmentService`：治疗方案服务
- `HealthRiskService`：健康风险评估
- `MedicalQueryService`：医疗咨询服务

### REST接口

为前端应用和第三方集成提供的HTTP接口：

- `GET/POST /api/medical-records`：医疗记录管理
- `GET/POST /api/diagnosis`：健康诊断服务
- `GET/POST /api/treatments`：治疗方案管理
- `GET/POST /api/health-risks`：健康风险评估
- `GET/POST /api/medical-queries`：医疗咨询服务

详细API文档请参考Swagger UI：`http://localhost:8080/api/ui/`

## 环境变量

服务可通过以下环境变量进行配置：

| 变量名 | 说明 | 默认值 |
|-------|------|-------|
| LOG_LEVEL | 日志级别 | info |
| LOG_FORMAT | 日志格式(text/json) | json |
| DB_HOST | 数据库主机 | localhost |
| DB_PORT | 数据库端口 | 5432 |
| DB_USER | 数据库用户名 | postgres |
| DB_PASSWORD | 数据库密码 | postgres |
| DB_NAME | 数据库名称 | medical_service |
| RAG_SERVICE_HOST | RAG服务主机 | localhost |
| RAG_SERVICE_PORT | RAG服务端口 | 50051 |
| MED_KNOWLEDGE_SERVICE_HOST | 医学知识服务主机 | localhost |
| MED_KNOWLEDGE_SERVICE_PORT | 医学知识服务端口 | 50051 |

## 部署指南

### 本地开发环境

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 创建并初始化数据库

```bash
# 创建PostgreSQL数据库
createdb medical_service

# 运行数据库初始化脚本
python scripts/create_tables.py
```

3. 运行服务

```bash
python cmd/server/main.py
```

服务默认在以下端口运行：
- REST API: http://localhost:8080
- gRPC: localhost:50051
- Prometheus指标: http://localhost:9090/metrics

### Docker部署

1. 构建Docker镜像

```bash
docker build -t suoke-life/medical-service:latest .
```

2. 运行容器

```bash
docker run -d \
  --name medical-service \
  -p 8080:8080 \
  -p 50051:50051 \
  -p 9090:9090 \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e DB_NAME=medical_service \
  -e RAG_SERVICE_HOST=rag-service \
  -e RAG_SERVICE_PORT=50051 \
  -e MED_KNOWLEDGE_SERVICE_HOST=med-knowledge \
  -e MED_KNOWLEDGE_SERVICE_PORT=50051 \
  suoke-life/medical-service:latest
```

### Kubernetes部署

1. 应用Kubernetes配置

```bash
kubectl apply -f deploy/kubernetes/
```

这将部署以下资源：
- Deployment：服务实例
- Service：服务发现
- ConfigMap：配置
- Secret：敏感配置
- HorizontalPodAutoscaler：自动扩缩容
- PodDisruptionBudget：可用性保证

## 健康检查

服务提供以下健康检查端点：

- `GET /api/health`：简单健康检查
- `GET /api/readiness`：就绪检查（检查数据库和依赖服务连接）
- `GET /api/liveness`：活跃检查

## 监控与可观测性

服务支持以下可观测性功能：

- **指标**：Prometheus格式的指标，暴露在`:9090/metrics`
- **日志**：结构化日志，支持JSON格式输出
- **追踪**：与Jaeger集成的分布式追踪

## 数据库架构

数据库主要包含以下表：

- `medical_records`：存储用户医疗记录
- `diagnosis_results`：存储诊断结果
- `treatment_plans`：存储治疗方案
- `health_risk_assessments`：存储健康风险评估结果
- `medical_queries`：存储医疗咨询历史

## 集成测试

运行集成测试：

```bash
pytest test/integration/
```

## 性能和安全

- 使用连接池优化数据库性能
- 实现JWT身份验证和授权
- 所有API调用记录审计日志
- 敏感数据加密存储
- 定期更新依赖以修复安全漏洞

## 贡献

请参阅CONTRIBUTING.md文件了解如何贡献代码。

## 许可证

本项目采用私有许可证，未经授权不得使用。 