# RAG服务 (检索增强生成服务)

## 服务概述

RAG服务是索克生活平台的核心知识服务，负责将用户查询与知识库中的相关内容进行关联，增强AI回复的准确性、专业性和可信度。服务集成了向量检索、知识图谱遍历和语义理解能力，为各个智能体提供知识支持。

## 技术栈

- **语言**: Python 3.9+
- **主要框架**: FastAPI
- **向量数据库**: Qdrant
- **知识图谱**: Neo4j
- **缓存**: Redis
- **监控**: Prometheus + Grafana
- **日志**: OpenTelemetry + Loki
- **部署**: Kubernetes + Docker

## 核心功能

1. **多模态知识检索**: 支持文本、图像、音频输入，返回相关知识结果
2. **知识图谱遍历**: 支持实体关系查询和路径探索
3. **语义匹配**: 使用最新的向量嵌入模型进行语义相似度计算
4. **结果融合与排序**: 智能合并来自不同数据源的结果
5. **知识上下文处理**: 构建结构化知识上下文供LLM使用

## 最新优化

### 1. 容器化优化

- 多阶段构建，减小镜像体积约35%
- 实现健壮的启动脚本，支持健康检查和依赖验证
- 配置优雅关闭机制，保障数据一致性

### 2. Kubernetes配置标准化

- 实现符合微服务部署标准的K8s资源
- 增加备份CronJob保障数据安全
- 配置Pod中断预算(PDB)确保高可用性
- 实现Horizontal Pod Autoscaler自动扩缩容

### 3. 可观测性增强

- 集成OpenTelemetry分布式追踪
- 配置Prometheus监控指标
- 构建Grafana自定义仪表盘
- 实现结构化日志和集中式日志收集

### 4. 性能优化

- 向量索引并行加载与预热
- Redis结果缓存机制
- 批量查询优化
- 按需加载大型模型

## 快速开始

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/suoke/rag-service.git
cd rag-service

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件设置必要参数

# 启动服务
python -m src.main
```

### Docker 运行

```bash
# 构建镜像
docker build -t suoke/rag-service:latest .

# 运行容器
docker run -p 8000:8000 --env-file .env suoke/rag-service:latest
```

### Kubernetes 部署

```bash
# 使用Kustomize部署
kubectl apply -k k8s/base

# 或使用特定环境配置
kubectl apply -k k8s/overlays/production
```

## 接口文档

启动服务后访问 `/docs` 或 `/redoc` 获取Swagger或ReDoc格式的API文档。

## 贡献指南

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何为项目做出贡献。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。