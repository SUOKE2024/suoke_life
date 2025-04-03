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
- **CI/CD**: GitHub Actions

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

### 5. CI/CD 自动化

- 完整的持续集成与持续部署流程
- 代码质量检查与测试自动化
- 安全扫描确保依赖和容器安全
- 多环境自动部署流水线
- 自动化性能测试与监控
- 部署结果通知机制

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

### 本地测试

```bash
# 运行全套本地测试（代码检查、单元测试、Docker构建）
./scripts/run_local_tests.sh

# 测试并自动部署
./scripts/test_and_deploy.sh <分支名> "<提交消息>" [Y/N]

# 例如：测试并部署到功能分支
./scripts/test_and_deploy.sh feature/new-feature "添加新功能" Y

# 例如：测试并部署到发布分支
./scripts/test_and_deploy.sh release/1.2.0 "准备发布1.2.0版本" Y
```

详细的本地测试和自动部署文档请参阅 [本地测试指南](docs/LOCAL_TESTING.md)。

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

## CI/CD 流程

服务使用GitHub Actions实现自动化CI/CD流程，主要包括：

### 自动化流程

1. **代码检查与测试**: 每次提交自动运行代码格式检查、类型检查、单元测试
2. **安全扫描**: 自动检测依赖和容器中的安全漏洞
3. **镜像构建与推送**: 自动构建Docker镜像并推送到容器镜像仓库
4. **多环境部署**: 根据分支策略自动部署到相应环境
5. **性能测试**: 自动执行负载测试并分析性能指标
6. **部署验证**: 自动验证服务部署状态和功能可用性

### 使用方法

- **开发新功能**: 创建feature/*分支进行开发，提交PR触发测试
- **发布版本**: 合并到main自动部署到开发环境，创建release/*分支部署到生产
- **手动部署**: 通过GitHub Actions界面手动触发特定环境的部署

详细说明请参阅 [CI/CD文档](docs/CI_CD_README.md)。

## 贡献指南

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何为项目做出贡献。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。