# 知识库服务 (Knowledge Base Service)

知识库服务是索克生活APP的核心知识管理服务，负责存储、索引和提供健康养生相关的结构化知识内容。本服务与知识图谱服务和RAG服务协同工作，为用户提供精准、专业的健康知识内容。

> **重要更新**: 本服务已完成从Node.js到Go的重构，以提高性能、可靠性和可维护性。所有API路径前缀从'/'更改为'/api/v1/'。

## 功能特性

- 知识内容管理（CRUD操作）
- 知识分类与标签管理
- 多维度知识检索
- 中医特色知识体系
- 传统文化知识管理
- 现代医学知识管理
- 精准医学知识库
- 多模态健康数据分析
- 环境健康知识库
- 心理健康扩展服务
- 循证医学证据评估
- 内容版本控制
- 知识图谱集成接口
- RAG服务知识源支持
- 内容审核与质量控制
- 向量化存储与语义搜索
- 可穿戴设备数据整合
- 多学科知识整合

## 技术栈

- Go语言
- Chi路由框架
- RESTful API
- PostgreSQL数据库
- Milvus向量数据库
- 微服务架构
- Docker容器化
- Kubernetes编排

## 项目结构

```
knowledge-base-service/
├── cmd/                     # 命令和入口点
│   ├── server/              # 主服务入口
│   ├── tools/               # 工具命令
│   └── benchmark/           # 性能测试
├── config/                  # 配置管理
├── internal/                # 内部代码
│   ├── api/                 # API定义
│   ├── domain/              # 领域模型和服务
│   │   ├── entity/          # 领域实体
│   │   ├── repository/      # 存储库接口
│   │   └── service/         # 领域服务
│   ├── infrastructure/      # 基础设施
│   │   ├── database/        # 数据库实现
│   │   ├── nlp/             # 自然语言处理
│   │   ├── repository/      # 存储库实现
│   │   └── vectorstore/     # 向量存储实现
│   ├── interfaces/          # 接口层
│   │   ├── rest/            # REST API
│   │   └── ai/              # AI集成
│   ├── mocks/               # 模拟测试
│   └── test/                # 测试辅助
├── pkg/                     # 公共包
│   └── logger/              # 日志工具
├── contracts/               # 协议定义
├── docs/                    # 文档目录
├── k8s/                     # Kubernetes配置
├── helm/                    # Helm Chart配置
├── scripts/                 # 脚本
├── .env.example             # 环境变量示例
├── Dockerfile               # Docker构建文件
├── go.mod                   # Go模块定义
└── go.sum                   # Go依赖校验
```

## 安装与运行

### 本地开发

1. 克隆仓库：
```bash
git clone https://github.com/suoke-life/knowledge-base-service.git
cd knowledge-base-service
```

2. 安装依赖：
```bash
go mod download
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

4. 启动开发服务器：
```bash
go run cmd/server/main.go
```

服务将在 http://localhost:3002 启动，健康检查接口可访问 http://localhost:3002/api/v1/health

### Docker部署

1. 构建Docker镜像：
```bash
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-base-service:latest .
```

2. 推送镜像到仓库：
```bash
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-base-service:latest
```

3. 运行容器：
```bash
docker run -d -p 3002:3002 --name knowledge-base-service \
  -v /path/to/data:/app/data \
  -v /path/to/logs:/app/logs \
  --env-file .env \
  suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-base-service:latest
```

### Docker Compose部署

使用项目中的docker-compose.yml文件启动服务及其依赖：

```bash
docker-compose up -d
```

### Kubernetes部署

#### 使用kubectl和Kustomize

1. 切换到正确的上下文：
```bash
kubectl config use-context your-cluster-context
```

2. 部署服务：
```bash
kubectl apply -k k8s/
```

3. 验证部署：
```bash
kubectl get pods -n suoke-prod -l app=knowledge-base-service
kubectl get svc -n suoke-prod -l app=knowledge-base-service
```

#### 使用Helm部署

1. 安装或升级Chart：
```bash
helm upgrade --install knowledge-base-service ./helm \
  --namespace suoke-prod \
  --create-namespace \
  --set image.tag=latest \
  --values ./helm/values.yaml
```

2. 使用自定义值文件：
```bash
cp ./helm/values.yaml ./helm/custom-values.yaml
# 编辑custom-values.yaml以适应环境
helm upgrade --install knowledge-base-service ./helm \
  --namespace suoke-prod \
  --values ./helm/custom-values.yaml
```

3. 卸载Chart：
```bash
helm uninstall knowledge-base-service -n suoke-prod
```

## API文档

服务将在后续版本中集成Swagger/OpenAPI文档系统，目前主要API端点如下：

- **健康检查**: `/api/v1/health`
- **文档列表**: `/api/v1/documents`
- **文档详情**: `/api/v1/documents/{id}`
- **创建文档**: `/api/v1/documents`
- **更新文档**: `/api/v1/documents/{id}`
- **删除文档**: `/api/v1/documents/{id}`
- **搜索文档**: `/api/v1/documents/search?q={query}`
- **语义搜索**: `/api/v1/documents/semantic-search?q={query}`

## 数据库配置

### PostgreSQL配置

服务需要配置以下PostgreSQL环境变量：

```
DB_CONNECTION_STRING=postgresql://username:password@host:port/dbname?sslmode=disable
```

### Milvus向量数据库配置

服务需要配置以下Milvus环境变量：

```
VECTOR_STORE_HOST=milvus-host
VECTOR_STORE_PORT=19530
VECTOR_STORE_API_KEY=your-api-key
VECTOR_STORE_COLLECTION=documents
```

### 嵌入服务配置

文本嵌入服务配置：

```
EMBEDDING_MODEL_URL=http://embedding-service:8000/embed
EMBEDDING_API_TOKEN=your-api-token
EMBEDDING_DIMENSIONS=1536
EMBEDDING_BATCH_SIZE=10
```

## 文档迁移

如需从旧版本MongoDB数据迁移到新版PostgreSQL和Milvus数据库，可参考：

1. 导出MongoDB数据：
```bash
./scripts/export_mongo_data.sh
```

2. 导入到PostgreSQL和Milvus：
```bash
./knowledge-base-service migrate --source=./exported_data.json
```

## 集成服务

- **知识图谱服务**：同步结构化知识到知识图谱
- **RAG服务**：提供知识内容作为检索增强生成的数据源
- **用户服务**：获取用户权限和个性化推荐信息
- **小艾服务**：提供知识支持给智能助手
- **可穿戴设备服务**：接收并分析可穿戴设备数据
- **环境监测服务**：获取环境健康数据
- **代理协调服务**：协调多个AI代理进行复杂分析

## 可观测性

服务通过以下方式支持可观测性：

1. **Prometheus指标**：
   - 服务在`:9090/metrics`端点暴露Prometheus指标
   - 包含请求计数、响应时间、缓存命中率等关键指标
   - ServiceMonitor自动配置了指标收集

2. **OpenTelemetry集成**：
   - 分布式追踪支持，可与Jaeger和Zipkin集成
   - 自动追踪HTTP请求和数据库操作
   - 通过环境变量`OTEL_EXPORTER_OTLP_ENDPOINT`配置

3. **健康检查端点**：
   - `/health`：提供服务总体健康状态
   - `/metrics`：提供Prometheus格式的指标
   - 适配Kubernetes的liveness和readiness探针

## 安全配置

1. **安全存储**：
   - 集成Vault进行密钥管理
   - 支持敏感数据加密
   - 自动密钥轮换

2. **认证与授权**：
   - JWT基础验证
   - 基于角色的访问控制
   - API密钥支持

3. **容器安全**：
   - 非root用户运行
   - 只读文件系统
   - 最小权限原则

## 知识体系

本服务管理的知识主要包括：

- **基础知识**
  - 常见疾病预防知识
  - 养生保健知识
  - 饮食营养学知识
  - 运动健身知识
  - 健康生活方式指导

- **传统文化知识**
  - 中医理论体系知识
  - 易经与五行
  - 道家养生理论
  - 佛家修心法门
  - 传统文化经典
  - 面相与命理
  - 风水与环境

- **现代医学知识**
  - 内科学知识
  - 外科学知识
  - 妇产科知识
  - 儿科学知识
  - 预防医学知识
  - 营养学研究
  - 心理学研究

- **精准医学知识**
  - 基因组学数据
  - 药物基因组学
  - 营养基因组学
  - 风险评估模型
  - 个性化健康建议
  - 生物标记物指南

- **多模态健康数据**
  - 图像分析知识
  - 语音特征解读
  - 可穿戴设备指标
  - 多源数据融合分析
  - 健康数据模式识别

- **环境健康知识**
  - 空气质量影响
  - 水质安全标准
  - 环境污染指标
  - 季节性健康风险
  - 气候变化健康影响

- **心理健康知识**
  - 认知行为理论
  - 情绪管理策略
  - 压力应对机制
  - 心理韧性培养
  - 健康心态构建

## 特色功能

### 精准医学特性
- 基因型-表型关联解读
- 药物反应个体化预测
- 营养需求个性化建议
- 疾病风险个体化评估
- 针对具体基因变异的健康建议

### 多模态健康特性
- 图像识别与分析
- 语音特征提取
- 可穿戴设备数据解读
- 多源数据融合分析
- 健康模式识别与预警

### 环境健康特性
- 空气质量与健康关联
- 季节性疾病预警
- 环境健康指数评估
- 环境风险因素分析
- 气候变化健康影响评估

### 循证医学特性
- 医学证据等级评估
- 临床指南整合
- 最新研究结果同步
- 证据置信度计算
- 医学建议可靠性评级

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 许可证

Copyright © 2024 索克生活. 保留所有权利。