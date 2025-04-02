# 索克生活知识图谱服务 [完成度: 100%]

基于Neo4j和Milvus的中医知识图谱系统，为索克生活APP提供知识图谱服务支持。

## 功能特点

- 支持中医知识的图谱化存储和检索
- 集成向量数据库实现语义相似度搜索
- 支持多领域知识的组织和管理
- 提供RESTful API接口
- 支持知识图谱的动态扩展和更新
- 集成RAG服务增强检索效果
- 支持精准医学知识节点管理
- 多模态健康数据节点支持
- 环境健康知识节点支持
- 心理健康知识节点支持
- 知识间复杂关系建模
- 跨领域知识图谱对齐
- 3D/AR/VR知识图谱沉浸式可视化

## 技术栈

- Node.js + TypeScript
- Neo4j图数据库
- Milvus向量数据库
- Redis缓存
- Fastify Web框架
- Docker容器化
- Kubernetes编排
- Three.js/A-Frame 3D可视化引擎
- AR.js/8th Wall AR技术支持
- WebXR/WebVR VR支持

## 开发环境要求

- Node.js >= 18.0.0
- Neo4j >= 4.4
- Milvus >= 2.2
- Redis >= 6.0
- Docker >= 20.10
- Kubernetes >= 1.24 (生产环境)

## 快速开始

1. 安装依赖：
```bash
npm install
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件配置相关参数
```

3. 开发模式运行：
```bash
npm run dev
```

4. 构建生产版本：
```bash
npm run build
```

5. 生产模式运行：
```bash
npm start
```

## Docker部署

1. 构建镜像：
```bash
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service:latest .
```

2. 推送镜像：
```bash
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service:latest
```

3. 运行容器：
```bash
docker run -d \
  --name knowledge-graph-service \
  -p 3000:3000 \
  -v /path/to/data:/app/data \
  -v /path/to/models:/app/models \
  --env-file .env \
  suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service:latest
```

## Kubernetes部署

本服务提供了完整的Kubernetes配置，支持在Kubernetes集群中部署。

### 使用kubectl和Kustomize部署

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
kubectl get pods -n suoke -l app=knowledge-graph-service
kubectl get svc -n suoke -l app=knowledge-graph-service
```

### 使用Helm部署

1. 安装或升级Chart：
```bash
helm upgrade --install knowledge-graph-service ./helm \
  --namespace suoke \
  --create-namespace \
  --set image.tag=latest \
  --values ./helm/values.yaml
```

2. 自定义值文件：
```bash
# 创建自定义值文件
cp ./helm/values.yaml ./helm/custom-values.yaml
# 编辑custom-values.yaml以适应环境
```

3. 使用自定义值文件：
```bash
helm upgrade --install knowledge-graph-service ./helm \
  --namespace suoke \
  --values ./helm/custom-values.yaml
```

4. 卸载Chart：
```bash
helm uninstall knowledge-graph-service -n suoke
```

### 持久化存储配置

服务使用三个持久化卷：
- `data`：存储知识图谱数据
- `models`：存储嵌入模型和其他机器学习模型
- `tmp`：临时文件存储

确保在部署前配置了适当的存储类。

### 安全配置

本服务集成了Vault进行密钥管理。请确保在部署前正确配置了Vault。

## API文档

服务集成了完整的Swagger/OpenAPI文档系统，提供了交互式的API文档界面。

### 访问API文档

启动服务后，访问以下URL查看API文档：

- **本地开发环境**：http://localhost:3000/api-docs
- **测试环境**：https://test-api.suoke.life/knowledge-graph/api-docs
- **生产环境**：https://api.suoke.life/knowledge-graph/api-docs

### API文档特性

- 完整的API端点描述和参数说明
- 交互式API测试界面
- 请求和响应示例
- 模型定义和验证规则
- 安全认证方式说明
- 按功能分组的API端点
- 可视化数据模型和关系
- 详细的错误码和响应格式说明
- 支持API导出为其他格式（如Postman Collection）
- 基于环境变量的文档保护机制

### API开发与使用指南

详细的API文档使用和开发指南可在以下文件找到：

- [API文档使用指南](./docs/API_DOCS_GUIDE.md) - 如何使用API文档和测试API
- [Fastify Schema指南](./docs/FASTIFY_SCHEMA_GUIDE.md) - 如何为API端点添加文档和验证
- [API测试指南](./docs/API_TESTING_GUIDE.md) - 如何进行API自动化测试和手动测试

### API文档配置

API文档支持通过环境变量进行配置：

- `SWAGGER_PROTECTED`: 是否对API文档启用访问保护（true/false）
- `SWAGGER_USERNAME`: 访问API文档的用户名
- `SWAGGER_PASSWORD`: 访问API文档的密码

这些配置可以在`.env`文件中设置，示例：

```
SWAGGER_PROTECTED=true
SWAGGER_USERNAME=admin
SWAGGER_PASSWORD=suoke@2024
```

## 可观测性

服务通过以下方式支持可观测性：

1. Prometheus指标：
   - 服务在`:9090/metrics`端点暴露Prometheus指标
   - ServiceMonitor自动配置了指标收集

2. OpenTelemetry集成：
   - 通过环境变量`OTEL_EXPORTER_OTLP_ENDPOINT`配置OpenTelemetry导出器
   - 支持分布式追踪

3. 健康检查端点：
   - `/health/live`：活性检查
   - `/health/ready`：就绪检查
   - `/health/startup`：启动检查

## 目录结构

```
src/
├── config/           # 配置文件
├── core/            # 核心功能
├── domain/          # 领域模型
│   ├── entities/    # 实体定义
│   │   ├── base-node.ts                # 基础节点
│   │   ├── tcm-node.ts                 # 中医节点
│   │   ├── herb-node.ts                # 中药节点
│   │   ├── prescription-node.ts        # 方剂节点
│   │   ├── symptom-node.ts             # 症状节点
│   │   ├── constitution-node.ts        # 体质节点
│   │   ├── acupoint-node.ts            # 穴位节点
│   │   ├── diagnosis-node.ts           # 诊断节点
│   │   ├── meridian-node.ts            # 经络节点
│   │   ├── modern-medicine-node.ts     # 现代医学节点
│   │   ├── precision-medicine-node.ts  # 精准医学节点
│   │   ├── multimodal-health-node.ts   # 多模态健康节点
│   │   ├── environmental-health-node.ts # 环境健康节点
│   │   ├── mental-health-node.ts       # 心理健康节点
│   │   └── relationship-types.ts       # 关系类型定义
│   └── repositories/# 仓储接口
├── infrastructure/  # 基础设施
│   ├── database/    # 数据库连接
│   ├── swagger.ts   # API文档配置
│   └── logger.ts    # 日志工具
├── application/     # 应用服务
├── interfaces/      # 接口层
│   └── http/       # HTTP接口
└── index.ts         # 应用入口
```

## 部署架构

```
                           ┌────────────────┐
                           │  Ingress/Gateway │
                           └────────┬─────────┘
                                   │
                           ┌────────┴─────────┐
                           │  Service         │
                           └────────┬─────────┘
                                   │
              ┌──────────────────┬─┴───────────────────┐
              │                 │                     │
    ┌─────────┴─────────┐  ┌────┴─────────────┐  ┌────┴─────────────┐
    │  Pod             │  │  Pod             │  │  Pod             │
    │                 │  │                 │  │                 │
    │  ┌─────────────┐  │  │  ┌─────────────┐  │  │  ┌─────────────┐  │
    │  │ Container   │  │  │  │ Container   │  │  │  │ Container   │  │
    │  └─────────────┘  │  │  └─────────────┘  │  │  └─────────────┘  │
    │                 │  │                 │  │                 │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
             │                  │                     │
             │                  │                     │
    ┌────────┴──────────────────┴─────────────────────┴────────┐
    │                                                         │
    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
    │  │  PVC Data  │    │  PVC Models │    │  PVC Tmp    │   │
    │  └─────────────┘    └─────────────┘    └─────────────┘   │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
```

## 知识领域

- 中医基础理论
- 方剂学
- 中药学
- 诊断学
- 体质学说
- 食疗学
- 针灸学
- 经络学
- 气功推拿
- 现代医学
- 精准医学
- 多模态健康数据
- 环境健康
- 心理健康

## 数据集和训练集

知识图谱服务包含丰富的数据集和训练集，用于构建和训练知识图谱：

### 数据集

数据集位于 `datasets/` 目录下，包含以下类别：

- **中医特色数据集**：包含中药材、方剂、证型、穴位、经络等中医专业数据
- **多模态数据集**：包含图像、音频、文本等多模态数据
- **健康数据集**：包含基因组、环境健康、心理健康等健康数据

数据集遵循标准命名规范：`{dataset_name}_v{version}_{type}.{ext}`

### 训练集

训练集位于 `training/` 目录下，用于训练以下模型：

- **嵌入模型**：用于节点、关系和图的嵌入表示
- **关系抽取模型**：用于从文本中抽取实体间关系
- **实体识别模型**：用于识别文本中的领域实体
- **知识融合模型**：用于整合多源知识

## 知识服务

知识图谱服务提供以下核心知识服务：

### 1. 多源知识整合

整合以下三类知识源的查询结果：
- **RAG服务**：提供检索增强生成能力
- **知识库服务**：提供结构化和半结构化知识
- **知识图谱**：提供图结构知识和关系推理

### 2. 领域特定知识

支持在特定领域内进行知识查询和分析：
- **领域搜索**：在特定领域内搜索知识
- **领域统计**：获取领域知识统计信息
- **核心概念**：识别领域内的核心概念

### 3. 精准医学分析

整合基因组数据和健康历史，提供个性化健康建议：
- **基因组分析**：分析基因变异和健康风险
- **健康历史分析**：分析个人和家族健康史
- **个性化推荐**：基于基因和健康史的个性化建议

### 4. 多模态健康分析

支持图像、音频等多模态数据输入：
- **图像分析**：分析医学图像和健康相关图像
- **音频分析**：分析语音和生物声学数据
- **健康指标分析**：分析多源健康指标数据

### 5. 环境健康分析

分析环境因素对健康的影响：
- **环境数据分析**：分析空气、水、食物等环境因素
- **地理位置分析**：基于地理位置的健康风险分析
- **季节性分析**：分析季节变化对健康的影响

### 6. 心理健康支持

提供心理健康知识和情绪分析：
- **情绪分析**：分析用户情绪状态
- **心理健康知识**：提供心理健康相关知识
- **干预建议**：根据情绪状态提供干预建议

### 7. 图谱可视化

提供知识图谱的可视化数据：
- **子图可视化**：围绕特定节点的子图可视化
- **领域可视化**：特定领域知识的图谱可视化
- **健康画像可视化**：用户健康数据的图谱可视化

### 8. 沉浸式知识可视化

基于3D、AR、VR技术的知识图谱沉浸式体验：
- **3D图谱可视化**：提供交互式3D知识图谱
- **AR知识叠加**：将知识图谱叠加到现实环境
- **VR沉浸体验**：提供完全沉浸式图谱探索体验

## 3D/AR/VR可视化技术

知识图谱服务支持先进的沉浸式可视化技术，为用户提供直观、交互式的知识探索体验：

### 3D可视化

- **技术实现**：基于Three.js/WebGL的3D图谱渲染
- **特点**：
  - 立体化知识节点和关系表示
  - 多维度数据可视化
  - 动态缩放和旋转
  - 节点类型差异化3D表示
  - 交互式图谱导航

### AR可视化

- **技术实现**：AR.js和8th Wall跨平台AR引擎
- **特点**：
  - 基于图像/QR识别的知识锚定
  - 将知识图谱叠加到实物上
  - 空间中的知识标记
  - 协作式AR知识探索
  - 手势交互和语音控制

### VR可视化

- **技术实现**：WebXR/A-Frame沉浸式VR体验
- **特点**：
  - 完全沉浸式知识空间
  - 体感交互式知识导航
  - "知识宇宙"漫游体验
  - 多人协作VR知识探索
  - 空间音效增强感知
  - 根据相似度优化空间布局

### 应用场景

- **医学教育**：3D解剖与生理系统可视化
- **中医经络**：AR叠加人体经络与穴位
- **食疗推荐**：AR识别食材提供食疗知识
- **健康画像**：VR沉浸式个人健康数据探索
- **药材识别**：AR识别中药材提供详细信息
- **虚拟问诊**：VR环境下的医师咨询
- **环境健康**：AR叠加环境健康风险提示
- **传统文化**：中医经典知识的VR沉浸式学习

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 许可证

版权所有 © 2024 索克生活技术团队