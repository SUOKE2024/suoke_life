# 索克生活知识图谱训练集

本目录包含用于训练知识图谱嵌入模型、实体关系识别模型和知识融合模型的训练数据。

## 目录结构

```
training/
├── embedding/             # 嵌入模型训练数据
│   ├── node_embeddings/   # 节点嵌入训练数据
│   ├── relation_embeddings/ # 关系嵌入训练数据
│   └── graph_embeddings/  # 图嵌入训练数据
├── relation_extraction/   # 关系抽取训练数据
│   ├── tcm/               # 中医领域
│   ├── medicine/          # 现代医学领域
│   └── cross_domain/      # 跨领域关系
├── entity_recognition/    # 实体识别训练数据
│   ├── tcm_entities/      # 中医实体
│   ├── medical_entities/  # 医学实体
│   └── health_entities/   # 健康实体
└── fusion/                # 知识融合训练数据
    ├── rag_fusion/        # RAG融合训练数据
    ├── multimodal_fusion/ # 多模态融合训练数据
    └── domain_fusion/     # 领域融合训练数据
```

## 训练数据格式

根据不同的训练任务，训练数据采用不同格式:

1. 嵌入训练数据: JSON格式，包含节点ID、标签和属性
2. 关系抽取数据: CSV格式，包含头实体、尾实体、关系类型和上下文
3. 实体识别数据: CONLL格式，包含文本和BIO标注
4. 知识融合数据: JSON格式，包含来自不同源的实体对应关系

## 训练指南

### 嵌入模型训练

1. 使用`training/embedding`目录中的数据训练嵌入模型
2. 运行`scripts/train_embeddings.sh`脚本开始训练
3. 模型保存在`models/embeddings/`目录

### 关系抽取模型训练

1. 使用`training/relation_extraction`目录中的数据训练关系抽取模型
2. 运行`scripts/train_relation_extraction.sh`脚本开始训练
3. 模型保存在`models/relation_extraction/`目录

### 实体识别模型训练

1. 使用`training/entity_recognition`目录中的数据训练实体识别模型
2. 运行`scripts/train_entity_recognition.sh`脚本开始训练
3. 模型保存在`models/entity_recognition/`目录

### 知识融合模型训练

1. 使用`training/fusion`目录中的数据训练知识融合模型
2. 运行`scripts/train_fusion.sh`脚本开始训练
3. 模型保存在`models/fusion/`目录

## 评估指标

- 嵌入模型：链接预测准确率、三元组分类准确率
- 关系抽取：精确率、召回率、F1
- 实体识别：精确率、召回率、F1
- 知识融合：融合准确率、冲突解决率

## 超参数与实验

超参数设置与实验结果记录在`experiments/`目录中。

## 最佳实践

1. 数据分割：确保训练集、验证集和测试集之间没有重叠
2. 数据平衡：对于不平衡类别，使用权重或过采样技术
3. 训练监控：记录训练日志，监控损失和评估指标
4. 模型选择：根据验证集性能选择最佳模型

## 已训练模型

已训练的模型保存在`models/`目录，按照模型类型和版本组织。

## 更新日志

- 2023-12-20: 初始训练数据集发布 (v1.0)
- 2024-01-25: 添加跨领域关系抽取训练数据 (v1.1)
- 2024-02-15: 扩展中医实体识别训练数据 (v1.2)
- 2024-03-10: 添加多模态融合训练数据 (v1.3) 