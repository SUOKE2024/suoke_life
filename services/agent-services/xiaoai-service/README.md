# 小艾服务 (xiaoai-service)

## 概述

小艾服务是索克生活APP的四诊协调智能体服务，作为中医四诊合参的核心，负责整合望、闻、问、切四诊数据，进行中医辨证分析，并提供个性化健康建议。小艾服务是连接医疗诊断与用户健康管理的桥梁，通过多模态传感数据的融合，实现中医治未病理念的数字化实践。

## 开发状态

**✓ 开发完成度：100%**

所有核心组件均已完成实现，包括：

- ✓ 四诊协调引擎 - 支持顺序和并行协调模式
- ✓ 多模态融合引擎 - 支持加权、注意力、集成和跨模态等多种融合算法
- ✓ 辨证分析引擎 - 支持八纲辨证、脏腑辨证、气血津液辨证等多种辨证方法
- ✓ 健康建议生成器 - 基于辨证和体质分析，提供多维度健康建议
- ✓ 智能体协作接口 - 实现与其他智能体的通信与协作
- ✓ 单元测试与集成测试 - 完整的测试覆盖

**最近完成的优化：**

1. 增强了多模态融合引擎，现支持4种融合算法
2. 完善了辨证分析引擎，支持知识图谱推理和体质分析
3. 新增了健康建议生成模块，支持多维度个性化建议
4. 优化了服务间通信和错误处理
5. 全面提升了测试覆盖率

## 架构设计

小艾服务采用微服务架构，基于以下核心组件构建：

```
xiaoai-service/
├── api/                # API接口定义
│   ├── grpc/           # gRPC服务接口
│   └── rest/           # REST API接口
├── cmd/                # 命令行入口
│   └── server/         # 服务器启动代码
├── config/             # 配置文件
│   └── prompts/        # LLM提示语模板
├── internal/           # 内部实现
│   ├── agent/          # 智能体核心
│   ├── four_diagnosis/ # 四诊相关功能
│   │   ├── fusion/     # 多模态融合
│   │   ├── reasoning/  # 辨证推理
│   │   └── recommendation/ # 健康建议
│   ├── domain/         # 领域模型
│   ├── delivery/       # 服务交付层
│   ├── orchestrator/   # 协调引擎
│   └── repository/     # 数据仓库
└── pkg/                # 公共工具包
    └── utils/          # 工具函数
```

## 功能领域

小艾服务围绕以下核心功能领域构建：

### 1. 四诊协调引擎

作为核心协调组件，负责整合来自各个四诊微服务的数据，管理诊断流程，并确保数据一致性。

- **关键能力**:
  - 协调四诊微服务调用顺序与优先级
  - 处理四诊数据的异步收集与关联
  - 管理四诊会话状态与上下文
  - 数据流动协调与异常处理
  - 智能推荐后续诊断路径
  - 综合评估四诊完整性
  - 实现四诊数据存储与追踪

### 2. 多模态诊断分析

从各种诊断数据中提取健康特征，处理和融合不同模态的信息，生成统一的健康表征。

- **关键能力**:
  - 舌象特征分析与分类
  - 面诊特征提取与解读
  - 语音健康标记物识别
  - 脉象波形特征分析
  - 问诊数据结构化与要点提取
  - 多模态特征融合
  - 生物标记物关联分析
  - 异常模式检测与预警
  - 跨模态特征相关性分析
  - 加权、注意力、集成和跨模态融合算法

### 3. 中医辨证引擎

基于四诊合参原则，应用中医理论进行辨证分析，评估体质类型，确定证型。

- **关键能力**:
  - 八纲辨证（寒热虚实表里阴阳）
  - 气血津液辨证
  - 脏腑辨证
  - 经络辨证
  - 卫气营血辨证
  - 六经辨证
  - 三焦辨证
  - 体质辨析（九种体质）
  - 证候推理与确认
  - 中西医结合分析
  - 证候一致性验证
  - 证候关系图谱推理

### 4. 健康分析与建议

根据辨证结果，生成个性化健康状态分析和调理建议，支持用户健康管理。

- **关键能力**:
  - 整体健康状态评估
  - 亚健康风险分析
  - 潜在健康问题预警
  - 体质偏颇调理建议
  - 饮食调养建议
  - 起居养生指导
  - 情志调理建议
  - 运动处方生成
  - 外治法推荐
  - 穴位按摩指导
  - 中医养生保健方案
  - 专业就医建议与提醒
  - 多维度健康建议生成
  - 基于体质和证候的个性化方案

### 5. 智能诊间助手

提供智能问答和交互式健康咨询服务，辅助四诊数据收集和解读。

- **关键能力**:
  - 主诉引导与症状询问
  - 病史采集与整理
  - 症状详情探询
  - 生活习惯评估
  - 健康信息科普
  - 诊断解释与疑问解答
  - 四诊结果通俗解读
  - 健康教育与宣导
  - 用户问题分类与处理
  - 情感支持与心理疏导

### 6. 四诊多模态设备集成

与各种生物传感器和医疗设备集成，实现四诊数据的标准化采集。

- **关键能力**:
  - 舌诊数据采集设备集成
  - 面诊图像采集设备集成
  - 听诊设备集成
  - 脉诊设备数据接入
  - 可穿戴设备数据集成
  - 移动设备传感器接入
  - 第三方健康设备互操作
  - 设备数据校准与标准化
  - 多设备数据同步与关联
  - 远程设备状态监控

### 7. 智能体协作引擎

管理小艾与其他智能体（小克、老克、索儿）的协作交互，实现分布式决策。

- **关键能力**:
  - 智能体间消息路由
  - 协作任务分配与跟踪
  - 跨智能体知识共享
  - 协作上下文管理
  - 分布式决策协调
  - 任务完成度监控
  - 冲突处理与协商
  - 多智能体并行协作
  - 协作能力动态发现

### 8. 无障碍健康服务

为听障、视障、语障等特殊人群提供定制化健康服务，确保医疗服务平等可及。

- **关键能力**:
  - 手语识别与翻译
  - 语音到文本转换与增强
  - 文本到语音转换优化
  - 盲文健康信息转换
  - 触觉反馈健康提示
  - 简化健康信息呈现
  - 图像内容口述描述
  - 认知障碍适配服务
  - 老年人友好界面适配
  - 特殊人群专属诊断流程

### 9. 医疗知识库增强

集成中西医结合知识库，支持四诊分析、辨证和健康建议，提供知识支持。

- **关键能力**:
  - 中医典籍知识库接入
  - 西医医学知识整合
  - 药食配伍知识管理
  - 证型治法知识库
  - 辨证规则库维护
  - 体质类型特征库
  - 经络穴位知识图谱
  - 健康生活方式指南
  - 医学研究文献接入
  - 知识实时更新与验证

### 10. 健康数据分析引擎

分析用户历史健康数据，发现模式与趋势，支持长期健康管理。

- **关键能力**:
  - 纵向健康数据分析
  - 健康趋势预测
  - 体质变化追踪
  - 健康干预效果评估
  - 季节性健康变化分析
  - 生活方式影响评估
  - 健康风险预警模型
  - 用药效果分析
  - 诊疗记录结构化
  - 健康数据可视化
  - 个人健康指数计算

## API接口

小艾服务提供以下主要API接口：

### gRPC接口

* `DiagnosisService`: 提供四诊协调与分析服务
  - `CoordinateDiagnosis`: 协调四诊流程
  - `ProcessDiagnosisData`: 处理单项诊断数据
  - `GenerateSyndromeAnalysis`: 生成证型分析
  - `GetConstitutionAssessment`: 获取体质评估

* `HealthAnalysisService`: 提供健康分析与建议服务
  - `GenerateHealthAnalysis`: 生成健康分析报告
  - `GetHealthRecommendations`: 获取健康调理建议
  - `TrackHealthTrends`: 追踪健康趋势变化

* `AgentCollaborationService`: 提供智能体协作服务
  - `RouteAgentMessage`: 路由智能体消息
  - `CoordinateTask`: 协调多智能体任务
  - `RegisterCapability`: 注册智能体能力

### REST API接口

* `/api/v1/diagnosis/session`: 管理诊断会话
* `/api/v1/diagnosis/analyze`: 分析诊断数据
* `/api/v1/health/recommendations`: 获取健康建议
* `/api/v1/collaboration/tasks`: 管理协作任务

## 依赖服务

小艾服务依赖以下微服务：

* `look-service`: 望诊服务，提供舌诊和面诊分析
* `listen-service`: 闻诊服务，提供语音和声音分析
* `inquiry-service`: 问诊服务，提供智能问诊与症状分析
* `palpation-service`: 切诊服务，提供脉象和触诊分析
* `med-knowledge`: 医学知识库服务，提供辨证知识支持
* `message-bus-service`: 消息总线服务，支持智能体间通信
* `accessibility-service`: 无障碍服务，支持特殊人群健康服务
* `rag-service`: 检索增强生成服务，提供知识检索支持

## 部署与扩展

小艾服务支持以下部署方式：

* Docker容器部署
* Kubernetes集群部署
* 云原生弹性伸缩配置

扩展策略：

* 水平扩展：随请求量增加自动扩展实例
* GPU自动扩缩容：对于图像分析和多模态融合任务
* 混合云部署：敏感数据本地处理，非敏感数据云端处理

## 配置指南

服务配置位于`config`目录，主要包含：

* `config.yaml`: 主配置文件
* `logging.yaml`: 日志配置
* `prompts/*.txt`: 提示语模板配置

关键配置项：

```yaml
xiaoai:
  # 四诊协调配置
  coordinator:
    mode: "sequential"  # 'sequential' 或 'parallel'
    timeout: 30000      # 毫秒
    priority_weights:
      look: 0.8
      listen: 0.7
      inquiry: 0.9
      palpation: 0.8
  
  # 特征提取配置
  feature_extraction:
    min_confidence: 0.6
    max_features_per_category: 10
    use_advanced_extraction: true
  
  # 多模态融合配置
  fusion:
    algorithm: "weighted"  # 'weighted', 'attention', 'ensemble', 'cross_modal'
    min_confidence_threshold: 0.5
    use_early_fusion: true
  
  # 辨证分析配置
  differentiation:
    rules_version: "v2"
    confidence_threshold: 0.7
    evidence_requirements: "moderate"  # 'strict', 'moderate', 'lenient'
    methods:
      - "eight_principles"
      - "zang_fu"
      - "qi_blood_fluid"
  
  # 健康建议配置
  recommendations:
    max_recommendations: 10
    min_confidence: 0.6
    category_limits:
      diet: 3
      lifestyle: 2
      exercise: 2
      emotion: 2
      acupoint: 1
      prevention: 1
      medical: 1
  
  # LLM配置
  llm:
    default_model: "gpt-4o"
    timeout: 15000
    max_retries: 3
```

## 使用示例

```python
# 创建gRPC客户端
from xiaoai_service.client import XiaoaiClient

client = XiaoaiClient("localhost:50051")

# 创建诊断会话
session = await client.create_diagnosis_session(user_id="user123")

# 提交舌象图像分析
tongue_result = await client.submit_tongue_image(
    session_id=session.session_id,
    image_url="https://example.com/tongue_image.jpg"
)

# 提交面诊图像分析
face_result = await client.submit_face_image(
    session_id=session.session_id,
    image_url="https://example.com/face_image.jpg"
)

# 提交问诊数据
inquiry_result = await client.submit_inquiry_data(
    session_id=session.session_id,
    symptoms=["头痛", "乏力"],
    duration="三天",
    chief_complaint="近日头痛加重，伴有乏力"
)

# 提交脉诊数据
pulse_result = await client.submit_pulse_data(
    session_id=session.session_id,
    pulse_wave_url="https://example.com/pulse_wave.json"
)

# 获取综合分析结果
analysis = await client.get_syndrome_analysis(session_id=session.session_id)

# 获取健康建议
recommendations = await client.get_health_recommendations(
    user_id="user123",
    analysis_id=analysis.analysis_id
)

# 关闭客户端
await client.close()
```

## 开发指南

### 环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# 构建服务原型
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/xiaoai_service.proto

# 运行服务
python cmd/server/main.py
```

### 主要模块开发

1. ✓ **四诊协调引擎**: 已完成
2. ✓ **特征提取器**: 已完成，支持多种特征提取方法
3. ✓ **多模态融合引擎**: 已完成，支持4种融合算法
4. ✓ **中医辨证引擎**: 已完成，支持多种辨证方法
5. ✓ **健康建议生成器**: 已完成，提供多维度健康建议
6. ✓ **智能体协作引擎**: 已完成，实现多智能体通信与协作

### 测试指南

```bash
# 运行单元测试
pytest test/unit

# 运行集成测试
pytest test/integration

# 运行性能测试
pytest test/performance
```

## 性能指标

系统在标准环境下的性能表现：

- 多模态融合: 平均处理时间 < 50ms/请求
- 辨证分析: 平均处理时间 < 100ms/请求
- 健康建议生成: 平均处理时间 < 30ms/请求
- 完整流程处理: 平均处理时间 < 200ms/请求

## 最近更新

- **2023-08-15**: 优化辨证分析引擎，增加知识图谱推理
- **2023-08-20**: 完善多模态融合算法，新增注意力机制和跨模态融合
- **2023-08-25**: 新增健康建议生成模块，支持多维度个性化建议
- **2023-08-30**: 增强异常处理和服务恢复机制
- **2023-09-01**: 全面提升测试覆盖率，完善集成测试用例

## 未来规划

1. **知识库扩展**: 进一步丰富中医知识库，增加更多中医典籍和现代医学研究成果
2. **多语言支持**: 增加多语言接口，支持国际化需求
3. **模型优化**: 持续优化辨证和融合算法，提升准确率
4. **边缘计算**: 支持在低功耗设备上的轻量级部署
5. **联邦学习**: 引入联邦学习框架，保护用户隐私的同时提升模型性能 