# 索克生活共享服务库

## 共享服务目录

这个目录包含所有智能体服务可共用的功能组件，确保代码复用和一致性。

## 目录结构

```
services/shared/
├── api-contract-tests/      # API契约测试
├── config/                  # 共享配置
├── constants/               # 常量定义
├── docs/                    # 文档
├── interfaces/              # 接口定义
├── linting/                 # 代码风格检查配置
├── loadtest/                # 负载测试脚本
├── middlewares/             # 中间件
├── models/                  # 数据模型
│   ├── dialect.model.js     # 方言模型
│   ├── knowledge-node.model.js
│   └── ...
├── scripts/                 # 工具脚本
├── services/                # 共享服务
│   ├── dialect/             # 方言服务
│   │   ├── index.js         # 方言服务入口
│   │   ├── model-training.service.js  # 模型训练功能
│   │   └── sample-collection.service.js  # 样本收集功能
│   └── ...
├── tests/                   # 测试
├── types/                   # 类型定义
└── utils/                   # 工具函数
```

## 方言服务

共享方言服务提供了支持多个智能体使用的方言识别和翻译功能，包括：

### 1. 样本收集管理

- 方言音频样本收集和管理
- 样本质量评估和验证
- 方言数据挑战活动

### 2. 模型训练流程

- 训练数据准备
- 模型训练作业管理
- 模型评估和部署

### 3. 如何使用

在各个智能体服务中引入方言服务：

```javascript
// 在老克服务中使用方言服务
const { dialect } = require('../../shared/services');

// 样本收集
const stats = await dialect.sample.getDialectSampleStats('cantonese');

// 模型训练
const trainingJob = await dialect.training.startModelTraining({
  dialectCode: 'cantonese',
  modelType: 'speech_recognition'
});
```

## 集群部署支持

方言服务支持集群部署，通过以下配置实现：

```
# 集群配置
CLUSTER_ENABLED=true
INSTANCE_ID=1
REDIS_CLUSTER_URL=redis://redis-master:6379
TASK_DISTRIBUTION_STRATEGY=round-robin
```

任务分发基于Redis实现协调，适用于多实例协同工作的场景。

## 扩展方言样本库

建议通过以下途径扩展方言样本库：

1. 用户贡献 - 鼓励用户通过应用上传方言样本
2. 线下收集 - 组织线下方言采集活动
3. 公开数据集整合 - 整合现有公开的方言数据集
4. 研究合作 - 与语言学研究机构合作收集专业样本

## 模型训练流程

方言翻译模型训练流程包括：

1. 数据准备：清洗和标准化样本
2. 训练配置：设置模型参数
3. 训练执行：运行训练作业
4. 模型评估：评测模型性能
5. 模型部署：部署到目标环境

## 贡献指南

如需为方言服务添加新功能，请按以下步骤进行：

1. 创建功能分支
2. 遵循现有代码风格
3. 添加测试用例
4. 提交变更请求

## 配置说明

服务使用环境变量配置，可参考 `laoke-service/.env.example` 文件中的设置。