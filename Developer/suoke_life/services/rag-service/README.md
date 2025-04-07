# RAG服务 (Go实现)

本项目是索克生活RAG（检索增强生成）服务的Go语言实现版本。原Python/Node.js版本已归档至archived_code目录。

## 项目概述

索克生活 RAG（检索增强生成）服务是一个用 Go 语言开发的轻量级、高性能检索增强生成服务，为索克生活 APP 提供知识检索和文档管理能力。该服务通过向量数据库（Milvus）存储文档嵌入，支持高效的语义搜索，并使用嵌入模型将查询和文档转换为向量表示。

## 特性

- 支持多种嵌入模型（OpenAI、本地模型）
- 支持向量数据库（Milvus）和本地向量存储
- 提供 RESTful API 用于文档管理和语义搜索
- 内置指标监控（Prometheus）
- 可水平扩展支持高并发
- 支持文档过滤和元数据管理
- 健康检查和优雅关闭
- 完整的监控和日志系统

## 快速开始

### 环境要求

- Go 1.21+
- Docker 和 Docker Compose（可选，用于容器化部署）
- Milvus 向量数据库（可选，支持本地向量存储）

### 本地开发

1. 克隆仓库
```bash
git clone https://github.com/suoke/suoke_life.git
cd services/rag-service
```

2. 安装依赖
```bash
go mod tidy
```

3. 配置环境变量
```bash
cp .env.example .env  # 创建 .env 文件并配置
```

4. 运行服务
```bash
go run main.go
```

### Docker 部署

使用 Docker Compose 启动整个 RAG 服务生态系统（包括 Milvus、Redis、Prometheus 和 Grafana）：

```bash
docker-compose up -d
```

## API 文档

该服务提供以下主要 API 端点：

### RAG 查询
- `POST /api/rag/query` - 执行RAG查询
- `POST /api/rag/stream` - 执行流式RAG查询
- `POST /api/rag/search/:collection` - 在集合中搜索文档
- `GET /api/rag/collections` - 列出所有集合
- `POST /api/rag/collections` - 创建新集合
- `GET /api/rag/collections/:name` - 获取集合信息
- `DELETE /api/rag/collections/:name` - 删除集合
- `POST /api/rag/upload` - 上传文档到集合
- `GET /api/rag/documents/:collection/:id` - 获取文档
- `DELETE /api/rag/documents/:collection/:id` - 从集合中删除文档

### 嵌入生成
- `POST /api/embeddings` - 生成文本嵌入
- `GET /api/embeddings/models` - 列出可用的嵌入模型

### 系统管理
- `GET /health` - 健康检查
- `GET /metrics` - Prometheus 指标

## 配置

服务配置可以通过 `.env` 文件或环境变量进行配置。主要配置项包括：

- `SERVER_PORT`: 服务端口（默认 8080）
- `LOG_LEVEL`: 日志级别
- `VECTOR_DB_HOST`: 向量数据库主机
- `VECTOR_DB_PORT`: 向量数据库端口
- `EMBEDDING_MODEL`: 默认嵌入模型
- `OPENAI_API_KEY`: OpenAI API 密钥（如果使用 OpenAI 嵌入）

详细配置请参考 `config/config.yaml` 文件。

## 项目结构

```
.
├── api/              # API 定义和文档
├── config/           # 配置文件和加载器
├── core/             # 核心功能
├── database/         # 数据库连接和迁移
├── embeddings/       # 嵌入模型实现
├── handlers/         # HTTP 处理器
├── middleware/       # HTTP 中间件
├── models/           # 数据模型
├── rag/              # RAG 服务实现
├── tests/            # 测试文件
├── utils/            # 工具函数
├── vector_store/     # 向量存储实现
├── Dockerfile        # Docker 构建文件
├── docker-compose.yml# Docker Compose 配置
├── go.mod            # Go 模块定义
├── go.sum            # Go 模块校验和
├── main.go           # 应用入口
└── README.md         # 项目文档
```

## Kubernetes部署

```bash
# 使用Kustomize部署到开发环境
kubectl apply -k k8s/overlays/dev

# 部署到预发布环境
kubectl apply -k k8s/overlays/staging

# 部署到生产环境
kubectl apply -k k8s/overlays/prod
```

## 贡献指南

我们欢迎任何形式的贡献，包括新功能、bug 修复或文档改进。请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加了一个很棒的功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参见 LICENSE 文件。


