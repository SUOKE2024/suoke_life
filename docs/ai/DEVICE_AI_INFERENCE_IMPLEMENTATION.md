# 索克生活 - 设备端AI推理功能实现文档

## 概述

本文档详细介绍了为"索克生活（Suoke Life）"项目实现的设备端AI推理功能。该功能基于ONNX Runtime，提供完整的边缘计算和本地推理能力，支持中医诊断、健康评估、症状分析和生活方式推荐等核心业务场景。

## 架构设计

### 核心组件架构

```
src/core/onnx-runtime/
├── index.ts                    # 主入口文件和管理器
├── types.ts                    # 完整类型定义
├── constants.ts                # 配置常量
├── ONNXInferenceEngine.ts      # 推理引擎核心
├── ModelLoader.ts              # 模型加载器
├── ModelQuantizer.ts           # 模型量化工具
├── ModelOptimizer.ts           # 模型优化器
├── EdgeComputeManager.ts       # 边缘计算管理器
├── DeviceCapabilityDetector.ts # 设备能力检测
├── InferenceCache.ts           # 推理缓存
├── TensorProcessor.ts          # 张量处理器
└── README.md                   # 模块文档
```

### 支持组件

```
src/
├── config/
│   └── onnxConfig.ts           # ONNX Runtime配置管理
├── utils/
│   └── modelQuantization.ts   # 模型量化工具集成
├── components/ai/
│   └── ONNXInferenceProvider.tsx # React Native组件和钩子
├── examples/
│   └── onnx-runtime-usage.ts  # 使用示例
└── services/accessibility-service/
    └── local_inference_engine.py # Python本地推理引擎
```

## 核心功能特性

### 1. ONNXInferenceEngine - 推理引擎

**主要功能：**
- 支持多种执行提供者（CPU、CoreML、NNAPI等）
- 模型加载、卸载和会话管理
- 推理执行和结果处理
- 性能监控和事件系统
- 预热和优化功能

**关键特性：**
- 跨平台兼容（iOS/Android）
- 自动设备能力检测
- 智能执行提供者选择
- 实时性能监控

### 2. ModelQuantizer - 模型量化工具

**支持的量化类型：**
- INT8量化：适用于CPU推理，平衡精度和性能
- INT16量化：中等压缩比，保持较好精度
- FP16量化：适用于支持半精度的设备
- 动态量化：运行时量化，灵活性高

**特色功能：**
- 校准数据管理
- 批量量化处理
- 量化效果评估
- 针对索克生活模型的优化配置

### 3. EdgeComputeManager - 边缘计算管理

**核心能力：**
- 计算任务调度和队列管理
- 资源监控（CPU、内存、GPU）
- 热管理和功耗优化
- 动态配置调整
- 负载均衡

**智能调度：**
- 基于设备性能的任务分配
- 热状态感知的性能调节
- 电池状态优化
- 网络状况适应

### 4. DeviceCapabilityDetector - 设备能力检测

**检测能力：**
- CPU核心数和架构
- 内存容量和可用性
- GPU/NPU支持情况
- 执行提供者兼容性
- 平台特定优化

**自适应配置：**
- 根据设备性能自动调整配置
- 推荐最优执行策略
- 动态资源分配

### 5. InferenceCache - 推理缓存系统

**缓存策略：**
- LRU（最近最少使用）策略
- TTL（生存时间）管理
- 压缩和加密支持
- 持久化存储

**智能缓存：**
- 基于模型类型的缓存策略
- 中医诊断结果长期缓存
- 症状分析短期缓存
- 缓存命中率优化

## 索克生活专用功能

### 1. 中医诊断模型（TCM Diagnosis）

**输入数据：**
- 脉诊数据：脉象特征向量
- 舌诊数据：舌象特征向量
- 面诊数据：面色特征向量
- 症状数据：症状编码向量

**输出结果：**
- 证型识别：气虚、血虚、阴虚、阳虚等
- 体质分类：平和质、气虚质等九种体质
- 置信度评分
- 个性化调理建议

**优化配置：**
- INT8量化保持诊断精度
- 扩展级图优化
- 2小时缓存时间

### 2. 健康评估模型（Health Assessment）

**输入数据：**
- 生命体征：血压、心率、体温等
- 生物标志物：血糖、血脂、炎症指标等
- 生活方式：运动、饮食、睡眠评分

**输出结果：**
- 综合健康评分（0-100）
- 风险因子分析
- 健康改善建议
- 预防性措施推荐

**优化配置：**
- FP16量化保持精度
- 扩展级优化
- 1小时缓存时间

### 3. 症状分析模型（Symptom Analysis）

**输入数据：**
- 症状向量：症状类型和强度
- 持续时间：症状持续时长
- 严重程度：症状严重性评级

**输出结果：**
- 可能疾病列表及概率
- 紧急程度评估（低/中/高）
- 就医建议
- 自我护理指导

**优化配置：**
- 动态量化提升速度
- 全级别优化
- 30分钟缓存时间

### 4. 生活方式推荐模型（Lifestyle Recommendation）

**输入数据：**
- 用户基本信息：年龄、性别
- 活动水平：运动频率和强度
- 饮食习惯：营养摄入评分
- 睡眠质量：睡眠时长和质量

**输出结果：**
- 运动建议评分
- 饮食调整建议
- 睡眠优化建议
- 压力管理建议
- 个性化生活方式计划

**优化配置：**
- INT8量化提升效率
- 全级别优化
- 24小时缓存时间

## 技术实现细节

### 1. 跨平台兼容性

**iOS平台优化：**
```typescript
const IOS_CONFIG = {
  inference: {
    executionProviders: ['coreml', 'cpu'], // 优先使用CoreML
    sessionOptions: {
      intraOpNumThreads: 2,
      interOpNumThreads: 1
    }
  },
  edgeCompute: {
    maxConcurrentTasks: 3,
    memoryLimit: 512,
    cpuThreshold: 75 // iOS设备热管理更严格
  }
};
```

**Android平台优化：**
```typescript
const ANDROID_CONFIG = {
  inference: {
    executionProviders: ['nnapi', 'cpu'], // 优先使用NNAPI
    sessionOptions: {
      intraOpNumThreads: 4,
      interOpNumThreads: 2
    }
  },
  edgeCompute: {
    maxConcurrentTasks: 4,
    memoryLimit: 768,
    cpuThreshold: 85
  }
};
```

### 2. 智能配置管理

**设备性能自适应：**
```typescript
// 根据CPU核心数调整线程数
if (cpuCores >= 8) {
  config.sessionOptions.intraOpNumThreads = 6;
  config.edgeCompute.maxConcurrentTasks = 6;
} else if (cpuCores >= 4) {
  config.sessionOptions.intraOpNumThreads = 4;
  config.edgeCompute.maxConcurrentTasks = 4;
}

// 根据内存大小调整缓存
if (memoryGB >= 8) {
  config.cache.maxSize = 200;
  config.edgeCompute.memoryLimit = 2048;
}
```

**网络状况自适应：**
```typescript
// 离线模式优化
if (!isOnline) {
  config.models.downloadTimeout = 0;
  config.cache.maxSize *= 2; // 增加缓存
  config.cache.ttl *= 2;     // 延长缓存时间
}
```

### 3. React Native集成

**Provider组件使用：**
```tsx
import { ONNXInferenceProvider } from './src/components/ai/ONNXInferenceProvider';

function App() {
  return (
    <ONNXInferenceProvider 
      autoInitialize={true}
      preloadModels={['tcm_diagnosis.onnx', 'health_assessment.onnx']}
    >
      <YourAppComponents />
    </ONNXInferenceProvider>
  );
}
```

**钩子函数使用：**
```tsx
import { useTCMDiagnosis } from './src/components/ai/ONNXInferenceProvider';

function TCMDiagnosisScreen() {
  const { diagnose, isRunning, result, error, isReady } = useTCMDiagnosis();

  const handleDiagnosis = async () => {
    const patientData = {
      pulse: [0.8, 0.6, 0.7],
      tongue: [0.5, 0.3, 0.9],
      complexion: [0.4, 0.8, 0.2],
      symptoms: [1, 0, 1, 0, 1]
    };

    try {
      const result = await diagnose(patientData);
      console.log('诊断结果:', result);
    } catch (error) {
      console.error('诊断失败:', error);
    }
  };

  return (
    <View>
      <Button 
        title="开始诊断" 
        onPress={handleDiagnosis}
        disabled={!isReady || isRunning}
      />
      {isRunning && <Text>正在分析...</Text>}
      {result && <DiagnosisResult result={result} />}
      {error && <Text style={{color: 'red'}}>{error}</Text>}
    </View>
  );
}
```

### 4. Python服务集成

**无障碍服务推理引擎：**
```python
from accessibility_service.local_inference_engine import AccessibilityInferenceService

# 初始化服务
service = AccessibilityInferenceService()
await service.initialize()

# 执行推理
input_data = np.random.randn(1, 224, 224, 3).astype(np.float32)
result = await service.enhance_accessibility(input_data)
print(f"推理结果: {result}")
```

## 性能优化策略

### 1. 模型优化

**量化策略：**
- 中医诊断：INT8量化，保持精度
- 健康评估：FP16量化，平衡精度和性能
- 症状分析：动态量化，优先速度
- 生活方式：INT8量化，优先效率

**图优化：**
- 开发环境：基础级优化，便于调试
- 生产环境：全级别优化，最大化性能

### 2. 缓存策略

**分层缓存：**
- 模型缓存：长期缓存已加载模型
- 推理缓存：基于输入哈希的结果缓存
- 配置缓存：设备配置和能力检测结果

**智能失效：**
- TTL过期自动清理
- LRU策略管理容量
- 内存压力时主动清理

### 3. 资源管理

**内存管理：**
- 模型按需加载和卸载
- 推理结果及时释放
- 内存池复用张量空间

**CPU调度：**
- 基于设备性能调整线程数
- 热状态感知的频率调节
- 后台任务优先级管理

## 部署和使用指南

### 1. 环境要求

**React Native项目：**
- React Native >= 0.68
- TypeScript >= 4.5
- ONNX Runtime React Native >= 1.14

**Python服务：**
- Python >= 3.8
- ONNX Runtime >= 1.14
- NumPy >= 1.21

### 2. 安装配置

**安装依赖：**
```bash
# React Native
npm install onnxruntime-react-native
npm install @react-native-async-storage/async-storage
npm install @react-native-netinfo/netinfo

# Python
pip install onnxruntime
pip install numpy
pip install asyncio
```

**配置模型路径：**
```typescript
// 更新配置
updateONNXConfig({
  models: {
    baseUrl: 'https://your-model-server.com',
    preloadModels: [
      'tcm_diagnosis_v2.onnx',
      'health_assessment_v1.onnx'
    ]
  }
});
```

### 3. 快速开始

**基础使用：**
```typescript
import { quickDeploy } from './src/core/onnx-runtime';

// 快速部署模型
const { manager, model } = await quickDeploy('/models/tcm_diagnosis.onnx');

// 执行推理
const result = await manager.smartInference(model.id, inputs);
```

**索克生活专用：**
```typescript
import { deploySuokeLifeModel } from './src/core/onnx-runtime';

// 部署中医诊断模型
const { manager, model } = await deploySuokeLifeModel(
  '/models/tcm_diagnosis.onnx',
  'tcm'
);
```

## 监控和调试

### 1. 性能监控

**系统状态监控：**
```typescript
const systemStatus = manager.getSystemStatus();
console.log('系统状态:', {
  isInitialized: systemStatus.isInitialized,
  loadedModels: systemStatus.loadedModels,
  performanceMetrics: systemStatus.performanceMetrics,
  cacheStats: systemStatus.cacheStats
});
```

**实时性能指标：**
- 推理延迟
- 内存使用峰值
- CPU使用率
- 缓存命中率
- 错误率统计

### 2. 调试工具

**开发环境配置：**
```typescript
const DEVELOPMENT_CONFIG = {
  inference: {
    enableProfiling: true,    // 启用性能分析
    enableOptimization: false // 关闭优化便于调试
  },
  logging: {
    enabled: true,
    level: 'debug',
    maxLogFiles: 10
  }
};
```

**日志输出：**
- 模型加载状态
- 推理执行时间
- 错误堆栈信息
- 性能瓶颈分析

## 最佳实践

### 1. 模型管理

**模型版本控制：**
- 使用语义化版本号
- 向后兼容性检查
- 渐进式模型更新

**模型优化流程：**
1. 原始模型验证
2. 量化处理
3. 图优化
4. 性能测试
5. 部署验证

### 2. 错误处理

**分层错误处理：**
```typescript
try {
  const result = await runTCMDiagnosis(patientData);
} catch (error) {
  if (error.code === 'MODEL_NOT_LOADED') {
    // 尝试重新加载模型
    await loadModel('tcm_diagnosis.onnx');
    // 重试推理
  } else if (error.code === 'INFERENCE_TIMEOUT') {
    // 降级到简化模型
    const fallbackResult = await runSimpleDiagnosis(patientData);
  } else {
    // 记录错误并提供用户友好的反馈
    logError(error);
    showUserFriendlyError('诊断服务暂时不可用，请稍后重试');
  }
}
```

### 3. 用户体验优化

**渐进式加载：**
- 应用启动时预加载核心模型
- 按需加载特定功能模型
- 后台预热模型会话

**响应式设计：**
- 推理进度指示
- 结果渐进式展示
- 错误状态友好提示

## 未来扩展计划

### 1. 技术增强

**模型压缩：**
- 知识蒸馏技术
- 神经网络剪枝
- 更高效的量化算法

**硬件加速：**
- GPU推理支持
- NPU专用优化
- 自定义算子开发

### 2. 功能扩展

**新模型类型：**
- 图像诊断模型（舌象、面象）
- 语音分析模型（咳嗽、呼吸音）
- 多模态融合模型

**智能化增强：**
- 联邦学习支持
- 个性化模型微调
- 自适应推理策略

### 3. 生态集成

**云边协同：**
- 云端模型训练
- 边缘模型部署
- 增量学习更新

**开放平台：**
- 第三方模型接入
- 插件化架构
- API标准化

## 总结

本实现为索克生活项目提供了完整的设备端AI推理能力，具有以下特点：

1. **完整性**：覆盖从模型加载到推理执行的全流程
2. **专业性**：针对中医诊断等业务场景深度优化
3. **高性能**：多层次优化策略确保推理效率
4. **易用性**：React Native组件和钩子简化集成
5. **可扩展**：模块化设计支持功能扩展
6. **跨平台**：iOS和Android平台统一支持

通过这套设备端AI推理系统，索克生活应用能够在用户设备上直接运行AI模型，提供实时、隐私保护的智能健康服务，真正实现了"将中医智慧数字化，融入现代生活场景"的项目愿景。 