# 多模态RAG增强系统

本系统为索克生活平台提供了完整的多模态检索增强生成功能，专门针对中医诊断场景进行优化。系统支持文本、舌象、脉象等多种模态的数据融合和智能分析。

## 🌟 核心特性

- **多模态数据编码**：支持文本、舌象图像、脉象信号的智能编码
- **跨模态嵌入融合**：使用注意力机制融合不同模态的特征向量
- **中医诊断优化**：针对中医"望闻问切"四诊合参进行特别优化
- **智能检索生成**：基于融合向量进行精准检索和专业回答生成
- **策略可配置**：支持多种融合策略，适应不同诊断场景

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   文本编码器    │    │   舌象编码器    │    │   脉象编码器    │
│  TextEncoder    │    │  TongueEncoder  │    │  PulseEncoder   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  多模态融合器   │
                    │ EmbeddingFusion │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   向量检索器    │
                    │  VectorSearch   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   回答生成器    │
                    │ AnswerGenerator │
                    └─────────────────┘
```

## 🚀 快速开始

### 1. 基本使用

```typescript
import { 
  createConfiguredMultimodalRAGService,
  FUSION_STRATEGIES,
  MODALITY_TYPES 
} from './src/core/multimodal';

// 创建服务实例
const ragService = await createConfiguredMultimodalRAGService(
  vectorDatabase,  // 你的向量数据库实例
  languageModel,   // 你的语言模型实例
  {
    defaultStrategy: FUSION_STRATEGIES.TCM_DIAGNOSIS_ENHANCED,
    defaultTopK: 5,
    defaultThreshold: 0.7
  }
);

// 执行多模态查询
const response = await ragService.query({
  text: '患者舌质红，苔薄黄，脉数，请分析病情',
  tongueImage: tongueImageData,
  pulseSignal: pulseSignalArray,
  strategy: FUSION_STRATEGIES.TCM_DIAGNOSIS_ENHANCED
});

console.log('诊断结果:', response.answer);
console.log('置信度:', response.confidence);
console.log('参考文献:', response.sources);
```

### 2. 添加医学知识库

```typescript
// 批量添加中医知识文档
await ragService.addDocuments([
  {
    id: 'tcm_doc_1',
    content: '舌红苔黄，脉数有力，为实热证。治宜清热泻火，方用白虎汤。',
    modality: MODALITY_TYPES.TEXT,
    metadata: { 
      category: '中医诊断',
      syndrome: '实热证',
      prescription: '白虎汤'
    }
  },
  {
    id: 'tcm_doc_2',
    content: '舌淡苔白，脉沉细，为虚寒证。治宜温阳补气，方用四君子汤。',
    modality: MODALITY_TYPES.TEXT,
    metadata: { 
      category: '中医诊断',
      syndrome: '虚寒证',
      prescription: '四君子汤'
    }
  }
]);
```

### 3. 自定义融合策略

```typescript
import { FusionStrategy } from './src/core/multimodal';

// 创建自定义策略
const customStrategy: FusionStrategy = {
  name: 'pediatric_diagnosis',
  weights: {
    [MODALITY_TYPES.TEXT]: 0.5,      // 儿科重视症状描述
    [MODALITY_TYPES.TONGUE]: 0.3,    // 舌象参考
    [MODALITY_TYPES.PULSE]: 0.2,     // 脉象参考（儿童脉象特殊）
    [MODALITY_TYPES.AUDIO]: 0.0,
    [MODALITY_TYPES.IMAGE]: 0.0
  },
  method: 'weighted_sum',
  parameters: {
    normalization: 'l2'
  }
};

// 添加到服务
ragService.addFusionStrategy(customStrategy);
```

## 📊 支持的模态类型

### 1. 文本模态 (TEXT)
- **输入格式**：字符串
- **应用场景**：症状描述、病史记录、问诊信息
- **编码维度**：768维
- **特征提取**：基于BERT类模型的语义编码

```typescript
const textQuery = {
  text: '患者主诉头痛、失眠、心烦易怒',
  modality: MODALITY_TYPES.TEXT
};
```

### 2. 舌象模态 (TONGUE)
- **输入格式**：ImageData 或 base64字符串
- **应用场景**：舌质、舌苔、舌形分析
- **编码维度**：512维
- **特征提取**：CNN提取颜色、纹理、形状特征

```typescript
const tongueQuery = {
  tongueImage: 'data:image/jpeg;base64,/9j/4AAQ...',
  modality: MODALITY_TYPES.TONGUE
};
```

### 3. 脉象模态 (PULSE)
- **输入格式**：number[] 或 Float32Array
- **应用场景**：脉率、脉律、脉力分析
- **编码维度**：256维
- **特征提取**：信号处理提取时域频域特征

```typescript
const pulseQuery = {
  pulseSignal: [0.1, 0.3, 0.8, 0.5, ...], // 脉象信号数组
  modality: MODALITY_TYPES.PULSE
};
```

## 🎯 融合策略详解

### 1. 中医诊断策略 (tcm_diagnosis_enhanced)
- **适用场景**：综合性中医诊断
- **权重分配**：文本25%，舌象40%，脉象35%
- **融合方法**：跨模态注意力机制
- **特点**：重视舌象和脉象的客观信息

### 2. 症状分析策略 (symptom_analysis)
- **适用场景**：基于症状的初步分析
- **权重分配**：文本60%，舌象20%，脉象20%
- **融合方法**：加权求和
- **特点**：以文本症状描述为主导

### 3. 体质辨识策略 (constitution_identification)
- **适用场景**：中医体质类型判断
- **权重分配**：文本30%，舌象35%，脉象35%
- **融合方法**：多头注意力
- **特点**：平衡各模态信息，适合体质分析

## 🔧 高级配置

### 1. 编码器配置

```typescript
const config = {
  encoders: {
    text: {
      dimension: 768,
      maxLength: 512,
      device: 'gpu'
    },
    tongue: {
      dimension: 512,
      batchSize: 16
    },
    pulse: {
      dimension: 256,
      batchSize: 64
    }
  }
};
```

### 2. 缓存配置

```typescript
const config = {
  cacheSize: 1000,      // 缓存条目数
  cacheTTL: 3600000,    // 缓存时间（毫秒）
  defaultTopK: 5,       // 默认检索数量
  defaultThreshold: 0.7 // 默认相似度阈值
};
```

### 3. 性能配置

```typescript
const config = {
  batchSize: 32,        // 批处理大小
  maxConcurrency: 4     // 最大并发数
};
```

## 📈 性能优化建议

### 1. 向量维度选择
- **文本**：768维（BERT标准）
- **舌象**：512维（平衡精度和性能）
- **脉象**：256维（信号特征相对简单）

### 2. 缓存策略
- 启用查询缓存，避免重复计算
- 定期清理过期缓存
- 根据内存情况调整缓存大小

### 3. 批处理优化
- 批量编码多个文档
- 并行处理不同模态
- 异步执行非关键操作

## 🧪 测试示例

```typescript
// 运行测试
npm test src/core/multimodal/__tests__/

// 性能测试
npm run test:performance

// 集成测试
npm run test:integration
```

## 🔍 故障排除

### 常见问题

1. **编码器初始化失败**
   - 检查模型文件路径
   - 确认设备资源充足
   - 验证依赖库版本

2. **融合结果置信度低**
   - 调整模态权重
   - 检查输入数据质量
   - 尝试不同融合策略

3. **检索结果不准确**
   - 增加知识库文档
   - 调整相似度阈值
   - 优化向量索引

### 调试模式

```typescript
// 启用详细日志
ragService.on('fusionCompleted', (result) => {
  console.log('融合结果:', result);
});

ragService.on('retrievalCompleted', (data) => {
  console.log('检索结果:', data);
});

ragService.on('answerGenerated', (data) => {
  console.log('生成回答:', data);
});
```

## 📚 API参考

详细的API文档请参考各模块的TypeScript类型定义：

- [MultimodalRAGService](./MultimodalRAGService.ts)
- [MultimodalEmbeddingFusion](./MultimodalEmbeddingFusion.ts)
- [MultimodalEncoder](./MultimodalEncoder.ts)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../../../LICENSE) 文件了解详情。 