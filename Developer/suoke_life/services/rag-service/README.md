# SUOKE生活 RAG服务

本服务提供基于RAG（Retrieval Augmented Generation）的知识库检索和问答功能，专注于中医健康养生领域的智能问答。

## 功能特点

- **复杂查询分解与重组**: 自动分解复杂问题，分别检索答案，再融合为完整回复
- **多模态支持**: 支持图像（舌诊、面诊）和音频（声音分析）输入的医学数据处理
- **TCM特色功能**: 专注中医药知识库的智能检索和推理
- **深度上下文理解**: 理解用户查询的深层含义，提供准确回答
- **结果重排与优化**: 基于多种指标对检索结果进行智能重排序
- **自适应学习系统**: 从用户反馈中持续学习和优化检索质量
- **多源检索融合**: 结合内部知识库与互联网搜索的混合检索框架
- **知识图谱深度推理**: 将知识图谱与RAG结合，提供深度推理能力

## 系统架构

系统采用微服务架构，主要组件包括：

1. **API网关层**: 处理请求路由、认证和负载均衡
2. **RAG核心服务**: 提供检索增强生成的核心功能
3. **向量存储服务**: 管理文档的嵌入向量和相似度搜索
4. **知识库管理服务**: 负责知识文档的管理和同步
5. **AI推理服务**: 处理LLM和嵌入模型的调用
6. **多模态处理服务**: 处理图像和音频输入
7. **自适应学习服务**: 处理用户反馈和系统优化
8. **知识图谱服务**: 提供知识图谱存储和推理能力

## 最新增强功能

### 1. 自适应学习模块

`adaptive_learning.go` 实现了从用户反馈中持续优化系统的功能：

- **用户反馈处理**: 收集和分析各类型用户反馈
- **多策略学习**: 支持规则型和强化学习两种学习策略
- **参数自动调整**: 根据反馈自动调整检索和生成参数
- **持续优化循环**: 定期批量学习，不断提升系统性能

### 2. 多源检索融合

`multi_source_retrieval.go` 提供了结合多种数据源的融合检索框架：

- **多源注册机制**: 支持注册不同类型的数据源（内部知识库、互联网搜索等）
- **权重调整系统**: 动态调整各数据源权重
- **结果智能融合**: 基于相关性和多样性融合结果
- **缓存管理**: 高效缓存常见查询结果

### 3. 知识图谱推理

`kg_reasoning.go` 实现了将知识图谱与RAG结合的深度推理能力：

- **图谱路径推理**: 在概念间发现推理路径
- **子图分析**: 为复杂问题构建推理子图
- **证据链生成**: 提供推理的完整证据链
- **知识图谱增强检索**: 使用知识图谱信息增强RAG结果

## 使用方法

### API接口

主要API接口包括：

```
POST /api/search              # 基础文本搜索
POST /api/search/multimodal   # 多模态搜索（支持图像和音频）
POST /api/analyze/tongue      # 舌诊分析
POST /api/analyze/face        # 面诊分析
POST /api/analyze/audio       # 音频分析
POST /api/feedback            # 提交用户反馈
POST /api/reason              # 知识图谱推理
```

### 示例：基础搜索请求

```json
{
  "query": "黄芪的功效与作用",
  "user_id": "user123",
  "max_results": 5,
  "domain": "tcm"
}
```

### 示例：多源检索请求

```json
{
  "query": "黄芪的功效与作用",
  "user_id": "user123",
  "max_results": 5,
  "sources": ["internal_kb", "web_search"],
  "source_weights": {
    "internal_kb": 1.2,
    "web_search": 0.8
  }
}
```

### 示例：知识图谱推理请求

```json
{
  "query": "黄芪和白术可以一起服用吗？",
  "user_id": "user123",
  "max_depth": 3,
  "include_documents": true,
  "max_documents": 3
}
```

## 配置说明

服务配置通过环境变量和配置文件进行设置：

```yaml
server:
  port: 8080
  timeout: 30s

rag:
  models:
    embedding: "bge-large-zh"
    llm: "mistral-7b"
  
  retrieval:
    max_results: 10
    relevance_threshold: 0.7
  
  adaptive_learning:
    enabled: true
    learning_interval_ms: 3600000
    default_strategy: "rule_based"
  
  multi_source:
    timeout_ms: 5000
    min_success_sources: 1
    
  knowledge_graph:
    enabled: true
    max_depth: 3
    max_paths: 5
```

## 部署

支持Docker和Kubernetes部署：

```bash
# 使用Docker Compose部署
docker-compose up -d

# 或使用Kubernetes
kubectl apply -f k8s/
```

## 测试工具

提供了一系列测试工具，位于 `./tests` 目录：

- `test_multimodal.go`: 测试多模态检索功能
- `test_reasoning.go`: 测试复杂推理能力
- `test_adaptive.go`: 测试自适应学习功能
- `test_multi_source.go`: 测试多源检索功能
- `test_kg_reasoning.go`: 测试知识图谱推理功能

运行测试示例：

```bash
go run ./tests/test_multimodal.go --image=./samples/tongue.jpg --query="舌头发白是什么原因"
go run ./tests/test_kg_reasoning.go --query="黄芪和白术可以一起服用吗？"
```

## 功能测试工具

### 多模态测试工具

索克生活RAG服务提供了一个完整的多模态测试工具，用于测试服务的多模态搜索和分析能力。这些工具位于`tools/multimodal`目录下。

#### 主要功能

- 健康检查测试
- 基本搜索测试
- 舌诊分析测试（图像分析）
- 音频分析测试（声音分析）
- 多模态组合搜索测试

#### 使用方法

```bash
# 进入工具目录
cd tools/multimodal

# 查看帮助信息
make help

# 运行测试
make test

# 指定服务器URL
make test SERVER=http://dev.suoke.life:8080

# 运行Go版测试
make test-go

# 运行Bash版测试
make test-bash

# 清理输出
make clean
```

详细说明请参考 [多模态测试工具文档](tools/multimodal/README.md)。

## 开发说明

详细的开发文档参见 `./docs` 目录：

- [架构设计](./docs/ARCHITECTURE.md)
- [API文档](./docs/API.md)
- [数据模型](./docs/DATA_MODELS.md)
- [实现总结](./docs/IMPLEMENTATION_SUMMARY.md)

## 许可证

版权所有 © 2023 SUOKE生活
