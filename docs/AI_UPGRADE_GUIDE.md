# 索克生活 AI 技术栈升级指南

## 概述

本指南详细介绍了索克生活项目的技术栈升级，包括：
- React Native 0.80+ (支持新架构)
- TypeScript 5.1+ (装饰器支持)
- 最新 AI 框架集成

## 升级内容

### 1. React Native 升级

#### 版本变更
- **从**: 0.79.2
- **到**: 0.80.2

#### 新特性
- ✅ 新架构 (New Architecture) 支持
- ✅ Fabric 渲染器
- ✅ Hermes JavaScript 引擎
- ✅ TurboModules 支持

#### 配置变更
```javascript
// metro.config.js
const config = {
  transformer: {
    unstable_allowRequireContext: true, // 新增
  },
  server: {
    enhanceMiddleware: (middleware) => {
      // AI模型文件支持
      return (req, res, next) => {
        if (req.url.endsWith('.onnx') || req.url.endsWith('.tflite')) {
          res.setHeader('Content-Type', 'application/octet-stream');
        }
        return middleware(req, res, next);
      };
    },
  }
};
```

### 2. TypeScript 升级

#### 版本变更
- **从**: 5.0.4
- **到**: 5.6.3

#### 新特性
- ✅ 装饰器支持 (Decorators)
- ✅ 更好的类型推断
- ✅ 性能优化

#### 配置变更
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "moduleResolution": "bundler",
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "useDefineForClassFields": false
  }
}
```

### 3. AI 框架升级

#### Python 后端
```toml
# pyproject.toml
dependencies = [
    "torch>=2.4.0",
    "transformers>=4.45.0",
    "openai>=1.40.0",
    "anthropic>=0.34.0",
    "langchain>=0.2.0",
    "sentence-transformers>=3.0.0",
    # ... 更多最新依赖
]
```

#### React Native 前端
```json
{
  "dependencies": {
    "@react-native-ai/core": "^1.2.0",
    "@react-native-ai/transformers": "^1.1.0",
    "@react-native-ai/llm": "^1.0.5",
    "react-native-onnx": "^1.3.0",
    "react-native-ml-kit": "^2.1.0"
  }
}
```

## 新增功能

### 1. AI 装饰器系统

使用 TypeScript 5.1+ 的装饰器功能：

```typescript
import { AIModel, AITask, AICache, AIRetry } from '@/ai/decorators/AIDecorators';

@AIModel(LLMModelType.GPT4O)
class HealthAnalysisService {
  
  @AITask(AITaskType.HEALTH_ANALYSIS)
  @AICache(true)
  @AIRetry(3)
  async analyzeSymptoms(symptoms: string[]): Promise<AnalysisResult> {
    // AI 分析逻辑
  }
}
```

### 2. 多模型协调器

```typescript
import { AICoordinator } from '@/ai';

const aiCoordinator = new AICoordinator();

// 智能健康分析
const result = await aiCoordinator.analyzeHealthIntelligently({
  taskType: AITaskType.HEALTH_ANALYSIS,
  patientData: {
    age: 35,
    gender: 'female',
    symptoms: ['头痛', '失眠', '疲劳']
  },
  analysisType: 'integrated'
});
```

### 3. 支持的 AI 模型

#### 云端模型
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-4o
- **Anthropic**: Claude-3 Opus, Sonnet, Haiku
- **Google**: Gemini Pro, Gemini Ultra

#### 本地模型
- **Meta**: Llama-3 70B, Llama-3 8B
- **阿里**: Qwen-72B
- **百川**: Baichuan-13B

### 4. 健康分析 AI

```typescript
// 中医诊断
const tcmAnalysis = await llmService.analyzeHealth({
  taskType: AITaskType.TCM_DIAGNOSIS,
  patientData: {
    age: 40,
    gender: 'male',
    symptoms: ['舌苔厚腻', '脉滑数', '口苦']
  },
  analysisType: 'tcm'
});

// 西医分析
const westernAnalysis = await llmService.analyzeHealth({
  taskType: AITaskType.HEALTH_ANALYSIS,
  patientData: {
    age: 40,
    gender: 'male',
    symptoms: ['血压升高', '心率不齐']
  },
  analysisType: 'western'
});
```

## 使用指南

### 1. 环境配置

#### API 密钥配置
```bash
# .env 文件
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-key
```

#### 本地模型配置
```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama3:70b
ollama pull qwen:72b
```

### 2. 开发使用

#### 基础 AI 请求
```typescript
import { LLMService, AITaskType, LLMModelType } from '@/ai';

const llmService = new LLMService();

const response = await llmService.process({
  taskType: AITaskType.TEXT_GENERATION,
  input: '请分析这个健康问题...',
  modelConfig: {
    modelType: LLMModelType.GPT4O,
    temperature: 0.3,
    maxTokens: 1000
  }
});
```

#### 批量处理
```typescript
const requests = [
  { taskType: AITaskType.SUMMARIZATION, input: '长文本1...' },
  { taskType: AITaskType.TRANSLATION, input: '需要翻译的文本...' },
  { taskType: AITaskType.SENTIMENT_ANALYSIS, input: '用户反馈...' }
];

const results = await aiCoordinator.processBatch(requests);
```

### 3. 性能优化

#### 缓存配置
```typescript
// 启用智能缓存
@AICache(true)
async processRequest(input: string) {
  // 相同输入会使用缓存结果
}
```

#### 负载均衡
```typescript
// 动态调整模型优先级
aiCoordinator.updateLoadBalancer(AITaskType.HEALTH_ANALYSIS, [
  LLMModelType.GPT4O,
  LLMModelType.CLAUDE_3_SONNET,
  LLMModelType.GEMINI_PRO
]);
```

## 升级步骤

### 1. 自动升级
```bash
# 运行升级脚本
./scripts/upgrade-tech-stack.sh
```

### 2. 手动升级

#### 步骤 1: 备份
```bash
cp package.json package.json.backup
cp pyproject.toml pyproject.toml.backup
```

#### 步骤 2: 更新依赖
```bash
# Node.js 依赖
npm install

# Python 依赖
uv sync --upgrade
```

#### 步骤 3: 配置新架构
```bash
# iOS
cd ios && pod install --repo-update

# Android
cd android && ./gradlew clean
```

#### 步骤 4: 验证
```bash
npm run type-check
npm run test:unit
```

## 故障排除

### 常见问题

#### 1. TypeScript 装饰器错误
```bash
# 确保 tsconfig.json 配置正确
{
  "experimentalDecorators": true,
  "emitDecoratorMetadata": true
}
```

#### 2. React Native 新架构问题
```bash
# 清理缓存
npx react-native start --reset-cache
rm -rf node_modules && npm install
```

#### 3. AI 模型连接失败
```bash
# 检查 API 密钥
echo $OPENAI_API_KEY

# 测试网络连接
curl -I https://api.openai.com/v1/models
```

### 性能监控

#### AI 请求监控
```typescript
// 启用性能监控
@AIPerformance()
async processAIRequest() {
  // 自动记录性能指标
}
```

#### 系统状态检查
```typescript
// 获取服务状态
const status = aiCoordinator.getServiceStatus();
console.log('AI 服务状态:', status);

// 获取负载均衡信息
const loadBalancer = aiCoordinator.getLoadBalancerInfo();
console.log('负载均衡配置:', loadBalancer);
```

## 最佳实践

### 1. 模型选择策略
- **健康分析**: 优先使用 GPT-4o 或 Claude-3 Opus
- **中医诊断**: 推荐 Qwen-72B 或 GPT-4o
- **文本生成**: Claude-3 Sonnet 性价比最高
- **快速响应**: Claude-3 Haiku 速度最快

### 2. 错误处理
```typescript
try {
  const result = await aiCoordinator.process(request);
} catch (error) {
  // 自动故障转移已内置
  console.error('AI 处理失败:', error);
}
```

### 3. 成本控制
```typescript
import { estimateCost } from '@/ai/utils/AIUtils';

// 估算成本
const cost = estimateCost(LLMModelType.GPT4O, tokensUsed);
if (cost > maxBudget) {
  // 切换到更便宜的模型
}
```

## 后续计划

### 短期目标 (1-2 个月)
- [ ] 完善 AI 模型微调
- [ ] 优化健康分析准确性
- [ ] 增加更多本地模型支持

### 中期目标 (3-6 个月)
- [ ] 实现多模态 AI (文本+图像+语音)
- [ ] 构建专业医疗知识图谱
- [ ] 开发 AI 辅助诊断系统

### 长期目标 (6-12 个月)
- [ ] 个性化 AI 健康助手
- [ ] 实时健康监测与预警
- [ ] 中西医结合智能诊疗

## 支持与反馈

如有问题或建议，请联系开发团队：
- 邮箱: dev@suoke.life
- 技术支持: support@suoke.life
- GitHub Issues: https://github.com/SUOKE2024/suoke_life/issues

---

*最后更新: 2024年12月* 