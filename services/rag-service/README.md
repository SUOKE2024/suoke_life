# RAG服务 (rag-service)

RAG服务是苏柯生命平台的知识增强检索生成服务，提供基于向量数据库的检索和大型语言模型的生成能力，为用户提供高质量的医疗知识问答。

## 功能特性

- **混合检索**：结合向量检索和关键词检索，提供更精准的医学知识查询结果
- **上下文增强生成**：基于检索结果，通过大模型生成准确的回答
- **分布式追踪**：集成OpenTelemetry，提供完整的可观测性支持
- **故障恢复**：实现断路器模式，具备微服务弹性能力
- **健康监控**：提供健康检查、资源监控和告警功能
- **高性能**：支持异步处理和缓存机制
- **可扩展**：支持水平扩展，适配高并发场景

## 技术架构

```
+-------------------+       +-------------------+       +-------------------+
|     客户端        |------>|     API网关       |------>|    RAG服务        |
+-------------------+       +-------------------+       +-------------------+
                                                               |
                                                               v
+-------------------+       +-------------------+       +-------------------+
|    OpenAI API     |<------|    生成器模块     |<------|    检索器模块     |
+-------------------+       +-------------------+       +-------------------+
                                                               |
                                                               v
                                                       +-------------------+
                                                       |   向量数据库      |
                                                       +-------------------+
```

## 目录结构

```
services/rag-service/
├── api/                # API接口定义
│   ├── grpc/           # gRPC接口
│   └── rest/           # REST接口
├── cmd/                # 命令行入口
│   └── server/         # 服务器入口
├── config/             # 配置文件
│   └── prompts/        # 提示词模板
├── deploy/             # 部署配置
│   ├── docker/         # Docker配置
│   ├── grafana/        # Grafana监控面板
│   ├── kubernetes/     # Kubernetes配置
│   └── prometheus/     # Prometheus监控配置
├── internal/           # 内部实现
│   ├── delivery/       # API处理层
│   ├── generator/      # 生成器实现
│   ├── indexer/        # 索引器实现
│   ├── model/          # 数据模型
│   ├── observability/  # 可观测性
│   ├── repository/     # 数据访问层
│   ├── resilience/     # 弹性能力
│   ├── retriever/      # 检索器实现
│   └── service/        # 业务逻辑层
├── pkg/                # 公共包
│   └── utils/          # 工具函数
└── test/               # 测试文件
    ├── integration/    # 集成测试
    └── unit/           # 单元测试
```

## 快速开始

### 前置条件

- Python 3.9+
- Poetry
- Docker和Docker Compose（可选，用于本地运行依赖服务）
- Kubernetes（可选，用于生产部署）

### 本地开发环境设置

1. 克隆仓库并进入项目目录

```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd life/services/rag-service
```

2. 使用Poetry安装依赖

```bash
poetry install
```

3. 启动依赖服务

```bash
docker-compose -f deploy/docker/docker-compose.dev.yml up -d
```

4. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，设置必要的配置项
```

5. 运行服务

```bash
poetry run python -m services.rag_service.cmd.server
```

### 使用Docker运行

```bash
docker build -t suokelife/rag-service:latest -f deploy/docker/Dockerfile .
docker run -p 8000:8000 -p 9000:9000 --env-file .env suokelife/rag-service:latest
```

### 使用Kubernetes部署

```bash
# 部署到开发环境
kubectl apply -k deploy/kubernetes/overlays/development

# 部署到生产环境
kubectl apply -k deploy/kubernetes/overlays/production
```

## API文档

### REST API

- 检索接口 `POST /api/v1/retrieve`
  - 请求体:
    ```json
    {
      "query": "高血压的中医治疗方法",
      "top_k": 5,
      "filter": {"category": "中医理论"},
      "collections": ["med_knowledge"]
    }
    ```
  - 响应:
    ```json
    {
      "documents": [
        {
          "id": "doc123",
          "content": "高血压在中医理论中属于...",
          "metadata": {"source": "中医基础理论"},
          "score": 0.92
        }
      ]
    }
    ```

- 查询接口 `POST /api/v1/query`
  - 请求体:
    ```json
    {
      "query": "高血压的中医治疗方法",
      "top_k": 5,
      "filter": {"category": "中医理论"}
    }
    ```
  - 响应:
    ```json
    {
      "answer": "中医治疗高血压主要从...",
      "references": [
        {
          "id": "doc123",
          "title": "中医高血压治疗",
          "source": "中医基础理论",
          "url": "http://example.com/doc123"
        }
      ]
    }
    ```

### gRPC API

服务定义可在 `api/grpc/rag.proto` 文件中查看。

## 监控和可观测性

服务集成了以下可观测性工具:

- Prometheus指标收集 (`/metrics` 端点)
- Grafana监控面板
- OpenTelemetry分布式追踪
- 结构化日志

## 测试

### 运行单元测试

```bash
poetry run pytest test/unit
```

### 运行集成测试

```bash
poetry run pytest test/integration
```

### 运行负载测试

```bash
poetry run python test/performance/load_test.py --url http://localhost:8000 --users 10 --time 60
```

## 贡献指南

1. Fork此仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

苏柯生命专有软件