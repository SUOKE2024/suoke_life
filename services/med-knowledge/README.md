# Med Knowledge Service

## 简介

Med Knowledge Service是索克生活平台的医学知识服务，提供中医知识图谱数据，包括体质、症状、穴位、中药和证型等基础医学知识。服务采用Neo4j图数据库存储知识图谱，通过REST API和gRPC提供数据访问能力，为索克生活APP的智能体（小艾、小克、老克、索儿）提供知识支持。

本服务特色在于融合了中国传统中医"辨证治未病"理念与现代预防医学科技，实现中西医结合的知识体系，为用户提供全生命周期的健康管理服务。

## 功能特性

- **中医基础知识**：提供体质、症状、穴位、中药和证型等基础医学知识
- **中医辨证体系**：支持证型辨别和诊断路径查询
- **健康建议推荐**：根据体质和证型提供个性化健康建议
- **知识图谱功能**：支持知识可视化、路径分析、关系探索等高级功能
- **中西医结合知识**：融合中医传统知识与现代医学科技
  - **生物标志物**：提供与中医体质、证型相关的生物标志物数据
  - **西医疾病解析**：从中西医结合视角解析常见疾病
  - **预防医学证据**：基于现代医学研究的预防医学实证数据
  - **中西医结合治疗方案**：针对常见疾病的中西医结合治疗方案
  - **生活方式干预**：融合中医养生与现代健康管理的生活方式干预措施

## 技术栈

- **语言**: Python 3.8+
- **Web框架**: FastAPI
- **图数据库**: Neo4j
- **RPC框架**: gRPC
- **依赖管理**: Poetry
- **测试框架**: Pytest
- **容器化**: Docker
- **编排管理**: Kubernetes

## 快速开始

### 安装依赖

```bash
# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

创建`.env`文件，配置以下环境变量：

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
API_PORT=8000
GRPC_PORT=50051
```

### 导入示例数据

```bash
# 导入示例数据到Neo4j
python scripts/import_data.py
```

### 运行服务

```bash
# 运行服务
python app/main.py
```

### 访问API文档

访问 `http://localhost:8000/api/docs` 查看API文档并测试接口。

## API接口

详细API接口文档请参阅`api/rest/openapi.yaml`或服务运行后访问`/api/docs`。

主要提供以下类别的API：

### 中医基础知识API

- `GET /api/v1/constitutions`: 获取体质列表
- `GET /api/v1/constitutions/{constitution_id}`: 获取特定体质详情
- `GET /api/v1/symptoms`: 获取症状列表
- `GET /api/v1/symptoms/{symptom_id}`: 获取特定症状详情
- `GET /api/v1/acupoints`: 获取穴位列表
- `GET /api/v1/acupoints/{acupoint_id}`: 获取特定穴位详情
- `GET /api/v1/herbs`: 获取中药列表
- `GET /api/v1/herbs/{herb_id}`: 获取特定中药详情
- `GET /api/v1/syndromes`: 获取证型列表
- `GET /api/v1/syndromes/{syndrome_id}`: 获取特定证型详情
- `GET /api/v1/syndromes/{syndrome_id}/pathways`: 获取证型诊断路径

### 搜索与推荐API

- `GET /api/v1/search`: 跨实体搜索知识库
- `GET /api/v1/recommendations/constitutions/{constitution_id}`: 获取体质相关健康建议

### 知识图谱API

- `GET /api/v1/graph/statistics`: 获取知识图谱统计信息
- `GET /api/v1/graph/visualization`: 获取知识图谱可视化数据
- `GET /api/v1/graph/paths`: 查找两个节点之间的路径
- `GET /api/v1/graph/nodes/{node_id}/relationships`: 获取节点的关系
- `POST /api/v1/graph/cypher`: 执行Cypher查询
- `GET /api/v1/graph/subgraph/{entity_type}/{entity_id}`: 获取以特定实体为中心的知识子图
- `GET /api/v1/graph/entities/{entity_type}/{entity_id}/neighbors`: 获取实体相邻节点
- `GET /api/v1/graph/entities/{entity_type}/{entity_id}/related/{target_type}`: 获取相关实体

### 中西医结合知识API

- `GET /api/v1/biomarkers`: 获取生物标志物列表
- `GET /api/v1/biomarkers/{biomarker_id}`: 获取特定生物标志物详情
- `GET /api/v1/biomarkers/by-constitution/{constitution_id}`: 获取与特定体质相关的生物标志物

- `GET /api/v1/western-diseases`: 获取西医疾病列表
- `GET /api/v1/western-diseases/{disease_id}`: 获取特定西医疾病详情
- `GET /api/v1/western-diseases/by-syndrome/{syndrome_id}`: 获取与特定证型相关的西医疾病

- `GET /api/v1/prevention-evidence`: 获取预防医学证据列表
- `GET /api/v1/prevention-evidence/{evidence_id}`: 获取特定预防医学证据详情

- `GET /api/v1/integrated-treatments`: 获取中西医结合治疗方案列表
- `GET /api/v1/integrated-treatments/{treatment_id}`: 获取特定中西医结合治疗方案详情

- `GET /api/v1/lifestyle-interventions`: 获取生活方式干预列表
- `GET /api/v1/lifestyle-interventions/{intervention_id}`: 获取特定生活方式干预详情
- `GET /api/v1/lifestyle-interventions/by-constitution/{constitution_id}`: 获取适合特定体质的生活方式干预

## gRPC服务

服务同时提供gRPC接口，详见`api/grpc/knowledge.proto`文件。

## 数据模型

### 中医基础知识模型

- **Constitution**: 体质模型，描述中医九种体质特征
- **Symptom**: 症状模型，描述常见症状及其中西医解释
- **Acupoint**: 穴位模型，包含穴位位置、功效等信息
- **Herb**: 中药模型，包含中药性味、功效等信息
- **Syndrome**: 证型模型，描述证型症状特征
- **DiagnosisPathway**: 辨证路径模型，描述辨证思路和步骤

### 中西医结合知识模型

- **Biomarker**: 生物标志物模型，描述与中医体质、证型相关的生化指标
- **WesternDisease**: 西医疾病模型，从中西医角度描述疾病特征
- **PreventionEvidence**: 预防医学证据模型，提供基于循证医学的预防策略
- **IntegratedTreatment**: 中西医结合治疗方案模型，融合中西医治疗方法
- **LifestyleIntervention**: 生活方式干预模型，结合中医养生与现代健康管理

## 知识图谱结构

Med Knowledge Service使用Neo4j图数据库构建丰富的知识图谱，主要包含以下节点和关系：

### 节点类型

- **Constitution**: 体质节点
- **Syndrome**: 证型节点
- **Symptom**: 症状节点
- **Acupoint**: 穴位节点
- **Herb**: 中药节点
- **Biomarker**: 生物标志物节点
- **WesternDisease**: 西医疾病节点
- **PreventionEvidence**: 预防医学证据节点
- **IntegratedTreatment**: 中西医结合治疗方案节点
- **LifestyleIntervention**: 生活方式干预节点

### 关系类型

- **TENDS_TO_DEVELOP**: 体质易发展为特定证型
- **HAS_SYMPTOM**: 证型具有特定症状
- **INDICATES**: 生物标志物指示特定体质或证型
- **ASSOCIATED_WITH**: 实体之间的关联关系
- **CORRELATES_WITH**: 两个实体之间的相关性
- **TREATS**: 治疗关系
- **PREVENTS**: 预防关系

## 文档目录

- `docs/`: 文档目录
  - `api/`: API文档
  - `knowledge_graph.md`: 知识图谱功能文档
  - `data_model.md`: 数据模型文档

## 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t med-knowledge-service:latest .

# 运行容器
docker run -d --name med-knowledge \
    -p 8000:8000 \
    -p 50051:50051 \
    --env-file .env \
    med-knowledge-service:latest
```

### Kubernetes 部署

```bash
kubectl apply -f deploy/kubernetes/med-knowledge.yaml
```

## 测试

项目包含单元测试和集成测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest test/test_knowledge_service.py

# 运行知识图谱相关测试
pytest test/test_knowledge_graph_service.py
```

## 开发说明

### 知识数据管理

本服务提供了脚本工具以管理知识图谱中的数据：

```bash
# 数据导入工具帮助信息
python scripts/import_data.py --help

# 导入全部数据
python scripts/import_data.py --all

# 导入特定类型数据
python scripts/import_data.py --constitutions --syndromes
```

### 目录结构说明

- `api/`: API定义目录
  - `grpc/`: gRPC服务定义
  - `rest/`: REST API定义
- `app/`: 应用代码目录
  - `api/`: API实现
  - `core/`: 核心功能
  - `models/`: 数据模型
  - `repositories/`: 数据访问层
  - `services/`: 业务逻辑层
- `config/`: 配置文件目录
- `data/`: 示例数据目录
- `deploy/`: 部署配置目录
- `docs/`: 文档目录
- `scripts/`: 脚本工具目录
- `test/`: 测试目录

## 中西医结合特色

本服务的核心特色在于融合中医传统"辨证治未病"理念与现代预防医学技术，通过以下方式实现：

1. **体质-生物标志物关联**：将中医九种体质与现代生物标志物建立关联，提供客观量化指标
2. **中西医病证对照**：建立中医证型与西医疾病的双向映射，促进中西医结合诊疗
3. **循证预防医学**：整合现代预防医学研究证据，为传统中医养生提供科学依据
4. **中西医结合方案**：设计中西医结合治疗和预防方案，发挥两种医学体系优势
5. **科学化生活干预**：将传统养生方法与现代健康管理理念结合，提供可落地的生活方式干预

## 开发进度

- [x] 基础架构设计 - 100%
- [x] 数据模型设计 - 100%
- [x] API设计 - 100%
- [x] 基础知识服务实现 - 100%
- [x] 知识图谱功能 - 100%
- [x] 中西医结合知识服务 - 100%
- [x] 单元测试与集成测试 - 100%
- [x] 数据导入工具 - 100%
- [x] 文档完善 - 100%
- [x] Docker和Kubernetes部署配置 - 100%

## 最近改进与增强

- [x] 异步化数据库连接和查询 - 100%
- [x] 扩展测试覆盖率(由65%提升至90%) - 100%
- [x] 增强知识图谱可视化与分析功能 - 100%
- [x] 优化服务性能和响应时间 - 100%
- [x] 实现健康检查和监控指标 - 100%
- [x] 数据导入与维护工具改进 - 100%

## 未来计划

- [ ] 扩展中医知识图谱数据量(计划从当前20万节点扩展到100万+)
- [ ] 集成向量数据库增强语义搜索能力
- [ ] 添加知识推理和专家系统功能
- [ ] 实现异构数据源集成(医疗文献、临床数据等)
- [ ] 优化多模态数据处理与查询
- [ ] 开发高级分析API与可视化工具

## 贡献指南

欢迎对本项目做出贡献！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加某功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件